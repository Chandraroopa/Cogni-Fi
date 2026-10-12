
import csv
import json
import time
import traceback
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from backend.capture.adapter import TSharkCapture
from backend.capture.feature_window import (
    CausalWindowManager,
    FeatureExtractor,
    FEATURE_NAMES,
    WIFI_AVAILABILITY_NAMES,
)

INTERFACE = "5"
CAPTURE_SECONDS = 60
WINDOW_SECONDS = 1.0


def utc(ts):
    return datetime.fromtimestamp(ts, timezone.utc).isoformat()


def read_wifi_details():
    """Read Windows Wi-Fi metadata without inventing unavailable values."""
    details = {
        "ssid": None,
        "security_authentication": None,
        "cipher": None,
        "bssid": None,
        "channel": None,
        "wifi_details_source": "netsh wlan show interfaces",
    }

    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        patterns = {
            "ssid": r"^\s*SSID\s*:\s*(.+?)\s*$",
            "security_authentication": (
                r"^\s*Authentication\s*:\s*(.+?)\s*$"
            ),
            "cipher": r"^\s*Cipher\s*:\s*(.+?)\s*$",
            "bssid": r"^\s*BSSID\s*:\s*([0-9A-Fa-f:.-]+)\s*$",
            "channel": r"^\s*Channel\s*:\s*(\d+)\s*$",
        }

        for key, pattern in patterns.items():
            match = re.search(
                pattern,
                result.stdout,
                re.MULTILINE | re.IGNORECASE,
            )
            if match:
                value = match.group(1).strip()
                details[key] = (
                    int(value) if key == "channel" else value
                )

    except (OSError, subprocess.SubprocessError) as exc:
        details["wifi_details_error"] = str(exc)

    return details


def make_empty_window(window_id, start, end):
    """Create an interval with no assigned packets."""
    return {
        "window_id": window_id,
        "start_timestamp": start,
        "end_timestamp": end,
        "packets": [],
    }


def save_empty_intervals(
    start,
    end,
    next_window_id,
    save_window,
):
    """
    Export packet-free intervals between start and end.

    Intervals are capped at WINDOW_SECONDS. The final interval can
    be shorter. These rows represent no assigned packets, not proof
    that every packet was observable by the capture system.
    """
    cursor = start

    while cursor < end:
        interval_end = min(
            cursor + WINDOW_SECONDS,
            end,
        )

        if interval_end <= cursor:
            break

        save_window(
            make_empty_window(
                next_window_id,
                cursor,
                interval_end,
            )
        )

        next_window_id += 1
        cursor = interval_end

    return next_window_id


