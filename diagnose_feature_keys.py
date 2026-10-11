from backend.capture.adapter import TSharkCapture
from backend.capture.feature_window import FeatureExtractor
from backend.capture.schema_aggregator import SchemaFeatureAggregator
from backend.capture.feature_adapter import FeatureAdapter

capture = TSharkCapture("5")
extractor = FeatureExtractor(window_size=1.0)
aggregator = SchemaFeatureAggregator()
adapter = FeatureAdapter(ml_dir="ml")

try:
    packet = next(capture.packets())
    print("Packet frame.len:", packet.get("frame.len"))
    print("Packet ip.proto:", packet.get("ip.proto"))

    features = extractor.extract_window_features([packet])
    print("\nExtractor keys:", sorted(features.keys()))

    aggregates = aggregator.aggregate([packet])
    print("\nAggregator keys:", sorted(aggregates.keys()))

    combined = {**features, **aggregates}
    print("\nCombined feature count:", len(combined))
    print("Schema feature count:", len(adapter.binary_features))

    available = [
        name for name in adapter.binary_features
        if combined.get(name) is not None
    ]
    missing = [
        name for name in adapter.binary_features
        if combined.get(name) is None
    ]

    print("Available schema features:", len(available))
    print("Missing schema features:", len(missing))
    print("Missing names:", missing)

finally:
    capture.stop()
