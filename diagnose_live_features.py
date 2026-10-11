import json
import time

from backend.capture.adapter import TSharkCapture
from backend.capture.feature_window import (
    CausalWindowManager,
    FeatureExtractor,
)
from backend.capture.feature_adapter import FeatureAdapter
from backend.capture.schema_aggregator import SchemaFeatureAggregator

capture = TSharkCapture("5")
windows = CausalWindowManager(window_size=1.0)
extractor = FeatureExtractor(window_size=1.0)
adapter = FeatureAdapter(ml_dir="ml")
aggregator = SchemaFeatureAggregator()

count = 0
checked = 0
started = time.monotonic()

print("Capturing for up to 12 seconds. Generate normal traffic.")

try:
    for packet in capture.packets():
        count += 1

        if count == 1:
            print("\nFirst packet normalized keys:")
            print(sorted(packet.keys()))
            print("\nActual TShark layer keys:")
            layers = packet.get("layers", {})
            for layer, data in layers.items():
                if isinstance(data, dict) and data:
                    print(layer, sorted(data.keys()))

        completed = windows.add_packet(packet)

        for window in completed:
            packets = window.get("packets", [])
            if not packets:
                continue

            features = extractor.extract_window_features(packets)
            features.update(aggregator.aggregate(packets))

            missing = []
            invalid = []

            for name in adapter.binary_features:
                value = features.get(name)
                if value is None:
                    missing.append(name)
                    continue
                try:
                    number = float(value)
                    if number != number or abs(number) == float("inf"):
                        invalid.append(name)
                except (TypeError, ValueError, OverflowError):
                    invalid.append(name)

            checked += 1
            print(
                f"\nWindow {checked}: packets={len(packets)}, "
                f"features={len(features)}, "
                f"missing={len(missing)}, invalid={len(invalid)}"
            )
            print("Missing:", missing)
            print("Invalid:", invalid)

            try:
                result = adapter.adapt_for_binary(features)
                print("STRICT VALIDATION PASSED:", result.shape)
            except Exception as exc:
                print("STRICT VALIDATION FAILED:", exc)

        if time.monotonic() - started >= 12:
            break

except KeyboardInterrupt:
    print("Capture interrupted.")

except Exception as exc:
    print("CAPTURE ERROR:", type(exc).__name__, str(exc))

finally:
    capture.stop()

print("\nTotal packets:", count)
print("Completed windows checked:", checked)
