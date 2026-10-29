
import json
import os
import re
import subprocess
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import pandas as pd
from flask import Blueprint, Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

api_blueprint = Blueprint("api", __name__)

# Path to the Wireshark CSV capture file.
DATA_FILE = os.path.join(os.path.dirname(__file__), "normal_01.csv")


@api_blueprint.route("/api/wifi-signal", methods=["GET"])
def proxy_wifi_signal():
    """Forward Wi-Fi signal requests to the FastAPI service."""
    url = "http://127.0.0.1:8001/wifi-signal"

    try:
        with urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            return jsonify(data), response.status

    except HTTPError as exc:
        try:
            data = json.loads(exc.read().decode("utf-8"))
            return jsonify(data), exc.code
        except (ValueError, OSError):
            return jsonify({
                "available": False,
                "error": "FastAPI returned an invalid error response.",
            }), 502

    except (URLError, TimeoutError, OSError, ValueError) as exc:
        return jsonify({
            "available": False,
            "error": f"FastAPI Wi-Fi signal service unavailable: {exc}",
        }), 502


def load_network_data(filepath):
    """Load captured packet data, or return an empty frame if absent."""
    empty_columns = [
        "frame.time_epoch",
        "ip.src",
        "ip.dst",
        "tcp.srcport",
        "udp.dstport",
    ]

    if not os.path.exists(filepath):
        return pd.DataFrame(columns=empty_columns)

    if filepath.lower().endswith(".csv"):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_json(filepath)

    if "frame.time_epoch" in df.columns:
        df["frame.time_epoch"] = pd.to_numeric(
            df["frame.time_epoch"], errors="coerce"
        )

    return df


@api_blueprint.route("/api/network-metrics", methods=["GET"])
def get_network_metrics():
    """Return packet-rate and approximate DNS-latency metrics."""
    df = load_network_data(DATA_FILE)

    if df.empty or "frame.time_epoch" not in df.columns:
        return jsonify({
            "packet_rate": [],
            "avg_dns_latency": 0.0,
            "total_packets": 0,
        })

    df = df.dropna(subset=["frame.time_epoch"]).sort_values(
        "frame.time_epoch"
    )

    if df.empty:
        return jsonify({
            "packet_rate": [],
            "avg_dns_latency": 0.0,
            "total_packets": 0,
        })

    df["time_bin"] = (df["frame.time_epoch"] // 1).astype(int)
    packet_rate_df = (
        df.groupby("time_bin")
        .size()
        .reset_index(name="packet_rate")
    )

    dns_lat = 0.0
    try:
        src_col = next(
            (c for c in ("tcp.srcport", "udp.srcport")
             if c in df.columns),
            None,
        )
        dst_col = next(
            (c for c in ("tcp.dstport", "udp.dstport")
             if c in df.columns),
            None,
        )

        if src_col or dst_col:
            dns_mask = pd.Series(False, index=df.index)

            if src_col:
                dns_mask |= pd.to_numeric(
                    df[src_col], errors="coerce"
                ).eq(53)

            if dst_col:
                dns_mask |= pd.to_numeric(
                    df[dst_col], errors="coerce"
                ).eq(53)

            dns_df = df.loc[dns_mask]
            if len(dns_df) > 1:
                dns_lat = float(
                    dns_df["frame.time_epoch"].diff().dropna().mean()
                    * 1000
                )

    except (KeyError, TypeError, ValueError):
        dns_lat = 0.0

    # This is a general packet-interarrival estimate, not a
    # measured DNS response time.
    if dns_lat == 0.0 and len(df) > 1:
        diffs = df["frame.time_epoch"].diff().dropna()
        if not diffs.empty:
            dns_lat = float(diffs.mean() * 1000)

    return jsonify({
        "packet_rate": packet_rate_df.tail(20).to_dict(
            orient="records"
        ),
        "avg_dns_latency": round(dns_lat, 2),
        "total_packets": int(len(df)),
    })


def _parse_signal_percentage(value):
    """Parse a Windows signal percentage, if present."""
    match = re.search(r"(\d+)\s*%", value)
    if not match:
        return None

    percentage = int(match.group(1))
    if not 0 <= percentage <= 100:
        return None

    return percentage


def _classify_security(authentication):
    """Normalize Windows authentication text for display."""
    auth = (authentication or "").strip()
    upper_auth = auth.upper()

    if "WPA3" in upper_auth:
        encryption = "WPA3"
        status = "Secure"
    elif "WPA2" in upper_auth:
        encryption = "WPA2"
        status = "Secure"
    elif "WPA" in upper_auth:
        encryption = "WPA"
        status = "Secure"
    elif "WEP" in upper_auth:
        encryption = "WEP"
        status = "Vulnerable"
    elif "OPEN" in upper_auth or "NONE" in upper_auth:
        encryption = "Open"
        status = "Vulnerable"
    else:
        encryption = "Unknown"
        status = "Unknown"

    return encryption, status


@api_blueprint.route("/api/scan", methods=["GET"])
def scan_networks():
    """Discover nearby Wi-Fi networks using Windows netsh."""
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            errors="ignore",
            timeout=15,
        )

        networks = []
        current = None

        def save_current():
            if current is None or not current["ssid"]:
                return

            encryption, status = _classify_security(
                current["security"]
            )

            network = {
                "ssid": current["ssid"],
                "name": current["ssid"],
                "network_name": current["ssid"],
                "security": current["security"] or "Unknown",
                "encryption": encryption,
                "status": status,
                "signal": (
                    round(current["signal_percentage"] / 2 - 100)
                    if current["signal_percentage"] is not None
                    else None
                ),
                "signal_percentage": current["signal_percentage"],
                "channel": current["channel"],
            }
            networks.append(network)

        for raw_line in output.splitlines():
            line = raw_line.strip()

            # Match "SSID 1 : Redmi 12C"; do not match BSSID lines.
            ssid_match = re.match(
                r"^SSID\s+\d+\s*:\s*(.*)$",
                line,
                flags=re.IGNORECASE,
            )

            if ssid_match:
                save_current()
                current = {
                    "ssid": ssid_match.group(1).strip(),
                    "security": None,
                    "signal_percentage": None,
                    "channel": None,
                }
                continue

            if current is None or ":" not in line:
                continue

            key, value = (
                part.strip() for part in line.split(":", 1)
            )
            key_lower = key.lower()

            if key_lower == "authentication":
                current["security"] = value

            elif key_lower == "signal":
                percentage = _parse_signal_percentage(value)
                if percentage is not None:
                    current["signal_percentage"] = percentage

            elif key_lower == "channel":
                try:
                    current["channel"] = int(value)
                except (ValueError, TypeError):
                    pass

        save_current()

        # Merge duplicate SSIDs, retaining available signal/channel data.
        unique_networks = {}

        for network in networks:
            ssid = network["ssid"]

            if ssid not in unique_networks:
                unique_networks[ssid] = network
                continue

            existing = unique_networks[ssid]

            if (
                existing["signal_percentage"] is None
                and network["signal_percentage"] is not None
            ):
                existing["signal_percentage"] = (
                    network["signal_percentage"]
                )
                existing["signal"] = network["signal"]

            if existing["channel"] is None and network["channel"] is not None:
                existing["channel"] = network["channel"]

        return jsonify({
            "success": True,
            "networks": list(unique_networks.values()),
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "networks": [],
            "error": "Windows Wi-Fi scan timed out.",
        }), 504

    except (subprocess.CalledProcessError, OSError) as exc:
        print(f"Live Wi-Fi scan error: {exc}")
        return jsonify({
            "success": False,
            "networks": [],
            "error": "Windows Wi-Fi scan failed. Check Wi-Fi availability.",
        }), 500


