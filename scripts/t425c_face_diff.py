#!/usr/bin/env python3
"""t425c probe 3: EXACT diff refcap vs decoded .shp faces.

Three questions, answered by pixel equality (not eyeball):

 Q1 TOGGLES: does refcap rect(X0,Y0,30x30) == decode(k15..k18) for all four
    layer-toggle buttons? TOGEMPIRE is BUTTONSTATE 0 (OFF) while the other
    three are 1. If the refcap matches frame 16 EXACTLY like 15/17/18 match
    theirs, the vendor has NO OFF-state art: SHAPEFRAME is state-INDEPENDENT
    and the ON/OFF encoding is behavioural only.

 Q2 STRIP BG: refcap strip rows 443.. (inside 474,442..632,472) measured
    (89,24,56)=conv idx80 as dominant, but k19's dominant is idx200
    (12,12,16). Is the strip backdrop the vendor's Markov chrome showing
    THROUGH transparent pixels of k19, or is k19 itself painted with a
    runtime-remapped colour?

 Q3 SLOT FACES: refcap slot rects 479..627 x 449..465 vs decode of the
    +0/+2/+4 family members. Which member matches, and in which palette
    indices (static or remapped)?

Exit 0 always.
"""
import collections
import struct

LIB = "extracted/ascend01/data/1starmap.shp"
PAL = "extracted/ascend01/data/game.pal"
REFCAP = "docs/assets/refcap/original-strategic-map.png"
BTNS = [("TOGLANES", 479, 403, 15), ("TOGEMPIRE", 518, 403, 16),
        ("TOGSHIPS", 557, 403, 17), ("TOGCOLONIES", 596, 403, 18)]


def load(path):
    d = open(path, "rb").read()
    magic, count, tsz = struct.unpack_from("<III", d, 0)
    starts = [0x10 + tsz] + list(struct.unpack_from("<%dQ" % (count - 1), d, 0x10))
    return d, count, starts


def decode(d, rec, k):
    off = rec if k == 0 else rec + 0x10
    s = rec + 8 if k == 0 else rec + 0x18
    w, h = struct.unpack_from("<II", d, off)
    pos, rows = s, []
    for _ in range(h):
        row = []
        while True:
            c = d[pos]; pos += 1
            if c == 0:
                break
            if c == 1:
                row += [-1] * d[pos]; pos += 1
            elif c & 1:
                n = c >> 1
                row += list(d[pos:pos + n]); pos += n
            else:
                row += [d[pos]] * (c >> 1); pos += 1
        rows.append(row[:w])
    return w, h, rows


def main():
    from PIL import Image
    import numpy as np
    d, count, starts = load(LIB)
    pal = open(PAL, "rb").read()
    raw = [(pal[i], pal[i + 1], pal[i + 2]) for i in range(0, 768, 3)]
    conv = [tuple((c << 2) | (c >> 4) for c in t) for t in raw]
    c2i = collections.defaultdict(list)
    for i, c in enumerate(conv):
        c2i[c].append(i)
    A = np.asarray(Image.open(REFCAP).convert("RGB")).astype(int)

    print("== Q1 toggle buttons: exact diff refcap vs decode(k)")
    for name, x0, y0, k in BTNS:
        w, h, rows = decode(d, starts[k], k)
        ref = A[y0:y0 + h, x0:x0 + w]
        face = np.array([[conv[v] if v >= 0 else None for v in r] for r in rows],
                        dtype=object)
        eq = ne = transp = 0
        mism = collections.Counter()
        for y in range(h):
            for x in range(w):
                v = rows[y][x] if x < len(rows[y]) else -1
                if v < 0:
                    transp += 1
                    continue
                rc = tuple(int(t) for t in ref[y][x])
                if rc == conv[v]:
                    eq += 1
                else:
                    ne += 1
                    mism[(v, rc)] += 1
        print(f"  {name:12s} k{k}: eq={eq} ne={ne} transp={transp} "
              f"-> {'EXACT' if ne == 0 else 'DIFF'}")
        for (v, rc), n in mism.most_common(4):
            print(f"      idx{v} raw{raw[v]} conv{conv[v]} != refcap{rc}"
                  f"{c2i.get(rc, '?')} x{n}")

    print("\n== Q2 strip rows 442..472 x 474..632: colour census vs k19")
    w, h, rows = decode(d, starts[19], 19)
    print(f"  k19 {w}x{h}")
    ref = A[442:442 + 30, 474:474 + 158]
    cnt = collections.Counter(tuple(int(t) for t in p) for p in ref.reshape(-1, 3))
    print("  refcap strip top colours: "
          + " ".join(f"{c}:{n}{c2i.get(c, ['-'])}" for c, n in cnt.most_common(6)))
    idx19 = collections.Counter(v for r in rows for v in r if v >= 0)
    print("  k19 idx counts: " + " ".join(f"idx{v}:{n}->{conv[v]}"
                                          for v, n in idx19.most_common(6)))
    # per-column: does the strip's non-slot area follow k19's alpha mask?
    slot_x = {s: x for s, x, *_ in [(1, 479), (2, 501), (3, 523), (4, 545),
                                    (5, 567), (6, 589), (7, 611)]}
    gap_cols = [x for x in range(474, 632) if not any(sx <= x <= sx + 16 for sx in slot_x.values())]
    gc = collections.Counter(tuple(int(t) for t in A[y, x]) for y in range(443, 472) for x in gap_cols)
    print("  GAP columns (between slots): "
          + " ".join(f"{c}:{n}{c2i.get(c, ['-'])}" for c, n in gc.most_common(5)))

    print("\n== Q3 slot rects vs family members (+0 plain, +1 bright, +2 "
          "outline, +3 outline-bright, +4 grey)")
    for i, (s, x0) in enumerate([(1, 479), (3, 523), (5, 567), (7, 611)]):
        base = 20 + 5 * i
        ref = A[449:466, x0:x0 + 17]
        rcnt = collections.Counter(tuple(int(t) for t in p) for p in ref.reshape(-1, 3))
        print(f"  slot{s} rect: " + " ".join(f"{c}:{n}{c2i.get(c, ['-'])}"
                                             for c, n in rcnt.most_common(4)))
        for off in (0, 1, 2, 3, 4):
            k = base + off
            try:
                w2, h2, rws = decode(d, starts[k], k)
            except Exception as e:                                # noqa: BLE001
                print(f"      k{k}: fail {e}")
                continue
            idx = collections.Counter(v for r in rws for v in r if v >= 0)
            top = sorted(idx.items(), key=lambda kv: -kv[1])[:3]
            eq = 0
            tot = 0
            for y in range(min(h2, 17)):
                for x in range(min(w2, 17)):
                    v = rws[y][x] if x < len(rws[y]) else -1
                    if v < 0:
                        continue
                    tot += 1
                    if tuple(int(t) for t in ref[y][x]) == conv[v]:
                        eq += 1
            print(f"      k{k} {w2}x{h2} eq={eq}/{tot} "
                  + " ".join(f"idx{v}:{n}" for v, n in top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
