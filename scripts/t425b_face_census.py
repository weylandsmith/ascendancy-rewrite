#!/usr/bin/env python3
"""t425b F-S-e: 1starmap race-filter FACE census.

windows.txt RACE<N>CONTROL rows (extracted/ascend00/windows.txt, tr -d '\\r')
give slot rects + FRAME column 20,25,30,35,40,45,50 and a STRIDE frame 19.
This tool decodes those faces with the project's own .shp row-walk law
(scripts/t399_digit_faces.py grammar == docs/re/shp.md S9/S21) and prints,
per face: dims, the multiset of palette INDICES, and whether the face is
solid. It then compares the face indices against the refcap slot pixels of
docs/assets/refcap/original-strategic-map.png measured through the CONVERTED
game.pal (c = (v<<2)|(v>>4), docs/re/palette.md S2) so the "runtime ramp"
question is answered by pixels, not by the raw table.

Read-only. Prints a verdict line. Exit 0 always (it is a census).
"""
import collections
import struct
import sys

LIB = "extracted/ascend01/data/1starmap.shp"
PAL = "extracted/ascend01/data/game.pal"
REFCAP = "docs/assets/refcap/original-strategic-map.png"

# windows.txt verbatim: bit, x0, x1, frame  (RACE1..7CONTROL; ln429-435)
SLOTS = [(1, 479, 20), (2, 501, 25), (4, 523, 30), (8, 545, 35),
         (16, 567, 40), (32, 589, 45), (64, 611, 50)]
STRIDE_FRAME = 19


def load(path):
    d = open(path, "rb").read()
    magic, count, tsz = struct.unpack_from("<III", d, 0)
    starts = [0x10 + tsz] + list(struct.unpack_from("<%dQ" % (count - 1), d, 0x10))
    return d, count, starts


def decode(d, rec, k):
    """CANONICAL walk (docs/re/shp.md S16/S17 + scripts/r1_shp_unifiedlaw.py
    rec_state): k==0 stream at rec+8; k>=1 stream at rec+0x18 (dims at
    rec+0x10; the 1starmap family is tag B/A). The row terminates ONLY at the
    C==0 terminator — ops may over-paint past W (measured k20: n=17 at W=16),
    so consume-until-terminator then clamp, exactly like rowwalk(). (The
    t399_digit_faces.py while-len(row)<w variant desyncs here — do not
    reuse it for this lib.)"""
    off = rec if k == 0 else rec + 0x10
    s = rec + 8 if k == 0 else rec + 0x18
    w, h = struct.unpack_from("<II", d, off)
    pos = s
    rows = []
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
    d, count, starts = load(LIB)
    pal = open(PAL, "rb").read()
    raw = [(pal[i], pal[i + 1], pal[i + 2]) for i in range(0, 768, 3)]
    conv = [tuple((c << 2) | (c >> 4) for c in t) for t in raw]

    faces = {}
    print(f"lib {LIB} records={count}")
    for name, k in [("STRIDE", STRIDE_FRAME)] + [(f"slot{s}", f) for s, _, f in SLOTS]:
        w, h, rows = decode(d, starts[k], k)
        idx = collections.Counter(v for r in rows for v in r)
        opaque = {v: n for v, n in idx.items() if v >= 0}
        solid = len(opaque) == 1
        faces[name] = (w, h, opaque, rows)
        top = sorted(opaque.items(), key=lambda kv: -n_of(kv, opaque))[:6]
        print(f"{name:8s} k{k:<3d} {w}x{h} distinct={len(opaque)} solid={solid} "
              + " ".join(f"idx{v}:{opaque[v]}px->{conv[v]}" for v, _ in top))

    # refcap slot measurement. original-strategic-map.png is 640x480 = the
    # WINDOW already (refcap.md S1: root grabs carry a +40 title band; a 640x480
    # capture has none), so the windows.txt rect y 449..465 applies DIRECTLY
    # (verified this session: the strip reads the slot colours at y 449).
    try:
        from PIL import Image
        import numpy as np
        A = np.asarray(Image.open(REFCAP).convert("RGB"))
        c2i = {}
        for i, c in enumerate(conv):
            c2i.setdefault(c, []).append(i)
        print(f"\nrefcap {REFCAP} {A.shape[1]}x{A.shape[0]} (window rect +40y law, refcap.md S1)")
        for s, x0, f in SLOTS:
            crop = A[449 + 40:466 + 40, x0:x0 + 16].reshape(-1, 3)
            cnt = collections.Counter(map(tuple, crop))
            top = cnt.most_common(3)
            print(f"  slot{s} x{x0} frame{f}: " + " | ".join(
                f"{tuple(int(v) for v in c)} {k/len(crop)*100:.0f}% pal{c2i.get(tuple(int(v) for v in c))}"
                for c, k in top))
    except ImportError as e:
        print(f"(PIL/numpy unavailable: {e} — refcap half skipped)")
    return 0


def n_of(kv, opaque):
    return opaque[kv[0]]


if __name__ == "__main__":
    sys.exit(main())
