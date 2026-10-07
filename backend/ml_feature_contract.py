from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import math

from ml.predictor import CognifiPredictor


class MLFeatureContractError(ValueError):
    """Raised when an ML feature payload violates the frozen feature contract."""


class MLFeatureContract:
    """
    Strict validator for the frozen CogniFi ML feature contracts.

    Binary model:
        82 features

    Multiclass model:
        81 features

    The validator checks feature names, feature count, numeric
    convertibility, and finite numeric values. It does not modify
    the input payload and does not perform model inference.
    """

    def __init__(self, ml_dir: str | Path | None = None):
        if ml_dir is None:
            ml_dir = Path(__file__).resolve().parent.parent / "ml"

        self.ml_dir = Path(ml_dir).resolve()

        if not self.ml_dir.exists():
            raise FileNotFoundError(
                f"ML directory not found: {self.ml_dir}"
            )

        predictor = CognifiPredictor(self.ml_dir)

        self.binary_features = tuple(predictor.binary.features)
        self.multiclass_features = tuple(predictor.multiclass.features)

    @staticmethod
    def _check_numeric_convertibility(
        features: tuple[str, ...],
        payload: Mapping[str, Any],
    ) -> tuple[list[str], list[str]]:
        """
        Return:
            non_numeric: values that cannot be converted to float
            non_finite: values that become NaN/inf after conversion
        """

        non_numeric: list[str] = []
        non_finite: list[str] = []

        for feature in features:
            value = payload[feature]

            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                non_numeric.append(feature)
                continue

            if not math.isfinite(numeric_value):
                non_finite.append(feature)

        return non_numeric, non_finite

    @staticmethod
    def _validate(
        payload: Mapping[str, Any],
        features: tuple[str, ...],
        model_name: str,
    ) -> dict[str, Any]:

        if not isinstance(payload, Mapping):
            return {
                "valid": False,
                "model": model_name,
                "expected_feature_count": len(features),
                "received_feature_count": None,
                "missing_features": [],
                "extra_features": [],
                "non_numeric_features": [],
                "non_finite_features": [],
                "errors": ["Input must be a mapping/dictionary."],
            }

        expected = set(features)
        received = set(payload.keys())

        missing = sorted(expected - received)
        extra = sorted(received - expected)

        non_numeric: list[str] = []
        non_finite: list[str] = []

        if not missing:
            non_numeric, non_finite = MLFeatureContract._check_numeric_convertibility(
                features,
                payload,
            )

        errors: list[str] = []

        if missing:
            errors.append(
                f"Missing {len(missing)} required feature(s)."
            )

        if extra:
            errors.append(
                f"Received {len(extra)} unexpected feature(s)."
            )

        if len(payload) != len(features):
            errors.append(
                f"Expected exactly {len(features)} features; "
                f"received {len(payload)}."
            )

        if non_numeric:
            errors.append(
                f"{len(non_numeric)} feature(s) contain non-numeric values."
            )

        if non_finite:
            errors.append(
                f"{len(non_finite)} feature(s) contain NaN or infinity."
            )

        return {
            "valid": len(errors) == 0,
            "model": model_name,
            "expected_feature_count": len(features),
            "received_feature_count": len(payload),
            "missing_features": missing,
            "extra_features": extra,
            "non_numeric_features": non_numeric,
            "non_finite_features": non_finite,
            "errors": errors,
        }

    def validate_binary(
        self,
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Strictly validate a binary-model feature payload."""

        return self._validate(
            payload,
            self.binary_features,
            "binary",
        )

    def validate_multiclass(
        self,
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Strictly validate a multiclass-model feature payload."""

        return self._validate(
            payload,
            self.multiclass_features,
            "multiclass",
        )

    def require_binary(
        self,
        payload: Mapping[str, Any],
    ) -> None:
        """Raise if the binary feature payload is invalid."""

        result = self.validate_binary(payload)

        if not result["valid"]:
            raise MLFeatureContractError(
                "Invalid binary ML feature payload: "
                + " ".join(result["errors"])
            )

    def require_multiclass(
        self,
        payload: Mapping[str, Any],
    ) -> None:
        """Raise if the multiclass feature payload is invalid."""

        result = self.validate_multiclass(payload)

        if not result["valid"]:
            raise MLFeatureContractError(
                "Invalid multiclass ML feature payload: "
                + " ".join(result["errors"])
            )
