
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCHEMAS = ROOT / "ml" / "schemas"

# Fields emitted directly by the current packet adapter.
# This list is based on the adapter implementation we've inspected.
RAW_FIELDS = {
    "frame.len", "frame.time_delta", "frame.time_delta_displayed",
    "radiotap.channel.flags.ofdm", "radiotap.channel.freq",
    "radiotap.datarate", "radiotap.dbm_antsignal", "radiotap.length",
    "radiotap.timestamp.ts", "wlan.duration", "wlan.fc.protected",
    "wlan.fc.type", "wlan.fc.retry", "wlan.fc.subtype",
    "wlan.fixed.reason_code", "wlan_radio.duration", "wlan.seq",
    "wlan.tag.length", "wlan_radio.channel", "wlan_radio.data_rate",
    "wlan_radio.frequency", "wlan_radio.signal_dbm", "wlan_radio.phy",
    "wlan.rsn.capabilities.mfpc", "arp.opcode", "arp.src.proto_ipv4",
    "arp.dst.proto_ipv4", "ip.proto", "ip.ttl", "ip.version",
    "tcp.ack", "tcp.ack_raw", "tcp.analysis.retransmission",
    "tcp.flags.syn", "tcp.dstport", "tcp.flags.ack", "tcp.flags.fin",
    "tcp.flags.push", "tcp.flags.reset", "tcp.option_len", "tcp.seq",
    "tcp.seq_raw", "tcp.srcport", "tcp.time_delta", "tcp.time_relative",
    "udp.dstport", "udp.srcport", "udp.length", "udp.time_relative",
    "udp.time_delta", "http.content_length", "http.content_type",
    "http.request.method", "http.request.version", "tls.record.version",
}

# Values that require aggregation over a packet window.
AGGREGATED_SUFFIXES = (
    "__mean", "__std", "__count", "__active", "__present"
)

BEHAVIOR_FIELDS = {
    "behavior_iat",
    "behavior_tcp_seq_delta_flow",
    "behavior_tcp_ack_delta_flow",
    "behavior_wlan_seq_delta_sender",
}

def classify(feature):
    if feature in BEHAVIOR_FIELDS:
        return "behavior/history-dependent"
    if feature.endswith(AGGREGATED_SUFFIXES):
        return "window aggregate"
    if feature in RAW_FIELDS:
        return "raw adapter field (runtime availability still needs checking)"
    if feature.startswith("delta_"):
        return "delta / prior-window history"
    if feature.startswith("rolling_"):
        return "rolling / prior-window history"
    return "unconfirmed: inspect adapter and training semantics"

def load_features(path):
    schema = json.loads(path.read_text(encoding="utf-8"))
    return schema.get("feature_order", schema.get("features", []))

for filename in (
    "binary_feature_schema.json",
    "multiclass_feature_schema.json",
):
    path = SCHEMAS / filename
    features = load_features(path)

    print(f"\n{'=' * 72}\n{filename} ({len(features)} features)\n{'=' * 72}")
    groups = {}
    for feature in features:
        groups.setdefault(classify(feature), []).append(feature)

    for category, items in groups.items():
        print(f"\n[{category}] — {len(items)}")
        for item in items:
            print(f"  {item}")
