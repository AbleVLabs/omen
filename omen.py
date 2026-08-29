"""
OMEN -- Open Movement & Exercise Nomenclature.

A generative, computable naming standard for resistance-training movements.
This module is the *reference implementation* of the standard: it turns a
structured description of a movement into a canonical form and a stable
identifier, and it is the single source of truth for the controlled
vocabularies the standard defines.

THE THREE LAYERS (why this exists)
----------------------------------
A movement in OMEN is stored three ways, and keeping them separate is the whole
point -- it is how every durable naming standard (InChI for molecules, SNOMED
for clinical terms) actually works:

  1. THE FACET RECORD -- the source of truth. A movement is a bundle of
     orthogonal facets (posture, implement, laterality, movement pattern, and
     optional modifiers). Muscle worked is NOT a facet you type; it is derived
     from the movement pattern.

  2. THE CANONICAL FORM + KEY -- derived deterministically from the record.
     `omen_x()` is the fully-explicit canonical string (human-inspectable);
     `omen_key()` is a short, stable, language-neutral identifier suitable as a
     database primary key -- the equivalent of an InChIKey.

  3. THE DISPLAY NAME -- a curated label ("Bench Press") that hangs off the
     record as an alias. Never generated, never the primary key, and free to be
     localised, so the real-world vocabulary is preserved without contaminating
     identity.

The exercise NAME is therefore an output, not an input: you describe the
movement by its facets, and "bench press" is the label those facets resolve to.

    python omen.py --name "bench press"
    python omen.py --posture supine --implement barbell --pattern horizontal-push
    python omen.py --demo
"""

from __future__ import annotations

import argparse
import base64
import dataclasses
import hashlib
import json

STANDARD_VERSION = "0.1"  # embedded in every key, so identifiers are versioned


# ===========================================================================
# 1. CONTROLLED VOCABULARIES
#    The standard is only as good as its closed term lists. Every facet draws
#    from one of these; anything outside them is a validation error, which is
#    what keeps two people encoding the same movement the same way.
# ===========================================================================

POSTURES = {
    "standing", "seated", "supine", "prone", "kneeling", "half-kneeling",
    "bent-over", "quadruped", "hanging", "side-lying", "suspended",
}

IMPLEMENTS = {
    "barbell", "dumbbell", "ez-bar", "trap-bar", "kettlebell", "cable",
    "machine", "smith-machine", "band", "bodyweight", "plate", "sandbag",
    "suspension", "medicine-ball",
}

# Attachments are meaningful only for cable / machine; validated in context.
ATTACHMENTS = {
    "rope", "straight-bar", "ez-attachment", "single-handle", "lat-bar",
    "v-bar", "ankle-strap", "none",
}

GRIP_ORIENTATIONS = {"pronated", "supinated", "neutral", "mixed", "false", "hook"}
GRIP_WIDTHS = {"wide", "standard", "narrow", "close"}

LATERALITIES = {"bilateral", "unilateral", "alternating", "bilateral-independent"}

