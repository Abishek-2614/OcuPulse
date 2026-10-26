# OcuPulse — Experimental Ocular-Motion Research Prototype

OcuPulse is an experimental research project exploring whether distance-waveform features from a VL53L1X Time-of-Flight (ToF) sensor, together with timing information from a MAX30102 photoplethysmography (PPG) sensor, can be studied for possible non-contact intraocular pressure (IOP) estimation.

> **Safety and scope:** OcuPulse is not a medical device and is not validated for diagnosis, screening, treatment, or clinical decision-making. Do not point an unassessed optical prototype at a human eye. The sample data in this repository are synthetic and are not patient data or measurements from a physical prototype. Do not interpret the demonstration pipeline output as IOP in mmHg.

## Hardware concept

- ESP32 DevKit V1
- VL53L1X ToF distance sensor
- MAX30102 PPG sensor
- SSD1306 128×64 I²C OLED (optional)
- Stable bench fixture and a non-human test target for characterization

Typical ESP32 I²C wiring in the project concept: SDA GPIO 21 and SCL GPIO 22. Confirm your board, module voltage levels, breakout-board documentation, and installed library versions before powering hardware.

## Repository map

```text
.
├── firmware/OcuPulse_Logger/OcuPulse_Logger.ino  # ESP32 acquisition/event logger (needs hardware verification)
├── src/oculpulse/processing.py                   # Exploratory signal-processing utilities
├── analysis/analyze_csv.py                       # CSV analysis entry point
├── sample_data/                                  # Clearly labelled synthetic bench-like data
├── tests/test_processing.py                      # Python unit tests
├── docs/TECHNICAL_DESIGN.md                      # Architecture, data flow, assumptions, risks
├── docs/DATA_DICTIONARY.md                       # CSV fields and units
├── docs/TEST_PLAN.md                             # Bench and software test plan
├── docs/REFERENCES.md                            # Sensor/library documentation
├── docs/AI_DISCLOSURE.md                         # AI-use and contribution disclosure
├── LICENSE                                      # MIT License for original repository content
└── .github/workflows/python-tests.yml            # Automated Python tests
```

## Python setup

Recommended: Python 3.10 or newer.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python analysis/analyze_csv.py sample_data/synthetic_bench_data.csv
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python analysis/analyze_csv.py sample_data/synthetic_bench_data.csv
```

The Python analysis pipeline is designed to run without cloud credentials. No environment variables or API keys are required. It accepts a CSV path as a command-line argument; refer to `docs/DATA_DICTIONARY.md` for required columns and units.

## Firmware setup (bench testing only)

1. Install Arduino IDE or another ESP32-compatible build environment.
2. Install the Espressif ESP32 board support package.
3. Install and verify compatible versions of the Pololu VL53L1X and SparkFun MAX3010x/MAX30105 libraries used by the sketch.
4. Open `firmware/OcuPulse_Logger/OcuPulse_Logger.ino`, select the correct ESP32 board and port, compile, and resolve any library-version-specific API differences.
5. Test on a bench target only. Log sensor availability, actual sampling intervals, missing samples, and timeouts before any physiological interpretation.

The firmware has not been confirmed on the team's physical hardware in this repository release. Sensor APIs and timing behavior may vary by library version. The ToF and PPG streams must be timestamped independently; equal nominal sample-rate settings do not guarantee synchronization.

## Data and tests

`sample_data/synthetic_bench_data.csv` is deterministic synthetic data used to exercise software paths. It is **not** measured device output. Run tests with `python -m unittest discover -s tests -v`. Test status and limitations are recorded in `TEST_RESULTS.md` and `docs/TEST_PLAN.md`.

For physical bench characterization, first record stationary-target measurements, then controlled target shifts with an independent reference. Report mean, bias, standard deviation, missing-sample rate, repeatability, and stability. Keep raw logs and configuration details so results can be reproduced.

## Research workflow and limits

1. Characterize sensor repeatability and actual usable range under controlled bench conditions.
2. Validate controlled displacement response independently of physiological assumptions.
3. Validate PPG peak detection and timestamp quality.
4. Acquire separate timestamped ToF and PPG streams and quantify synchronization uncertainty.
5. Preprocess signals and extract features only when quality checks pass.
6. If future ethically approved research produces paired reference IOP data, fit and evaluate any model on subject-independent splits, with appropriate statistical and clinical oversight.

Do not use invented coefficients or synthetic data to claim measurement accuracy. Any model output remains an exploratory feature score unless calibrated and independently validated against suitable reference measurements. Clinical translation requires optical safety assessment, ethics approval, qualified ophthalmology oversight, and robust external validation.

## Technical documentation

- [Technical Design Document](docs/TECHNICAL_DESIGN.md)
- [Data Dictionary](docs/DATA_DICTIONARY.md)
- [Test Plan](docs/TEST_PLAN.md)
- [References](docs/REFERENCES.md)
- [AI-use disclosure](docs/AI_DISCLOSURE.md)
- [Test record](TEST_RESULTS.md)

## License

This repository's original content is released under the MIT License. Third-party libraries and sensor firmware remain under their respective licenses; see `docs/REFERENCES.md`. Ensure all team members have authority to release contributed code before publishing.

## Citation

For a project or academic report, cite this as the OcuPulse experimental ocular-motion research prototype repository and include the access date and commit hash used.
