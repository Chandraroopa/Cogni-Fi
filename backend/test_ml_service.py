
from __future__ import annotations

import json
import math
from pathlib import Path

from ml.candidate_30.predictor_30 import (
    load_predictor,
    predict_one,
)

SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent
    / "ml"
    / "candidate_30"
    / "feature_schema.json"
)


def assert_probability(value: float, name: str) -> None:
    assert math.isfinite(value), f"{name} is not finite"
    assert 0.0 <= value <= 1.0, f"{name} outside [0, 1]"


def main() -> None:
    print("=" * 65)
    print("COGNIFI 30-FEATURE ML SMOKE TEST")
    print("=" * 65)

    with SCHEMA_PATH.open("r", encoding="utf-8") as file:
        schema = json.load(file)

    feature_names = schema["features"]

    assert schema["model_input_count"] == 30
    assert schema["availability_flags_are_model_inputs"] is False
    assert len(feature_names) == 30

    model, loaded_features = load_predictor()

    assert loaded_features == feature_names
    assert model.n_features_in_ == 30
    assert len(model.classes_) == 14

    print("[PASS] Schema contains exactly 30 features")
    print("[PASS] Availability flags excluded from model inputs")
    print("[PASS] Model loaded with 14 classes")

    # Zero input checks software behavior only, not detection quality.
    test_features = {name: 0.0 for name in feature_names}
    result = predict_one(test_features)

    assert result["predicted_class"] in [str(c) for c in model.classes_]
    assert isinstance(result["is_threat"], bool)

    assert_probability(result["confidence"], "confidence")
    assert_probability(result["threat_probability"], "threat_probability")
    assert_probability(result["normal_probability"], "normal_probability")

    probabilities = result["class_probabilities"]
    assert len(probabilities) == 14
    assert abs(sum(probabilities.values()) - 1.0) < 1e-6

    assert abs(
        result["threat_probability"] + result["normal_probability"] - 1.0
    ) < 1e-6

    assert len(result["top_3"]) == 3
    assert result["is_threat"] == (result["predicted_class"] != "Normal")

    print("[PASS] Multiclass inference")
    print(f"       Predicted class: {result['predicted_class']}")
    print(f"       Threat detected: {result['is_threat']}")
    print(f"       Confidence: {result['confidence']:.6f}")
    print(f"       Threat probability: {result['threat_probability']:.6f}")
    print("[PASS] Class probabilities sum to 1")
    print("[PASS] Threat probability matches non-Normal class probabilities")
    print("[PASS] Top-three predictions returned")

    # Missing-feature rejection
    missing = dict(test_features)
    missing.pop(feature_names[0])

    try:
        predict_one(missing)
    except ValueError:
        print("[PASS] Missing feature rejected")
    else:
        raise AssertionError("Missing feature was not rejected")

    # Non-finite input rejection
    invalid = dict(test_features)
    invalid[feature_names[0]] = float("nan")

    try:
        predict_one(invalid)
    except ValueError:
        print("[PASS] NaN input rejected")
    else:
        raise AssertionError("NaN input was not rejected")

    print("=" * 65)
    print("ALL 30-FEATURE ML SMOKE TESTS PASSED")
    print("=" * 65)


if __name__ == "__main__":
    main()