# The movement pattern is the biomechanical primitive. It IMPLIES the muscles.
# Stored as pattern -> (family, mechanic, force, primary[], secondary[]).
# mechanic and force are DERIVED attributes, never typed by the user.
MOVEMENT_PATTERNS = {
    # ---- multi-joint (compound) ----
    "horizontal-push": ("push", "compound", "push",
                        ["pectoralis-major", "anterior-deltoid", "triceps"], []),
    "vertical-push": ("push", "compound", "push",
                     ["anterior-deltoid", "triceps", "upper-pectoralis"], []),
    "horizontal-pull": ("pull", "compound", "pull",
                       ["latissimus-dorsi", "rhomboids", "mid-trapezius",
                        "posterior-deltoid"], ["biceps"]),
    "vertical-pull": ("pull", "compound", "pull",
                     ["latissimus-dorsi", "teres-major"], ["biceps"]),
    "squat": ("squat", "compound", "push",
             ["quadriceps", "gluteus-maximus"], ["adductors", "erector-spinae"]),
    "hip-hinge": ("hinge", "compound", "pull",
                 ["gluteus-maximus", "hamstrings", "erector-spinae"], []),
    "lunge": ("lunge", "compound", "push",
             ["quadriceps", "gluteus-maximus"], ["hamstrings"]),
    "loaded-carry": ("carry", "compound", "static",
                    ["trapezius", "forearm-flexors", "core"], ["erector-spinae"]),
    # ---- single-joint (isolation), upper ----
    "elbow-flexion": ("curl", "isolation", "pull",
                     ["biceps", "brachialis"], ["brachioradialis"]),
    "elbow-extension": ("extension", "isolation", "push", ["triceps"], []),
    "shoulder-abduction": ("raise", "isolation", "push", ["lateral-deltoid"], []),
    "shoulder-flexion": ("raise", "isolation", "push", ["anterior-deltoid"], []),
    "shoulder-horizontal-abduction": ("raise", "isolation", "pull",
                                     ["posterior-deltoid"], ["rhomboids"]),
    "wrist-flexion": ("curl", "isolation", "pull", ["forearm-flexors"], []),
    "wrist-extension": ("extension", "isolation", "push", ["forearm-extensors"], []),
    # ---- single-joint (isolation), lower ----
    "knee-extension": ("extension", "isolation", "push", ["quadriceps"], []),
    "knee-flexion": ("curl", "isolation", "pull", ["hamstrings"], []),
    "hip-extension": ("extension", "isolation", "pull", ["gluteus-maximus"], []),
    "hip-abduction": ("abduction", "isolation", "push", ["gluteus-medius"], []),
    "hip-adduction": ("adduction", "isolation", "pull", ["adductors"], []),
    "plantarflexion": ("raise", "isolation", "push",
                      ["gastrocnemius", "soleus"], []),
    # ---- core / anti-movement ----
    "spinal-flexion": ("core", "isolation", "pull", ["rectus-abdominis"], []),
    "anti-extension": ("core", "isolation", "static", ["rectus-abdominis"], []),
    "anti-rotation": ("core", "isolation", "static", ["obliques"], []),
    "anti-lateral-flexion": ("core", "isolation", "static", ["obliques"], []),
    "rotation": ("core", "isolation", "pull", ["obliques"], []),
}

ANGLES = {"flat", "incline", "decline", "horizontal", "vertical"}
CONTRACTIONS = {
    "dynamic", "eccentric-only", "concentric-only", "isometric", "plyometric",
}
RANGES = {"full", "partial", "deficit", "top-range", "bottom-range", "paused"}

# Global defaults for optional facets. The compact form omits anything equal to
# its default; the canonical form makes every field explicit again.
DEFAULTS = {
    "attachment": "none",
    "grip_orientation": None,   # None => derive per pattern (see PATTERN_GRIP)
    "grip_width": "standard",
    "laterality": "bilateral",
    "angle": "flat",
    "contraction": "dynamic",
    "range": "full",
}

# When grip orientation is unstated, the pattern implies the natural default.
PATTERN_GRIP = {
    "elbow-flexion": "supinated",
    "vertical-pull": "pronated",
    "horizontal-pull": "pronated",
    "elbow-extension": "pronated",
    "horizontal-push": "pronated",
    "vertical-push": "pronated",
}


# ===========================================================================
# 2. THE FACET RECORD
# ===========================================================================

