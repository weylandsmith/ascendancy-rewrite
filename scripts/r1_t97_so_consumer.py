#!/usr/bin/env python3
"""t97: hunt the CONSUMER of the SO order-name block (F 0x88e60, pool-rel
0x62b0, 10 records stride 20). Hammers:
  (H) disasm adjust-helper 0x2fb38, census its rel32 callers;
  (D) full extent of the display fn containing the whole-block copy 0x1dae5
      (prologue walk back, terminators forward) + esp-rel readers of the
      [esp+0x10] staging slot over the FULL extent;
  (I) 20-stride indexed-read census (imul 0x14 / lea *,reg,reg,*0x14) in
      obj0 code.
Restored-image law: work/ascend_restored.bin, base-0 VA == FILE offset;
code obj0 [0x14bb0,0x82bb0); cs-rel imm -> FILE = cs-rel + 0x14bb0.
RC=0 on completion."""
import re, subprocess, collections

DATA = open('/home/hrethric/projects/ascendancy/work/ascend_restored.bin','rb').read()
CODE = (0x14bb0, 0x82bb0)

def objdump(start, end):
    r = subprocess.run(['objdump','-D','-b','binary','-m','i386','-M','intel',
                        f'--start-address=0x{start:x}',f'--stop-address=0x{end}',
                        '/home/hrethric/projects/ascendancy/work/ascend_restored.bin'],
                       capture_output=True, text=True)
    out=[]
    for ln in r.stdout.splitlines():
        m=re.match(r'\s+([0-9a-f]+):\s((?:[0-9a-f]{2} )+)\s*(.*)', ln)
        if m: out.append((int(m.group(1),16), m.group(3).strip()))
    return out

print('=== (H) helper 0x2fb38 body ===')
for a,t in objdump(0x2fb38, 0x2fb38+96): print(hex(a), t)

print('=== (H) rel32 callers of 0x2fb38 ===')
disp = 0x2fb38 - 5   # rel32 = target - (site+5); call rel32 enc: e8 <rel32 where next_insn = site+5
rel = (0x2fb38 - 5).to_bytes(4,'little')
sites=[]
i=CODE[0]
while True:
    j=DATA.find(rel,i)
    if j<0 or j>=CODE[1]: break
    if DATA[j-1]==0xe8: sites.append(j-1)
    i=j+1
# also any e8 XX.. where target lands 0x2fb38 (general)
i=CODE[0]
while True:
    j=DATA.find(b'\xe8',i)
    if j<0 or j>=CODE[1]: break
    if j+5<=CODE[1]:
        r_=int.from_bytes(DATA[j+1:j+5],'little',signed=True)
        if (j+5+r_)&0xffffffff==0x2fb38 and (j-1) not in sites and j not in [s for s in sites]:
            # site of call is j
            if j not in sites: sites.append(j)
    i=j+1
sites=sorted(set(sites))
print('caller sites:', [hex(s) for s in sites])
for s in sites:
    ctx=objdump(max(s-24,CODE[0]), s+40)
    print('--- site',hex(s))
    for a,t in ctx: print(' ',hex(a),t)

print('=== (D) display fn extent around copy site 0x1dae5 ===')
# prologue walk-back: look for push ebp (55) followed by mov ebp,esp (8b ec), or
# watcom-style push ebx/push esi/push edi at function starts. Scan back 0x3000.
back = DATA[0x1dae5-0x3000:0x1dae5]
starts=[]
for k in range(len(back)-3):
    p=0x1dae5-0x3000+k
    if DATA[p]==0x55 and DATA[p+1:p+3]==b'\x8b\xec': starts.append(p)
    elif DATA[p:p+3]==b'\x53\x56\x57': starts.append(p)      # push ebx;push esi;push edi
    elif DATA[p:p+2]==b'\x55\x53': starts.append(p)          # push ebp;push ebx
print('prologue candidates back-walk:', [hex(x) for x in starts][-12:])
# terminators forward: ret (c3), ret imm (c2 xx xx), jmp rel32 (e9) landing outside
# simple heuristic: find `c3` at depth of function: walk linearly from each cand.
best=None
for p in sorted(starts, reverse=True):
    body=objdump(p, min(p+0x4000, CODE[1]))
    end=None
    for a,t in body:
        if t in ('ret',) or t.startswith('ret ') :
            end=a; break
    if end and end>0x1dae5:
        best=(p,end,body); break
if best:
    p,end,body=best
    print('function extent', hex(p),'..',hex(end), 'insns', len(body))
    print('=== esp-rel readers of +0x10 slot over FULL extent ===')
    for a,t in body:
        if 'esp' in t and re.search(r'\+ 0x10\b|\+0x10\b', t):
            print(' ',hex(a),t)
    print('=== calls out of the display fn ===')
    for a,t in body:
        if t.startswith('call'): print(' ',hex(a),t)
else:
    print('NO extent resolved (walk failed)')

print('=== (I) 20-stride indexed patterns in obj0 ===')
pat_imul = re.compile(r'imul\s+\w+,\s*\w+,\s*0x14\b')
pat_lea  = re.compile(r'lea\s+\w+,\s*\[[^\]]*\*\s*0x14\b')
hits=collections.Counter(); lines=[]
# linear disasm of whole obj0 is big; use objdump output streaming
proc=subprocess.Popen(['objdump','-D','-b','binary','-m','i386','-M','intel',
     f'--start-address=0x{CODE[0]:x}',f'--stop-address=0x{CODE[1]}',
     '/home/hrethric/projects/ascendancy/work/ascend_restored.bin'], stdout=subprocess.PIPE, text=True)
cur=0; n=0
for ln in proc.stdout:
    m=re.match(r'\s+([0-9a-f]+):\s((?:[0-9a-f]{2} )+)\s*(.*)', ln)
    if not m: continue
    a=int(m.group(1),16); t=m.group(3).strip(); n+=1
    if pat_imul.search(t) or pat_lea.search(t):
        hits['pat']+=1; lines.append((a,t))
proc.wait()
print('insns scanned', n, 'pattern hits', len(lines))
for a,t in lines[:80]: print(' ',hex(a),t)
print('RC', proc.returncode)
