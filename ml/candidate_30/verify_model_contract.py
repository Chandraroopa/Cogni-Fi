
import json
from pathlib import Path

from ml.candidate_30.predictor_30 import load_predictor

BASE_DIR = Path(__file__).resolve().parent


def main():
    model, features = load_predictor()

    with open(BASE_DIR / "class_mapping.json", "r", encoding="utf-8") as f:
        mapping = json.load(f)

    print("Model classes:", list(model.classes_))
    print("Mapping file:", mapping)

    print("\nFeature count:", len(features))
    print("Class count:", len(model.classes_))

    assert len(features) == 30, "Expected 30 features"
    assert len(model.classes_) == 14, "Expected 14 classes"

    # Show mapping structure before comparing it.
    print("\nMapping JSON type:", type(mapping).__name__)
    print("PASS: model has 30 features and 14 classes")


if __name__ == "__main__":
    main()
