# OMEN — Open Movement & Exercise Nomenclature

**AbleVLabs · a generative, computable naming standard for resistance-training movements**

Exercise names are a mess. The same movement shows up as *arm curl*, *bicep curl*,
and *biceps curl*; every app invents its own schema; and there's no shared key that
lets a training log, a research dataset, and a coaching app agree on **which movement**
they mean. Surveys show professionals know it's a problem and want it fixed.

OMEN fixes it the way chemistry fixed molecule naming (SMILES/InChI) and medicine
fixed clinical terms (SNOMED CT): describe the thing as a bundle of **orthogonal
facets**, then generate a canonical form and a stable identifier from that bundle
deterministically.

## The three layers

1. **The facet record** — the source of truth. Posture, implement, movement pattern,
   laterality, and optional modifiers (grip, angle, contraction, range). The muscle
   worked is **derived** from the movement pattern, not typed in.
2. **The canonical form + key** — generated from the record:
   - `OMEN-C` — the short human form (`incline dumbbell horizontal-push`)
   - `OMEN-X` — the fully-explicit canonical string
   - `OMEN key` — a short, stable, versioned identifier (`OMEN-0.1-VRQRJHQSX5NX6`)
3. **The display name** — a curated alias (`Bench Press`) hanging off the record.
   Never the identity, so it's free to be localized.

The exercise **name is an output, not an input**: you describe the movement, and
"bench press" is the label those facets resolve to.

## Try it

```bash
python omen.py --name "chin-up"
python omen.py --posture supine --implement dumbbell --pattern horizontal-push --angle incline
python omen.py --demo          # worked examples
python omen.py --name "bench press" --json
```

## Tests

```bash
pip install pytest
pytest test_omen.py -q
```

The suite is the standard's guarantees made executable: determinism (same movement →
same key), non-collision, predictable default expansion, first-class contraction type
(an eccentric-only variant is its own identity), and name round-tripping.

## The paper

`OMEN_whitepaper.docx` is the full proposal: the problem and its documented cost, the
three layers of prior art, the design principles, the facet model, the serialization
and identifier scheme, worked examples, the reference implementation, **an evaluation
with results (Section 9)**, and a governance/versioning model. `build_paper.js`
regenerates it. Figures live in `figures/`.

## Reproduce the results

Every number in Section 9 regenerates from `audit/`:

```
cd audit
python audit2.py     # coverage audit + extension queue + synonymy
python stress.py     # collision / determinism sweep (~30s)
```

## Status

Standard version **0.2**. The vocabulary now covers, for every joint it addresses, the
complete set of that joint's anatomical actions (42 movement patterns, 21 implements).
The evaluation is reported in Section 9 of the paper:

- **84.7%** of 678 resistance-training records in the Free Exercise DB encode without
  inventing a term (**91.4%** of records carrying enough information to encode at all)
- on a second corpus, **wger** (847 exercises, different naming conventions, audited with
  the *same* script), only **1.9%** of records need a term the standard lacks
- what remains uncovered is one principled category: **multi-phase Olympic lifts**
- **574** distinct source names collapse to **304** keys, exposing 106 synonym clusters
- **81%** of source names never state posture
- **0** key collisions across **6,054,048** generated records
- a **crosswalk** (`audit/omen_crosswalk.csv`) maps every audited record to its key

Still outstanding, and the reason this is 0.2 and not 1.0: the **inter-annotator study**.
Whether independent humans encode the same movement identically requires annotators. The
full study kit lives in `iaa/` so anyone can run it.

---

&copy; 2026 AbleVLabs — Carlos Abel Vivanco
