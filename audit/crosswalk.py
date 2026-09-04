"""Emit an OMEN crosswalk: every Free Exercise DB record -> its OMEN key.

This is the directly usable artifact of the audit: a mapping any application can
adopt to give its exercises a shared, stable identifier.
"""
import json, csv, collections, omen, mapper

SCOPE = {"strength", "powerlifting", "olympic weightlifting", "strongman"}
ex = json.load(open("exercises.json", encoding="utf-8"))

rows, unmapped = [], []
for e in ex:
    if e.get("category") not in SCOPE:
        continue
    status, m, _ = mapper.map_one(e)
    if status == "encoded_scope":
        rows.append({
            "source_db": "free-exercise-db",
            "source_id": e["id"],
            "source_name": e["name"],
            "omen_key": omen.omen_key(m),
            "omen_c": omen.omen_c(m),
            "omen_x": omen.omen_x(m),
            "posture": m.posture, "implement": m.implement, "pattern": m.pattern,
            "laterality": m.laterality, "angle": m.angle,
            "mechanic": m.mechanic,
            "primary_muscles": ";".join(m.primary_muscles),
        })
    else:
        unmapped.append({"source_id": e["id"], "source_name": e["name"], "reason": status})

with open("omen_crosswalk.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
json.dump({"standard_version": omen.STANDARD_VERSION,
           "source": "free-exercise-db (public domain)",
           "mapped": len(rows), "unmapped": len(unmapped),
           "distinct_keys": len({r["omen_key"] for r in rows}),
           "crosswalk": rows, "unmapped_records": unmapped},
          open("omen_crosswalk.json", "w", encoding="utf-8"), indent=1)

clusters = collections.Counter(r["omen_key"] for r in rows)
multi = {k: v for k, v in clusters.items() if v > 1}
print(f"mapped records   {len(rows)}")
print(f"distinct keys    {len(clusters)}")
print(f"synonym clusters {len(multi)}")
print(f"unmapped         {len(unmapped)}")
print("\nsample rows:")
for r in rows[:4]:
    print(f"  {r['source_name'][:34]:34s} -> {r['omen_key']}  ({r['omen_c']})")
