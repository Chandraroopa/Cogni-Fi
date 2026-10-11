
from backend.capture.adapter import TSharkCapture
import json
from numbers import Real
import math

with open("ml/schemas/binary_feature_schema.json", encoding="utf-8") as f:
    schema = json.load(f)

expected = schema["feature_order"]
capture = TSharkCapture(interface="5")
counts = {name: 0 for name in expected}
layers_seen = set()
packets_seen = 0

try:
    for packet in capture.packets():
        packets_seen += 1
        layers = packet.get("layers", {})
        layers_seen.update(layers.keys())

        for name in expected:
            value = packet.get(name)
            if (
                isinstance(value, Real)
                and not isinstance(value, bool)
                and math.isfinite(float(value))
            ):
                counts[name] += 1

        if packets_seen >= 30:
            break
finally:
    capture.stop()

print(f"\nPackets inspected: {packets_seen}")
print("Observed layers:", sorted(layers_seen))
print("\nSchema feature availability:")
for name in expected:
    print(f"{name}: {counts[name]}/{packets_seen}")

print(
    "\nFeatures observed at least once:",
    sum(count > 0 for count in counts.values()),
    "/",
    len(expected),
)
