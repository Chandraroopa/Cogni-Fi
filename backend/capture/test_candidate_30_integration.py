
import json
from pathlib import Path

from backend.capture.feature_window import (
    FeatureExtractor,
    FEATURE_NAMES,
    WIFI_AVAILABILITY_NAMES,
)
from ml.candidate_30.predictor_30 import predict_one


def main():
    print("=" * 65)
    print("COGNIFI LIVE FEATURE → 30-FEATURE MODEL TEST")
    print("=" * 65)

    # Synthetic packet metadata for software integration testing only.
    packets = [
        {
            "timestamp": 1000.0,
            "length": 128,
            "source": "192.168.1.10",
            "destination": "192.168.1.1",
            "protocol": "UDP",
            "retry": False,
            "protected": False,
            "signal": -50,
            "data_rate": 54,
            "bssid": "AA:BB:CC:DD:EE:FF",
            "dns_query": False,
            "dns_response": False,
            "tcp_syn": False,
            "tcp_rst": False,
            "retransmission": False,
            "destination_port": 53,
        },
        {
            "timestamp": 1000.2,
            "length": 256,
            "source": "192.168.1.1",
            "destination": "192.168.1.10",
            "protocol": "UDP",
            "retry": False,
            "protected": False,
            "signal": -48,
            "data_rate": 54,
            "bssid": "AA:BB:CC:DD:EE:FF",
            "dns_query": True,
            "dns_response": False,
            "tcp_syn": False,
            "tcp_rst": False,
            "retransmission": False,
            "destination_port": 53,
        },
    ]

    extractor = FeatureExtractor(window_size=1.0)
    features = extractor.extract_window_features(packets)

    missing = [name for name in FEATURE_NAMES if name not in features]
    assert not missing, f"Extractor missing features: {missing}"

    missing_flags = [
        name for name in WIFI_AVAILABILITY_NAMES if name not in features
    ]
    assert not missing_flags, f"Extractor missing availability flags: {missing_flags}"

    model_features = {name: features[name] for name in FEATURE_NAMES}
    result = predict_one(model_features)

    assert len(model_features) == 30
    assert len(result["class_probabilities"]) == 14
    assert result["is_threat"] == (result["predicted_class"] != "Normal")

    print("[PASS] Feature extractor produced all 30 model features")
    print("[PASS] All six diagnostic flags are present")
    print("[PASS] Only 30 features passed to the model")
    print("[PASS] Model returned a 14-class prediction")
    print(f"Predicted class: {result['predicted_class']}")
    print(f"Confidence: {result['confidence']:.6f}")
    print(f"Threat probability: {result['threat_probability']:.6f}")
    print()
    print("NOTE: Synthetic packets test integration only, not detection quality.")
    print("=" * 65)


if __name__ == "__main__":
    main()
