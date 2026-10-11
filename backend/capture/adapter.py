
import json
import subprocess
from datetime import datetime


def _value(layer, key, default=None):
    """Safely get a value from a TShark layer."""
    if not isinstance(layer, dict):
        return default
    value = layer.get(key)
    return default if value in (None, "") else value


def _float(value, default=None):
    """Convert a value to a finite float."""
    try:
        result = float(value)
        return result if result == result and abs(result) != float("inf") else default
    except (ValueError, TypeError, OverflowError):
        return default


def _int(value, default=None):
    """Convert a numeric value to int."""
    try:
        return int(float(value))
    except (ValueError, TypeError, OverflowError):
        return default


def _optional_bool(value):
    """Preserve unavailable boolean fields as None."""
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "set"}


def _timestamp(packet_dict, frame):
    """Read a TShark epoch timestamp, with a safe fallback."""
    raw_epoch = _value(frame, "frame_frame_time_epoch")

    if raw_epoch is not None:
        value = _float(raw_epoch)
        if value is not None:
            return value / 1000.0 if value > 10_000_000_000 else value
        try:
            return datetime.fromisoformat(
                str(raw_epoch).replace("Z", "+00:00")
            ).timestamp()
        except (ValueError, TypeError, OverflowError, OSError):
            pass

    raw = packet_dict.get("timestamp")
    if raw not in (None, ""):
        value = _float(raw)
        if value is not None:
            return value / 1000.0 if value > 10_000_000_000 else value
        try:
            return datetime.fromisoformat(
                str(raw).replace("Z", "+00:00")
            ).timestamp()
        except (ValueError, TypeError, OverflowError, OSError):
            pass

    return None


def _detect_tcp_retransmission(tcp):
    """
    Detect TShark TCP retransmission markers.

    Returns:
        True: retransmission explicitly identified.
        False: an explicit false marker is available.
        None: retransmission status is unavailable.

    TShark EK may store expert records as a list under _ws_expert.
    Lost-segment messages alone are not treated as retransmissions.
    """
    if not isinstance(tcp, dict) or not tcp:
        return None

    marker_keys = (
        "tcp_analysis_retransmission",
        "tcp_analysis_fast_retransmission",
        "tcp_analysis_spurious_retransmission",
        "tcp_tcp_analysis_retransmission",
        "tcp_tcp_analysis_fast_retransmission",
        "tcp_tcp_analysis_spurious_retransmission",
    )

    values = [_optional_bool(tcp.get(key)) for key in marker_keys]

    if any(value is True for value in values):
        return True

    # TShark EK commonly stores expert records as a list.
    expert = tcp.get("_ws_expert", [])
    if isinstance(expert, dict):
        expert = [expert]

    if isinstance(expert, list):
        for entry in expert:
            if not isinstance(entry, dict):
                continue

            # Null-valued marker keys still indicate that TShark
            # included the corresponding analysis marker.
            if any(key in entry for key in marker_keys):
                return True

            message = str(
                entry.get("_ws_expert__ws_expert_message", "")
            ).lower()

            if "retransmission" in message:
                return True

    if any(value is False for value in values):
        return False

    return None


