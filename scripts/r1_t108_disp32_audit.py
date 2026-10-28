#!/usr/bin/env python3
"""r1_t108_disp32_audit.py — adjudicate disp32 + FPU store-census claims.

t108 audit tool (first revision generated mod=10 [base+disp32] forms only and
MISSED moffs encodings entirely — disclosed in census-audit S2).

Per disp value V three scans over work/ascend_restored.bin, code span
[0x14bb0,0x82bb0) (t107 S1b law); every candidate boundary-checked
(insn must START at candidate addr per function-start objdump decode AND its
operand text must name the disp):

  SCAN 1 RAW TOKEN upper bound: every raw u32-LE occurrence of V in the code
         span; try instruction boundaries at the occurrence and at +1/+2
         (0x66/0x0F prefixes shift the disp position); report any insn whose
         operands name 0xV. This is encoding-agnostic — catches anything the
         generator below forgot.
  SCAN 2 MOFFS + acc forms: mov A0-A3 both dirs, test A8/A9, arith pair set
         (00/01,08/09,10/11,18/19,20/21,28/29,30/31,38/39,88/89,8A/8B) —
         byte/word(66)/dword. Group ops (80/81/83...) have NO moffs form.
  SCAN 3 FPU D8..DF r=6/r=7 in every disp-bearing addressing form
         (mod00 rm101 disp32, mod01, mod10, SIB scale00 base=disp32).

Usage: r1_t108_disp32_audit.py [0x7458e 0xccb 0x67]
"""
import bisect, subprocess, sys, os, re

ROOT = "/home/hrethric/projects/ascendancy"
IMG = os.path.join(ROOT, "work/ascend_restored.bin")
FUNCS = os.path.join(ROOT, "work/functions_full.tsv")
CODE_LO, CODE_HI = 0x14BB0, 0x82BB0

def load_funcs():
    addrs, names = [], {}
    with open(FUNCS) as f:
        f.readline()
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            try:
                a = int(p[0], 16)
            except Exception:
                continue
            addrs.append(a); names[a] = p[1] if len(p) > 1 else "?"
    addrs.sort()
    return addrs, names

def find_all(data, pat):
    res, start = [], 0
    while True:
        i = data.find(pat, start)
        if i < 0:
            return res
        res.append(i); start = i + 1

