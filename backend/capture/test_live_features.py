
from backend.capture.adapter import TSharkCapture
from backend.capture.feature_window import FeatureExtractor


def main():
    print("Starting live TShark feature test...")
    print("Interface: 5")
    print("Waiting for packets...\n")

    capture = TSharkCapture("5")
    extractor = FeatureExtractor(window_size=1.0)

    packets = []

    try:
        for packet in capture.packets():
            packets.append(packet)

            print(
                f"Packet {len(packets)} | "
                f"timestamp={packet['timestamp']:.3f} | "
                f"length={packet['length']} | "
                f"source={packet['source']} | "
                f"destination={packet['destination']}"
            )

            if len(packets) >= 10:
                break

    except KeyboardInterrupt:
        print("\nStopped.")

    if not packets:
        print("\nERROR: No packets captured.")
        return

    print("\nExtracting features from captured packets...")

    features = extractor.extract_window_features(packets)

    print("\n=== LIVE FEATURE OUTPUT ===")

    for name, value in features.items():
        print(f"{name}: {value}")

    print("\n[SUCCESS] Live packet → feature extraction works.")


if __name__ == "__main__":
    main()

