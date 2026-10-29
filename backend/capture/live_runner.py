
import argparse
import time

from backend.capture.adapter import TSharkCapture
from backend.capture.feature_window import (
    CausalWindowManager,
    FeatureExtractor,
)


DNS_FEATURES = (
    "dns_request_count",
    "dns_response_count",
    "dns_latency_mean",
)


def run_live_capture(interface: str = "5"):
    capture = TSharkCapture(interface=interface)
    window_size = 1.0

    window_manager = CausalWindowManager(window_size=window_size)
    extractor = FeatureExtractor(window_size=window_size)

    packet_count = 0
    window_count = 0

    print(f"Starting capture on interface: {interface}")
    print("Press Ctrl+C to stop.")

    def process_windows(completed_windows):
        nonlocal window_count

        for window in completed_windows:
            packets = window["packets"]
            if not packets:
                continue

            duration = window.get("duration", window_size)

            features = extractor.extract_window_features(
                packets,
                duration=duration,
            )
            window_count += 1

            print(
                f"\nWindow {window['window_id']} "
                f"({len(packets)} packets, duration: {duration:.6f}s)"
            )

            for name, value in features.items():
                print(f"  {name}: {value}")

            print("  DNS SUMMARY:")
            for name in DNS_FEATURES:
                print(f"    {name}: {features.get(name, 'MISSING')}")

    try:
        for packet in capture.packets():
            packet_count += 1

            process_windows(window_manager.add_packet(packet))

            if packet_count % 100 == 0:
                print(f"Packets captured: {packet_count}")

    except KeyboardInterrupt:
        print("\nCapture interrupted.")

    except (OSError, RuntimeError, ValueError) as exc:
        print(f"\nCapture stopped: {exc}")

    finally:
        # Record shutdown time in the same epoch time base as packet timestamps.
        stop_timestamp = time.time()

        try:
            capture.stop()
        except Exception as exc:
            print(f"[TShark] Stop error: {exc}")

        # Process the remaining partial window, if any.
        process_windows(
            window_manager.flush(stop_timestamp=stop_timestamp)
        )

        print(f"\nTotal packets captured: {packet_count}")
        print(f"Feature windows processed: {window_count}")


def main():
    parser = argparse.ArgumentParser(
        description="Cogni-Fi live packet feature extraction"
    )
    parser.add_argument(
        "--interface",
        default="5",
        help="TShark interface name or number (default: 5)",
    )

    args = parser.parse_args()
    run_live_capture(args.interface)


if __name__ == "__main__":
    main()