_wcache = {}
def decode(start, stop):
    key = (start, stop)
    if key in _wcache:
        return _wcache[key]
    r = subprocess.run(["objdump", "-b", "binary", "-D", "-m", "i386",
                        "-M", "intel", f"--start-address={start}",
                        f"--stop-address={stop}", IMG],
                       capture_output=True, text=True)
    ins = {}
    for ln in r.stdout.splitlines():
        m = ln.split(":", 1)
        if len(m) != 2:
            continue
        hx = m[0].strip().rstrip(":")
        if not hx or not all(c in "0123456789abcdef" for c in hx):
            continue
        parts = m[1].split("\t")
        if len(parts) < 3:
            continue
        bs = parts[1].replace(" ", "")
        if len(bs) % 2:
            continue
        ins[int(hx, 16)] = (len(bs) // 2, parts[2].strip())
    _wcache[key] = ins
    return ins

ADDRS, NAMES = None, None

def at_boundary(i, tokre):
    """decoded text of the insn starting exactly at i if its operands name tokre."""
    k = bisect.bisect_right(ADDRS, i) - 1
    fstart = ADDRS[k] if k >= 0 else None
    fn = NAMES[ADDRS[k]] if k >= 0 else "?"
    if fstart is not None:
        ins = decode(fstart, min(fstart + 0x600, 0x90000))
        if i in ins and tokre.search(ins[i][1]):
            return ins[i][1], fn
    ins2 = decode(i, i + 24)
    if i in ins2 and tokre.search(ins2[i][1]):
        return ins2[i][1], fn
    return None, fn

ARITH = [0x00, 0x01, 0x08, 0x09, 0x10, 0x11, 0x18, 0x19, 0x20, 0x21,
         0x28, 0x29, 0x30, 0x31, 0x38, 0x39, 0x88, 0x89, 0x8A, 0x8B]

def moffs_patterns(V):
    disp = V.to_bytes(4, "little")
    out = []
    for op in ARITH + [0xA0, 0xA1, 0xA2, 0xA3, 0xA8, 0xA9]:
        for pfx in (b"", b"\x66"):
            out.append((pfx + bytes([op]) + disp, f"m{op:02x}"))
    return out

def fpu_patterns(V):
    disp = V.to_bytes(4, "little")
    out = []
    for op in range(0xD8, 0xE0):
        for r in (6, 7):
            out.append((bytes([op, 0x05 | (r << 3)]) + disp, f"fpu{op:02x}_{r}_m0d32"))
            for rm in (0, 1, 2, 3, 5, 6, 7):
                out.append((bytes([op, 0x40 | (r << 3) | rm]), f"fpu{op:02x}_{r}_m1"))
                out.append((bytes([op, 0x80 | (r << 3) | rm]) + disp, f"fpu{op:02x}_{r}_m2"))
            out.append((bytes([op, 0x44 | (r << 3), (0 << 6) | (4 << 3) | 5]), f"fpu{op:02x}_{r}_m1sib"))
            out.append((bytes([op, 0x84 | (r << 3), (0 << 6) | (4 << 3) | 5]) + disp, f"fpu{op:02x}_{r}_m2sib"))
            out.append((bytes([op, (r << 3) | 4, (0 << 6) | (4 << 3) | 5]) + disp, f"fpu{op:02x}_{r}_m0sib"))
    return out

def is_store(text):
    t = text.lower()
    if re.search(r"\b(fst|fstp|fnst)\w*\b", t):
        return True
    m = re.match(r"^(mov[a-z]*)\s+(.+?)\s*,\s*(.+)$", t)
    if m:
        dst = m.group(2)
        return "ptr" in dst or "ds:" in dst
    if t.startswith("cmp") or t.startswith("test"):
        return False
    for op in ("and", "or", "xor", "adc", "sbb", "sub", "add", "not", "neg",
               "inc", "dec", "shl", "shr", "sar", "sal", "rol", "ror", "xchg",
               "fld", "fild"):
        if t.startswith(op):
            return op not in ("fld", "fild")
    return False

def run_scan(label, V, pats, tokre):
    data = open(IMG, "rb").read()
    verified = {}
    for pat, fam in pats:
        for i in find_all(data, pat):
            if not (CODE_LO <= i < CODE_HI):
                continue
            t, fn = at_boundary(i, tokre)
            if t:
                verified[i] = (fam, t, fn)
    print(f"[{label}] verified: {len(verified)}")
    for i, (fam, t, fn) in sorted(verified.items()):
        print(f"    0x{i:x} [{fn}] {'WRITE' if is_store(t) else 'read '} {fam:20s} {t}")
    return verified

def main():
    global ADDRS, NAMES
    vals = [int(x, 0) for x in sys.argv[1:]] or [0x7458E, 0xCCB, 0x67]
    ADDRS, NAMES = load_funcs()
    data = open(IMG, "rb").read()
    for V in vals:
        tokre = re.compile(rf"0x{V:x}(?![0-9a-f])")
        print(f"\n================ disp V=0x{V:x} ================")
        raw = [i for i in find_all(data, V.to_bytes(4, "little"))
               if CODE_LO <= i < CODE_HI]
        print(f"[scan1 raw] raw u32 occurrences in code span: {len(raw)}")
        found = {}
        for i in raw:
            for j in (i, i + 1, i + 2):
                t, fn = at_boundary(j, tokre)
                if t:
                    found[j] = (t, fn)
        for j, (t, fn) in sorted(found.items()):
            print(f"    0x{j:x} [{fn}] {'WRITE' if is_store(t) else 'read '} {t}")
        if not found and raw:
            print("    (no raw occurrence sits at an operand-owning boundary)")
        run_scan("scan2 moffs", V, moffs_patterns(V), tokre)
        run_scan("scan3 fpu", V, fpu_patterns(V),
                 re.compile(rf"0x{V:x}(?![0-9a-f])"))

if __name__ == "__main__":
    main()
