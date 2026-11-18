#!/usr/bin/env python3
"""t425c probe 2: per-button measurement of the four layer-toggle circles.

windows.txt (extracted/ascend00/windows.txt, tr -d '\\r') says the four
buttons ABOVE the race strip are
  TOGLANES    479,403..509,433 SHAPEFRAME 15 SENDMESSAGE 57 BUTTONSTATE 1
  TOGEMPIRE   518,403..548,433 SHAPEFRAME 16 SENDMESSAGE 60 BUTTONSTATE 0
  TOGSHIPS    557,403..587,433 SHAPEFRAME 17 SENDMESSAGE 58 BUTTONSTATE 1
  TOGCOLONIES 596,403..626,433 SHAPEFRAME 18 SENDMESSAGE 61 BUTTONSTATE 1
i.e. 30x30 rects at pitch 39 — NOT pitch 44, and NOT inside the race strip.
TOGEMPIRE is the only one whose declared default is OFF, so the refcap is a
natural experiment: if the vendor draws the OFF state differently (dimmed
glyph / different frame) button 2 must differ from buttons 1/3/4.

Prints, per rect: measured extent of the face background (conv pal 242),
the glyph colour histogram, glyph mean luminance, and an ASCII render of the
matching static .shp face so glyph identity is checked against pixels.
Read-only census; exit 0.
"""
import collections
import struct

LIB = "extracted/ascend01/data/1starmap.shp"
PAL = "extracted/ascend01/data/game.pal"
REFCAP = "docs/assets/refcap/original-strategic-map.png"
BTNS = [("TOGLANES", 479, 403, 15, 57, 1), ("TOGEMPIRE", 518, 403, 16, 60, 0),
        ("TOGSHIPS", 557, 403, 17, 58, 1), ("TOGCOLONIES", 596, 403, 18, 61, 1)]


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


def lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


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

    print("== A. measured extent of face-bg (conv pal242 = (12,32,48)) per band")
    bg = conv[242]
    for y0, y1, lbl in [(403, 434, "toggles"), (442, 473, "race strip")]:
        band = A[y0:y1, 460:640]
        m = (band == np.array(bg)).all(axis=2)
        cols = m.sum(axis=0)
        runs, x = [], 0
        while x < len(cols):
            if cols[x] > (y1 - y0) * 0.5:
                j = x
                while j + 1 < len(cols) and cols[j + 1] > (y1 - y0) * 0.5:
                    j += 1
                runs.append((460 + x, 460 + j, j - x + 1))
                x = j + 1
            else:
                x += 1
        rows = m.sum(axis=1)
        ry = [y0 + i for i, v in enumerate(rows) if v > 20]
        print(f"  {lbl}: {len(runs)} wide runs {runs}  rows {ry[:1]}..{ry[-1:]}")

    print("\n== B. per-button pixel census (rect from windows.txt, no offset)")
    for name, x0, y0, frame, msg, state in BTNS:
        crop = A[y0:y0 + 30, x0:x0 + 30].reshape(-1, 3)
        cnt = collections.Counter(tuple(v) for v in crop)
        glyph = [c for c in cnt if c != bg]
        gl = sum(lum(c) * cnt[c] for c in glyph) / max(1, sum(cnt[c] for c in glyph))
        tot = sum(cnt[c] for c in glyph)
        top = cnt.most_common(7)
        print(f"  {name:12s} x{x0} f{frame} msg{msg} STATE{state} "
              f"bg={cnt[bg]}/900 glyph_px={tot} glyph_lum={gl:.1f}")
        print("      " + " ".join(f"{c}:{n}{c2i.get(c, ['-'])}" for c, n in top))

    print("\n== C. static faces 15..18 (ASCII: '.'=242 bg, '#'=bright, '+'=mid, "
          "'-'=dark, 'R'=red 116..119, 'Y'=26)")
    for name, x0, y0, frame, msg, state in BTNS:
        w, h, rows = decode(d, starts[frame], frame)
        print(f"  {name} k{frame} {w}x{h} idxset="
              + ",".join(f"{v}" for v in sorted({v for r in rows for v in r if v >= 0})))
        for r in rows:
            line = ""
            for v in r:
                if v < 0:
                    line += " "
                elif v == 242:
                    line += "."
                elif 116 <= v <= 119:
                    line += "R"
                elif v == 26:
                    line += "Y"
                elif lum(conv[v]) > 170:
                    line += "#"
                elif lum(conv[v]) > 90:
                    line += "+"
                else:
                    line += "-"
            print("    |" + line + "|")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
