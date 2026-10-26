"""Dependency-light, exploratory signal processing for OcuPulse.

These functions are for software tests and research exploration. They are not
clinically validated biomarkers or a medical-device algorithm.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite, sqrt
from statistics import fmean, pstdev
from typing import Iterable, Sequence


@dataclass(frozen=True)
class CycleFeature:
    ppg_peak_index: int
    distance_peak_index: int
    opa_proxy_mm: float
    rise_fall_ratio: float | None
    ppg_to_distance_delay_ms: float


def _finite_values(values: Iterable[float]) -> list[float]:
    result = []
    for value in values:
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if isfinite(number):
            result.append(number)
    return result


def moving_average(values: Sequence[float], window: int) -> list[float]:
    """Centered moving average, returning a list with the same length.

    Edges use the available points. Non-finite data is not silently imputed;
    callers should clean/flag missing samples before calling this function.
    """
    if window < 1:
        raise ValueError("window must be >= 1")
    xs = [float(v) for v in values]
    if any(not isfinite(v) for v in xs):
        raise ValueError("values must be finite; handle missing samples explicitly")
    if not xs:
        return []
    radius_left = (window - 1) // 2
    radius_right = window // 2
    prefix = [0.0]
    for value in xs:
        prefix.append(prefix[-1] + value)
    out: list[float] = []
    for i in range(len(xs)):
        left = max(0, i - radius_left)
        right = min(len(xs), i + radius_right + 1)
        out.append((prefix[right] - prefix[left]) / (right - left))
    return out


def _mean_std(values: Sequence[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    mean = fmean(values)
    return mean, pstdev(values)


def detect_peaks(
    signal: Sequence[float],
    sample_rate_hz: float,
    *,
    min_distance_s: float = 0.4,
    threshold: float | None = None,
) -> list[int]:
    """Detect local maxima above a global threshold with minimum separation.

    This simple detector is provided as an educational baseline. Real PPG often
    needs quality checks, adaptive thresholds, motion-artifact handling, and
    validation against annotated signals.
    """
    if sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be > 0")
    if min_distance_s < 0:
        raise ValueError("min_distance_s must be >= 0")
    xs = [float(v) for v in signal]
    if any(not isfinite(v) for v in xs):
        raise ValueError("signal must contain only finite values")
    if len(xs) < 3:
        return []
    if threshold is None:
        mean, std = _mean_std(xs)
        threshold = mean + 0.35 * std
    min_gap = max(1, int(round(min_distance_s * sample_rate_hz)))
    candidates = [
        i for i in range(1, len(xs) - 1)
        if xs[i] >= threshold and xs[i] > xs[i - 1] and xs[i] >= xs[i + 1]
    ]
    selected: list[int] = []
    for index in candidates:
        if not selected or index - selected[-1] >= min_gap:
            selected.append(index)
        elif xs[index] > xs[selected[-1]]:
            selected[-1] = index
    return selected


def estimate_heart_rate_bpm(
    ppg: Sequence[float], sample_rate_hz: float, *, min_hr_bpm: float = 40.0, max_hr_bpm: float = 180.0
) -> float | None:
    """Estimate average heart rate from detected PPG peaks; return None if insufficient."""
    peaks = detect_peaks(ppg, sample_rate_hz)
    if len(peaks) < 2:
        return None
    valid_rr = []
    for left, right in zip(peaks, peaks[1:]):
        rr = (right - left) / sample_rate_hz
        if rr > 0:
            bpm = 60.0 / rr
            if min_hr_bpm <= bpm <= max_hr_bpm:
                valid_rr.append(rr)
    if not valid_rr:
        return None
    return 60.0 / fmean(valid_rr)


def extract_distance_cycle_features(
    distance_mm: Sequence[float],
    ppg: Sequence[float],
    sample_rate_hz: float,
    *,
    pre_window_s: float = 0.20,
    post_window_s: float = 0.65,
) -> list[CycleFeature]:
    """Extract exploratory local distance features around each detected PPG peak.

    OPA proxy is defined here as the local max-minus-min distance range. It is
    not asserted to be a validated ocular pulse amplitude. A cycle gets a rise /
    fall ratio only when a trough before and after the selected maximum exists.
    """
    if sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be > 0")
    if pre_window_s < 0 or post_window_s <= 0:
        raise ValueError("window lengths must be non-negative and post_window_s > 0")
    d = [float(v) for v in distance_mm]
    p = [float(v) for v in ppg]
    if any(not isfinite(v) for v in d + p):
        raise ValueError("inputs must be finite; handle invalid/missing samples explicitly")
    if len(d) != len(p):
        raise ValueError("distance_mm and ppg must have equal length after explicit alignment")
    ppg_peaks = detect_peaks(p, sample_rate_hz)
    pre = int(round(pre_window_s * sample_rate_hz))
    post = int(round(post_window_s * sample_rate_hz))
    features: list[CycleFeature] = []
    for ppg_index in ppg_peaks:
        left = max(0, ppg_index - pre)
        right = min(len(d), ppg_index + post + 1)
        if right - left < 5:
            continue
        segment = d[left:right]
        local_max_index = max(range(len(segment)), key=segment.__getitem__)
        local_min_index = min(range(len(segment)), key=segment.__getitem__)
        distance_peak_index = left + local_max_index
        opa = segment[local_max_index] - segment[local_min_index]
        ratio: float | None = None
        if local_max_index >= 1 and local_max_index < len(segment) - 2:
            before = min(range(local_max_index + 1), key=segment.__getitem__)
            after_rel = local_max_index + 1 + min(
                range(len(segment) - local_max_index - 1),
                key=lambda j: segment[local_max_index + 1 + j],
            )
            rise_s = (local_max_index - before) / sample_rate_hz
            fall_s = (after_rel - local_max_index) / sample_rate_hz
            if rise_s > 0 and fall_s > 0:
                ratio = rise_s / fall_s
        features.append(CycleFeature(
            ppg_peak_index=ppg_index,
            distance_peak_index=distance_peak_index,
            opa_proxy_mm=float(opa),
            rise_fall_ratio=float(ratio) if ratio is not None and isfinite(ratio) else None,
            ppg_to_distance_delay_ms=1000.0 * (distance_peak_index - ppg_index) / sample_rate_hz,
        ))
    return features


def summarize_features(features: Sequence[CycleFeature]) -> dict[str, object]:
    """Create a JSON-friendly summary without inferring IOP."""
    if not features:
        return {"valid_cycles": 0, "opa_proxy_mean_mm": None, "rise_fall_ratio_mean": None,
                "ppg_to_distance_delay_mean_ms": None, "clinical_iop_estimate": None}
    opas = [f.opa_proxy_mm for f in features if isfinite(f.opa_proxy_mm)]
    ratios = [f.rise_fall_ratio for f in features if f.rise_fall_ratio is not None and isfinite(f.rise_fall_ratio)]
    delays = [f.ppg_to_distance_delay_ms for f in features if isfinite(f.ppg_to_distance_delay_ms)]
    return {
        "valid_cycles": len(features),
        "opa_proxy_mean_mm": fmean(opas) if opas else None,
        "opa_proxy_population_std_mm": pstdev(opas) if len(opas) > 1 else (0.0 if opas else None),
        "rise_fall_ratio_mean": fmean(ratios) if ratios else None,
        "ppg_to_distance_delay_mean_ms": fmean(delays) if delays else None,
        "clinical_iop_estimate": None,
        "note": "Exploratory signal features only; no clinical IOP estimate is calculated."
    }
