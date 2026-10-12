import sys
from pathlib import Path

BACKEND_DIR = (
    Path(__file__)
    .resolve()
    .parents[1]
)

sys.path.insert( 0, str(BACKEND_DIR) )

from risk_engine import RiskEngine
# No behavioral baseline yet.
engine = RiskEngine()

def binary_result(
    probability,
    is_threat=None
):

    threshold = 0.09

    if is_threat is None:
        is_threat = (
            probability >= threshold
        )

    return {
        "is_threat": is_threat,
        "attack_probability": probability,
        "normal_probability": (
            1.0 - probability
        ),
        "confidence": (
            probability
            if is_threat
            else 1.0 - probability
        ),
        "threshold": threshold,
    }

# ============================================================
# ML risk transformation
# ============================================================
def test_ml_zero_probability():
    result = (
        RiskEngine.calculate_ml_risk(
            binary_result(0.0)
        )
    )
    assert result == 0.0

def test_ml_below_threshold():
    result = (
        RiskEngine.calculate_ml_risk(
            binary_result(0.05)
        )
    )
    assert 0 < result < 30

def test_ml_at_threshold():
    result = (
        RiskEngine.calculate_ml_risk(
            binary_result(0.09)
        )
    )
    assert result == 30.0

def test_ml_probability_one():
    result = (
        RiskEngine.calculate_ml_risk(
            binary_result(1.0)
        )
    )
    assert result == 100.0

# ============================================================
# Preliminary assessment
# ============================================================
def test_preliminary_wpa3():
    result = engine.analyze(
        mode="preliminary",
        security="WPA3"
    )
    assert result["risk_score"] == 0.0
    assert result["trust_score"] == 30.0
    assert result["status"] == "Unverified"
    assert result["assessment"] == "preliminary"
    assert result["evidence_completeness"] == 0.30
    assert result["factors"]["ml"] is None
    assert result["factors"]["behavior"] is None
    assert result[ "factors" ]["static"] == 0.0

# ============================================================
# Binary ML + static evidence
# ============================================================
def test_partial_live_normal():
    ml_result = {
        "binary": binary_result( 0.01 ),
        "multiclass": None,
    }
    result = engine.analyze(
        mode="live",
        ml_result=ml_result,
        security="WPA3",
    )
    assert (
        result["risk_score"]
        is not None
    )
    assert (
        result[ "evidence_completeness" ] == 0.75
    )
    assert (
        result["factors"]["ml"] < 30
    )
    assert (
        result["factors"]["behavior"]
        is None
    )

# ============================================================
# High-confidence threat
# ============================================================
def test_high_probability_threat():
    ml_result = {
        "binary": binary_result( 0.95 ),
        "multiclass": {
            "predicted_class": "Evil_Twin",
            "class_id": 5,
            "confidence": 0.97,
            "class_probabilities": {},
        },
    }
    result = engine.analyze(
        mode="live",
        ml_result=ml_result,
        security="Open",
    )
    assert (
        result["risk_score"] >= 70
    )
    assert (
        result["status"] == "Risky"
    )
    assert (
        result["attack"]["type"] == "Evil_Twin"
    )
    assert (
        result["attack"]["confidence"] == 0.97
    )

# ============================================================
# No fabricated attack type
# ============================================================
def test_binary_threat_without_multiclass():
    ml_result = {
        "binary": binary_result( 0.70 ),
        "multiclass": None,
    }
    result = engine.analyze(
        mode="live",
        ml_result=ml_result,
        security="WPA2",
    )
    assert (
        result["attack"]["type"]
        is None
    )
    assert (
        result["attack"]["confidence"]
        is None
    )

# ============================================================
# No evidence
# ============================================================
def test_missing_all_evidence():
    result = engine.analyze(
        mode="live",
        ml_result=None,
        behavioral_features=None,
        security=None,
    )
    assert (
        result["risk_score"]
        is None
    )
    assert (
        result["trust_score"]
        is None
    )
    assert (
        result["status"]
        == "Unknown"
    )
    assert (
        result[ "evidence_completeness" ] == 0.0
    )

# ============================================================
# Invalid mode
# ============================================================
def test_invalid_mode():
    try:
        engine.analyze(
            mode="wrong-mode"
        )
        assert False
    except ValueError:
        assert True