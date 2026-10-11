import json
from collections import Counter
from backend.capture.adapter import TSharkCapture
from ml.predictor import CognifiPredictor

capture = TSharkCapture(interface="5")
predictor = CognifiPredictor("ml")

results = []
availability_counts = Counter()

try:
    for packet in capture.packets():
        with open("ml/schemas/binary_feature_schema.json", encoding="utf-8") as f:
            schema = json.load(f)

        names = schema["feature_order"]
        row = {name: packet.get(name) for name in names}
        available = sum(value is not None for value in row.values())

        result = predictor.predict_binary(row)
        probability = result.get("attack_probability")

        availability_counts[available] += 1
        results.append(probability)

        print(
            f"Packet {len(results)} | "
            f"Available: {available}/82 | "
            f"Threat probability: {probability:.4f} | "
            f"Prediction: {result.get('is_threat')}"
        )

        if len(results) >= 30:
            break

except Exception as exc:
    print(f"Diagnostic error: {type(exc).__name__}: {exc}")

finally:
    try:
        capture.stop()
    except Exception:
        pass

print("\nPackets tested:", len(results))
print("Feature availability counts:", dict(availability_counts))

if results:
    print("Lowest threat probability:", round(min(results), 4))
    print("Highest threat probability:", round(max(results), 4))
    print("Average threat probability:", round(sum(results) / len(results), 4))