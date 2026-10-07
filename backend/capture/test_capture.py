import time
from backend.capture.feature_window import FeatureExtractor, FEATURE_NAMES, feature_dict_to_vector

def test_feature_extraction():
    print("Initializing FeatureExtractor test suite...")
    
    # Create mock packets mimicking the layer/attribute structures parsed from TShark
    mock_packets = [
        {
            "timestamp": time.time(),
            "length": 150,
            "retry": False,
            "protected": True,
            "frame_type": 0,
            "frame_subtype": 8,  # Beacon frame
            "signal": -65,
            "data_rate": 54.0,
            "bssid": "00:11:22:33:44:55",
            "source": "AA:BB:CC:DD:EE:FF",
            "destination": "11:22:33:44:55:66",
            "tcp_syn": True,
            "tcp_rst": False,
            "tcp_retransmission": False,
        },
        {
            "timestamp": time.time() + 0.1,
            "length": 300,
            "retry": True,
            "protected": False,
            "frame_type": 2,  # Data frame
            "frame_subtype": 0,
            "signal": -70,
            "data_rate": 48.0,
            "bssid": "00:11:22:33:44:55",
            "source": "11:22:33:44:55:66",
            "destination": "AA:BB:CC:DD:EE:FF",
            "udp_destination_port": 53,
        }
    ]

    extractor = FeatureExtractor(window_size=1.0)
    features = extractor.extract_window_features(mock_packets)
    vector = feature_dict_to_vector(features)

    # Validation checks
    assert isinstance(features, dict), "Error: Feature extraction must return a dictionary."
    assert len(features) == len(FEATURE_NAMES), f"Error: Expected {len(FEATURE_NAMES)} features, got {len(features)}."
    assert len(vector) == 30, f"Error: Feature vector length must be 30, got {len(vector)}."

    print("\n[SUCCESS] All feature validation assertions passed!")
    print(f" - Total features extracted: {len(features)}")
    print(f" - Vectorized list length: {len(vector)}")
    
    print("\nSample Feature Output Preview:")
    for name in ["packet_count", "byte_count", "retry_rate", "signal_mean", "unique_source_count", "syn_rate"]:
        print(f"   • {name}: {features.get(name)}")

if __name__ == "__main__":
    test_feature_extraction()