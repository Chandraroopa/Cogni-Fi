import subprocess
import json
from datetime import datetime


def _value(layer, key, default=None):
    """Safely get a value from a TShark layer."""
    if not isinstance(layer, dict):
        return default

    value = layer.get(key)

    if value in (None, ""):
        return default

    return value


def _float(value, default=None):
    """Convert a value to float without turning missing values into zero."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _int(value, default=None):
    """Convert a value to int without turning missing values into zero."""
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def _bool(value):
    """Safely convert a TShark value to bool."""
    if isinstance(value, bool):
        return value

    if value is None:
        return False

    return str(value).lower() in {
        "1",
        "true",
        "yes",
        "set",
    }


def _timestamp(packet_dict, frame):
    """
    Prefer TShark frame.time_epoch when available.

    Falls back to EK top-level millisecond timestamp.
    """

    raw_epoch = _value(
        frame,
        "frame_frame_time_epoch",
        None,
    )

    if raw_epoch:
        try:
            iso = str(raw_epoch).replace("Z", "+00:00")
            return datetime.fromisoformat(iso).timestamp()
        except (ValueError, TypeError):
            pass

    raw = packet_dict.get("timestamp")

    if raw not in (None, ""):
        try:
            value = float(raw)

            if value > 10_000_000_000:
                return value / 1000.0

            return value

        except (ValueError, TypeError):
            pass

    return 0.0


def normalize_packet(packet_dict):
    """
    Convert TShark -T ek output into the normalized packet format.

    Important semantic rule:

        Missing TShark field -> None

        Actual TShark value of 0 -> 0

    This distinction is required by the feature aggregation layer.
    A missing UDP field must not be confused with a real UDP value of 0.
    """

    layers = packet_dict.get("layers", {})

    if not isinstance(layers, dict):
        layers = {}

    frame = layers.get("frame", {})
    eth = layers.get("eth", {})
    ip = layers.get("ip", {})
    ipv6 = layers.get("ipv6", {})
    tcp = layers.get("tcp", {})
    udp = layers.get("udp", {})
    dns = layers.get("dns", {})
    arp = layers.get("arp", {})
    wlan = layers.get("wlan", {})
    radiotap = layers.get("radiotap", {})
    wlan_radio = layers.get("wlan_radio", {})
    tls = layers.get("tls", {})
    http = layers.get("http", {})
    ssdp = layers.get("ssdp", {})
    llc = layers.get("llc", {})

    # =========================================================
    # LAYER PRESENCE
    # =========================================================

    frame_present = bool(frame)
    eth_present = bool(eth)
    ip_present = bool(ip)
    ipv6_present = bool(ipv6)
    tcp_present = bool(tcp)
    udp_present = bool(udp)
    dns_present = bool(dns)
    arp_present = bool(arp)
    wlan_present = bool(wlan)
    radiotap_present = bool(radiotap)
    wlan_radio_present = bool(wlan_radio)
    tls_present = bool(tls)
    http_present = bool(http)
    ssdp_present = bool(ssdp)
    llc_present = bool(llc)

    # =========================================================
    # TIMESTAMP
    # =========================================================

    timestamp = _timestamp(packet_dict, frame)

    # =========================================================
    # FRAME
    # =========================================================

    length = _int(
        _value(
            frame,
            "frame_frame_len",
            None,
        )
    )

    frame_time_delta = _float(
        _value(
            frame,
            "frame_frame_time_delta",
            None,
        )
    )

    frame_time_delta_displayed = _float(
        _value(
            frame,
            "frame_frame_time_delta_displayed",
            None,
        )
    )

    frame_time_relative = _float(
        _value(
            frame,
            "frame_frame_time_relative",
            None,
        )
    )

    # =========================================================
    # ETHERNET
    # =========================================================

    eth_source = _value(
        eth,
        "eth_eth_src",
        None,
    )

    eth_destination = _value(
        eth,
        "eth_eth_dst",
        None,
    )

    # =========================================================
    # IPv4 / IPv6
    #
    # IMPORTANT:
    # We do not silently convert IPv6 values into IPv4 fields.
    # The frozen ML semantics must not be invented here.
    # =========================================================

    ip_source = _value(
        ip,
        "ip_ip_src",
        None,
    )

    ip_destination = _value(
        ip,
        "ip_ip_dst",
        None,
    )

    ipv6_source = _value(
        ipv6,
        "ipv6_ipv6_src",
        None,
    )

    ipv6_destination = _value(
        ipv6,
        "ipv6_ipv6_dst",
        None,
    )

    source = (
        ip_source
        or ipv6_source
        or eth_source
        or None
    )

    destination = (
        ip_destination
        or ipv6_destination
        or eth_destination
        or None
    )

    ip_proto = _int(
        _value(
            ip,
            "ip_ip_proto",
            None,
        )
    )

    ip_ttl = _int(
        _value(
            ip,
            "ip_ip_ttl",
            None,
        )
    )

    ip_version = _int(
        _value(
            ip,
            "ip_ip_version",
            None,
        )
    )

    # =========================================================
    # TCP
    # =========================================================

    tcp_srcport = _int(
        _value(
            tcp,
            "tcp_tcp_srcport",
            None,
        )
    )

    tcp_dstport = _int(
        _value(
            tcp,
            "tcp_tcp_dstport",
            None,
        )
    )

    tcp_seq = _int(
        _value(
            tcp,
            "tcp_tcp_seq",
            None,
        )
    )

    tcp_seq_raw = _int(
        _value(
            tcp,
            "tcp_tcp_seq_raw",
            None,
        )
    )

    tcp_ack = _int(
        _value(
            tcp,
            "tcp_tcp_ack",
            None,
        )
    )

    tcp_ack_raw = _int(
        _value(
            tcp,
            "tcp_tcp_ack_raw",
            None,
        )
    )

    tcp_time_delta = _float(
        _value(
            tcp,
            "tcp_tcp_time_delta",
            None,
        )
    )

    tcp_time_relative = _float(
        _value(
            tcp,
            "tcp_tcp_time_relative",
            None,
        )
    )

    tcp_option_len = _int(
        _value(
            tcp,
            "tcp_tcp_hdr_len",
            None,
        )
    )

    tcp_syn = _bool(
        _value(
            tcp,
            "tcp_tcp_flags_syn",
            None,
        )
    )

    tcp_ack_flag = _bool(
        _value(
            tcp,
            "tcp_tcp_flags_ack",
            None,
        )
    )

    tcp_fin = _bool(
        _value(
            tcp,
            "tcp_tcp_flags_fin",
            None,
        )
    )

    tcp_push = _bool(
        _value(
            tcp,
            "tcp_tcp_flags_push",
            None,
        )
    )

    tcp_rst = _bool(
        _value(
            tcp,
            "tcp_tcp_flags_reset",
            None,
        )
    )

    tcp_retransmission = any(
        _bool(
            _value(
                tcp,
                key,
                None,
            )
        )
        for key in (
            "tcp_analysis_retransmission",
            "tcp_analysis_fast_retransmission",
            "tcp_analysis_lost_segment",
        )
    )

    tcp_analysis_present = (
        "tcp_tcp_analysis" in tcp
        and tcp.get("tcp_tcp_analysis") is not None
    )

    tcp_analysis_flags_present = any(
        key.startswith("tcp_tcp_analysis_")
        for key in tcp
    )

    # =========================================================
    # UDP
    # =========================================================

    udp_srcport = _int(
        _value(
            udp,
            "udp_udp_srcport",
            None,
        )
    )

    udp_dstport = _int(
        _value(
            udp,
            "udp_udp_dstport",
            None,
        )
    )

    udp_length = _int(
        _value(
            udp,
            "udp_udp_length",
            None,
        )
    )

    udp_time_delta = _float(
        _value(
            udp,
            "udp_udp_time_delta",
            None,
        )
    )

    udp_time_relative = _float(
        _value(
            udp,
            "udp_udp_time_relative",
            None,
        )
    )

    # =========================================================
    # DNS
    # =========================================================

    dns_transaction_id = _value(
        dns,
        "dns_dns_id",
        None,
    )

    dns_response = _bool(
        _value(
            dns,
            "dns_dns_flags_response",
            None,
        )
    )

    # =========================================================
    # ARP
    # =========================================================

    arp_opcode = _int(
        _value(
            arp,
            "arp_arp_opcode",
            None,
        )
    )

    arp_src_proto_ipv4 = _value(
        arp,
        "arp_arp_src_proto_ipv4",
        None,
    )

    arp_dst_proto_ipv4 = _value(
        arp,
        "arp_arp_dst_proto_ipv4",
        None,
    )

    # =========================================================
    # 802.11
    # =========================================================

    frame_type = _int(
        _value(
            wlan,
            "wlan_wlan_fc_type",
            None,
        )
    )

    frame_subtype = _int(
        _value(
            wlan,
            "wlan_wlan_fc_subtype",
            None,
        )
    )

    retry = _bool(
        _value(
            wlan,
            "wlan_wlan_fc_retry",
            None,
        )
    )

    protected = _bool(
        _value(
            wlan,
            "wlan_wlan_fc_protected",
            None,
        )
    )

    wlan_duration = _float(
        _value(
            wlan,
            "wlan_wlan_duration",
            None,
        )
    )

    wlan_seq = _int(
        _value(
            wlan,
            "wlan_wlan_seq",
            None,
        )
    )

    bssid = _value(
        wlan,
        "wlan_wlan_bssid",
        None,
    )

    wlan_tag_length = _int(
        _value(
            wlan,
            "wlan_wlan_tag_length",
            None,
        )
    )

    # =========================================================
    # RADIOTAP
    # =========================================================

    signal = _float(
        _value(
            radiotap,
            "radiotap_radiotap_dbm_antsignal",
            None,
        )
    )

    data_rate = _float(
        _value(
            radiotap,
            "radiotap_radiotap_datarate",
            None,
        )
    )

    radio_frequency = _float(
        _value(
            radiotap,
            "radiotap_radiotap_channel_freq",
            None,
        )
    )

    radio_channel_ofdm = _float(
        _value(
            radiotap,
            "radiotap_radiotap_channel_flags_ofdm",
            None,
        )
    )

    radiotap_length = _float(
        _value(
            radiotap,
            "radiotap_radiotap_length",
            None,
        )
    )

    # =========================================================
    # WLAN RADIO
    # =========================================================

    wlan_radio_signal = _float(
        _value(
            wlan_radio,
            "wlan_radio_wlan_radio_signal_dbm",
            None,
        )
    )

    wlan_radio_data_rate = _float(
        _value(
            wlan_radio,
            "wlan_radio_wlan_radio_data_rate",
            None,
        )
    )

    wlan_radio_duration = _float(
        _value(
            wlan_radio,
            "wlan_radio_wlan_radio_duration",
            None,
        )
    )

    wlan_radio_phy = _value(
        wlan_radio,
        "wlan_radio_wlan_radio_phy",
        None,
    )

    wlan_radio_channel = _float(
        _value(
            wlan_radio,
            "wlan_radio_wlan_radio_channel",
            None,
        )
    )

    wlan_radio_frequency = _float(
        _value(
            wlan_radio,
            "wlan_radio_wlan_radio_frequency",
            None,
        )
    )

    wlan_radio_timestamp = _float(
        _value(
            wlan_radio,
            "wlan_radio_wlan_radio_timestamp",
            None,
        )
    )

    wlan_radio_start_tsf = _float(
        _value(
            wlan_radio,
            "wlan_radio_wlan_radio_start_tsf",
            None,
        )
    )

    wlan_radio_end_tsf = _float(
        _value(
            wlan_radio,
            "wlan_radio_wlan_radio_end_tsf",
            None,
        )
    )

    # =========================================================
    # TLS
    # =========================================================

    tls_record_version = _float(
        _value(
            tls,
            "tls_tls_record_version",
            None,
        )
    )

    # =========================================================
    # HTTP
    # =========================================================

    http_request_method = _value(
        http,
        "http_http_request_method",
        None,
    )

    http_content_length = _float(
        _value(
            http,
            "http_http_content_length",
            None,
        )
    )

    http_content_type = _value(
        http,
        "http_http_content_type",
        None,
    )

    http_request_version = _value(
        http,
        "http_http_request_version",
        None,
    )

    # =========================================================
    # NORMALIZED PACKET
    # =========================================================

    packet = {
        # =====================================================
        # Existing normalized fields
        # =====================================================

        "timestamp": timestamp,
        "length": length,

        "retry": retry,
        "protected": protected,

        "frame_type": frame_type,
        "frame_subtype": frame_subtype,

        "signal": signal,
        "data_rate": data_rate,

        "bssid": bssid,
        "source": source,
        "destination": destination,

        "dns": dns_present,
        "dns_transaction_id": dns_transaction_id,
        "dns_response": dns_response,

        "tcp_syn": tcp_syn,
        "tcp_rst": tcp_rst,
        "tcp_retransmission": tcp_retransmission,

        "udp_destination_port": udp_dstport,

        # =====================================================
        # Layer presence
        # =====================================================

        "frame__present": float(frame_present),
        "eth__present": float(eth_present),
        "ip__present": float(ip_present),
        "ipv6__present": float(ipv6_present),
        "tcp__present": float(tcp_present),
        "udp__present": float(udp_present),
        "dns__present": float(dns_present),
        "arp__present": float(arp_present),
        "wlan__present": float(wlan_present),
        "radiotap__present": float(radiotap_present),
        "wlan_radio__present": float(wlan_radio_present),
        "tls__present": float(tls_present),
        "http__present": float(http_present),
        "ssdp__present": float(ssdp_present),
        "llc__present": float(llc_present),

        # =====================================================
        # Frozen / raw feature fields
        # =====================================================

        "frame.len": (
            float(length)
            if length is not None
            else None
        ),

        "frame.time_delta": frame_time_delta,
        "frame.time_delta_displayed": frame_time_delta_displayed,

        # -----------------------------------------------------
        # Radiotap
        # -----------------------------------------------------

        "radiotap.channel.flags.ofdm": radio_channel_ofdm,
        "radiotap.channel.freq": radio_frequency,
        "radiotap.datarate": data_rate,
        "radiotap.dbm_antsignal": signal,
        "radiotap.length": radiotap_length,

        # -----------------------------------------------------
        # WLAN
        # -----------------------------------------------------

        "wlan.duration": wlan_duration,

        "wlan.fc.protected": (
            float(protected)
            if wlan_present
            else None
        ),

        "wlan.fc.type": (
            float(frame_type)
            if frame_type is not None
            else None
        ),

        "wlan.fc.retry": (
            float(retry)
            if wlan_present
            else None
        ),

        "wlan.fc.subtype": (
            float(frame_subtype)
            if frame_subtype is not None
            else None
        ),

        "wlan.seq": (
            float(wlan_seq)
            if wlan_seq is not None
            else None
        ),

        "wlan.tag.length": (
            float(wlan_tag_length)
            if wlan_tag_length is not None
            else None
        ),

        # -----------------------------------------------------
        # WLAN radio
        # -----------------------------------------------------

        "wlan_radio.signal_dbm": wlan_radio_signal,
        "wlan_radio.data_rate": wlan_radio_data_rate,
        "wlan_radio.duration": wlan_radio_duration,
        "wlan_radio.phy": wlan_radio_phy,
        "wlan_radio.channel": wlan_radio_channel,
        "wlan_radio.frequency": wlan_radio_frequency,
        "wlan_radio.timestamp": wlan_radio_timestamp,
        "wlan_radio.start_tsf": wlan_radio_start_tsf,
        "wlan_radio.end_tsf": wlan_radio_end_tsf,

        # -----------------------------------------------------
        # IP
        # -----------------------------------------------------

        "ip.proto": (
            float(ip_proto)
            if ip_proto is not None
            else None
        ),

        "ip.ttl": (
            float(ip_ttl)
            if ip_ttl is not None
            else None
        ),

        "ip.version": (
            float(ip_version)
            if ip_version is not None
            else None
        ),

        # -----------------------------------------------------
        # TCP
        # -----------------------------------------------------

        "tcp.ack": (
            float(tcp_ack)
            if tcp_ack is not None
            else None
        ),

        "tcp.ack_raw": (
            float(tcp_ack_raw)
            if tcp_ack_raw is not None
            else None
        ),

        "tcp.seq": (
            float(tcp_seq)
            if tcp_seq is not None
            else None
        ),

        "tcp.seq_raw": (
            float(tcp_seq_raw)
            if tcp_seq_raw is not None
            else None
        ),

        "tcp.srcport": (
            float(tcp_srcport)
            if tcp_srcport is not None
            else None
        ),

        "tcp.dstport": (
            float(tcp_dstport)
            if tcp_dstport is not None
            else None
        ),

        "tcp.time_delta": tcp_time_delta,
        "tcp.time_relative": tcp_time_relative,

        "tcp.flags.syn": (
            float(tcp_syn)
            if tcp_present
            else None
        ),

        "tcp.flags.ack": (
            float(tcp_ack_flag)
            if tcp_present
            else None
        ),

        "tcp.flags.fin": (
            float(tcp_fin)
            if tcp_present
            else None
        ),

        "tcp.flags.push": (
            float(tcp_push)
            if tcp_present
            else None
        ),

        "tcp.flags.reset": (
            float(tcp_rst)
            if tcp_present
            else None
        ),

        "tcp.option_len": (
            float(tcp_option_len)
            if tcp_option_len is not None
            else None
        ),

        "tcp.analysis.retransmission": (
            float(tcp_retransmission)
            if tcp_present
            else None
        ),

        # -----------------------------------------------------
        # UDP
        # -----------------------------------------------------

        "udp.srcport": (
            float(udp_srcport)
            if udp_srcport is not None
            else None
        ),

        "udp.dstport": (
            float(udp_dstport)
            if udp_dstport is not None
            else None
        ),

        "udp.length": (
            float(udp_length)
            if udp_length is not None
            else None
        ),

        "udp.time_delta": udp_time_delta,
        "udp.time_relative": udp_time_relative,

        # -----------------------------------------------------
        # ARP
        # -----------------------------------------------------

        "arp.opcode": (
            float(arp_opcode)
            if arp_opcode is not None
            else None
        ),

        "arp.src.proto_ipv4": arp_src_proto_ipv4,
        "arp.dst.proto_ipv4": arp_dst_proto_ipv4,

        # -----------------------------------------------------
        # TLS
        # -----------------------------------------------------

        "tls.record.version": tls_record_version,

        # -----------------------------------------------------
        # HTTP
        # -----------------------------------------------------

        "http.request.method": http_request_method,
        "http.content_length": http_content_length,
        "http.content_type": http_content_type,
        "http.request.version": http_request_version,

        # =====================================================
        # Presence / active indicators
        # =====================================================

        "arp__present": float(arp_present),

        "ssdp__present": float(ssdp_present),

        "http.request.method__present": float(
            bool(http_request_method)
        ),

        "tls.record.version__present": float(
            tls_present
        ),

        "ip.version__present": float(
            ip_present
        ),

        "tcp.analysis__present": float(
            tcp_analysis_present
        ),

        "tcp.analysis.flags__present": float(
            tcp_analysis_flags_present
        ),

        # =====================================================
        # Raw TShark data
        # =====================================================

        "layers": layers,
    }

    return packet


class TSharkCapture:
    """
    Live TShark packet capture.

    The interface is supplied by the caller; no machine-specific
    interface is hardcoded here.
    """

    def __init__(self, interface):
        self.interface = str(interface)

    def packets(self):
        cmd = [
            "tshark",
            "-i",
            self.interface,
            "-T",
            "ek",
            "-l",
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        try:
            if process.stdout is None:
                return

            for line in process.stdout:

                line = line.strip()

                if not line:
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # TShark EK metadata records contain "index".
                # They are not packet records.
                if "index" in data:
                    continue

                yield normalize_packet(data)

        finally:

            if process.poll() is None:
                process.terminate()

            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()