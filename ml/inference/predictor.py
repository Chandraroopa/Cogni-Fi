
"""Prediction interface for Cognifi's 30-feature multiclass candidate."""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


ML_DIR = Path(__file__).resolve().parents[1]

MODEL_PATH = ML_DIR / "models" / "cognifi_multiclass_30_candidate.joblib"
SCHEMA_PATH = ML_DIR / "schemas" / "feature_schema.json"
NORMAL_CLASS = "Normal"


def load_predictor():
    """Load the candidate model and validate its feature contract."""
    with SCHEMA_PATH.open("r", encoding="utf-8") as file:
        schema = json.load(file)

    features = schema["features"]
    if features and isinstance(features[0], dict):
        feature_names = [item["name"] for item in features]
    else:
        feature_names = list(features)

    model = joblib.load(MODEL_PATH)

    if len(feature_names) != 30:
        raise ValueError(
            f"Expected 30 schema features; found {len(feature_names)}."
        )

    if getattr(model, "n_features_in_", None) != len(feature_names):
        raise ValueError("Model input count does not match the schema.")

    model_features = list(
        getattr(model, "feature_name_", feature_names)
    )

    if model_features != feature_names:
        raise ValueError("Model feature order does not match the schema.")

    return model, feature_names


def predict_one(feature_values):
    """
    Predict one window.

    feature_values must be a dictionary containing all 30 model features.
    Availability flags may be included, but are not model inputs.
    """
    model, feature_names = load_predictor()

    missing = [name for name in feature_names if name not in feature_values]
    if missing:
        raise ValueError(f"Missing model features: {missing}")

    row = {}
    for name in feature_names:
        try:
            value = float(feature_values[name])
        except (TypeError, ValueError):
            raise ValueError(f"Feature {name!r} must be numeric.")

        if not np.isfinite(value):
            raise ValueError(f"Feature {name!r} must be finite.")

        row[name] = value

    frame = pd.DataFrame([row], columns=feature_names)
    probabilities = model.predict_proba(frame)[0]
    classes = list(model.classes_)

    if not np.isfinite(probabilities).all():
        raise ValueError("Model returned non-finite probabilities.")

    if not np.isclose(probabilities.sum(), 1.0, atol=1e-5):
        raise ValueError("Model probabilities do not sum to 1.")

    best_index = int(np.argmax(probabilities))
    predicted_class = str(classes[best_index])
    probability_by_class = {
        str(label): float(probability)
        for label, probability in zip(classes, probabilities)
    }

    normal_probability = probability_by_class.get(NORMAL_CLASS, 0.0)

    threat_probability = sum(
        probability
        for label, probability in probability_by_class.items()
        if label != NORMAL_CLASS
    )
    
    top_indices = np.argsort(probabilities)[::-1][:3]
    top_predictions = [
        {
            "class": str(classes[index]),
            "probability": float(probabilities[index]),
        }
        for index in top_indices
    ]

    return {
        "predicted_class": predicted_class,
        "is_threat": predicted_class != NORMAL_CLASS,
        "threat_type": (
            predicted_class if predicted_class != NORMAL_CLASS else None
        ),
        "confidence": float(probabilities[best_index]),
        "threat_probability": threat_probability,
        "normal_probability": float(normal_probability),
        "class_probabilities": probability_by_class,
        "top_3": top_predictions,
        "model_features": len(feature_names),
    }


if __name__ == "__main__":
    model, feature_names = load_predictor()
    print("Cognifi 30-feature predictor loaded successfully.")
    print(f"Model: {type(model).__name__}")
    print(f"Features: {len(feature_names)}")
    print(f"Classes: {len(model.classes_)}")
    print("Feature order: PASS")
    print("This check loads the model; it does not perform a prediction.")
