from __future__ import annotations

import math

from backend.ml_feature_contract import MLFeatureContract
from backend.ml_service import CognifiMLService


def assert_probability(value: float, name: str) -> None:
    assert math.isfinite(value), f"{name} is not finite"
    assert 0.0 <= value <= 1.0, f"{name} is outside [0, 1]"


def main() -> None:
    print("=" * 70)
    print("CogniFi ML HANDOFF SMOKE TEST")
    print("=" * 70)

    service = CognifiMLService()
    contract = MLFeatureContract()

    # ---------------------------------------------------------------
    # 1. Frozen schema checks
    # ---------------------------------------------------------------
    assert len(service.binary_features) == 82
    assert len(service.multiclass_features) == 81

    assert len(contract.binary_features) == 82
    assert len(contract.multiclass_features) == 81

    print("[PASS] Binary schema: 82 features")
    print("[PASS] Multiclass schema: 81 features")
    print(f"[PASS] Binary threshold: {service.binary_threshold}")
    print(f"[PASS] Multiclass classes: {len(service.multiclass_classes)}")

    # ---------------------------------------------------------------
    # 2. Build deterministic test payloads
    #
    # Use zero-valued feature vectors because the purpose of this
    # script is to verify loading, validation, and inference—not to
    # evaluate model accuracy.
    # ---------------------------------------------------------------
    binary_input = {
        feature: 0.0
        for feature in service.binary_features
    }

    multiclass_input = {
        feature: 0.0
        for feature in service.multiclass_features
    }

    # ---------------------------------------------------------------
    # 3. Contract validation
    # ---------------------------------------------------------------
    binary_validation = contract.validate_binary(binary_input)
    multiclass_validation = contract.validate_multiclass(multiclass_input)

    assert binary_validation["valid"], binary_validation
    assert multiclass_validation["valid"], multiclass_validation

    print("[PASS] Binary feature contract validation")
    print("[PASS] Multiclass feature contract validation")

    # ---------------------------------------------------------------
    # 4. Binary inference
    # ---------------------------------------------------------------
    binary_result = service.predict_binary(binary_input)

    assert isinstance(binary_result["is_threat"], bool)

    attack_probability = float(binary_result["attack_probability"])
    normal_probability = float(binary_result["normal_probability"])
    confidence = float(binary_result["confidence"])
    threshold = float(binary_result["threshold"])

    assert_probability(attack_probability, "attack_probability")
    assert_probability(normal_probability, "normal_probability")
    assert_probability(confidence, "confidence")

    assert abs(
        attack_probability + normal_probability - 1.0
    ) < 1e-6

    assert threshold == 0.09

    print("[PASS] Binary inference")
    print(f"       is_threat: {binary_result['is_threat']}")
    print(f"       attack_probability: {attack_probability:.6f}")
    print(f"       normal_probability: {normal_probability:.6f}")
    print(f"       confidence: {confidence:.6f}")

    # ---------------------------------------------------------------
    # 5. Multiclass inference
    # ---------------------------------------------------------------
    multiclass_result = service.predict_multiclass(multiclass_input)

    predicted_class = multiclass_result["predicted_class"]
    class_id = int(multiclass_result["class_id"])
    multiclass_confidence = float(multiclass_result["confidence"])
    probabilities = multiclass_result["class_probabilities"]

    assert predicted_class in service.multiclass_classes
    assert 0 <= class_id < len(service.multiclass_classes)

    assert_probability(
        multiclass_confidence,
        "multiclass confidence",
    )

    probability_values = [
        float(value)
        for value in probabilities.values()
    ]

    assert probability_values
    assert all(
        0.0 <= value <= 1.0
        for value in probability_values
    )

    assert abs(sum(probability_values) - 1.0) < 1e-6

    print("[PASS] Multiclass inference")
    print(f"       predicted_class: {predicted_class}")
    print(f"       class_id: {class_id}")
    print(f"       confidence: {multiclass_confidence:.6f}")

    # ---------------------------------------------------------------
    # 6. Invalid payload checks
    # ---------------------------------------------------------------

    # Missing feature
    invalid_missing = dict(binary_input)
    invalid_missing.pop(service.binary_features[0])

    result = contract.validate_binary(invalid_missing)

    assert result["valid"] is False
    assert service.binary_features[0] in result["missing_features"]

    print("[PASS] Missing binary feature rejected")

    # Extra feature
    invalid_extra = dict(binary_input)
    invalid_extra["unexpected_feature"] = 123.0

    result = contract.validate_binary(invalid_extra)

    assert result["valid"] is False
    assert "unexpected_feature" in result["extra_features"]

    print("[PASS] Extra binary feature rejected")

    # Non-numeric value
    invalid_type = dict(binary_input)
    invalid_type[service.binary_features[0]] = "not-a-number"

    result = contract.validate_binary(invalid_type)

    assert result["valid"] is False
    assert service.binary_features[0] in result["non_numeric_features"]

    print("[PASS] Non-numeric binary feature rejected")

    # NaN
    invalid_nan = dict(binary_input)
    invalid_nan[service.binary_features[0]] = float("nan")

    result = contract.validate_binary(invalid_nan)

    assert result["valid"] is False
    assert service.binary_features[0] in result["non_finite_features"]

    print("[PASS] NaN binary feature rejected")

    # Infinity
    invalid_inf = dict(binary_input)
    invalid_inf[service.binary_features[0]] = float("inf")

    result = contract.validate_binary(invalid_inf)

    assert result["valid"] is False
    assert service.binary_features[0] in result["non_finite_features"]

    print("[PASS] Infinity binary feature rejected")

    # ---------------------------------------------------------------
    # Final
    # ---------------------------------------------------------------
    print("=" * 70)
    print("ALL ML HANDOFF SMOKE TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
