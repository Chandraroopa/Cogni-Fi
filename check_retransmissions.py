import json
import subprocess
from backend.capture.adapter import normalize_packet

frames = {73, 198, 216, 377, 398, 594, 698, 702, 707, 732, 733, 734, 735, 1377}
result = subprocess.run(
    ["tshark", "-r", "tcp_capture.pcapng", "-T", "ek"],
    capture_output=True, text=True, check=True
)

for line in result.stdout.splitlines():
    if not line.strip():
        continue
    item = json.loads(line)
    if not isinstance(item, dict) or "layers" not in item:
        continue
    layers = item["layers"]
    frame = layers.get("frame", {}).get("frame_frame_number")
    if frame and int(frame) in frames:
        packet = normalize_packet(item)
        print(f"Frame {frame}: tcp_retransmission={packet.get('tcp_retransmission')}")
