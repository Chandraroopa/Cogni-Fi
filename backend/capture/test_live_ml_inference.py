
import json
import time
from pathlib import Path

from backend.capture.adapter import TSharkCapture
from backend.capture.feature_window import (
    CausalWindowManager,
    FeatureExtractor,
)
from backend.capture.feature_adapter import FeatureAdapter
from backend.capture.schema_aggregator import SchemaFeatureAggregator
from backend.capture.feature_engineering import WindowFeatureEngineer
from backend.ml_service import CognifiMLService


RESULTS_PATH = Path("live_ml_results.jsonl")
CAPTURE_DURATION_SECONDS = 60
WINDOW_SIZE_SECONDS = 1.0

BEHAVIOR_FEATURE_NAMES = (
    "behavior_iat",
    "behavior_tcp_seq_delta_flow",
    "behavior_tcp_ack_delta_flow",
    "behavior_wlan_seq_delta_sender",
)


def _write_result(output):
    """Append one result record to the JSON Lines file."""
    try:
        with RESULTS_PATH.open("a", encoding="utf-8") as file:
            file.write(
                json.dumps(
                    output,
                    default=str,
                    allow_nan=False,
                )
                + "\n"
            )
    except (OSError, ValueError) as exc:
        print(
            f"Could not write results file: "
            f"{type(exc).__name__}: {exc}"
        )


def main():
    interface = (
        input(
            "Enter TShark interface number (Wi-Fi is 5 on your PC): "
        ).strip()
        or "5"
    )

    capture = TSharkCapture(interface=interface)
    windows = CausalWindowManager(
        window_size=WINDOW_SIZE_SECONDS
    )
    extractor = FeatureExtractor(
        window_size=WINDOW_SIZE_SECONDS
    )
    adapter = FeatureAdapter(ml_dir="ml")
    schema_aggregator = SchemaFeatureAggregator()
    behavior_engineer = WindowFeatureEngineer()
    ml = CognifiMLService()

    packet_count = 0
    window_count = 0
    binary_success_count = 0
    multiclass_success_count = 0
    started = time.monotonic()

    print(f"\nCapturing on interface {interface}.")
    print("Generate normal traffic, e.g. open a few websites.")
    print(f"Capture limit: {CAPTURE_DURATION_SECONDS} seconds.")
    print("Press Ctrl+C to stop early.")
    print(f"Results will be appended to: {RESULTS_PATH.resolve()}")

    def process(completed):
        nonlocal window_count
        nonlocal binary_success_count
        nonlocal multiclass_success_count

        for window in completed:
            packets = window.get("packets", [])

            if not packets:
                continue

            window_count += 1

            print(
                f"\nWindow {window.get('window_id', 'unknown')}: "
                f"{len(packets)} packets"
            )

            output = {
                "window_id": window.get("window_id"),
                "packet_count": len(packets),
                "binary": None,
                "multiclass": None,
                "errors": [],
            }

            # Step 1: Extract operational window features,
            # schema aggregates, and existing behavioral features.
            try:
                features = extractor.extract_window_features(
                    packets,
                    duration=WINDOW_SIZE_SECONDS,
                )

                aggregate_features = schema_aggregator.aggregate(
                    packets
                )
                features.update(aggregate_features)

                behavior_features = behavior_engineer.extract(
                    packets
                )

                for name in BEHAVIOR_FEATURE_NAMES:
                    if name in behavior_features:
                        features[name] = behavior_features[name]

                output["behavior_features"] = {
                    name: features.get(name)
                    for name in BEHAVIOR_FEATURE_NAMES
                }

            except Exception as exc:
                message = (
                    f"Feature extraction failed: "
                    f"{type(exc).__name__}: {exc}"
                )
                output["errors"].append(message)
                print(message)
                _write_result(output)
                continue

            # Step 2: Binary Normal/Threat prediction.
            try:
                binary_input = adapter.adapt_for_binary(features)
                binary_dict = binary_input.iloc[0].to_dict()

                output["binary"] = ml.predict_binary(binary_dict)
                binary_success_count += 1

                print("Binary inference: ACCEPTED")
                print(json.dumps(output["binary"], indent=2))

            except Exception as exc:
                message = (
                    f"Binary inference failed: "
                    f"{type(exc).__name__}: {exc}"
                )
                output["errors"].append(message)
                print(message)

                # Do not run multiclass when binary inference fails.
                _write_result(output)
                continue

            # Step 3: Run multiclass classification only for threats.
            if output["binary"]["is_threat"]:
                try:
                    multiclass_input = adapter.adapt_for_multiclass(
                        features
                    )
                    multiclass_dict = (
                        multiclass_input.iloc[0].to_dict()
                    )

                    output["multiclass"] = ml.predict_multiclass(
                        multiclass_dict
                    )
                    multiclass_success_count += 1

                    print("Multiclass inference: ACCEPTED")
                    print(
                        json.dumps(
                            output["multiclass"],
                            indent=2,
                        )
                    )

                except Exception as exc:
                    message = (
                        f"Multiclass inference failed: "
                        f"{type(exc).__name__}: {exc}"
                    )
                    output["errors"].append(message)
                    print(message)
            else:
                print(
                    "Multiclass skipped: binary result is Normal."
                )

            _write_result(output)

    try:
        for packet in capture.packets():
            packet_count += 1

            completed_windows = windows.add_packet(packet)
            process(completed_windows)

            if (
                time.monotonic() - started
                >= CAPTURE_DURATION_SECONDS
            ):
                print("\nCapture time limit reached.")
                break

    except KeyboardInterrupt:
        print("\nCapture interrupted by user.")

    except Exception as exc:
        print(
            f"\nCapture error: {type(exc).__name__}: {exc}"
        )

    finally:
        # Stop capture before processing the final partial window.
        try:
            capture.stop()
        except Exception as exc:
            print(
                f"Capture cleanup warning: "
                f"{type(exc).__name__}: {exc}"
            )

        try:
            process(windows.flush())
        except Exception as exc:
            print(
                f"Final window processing error: "
                f"{type(exc).__name__}: {exc}"
            )

        elapsed = time.monotonic() - started

        print("\nCapture summary")
        print(f"Packets captured: {packet_count}")
        print(f"Feature windows processed: {window_count}")
        print(f"Binary inferences accepted: {binary_success_count}")
        print(
            "Multiclass inferences accepted: "
            f"{multiclass_success_count}"
        )
        print(f"Elapsed time: {elapsed:.1f} seconds")
        print(f"Results file: {RESULTS_PATH.resolve()}")


if __name__ == "__main__":
    main()
