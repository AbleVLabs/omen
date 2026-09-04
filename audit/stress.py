import itertools, time, json, random, omen

P=sorted(omen.POSTURES); I=sorted(omen.IMPLEMENTS); PAT=sorted(omen.MOVEMENT_PATTERNS)
L=sorted(omen.LATERALITIES); A=sorted(omen.ANGLES); C=sorted(omen.CONTRACTIONS)
R=sorted(omen.RANGES); GO=sorted(omen.GRIP_ORIENTATIONS); GW=sorted(omen.GRIP_WIDTHS)

t0=time.time(); seen={}; n=0; coll=[]
for po,im,pa,la,an,co,ra in itertools.product(P,I,PAT,L,A,C,R):
    m=omen.Movement(posture=po,implement=im,pattern=pa,laterality=la,
                    angle=an,contraction=co,range=ra)
    x=omen.omen_x(m); k=omen.omen_key(m); n+=1
    if k in seen:
        if seen[k]!=x: coll.append((k,seen[k],x))
    else: seen[k]=x
t1=time.time()
print(f"records encoded          {n:,}")
print(f"distinct canonical forms {len(seen):,}")
print(f"KEY COLLISIONS           {len(coll)}")
print(f"elapsed                  {t1-t0:.1f}s")

# grip/width axis too (second sweep, defaults elsewhere)
seen2={}; n2=0; coll2=0
for po,im,pa,go,gw in itertools.product(P,I,PAT,GO,GW):
    m=omen.Movement(posture=po,implement=im,pattern=pa,grip_orientation=go,grip_width=gw)
    x=omen.omen_x(m); k=omen.omen_key(m); n2+=1
    if k in seen2 and seen2[k]!=x: coll2+=1
    seen2[k]=x
print(f"\ngrip sweep records       {n2:,}   collisions {coll2}")

# determinism: same movement encoded repeatedly, and field-order independence
random.seed(1); ok=True
for _ in range(20000):
    kw=dict(posture=random.choice(P),implement=random.choice(I),pattern=random.choice(PAT),
            laterality=random.choice(L),angle=random.choice(A),contraction=random.choice(C),
            range=random.choice(R))
    a=omen.omen_key(omen.Movement(**kw))
    b=omen.omen_key(omen.Movement(**dict(reversed(list(kw.items())))))
    if a!=b: ok=False; break
print(f"determinism / field-order independence over 20,000 records: {'PASS' if ok else 'FAIL'}")
total=n+n2
print(f"\nTOTAL distinct records encoded: {total:,}  |  total collisions: {len(coll)+coll2}")
json.dump({"sweep1":n,"distinct1":len(seen),"collisions1":len(coll),
           "sweep2":n2,"collisions2":coll2,"total":total,
           "total_collisions":len(coll)+coll2,"determinism":ok,
           "seconds":round(t1-t0,1)}, open("stress.json","w"), indent=1)
