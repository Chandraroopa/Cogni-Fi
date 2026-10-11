
from numbers import Real
import math

from backend.capture.adapter import TSharkCapture
from backend.capture.feature_availability import FeatureAvailabilityAnalyzer
from backend.capture.schema_aggregator import aggregate_schema_features
from backend.capture.feature_engineering import WindowFeatureEngineer


def valid_number(value):
    return (
        isinstance(value, Real)
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def main():
    interface = "5"
    packet_limit = 100

    capture = TSharkCapture(interface=interface)
    packets = []

    print(f"Capturing up to {packet_limit} packets on interface {interface}...")

    for packet in capture.packets():
        packets.append(packet)
        if len(packets) >= packet_limit:
            break

    if not packets:
        print("No packets captured. Check the interface and capture permissions.")
        return

    # Availability across captured packets, for diagnostics only.
    observed = {}
    for packet in packets:
        for name, value in packet.items():
            if valid_number(value):
                observed.setdefault(name, value)

    # Derived features are computed from the captured batch.
    aggregate = aggregate_schema_features(packets)
    engineered = WindowFeatureEngineer().extract(packets)

    # Combine only for availability diagnostics.
    # This is NOT a valid ML input vector.
    diagnostic_values = dict(observed)
    diagnostic_values.update(aggregate)
    diagnostic_values.update(engineered)

    analyzer = FeatureAvailabilityAnalyzer()

    binary = analyzer.binary_report(diagnostic_values)
    multiclass = analyzer.multiclass_report(diagnostic_values)

    print(f"\nPackets captured: {len(packets)}")
    print(f"Binary: {binary['available']}/{binary['expected']} numeric features found")
    print(f"Multiclass: {multiclass['available']}/{multiclass['expected']} numeric features found")

    print("\nBinary features unavailable:")
    for name in binary["unavailable_features"]:
        print(f"  - {name}")

    print("\nMulticlass features unavailable:")
    for name in multiclass["unavailable_features"]:
        print(f"  - {name}")

    print(
        "\nIMPORTANT: This is an availability audit, not a prediction. "
        "A numeric value found somewhere in the capture does not prove "
        "that its training-time aggregation semantics are satisfied."
    )


if __name__ == "__main__":
    main()
