#!/usr/bin/env python3
"""r1_t182_pngdump.py — OQ-005 shape-PNG evidence dumper (t182).

Ships EVIDENCE for the player's closure ruling on the 80-record dims-location
residue (docs/BLOCKED.md t68, docs/re/shp.md S16/S17). This tool does NOT
grade correctness of any frame: R13 + strict-close mean only the player's
eyeball closes OQ-005. What the tool guarantees is narrower and checkable:

  1. Every rendered PNG came out of the rewrite's OWN decoder
     (ascend::formats::ShapeLibrary via tools/shp_pngdump.cpp, linked against
     rewrite/build/libascend_core.a) — not a second guess at the codec.
  2. NO candidate search (GOAL.txt: a 7th blind .shp codec sweep is FORBIDDEN;
     docs/REFUTED-ROUTES.md R2). Dims = S16/S17 V/A slots, stream = uniform
     law; uninterpretable dims are reported as decode failures verbatim.
  3. Each PNG is validated by this tool: file exists, non-empty, decodes back
     through PIL, dimensions match the decoder's reported W/H (or W/H of the
     swapped plane, flagged), and >=1 non-background pixel.

Sets rendered:
  CONTROLS  — 5 records from verbatim-verified / every-record-passing libs
              spanning size classes:
                17np.shp k0   639x479  full-screen panel (LARGE)
                dkship20 k3   314x222  capital-ship sprite (k>=1 law)
                racering k0    53x53   S17 RAM-table-verified lib
                listbox  k1    24x24   S17-verified, k>=1 small UI
                bullet04 k0     10x11  S17-verified, smallest class
  RESIDUE   — all FAIL-class records per the re-run of
              scripts/r1_shp_unifiedlaw.py, grouped in index.txt by the three
              banked classes (span-undersized planind/3cfgnew, simple-format
              cos_star, stragglers). Most will legitimately fail to render —
              the report column IS the evidence for the class diagnosis.

Palette: extracted/ascend01/data/game.pal (256xRGB, 768 B). This choice is an
UNVERIFIED DEFAULT, stated in index.txt — palette identity for .shp shape sets
was never measured, and the player should treat washed-out colour as
palette-noise, not shape evidence.

Run (PIL is only in ~/tools/revenv):
    ~/tools/revenv/bin/python scripts/r1_t182_pngdump.py [--out work/r1/shp_png]
Exit 0 iff every RENDERED png validated; decode failures never fail the run.
"""
import argparse
import collections
import glob
import importlib.util
import os
import subprocess
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    from PIL import Image
except ImportError:
    sys.exit("PIL missing — run with ~/tools/revenv/bin/python (PIL 12.x verified)")

# law source (read-only import; same parse/rec_state the ledger numbers came from)
_spec = importlib.util.spec_from_file_location(
    "unifiedlaw", os.path.join(ROOT, "scripts", "r1_shp_unifiedlaw.py"))
law = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(law)

CONTROLS = [  # (library relative path, record, why chosen)
    ("17np.shp", 0, "639x479 full-screen panel — LARGE class"),
    ("dkship20.shp", 3, "314x222 capital-ship sprite — k>=1/A-law class"),
    ("racering.shp", 0, "53x53 — S17 live-RAM-table-verified lib"),
    ("listbox.shp", 1, "24x24 — S17-verified small UI, k>=1"),
    ("bullet04.shp", 0, "10x11 — smallest size class, S17-verified lib"),
]
# Snapshot, cited: the 10 k==0 records the t182 validator off-by-8 fix
# promoted FAIL->V (scripts/r1_shp_unifiedlaw.py:49 comment; shp.md S18).
# They are banked here as a set so the evidence packet survives re-runs;
# the dumper still decodes them live (any failure shows as DECODE-FAIL).
RESTORED = [("10status.shp", 0), ("2savegam.shp", 0), ("4loadgam.shp", 0),
            ("planpro.shp", 0), ("planres.shp", 0), ("smship11.shp", 0),
            ("smship15.shp", 0), ("lgrace07.shp", 0), ("lgrace09.shp", 0),
            ("lgrace10.shp", 0)]
