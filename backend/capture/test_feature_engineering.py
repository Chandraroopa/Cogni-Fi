from backend.capture.adapter import TSharkCapture
from backend.capture.feature_window import (
    CausalWindowManager,
)
from backend.capture.feature_engineering import (
    WindowFeatureEngineer,
)


def print_feature(name, value):

    if isinstance(value, float):
        print(
            f"{name}: {value:.6f}"
        )
    else:
        print(
            f"{name}: {value}"
        )


def main():

    interface = "5"

    capture = TSharkCapture(
        interface
    )

    window_manager = CausalWindowManager(
        window_size=1.0
    )

    engineer = WindowFeatureEngineer()

    completed = 0

    print(
        "Starting live feature engineering test..."
    )

    print(
        f"Interface: {interface}"
    )

    print(
        "Waiting for packets...\n"
    )

    try:

        for packet in capture.packets():

            completed_windows = (
                window_manager.add_packet(
                    packet
                )
            )

            for window in completed_windows:

                completed += 1

                features = engineer.extract(
                    window["packets"]
                )

                print(
                    f"\n===== ENGINEERED WINDOW "
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
                    f"{features['packet_count']}"
                )

                print(
                    f"Bytes: "
                    f"{features['byte_count']}"
                )

                print(
                    f"Packet size mean: "
                    f"{features['packet_size_mean']:.2f}"
                )

                print(
                    f"Packet size std: "
                    f"{features['packet_size_std']:.2f}"
                )

                print(
                    f"IAT mean: "
                    f"{features['iat_mean']:.6f}"
                )

                print(
                    f"IAT std: "
                    f"{features['iat_std']:.6f}"
                )

                print(
                    f"Retry rate: "
                    f"{features['retry_rate']:.4f}"
                )

                print(
                    f"Protected rate: "
                    f"{features['protected_rate']:.4f}"
                )

                print(
                    f"Beacon rate: "
                    f"{features['beacon_rate']:.4f}"
                )

                print(
                    f"Probe response rate: "
                    f"{features['probe_response_rate']:.4f}"
                )

                print(
                    f"Deauth rate: "
                    f"{features['deauth_rate']:.4f}"
                )

                print(
                    f"Disassoc rate: "
                    f"{features['disassoc_rate']:.4f}"
                )

                print(
                    f"Signal mean: "
                    f"{features['signal_mean']:.4f}"
                )

                print(
                    f"Data rate mean: "
                    f"{features['data_rate_mean']:.4f}"
                )

                print(
                    f"Unique BSSIDs: "
                    f"{features['unique_bssid_count']}"
                )

                print(
                    f"Unique sources: "
                    f"{features['unique_source_count']}"
                )

                print(
                    f"Unique destinations: "
                    f"{features['unique_destination_count']}"
                )

                print(
                    f"DNS requests: "
                    f"{features['dns_request_count']}"
                )

                print(
                    f"DNS responses: "
                    f"{features['dns_response_count']}"
                )

                print(
                    f"DNS latency mean: "
                    f"{features['dns_latency_mean']:.6f}"
                )

                print(
                    f"SYN rate: "
                    f"{features['syn_rate']:.4f}"
                )

                print(
                    f"RST rate: "
                    f"{features['rst_rate']:.4f}"
                )

                print(
                    f"Retransmission rate: "
                    f"{features['retransmission_rate']:.4f}"
                )

                print(
                    f"UDP packet rate: "
                    f"{features['udp_packet_rate']:.4f}"
                )

                print(
                    f"Unique UDP destination ports: "
                    f"{features['unique_udp_destination_ports']}"
                )

                print(
                    "\n--- Behavioral Features ---"
                )

                print(
                    f"behavior_iat: "
                    f"{features['behavior_iat']:.6f}"
                )

                print(
                    f"behavior_tcp_seq_delta_flow: "
                    f"{features['behavior_tcp_seq_delta_flow']:.6f}"
                )

                print(
                    f"behavior_tcp_ack_delta_flow: "
                    f"{features['behavior_tcp_ack_delta_flow']:.6f}"
                )

                print(
                    f"behavior_wlan_seq_delta_sender: "
                    f"{features['behavior_wlan_seq_delta_sender']:.6f}"
                )

                if completed >= 5:

                    print(
                        "\n[SUCCESS] "
                        "5 live engineered windows completed."
                    )

                    return

    except KeyboardInterrupt:

        print(
            "\nStopping capture..."
        )

    finally:

        remaining_windows = (
            window_manager.flush()
        )

        for window in remaining_windows:

            features = engineer.extract(
                window["packets"]
            )

            print(
                "\n===== FINAL WINDOW ====="
            )

            print(
                f"Window ID: "
                f"{window['window_id']}"
            )

            print(
                f"Packets: "
                f"{features['packet_count']}"
            )

            print(
                f"Bytes: "
                f"{features['byte_count']}"
            )

            print(
                f"behavior_iat: "
                f"{features['behavior_iat']:.6f}"
            )

            print(
                f"behavior_tcp_seq_delta_flow: "
                f"{features['behavior_tcp_seq_delta_flow']:.6f}"
            )

            print(
                f"behavior_tcp_ack_delta_flow: "
                f"{features['behavior_tcp_ack_delta_flow']:.6f}"
            )

            print(
                f"behavior_wlan_seq_delta_sender: "
                f"{features['behavior_wlan_seq_delta_sender']:.6f}"
            )


if __name__ == "__main__":
    main()