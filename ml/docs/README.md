# Cognifi — 30-Feature Multiclass ML Candidate

## 1. Purpose

This module classifies a window of Wi-Fi/network traffic features as Normal or one of 13 threat classes. It provides multiclass predictions and class probabilities for integration with Cognifi's trust and risk engine.

**Status:** Offline evaluation completed. Predictor, smoke tests, capture integration test, and a synthetic-input SHAP execution test have passed. Live detection quality and explanations on real captured traffic remain unverified.

## 2. Model Contract

- Model: LightGBM multiclass classifier.
- Input: exactly 30 numerical features.
- Feature names and order: `../schemas/feature_schema.json`.
- Class mapping: `../schemas/class_mapping.json`.
- Model artifact: `../models/cognifi_multiclass_30_candidate.joblib`.
- Inference interface: `../inference/predictor.py`.
- Six availability flags are diagnostic metadata only; they are not model inputs.

Do not reorder, omit, or rename model input features.

## 3. Supported Classes

The model's class order is:

1. (Re)Assoc
2. Botnet
3. Deauth
4. Disas
5. Evil_Twin
6. Kr00k
7. Krack
8. Normal
9. Malware
10. RogueAP
11. SQL_Injection
12. SSDP
13. SSH
14. Website_spoofing

The mapping file is authoritative. Normal is the non-threat class; other predicted classes are treated as threat classifications by the current integration logic.

## 4. Offline Evaluation

Evaluation on 508 held-out windows:

- Accuracy: 96.26%
- Balanced accuracy: 95.16%
- Macro-F1: 94.50%
- Weighted F1: 96.22%

These are offline evaluation metrics. They do not establish live performance, generalization to unseen environments, or false-positive and false-negative rates on real traffic.

## 5. Prediction and Threat Probability

The candidate is a multiclass model, not a separate binary detector.

- `predicted_class`: selected class.
- `confidence`: probability associated with the predicted class.
- `is_threat`: true when the predicted class is not Normal.
- `normal_probability`: probability assigned to Normal.
- `threat_probability`: sum of probabilities assigned to all non-Normal classes.

A predicted class is a model classification, not proof that an attack occurred. Do not invent a specific threat type from a binary threat flag alone.

## 6. Explainability

`../explainability/explainer.py` implements local SHAP explanations using `shap.TreeExplainer`.

The explainer returns the predicted class, confidence, explanation method, and ranked feature contributions for the predicted class.

A synthetic all-zero input test successfully executed and returned feature contributions. Explanations have not yet been validated against representative real captured traffic. Contributions are in the model output space and must not be described as probability points or proof of malicious activity.

## 7. Project Structure

- `../models/` — candidate model artifact.
- `../schemas/` — ordered feature schema and class mapping.
- `../inference/` — prediction interface.
- `../evaluation/` — metrics, split manifest, and model-contract verification.
- `../explainability/` — SHAP explanation implementation.
- `../tests/` — predictor and ML service tests.
- `../requirements.txt` — ML dependencies.

## 8. Validation and Production Readiness

The current tests cover the model contract, inference outputs, invalid inputs, service behavior, and synthetic capture-to-model integration.

Before claiming production readiness:

1. Validate predictions on representative real captured feature windows.
2. Evaluate false positives, false negatives, and per-class performance.
3. Validate SHAP explanations on representative inputs.
4. Verify end-to-end integration with the actual live capture pipeline.
5. Confirm dependency installation and failure handling in the deployment environment.

The candidate must not be described as fully live-validated until these checks are complete.
