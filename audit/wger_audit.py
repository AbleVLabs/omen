"""Second-corpus audit: the SAME mapper, run against wger.

Uses no new heuristics, so this measures the standard rather than the mapping.
"""
import json, collections, omen, mapper
ex = json.load(open("wger_exercises.json", encoding="utf-8"))
enc=gap=und=mapfail=0; gaps=collections.Counter(); by_key=collections.defaultdict(list)
for e in ex:
    s,m,_ = mapper.map_one(e)
    if s in ("encoded_scope","encoded_borderline"):
        enc+=1; by_key[omen.omen_key(m)].append(e["name"])
    elif s=="source_underspecified": und+=1
    elif _ and _.startswith("no pattern rule"): mapfail+=1
    else: gap+=1; gaps[_]+=1
n=len(ex); adj=n-und
print("="*64); print(f"OMEN v{omen.STANDARD_VERSION} SECOND-CORPUS AUDIT  ·  wger ({n} exercises)"); print("="*64)
print(f"  encodable                    {enc}  ({enc/n*100:.1f}%)")
print(f"  OMEN vocabulary gap          {gap}  ({gap/n*100:.1f}%)")
print(f"  mapper could not determine   {mapfail}  (automation limit, not OMEN)")
print(f"  source underspecified        {und}")
print(f"  coverage of encodable-info   {enc}/{adj} = {enc/adj*100:.1f}%")
print(f"  {enc} names -> {len(by_key)} keys ({len([v for v in by_key.values() if len(v)>1])} synonym clusters)")
print("\n  remaining gaps:")
for t_,c in gaps.most_common(8): print(f"    {c:3d}  {t_}")
json.dump({"corpus":"wger","n":n,"encoded":enc,"gap":gap,"mapper_undetermined":mapfail,"underspecified":und,
           "coverage_pct":round(enc/n*100,1),"coverage_adj_pct":round(enc/adj*100,1),
           "keys":len(by_key)}, open("wger_results.json","w"), indent=1)
