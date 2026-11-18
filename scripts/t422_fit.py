#!/usr/bin/env python3
"""t422: fit the chrome Markov-field parameters against the vendor left
band statistics (docs/re/chrome.md SS1.5). Vendor targets measured from
docs/assets/refcap/original-strategic-map.png rows 40..479 x1..6:
  h_eq 0.201 v_eq 0.398 lag1 0.62/0.40 vrun1 0.616 vrun2 0.234
  hrun1 0.833 hrun2 0.138
Model: per-pixel chain, P(copy left)=PH else P(repeat up)=PV else fresh
weighted draw from the per-column census (F7 table, _wip_t422.md).
Best fit PH=0.05 PV=0.25 -> mean abs deviation 0.063.
Run: python3 scripts/t422_fit.py  (numpy only)"""
import numpy as np
from collections import Counter

COLC = [  # x1..x6 per-column census {game.pal rgb tuple: count}
 {(97,97,97):46,(77,113,117):209,(85,125,125):94,(89,134,138):59,(89,89,89):28,(81,81,81):2,(97,146,146):2},
 {(81,81,81):42,(69,105,109):143,(77,113,117):126,(85,125,125):45,(89,89,89):76,(89,134,138):6,(73,73,85):2},
 {(60,93,97):58,(69,105,109):150,(77,113,117):49,(73,73,85):92,(89,89,89):53,(48,48,48):15,(81,81,81):11,(85,125,125):8,(89,134,138):2,(60,52,56):2},
 {(28,28,28):5,(48,48,48):47,(48,77,81):83,(60,93,97):103,(69,105,109):90,(73,73,85):92,(60,52,56):10,(77,113,117):7,(85,125,125):1,(89,134,138):2},
 {(48,48,48):39,(48,77,81):80,(60,93,97):117,(69,105,109):76,(73,73,85):108,(60,52,56):10,(40,65,69):1,(56,85,89):1,(77,113,117):5,(85,125,125):3},
 {(28,28,28):6,(48,48,48):123,(24,48,40):45,(36,56,60):143,(40,65,69):86,(48,77,81):27,(56,85,89):7,(60,93,97):1,(77,113,117):2},
]
LUM = lambda c: 0.299*c[0]+0.587*c[1]+0.114*c[2]
V = dict(h_eq=0.201, v_eq=0.398, l1h=0.62, l1v=0.40,
         vr1=0.616, vr2=0.234, hr1=0.833, hr2=0.138)

def vruns(col):
    r=[]; cur=1
    for i in range(1,len(col)):
        if col[i]==col[i-1]: cur+=1
        else: r.append(cur); cur=1
    r.append(cur); return r

def gen(PH, PV, seed, H=440, W=6):
    rng=np.random.default_rng(seed)
    tabs=[(list(d.keys()), np.array(list(d.values()),float)) for d in COLC]
    f=[[None]*W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            r=rng.random()
            if x>0 and r<PH: f[y][x]=f[y][x-1]; continue
            if y>0 and r<PH+PV: f[y][x]=f[y-1][x]; continue
            ids,w=tabs[x]; f[y][x]=ids[int(rng.choice(len(ids),p=w/w.sum()))]
    return f

def stats(f):
    A=np.array([[LUM(p) for p in row] for row in f])
    E=np.array([[f[y][x]==f[y][x-1] for x in range(1,len(f[0]))] for y in range(len(f))])
    E2=np.array([[f[y][x]==f[y-1][x] for x in range(len(f[0]))] for y in range(1,len(f))])
    vr=[]; hr=[]
    for x in range(len(f[0])): vr+=vruns([f[y][x] for y in range(len(f))])
    for y in range(len(f)): hr+=vruns(f[y])
    cv=Counter(vr); ch=Counter(hr)
    return dict(h_eq=E.mean(), v_eq=E2.mean(),
                l1h=np.abs(np.diff(A,axis=1)).mean()/np.abs(A-A.mean()).mean(),
                l1v=np.abs(np.diff(A,axis=0)).mean()/np.abs(A-A.mean()).mean(),
                vr1=cv[1]/len(vr), vr2=cv[2]/len(vr),
                hr1=ch[1]/len(hr), hr2=ch[2]/len(hr))

if __name__ == '__main__':
    best=None
    for PH in (0.0,0.05,0.10,0.15):
        for PV in (0.15,0.20,0.25,0.30,0.35,0.385):
            ds=[{k:abs(s[k]-V[k]) for k in V} for s in
                (stats(gen(PH,PV,sd)) for sd in (1,2,3))]
            arr=np.array([[d[k] for k in V] for d in ds])
            err=float(arr.mean())
            if best is None or err<best[0]:
                best=(err,PH,PV,dict(zip(V, arr.mean(axis=0))))
    print(f"best err {best[0]:.3f}  PH {best[1]}  PV {best[2]}")
    print({k: round(float(best[3][k]),3) for k in V})
