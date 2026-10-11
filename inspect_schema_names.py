import json

for path, key in [
    ("ml/schemas/binary_feature_schema.json", "feature_order"),
    ("ml/schemas/multiclass_feature_schema.json", "features"),
]:
    with open(path, encoding="utf-8") as f:
        schema = json.load(f)

    names = schema.get(key, schema.get("feature_order", []))
    print(f"\n{path}: {len(names)} features")
    for i, name in enumerate(names):
        print(f"{i:02d}: {name!r}")
