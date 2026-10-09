from collections import deque
from typing import Dict, List


class CausalRollingFeatureEngine:
    """
    Computes causal rolling statistics over completed windows.

    Default history:
        3 windows

    At window t, only:
        t-2
        t-1
        t

    are available.

    No future window is ever used.
    """

    def __init__(self, window_count: int = 3):
        if window_count < 1:
            raise ValueError(
                "window_count must be >= 1"
            )

        self.window_count = window_count

        self.history = deque(
            maxlen=window_count
        )

    def transform(
        self,
        current_features: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Add current window to causal history and
        calculate rolling mean/std.

        The current window IS included.

        Therefore for window t:

            history = [t-2, t-1, t]

        when enough windows exist.
        """

        if not current_features:
            return {}

        # Add a copy so external mutation cannot
        # modify our stored history.
        self.history.append(
            dict(current_features)
        )

        result = {}

        feature_names = set()

        for window in self.history:
            feature_names.update(
                window.keys()
            )

        for feature_name in sorted(
            feature_names
        ):

            values: List[float] = []

            for window in self.history:

                value = window.get(
                    feature_name,
                    0.0,
                )

                try:
                    value = float(value)
                except (
                    TypeError,
                    ValueError,
                ):
                    value = 0.0

                values.append(value)

            if not values:
                continue

            rolling_mean = (
                sum(values)
                / len(values)
            )

            if len(values) > 1:

                variance = sum(
                    (
                        value
                        - rolling_mean
                    ) ** 2
                    for value in values
                ) / len(values)

                rolling_std = (
                    variance ** 0.5
                )

            else:
                rolling_std = 0.0

            result[
                f"rolling_{feature_name}_mean"
            ] = rolling_mean

            result[
                f"rolling_{feature_name}_std"
            ] = rolling_std

        return result

    def reset(self):
        """
        Clear causal history.
        """

        self.history.clear()

    @property
    def history_size(self):
        return len(self.history)