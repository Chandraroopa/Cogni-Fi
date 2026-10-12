import math
try:
    from .risk_config import BEHAVIOR_GROUPS
except ImportError:
    from risk_config import BEHAVIOR_GROUPS

class BehavioralSeverityEngine:
    def __init__(self, baseline=None):
        self.baseline = baseline or {}

    # ---------------------------------------------------------
    # Basic severity conversion
    # ---------------------------------------------------------
    @staticmethod
    def upper_tail_severity(value, p95, p99):

        if value is None:
            return None

        try:
            value = float(value)
            p95 = float(p95)
            p99 = float(p99)
        except (TypeError, ValueError):
            return None

        if not all(math.isfinite(v) for v in (value, p95, p99)) or p95 < 0 or p99 < p95:
            return None

        if value <= p95:
            return 0.0
        # Handles zero-heavy indicators such as deauth events.
        if p99 <= p95:
            return 100.0

        if value >= p99:
            return 100.0

        severity = (
            (value - p95)
            / (p99 - p95)
            * 100.0
        )

        return round(
            max(0.0, min(100.0, severity)),
            2,
        )

    # ---------------------------------------------------------
    # Score one behavioral feature
    # ---------------------------------------------------------
    def score_feature(self, feature_name, value):

        thresholds = self.baseline.get(
            feature_name
        )
        # No validated baseline -> no score.
        if thresholds is None:
            return None

        if (
            "p95" not in thresholds
            or "p99" not in thresholds
        ):
            return None

        return self.upper_tail_severity(
            value=value,
            p95=thresholds["p95"],
            p99=thresholds["p99"],
        )

    # ---------------------------------------------------------
    # Analyze behavioral evidence
    # ---------------------------------------------------------
    def analyze(self, features):

        if not isinstance(features, dict):
            return {
                "risk": None,
                "groups": {},
                "features": {},
                "missing_features": [],
                "unscored_features": [],
                "baseline_available": bool(self.baseline),
            }

        feature_severity = {}
        group_scores = {}

        missing_features = []
        unscored_features = []

        for (
            group_name,
            group_features
        ) in BEHAVIOR_GROUPS.items():
            available_scores = []

            for feature_name in group_features:
                value = features.get(
                    feature_name
                )

                if value is None:
                    feature_severity[
                        feature_name
                    ] = None

                    missing_features.append(
                        feature_name
                    )

                    continue

                severity = self.score_feature(
                    feature_name,
                    value,
                )

                feature_severity[
                    feature_name
                ] = severity

                if severity is None:
                    unscored_features.append(
                        feature_name
                    )

                    continue

                available_scores.append(
                    severity
                )
            if available_scores:
                group_scores[group_name] = round(
                    max(available_scores),
                    2,
                )

            else:
                group_scores[group_name] = None

        available_group_scores = [
            score
            for score in group_scores.values()
            if score is not None
        ]

        if available_group_scores:
            behavioral_risk = round(
                sum(available_group_scores)
                / len(available_group_scores),
                2,
            )
        else:
            behavioral_risk = None

        return {
            "risk": behavioral_risk,
            "groups": group_scores,
            "features": feature_severity,
            "missing_features": missing_features,
            "unscored_features": unscored_features,
            "baseline_available": bool(
                self.baseline
            ),
        }