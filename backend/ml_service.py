"""Production service for Cogni-Fi's 30-feature multiclass model."""

from collections.abc import Mapping
from typing import Any

import math
import numpy as np
import pandas as pd

from ml.inference.predictor import load_predictor


class MLInputError(ValueError):
    """Raised when the live ML feature payload is invalid."""


class CognifiMLService:
    def __init__(self):
        # Load the model once, not for every captured window.
        self.model, self.feature_names = load_predictor()

        if len(self.feature_names) != 30:
            raise RuntimeError(
                f"Expected 30 features, got {len(self.feature_names)}."
            )

        if len(self.model.classes_) != 14:
            raise RuntimeError(
                f"Expected 14 classes, got {len(self.model.classes_)}."
            )

    def analyze(self, features: Mapping[str, Any]) -> dict:
        if not isinstance(features, Mapping):
            raise MLInputError("Features must be a dictionary.")

        missing = [
            name for name in self.feature_names
            if name not in features
        ]
        if missing:
            raise MLInputError(
                f"Missing model features: {missing}"
            )

        values = []
        for name in self.feature_names:
            value = features[name]

            if isinstance(value, (bool, np.bool_)):
                raise MLInputError(
                    f"Feature {name!r} must be numeric, not Boolean."
                )

            try:
                value = float(value)
            except (TypeError, ValueError, OverflowError) as exc:
                raise MLInputError(
                    f"Feature {name!r} is not numeric."
                ) from exc

            if not math.isfinite(value):
                raise MLInputError(
                    f"Feature {name!r} is not finite."
                )

            values.append(value)

        frame = pd.DataFrame(
            [values],
            columns=self.feature_names,
            dtype=np.float64,
        )

        probabilities = self.model.predict_proba(frame)[0]
        classes = [str(label) for label in self.model.classes_]

        if not np.isfinite(probabilities).all():
            raise RuntimeError("Model returned invalid probabilities.")

        if not np.isclose(probabilities.sum(), 1.0, atol=1e-5):
            raise RuntimeError("Model probabilities do not sum to 1.")

        class_probabilities = {
            label: float(probability)
            for label, probability in zip(classes, probabilities)
        }

        best_index = int(np.argmax(probabilities))
        predicted_class = classes[best_index]
        normal_probability = class_probabilities.get("Normal", 0.0)
        threat_probability = 1.0 - normal_probability

        return {
            "model_type": "multiclass_30",
            "predicted_class": predicted_class,
            "is_threat": predicted_class != "Normal",
            "threat_type": (
                predicted_class if predicted_class != "Normal" else None
            ),
            "confidence": float(probabilities[best_index]),
            "threat_probability": float(threat_probability),
            "normal_probability": float(normal_probability),
            "class_probabilities": class_probabilities,
            "model_features": len(self.feature_names),
        }

    def metadata(self) -> dict:
        return {
            "model_type": "multiclass_30",
            "feature_count": len(self.feature_names),
            "class_count": len(self.model.classes_),
            "classes": [str(label) for label in self.model.classes_],
        }


ml_service = CognifiMLService()


