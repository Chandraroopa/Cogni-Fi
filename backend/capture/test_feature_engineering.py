
from statistics import mean, pstdev
from numbers import Real
import math


def _safe_float(value, default=0.0):
    """Convert a value to a finite float, using default when invalid."""
    if value is None or value == "":
        return default

    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return default

    return result if math.isfinite(result) else default


def _safe_int(value, default=0):
    """Convert a value to an integer, using default when invalid."""
    if value is None or value == "":
        return default

    try:
        result = int(float(value))
    except (TypeError, ValueError, OverflowError):
        return default

    return result


def _has_value(value):
    """True if a field contains a usable value, including numeric zero."""
    return value is not None and value != ""


def _mean(values):
    return mean(values) if values else 0.0


def _std(values):
    return pstdev(values) if len(values) > 1 else 0.0


class WindowFeatureEngineer:
    """
    Converts a packet window into operational and behavioral features.

    Input:
        Normalized packets produced by TSharkCapture.

    Output:
        Existing feature names plus diagnostic availability indicators.

    Availability indicators are diagnostic only. Do not append them to
    frozen ML model vectors unless the training schema changes.
    """

    # -------------------------------------------------------------
    # Basic helpers
    # -------------------------------------------------------------

    def _get_timestamp(self, packet):
        value = packet.get("timestamp")

        if not _has_value(value):
            return None

        try:
            timestamp = float(value)
        except (TypeError, ValueError, OverflowError):
            return None

        return timestamp if math.isfinite(timestamp) else None

    @staticmethod
    def _valid_numeric(value):
        if isinstance(value, bool) or not isinstance(value, Real):
            return False

        return math.isfinite(float(value))

    @staticmethod
    def _usable_field(packet, field):
        value = packet.get(field)

        if not _has_value(value):
            return False

        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            return False

        return math.isfinite(number)

    @staticmethod
    def _valid_sequence(value):
        """Accept zero; reject absent, invalid, or non-finite values."""
        if not _has_value(value):
            return None

        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            return None

        return number if math.isfinite(number) else None

    def _ordered_packets(self, packets):
        """Sort valid timestamps first, preserving input order for ties."""
        indexed = list(enumerate(packets))

        def sort_key(item):
            timestamp = self._get_timestamp(item[1])
            return (
                timestamp is None,
                timestamp if timestamp is not None else 0.0,
                item[0],
            )

        return [
            packet
            for _, packet in sorted(indexed, key=sort_key)
        ]

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

            sequence = self._valid_sequence(packet.get("tcp.seq"))

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

            acknowledgement = self._valid_sequence(
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

            sequence = self._valid_sequence(packet.get("wlan.seq"))

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

        # Packet and byte statistics
        lengths = [
            _safe_float(packet.get("frame.len"))
            for packet in packets
        ]

        valid_timestamps = [
            self._get_timestamp(packet)
            for packet in packets
        ]

        valid_timestamps = [
            timestamp
            for timestamp in valid_timestamps
            if timestamp is not None
        ]

        result["packet_count"] = float(packet_count)
        result["byte_count"] = float(sum(lengths))
        result["packet_size_mean"] = _mean(lengths)
        result["packet_size_std"] = _std(lengths)

        # Inter-arrival statistics
        iats = [
            valid_timestamps[i] - valid_timestamps[i - 1]
            for i in range(1, len(valid_timestamps))
            if valid_timestamps[i] >= valid_timestamps[i - 1]
        ]

        result["iat_mean"] = _mean(iats)
        result["iat_std"] = _std(iats)

        # Wi-Fi feature availability diagnostics
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
                    self._usable_field(packet, field_name)
                    for packet in packets
                )
            )

        # WLAN retry and protected rates
        retry_values = [
            packet.get("wlan.fc.retry")
            for packet in packets
            if self._usable_field(packet, "wlan.fc.retry")
        ]

        protected_values = [
            packet.get("wlan.fc.protected")
            for packet in packets
            if self._usable_field(packet, "wlan.fc.protected")
        ]

        result["retry_rate"] = (
            sum(_safe_float(value) > 0 for value in retry_values)
            / len(retry_values)
            if retry_values else 0.0
        )

        result["protected_rate"] = (
            sum(_safe_float(value) > 0 for value in protected_values)
            / len(protected_values)
            if protected_values else 0.0
        )

        # WLAN frame types
        valid_frame_packets = [
            packet
            for packet in packets
            if (
                self._usable_field(packet, "wlan.fc.type")
                and self._usable_field(packet, "wlan.fc.subtype")
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

        # Signal strength
        signals = []

        for packet in packets:
            value = packet.get("radiotap.dbm_antsignal")

            if not self._usable_field(packet, "radiotap.dbm_antsignal"):
                value = packet.get("signal")

            if not self._usable_field({"value": value}, "value"):
                continue

            signals.append(_safe_float(value))

        result["signal_mean"] = _mean(signals)
        result["signal_std"] = _std(signals)

        # Data rate
        data_rates = []

        for packet in packets:
            value = packet.get("radiotap.datarate")

            if not self._usable_field(packet, "radiotap.datarate"):
                value = packet.get("data_rate")

            if not self._usable_field({"value": value}, "value"):
                continue

            data_rates.append(_safe_float(value))

        result["data_rate_mean"] = _mean(data_rates)
        result["data_rate_std"] = _std(data_rates)

        # Address cardinality
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

        # DNS
        dns_requests = 0
        dns_responses = 0
        dns_requests_by_id = {}
        dns_latencies = []

        for packet in packets:
            if not packet.get("dns"):
                continue

            transaction_id = packet.get("dns_transaction_id")
            timestamp = self._get_timestamp(packet)

            if timestamp is None:
                continue

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

        # TCP
        syn_values = [
            packet.get("tcp.flags.syn")
            for packet in packets
            if self._usable_field(packet, "tcp.flags.syn")
        ]

        rst_values = [
            packet.get("tcp.flags.reset")
            for packet in packets
            if self._usable_field(packet, "tcp.flags.reset")
        ]

        retransmission_values = [
            packet.get("tcp.analysis.retransmission")
            for packet in packets
            if packet.get("tcp.analysis.retransmission") is not None
        ]

        result["syn_rate"] = (
            sum(_safe_float(value) > 0 for value in syn_values)
            / len(syn_values)
            if syn_values else 0.0
        )

        result["rst_rate"] = (
            sum(_safe_float(value) > 0 for value in rst_values)
            / len(rst_values)
            if rst_values else 0.0
        )

        result["retransmission_rate"] = (
            sum(
                str(value).strip().lower() in ("true", "1", "1.0")
                for value in retransmission_values
            )
            / len(retransmission_values)
            if retransmission_values else 0.0
        )

        # UDP
        udp_packets = []

        for packet in packets:
            has_udp = any(
                self._usable_field(packet, field)
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
            if (
                self._usable_field(packet, "udp.dstport")
                and _safe_int(packet.get("udp.dstport")) > 0
            )
        }

        result["unique_udp_destination_ports"] = float(
            len(udp_destination_ports)
        )

        # Behavioral features
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
