
import numpy as np

from ml.inference.predictor import load_predictor, predict_one


def test_predictor_loads_30_features_and_14_classes():
    model, features = load_predictor()

    assert len(features) == 30
    assert model.n_features_in_ == 30
    assert len(model.classes_) == 14


def test_predictor_returns_valid_probabilities():
    model, features = load_predictor()
    feature_values = {name: 0.0 for name in features}

    result = predict_one(feature_values)

    assert result["predicted_class"] in [str(c) for c in model.classes_]
    assert len(result["class_probabilities"]) == 14

    probabilities = np.array(
        list(result["class_probabilities"].values()), dtype=float
    )

    assert np.isfinite(probabilities).all()
    assert np.all(probabilities >= 0)
    assert np.all(probabilities <= 1)
    assert np.isclose(probabilities.sum(), 1.0, atol=1e-5)
    assert result["is_threat"] == (result["predicted_class"] != "Normal")


def test_predictor_rejects_missing_features():
    _, features = load_predictor()
    values = {name: 0.0 for name in features}
    values.pop(features[0])

    try:
        predict_one(values)
    except ValueError:
        pass
    else:
        raise AssertionError("Missing features were accepted")


def test_predictor_rejects_nan():
    _, features = load_predictor()
    values = {name: 0.0 for name in features}
    values[features[0]] = float("nan")

    try:
        predict_one(values)
    except ValueError:
        pass
    else:
        raise AssertionError("NaN input was accepted")
