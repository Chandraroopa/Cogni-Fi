import math
from numbers import Real

from backend.capture.adapter import TSharkCapture
from backend.capture.feature_availability import FeatureAvailabilityAnalyzer
from backend.capture.feature_window import (
    CausalWindowManager,
    FeatureExtractor,
    FEATURE_NAMES,
)

INTERFACE = "5"
PACKET_LIMIT = 100
WINDOW_SIZE = 1.0

WIFI_FLAGS = (
    "wifi_retry_available",
    "wifi_protected_available",
    "wifi_management_frames_available",
    "wifi_signal_available",
    "wifi_data_rate_available",
    "wifi_bssid_available",
)


def is_valid_number(value):
    return (
        isinstance(value, Real)
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def main():
    capture = TSharkCapture(interface=INTERFACE)
    window_manager = CausalWindowManager(window_size=WINDOW_SIZE)
    extractor = FeatureExtractor(window_size=WINDOW_SIZE)
    analyzer = FeatureAvailabilityAnalyzer()

    packet_count = 0
    windows = []

    print(f"Capturing up to {PACKET_LIMIT} packets on interface {INTERFACE}...")

    try:
        for packet in capture.packets():
            packet_count += 1
            windows.extend(window_manager.add_packet(packet))

            if packet_count >= PACKET_LIMIT:
                break
    except KeyboardInterrupt:
        print("\nCapture interrupted.")
    finally:
        try:
            capture.stop()
        finally:
            windows.extend(window_manager.flush())

    if packet_count == 0:
        print("No packets captured. Check the interface and capture permissions.")
        return

    if not windows:
        print("Packets were captured, but no feature windows were produced.")
        return

    print(f"\nPackets captured: {packet_count}")
    print(f"Feature windows audited: {len(windows)}")

    all_windows_pass = True

    for window in windows:
        packets = window["packets"]
        if not packets:
            continue

        features = extractor.extract_window_features(
            packets,
            duration=WINDOW_SIZE,
        )

        report = analyzer.multiclass_report(features)
        unavailable = report["unavailable_features"]

        print(
            f"\nWindow {window['window_id']}: "
            f"{len(packets)} packets"
        )
        print(
            f"Canonical model features: "
            f"{report['available']}/{report['expected']}"
        )

        if unavailable:
            all_windows_pass = False
            print("Unavailable model features:")
            for name in unavailable:
                print(f"  - {name}")

        vector_values = [features.get(name) for name in FEATURE_NAMES]
        valid_vector = (
            len(FEATURE_NAMES) == 30
            and len(set(FEATURE_NAMES)) == 30
            and len(vector_values) == 30
            and all(is_valid_number(value) for value in vector_values)
        )

        print(f"30 numeric model inputs present: {valid_vector}")
        if not valid_vector:
            all_windows_pass = False

        print("Wi-Fi diagnostic flags:")
        for name in WIFI_FLAGS:
            print(f"  {name}: {features.get(name, False)}")

    print("\nFINAL RESULT")
    if all_windows_pass:
        print("PASS: All audited windows contain 30 numeric canonical features.")
    else:
        print("CHECK REQUIRED: One or more windows failed canonical feature validation.")

    print(
        "Wi-Fi flags are diagnostics only; they are not model inputs. "
        "Numeric availability does not prove training-time semantic compatibility."
    )


if __name__ == "__main__":
    main()
