"""Live detector backed by Cognifi's 30-feature, 14-class model."""

from ml.candidate_30.predictor_30 import (
    load_predictor,
    predict_one,
)
from backend.capture.feature_window import (
    FEATURE_NAMES,
    WIFI_AVAILABILITY_NAMES,
)


class LiveRiskDetector:
    def __init__(self):
        # Fail early if the candidate model or schema cannot load.
        self.model, self.model_features = load_predictor()

        if self.model_features != FEATURE_NAMES:
            raise ValueError(
                "Live extractor feature order does not match "
                "the candidate model schema."
            )

        if len(WIFI_AVAILABILITY_NAMES) != 6:
            raise ValueError(
                "Expected six diagnostic availability flags."
            )

    def analyze(self, features):
        if not isinstance(features, dict):
            raise ValueError("Features must be supplied as a dictionary.")

        missing = [
            name for name in FEATURE_NAMES
            if name not in features
        ]
        if missing:
            raise ValueError(
                f"Live feature window is missing required features: {missing}"
            )

        # Pass only the 30 model features.
        model_input = {
            name: features[name]
            for name in FEATURE_NAMES
        }

        result = predict_one(model_input)

        threat_probability = float(result["threat_probability"])
        risk_score = round(threat_probability * 100)

        # Provisional display bands only; not the final Trust/Risk Engine.
        if threat_probability >= 0.60:
            risk_level = "High"
        elif threat_probability >= 0.30:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        predicted_class = result["predicted_class"]
        reasons = [
            f"ML predicted class: {predicted_class}",
            f"Prediction confidence: {result['confidence']:.3f}",
            (
                "Threat likelihood is derived from the sum of "
                "non-Normal class probabilities."
            ),
        ]

        # Availability flags are returned for diagnostics only.
        availability = {
            name: bool(features.get(name, False))
            for name in WIFI_AVAILABILITY_NAMES
        }

        return {
            # Existing fields retained for backend/frontend compatibility.
            "risk_level": risk_level,
            "risk_score": risk_score,
            "reasons": reasons,

            # Explicit ML outputs.
            "predicted_class": predicted_class,
            "is_threat": bool(result["is_threat"]),
            "confidence": float(result["confidence"]),
            "threat_probability": threat_probability,
            "normal_probability": float(result["normal_probability"]),
            "class_probabilities": result["class_probabilities"],
            "top_3": result["top_3"],

            # These scores are provisional, not calibrated risk scores.
            "risk_score_basis": "provisional_non_normal_probability_percent",
            "risk_score_is_final_trust_score": False,

            "availability": availability,
        }