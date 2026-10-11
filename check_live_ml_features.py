
import math
from numbers import Real

from backend.capture.adapter import TSharkCapture
from backend.capture.feature_engineering import WindowFeatureEngineer
from backend.capture.schema_aggregator import SchemaFeatureAggregator
from backend.ml_service import CognifiMLService


INTERFACE = "5"
PACKET_LIMIT = 100


def is_valid_number(value):
    """True only for finite numeric values, excluding booleans."""
    return (
        isinstance(value, Real)
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def capture_packets(interface, limit):
    """Capture up to limit packets and close the iterator safely."""
    capture = TSharkCapture(interface=interface)
    packets_iter = capture.packets()
    packets = []

    try:
        for _ in range(limit):
            try:
                packet = next(packets_iter)
            except StopIteration:
                break

            if isinstance(packet, dict):
                packets.append(packet)
    finally:
        close = getattr(packets_iter, "close", None)
        if callable(close):
            close()

    return packets


def summarize_schema(label, schema, features, raw_keys,
                     final_packet, window_features, aggregate_features):
    missing = []
    invalid = []
    valid = []
    raw_seen_elsewhere = []
    raw_never_seen = []

    for name in schema:
        value = features.get(name, "<MISSING>")

        if value == "<MISSING>":
            missing.append(name)
        elif is_valid_number(value):
            valid.append(name)
        else:
            invalid.append(name)

        # These checks refer to the original raw packet dictionaries.
        if name not in final_packet and name in raw_keys:
            if name not in window_features and name not in aggregate_features:
                raw_seen_elsewhere.append(name)

        if name not in raw_keys:
            raw_never_seen.append(name)

    print(f"\n{'=' * 18} {label} {'=' * 18}")
    print("Expected features:", len(schema))
    print("Valid numeric values:", len(valid))
    print("Missing keys:", len(missing))
    print("Invalid/unavailable values:", len(invalid))
    print("Raw fields seen only outside final packet:",
          raw_seen_elsewhere)
    print("Expected raw names never seen in capture:", raw_never_seen)

    if missing:
        print("\nMissing key names:")
        for name in missing:
            print("  ", name)

    if invalid:
        print("\nInvalid/unavailable key names:")
        for name in invalid:
            print("  ", name)

    return {
        "valid": valid,
        "missing": missing,
        "invalid": invalid,
        "raw_seen_elsewhere": raw_seen_elsewhere,
        "raw_never_seen": raw_never_seen,
    }


def main():
    print("Capturing live packets...")
    packets = capture_packets(INTERFACE, PACKET_LIMIT)

    if not packets:
        print(
            f"No packets captured on interface {INTERFACE}. "
            "Check TShark, interface selection, and permissions."
        )
        raise SystemExit(1)

    # Keys that occurred in at least one packet in the capture window.
    raw_keys = set()
    for packet in packets:
        raw_keys.update(packet.keys())

    # Build the current feature dictionary using the existing pipeline.
    window_features = WindowFeatureEngineer().extract(packets)
    aggregate_features = SchemaFeatureAggregator().aggregate(packets)

    features = dict(packets[-1])
    features.update(window_features)
    features.update(aggregate_features)

    service = CognifiMLService()

    print("\nCAPTURE SUMMARY")
    print("Packets captured:", len(packets))
    print("Distinct raw keys across capture:", len(raw_keys))
    print("Raw keys in final packet:", len(packets[-1]))
    print("Window features:", len(window_features))
    print("Aggregate features:", len(aggregate_features))
    print("Combined feature keys:", len(features))

    binary_report = summarize_schema(
        "BINARY SCHEMA",
        service.binary_features,
        features,
        raw_keys,
        packets[-1],
        window_features,
        aggregate_features,
    )

    multiclass_report = summarize_schema(
        "MULTICLASS SCHEMA",
        service.multiclass_features,
        features,
        raw_keys,
        packets[-1],
        window_features,
        aggregate_features,
    )

    # Print each expected multiclass field in frozen schema order.
    print("\nMULTICLASS LIVE FEATURE VALUES")
    for name in service.multiclass_features:
        value = features.get(name, "<MISSING>")
        status = "VALID" if is_valid_number(value) else "UNAVAILABLE"
        print(f"{name}: {value} [{status}]")

    print("\nDIAGNOSTIC RESULT")
    if multiclass_report["missing"] or multiclass_report["invalid"]:
        print(
            "Multiclass input is not fully populated with valid numeric "
            "values. Do not treat a prediction from this diagnostic "
            "dictionary as a validated live threat classification."
        )
    else:
        print(
            "All multiclass schema keys have finite numeric values. "
            "This confirms numeric completeness only, not model accuracy "
            "or semantic correctness."
        )

    if binary_report["missing"] or binary_report["invalid"]:
        print(
            "Binary input also has missing or unavailable values; "
            "review its preprocessing and feature-generation contract."
        )


if __name__ == "__main__":
    main()
