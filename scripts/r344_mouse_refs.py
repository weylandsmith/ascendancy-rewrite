#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t344: exhaustive immediate-reference hunt for DATA\\MOUSE.SHP.

Law context (docs/re/datafiles.md pool-relative-immediate law, OQ-004 CLOSED):
a code immediate naming a name-pool string is imm = str_off - 0x82BB0, which
the loader relocates to P0 + str_off. t328's zero-ref claim scanned u32 ==
0x84314 (the raw string offset) — that scan CANNOT see a pool-relative imm.
This script scans the whole image for ALL candidate encodings:
  A) imm == 0x84314                     (raw string offset)
  B) imm == 0x1764                      (pool-relative str_off - 0x82BB0)
  C) imm == P0 + 0x84314 (relocated)    for a list of known P0 values
  D) u32 == any of the above            (data-region pointer)
Reports byte offsets + (if in the disasm range) nearest preceding known fn
start from artifacts/functions_full.tsv.
"""
import re, struct, sys

IMG = open("artifacts/ascend_restored.bin", "rb").read()
N = len(IMG)
print("image bytes:", N)

# 1) locate every verbatim 'DATA\\MOUSE.SHP'
offs = []
i = IMG.find(b"DATA\\MOUSE.SHP")
while i != -1:
    offs.append(i)
    i = IMG.find(b"DATA\\MOUSE.SHP", i + 1)
print("verbatim string offsets:", [hex(o) for o in offs])
if not offs:
    sys.exit(1)
S = offs[0]
POOL = 0x82BB0
REL = S - POOL
print("pool-relative imm value:", hex(REL))

P0S = {"t343-scan": 0x1BF450}  # B - H from r1sav-20261011-213606 (STATE law)

cands = {hex(S): S, hex(REL): REL}
for name, p0 in P0S.items():
    cands["P0(%s)+S" % name] = p0 + S

def scan_val(v):
    """all 4-byte-aligned+unaligned LE-u32 occurrences of v"""
    pat = struct.pack("<I", v & 0xFFFFFFFF)
    out, i = [], IMG.find(pat)
    while i != -1:
        out.append(i)
        i = IMG.find(pat, i + 1)
    return out

# tsv function starts for attribution
fn_starts = []
try:
    for line in open("artifacts/functions_full.tsv"):
        m = re.match(r"^[0-9a-fA-F]+\t?(\d+)?", line)
        parts = line.rstrip("\n").split("\t")
        for p in parts:
            if re.fullmatch(r"0x[0-9a-fA-F]+|[0-9a-fA-F]{4,}", p):
                try:
                    fn_starts.append(int(p, 0))
                except ValueError:
                    pass
                break
except OSError:
    pass
fn_starts = sorted(set(fn_starts))

def attr(off):
    lo, hi = 0, len(fn_starts) - 1
    if not fn_starts:
        return "?"
    # binary search greatest start <= off
    best = None
    l, r = 0, len(fn_starts) - 1
    while l <= r:
        m = (l + r) // 2
        if fn_starts[m] <= off:
            best = fn_starts[m]; l = m + 1
        else:
            r = m - 1
    nxt = None
    for f in fn_starts:
        if f > off:
            nxt = f; break
    return "fn%s next=%s" % (hex(best) if best is not None else "?", hex(nxt) if nxt else "EOF")

CODE_LO, CODE_HI = 0x14BB0, 0x82BB0
for label, v in cands.items():
    hits = scan_val(v)
    in_code = [h for h in hits if CODE_LO <= h < CODE_HI]
    in_data = [h for h in hits if not (CODE_LO <= h < CODE_HI)]
    print("\ncandidate %s = %s: %d hits (%d in code, %d in data)"
          % (label, hex(v), len(hits), len(in_code), len(in_data)))
    for h in hits[:40]:
        zone = "CODE" if CODE_LO <= h < CODE_HI else "data"
        print("   %s @%s  ctx=%s" % (zone, hex(h), attr(h)))

# also: disasm grep for the immediates as text (catch e.g. mov edx,0x1764)
print("\n(disasm immediates grepped separately by the session)")
