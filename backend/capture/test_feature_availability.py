from backend.capture.feature_availability import (
    FeatureAvailabilityAnalyzer,
)


def main():

    analyzer = (
        FeatureAvailabilityAnalyzer()
    )

    # These are the normalized/engineered
    # fields currently implemented upstream.
    #
    # This list deliberately contains only
    # features that we have actually implemented.
    available_features = {

        # ---------------------------------------------------------
        # Raw packet fields
        # ---------------------------------------------------------

        "frame.len",
        "frame.time_delta",
        "frame.time_delta_displayed",

        # ---------------------------------------------------------
        # Radiotap fields currently parsed by adapter.py
        # ---------------------------------------------------------

        "radiotap.channel.flags.ofdm",
        "radiotap.channel.freq",
        "radiotap.datarate",
        "radiotap.dbm_antsignal",
        "radiotap.length",
        "radiotap.mactime",
        "radiotap.present.tsft",
        "radiotap.timestamp.ts",

        # ---------------------------------------------------------
        # WLAN fields currently parsed
        # ---------------------------------------------------------

        "wlan.duration",
        "wlan.fc.ds",
        "wlan.fc.protected",
        "wlan.fc.type",
        "wlan.fc.retry",
        "wlan.fc.subtype",
        "wlan.fixed.reason_code",
        "wlan.seq",

        # ---------------------------------------------------------
        # WLAN radio
        # ---------------------------------------------------------

        "wlan_radio.duration",
        "wlan_radio.data_rate",
        "wlan_radio.signal_dbm",
        "wlan_radio.phy",

        # ---------------------------------------------------------
        # IP
        # ---------------------------------------------------------

        "ip.proto",
        "ip.ttl",
        "ip.version",

        # ---------------------------------------------------------
        # TCP
        # ---------------------------------------------------------

        "tcp.ack",
        "tcp.ack_raw",
        "tcp.analysis",
        "tcp.analysis.flags",
        "tcp.analysis.retransmission",
        "tcp.analysis.rto_frame",
        "tcp.checksum",
        "tcp.checksum.status",
        "tcp.flags.syn",
        "tcp.dstport",
        "tcp.flags.ack",
        "tcp.flags.fin",
        "tcp.flags.push",
        "tcp.flags.reset",
        "tcp.option_len",
        "tcp.seq",
        "tcp.seq_raw",
        "tcp.srcport",
        "tcp.time_delta",
        "tcp.time_relative",

        # ---------------------------------------------------------
        # UDP
        # ---------------------------------------------------------

        "udp.dstport",
        "udp.srcport",
        "udp.length",
        "udp.time_relative",
        "udp.time_delta",

        # ---------------------------------------------------------
        # ARP
        # ---------------------------------------------------------

        "arp",
        "arp.hw.type",
        "arp.proto.type",
        "arp.hw.size",
        "arp.proto.size",
        "arp.opcode",
        "arp.src.proto_ipv4",
        "arp.dst.proto_ipv4",

        # ---------------------------------------------------------
        # LLC
        # ---------------------------------------------------------

        "llc",

        # ---------------------------------------------------------
        # HTTP
        # ---------------------------------------------------------

        "http.content_length",
        "http.content_type",
        "http.request.method",
        "http.request.version",

        # ---------------------------------------------------------
        # SSH
        # ---------------------------------------------------------

        "ssh.direction",

        # ---------------------------------------------------------
        # TLS
        # ---------------------------------------------------------

        "tls.record.version",

        # ---------------------------------------------------------
        # SSDP
        # ---------------------------------------------------------

        "ssdp",

        # ---------------------------------------------------------
        # Data
        # ---------------------------------------------------------

        "data.len",

        # ---------------------------------------------------------
        # Engineered behavioral features
        # ---------------------------------------------------------

        "behavior_iat",
        "behavior_tcp_seq_delta_flow",
        "behavior_tcp_ack_delta_flow",
        "behavior_wlan_seq_delta_sender",
    }

    # =============================================================
    # Binary
    # =============================================================

    binary = analyzer.binary_report(
        available_features
    )

    print(
        "=================================================="
    )

    print(
        "BINARY FEATURE AVAILABILITY"
    )

    print(
        "=================================================="
    )

    print(
        f"Expected:     {binary['expected']}"
    )

    print(
        f"Available:    {binary['available']}"
    )

    print(
        f"Unavailable:  {binary['unavailable']}"
    )

    print(
        "\nAVAILABLE BINARY FEATURES:"
    )

    for feature in binary[
        "available_features"
    ]:

        print(
            f"  [YES] {feature}"
        )

    print(
        "\nUNAVAILABLE BINARY FEATURES:"
    )

    for feature in binary[
        "unavailable_features"
    ]:

        print(
            f"  [NO]  {feature}"
        )

    # =============================================================
    # Multiclass
    # =============================================================

    multiclass = (
        analyzer.multiclass_report(
            available_features
        )
    )

    print(
        "\n=================================================="
    )

    print(
        "MULTICLASS FEATURE AVAILABILITY"
    )

    print(
        "=================================================="
    )

    print(
        f"Expected:     {multiclass['expected']}"
    )

    print(
        f"Available:    {multiclass['available']}"
    )

    print(
        f"Unavailable:  {multiclass['unavailable']}"
    )

    print(
        "\nAVAILABLE MULTICLASS FEATURES:"
    )

    for feature in multiclass[
        "available_features"
    ]:

        print(
            f"  [YES] {feature}"
        )

    print(
        "\nUNAVAILABLE MULTICLASS FEATURES:"
    )

    for feature in multiclass[
        "unavailable_features"
    ]:

        print(
            f"  [NO]  {feature}"
        )

    print(
        "\n[SUCCESS] "
        "Feature availability analysis completed."
    )


if __name__ == "__main__":
    main()
    