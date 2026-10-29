
from collections import defaultdict
import math
from typing import Any, Dict, List, Optional, Tuple


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

WIFI_AVAILABILITY_NAMES = [
    "wifi_retry_available",
    "wifi_protected_available",
    "wifi_management_frames_available",
    "wifi_signal_available",
    "wifi_data_rate_available",
    "wifi_bssid_available",
]


def _number(value: Any) -> Optional[float]:
    """Convert a finite numeric value to float."""
    if value is None or isinstance(value, bool):
        return None

    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return None

    return result if math.isfinite(result) else None


def _first_available(
    packet: Dict[str, Any],
    *keys: str,
) -> Any:
    """Return the first present, non-None packet field."""
    for key in keys:
        value = packet.get(key)
        if value is not None:
            return value
    return None


def _flag(value: Any) -> bool:
    """Safely interpret common boolean representations."""
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return value != 0

    if isinstance(value, str):
        return value.strip().lower() in {
            "1", "true", "yes", "on"
        }

    return False


def _flag_value(packet: Dict[str, Any], *keys: str) -> bool:
    return _flag(_first_available(packet, *keys))


def _mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def _std(values: List[float]) -> float:
    """Population standard deviation."""
    if not values:
        return 0.0

    mean_value = _mean(values)
    variance = sum(
        (value - mean_value) ** 2 for value in values
    ) / len(values)

    return float(math.sqrt(max(variance, 0.0)))


def _dns_transaction_id(packet: Dict[str, Any]) -> Optional[str]:
    value = _first_available(
        packet,
        "dns_id",
        "dns.id",
        "dns_transaction_id",
        "transaction_id",
    )

    if value is None:
        return None

    return str(value)


def _dns_is_packet(packet: Dict[str, Any]) -> bool:
    """Recognize DNS packets from normalized or TShark-style fields."""
    if "dns" in packet:
        return _flag(packet.get("dns"))

    return any(
        key in packet
        for key in (
            "dns_id",
            "dns.id",
            "dns_response",
            "dns.flags.response",
            "dns_transaction_id",
        )
    )


def _dns_is_response(packet: Dict[str, Any]) -> bool:
    return _flag_value(
        packet,
        "dns_response",
        "dns.flags.response",
    )


def _dns_latencies(
    packets: List[Dict[str, Any]],
) -> List[float]:
    """
    Calculate DNS request-to-response latencies in seconds.

    Packets should contain timestamps and, when available, a DNS
    transaction ID. Requests and responses are paired using their
    transaction ID and reversed source/destination endpoints.

    If transaction IDs are unavailable, requests are paired FIFO by
    endpoint tuple. Unmatched packets are ignored.
    """
    pending = defaultdict(list)
    latencies = []

    ordered_packets = sorted(
        packets,
        key=lambda p: _number(p.get("timestamp"))
        if _number(p.get("timestamp")) is not None
        else float("inf"),
    )

    for packet in ordered_packets:
        if not _dns_is_packet(packet):
            continue

        timestamp = _number(packet.get("timestamp"))
        if timestamp is None or timestamp <= 0:
            continue

        source = str(
            _first_available(packet, "source", "ip.src", "ipv6.src")
            or ""
        )
        destination = str(
            _first_available(
                packet, "destination", "ip.dst", "ipv6.dst"
            )
            or ""
        )

        transaction_id = _dns_transaction_id(packet)

        if transaction_id is not None:
            key = (transaction_id, source, destination)
        else:
            key = ("no-id", source, destination)

        if not _dns_is_response(packet):
            pending[key].append(timestamp)
            continue

        # A response travels in the opposite direction to its request.
        request_key = (
            transaction_id,
            destination,
            source,
        ) if transaction_id is not None else (
            "no-id",
            destination,
            source,
        )

        requests = pending.get(request_key)
        if not requests:
            continue

        request_timestamp = requests.pop(0)
        latency = timestamp - request_timestamp

        if math.isfinite(latency) and latency >= 0:
            latencies.append(float(latency))

    return latencies


class DNSLatencyTracker:
    """Track DNS requests across feature windows."""

    def __init__(self) -> None:
        self.pending = defaultdict(list)

    def process(
        self,
        dns_packets: List[Dict[str, Any]],
    ) -> List[float]:
        latencies = []

        ordered_packets = sorted(
            dns_packets,
            key=lambda p: _number(p.get("timestamp"))
            if _number(p.get("timestamp")) is not None
            else float("inf"),
        )

        for packet in ordered_packets:
            timestamp = _number(packet.get("timestamp"))
            if timestamp is None or timestamp <= 0:
                continue

            source = str(
                _first_available(
                    packet, "source", "ip.src", "ipv6.src"
                ) or ""
            )
            destination = str(
                _first_available(
                    packet, "destination", "ip.dst", "ipv6.dst"
                ) or ""
            )

            transaction_id = _dns_transaction_id(packet)

            if transaction_id is not None:
                key = (transaction_id, source, destination)
            else:
                key = ("no-id", source, destination)

            if not _dns_is_response(packet):
                self.pending[key].append(timestamp)
                continue

            request_key = (
                transaction_id,
                destination,
                source,
            ) if transaction_id is not None else (
                "no-id",
                destination,
                source,
            )

            requests = self.pending.get(request_key)
            if not requests:
                continue

            request_timestamp = requests.pop(0)
            latency = timestamp - request_timestamp

            if math.isfinite(latency) and latency >= 0:
                latencies.append(float(latency))

        return latencies


