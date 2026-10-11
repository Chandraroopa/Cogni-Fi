
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
    TShark EK provides:
        timestamp = milliseconds since epoch

    Example:
        1791374395785
    """

    raw = packet_dict.get("timestamp")

    if raw not in (None, ""):
        try:
            value = float(raw)

            # TShark timestamp is milliseconds.
            if value > 10_000_000_000:
                return value / 1000.0

            return value

        except (ValueError, TypeError):
            pass

    # Fallback to TShark ISO timestamp.
    raw_iso = _value(
        frame,
        "frame_frame_time_epoch",
        None,
    )

    if raw_iso:
        try:
            iso = str(raw_iso).replace("Z", "+00:00")
            return datetime.fromisoformat(iso).timestamp()
        except (ValueError, TypeError):
            pass

    return 0.0


def normalize_packet(packet_dict):
    """
    Convert TShark -T ek output into the normalized packet
    format expected by FeatureExtractor.
    """

    layers = packet_dict.get("layers", {})

    frame = layers.get("frame", {})
    eth = layers.get("eth", {})
    ip = layers.get("ip", {})
    ipv6 = layers.get("ipv6", {})
    tcp = layers.get("tcp", {})
    udp = layers.get("udp", {})
    dns = layers.get("dns", {})

    # ---------------------------------------------------------
    # Timestamp
    # ---------------------------------------------------------

    timestamp = _timestamp(packet_dict, frame)

    # ---------------------------------------------------------
    # Packet length
    # ---------------------------------------------------------

    length = _int(
        _value(
            frame,
            "frame_frame_len",
            0,
        )
    )

    # ---------------------------------------------------------
    # Ethernet addresses
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # IP addresses
    # ---------------------------------------------------------

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

    source = ip_source or ipv6_source or eth_source
    destination = ip_destination or ipv6_destination or eth_destination

    # ---------------------------------------------------------
    # TCP
    # ---------------------------------------------------------

    tcp_syn = _bool(
        _value(
            tcp,
            "tcp_tcp_flags_syn",
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

    # ---------------------------------------------------------
    # UDP
    # ---------------------------------------------------------

    udp_destination_port = _int(
        _value(
            udp,
            "udp_udp_dstport",
            0,
        )
    )

    # ---------------------------------------------------------
    # DNS
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # 802.11 / radio fields
    #
    # These are optional because Windows Wi-Fi captures may
    # expose Ethernet/IP packets instead of 802.11/radiotap.
    # ---------------------------------------------------------

    wlan = layers.get("wlan", {})
    radiotap = layers.get("radiotap", {})

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

    bssid = _value(
        wlan,
        "wlan_wlan_bssid",
        "",
    )

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

    # ---------------------------------------------------------
    # Return normalized packet
    # ---------------------------------------------------------

    return {
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

        "udp_destination_port": udp_destination_port,

        # Keep raw layers available for debugging.
        "layers": layers,
    }


class TSharkCapture:
    def __init__(self, interface):
        self.interface = interface

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

                # Ignore TShark metadata/index records.
                if "index" in data:
                    continue

                yield normalize_packet(data)

        finally:
            if process.poll() is None:
                process.terminate()

            process.wait()

