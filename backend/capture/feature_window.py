
import math
import statistics
from collections import defaultdict, deque
from typing import List, Dict, Any, Optional


# Stable order of the 30 operational features.
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

# Diagnostic metadata; not part of the 30-feature vector.
WIFI_AVAILABILITY_NAMES = [
    "wifi_retry_available",
    "wifi_protected_available",
    "wifi_management_frames_available",
    "wifi_signal_available",
    "wifi_data_rate_available",
    "wifi_bssid_available",
]


def _number(value):
    """Return a finite float, or None if unavailable or invalid."""
    if value is None or value == "":
        return None

    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return None

    return result if math.isfinite(result) else None


def _first_available(packet, *keys):
    """Return the first non-empty value."""
    for key in keys:
        value = packet.get(key)
        if value is not None and value != "":
            return value
    return None


def _flag(value):
    """Interpret common Boolean and numeric flag representations."""
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        number = _number(value)
        return number is not None and number != 0

    if isinstance(value, str):
        return value.strip().lower() in {
            "1", "1.0", "true", "yes", "set"
        }

    return False


def _mean(values):
    return float(statistics.mean(values)) if values else 0.0


def _std(values):
    """Sample standard deviation; zero with fewer than two values."""
    return float(statistics.stdev(values)) if len(values) > 1 else 0.0


def _flag_value(packet, primary_key, alternate_key=None):
    value = packet.get(primary_key)

    if value is None and alternate_key:
        value = packet.get(alternate_key)

    return _flag(value)


def _dns_match_key(packet, transaction_id, is_response):
    """Build a DNS transaction key using endpoints when available."""
    source = packet.get("source")
    destination = packet.get("destination")

    if source in (None, "") or destination in (None, ""):
        return (str(transaction_id),)

    if is_response:
        requester = str(destination)
        resolver = str(source)
    else:
        requester = str(source)
        resolver = str(destination)

    return (str(transaction_id), requester, resolver)


def _dns_latencies(dns_packets):
    """Match responses to earlier unmatched DNS requests."""
    timestamped_packets = []

    for packet in dns_packets:
        transaction_id = packet.get("dns_transaction_id")
        timestamp = _number(packet.get("timestamp"))

        if transaction_id is None or timestamp is None:
            continue

        is_response = _flag(packet.get("dns_response"))

        timestamped_packets.append(
            (timestamp, str(transaction_id), is_response, packet)
        )

    timestamped_packets.sort(key=lambda item: item[0])
    pending_requests = defaultdict(deque)
    latencies = []

    for timestamp, transaction_id, is_response, packet in timestamped_packets:
        key = _dns_match_key(packet, transaction_id, is_response)

        if not is_response:
            pending_requests[key].append(timestamp)
            continue

        requests = pending_requests[key]

        while requests and requests[0] > timestamp:
            requests.popleft()

        if not requests:
            continue

        request_timestamp = requests.popleft()
        latency = timestamp - request_timestamp

        if math.isfinite(latency) and latency >= 0:
            latencies.append(latency)

    return latencies


def feature_dict_to_vector(features: Dict[str, Any]) -> List[float]:
    """
    Convert operational features into the stable 30-feature order.

    Missing or invalid values are represented as 0.0 in this vector.
    Consult availability flags before interpreting Wi-Fi measurements.
    This function does not convert to the frozen 81/82-feature schemas.
    """
    return [
        value if (value := _number(features.get(name))) is not None else 0.0
        for name in FEATURE_NAMES
    ]


