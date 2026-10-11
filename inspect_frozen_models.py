import json
import joblib
from pathlib import Path

root = Path("ml")

for kind, schema_file, model_file in [
    ("binary", "schemas/binary_feature_schema.json",
     "models/binary_model.joblib"),
    ("multiclass", "schemas/multiclass_feature_schema.json",
     "models/multiclass_model.joblib"),
]:
    print(f"\n===== {kind.upper()} =====")

    schema = json.loads((root / schema_file).read_text(encoding="utf-8"))
    features = schema.get("feature_order", schema.get("features", []))
    model = joblib.load(root / model_file)

    print("Schema feature count:", len(features))
    print("Model type:", type(model).__name__)
    print("Model n_features_in_:", getattr(model, "n_features_in_", None))
    print("Model feature_names_in_:",
          list(getattr(model, "feature_names_in_", []))[:100])

    if hasattr(model, "get_params"):
        print("Model parameters:", model.get_params(deep=False))

    if hasattr(model, "steps"):
        print("Pipeline steps:", [name for name, _ in model.steps])

    print("First 10 schema features:", features[:10])

medians_path = root / "preprocessing/binary_train_medians.joblib"
medians = joblib.load(medians_path)
print("\n===== BINARY MEDIANS =====")
print("Type:", type(medians).__name__)
print("Count:", len(medians))
print("First 10:", list(medians.items())[:10]
      if isinstance(medians, dict) else str(medians)[:500])
