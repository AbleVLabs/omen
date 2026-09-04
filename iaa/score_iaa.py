"""Score the inter-annotator study.

Reads annotator_*.csv, reports exact-key agreement and per-facet Fleiss' kappa.
Requires REAL annotator data. Do not synthesise responses.
"""
import csv, glob, sys, collections, json
sys.path.insert(0,"../audit")
import omen

files=sorted(glob.glob("annotator_*.csv"))
if len(files)<3:
    raise SystemExit(f"Found {len(files)} annotator file(s). Need at least 3 "
                     "(annotator_<name>.csv) to compute agreement.")
print(f"annotators: {len(files)} -> {', '.join(files)}\n")

resp=collections.defaultdict(dict)   # item -> annotator -> row
for fn in files:
    for r in csv.DictReader(open(fn,encoding="utf-8")):
        resp[r["item_id"]][fn]=r

def fleiss(table):
    """table: list of dicts {category: count} per item."""
    N=len(table); n=sum(table[0].values())
    if N==0 or n<2: return float("nan")
    cats=sorted({c for row in table for c in row})
    P=[]
    for row in table:
        s=sum(row.get(c,0)**2 for c in cats)
        P.append((s-n)/(n*(n-1)))
    Pbar=sum(P)/N
    pj=[sum(row.get(c,0) for row in table)/(N*n) for c in cats]
    Pe=sum(p*p for p in pj)
    return (Pbar-Pe)/(1-Pe) if Pe<1 else 1.0

FACETS=["posture","implement","pattern","laterality","angle","grip_orientation"]
print("per-facet agreement (Fleiss' kappa):")
for f in FACETS:
    table=[]
    for item,byann in resp.items():
        c=collections.Counter((byann[a].get(f) or "").strip().lower() or "<blank>" for a in files)
        if sum(c.values())==len(files): table.append(dict(c))
    k=fleiss(table)
    print(f"  {f:18s} kappa = {k:.3f}   ({len(table)} items)")

exact=0; total=0
for item,byann in resp.items():
    keys=set()
    for a in files:
        r=byann[a]
        try:
            m=omen.Movement(posture=(r["posture"] or "standing").strip(),
                            implement=(r["implement"] or "bodyweight").strip(),
                            pattern=(r["pattern"] or "").strip(),
                            laterality=(r["laterality"] or "bilateral").strip(),
                            angle=(r["angle"] or "flat").strip(),
                            grip_orientation=((r["grip_orientation"] or "").strip() or None))
            if omen.validate(m): keys.add("INVALID"); continue
            keys.add(omen.omen_key(m))
        except Exception: keys.add("ERROR")
    total+=1
    if len(keys)==1 and "INVALID" not in keys and "ERROR" not in keys: exact+=1
print(f"\nEXACT KEY AGREEMENT: {exact}/{total} = {exact/total*100:.1f}% of movements "
      f"received an identical OMEN key from every annotator")
json.dump({"annotators":len(files),"items":total,
           "exact_key_agreement_pct":round(exact/total*100,1)},
          open("iaa_results.json","w"),indent=1)
