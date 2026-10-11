import argparse

from backend.capture.adapter import TSharkCapture
from backend.capture.feature_window import (
    CausalWindowManager,
    FeatureExtractor,
)


def run_live_capture(interface: str = "1"):
    capture = TSharkCapture(interface=interface)
    windows = CausalWindowManager(window_size=1.0)
    extractor = FeatureExtractor(window_size=1.0)

    packet_count = 0
    window_count = 0

    print(f"Starting capture on interface: {interface}")
    print("Press Ctrl+C to stop.")

    def process_windows(completed_windows):
        nonlocal window_count

        for window in completed_windows:
            packets = window["packets"]

            # Extract operational features from this window's packets.
            features = extractor.extract_window_features(packets)
            window_count += 1

            print(
                f"\nWindow {window['window_id']} "
                f"({len(packets)} packets)"
            )

            for name, value in features.items():
                print(f"  {name}: {value}")

    try:
        for packet in capture.packets():
            packet_count += 1

            # Each packet must have a valid timestamp.
            process_windows(windows.add_packet(packet))

            if packet_count % 100 == 0:
                print(f"Packets captured: {packet_count}")

    except KeyboardInterrupt:
        print("\nCapture interrupted.")

    except (OSError, RuntimeError, ValueError) as exc:
        print(f"\nCapture stopped: {exc}")

    finally:
        capture.stop()

        # Process the final partial window before exiting.
        process_windows(windows.flush())

        print(f"\nTotal packets captured: {packet_count}")
        print(f"Feature windows processed: {window_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cogni-Fi packet capture and feature extraction"
    )
    parser.add_argument(
        "--interface",
        default="1",
        help="TShark interface name or number (default: 1)",
    )
    args = parser.parse_args()

    run_live_capture(args.interface)
