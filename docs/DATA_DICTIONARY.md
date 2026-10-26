# Data Dictionary

## ESP32 event-stream CSV

| Column | Type | Definition |
|---|---|---|
| event | string | TOF or PPG |
| timestamp_us | integer | ESP32 micros() timestamp at acquisition/read, in microseconds |
| value | numeric | For TOF, distance in millimetres; for PPG, raw IR count |
| valid | integer 0/1 | Basic firmware plausibility flag, not a clinical quality assessment |

Keep this raw event log unchanged. micros() wrap-around must be addressed in long recordings. Use event to interpret the value units.

## Paired/resampled analysis CSV

The included Python CLI expects:

| Column | Type | Definition |
|---|---|---|
| time_s | float | Time axis in seconds after documented alignment/resampling |
| tof_distance_mm | float | ToF distance measurement, mm |
| ppg_ir | float | PPG IR count |

The paired format is not the same as the firmware event stream. Align/resample explicitly before analysis; do not silently fabricate missing values. Record provenance, original timestamps, resampling details, exclusions, and any filters in a separate metadata file.

## Synthetic sample provenance

sample_data/synthetic_bench_data.csv is computer-generated solely to test the code path. It contains no human data, does not represent actual sensor measurements, and must not be reported as an experimental result.
