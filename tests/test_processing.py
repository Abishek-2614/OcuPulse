import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from oculpulse.processing import detect_peaks, estimate_heart_rate_bpm, extract_distance_cycle_features, moving_average, summarize_features


class ProcessingTests(unittest.TestCase):
    def test_moving_average_length_and_values(self):
        self.assertEqual(moving_average([1, 2, 3, 4], 1), [1.0, 2.0, 3.0, 4.0])
        out = moving_average([1, 2, 3], 3)
        self.assertEqual(len(out), 3)
        self.assertAlmostEqual(out[1], 2.0)

    def test_moving_average_rejects_invalid(self):
        with self.assertRaises(ValueError):
            moving_average([1.0, float("nan")], 2)

    def test_peak_detection_respects_separation(self):
        signal = [0.0] * 30
        signal[5], signal[7], signal[18] = 3.0, 4.0, 5.0
        peaks = detect_peaks(signal, 10, min_distance_s=0.5, threshold=1.0)
        self.assertEqual(peaks, [7, 18])

    def test_heart_rate_from_regular_pulses(self):
        fs, seconds = 50, 10
        x = [0.0] * (fs * seconds)
        for index in range(10, len(x), 40):
            x[index] = 10.0
        hr = estimate_heart_rate_bpm(x, fs)
        self.assertIsNotNone(hr)
        self.assertAlmostEqual(hr, 75.0, delta=2.0)

    def test_heart_rate_returns_none_without_enough_peaks(self):
        self.assertIsNone(estimate_heart_rate_bpm([0.0, 1.0, 0.0], 50))

    def test_feature_extraction_and_no_iop_value(self):
        fs, n = 50, 500
        ppg = [0.0] * n
        distance = []
        for i in range(n):
            t = i / fs
            phase = (t % 0.8) / 0.8
            distance.append(14.0 + 0.05 * math.sin(2 * math.pi * phase))
        for idx in range(10, n, 40):
            ppg[idx] = 10.0
        features = extract_distance_cycle_features(distance, ppg, fs)
        self.assertGreaterEqual(len(features), 5)
        summary = summarize_features(features)
        self.assertIsNone(summary["clinical_iop_estimate"])
        self.assertGreater(summary["opa_proxy_mean_mm"], 0.0)

    def test_channel_length_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            extract_distance_cycle_features([1, 2, 3], [1, 2], 50)


if __name__ == "__main__":
    unittest.main()
