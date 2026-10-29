from datetime import datetime, timezone


class AlertEngine:
    """Create alerts for suspicious or high-risk network assessments."""

    @staticmethod
    def create_alert(
        status,
        risk_score,
        trust_score,
        attack_type=None,
        confidence=None,
        reasons=None,
        assessment=None,
    ):
        if status not in ("Risky", "Suspicious"):
            return None

        is_risky = status == "Risky"

        return {
            "severity": "high" if is_risky else "medium",
            "title": (
                "High-risk network detected"
                if is_risky
                else "Security warning"
            ),
            "risk_score": risk_score,
            "trust_score": trust_score,
            "attack_type": attack_type,
            "confidence": confidence,
            "reasons": list(reasons or []),
            "assessment": assessment,
            "provisional": assessment != "full",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
