import json
import subprocess
from pathlib import Path

from backend.capture.adapter import normalize_packet
from backend.capture.feature_window import FeatureExtractor

def replay(filename):
    path = Path(filename)
    print(f"\n{'=' * 65}\nREPLAY: {filename}\n{'=' * 65}")

    result = subprocess.run(
        ["tshark", "-r", str(path), "-T", "ek"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )

    packets = []
    raw_packets = []

    for line in result.stdout.splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue

        if not isinstance(item, dict) or "layers" not in item:
            continue

        raw_packets.append(item)
        packets.append(normalize_packet(item))

    print("Packets replayed:", len(packets))

    if not packets:
        print("No packets were parsed.")
        return

    if "dns" in filename.lower():
        print("\nDNS packet fields:")
        for i, (raw, packet) in enumerate(zip(raw_packets, packets), 1):
            if packet.get("dns"):
                print({
                    "packet": i,
                    "timestamp": packet.get("timestamp"),
                    "dns_transaction_id": packet.get("dns_transaction_id"),
                    "dns_response": packet.get("dns_response"),
                    "raw_dns_keys": list(
                        raw.get("layers", {}).get("dns", {}).keys()
                    ),
                })

        features = FeatureExtractor(window_size=1.0).extract_window_features(packets)
        print("\nDNS feature results:")
        for key in (
            "packet_count", "dns_request_count",
            "dns_response_count", "dns_latency_mean",
            "dns_latency_std",
        ):
            print(f"{key}: {features.get(key)!r}")

    else:
        print("\nTCP retransmission-related packets:")
        for i, (raw, packet) in enumerate(zip(raw_packets, packets), 1):
            tcp = raw.get("layers", {}).get("tcp", {})
            keys = {
                key: value for key, value in tcp.items()
                if "analysis" in key.lower()
            }
            if keys or packet.get("tcp_retransmission") is True:
                print({
                    "packet": i,
                    "timestamp": packet.get("timestamp"),
                    "tcp_retransmission": packet.get("tcp_retransmission"),
                    "raw_analysis_fields": keys,
                })

        features = FeatureExtractor(window_size=1.0).extract_window_features(packets)
        print("\nTCP feature results:")
        for key in ("packet_count", "retransmission_rate"):
            print(f"{key}: {features.get(key)!r}")

    print("\nSample normalized packet:")
    print(json.dumps(packets[0], indent=2, default=str)[:2500])

for filename in ("dns_capture.pcapng", "tcp_capture.pcapng"):
    try:
        replay(filename)
    except Exception as exc:
        print(f"\nERROR replaying {filename}: {type(exc).__name__}: {exc}")
