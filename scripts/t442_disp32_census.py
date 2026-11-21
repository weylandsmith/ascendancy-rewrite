import bisect
from collections import defaultdict
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
hits=set()
needle=b'\x10\x2e\x01\x00'
i=0
while True:
    j=data.find(needle,i)
    if j<0: break
    if j>0:
        modrm=data[j-1]
        if (modrm >> 6)==2 and (modrm & 7)==5:   # mod=10, rm=101, no SIB
            hits.add(j-2)
    i=j+1
per=defaultdict(list)
for h in sorted(hits):
    per[enc(h)].append(hex(h))
for k,v in sorted(per.items()):
    print(k, len(v), v[:12])
