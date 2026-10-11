import json
from pathlib import Path

from backend.capture.feature_window import FeatureExtractor

binary_path = Path("ml/schemas/binary_feature_schema.json")
multi_path = Path("ml/schemas/multiclass_feature_schema.json")

binary = json.loads(binary_path.read_text(encoding="utf-8"))["feature_order"]
multi_data = json.loads(multi_path.read_text(encoding="utf-8"))
multi = multi_data.get("feature_order", multi_data.get("features", []))

# Empty input is used only to inspect which keys the extractor emits.
sample = FeatureExtractor().extract_window_features([])

for name, schema in [("BINARY", binary), ("MULTICLASS", multi)]:
    present = [feature for feature in schema if feature in sample]
    missing = [feature for feature in schema if feature not in sample]

    print(f"\n{name}: {len(schema)} required features")
    print(f"Matching extractor keys: {len(present)}")
    print(f"Missing extractor keys: {len(missing)}")
    print("Matching:", present)
    print("Missing:", missing)

print("\nExtractor's operational feature keys:")
print(sorted(sample.keys()))
