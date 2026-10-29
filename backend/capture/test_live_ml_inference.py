
import json
import time
from pathlib import Path

from backend.capture.adapter import TSharkCapture
from backend.capture.feature_window import (
    CausalWindowManager,
    FeatureExtractor,
    FEATURE_NAMES,
)
from ml.inference.predictor import predict_one


RESULTS_PATH = Path("live_ml_results.jsonl")
CAPTURE_DURATION_SECONDS = 60
WINDOW_SIZE_SECONDS = 1.0


def write_result(output):
    """Append one result to the JSON Lines file."""
    try:
        with RESULTS_PATH.open("a", encoding="utf-8") as file:
            file.write(
                json.dumps(output, default=str, allow_nan=False) + "\n"
            )
    except (OSError, ValueError) as exc:
        print(f"Could not write results: {type(exc).__name__}: {exc}")


def main():
    interface = input(
        "Enter TShark interface number (Wi-Fi is 5): "
    ).strip() or "5"

    capture = TSharkCapture(interface=interface)
    windows = CausalWindowManager(window_size=WINDOW_SIZE_SECONDS)
    extractor = FeatureExtractor(window_size=WINDOW_SIZE_SECONDS)

    packet_count = 0
    window_count = 0
    inference_count = 0
    started = time.monotonic()

    # Start a fresh results file for this run.
    RESULTS_PATH.write_text("", encoding="utf-8")

    print(f"\nCapturing on interface {interface}.")
    print("Generate normal traffic by browsing a few websites.")
    print(f"Capture duration: {CAPTURE_DURATION_SECONDS} seconds.")
    print(f"Results: {RESULTS_PATH.resolve()}")
    print("Press Ctrl+C to stop early.")

    def process(completed):
        nonlocal window_count, inference_count

        for window in completed:
            packets = window.get("packets", [])
            if not packets:
                continue

            window_count += 1
            output = {
                "window_id": window.get("window_id"),
                "packet_count": len(packets),
                "model": "multiclass_30",
                "prediction": None,
                "error": None,
            }

            try:
                features = extractor.extract_window_features(
                    packets,
                    duration=WINDOW_SIZE_SECONDS,
                )

                missing = [
                    name for name in FEATURE_NAMES
                    if name not in features
                ]
                if missing:
                    raise ValueError(
                        f"Missing model features: {missing}"
                    )

                model_features = {
                    name: features[name] for name in FEATURE_NAMES
                }

                result = predict_one(model_features)
                output["prediction"] = result
                inference_count += 1

                print(
                    f"Window {window.get('window_id', window_count)} | "
                    f"packets={len(packets)} | "
                    f"class={result['predicted_class']} | "
                    f"confidence={result['confidence']:.3f} | "
                    f"threat_probability="
                    f"{result['threat_probability']:.3f}"
                )

            except Exception as exc:
                output["error"] = (
                    f"{type(exc).__name__}: {exc}"
                )
                print(f"Window {window_count} failed: {output['error']}")

            write_result(output)

    try:
        for packet in capture.packets():
            packet_count += 1
            process(windows.add_packet(packet))

            if time.monotonic() - started >= CAPTURE_DURATION_SECONDS:
                print("\nCapture time limit reached.")
                break

    except KeyboardInterrupt:
        print("\nCapture stopped by user.")

    except Exception as exc:
        print(f"\nCapture error: {type(exc).__name__}: {exc}")

    finally:
        try:
            capture.stop()
        except Exception as exc:
            print(f"Capture cleanup warning: {exc}")

        try:
            process(windows.flush())
        except Exception as exc:
            print(f"Final window error: {exc}")

        print("\n--- Capture summary ---")
        print(f"Packets captured: {packet_count}")
        print(f"Windows processed: {window_count}")
        print(f"Successful model inferences: {inference_count}")
        print(f"Elapsed: {time.monotonic() - started:.1f} seconds")
        print(f"Results saved to: {RESULTS_PATH.resolve()}")


if __name__ == "__main__":
    main()