@dataclasses.dataclass
class Movement:
    """The source-of-truth facet record for one movement.

    Required facets: posture, implement, pattern. Laterality has a global
    default. Everything else is an optional modifier. Muscles, mechanic and
    force are NOT stored -- they are derived on demand from `pattern`.
    """
    posture: str
    implement: str
    pattern: str
    laterality: str = "bilateral"
    grip_orientation: str | None = None
    grip_width: str = "standard"
    attachment: str = "none"
    angle: str = "flat"
    contraction: str = "dynamic"
    range: str = "full"

    # -- derived properties (movement pattern is the primitive) --------------
    @property
    def family(self):
        return MOVEMENT_PATTERNS[self.pattern][0]

    @property
    def mechanic(self):
        return MOVEMENT_PATTERNS[self.pattern][1]

    @property
    def force(self):
        return MOVEMENT_PATTERNS[self.pattern][2]

    @property
    def primary_muscles(self):
        return list(MOVEMENT_PATTERNS[self.pattern][3])

    @property
    def secondary_muscles(self):
        return list(MOVEMENT_PATTERNS[self.pattern][4])

    @property
    def resolved_grip(self):
        """Grip orientation after defaults: explicit value, else the pattern's
        natural grip, else neutral."""
        if self.grip_orientation:
            return self.grip_orientation
        return PATTERN_GRIP.get(self.pattern, "neutral")


# ===========================================================================
# 3. VALIDATION
# ===========================================================================

def validate(m: Movement) -> list[str]:
    """Return a list of human-readable problems. Empty list == valid."""
    errs = []
    if m.posture not in POSTURES:
        errs.append(f"posture '{m.posture}' not in the controlled vocabulary")
    if m.implement not in IMPLEMENTS:
        errs.append(f"implement '{m.implement}' not in the controlled vocabulary")
    if m.pattern not in MOVEMENT_PATTERNS:
        errs.append(f"pattern '{m.pattern}' not in the controlled vocabulary")
    if m.laterality not in LATERALITIES:
        errs.append(f"laterality '{m.laterality}' invalid")
    if m.grip_orientation and m.grip_orientation not in GRIP_ORIENTATIONS:
        errs.append(f"grip '{m.grip_orientation}' invalid")
    if m.grip_width not in GRIP_WIDTHS:
        errs.append(f"grip width '{m.grip_width}' invalid")
    if m.attachment not in ATTACHMENTS:
        errs.append(f"attachment '{m.attachment}' invalid")
    if m.attachment != "none" and m.implement not in {"cable", "machine"}:
        errs.append("attachment is only meaningful with a cable or machine")
    if m.angle not in ANGLES:
        errs.append(f"angle '{m.angle}' invalid")
    if m.contraction not in CONTRACTIONS:
        errs.append(f"contraction '{m.contraction}' invalid")
    if m.range not in RANGES:
        errs.append(f"range '{m.range}' invalid")
    return errs


# ===========================================================================
# 4. CANONICAL FORMS AND THE STABLE KEY
#    The citation order is FIXED. This is the deterministic serialization that
#    makes the same movement always produce the same string and the same key.
# ===========================================================================

# The one true field order. General context -> specific execution.
CITATION_ORDER = [
    "posture", "implement", "attachment", "grip_orientation", "grip_width",
    "laterality", "pattern", "angle", "contraction", "range",
]


def omen_x(m: Movement) -> str:
    """OMEN-X: the fully-explicit canonical string. Every facet present, in
    citation order, grip resolved. This is what the key is hashed from, so it
    must be stable and lossless."""
    fields = {
        "posture": m.posture,
        "implement": m.implement,
        "attachment": m.attachment,
        "grip_orientation": m.resolved_grip,
        "grip_width": m.grip_width,
        "laterality": m.laterality,
        "pattern": m.pattern,
        "angle": m.angle,
        "contraction": m.contraction,
        "range": m.range,
    }
    return "|".join(f"{k}={fields[k]}" for k in CITATION_ORDER)


def omen_c(m: Movement) -> str:
    """OMEN-C: the compact human form. Only facets that differ from a default
    survive, in citation order, space-joined. This is the readable rendering --
    'incline dumbbell unilateral horizontal-push'."""
    parts = []
    if m.angle != DEFAULTS["angle"]:
        parts.append(m.angle)
    if m.posture != _implied_posture(m):
        parts.append(m.posture)
    if m.attachment != "none":
        parts.append(m.attachment)
    if m.implement != "bodyweight":
        parts.append(m.implement)
    if m.grip_orientation and m.grip_orientation != PATTERN_GRIP.get(m.pattern):
        parts.append(m.grip_orientation)
    if m.grip_width != "standard":
        parts.append(m.grip_width + "-grip")
    if m.laterality != "bilateral":
        parts.append(m.laterality)
    parts.append(m.pattern)
    if m.contraction != "dynamic":
        parts.append(m.contraction)
    if m.range != "full":
        parts.append(m.range)
    return " ".join(parts)


