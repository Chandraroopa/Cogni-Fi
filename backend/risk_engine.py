
import math
from collections.abc import Mapping

try:
    from .risk_config import (
        LIVE_WEIGHTS,
        RISK_THRESHOLDS,
        TRUST_SAFE_THRESHOLD,
        ENCRYPTION_RISK,
    )
    from .behavioral_severity import BehavioralSeverityEngine
    from .explanation import RiskExplanationEngine
    from .alerts import AlertEngine
except ImportError:
    # Supports running from the backend directory and existing tests.
    from risk_config import (
        LIVE_WEIGHTS,
        RISK_THRESHOLDS,
        TRUST_SAFE_THRESHOLD,
        ENCRYPTION_RISK,
    )
    from behavioral_severity import BehavioralSeverityEngine
    from explanation import RiskExplanationEngine
    from alerts import AlertEngine


def valid_probability(value):
    """Return a finite probability in [0, 1], or None."""
    if isinstance(value, bool):
        return None

    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError):
        return None

    return value if math.isfinite(value) and 0.0 <= value <= 1.0 else None


class RiskEngine:
    def __init__(self, behavior_baseline=None):
        self.behavior_engine = BehavioralSeverityEngine(
            baseline=behavior_baseline
        )
        self.explanation_engine = RiskExplanationEngine()
        self.alert_engine = AlertEngine()

    @staticmethod
    def clamp(value):
        """Clamp a valid finite score to [0, 100]."""
        if value is None or isinstance(value, bool):
            return None

        try:
            value = float(value)
        except (TypeError, ValueError, OverflowError):
            return None

        if not math.isfinite(value):
            return None

        return max(0.0, min(100.0, value))

    @staticmethod
    def normalize_security(security):
        """Normalize common Wi-Fi security labels."""
        if not isinstance(security, str) or not security.strip():
            return None

        security = security.upper().strip()

        if "WPA3" in security:
            return "WPA3"
        if "WPA2" in security:
            return "WPA2"
        if "WEP" in security:
            return "WEP"
        if "WPA" in security:
            return "WPA"
        if (
            "OPEN" in security
            or security in {"NONE", "NO AUTHENTICATION"}
        ):
            return "OPEN"

        return None

    def calculate_static_risk(self, security):
        """Return configured encryption risk, or None if unknown."""
        category = self.normalize_security(security)

        if category is None:
            return None

        # An unknown category must not crash the live risk pipeline.
        value = ENCRYPTION_RISK.get(category)
        return self.clamp(value)

    @staticmethod
    def calculate_ml_risk(binary_result):
        """
        Convert legacy binary-model probabilities to a risk score.

        This mapping is for the legacy binary model only. The 30-feature
        multiclass model uses its supplied threat_probability directly.
        """
        if not isinstance(binary_result, Mapping):
            return None

        probability = valid_probability(
            binary_result.get("attack_probability")
        )
        threshold = valid_probability(
            binary_result.get(
                "threshold",
                binary_result.get("decision_threshold"),
            )
        )

        if (
            probability is None
            or threshold is None
            or not 0.0 < threshold < 1.0
        ):
            return None

        suspicious_bound = float(RISK_THRESHOLDS["suspicious"])

        if probability < threshold:
            score = (probability / threshold) * suspicious_bound
        else:
            score = suspicious_bound + (
                (probability - threshold)
                / (1.0 - threshold)
            ) * (100.0 - suspicious_bound)

        return round(max(0.0, min(100.0, score)), 2)

    @staticmethod
    def parse_ml_evidence(ml_result):
        """
        Return:
            ml_score, normalized_evidence, attack_type,
            attack_confidence, ml_is_threat

        Invalid or unrecognized model output is treated as missing evidence,
        not as a Normal prediction.
        """
        empty = (
            None,
            {
                "model_type": None,
                "binary": None,
                "multiclass": None,
            },
            None,
            None,
            None,
        )

        if not isinstance(ml_result, Mapping):
            return empty

        # Current single-stage, 30-feature multiclass prediction.
        if (
            "class_probabilities" in ml_result
            and "threat_probability" in ml_result
        ):
            predicted = ml_result.get("predicted_class")
            is_threat = ml_result.get("is_threat")
            probabilities = ml_result.get("class_probabilities")

            threat_probability = valid_probability(
                ml_result.get("threat_probability")
            )
            confidence = valid_probability(
                ml_result.get("confidence")
            )
            normal_probability = valid_probability(
                ml_result.get("normal_probability")
            )

            if (
                not isinstance(predicted, str)
                or not predicted
                or type(is_threat) is not bool
                or is_threat != (predicted != "Normal")
                or not isinstance(probabilities, Mapping)
                or threat_probability is None
                or normal_probability is None
                or abs(
                    threat_probability + normal_probability - 1.0
                ) > 1e-4
            ):
                return empty

            if (
                "Normal" not in probabilities
                or any(
                    valid_probability(value) is None
                    for value in probabilities.values()
                )
            ):
                return empty

            probability_sum = sum(
                float(value) for value in probabilities.values()
            )
            if abs(probability_sum - 1.0) > 1e-4:
                return empty

            score = round(100.0 * threat_probability, 2)
            attack_type = predicted if is_threat else None

            evidence = {
                "model_type": "multiclass_30",
                "binary": None,
                "multiclass": dict(ml_result),
            }

            return (
                score,
                evidence,
                attack_type,
                confidence if attack_type else None,
                is_threat,
            )

        # Legacy binary model, optionally accompanied by multiclass output.
        if "binary" in ml_result:
            binary = ml_result.get("binary")
            multiclass = ml_result.get("multiclass")
        else:
            binary = ml_result
            multiclass = None

        if (
            not isinstance(binary, Mapping)
            or type(binary.get("is_threat")) is not bool
        ):
            return empty

        score = RiskEngine.calculate_ml_risk(binary)
        probability = valid_probability(
            binary.get("attack_probability")
        )
        threshold = valid_probability(
            binary.get(
                "threshold",
                binary.get("decision_threshold"),
            )
        )

        if (
            score is None
            or probability is None
            or threshold is None
            or binary["is_threat"] != (probability >= threshold)
        ):
            return empty

        attack_type = None
        attack_confidence = None
        normalized_multiclass = None

        if binary["is_threat"] and isinstance(multiclass, Mapping):
            candidate = multiclass.get("predicted_class")

            if (
                isinstance(candidate, str)
                and candidate
                and candidate != "Normal"
            ):
                attack_type = candidate
                attack_confidence = valid_probability(
                    multiclass.get("confidence")
                )
                normalized_multiclass = dict(multiclass)

        evidence = {
            "model_type": "legacy_binary",
            "binary": dict(binary),
            "multiclass": normalized_multiclass,
        }

        return (
            score,
            evidence,
            attack_type,
            attack_confidence,
            binary["is_threat"],
        )

    def calculate_risk(self, factors):
        """
        Calculate a weighted mean using available factors only.

        Evidence completeness records the fraction of configured weight
        represented by available factors.
        """
        total = 0.0
        available_weight = 0.0
        configured_weight = sum(LIVE_WEIGHTS.values())

        if configured_weight <= 0:
            return None, 0.0

        for key, weight in LIVE_WEIGHTS.items():
            score = self.clamp(factors.get(key))

            if score is not None and weight > 0:
                total += weight * score
                available_weight += weight

        if available_weight <= 0:
            return None, 0.0

        risk_score = total / available_weight
        completeness = min(
            1.0,
            available_weight / configured_weight,
        )

        return round(risk_score, 2), round(completeness, 2)

    @staticmethod
    def calculate_trust(risk_score, evidence_completeness):
        if risk_score is None:
            return None

        completeness = RiskEngine.clamp(
            float(evidence_completeness) * 100.0
        )
        if completeness is None:
            return None

        return round(
            (100.0 - risk_score) * (completeness / 100.0),
            2,
        )

    @staticmethod
    def classify(risk_score, trust_score):
        if risk_score is None:
            return "Unknown"

        if risk_score >= RISK_THRESHOLDS["risky"]:
            return "Risky"

        if risk_score >= RISK_THRESHOLDS["suspicious"]:
            return "Suspicious"

        if (
            trust_score is not None
            and trust_score >= TRUST_SAFE_THRESHOLD
        ):
            return "Safe"

        return "Unverified"

    def analyze(
        self,
        mode="live",
        ml_result=None,
        behavioral_features=None,
        security=None,
        behavioral_availability=None,
    ):
        """Build a risk assessment from the evidence currently available."""
        mode = str(mode).strip().lower()

        if mode not in ("live", "preliminary"):
            raise ValueError(
                "Mode must be 'live' or 'preliminary'"
            )

        static_score = self.calculate_static_risk(security)

        ml_score = None
        ml_evidence = {
            "model_type": None,
            "binary": None,
            "multiclass": None,
        }
        attack_type = None
        attack_confidence = None
        ml_threat = None

        behavior_result = None
        behavior_score = None

        if mode == "live":
            (
                ml_score,
                ml_evidence,
                attack_type,
                attack_confidence,
                ml_threat,
            ) = self.parse_ml_evidence(ml_result)

            if behavioral_features is not None:
                behavior_result = self.behavior_engine.analyze(
                    behavioral_features,
                    availability=behavioral_availability,
                )

                # Only use behavioral risk as a weighted factor when the
                # configured behavioral groups are fully scored.
                group_scores = behavior_result.get("groups", {})

                if (
                    isinstance(group_scores, Mapping)
                    and group_scores
                    and all(
                        value is not None
                        for value in group_scores.values()
                    )
                    and not behavior_result.get("missing_features")
                    and not behavior_result.get("unscored_features")
                ):
                    behavior_score = self.clamp(
                        behavior_result.get("risk")
                    )

        factors = {
            "ml": ml_score,
            "behavior": behavior_score,
            "static": static_score,
        }

        risk_score, completeness = self.calculate_risk(factors)
        trust_score = self.calculate_trust(
            risk_score,
            completeness,
        )

        if mode == "preliminary":
            assessment = "preliminary"
        elif all(value is not None for value in factors.values()):
            assessment = "full"
        else:
            assessment = "partial"

        status = self.classify(risk_score, trust_score)

        # Preliminary or incomplete evidence must not produce a Safe label.
        if status == "Safe" and assessment != "full":
            status = "Unverified"

        # A positive ML threat decision must not be hidden by a low
        # aggregate score. The result remains an alert requiring validation.
        if ml_threat is True and status in ("Safe", "Unverified"):
            status = "Suspicious"

        security_type = self.normalize_security(security)

        # build_reasons does not accept attack_type.
        reasons = self.explanation_engine.build_reasons(
            binary_result=ml_evidence["binary"],
            multiclass_result=ml_evidence["multiclass"],
            factors=factors,
            security_type=security_type,
            assessment=assessment,
            ml_is_threat=ml_threat,
            ml_model_type=ml_evidence["model_type"],
        )

        # build_recommendations DOES accept attack_type.
        recommendations = (
            self.explanation_engine.build_recommendations(
                status=status,
                assessment=assessment,
                attack_type=attack_type,
            )
        )

        alert = self.alert_engine.create_alert(
            status=status,
            risk_score=risk_score,
            trust_score=trust_score,
            attack_type=attack_type,
            confidence=attack_confidence,
            reasons=reasons,
            assessment=assessment,
        )

        return {
            "mode": mode,
            "assessment": assessment,
            "risk_score": risk_score,
            "trust_score": trust_score,
            "status": status,
            "evidence_completeness": completeness,
            "factors": factors,
            "ml_evidence": ml_evidence,
            "ml_is_threat": ml_threat,
            "attack": {
                "type": attack_type,
                "confidence": attack_confidence,
            },
            "behavioral_analysis": behavior_result,
            "missing_signals": [
                key
                for key, value in factors.items()
                if value is None
            ],
            "reasons": reasons,
            "recommendations": recommendations,
            "alert": alert,
        }
