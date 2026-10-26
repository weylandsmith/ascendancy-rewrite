#!/usr/bin/env python3
"""t91 (W6-A4): research-picker field-identity + write-census self-check.

Pins the law banked in docs/re/aicode.md §3b:
  1. FIELD IDENTITY: 0x74744 + 0x1d4e == 0x76492 and +0x1d5c == 0x764a0
     (the completion consumer FUN_00046aec is called with EAX=0x74744 at
     0x2502f, so race+0x1d4e IS DAT_00076492[race]).
  2. TURN CALL SITE: insn at 0x25028 is 'mov eax,0x74744' and 0x2502f is
     'call 0x46aec'.
  3. WRITE CENSUS over obj0 code [0x14bb0,0x82bb0) of work/ascend_restored.bin:
     - disp32 0x76492: value-writer 0x40164 (FUN_00040018 picker) and
       0x47e34 (UI); clear-writers 0x22db7/0x43f5b/0x47880/0x47985.
     - raw-byte scan for u16 0x1d4e: exactly 6 hits, all inside aligned
       insns in FUN_00046aec / FUN_00046e84 (no hidden second base).
  4. PICK GATE: 0x3eb1d is 'call 0x40018' and 0x3eb05 reads [edx*2+0x76492].
  5. BUILD-COMPLETION GRANT: sole E8 caller of 0x46e84 is 0x39173.
Exit 0 iff all hold. R12 law: scan work/ascend_restored.bin only.
"""
import os, re, struct, sys

ROOT = "/home/hrethric/projects/ascendancy"
IMG = os.path.join(ROOT, "work/ascend_restored.bin")
CODE = (0x14BB0, 0x82BB0)

fails = []
def check(name, ok, detail=""):
    print(f"{'OK ' if ok else 'FAIL'} {name} {detail}")
    if not ok:
        fails.append(name)

data = open(IMG, "rb").read()

# linear disasm of obj0 (objdump, boundary-authoritative)
import subprocess
r = subprocess.run(["objdump", "-b", "binary", "-m", "i386", "-M", "intel",
                    "-D", f"--start-address=0x{CODE[0]:x}",
                    f"--stop-address=0x{CODE[1]:x}", IMG],
                   capture_output=True, text=True)
if r.returncode != 0:
    sys.exit(f"objdump failed: {r.stderr[:200]}")
pat = re.compile(r"^\s*([0-9a-f]+):\t([0-9a-f ]+)\t(.*)$")
insn = {}
for ln in r.stdout.splitlines():
    m = pat.match(ln)
    if m:
        insn[int(m.group(1), 16)] = m.group(3).strip()

def ins(a):
    return insn.get(a, "")

check("field identity 0x1d4e/0x1d5c", 0x74744 + 0x1D4E == 0x76492 and 0x74744 + 0x1D5C == 0x764A0)
check("turn call site 0x25028", "0x74744" in ins(0x25028), ins(0x25028))
check("turn call site 0x2502f", ins(0x2502f).startswith("call") and "0x46aec" in ins(0x2502f), ins(0x2502f))

# disp32 census for DAT_00076492
def hits_u32(val):
    p = val.to_bytes(4, "little")
    addrs_sorted = sorted(insn)
    import bisect
    out = []
    s = 0
    while True:
        i = data.find(p, s)
        if i < 0:
            break
        s = i + 1
        if not (CODE[0] <= i < CODE[1]):
            continue
        j = bisect.bisect_right(addrs_sorted, i) - 1
        if j < 0:
            continue
        a = addrs_sorted[j]
        nxt = addrs_sorted[j + 1] if j + 1 < len(addrs_sorted) else a + 16
        if a <= i < nxt:
            out.append((a, ins(a)))
    return out

sites = dict(hits_u32(0x76492))
for w in (0x40164, 0x47E34):
    check(f"value-writer 0x{w:x}", w in sites, sites.get(w, "MISSING"))
# clear sites store 0xffff; 0x43f5b uses the immediate, the other three load
# the constant into the value register shortly before (verify that instead).
for w, regload in ((0x22DB7, (0x22DA1, "ebx", "mov ebx,0xffff")),
                   (0x43F5B, None),
                   (0x47880, (0x47879, "edx", "mov edx,0xffff")),
                   (0x47985, (0x4797E, "ecx", "mov ecx,0xffff"))):
    ok = w in sites and ("0x76492" in sites[w])
    detail = sites.get(w, "MISSING")
    if ok and regload is not None:
        la, reg, want = regload
        ok = ins(la).replace(" ", "") == want.replace(" ", "")
        detail = f"{detail}  <- {ins(la)}"
    check(f"writer-of-0xffff 0x{w:x}", ok, detail)
check("picker stores to 0x76492 at 0x40164", "0x76492" in sites.get(0x40164, ""), sites.get(0x40164, ""))

# raw u16 disp scan for 0x1d4e: expect exactly the 6 banked sites
h = []
p = (0x1D4E).to_bytes(2, "little")
s = 0
while True:
    i = data.find(p, s)
    if i < 0:
        break
    s = i + 1
    if CODE[0] <= i < CODE[1]:
        h.append(i)
expect = {0x46BBE, 0x46C14, 0x46C39, 0x46C56, 0x46C6A, 0x46EEA}
check("raw 0x1d4e disp hits == banked 6", set(h) == expect, f"got {sorted(hex(x) for x in h)}")

# pick gate
check("pick gate reads target 0x3eb05", "0x76492" in ins(0x3EB05), ins(0x3EB05))
check("pick gate calls 0x40018 at 0x3eb1d", "0x40018" in ins(0x3EB1D), ins(0x3EB1D))

# build-completion grant: sole caller of 0x46e84 is 0x39173
callers = []
for a in insn:
    if CODE[0] <= a < CODE[1] - 5 and data[a] == 0xE8:
        t = a + 5 + struct.unpack("<i", data[a + 1:a + 5])[0]
        if t == 0x46E84:
            callers.append(a)
check("sole caller of FUN_00046e84 == 0x39173", callers == [0x39173], str([hex(c) for c in callers]))

print("T91 PICKER CENSUS:", "PASS" if not fails else f"FAIL ({fails})")
sys.exit(0 if not fails else 1)
