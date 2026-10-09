from backend.capture.rolling_features import (
    CausalRollingFeatureEngine,
)


def main():

    engine = CausalRollingFeatureEngine(
        window_count=3
    )

    # =========================================================
    # Window 0
    # =========================================================

    window_0 = {
        "packet_count": 10.0,
        "byte_count": 1000.0,
    }

    rolling_0 = engine.transform(
        window_0
    )

    print("WINDOW 0")
    print(rolling_0)

    assert (
        rolling_0[
            "rolling_packet_count_mean"
        ]
        == 10.0
    )

    assert (
        rolling_0[
            "rolling_packet_count_std"
        ]
        == 0.0
    )

    # =========================================================
    # Window 1
    # =========================================================

    window_1 = {
        "packet_count": 20.0,
        "byte_count": 2000.0,
    }

    rolling_1 = engine.transform(
        window_1
    )

    print("\nWINDOW 1")
    print(rolling_1)

    assert (
        rolling_1[
            "rolling_packet_count_mean"
        ]
        == 15.0
    )

    # Population standard deviation:
    # sqrt(((10-15)^2 + (20-15)^2) / 2)
    assert abs(
        rolling_1[
            "rolling_packet_count_std"
        ]
        - 5.0
    ) < 1e-9

    # =========================================================
    # Window 2
    # =========================================================

    window_2 = {
        "packet_count": 30.0,
        "byte_count": 3000.0,
    }

    rolling_2 = engine.transform(
        window_2
    )

    print("\nWINDOW 2")
    print(rolling_2)

    # History is now:
    #
    # [10, 20, 30]
    #
    assert (
        rolling_2[
            "rolling_packet_count_mean"
        ]
        == 20.0
    )

    # Population std of [10,20,30]
    # = sqrt(200/3)
    expected_std = (
        200.0 / 3.0
    ) ** 0.5

    assert abs(
        rolling_2[
            "rolling_packet_count_std"
        ]
        - expected_std
    ) < 1e-9

    # =========================================================
    # Window 3
    # =========================================================

    window_3 = {
        "packet_count": 40.0,
        "byte_count": 4000.0,
    }

    rolling_3 = engine.transform(
        window_3
    )

    print("\nWINDOW 3")
    print(rolling_3)

    # Window 0 must now be removed.
    #
    # History:
    # [20, 30, 40]
    #
    assert (
        rolling_3[
            "rolling_packet_count_mean"
        ]
        == 30.0
    )

    # =========================================================
    # Verify history size
    # =========================================================

    assert (
        engine.history_size
        == 3
    )

    # =========================================================
    # Reset
    # =========================================================

    engine.reset()

    assert (
        engine.history_size
        == 0
    )

    print(
        "\n[SUCCESS] "
        "Causal rolling feature tests passed."
    )


if __name__ == "__main__":
    main()