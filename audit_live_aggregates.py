
import json
from pathlib import Path

from backend.capture.adapter import TSharkCapture
from backend.capture.schema_aggregator import aggregate_schema_features
from backend.capture.feature_engineering import WindowFeatureEngineer

ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "ml" / "schemas" / "multiclass_feature_schema.json"

schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
expected = schema.get("feature_order", schema.get("features", []))

interface = input('TShark interface (Enter for "5"): ').strip() or "5"
limit = 200
packets = []

print(f"Capturing up to {limit} packets...")
try:
    for packet in TSharkCapture(interface=interface).packets():
        packets.append(packet)
        if len(packets) >= limit:
            break
except KeyboardInterrupt:
    print("Capture interrupted.")

if not packets:
    raise SystemExit("No packets captured.")

aggregated = aggregate_schema_features(packets)
engineered = WindowFeatureEngineer().extract(packets)
combined = {**aggregated, **engineered}

print(f"\nPackets captured: {len(packets)}")
print(f"Aggregate output keys: {len(aggregated)}")
print(f"Behavior/engineered output keys: {len(engineered)}")
print(f"Combined keys: {len(combined)}")

print("\n--- REQUIRED MULTICLASS FEATURES ---")
for name in expected:
    value = combined.get(name, "<MISSING>")
    print(f"{name:46} {value!r}")

missing = [name for name in expected if name not in combined]
nulls = [name for name in expected if name in combined and combined[name] is None]

print("\n--- SUMMARY ---")
print(f"Required features: {len(expected)}")
print(f"Missing keys: {len(missing)}")
print(f"Present but None: {len(nulls)}")
print("Missing:", missing)
print("None:", nulls)
