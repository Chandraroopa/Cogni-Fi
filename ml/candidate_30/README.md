
# Cognifi — 30-Feature Multiclass ML Candidate

## 1. Purpose

This folder contains the candidate machine-learning model for Cognifi's Wi-Fi trust and risk classification system.

The model classifies a feature window into one of 14 classes: Normal or one of 13 threat classes.

**Status:** Offline evaluation completed; live integration not yet verified.

## 2. Model Contract

- Input: exactly 30 numerical features.
- Feature names and order: defined in `feature_schema.json`.
- Model: LightGBM multiclass classifier.
- Output: predicted class and probabilities for all 14 classes.
- Class order: defined in `class_mapping.json`.
- The six availability flags are diagnostic information only and are not model inputs.

Do not reorder, omit, or rename input features.

## 3. Classes

The model supports:

1. (Re)Assoc
2. Botnet
3. Deauth
4. Disas
5. Evil_Twin
6. Kr00k
7. Krack
8. Malware
9. Normal
10. RogueAP
11. SQL_Injection
12. SSDP
13. SSH
14. Website_spoofing

Use `class_mapping.json` as the authoritative class mapping.

## 4. Offline Evaluation

Evaluation on 508 held-out windows:

- Accuracy: 96.26%
- Balanced accuracy: 95.16%
- Macro-F1: 94.50%
- Weighted F1: 96.22%

These are offline evaluation results, not proof of live performance.

## 5. Threat Probability

There is no separate binary detector in this candidate.

- `is_threat` is true when the predicted class is not `Normal`.
- `normal_probability` is the model probability for `Normal`.
- `threat_probability` is the sum of the probabilities for all non-Normal classes.

Do not infer a specific threat type from `is_threat` alone.

## 6. Explainability

Local SHAP-based explanations are planned but have not yet been implemented and validated.

When implemented, explanations should identify features contributing toward or away from the predicted class. Feature contributions must not be presented as proof that an attack occurred.

## 7. Files

- `cognifi_multiclass_30_candidate.joblib` — candidate model.
- `feature_schema.json` — ordered input features and diagnostic flags.
- `class_mapping.json` — class mapping.
- `evaluation_metrics.json` — offline evaluation summary.
- `split_manifest.json` — split and feature-reconstruction information.
- `predictor_30.py` — candidate inference interface.

## 8. Integration Requirements

Before production integration:

1. Install compatible dependencies.
2. Validate the predictor's input and output contract.
3. Test with actual feature windows from the live capture pipeline.
4. Verify probability outputs and class mapping.
5. Implement and validate local explanations.
6. Test failure handling for missing, invalid, or non-finite feature values.

Do not mark this candidate as production-ready until live integration tests pass.
