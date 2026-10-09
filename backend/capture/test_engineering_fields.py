from backend.capture.adapter import TSharkCapture


def main():

    capture = TSharkCapture("5")

    print("Inspecting normalized packet fields...")
    print("Waiting for one packet...\n")

    try:

        for packet in capture.packets():

            print("=== PACKET FIELDS ===")

            for key in sorted(packet.keys()):
                print(
                    f"{key}: {packet[key]!r}"
                )

            break

    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()