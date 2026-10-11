
import json
import math
import os
from numbers import Real


class FeatureAvailabilityAnalyzer:
    """
    Reports whether frozen ML features have valid numeric values.

    This checks value availability only. It does not establish that
    a value has the correct training-time meaning or distribution.
    It never invents feature values.
    """

    def __init__(self, ml_dir="ml"):
        self.ml_dir = os.path.abspath(ml_dir)

        binary_path = os.path.join(
            self.ml_dir,
            "schemas",
            "binary_feature_schema.json",
        )
        multiclass_path = os.path.join(
            self.ml_dir,
            "schemas",
            "multiclass_feature_schema.json",
        )

        with open(binary_path, "r", encoding="utf-8") as file:
            binary_schema = json.load(file)

        with open(multiclass_path, "r", encoding="utf-8") as file:
            multiclass_schema = json.load(file)

        self.binary_features = binary_schema["feature_order"]
        self.multiclass_features = multiclass_schema.get(
            "feature_order",
            multiclass_schema.get("features", []),
        )

    @staticmethod
    def _is_valid_numeric(value):
        # bool is a subclass of int, but is not accepted as a feature value.
        return (
            isinstance(value, Real)
            and not isinstance(value, bool)
            and math.isfinite(float(value))
        )

    @classmethod
    def analyze(cls, feature_names, feature_values):
        """
        feature_values must be a mapping: feature name -> actual value.
        Missing, None, non-numeric, NaN and infinite values are unavailable.
        """
        available = []
        unavailable = []

        for name in feature_names:
            value = feature_values.get(name)

            if cls._is_valid_numeric(value):
                available.append(name)
            else:
                unavailable.append(name)

        return {
            "expected": len(feature_names),
            "available": len(available),
            "unavailable": len(unavailable),
            "available_features": available,
            "unavailable_features": unavailable,
        }

    def binary_report(self, feature_values):
        return self.analyze(self.binary_features, feature_values)

    def multiclass_report(self, feature_values):
        return self.analyze(self.multiclass_features, feature_values)