def _implied_posture(m: Movement) -> str:
    """Posture that a pattern assumes by default, so the compact form can omit
    it when it's the obvious one (a squat is standing; a bench press supine)."""
    implied = {
        "squat": "standing", "hip-hinge": "standing", "lunge": "standing",
        "vertical-push": "standing", "vertical-pull": "hanging",
        "plantarflexion": "standing", "loaded-carry": "standing",
        "horizontal-push": "supine",
    }
    return implied.get(m.pattern, m.posture)


def omen_key(m: Movement) -> str:
    """OMEN key: a short, stable, language-neutral identifier derived from the
    canonical string. Versioned, so identifiers never silently change meaning
    across editions of the standard. The database primary key."""
    digest = hashlib.blake2b(omen_x(m).encode("utf-8"), digest_size=8).digest()
    code = base64.b32encode(digest).decode("ascii").rstrip("=")
    return f"OMEN-{STANDARD_VERSION}-{code}"


def record(m: Movement) -> dict:
    """The full structured record: facets + everything derived + both canonical
    forms + the key + preferred display name. This is what a database stores."""
    return {
        "facets": {k: getattr(m, k) for k in [
            "posture", "implement", "attachment", "grip_orientation",
            "grip_width", "laterality", "pattern", "angle", "contraction",
            "range"]},
        "derived": {
            "family": m.family,
            "mechanic": m.mechanic,
            "force": m.force,
            "primary_muscles": m.primary_muscles,
            "secondary_muscles": m.secondary_muscles,
            "grip_resolved": m.resolved_grip,
        },
        "omen_c": omen_c(m),
        "omen_x": omen_x(m),
        "omen_key": omen_key(m),
        "display_name": display_name(m),
    }


# ===========================================================================
# 5. THE ALIAS TABLE  (display names <-> facet bundles)
#    Named exercises are curated aliases, not generated strings. This is the
#    presentation layer: it maps the real-world vocabulary onto canonical
#    records both ways.
# ===========================================================================

# name -> the facet overrides that define it (the rest fall to defaults).
ALIASES = {
    "back squat": dict(posture="standing", implement="barbell", pattern="squat"),
    "front squat": dict(posture="standing", implement="barbell", pattern="squat",
                        grip_orientation="supinated"),
    "bench press": dict(posture="supine", implement="barbell",
                        pattern="horizontal-push"),
    "incline dumbbell press": dict(posture="supine", implement="dumbbell",
                                   pattern="horizontal-push", angle="incline"),
    "overhead press": dict(posture="standing", implement="barbell",
                           pattern="vertical-push"),
    "romanian deadlift": dict(posture="standing", implement="barbell",
                              pattern="hip-hinge"),
    "barbell row": dict(posture="bent-over", implement="barbell",
                        pattern="horizontal-pull"),
    "pull-up": dict(posture="hanging", implement="bodyweight",
                    pattern="vertical-pull", grip_orientation="pronated"),
    "chin-up": dict(posture="hanging", implement="bodyweight",
                    pattern="vertical-pull", grip_orientation="supinated"),
    "lat pulldown": dict(posture="seated", implement="cable", attachment="lat-bar",
                         pattern="vertical-pull"),
    "dumbbell lateral raise": dict(posture="standing", implement="dumbbell",
                                   pattern="shoulder-abduction"),
    "biceps curl": dict(posture="standing", implement="dumbbell",
                        pattern="elbow-flexion"),
    "triceps pushdown": dict(posture="standing", implement="cable",
                             attachment="rope", pattern="elbow-extension"),
    "leg extension": dict(posture="seated", implement="machine",
                          pattern="knee-extension"),
    "seated leg curl": dict(posture="seated", implement="machine",
                            pattern="knee-flexion"),
    "standing calf raise": dict(posture="standing", implement="machine",
                                pattern="plantarflexion"),
    "plank": dict(posture="prone", implement="bodyweight",
                  pattern="anti-extension", contraction="isometric"),
}

