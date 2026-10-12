from backend.behavioral_severity import BehavioralSeverityEngine

TEST_BASELINE = {
    "retry_rate": {"p95": 0.1, "p99": 0.3},
    "deauth_rate": {"p95": 1.0, "p99": 3.0},
    "disassoc_rate": {"p95": 1.0, "p99": 3.0},
    "dns_latency_mean": {"p95": 0.1, "p99": 0.3},
    "retransmission_rate": {"p95": 0.1, "p99": 0.3},
    "rst_rate": {"p95": 1.0, "p99": 3.0},
}

def test_unavailable_zero_is_not_scored():
    engine = BehavioralSeverityEngine(TEST_BASELINE)

    result = engine.analyze(
        {"retry_rate": 0.0},
        availability={"wifi_retry_available": False},
    )

    assert result["features"]["retry_rate"] is None
    assert "retry_rate" in result["unavailable_features"]
    assert result["risk"] is None


def test_verified_zero_can_be_scored():
    engine = BehavioralSeverityEngine(TEST_BASELINE)

    result = engine.analyze(
        {"retry_rate": 0.0},
        availability={"wifi_retry_available": True},
    )

    assert result["features"]["retry_rate"] == 0.0


def test_unknown_tcp_availability_is_not_assumed():
    engine = BehavioralSeverityEngine(TEST_BASELINE)

    result = engine.analyze(
        {"rst_rate": 0.0},
        availability={"wifi_retry_available": True},
    )

    assert result["features"]["rst_rate"] is None
    assert "rst_rate" in result["unavailable_features"]


def test_verified_tcp_feature():
    engine = BehavioralSeverityEngine(TEST_BASELINE)

    result = engine.analyze(
        {"rst_rate": 2.0},
        availability={"rst_rate": True},
    )

    assert result["features"]["rst_rate"] == 50.0


def test_no_baseline_means_no_behavior_score():
    engine = BehavioralSeverityEngine()

    result = engine.analyze(
        {"retry_rate": 0.2},
        availability={"retry_rate": True},
    )

    assert result["risk"] is None
    assert result["features"]["retry_rate"] is None
