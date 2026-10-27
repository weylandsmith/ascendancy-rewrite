#!/usr/bin/env python3
"""t105 self-verification — STATIC PAIR (OQ-016 residuals from t99 S6.4):
  (b) "stride-45 table 0x74782" REFUTED: 0x74782 is the ROW-0 RUNTIME COST
      WORD of the research-state table (base 0x74744, stride 75 == the
      OQ-013 restree runtime record law, cost u16 @ record+62).
  (a) GOVOROM SA_Cornucopia min key WORD[planet+0x42] IS the population
      counter word (identity with the t24 CLOSED pop law), not a cache.

LEGS (all must pass; RC=0 only on all-pass):
  1 jump table FILE 0x43b10 entry5==0x43de4 (ability 10 Cornucopia),
    entry14==0x4414e (ability 19 FreeResearch).
  2 FreeResearch body *75 DECOMPOSITION byte-pinned 0x4416b..0x44189:
      lea eax,[edx*4] (8d 04 95 00 00 00 00); add eax,edx (01 d0);
      mov edx,eax (89 c2); shl eax,4 (c1 e0 04); sub eax,edx (29 d0)
      => eax = 75*target; then mov ax,[eax+0x74782] (66 8b 80 82 47 07 00)
      and mov [ebx+0x764a0],ax (66 89 83 a0 64 07 00). 75 != 45.
  3 LIVE 60.sav: restree row-0 spaced name at corollary X 0x74746 (record
    base +2), 61 consecutive stride-75 deltas, and cost u16 at
    0x74782 + 75*i fits the CITED OQ-013 runtime cost law 66/66
    (runtime = file_cost*(2*row-20) row>10, clamp 65000; else file_cost).
  4 Cornucopia body 0x43de4 byte-pinned: pool base 0x2b057 (b8 57 b0 02 00),
    stride 0x7b (83 c0 7b), owner gate [eax+0x57] (8a 58 57), skip-class
    [eax+0x16]==10 (83 fb 0a), MIN key WORD [eax+0x42] (66 8b 70 42 +
    66 39 f1), pick pool esi=0x6838 (be 38 68 00 00) + idiv 3 (f7 fe).
  5 LIVE 60.sav planet pool (base 0x2b057 stride 123, count hi16 ds
    0x3a091 == 145): max growth counter +0x4e < 50 (t81 law) AND every
    pop(+0x42) >= cap(+0x4a) row carries counter 0 (LAB_000393f9 law),
    zero violations.
Working notes: docs/re/_wip_t105.md.
"""
import os, re, re as _re, struct, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "work/ascend_restored.bin")
SAV = os.path.join(ROOT, "work/r1/playcap/save/60.sav")
RESTREE = os.path.join(ROOT, "extracted/ascend00/restree.txt")

def img():
    return open(IMG, "rb").read()

def mem():
    m = zipfile.ZipFile(SAV).read("Memory")
    hits = [mo.start() - (0x82bb0 + 0x73e40 + 8)
            for mo in _re.finditer(rb"\x1e\x00Factory", m)]
    if len(set(hits)) != 1:
        raise SystemExit("harness-error: item-table anchor not unique")
    return m, hits[0]

def file_rows():
    txt = open(RESTREE, "rb").read().decode("cp437")
    rows = []
    for line in txt.split("\r\n"):
        t = line.split()
        if not t or (len(t) == 1 and t[0].isdigit()) or len(t) < 3:
            continue
        rows.append({"spaced": t[0].replace("^", " "), "cost": int(t[2])})
    return rows[:66]

def leg1():
    d = img()
    e5 = struct.unpack_from("<I", d, 0x43b10 + 4 * 5)[0]
    e14 = struct.unpack_from("<I", d, 0x43b10 + 4 * 14)[0]
    ok = e5 == 0x43de4 and e14 == 0x4414e
    return ok, f"jump-table entry5=0x{e5:x} (want 0x43de4) entry14=0x{e14:x} (want 0x4414e)"

def leg2():
    d = img()
    pins = [(0x4416b, b"\x8d\x04\x95\x00\x00\x00\x00", "lea eax,[edx*4]"),
            (0x44172, b"\x01\xd0", "add eax,edx"),
            (0x44174, b"\x89\xc2", "mov edx,eax"),
            (0x44176, b"\xc1\xe0\x04", "shl eax,4"),
            (0x44179, b"\x29\xd0", "sub eax,edx  -> eax = 75*t"),
            (0x4417b, b"\x66\x8b\x80\x82\x47\x07\x00", "mov ax,[eax+0x74782]"),
            (0x44182, b"\x66\x89\x83\xa0\x64\x07\x00", "mov [ebx+0x764a0],ax")]
    bad = [f"{a:x}:{lbl}" for a, pat, lbl in pins if d[a:a+len(pat)] != pat]
    # arithmetic seal: the decomposition computes 16*5t - 5t = 75t, NOT 45t
    ok = not bad
    return ok, "75x decomposition + cost-word load pinned" + (f" BAD: {bad}" if bad else "")