class CausalWindowManager:
    """Split packets into fixed-duration windows."""

    def __init__(self, window_size: float = 1.0) -> None:
        if not math.isfinite(window_size) or window_size <= 0:
            raise ValueError("window_size must be positive")

        self.window_size = float(window_size)
        self.capture_start: Optional[float] = None
        self.current_window_id: Optional[int] = None
        self.current_packets: List[Dict[str, Any]] = []

    def add_packet(
        self,
        packet: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        timestamp = _number(packet.get("timestamp"))
        if timestamp is None or timestamp <= 0:
            return []

        if self.capture_start is None:
            self.capture_start = timestamp
            self.current_window_id = 0

        window_id = max(
            0,
            int((timestamp - self.capture_start) / self.window_size),
        )

        completed = []

        if self.current_window_id is None:
            self.current_window_id = window_id

        while window_id > self.current_window_id:
            start = (
                self.capture_start
                + self.current_window_id * self.window_size
            )

            completed.append({
                "window_id": self.current_window_id,
                "start_timestamp": start,
                "end_timestamp": start + self.window_size,
                "duration": self.window_size,
                "packets": list(self.current_packets),
            })

            self.current_packets = []
            self.current_window_id += 1

        self.current_packets.append(packet)
        return completed

    def flush(
        self,
        stop_timestamp: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Return the remaining partial window, if it contains packets."""
        if (
            self.capture_start is None
            or self.current_window_id is None
            or not self.current_packets
        ):
            self.current_packets = []
            return []

        start = (
            self.capture_start
            + self.current_window_id * self.window_size
        )

        last_packet_timestamp = max(
            (
                _number(packet.get("timestamp")) or start
                for packet in self.current_packets
            ),
            default=start,
        )

        stop = _number(stop_timestamp)
        if stop is None or stop <= 0:
            stop = last_packet_timestamp

        end = min(
            max(stop, last_packet_timestamp),
            start + self.window_size,
        )
        duration = max(end - start, 0.0)

        completed = [{
            "window_id": self.current_window_id,
            "start_timestamp": start,
            "end_timestamp": end,
            "duration": duration,
            "packets": list(self.current_packets),
        }]

        self.current_packets = []
        return completed


class FeatureExtractor:
    """Extract the fixed 30-feature model input from packet windows."""

    def __init__(self, window_size: float = 1.0) -> None:
        if not math.isfinite(window_size) or window_size <= 0:
            raise ValueError("window_size must be positive")

        self.window_size = float(window_size)
        self.dns_latency_tracker = DNSLatencyTracker()

    def extract_window_features(
        self,
        window_packets: List[Dict[str, Any]],
        duration: Optional[float] = None,
    ) -> Dict[str, Any]:

        packet_count = len(window_packets)

        if packet_count == 0:
            result = {name: 0.0 for name in FEATURE_NAMES}
            result.update({
                name: False for name in WIFI_AVAILABILITY_NAMES
            })
            return result

        wifi_availability = {
            "wifi_retry_available": any(
                packet.get("retry") is not None
                for packet in window_packets
            ),
            "wifi_protected_available": any(
                packet.get("protected") is not None
                for packet in window_packets
            ),
            "wifi_management_frames_available": any(
                packet.get("frame_type") is not None
                and packet.get("frame_subtype") is not None
                for packet in window_packets
            ),
            "wifi_signal_available": any(
                _number(_first_available(
                    packet, "signal", "radiotap.dbm_antsignal"
                )) is not None
                for packet in window_packets
            ),
            "wifi_data_rate_available": any(
                _number(_first_available(
                    packet, "data_rate", "radiotap.datarate"
                )) is not None
                for packet in window_packets
            ),
            "wifi_bssid_available": any(
                packet.get("bssid") not in (None, "")
                for packet in window_packets
            ),
        }

        parsed_duration = _number(duration)

        if parsed_duration is not None and parsed_duration > 0:
            dur = parsed_duration
        else:
            timestamps_for_duration = [
                value
                for packet in window_packets
                if (value := _number(packet.get("timestamp")))
                is not None and value > 0
            ]

            dur = (
                max(timestamps_for_duration)
                - min(timestamps_for_duration)
                if len(timestamps_for_duration) >= 2
                else self.window_size
            )

            if not math.isfinite(dur) or dur <= 0:
                dur = self.window_size

        lengths = [
            value
            for packet in window_packets
            if (value := _number(_first_available(
                packet, "length", "frame.len"
            ))) is not None and value >= 0
        ]

        byte_count = sum(lengths)
        packets_per_second = packet_count / dur
        bytes_per_second = byte_count / dur
        packet_size_mean = _mean(lengths)
        packet_size_std = _std(lengths)

        timestamps = sorted(
            value
            for packet in window_packets
            if (value := _number(packet.get("timestamp")))
            is not None and value > 0
        )

        iats = [
            timestamps[index] - timestamps[index - 1]
            for index in range(1, len(timestamps))
        ]
        iats = [
            value for value in iats
            if math.isfinite(value) and value >= 0
        ]

        iat_mean = _mean(iats)
        iat_std = _std(iats)

        retries = sum(
            _flag(packet.get("retry"))
            for packet in window_packets
        )
        protected_count = sum(
            _flag(packet.get("protected"))
            for packet in window_packets
        )

        retry_rate = retries / packet_count
        protected_rate = protected_count / packet_count

        def is_management_subtype(
            packet: Dict[str, Any],
            subtype: int,
        ) -> bool:
            return (
                _number(packet.get("frame_type")) == 0
                and _number(packet.get("frame_subtype")) == subtype
            )

        beacon_count = sum(
            is_management_subtype(packet, 8)
            for packet in window_packets
        )
        probe_response_count = sum(
            is_management_subtype(packet, 5)
            for packet in window_packets
        )
        deauth_count = sum(
            is_management_subtype(packet, 12)
            for packet in window_packets
        )
        disassoc_count = sum(
            is_management_subtype(packet, 10)
            for packet in window_packets
        )

        beacon_rate = beacon_count / dur
        probe_response_rate = probe_response_count / dur
        deauth_rate = deauth_count / dur
        disassoc_rate = disassoc_count / dur

        signals = [
            value
            for packet in window_packets
            if (value := _number(_first_available(
                packet, "signal", "radiotap.dbm_antsignal"
            ))) is not None
        ]

        data_rates = [
            value
            for packet in window_packets
            if (value := _number(_first_available(
                packet, "data_rate", "radiotap.datarate"
            ))) is not None
        ]

        signal_mean = _mean(signals)
        signal_std = _std(signals)
        data_rate_mean = _mean(data_rates)
        data_rate_std = _std(data_rates)

        bssids = {
            str(packet["bssid"])
            for packet in window_packets
            if packet.get("bssid") not in (None, "")
        }
        sources = {
            str(packet["source"])
            for packet in window_packets
            if packet.get("source") not in (None, "")
        }
        destinations = {
            str(packet["destination"])
            for packet in window_packets
            if packet.get("destination") not in (None, "")
        }

        # These three counts must be defined before the result dictionary.
        unique_bssid_count = float(len(bssids))
        unique_source_count = float(len(sources))
        unique_destination_count = float(len(destinations))

        dns_packets = [
            packet
            for packet in window_packets
            if _dns_is_packet(packet)
        ]

        dns_request_packets = [
            packet for packet in dns_packets
            if not _dns_is_response(packet)
        ]
        dns_response_packets = [
            packet for packet in dns_packets
            if _dns_is_response(packet)
        ]

        dns_request_count = float(len(dns_request_packets))
        dns_response_count = float(len(dns_response_packets))

        latencies = self.dns_latency_tracker.process(dns_packets)
        dns_latency_mean = _mean(latencies)
        dns_latency_std = _std(latencies)

        syn_count = sum(
            _flag_value(packet, "tcp_syn", "tcp.flags.syn")
            for packet in window_packets
        )
        rst_count = sum(
            _flag_value(packet, "tcp_rst", "tcp.flags.reset")
            for packet in window_packets
        )
        retransmission_count = sum(
            _flag_value(
                packet,
                "tcp_retransmission",
                "tcp.analysis.retransmission",
            )
            for packet in window_packets
        )

        syn_rate = syn_count / dur
        rst_rate = rst_count / dur
        retransmission_rate = retransmission_count / packet_count

        udp_ports = set()
        udp_count = 0

        for packet in window_packets:
            port_number = _number(_first_available(
                packet,
                "udp_destination_port",
                "udp.dstport",
            ))

            if (
                port_number is not None
                and port_number.is_integer()
                and 1 <= port_number <= 65535
            ):
                udp_count += 1
                udp_ports.add(int(port_number))

        udp_packet_rate = udp_count / dur
        unique_udp_destination_ports = float(len(udp_ports))

        result = {
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
            "unique_bssid_count": unique_bssid_count,
            "unique_source_count": unique_source_count,
            "unique_destination_count": unique_destination_count,
            "dns_request_count": dns_request_count,
            "dns_response_count": dns_response_count,
            "dns_latency_mean": float(dns_latency_mean),
            "dns_latency_std": float(dns_latency_std),
            "syn_rate": float(syn_rate),
            "rst_rate": float(rst_rate),
            "retransmission_rate": float(retransmission_rate),
            "udp_packet_rate": float(udp_packet_rate),
            "unique_udp_destination_ports": unique_udp_destination_ports,
        }

        # Keep the model feature contract stable.
        result = {name: result[name] for name in FEATURE_NAMES}
        result.update(wifi_availability)

        return result

def feature_dict_to_vector(
    features: Dict[str, Any],
) -> List[float]:
    """Convert a feature dictionary into the ordered 30-feature vector."""
    vector = []

    for name in FEATURE_NAMES:
        value = _number(features.get(name))
        vector.append(value if value is not None else 0.0)

    return vector
