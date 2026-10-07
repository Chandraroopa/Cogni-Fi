import statistics
import math
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
    """Converts a 30-feature dictionary into a fixed-order list consumable by the ML model."""
    return [float(features.get(name, 0.0)) for name in FEATURE_NAMES]


class FeatureExtractor:
    """Groups normalized packets into time windows and extracts the 30 Cognifi behavioral features."""

    def __init__(self, window_size: float = 1.0):
        self.window_size = window_size

    def extract_window_features(self, window_packets: List[Dict[str, Any]], duration: Optional[float] = None) -> Dict[str, float]:
        dur = duration if duration is not None else self.window_size
        if dur <= 0:
            dur = 1.0

        packet_count = len(window_packets)
        
        if packet_count == 0:
            # Empty window consistent zero/default convention
            return {name: 0.0 for name in FEATURE_NAMES}

        # 1-8. Traffic Features
        lengths = [p.get("length", 0) for p in window_packets]
        byte_count = sum(lengths)
        packets_per_second = packet_count / dur
        bytes_per_second = byte_count / dur

        packet_size_mean = statistics.mean(lengths) if lengths else 0.0
        packet_size_std = statistics.stdev(lengths) if len(lengths) > 1 else 0.0

        # Inter-arrival times (IAT)
        timestamps = sorted([p.get("timestamp", 0.0) for p in window_packets])
        iats = [timestamps[i] - timestamps[i - 1] for i in range(1, len(timestamps))] if len(timestamps) > 1 else []
        iat_mean = statistics.mean(iats) if iats else 0.0
        iat_std = statistics.stdev(iats) if len(iats) > 1 else 0.0

        # 9-14. Wi-Fi Features
        retries = sum(1 for p in window_packets if p.get("retry") is True)
        retry_rate = retries / packet_count if packet_count > 0 else 0.0

        protected_count = sum(1 for p in window_packets if p.get("protected") is True)
        protected_rate = protected_count / packet_count if packet_count > 0 else 0.0

        # Management frames based on IEEE 802.11 subtypes (Type 0 = Management)
        # Beacon = subtype 8, Deauth = subtype 12, Disassoc = subtype 10, Probe Response = subtype 5
        beacon_count = sum(1 for p in window_packets if p.get("frame_type") == 0 and p.get("frame_subtype") == 8)
        deauth_count = sum(1 for p in window_packets if p.get("frame_type") == 0 and p.get("frame_subtype") == 12)
        disassoc_count = sum(1 for p in window_packets if p.get("frame_type") == 0 and p.get("frame_subtype") == 10)
        probe_resp_count = sum(1 for p in window_packets if p.get("frame_type") == 0 and p.get("frame_subtype") == 5)

        beacon_rate = beacon_count / dur
        deauth_rate = deauth_count / dur
        disassoc_rate = disassoc_count / dur
        probe_response_rate = probe_resp_count / dur

        # 15-18. Radio Features
        signals = [p["signal"] for p in window_packets if p.get("signal") is not None]
        signal_mean = statistics.mean(signals) if signals else 0.0
        signal_std = statistics.stdev(signals) if len(signals) > 1 else 0.0

        data_rates = [p["data_rate"] for p in window_packets if p.get("data_rate") is not None]
        data_rate_mean = statistics.mean(data_rates) if data_rates else 0.0
        data_rate_std = statistics.stdev(data_rates) if len(data_rates) > 1 else 0.0

        # 19-21. Identity Features
        bssids = {p["bssid"] for p in window_packets if p.get("bssid")}
        unique_bssid_count = float(len(bssids))

        sources = {p["source"] for p in window_packets if p.get("source")}
        unique_source_count = float(len(sources))

        destinations = {p["destination"] for p in window_packets if p.get("destination")}
        unique_destination_count = float(len(destinations))

        # 22-25. DNS Features
        dns_requests = [p for p in window_packets if p.get("dns") is not None]
        dns_request_count = float(len(dns_requests))
        # Assuming response is tracked or matched by transaction ID in a comprehensive context
        dns_responses = [p for p in window_packets if p.get("dns_transaction_id") is not None and p.get("dns") is None]
        dns_response_count = float(len(dns_responses))

        # Latency mock matching if available
        latencies = []
        req_map = {p.get("dns_transaction_id"): p.get("timestamp") for p in dns_requests if p.get("dns_transaction_id")}
        for resp in dns_responses:
            tx_id = resp.get("dns_transaction_id")
            if tx_id in req_map:
                lat = resp.get("timestamp", 0.0) - req_map[tx_id]
                if lat >= 0:
                    latencies.append(lat)

        dns_latency_mean = statistics.mean(latencies) if latencies else 0.0
        dns_latency_std = statistics.stdev(latencies) if len(latencies) > 1 else 0.0

        # 26-28. TCP Features
        syn_count = sum(1 for p in window_packets if p.get("tcp_syn") is True)
        syn_rate = syn_count / dur

        rst_count = sum(1 for p in window_packets if p.get("tcp_rst") is True)
        rst_rate = rst_count / dur

        retrans_count = sum(1 for p in window_packets if p.get("tcp_retransmission") is True)
        retransmission_rate = retrans_count / packet_count if packet_count > 0 else 0.0

        # 29-30. UDP Features
        udp_packets = [p for p in window_packets if p.get("udp_destination_port") is not None]
        udp_packet_rate = float(len(udp_packets)) / dur
        udp_ports = {p["udp_destination_port"] for p in udp_packets}
        unique_udp_destination_ports = float(len(udp_ports))

        return {
            "packet_count": float(packet_count),
            "byte_count": float(byte_count),
            "packets_per_second": packets_per_second,
            "bytes_per_second": bytes_per_second,
            "packet_size_mean": packet_size_mean,
            "packet_size_std": packet_size_std,
            "iat_mean": iat_mean,
            "iat_std": iat_std,
            "retry_rate": retry_rate,
            "protected_rate": protected_rate,
            "beacon_rate": beacon_rate,
            "deauth_rate": deauth_rate,
            "disassoc_rate": disassoc_rate,
            "probe_response_rate": probe_response_rate,
            "signal_mean": signal_mean,
            "signal_std": signal_std,
            "data_rate_mean": data_rate_mean,
            "data_rate_std": data_rate_std,
            "unique_bssid_count": unique_bssid_count,
            "unique_source_count": unique_source_count,
            "unique_destination_count": unique_destination_count,
            "dns_request_count": dns_request_count,
            "dns_response_count": dns_response_count,
            "dns_latency_mean": dns_latency_mean,
            "dns_latency_std": dns_latency_std,
            "syn_rate": syn_rate,
            "rst_rate": rst_rate,
            "retransmission_rate": retransmission_rate,
            "udp_packet_rate": udp_packet_rate,
            "unique_udp_destination_ports": unique_udp_destination_ports,
        }