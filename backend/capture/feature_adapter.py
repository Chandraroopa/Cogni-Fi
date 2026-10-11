
import json
import os

import numpy as np
import pandas as pd


class FeatureAdapter:
    def __init__(self, ml_dir="ml"):
        self.ml_dir = os.path.abspath(ml_dir)

        with open(
            os.path.join(self.ml_dir, "schemas", "binary_feature_schema.json"),
            encoding="utf-8",
        ) as f:
            self.binary_schema = json.load(f)
            self.binary_features = self.binary_schema["feature_order"]

        with open(
            os.path.join(self.ml_dir, "schemas", "multiclass_feature_schema.json"),
            encoding="utf-8",
        ) as f:
            self.multiclass_schema = json.load(f)
            self.multiclass_features = self.multiclass_schema.get(
                "feature_order",
                self.multiclass_schema.get("features", []),
            )

    def _map_features(self, features, target_features):
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
                preview += f", ... and {len(missing) - 10} more"

            raise ValueError(
                f"Cannot run inference: {len(missing)} model features "
                f"are missing or invalid: {preview}"
            )

        row = {
            name: float(features[name])
            for name in target_features
        }

        return pd.DataFrame([row], columns=target_features)

    def adapt_for_binary(self, features):
        return self._map_features(features, self.binary_features)

    def adapt_for_multiclass(self, features):
        return self._map_features(features, self.multiclass_features)
