
from statistics import mean, pstdev
import math


def _safe_float(value, default=0.0):
    """Convert a value to a finite float, or return default."""
    if value is None or value == "":
        return default

    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return default

    return result if math.isfinite(result) else default


def _safe_int(value, default=0):
    """Convert a value to an integer, or return default."""
    if value is None or value == "":
        return default

    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return default

    if not math.isfinite(result):
        return default

    try:
        return int(result)
    except (TypeError, ValueError, OverflowError):
        return default


def _mean(values):
    return mean(values) if values else 0.0


def _std(values):
    return pstdev(values) if len(values) > 1 else 0.0


def _numeric_value(value):
    """Return a finite float, preserving zero; return None if unavailable."""
    if value is None or value == "":
        return None

    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return None

    return result if math.isfinite(result) else None


class WindowFeatureEngineer:
    """
    Extract operational and behavioral features from normalized packets.

    Availability indicators are diagnostic only. They are not part of
    the frozen binary or multiclass ML schemas.

    A zero-valued measurement is preserved when it is explicitly present.
    Missing values are not interpreted as measured values by the
    availability diagnostics.
    """

    def _get_timestamp(self, packet):
        return _numeric_value(packet.get("timestamp"))

    def _ordered_packets(self, packets):
        """Sort packets chronologically, keeping untimestamped packets last."""
        indexed = list(enumerate(packets))

        def sort_key(item):
            index, packet = item
            timestamp = self._get_timestamp(packet)

            return (
                timestamp is None,
                timestamp if timestamp is not None else 0.0,
                index,
            )

        return [
            packet
            for _, packet in sorted(indexed, key=sort_key)
        ]

    @staticmethod
    def _field_value(packet, field):
        return _numeric_value(packet.get(field))

    @classmethod
    def _field_available(cls, packet, field):
        return cls._field_value(packet, field) is not None

    # -------------------------------------------------------------
    # Behavioral feature: inter-arrival time
    # -------------------------------------------------------------

    def _behavior_iat(self, packets):
        timestamps = [
            self._get_timestamp(packet)
            for packet in packets
        ]

        timestamps = sorted(
            timestamp
            for timestamp in timestamps
            if timestamp is not None
        )

        if len(timestamps) < 2:
            return 0.0

        deltas = [
            timestamps[i] - timestamps[i - 1]
            for i in range(1, len(timestamps))
            if timestamps[i] >= timestamps[i - 1]
        ]

        return _mean(deltas)

    # -------------------------------------------------------------
    # Behavioral feature: TCP sequence delta by directional flow
    # -------------------------------------------------------------

    def _behavior_tcp_seq_delta_flow(self, packets):
        previous_seq = {}
        deltas = []

        for packet in self._ordered_packets(packets):
            source = packet.get("source")
            destination = packet.get("destination")

            source_port = _safe_int(packet.get("tcp.srcport"))
            destination_port = _safe_int(packet.get("tcp.dstport"))

            if not source or not destination:
                continue

            if source_port <= 0 or destination_port <= 0:
                continue

            # Zero is a valid sequence value; only missing/invalid values
            # should be skipped.
            sequence = _numeric_value(packet.get("tcp.seq"))

            if sequence is None:
                continue

            flow = (
                str(source),
                str(destination),
                source_port,
                destination_port,
            )

            if flow in previous_seq:
                delta = sequence - previous_seq[flow]

                if delta >= 0:
                    deltas.append(delta)

            previous_seq[flow] = sequence

        return _mean(deltas)

    # -------------------------------------------------------------
    # Behavioral feature: TCP ACK delta by directional flow
    # -------------------------------------------------------------

    def _behavior_tcp_ack_delta_flow(self, packets):
        previous_ack = {}
        deltas = []

        for packet in self._ordered_packets(packets):
            source = packet.get("source")
            destination = packet.get("destination")

            source_port = _safe_int(packet.get("tcp.srcport"))
            destination_port = _safe_int(packet.get("tcp.dstport"))

            if not source or not destination:
                continue

            if source_port <= 0 or destination_port <= 0:
                continue

            # Zero is preserved if explicitly present. Whether the ACK
            # field is meaningful for a packet depends on TCP flags.
            acknowledgement = _numeric_value(
                packet.get("tcp.ack_raw")
            )

            if acknowledgement is None:
                continue

            flow = (
                str(source),
                str(destination),
                source_port,
                destination_port,
            )

            if flow in previous_ack:
                delta = acknowledgement - previous_ack[flow]

                if delta >= 0:
                    deltas.append(delta)

            previous_ack[flow] = acknowledgement

        return _mean(deltas)

    # -------------------------------------------------------------
    # Behavioral feature: WLAN sequence delta by sender
    # -------------------------------------------------------------

    def _behavior_wlan_seq_delta_sender(self, packets):
        previous_seq = {}
        deltas = []

        for packet in self._ordered_packets(packets):
            sender = packet.get("source")

            if not sender:
                continue

            sequence = _numeric_value(packet.get("wlan.seq"))

            if sequence is None:
                continue

            sender = str(sender)

            if sender in previous_seq:
                delta = sequence - previous_seq[sender]

                if delta >= 0:
                    deltas.append(delta)

            previous_seq[sender] = sequence

        return _mean(deltas)

    # -------------------------------------------------------------
    # Main extraction
    # -------------------------------------------------------------

    def extract(self, packets):
        if not packets:
            return {}

        packets = self._ordered_packets(packets)
        result = {}
        packet_count = len(packets)

        # Packet and byte statistics.
        lengths = [
            _safe_float(packet.get("frame.len"))
            for packet in packets
        ]

        timestamps = [
            self._get_timestamp(packet)
            for packet in packets
        ]

        valid_timestamps = sorted(
            timestamp
            for timestamp in timestamps
            if timestamp is not None
        )

        result["packet_count"] = float(packet_count)
        result["byte_count"] = float(sum(lengths))
        result["packet_size_mean"] = _mean(lengths)
        result["packet_size_std"] = _std(lengths)

        # Inter-arrival statistics. Packets without timestamps are omitted.
        iats = [
            valid_timestamps[i] - valid_timestamps[i - 1]
            for i in range(1, len(valid_timestamps))
            if valid_timestamps[i] >= valid_timestamps[i - 1]
        ]

        result["iat_mean"] = _mean(iats)
        result["iat_std"] = _std(iats)

        # Diagnostic availability indicators.
        wifi_fields = {
            "wifi_retry_available": "wlan.fc.retry",
            "wifi_protected_available": "wlan.fc.protected",
            "wifi_management_frames_available": "wlan.fc.type",
            "wifi_signal_available": "radiotap.dbm_antsignal",
            "wifi_data_rate_available": "radiotap.datarate",
            "wifi_bssid_available": "bssid",
            "wifi_sequence_available": "wlan.seq",
        }

        for output_name, field_name in wifi_fields.items():
            result[output_name] = float(
                any(
                    self._field_available(packet, field_name)
                    for packet in packets
                )
            )

        # WLAN retry and protection rates, calculated over packets
        # where the corresponding field is actually available.
        retry_values = [
            self._field_value(packet, "wlan.fc.retry")
            for packet in packets
        ]
        retry_values = [
            value for value in retry_values if value is not None
        ]

        protected_values = [
            self._field_value(packet, "wlan.fc.protected")
            for packet in packets
        ]
        protected_values = [
            value for value in protected_values if value is not None
        ]

        result["retry_rate"] = (
            sum(value > 0 for value in retry_values) / len(retry_values)
            if retry_values else 0.0
        )

        result["protected_rate"] = (
            sum(value > 0 for value in protected_values)
            / len(protected_values)
            if protected_values else 0.0
        )

        # WLAN frame subtype rates, calculated over packets where both
        # frame type and subtype are available.
        valid_frame_packets = [
            packet
            for packet in packets
            if (
                self._field_available(packet, "wlan.fc.type")
                and self._field_available(packet, "wlan.fc.subtype")
            )
        ]

        def frame_rate(type_value, subtype_value):
            if not valid_frame_packets:
                return 0.0

            count = sum(
                _safe_int(packet.get("wlan.fc.type")) == type_value
                and _safe_int(packet.get("wlan.fc.subtype")) == subtype_value
                for packet in valid_frame_packets
            )

            return count / len(valid_frame_packets)

        result["beacon_rate"] = frame_rate(0, 8)
        result["probe_response_rate"] = frame_rate(0, 5)
        result["deauth_rate"] = frame_rate(0, 12)
        result["disassoc_rate"] = frame_rate(0, 10)

        # Signal strength: preserve explicitly reported zero values.
        signals = []

        for packet in packets:
            value = self._field_value(packet, "radiotap.dbm_antsignal")

            if value is None:
                value = _numeric_value(packet.get("signal"))

            if value is not None:
                signals.append(value)

        result["signal_mean"] = _mean(signals)
        result["signal_std"] = _std(signals)

        # Data rate: preserve explicitly reported zero values.
        data_rates = []

        for packet in packets:
            value = self._field_value(packet, "radiotap.datarate")

            if value is None:
                value = _numeric_value(packet.get("data_rate"))

            if value is not None:
                data_rates.append(value)

        result["data_rate_mean"] = _mean(data_rates)
        result["data_rate_std"] = _std(data_rates)

        # Address cardinality.
        bssids = {
            str(packet["bssid"])
            for packet in packets
            if packet.get("bssid")
        }

        sources = {
            str(packet["source"])
            for packet in packets
            if packet.get("source")
        }

        destinations = {
            str(packet["destination"])
            for packet in packets
            if packet.get("destination")
        }

        result["unique_bssid_count"] = float(len(bssids))
        result["unique_source_count"] = float(len(sources))
        result["unique_destination_count"] = float(len(destinations))

        # DNS counts and transaction latency.
        dns_requests = 0
        dns_responses = 0
        dns_requests_by_id = {}
        dns_latencies = []

        for packet in packets:
            if not packet.get("dns"):
                continue

            timestamp = self._get_timestamp(packet)

            if timestamp is None:
                continue

            transaction_id = packet.get("dns_transaction_id")
            is_response = bool(packet.get("dns_response"))

            if is_response:
                dns_responses += 1

                if transaction_id is not None:
                    request_time = dns_requests_by_id.get(
                        str(transaction_id)
                    )

                    if request_time is not None:
                        latency = timestamp - request_time

                        if latency >= 0:
                            dns_latencies.append(latency)
            else:
                dns_requests += 1

                if transaction_id is not None:
                    dns_requests_by_id[str(transaction_id)] = timestamp

        result["dns_request_count"] = float(dns_requests)
        result["dns_response_count"] = float(dns_responses)
        result["dns_latency_mean"] = _mean(dns_latencies)
        result["dns_latency_std"] = _std(dns_latencies)

        # TCP rates over packets where each corresponding field exists.
        syn_values = [
            self._field_value(packet, "tcp.flags.syn")
            for packet in packets
        ]
        syn_values = [
            value for value in syn_values if value is not None
        ]

        rst_values = [
            self._field_value(packet, "tcp.flags.reset")
            for packet in packets
        ]
        rst_values = [
            value for value in rst_values if value is not None
        ]

        retransmission_values = [
            packet.get("tcp.analysis.retransmission")
            for packet in packets
            if packet.get("tcp.analysis.retransmission") is not None
            and packet.get("tcp.analysis.retransmission") != ""
        ]

        result["syn_rate"] = (
            sum(value > 0 for value in syn_values) / len(syn_values)
            if syn_values else 0.0
        )

        result["rst_rate"] = (
            sum(value > 0 for value in rst_values) / len(rst_values)
            if rst_values else 0.0
        )

        def is_true_retransmission(value):
            if isinstance(value, bool):
                return value

            if isinstance(value, (int, float)):
                return value != 0

            return str(value).strip().lower() in ("true", "1", "1.0", "yes")

        result["retransmission_rate"] = (
            sum(
                is_true_retransmission(value)
                for value in retransmission_values
            ) / len(retransmission_values)
            if retransmission_values else 0.0
        )

        # UDP packet rate: count packets with at least one usable UDP field.
        udp_packets = []

        for packet in packets:
            has_udp = any(
                self._field_available(packet, field)
                for field in (
                    "udp.srcport",
                    "udp.dstport",
                    "udp.length",
                )
            )

            if has_udp:
                udp_packets.append(packet)

        result["udp_packet_rate"] = len(udp_packets) / packet_count

        udp_destination_ports = {
            _safe_int(packet.get("udp.dstport"))
            for packet in udp_packets
            if self._field_available(packet, "udp.dstport")
            and _safe_int(packet.get("udp.dstport")) > 0
        }

        result["unique_udp_destination_ports"] = float(
            len(udp_destination_ports)
        )

        # Behavioral features.
        result["behavior_iat"] = self._behavior_iat(packets)

        result["behavior_tcp_seq_delta_flow"] = (
            self._behavior_tcp_seq_delta_flow(packets)
        )

        result["behavior_tcp_ack_delta_flow"] = (
            self._behavior_tcp_ack_delta_flow(packets)
        )

        result["behavior_wlan_seq_delta_sender"] = (
            self._behavior_wlan_seq_delta_sender(packets)
        )

        return result
