
import json
import os
import numpy as np
from ml.predictor import CognifiPredictor

base_dir = os.path.abspath("ml")

with open("ml/samples/sample_input_81_features.json", encoding="utf-8") as f:
    sample = json.load(f)

predictor = CognifiPredictor(base_dir)
model = predictor.multiclass

missing_fields = [
    "radiotap.channel.flags.ofdm",
    "radiotap.channel.freq",
    "radiotap.datarate",
    "radiotap.length",
    "radiotap.mactime",
    "radiotap.timestamp.ts",
    "wlan.duration",
    "wlan.fc.protected",
    "wlan.fc.type",
    "wlan.fc.retry",
    "wlan.fc.subtype",
    "wlan.fixed.reason_code",
    "wlan_radio.duration",
    "wlan.seq",
    "wlan_radio.data_rate",
    "wlan_radio.signal_dbm",
    "wlan_radio.phy",
]


tests = [
    ("Original sample", dict(sample)),
    (
        "Signal missing",
        {**sample, "wlan_radio.signal_dbm": np.nan},
    ),
    (
        "Channel frequency missing",
        {**sample, "radiotap.channel.freq": np.nan},
    ),
    (
        "Retry field missing",
        {**sample, "wlan.fc.retry": np.nan},
    ),
]

for label, row in tests:
    try:
        result = model.predict(row)
        print(f"\n{label}: SUCCESS")
        print(result)
    except Exception as exc:
        print(f"\n{label}: FAILED")
        print(f"{type(exc).__name__}: {exc}")