class FeatureExtractor:
    """
    Extract 30 operational features and six availability flags.

    Duration:
      A positive supplied duration is used for rate denominators.
      Otherwise use the observed timestamp span, falling back to
      window_size when that span is invalid or zero.

    Rates:
      packets_per_second, bytes_per_second, management-frame rates,
      syn_rate, rst_rate and udp_packet_rate use duration.
      retry_rate, protected_rate and retransmission_rate use packet_count.

    retransmission_rate counts marked retransmission packets divided
    by all packets, not only TCP packets.

    Missing Wi-Fi measurements produce numeric zero summaries, with
    availability flags indicating whether measurements were observed.
    """

    def __init__(self, window_size: float = 1.0):
        value = _number(window_size)
        self.window_size = (
            value if value is not None and value > 0 else 1.0
        )

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
                p.get("retry") is not None for p in window_packets
            ),
            "wifi_protected_available": any(
                p.get("protected") is not None for p in window_packets
            ),
            "wifi_management_frames_available": any(
                p.get("frame_type") is not None
                and p.get("frame_subtype") is not None
                for p in window_packets
            ),
            "wifi_signal_available": any(
                _number(_first_available(
                    p, "signal", "radiotap.dbm_antsignal"
                )) is not None
                for p in window_packets
            ),
            "wifi_data_rate_available": any(
                _number(_first_available(
                    p, "data_rate", "radiotap.datarate"
                )) is not None
                for p in window_packets
            ),
            "wifi_bssid_available": any(
                p.get("bssid") not in (None, "")
                for p in window_packets
            ),
        }

        # Duration used for rate features.
        parsed_duration = _number(duration)

        if parsed_duration is not None and parsed_duration > 0:
            dur = parsed_duration
        else:
            valid_timestamps = [
                value
                for p in window_packets
                if (value := _number(p.get("timestamp"))) is not None
                and value > 0
            ]

            dur = (
                max(valid_timestamps) - min(valid_timestamps)
                if len(valid_timestamps) >= 2
                else self.window_size
            )

            if not math.isfinite(dur) or dur <= 0:
                dur = self.window_size

        # Packet lengths and byte totals.
        lengths = [
            value
            for p in window_packets
            if (value := _number(_first_available(
                p, "length", "frame.len"
            ))) is not None
            and value >= 0
        ]

        byte_count = sum(lengths)
        packets_per_second = packet_count / dur
        bytes_per_second = byte_count / dur
        packet_size_mean = _mean(lengths)
        packet_size_std = _std(lengths)

        # Inter-arrival times in seconds.
        timestamps = sorted(
            value
            for p in window_packets
            if (value := _number(p.get("timestamp"))) is not None
            and value > 0
        )

        iats = [
            timestamps[i] - timestamps[i - 1]
            for i in range(1, len(timestamps))
        ]
        iats = [
            value for value in iats
            if math.isfinite(value) and value >= 0
        ]

        iat_mean = _mean(iats)
        iat_std = _std(iats)

        # Wi-Fi retry and protection ratios.
        retries = sum(_flag(p.get("retry")) for p in window_packets)
        protected_count = sum(
            _flag(p.get("protected")) for p in window_packets
        )

        retry_rate = retries / packet_count
        protected_rate = protected_count / packet_count

        # Wi-Fi management frame event rates.
        def is_management_subtype(packet, subtype):
            return (
                _number(packet.get("frame_type")) == 0
                and _number(packet.get("frame_subtype")) == subtype
            )

        beacon_count = sum(
            is_management_subtype(p, 8) for p in window_packets
        )
        probe_resp_count = sum(
            is_management_subtype(p, 5) for p in window_packets
        )
        deauth_count = sum(
            is_management_subtype(p, 12) for p in window_packets
        )
        disassoc_count = sum(
            is_management_subtype(p, 10) for p in window_packets
        )

        beacon_rate = beacon_count / dur
        probe_response_rate = probe_resp_count / dur
        deauth_rate = deauth_count / dur
        disassoc_rate = disassoc_count / dur

        # Signal and data-rate summaries; units follow capture adapter.
        signals = [
            value
            for p in window_packets
            if (value := _number(_first_available(
                p, "signal", "radiotap.dbm_antsignal"
            ))) is not None
        ]

        data_rates = [
            value
            for p in window_packets
            if (value := _number(_first_available(
                p, "data_rate", "radiotap.datarate"
            ))) is not None
        ]

        signal_mean = _mean(signals)
        signal_std = _std(signals)
        data_rate_mean = _mean(data_rates)
        data_rate_std = _std(data_rates)

        # Unique addresses.
        bssids = {
            str(p["bssid"])
            for p in window_packets
            if p.get("bssid") not in (None, "")
        }
        sources = {
            str(p["source"])
            for p in window_packets
            if p.get("source") not in (None, "")
        }
        destinations = {
            str(p["destination"])
            for p in window_packets
            if p.get("destination") not in (None, "")
        }

        unique_bssid_count = float(len(bssids))
        unique_source_count = float(len(sources))
        unique_destination_count = float(len(destinations))

        # DNS request/response counts and matched latency in seconds.
        dns_packets = [
            p for p in window_packets if _flag(p.get("dns"))
        ]
        dns_request_packets = [
            p for p in dns_packets if not _flag(p.get("dns_response"))
        ]
        dns_response_packets = [
            p for p in dns_packets if _flag(p.get("dns_response"))
        ]

        dns_request_count = float(len(dns_request_packets))
        dns_response_count = float(len(dns_response_packets))

        latencies = _dns_latencies(dns_packets)
        dns_latency_mean = _mean(latencies)
        dns_latency_std = _std(latencies)

        # TCP flags and retransmission rate.
        syn_count = sum(
            _flag_value(p, "tcp_syn", "tcp.flags.syn")
            for p in window_packets
        )
        rst_count = sum(
            _flag_value(p, "tcp_rst", "tcp.flags.reset")
            for p in window_packets
        )
        retrans_count = sum(
            _flag_value(
                p, "tcp_retransmission", "tcp.analysis.retransmission"
            )
            for p in window_packets
        )

        syn_rate = syn_count / dur
        rst_rate = rst_count / dur
        retransmission_rate = retrans_count / packet_count

        # UDP packets with a valid destination port.
        udp_ports = set()
        udp_count = 0

        for packet in window_packets:
            port_number = _number(_first_available(
                packet, "udp_destination_port", "udp.dstport"
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

        # Keep result names and order aligned with FEATURE_NAMES.
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

        result.update(wifi_availability)
        return result


class CausalWindowManager:
    """Group chronologically ordered packets into causal time windows."""

    def __init__(self, window_size: float = 1.0):
        value = _number(window_size)
        self.window_size = (
            value if value is not None and value > 0 else 1.0
        )
        self.start_timestamp: Optional[float] = None
        self.current_window_id: Optional[int] = None
        self.current_packets: List[Dict[str, Any]] = []

    def _packet_timestamp(self, packet: Dict[str, Any]) -> float:
        timestamp = _number(packet.get("timestamp"))

        if timestamp is None:
            raise ValueError("Packet has a missing or invalid timestamp.")

        return timestamp

    def add_packet(
        self, packet: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Add a packet and return completed windows."""

        timestamp = self._packet_timestamp(packet)

        if self.start_timestamp is None:
            self.start_timestamp = timestamp
            self.current_window_id = 0
            self.current_packets = [packet]
            return []

        relative_time = timestamp - self.start_timestamp

        if relative_time < 0:
            raise ValueError(
                "Packet timestamp moved backwards before capture start."
            )

        window_id = int(relative_time // self.window_size)

        if window_id < self.current_window_id:
            raise ValueError(
                "Packet timestamp moved backwards across a completed window."
            )

        if window_id == self.current_window_id:
            self.current_packets.append(packet)
            return []

        completed = [{
            "window_id": self.current_window_id,
            "start_timestamp": (
                self.start_timestamp
                + self.current_window_id * self.window_size
            ),
            "end_timestamp": (
                self.start_timestamp
                + (self.current_window_id + 1) * self.window_size
            ),
            "packets": self.current_packets,
        }]

        self.current_window_id = window_id
        self.current_packets = [packet]
        return completed

    def flush(self) -> List[Dict[str, Any]]:
        """Emit the final partial window, if one exists."""

        if self.current_window_id is None or not self.current_packets:
            return []

        completed = [{
            "window_id": self.current_window_id,
            "start_timestamp": (
                self.start_timestamp
                + self.current_window_id * self.window_size
            ),
            "end_timestamp": (
                self.start_timestamp
                + (self.current_window_id + 1) * self.window_size
            ),
            "packets": self.current_packets,
        }]

        self.current_packets = []
        return completed


def extract_causal_window(
    packets: List[Dict[str, Any]],
    window_size: float = 1.0,
) -> List[Dict[str, Any]]:
    """Group chronologically ordered packets into causal time windows."""

    manager = CausalWindowManager(window_size=window_size)
    windows = []

    for packet in packets:
        windows.extend(manager.add_packet(packet))

    windows.extend(manager.flush())
    return windows
