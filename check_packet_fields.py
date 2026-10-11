
from collections import Counter

from backend.capture.adapter import TSharkCapture


def main():
    capture = TSharkCapture(interface="5")
    limit = 100

    counts = Counter()
    examples = {
        "ipv4": None,
        "ipv6": None,
        "tcp": None,
        "udp": None,
    }

    print(f"Capturing up to {limit} packets. Press Ctrl+C to stop early.\n")

    try:
        for index, packet in enumerate(capture.packets()):
            if index >= limit:
                break

            counts["packets"] += 1

            if packet.get("ip__present") == 1.0:
                counts["ipv4"] += 1
                if examples["ipv4"] is None:
                    examples["ipv4"] = packet

            if packet.get("ipv6__present") == 1.0:
                counts["ipv6"] += 1
                if examples["ipv6"] is None:
                    examples["ipv6"] = packet

            if packet.get("tcp__present") == 1.0:
                counts["tcp"] += 1
                if examples["tcp"] is None:
                    examples["tcp"] = packet

            if packet.get("udp__present") == 1.0:
                counts["udp"] += 1
                if examples["udp"] is None:
                    examples["udp"] = packet

            if packet.get("ip.proto") is not None:
                counts["ipv4_proto_populated"] += 1

            if packet.get("ip.ttl") is not None:
                counts["ipv4_ttl_populated"] += 1

            if packet.get("ip.version") is not None:
                counts["ipv4_version_populated"] += 1

            if packet.get("ipv6.nxt") is not None:
                counts["ipv6_next_header_populated"] += 1

            if packet.get("ipv6.hlim") is not None:
                counts["ipv6_hop_limit_populated"] += 1

            if packet.get("ipv6.version") is not None:
                counts["ipv6_version_populated"] += 1

    except KeyboardInterrupt:
        print("\nCapture stopped by user.")

    print("\n========== CAPTURE SUMMARY ==========")
    print(f"Packets captured:             {counts['packets']}")
    print(f"IPv4 layer present:            {counts['ipv4']}")
    print(f"IPv6 layer present:            {counts['ipv6']}")
    print(f"TCP layer present:             {counts['tcp']}")
    print(f"UDP layer present:             {counts['udp']}")
    print(f"IPv4 protocol populated:       {counts['ipv4_proto_populated']}")
    print(f"IPv4 TTL populated:            {counts['ipv4_ttl_populated']}")
    print(f"IPv4 version populated:        {counts['ipv4_version_populated']}")
    print(f"IPv6 next header populated:    {counts['ipv6_next_header_populated']}")
    print(f"IPv6 hop limit populated:      {counts['ipv6_hop_limit_populated']}")
    print(f"IPv6 version populated:        {counts['ipv6_version_populated']}")

    for label in ("ipv4", "ipv6", "tcp", "udp"):
        packet = examples[label]
        print(f"\n========== FIRST {label.upper()} PACKET ==========")

        if packet is None:
            print("No such packet was observed in this capture.")
            continue

        keys = (
            "source",
            "destination",
            "ip__present",
            "ipv6__present",
            "ip.proto",
            "ip.ttl",
            "ip.version",
            "ipv6.nxt",
            "ipv6.hlim",
            "ipv6.version",
            "tcp__present",
            "udp__present",
        )

        for key in keys:
            print(f"{key}: {packet.get(key, '<MISSING>')}")


if __name__ == "__main__":
    main()
