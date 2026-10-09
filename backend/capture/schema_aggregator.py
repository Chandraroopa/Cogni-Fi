from typing import Dict, List, Optional


class SchemaFeatureAggregator:
    """
    Aggregates packet-level fields into the frozen ML schema-derived
    feature names.

    Important semantic rule:

        None = field absent from this packet
        0    = field was actually present and its value is zero

    Missing packet fields are NOT converted to zero before aggregation.

    For mean/std/count:
        only genuinely available numeric values are included.

    For presence:
        the feature is 1 if the relevant field/layer was present
        in at least one packet in the window.

    For active:
        the feature is 1 if at least one packet has the relevant
        active flag set.
    """

    # =========================================================
    # BASIC HELPERS
    # =========================================================

    @staticmethod
    def _number(value) -> Optional[float]:
        """
        Convert a value to float.

        None, empty strings and invalid values are treated as
        unavailable rather than zero.
        """
        if value is None:
            return None

        if isinstance(value, bool):
            return float(value)

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _values(
        cls,
        packets: List[Dict],
        field_name: str,
    ) -> List[float]:
        """
        Return only genuinely available numeric values.
        """
        values = []

        for packet in packets:
            value = cls._number(
                packet.get(field_name)
            )

            if value is not None:
                values.append(value)

        return values

    @classmethod
    def _mean(
        cls,
        packets: List[Dict],
        field_name: str,
    ) -> float:
        values = cls._values(
            packets,
            field_name,
        )

        if not values:
            return 0.0

        return sum(values) / len(values)

    @classmethod
    def _std(
        cls,
        packets: List[Dict],
        field_name: str,
    ) -> float:
        values = cls._values(
            packets,
            field_name,
        )

        if len(values) <= 1:
            return 0.0

        mean = sum(values) / len(values)

        variance = sum(
            (value - mean) ** 2
            for value in values
        ) / len(values)

        return variance ** 0.5

    @classmethod
    def _count(
        cls,
        packets: List[Dict],
        field_name: str,
    ) -> float:
        """
        Count packets where the field is genuinely available.
        """
        values = cls._values(
            packets,
            field_name,
        )

        return float(len(values))

    @staticmethod
    def _present(
        packets: List[Dict],
        field_name: str,
    ) -> float:
        """
        Return 1 if the field is present in at least one packet.

        None means absent.

        A real numeric 0 still counts as present.
        """
        for packet in packets:
            if field_name in packet:
                value = packet.get(field_name)

                if value is not None:
                    return 1.0

        return 0.0

    @classmethod
    def _active(
        cls,
        packets: List[Dict],
        field_name: str,
    ) -> float:
        """
        Return 1 if the field is present and truthy in at least
        one packet.
        """
        for packet in packets:
            value = packet.get(field_name)

            if value is None:
                continue

            numeric = cls._number(value)

            if numeric is not None and numeric != 0:
                return 1.0

            if isinstance(value, str):
                if value.lower() in {
                    "true",
                    "yes",
                    "set",
                    "1",
                }:
                    return 1.0

        return 0.0

    # =========================================================
    # AGGREGATION
    # =========================================================

    def aggregate(
        self,
        packets: List[Dict],
    ) -> Dict[str, float]:
        """
        Produce schema-derived aggregate features for one
        completed causal window.

        The output contains aggregate names used by the frozen
        multiclass schema and diagnostic schema processing.

        It does NOT invent unavailable values.
        """

        if not packets:
            return {}

        features: Dict[str, float] = {}

        # =====================================================
        # RADIOTAP
        # =====================================================

        features[
            "radiotap.dbm_antsignal_mean"
        ] = self._mean(
            packets,
            "radiotap.dbm_antsignal",
        )

        features[
            "radiotap.dbm_antsignal_std"
        ] = self._std(
            packets,
            "radiotap.dbm_antsignal",
        )

        # =====================================================
        # COUNTS
        # =====================================================

        count_fields = [
            "wlan.tag.length",
            "data.len",
            "tcp.analysis.rto_frame",
            "tcp.time_delta",
            "tcp.time_relative",
            "udp.dstport",
            "udp.srcport",
            "http.content_length",
            "tcp.option_len",
            "ip.proto",
            "ip.ttl",
            "ip.version",
        ]

        for field_name in count_fields:
            features[
                f"{field_name}__count"
            ] = self._count(
                packets,
                field_name,
            )

        # =====================================================
        # TCP MEANS
        # =====================================================

        features[
            "tcp.time_delta__mean"
        ] = self._mean(
            packets,
            "tcp.time_delta",
        )

        features[
            "tcp.time_relative__mean"
        ] = self._mean(
            packets,
            "tcp.time_relative",
        )

        features[
            "udp.dstport__mean"
        ] = self._mean(
            packets,
            "udp.dstport",
        )

        features[
            "udp.srcport__mean"
        ] = self._mean(
            packets,
            "udp.srcport",
        )

        features[
            "udp.length__mean"
        ] = self._mean(
            packets,
            "udp.length",
        )

        features[
            "udp.time_relative__mean"
        ] = self._mean(
            packets,
            "udp.time_relative",
        )

        features[
            "udp.time_delta__mean"
        ] = self._mean(
            packets,
            "udp.time_delta",
        )

        features[
            "http.content_length__mean"
        ] = self._mean(
            packets,
            "http.content_length",
        )

        # =====================================================
        # TCP ACTIVE FLAGS
        # =====================================================

        features[
            "tcp.flags.syn__active"
        ] = self._active(
            packets,
            "tcp.flags.syn",
        )

        features[
            "tcp.flags.ack__active"
        ] = self._active(
            packets,
            "tcp.flags.ack",
        )

        features[
            "tcp.flags.fin__active"
        ] = self._active(
            packets,
            "tcp.flags.fin",
        )

        features[
            "tcp.flags.push__active"
        ] = self._active(
            packets,
            "tcp.flags.push",
        )

        # =====================================================
        # PRESENCE FEATURES
        # =====================================================

        presence_fields = [
            "tcp.analysis.retransmission",
            "arp",
            "ssdp",
            "http.request.method",
            "tls.record.version",
            "ip.version",
            "tcp.analysis",
            "tcp.analysis.flags",
            "tcp.option_len",
            "tcp.flags.syn",
            "tcp.flags.ack",
            "tcp.flags.fin",
            "tcp.flags.push",
            "tcp.flags.reset",
            "http.request.version",
            "http.content_type",
            "http.content_length",
            "ssh.direction",
        ]

        for field_name in presence_fields:
            # Prefer the explicit normalized presence field
            # when one exists.
            explicit_presence_name = (
                f"{field_name}__present"
            )

            if any(
                explicit_presence_name in packet
                for packet in packets
            ):
                values = [
                    packet.get(
                        explicit_presence_name
                    )
                    for packet in packets
                ]

                features[
                    explicit_presence_name
                ] = 1.0 if any(
                    value not in (None, 0, 0.0, False)
                    for value in values
                ) else 0.0

            else:
                features[
                    explicit_presence_name
                ] = self._present(
                    packets,
                    field_name,
                )

        # =====================================================
        # TCP OPTION LENGTH
        # =====================================================

        features[
            "tcp.option_len__mean"
        ] = self._mean(
            packets,
            "tcp.option_len",
        )

        features[
            "tcp.option_len__std"
        ] = self._std(
            packets,
            "tcp.option_len",
        )

        features[
            "tcp.option_len__count"
        ] = self._count(
            packets,
            "tcp.option_len",
        )

        # =====================================================
        # TCP TIME
        # =====================================================

        features[
            "tcp.time_delta__std"
        ] = self._std(
            packets,
            "tcp.time_delta",
        )

        features[
            "tcp.time_relative__std"
        ] = self._std(
            packets,
            "tcp.time_relative",
        )

        features[
            "tcp.time_relative__count"
        ] = self._count(
            packets,
            "tcp.time_relative",
        )

        # =====================================================
        # IP PROTOCOL
        # =====================================================

        features[
            "ip.proto__mean"
        ] = self._mean(
            packets,
            "ip.proto",
        )

        features[
            "ip.proto__std"
        ] = self._std(
            packets,
            "ip.proto",
        )

        features[
            "ip.proto__count"
        ] = self._count(
            packets,
            "ip.proto",
        )

        # =====================================================
        # IP TTL
        # =====================================================

        features[
            "ip.ttl__mean"
        ] = self._mean(
            packets,
            "ip.ttl",
        )

        features[
            "ip.ttl__std"
        ] = self._std(
            packets,
            "ip.ttl",
        )

        features[
            "ip.ttl__count"
        ] = self._count(
            packets,
            "ip.ttl",
        )

        # =====================================================
        # IP VERSION
        # =====================================================

        features[
            "ip.version__mean"
        ] = self._mean(
            packets,
            "ip.version",
        )

        features[
            "ip.version__std"
        ] = self._std(
            packets,
            "ip.version",
        )

        features[
            "ip.version__count"
        ] = self._count(
            packets,
            "ip.version",
        )

        # =====================================================
        # HTTP CONTENT LENGTH
        # =====================================================

        features[
            "http.content_length__mean"
        ] = self._mean(
            packets,
            "http.content_length",
        )

        features[
            "http.content_length__std"
        ] = self._std(
            packets,
            "http.content_length",
        )

        return features


# =============================================================
# CONVENIENCE FUNCTION
# =============================================================

def aggregate_schema_features(
    packets: List[Dict],
) -> Dict[str, float]:
    """
    Convenience wrapper.
    """
    aggregator = SchemaFeatureAggregator()
    return aggregator.aggregate(packets)