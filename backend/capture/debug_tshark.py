
import subprocess
import json

print("Starting raw TShark debug...")
print("Interface: 5")
print("Waiting for the first real packet...\n")

cmd = [
    "tshark",
    "-i", "5",
    "-T", "ek",
    "-l",
]

process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding="utf-8",
    errors="replace",
)

try:
    for line in process.stdout:
        line = line.strip()

        if not line:
            continue

        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Skip TShark metadata/index records.
        if "index" in data:
            continue

        print("=== RAW PACKET JSON OBJECT ===")
        print(json.dumps(data, indent=2))

        print("\n=== TOP LEVEL KEYS ===")
        print(list(data.keys()))

        layers = data.get("layers", {})

        print("\n=== LAYER KEYS ===")
        print(list(layers.keys()))

        print("\n=== COMPLETE DEBUG PACKET ===")
        print(json.dumps(layers, indent=2))

        break

finally:
    if process.poll() is None:
        process.terminate()

    process.wait()

print("\n=== DEBUG COMPLETE ===")

