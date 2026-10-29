
import json
import math
import os
from numbers import Real


# Diagnostic metadata only. Never append these to the model vector.
WIFI_AVAILABILITY_NAMES = [
    "wifi_retry_available",
    "wifi_protected_available",
    "wifi_management_frames_available",
    "wifi_signal_available",
    "wifi_data_rate_available",
    "wifi_bssid_available",
]


class FeatureAvailabilityAnalyzer:
    """Report whether features have finite numeric values.

    Numeric presence does not prove that a feature has the correct
    training-time meaning or aggregation semantics.
    """

    def __init__(self, schema_path=None):
        if schema_path is None:
            project_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..")
            )
            schema_path = os.path.join(
                project_root, "ml", "schemas", "feature_schema.json"
            )

        with open(schema_path, "r", encoding="utf-8") as file:
            schema = json.load(file)

        self.multiclass_features = schema["features"]

        expected_count = schema["model_input_count"]
        if len(self.multiclass_features) != expected_count:
            raise ValueError(
                f"Schema declares {expected_count} model inputs but lists "
                f"{len(self.multiclass_features)} features"
            )

        if schema.get("availability_flags_are_model_inputs") is not False:
            raise ValueError(
                "Availability flags must remain diagnostic-only metadata"
            )

    @staticmethod
    def _is_valid_numeric(value):
        return (
            isinstance(value, Real)
            and not isinstance(value, bool)
            and math.isfinite(float(value))
        )

    @classmethod
    def analyze(cls, feature_names, feature_values):
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
            "unavailable_features": unavailable,
        }

    def multiclass_report(self, feature_values):
        return self.analyze(self.multiclass_features, feature_values)

    def wifi_diagnostic_report(self, feature_values):
        return self.analyze(WIFI_AVAILABILITY_NAMES, feature_values)
