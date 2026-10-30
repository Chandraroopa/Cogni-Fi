"""Availability-aware behavioral reference generation.

Candidate/unverified traffic is NEVER promoted to a production baseline.
CSV units (for example dns_latency_mean in seconds) are preserved.
"""
import csv
import json
import math
from pathlib import Path

from .risk_config import BEHAVIOR_GROUPS

AVAILABILITY = {
    'retry_rate': 'wifi_retry_available',
    'deauth_rate': 'wifi_management_frames_available',
    'disassoc_rate': 'wifi_management_frames_available',
    'dns_latency_mean': 'dns_latency_available',
    'retransmission_rate': 'tcp_retransmission_available',
    'rst_rate': 'tcp_rst_available',
}


def percentile(values, q):
    """Linear interpolation on the sorted observations (numpy's default convention)."""
    values = sorted(values)
    if not values:
        return None
    position = (len(values) - 1) * q
    low = int(position)
    high = min(low + 1, len(values) - 1)
    return values[low] + (values[high] - values[low]) * (position - low)


def analyze_capture(csv_path, metadata_path):
    csv_path = Path(csv_path)
    with Path(metadata_path).open(encoding='utf-8') as source:
        metadata = json.load(source)
    with csv_path.open(encoding='utf-8-sig', newline='') as source:
        rows = list(csv.DictReader(source))
    if not rows:
        raise ValueError('Capture contains no feature windows')
    if len(rows) != metadata.get('windows_exported'):
        raise ValueError('CSV window count does not match capture metadata')
    if any(row.get('traffic_label') != metadata.get('traffic_label') for row in rows):
        raise ValueError('Traffic labels do not match capture metadata')
    if any(name not in rows[0] for name in AVAILABILITY):
        raise ValueError('Missing required behavioral feature columns')
    if any(flag not in rows[0] for flag in AVAILABILITY.values()):
        raise ValueError('Missing required availability columns')

    statistics = {}
    for feature, flag in AVAILABILITY.items():
        valid = []
        available_count = 0
        for row in rows:
            if str(row[flag]).strip().lower() != 'true':
                continue
            available_count += 1
            try:
                value = float(row[feature])
            except (ValueError, TypeError):
                continue
            if math.isfinite(value) and value >= 0:
                valid.append(value)
        statistics[feature] = {
            'available_windows': available_count,
            'valid_windows': len(valid),
            'p95': round(percentile(valid, .95), 9) if valid else None,
            'p99': round(percentile(valid, .99), 9) if valid else None,
        }

    return {
        'traffic_label': metadata['traffic_label'],
        'verified_normal': metadata['traffic_label'] == 'verified_normal',
        'usable_as_production_baseline': metadata['traffic_label'] == 'verified_normal',
        'window_count': len(rows),
        'link_type': metadata.get('capture_link_type'),
        'source_csv': csv_path.name,
        'behavioral_statistics': statistics,
        'warning': ('Candidate reference statistics only; NOT a calibrated normal baseline.'
                    if metadata['traffic_label'] != 'verified_normal' else None),
    }


def load_verified_baseline(report_path):
    """Fail closed: reject candidate/unverified reports and missing measurements."""
    with Path(report_path).open(encoding='utf-8') as source:
        report = json.load(source)
    if report.get('traffic_label') != 'verified_normal' or report.get('verified_normal') is not True:
        raise ValueError('Only verified_normal datasets may calibrate production behavior')
    return {
        name: {'p95': result['p95'], 'p99': result['p99']}
        for name, result in report['behavioral_statistics'].items()
        if result['valid_windows'] > 0 and result['p95'] is not None and result['p99'] is not None
    }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('csv')
    parser.add_argument('metadata')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    report = analyze_capture(args.csv, args.metadata)
    Path(args.output).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f"Generated {args.output}; verified_normal={report['verified_normal']}")
