
from backend.capture.feature_availability import FeatureAvailabilityAnalyzer


def main():
    analyzer = FeatureAvailabilityAnalyzer()

    # Synthetic test values only — not real captured traffic.
    sample = {
        "frame.len": 128.0,
        "frame.time_delta": 0.01,
        "radiotap.dbm_antsignal": None,
        "tcp.srcport": float("nan"),
        "tcp.dstport": 443,
        "behavior_iat": 0.05,
    }

    binary = analyzer.binary_report(sample)
    multiclass = analyzer.multiclass_report(sample)

    print("=== Synthetic availability test ===")
    print(f"Binary: {binary['available']}/{binary['expected']} available")
    print(
        "Binary unavailable examples:",
        binary["unavailable_features"][:10],
    )

    print(
        f"Multiclass: {multiclass['available']}/"
        f"{multiclass['expected']} available"
    )
    print(
        "Multiclass unavailable examples:",
        multiclass["unavailable_features"][:10],
    )

    assert "frame.len" in binary["available_features"]
    assert "radiotap.dbm_antsignal" in binary["unavailable_features"]
    assert "tcp.srcport" in binary["unavailable_features"]
    assert "tcp.dstport" in binary["available_features"]

    print("\nPASS: missing and invalid values are detected.")


if __name__ == "__main__":
    main()
