# Software test record

Tested in the file-generation environment using the Python standard library.

Command:

    python -m unittest discover -s tests -v

Result: **7 unit tests passed**. The sample CLI was also run against sample_data/synthetic_bench_data.csv at 50 Hz and produced a JSON summary. This confirms only the local Python test path with synthetic data.

**Not tested here:** Arduino compilation on a target toolchain, physical ESP32/sensor operation, optical safety, true sample cadence, controlled displacement sensitivity, human-subject testing, or clinical validity. Do not interpret the synthetic summary values as hardware measurements or clinical results.
