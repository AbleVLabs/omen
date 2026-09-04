"""Map Free Exercise DB records onto OMEN v0.1 facets, recording every gap."""
import re, json, collections
import omen

IN_SCOPE = {"strength", "powerlifting", "olympic weightlifting", "strongman"}
OUT_SCOPE = {"stretching", "cardio"}          # explicitly out of scope (Sec.10)
BORDERLINE = {"plyometrics"}

EQUIP = {
    "barbell": "barbell", "dumbbell": "dumbbell", "cable": "cable",
    "machine": "machine", "kettlebells": "kettlebell", "bands": "band",
    "body only": "bodyweight", "e-z curl bar": "ez-bar",
    "medicine ball": "medicine-ball",
}
EQUIP_GAP = {"foam roll": "foam-roller"}
EQUIP["exercise ball"] = "stability-ball"
NAME_IMPLEMENT = [("smith", "smith-machine"), ("trap bar", "trap-bar"),
                  ("hex bar", "trap-bar"), ("sandbag", "sandbag"),
                  ("suspension", "suspension"), ("trx", "suspension"),
                  ("plate", "plate"), ("kettlebell", "kettlebell"),
                  ("bodyweight", "bodyweight"), ("body weight", "bodyweight"),
                  ("atlas stone", "atlas-stone"), ("ab roller", "ab-wheel"),
                  ("ab wheel", "ab-wheel"), ("sled", "sled"), ("tire", "tire"),
                  ("rope climb", "climbing-rope"), ("chain", "chain"),
                  ("exercise ball", "stability-ball"), ("stability ball", "stability-ball"),
                  ("swiss ball", "stability-ball"),
                  ("barbell", "barbell"), ("dumbbell", "dumbbell"),
                  ("cable", "cable"), ("machine", "machine"), ("band", "band")]

# Implements OMEN v0.1 has no term for (genuine vocabulary gaps).
MISSING_IMPLEMENTS = [
    (r"foam roll", "foam-roller"), (r"\bbag\b", "heavy-bag"),
]

# Movements OMEN v0.1 has no pattern for -> the extension queue.
KNOWN_GAPS = [
    (r"\bclean\b|\bsnatch\b|\bjerk\b|muscle up|muscle-up", "olympic / multi-phase lift"),
    (r"thruster|burpee|turkish", "complex multi-pattern"),
    (r"wrist roller|finger|gripper", "grip / finger flexion"),
]
# Ordered, specific first. (regex, pattern)
RULES = [
    (r"side plank|suitcase", "anti-lateral-flexion"),
    (r"side bend|lateral flexion", "spinal-lateral-flexion"),
    (r"pallof", "anti-rotation"),
    (r"\bplank\b|ab wheel|rollout|hollow", "anti-extension"),
    (r"russian twist|wood ?chop|twist\b", "rotation"),
    (r"leg raise|knee raise|leg lift|hip flexion", "hip-flexion"),
    (r"crunch|sit-?up|v-?up|toe touch|jackknife", "spinal-flexion"),
    (r"back extension|hyperextension|superman", "spinal-extension"),
    (r"\bneck\b", "cervical-flexion"),
    (r"carry|farmer", "loaded-carry"),
    (r"tibialis|dorsiflex", "dorsiflexion"),
    (r"calf raise|calf press|heel raise|toe press", "plantarflexion"),
    (r"leg extension|knee extension", "knee-extension"),
    (r"leg curl|hamstring curl|lying curl", "knee-flexion"),
    (r"hip thrust|glute bridge|glute kickback|donkey kick|glute-ham|pull-?through", "hip-extension"),
    (r"abduct|abductor", "hip-abduction"),
    (r"adduct|adductor", "hip-adduction"),
    (r"lunge|split squat|step-?up|bulgarian", "lunge"),
    (r"squat|leg press|hack ", "squat"),
    (r"deadlift|romanian|rdl|good morning|swing|hinge", "hip-hinge"),
    (r"external rotation", "shoulder-external-rotation"),
    (r"internal rotation", "shoulder-internal-rotation"),
    (r"shrug|upright row", "scapular-elevation"),
    (r"pullover", "shoulder-extension"),
    (r"rear delt|reverse fly|rear lateral|face pull|reverse pec", "shoulder-horizontal-abduction"),
    (r"\bfly|\bflye|pec deck|pec-deck", "shoulder-horizontal-adduction"),
    (r"lateral raise|side lateral|side raise", "shoulder-abduction"),
    (r"front raise", "shoulder-flexion"),
    (r"pull-?up|chin-?up|pulldown|pull down|lat pull", "vertical-pull"),
    (r"\brow\b|rowing", "horizontal-pull"),
    (r"shoulder press|overhead press|military press|push press|arnold|handstand push", "vertical-push"),
    (r"bench press|chest press|push-?up|pushup|floor press|\bdip\b", "horizontal-push"),
    (r"wrist curl", "wrist-flexion"),
    (r"reverse wrist|wrist extension", "wrist-extension"),
    (r"pushdown|push-?down|skull|french press|triceps ext|tricep ext|kick-?back", "elbow-extension"),
    (r"\bcurl\b", "elbow-flexion"),
    (r"\bpress\b", "vertical-push"),
    (r"extension", "elbow-extension"),
]
MUSCLE_FALLBACK = {
    "biceps": "elbow-flexion", "triceps": "elbow-extension",
    "quadriceps": "squat", "hamstrings": "knee-flexion", "glutes": "hip-extension",
    "calves": "plantarflexion", "abdominals": "spinal-flexion",
    "lats": "vertical-pull", "middle back": "horizontal-pull",
    "lower back": "hip-hinge", "chest": "horizontal-push",
    "shoulders": "vertical-push", "forearms": "wrist-flexion",
    "abductors": "hip-abduction", "adductors": "hip-adduction",
    "traps": "scapular-elevation", "neck": "cervical-flexion",
}
MUSCLE_GAP = {}
POSTURE_TOK = [("seated", "seated"), ("sitting", "seated"), ("standing", "standing"),
               ("lying", "supine"), ("supine", "supine"), ("prone", "prone"),
               ("kneeling", "kneeling"), ("bent-over", "bent-over"), ("bent over", "bent-over"),
               ("hanging", "hanging"), ("side-lying", "side-lying")]
