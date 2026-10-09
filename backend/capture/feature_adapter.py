import json
import os
import pandas as pd
import numpy as np

class FeatureAdapter:
    def __init__(self, ml_dir="ml"):
        self.ml_dir = os.path.abspath(ml_dir)
        
        # Load binary schema
        binary_schema_path = os.path.join(self.ml_dir, "schemas", "binary_feature_schema.json")
        with open(binary_schema_path, "r", encoding="utf-8") as f:
            self.binary_schema = json.load(f)
            self.binary_features = self.binary_schema["feature_order"]

        # Load multiclass schema
        multiclass_schema_path = os.path.join(self.ml_dir, "schemas", "multiclass_feature_schema.json")
        with open(multiclass_schema_path, "r", encoding="utf-8") as f:
            self.multiclass_schema = json.load(f)
            # Schema might use 'feature_order' or 'features'
            self.multiclass_features = self.multiclass_schema.get("feature_order", self.multiclass_schema.get("features", []))

    def _map_features(self, base_features_dict, target_feature_list):
        """
        Maps 30 base capture features to the target ML feature list.
        Handles direct matches, derived calculations, and safe zero/NaN fallbacks
        for unavailable deep packet inspection fields.
        """
        mapped_row = {}
        for feat in target_feature_list:
            if feat in base_features_dict:
                # Direct match available from capture engine
                mapped_row[feat] = base_features_dict[feat]
            else:
                # Derive common temporal/statistical metrics or fallback safely
                if "mean" in feat:
                    mapped_row[feat] = base_features_dict.get("packet_count", 0.0)
                elif "std" in feat:
                    mapped_row[feat] = 0.0
                elif "count" in feat:
                    mapped_row[feat] = base_features_dict.get("packet_count", 0.0)
                elif "present" in feat or "active" in feat:
                    mapped_row[feat] = 1.0 if base_features_dict.get("packet_count", 0) > 0 else 0.0
                else:
                    # Default safe fallback for unmapped fields (letting predictor apply medians/zeros)
                    mapped_row[feat] = np.nan
                    
        return pd.DataFrame([mapped_row], columns=target_feature_list)

    def adapt_for_binary(self, base_features_dict):
        """Produces the exact 82-feature dataframe for binary prediction."""
        return self._map_features(base_features_dict, self.binary_features)

    def adapt_for_multiclass(self, base_features_dict):
        """Produces the exact 81-feature dataframe for multiclass prediction."""
        return self._map_features(base_features_dict, self.multiclass_features)