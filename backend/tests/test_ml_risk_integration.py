import pytest

from ml.inference.predictor import predict_one, load_predictor
from backend.risk_engine import RiskEngine


def test_actual_predictor_to_risk_engine():
    # Load the actual trained 30-feature model.
    _, feature_names = load_predictor()

    assert len(feature_names) == 30

    # Synthetic software-test input, NOT real Wi-Fi traffic.
    features = {name: 0.0 for name in feature_names}

    # Person 1's actual ML model performs inference.
    ml_prediction = predict_one(features)

    # Your Risk Engine consumes the model's actual output.
    risk_result = RiskEngine().analyze(
        mode="live",
        ml_result=ml_prediction,
        behavioral_features=None,
        security=None,
    )

    # Verify the model-to-risk interface.
    assert risk_result["factors"]["ml"] is not None
    assert 0 <= risk_result["factors"]["ml"] <= 100

    assert risk_result["attack"]["type"] == (
        ml_prediction["predicted_class"]
        if ml_prediction["is_threat"]
        else None
    )

    assert risk_result["assessment"] == "partial"
    assert isinstance(risk_result["reasons"], list)
    assert isinstance(risk_result["recommendations"], list)
    assert "alert" in risk_result

import json
import math
from pathlib import Path

from ml.inference.predictor import predict_one, load_predictor
from backend.risk_engine import RiskEngine


def test_real_43_packet_window_to_risk_engine():
    root = Path(__file__).resolve().parents[2]
    handoff_path = root / "docs" / "risk_engine_window_handoff.json"

    with handoff_path.open("r", encoding="utf-8") as file:
        handoff = json.load(file)

    window = handoff["window"]
    features = window["features"]
    flags = window["availability_flags"]

    _, feature_names = load_predictor()

    assert len(feature_names) == 30
    assert set(features) == set(feature_names)
    assert window["packet_count"] == 43
    assert window["traffic_label"] == "unlabelled"

    for name in feature_names:
        assert isinstance(features[name], (int, float))
        assert math.isfinite(features[name])

    expected_flags = {
        "wifi_retry_available",
        "wifi_protected_available",
        "wifi_management_frames_available",
        "wifi_signal_available",
        "wifi_data_rate_available",
        "wifi_bssid_available",
    }

    assert set(flags) == expected_flags
    assert all(flags[name] is False for name in expected_flags)

    # Predict using the current 30-feature model.
    # Availability metadata is NOT a model input.
    ml_result = predict_one(features)

    assert ml_result["model_features"] == 30
    assert len(ml_result["class_probabilities"]) == 14
    assert ml_result["is_threat"] == (
        ml_result["predicted_class"] != "Normal"
    )

    # No validated behavioral baseline or security evidence yet.
    risk_result = RiskEngine(behavior_baseline=None).analyze(
        mode="live",
        ml_result=ml_result,
        behavioral_features=None,
        security=None,
    )

    assert risk_result["assessment"] == "partial"
    assert risk_result["factors"]["ml"] is not None
    assert risk_result["factors"]["behavior"] is None
    assert risk_result["factors"]["static"] is None

    assert 0 <= risk_result["risk_score"] <= 100
    assert 0 <= risk_result["trust_score"] <= 100

    expected_attack = (
        ml_result["predicted_class"]
        if ml_result["is_threat"]
        else None
    )

    assert risk_result["attack"]["type"] == expected_attack
    assert isinstance(risk_result["reasons"], list)
    assert isinstance(risk_result["recommendations"], list)
    assert "alert" in risk_result


import csv
import json
from pathlib import Path

from ml.inference.predictor import load_predictor, predict_one
from backend.risk_engine import RiskEngine


def test_real_five_minute_capture_to_risk_engine():
    root = Path(__file__).resolve().parents[2]

    csv_path = root / "data" / "live_windows_20261013_013828.csv"
    json_path = root / "data" / "live_windows_20261013_013828.json"

    with json_path.open(encoding="utf-8") as file:
        metadata = json.load(file)

    with csv_path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    _, feature_names = load_predictor()

    assert metadata["window_count"] == len(rows)
    assert metadata["feature_names"] == feature_names
    assert len(feature_names) == 30

    risk_engine = RiskEngine(behavior_baseline=None)
    tested = 0

    for row in rows:
        assert row["traffic_label"] == "unlabelled"

        # Empty exported windows have no observed packet evidence.
        # Do not interpret their zero-filled features as a normal
        # or safe classification.
        if row["is_empty"].lower() == "true":
            continue

        features = {
            name: float(row[name])
            for name in feature_names
        }

        ml_result = predict_one(features)

        result = risk_engine.analyze(
            mode="live",
            ml_result=ml_result,
            behavioral_features=None,
            security=None,
        )

        assert result["assessment"] == "partial"
        assert result["factors"]["ml"] is not None
        assert result["factors"]["behavior"] is None
        assert result["factors"]["static"] is None

        assert 0 <= result["risk_score"] <= 100
        assert 0 <= result["trust_score"] <= 100

        assert result["attack"]["type"] == (
            ml_result["predicted_class"]
            if ml_result["is_threat"]
            else None
        )

        assert isinstance(result["reasons"], list)
        assert isinstance(result["recommendations"], list)

        tested += 1

    assert tested > 0
