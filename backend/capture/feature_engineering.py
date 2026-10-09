from statistics import mean, pstdev


def _safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def _safe_int(value, default=0):
    try:
        if value is None or value == "":
            return default

        return int(float(value))

    except (TypeError, ValueError):
        return default


def _mean(values):
    return mean(values) if values else 0.0


def _std(values):
    return pstdev(values) if len(values) > 1 else 0.0


class WindowFeatureEngineer:
    """
    Converts one causal packet window into engineered features.

    Input:
        A list of normalized packets produced by TSharkCapture.

    Output:
        A dictionary containing currently implemented base and
        behavioral features.

    Important:
        This class does NOT create fake values for unavailable
        Wi-Fi/radiotap information.

        The current Windows adapter captures Ethernet/IP traffic,
        so raw 802.11-specific fields may legitimately be zero.
    """

    # =============================================================
    # Basic helpers
    # =============================================================

    def _get_timestamp(self, packet):
        return _safe_float(
            packet.get("timestamp")
        )

    # =============================================================
    # Behavioral feature: IAT
    # =============================================================

    def _behavior_iat(self, packets):
        """
        Mean inter-arrival time for packets in this window.
        """

        timestamps = sorted(
            self._get_timestamp(packet)
            for packet in packets
        )

        if len(timestamps) < 2:
            return 0.0

        deltas = []

        for index in range(1, len(timestamps)):

            delta = (
                timestamps[index]
                - timestamps[index - 1]
            )

            if delta >= 0:
                deltas.append(delta)

        return _mean(deltas)

    # =============================================================
    # Behavioral feature: TCP sequence delta by flow
    # =============================================================

    def _behavior_tcp_seq_delta_flow(self, packets):
        """
        Mean TCP sequence-number delta within each directional flow.

        Flow identity:

            source
            destination
            TCP source port
            TCP destination port
        """

        previous_seq = {}
        deltas = []

        ordered_packets = sorted(
            packets,
            key=self._get_timestamp
        )

        for packet in ordered_packets:

            source = packet.get(
                "source"
            )

            destination = packet.get(
                "destination"
            )

            source_port = _safe_int(
                packet.get("tcp.srcport")
            )

            destination_port = _safe_int(
                packet.get("tcp.dstport")
            )

            sequence = packet.get(
                "tcp.seq"
            )

            # Not a usable TCP flow.
            if not source or not destination:
                continue

            if source_port == 0:
                continue

            if destination_port == 0:
                continue

            if sequence in (
                None,
                "",
                0,
                "0",
            ):
                continue

            sequence = _safe_float(
                sequence
            )

            flow = (
                str(source),
                str(destination),
                source_port,
                destination_port,
            )

            if flow in previous_seq:

                delta = (
                    sequence
                    - previous_seq[flow]
                )

                # Ignore backwards sequence movement.
                if delta >= 0:
                    deltas.append(delta)

            previous_seq[flow] = sequence

        return _mean(deltas)

    # =============================================================
    # Behavioral feature: TCP ACK delta by flow
    # =============================================================

    def _behavior_tcp_ack_delta_flow(self, packets):
        """
        Mean TCP acknowledgement-number delta within each
        directional flow.
        """

        previous_ack = {}
        deltas = []

        ordered_packets = sorted(
            packets,
            key=self._get_timestamp
        )

        for packet in ordered_packets:

            source = packet.get(
                "source"
            )

            destination = packet.get(
                "destination"
            )

            source_port = _safe_int(
                packet.get("tcp.srcport")
            )

            destination_port = _safe_int(
                packet.get("tcp.dstport")
            )

            acknowledgement = packet.get(
                "tcp.ack_raw"
            )

            if not source or not destination:
                continue

            if source_port == 0:
                continue

            if destination_port == 0:
                continue

            if acknowledgement in (
                None,
                "",
                0,
                "0",
            ):
                continue

            acknowledgement = _safe_float(
                acknowledgement
            )

            flow = (
                str(source),
                str(destination),
                source_port,
                destination_port,
            )

            if flow in previous_ack:

                delta = (
                    acknowledgement
                    - previous_ack[flow]
                )

                if delta >= 0:
                    deltas.append(delta)

            previous_ack[flow] = acknowledgement

        return _mean(deltas)

    # =============================================================
    # Behavioral feature: WLAN sequence delta by sender
    # =============================================================

    def _behavior_wlan_seq_delta_sender(self, packets):
        """
        Mean WLAN sequence-number delta for each sender.

        The current Windows capture does not expose raw 802.11
        sequence numbers, so this will normally be 0.0 here.

        It is intentionally NOT replaced with a fake value.
        """

        previous_seq = {}
        deltas = []

        ordered_packets = sorted(
            packets,
            key=self._get_timestamp
        )

        for packet in ordered_packets:

            sender = packet.get(
                "source"
            )

            sequence_value = packet.get(
                "wlan.seq"
            )

            if not sender:
                continue

            if sequence_value in (
                None,
                "",
                0,
                "0",
            ):
                continue

            sequence = _safe_float(
                sequence_value
            )

            sender = str(sender)

            if sender in previous_seq:

                delta = (
                    sequence
                    - previous_seq[sender]
                )

                if delta >= 0:
                    deltas.append(delta)

            previous_seq[sender] = sequence

        return _mean(deltas)

    # =============================================================
    # Main extraction
    # =============================================================

    def extract(self, packets):

        if not packets:
            return {}

        # ---------------------------------------------------------
        # Chronological ordering
        # ---------------------------------------------------------

        packets = sorted(
            packets,
            key=self._get_timestamp
        )

        result = {}

        packet_count = len(packets)

        # ---------------------------------------------------------
        # Packet / byte statistics
        # ---------------------------------------------------------

        lengths = [
            _safe_float(
                packet.get("frame.len")
            )
            for packet in packets
        ]

        timestamps = [
            self._get_timestamp(packet)
            for packet in packets
        ]

        result["packet_count"] = float(
            packet_count
        )

        result["byte_count"] = float(
            sum(lengths)
        )

        result["packet_size_mean"] = _mean(
            lengths
        )

        result["packet_size_std"] = _std(
            lengths
        )

        # ---------------------------------------------------------
        # IAT
        # ---------------------------------------------------------

        iats = []

        for index in range(1, len(timestamps)):

            delta = (
                timestamps[index]
                - timestamps[index - 1]
            )

            if delta >= 0:
                iats.append(delta)

        result["iat_mean"] = _mean(
            iats
        )

        result["iat_std"] = _std(
            iats
        )

        # ---------------------------------------------------------
        # WLAN retry / protected
        # ---------------------------------------------------------

        retry_count = 0
        protected_count = 0

        for packet in packets:

            retry = _safe_float(
                packet.get(
                    "wlan.fc.retry"
                )
            )

            protected = _safe_float(
                packet.get(
                    "wlan.fc.protected"
                )
            )

            if retry > 0:
                retry_count += 1

            if protected > 0:
                protected_count += 1

        result["retry_rate"] = (
            retry_count / packet_count
        )

        result["protected_rate"] = (
            protected_count / packet_count
        )

        # ---------------------------------------------------------
        # WLAN frame types
        # ---------------------------------------------------------

        frame_types = [
            _safe_int(
                packet.get("wlan.fc.type")
            )
            for packet in packets
        ]

        frame_subtypes = [
            _safe_int(
                packet.get("wlan.fc.subtype")
            )
            for packet in packets
        ]

        def frame_rate(
            type_value,
            subtype_value
        ):

            count = 0

            for frame_type, subtype in zip(
                frame_types,
                frame_subtypes
            ):

                if (
                    frame_type == type_value
                    and subtype == subtype_value
                ):
                    count += 1

            return count / packet_count

        result["beacon_rate"] = frame_rate(
            0,
            8
        )

        result["probe_response_rate"] = frame_rate(
            0,
            5
        )

        result["deauth_rate"] = frame_rate(
            0,
            12
        )

        result["disassoc_rate"] = frame_rate(
            0,
            10
        )

        # ---------------------------------------------------------
        # Signal strength
        # ---------------------------------------------------------

        signals = []

        for packet in packets:

            value = packet.get(
                "radiotap.dbm_antsignal"
            )

            if value in (
                None,
                "",
                0,
                "0",
            ):
                value = packet.get(
                    "signal"
                )

            value = _safe_float(
                value
            )

            if value != 0:
                signals.append(value)

        result["signal_mean"] = _mean(
            signals
        )

        result["signal_std"] = _std(
            signals
        )

        # ---------------------------------------------------------
        # Data rate
        # ---------------------------------------------------------

        data_rates = []

        for packet in packets:

            value = packet.get(
                "radiotap.datarate"
            )

            if value in (
                None,
                "",
                0,
                "0",
            ):
                value = packet.get(
                    "data_rate"
                )

            value = _safe_float(
                value
            )

            if value != 0:
                data_rates.append(value)

        result["data_rate_mean"] = _mean(
            data_rates
        )

        result["data_rate_std"] = _std(
            data_rates
        )

        # ---------------------------------------------------------
        # Address cardinality
        # ---------------------------------------------------------

        bssids = set()
        sources = set()
        destinations = set()

        for packet in packets:

            # These are the normalized fields from adapter.py.
            bssid = packet.get(
                "bssid"
            )

            source = packet.get(
                "source"
            )

            destination = packet.get(
                "destination"
            )

            if bssid:
                bssids.add(
                    str(bssid)
                )

            if source:
                sources.add(
                    str(source)
                )

            if destination:
                destinations.add(
                    str(destination)
                )

        result["unique_bssid_count"] = float(
            len(bssids)
        )

        result["unique_source_count"] = float(
            len(sources)
        )

        result["unique_destination_count"] = float(
            len(destinations)
        )

        # ---------------------------------------------------------
        # DNS
        # ---------------------------------------------------------

        dns_requests = 0
        dns_responses = 0

        dns_requests_by_id = {}
        dns_latencies = []

        for packet in packets:

            if not packet.get("dns"):
                continue

            transaction_id = packet.get(
                "dns_transaction_id"
            )

            timestamp = self._get_timestamp(
                packet
            )

            is_response = bool(
                packet.get(
                    "dns_response"
                )
            )

            if is_response:

                dns_responses += 1

                if transaction_id is not None:

                    transaction_id = str(
                        transaction_id
                    )

                    request_time = (
                        dns_requests_by_id.get(
                            transaction_id
                        )
                    )

                    if request_time is not None:

                        latency = (
                            timestamp
                            - request_time
                        )

                        if latency >= 0:
                            dns_latencies.append(
                                latency
                            )

            else:

                dns_requests += 1

                if transaction_id is not None:

                    dns_requests_by_id[
                        str(transaction_id)
                    ] = timestamp

        result["dns_request_count"] = float(
            dns_requests
        )

        result["dns_response_count"] = float(
            dns_responses
        )

        result["dns_latency_mean"] = _mean(
            dns_latencies
        )

        result["dns_latency_std"] = _std(
            dns_latencies
        )

        # ---------------------------------------------------------
        # TCP
        # ---------------------------------------------------------

        syn_count = 0
        rst_count = 0
        retransmission_count = 0

        for packet in packets:

            syn = _safe_float(
                packet.get(
                    "tcp.flags.syn"
                )
            )

            rst = _safe_float(
                packet.get(
                    "tcp.flags.reset"
                )
            )

            retransmission = packet.get(
                "tcp.analysis.retransmission"
            )

            if syn > 0:
                syn_count += 1

            if rst > 0:
                rst_count += 1

            if retransmission not in (
                None,
                "",
                False,
                0,
                0.0,
                "0",
                "False",
            ):
                retransmission_count += 1

        result["syn_rate"] = (
            syn_count / packet_count
        )

        result["rst_rate"] = (
            rst_count / packet_count
        )

        result["retransmission_rate"] = (
            retransmission_count
            / packet_count
        )

        # ---------------------------------------------------------
        # UDP
        # ---------------------------------------------------------

        udp_packets = []

        for packet in packets:

            src_port = packet.get(
                "udp.srcport"
            )

            dst_port = packet.get(
                "udp.dstport"
            )

            udp_length = packet.get(
                "udp.length"
            )

            has_udp = (
                src_port not in (
                    None,
                    "",
                    0,
                    "0",
                )
                or
                dst_port not in (
                    None,
                    "",
                    0,
                    "0",
                )
                or
                udp_length not in (
                    None,
                    "",
                    0,
                    "0",
                )
            )

            if has_udp:
                udp_packets.append(
                    packet
                )

        result["udp_packet_rate"] = (
            len(udp_packets)
            / packet_count
        )

        # ---------------------------------------------------------
        # Unique UDP destination ports
        # ---------------------------------------------------------

        udp_destination_ports = set()

        for packet in udp_packets:

            port = packet.get(
                "udp.dstport"
            )

            if port in (
                None,
                "",
                0,
                "0",
            ):
                continue

            port = _safe_int(
                port
            )

            if port > 0:
                udp_destination_ports.add(
                    port
                )

        result[
            "unique_udp_destination_ports"
        ] = float(
            len(udp_destination_ports)
        )

        # =========================================================
        # Behavioral features
        # =========================================================

        result["behavior_iat"] = (
            self._behavior_iat(
                packets
            )
        )

        result[
            "behavior_tcp_seq_delta_flow"
        ] = (
            self._behavior_tcp_seq_delta_flow(
                packets
            )
        )

        result[
            "behavior_tcp_ack_delta_flow"
        ] = (
            self._behavior_tcp_ack_delta_flow(
                packets
            )
        )

        result[
            "behavior_wlan_seq_delta_sender"
        ] = (
            self._behavior_wlan_seq_delta_sender(
                packets
            )
        )

        return result