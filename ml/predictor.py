"""
CogniFi ML inference module.

Loads the frozen LightGBM champion model and production schema
for real-time threat prediction.
"""

import json
from pathlib import Path

import joblib
import pandas as pd


class CognifiThreatPredictor:
    """Run threat predictions using the frozen CogniFi ML model."""

    def __init__(self, model_path=None, schema_path=None):
        base_dir = Path(__file__).resolve().parent / "models"

        self.model_path = Path(
            model_path or base_dir / "cognifi_final_champion_328_model.joblib"
        )
        self.schema_path = Path(
            schema_path or base_dir / "cognifi_production_schema.json"
        )

        self.model = joblib.load(self.model_path)

        with open(self.schema_path, "r", encoding="utf-8") as file:
            self.schema = json.load(file)

        self.feature_names = [
            feature["name"] for feature in self.schema["features"]
        ]

        self.threshold = float(
            self.schema.get("decision_threshold", 0.50)
        )

    def predict_window(self, features):
        """
        Predict whether one or more feature windows represent an attack.

        Parameters
        ----------
        features : dict, pandas.Series, or pandas.DataFrame
            Feature values matching the production schema.

        Returns
        -------
        dict or list[dict]
            Attack probability, normal probability, threat decision,
            confidence, and decision threshold.
        """

        if isinstance(features, dict):
            missing = [
                name for name in self.feature_names
                if name not in features
            ]

            if missing:
                raise ValueError(
                    f"Missing required features: {missing}"
                )

            df = pd.DataFrame(
                [[features[name] for name in self.feature_names]],
                columns=self.feature_names,
            )

        elif isinstance(features, pd.Series):
            missing = [
                name for name in self.feature_names
                if name not in features.index
            ]

            if missing:
                raise ValueError(
                    f"Missing required features: {missing}"
                )

            df = pd.DataFrame(
                [features[self.feature_names].values],
                columns=self.feature_names,
            )

        elif isinstance(features, pd.DataFrame):
            missing = [
                name for name in self.feature_names
                if name not in features.columns
            ]

            if missing:
                raise ValueError(
                    f"Missing required features: {missing}"
                )

            df = features[self.feature_names].copy()

        else:
            raise ValueError(
                "Input must be a dict, pandas Series, or pandas DataFrame"
            )

        probabilities = self.model.predict_proba(df)[:, 1]

        predictions = []

        for probability in probabilities:
            probability = float(probability)

            predictions.append(
                {
                    "is_threat": bool(
                        probability >= self.threshold
                    ),
                    "attack_probability": round(
                        probability, 4
                    ),
                    "normal_probability": round(
                        1.0 - probability, 4
                    ),
                    "confidence": round(
                        abs(probability - 0.5) * 2, 4
                    ),
                    "decision_threshold": self.threshold,
                }
            )

        return predictions[0] if len(predictions) == 1 else predictions
