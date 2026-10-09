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


def feature_dict_to_vector(
    features: Dict[str, float]
) -> List[float]:
    """
    Convert the 30-feature dictionary into fixed order.
    """

    return [
        float(features.get(name, 0.0))
        for name in FEATURE_NAMES
    ]


class FeatureExtractor:
    """
    Extracts the current 30 operational/debugging features
    from one completed packet window.

    IMPORTANT:
    These 30 features are NOT the frozen 81/82 ML schemas.
    """

    def __init__(self, window_size: float = 1.0):
        self.window_size = float(window_size)

        if self.window_size <= 0:
            self.window_size = 1.0

    def extract_window_features(
        self,
        window_packets: List[Dict[str, Any]],
        duration: Optional[float] = None,
    ) -> Dict[str, float]:

        dur = (
            float(duration)
            if duration is not None
            else self.window_size
        )

        if dur <= 0:
            dur = self.window_size

        packet_count = len(window_packets)

        if packet_count == 0:
            return {
                name: 0.0
                for name in FEATURE_NAMES
            }

        # =========================================================
        # TRAFFIC
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

        # =========================================================
        # IAT
        # =========================================================

        ordered_packets = sorted(
            window_packets,
            key=lambda p: float(
                p.get("timestamp", 0.0) or 0.0
            ),
        )

        timestamps = [
            float(p.get("timestamp", 0.0) or 0.0)
            for p in ordered_packets
        ]

        iats = [
            timestamps[i] - timestamps[i - 1]
            for i in range(1, len(timestamps))
        ]

        iats = [
            value
            for value in iats
            if value >= 0
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
        # WI-FI
        # =========================================================

        retries = sum(
            1
            for p in window_packets
            if p.get("retry") is True
        )

        retry_rate = (
            retries / packet_count
            if packet_count
            else 0.0
        )

        protected_count = sum(
            1
            for p in window_packets
            if p.get("protected") is True
        )

        protected_rate = (
            protected_count / packet_count
            if packet_count
            else 0.0
        )

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

        beacon_rate = beacon_count / dur
        deauth_rate = deauth_count / dur
        disassoc_rate = disassoc_count / dur
        probe_response_rate = probe_resp_count / dur

        # =========================================================
        # RADIO
        # =========================================================

        signals = [
            float(p.get("signal", 0.0) or 0.0)
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
            float(p.get("data_rate", 0.0) or 0.0)
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
        # IDENTITY
        # =========================================================

        bssids = {
            p.get("bssid")
            for p in window_packets
            if p.get("bssid")
        }

        sources = {
            p.get("source")
            for p in window_packets
            if p.get("source")
        }

        destinations = {
            p.get("destination")
            for p in window_packets
            if p.get("destination")
        }

        unique_bssid_count = float(len(bssids))
        unique_source_count = float(len(sources))
        unique_destination_count = float(len(destinations))

        # =========================================================
        # DNS
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
        # TCP
        # =========================================================

        syn_count = sum(
            1
            for p in window_packets
            if p.get("tcp_syn") is True
        )

        rst_count = sum(
            1
            for p in window_packets
            if p.get("tcp_rst") is True
        )

        retrans_count = sum(
            1
            for p in window_packets
            if p.get("tcp_retransmission") is True
        )

        syn_rate = syn_count / dur
        rst_rate = rst_count / dur

        retransmission_rate = (
            retrans_count / packet_count
            if packet_count
            else 0.0
        )

        # =========================================================
        # UDP
        # =========================================================

        udp_packets = [
            p
            for p in window_packets
            if (
                p.get(
                    "udp_destination_port",
                    0,
                )
                or 0
            ) > 0
        ]

        udp_packet_rate = (
            len(udp_packets) / dur
        )

        udp_ports = {
            p.get("udp_destination_port")
            for p in udp_packets
            if (
                p.get(
                    "udp_destination_port",
                    0,
                )
                or 0
            ) > 0
        }

        unique_udp_destination_ports = float(
            len(udp_ports)
        )

        # =========================================================
        # RESULT
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
            "probe_response_rate": float(
                probe_response_rate
            ),

            "signal_mean": float(signal_mean),
            "signal_std": float(signal_std),

            "data_rate_mean": float(data_rate_mean),
            "data_rate_std": float(data_rate_std),

            "unique_bssid_count": unique_bssid_count,
            "unique_source_count": unique_source_count,
            "unique_destination_count": (
                unique_destination_count
            ),

            "dns_request_count": dns_request_count,
            "dns_response_count": dns_response_count,
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
            "unique_udp_destination_ports": (
                unique_udp_destination_ports
            ),
        }


class CausalWindowManager:
    """
    Creates causal time windows from incoming packets.

    Frozen timing contract:

        window_id =
            floor(
                (timestamp - start_timestamp)
                / window_size
            )

    start_timestamp is the timestamp of the first
    chronologically processed packet.

    A completed window is emitted only when a packet
    belonging to a later window arrives.

    No future packet is included in an earlier window.
    """

    def __init__(
        self,
        window_size: float = 1.0,
    ):
        self.window_size = float(window_size)

        if self.window_size <= 0:
            self.window_size = 1.0

        self.start_timestamp: Optional[float] = None
        self.current_window_id: Optional[int] = None
        self.current_packets: List[
            Dict[str, Any]
        ] = []

    def _packet_timestamp(
        self,
        packet: Dict[str, Any],
    ) -> float:

        return float(
            packet.get(
                "timestamp",
                0.0,
            )
            or 0.0
        )

    def add_packet(
        self,
        packet: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Add one packet.

        Returns zero or more completed windows.

        Normally:
            one packet -> zero completed windows

        When packet crosses a boundary:
            one packet -> one or more completed windows
        """

        timestamp = self._packet_timestamp(
            packet
        )

        # ---------------------------------------------------------
        # First packet establishes start_timestamp.
        # ---------------------------------------------------------

        if self.start_timestamp is None:

            self.start_timestamp = timestamp

            self.current_window_id = 0

            self.current_packets = [
                packet
            ]

            return []

        # ---------------------------------------------------------
        # Calculate causal window ID.
        # ---------------------------------------------------------

        relative_time = (
            timestamp
            - self.start_timestamp
        )

        window_id = int(
            relative_time
            // self.window_size
        )

        # Protect against packets arriving slightly
        # out of chronological order.
        if (
            self.current_window_id is not None
            and window_id < self.current_window_id
        ):
            raise ValueError(
                "Packet timestamp moved backwards "
                "across an already completed window."
            )

        # ---------------------------------------------------------
        # Same window.
        # ---------------------------------------------------------

        if window_id == self.current_window_id:

            self.current_packets.append(
                packet
            )

            return []

        # ---------------------------------------------------------
        # New window.
        # ---------------------------------------------------------

        completed = []

        if self.current_window_id is not None:

            completed.append(
                {
                    "window_id": (
                        self.current_window_id
                    ),
                    "start_timestamp": (
                        self.start_timestamp
                        + (
                            self.current_window_id
                            * self.window_size
                        )
                    ),
                    "end_timestamp": (
                        self.start_timestamp
                        + (
                            (
                                self.current_window_id
                                + 1
                            )
                            * self.window_size
                        )
                    ),
                    "packets": (
                        self.current_packets
                    ),
                }
            )

        # ---------------------------------------------------------
        # Move directly to the packet's window.
        #
        # Empty windows are NOT fabricated here.
        # ---------------------------------------------------------

        self.current_window_id = window_id

        self.current_packets = [
            packet
        ]

        return completed

    def flush(self) -> List[Dict[str, Any]]:
        """
        Flush the current incomplete window.

        This is used during shutdown or capture stop.
        """

        if (
            self.current_window_id is None
            or not self.current_packets
        ):
            return []

        completed = [
            {
                "window_id": (
                    self.current_window_id
                ),
                "start_timestamp": (
                    self.start_timestamp
                    + (
                        self.current_window_id
                        * self.window_size
                    )
                ),
                "end_timestamp": (
                    self.start_timestamp
                    + (
                        (
                            self.current_window_id
                            + 1
                        )
                        * self.window_size
                    )
                ),
                "packets": (
                    self.current_packets
                ),
            }
        ]

        self.current_packets = []

        return completed


def extract_causal_window(
    packets: List[Dict[str, Any]],
    window_size: float = 1.0,
) -> List[Dict[str, Any]]:
    """
    Convenience function.

    Takes chronologically ordered packets and returns
    completed causal windows.
    """

    manager = CausalWindowManager(
        window_size=window_size
    )

    windows = []

    for packet in packets:

        windows.extend(
            manager.add_packet(packet)
        )

    windows.extend(
        manager.flush()
    )

    return windows