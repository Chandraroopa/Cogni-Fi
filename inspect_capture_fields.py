
from backend.capture.adapter import TSharkCapture

capture = TSharkCapture("5")
wanted_layers = (
    "radiotap", "wlan", "frame", "tcp", "udp",
    "ip", "ipv6", "arp", "llc", "tls", "http",
    "ssdp", "ssh",
)

try:
    for index, packet in enumerate(capture.packets(), start=1):
        layers = packet.get("layers", {})
        print(f"\nPACKET {index}")

        for layer_name in wanted_layers:
            layer = layers.get(layer_name, {})
            if isinstance(layer, dict) and layer:
                print(f"{layer_name}: {list(layer.keys())}")

        if index >= 10:
            break
finally:
    capture.stop()
