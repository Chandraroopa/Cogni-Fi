import json
import os


class FeatureAvailabilityAnalyzer:
    """
    Analyzes which frozen ML features can currently be supplied
    by the packet/feature-engineering pipeline.

    This does NOT create ML values.

    It only reports:

        AVAILABLE
        UNAVAILABLE

    This is important because unavailable Wi-Fi/radiotap fields
    must not be silently replaced with fake values.
    """

    def __init__(self, ml_dir="ml"):

        self.ml_dir = os.path.abspath(
            ml_dir
        )

        # ---------------------------------------------------------
        # Binary schema
        # ---------------------------------------------------------

        binary_path = os.path.join(
            self.ml_dir,
            "schemas",
            "binary_feature_schema.json",
        )

        with open(
            binary_path,
            "r",
            encoding="utf-8",
        ) as file:

            binary_schema = json.load(
                file
            )

        self.binary_features = (
            binary_schema["feature_order"]
        )

        # ---------------------------------------------------------
        # Multiclass schema
        # ---------------------------------------------------------

        multiclass_path = os.path.join(
            self.ml_dir,
            "schemas",
            "multiclass_feature_schema.json",
        )

        with open(
            multiclass_path,
            "r",
            encoding="utf-8",
        ) as file:

            multiclass_schema = json.load(
                file
            )

        self.multiclass_features = (
            multiclass_schema.get(
                "feature_order",
                multiclass_schema.get(
                    "features",
                    [],
                ),
            )
        )

    # =============================================================
    # Analyze one feature dictionary
    # =============================================================

    @staticmethod
    def analyze(
        feature_names,
        available_features,
    ):

        available_features = set(
            available_features
        )

        available = []
        unavailable = []

        for feature in feature_names:

            if feature in available_features:

                available.append(
                    feature
                )

            else:

                unavailable.append(
                    feature
                )

        return {
            "expected": len(
                feature_names
            ),
            "available": len(
                available
            ),
            "unavailable": len(
                unavailable
            ),
            "available_features": available,
            "unavailable_features": unavailable,
        }

    # =============================================================
    # Binary report
    # =============================================================

    def binary_report(
        self,
        available_features,
    ):

        return self.analyze(
            self.binary_features,
            available_features,
        )

    # =============================================================
    # Multiclass report
    # =============================================================

    def multiclass_report(
        self,
        available_features,
    ):

        return self.analyze(
            self.multiclass_features,
            available_features,
        )