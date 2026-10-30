import time

from backend.capture.feature_window import (
    FeatureExtractor,
    FEATURE_NAMES,
    WIFI_AVAILABILITY_NAMES,
    NETWORK_AVAILABILITY_NAMES,
    feature_dict_to_vector,
)


def test_feature_extraction():
    print("Initializing FeatureExtractor test suite...")

    # Mock packets mimicking the structures parsed from TShark.
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
        },
    ]

    extractor = FeatureExtractor(window_size=1.0)

    features = extractor.extract_window_features(
        mock_packets
    )

    vector = feature_dict_to_vector(features)

    # --------------------------------------------------------
    # 1. Validate output types
    # --------------------------------------------------------

    assert isinstance(features, dict), (
        "Feature extraction must return a dictionary."
    )

    assert isinstance(vector, list), (
        "Feature vector must be a list."
    )

    # --------------------------------------------------------
    # 2. Validate the frozen 30-feature model contract
    # --------------------------------------------------------

    assert len(FEATURE_NAMES) == 30, (
        f"Expected exactly 30 model features, "
        f"got {len(FEATURE_NAMES)}."
    )

    assert all(
        name in features
        for name in FEATURE_NAMES
    ), "One or more required model features are missing."

    assert len(vector) == 30, (
        f"Expected a 30-element ML vector, "
        f"got {len(vector)}."
    )

    assert all(
        isinstance(value, (int, float))
        for value in vector
    ), "The ML vector contains a non-numeric value."

    # --------------------------------------------------------
    # 3. Validate Wi-Fi availability metadata
    # --------------------------------------------------------

    assert len(WIFI_AVAILABILITY_NAMES) == 6

    assert all(
        name in features
        for name in WIFI_AVAILABILITY_NAMES
    ), "One or more Wi-Fi availability flags are missing."

    assert all(
        isinstance(features[name], bool)
        for name in WIFI_AVAILABILITY_NAMES
    ), "Wi-Fi availability flags must be booleans."

    # --------------------------------------------------------
    # 4. Validate network availability metadata
    # --------------------------------------------------------

    assert len(NETWORK_AVAILABILITY_NAMES) == 3

    assert all(
        name in features
        for name in NETWORK_AVAILABILITY_NAMES
    ), "One or more network availability flags are missing."

    assert all(
        isinstance(features[name], bool)
        for name in NETWORK_AVAILABILITY_NAMES
    ), "Network availability flags must be booleans."

    # --------------------------------------------------------
    # 5. Validate total dictionary entries
    # --------------------------------------------------------

    expected_entries = (
        len(FEATURE_NAMES)
        + len(WIFI_AVAILABILITY_NAMES)
        + len(NETWORK_AVAILABILITY_NAMES)
    )

    assert len(features) == expected_entries, (
        f"Expected {expected_entries} entries "
        f"(30 model features + 9 metadata flags), "
        f"got {len(features)}."
    )

    # --------------------------------------------------------
    # 6. Verify metadata is excluded from the ML vector
    # --------------------------------------------------------

    assert not any(
        name in FEATURE_NAMES
        for name in WIFI_AVAILABILITY_NAMES
    ), "Wi-Fi metadata must not be included in model inputs."

    assert not any(
        name in FEATURE_NAMES
        for name in NETWORK_AVAILABILITY_NAMES
    ), "Network metadata must not be included in model inputs."

    # --------------------------------------------------------
    # 7. Validate expected sample values
    # --------------------------------------------------------

    assert features["packet_count"] == 2.0

    assert features["byte_count"] == 450.0

    assert features["unique_bssid_count"] == 1.0

    assert features["retry_rate"] == 0.5

    assert features["protected_rate"] == 0.5

    assert features["beacon_rate"] > 0

    assert features["syn_rate"] > 0

    assert features["udp_packet_rate"] > 0

    # --------------------------------------------------------
    # Success output
    # --------------------------------------------------------

    print("\n[SUCCESS] All feature validation assertions passed!")

    print(f" - Model features: {len(FEATURE_NAMES)}")
    print(
        f" - Wi-Fi metadata flags: "
        f"{len(WIFI_AVAILABILITY_NAMES)}"
    )
    print(
        f" - Network metadata flags: "
        f"{len(NETWORK_AVAILABILITY_NAMES)}"
    )
    print(f" - Total dictionary entries: {len(features)}")
    print(f" - ML vector length: {len(vector)}")

    print("\nSample Feature Output Preview:")

    preview_features = [
        "packet_count",
        "byte_count",
        "retry_rate",
        "signal_mean",
        "unique_source_count",
        "syn_rate",
    ]

    for name in preview_features:
        print(f"   - {name}: {features.get(name)}")


if __name__ == "__main__":
    test_feature_extraction()