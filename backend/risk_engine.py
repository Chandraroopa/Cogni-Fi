import math
from collections.abc import Mapping

try:
    from .risk_config import LIVE_WEIGHTS, RISK_THRESHOLDS, TRUST_SAFE_THRESHOLD, ENCRYPTION_RISK
    from .behavioral_severity import BehavioralSeverityEngine
    from .explanation import RiskExplanationEngine
    from .alerts import AlertEngine
except ImportError:  # supports `cd backend; python ...` and existing tests
    from risk_config import LIVE_WEIGHTS, RISK_THRESHOLDS, TRUST_SAFE_THRESHOLD, ENCRYPTION_RISK
    from behavioral_severity import BehavioralSeverityEngine
    from explanation import RiskExplanationEngine
    from alerts import AlertEngine


def valid_probability(value):
    if isinstance(value, bool):
        return None
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return value if math.isfinite(value) and 0 <= value <= 1 else None


class RiskEngine:
    def __init__(self, behavior_baseline=None):
        self.behavior_engine = BehavioralSeverityEngine(baseline=behavior_baseline)
        self.explanation_engine = RiskExplanationEngine()
        self.alert_engine = AlertEngine()

    @staticmethod
    def clamp(value):
        if value is None or isinstance(value, bool):
            return None
        try:
            value = float(value)
        except (TypeError, ValueError, OverflowError):
            return None
        return max(0., min(100., value)) if math.isfinite(value) else None

    @staticmethod
    def normalize_security(security):
        if not isinstance(security, str) or not security.strip():
            return None
        security = security.upper().strip()
        if 'WPA3' in security:
            return 'WPA3'
        if 'WPA2' in security:
            return 'WPA2'
        if 'WEP' in security:
            return 'WEP'
        if 'WPA' in security:
            return 'WPA'
        if 'OPEN' in security or security in {'NONE', 'NO AUTHENTICATION'}:
            return 'OPEN'
        return None

    def calculate_static_risk(self, security):
        category = self.normalize_security(security)
        return float(ENCRYPTION_RISK[category]) if category else None

    @staticmethod
    def calculate_ml_risk(binary_result):
        """Legacy binary threshold-aware mapping. Not used for the 30-feature model."""
        if not isinstance(binary_result, Mapping):
            return None
        p = valid_probability(binary_result.get('attack_probability'))
        threshold = valid_probability(binary_result.get('threshold', binary_result.get('decision_threshold')))
        if p is None or threshold is None or not 0 < threshold < 1:
            return None
        bound = float(RISK_THRESHOLDS['suspicious'])
        value = (p / threshold) * bound if p < threshold else bound + (p - threshold) / (1 - threshold) * (100 - bound)
        return round(value, 2)

    @staticmethod
    def parse_ml_evidence(ml_result):
        """Return (ml_score, normalized evidence, attack_type, confidence, positive).

        Invalid/unrecognized ML data remains missing, never automatically normal.
        """
        empty = (None, {'model_type': None, 'binary': None, 'multiclass': None}, None, None, None)
        if not isinstance(ml_result, Mapping):
            return empty

        # New single-stage 30-feature multiclass prediction.
        if 'class_probabilities' in ml_result and 'threat_probability' in ml_result:
            predicted = ml_result.get('predicted_class')
            is_threat = ml_result.get('is_threat')
            probs = ml_result.get('class_probabilities')
            p = valid_probability(ml_result.get('threat_probability'))
            confidence = valid_probability(ml_result.get('confidence'))
            normal = valid_probability(ml_result.get('normal_probability'))
            if (not isinstance(predicted, str) or not predicted or type(is_threat) is not bool
                or is_threat != (predicted != 'Normal') or not isinstance(probs, Mapping)
                or p is None or normal is None or abs(p + normal - 1) > 1e-4):
                return empty
            if any(valid_probability(x) is None for x in probs.values()) or 'Normal' not in probs:
                return empty
            if abs(sum(float(x) for x in probs.values()) - 1) > 1e-4:
                return empty
            
            score = round(100 * p, 2)
            attack = predicted if is_threat else None
            evidence = {'model_type': 'multiclass_30', 'binary': None, 'multiclass': dict(ml_result)}
            return score, evidence, attack, confidence if attack else None, is_threat

        binary = ml_result.get('binary') if 'binary' in ml_result else ml_result
        multiclass = ml_result.get('multiclass') if 'binary' in ml_result else None
        if not isinstance(binary, Mapping) or type(binary.get('is_threat')) is not bool:
            return empty
        score = RiskEngine.calculate_ml_risk(binary)
        p = valid_probability(binary.get('attack_probability'))
        threshold = valid_probability(binary.get('threshold', binary.get('decision_threshold')))
        if score is None or p is None or threshold is None or binary['is_threat'] != (p >= threshold):
            return empty
        attack, confidence = None, None
        if binary['is_threat'] and isinstance(multiclass, Mapping):
            candidate = multiclass.get('predicted_class')
            if isinstance(candidate, str) and candidate and candidate != 'Normal':
                attack = candidate
                confidence = valid_probability(multiclass.get('confidence'))
        normalized = {'model_type': 'legacy_binary', 'binary': dict(binary), 'multiclass': dict(multiclass) if attack else None}
        return score, normalized, attack, confidence, binary['is_threat']

    def calculate_risk(self, factors):
        total, available, configured = 0., 0., sum(LIVE_WEIGHTS.values())
        for key, weight in LIVE_WEIGHTS.items():
            score = self.clamp(factors.get(key))
            if score is not None:
                total += weight * score
                available += weight
        if not available or configured <= 0:
            return None, 0.
        return round(total / available, 2), round(min(1., available / configured), 2)

    def calculate_trust(self, risk_score, evidence_completeness):
        if risk_score is None:
            return None
        return round((100. - risk_score) * evidence_completeness, 2)

    @staticmethod
    def classify(risk_score, trust_score):
        if risk_score is None:
            return 'Unknown'
        if risk_score >= RISK_THRESHOLDS['risky']:
            return 'Risky'
        if risk_score >= RISK_THRESHOLDS['suspicious']:
            return 'Suspicious'
        if trust_score is not None and trust_score >= TRUST_SAFE_THRESHOLD:
            return 'Safe'
        return 'Unverified'  # missing evidence is NOT proof of suspicious activity

    def analyze(self, mode='live', ml_result=None, behavioral_features=None, security=None, behavioral_availability=None):
        mode = str(mode).strip().lower()
        if mode not in ('live', 'preliminary'):
            raise ValueError("Mode must be 'live' or 'preliminary'")
        static = self.calculate_static_risk(security)
        ml_score, ml_evidence, attack_type, attack_confidence, ml_threat = (None, {'model_type': None, 'binary': None, 'multiclass': None}, None, None, None)
        behavior_result, behavior_score = None, None
        if mode == 'live':
            ml_score, ml_evidence, attack_type, attack_confidence, ml_threat = self.parse_ml_evidence(ml_result)
            if behavioral_features is not None:
                behavior_result = self.behavior_engine.analyze(
                    behavioral_features,
                    availability=behavioral_availability,
                )
                # Partial behavioral inputs remain diagnostic; do not call them a full component.
                group_scores = behavior_result.get('groups', {})
                if group_scores and all(value is not None for value in group_scores.values()) and not behavior_result.get('missing_features'):
                    behavior_score = self.clamp(behavior_result.get('risk'))
        factors = {'ml': ml_score, 'behavior': behavior_score, 'static': static}
        risk_score, completeness = self.calculate_risk(factors)
        trust_score = self.calculate_trust(risk_score, completeness)
        assessment = 'preliminary' if mode == 'preliminary' else ('full' if all(v is not None for v in factors.values()) else 'partial')
        status = self.classify(risk_score, trust_score)
        # Never claim Safe on an incomplete assessment.
        if status == 'Safe' and assessment != 'full':
            status = 'Unverified'
        
        if ml_threat is True and status in ('Safe', 'Unverified'):
            status = 'Suspicious'
        security_type = self.normalize_security(security)
        reasons = self.explanation_engine.build_reasons(
            binary_result=ml_evidence['binary'],
            multiclass_result=ml_evidence['multiclass'],
            factors=factors,
            security_type=security_type,
            assessment=assessment,
            ml_is_threat=ml_threat,
            ml_model_type=ml_evidence['model_type'],
        )
        recommendations = self.explanation_engine.build_recommendations(status=status, assessment=assessment, attack_type=attack_type)
        alert = self.alert_engine.create_alert(status=status, risk_score=risk_score, trust_score=trust_score, attack_type=attack_type, confidence=attack_confidence, reasons=reasons)
        return {
            'mode': mode, 'assessment': assessment, 'risk_score': risk_score,
            'trust_score': trust_score, 'status': status,
            'evidence_completeness': completeness, 'factors': factors,
            'ml_evidence': ml_evidence,
            'ml_is_threat': ml_threat,
            'attack': {'type': attack_type, 'confidence': attack_confidence},
            'behavioral_analysis': behavior_result,
            'missing_signals': [k for k, v in factors.items() if v is None],
            'reasons': reasons, 'recommendations': recommendations, 'alert': alert,
        }
