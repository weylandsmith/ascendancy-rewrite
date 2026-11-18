#!/usr/bin/env python3
"""t425c: the OTHER vendor shot settles the RACE-SLOT face law.

docs/assets/refcap/original-strategic-map.png is 640x480 with png = screen+40,
so its rows 482..512 (the race strip) are CLIPPED — it contains zero race-slot
pixels (docs/re/_wip_t425.md F8/F9). scratchpad/galaxymap-original.png is
642x481 with IDENTITY mapping (t394 measured law) and its rows 442..472 DO
carry the RACECONTROLS strip: dominant idx200, exactly 1starmap k19's own
backdrop colour.

This tool diffs every slot rect against the five family members t425b
proposed (base 20+5i, +0 plain dark, +1 plain bright, +2 outlined dark,
+3 outlined bright, +4 grey) and reports which member is bit-exact per slot,
plus the exact well/glyph colours. It also re-checks the four TOGGLE buttons
in this second shot as a cross-check of the F8 well law on a DIFFERENT frame
of the vendor's own screen.

Read-only census; exit 0.
"""
import collections
import struct

LIB = "extracted/ascend01/data/1starmap.shp"
PAL = "extracted/ascend01/data/game.pal"
SHOT = "scratchpad/galaxymap-original.png"
SLOTS = [(1, 479), (2, 501), (3, 523), (4, 545), (5, 567), (6, 589), (7, 611)]
TOGGLES = [("TOGLANES", 479, 15, 1), ("TOGEMPIRE", 518, 16, 0),
           ("TOGSHIPS", 557, 17, 1), ("TOGCOLONIES", 596, 18, 1)]


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
    A = np.asarray(Image.open(SHOT).convert("RGB")).astype(int)
    print(f"shot {SHOT} {A.shape[1]}x{A.shape[0]} (identity mapping, t394)")

    print("\n== A. RACE SLOTS: which family member is bit-exact? (rect 449..465)")
    best_overall = collections.Counter()
    for i, (s, x0) in enumerate(SLOTS):
        base = 20 + 5 * i
        ref = A[449:466, x0:x0 + 17]
        line = []
        best = (-1, None)
        for off in range(5):
            k = base + off
            w, h, rows = decode(d, starts[k], k)
            eq = tot = 0
            for y in range(min(h, 17)):
                for x in range(min(w, 17)):
                    v = rows[y][x]
                    if v < 0:
                        continue
                    tot += 1
                    if tuple(int(t) for t in ref[y][x]) == conv[v]:
                        eq += 1
            rate = eq / max(1, tot)
            line.append(f"+{off}:{100*rate:5.1f}%")
            if rate > best[0]:
                best = (rate, k)
        rc = collections.Counter(tuple(v) for v in ref.reshape(-1, 3))
        print(f"  slot{s} x{x0} {' '.join(line)}  best=+{best[1]-base} "
              f"({100*best[0]:.1f}%)  colours: "
              + " ".join(f"{k2}:{n}{c2i.get(k2, ['-'])}" for k2, n in rc.most_common(4)))
        best_overall[best[1] - base] += 1
    print("  best-member histogram:", dict(best_overall))

    print("\n== B. stride backdrop k19 vs the strip's non-slot columns")
    w, h, rows = decode(d, starts[19], 19)
    eq = tot = 0
    for y in range(h):
        for x in range(w):
            v = rows[y][x]
            if v < 0:
                continue
            px = tuple(int(t) for t in A[442 + y, 474 + x])
            tot += 1
            if px == conv[v]:
                eq += 1
    print(f"  k19 exact over full 158x30: {eq}/{tot} {100*eq/tot:.1f}%")

    print("\n== C. toggle well law cross-check on THIS shot (screen coords)")
    for name, x0, k, bs in TOGGLES:
        w, h, rows = decode(d, starts[k], k)
        cell = A[403:403 + h, x0:x0 + w]
        for label, swap in [("raw", False), ("242->80", True)]:
            eq = t2 = 0
            for y in range(h):
                for x in range(w):
                    v = rows[y][x]
                    if v < 0:
                        continue
                    tgt = conv[80] if (swap and v == 242) else conv[v]
                    t2 += 1
                    if tuple(int(t) for t in cell[y][x]) == tgt:
                        eq += 1
            print(f"  {name:12s} BS{bs} {label:7s} {eq}/{t2} {100*eq/t2:5.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
