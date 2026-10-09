from backend.capture.adapter import TSharkCapture
from backend.capture.feature_window import CausalWindowManager
from backend.capture.schema_aggregator import SchemaFeatureAggregator


def main():
    capture = TSharkCapture(interface="5")

    manager = CausalWindowManager(window_size=1.0)
    aggregator = SchemaFeatureAggregator()

    completed = 0

    print("=" * 60)
    print("SCHEMA AGGREGATOR LIVE TEST")
    print("=" * 60)

    try:
        for packet in capture.packets():

            windows = manager.add_packet(packet)

            for window in windows:
                completed += 1

                features = aggregator.aggregate(
                    window["packets"]
                )

                print()
                print(f"WINDOW {window['window_id']}")
                print(
                    f"Packets: {len(window['packets'])}"
                )

                print(
                    "tcp.time_delta__mean =",
                    features.get(
                        "tcp.time_delta__mean",
                        0.0
                    )
                )

                print(
                    "tcp.time_delta__count =",
                    features.get(
                        "tcp.time_delta__count",
                        0.0
                    )
                )

                print(
                    "udp.length__mean =",
                    features.get(
                        "udp.length__mean",
                        0.0
                    )
                )

                print(
                    "ip.ttl__mean =",
                    features.get(
                        "ip.ttl__mean",
                        0.0
                    )
                )

                print(
                    "ip.ttl__std =",
                    features.get(
                        "ip.ttl__std",
                        0.0
                    )
                )

                print(
                    "tcp.flags.syn__active =",
                    features.get(
                        "tcp.flags.syn__active",
                        0.0
                    )
                )

                print(
                    "arp__present =",
                    features.get(
                        "arp__present",
                        0.0
                    )
                )

                print(
                    "http.content_length__mean =",
                    features.get(
                        "http.content_length__mean",
                        0.0
                    )
                )

                if completed >= 5:
                    return

    except KeyboardInterrupt:
        pass

    finally:
        # TSharkCapture owns its process lifecycle.
        # No start()/stop() methods are required here.
        pass

    print()
    print("=" * 60)
    print(
        f"[SUCCESS] Aggregated {completed} live windows."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()