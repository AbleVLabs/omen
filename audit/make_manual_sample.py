"""Draw a reproducible random sample for hand-encoding, to de-bias the
automated coverage figure. Fixed seed so anyone can regenerate the same rows."""
import json, csv, random
random.seed(20260904)
SCOPE={"strength","powerlifting","olympic weightlifting","strongman"}
ex=[e for e in json.load(open("exercises.json",encoding="utf-8")) if e.get("category") in SCOPE]
sample=random.sample(ex,50)
with open("manual_sample.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f)
    w.writerow(["source_id","source_name","db_equipment","db_primary_muscles",
                "your_posture","your_implement","your_pattern","your_laterality",
                "your_angle","your_grip","notes"])
    for e in sample:
        w.writerow([e["id"],e["name"],e.get("equipment") or "",
                    ";".join(e.get("primaryMuscles") or []),"","","","","","",""])
print("wrote manual_sample.csv (50 rows) - fill in the your_* columns by hand")