@api_blueprint.route("/api/network-details", methods=["GET"])
def get_network_details():
    """Return packet metrics, ARP devices, and active socket connections."""
    df = load_network_data(DATA_FILE)
    total_packets = len(df)

    dns_latency = 0.0
    gateway_rtt = 0.0
    beacon_interval = 0.0
    packet_rate_val = 0.0

    if not df.empty and "frame.time_epoch" in df.columns:
        df = df.dropna(
            subset=["frame.time_epoch"]
        ).sort_values("frame.time_epoch")

        diffs = df["frame.time_epoch"].diff().dropna() * 1000

        if not diffs.empty:
            # These are packet timing estimates, not direct measurements
            # of DNS response time, gateway RTT, or beacon interval.
            dns_latency = float(diffs.mean())
            gateway_rtt = float(diffs.median())
            beacon_interval = float(diffs.mean())

        if not df.empty:
            duration = (
                df["frame.time_epoch"].max()
                - df["frame.time_epoch"].min()
            )
            if duration > 0:
                packet_rate_val = float(len(df) / duration)

    devices = []
    try:
        arp_out = subprocess.check_output(
            ["arp", "-a"],
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            errors="ignore",
            timeout=10,
        )

        for line in arp_out.splitlines():
            parts = line.strip().split()
            if len(parts) < 2:
                continue

            ip_candidate = parts[0]
            mac_candidate = parts[1]

            if (
                re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip_candidate)
                and re.match(
                    r"^[0-9a-fA-F]{2}(-[0-9a-fA-F]{2}){5}$",
                    mac_candidate,
                )
            ):
                devices.append({
                    "device": "Local Subnet Node",
                    "ip": ip_candidate,
                    "mac": mac_candidate.replace("-", ":"),
                    "status": "Active",
                })

    except (subprocess.CalledProcessError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"ARP error: {exc}")

    connections = []
    try:
        netstat_out = subprocess.check_output(
            ["netstat", "-ano"],
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            errors="ignore",
            timeout=10,
        )

        for line in netstat_out.splitlines():
            parts = line.strip().split()
            if len(parts) < 4 or parts[0] not in ("TCP", "UDP"):
                continue

            proto = parts[0]
            local_addr = parts[1]
            foreign_addr = parts[2]
            state = parts[3] if proto == "TCP" else "LISTEN"

            if state not in ("LISTENING", "ESTABLISHED"):
                continue

            local_parts = local_addr.rsplit(":", 1)
            foreign_parts = foreign_addr.rsplit(":", 1)

            connections.append({
                "local_ip": (
                    local_parts[0] if len(local_parts) > 1 else local_addr
                ),
                "local_port": (
                    local_parts[1] if len(local_parts) > 1 else "*"
                ),
                "remote_ip": (
                    foreign_parts[0]
                    if len(foreign_parts) > 1
                    else foreign_addr
                ),
                "remote_port": (
                    foreign_parts[1]
                    if len(foreign_parts) > 1
                    else "*"
                ),
                "status": (
                    "LISTEN" if state == "LISTENING" else "ESTABLISHED"
                ),
                "protocol": proto,
            })

            if len(connections) >= 50:
                break

    except (subprocess.CalledProcessError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"Netstat error: {exc}")

    return jsonify({
        "success": True,
        "dns_latency": round(dns_latency, 2),
        "gateway_rtt": round(gateway_rtt, 2),
        "beacon_interval": round(beacon_interval, 4),
        "packet_rate": round(packet_rate_val, 2),
        "total_packets": total_packets,
        "devices": devices,
        "connections": connections,
    })


app.register_blueprint(api_blueprint)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
