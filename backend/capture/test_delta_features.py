from backend.capture.delta_features import (
    DeltaFeatureEngine,
)


def main():

    engine = DeltaFeatureEngine()

    # =========================================================
    # Window 0
    # =========================================================

    window_0 = {
        "packet_count": 10.0,
        "byte_count": 1000.0,
        "iat_mean": 0.10,
        "syn_rate": 0.20,
    }

    delta_0 = engine.transform(
        window_0
    )

    print("WINDOW 0")
    print(delta_0)

    assert delta_0["delta_packet_count"] == 0.0
    assert delta_0["delta_byte_count"] == 0.0
    assert delta_0["delta_iat_mean"] == 0.0
    assert delta_0["delta_syn_rate"] == 0.0

    # =========================================================
    # Window 1
    # =========================================================

    window_1 = {
        "packet_count": 15.0,
        "byte_count": 1500.0,
        "iat_mean": 0.20,
        "syn_rate": 0.50,
    }

    delta_1 = engine.transform(
        window_1
    )

    print("\nWINDOW 1")
    print(delta_1)

    assert delta_1["delta_packet_count"] == 5.0
    assert delta_1["delta_byte_count"] == 500.0
    assert delta_1["delta_iat_mean"] == 0.10
    assert delta_1["delta_syn_rate"] == 0.30

    # =========================================================
    # Window 2
    # =========================================================

    window_2 = {
        "packet_count": 12.0,
        "byte_count": 1200.0,
        "iat_mean": 0.15,
        "syn_rate": 0.25,
    }

    delta_2 = engine.transform(
        window_2
    )

    print("\nWINDOW 2")
    print(delta_2)

    assert delta_2["delta_packet_count"] == -3.0
    assert delta_2["delta_byte_count"] == -300.0

    assert (
        abs(
            delta_2["delta_iat_mean"]
            - (-0.05)
        )
        < 1e-9
    )

    assert (
        abs(
            delta_2["delta_syn_rate"]
            - (-0.25)
        )
        < 1e-9
    )

    # =========================================================
    # Verify reset
    # =========================================================

    engine.reset()

    window_after_reset = {
        "packet_count": 20.0,
    }

    delta_after_reset = engine.transform(
        window_after_reset
    )

    print("\nAFTER RESET")
    print(delta_after_reset)

    assert (
        delta_after_reset[
            "delta_packet_count"
        ]
        == 0.0
    )

    print(
        "\n[SUCCESS] "
        "Delta feature tests passed."
    )


if __name__ == "__main__":
    main()