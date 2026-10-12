import pytest

from backend.capture.feature_window import _dns_latencies, FeatureExtractor


def packet(timestamp, transaction_id="1234", response=False,
           source="192.168.1.10", destination="8.8.8.8"):
    return {
        "timestamp": timestamp,
        "dns_transaction_id": transaction_id,
        "dns_response": response,
        "dns": True,
        "source": source,
        "destination": destination,
    }


def test_matches_request_and_response():
    packets = [
        packet(10.0, response=False),
        packet(10.125, response=True,
               source="8.8.8.8", destination="192.168.1.10"),
    ]
    assert _dns_latencies(packets) == pytest.approx([0.125])


def test_ignores_unmatched_response():
    packets = [
        packet(10.125, response=True,
               source="8.8.8.8", destination="192.168.1.10"),
    ]
    assert _dns_latencies(packets) == []


def test_matches_reused_transaction_id_in_fifo_order():
    packets = [
        packet(1.0),
        packet(1.1),
        packet(1.2, response=True,
               source="8.8.8.8", destination="192.168.1.10"),
        packet(1.4, response=True,
               source="8.8.8.8", destination="192.168.1.10"),
    ]
    assert _dns_latencies(packets) == pytest.approx([0.2, 0.3])


def test_does_not_match_different_endpoint_pair():
    packets = [
        packet(1.0),
        packet(1.2, response=True,
               source="1.1.1.1", destination="192.168.1.10"),
    ]
    assert _dns_latencies(packets) == []


def test_ignores_missing_id_or_invalid_timestamp():
    packets = [
        packet(1.0, transaction_id=None),
        packet(float("nan")),
        packet(1.2, response=True,
               source="8.8.8.8", destination="192.168.1.10"),
    ]
    assert _dns_latencies(packets) == []


def test_matches_dns_across_feature_windows():
    extractor = FeatureExtractor(window_size=1.0)

    request = packet(
        100.1,
        response=False,
        source="192.168.1.10",
        destination="8.8.8.8",
    )
    response = packet(
        101.1,
        response=True,
        source="8.8.8.8",
        destination="192.168.1.10",
    )

    first = extractor.extract_window_features([request], duration=1.0)
    second = extractor.extract_window_features([response], duration=1.0)

    assert first["dns_latency_mean"] == pytest.approx(0.0)
    assert second["dns_latency_mean"] == pytest.approx(1.0)
