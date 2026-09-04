import json, collections, importlib, omen, mapper
importlib.reload(mapper)
ex = json.load(open("exercises.json", encoding="utf-8"))
SCOPE = {"strength","powerlifting","olympic weightlifting","strongman"}
recs = [e for e in ex if e.get("category") in SCOPE]

enc=0; vocab_gap=0; under=0
gaps=collections.Counter(); gap_ex=collections.defaultdict(list)
by_key=collections.defaultdict(list); xk={}; coll=0; pst=collections.Counter()
for e in recs:
    s,m,d = mapper.map_one(e)
    if s=="encoded_scope":
        enc+=1; k=omen.omen_key(m); x=omen.omen_x(m)
        if k in xk and xk[k]!=x: coll+=1
        xk[k]=x; by_key[k].append(e["name"]); pst[d]+=1
    elif s=="source_underspecified": under+=1
    else:
        vocab_gap+=1; gaps[d]+=1
        if len(gap_ex[d])<3: gap_ex[d].append(e["name"])

den_all=len(recs); den_adj=den_all-under
print("="*68)
print("OMEN v0.1 COVERAGE AUDIT  ·  Free Exercise DB (876 records)")
print("="*68)
print(f"Out of scope by design (stretching, cardio)   {len(ex)-len(recs)}")
print(f"Resistance-training records                   {den_all}")
print(f"  encodable in OMEN v0.1                      {enc}")
print(f"  OMEN vocabulary gap (needs new term)        {vocab_gap}")
print(f"  source record underspecified (not OMEN)     {under}")
print()
print(f"COVERAGE, all resistance records      {enc}/{den_all} = {enc/den_all*100:.1f}%")
print(f"COVERAGE, records w/ sufficient info  {enc}/{den_adj} = {enc/den_adj*100:.1f}%")
print()
print(f"Synonymy   {enc} names -> {len(by_key)} unique keys "
      f"({len([v for v in by_key.values() if len(v)>1])} synonym clusters)")
print(f"Key collisions (distinct records, same key)   {coll}")
print(f"Posture unstated in source name  {pst['posture_inferred']}/{enc} "
      f"({pst['posture_inferred']/enc*100:.0f}% underspecified)")
print()
print("--- v0.2 EXTENSION QUEUE (vocabulary gaps only) ---")
for t,c in gaps.most_common():
    print(f"  {c:3d}  {t}\n         e.g. {', '.join(gap_ex[t][:3])}")
json.dump({"total":len(ex),"out_of_scope":len(ex)-len(recs),"resistance":den_all,
 "encoded":enc,"vocab_gap":vocab_gap,"underspecified":under,
 "cov_all":round(enc/den_all*100,1),"cov_adj":round(enc/den_adj*100,1),
 "unique_keys":len(by_key),"clusters":len([v for v in by_key.values() if len(v)>1]),
 "collisions":coll,"posture_inferred_pct":round(pst['posture_inferred']/enc*100),
 "gaps":gaps.most_common()}, open("results.json","w"), indent=1)
