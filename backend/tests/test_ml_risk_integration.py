import pytest

from ml.inference.predictor import predict_one, load_predictor
from backend.risk_engine import RiskEngine


def test_actual_predictor_to_risk_engine():
    # Load the actual trained 30-feature model.
    _, feature_names = load_predictor()

    assert len(feature_names) == 30

    # Synthetic software-test input, NOT real Wi-Fi traffic.
    features = {name: 0.0 for name in feature_names}

    # Person 1's actual ML model performs inference.
    ml_prediction = predict_one(features)

    # Your Risk Engine consumes the model's actual output.
    risk_result = RiskEngine().analyze(
        mode="live",
        ml_result=ml_prediction,
        behavioral_features=None,
        security=None,
    )

    # Verify the model-to-risk interface.
    assert risk_result["factors"]["ml"] is not None
    assert 0 <= risk_result["factors"]["ml"] <= 100

    assert risk_result["attack"]["type"] == (
        ml_prediction["predicted_class"]
        if ml_prediction["is_threat"]
        else None
    )

    assert risk_result["assessment"] == "partial"
    assert isinstance(risk_result["reasons"], list)
    assert isinstance(risk_result["recommendations"], list)
    assert "alert" in risk_result
