
"""SHAP explanations for Cognifi's 30-feature multiclass model."""

import numpy as np
import pandas as pd
import shap

from ml.inference.predictor import load_predictor


def explain_one(feature_values, top_n=10):
    model, feature_names = load_predictor()

    missing = [name for name in feature_names if name not in feature_values]
    if missing:
        raise ValueError(f"Missing features: {missing}")

    row = {}
    for name in feature_names:
        value = float(feature_values[name])
        if not np.isfinite(value):
            raise ValueError(f"Feature {name} must be finite.")
        row[name] = value

    frame = pd.DataFrame([row], columns=feature_names)
    probabilities = model.predict_proba(frame)[0]
    classes = [str(c) for c in model.classes_]
    predicted_index = int(np.argmax(probabilities))
    predicted_class = classes[predicted_index]

    explainer = shap.TreeExplainer(model)
    values = explainer.shap_values(frame, check_additivity=False)

    # SHAP versions may return a list or a 3-D array for multiclass.
    if isinstance(values, list):
        contributions = np.asarray(values[predicted_index])[0]
    else:
        values = np.asarray(values)
        if values.ndim == 3:
            if values.shape[-1] == len(classes):
                contributions = values[0, :, predicted_index]
            elif values.shape[0] == len(classes):
                contributions = values[predicted_index, 0, :]
            else:
                raise ValueError(f"Unexpected SHAP shape: {values.shape}")
        elif values.ndim == 2:
            contributions = values[0]
        else:
            raise ValueError(f"Unexpected SHAP shape: {values.shape}")

    if len(contributions) != len(feature_names):
        raise ValueError("SHAP contribution count does not match features.")

    ranked = sorted(
        [
            {
                "feature": name,
                "value": float(row[name]),
                "contribution": float(contribution),
            }
            for name, contribution in zip(feature_names, contributions)
        ],
        key=lambda item: abs(item["contribution"]),
        reverse=True,
    )

    return {
        "predicted_class": predicted_class,
        "confidence": float(probabilities[predicted_index]),
        "explanation_method": "SHAP TreeExplainer",
        "contribution_space": "model output; not probability points",
        "top_features": ranked[:max(1, min(top_n, len(ranked)))],
    }
