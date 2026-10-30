
import math

try:
    from .risk_config import BEHAVIOR_GROUPS
except ImportError:
    from risk_config import BEHAVIOR_GROUPS


# Wi-Fi capture availability metadata.
BEHAVIOR_WIFI_FLAGS = {
    "retry_rate": "wifi_retry_available",
    "deauth_rate": "wifi_management_frames_available",
    "disassoc_rate": "wifi_management_frames_available",
}

WIFI_AVAILABILITY_FLAGS = BEHAVIOR_WIFI_FLAGS.copy()


# Explicit network measurement availability metadata.
NETWORK_AVAILABILITY_FLAGS = {
    "rst_rate": "tcp_rst_available",
    "retransmission_rate": "tcp_retransmission_available",
    "dns_latency_mean": "dns_latency_available",
}


class BehavioralSeverityEngine:
    def __init__(self, baseline=None):
        self.baseline = baseline or {}

    @staticmethod
    def upper_tail_severity(value, p95, p99):
        """Calculate severity using validated p95 and p99 thresholds."""

        if any(
            isinstance(v, bool)
            for v in (value, p95, p99)
        ):
            return None

        try:
            value = float(value)
            p95 = float(p95)
            p99 = float(p99)
        except (TypeError, ValueError, OverflowError):
            return None

        if not all(
            math.isfinite(v)
            for v in (value, p95, p99)
        ):
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
        """Score a feature only when valid baseline thresholds exist."""

        thresholds = self.baseline.get(feature_name)

        if not isinstance(thresholds, dict):
            return None

        if (
            "p95" not in thresholds
            or "p99" not in thresholds
        ):
            return None

        return self.upper_tail_severity(
            value,
            thresholds["p95"],
            thresholds["p99"],
        )

    @staticmethod
    def is_available(feature_name, availability):
        """
        Check explicit per-feature availability first.

        If no explicit feature entry exists, use the corresponding
        Wi-Fi or network metadata flag.
        """

        if not isinstance(availability, dict):
            return False

        # Explicit per-feature verdict takes priority.
        if feature_name in availability:
            return availability[feature_name] is True

        # Wi-Fi metadata fallback.
        wifi_flag = WIFI_AVAILABILITY_FLAGS.get(feature_name)

        if wifi_flag is not None:
            return availability.get(wifi_flag) is True

        # Network metadata fallback.
        network_flag = NETWORK_AVAILABILITY_FLAGS.get(
            feature_name
        )

        if network_flag is not None:
            return availability.get(network_flag) is True

        return False

    def analyze(self, features, availability=None):
        """Calculate feature and group severity from available evidence."""

        features = (
            features
            if isinstance(features, dict)
            else {}
        )

        availability = (
            availability
            if isinstance(availability, dict)
            else {}
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

                # Check metadata and explicit feature availability.
                verified = self.is_available(
                    feature_name,
                    availability,
                )

                if not verified:

                    feature_severity[feature_name] = None
                    unavailable_features.append(feature_name)

                    continue

                if value is None:

                    feature_severity[feature_name] = None
                    missing_features.append(feature_name)

                    continue

                # Apply validated baseline thresholds.
                severity = self.score_feature(
                    feature_name,
                    value,
                )

                feature_severity[feature_name] = severity

                if severity is None:

                    unscored_features.append(feature_name)

                    continue

                scored_values.append(severity)

            # Preserve the existing maximum-severity group calculation.
            group_scores[group_name] = (
                round(max(scored_values), 2)
                if scored_values
                else None
            )

        # Calculate behavioral risk from available groups.
        valid_group_scores = [
            score
            for score in group_scores.values()
            if score is not None
        ]

        behavioral_risk = (
            round(
                sum(valid_group_scores)
                / len(valid_group_scores),
                2,
            )
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
