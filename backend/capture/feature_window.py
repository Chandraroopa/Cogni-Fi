
import math
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


WIFI_AVAILABILITY_NAMES = [
    "wifi_retry_available",
    "wifi_protected_available",
    "wifi_management_frames_available",
    "wifi_signal_available",
    "wifi_data_rate_available",
    "wifi_bssid_available",
]


def _number(value):
    """Return a finite float, or None if the value is unavailable/invalid."""
    if value is None or value == "":
        return None

    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return None

    return result if math.isfinite(result) else None


def _first_available(packet, *keys):
    """Return the first non-None, non-empty value among candidate keys."""
    for key in keys:
        value = packet.get(key)
        if value is not None and value != "":
            return value
    return None


def _flag(value):
    """Interpret common Boolean/numeric protocol flag representations."""
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return math.isfinite(float(value)) and value != 0

    if isinstance(value, str):
        return value.strip().lower() in {
            "1", "1.0", "true", "yes", "set"
        }

    return False


def _mean(values):
    return statistics.mean(values) if values else 0.0


def _std(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def _flag_value(packet, primary_key, alternate_key=None):
    """Read a flag from normalized or alternate field names."""
    value = packet.get(primary_key)

    if value is None and alternate_key:
        value = packet.get(alternate_key)

    return _flag(value)


def feature_dict_to_vector(
    features: Dict[str, Any],
) -> List[float]:
    """
    Convert the 30 operational features into their fixed order.

    This is not a conversion to either frozen 81/82-feature ML schema.
    """
    vector = []

    for name in FEATURE_NAMES:
        value = _number(features.get(name))

        # Preserve the historical vector helper's zero default.
        vector.append(value if value is not None else 0.0)

    return vector


class FeatureExtractor:
    """
    Extract 30 operational features plus six Wi-Fi availability flags.

    Availability flags are diagnostic metadata. They are not part of
    FEATURE_NAMES and are not included in the 30-feature vector.

    Important:
    - A numeric zero is a valid measurement when explicitly present.
    - Missing lengths are excluded from packet-size statistics.
    - Missing Wi-Fi measurements are not considered available.
    - This class does not produce the frozen 81/82-feature ML schemas.
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

        # ---------------------------------------------------------
        # WI-FI FIELD AVAILABILITY
        # ---------------------------------------------------------

        wifi_availability = {
            "wifi_retry_available": any(
                p.get("retry") is not None
                for p in window_packets
            ),
            "wifi_protected_available": any(
                p.get("protected") is not None
                for p in window_packets
            ),
            "wifi_management_frames_available": any(
                p.get("frame_type") is not None
                and p.get("frame_subtype") is not None
                for p in window_packets
            ),
            "wifi_signal_available": any(
                _first_available(
                    p, "signal", "radiotap.dbm_antsignal"
                ) is not None
                for p in window_packets
            ),
            "wifi_data_rate_available": any(
                _first_available(
                    p, "data_rate", "radiotap.datarate"
                ) is not None
                for p in window_packets
            ),
            "wifi_bssid_available": any(
                p.get("bssid") is not None
                for p in window_packets
            ),
        }

        # ---------------------------------------------------------
        # DURATION
        # ---------------------------------------------------------

        parsed_duration = _number(duration)

        if parsed_duration is not None and parsed_duration > 0:
            dur = parsed_duration
        else:
            timestamps_for_duration = [
                _number(p.get("timestamp"))
                for p in window_packets
            ]

            valid_timestamps = [
                timestamp
                for timestamp in timestamps_for_duration
                if timestamp is not None and timestamp > 0
            ]

            if len(valid_timestamps) >= 2:
                dur = max(valid_timestamps) - min(valid_timestamps)
            else:
                dur = self.window_size

            if not math.isfinite(dur) or dur <= 0:
                dur = self.window_size

        # ---------------------------------------------------------
        # TRAFFIC AND PACKET LENGTHS
        # ---------------------------------------------------------

        lengths = []

        for packet in window_packets:
            raw_length = _first_available(
                packet, "length", "frame.len"
            )
            length = _number(raw_length)

            if length is not None and length >= 0:
                lengths.append(length)

        byte_count = sum(lengths)
        packets_per_second = packet_count / dur
        bytes_per_second = byte_count / dur

        packet_size_mean = _mean(lengths)
        packet_size_std = _std(lengths)

        # ---------------------------------------------------------
        # INTER-ARRIVAL TIME
        # ---------------------------------------------------------

        timestamps = []

        for packet in window_packets:
            timestamp = _number(packet.get("timestamp"))

            if timestamp is not None and timestamp > 0:
                timestamps.append(timestamp)

        timestamps.sort()

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

        # ---------------------------------------------------------
        # WI-FI RETRY AND PROTECTION
        # ---------------------------------------------------------

        retries = sum(
            _flag(p.get("retry"))
            for p in window_packets
        )

        protected_count = sum(
            _flag(p.get("protected"))
            for p in window_packets
        )

        retry_rate = retries / packet_count
        protected_rate = protected_count / packet_count

        # ---------------------------------------------------------
        # WI-FI MANAGEMENT FRAME RATES
        # ---------------------------------------------------------

        def is_management_subtype(packet, subtype):
            frame_type = _number(packet.get("frame_type"))
            frame_subtype = _number(packet.get("frame_subtype"))

            return (
                frame_type == 0
                and frame_subtype == subtype
            )

        beacon_count = sum(
            is_management_subtype(p, 8)
            for p in window_packets
        )

        probe_resp_count = sum(
            is_management_subtype(p, 5)
            for p in window_packets
        )

        deauth_count = sum(
            is_management_subtype(p, 12)
            for p in window_packets
        )

        disassoc_count = sum(
            is_management_subtype(p, 10)
            for p in window_packets
        )

        beacon_rate = beacon_count / dur
        probe_response_rate = probe_resp_count / dur
        deauth_rate = deauth_count / dur
        disassoc_rate = disassoc_count / dur

        # ---------------------------------------------------------
        # RADIO SIGNAL AND DATA RATE
        # ---------------------------------------------------------

        signals = []

        for packet in window_packets:
            value = _number(_first_available(
                packet, "signal", "radiotap.dbm_antsignal"
            ))

            if value is not None:
                signals.append(value)

        signal_mean = _mean(signals)
        signal_std = _std(signals)

        data_rates = []

        for packet in window_packets:
            value = _number(_first_available(
                packet, "data_rate", "radiotap.datarate"
            ))

            if value is not None:
                data_rates.append(value)

        data_rate_mean = _mean(data_rates)
        data_rate_std = _std(data_rates)

        # ---------------------------------------------------------
        # ADDRESS CARDINALITY
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # DNS COUNTS AND LATENCY
        # ---------------------------------------------------------

        dns_packets = [
            p for p in window_packets
            if _flag(p.get("dns"))
        ]

        dns_request_packets = [
            p for p in dns_packets
            if not _flag(p.get("dns_response"))
        ]

        dns_response_packets = [
            p for p in dns_packets
            if _flag(p.get("dns_response"))
        ]

        dns_request_count = float(len(dns_request_packets))
        dns_response_count = float(len(dns_response_packets))

        request_map = {}
        latencies = []

        for packet in dns_request_packets:
            transaction_id = packet.get("dns_transaction_id")
            timestamp = _number(packet.get("timestamp"))

            if transaction_id is None or timestamp is None:
                continue

            request_map[str(transaction_id)] = timestamp

        for packet in dns_response_packets:
            transaction_id = packet.get("dns_transaction_id")
            timestamp = _number(packet.get("timestamp"))

            if transaction_id is None or timestamp is None:
                continue

            request_timestamp = request_map.get(str(transaction_id))

            if request_timestamp is None:
                continue

            latency = timestamp - request_timestamp

            if math.isfinite(latency) and latency >= 0:
                latencies.append(latency)

        dns_latency_mean = _mean(latencies)
        dns_latency_std = _std(latencies)

        # ---------------------------------------------------------
        # TCP FLAGS AND RETRANSMISSION
        # ---------------------------------------------------------

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
                p,
                "tcp_retransmission",
                "tcp.analysis.retransmission",
            )
            for p in window_packets
        )

        # Preserve the existing definition: SYN/RST events per second,
        # and retransmission-marked packets divided by all window packets.
        syn_rate = syn_count / dur
        rst_rate = rst_count / dur
        retransmission_rate = retrans_count / packet_count

        # ---------------------------------------------------------
        # UDP
        # ---------------------------------------------------------

        udp_packets = []
        udp_ports = set()

        for packet in window_packets:
            raw_port = _first_available(
                packet, "udp_destination_port", "udp.dstport"
            )
            port_number = _number(raw_port)

            if (
                port_number is not None
                and port_number.is_integer()
                and 1 <= port_number <= 65535
            ):
                udp_packets.append(packet)
                udp_ports.add(int(port_number))

        udp_packet_rate = len(udp_packets) / dur
        unique_udp_destination_ports = float(len(udp_ports))

        # ---------------------------------------------------------
        # RESULT: preserve the established 30 feature names
        # ---------------------------------------------------------

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
            "unique_udp_destination_ports": (
                unique_udp_destination_ports
            ),
        }

        result.update(wifi_availability)
        return result


class CausalWindowManager:
    """
    Create causal time windows from incoming packets.

    A completed window is emitted when a packet from a later window
    arrives. Empty windows are not fabricated. Input packets must be
    timestamped and arrive chronologically.
    """

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
            raise ValueError(
                "Packet has a missing or invalid timestamp."
            )

        return timestamp

    def add_packet(
        self,
        packet: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Add a packet and return any newly completed windows."""

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

        if (
            self.current_window_id is not None
            and window_id < self.current_window_id
        ):
            raise ValueError(
                "Packet timestamp moved backwards across a completed window."
            )

        if window_id == self.current_window_id:
            self.current_packets.append(packet)
            return []

        completed = []

        if self.current_window_id is not None:
            completed.append({
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
            })

        self.current_window_id = window_id
        self.current_packets = [packet]

        return completed

    def flush(self) -> List[Dict[str, Any]]:
        """Emit the current partial window, if it contains packets."""

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
