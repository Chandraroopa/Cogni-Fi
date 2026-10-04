# CogniFi Feature Extraction Contract

## Purpose

This document defines the contract between:

1. Live Wi-Fi packet capture
2. Feature extraction
3. CogniFi ML inference

The ML models must receive engineered feature vectors that follow the
frozen production schemas.

Raw packet data must NOT be passed directly to the ML models.

---

# 1. Production ML Pipeline

The intended production flow is:

Wi-Fi packets
    ↓
Packet capture
    ↓
Raw packet fields
    ↓
Feature extraction
    ↓
1-second causal windows
    ↓
Base feature aggregation
    ↓
Behavioral features
    ↓
Delta features
    ↓
Causal rolling features
    ↓
Final ML feature vector
    ↓
Feature contract validation
    ↓
Binary threat detection
    ↓
If threat → multiclass classification
    ↓
ML evidence for Trust & Risk Engine

---

# 2. Windowing Contract

The production feature extraction process uses 1-second windows.

For a packet timestamp:

    timestamp

the window identifier is calculated relative to the beginning of the
capture sequence:

    window_id = floor((timestamp - start_timestamp) / 1.0)

where:

    start_timestamp = minimum timestamp in the processed sequence

The feature extractor must preserve chronological ordering.

Windows must be processed in chronological order.

---

# 3. Causal Requirement

Feature generation must be causal.

A feature for window t may use:

    t
    t-1
    t-2

when the corresponding feature definition requires temporal context.

A feature for window t must NOT use:

    t+1
    t+2
    any future window

This is required to prevent future-information leakage during live
inference.

The production implementation must therefore calculate temporal
features using only information available up to the current window.

---

# 4. Base Features

Raw packet fields are first converted into aggregated window-level
features.

Examples of feature families include:

- packet counts
- byte counts
- packet-size statistics
- inter-arrival-time statistics
- retry/protection rates
- management/control/data frame rates
- probe request/response rates
- beacon rates
- authentication/association rates
- deauthentication/disassociation rates
- RTS/CTS/ACK rates
- signal statistics
- data-rate statistics
- unique BSSID/source/destination counts
- DNS request/response statistics
- DNS latency statistics
- protocol-presence indicators
- TCP/UDP behavior
- ARP behavior
- WLAN sequence behavior
- timing behavior

The exact production feature set is defined by the frozen model schemas.

Do not manually reorder, rename, add, or remove production features.

---

# 5. Behavioral Features

CogniFi uses behavioral features in addition to simple packet
statistics.

Examples include temporal and sequence behavior such as:

- WLAN sequence deltas
- TCP sequence deltas
- TCP acknowledgement deltas
- inter-arrival-time behavior
- protocol/time aggregates
- packet timing behavior

Behavioral features must be calculated consistently between training
and live inference.

---

# 6. Delta Features

Temporal delta features compare the current window with the preceding
window.

Conceptually:

    delta_feature(t) =
        feature(t) - feature(t-1)

For the first available window, the training implementation uses a
zero-filled delta where no previous window exists.

Delta features must be generated in chronological order.

Future windows must never participate in delta calculation.

---

# 7. Rolling Features

Some production features use causal rolling statistics.

The rolling context uses the current window and preceding windows.

For a 3-window causal context:

    [t-2, t-1, t]

may be used.

The following must NEVER be used:

    [t-1, t, t+1]

because t+1 is future information relative to window t.

Rolling means and rolling standard deviations must therefore be
causal.

---

# 8. Binary Model Contract

The binary model is the first ML stage.

It consumes exactly:

    82 features

The feature order is frozen in:

    ml/schemas/binary_feature_schema.json

The binary model must receive exactly those features in exactly that
schema order.

Binary target mapping:

    0 = Normal
    1 = Threat

Binary decision threshold:

    attack_probability >= 0.09 → Threat
    attack_probability <  0.09 → Normal

The threshold is frozen and must not be changed by the integration
layer.

The threshold is defined in:

    ml/config/binary_threshold.json

---

# 9. Multiclass Model Contract

The multiclass model is used after binary detection identifies a
threat.

It consumes exactly:

    81 features

The feature order is frozen in:

    ml/schemas/multiclass_feature_schema.json

The multiclass taxonomy is:

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

The authoritative mapping is:

    ml/schemas/multiclass_label_mapping.json

---

# 10. Feature Order Is Mandatory

Feature names and feature order are part of the ML model contract.

Do NOT:

- alphabetically sort features
- create a new feature ordering
- remove unused-looking features
- rename features
- insert new features into the production vector
- assume model column order from a dataframe
- manually recreate the schema from memory

The inference code loads the frozen schemas.

The feature extraction layer must produce the required named
features, after which the ML inference layer places them into the
correct model order.

