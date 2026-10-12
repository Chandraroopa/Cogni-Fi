# Cogni-Fi Live Capture Audit

## Scope
Read-only audit of `data/live_windows_20261012_233850.csv`
and `ml/candidate_30/feature_schema.json`.

## Capture findings
- Windows inspected: 66.
- Traffic labels: all 66 are `unlabelled`.
- All six Wi-Fi availability flags are false in all 66 windows:
  retry, protected traffic, management frames, signal, data rate, BSSID.
- Wi-Fi-specific feature values being zero does not prove that the
  corresponding activity was absent; the required metadata was unavailable.
- Do not interpret these unlabelled predictions as verified accuracy.

## Verified rate formulas
- `syn_rate` = TCP SYN count / window duration (packets/second).
- `rst_rate` = TCP RST count / window duration (packets/second).
- `udp_packet_rate` = packets with a valid UDP destination port /
  window duration (packets/second).
- `retransmission_rate` = TCP retransmission count / packet count
  (dimensionless ratio, not packets/second).
- `retry_rate` and `protected_rate` = respective counts / packet count
  (dimensionless ratios).
- Beacon, deauthentication, disassociation and probe-response rates
  = respective management-frame counts / window duration (frames/second).

## Units and interpretation
- `packet_count`, `byte_count`, unique-address counts and unique-port
  counts are counts.
- `packets_per_second`, `bytes_per_second`, `syn_rate`, `rst_rate`
  and `udp_packet_rate` are rates per second.
- Packet-size statistics use the captured packet-length unit (normally bytes).
- `iat_mean` and `iat_std` use seconds when timestamps are in seconds.
- DNS latency statistics are in seconds according to the extractor.
- Signal and data-rate units depend on the actual capture source and
  must not be claimed as verified until confirmed from captured metadata.
- A zero feature value must not be treated as proof of absence when its
  availability flag is false.

## Documentation limitation
The candidate schema documents 30 feature names, but its
`availability_flags` list is empty despite six diagnostic availability
flags being emitted separately. Per-feature units are not documented
there. This note records the discrepancy without editing the schema.

## Validation status
- Feature mapping/order: previously verified against the 30-feature schema.
- Wi-Fi metadata availability: unavailable in this capture.
- Ground-truth labels: unavailable; accuracy is not established.
- Model, threshold, feature schema, median artifacts and capture code:
  intentionally unchanged.
