
import json
import os

import numpy as np
import pandas as pd


class FeatureAdapter:
    def __init__(self, ml_dir="ml"):
        self.ml_dir = os.path.abspath(ml_dir)

        # Load the frozen binary feature schema.
        binary_schema_path = os.path.join(
            self.ml_dir,
            "schemas",
            "binary_feature_schema.json",
        )

        with open(binary_schema_path, encoding="utf-8") as f:
            self.binary_schema = json.load(f)
            self.binary_features = self.binary_schema["feature_order"]

        # Load the frozen multiclass feature schema.
        multiclass_schema_path = os.path.join(
            self.ml_dir,
            "schemas",
            "multiclass_feature_schema.json",
        )

        with open(multiclass_schema_path, encoding="utf-8") as f:
            self.multiclass_schema = json.load(f)
            self.multiclass_features = self.multiclass_schema.get(
                "feature_order",
                self.multiclass_schema.get("features", []),
            )

        # Validate the schema definitions without modifying them.
        if not self.binary_features:
            raise ValueError(
                "Binary feature schema contains no features."
            )

        if not self.multiclass_features:
            raise ValueError(
                "Multiclass feature schema contains no features."
            )

        if len(set(self.binary_features)) != len(self.binary_features):
            raise ValueError(
                "Binary feature schema contains duplicate feature names."
            )

        if len(set(self.multiclass_features)) != len(
            self.multiclass_features
        ):
            raise ValueError(
                "Multiclass feature schema contains duplicate feature names."
            )

    def _map_features(self, features, target_features):
        """
        Validate and arrange input features in the exact schema order.

        Missing, non-numeric, NaN, and infinite values are rejected.
        This method does not impute values or change the frozen schemas.
        """
        if not isinstance(features, dict):
            raise TypeError(
                "Features must be provided as a dictionary."
            )

        missing = []

        for name in target_features:
            value = features.get(name)

            if value is None:
                missing.append(name)
                continue

            try:
                numeric = float(value)
            except (TypeError, ValueError, OverflowError):
                missing.append(name)
                continue

            if not np.isfinite(numeric):
                missing.append(name)

        if missing:
            preview = ", ".join(missing[:10])

            if len(missing) > 10:
                preview += (
                    f", ... and {len(missing) - 10} more"
                )

            raise ValueError(
                f"Cannot run inference: {len(missing)} model features "
                f"are missing or invalid: {preview}"
            )

        # Preserve the exact feature order specified by the schema.
        row = {
            name: float(features[name])
            for name in target_features
        }

        return pd.DataFrame(
            [row],
            columns=target_features,
            dtype=np.float64,
        )

    def adapt_for_binary(self, features):
        """Prepare input for the frozen 82-feature binary model."""
        return self._map_features(
            features,
            self.binary_features,
        )

    def adapt_for_multiclass(self, features):
        """Prepare input for the frozen 81-feature multiclass model."""
        return self._map_features(
            features,
            self.multiclass_features,
        )
