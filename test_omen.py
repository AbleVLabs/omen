"""
Tests for the OMEN reference encoder.

These are also the standard's correctness guarantees made executable: the same
movement always produces the same key (determinism), different movements never
collide, defaults expand predictably, and a colloquial name round-trips to its
canonical record and back to its name.
"""

import omen
from omen import Movement, omen_x, omen_c, omen_key, from_name, display_name, validate


# ---------------------------------------------------------------------------
# determinism and identity
# ---------------------------------------------------------------------------

def test_the_same_movement_always_gets_the_same_key():
    a = from_name("bench press")
    b = Movement(posture="supine", implement="barbell", pattern="horizontal-push")
    assert omen_key(a) == omen_key(b)          # name and facets agree
    assert omen_x(a) == omen_x(b)


def test_the_key_is_stable_across_field_order():
    # Building with fields in a different call order must not change identity.
    a = Movement(pattern="squat", implement="barbell", posture="standing")
    b = Movement(posture="standing", implement="barbell", pattern="squat")
    assert omen_key(a) == omen_key(b)


def test_grip_distinguishes_pullup_from_chinup():
    pull = from_name("pull-up")      # pronated
    chin = from_name("chin-up")      # supinated
    assert omen_key(pull) != omen_key(chin)
    assert pull.resolved_grip == "pronated"
    assert chin.resolved_grip == "supinated"


def test_laterality_changes_identity():
    two = Movement(posture="seated", implement="cable", pattern="horizontal-pull")
    one = Movement(posture="seated", implement="cable", pattern="horizontal-pull",
                   laterality="unilateral")
    assert omen_key(two) != omen_key(one)


def test_angle_changes_identity():
    flat = Movement(posture="supine", implement="dumbbell",
                    pattern="horizontal-push")
    incline = Movement(posture="supine", implement="dumbbell",
                       pattern="horizontal-push", angle="incline")
    assert omen_key(flat) != omen_key(incline)


def test_contraction_is_first_class_and_changes_identity():
    # The eccentric-nomenclature gap: an eccentric-only variant is its own thing.
    normal = Movement(posture="prone", implement="bodyweight",
                      pattern="knee-flexion")
    nordic = Movement(posture="prone", implement="bodyweight",
                      pattern="knee-flexion", contraction="eccentric-only")
    assert omen_key(normal) != omen_key(nordic)


# ---------------------------------------------------------------------------
# no collisions across the whole alias table
# ---------------------------------------------------------------------------

def test_all_named_exercises_have_distinct_keys():
    keys = [omen_key(from_name(n)) for n in omen.ALIASES]
    assert len(keys) == len(set(keys)), "two different exercises share a key"


def test_key_has_version_prefix():
    k = omen_key(from_name("back squat"))
    assert k.startswith(f"OMEN-{omen.STANDARD_VERSION}-")


# ---------------------------------------------------------------------------
# derivation: muscle and mechanic come from the pattern, not from input
# ---------------------------------------------------------------------------

def test_muscles_are_derived_from_movement_pattern():
    bench = from_name("bench press")
    assert "pectoralis-major" in bench.primary_muscles
    assert bench.mechanic == "compound"
    assert bench.force == "push"


def test_isolation_is_derived_for_single_joint():
    curl = from_name("biceps curl")
    assert curl.mechanic == "isolation"
    assert "biceps" in curl.primary_muscles


# ---------------------------------------------------------------------------
# defaults and the compact form
# ---------------------------------------------------------------------------

def test_compact_form_omits_defaults():
    # A flat bilateral dynamic full-range bench press is just "... press".
    bench = from_name("bench press")
    c = omen_c(bench)
    assert "bilateral" not in c        # default, omitted
    assert "dynamic" not in c          # default, omitted
    assert "horizontal-push" in c


def test_compact_form_keeps_overrides():
    m = Movement(posture="supine", implement="dumbbell",
                 pattern="horizontal-push", angle="incline",
                 laterality="unilateral")
    c = omen_c(m)
    assert "incline" in c
    assert "unilateral" in c


# ---------------------------------------------------------------------------
# round-trip: name -> record -> name
# ---------------------------------------------------------------------------

def test_name_round_trips_through_the_record():
    for name in omen.ALIASES:
        m = from_name(name)
        assert display_name(m) == name


def test_unnamed_movement_falls_back_to_compact_form():
    m = Movement(posture="seated", implement="cable", attachment="single-handle",
                 pattern="horizontal-pull", laterality="unilateral")
    # not in the alias table, so its display name is its compact string
    assert display_name(m) == omen_c(m)
    assert "unilateral" in display_name(m)


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------

def test_valid_movement_has_no_errors():
    assert validate(from_name("back squat")) == []


def test_unknown_token_is_rejected():
    m = Movement(posture="floating", implement="barbell", pattern="squat")
    errs = validate(m)
    assert any("posture" in e for e in errs)


def test_attachment_requires_cable_or_machine():
    m = Movement(posture="standing", implement="barbell", pattern="squat",
                 attachment="rope")
    errs = validate(m)
    assert any("attachment" in e for e in errs)


def test_canonical_string_uses_fixed_citation_order():
    m = from_name("bench press")
    x = omen_x(m)
    # posture must appear before implement before pattern in the string
    assert x.index("posture=") < x.index("implement=") < x.index("pattern=")
