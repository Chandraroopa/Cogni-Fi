from backend.capture.adapter import TSharkCapture
from backend.capture.feature_window import (
    CausalWindowManager,
    FeatureExtractor,
)


def main():
    interface = "5"

    capture = TSharkCapture(interface)

    window_manager = CausalWindowManager(
        window_size=1.0
    )

    extractor = FeatureExtractor(
        window_size=1.0
    )

    print("Starting live TShark window test...")
    print(f"Interface: {interface}")
    print("Waiting for packets...\n")

    completed_windows = 0

    try:
        for packet in capture.packets():

            completed = window_manager.add_packet(
                packet
            )

            for window in completed:

                completed_windows += 1

                features = (
                    extractor.extract_window_features(
                        window["packets"],
                        duration=1.0,
                    )
                )

                print(
                    f"\n===== WINDOW "
                    f"{window['window_id']} ====="
                )

                print(
                    f"Start: "
                    f"{window['start_timestamp']:.6f}"
                )

                print(
                    f"End:   "
                    f"{window['end_timestamp']:.6f}"
                )

                print(
                    f"Packets: "
                    f"{len(window['packets'])}"
                )

                print(
                    f"Bytes: "
                    f"{features['byte_count']}"
                )

                print(
                    f"Packet rate: "
                    f"{features['packets_per_second']:.2f}"
                )

                print(
                    f"IAT mean: "
                    f"{features['iat_mean']:.6f}"
                )

                print(
                    f"TCP SYN rate: "
                    f"{features['syn_rate']:.2f}"
                )

                print(
                    f"TCP RST rate: "
                    f"{features['rst_rate']:.2f}"
                )

                print(
                    f"UDP rate: "
                    f"{features['udp_packet_rate']:.2f}"
                )

                if completed_windows >= 10:
                    print(
                        "\n[SUCCESS] "
                        "10 live causal windows completed."
                    )
                    return

    except KeyboardInterrupt:
        print("\nStopping capture...")

    finally:
        remaining = window_manager.flush()

        for window in remaining:

            features = (
                extractor.extract_window_features(
                    window["packets"],
                    duration=1.0,
                )
            )

            print(
                "\n===== FINAL FLUSHED WINDOW ====="
            )

            print(
                f"Window ID: "
                f"{window['window_id']}"
            )

            print(
                f"Packets: "
                f"{len(window['packets'])}"
            )

            print(
                f"Bytes: "
                f"{features['byte_count']}"
            )


if __name__ == "__main__":
    main()