# Reverse index: canonical key -> preferred display name. Built once.
_KEY_TO_NAME = {}


def _build_reverse_index():
    for name, facets in ALIASES.items():
        m = Movement(**facets)
        _KEY_TO_NAME.setdefault(omen_key(m), name)


def from_name(name: str) -> Movement:
    """Build a canonical record from a colloquial name via the alias table.
    Defaults fill everything the alias leaves unsaid."""
    key = name.strip().lower()
    if key not in ALIASES:
        raise KeyError(f"'{name}' is not in the alias table "
                       f"({len(ALIASES)} names known)")
    return Movement(**ALIASES[key])


def display_name(m: Movement) -> str:
    """Preferred display name for a record, or its compact form if unnamed."""
    if not _KEY_TO_NAME:
        _build_reverse_index()
    return _KEY_TO_NAME.get(omen_key(m), omen_c(m))


# ===========================================================================
# 6. COMMAND LINE
# ===========================================================================

def _print_record(m: Movement):
    errs = validate(m)
    if errs:
        print("  INVALID movement:")
        for e in errs:
            print(f"    - {e}")
        return
    r = record(m)
    print(f"\n  {r['display_name'].upper()}")
    print("  " + "-" * 58)
    print(f"  OMEN-C (compact)   {r['omen_c']}")
    print(f"  OMEN-X (canonical) {r['omen_x']}")
    print(f"  OMEN key           {r['omen_key']}")
    d = r["derived"]
    print(f"  family / mechanic  {d['family']} / {d['mechanic']}  ({d['force']})")
    print(f"  primary muscles    {', '.join(d['primary_muscles'])}")
    if d["secondary_muscles"]:
        print(f"  secondary muscles  {', '.join(d['secondary_muscles'])}")
    print()


def _demo():
    print("\n  OMEN reference encoder -- worked examples")
    print("  " + "=" * 58)
    for name in ["back squat", "bench press", "incline dumbbell press",
                 "pull-up", "chin-up", "triceps pushdown", "biceps curl",
                 "romanian deadlift", "plank"]:
        _print_record(from_name(name))
    # a facet-built movement with no alias -> compact form becomes its name
    print("  A movement with no curated name (its OMEN-C IS the label):")
    _print_record(Movement(posture="seated", implement="cable",
                            attachment="single-handle", pattern="horizontal-pull",
                            laterality="unilateral"))


def main(argv=None):
    p = argparse.ArgumentParser(description="OMEN reference encoder.")
    p.add_argument("--name", help="encode a known exercise by colloquial name")
    p.add_argument("--posture")
    p.add_argument("--implement")
    p.add_argument("--pattern")
    p.add_argument("--laterality", default="bilateral")
    p.add_argument("--grip", dest="grip_orientation")
    p.add_argument("--attachment", default="none")
    p.add_argument("--angle", default="flat")
    p.add_argument("--contraction", default="dynamic")
    p.add_argument("--demo", action="store_true", help="print worked examples")
    p.add_argument("--json", action="store_true", help="emit the full record as JSON")
    args = p.parse_args(argv)

    if args.demo:
        _demo()
        return
    if args.name:
        try:
            m = from_name(args.name)
        except KeyError as e:
            print(f"  {e}")
            return
    elif args.posture and args.implement and args.pattern:
        m = Movement(posture=args.posture, implement=args.implement,
                     pattern=args.pattern, laterality=args.laterality,
                     grip_orientation=args.grip_orientation,
                     attachment=args.attachment, angle=args.angle,
                     contraction=args.contraction)
    else:
        p.print_help()
        return

    if args.json:
        errs = validate(m)
        print(json.dumps(record(m) if not errs else {"errors": errs}, indent=2))
    else:
        _print_record(m)


if __name__ == "__main__":
    main()
