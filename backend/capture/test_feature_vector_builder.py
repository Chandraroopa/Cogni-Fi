from backend.capture.feature_vector_builder import (
    FeatureVectorBuilder,
)


def main():

    builder = FeatureVectorBuilder()

    print(
        "Binary feature count:",
        builder.binary_feature_count(),
    )

    print(
        "Multiclass feature count:",
        builder.multiclass_feature_count(),
    )

    # ---------------------------------------------------------
    # Verify frozen schema sizes
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Create a deliberately incomplete feature dictionary.
    #
    # This is expected to fail strict construction.
    # ---------------------------------------------------------

    test_features = {
        "frame.len": 100.0,
        "frame.time_delta": 0.1,
        "ip.proto": 6.0,
        "ip.ttl": 128.0,
    }

    # ---------------------------------------------------------
    # Binary diagnostic
    # ---------------------------------------------------------

    binary_diagnostic = (
        builder.diagnose_binary(
            test_features
        )
    )

    print(
        "\n===== BINARY DIAGNOSTIC ====="
    )

    print(
        "Expected:",
        binary_diagnostic[
            "expected_count"
        ],
    )

    print(
        "Available:",
        binary_diagnostic[
            "available_count"
        ],
    )

    print(
        "Missing:",
        binary_diagnostic[
            "missing_count"
        ],
    )

    print(
        "Invalid:",
        binary_diagnostic[
            "invalid_count"
        ],
    )

    print(
        "\nFirst missing binary features:"
    )

    for feature in (
        binary_diagnostic["missing"][:15]
    ):

        print(
            "  -",
            feature,
        )

    # ---------------------------------------------------------
    # Multiclass diagnostic
    # ---------------------------------------------------------

    multiclass_diagnostic = (
        builder.diagnose_multiclass(
            test_features
        )
    )

    print(
        "\n===== MULTICLASS DIAGNOSTIC ====="
    )

    print(
        "Expected:",
        multiclass_diagnostic[
            "expected_count"
        ],
    )

    print(
        "Available:",
        multiclass_diagnostic[
            "available_count"
        ],
    )

    print(
        "Missing:",
        multiclass_diagnostic[
            "missing_count"
        ],
    )

    print(
        "Invalid:",
        multiclass_diagnostic[
            "invalid_count"
        ],
    )

    print(
        "\nFirst missing multiclass features:"
    )

    for feature in (
        multiclass_diagnostic[
            "missing"
        ][:15]
    ):

        print(
            "  -",
            feature,
        )

    # ---------------------------------------------------------
    # Verify strict mode rejects incomplete data
    # ---------------------------------------------------------

    try:

        builder.build_binary(
            test_features
        )

        raise AssertionError(
            "Incomplete binary vector "
            "was incorrectly accepted."
        )

    except ValueError:

        print(
            "\n[PASS] "
            "Incomplete binary vector rejected."
        )

    try:

        builder.build_multiclass(
            test_features
        )

        raise AssertionError(
            "Incomplete multiclass vector "
            "was incorrectly accepted."
        )

    except ValueError:

        print(
            "[PASS] "
            "Incomplete multiclass vector rejected."
        )

    print(
        "\n[SUCCESS] "
        "Feature vector builder tests passed."
    )


if __name__ == "__main__":
    main()