---

# 11. Missing Values

The binary model has a frozen training-median preprocessing artifact.

Binary preprocessing is:

    numeric conversion
        ↓
    +inf/-inf → NaN
        ↓
    training medians
        ↓
    remaining NaN → 0
        ↓
    float32
        ↓
    model

The live feature extractor should therefore produce valid numeric
values wherever possible.

It must not invent arbitrary replacement values.

The model's packaged preprocessing artifact is:

    ml/preprocessing/binary_train_medians.joblib

---

# 12. Feature Contract Validation

Before model inference, feature payloads must pass the strict
feature-contract validator.

Binary:

    82 required features

Multiclass:

    81 required features

Invalid conditions include:

- missing features
- unexpected features
- incorrect feature count
- non-numeric values
- NaN
- positive infinity
- negative infinity

Invalid payloads must not silently proceed to inference.

---

# 13. Raw TShark Data Is Not an ML Input

The following is NOT a valid ML input:

    raw TShark JSON packet
    raw Scapy packet
    raw packet dictionary
    individual packet fields

These are intermediate capture data.

They must first pass through the feature extraction pipeline.

Correct:

    packets
      ↓
    feature extraction
      ↓
    engineered window
      ↓
    schema validation
      ↓
    ML

Incorrect:

    packet
      ↓
    ML model

---

# 14. Binary → Multiclass Flow

Production inference is:

    engineered feature window
            ↓
       Binary model
            ↓
       Normal / Threat
            │
            ├── Normal
            │     ↓
            │   stop ML classification
            │
            └── Threat
                  ↓
            Multiclass model
                  ↓
            Attack class + probabilities

The binary model determines whether the window is considered a threat.

The multiclass model determines the class when the binary stage
identifies a threat.

---

# 15. ML Does Not Own the Final Risk Score

The ML layer provides model evidence.

It does NOT directly own the final:

    Risk Score 0–100

The intended architecture is:

    ML prediction/probabilities
            ↓
       Trust & Risk Engine
            ↓
       Risk Score 0–100
            ↓
          Explanation
            ↓
         Dashboard

The Trust & Risk Engine is responsible for combining ML evidence with
the project's other trust/risk signals.

---

# 16. Attack Type

The multiclass model may provide a predicted class from the frozen
14-class taxonomy.

The binary model alone does NOT provide a genuine attack type.

Therefore:

    is_threat = true

must NOT be converted into an arbitrary hard-coded attack type.

If multiclass inference is unavailable, the attack type must remain
unknown/null rather than being fabricated.

---

# 17. Training/Inference Consistency

The most important requirement is:

    training feature semantics
        =
    live feature semantics

The live extractor must reproduce the meaning of the features used
during training.

Changing the meaning of a feature while keeping its name is not
compatible with the frozen model.

Examples of incompatible changes include:

- changing the window duration
- changing aggregation semantics
- changing delta definitions
- using future windows
- changing missing-value semantics
- changing categorical encoding
- changing feature units
- silently replacing a behavioral feature with a different statistic

If a feature definition must change, the model must be treated as a
new model and retrained/validated.

---

# 18. Ownership Boundary

### Packet Capture / Feature Extraction Owner

Responsible for:

- live packet capture
- packet parsing
- 1-second window construction
- feature extraction
- behavioral feature generation
- delta generation
- causal rolling features
- producing the frozen feature vectors

### ML Owner

Responsible for:

- trained models
- model schemas
- preprocessing artifacts
- threshold
- label mapping
- inference code
- validation
- ML service
- ML integration contract

### Trust & Risk Owner

Responsible for:

- combining ML evidence
- trust/risk calculation
- final risk score
- risk explanation
- alerts

### Backend / Integration Owner

Responsible for:

- APIs
- WebSocket integration
- database
- routing
- frontend integration
- deployment

---

# 19. Frozen Production Artifacts

The ML package contains the authoritative production artifacts:

    ml/models/binary_model.joblib
    ml/models/multiclass_model.joblib

    ml/schemas/binary_feature_schema.json
    ml/schemas/multiclass_feature_schema.json
    ml/schemas/multiclass_label_mapping.json
    ml/schemas/model_output_schema.json

    ml/config/binary_threshold.json
    ml/preprocessing/binary_train_medians.joblib

    ml/predictor.py

These artifacts must be treated as versioned production assets.

Do not replace them casually.

---

# 20. Final Rule

The live pipeline must produce the same feature semantics expected by
the frozen schemas.

The ML model is NOT responsible for converting raw packets into
features.

The feature extractor is NOT responsible for changing the ML model.

The Trust & Risk Engine is NOT responsible for inventing ML
predictions.

Each layer must respect its contract.
