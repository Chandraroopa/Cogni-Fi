import json
from pathlib import Path
import pytest
from backend.behavioral_baseline import analyze_capture, load_verified_baseline

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / 'data/behavioral/normal_001_features.csv'
METADATA = ROOT / 'data/behavioral/normal_001_metadata.json'


def test_candidate_capture_is_not_verified():
    report = analyze_capture(CSV, METADATA)
    assert report['window_count'] == 300
    assert report['verified_normal'] is False
    assert report['usable_as_production_baseline'] is False
    assert report['behavioral_statistics']['dns_latency_mean']['valid_windows'] == 146
    assert report['behavioral_statistics']['rst_rate']['valid_windows'] == 285
    assert report['behavioral_statistics']['retransmission_rate']['valid_windows'] == 0
    for feature in ('retry_rate', 'deauth_rate', 'disassoc_rate', 'retransmission_rate'):
        assert report['behavioral_statistics'][feature]['p95'] is None


def test_candidate_baseline_cannot_be_loaded():
    report_path = ROOT / 'data/behavioral/normal_001_candidate_report.json'
    with pytest.raises(ValueError, match='verified_normal'):
        load_verified_baseline(report_path)


def test_mismatched_metadata_is_rejected(tmp_path):
    metadata = json.loads(METADATA.read_text())
    metadata['windows_exported'] = 301
    edited = tmp_path / 'metadata.json'
    edited.write_text(json.dumps(metadata))
    with pytest.raises(ValueError, match='count'):
        analyze_capture(CSV, edited)
