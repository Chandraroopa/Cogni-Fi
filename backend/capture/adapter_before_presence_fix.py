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


def _float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _int(value, default=0):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def _bool(value):
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

    The returned packet contains:
    1. Existing normalized fields used by the live detector.
    2. Frozen ML/TShark fields where available.
    3. Raw TShark layers for debugging and future extraction.
    """

    layers = packet_dict.get("layers", {})

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
            0,
        )
    )

    frame_time_delta = _float(
        _value(
            frame,
            "frame_frame_time_delta",
            0.0,
        )
    )

    frame_time_delta_displayed = _float(
        _value(
            frame,
            "frame_frame_time_delta_displayed",
            0.0,
        )
    )

    frame_time_relative = _float(
        _value(
            frame,
            "frame_frame_time_relative",
            0.0,
        )
    )

    # =========================================================
    # ETHERNET
    # =========================================================

    eth_source = _value(
        eth,
        "eth_eth_src",
        "",
    )

    eth_destination = _value(
        eth,
        "eth_eth_dst",
        "",
    )

    # =========================================================
    # IP
    # =========================================================

    ip_source = _value(
        ip,
        "ip_ip_src",
        "",
    )

    ip_destination = _value(
        ip,
        "ip_ip_dst",
        "",
    )

    ipv6_source = _value(
        ipv6,
        "ipv6_ipv6_src",
        "",
    )

    ipv6_destination = _value(
        ipv6,
        "ipv6_ipv6_dst",
        "",
    )

    source = (
        ip_source
        or ipv6_source
        or eth_source
    )

    destination = (
        ip_destination
        or ipv6_destination
        or eth_destination
    )

    ip_proto = _int(
        _value(
            ip,
            "ip_ip_proto",
            0,
        )
    )

    ip_ttl = _int(
        _value(
            ip,
            "ip_ip_ttl",
            0,
        )
    )

    ip_version = _int(
        _value(
            ip,
            "ip_ip_version",
            0,
        )
    )

    # =========================================================
    # TCP
    # =========================================================

    tcp_srcport = _int(
        _value(
            tcp,
            "tcp_tcp_srcport",
            0,
        )
    )

    tcp_dstport = _int(
        _value(
            tcp,
            "tcp_tcp_dstport",
            0,
        )
    )

    tcp_seq = _int(
        _value(
            tcp,
            "tcp_tcp_seq",
            0,
        )
    )

    tcp_seq_raw = _int(
        _value(
            tcp,
            "tcp_tcp_seq_raw",
            0,
        )
    )

    tcp_ack = _int(
        _value(
            tcp,
            "tcp_tcp_ack",
            0,
        )
    )

    tcp_ack_raw = _int(
        _value(
            tcp,
            "tcp_tcp_ack_raw",
            0,
        )
    )

    tcp_time_delta = _float(
        _value(
            tcp,
            "tcp_tcp_time_delta",
            0.0,
        )
    )

    tcp_time_relative = _float(
        _value(
            tcp,
            "tcp_tcp_time_relative",
            0.0,
        )
    )

    tcp_option_len = _int(
        _value(
            tcp,
            "tcp_tcp_hdr_len",
            0,
        )
    )

    tcp_syn = _bool(
        _value(
            tcp,
            "tcp_tcp_flags_syn",
            False,
        )
    )

    tcp_ack_flag = _bool(
        _value(
            tcp,
            "tcp_tcp_flags_ack",
            False,
        )
    )

    tcp_fin = _bool(
        _value(
            tcp,
            "tcp_tcp_flags_fin",
            False,
        )
    )

    tcp_push = _bool(
        _value(
            tcp,
            "tcp_tcp_flags_push",
            False,
        )
    )

    tcp_rst = _bool(
        _value(
            tcp,
            "tcp_tcp_flags_reset",
            False,
        )
    )

    tcp_retransmission = any(
        _bool(
            _value(
                tcp,
                key,
                False,
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
            0,
        )
    )

    udp_dstport = _int(
        _value(
            udp,
            "udp_udp_dstport",
            0,
        )
    )

    udp_length = _int(
        _value(
            udp,
            "udp_udp_length",
            0,
        )
    )

    udp_time_delta = _float(
        _value(
            udp,
            "udp_udp_time_delta",
            0.0,
        )
    )

    udp_time_relative = _float(
        _value(
            udp,
            "udp_udp_time_relative",
            0.0,
        )
    )

    # =========================================================
    # DNS
    # =========================================================

    dns_present = bool(dns)

    dns_transaction_id = _value(
        dns,
        "dns_dns_id",
        None,
    )

    dns_response = _bool(
        _value(
            dns,
            "dns_dns_flags_response",
            False,
        )
    )

    # =========================================================
    # ARP
    # =========================================================

    arp_present = bool(arp)

    arp_opcode = _int(
        _value(
            arp,
            "arp_arp_opcode",
            0,
        )
    )

    arp_src_proto_ipv4 = _value(
        arp,
        "arp_arp_src_proto_ipv4",
        "",
    )

    arp_dst_proto_ipv4 = _value(
        arp,
        "arp_arp_dst_proto_ipv4",
        "",
    )

    # =========================================================
    # 802.11
    # =========================================================

    frame_type = _int(
        _value(
            wlan,
            "wlan_wlan_fc_type",
            0,
        )
    )

    frame_subtype = _int(
        _value(
            wlan,
            "wlan_wlan_fc_subtype",
            0,
        )
    )

    retry = _bool(
        _value(
            wlan,
            "wlan_wlan_fc_retry",
            False,
        )
    )

    protected = _bool(
        _value(
            wlan,
            "wlan_wlan_fc_protected",
            False,
        )
    )

    wlan_duration = _float(
        _value(
            wlan,
            "wlan_wlan_duration",
            0.0,
        )
    )

    wlan_seq = _int(
        _value(
            wlan,
            "wlan_wlan_seq",
            0,
        )
    )

    bssid = _value(
        wlan,
        "wlan_wlan_bssid",
        "",
    )

    wlan_tag_length = _int(
        _value(
            wlan,
            "wlan_wlan_tag_length",
            0,
        )
    )

    # =========================================================
    # RADIOTAP
    # =========================================================

    signal = _float(
        _value(
            radiotap,
            "radiotap_radiotap_dbm_antsignal",
            0.0,
        )
    )

    data_rate = _float(
        _value(
            radiotap,
            "radiotap_radiotap_datarate",
            0.0,
        )
    )

    radio_frequency = _float(
        _value(
            radiotap,
            "radiotap_radiotap_channel_freq",
            0.0,
        )
    )

    radio_channel_ofdm = _float(
        _value(
            radiotap,
            "radiotap_radiotap_channel_flags_ofdm",
            0.0,
        )
    )

    radiotap_length = _float(
        _value(
            radiotap,
            "radiotap_radiotap_length",
            0.0,
        )
    )

    # =========================================================
    # TLS
    # =========================================================

    tls_record_version = _float(
        _value(
            tls,
            "tls_tls_record_version",
            0.0,
        )
    )

    # =========================================================
    # HTTP / SSDP / LLC PRESENCE
    # =========================================================

    http_present = bool(http)
    ssdp_present = bool(ssdp)
    llc_present = bool(llc)

    http_request_method = _value(
        http,
        "http_http_request_method",
        "",
    )

    http_content_length = _float(
        _value(
            http,
            "http_http_content_length",
            0.0,
        )
    )

    http_content_type = _value(
        http,
        "http_http_content_type",
        "",
    )

    http_request_version = _value(
        http,
        "http_http_request_version",
        "",
    )

    # =========================================================
    # NORMALIZED PACKET
    # =========================================================

    packet = {
        # Existing normalized fields
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
        # Frozen / raw feature fields
        # =====================================================

        "frame.len": float(length),
        "frame.time_delta": frame_time_delta,
        "frame.time_delta_displayed": frame_time_delta_displayed,

        "radiotap.channel.flags.ofdm": radio_channel_ofdm,
        "radiotap.channel.freq": radio_frequency,
        "radiotap.datarate": data_rate,
        "radiotap.dbm_antsignal": signal,
        "radiotap.length": radiotap_length,

        "wlan.duration": wlan_duration,
        "wlan.fc.protected": float(protected),
        "wlan.fc.type": float(frame_type),
        "wlan.fc.retry": float(retry),
        "wlan.fc.subtype": float(frame_subtype),
        "wlan.seq": float(wlan_seq),
        "wlan.tag.length": float(wlan_tag_length),

        "ip.proto": float(ip_proto),
        "ip.ttl": float(ip_ttl),
        "ip.version": float(ip_version),

        "tcp.ack": float(tcp_ack),
        "tcp.ack_raw": float(tcp_ack_raw),
        "tcp.seq": float(tcp_seq),
        "tcp.seq_raw": float(tcp_seq_raw),
        "tcp.srcport": float(tcp_srcport),
        "tcp.dstport": float(tcp_dstport),
        "tcp.time_delta": tcp_time_delta,
        "tcp.time_relative": tcp_time_relative,
        "tcp.flags.syn": float(tcp_syn),
        "tcp.flags.ack": float(tcp_ack_flag),
        "tcp.flags.fin": float(tcp_fin),
        "tcp.flags.push": float(tcp_push),
        "tcp.flags.reset": float(tcp_rst),
        "tcp.option_len": float(tcp_option_len),
        "tcp.analysis.retransmission": float(tcp_retransmission),

        "udp.srcport": float(udp_srcport),
        "udp.dstport": float(udp_dstport),
        "udp.length": float(udp_length),
        "udp.time_delta": udp_time_delta,
        "udp.time_relative": udp_time_relative,

        "arp.opcode": float(arp_opcode),
        "arp.src.proto_ipv4": arp_src_proto_ipv4,
        "arp.dst.proto_ipv4": arp_dst_proto_ipv4,

        "tls.record.version": tls_record_version,

        "http.request.method": http_request_method,
        "http.content_length": http_content_length,
        "http.content_type": http_content_type,
        "http.request.version": http_request_version,

        "arp__present": float(arp_present),
        "ssdp__present": float(ssdp_present),
        "http.request.method__present": float(
            bool(http_request_method)
        ),
        "tls.record.version__present": float(
            tls_record_version != 0
        ),
        "ip.version__present": float(
            ip_version != 0
        ),
        "tcp.analysis__present": float(
            tcp_analysis_present
        ),
        "tcp.analysis.flags__present": float(
            tcp_analysis_flags_present
        ),

        # Raw TShark data
        "layers": layers,
    }

    return packet


class TSharkCapture:

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

            for line in process.stdout:

                line = line.strip()

                if not line:
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

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