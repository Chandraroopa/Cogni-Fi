
import numpy as np

from ml.candidate_30.predictor_30 import load_predictor, predict_one


def main():
    model, features = load_predictor()

    assert len(features) == 30, f"Expected 30 features, got {len(features)}"

    # Neutral test input to check the inference pipeline.
    # This is not a real captured Wi-Fi window.
    feature_values = {name: 0.0 for name in features}

    result = predict_one(feature_values)

    assert result["predicted_class"] in model.classes_, (
        "Predicted class is not in the model's class list"
    )
    assert len(result["class_probabilities"]) == 14, (
        "Expected probabilities for 14 classes"
    )

    probabilities = np.array(
        list(result["class_probabilities"].values()), dtype=float
    )

    assert np.isfinite(probabilities).all(), "Probabilities contain invalid values"
    assert np.all(probabilities >= 0), "Negative probability found"
    assert np.isclose(probabilities.sum(), 1.0, atol=1e-5), (
        f"Probabilities do not sum to 1: {probabilities.sum()}"
    )

    assert result["is_threat"] == (result["predicted_class"] != "Normal"), (
        "Threat flag does not match the predicted class"
    )

    print("PASS: 30-feature predictor smoke test")
    print("Predicted class:", result["predicted_class"])
    print("Threat detected:", result["is_threat"])
    print("Confidence:", result["confidence"])
    print("Probability sum:", probabilities.sum())
    print("Note: zero-valued input is a software test, not a valid attack assessment.")


if __name__ == "__main__":
    main()
