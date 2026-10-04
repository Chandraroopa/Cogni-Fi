# CogniFi ML Integration Guide

## Purpose

This document explains how the CogniFi backend/integration layer uses
the finalized ML package.

The ML package provides:

1. Binary threat detection
2. Multiclass attack classification
3. Frozen feature schemas
4. Frozen preprocessing artifacts
5. Frozen binary decision threshold
6. Label mapping
7. Strict feature validation

The ML package does NOT calculate the final Trust/Risk score.

---

# 1. ML Package Location

The production ML package is:

    ml/

Important files:

    ml/predictor.py

    ml/models/binary_model.joblib
    ml/models/multiclass_model.joblib

    ml/schemas/binary_feature_schema.json
    ml/schemas/multiclass_feature_schema.json
    ml/schemas/multiclass_label_mapping.json
    ml/schemas/model_output_schema.json

    ml/config/binary_threshold.json
    ml/preprocessing/binary_train_medians.joblib

---

# 2. Backend ML Service

The backend adapter is:

    backend/ml_service.py

It provides a clean interface around the production predictor.

The integration layer should use:

    CognifiMLService

rather than directly loading joblib model files.

Example:

    from backend.ml_service import CognifiMLService

    service = CognifiMLService()

---

# 3. Binary Prediction

Binary inference requires exactly 82 features.

Example:

    binary_result = service.predict_binary(feature_payload)

The result contains:

    {
        "is_threat": true/false,
        "attack_probability": 0.0-1.0,
        "normal_probability": 0.0-1.0,
        "confidence": 0.0-1.0,
        "threshold": 0.09
    }

Interpretation:

    attack_probability >= 0.09
        → Threat

    attack_probability < 0.09
        → Normal

The threshold is frozen and must not be changed in the backend.

---

# 4. Multiclass Prediction

Multiclass inference requires exactly 81 features.

Example:

    multiclass_result = service.predict_multiclass(feature_payload)

The result contains:

    {
        "predicted_class": "...",
        "class_id": integer,
        "confidence": 0.0-1.0,
        "class_probabilities": {...}
    }

The authoritative classes are:

    0  Normal
    1  (Re)Assoc
    2  Botnet
    3  Deauth
    4  Disas
    5  Evil_Twin
    6  Kr00k
    7  Krack
    8  Malware
    9  RogueAP
    10 SQL_Injection
    11 SSDP
    12 SSH
    13 Website_spoofing

Use:

    ml/schemas/multiclass_label_mapping.json

as the authoritative mapping.

---

# 5. Recommended Production Flow

The normal integration flow is:

    Feature extraction
          ↓
    Validate binary features
          ↓
    Binary prediction
          ↓
    Is threat?
       /       \
     No         Yes
     ↓           ↓
    Stop    Multiclass prediction
                ↓
          Trust/Risk Engine
                ↓
           Risk score
                ↓
            Frontend

The multiclass model should normally be used when the binary stage
identifies a threat.

---

# 6. Feature Validation

Before inference, validate the feature payload.

Use:

    from backend.ml_feature_contract import MLFeatureContract

    contract = MLFeatureContract()

Binary:

    result = contract.validate_binary(feature_payload)

Multiclass:

    result = contract.validate_multiclass(feature_payload)

A valid payload must have:

- all required features
- no unexpected features
- exactly the expected number of features
- numeric values
- finite values

Invalid payloads must not silently proceed.

---

# 7. Feature Source

The ML service does NOT convert raw packets into the production
feature vectors.

The upstream feature-extraction layer is responsible for producing
the engineered feature vector.

Raw:

    TShark JSON
    Scapy packet
    raw packet dictionary

is NOT a valid direct ML input.

The feature-extraction layer must follow:

    ml/docs/FEATURE_EXTRACTION_CONTRACT.md

---

# 8. Binary vs Multiclass Feature Sets

The two models have different production feature contracts.

Binary:

    82 features

Multiclass:

    81 features

Do not assume they are interchangeable.

Do not pass the 82-feature binary vector directly to the multiclass
model.

Do not pass the 81-feature multiclass vector directly to the binary
model.

Use the corresponding frozen schema for each model.

---

# 9. Feature Ordering

Feature names and ordering are part of the model contract.

Do not:

- alphabetically sort features
- manually reorder columns
- remove features because they appear unimportant
- add new features
- rename features
- construct feature lists from memory

The frozen schemas are authoritative.

---

# 10. Binary Preprocessing

Binary inference uses the frozen training preprocessing artifact.

Conceptually:

    numeric conversion
          ↓
    infinity → NaN
          ↓
    training medians
          ↓
    remaining missing values → 0
          ↓
    float32
          ↓
    binary model

The training medians are stored in:

    ml/preprocessing/binary_train_medians.joblib

Do not substitute arbitrary production medians.

---

# 11. ML Output Is Evidence

The ML layer produces evidence for the Trust/Risk Engine.

It does NOT directly decide the final 0-100 risk score.

For example, the Trust/Risk Engine may consume:

    is_threat
    attack_probability
    normal_probability
    confidence
    predicted_class
    class_probabilities

The final risk calculation belongs to the Trust/Risk Engine.

---

# 12. Attack Type Rule

The binary detector only answers:

    Normal / Threat

It does not determine a genuine attack type.

Therefore:

    is_threat = true

must NOT be converted into a hard-coded attack type.

The multiclass model is responsible for attack-class prediction.

If multiclass classification is unavailable, the attack type should
remain unknown/null rather than being fabricated.

---

# 13. Do Not Modify Frozen ML Configuration

The following are production ML contracts:

    Binary feature schema
    Multiclass feature schema
    Multiclass label mapping
    Binary threshold
    Binary training medians
    Model artifacts

Do not change these during backend integration.

A change to the feature semantics or production model requires a new
training/validation cycle.

---

# 14. Smoke Test

The repository contains:

    backend/test_ml_service.py

Run it from the repository root:

    python -m backend.test_ml_service

The test verifies:

- binary schema loading
- multiclass schema loading
- binary threshold
- class mapping
- feature validation
- binary inference
- multiclass inference
- invalid-feature rejection
- NaN rejection
- infinity rejection

A successful run ends with:

    ALL ML HANDOFF SMOKE TESTS PASSED

---

# 15. Ownership

ML owns:

- trained models
- schemas
- preprocessing artifacts
- threshold
- label mapping
- inference code
- feature contract
- ML validation
- ML service

Packet capture / feature extraction owns:

- packet capture
- raw packet parsing
- windowing
- feature generation
- behavioral features
- delta features
- rolling features

Trust/Risk owns:

- risk calculation
- final 0-100 score
- risk explanation
- alerts

Backend/frontend integration owns:

- API
- WebSocket
- database
- UI integration
- deployment

---

# 16. Final Architecture

    Wi-Fi
      ↓
    Packet Capture
      ↓
    Feature Extraction
      ↓
    1-second Engineered Window
      ↓
    Feature Contract Validation
      ↓
    Binary ML
      ↓
    Normal / Threat
      ↓
    Multiclass ML (Threat)
      ↓
    ML Evidence
      ↓
    Trust & Risk Engine
      ↓
    Risk Score 0-100
      ↓
    Explanation
      ↓
    Dashboard

The ML package is an inference component inside this pipeline.

It is not the packet-capture system and it is not the Trust/Risk
Engine.
