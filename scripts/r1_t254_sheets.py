#!/usr/bin/env python3
"""r1_t254_sheets.py — t254 population-slot library + planitem ruling sheets.

Renders candidate libraries with the rewrite's OWN decoder (tools/shp_pngdump,
S16/S17 V/A dims law) on the corrected 6-bit palette (v*255//63, t188 fix) and
assembles labelled contact sheets for IDENTIFICATION-BY-CONTEXT (t193 vision
oracle law). R13: no self-grading of codec correctness here.

Sheets (work/r1/shp_png/sheets/):
  t254_A_planets      planets.shp all 55 recs (dims-ladder order = file order)
  t254_B_planitem     planitem.shp all 40 recs
  t254_C_iconcands    the <=10px-pitch candidates: bullet04, shipicon, 14intel,
                      listbox, 17np, mouse  (pop-slot library must fit the
                      PLPOP 0x0a pitch — see docs/re/_wip_t254.md S1)
  t254_D_planal00     planal00.shp all 5 recs (size ladder, pose theory dead)

Run: ~/tools/revenv/bin/python scripts/r1_t254_sheets.py
Exit 0 iff every sheet exists and reopens via PIL.
"""
import importlib.util
import os
import struct
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("PIL missing — run with ~/tools/revenv/bin/python")

_spec = importlib.util.spec_from_file_location(
    "unifiedlaw", os.path.join(ROOT, "scripts", "r1_shp_unifiedlaw.py"))
law = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(law)
_spec2 = importlib.util.spec_from_file_location(
    "t182", os.path.join(ROOT, "scripts", "r1_t182_pngdump.py"))
t182 = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(t182)

OUT = os.path.join(ROOT, "work", "r1", "shp_png")
SHEETS = os.path.join(OUT, "sheets")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DRIVER = os.path.join(ROOT, "tools", "shp_pngdump")


def data_dir():
    return os.path.join(ROOT, "extracted", "ascend01", "data")


def render(lib, recs, tag):
    """-> dict rec -> (W,H,plane_bytes) via the rewrite decoder."""
    p = os.path.join(data_dir(), lib)
    spec = os.path.join(OUT, f"_spec_t254_{tag}.tsv")
    with open(spec, "w") as f:
        for k in recs:
            f.write(f"{p}\t{k}\n")
    proc = subprocess.run([DRIVER, spec, OUT], capture_output=True,
                          text=True, timeout=600)
    if proc.returncode != 0:
        sys.exit(f"driver exit {proc.returncode}: {proc.stderr[:400]}")
    out = {}
    for line in proc.stdout.splitlines():
        c = line.split("\t")
        if len(c) >= 8 and c[2] == "ok":
            W, H, sw = int(c[3]), int(c[4]), c[6]
            plane = open(os.path.join(OUT, c[7]), "rb").read()
            out[int(c[1])] = (W, H, sw, plane)
    return out


def tile(lib, k, W, H, sw, plane, pal, scale=2):
    # t182 convention: swapped means the plane's stored orientation is (H,W)
    w_px, h_px = (H, W) if sw == "1" else (W, H)
    img = Image.frombytes("P", (w_px, h_px), plane[:w_px * h_px])
    img.putpalette(pal)
    return img.convert("RGB").resize((w_px * scale, h_px * scale),
                                     Image.NEAREST)


def sheet(name, items, pal, cols=8, pad=6, label_h=26):
    """items: list of (label, Image|None)."""
    if not items:
        print(f"sheet {name}: EMPTY ITEM LIST")
        return False
    cells = []
    for lab, im in items:
        cw = max(im.width if im else 40, 40)
        ch = max(im.height if im else 40, 40)
        cells.append((lab, im, cw, ch))
    rows = [cells[i:i + cols] for i in range(0, len(cells), cols)]
    row_hs = [max(c[3] for c in r) + label_h for r in rows]
    W = sum(max(c[2] for c in r) + pad for r in rows) + pad
    Htot = sum(row_hs) + pad * (len(rows) + 1)
    canvas = Image.new("RGB", (W, Htot), (24, 24, 24))
    dr = ImageDraw.Draw(canvas)
    try:
        font = __import__("PIL.ImageFont", fromlist=["ImageFont"]).truetype(FONT, 13)
    except Exception:
        font = None
    y = pad
    for r, rh in zip(rows, row_hs):
        x = pad
        for lab, im, cw, ch in r:
            dr.text((x + 2, y + 2), lab, fill=(255, 255, 0), font=font)
            if im:
                canvas.paste(im, (x + (cw - im.width) // 2,
                                  y + label_h + (rh - label_h - im.height) // 2))
            dr.rectangle([x, y, x + cw + pad, y + rh], outline=(90, 200, 255))
            x += cw + pad
        y += rh + pad
    path = os.path.join(SHEETS, name)
    canvas.save(path)
    ok = True
    try:
        Image.open(path).verify()
    except Exception:
        ok = False
    print(f"sheet {name}: {W}x{Htot} items={len(items)} reopen_ok={ok}")
    return ok


def main():
    os.makedirs(SHEETS, exist_ok=True)
    pal = t182.load_palette()
    all_ok = True

    def items_of(lib, tag):
        p = os.path.join(data_dir(), lib)
        d, count, te, tsz, starts, ends = law.parse(p)
        rendered = render(lib, range(count), tag)
        its = []
        for k in range(count):
            d_off = starts[k] if k == 0 else starts[k] + 0x10
            W, H = struct.unpack_from("<II", d, d_off)
            if k in rendered:
                W2, H2, sw, plane = rendered[k]
                its.append((f"{lib[:-4]} k{k} {W}x{H}",
                            tile(lib, k, W2, H2, sw, plane, pal)))
            else:
                its.append((f"{lib[:-4]} k{k} {W}x{H} DECODE-FAIL", None))
        return its

    all_ok &= sheet("t254_A_planets.png", items_of("planets.shp", "planets"), pal)
    all_ok &= sheet("t254_B_planitem.png", items_of("planitem.shp", "planitem"), pal, cols=5)
    cands = []
    for lib in ("bullet04.shp", "shipicon.shp", "14intel.shp",
                "listbox.shp", "17np.shp", "mouse.shp"):
        try:
            cands += items_of(lib, lib.replace(".shp", ""))
        except SystemExit:
            raise
        except Exception as e:
            print(f"  {lib}: {e}")
    all_ok &= sheet("t254_C_iconcands.png", cands, pal, cols=6)
    all_ok &= sheet("t254_D_planal00.png", items_of("planal00.shp", "planal"), pal, cols=5)
    print("ALL_OK" if all_ok else "SHEET-VALIDATION-FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
