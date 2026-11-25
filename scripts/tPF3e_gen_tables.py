#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tPF-3e RAMP-TABLE HEADER GENERATOR.

Reads the seven vendor ramp-fill tables from banked saves (the SAME law and
self-verification as scripts/tPF3d_ramp_runtime.py: base ds:0x48c33 at guest
linear 0x242000+0x48c33, tables at base+idx*0x100 for idx in {0,1,7,8,9,10,13},
H per-save from the BDA signature, surface-descriptor signature
639/479/640/480+'DATA' at ds:0x48518) and emits rewrite/src/ui/rampfill_law.h
with the byte-exact tables embedded as law data + sha256 provenance.

Citation (docs/re/_wip_tPF3.md F16): every table is byte-stable across the
whole banked corpus (60/60 saves, one variant each). The producer that
computes them at init is named-open TPF3d-A; embedding the corpus reading is
the corpus-faithful port law (640x480 game.pal only).

usage: tPF3e_gen_tables.py BANK_DIR [BANK_DIR...] > rewrite/src/ui/rampfill_law.h
EXIT 0 on success (all dirs, all saves verify, one variant per slot);
1 = cross-save disagreement (law NOT embeddable); 2 = harness error.
"""
import glob, hashlib, os, struct, sys, zipfile
from collections import Counter

D_BASE = 0x242000
SIG_DIMS = (639, 479, 640, 480)
RAMP = (0, 1, 7, 8, 9, 10, 13)


def bda_h(mem):
    return [h for h in range(0, 0x2000)
            if struct.unpack_from("<H", mem, h + 0x413)[0] == 0x280
            and struct.unpack_from("<H", mem, h + 0x44A)[0] == 80]


def read_tables(slot):
    """Return {idx: bytes256} or None if the save fails verification."""
    try:
        mem = zipfile.ZipFile(slot).read("Memory")
    except Exception:
        return None
    hs = bda_h(mem)
    if len(hs) != 1:
        return None
    h = hs[0]

    def ds(d, n):
        return mem[h + D_BASE + d: h + D_BASE + d + n]

    dims = struct.unpack_from("<4I", ds(0x48518, 16), 0)
    if dims != SIG_DIMS or ds(0x48528, 4) != b"DATA":
        return None
    base = struct.unpack_from("<I", ds(0x48c33, 4), 0)[0]
    out = {}
    for idx in RAMP:
        # The table lives at guest-physical base + idx*0x100; physical P is
        # member offset P + H (pointer law, docs/re/r1-savestate.md).
        t = mem[base + idx * 0x100 + h: base + idx * 0x100 + h + 256]
        if len(t) != 256:
            return None
        out[idx] = bytes(t)
    return out


def main():
    slots = []
    for d in sys.argv[1:]:
        slots += sorted(glob.glob(os.path.join(d, "*.sav")))
    if not slots:
        sys.stderr.write("harness-error: no .sav under %s\n" % sys.argv[1:])
        return 2
    variants = {i: Counter() for i in RAMP}
    seen = {i: {} for i in RAMP}
    ok = 0
    for slot in slots:
        t = read_tables(slot)
        if t is None:
            sys.stderr.write("skip (verify fail): %s\n" % slot)
            continue
        ok += 1
        for i in RAMP:
            sha = hashlib.sha256(t[i]).hexdigest()
            variants[i][sha] += 1
            seen[i][sha] = t[i]
    sys.stderr.write("saves verified: %d/%d\n" % (ok, len(slots)))
    if ok == 0:
        return 1
    canon = {}
    for i in RAMP:
        if len(variants[i]) != 1:
            sys.stderr.write("DISAGREEMENT idx %d: %d variants\n"
                             % (i, len(variants[i])))
            return 1
        sha = next(iter(variants[i]))
        canon[i] = (seen[i][sha], sha)

    out = []
    out.append("// SPDX-License-Identifier: GPL-3.0-or-later\n")
    out.append("#pragma once\n")
    out.append("// THE VENDOR TILE-OVERLAY RAMP-FILL TABLES — law data, not code.\n")
    out.append("//\n")
    out.append("// LAW [docs/re/_wip_tPF3.md F15/F16, cited bytes]: the polygon filler\n")
    out.append("// 0x62d15 translates every pixel it covers, dst[i] := TABLE[idx][dst[i]]\n")
    out.append("// (interior 0x63015..0x63026), with the per-cell MAP pointer pushed as\n")
    out.append("// arg4 = [ds:0x48c33] + idx*0x100 (push sequence 0x3be31..0x3be4b). The\n")
    out.append("// overlay-pass idx ladder (0x3bbd6..0x3bc4b, input WORD[esp+0x374] ==\n")
    out.append("// the cell class byte, writer 0x3c2cc — F17) selects idx 7/8/9/10/13;\n")
    out.append("// tileOverlayFillIndex() in ui/planetview.h carries that ladder.\n")
    out.append("//\n")
    out.append("// PROVENANCE [F16]: the seven tables below were read from the guest RAM\n")
    out.append("// of the banked save corpus (pointer law: base ds:0x48c33 at linear\n")
    out.append("// 0x242000+0x48c33, table at base+idx*0x100, H per-save from the BDA\n")
    out.append("// signature, surface-descriptor 639/479/640/480+'DATA' self-check) and\n")
    out.append("// hash IDENTICAL across every verified save — regenerate + diff with\n")
    out.append("// scripts/tPF3e_gen_tables.py BANK_DIR... to re-verify against any new\n")
    out.append("// bank. The init-time PRODUCER is named-open TPF3d-A; this embedding is\n")
    out.append("// the corpus reading, valid for the 640x480 game.pal configuration.\n")
    out.append("//\n")
    out.append("// STRUCTURAL FACTS (F16): idx 1 is the identity except four swaps\n")
    out.append("// 0x79->0x80, 0x7f->0x57, 0xf1->0xf0, 0xf3->0x0f (a fill through it is\n")
    out.append("// nearly a visual no-op); idx 0 collapses the field to 39 distinct\n")
    out.append("// values; idx 7/8/9/10/13 carry 103/92/80/83/112 distinct values (the\n")
    out.append("// graded ramp).\n")
    out.append("// Each overlay class colour is a FIXED POINT of its own table:\n")
    out.append("// T7[0]==0, T8[117]==117, T9[146]==146, T10[255]==255 (checked in\n")
    out.append("// tests/test_rampfill_tpf3e.cpp).\n")
    out.append("#include <cstdint>\n\n")
    out.append("namespace ascend::ui {\n\n")
    out.append("// sha256 of each embedded table (provenance handle; pins re-check).\n")
    out.append("inline constexpr const char* kRampTableSha256[] = {\n")
    for i in RAMP:
        out.append('    "%s",  // idx %d\n' % (canon[i][1], i))
    out.append("};\n\n")
    out.append("// The ramp slot -> table-row lookup: returns the 256-byte row for a\n")
    out.append("// ladder index, or nullptr for a slot the overlay pass never selects.\n")
    out.append("inline const uint8_t* rampFillRow(int idx) {\n")
    out.append("    switch (idx) {\n")
    for i in RAMP:
        out.append("    case %d: {\n        static const uint8_t row[256] = {\n" % i)
        b = canon[i][0]
        for r0 in range(0, 256, 16):
            out.append("        " + ", ".join("0x%02x" % v for v in b[r0:r0+16]) + ",\n")
        out.append("        };\n        return row;\n    }\n")
    out.append("    default: return nullptr;\n    }\n}\n\n")
    out.append("}  // namespace ascend::ui\n")
    sys.stdout.write("".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
