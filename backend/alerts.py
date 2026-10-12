from datetime import datetime, timezone

class AlertEngine:
    @staticmethod
    def create_alert(status, risk_score, trust_score, attack_type=None,
                     confidence=None, reasons=None):
        if status not in ('Risky', 'Suspicious'):
            return None
        return {
            'severity': 'high' if status == 'Risky' else 'medium',
            'title': 'High-risk network detected' if status == 'Risky' else 'Security warning',
            'risk_score': risk_score,
            'trust_score': trust_score,
            'attack_type': attack_type,
            'confidence': confidence,
            'reasons': list(reasons or []),
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }
