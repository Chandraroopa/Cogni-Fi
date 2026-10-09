from backend.capture.feature_window import FeatureExtractor
from backend.capture.adapter import TSharkCapture
from backend.capture.live_detector import LiveRiskDetector


INTERFACE = "5"


def main():
    print("Starting live TShark → Feature → Risk test...")
    print(f"Interface: {INTERFACE}")
    print("Waiting for packets...\n")

    capture = TSharkCapture(interface=INTERFACE)
    extractor = FeatureExtractor(window_size=1.0)
    detector = LiveRiskDetector()

    packets = []

    for packet in capture.packets():
        packets.append(packet)

        print(
            f"Packet {len(packets)} | "
            f"timestamp={packet.get('timestamp')} | "
            f"length={packet.get('length')} | "
            f"source={packet.get('source')} | "
            f"destination={packet.get('destination')}"
        )

        if len(packets) >= 10:
            break

    if not packets:
        print("\n[ERROR] No packets captured.")
        return

    # Use the actual FeatureExtractor API.
    features = extractor.extract_window_features(packets)

    print("\n=== LIVE FEATURES ===")

    for name, value in features.items():
        print(f"{name}: {value}")

    # Run the live risk engine.
    risk = detector.analyze(features)

    print("\n=== LIVE RISK RESULT ===")
    print(f"Risk Level : {risk['risk_level']}")
    print(f"Risk Score : {risk['risk_score']}")

    print("Reasons:")
    for reason in risk["reasons"]:
        print(f" - {reason}")


if __name__ == "__main__":
    main()