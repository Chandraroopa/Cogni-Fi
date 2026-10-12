import math

try:
    from .risk_config import BEHAVIOR_GROUPS
except ImportError:
    from risk_config import BEHAVIOR_GROUPS


# These flags come from Person 2's capture metadata.
WIFI_AVAILABILITY_FLAGS = {
    "retry_rate": "wifi_retry_available",
    "deauth_rate": "wifi_management_frames_available",
    "disassoc_rate": "wifi_management_frames_available",
}


class BehavioralSeverityEngine:

    def __init__(self, baseline=None):
        self.baseline = baseline or {}

    @staticmethod
    def upper_tail_severity(value, p95, p99):
        if any(isinstance(v, bool) for v in (value, p95, p99)):
            return None

        try:
            value = float(value)
            p95 = float(p95)
            p99 = float(p99)
        except (TypeError, ValueError, OverflowError):
            return None

        if not all(math.isfinite(v) for v in (value, p95, p99)):
            return None

        if value < 0 or p95 < 0 or p99 < p95:
            return None

        if value <= p95:
            return 0.0

        if p99 == p95:
            return 100.0

        if value >= p99:
            return 100.0

        return round(
            100.0 * (value - p95) / (p99 - p95),
            2,
        )

    def score_feature(self, feature_name, value):
        thresholds = self.baseline.get(feature_name)

        if not isinstance(thresholds, dict):
            return None

        if "p95" not in thresholds or "p99" not in thresholds:
            return None

        return self.upper_tail_severity(
            value,
            thresholds["p95"],
            thresholds["p99"],
        )

    @staticmethod
    def is_available(feature_name, availability):
        if not isinstance(availability, dict):
            return False

        # Explicit per-feature verdict takes priority.
        if feature_name in availability:
            return availability[feature_name] is True

        # Allow Person 2's actual Wi-Fi availability flags.
        flag = WIFI_AVAILABILITY_FLAGS.get(feature_name)

        if flag is not None:
            return availability.get(flag) is True

        return False

    def analyze(self, features, availability=None):
        features = features if isinstance(features, dict) else {}
        availability = (
            availability if isinstance(availability, dict) else {}
        )

        feature_severity = {}
        group_scores = {}
        missing_features = []
        unavailable_features = []
        unscored_features = []

        for group_name, group_features in BEHAVIOR_GROUPS.items():
            scored_values = []

            for feature_name in group_features:
                value = features.get(feature_name)

                if value is None:
                    feature_severity[feature_name] = None
                    missing_features.append(feature_name)
                    continue

                if not self.is_available(feature_name, availability):
                    feature_severity[feature_name] = None
                    unavailable_features.append(feature_name)
                    continue

                severity = self.score_feature(feature_name, value)
                feature_severity[feature_name] = severity

                if severity is None:
                    unscored_features.append(feature_name)
                    continue

                scored_values.append(severity)

            group_scores[group_name] = (
                round(max(scored_values), 2)
                if scored_values
                else None
            )

        valid_group_scores = [
            score
            for score in group_scores.values()
            if score is not None
        ]

        behavioral_risk = (
            round(sum(valid_group_scores) / len(valid_group_scores), 2)
            if valid_group_scores
            else None
        )

        return {
            "risk": behavioral_risk,
            "groups": group_scores,
            "features": feature_severity,
            "missing_features": missing_features,
            "unavailable_features": unavailable_features,
            "unscored_features": unscored_features,
            "baseline_available": bool(self.baseline),
        }
