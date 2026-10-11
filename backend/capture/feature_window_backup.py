
import statistics
from typing import List, Dict, Any, Optional


FEATURE_NAMES = [
    "packet_count",
    "byte_count",
    "packets_per_second",
    "bytes_per_second",
    "packet_size_mean",
    "packet_size_std",
    "iat_mean",
    "iat_std",

    "retry_rate",
    "protected_rate",
    "beacon_rate",
    "deauth_rate",
    "disassoc_rate",
    "probe_response_rate",

    "signal_mean",
    "signal_std",
    "data_rate_mean",
    "data_rate_std",

    "unique_bssid_count",
    "unique_source_count",
    "unique_destination_count",

    "dns_request_count",
    "dns_response_count",
    "dns_latency_mean",
    "dns_latency_std",

    "syn_rate",
    "rst_rate",
    "retransmission_rate",

    "udp_packet_rate",
    "unique_udp_destination_ports",
]


def feature_dict_to_vector(features: Dict[str, float]) -> List[float]:
    """
    Convert the 30-feature dictionary into a fixed-order list.
    """
    return [
        float(features.get(name, 0.0))
        for name in FEATURE_NAMES
    ]


class FeatureExtractor:
    """
    Groups normalized packets into time windows and extracts
    the 30 Cognifi behavioral features.
    """

    def __init__(self, window_size: float = 1.0):
        self.window_size = window_size

    def extract_window_features(
        self,
        window_packets: List[Dict[str, Any]],
        duration: Optional[float] = None,
    ) -> Dict[str, float]:

        # ---------------------------------------------------------
        # Window duration
        # ---------------------------------------------------------
        dur = (
            duration
            if duration is not None
            else self.window_size
        )

        if dur <= 0:
            dur = 1.0

        packet_count = len(window_packets)

        # ---------------------------------------------------------
        # Empty window
        # ---------------------------------------------------------
        if packet_count == 0:
            return {
                name: 0.0
                for name in FEATURE_NAMES
            }

        # =========================================================
        # 1-8. TRAFFIC FEATURES
        # =========================================================

        lengths = [
            float(p.get("length", 0) or 0)
            for p in window_packets
        ]

        byte_count = sum(lengths)

        packets_per_second = (
            packet_count / dur
        )

        bytes_per_second = (
            byte_count / dur
        )

        packet_size_mean = (
            statistics.mean(lengths)
            if lengths
            else 0.0
        )

        packet_size_std = (
            statistics.stdev(lengths)
            if len(lengths) > 1
            else 0.0
        )

        # ---------------------------------------------------------
        # Inter-arrival time
        # ---------------------------------------------------------

        timestamps = sorted(
            float(p.get("timestamp", 0.0) or 0.0)
            for p in window_packets
        )

        iats = [
            timestamps[i] - timestamps[i - 1]
            for i in range(1, len(timestamps))
        ]

        # Protect against invalid negative timestamps.
        iats = [
            iat
            for iat in iats
            if iat >= 0
        ]

        iat_mean = (
            statistics.mean(iats)
            if iats
            else 0.0
        )

        iat_std = (
            statistics.stdev(iats)
            if len(iats) > 1
            else 0.0
        )

        # =========================================================
        # 9-14. WI-FI FEATURES
        # =========================================================

        retries = sum(
            1
            for p in window_packets
            if p.get("retry") is True
        )

        retry_rate = (
            retries / packet_count
            if packet_count > 0
            else 0.0
        )

        protected_count = sum(
            1
            for p in window_packets
            if p.get("protected") is True
        )

        protected_rate = (
            protected_count / packet_count
            if packet_count > 0
            else 0.0
        )

        # IEEE 802.11 management frame:
        # Type 0 = Management
        #
        # Beacon          = subtype 8
        # Disassociation  = subtype 10
        # Deauthentication= subtype 12
        # Probe Response   = subtype 5

        beacon_count = sum(
            1
            for p in window_packets
            if (
                p.get("frame_type") == 0
                and p.get("frame_subtype") == 8
            )
        )

        deauth_count = sum(
            1
            for p in window_packets
            if (
                p.get("frame_type") == 0
                and p.get("frame_subtype") == 12
            )
        )

        disassoc_count = sum(
            1
            for p in window_packets
            if (
                p.get("frame_type") == 0
                and p.get("frame_subtype") == 10
            )
        )

        probe_resp_count = sum(
            1
            for p in window_packets
            if (
                p.get("frame_type") == 0
                and p.get("frame_subtype") == 5
            )
        )

        beacon_rate = (
            beacon_count / dur
        )

        deauth_rate = (
            deauth_count / dur
        )

        disassoc_rate = (
            disassoc_count / dur
        )

        probe_response_rate = (
            probe_resp_count / dur
        )

        # =========================================================
        # 15-18. RADIO FEATURES
        # =========================================================

        signals = [
            float(p.get("signal"))
            for p in window_packets
            if p.get("signal") is not None
        ]

        signal_mean = (
            statistics.mean(signals)
            if signals
            else 0.0
        )

        signal_std = (
            statistics.stdev(signals)
            if len(signals) > 1
            else 0.0
        )

        data_rates = [
            float(p.get("data_rate"))
            for p in window_packets
            if p.get("data_rate") is not None
        ]

        data_rate_mean = (
            statistics.mean(data_rates)
            if data_rates
            else 0.0
        )

        data_rate_std = (
            statistics.stdev(data_rates)
            if len(data_rates) > 1
            else 0.0
        )

        # =========================================================
        # 19-21. IDENTITY FEATURES
        # =========================================================

        bssids = {
            p.get("bssid")
            for p in window_packets
            if p.get("bssid")
        }

        unique_bssid_count = float(
            len(bssids)
        )

        sources = {
            p.get("source")
            for p in window_packets
            if p.get("source")
        }

        unique_source_count = float(
            len(sources)
        )

        destinations = {
            p.get("destination")
            for p in window_packets
            if p.get("destination")
        }

        unique_destination_count = float(
            len(destinations)
        )

        # =========================================================
        # 22-25. DNS FEATURES
        # =========================================================
        #
        # IMPORTANT:
        #
        # The adapter provides:
        #
        #     dns = True / False
        #
        # and:
        #
        #     dns_response = True / False
        #
        # Therefore we must NOT use:
        #
        #     p.get("dns") is not None
        #
        # because False is also "not None".
        # =========================================================

        dns_packets = [
            p
            for p in window_packets
            if p.get("dns") is True
        ]

        dns_request_packets = [
            p
            for p in dns_packets
            if p.get("dns_response") is not True
        ]

        dns_response_packets = [
            p
            for p in dns_packets
            if p.get("dns_response") is True
        ]

        dns_request_count = float(
            len(dns_request_packets)
        )

        dns_response_count = float(
            len(dns_response_packets)
        )

        # ---------------------------------------------------------
        # DNS latency
        # ---------------------------------------------------------

        latencies = []

        request_map = {}

        for packet in dns_request_packets:

            transaction_id = packet.get(
                "dns_transaction_id"
            )

            timestamp = packet.get(
                "timestamp"
            )

            if (
                transaction_id is not None
                and timestamp is not None
            ):
                request_map[
                    transaction_id
                ] = float(timestamp)

        for response in dns_response_packets:

            transaction_id = response.get(
                "dns_transaction_id"
            )

            timestamp = response.get(
                "timestamp"
            )

            if (
                transaction_id is None
                or timestamp is None
            ):
                continue

            if transaction_id not in request_map:
                continue

            latency = (
                float(timestamp)
                - request_map[transaction_id]
            )

            if latency >= 0:
                latencies.append(latency)

        dns_latency_mean = (
            statistics.mean(latencies)
            if latencies
            else 0.0
        )

        dns_latency_std = (
            statistics.stdev(latencies)
            if len(latencies) > 1
            else 0.0
        )

        # =========================================================
        # 26-28. TCP FEATURES
        # =========================================================

        syn_count = sum(
            1
            for p in window_packets
            if p.get("tcp_syn") is True
        )

        syn_rate = (
            syn_count / dur
        )

        rst_count = sum(
            1
            for p in window_packets
            if p.get("tcp_rst") is True
        )

        rst_rate = (
            rst_count / dur
        )

        retrans_count = sum(
            1
            for p in window_packets
            if p.get("tcp_retransmission") is True
        )

        retransmission_rate = (
            retrans_count / packet_count
            if packet_count > 0
            else 0.0
        )

        # =========================================================
        # 29-30. UDP FEATURES
        # =========================================================
        #
        # The adapter uses:
        #
        #     0 = not UDP
        #
        # Therefore we must NOT test:
        #
        #     is not None
        #
        # because the default value 0 is still not None.
        # =========================================================

        udp_packets = [
            p
            for p in window_packets
            if (
                p.get(
                    "udp_destination_port",
                    0
                ) or 0
            ) > 0
        ]

        udp_packet_rate = (
            float(len(udp_packets)) / dur
        )

        udp_ports = {
            p.get("udp_destination_port")
            for p in udp_packets
            if (
                p.get(
                    "udp_destination_port",
                    0
                ) or 0
            ) > 0
        }

        unique_udp_destination_ports = float(
            len(udp_ports)
        )

        # =========================================================
        # FINAL FEATURE DICTIONARY
        # =========================================================

        return {
            "packet_count": float(packet_count),
            "byte_count": float(byte_count),
            "packets_per_second": float(packets_per_second),
            "bytes_per_second": float(bytes_per_second),

            "packet_size_mean": float(packet_size_mean),
            "packet_size_std": float(packet_size_std),

            "iat_mean": float(iat_mean),
            "iat_std": float(iat_std),

            "retry_rate": float(retry_rate),
            "protected_rate": float(protected_rate),

            "beacon_rate": float(beacon_rate),
            "deauth_rate": float(deauth_rate),
            "disassoc_rate": float(disassoc_rate),
            "probe_response_rate": float(probe_response_rate),

            "signal_mean": float(signal_mean),
            "signal_std": float(signal_std),

            "data_rate_mean": float(data_rate_mean),
            "data_rate_std": float(data_rate_std),

            "unique_bssid_count": float(
                unique_bssid_count
            ),
            "unique_source_count": float(
                unique_source_count
            ),
            "unique_destination_count": float(
                unique_destination_count
            ),

            "dns_request_count": float(
                dns_request_count
            ),
            "dns_response_count": float(
                dns_response_count
            ),
            "dns_latency_mean": float(
                dns_latency_mean
            ),
            "dns_latency_std": float(
                dns_latency_std
            ),

            "syn_rate": float(syn_rate),
            "rst_rate": float(rst_rate),

            "retransmission_rate": float(
                retransmission_rate
            ),

            "udp_packet_rate": float(
                udp_packet_rate
            ),
            "unique_udp_destination_ports": float(
                unique_udp_destination_ports
            ),
        }
