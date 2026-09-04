# OMEN v0.1 audit scripts

Reproduces every number in Section 9 of the paper.

- `mapper.py`  maps Free Exercise DB records onto OMEN facets using only v0.1 vocabularies
- `audit2.py`  coverage audit + extension queue + synonymy   -> results.json
- `stress.py`  collision / determinism sweep (2,498,496 records) -> stress.json

## Run
```
pip install nothing        # no dependencies beyond the standard library
# place omen.py and exercises.json (Free Exercise DB) beside these scripts
python audit2.py
python stress.py
```
Free Exercise DB: https://github.com/yuhonas/free-exercise-db (public domain)
