
import json
from pathlib import Path

from ml.inference.predictor import load_predictor


ML_DIR = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ML_DIR / "schemas"
EVALUATION_DIR = ML_DIR / "evaluation"


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main():
    model, feature_names = load_predictor()

    schema = read_json(SCHEMA_DIR / "feature_schema.json")
    mapping = read_json(SCHEMA_DIR / "class_mapping.json")
    metrics = read_json(EVALUATION_DIR / "evaluation_metrics.json")

    expected_features = schema["features"]
    if expected_features and isinstance(expected_features[0], dict):
        expected_features = [item["name"] for item in expected_features]

    # Verify the exact model input contract.
    assert len(feature_names) == 30, (
        f"Expected 30 model features, found {len(feature_names)}"
    )
    assert feature_names == expected_features, (
        "Predictor feature order differs from the schema."
    )
    assert len(set(feature_names)) == 30, "Duplicate feature names detected."
    assert schema["model_input_count"] == 30
    assert schema["availability_flags_are_model_inputs"] is False

    # Verify class labels and their model order.
    model_classes = [str(label) for label in model.classes_]
    expected_mapping = {
        str(index): label for index, label in enumerate(model_classes)
    }

    assert mapping == expected_mapping, (
        "Class mapping does not match the model's class order."
    )
    assert len(model_classes) == 14, (
        f"Expected 14 classes, found {len(model_classes)}"
    )
    assert "Normal" in model_classes, "'Normal' class is missing."

    # Verify the saved offline evaluation report.
    assert metrics["input_feature_count"] == 30
    assert metrics["class_count"] == 14
    assert metrics["heldout_windows"] > 0
    assert metrics["live_inference_verified"] is False, (
        "Review the live-verification status before changing it."
    )

    print("PASS: feature count and exact feature order")
    print("PASS: unique feature names")
    print("PASS: availability flags excluded from model inputs")
    print("PASS: all 14 class labels and their mapping order")
    print("PASS: evaluation report consistency")
    print(f"Offline held-out accuracy: {metrics['accuracy']:.2%}")
    print(f"Offline macro-F1: {metrics['macro_f1']:.2%}")
    print("Status: candidate; live integration remains unverified.")


if __name__ == "__main__":
    main()