PATTERN_POSTURE = {  # implied posture when the source name doesn't say
    "horizontal-push": "supine", "vertical-push": "standing", "horizontal-pull": "bent-over",
    "vertical-pull": "hanging", "squat": "standing", "hip-hinge": "standing",
    "lunge": "standing", "loaded-carry": "standing", "elbow-flexion": "standing",
    "elbow-extension": "standing", "shoulder-abduction": "standing",
    "shoulder-flexion": "standing", "shoulder-horizontal-abduction": "bent-over",
    "wrist-flexion": "seated", "wrist-extension": "seated", "knee-extension": "seated",
    "knee-flexion": "prone", "hip-extension": "supine", "hip-abduction": "seated",
    "hip-adduction": "seated", "plantarflexion": "standing", "spinal-flexion": "supine",
    "anti-extension": "prone", "anti-rotation": "standing",
    "anti-lateral-flexion": "side-lying", "rotation": "standing",
}

def map_one(ex):
    """-> (status, Movement|None, detail)"""
    name = ex["name"].lower()
    cat = ex.get("category")
    if cat in OUT_SCOPE:
        return "out_of_scope", None, cat

    # implement
    eq = ex.get("equipment")
    imp = EQUIP.get(eq)
    if imp is None and eq in EQUIP_GAP:
        return "gap_implement", None, EQUIP_GAP[eq]
    if imp is None:
        for tok, val in NAME_IMPLEMENT:
            if tok in name:
                imp = val; break
    if imp is None:
        for rx, label in MISSING_IMPLEMENTS:
            if re.search(rx, name):
                return "gap_implement", None, label
    if imp is None:
        if eq in (None, "other"):
            return "source_underspecified", None, f"equipment='{eq}', name discloses no implement"
        return "gap_implement", None, str(eq)

    # explicit known gaps first
    for rx, label in KNOWN_GAPS:
        if re.search(rx, name):
            return "gap_pattern", None, label

    pat = None
    for rx, p in RULES:
        if re.search(rx, name):
            pat = p; break
    if pat is None:
        prim = (ex.get("primaryMuscles") or [None])[0]
        if prim in MUSCLE_GAP:
            return "gap_pattern", None, MUSCLE_GAP[prim]
        pat = MUSCLE_FALLBACK.get(prim)
        if pat and prim == "quadriceps" and ex.get("mechanic") == "isolation":
            pat = "knee-extension"
        if pat and prim == "shoulders" and ex.get("mechanic") == "isolation":
            pat = "shoulder-abduction"
    if pat is None:
        return "gap_pattern", None, f"no pattern rule (primary={ex.get('primaryMuscles')})"

    # posture
    posture, stated = None, False
    for tok, val in POSTURE_TOK:
        if tok in name:
            posture, stated = val, True; break
    if posture is None:
        posture = PATTERN_POSTURE.get(pat, "standing")

    # modifiers
    angle = "incline" if "incline" in name else "decline" if "decline" in name else "flat"
    lat = ("unilateral" if re.search(r"one-?arm|single-?arm|one-?leg|single-?leg|unilateral", name)
           else "alternating" if "alternat" in name else "bilateral")
    grip_o = ("supinated" if re.search(r"reverse grip|supinated|underhand", name)
              else "neutral" if re.search(r"neutral|hammer", name)
              else "pronated" if "overhand" in name else None)
    grip_w = ("wide" if "wide" in name else "close" if "close" in name
              else "narrow" if "narrow" in name else "standard")
    att = "none"
    if imp in ("cable", "machine"):
        att = ("rope" if "rope" in name else "straight-bar" if "straight bar" in name
               else "v-bar" if "v-bar" in name else "lat-bar" if "lat bar" in name else "none")
    contr = ("plyometric" if cat == "plyometrics"
             else "isometric" if re.search(r"\bplank\b|isometric|\bhold\b", name)
             else "eccentric-only" if re.search(r"eccentric|negative", name) else "dynamic")
    rng = ("partial" if "partial" in name else "paused" if "paus" in name
           else "deficit" if "deficit" in name else "full")

    m = omen.Movement(posture=posture, implement=imp, pattern=pat, laterality=lat,
                      grip_orientation=grip_o, grip_width=grip_w, attachment=att,
                      angle=angle, contraction=contr, range=rng)
    errs = omen.validate(m)
    if errs:
        return "invalid", None, "; ".join(errs)
    return ("encoded_scope" if cat in IN_SCOPE else "encoded_borderline"), m, ("posture_stated" if stated else "posture_inferred")
