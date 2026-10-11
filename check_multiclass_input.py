import os
import numpy as np

from ml.predictor import CognifiPredictor

predictor = CognifiPredictor(base_dir=os.path.abspath("ml"))

# Use the existing saved sample as a baseline.
sample_path = "ml/samples/sample_input_81_features.json"

import json
with open(sample_path, "r", encoding="utf-8") as f:
    sample = json.load(f)

features = predictor.multiclass.features

def report(label, values):
    missing = [
        name for name in features
        if name not in values or values[name] is None
    ]
    non_numeric = []
    for name in features:
        value = values.get(name)
        if value is not None:
            try:
                number = float(value)
                if not np.isfinite(number):
                    non_numeric.append(name)
            except (TypeError, ValueError):
                non_numeric.append(name)

    print(f"\n{label}")
    print(f"Expected features: {len(features)}")
    print(f"Missing/None: {len(missing)}")
    print(f"Non-numeric or non-finite: {len(non_numeric)}")
    print("Missing names:", missing)
    print("Invalid names:", non_numeric)

report("Saved sample baseline", sample)

# Simulate the wireless fields unavailable on your adapter.
simulated = dict(sample)
wireless_fields = [
    name for name in features
    if name.startswith(("radiotap.", "wlan.", "wlan_radio."))
]

for name in wireless_fields:
    simulated[name] = None

report("Sample with Wi-Fi fields unavailable", simulated)
