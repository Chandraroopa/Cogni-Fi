from itertools import islice

from backend.capture.adapter import TSharkCapture
from backend.capture.schema_aggregator import aggregate_schema_features
from backend.capture.feature_engineering import WindowFeatureEngineer
from backend.capture.feature_vector_builder import FeatureVectorBuilder


def main():
    print("Capturing up to 100 packets...")
    packets = list(
        islice(TSharkCapture(interface="5").packets(), 100)
    )

    if not packets:
        print("No packets captured.")
        return

    # Preserve the most recent packet's raw fields, then add
    # window-level aggregate and behavioral features.
    raw_features = dict(packets[-1])
    aggregate_features = aggregate_schema_features(packets)
    behavioral_features = WindowFeatureEngineer().extract(packets)

    combined = {
        **raw_features,
        **aggregate_features,
        **behavioral_features,
    }

    builder = FeatureVectorBuilder()

    for name, diagnose in (
        ("Binary", builder.diagnose_binary),
        ("Multiclass", builder.diagnose_multiclass),
    ):
        result = diagnose(combined)

        print(f"\n--- {name} schema ---")
        for key in (
            "missing_count",
            "invalid_count",
            "unexpected_count",
            "missing",
            "invalid",
        ):
            if key in result:
                print(f"{key}: {result[key]}")

    print("\n--- Capture availability ---")
    for key in (
        "wlan__present",
        "radiotap__present",
        "wlan_radio__present",
        "ip__present",
        "ipv6__present",
        "tcp__present",
        "udp__present",
    ):
        print(f"{key}: {raw_features.get(key)}")

    print("\nDiagnostic only; no predictions made.")


if __name__ == "__main__":
    main()
