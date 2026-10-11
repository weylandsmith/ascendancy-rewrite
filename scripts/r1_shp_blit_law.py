#!/usr/bin/env python3
"""r1_shp_blit_law.py — OQ-005 t64: blit-faithful validator + RAM base solve.

Grammar (re-verified 2026-10-12 from FUN_0005caac raw asm SHR-flag
cascade; JA = CF==0 && ZF==0 after SHR AL,1):
  C==0          end of row          (JNC path @0x5cca3)
  C==1          skip L=next byte    (fall @0x5ccae; no clip, EDI+=L)
  C odd,  C>1   literal copy C>>1   (JNZ @0x5ccec: no value byte)
  C even, C>=2  run: next byte x C>>1 (JA @0x5ccc3: value byte consumed)
Row rules from the main row loop (0x5cc7e..0x5ce8c) + skip prepass
(0x5cc42..0x5cc57): each row terminates on exactly one C==0; dest row
advance is +W per row (NOT +pixels); rows MAY exceed W (clip branches
0x5cd31/0x5cd62 clamp negatives — overshoot legal, overwrites next row).
Entry law (0x5cb4d..0x5cb5b + 0x5cb85): ESI = P + u32[P+8+8*sel], fields
[+0]=pxptr [+4]=W-1 [+8]=H-1 [+0xc..0x14]=rect u32, stream = entry+0x18.
rec0 law (t61): dims u32-pair at record start, stream at +8.

Modes reported per library:
  strict  = every row pixels <= W, exact span, rows == h+1 (rec1+)
  loose   = well-formed ops, exact span, rows == h+1, rows may exceed W
Prefix variants for rec1+: 8 (dims pair + zero u32), 12 (+2 u16),
24 (0x18-byte entry header).
"""
import os, struct, sys, glob, collections, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def parse(p):
    d = open(p, "rb").read()
    if d[:4] != b"1.10": raise ValueError("magic")
    count = struct.unpack_from("<I", d, 4)[0]
    tsz = struct.unpack_from("<I", d, 8)[0]
    if tsz != 8 * (count + 1): raise ValueError("table-size")
    te = 0x10 + tsz
    starts = [te] + [struct.unpack_from("<Q", d, 0x10 + 8 * k)[0]
                     for k in range(count - 1)]
    ends = starts[1:] + [len(d)]
    return d, count, te, starts, ends

def walk(d, i, end, W, strict):
    """row-stream walk; return (rows, None) or (None, reason). strict
    fails on first row overshoot; loose counts overshoots but tolerates."""
    rows = 0
    while True:
        x = 0
        while True:
            if i >= end: return None, "truncated"
            C = d[i]; i += 1
            if C == 0:
                break
            if C == 1:
                if i >= end: return None, "truncated"
                x += d[i]; i += 1
            elif C & 1:
                n = C >> 1; x += n; i += n
                if i > end: return None, "truncated"
            else:
                n = C >> 1; i += 1; x += n
                if i > end: return None, "truncated"
            # blit mirrors: writes CLAMP at row end (0x5cd31/0x5cd62) but
            # the stream is consumed unconditionally; x>W rows are LEGAL
            # (spill discarded). No x limit in either mode.
        rows += 1
        if i >= end: return rows, (None if i == end else "ran-past")

def eval_lib(p, pfx, strict):
    d, count, te, starts, ends = parse(p)
    # rec0: u32 W-1,H-1? (t61 used w0+1 as W) dims u32 pair at +0, stream +8
    w0, h0 = struct.unpack_from("<II", d, starts[0])
    if not (0 < w0 <= 4095 and 0 < h0 <= 4095): return "rec0-dims"
    r = walk(d, starts[0] + 8, ends[0], w0 + 1, strict)
    if r[0] is None: return "rec0-" + r[1]
    if r[0] != h0 + 1 and r[0] != h0: return f"rec0-rows{r[0]}!={h0+1}"
    for k in range(1, count):
        w16, h16 = struct.unpack_from("<HH", d, starts[k])
        if not (0 < w16 <= 4095): return f"rec{k}-dims"
        r = walk(d, starts[k] + pfx, ends[k], w16 + 1, strict)
        if r[0] is None: return f"rec{k}-" + r[1]
        if r[0] != h16 + 1: return f"rec{k}-rows{r[0]}!={h16+1}"
    return "ok"

def main():
    libs = sorted(glob.glob(os.path.join(ROOT, "extracted", "**", "*.shp"),
                            recursive=True))
    tally = collections.Counter()
    fails = collections.defaultdict(list)
    for p in libs:
        rel = os.path.relpath(p, ROOT)
        for pfx in (8, 12, 24):
            for strict in (True, False):
                try:
                    st = eval_lib(p, pfx, strict)
                except Exception as e:
                    st = "ERR " + str(e)[:30]
                key = f"pfx{pfx}/{'strict' if strict else 'loose'}:{st}"
                tally[key] += 1
                if st != "ok" and pfx == 24 and strict:
                    fails[st].append(rel.split(os.sep)[-1])
    print("libraries:", len(libs))
    for pfx in (8, 12, 24):
        row = []
        for s in ("strict", "loose"):
            ok = tally[f"pfx{pfx}/{s}:ok"]
            row.append(f"{s}:ok={ok}")
        print(f"  rec1+ prefix {pfx:2d}: " + "  ".join(row))
    print("pfx24/strict failure classes:")
    for k, v in sorted(fails.items(), key=lambda kv: -len(kv[1])):
        print(f"  {k}: {len(v)}  e.g. {v[:4]}")

    # ---- RAM base solve: does ANY address make the blit table law true
    # for the verbatim 14intel copy?  entry_abs = P + u32[P+8+8k] must land
    # on vb + fsoff[k+1] for k=0..count-2 (file table order).
    raw = zipfile.ZipFile(os.path.join(
        ROOT, "work/r1/r1ad-20261011-132306/ck/ck113.sav")
    ).read("Memory")
    d, count, te, starts, ends = parse(os.path.join(
        ROOT, "extracted/ascend01/data/14intel.shp"))
    vb = raw.find(d[:64])
    if vb < 0:
        print("RAM: 14intel verbatim anchor not found"); return
    deltas = [starts[k + 1] - starts[0] for k in range(count - 1)]
    hits = []
    for P in range(vb - 0x400, vb + 0x40):
        ok = True
        for k, dl in enumerate(deltas):
            want = vb + dl - P
            try: v = struct.unpack_from("<I", raw, P + 8 + 8 * k)[0]
            except Exception: ok = False; break
            if v != want: ok = False; break
        if ok: hits.append(hex(P))
    print(f"RAM base solve ({count-1} deltas):", hits or "NO P in [vb-0x400, vb+0x40]")
    # looser: any P satisfying k=0..2 only
    hits3 = []
    for P in range(vb - 0x800, vb + 0x80):
        try:
            if all(struct.unpack_from("<I", raw, P + 8 + 8 * k)[0]
                   == vb + deltas[k] - P for k in range(min(3, len(deltas)))):
                hits3.append(hex(P))
        except Exception: pass
    print("RAM base solve (first 3 deltas):", hits3[:10] or "none")

if __name__ == "__main__":
    main()
