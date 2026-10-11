import unittest

from backend.capture.feature_adapter import FeatureAdapter


class TestFeatureAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = FeatureAdapter(ml_dir="ml")

        # Deliberately incomplete input: missing model features must
        # be rejected rather than filled with fabricated values.
        self.sample_base_features = {
            "packet_count": 25.0,
            "byte_count": 5000.0,
            "frame.len": 200.0,
            "radiotap.channel.freq": 2412.0,
            "wlan.duration": 0.0,
            "wlan.fc.retry": 0.0,
            "tcp.ack": 12345.0,
            "tcp.dstport": 443.0,
            "tcp.seq": 67890.0,
            "tcp.srcport": 54321.0,
            "udp.dstport": 53.0,
            "udp.srcport": 1234.0,
            "udp.length": 64.0,
        }

    def test_binary_rejects_missing_features(self):
        with self.assertRaisesRegex(ValueError, "missing or invalid"):
            self.adapter.adapt_for_binary(self.sample_base_features)

    def test_multiclass_rejects_missing_features(self):
        with self.assertRaisesRegex(ValueError, "missing or invalid"):
            self.adapter.adapt_for_multiclass(self.sample_base_features)

    def test_binary_schema_has_82_features(self):
        self.assertEqual(len(self.adapter.binary_features), 82)

    def test_multiclass_schema_has_81_features(self):
        self.assertEqual(len(self.adapter.multiclass_features), 81)

    def test_binary_rejects_nan(self):
        features = {
            feature: 1.0 for feature in self.adapter.binary_features
        }
        features[self.adapter.binary_features[0]] = float("nan")

        with self.assertRaisesRegex(ValueError, "missing or invalid"):
            self.adapter.adapt_for_binary(features)

    def test_binary_rejects_infinity(self):
        features = {
            feature: 1.0 for feature in self.adapter.binary_features
        }
        features[self.adapter.binary_features[0]] = float("inf")

        with self.assertRaisesRegex(ValueError, "missing or invalid"):
            self.adapter.adapt_for_binary(features)

    def test_binary_preserves_feature_order(self):
        features = {
            feature: float(index)
            for index, feature in enumerate(self.adapter.binary_features)
        }

        result = self.adapter.adapt_for_binary(features)

        self.assertEqual(
            list(result.columns),
            self.adapter.binary_features,
        )
        self.assertEqual(result.shape, (1, 82))


if __name__ == "__main__":
    unittest.main()
