import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
INK="#1a1a1a"; MUTE="#5a5a5a"; ACC="#6a2c91"; LIGHT="#f4f0f8"; GREY="#ececec"
plt.rcParams.update({"font.family":"DejaVu Sans"})
TS,LS,AS_=8.4,7.4,7.0; PAD_TOP,LINE_H=0.075,0.050
def bh(n): return PAD_TOP+n*LINE_H+0.030
def box(ax,x,y,w,lines,title,fc="white",ec=INK,tc=INK,mono=False,**kw):
    h=bh(len(lines))
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.008,rounding_size=0.018",fc=fc,ec=ec,lw=1.1,zorder=2))
    ax.text(x+0.018,y+h-0.030,title,fontsize=kw.get("ts",TS),fontweight="bold",color=tc,va="top",zorder=3)
    for i,l in enumerate(lines):
        ax.text(x+0.018,y+h-PAD_TOP-0.018-i*LINE_H,l,fontsize=LS,color=MUTE,va="top",zorder=3,
                family="DejaVu Sans Mono" if mono else "DejaVu Sans")
    return h
def arrow(ax,p1,p2,label=None,ls="-",col=INK,style="-|>"):
    ax.add_patch(FancyArrowPatch(p1,p2,arrowstyle=style,mutation_scale=11,lw=1.1,color=col,linestyle=ls,zorder=4))
    if label: ax.text(p1[0]+0.012,(p1[1]+p2[1])/2,label,fontsize=AS_,color=ACC,ha="left",va="center",style="italic",zorder=5)
# FIG 1
fig,ax=plt.subplots(figsize=(6.5,4.6)); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
W,X,AX=0.455,0.035,0.515
y1=0.635; h1=box(ax,X,y1,W,["posture = supine","implement = barbell","pattern = horizontal-push","laterality = bilateral  ..."],"1.  FACET RECORD",fc=LIGHT,ec=ACC,tc=ACC,mono=True)
ax.text(AX,y1+h1/2,"source of truth:\nthe only layer\na human authors",fontsize=AS_,color=MUTE,style="italic",va="center")
y2=0.285; h2_=box(ax,X,y2,W,["OMEN-C  barbell horizontal-push","OMEN-X  posture=supine|...","key     OMEN-0.2-VRQRJHQSX5NX6"],"2.  CANONICAL FORM + KEY",mono=True)
ax.text(AX,y2+h2_/2,"derived deterministically:\nsame movement,\nsame key, always",fontsize=AS_,color=MUTE,style="italic",va="center")
y3=0.065; h3=box(ax,X,y3,W,['"Bench Press"   ·   "Press de banca"'],"3.  DISPLAY NAME",fc=GREY)
ax.text(AX,y3+h3/2,"curated alias:\nlocalizable,\nnever the identity",fontsize=AS_,color=MUTE,style="italic",va="center")
arrow(ax,(0.20,y1),(0.20,y2+h2_),"generated"); arrow(ax,(0.20,y2),(0.20,y3+h3),"alias table",ls=(0,(4,2)),style="<|-|>")
ax.text(0.5,0.012,"The name is an output, not an input.",fontsize=8.4,color=ACC,ha="center",fontweight="bold")
fig.savefig("fig1_three_layers.png",dpi=300,bbox_inches="tight",facecolor="white")
# FIG 2
fig,ax=plt.subplots(figsize=(7.2,3.1)); ax.set_xlim(-0.012,1.06); ax.set_ylim(0,1); ax.axis("off")
steps=[("Facet record",["3 required","+ modifiers"]),("Validate",["closed","vocabularies"]),
       ("Defaults",["flat · standard","grip per pattern"]),("Serialize",["citation order","→ OMEN-X"]),
       ("Hash",["base-32","→ OMEN key"])]
w,gap=0.188,0.015; xs=[i*(w+gap) for i in range(5)]; ytop=0.58
for i,(t,ls_) in enumerate(steps):
    hh=box(ax,xs[i],ytop,w,ls_,t,fc=LIGHT if i in (0,4) else "white",ec=ACC if i in (0,4) else INK,tc=ACC if i in (0,4) else INK,ts=7.3)
    if i<4: arrow(ax,(xs[i]+w,ytop+hh/2),(xs[i+1],ytop+hh/2))
hb=box(ax,0.115,0.10,0.80,["horizontal-push  →  pectoralis-major, anterior-deltoid, triceps","                 →  compound"],
       "pattern → muscle / mechanic   (derived, never entered)",ec=MUTE,tc=MUTE,mono=True,ts=7.6)
arrow(ax,(xs[2]+0.05,ytop),(xs[2]+0.05,0.10+hb),None,ls=(0,(3,2)),col=MUTE)
ax.text(0.52,0.02,"Every canonical string and key in this paper is emitted by the reference encoder.",fontsize=AS_,color=MUTE,ha="center",style="italic")
fig.savefig("fig2_pipeline.png",dpi=300,bbox_inches="tight",facecolor="white")
print("figures regenerated with v0.2 key")
