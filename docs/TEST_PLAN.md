# Test Plan

| ID | Category | Procedure | Expected result | Status |
|---|---|---|---|---|
| SW-01 | Unit | Run python -m unittest discover -s tests -v | All unit tests pass | Run locally before submission |
| SW-02 | Input validation | Supply unequal channel lengths to feature extractor | Raises ValueError | Automated test |
| SW-03 | Peak detection | Provide synthetic peaks with known spacing | Detected indices respect minimum separation | Automated test |
| SW-04 | Heart-rate calculation | Provide regular synthetic pulses at 0.8 s intervals | Approximately 75 BPM | Automated test |
| HW-01 | ToF stationary stability | Log a stationary non-human target for a defined duration | Mean, standard deviation, valid-reading percentage documented | Not yet performed by this repository |
| HW-02 | Displacement response | Use a controlled stage/reference and multiple known offsets | Plot measured vs reference displacement; report slope, intercept, uncertainty | Not yet performed |
| HW-03 | PPG acquisition | Compare detected peaks with annotated/reference waveform | Sensitivity, precision and failure cases reported | Not yet performed |
| INT-01 | Timestamp integrity | Log both channels and inspect timestamp intervals / dropped samples | Gaps and cadence documented; no assumed synchronization | Not yet performed |
| SAF-01 | Human/clinical safety | Review optical safety, protocol, ethics and qualified supervision | No human-eye testing without appropriate review and approval | Mandatory gate |
