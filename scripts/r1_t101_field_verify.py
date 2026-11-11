#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t101: SHIP-FIELD RE-ATTRIBUTION verify (+0x88=POWER, +0x94=MOVES,
+0x8c=INTEGRITY, +0x98=MAX-INTEGRITY, [+0x18]=POWER capacity). RC=0 iff all legs pass.

LEG 1 (vendor panel law, restored image): the kind4/5 ship-panel arm bytes at
0x1da8a..0x1daaf must be exactly
  8b 88 8c 00 00 00 51   mov ecx,[eax+0x8c]; push ecx   (3rd arg INTEGRITY)
  8b b0 94 00 00 00 56   mov esi,[eax+0x94]; push esi   (2nd arg MOVES)
  8b b8 88 00 00 00 57   mov edi,[eax+0x88]; push edi   (1st arg POWER)
  68 c9 31 08 00         push 0x831c9 = 'POWER %d MOVES %d INTEGRITY %d'
LEG 2 (jump-table law): FILE 0x43b10 (cs-rel 0x2ef60, t96 code-object law) =
16 u32 entries == t99 case bodies EXACTLY — pins 7 SA_DoublePower=0x43c3f
(+0x88<<=1) and 9 SA_SapAlienPower=0x43d33 (+0x88:=0) as ABILITY BODIES
(edx==1 dispatch at 0x441c1), not per-turn race-maintenance legs.
LEG 3 (live, work/r1/playcap/save/60.sav, item-table-anchored B):
 a) [rec+0x8c] == [rec+0x98] on ALL active rows (boundary integrity law);
 b) [rec+0x94] == [rec+0x10] (drive stat) on >= 30/35 rows (MOVES base;
    exceptions = ships that moved/were bumped the same day);
 c) POWER bounded by the cited 0x4a99c recharge init on ALL rows:
    init = trunc(cap * clamp(base*0.1+1.0, 1.0, 2.0)), cap=[rec+0x18],
    base = clamp((T - [rec+0x52])//100, 0, 10), T = u32 guest X 0x12e10
    (deviations are same-day burns: upkeep 0x4a6ff, travel 0x4a2f6 —
    observed value can only be BELOW init);
 d) exact init fit >= 24/35 (measured 25/35; the 5 zero-power outliers all
    carry [rec+0x52] > T and belong to the at-war race — residue noted).
"""
import struct, os, sys, zipfile, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "work/ascend_restored.bin")
SAV = os.path.join(ROOT, "work/r1/playcap/save/60.sav")

CASES = {5: 0x43baf, 6: 0x43bf0, 7: 0x43c3f, 8: 0x43c79, 9: 0x43d33,
         10: 0x43de4, 11: 0x43e98, 12: 0x43eec, 13: 0x43fba, 14: 0x4402a,
         15: 0x4400a, 16: 0x4405f, 17: 0x440b5, 18: 0x4400a, 19: 0x4414e,
         20: 0x4418e}


def leg1():
    d = open(IMG, "rb").read()
    w = d[0x1da8a:0x1daaf]
    seq = (w[0:6] == b"\x8b\x88\x8c\x00\x00\x00" and w[6] == 0x51 and
           w[7:13] == b"\x8b\xb0\x94\x00\x00\x00" and w[13] == 0x56 and
           w[14:20] == b"\x8b\xb8\x88\x00\x00\x00" and w[20] == 0x57 and
           w[21:26] == b"\x68\xc9\x31\x08\x00")
    fmt = d[0x831c9:0x831c9 + 40].split(b"\0")[0] == b"POWER %d MOVES %d INTEGRITY %d"
    return seq and fmt, f"push-seq={seq} fmt-string={fmt}"


def leg2():
    d = open(IMG, "rb").read()
    ent = [struct.unpack_from("<I", d, 0x43b10 + 4 * k)[0] for k in range(16)]
    bad = [(k + 5, hex(v)) for k, v in enumerate(ent) if v != CASES[k + 5]]
    return not bad, f"16/16 jump-table entries == t99 bodies (mismatches: {bad})"


def leg3():
    m = zipfile.ZipFile(SAV).read("Memory")
    hits = {mo.start() - (0x82bb0 + 0x73e40 + 8)
            for mo in re.finditer(rb"\x1e\x00Factory", m)}
    if len(hits) != 1:
        raise SystemExit("harness-error: item-table anchor not unique")
    B = hits.pop()
    u32 = lambda X: struct.unpack("<I", m[B + 0x82bb0 + X:B + 0x82bb0 + X + 4])[0]
    T = u32(0x12e10)
    base = B + 0x82bb0 + 0x3a095
    n = min(u32(0x43489) >> 16, 0x6b)
    tot = int_ok = mov_ok = bound_ok = exact = 0
    for k in range(n):
        r = base + k * 0x162
        own = struct.unpack_from("<I", m, r + 0x54)[0] >> 16
        if own >= 20:
            continue
        tot += 1
        d10 = struct.unpack_from("<I", m, r + 0x10)[0]
        cap = struct.unpack_from("<I", m, r + 0x18)[0]
        d52 = struct.unpack_from("<I", m, r + 0x52)[0]
        POW = struct.unpack_from("<I", m, r + 0x88)[0]
        INT = struct.unpack_from("<I", m, r + 0x8c)[0]
        MOV = struct.unpack_from("<I", m, r + 0x94)[0]
        MAXI = struct.unpack_from("<I", m, r + 0x98)[0]
        int_ok += INT == MAXI
        mov_ok += MOV == d10
        age = T - d52
        b = max(0, min(10, age // 100)) if age >= 0 else 0
        init = int(cap * min(1.0 + 0.1 * b, 2.0))
        bound_ok += 0 <= POW <= init
        exact += POW == init
    ok = (tot >= 30 and int_ok == tot and mov_ok >= tot - 5
          and bound_ok == tot and exact >= tot - 11)
    return ok, (f"T={T} rows={tot} int==max:{int_ok}/{tot} mov==drive:{mov_ok}/{tot} "
                f"pow<=recharge-init:{bound_ok}/{tot} exact-init:{exact}/{tot}")


def main():
    rc = 0
    for name, fn in (("panel-law", leg1), ("jump-table-law", leg2), ("live-law", leg3)):
        try:
            ok, msg = fn()
        except SystemExit:
            raise
        except Exception as e:
            ok, msg = False, f"EXC {e!r}"
        print(f"{name}: {'OK' if ok else 'FAIL'}  {msg}")
        rc |= 0 if ok else 1
    print("RC=", rc)
    return rc


if __name__ == "__main__":
    sys.exit(main())
