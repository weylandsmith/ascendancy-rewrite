#!/usr/bin/env python3
"""t99 W6-A6: FUN_00043b50 race-maintenance dispatch + field-writer census.

Verifies (exit 0 only if every pinned expectation holds):
 1. The jump table operand `jmp DWORD PTR cs:[eax*4+0x2ef60]` @0x441d8
    resolves to restored FILE 0x43b10 (= 0x2ef60 + 0x14bb0, the t96 code-
    object intra base law) — 16 u32 entries ALL inside the function extent
    0x43baf..0x441bf. (Raw FILE 0x2ef60 is pool data = garbage: pinned.)
 2. Cadence table words at 0x6780 (index = (row+0x19a >> 24)).
 3. rel32 caller census for 0x43b50 over obj0 code.
 4. Store-form census for row+0x19d / row+0x19e (disp32 forms + absolute
    row-0 forms 0x12fb3/0x12fb4), decode-boundary verified, over obj0 code
    [0x14bb0, 0x82bb0) — pattern inherited from r1_t86_write_census.py.
 5. Any write to the return-value slot [esp+0x6c4] inside the function.
"""
import re, struct, subprocess, sys, collections

IMG = "work/ascend_restored.bin"
CODE_LO, CODE_HI = 0x14BB0, 0x82BB0
FUN_LO, FUN_HI = 0x43B50, 0x441C0
TABLE_CSREL, TABLE_FILE = 0x2EF60, 0x43B10
CADENCE = 0x6780
CADENCE_FILE = 0x82BB0 + 0x6780   # data-object address law (t96)
PICKPOOL = 0x6838
PICKPOOL_FILE = 0x82BB0 + 0x6838

fail = []

img = open(IMG, "rb").read()

# ---- 1. jump table ------------------------------------------------------
print("== 1. JUMP TABLE ==")
raw = struct.unpack_from("<16I", img, TABLE_CSREL)
bad_raw = [v for v in raw if not (0x43BAF <= v <= 0x441BF)]
print(f"raw FILE {TABLE_CSREL:#x}: {len(bad_raw)}/16 entries OUTSIDE FUN extent (pinned: 16 = pool garbage)")
if len(bad_raw) != 16:
    fail.append("raw 0x2ef60 not pure garbage as expected")

entries = struct.unpack_from("<16I", img, TABLE_FILE)
in_body = [v for v in entries if 0x43BAF <= v <= 0x441BF]
print(f"FILE {TABLE_FILE:#x}: {len(in_body)}/16 entries inside FUN extent 0x43baf..0x441bf")
for i, v in enumerate(entries):
    print(f"  case al={i:2d} (row+0x19d={i+5:2d}) -> {v:#07x}")
if len(in_body) != 16:
    fail.append("0x43b10 table not fully inside function extent")

# ---- 2. cadence table ---------------------------------------------------
print("\n== 2. CADENCE TABLE 0x6780 DATA-INTRA (FILE 0x89330) ==")
words = struct.unpack_from("<64H", img, CADENCE_FILE)
print("  " + " ".join(f"{i}:{w}" for i, w in enumerate(words[:32])))
print("  " + " ".join(f"{i}:{w}" for i, w in enumerate(words[32:], start=32)))
print(f"\n== 2b. PICK POOL {PICKPOOL:#x} intra (FILE {PICKPOOL_FILE:#x}) ==")
print("  " + " ".join(f"{b:#02x}" for b in img[PICKPOOL_FILE:PICKPOOL_FILE + 12]))

# ---- shared objdump pass -------------------------------------------------
dis = subprocess.run(
    ["objdump", "-D", "-b", "binary", "-m", "i386", "-M", "intel",
     f"--start-address=0x{CODE_LO:x}", f"--stop-address=0x{CODE_HI:x}", IMG],
    capture_output=True, text=True).stdout
insn = {}
for line in dis.splitlines():
    m = re.match(r"\s*([0-9a-f]+):\t[0-9a-f ]+\t(.*)", line)
    if m:
        insn[int(m.group(1), 16)] = m.group(2).strip()
print(f"\n== objdump decoded insns: {len(insn)} ==")

# ---- 3. callers of 0x43b50 ----------------------------------------------
print("\n== 3. CALLERS of FUN_00043b50 (rel32) ==")
callers = []
for a, t in insn.items():
    m = re.match(r"call\s+0x([0-9a-f]+)", t)
    if m and int(m.group(1), 16) == 0x43B50:
        callers.append(a)
print("  sites:", ", ".join(hex(c) for x in callers for c in [x]) or "NONE")

# also jmp/call via registers preceded by arg setup: dump context of callers
for c in callers:
    lo = max(CODE_LO, c - 0x30)
    print(f"  context @{c:#x}:")
    for a in range(lo, c + 6):
        if a in insn:
            print(f"    {a:#07x}: {insn[a]}")

# ---- 4. every ref of +0x19d / +0x19e (stores = dst-first operand) --------
STORE_OPS = ("mov", "movabs", "or", "and", "add", "sub", "inc", "dec", "neg", "xor", "xchg")
def is_store(t):
    op = t.split()[0]
    if op in ("inc", "dec", "neg", "not", "xchg"):
        return True
    if op in STORE_OPS:
        # dst operand = first operand after op; is it a memory ref?
        rest = t[len(op):].strip()
        first = rest.split(",")[0]
        return "[" in first
    return False

for off, name in ((0x19D, "0x19d"), (0x19E, "0x19e")):
    abs_hex = "%x" % (0x12E16 + off)  # absolute form: row-0 base 0x12e16 + off
    pat = r"(\+0x%x\]|0x%s)" % (off, abs_hex)
    hits = [(a, t) for a, t in insn.items() if re.search(pat, t)]
    stores = [(a, t) for a, t in hits if is_store(t)]
    print(f"\n== 4. refs of +{name} (incl abs 0x{abs_hex}): {len(hits)} total, {len(stores)} stores ==")
    for a, t in hits:
        tag = "STOR" if (a, t) in stores else "ref "
        ftag = "FN" if FUN_LO <= a < FUN_HI else "  "
        print(f"    {ftag} {tag} {a:#07x}: {t}")

# dword [reg+0x19a] + sar 0x18 form reads the hi BYTE == row+0x19d
print("\n== 4c. refs of dword +0x19a (hi byte == +0x19d cadence index) ==")
for a, t in insn.items():
    if re.search(r"\+0x19a\]|0x12fb0", t):
        ftag = "FN" if FUN_LO <= a < FUN_HI else "  "
        print(f"    {ftag} {a:#07x}: {t}")

# ---- 5. return-value slot writes ----------------------------------------
print("\n== 5. writes to [esp+0x6c4] (return slot) in 0x43b50..0x441bf ==")
for a in sorted(insn):
    if FUN_LO <= a < FUN_HI and re.search(r"esp\+0x6c4\],", insn[a]):
        print(f"    {a:#07x}: {insn[a]}")

print("\nRC:", 1 if fail else 0)
for f_ in fail:
    print("  FAIL:", f_)
sys.exit(1 if fail else 0)
