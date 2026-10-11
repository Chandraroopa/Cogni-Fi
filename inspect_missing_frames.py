import json
import subprocess

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
    if frame in ("198", "594"):
        print("FRAME:", frame)
        print("TCP:", json.dumps(layers.get("tcp", {}), indent=2))
