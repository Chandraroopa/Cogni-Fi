from backend.capture.feature_window import (
    CausalWindowManager,
)


def make_packet(timestamp, number):
    return {
        "timestamp": timestamp,
        "length": 100 + number,
        "source": f"source-{number}",
        "destination": f"destination-{number}",
    }


def main():

    manager = CausalWindowManager(
        window_size=1.0
    )

    packets = [
        make_packet(100.00, 1),
        make_packet(100.20, 2),
        make_packet(100.90, 3),

        make_packet(101.00, 4),
        make_packet(101.40, 5),

        make_packet(102.20, 6),
    ]

    for packet in packets:

        completed = manager.add_packet(
            packet
        )

        for window in completed:

            print(
                f"COMPLETED "
                f"window_id={window['window_id']} "
                f"packets={len(window['packets'])} "
                f"start={window['start_timestamp']:.2f} "
                f"end={window['end_timestamp']:.2f}"
            )

    for window in manager.flush():

        print(
            f"FLUSHED "
            f"window_id={window['window_id']} "
            f"packets={len(window['packets'])} "
            f"start={window['start_timestamp']:.2f} "
            f"end={window['end_timestamp']:.2f}"
        )


if __name__ == "__main__":
    main()