def normalize_packet(packet_dict):
    """Normalize one TShark EK JSON packet."""
    layers = packet_dict.get("layers", {})
    if not isinstance(layers, dict):
        layers = {}

    layer_names = (
        "frame", "eth", "ip", "ipv6", "tcp", "udp", "dns",
        "arp", "wlan", "radiotap", "wlan_radio", "tls",
        "http", "ssdp", "llc",
    )

    normalized_layers = {
        name: layers.get(name, {})
        if isinstance(layers.get(name, {}), dict)
        else {}
        for name in layer_names
    }

    frame = normalized_layers["frame"]
    eth = normalized_layers["eth"]
    ip = normalized_layers["ip"]
    ipv6 = normalized_layers["ipv6"]
    tcp = normalized_layers["tcp"]
    udp = normalized_layers["udp"]
    dns = normalized_layers["dns"]
    arp = normalized_layers["arp"]
    wlan = normalized_layers["wlan"]
    radiotap = normalized_layers["radiotap"]
    wlan_radio = normalized_layers["wlan_radio"]
    tls = normalized_layers["tls"]
    http = normalized_layers["http"]
    ssdp = normalized_layers["ssdp"]
    llc = normalized_layers["llc"]

    # Layer presence
    presence = {
        name: bool(layer)
        for name, layer in normalized_layers.items()
    }

    # Frame
    timestamp = _timestamp(packet_dict, frame)
    length = _int(_value(frame, "frame_frame_len"))
    frame_time_delta = _float(_value(frame, "frame_frame_time_delta"))
    frame_time_delta_displayed = _float(
        _value(frame, "frame_frame_time_delta_displayed")
    )

    # Ethernet and network addresses
    eth_source = _value(eth, "eth_eth_src")
    eth_destination = _value(eth, "eth_eth_dst")
    ip_source = _value(ip, "ip_ip_src")
    ip_destination = _value(ip, "ip_ip_dst")
    ipv6_source = _value(ipv6, "ipv6_ipv6_src")
    ipv6_destination = _value(ipv6, "ipv6_ipv6_dst")

    source = ip_source or ipv6_source or eth_source
    destination = ip_destination or ipv6_destination or eth_destination

    # IPv4
    ip_proto = _int(_value(ip, "ip_ip_proto"))
    ip_ttl = _int(_value(ip, "ip_ip_ttl"))
    ip_version = _int(_value(ip, "ip_ip_version"))

    # IPv6
    ipv6_next_header = _int(_value(ipv6, "ipv6_ipv6_nxt"))
    ipv6_hop_limit = _int(_value(ipv6, "ipv6_ipv6_hlim"))
    ipv6_version = _int(_value(ipv6, "ipv6_ipv6_version"))

    # TCP
    tcp_srcport = _int(_value(tcp, "tcp_tcp_srcport"))
    tcp_dstport = _int(_value(tcp, "tcp_tcp_dstport"))
    tcp_seq = _int(_value(tcp, "tcp_tcp_seq"))
    tcp_seq_raw = _int(_value(tcp, "tcp_tcp_seq_raw"))
    tcp_ack = _int(_value(tcp, "tcp_tcp_ack"))
    tcp_ack_raw = _int(_value(tcp, "tcp_tcp_ack_raw"))
    tcp_time_delta = _float(_value(tcp, "tcp_tcp_time_delta"))
    tcp_time_relative = _float(_value(tcp, "tcp_tcp_time_relative"))
    tcp_option_len = _int(_value(tcp, "tcp_tcp_hdr_len"))

    tcp_syn = _optional_bool(_value(tcp, "tcp_tcp_flags_syn"))
    tcp_ack_flag = _optional_bool(_value(tcp, "tcp_tcp_flags_ack"))
    tcp_fin = _optional_bool(_value(tcp, "tcp_tcp_flags_fin"))
    tcp_push = _optional_bool(_value(tcp, "tcp_tcp_flags_push"))
    tcp_rst = _optional_bool(_value(tcp, "tcp_tcp_flags_reset"))
    tcp_retransmission = _detect_tcp_retransmission(tcp)

    tcp_analysis_present = any(
        key.startswith("tcp_tcp_analysis") for key in tcp
    )
    tcp_analysis_flags_present = any(
        "analysis" in key.lower() for key in tcp
    ) or isinstance(tcp.get("_ws_expert"), (dict, list))

    # UDP
    udp_srcport = _int(_value(udp, "udp_udp_srcport"))
    udp_dstport = _int(_value(udp, "udp_udp_dstport"))
    udp_length = _int(_value(udp, "udp_udp_length"))
    udp_time_delta = _float(_value(udp, "udp_udp_time_delta"))
    udp_time_relative = _float(_value(udp, "udp_udp_time_relative"))

    # DNS
    dns_transaction_id = _value(dns, "dns_dns_id")
    dns_response = _optional_bool(
        _value(dns, "dns_dns_flags_response")
    )

    # ARP
    arp_opcode = _int(_value(arp, "arp_arp_opcode"))
    arp_src_proto_ipv4 = _value(arp, "arp_arp_src_proto_ipv4")
    arp_dst_proto_ipv4 = _value(arp, "arp_arp_dst_proto_ipv4")

    # 802.11
    frame_type = _int(_value(wlan, "wlan_wlan_fc_type"))
    frame_subtype = _int(_value(wlan, "wlan_wlan_fc_subtype"))
    retry = _optional_bool(_value(wlan, "wlan_wlan_fc_retry"))
    protected = _optional_bool(_value(wlan, "wlan_wlan_fc_protected"))
    wlan_duration = _float(_value(wlan, "wlan_wlan_duration"))
    wlan_seq = _int(_value(wlan, "wlan_wlan_seq"))
    bssid = _value(wlan, "wlan_wlan_bssid")
    wlan_tag_length = _int(_value(wlan, "wlan_wlan_tag_length"))

    # Radiotap
    signal = _float(_value(radiotap, "radiotap_radiotap_dbm_antsignal"))
    data_rate = _float(_value(radiotap, "radiotap_radiotap_datarate"))
    radio_frequency = _float(
        _value(radiotap, "radiotap_radiotap_channel_freq")
    )
    radio_channel_ofdm = _float(
        _value(radiotap, "radiotap_radiotap_channel_flags_ofdm")
    )
    radiotap_length = _float(
        _value(radiotap, "radiotap_radiotap_length")
    )

    # WLAN radio
    wlan_radio_signal = _float(
        _value(wlan_radio, "wlan_radio_wlan_radio_signal_dbm")
    )
    wlan_radio_data_rate = _float(
        _value(wlan_radio, "wlan_radio_wlan_radio_data_rate")
    )
    wlan_radio_duration = _float(
        _value(wlan_radio, "wlan_radio_wlan_radio_duration")
    )
    wlan_radio_phy = _value(wlan_radio, "wlan_radio_wlan_radio_phy")
    wlan_radio_channel = _float(
        _value(wlan_radio, "wlan_radio_wlan_radio_channel")
    )
    wlan_radio_frequency = _float(
        _value(wlan_radio, "wlan_radio_wlan_radio_frequency")
    )
    wlan_radio_timestamp = _float(
        _value(wlan_radio, "wlan_radio_wlan_radio_timestamp")
    )
    wlan_radio_start_tsf = _float(
        _value(wlan_radio, "wlan_radio_wlan_radio_start_tsf")
    )
    wlan_radio_end_tsf = _float(
        _value(wlan_radio, "wlan_radio_wlan_radio_end_tsf")
    )

    # TLS
    tls_record_version = _float(
        _value(tls, "tls_tls_record_version")
    )

    # HTTP
    http_request_method = _value(http, "http_http_request_method")
    http_content_length = _float(
        _value(http, "http_http_content_length")
    )
    http_content_type = _value(http, "http_http_content_type")
    http_request_version = _value(http, "http_http_request_version")

    def numeric_bool(value):
        return float(value) if value is not None else None

    packet = {
        # Operational fields used by the feature extractor
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
        "dns": presence["dns"],
        "dns_transaction_id": dns_transaction_id,
        "dns_response": dns_response,
        "tcp_syn": tcp_syn,
        "tcp_rst": tcp_rst,
        "tcp_retransmission": tcp_retransmission,
        "udp_destination_port": udp_dstport,

        # Layer presence indicators
        **{
            f"{name}__present": float(value)
            for name, value in presence.items()
        },

        # Frame
        "frame.len": float(length) if length is not None else None,
        "frame.time_delta": frame_time_delta,
        "frame.time_delta_displayed": frame_time_delta_displayed,

        # Radiotap
        "radiotap.channel.flags.ofdm": radio_channel_ofdm,
        "radiotap.channel.freq": radio_frequency,
        "radiotap.datarate": data_rate,
        "radiotap.dbm_antsignal": signal,
        "radiotap.length": radiotap_length,

        # WLAN
        "wlan.duration": wlan_duration,
        "wlan.fc.protected": numeric_bool(protected),
        "wlan.fc.type": float(frame_type) if frame_type is not None else None,
        "wlan.fc.retry": numeric_bool(retry),
        "wlan.fc.subtype": (
            float(frame_subtype) if frame_subtype is not None else None
        ),
        "wlan.seq": float(wlan_seq) if wlan_seq is not None else None,
        "wlan.tag.length": (
            float(wlan_tag_length) if wlan_tag_length is not None else None
        ),

        # WLAN radio
        "wlan_radio.signal_dbm": wlan_radio_signal,
        "wlan_radio.data_rate": wlan_radio_data_rate,
        "wlan_radio.duration": wlan_radio_duration,
        "wlan_radio.phy": wlan_radio_phy,
        "wlan_radio.channel": wlan_radio_channel,
        "wlan_radio.frequency": wlan_radio_frequency,
        "wlan_radio.timestamp": wlan_radio_timestamp,
        "wlan_radio.start_tsf": wlan_radio_start_tsf,
        "wlan_radio.end_tsf": wlan_radio_end_tsf,

        # IPv4
        "ip.proto": float(ip_proto) if ip_proto is not None else None,
        "ip.ttl": float(ip_ttl) if ip_ttl is not None else None,
        "ip.version": float(ip_version) if ip_version is not None else None,

        # IPv6
        "ipv6.nxt": (
            float(ipv6_next_header) if ipv6_next_header is not None else None
        ),
        "ipv6.hlim": (
            float(ipv6_hop_limit) if ipv6_hop_limit is not None else None
        ),
        "ipv6.version": (
            float(ipv6_version) if ipv6_version is not None else None
        ),

        # TCP
        "tcp.ack": float(tcp_ack) if tcp_ack is not None else None,
        "tcp.ack_raw": float(tcp_ack_raw) if tcp_ack_raw is not None else None,
        "tcp.seq": float(tcp_seq) if tcp_seq is not None else None,
        "tcp.seq_raw": float(tcp_seq_raw) if tcp_seq_raw is not None else None,
        "tcp.srcport": (
            float(tcp_srcport) if tcp_srcport is not None else None
        ),
        "tcp.dstport": (
            float(tcp_dstport) if tcp_dstport is not None else None
        ),
        "tcp.time_delta": tcp_time_delta,
        "tcp.time_relative": tcp_time_relative,
        "tcp.flags.syn": numeric_bool(tcp_syn),
        "tcp.flags.ack": numeric_bool(tcp_ack_flag),
        "tcp.flags.fin": numeric_bool(tcp_fin),
        "tcp.flags.push": numeric_bool(tcp_push),
        "tcp.flags.reset": numeric_bool(tcp_rst),
        "tcp.option_len": (
            float(tcp_option_len) if tcp_option_len is not None else None
        ),
        "tcp.analysis.retransmission": numeric_bool(tcp_retransmission),

        # UDP
        "udp.srcport": (
            float(udp_srcport) if udp_srcport is not None else None
        ),
        "udp.dstport": (
            float(udp_dstport) if udp_dstport is not None else None
        ),
        "udp.length": float(udp_length) if udp_length is not None else None,
        "udp.time_delta": udp_time_delta,
        "udp.time_relative": udp_time_relative,

        # ARP
        "arp.opcode": float(arp_opcode) if arp_opcode is not None else None,
        "arp.src.proto_ipv4": arp_src_proto_ipv4,
        "arp.dst.proto_ipv4": arp_dst_proto_ipv4,

        # TLS
        "tls.record.version": tls_record_version,

        # HTTP
        "http.request.method": http_request_method,
        "http.content_length": http_content_length,
        "http.content_type": http_content_type,
        "http.request.version": http_request_version,

        # Presence indicators
        "http.request.method__present": float(bool(http_request_method)),
        "tls.record.version__present": float(presence["tls"]),
        "ip.version__present": float(presence["ip"]),
        "tcp.analysis__present": float(tcp_analysis_present),
        "tcp.analysis.flags__present": float(tcp_analysis_flags_present),

        # Preserve original layers for further extraction
        "layers": layers,
    }

    return packet


