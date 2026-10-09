import os
import json
import joblib
import numpy as np
import pandas as pd


class CognifiBinaryPredictor:

    def __init__(
        self,
        model_path,
        schema_path,
        medians_path,
        threshold_path
    ):

        self.model = joblib.load(model_path)

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        with open(threshold_path, "r", encoding="utf-8") as f:
            threshold_config = json.load(f)

        self.features = schema["feature_order"]

        self.threshold = float(
            threshold_config["threshold"]
        )

        self.medians = joblib.load(
            medians_path
        )

    def _prepare_input(self, X):

        if isinstance(X, dict):
            X = pd.DataFrame([X])

        elif isinstance(X, pd.Series):
            X = X.to_frame().T

        elif not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)

        X = X[self.features].copy()

        for col in self.features:
            X[col] = pd.to_numeric(
                X[col],
                errors="coerce"
            )

        X = X.replace(
            [np.inf, -np.inf],
            np.nan
        )

        X = X.fillna(
            self.medians
        )

        X = X.fillna(0)

        return X.astype(np.float32)

    def predict(self, X):

        Xp = self._prepare_input(X)

        probabilities = self.model.predict_proba(Xp)

        attack_probability = float(
            probabilities[:, 1][0]
        )

        normal_probability = float(
            probabilities[:, 0][0]
        )

        is_threat = (
            attack_probability >= self.threshold
        )

        confidence = (
            attack_probability
            if is_threat
            else normal_probability
        )

        return {
            "is_threat": bool(is_threat),
            "attack_probability": attack_probability,
            "normal_probability": normal_probability,
            "confidence": confidence,
            "threshold": self.threshold
        }


class CognifiMulticlassPredictor:

    def __init__(
        self,
        model_path,
        schema_path,
        label_mapping_path
    ):

        self.model = joblib.load(model_path)

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        with open(
            label_mapping_path,
            "r",
            encoding="utf-8"
        ) as f:
            labels = json.load(f)

        if "feature_order" in schema:
            self.features = schema["feature_order"]
        elif "features" in schema:
            self.features = schema["features"]
        else:
            raise KeyError(
                "Multiclass schema must contain "
                "'feature_order' or 'features'."
            )

        self.classes = labels["classes"]

    def _prepare_input(self, X):

        if isinstance(X, dict):
            X = pd.DataFrame([X])

        elif isinstance(X, pd.Series):
            X = X.to_frame().T

        elif not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)

        X = X[self.features].copy()

        for col in self.features:
            X[col] = pd.to_numeric(
                X[col],
                errors="coerce"
            )

        X = X.replace(
            [np.inf, -np.inf],
            np.nan
        )

        return X

    def predict(self, X):

        Xp = self._prepare_input(X)

        probabilities = self.model.predict_proba(Xp)

        probability_row = probabilities[0]

        class_id = int(
            np.argmax(probability_row)
        )

        confidence = float(
            probability_row[class_id]
        )

        predicted_class = self.classes[class_id]

        class_probabilities = {
            self.classes[i]: float(probability_row[i])
            for i in range(len(self.classes))
        }

        return {
            "predicted_class": predicted_class,
            "class_id": class_id,
            "confidence": confidence,
            "class_probabilities": class_probabilities
        }


class CognifiPredictor:

    def __init__(self, base_dir):

        ml_dir = os.path.abspath(base_dir)

        self.binary = CognifiBinaryPredictor(
            model_path=os.path.join(
                ml_dir,
                "models",
                "binary_model.joblib"
            ),
            schema_path=os.path.join(
                ml_dir,
                "schemas",
                "binary_feature_schema.json"
            ),
            medians_path=os.path.join(
                ml_dir,
                "preprocessing",
                "binary_train_medians.joblib"
            ),
            threshold_path=os.path.join(
                ml_dir,
                "config",
                "binary_threshold.json"
            )
        )

        self.multiclass = CognifiMulticlassPredictor(
            model_path=os.path.join(
                ml_dir,
                "models",
                "multiclass_model.joblib"
            ),
            schema_path=os.path.join(
                ml_dir,
                "schemas",
                "multiclass_feature_schema.json"
            ),
            label_mapping_path=os.path.join(
                ml_dir,
                "schemas",
                "multiclass_label_mapping.json"
            )
        )

    def predict_binary(self, X):

        return self.binary.predict(X)

    def predict_multiclass(self, X):

        return self.multiclass.predict(X)


if __name__ == "__main__":

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    predictor = CognifiPredictor(BASE_DIR)

    print("CogniFi predictor loaded successfully.")
    print(
        "Binary features:",
        len(predictor.binary.features)
    )
    print(
        "Multiclass features:",
        len(predictor.multiclass.features)
    )
