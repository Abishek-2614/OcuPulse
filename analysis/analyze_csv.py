#!/usr/bin/env python3
"""Analyse a paired/resampled OcuPulse CSV for exploratory features only."""
from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from oculpulse.processing import estimate_heart_rate_bpm, extract_distance_cycle_features, summarize_features


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--sample-rate", type=float, required=True, help="Sampling rate after explicit time alignment/resampling, in Hz")
    parser.add_argument("--output", type=Path, help="Write JSON summary to this path (also prints to stdout)")
    args = parser.parse_args()
    if not args.csv_file.exists():
        parser.error(f"CSV file not found: {args.csv_file}")
    distance, ppg = [], []
    with args.csv_file.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"time_s", "tof_distance_mm", "ppg_ir"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            parser.error("CSV must contain columns: time_s,tof_distance_mm,ppg_ir")
        for row_number, row in enumerate(reader, start=2):
            try:
                d = float(row["tof_distance_mm"])
                p = float(row["ppg_ir"])
            except (TypeError, ValueError):
                print(f"Warning: skipping row {row_number} with non-numeric channel values", file=sys.stderr)
                continue
            distance.append(d)
            ppg.append(p)
    if len(distance) < 3:
        parser.error("Need at least 3 valid paired rows")
    features = extract_distance_cycle_features(distance, ppg, args.sample_rate)
    result = {
        "input_file": args.csv_file.name,
        "data_type": "unknown; inspect metadata before any research reuse",
        "sample_rate_hz_assumed_after_alignment": args.sample_rate,
        "paired_rows_used": len(distance),
        "estimated_heart_rate_bpm_exploratory": estimate_heart_rate_bpm(ppg, args.sample_rate),
        **summarize_features(features),
    }
    rendered = json.dumps(result, indent=2)
    print(rendered)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
