#!/usr/bin/env python3
"""t426 probe: raceflag k0 stream-offset (rec+8 vs rec+0x18) x anchor test.
Establishes the F2b/F3 law: k0@A = 336/336 exact at BOTH anchors (plaque
png (10,50), crest png (285,117)); the rec+0x18 decode only matches at A+2
(shifted artefact). Trail docs/re/_wip_t426.md F2b. Read-only; exit 0."""

import struct, numpy as np
from PIL import Image
PALB=open("extracted/ascend01/data/game.pal","rb").read()
conv=[(round(PALB[3*i]*255/63),round(PALB[3*i+1]*255/63),round(PALB[3*i+2]*255/63)) for i in range(256)]
d=open("extracted/ascend01/data/raceflag.shp","rb").read()
def dec(rec, soff):
    w,h=struct.unpack_from("<II",d,rec)
    pos=rec+soff; rows=[]
    for _ in range(h):
        row=[]
        while True:
            c=d[pos]; pos+=1
            if c==0: break
            if c==1: row+=[-1]*d[pos]; pos+=1
            elif c&1: n=c>>1; row+=list(d[pos:pos+n]); pos+=n
            else: row+=[d[pos]]*(c>>1); pos+=1
        rows.append((row+[-1]*w)[:w])
    return w,h,rows
ref=np.asarray(Image.open("docs/assets/refcap/original-strategic-map.png").convert("RGB")).astype(int)
for soff in (8,0x18):
    w,h,rows=dec(0xc0,soff)
    op=[sum(1 for i in r if i>=0) for r in rows]
    print("soff",hex(soff),"opaque rows:",op[:4],"...last",op[-2:])
    for (ax,ay,name) in [(10,50,"plaque@png(10,50)"),(10,52,"plaque@png(10,52)"),(285,117,"crest@png(285,117)"),(285,119,"crest@png(285,119)")]:
        eq=0; tot=0; bad=0
        for r in range(h):
            for c in range(w):
                v=rows[r][c]
                if v<0: continue
                tot+=1
                p=ref[ay+r,ax+c]; cc=conv[v]
                if all(abs(int(p[k])-cc[k])<=3 for k in range(3)): eq+=1
        # residual: visible px in the 15x25 block at (ax,ay) not covered by opaque record px
        res=0
        for yy in range(ay,ay+25):
            for xx in range(ax,ax+15):
                if yy<ref.shape[0] and ref[yy,xx].sum()>0:
                    rr,ccx=yy-ay,xx-ax
                    if not (0<=rr<h and 0<=ccx<w and rows[rr][ccx]>=0): res+=1
        print(f"   {name}: eq {eq}/{tot}={100*eq/tot:.1f}%  residual-outside {res}")
