
import math
import unittest

from backend.capture.feature_engineering import (
    WindowFeatureEngineer,
)


class TestFeatureEngineeringSafety(unittest.TestCase):

    def setUp(self):
        self.engineer = WindowFeatureEngineer()

    def test_empty_input_returns_empty_dict(self):
        self.assertEqual(self.engineer.extract([]), {})

    def test_missing_wifi_fields_are_not_claimed_as_available(self):
        packets = [
            {
                "timestamp": 100.0,
                "frame.len": 100,
                "source": "A",
                "destination": "B",
            },
            {
                "timestamp": 100.5,
                "frame.len": 200,
                "source": "B",
                "destination": "A",
            },
        ]

        result = self.engineer.extract(packets)

        # These are current implementation outputs, not proof
        # that the corresponding Wi-Fi measurements exist.
        self.assertEqual(result["packet_count"], 2.0)
        self.assertEqual(result["byte_count"], 300.0)

        # The availability issue is intentionally documented here:
        # the existing schema does not yet expose availability flags.
        self.assertIn("retry_rate", result)
        self.assertIn("signal_mean", result)
        self.assertIn("data_rate_mean", result)

    def test_valid_zero_tcp_sequence_is_not_a_missing_value(self):
        packets = [
            {
                "timestamp": 1.0,
                "source": "A",
                "destination": "B",
                "tcp.srcport": 1234,
                "tcp.dstport": 80,
                "tcp.seq": 0,
            },
            {
                "timestamp": 2.0,
                "source": "A",
                "destination": "B",
                "tcp.srcport": 1234,
                "tcp.dstport": 80,
                "tcp.seq": 10,
            },
        ]

        result = self.engineer.extract(packets)

        # Current code skips the first sequence value of zero.
        # This assertion records the desired behavior and will
        # fail until zero handling is corrected.
        self.assertEqual(
            result["behavior_tcp_seq_delta_flow"],
            10.0,
        )

    def test_behavior_iat_is_finite_for_valid_timestamps(self):
        packets = [
            {"timestamp": 10.0, "frame.len": 60},
            {"timestamp": 10.25, "frame.len": 80},
            {"timestamp": 10.75, "frame.len": 70},
        ]

        result = self.engineer.extract(packets)

        self.assertTrue(math.isfinite(result["behavior_iat"]))
        self.assertAlmostEqual(result["behavior_iat"], 0.375)


if __name__ == "__main__":
    unittest.main()
