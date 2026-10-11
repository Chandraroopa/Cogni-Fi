import json
from backend.capture.adapter import TSharkCapture

binary = json.load(open("ml/schemas/binary_feature_schema.json", encoding="utf-8"))["feature_order"]
multi_schema = json.load(open("ml/schemas/multiclass_feature_schema.json", encoding="utf-8"))
multi = multi_schema.get("feature_order", multi_schema.get("features", []))

print("Starting capture on interface 5. Stop after the first packet with Ctrl+C.")
try:
    for packet in TSharkCapture("5").packets():
        for label, schema in [("Binary", binary), ("Multiclass", multi)]:
            available = [
                key for key in schema
                if packet.get(key) is not None
            ]
            print(f"\n{label}: {len(available)}/{len(schema)} fields available in this packet")
            print("Available:", available)
        break
except KeyboardInterrupt:
    print("Capture stopped.")
