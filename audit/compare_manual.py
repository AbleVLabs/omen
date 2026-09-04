"""Compare Able's hand-encodings against the automated mapper.

Answers the reviewer objection: 'your coverage number came from a script you
also wrote.' Run after filling in manual_sample.csv.
"""
import csv, json, omen, mapper
ex={e["id"]:e for e in json.load(open("exercises.json",encoding="utf-8"))}
rows=[r for r in csv.DictReader(open("manual_sample.csv",encoding="utf-8"))
      if r["your_pattern"].strip()]
if not rows:
    raise SystemExit("Fill in the your_* columns of manual_sample.csv first.")
agree_pat=agree_key=0; n=len(rows); disagreements=[]
for r in rows:
    auto_s, auto_m, _ = mapper.map_one(ex[r["source_id"]])
    man = omen.Movement(posture=r["your_posture"].strip() or "standing",
                        implement=r["your_implement"].strip() or "bodyweight",
                        pattern=r["your_pattern"].strip(),
                        laterality=r["your_laterality"].strip() or "bilateral",
                        angle=r["your_angle"].strip() or "flat",
                        grip_orientation=(r["your_grip"].strip() or None))
    if omen.validate(man): 
        disagreements.append((r["source_name"],"INVALID: "+"; ".join(omen.validate(man)))); continue
    if auto_m is None:
        disagreements.append((r["source_name"],"automated mapper produced nothing")); continue
    if man.pattern==auto_m.pattern: agree_pat+=1
    if omen.omen_key(man)==omen.omen_key(auto_m): agree_key+=1
    else: disagreements.append((r["source_name"],f"manual={omen.omen_c(man)} | auto={omen.omen_c(auto_m)}"))
print(f"hand-encoded records         {n}")
print(f"pattern agreement            {agree_pat}/{n} = {agree_pat/n*100:.1f}%")
print(f"full key agreement           {agree_key}/{n} = {agree_key/n*100:.1f}%")
print("\ndisagreements (inspect these - they are the interesting cases):")
for name,why in disagreements[:20]: print(f"  {name[:36]:36s} {why}")
json.dump({"n":n,"pattern_agreement_pct":round(agree_pat/n*100,1),
           "key_agreement_pct":round(agree_key/n*100,1)},
          open("manual_validation_results.json","w"),indent=1)
