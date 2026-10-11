
from backend.capture.adapter import TSharkCapture
from backend.capture.feature_window import (
    FeatureExtractor,
    CausalWindowManager,
)
import time

capture = TSharkCapture(interface="5")
manager = CausalWindowManager(window_size=1.0)
extractor = FeatureExtractor(window_size=1.0)

try:
    start = time.time()

    for packet in capture.packets():
        windows = manager.add_packet(packet)

        for window in windows:
            packets = window["packets"]
            features = extractor.extract_window_features(
    packets,
    duration=1.0,
)

            print("\n=== ACTUAL LIVE FEATURE WINDOW ===")
            print("Window ID:", window["window_id"])
            print("Packets:", len(packets))
            print("Feature count:", len(features))

            for name, value in features.items():
                print(f"{name}: {value!r}")

            missing = [
                name for name, value in features.items()
                if value is None
            ]
            print("\nMissing values:", missing)
            raise SystemExit

        if time.time() - start >= 15:
            print("No completed window received within 15 seconds.")
            break
finally:
    capture.stop()
