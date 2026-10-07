"""
CogniFi ML Service

Production adapter between the backend and the frozen CogniFi ML package.

Responsibilities:
- Validate ML feature inputs.
- Run binary threat detection.
- Run multiclass attack classification.
- Return ML evidence for the Trust/Risk Engine.

This module does NOT calculate the final trust/risk score.
"""

from pathlib import Path
from typing import Any, Dict, Mapping

from ml.predictor import CognifiPredictor


class MLInputError(ValueError):
    """Raised when the supplied ML feature input is invalid."""


class CognifiMLService:
    """
    Backend-facing service for the frozen CogniFi ML models.

    Binary model:
        82 features
        Normal / Threat
        Threshold = 0.09

    Multiclass model:
        81 features
        14 classes
    """

    def __init__(self, ml_dir: str | Path | None = None):
        if ml_dir is None:
            ml_dir = Path(__file__).resolve().parent.parent / "ml"

        self.ml_dir = Path(ml_dir).resolve()

        if not self.ml_dir.exists():
            raise FileNotFoundError(
                f"CogniFi ML directory not found: {self.ml_dir}"
            )

        self.predictor = CognifiPredictor(self.ml_dir)

        self.binary_features = list(
            self.predictor.binary.features
        )

        self.multiclass_features = list(
            self.predictor.multiclass.features
        )

        self.binary_threshold = float(
            self.predictor.binary.threshold
        )

        self.multiclass_classes = list(
            self.predictor.multiclass.classes
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_mapping(features: Mapping[str, Any]) -> None:
        if not isinstance(features, Mapping):
            raise MLInputError(
                "ML input must be a mapping/dictionary of feature names "
                "to values."
            )

    def validate_binary_input(
        self,
        features: Mapping[str, Any],
    ) -> Dict[str, Any]:

        self._validate_mapping(features)

        missing = [
            name
            for name in self.binary_features
            if name not in features
        ]

        if missing:
            raise MLInputError(
                "Binary ML input is missing required features: "
                + ", ".join(missing)
            )

        return {
            name: features[name]
            for name in self.binary_features
        }

    def validate_multiclass_input(
        self,
        features: Mapping[str, Any],
    ) -> Dict[str, Any]:

        self._validate_mapping(features)

        missing = [
            name
            for name in self.multiclass_features
            if name not in features
        ]

        if missing:
            raise MLInputError(
                "Multiclass ML input is missing required features: "
                + ", ".join(missing)
            )

        return {
            name: features[name]
            for name in self.multiclass_features
        }

    # ------------------------------------------------------------------
    # Binary detection
    # ------------------------------------------------------------------

    def predict_binary(
        self,
        features: Mapping[str, Any],
    ) -> Dict[str, Any]:

        prepared = self.validate_binary_input(features)

        result = self.predictor.binary.predict(prepared)

        return {
            "is_threat": bool(result["is_threat"]),
            "attack_probability": float(
                result["attack_probability"]
            ),
            "normal_probability": float(
                result["normal_probability"]
            ),
            "confidence": float(
                result["confidence"]
            ),
            "threshold": float(
                result["threshold"]
            ),
        }

    # ------------------------------------------------------------------
    # Multiclass classification
    # ------------------------------------------------------------------

    def predict_multiclass(
        self,
        features: Mapping[str, Any],
    ) -> Dict[str, Any]:

        prepared = self.validate_multiclass_input(features)

        result = self.predictor.multiclass.predict(prepared)

        return {
            "predicted_class": result["predicted_class"],
            "class_id": int(result["class_id"]),
            "confidence": float(result["confidence"]),
            "class_probabilities": {
                name: float(probability)
                for name, probability
                in result["class_probabilities"].items()
            },
        }

    # ------------------------------------------------------------------
    # Combined prediction
    # ------------------------------------------------------------------

    def analyze(
        self,
        binary_features: Mapping[str, Any],
        multiclass_features: Mapping[str, Any] | None = None,
    ) -> Dict[str, Any]:

        binary_result = self.predict_binary(binary_features)

        multiclass_result = None

        # Only classify attack type when the binary detector
        # identifies the window as a threat.
        if binary_result["is_threat"]:

            if multiclass_features is None:
                raise MLInputError(
                    "Multiclass features are required when "
                    "binary detection identifies a threat."
                )

            multiclass_result = self.predict_multiclass(
                multiclass_features
            )

        return {
            "binary": binary_result,
            "multiclass": multiclass_result,
        }

    # ------------------------------------------------------------------
    # Metadata / health information
    # ------------------------------------------------------------------

    def metadata(self) -> Dict[str, Any]:
        return {
            "binary": {
                "feature_count": len(self.binary_features),
                "threshold": self.binary_threshold,
                "classes": ["Normal", "Threat"],
            },
            "multiclass": {
                "feature_count": len(self.multiclass_features),
                "class_count": len(self.multiclass_classes),
                "classes": self.multiclass_classes,
            },
        }


# Singleton-style service for backend use.
# Models are loaded once instead of once per request.
ml_service = CognifiMLService()


if __name__ == "__main__":
    service = CognifiMLService()

    print("=" * 70)
    print("COGNIFI ML SERVICE")
    print("=" * 70)

    metadata = service.metadata()

    print("\nBinary:")
    print(
        "  Features :",
        metadata["binary"]["feature_count"]
    )
    print(
        "  Threshold:",
        metadata["binary"]["threshold"]
    )

    print("\nMulticlass:")
    print(
        "  Features :",
        metadata["multiclass"]["feature_count"]
    )
    print(
        "  Classes  :",
        metadata["multiclass"]["class_count"]
    )

    for index, name in enumerate(
        metadata["multiclass"]["classes"]
    ):
        print(f"  {index:2d} -> {name}")

    print("\n" + "=" * 70)
    print("ML SERVICE: READY")
    print("=" * 70)
