from backend.capture.adapter import TSharkCapture


FIELDS = [
    "frame.len",
    "frame.time_delta",
    "frame.time_delta_displayed",
    "radiotap.channel.freq",
    "radiotap.dbm_antsignal",
    "wlan.fc.type",
    "wlan.fc.retry",
    "wlan.seq",
    "ip.proto",
    "ip.ttl",
    "ip.version",
    "tcp.ack",
    "tcp.seq",
    "tcp.srcport",
    "tcp.dstport",
    "udp.srcport",
    "udp.dstport",
    "udp.length",
    "tls.record.version",
]


def main():
    capture = TSharkCapture("5")

    for number, packet in enumerate(capture.packets(), start=1):

        print(f"\n===== PACKET {number} =====")

        for field in FIELDS:
            print(
                f"{field:35} = "
                f"{packet.get(field)!r}"
            )

        if number >= 10:
            break


if __name__ == "__main__":
    main()