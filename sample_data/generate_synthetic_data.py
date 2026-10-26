"""Generate deterministic synthetic paired data for software tests only."""
import csv
import math
from pathlib import Path

OUTPUT = Path(__file__).with_name("synthetic_bench_data.csv")
FS_HZ = 50.0
DURATION_S = 15.0
HEART_PERIOD_S = 0.8
DISTANCE_DELAY_S = 0.12


def main() -> None:
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_s", "tof_distance_mm", "ppg_ir"])
        for i in range(int(FS_HZ * DURATION_S)):
            t = i / FS_HZ
            distance = (
                14.0
                + 0.002 * t
                + 0.035 * math.sin(2 * math.pi * (t - DISTANCE_DELAY_S) / HEART_PERIOD_S)
                + 0.0025 * math.sin(2 * math.pi * 7.3 * t)
            )
            ppg = 17000.0 + 300.0 * math.sin(2 * math.pi * 0.15 * t)
            for beat in (0.2 + j * HEART_PERIOD_S for j in range(20)):
                ppg += 7000.0 * math.exp(-0.5 * ((t - beat) / 0.055) ** 2)
            ppg += 90.0 * math.sin(2 * math.pi * 8.1 * t)
            writer.writerow([f"{t:.3f}", f"{distance:.6f}", f"{ppg:.2f}"])
    print(f"Wrote synthetic test data: {OUTPUT}")


if __name__ == "__main__":
    main()
