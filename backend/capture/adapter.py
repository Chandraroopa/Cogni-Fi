import subprocess
import json

def normalize_packet(packet_dict):
    """Normalize raw TShark packet dictionaries into a consistent schema."""
    layers = packet_dict.get("layers", {})
    
    # TShark -T ek nests frame details under 'frame' or 'layers'
    frame_layer = layers.get("frame", {})
    raw_len = (
        frame_layer.get("frame_len") or 
        layers.get("length") or 
        packet_dict.get("length") or 
        0
    )

    try:
        length = int(float(raw_len))
    except (ValueError, TypeError):
        length = 0

    timestamp = 0.0
    try:
        timestamp = float(frame_layer.get("frame_time_epoch", 0.0))
    except (ValueError, TypeError):
        pass

    return {
        "timestamp": timestamp,
        "length": length,
        "layers": layers
    }
class TSharkCapture:
    def __init__(self, interface):
        self.interface = interface

    def packets(self):
        cmd = [
            "tshark",
            "-i", self.interface,
            "-T", "ek"
        ]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        
        for line in process.stdout:
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                    if "index" not in data:
                        yield normalize_packet(data)
                except json.JSONDecodeError:
                    continue