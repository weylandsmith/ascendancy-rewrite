import bisect
data = open('work/ascend_restored.bin','rb').read()
rows=[]
for line in open('work/functions_full.tsv'):
    p=line.rstrip('\n').split('\t')
    if len(p)<2 or p[0]=='file_off': continue
    try: rows.append((int(p[0],16), int(p[1],16)))
    except: pass
rows.sort(); starts=[r[0] for r in rows]
def enc(a):
    i=bisect.bisect_right(starts,a)-1
    return hex(rows[i][0]) if i>=0 and a<rows[i][0]+rows[i][1] else 'GAP'

# call sites to 1fc34 / 5d5a1
c1=[]; c2=[]
for i in range(len(data)-4):
    if data[i]==0xe8:
        rel=int.from_bytes(data[i+1:i+5],'little',signed=True)
        t=i+5+rel
        if t==0x1fc34: c1.append(i)
        elif t==0x5d5a1: c2.append(i)

# reads of DAT_00013b96 (race count mirror) — dword disp32 forms
import re
pats=[rb'\x8b..(\x96;\x01\x00)', rb'\x0f\xb6..(\x96;\x01\x00)', rb'\x66\x8b..(\x96;\x01\x00)']
c3=set()
for rx in pats:
    for m in re.finditer(rx, data, re.S):
        c3.add(m.start())

f1=set(enc(i) for i in c1); f2=set(enc(i) for i in c2)
f3=set(enc(i) for i in c3)
print('readers of 13b96 by func:'); 
for k in sorted(f3): print('  ',k, 'also1fc34' if k in f1 else '', 'also5d5a1' if k in f2 else '')
print('GAP sites 13b96:', sorted(hex(i) for i in c3 if enc(i)=='GAP')[:40])
