
import json
import math
import unittest
from pathlib import Path

from backend.ml_service import MLInputError, ml_service


BASE_DIR = Path(__file__).resolve().parents[1] / "schemas"


def make_valid_features():
    with (BASE_DIR / "feature_schema.json").open(
        "r", encoding="utf-8"
    ) as file:
        schema = json.load(file)

    return {name: 0.0 for name in schema["features"]}


class TestMLService30(unittest.TestCase):
    def setUp(self):
        self.features = make_valid_features()

    def test_valid_input_returns_both_detection_outputs(self):
        result = ml_service.analyze(self.features)

        self.assertEqual(result["model_type"], "multiclass_30")
        self.assertEqual(result["model_features"], 30)
        self.assertIn(result["predicted_class"], ml_service.metadata()["classes"])
        self.assertIsInstance(result["is_threat"], bool)

        if result["predicted_class"] == "Normal":
            self.assertFalse(result["is_threat"])
            self.assertIsNone(result["threat_type"])
        else:
            self.assertTrue(result["is_threat"])
            self.assertEqual(
                result["threat_type"], result["predicted_class"]
            )

    def test_probabilities_are_consistent(self):
        result = ml_service.analyze(self.features)
        probabilities = result["class_probabilities"]

        self.assertTrue(
            math.isclose(sum(probabilities.values()), 1.0, abs_tol=1e-5)
        )
        self.assertTrue(
            math.isclose(
                result["normal_probability"],
                probabilities["Normal"],
                abs_tol=1e-5,
            )
        )

        expected_threat_probability = sum(
            probability
            for label, probability in probabilities.items()
            if label != "Normal"
        )
        self.assertTrue(
            math.isclose(
                result["threat_probability"],
                expected_threat_probability,
                abs_tol=1e-5,
            )
        )

    def test_extra_diagnostic_fields_are_ignored(self):
        features = self.features.copy()
        features.update({
            "radiotap_available": 0,
            "wifi_frame_metadata_available": 0,
        })

        result = ml_service.analyze(features)
        self.assertEqual(result["model_features"], 30)

    def test_missing_feature_is_rejected(self):
        features = self.features.copy()
        features.pop(next(iter(features)))

        with self.assertRaises(MLInputError):
            ml_service.analyze(features)

    def test_non_numeric_feature_is_rejected(self):
        features = self.features.copy()
        features["packet_count"] = "not-a-number"

        with self.assertRaises(MLInputError):
            ml_service.analyze(features)

    def test_boolean_feature_is_rejected(self):
        features = self.features.copy()
        features["packet_count"] = True

        with self.assertRaises(MLInputError):
            ml_service.analyze(features)

    def test_nan_and_infinity_are_rejected(self):
        for invalid_value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=invalid_value):
                features = self.features.copy()
                features["packet_count"] = invalid_value

                with self.assertRaises(MLInputError):
                    ml_service.analyze(features)

    def test_non_mapping_input_is_rejected(self):
        with self.assertRaises(MLInputError):
            ml_service.analyze(None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
