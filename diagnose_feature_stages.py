
from itertools import islice

from backend.capture.adapter import TSharkCapture
from backend.capture.feature_engineering import WindowFeatureEngineer
from backend.capture.schema_aggregator import aggregate_schema_features

packets = list(islice(TSharkCapture(interface="5").packets(), 20))

if not packets:
    print("No packets captured.")
    raise SystemExit(1)

aggregated = aggregate_schema_features(packets)
engineered = WindowFeatureEngineer().extract(packets)

print("\n--- RAW PACKET: KEY VALUES ---")
for key in [
    "frame.len", "frame.time_delta", "tcp.ack",
    "tcp.seq", "ip.version", "radiotap.dbm_antsignal"
]:
    print(f"{key}: {packets[0].get(key)!r}")

print("\n--- AGGREGATOR OUTPUT ---")
print("Feature count:", len(aggregated))
print("Contains frame.len:", "frame.len" in aggregated)
print("Contains tcp.ack:", "tcp.ack" in aggregated)
print("Contains tcp.ack__active:", "tcp.flags.ack__active" in aggregated)
print("Keys:", sorted(aggregated))

print("\n--- BEHAVIOR ENGINEER OUTPUT ---")
print("Feature count:", len(engineered))
print("Keys:", sorted(engineered))

print("\n--- COMBINED OUTPUT ---")
combined = {**aggregated, **engineered}
for key in [
    "frame.len", "frame.time_delta", "tcp.ack",
    "tcp.flags.ack__active", "ip.version",
    "radiotap.dbm_antsignal_mean", "behavior_iat"
]:
    print(f"{key}: {combined.get(key, '<MISSING>')!r}")

print("\nDiagnostic complete. No predictions made.")
