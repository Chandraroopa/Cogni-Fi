from typing import Dict, Optional


class DeltaFeatureEngine:
    """
    Computes causal cross-window delta features.

    Contract:

        delta_feature(t) = feature(t) - feature(t-1)

    The first window has no previous window, so its delta values
    are zero.

    Only the previous completed window is used.
    Future windows are never accessed.
    """

    def __init__(self):
        self.previous_features: Optional[Dict[str, float]] = None

    def transform(
        self,
        current_features: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Compute deltas for the current feature window.

        Parameters
        ----------
        current_features:
            Feature dictionary for the current completed window.

        Returns
        -------
        Dict[str, float]
            Delta features.

        Example:

            previous:
                packet_count = 10

            current:
                packet_count = 15

            output:
                delta_packet_count = 5
        """

        if not current_features:
            return {}

        delta_features = {}

        # ---------------------------------------------------------
        # First window
        # ---------------------------------------------------------

        if self.previous_features is None:

            for feature_name in current_features:

                value = current_features.get(
                    feature_name,
                    0.0,
                )

                try:
                    value = float(value)
                except (TypeError, ValueError):
                    value = 0.0

                delta_features[
                    f"delta_{feature_name}"
                ] = 0.0

            self.previous_features = dict(
                current_features
            )

            return delta_features

        # ---------------------------------------------------------
        # Subsequent windows
        # ---------------------------------------------------------

        for feature_name, current_value in (
            current_features.items()
        ):

            try:
                current_value = float(
                    current_value
                )
            except (TypeError, ValueError):
                current_value = 0.0

            previous_value = (
                self.previous_features.get(
                    feature_name,
                    0.0,
                )
            )

            try:
                previous_value = float(
                    previous_value
                )
            except (TypeError, ValueError):
                previous_value = 0.0

            delta = (
                current_value
                - previous_value
            )

            delta_features[
                f"delta_{feature_name}"
            ] = delta

        # ---------------------------------------------------------
        # Update state AFTER calculating deltas.
        # ---------------------------------------------------------

        self.previous_features = dict(
            current_features
        )

        return delta_features

    def reset(self):
        """
        Forget the previous window.

        The next window will therefore be treated as
        the first window.
        """

        self.previous_features = None