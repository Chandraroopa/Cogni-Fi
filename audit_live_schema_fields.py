
import json
from collections import Counter
from pathlib import Path

from backend.capture.adapter import TSharkCapture

ROOT = Path(__file__).resolve().parent
SCHEMA_DIR = ROOT / "ml" / "schemas"

PACKET_LIMIT = 200

def load_features(filename):
    schema = json.loads(
        (SCHEMA_DIR / filename).read_text(encoding="utf-8")
    )
    return schema.get("feature_order", schema.get("features", []))

def is_numeric(value):
    if value is None or isinstance(value, bool):
        return False
    try:
        number = float(value)
        return number == number and abs(number) != float("inf")
    except (TypeError, ValueError, OverflowError):
        return False

def inspect_packet(packet, field):
    # The adapter's normalized, top-level fields are the primary source.
    if field in packet:
        return True, packet[field] is not None, is_numeric(packet[field])

    # Also check raw TShark layer dictionaries for diagnostics.
    layers = packet.get("layers")
    if isinstance(layers, dict) and field in layers:
        value = layers[field]
        return True, value is not None, is_numeric(value)

    return False, False, False

def main():
    schemas = {
        "binary": load_features("binary_feature_schema.json"),
        "multiclass": load_features("multiclass_feature_schema.json"),
    }
    fields = list(dict.fromkeys(
        feature for features in schemas.values() for feature in features
    ))

    interface = input(
        'TShark interface number (press Enter for "5"): '
    ).strip() or "5"

    counts = {
        field: Counter() for field in fields
    }
    packet_count = 0

    print(f"\nCapturing up to {PACKET_LIMIT} packets on interface {interface}...")
    try:
        capture = TSharkCapture(interface=interface)
        for packet in capture.packets():
            packet_count += 1
            for field in fields:
                exists, nonnull, numeric = inspect_packet(packet, field)
                counts[field]["present"] += int(exists)
                counts[field]["nonnull"] += int(nonnull)
                counts[field]["numeric"] += int(numeric)

            if packet_count >= PACKET_LIMIT:
                break
    except KeyboardInterrupt:
        print("\nCapture interrupted.")
    except Exception as exc:
        print(f"\nCapture failed: {type(exc).__name__}: {exc}")
        return

    print(f"\nCaptured packets: {packet_count}")
    if not packet_count:
        print("No packets captured; check the interface number and permissions.")
        return

    for schema_name, features in schemas.items():
        print(f"\n{'=' * 76}\n{schema_name.upper()} ({len(features)} features)\n{'=' * 76}")
        print(f"{'FEATURE':46} {'KEY%':>6} {'VALUE%':>7} {'NUMERIC%':>9}")
        for field in features:
            c = counts[field]
            print(
                f"{field:46} "
                f"{100*c['present']/packet_count:5.1f}% "
                f"{100*c['nonnull']/packet_count:6.1f}% "
                f"{100*c['numeric']/packet_count:8.1f}%"
            )

if __name__ == "__main__":
    main()