class TSharkCapture:
    """Read live packets from a TShark-supported interface."""

    def __init__(self, interface):
        self.interface = str(interface)
        self._process = None

    def packets(self):
        """Yield normalized packets from TShark EK JSON output."""
        if self._process is not None and self._process.poll() is None:
            raise RuntimeError("TShark capture is already running.")

        cmd = ["tshark", "-i", self.interface, "-T", "ek", "-l"]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        self._process = process

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

                if not isinstance(data, dict):
                    continue

                # EK metadata records are not packet records.
                if "index" in data or "layers" not in data:
                    continue

                yield normalize_packet(data)

        finally:
            if process.stdout is not None:
                process.stdout.close()

            if process.poll() is None:
                process.terminate()

            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

            self._process = None

    def stop(self):
        """Request termination of the running TShark process."""
        process = self._process
        if process is not None and process.poll() is None:
            process.terminate()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Capture and normalize packets using TShark."
    )
    parser.add_argument(
        "-i",
        "--interface",
        required=True,
        help="Interface name or number recognized by TShark.",
    )
    args = parser.parse_args()

    capture = TSharkCapture(args.interface)

    try:
        for packet in capture.packets():
            print(json.dumps(packet, default=str))
    except KeyboardInterrupt:
        capture.stop()
        print("\nCapture stopped.")
