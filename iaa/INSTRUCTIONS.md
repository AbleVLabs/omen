# OMEN inter-annotator study — annotator instructions

You will be shown 30 exercise names. For each one, **describe the movement using the
facets below**. Do not try to guess a code or an ID. Just describe what the body does.

Fill in `response_template.csv` and save it as `annotator_<yourname>.csv`.

**Work independently.** Do not discuss the items with the other annotators. That is the
entire point of the study: we are measuring whether people who have read the same rules
independently arrive at the same description.

If you genuinely cannot decide, leave the cell blank rather than guessing.

## The three required facets

**posture** — the position of the body:
`standing, seated, supine, prone, kneeling, half-kneeling, bent-over, quadruped, hanging, side-lying, suspended`

**implement** — what provides the resistance:
`barbell, dumbbell, ez-bar, trap-bar, kettlebell, cable, machine, smith-machine, band, bodyweight, plate, sandbag, suspension, medicine-ball, stability-ball, sled, atlas-stone, ab-wheel, tire, climbing-rope, chain`

**pattern** — the movement itself (this is the important one):
`horizontal-push, vertical-push, horizontal-pull, vertical-pull, squat, hip-hinge, lunge, loaded-carry, elbow-flexion, elbow-extension, shoulder-abduction, shoulder-adduction, shoulder-flexion, shoulder-extension, shoulder-horizontal-abduction, shoulder-horizontal-adduction, shoulder-internal-rotation, shoulder-external-rotation, scapular-elevation, scapular-depression, scapular-retraction, scapular-protraction, wrist-flexion, wrist-extension, knee-extension, knee-flexion, hip-flexion, hip-extension, hip-abduction, hip-adduction, plantarflexion, dorsiflexion, spinal-flexion, spinal-extension, spinal-lateral-flexion, anti-extension, anti-rotation, anti-lateral-flexion, rotation`

## Optional facets

**laterality** — `bilateral` (both limbs together, the default), `unilateral` (one at a time), `alternating`
**angle** — `flat` (default), `incline`, `decline`
**grip_orientation** — `pronated` (overhand), `supinated` (underhand), `neutral`, `mixed`; leave blank if not specified

## Rules

1. **Never write a muscle.** Muscle is derived from the pattern, not entered.
2. Describe what the name says. If the name does not state the posture, use the posture
   the movement is normally performed in.
3. One pattern per movement. If a movement genuinely has two phases (a clean, a thruster),
   leave `pattern` blank and note it — those are known to be out of scope for v0.2.
