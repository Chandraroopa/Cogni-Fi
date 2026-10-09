"""
Cogni-Fi Feature Vector Builder

Builds and validates the exact frozen ML feature vectors.

Binary schema:
    ml/schemas/binary_feature_schema.json
    key: feature_order
    count: 82

Multiclass schema:
    ml/schemas/multiclass_feature_schema.json
    key: features
    count: 81

IMPORTANT:
- Feature order is frozen.
- No alphabetical sorting.
- No feature fabrication.
- Missing features are rejected during vector construction.
- Invalid values are rejected.
- Missing-value imputation belongs to ML preprocessing, not this builder.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, Mapping, Optional


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

BINARY_SCHEMA_PATH = (
    PROJECT_ROOT
    / "ml"
    / "schemas"
    / "binary_feature_schema.json"
)

MULTICLASS_SCHEMA_PATH = (
    PROJECT_ROOT
    / "ml"
    / "schemas"
    / "multiclass_feature_schema.json"
)


# ============================================================
# SCHEMA LOADING
# ============================================================

def _load_json(path: Path) -> dict:
    """Load and validate a JSON schema object."""

    if not path.exists():
        raise FileNotFoundError(
            f"Schema file not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            f"Schema must be a JSON object: {path}"
        )

    return data


def _load_feature_list(
    path: Path,
    key: str,
) -> list[str]:
    """
    Load the frozen feature list from a schema.

    Binary:
        key = feature_order

    Multiclass:
        key = features
    """

    schema = _load_json(path)

    features = schema.get(key)

    if not isinstance(features, list):
        raise ValueError(
            f"'{key}' not found in schema: {path}"
        )

    if not features:
        raise ValueError(
            f"'{key}' is empty in schema: {path}"
        )

    # Every feature name must be a string.
    for feature in features:

        if not isinstance(feature, str):
            raise ValueError(
                "Invalid feature name in "
                f"{path}: {feature!r}"
            )

    # Frozen schema must not contain duplicates.
    if len(features) != len(set(features)):

        raise ValueError(
            f"Duplicate feature names found: {path}"
        )

    # Verify declared feature count.
    declared_count = schema.get(
        "feature_count"
    )

    if declared_count is not None:

        if declared_count != len(features):

            raise ValueError(
                f"Schema declares "
                f"{declared_count} features, "
                f"but contains "
                f"{len(features)}: {path}"
            )

    return list(features)


# ============================================================
# FROZEN FEATURES
# ============================================================

BINARY_FEATURES = _load_feature_list(
    BINARY_SCHEMA_PATH,
    "feature_order",
)

MULTICLASS_FEATURES = _load_feature_list(
    MULTICLASS_SCHEMA_PATH,
    "features",
)


# ============================================================
# VALUE VALIDATION
# ============================================================

def _is_valid_value(
    value: Any,
) -> bool:
    """
    Return True only for finite numeric values.

    Valid:
        0
        1
        -1
        12.5

    Invalid:
        None
        bool
        strings
        NaN
        +inf
        -inf
    """

    if value is None:
        return False

    # bool is a subclass of int in Python.
    if isinstance(value, bool):
        return False

    if not isinstance(
        value,
        (int, float),
    ):
        return False

    try:

        return math.isfinite(
            float(value)
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):

        return False


def _to_float(
    value: Any,
) -> float:
    """Convert a valid feature value to float."""

    if not _is_valid_value(value):

        raise ValueError(
            f"Invalid feature value: {value!r}"
        )

    return float(value)


# ============================================================
# DIAGNOSTICS
# ============================================================

def _diagnose(
    features: Mapping[str, Any],
    expected_features: list[str],
) -> Dict[str, Any]:
    """
    Diagnose a feature dictionary.

    The returned keys intentionally match the existing
    test_feature_vector_builder.py API.
    """

    if not isinstance(
        features,
        Mapping,
    ):

        raise TypeError(
            "features must be a mapping"
        )

    missing = []
    invalid = []
    available = []

    expected_set = set(
        expected_features
    )

    for feature in expected_features:

        if feature not in features:

            missing.append(feature)
            continue

        value = features[feature]

        if _is_valid_value(value):

            available.append(feature)

        else:

            invalid.append(feature)

    unexpected = sorted(
        set(features.keys())
        - expected_set
    )

    return {
        # Existing test API
        "expected_count": len(
            expected_features
        ),

        "available_count": len(
            available
        ),

        "missing_count": len(
            missing
        ),

        "invalid_count": len(
            invalid
        ),

        "missing": missing,

        "invalid": invalid,

        "available": available,

        "unexpected": unexpected,

        # Additional useful diagnostic information
        "unexpected_count": len(
            unexpected
        ),

        "expected_features": list(
            expected_features
        ),

        "available_features": available,

        "missing_features": missing,

        "invalid_features": invalid,

        "unexpected_features": unexpected,
    }


# ============================================================
# FEATURE VECTOR BUILDER
# ============================================================

class FeatureVectorBuilder:
    """
    Build ML vectors using the frozen Cogni-Fi schemas.
    """

    def __init__(
        self,
        binary_schema_path: Optional[Path] = None,
        multiclass_schema_path: Optional[Path] = None,
    ):

        self.binary_schema_path = (
            Path(binary_schema_path)
            if binary_schema_path is not None
            else BINARY_SCHEMA_PATH
        )

        self.multiclass_schema_path = (
            Path(multiclass_schema_path)
            if multiclass_schema_path is not None
            else MULTICLASS_SCHEMA_PATH
        )

        self.binary_features = (
            _load_feature_list(
                self.binary_schema_path,
                "feature_order",
            )
        )

        self.multiclass_features = (
            _load_feature_list(
                self.multiclass_schema_path,
                "features",
            )
        )

    # ========================================================
    # REQUIRED COUNT METHODS
    # ========================================================

    def binary_feature_count(
        self,
    ) -> int:

        return len(
            self.binary_features
        )

    def multiclass_feature_count(
        self,
    ) -> int:

        return len(
            self.multiclass_features
        )

    # ========================================================
    # DIAGNOSTIC METHODS
    # ========================================================

    def diagnose_binary(
        self,
        features: Mapping[str, Any],
    ) -> Dict[str, Any]:

        return _diagnose(
            features,
            self.binary_features,
        )

    def diagnose_multiclass(
        self,
        features: Mapping[str, Any],
    ) -> Dict[str, Any]:

        return _diagnose(
            features,
            self.multiclass_features,
        )

    # ========================================================
    # STRICT VALIDATION
    # ========================================================

    @staticmethod
    def _validate_mapping(
        features: Mapping[str, Any],
        expected_features: list[str],
    ) -> None:

        diagnostic = _diagnose(
            features,
            expected_features,
        )

        errors = []

        if diagnostic[
            "missing_count"
        ]:

            errors.append(
                "missing features: "
                + ", ".join(
                    diagnostic["missing"]
                )
            )

        if diagnostic[
            "invalid_count"
        ]:

            errors.append(
                "invalid features: "
                + ", ".join(
                    diagnostic["invalid"]
                )
            )

        if diagnostic[
            "unexpected_count"
        ]:

            errors.append(
                "unexpected features: "
                + ", ".join(
                    diagnostic["unexpected"]
                )
            )

        if errors:

            raise ValueError(
                "Feature vector validation "
                "failed: "
                + "; ".join(errors)
            )

    # ========================================================
    # GENERIC VECTOR BUILD
    # ========================================================

    @staticmethod
    def _build(
        features: Mapping[str, Any],
        expected_features: list[str],
    ) -> list[float]:

        FeatureVectorBuilder._validate_mapping(
            features,
            expected_features,
        )

        vector = []

        # CRITICAL:
        # Preserve the exact frozen feature order.
        #
        # DO NOT:
        #   sorted(...)
        #   alphabetical ordering
        #   dictionary ordering
        #
        # The schema is authoritative.
        for feature in expected_features:

            vector.append(
                _to_float(
                    features[feature]
                )
            )

        return vector

    # ========================================================
    # BINARY VECTOR
    # ========================================================

    def build_binary(
        self,
        features: Mapping[str, Any],
    ) -> list[float]:

        vector = self._build(
            features,
            self.binary_features,
        )

        if len(vector) != 82:

            raise RuntimeError(
                "Binary vector size mismatch: "
                f"{len(vector)} != 82"
            )

        return vector

    # ========================================================
    # MULTICLASS VECTOR
    # ========================================================

    def build_multiclass(
        self,
        features: Mapping[str, Any],
    ) -> list[float]:

        vector = self._build(
            features,
            self.multiclass_features,
        )

        if len(vector) != 81:

            raise RuntimeError(
                "Multiclass vector size mismatch: "
                f"{len(vector)} != 81"
            )

        return vector

    # ========================================================
    # GENERIC BUILD
    # ========================================================

    def build(
        self,
        features: Mapping[str, Any],
        model_type: str,
    ) -> list[float]:

        model_type = (
            model_type
            .strip()
            .lower()
        )

        if model_type == "binary":

            return self.build_binary(
                features
            )

        if model_type in (
            "multiclass",
            "multi_class",
        ):

            return self.build_multiclass(
                features
            )

        raise ValueError(
            "model_type must be "
            "'binary' or 'multiclass'"
        )

    # ========================================================
    # VALIDATE BINARY
    # ========================================================

    def validate_binary(
        self,
        features: Mapping[str, Any],
    ) -> bool:

        self._validate_mapping(
            features,
            self.binary_features,
        )

        return True

    # ========================================================
    # VALIDATE MULTICLASS
    # ========================================================

    def validate_multiclass(
        self,
        features: Mapping[str, Any],
    ) -> bool:

        self._validate_mapping(
            features,
            self.multiclass_features,
        )

        return True


# ============================================================
# MODULE-LEVEL HELPERS
# ============================================================

def build_binary_vector(
    features: Mapping[str, Any],
) -> list[float]:

    return FeatureVectorBuilder().build_binary(
        features
    )


def build_multiclass_vector(
    features: Mapping[str, Any],
) -> list[float]:

    return FeatureVectorBuilder().build_multiclass(
        features
    )


def validate_binary(
    features: Mapping[str, Any],
) -> bool:

    return FeatureVectorBuilder().validate_binary(
        features
    )


def validate_multiclass(
    features: Mapping[str, Any],
) -> bool:

    return FeatureVectorBuilder().validate_multiclass(
        features
    )


# ============================================================
# SELF TEST
# ============================================================

def _self_test() -> None:

    print("=" * 60)
    print("FEATURE VECTOR BUILDER SELF TEST")
    print("=" * 60)

    builder = FeatureVectorBuilder()

    print(
        "Binary feature count:",
        builder.binary_feature_count(),
    )

    print(
        "Multiclass feature count:",
        builder.multiclass_feature_count(),
    )

    assert (
        builder.binary_feature_count()
        == 82
    )

    assert (
        builder.multiclass_feature_count()
        == 81
    )

    print(
        "\n[PASS] Frozen schema sizes correct."
    )

    # --------------------------------------------------------
    # Complete binary vector
    # --------------------------------------------------------

    binary_features = {
        feature: 1.0
        for feature
        in builder.binary_features
    }

    binary_vector = (
        builder.build_binary(
            binary_features
        )
    )

    assert len(binary_vector) == 82

    print(
        "[PASS] Complete binary vector built."
    )

    # --------------------------------------------------------
    # Complete multiclass vector
    # --------------------------------------------------------

    multiclass_features = {
        feature: 1.0
        for feature
        in builder.multiclass_features
    }

    multiclass_vector = (
        builder.build_multiclass(
            multiclass_features
        )
    )

    assert len(multiclass_vector) == 81

    print(
        "[PASS] Complete multiclass vector built."
    )

    # --------------------------------------------------------
    # Missing binary feature
    # --------------------------------------------------------

    incomplete_binary = dict(
        binary_features
    )

    incomplete_binary.pop(
        builder.binary_features[0]
    )

    try:

        builder.build_binary(
            incomplete_binary
        )

    except ValueError:

        print(
            "[PASS] Incomplete binary "
            "vector rejected."
        )

    else:

        raise AssertionError(
            "Incomplete binary vector "
            "was accepted."
        )

    # --------------------------------------------------------
    # Missing multiclass feature
    # --------------------------------------------------------

    incomplete_multiclass = dict(
        multiclass_features
    )

    incomplete_multiclass.pop(
        builder.multiclass_features[0]
    )

    try:

        builder.build_multiclass(
            incomplete_multiclass
        )

    except ValueError:

        print(
            "[PASS] Incomplete multiclass "
            "vector rejected."
        )

    else:

        raise AssertionError(
            "Incomplete multiclass vector "
            "was accepted."
        )

    print(
        "\n[SUCCESS] "
        "Feature vector builder self-test passed."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    _self_test()