UNDERSIZED = {"planind.shp", "3cfgnew.shp"}   # shp.md S16 class a
SIMPLE = {"cos_star.shp"}                     # shp.md S16 class b


def find_lib(name):
    hits = sorted(glob.glob(os.path.join(ROOT, "extracted", "**", name),
                            recursive=True))
    if not hits:
        sys.exit(f"library not found in extracted/: {name}")
    return hits[0]


def residue_records():
    """Re-derive the FAIL set live (never a hard-coded snapshot).
    t197: also returns the X set (span-free decodes) so the packet shows
    what the corrected law renders, FAIL and X side by side."""
    out = []
    xset = []
    tally = collections.Counter()
    for p in sorted(glob.glob(os.path.join(ROOT, "extracted", "**", "*.shp"),
                              recursive=True)):
        try:
            d, count, te, tsz, starts, ends = law.parse(p)
        except Exception:
            continue
        for k in range(count):
            tag = law.rec_state(d, k, starts[k], ends[k])
            tally[tag] += 1
            if tag == "FAIL":
                out.append((p, k, ends[k] - starts[k]))
            elif tag in ("X", "XS"):
                xset.append((p, k, ends[k] - starts[k]))
    return out, xset, tally


def load_palette():
    raw = open(os.path.join(ROOT, "extracted", "ascend01", "data",
                            "game.pal"), "rb").read()
    assert len(raw) == 768, f"game.pal size {len(raw)} != 768"
    # t188 FIX: game.pal is a 6-bit VGA palette (measured max byte 0x3f, 0/256
    # entries with any channel > 0x3f). Feeding it raw to putpalette() capped
    # every render at 25% brightness — player eyeball (2026-10-29): "They're
    # all too dark, INCLUDING the controls." Scale 6->8 bit (v*255//63).
    return list(min(255, v * 255 // 63) for v in raw)  # RGB triplets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "work", "r1", "shp_png"))
    args = ap.parse_args()
    out = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
    os.makedirs(os.path.join(out, "raw"), exist_ok=True)

    driver = os.path.join(ROOT, "tools", "shp_pngdump")
    lib_a = os.path.join(ROOT, "rewrite", "build", "libascend_core.a")
    if not (os.path.exists(driver) and os.path.exists(lib_a)):
        sys.exit("driver/lib missing — build rewrite/ first "
                 "(cmake --build rewrite/build) then "
                 "g++ -std=c++17 -O1 -I rewrite/src -o tools/shp_pngdump "
                 "tools/shp_pngdump.cpp rewrite/build/libascend_core.a")

    residue, xset, tally = residue_records()
    sets = []  # (kind, lib_path, rec, note)
    for name, k, why in CONTROLS:
        sets.append(("CONTROL", find_lib(name), k, why))
    for name, k in RESTORED:
        sets.append(("RESTORED-V", find_lib(name), k,
                     "t182 off-by-8 fix: canonical V law, was false FAIL"))

    # t197: X-class records render through decode() now (span-free walk);
    # they lead the packet as their own set.
    for p_, k, span in xset:
        sets.append(("SPAN-FREE", p_, k,
                     f"X-class (span-free law), span={span}"))

    def cls_of(base):
        return ("span-undersized" if base in UNDERSIZED else
                "simple-format" if base in SIMPLE else "straggler")
    # grouped by the three banked S16 classes, per the t182 assignment
    for cls in ("span-undersized", "simple-format", "straggler"):
        for p, k, span in residue:
            base = os.path.basename(p)
            if cls_of(base) != cls:
                continue
            sets.append((f"RESIDUE-{cls}", p, k, f"FAIL-class, span={span}"))

    spec_path = os.path.join(out, "_spec.tsv")
    with open(spec_path, "w") as f:
        for _, p, k, _ in sets:
            f.write(f"{p}\t{k}\n")
    proc = subprocess.run([driver, spec_path, out], capture_output=True,
                          text=True, timeout=300)
    if proc.returncode != 0:
        sys.exit(f"driver exit {proc.returncode}: {proc.stderr[:400]}")
    rows = {}
    for line in proc.stdout.splitlines():
        c = line.split("\t")
        rows[(c[0], int(c[1]))] = c

    pal = load_palette()
    index = []
    index.append("# t182 OQ-005 shape-PNG evidence dump — NO self-grading here.")
    index.append("# Renderer: rewrite ShapeLibrary (S9 grammar, S16/S17 V/A "
                 "dims+stream law).")
    index.append("# Palette: extracted/ascend01/data/game.pal — UNVERIFIED "
                 "default; judge SHAPE, not colour.")
    index.append(f"# Law snapshot this run: {dict(tally)} (re-derived from "
                 "scripts/r1_shp_unifiedlaw.py, 208 libs)")
    index.append("#")
    index.append("# status: RENDERED(<WxH>,stride,stride,swapped,validated) | "
                 "DECODE-FAIL(report is the evidence) | PNG-BAD")
    index.append("# t197: walk bound = FILE, not directory span (shp.md S21; "
                 "blit has no length arg, cache verbatim). SPAN-FREE set = X "
                 "records the old bound refused; XREC--*.png are full frames "
                 "(planind factory ladder, 3cfgnew race-config art). Past-span "
                 "rows desync into the next record and paint (r1_t197_"
                 "pastrows.py) — bottom bands of SPAN-FREE renders are NOT "
                 "vendor art, judge the upper rows.")
    n_rendered = n_valid = n_fail = 0
    ok = True
    for kind, p, k, note in sets:
        c = rows.get((p, k))
        base = os.path.basename(p)
        if c is None:
            index.append(f"{kind:22s} {base}--{k:<3d} NO-DRIVER-ROW")
            ok = False
            continue
        status, W, H, stride, sw = c[2], int(c[3]), int(c[4]), int(c[5]), c[6]
        if status == "fail":
            n_fail += 1
            index.append(f"{kind:22s} {base}--{k:<3d} DECODE-FAIL  {c[8]}  "
                         f"({note})")
            continue
        n_rendered += 1
        # Plane geometry per decode() contract: canonical = H rows of stride W
        # (image WxH); swapped = W rows of stride H (image HxW).
        imgw, imgh = (H, W) if sw == "1" else (W, H)
        stem = base.rsplit('.', 1)[0]
        prefix = ("CONTROL--" if kind == "CONTROL" else
                  "RESTORED--" if kind == "RESTORED-V" else
                  "XREC--" if kind == "SPAN-FREE" else "")
        png_name = f"{prefix}{stem}--rec{k}--{imgw}x{imgh}.png"
        png_path = os.path.join(out, png_name)
        plane = open(os.path.join(out, c[7]), "rb").read()
        # plane holds W*H bytes; canonical stride=W rows of H, swapped stride=H
        # rows of W (decode() contract in shp.h).
        good = len(plane) >= W * H
        if not good:
            index.append(f"{kind:22s} {png_name} PNG-BAD plane {len(plane)}B "
                         f"< {W * H}B")
            ok = False
            continue
        img = Image.frombytes("P", (W, H), plane[:W * H])
        img.putpalette(pal)
        # Skipped/clamped bytes are whatever decode left (zero-filled fresh
        # vector in the driver), so index 0 is the honest underlay render.
        img.save(png_path)
        # self-validate: reopen, size, non-empty
        back = Image.open(png_path)
        back.load()
        hist = back.convert("P").getcolors(maxcolors=256) or []
        nonbg = sum(n for i, n in hist if i != 0)
        valid = (os.path.getsize(png_path) > 0 and back.size == (imgw, imgh)
                 and nonbg >= 1)
        if valid:
            n_valid += 1
        else:
            ok = False
        vtag = f"VALIDATED nonbg={nonbg}" if valid else "PNG-BAD"
        index.append(f"{kind:22s} {png_name} RENDERED({W}x{H},"
                     f"stride={stride},swapped={sw}) {vtag}  ({note})")
    index.append("#")
    index.append(f"# rendered={n_rendered} validated={n_valid} "
                 f"decode-fail={n_fail} residue-total={len(residue)}")
    open(os.path.join(out, "index.txt"), "w").write("\n".join(index) + "\n")
    print(f"out={out}")
    print(f"sets={len(sets)} rendered={n_rendered} validated={n_valid} "
          f"decode-fail={n_fail} (residue {len(residue)})")
    print(f"law snapshot: {dict(tally)}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
