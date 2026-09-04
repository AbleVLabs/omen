# OMEN v0.1 audit scripts

Reproduces every number in Section 9 of the paper.

- `mapper.py`  maps Free Exercise DB records onto OMEN facets using only v0.1 vocabularies
- `audit2.py`  coverage audit + extension queue + synonymy   -> results.json
- `stress.py`  collision / determinism sweep (6,054,048 records) -> stress.json
- `wger_audit.py`  second-corpus audit, same mapper  -> wger_results.json
- `crosswalk.py`  emits omen_crosswalk.csv / .json (the adoptable artifact)
- `make_manual_sample.py` + `compare_manual.py`  hand-encode 50 records and measure
  how far the automated mapping departs from human judgement

## Run
```
pip install nothing        # no dependencies beyond the standard library
# place omen.py and exercises.json (Free Exercise DB) beside these scripts
python audit2.py
python stress.py
```
Free Exercise DB: https://github.com/yuhonas/free-exercise-db (public domain)
