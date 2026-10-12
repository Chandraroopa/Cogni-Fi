# ============================================================
# Evidence weights
# ============================================================
LIVE_WEIGHTS = {
    "ml": 0.45,
    "behavior": 0.25,
    "static": 0.30,
}

# ============================================================
# Final risk categories
# ============================================================
RISK_THRESHOLDS = {
    "suspicious": 30.0,
    "risky": 70.0,
}

TRUST_SAFE_THRESHOLD = 70.0

ENCRYPTION_RISK = {
    "WPA3": 0.0,
    "WPA2": 15.0,
    "WPA": 50.0,
    "WEP": 90.0,
    "OPEN": 100.0,
}

BEHAVIOR_GROUPS = {
    "management": [
        "retry_rate",
        "deauth_rate",
        "disassoc_rate",
    ],
    "network": [
        "dns_latency_mean",
        "retransmission_rate",
        "rst_rate",
    ],
}