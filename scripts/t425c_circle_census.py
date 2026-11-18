#!/usr/bin/env python3
"""t425c: identify the FOUR ~37px circles the t425b vision pass saw in the
refcap bottom-right corner (docs/assets/refcap/original-strategic-map.png).

Hypothesis under test (from windows.txt verbatim, tr -d '\\r'):
  TOGLANES    X0 479 Y0 403 X1 509 Y1 433  SHAPEFRAME 15  SENDMESSAGE 57
  TOGEMPIRE   X0 518 Y0 403 X1 548 Y1 433  SHAPEFRAME 16  SENDMESSAGE 60
  TOGSHIPS    X0 557 Y0 403 X1 587 Y1 433  SHAPEFRAME 17  SENDMESSAGE 58
  TOGCOLONIES X0 596 Y0 403 X1 626 Y1 433  SHAPEFRAME 18  SENDMESSAGE 61
  RACECONTROLS rect 474,442..632,472 with slots x 479..627 y 449..465 (16px)

The t425b report placed its circles at x 479,523,567,611 pitch 44 INSIDE the
y 442..472 strip. Note those x values are RACE1/3/5/7CONTROL x0s (pitch 44 ==
every other slot), NOT the toggle X0s (pitch 39). So the first thing this tool
does is separate the two bands by geometry rather than by eye:

  1. per-row colour census of x 470..640 for y 395..479, mapped through the
     CONVERTED game.pal (c = (v<<2)|(v>>4), docs/re/palette.md S2);
  2. a connected-component scan of the "filled disc" colour per band;
  3. the .shp faces for frames 15..18 vs 20/25/... decoded with the canonical
     B-family rowwalk (stream@rec+0x18) so face dims can be compared to the
     measured blob dims.

Read-only. Exit 0 always (census).
"""
import collections
import struct
import sys

LIB = "extracted/ascend01/data/1starmap.shp"
PAL = "extracted/ascend01/data/game.pal"
REFCAP = "docs/assets/refcap/original-strategic-map.png"

TOGGLES = [("TOGLANES", 479, 403, 509, 433, 15, 57),
           ("TOGEMPIRE", 518, 403, 548, 433, 16, 60),
           ("TOGSHIPS", 557, 403, 587, 433, 17, 58),
           ("TOGCOLONIES", 596, 403, 626, 433, 18, 61)]
RACE_SLOTS = [(1, 479, 449, 495, 465, 20), (2, 501, 449, 517, 465, 25),
              (3, 523, 449, 539, 465, 30), (4, 545, 449, 561, 465, 35),
              (5, 567, 449, 583, 465, 40), (6, 589, 449, 605, 465, 45),
              (7, 611, 449, 627, 465, 50)]


def load(path):
    d = open(path, "rb").read()
    magic, count, tsz = struct.unpack_from("<III", d, 0)
    starts = [0x10 + tsz] + list(struct.unpack_from("<%dQ" % (count - 1), d, 0x10))
    return d, count, starts


def decode(d, rec, k):
    """Canonical B-family walk: dims at rec+0x10, stream at rec+0x18 for
    k>=1 (docs/re/shp.md S16/S17); terminate ONLY on C==0, then clamp."""
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
    c2i = collections.defaultdict(list)
    for i, c in enumerate(conv):
        c2i[c].append(i)

    print("== static faces (1starmap.shp, %d records, canonical walk)" % count)
    for name, k in [("f15", 15), ("f16", 16), ("f17", 17), ("f18", 18),
                    ("f19", 19), ("f20", 20), ("f25", 25), ("f40", 40)]:
        try:
            w, h, rows = decode(d, starts[k], k)
        except Exception as e:                                    # noqa: BLE001
            print(f"  {name}: decode fail {e}")
            continue
        opaque = collections.Counter(v for r in rows for v in r if v >= 0)
        top = sorted(opaque.items(), key=lambda kv: -kv[1])[:5]
        print(f"  {name} k{k:<3d} {w}x{h} distinct={len(opaque)} "
              + " ".join(f"idx{v}:{n}px->raw{raw[v]}conv{conv[v]}" for v, n in top))

    try:
        from PIL import Image
        import numpy as np
    except ImportError as e:                                      # noqa: BLE001
        print(f"(no PIL/numpy: {e})")
        return 0
    A = np.asarray(Image.open(REFCAP).convert("RGB"))
    print(f"\n== refcap {A.shape[1]}x{A.shape[0]}")

    print("\n== per-row dominant colours, x 470..640, y 395..479")
    for y in range(395, 480):
        strip = A[y, 470:640].reshape(-1, 3)
        cnt = collections.Counter(tuple(int(v) for v in s) for s in strip)
        top = cnt.most_common(4)
        s = " ".join(f"{c}:{k:3d}{('/' + ','.join(map(str, c2i[c])) + 'i') if c2i[c] else '/-'}"
                     for c, k in top)
        print(f"  y{y}: {s}")

    print("\n== per-column ink profile in each band (non-background columns)")
    # background = most common colour of the whole corner
    corner = A[395:480, 470:640].reshape(-1, 3)
    bg = collections.Counter(map(tuple, (tuple(int(v) for v in s) for s in corner))).most_common(1)[0][0]
    print(f"  corner bg = {bg} (pal {c2i.get(bg)})")
    for label, y0, y1 in [("toggles y403..433", 403, 434), ("race y442..472", 442, 473)]:
        band = A[y0:y1, 470:640]
        ink = (band != np.array(bg)).any(axis=2)
        cols = ink.any(axis=0)
        runs = []
        x = 0
        while x < len(cols):
            if cols[x]:
                j = x
                while j + 1 < len(cols) and cols[j + 1]:
                    j += 1
                runs.append((470 + x, 470 + j, j - x + 1))
                x = j + 1
            else:
                x += 1
        print(f"  {label}: {len(runs)} ink runs {runs[:12]}")
        rowsi = ink.any(axis=1)
        print(f"    ink rows y {y0 + (0 if rowsi.all() else rowsi.argmax())}..{y1 - 1 - (0 if rowsi.all() else rowsi[::-1].argmax())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
