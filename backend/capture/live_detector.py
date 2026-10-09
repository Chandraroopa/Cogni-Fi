class LiveRiskDetector:
    def __init__(self):
        pass

    def analyze(self, features):
        risk_score = 0
        reasons = []

        # Packet rate
        packets_per_second = features.get("packets_per_second", 0)

        if packets_per_second > 100:
            risk_score += 30
            reasons.append("High packet rate")
        else:
            reasons.append("Normal packet rate")

        # TCP SYN rate
        syn_rate = features.get("syn_rate", 0)

        if syn_rate > 0.5:
            risk_score += 30
            reasons.append("TCP SYN spike")
        else:
            reasons.append("No TCP SYN spike")

        # Retransmission rate
        retransmission_rate = features.get("retransmission_rate", 0)

        if retransmission_rate > 0.3:
            risk_score += 25
            reasons.append("High retransmission rate")
        else:
            reasons.append("No retransmission spike")

        # RST rate
        rst_rate = features.get("rst_rate", 0)

        if rst_rate > 0.3:
            risk_score += 15
            reasons.append("High TCP RST rate")

        # DNS activity
        dns_requests = features.get("dns_request_count", 0)

        if dns_requests > 50:
            risk_score += 10
            reasons.append("High DNS request rate")

        # Limit score
        risk_score = min(risk_score, 100)

        # Risk level
        if risk_score >= 60:
            risk_level = "High"
        elif risk_score >= 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "reasons": reasons
        }