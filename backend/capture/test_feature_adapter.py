import unittest
import os
import pandas as pd
from backend.capture.feature_adapter import FeatureAdapter
from ml.predictor import CognifiPredictor

class TestFeatureAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = FeatureAdapter(ml_dir="ml")
        # Mock 30 foundational base features outputted by feature_window.py
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
            "udp.length": 64.0
        }

    def test_binary_feature_count_and_order(self):
        df_binary = self.adapter.adapt_for_binary(self.sample_base_features)
        self.assertEqual(len(df_binary.columns), 82)
        self.assertEqual(list(df_binary.columns), self.adapter.binary_features)

    def test_multiclass_feature_count_and_order(self):
        df_multi = self.adapter.adapt_for_multiclass(self.sample_base_features)
        self.assertEqual(len(df_multi.columns), 81)
        self.assertEqual(list(df_multi.columns), self.adapter.multiclass_features)

    def test_end_to_end_prediction(self):
        predictor = CognifiPredictor(base_dir="ml")
        
        df_binary = self.adapter.adapt_for_binary(self.sample_base_features)
        df_multi = self.adapter.adapt_for_multiclass(self.sample_base_features)
        
        binary_res = predictor.predict_binary(df_binary)
        multi_res = predictor.predict_multiclass(df_multi)
        
        self.assertIn("is_threat", binary_res)
        self.assertIn("predicted_class", multi_res)
        print("[TEST PASSED] End-to-end integration with CognifiPredictor successful!")

if __name__ == "__main__":
    unittest.main()