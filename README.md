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
and identifier scheme, worked examples, the reference implementation, an evaluation
protocol (inter-annotator agreement), and a governance/versioning model. `build_paper.js`
regenerates it.

## Status

Working draft, standard version **0.1**. The evaluation in the paper is a design, not
yet a result — the inter-annotator study and coverage audit come next, and drive v1.0.

---

&copy; 2026 AbleVLabs — Carlos Abel Vivanco
