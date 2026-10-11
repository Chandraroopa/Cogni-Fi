
import math
from numbers import Real

from backend.capture.adapter import TSharkCapture
from backend.capture.feature_engineering import WindowFeatureEngineer
from backend.capture.schema_aggregator import SchemaFeatureAggregator
from backend.ml_service import CognifiMLService


INTERFACE = "5"
PACKET_LIMIT = 100


def valid_number(value):
    return (
        isinstance(value, Real)
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def main():
    print("Capturing live packets...")

    iterator = TSharkCapture(interface=INTERFACE).packets()
    packets = []

    try:
        for _ in range(PACKET_LIMIT):
            try:
                packets.append(next(iterator))
            except StopIteration:
                break
    finally:
        close = getattr(iterator, "close", None)
        if callable(close):
            close()

    if not packets:
        print("No packets captured. Check TShark and interface.")
        return

    window_features = WindowFeatureEngineer().extract(packets)
    aggregate_features = SchemaFeatureAggregator().aggregate(packets)

    # Preserve the current pipeline for auditing only.
    features = dict(packets[-1])
    features.update(window_features)
    features.update(aggregate_features)

    service = CognifiMLService()

    print("\nPACKET COUNT:", len(packets))
    print("WINDOW FEATURE COUNT:", len(window_features))
    print("AGGREGATE FEATURE COUNT:", len(aggregate_features))

    for label, schema in (
        ("BINARY", service.binary_features),
        ("MULTICLASS", service.multiclass_features),
    ):
        valid = [
            name for name in schema
            if valid_number(features.get(name))
        ]
        unavailable = [
            name for name in schema
            if not valid_number(features.get(name))
        ]

        print(f"\n{label}: {len(valid)}/{len(schema)} numeric values")
        print("Unavailable features:")
        for name in unavailable:
            print(f"  {name}: {features.get(name, '<MISSING>')}")

    print("\nWINDOW FEATURES GENERATED:")
    for name, value in sorted(window_features.items()):
        print(f"  {name}: {value}")

    print("\nAGGREGATE FEATURES GENERATED:")
    for name, value in sorted(aggregate_features.items()):
        print(f"  {name}: {value}")


if __name__ == "__main__":
    main()