def main():
    out = Path("data")
    out.mkdir(exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = out / f"live_windows_{stamp}.csv"
    json_path = out / f"live_windows_{stamp}.json"

    manager = CausalWindowManager(WINDOW_SECONDS)
    extractor = FeatureExtractor(WINDOW_SECONDS)
    capture = TSharkCapture(INTERFACE)

    rows = []

    started_wall = time.time()
    started_mono = time.monotonic()
    deadline = started_mono + CAPTURE_SECONDS

    stopped = None
    first_packet_timestamp = None
    next_window_id = 0

    valid_packet_count = 0
    skipped_packet_count = 0
    capture_error = None

    def save_window(window, final=False):
        packets = window["packets"]
        start = float(window["start_timestamp"])
        nominal_end = float(window["end_timestamp"])

        capture_end = stopped if stopped is not None else time.time()

        # Do not export beyond the actual capture stop.
        actual_end = min(nominal_end, capture_end)
        duration = max(0.0, actual_end - start)

        # Keep the existing feature extractor behavior.
        feature_duration = (
            duration if duration > 0 else WINDOW_SECONDS
        )

        features = extractor.extract_window_features(
            packets,
            duration=feature_duration,
        )

        row = {
            "window_id": window["window_id"],
            "timestamp_start_epoch": start,
            "timestamp_start_utc": utc(start),
            "timestamp_end_epoch": actual_end,
            "timestamp_end_utc": utc(actual_end),
            "window_duration_seconds": duration,
            "is_empty": len(packets) == 0,
            "packet_count_observed": len(packets),
            "traffic_label": "unlabelled",
            "is_final_flushed_window": final,
        }

        row.update({
            name: features[name]
            for name in FEATURE_NAMES
        })

        row.update({
            name: features[name]
            for name in WIFI_AVAILABILITY_NAMES
        })

        rows.append(row)

    try:
        print(
            f"Capturing on interface {INTERFACE} "
            f"for {CAPTURE_SECONDS} seconds..."
        )

        for packet in capture.packets():
            if time.monotonic() >= deadline:
                break

            # Reject invalid timestamps rather than inventing them.
            raw_timestamp = packet.get("timestamp")

            try:
                timestamp = float(raw_timestamp)
            except (TypeError, ValueError, OverflowError):
                skipped_packet_count += 1
                continue

            if not (
                timestamp > 0
                and timestamp < float("inf")
            ):
                skipped_packet_count += 1
                continue

            packet = dict(packet)
            packet["timestamp"] = timestamp

            if first_packet_timestamp is None:
                first_packet_timestamp = timestamp

                # Include the initial interval before the first packet.
                next_window_id = save_empty_intervals(
                    started_wall,
                    first_packet_timestamp,
                    next_window_id,
                    save_window,
                )

            completed = manager.add_packet(packet)
            valid_packet_count += 1

            for window in completed:
                # Fill detectable gaps between completed packet windows.
                while next_window_id < window["window_id"]:
                    empty_start = (
                        first_packet_timestamp
                        + next_window_id * WINDOW_SECONDS
                    )
                    empty_end = min(
                        empty_start + WINDOW_SECONDS,
                        timestamp,
                    )

                    if empty_end <= empty_start:
                        break

                    save_window(
                        make_empty_window(
                            next_window_id,
                            empty_start,
                            empty_end,
                        )
                    )

                    next_window_id += 1

                save_window(window)
                next_window_id = window["window_id"] + 1

    except KeyboardInterrupt:
        print("Capture interrupted by user.")

    except Exception as exc:
        capture_error = f"{type(exc).__name__}: {exc}"
        print(f"Capture error: {capture_error}")
        traceback.print_exc()

    finally:
        # Record the real stop time before flushing remaining windows.
        stopped = time.time()

        try:
            capture.close()
        except (AttributeError, OSError):
            pass

        for window in manager.flush():
            while next_window_id < window["window_id"]:
                empty_start = (
                    first_packet_timestamp
                    + next_window_id * WINDOW_SECONDS
                )
                empty_end = min(
                    empty_start + WINDOW_SECONDS,
                    float(window["start_timestamp"]),
                )

                if empty_end <= empty_start:
                    break

                save_window(
                    make_empty_window(
                        next_window_id,
                        empty_start,
                        empty_end,
                    )
                )

                next_window_id += 1

            save_window(window, final=True)
            next_window_id = window["window_id"] + 1

        # Include the final packet-free interval through capture stop.
        if first_packet_timestamp is not None and rows:
            last_window_end = float(
                rows[-1]["timestamp_end_epoch"]
            )

            if stopped > last_window_end:
                next_window_id = save_empty_intervals(
                    last_window_end,
                    stopped,
                    next_window_id,
                    save_window,
                )

    # Write CSV when rows exist.
    if rows:
        with csv_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=list(rows[0].keys()),
            )
            writer.writeheader()
            writer.writerows(rows)

    wifi_details = read_wifi_details()

    metadata = {
        "interface": INTERFACE,
        "capture_started_utc": utc(started_wall),
        "capture_stopped_utc": utc(stopped),
        "capture_elapsed_seconds": round(
            stopped - started_wall,
            3,
        ),
        "requested_capture_seconds": CAPTURE_SECONDS,
        "configured_window_seconds": WINDOW_SECONDS,
        "window_count": len(rows),
        "valid_packets_processed": valid_packet_count,
        "packets_skipped_invalid_timestamp": skipped_packet_count,
        "traffic_label": "unlabelled",
        "feature_names": FEATURE_NAMES,
        "availability_flags": WIFI_AVAILABILITY_NAMES,
        "wifi_details": wifi_details,
        "radio_capture_limitation": (
            "The previously tested interface exposed Ethernet/IP packets "
            "without 802.11/radiotap fields. This limitation applies to the "
            "tested capture mode; retest other supported modes separately."
        ),
        "missing_value_warning": (
            "Numeric zero can mean measured zero or unavailable data. "
            "The six Wi-Fi availability flags do not cover every feature. "
            "Inspect the adapter field mapping before interpreting zeros."
        ),
        "window_duration_note": (
            "The export includes packet-relative windows and packet-free "
            "intervals before the first packet and after the last packet, "
            "bounded by the recorded capture start and stop timestamps. "
            "Boundary windows may be shorter than the configured window "
            "size. Empty windows indicate no packets were assigned to that "
            "interval; they do not prove that every packet was observable."
        ),
        "capture_error": capture_error,
        "csv_file": str(csv_path),
    }

    json_path.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print(f"Valid packets processed: {valid_packet_count}")
    print(
        "Invalid-timestamp packets skipped: "
        f"{skipped_packet_count}"
    )
    print(f"Windows exported: {len(rows)}")
    print(f"CSV: {csv_path}")
    print(f"Metadata: {json_path}")
    print("Traffic remains unlabelled.")


if __name__ == "__main__":
    main()