def leg3():
    rows = file_rows()
    if len(rows) != 66:
        return False, f"restree parse {len(rows)} != 66"
    m, B = mem()
    idx = lambda X, n: m[B + 0x82BB0 + X: B + 0x82BB0 + X + n]
    # row-0 name at corollary X 0x74746 == record base 0x74744 + 2 (OQ-013)
    nm0 = rows[0]["spaced"].encode("cp437")
    ok_name = idx(0x74746, len(nm0)) == nm0
    # 61 consecutive stride-75 deltas on the spaced names (member coords:
    # row-0 name member offset == B + 0x82bb0 + 0x74746)
    m0 = 0x82bb0 + 0x74746
    deltas = []
    prev = None
    for i, r in enumerate(rows):
        hs = [mo.start() - B for mo in _re.finditer(_re.escape(r["spaced"].encode("cp437")), m)]
        cand = [h for h in hs if m0 + 75 * i - 4 <= h <= m0 + 75 * i + 4]
        if cand:
            if prev is not None:
                deltas.append(cand[0] - prev)
            prev = cand[0]
    ok_stride = len(deltas) == 65 and all(x == 75 for x in deltas)
    # cost word law: WORD[0x74782 + 75*i] == runtime cost of row i
    ok_cost = 0
    for i, r in enumerate(rows):
        want = r["cost"] if i <= 10 else min(r["cost"] * (2 * i - 20), 65000)
        got = struct.unpack("<H", idx(0x74782 + 75 * i, 2))[0]
        if got == want:
            ok_cost += 1
    ok = ok_name and ok_stride and ok_cost == 66
    return ok, (f"row0@X0x74746 name {'OK' if ok_name else 'FAIL'}; "
                f"stride-75 deltas 61/61: {'OK' if ok_stride else deltas}; "
                f"cost law {ok_cost}/66 at 0x74782+75*i")

def leg4():
    d = img()
    pins = [(0x43de4, b"\xb8\x57\xb0\x02\x00", "mov eax,0x2b057 pool"),
            (0x43dfa, b"\x83\xc0\x7b", "add eax,0x7b stride 123"),
            (0x43e0a, b"\x8a\x58\x57", "mov bl,[eax+0x57] owner"),
            (0x43e18, b"\x83\xfb\x0a", "cmp ebx,0xa skip-class"),
            (0x43e1d, b"\x66\x8b\x70\x42", "mov si,WORD [eax+0x42] MIN KEY"),
            (0x43e21, b"\x66\x39\xf1", "cmp cx,si min prune"),
            (0x43e74, b"\xbe\x38\x68\x00\x00", "mov esi,0x6838 pick pool"),
            (0x43e8b, b"\xf7\xfe", "idiv esi (3)")]
    bad = [f"{a:x}:{lbl}" for a, pat, lbl in pins if d[a:a+len(pat)] != pat]
    return (not bad), "cornucopia min-key walk pinned" + (f" BAD: {bad}" if bad else "")

def leg5():
    m, B = mem()
    idx = lambda X, n: m[B + 0x82BB0 + X: B + 0x82BB0 + X + n]
    cnt = struct.unpack("<I", idx(0x3a091, 4))[0] >> 16
    if not (0 < cnt < 2000):
        return False, f"planet count law hi16(ds 0x3a091) = {cnt:#x} implausible"
    maxc = 0
    viol = 0
    checked = 0
    for i in range(cnt):
        r = idx(0x2b057 + 123 * i, 123)
        if len(r) < 123:
            return False, f"pool row {i} truncated"
        pop = struct.unpack_from("<H", r, 0x42)[0]
        cap = struct.unpack_from("<H", r, 0x4a)[0]
        acc = struct.unpack_from("<H", r, 0x4e)[0]
        maxc = max(maxc, acc)
        if pop >= cap:
            checked += 1
            if acc != 0:
                viol += 1
    ok = maxc < 50 and viol == 0
    return ok, (f"rows={cnt} max counter +0x4e={maxc} (<50) ; pop>=cap rows "
                f"{checked} with counter!=0: {viol} (want 0)")

def main():
    rc = 0
    for i, fn in enumerate([leg1, leg2, leg3, leg4, leg5], 1):
        ok, msg = fn()
        print(f"LEG {i}: {'PASS' if ok else 'FAIL'} — {msg}")
        rc |= 0 if ok else 1
    print("T105_RC", rc)
    sys.exit(rc)

if __name__ == "__main__":
    main()
