#!/usr/bin/env python3
"""r1_t196_sheet.py — OQ-005 residue triage: partial renders + contact sheets.

Continues r1_t182_pngdump.py (which renders only fully-valid records). The 71
FAIL-class residue records are triaged STRUCTURALLY first (verified census,
docs/re/_wip_t196.md S1):
    EMPTY  (0 stream bytes)        -> not renderable; the report says EMPTY-SLOT
    TINY   (1..8 stream bytes)     -> not renderable meaningfully; reported TINY
    ART    (>8 stream bytes)       -> rendered PERMISSIVELY: the S9 row walk run
                                      to span exhaustion yields a row-prefix of
                                      the declared frame (tools/shp_partialdump.cpp).
NO candidate search (REFUTED-ROUTES R2 / GOAL: 7th blind sweep forbidden): dims
and stream-start come from the same S16/S17 slots ShapeLibrary::decode reads.
Codec CORRECTNESS is still not graded here (R13 law): vision is used for
IDENTIFICATION-BY-CONTEXT only (the t193 vision-oracle law), player ruling
still closes OQ-005.

Sheets written to <out>/sheets/ (each tile labelled 'lib kN WxH rows=NN'):
  sheet1_span_undersized  planind k0..k12 + 3cfgnew k0..k12 partial renders
  sheet2_stragglers       14intel k8, 1starmap k3/k4/k6, mouse k6/k7 partials
                          + same-lib PASSED neighbours for style context
  sheet3_ladder_planres_pro   planres k0..k20 + planpro k0..k20 (all pass)
  sheet4_gauges_context   planind passed k's (decode()), planitem sampled,
                          planets sampled, planal00 all

Run: ~/tools/revenv/bin/python scripts/r1_t196_sheet.py [--out work/r1/shp_png]
Exit 0 iff every sheet + every claimed render exists and reopens via PIL.
"""
import argparse
import collections
import glob
import importlib.util
import os
import struct
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    from PIL import Image, Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("PIL missing — run with ~/tools/revenv/bin/python")

_spec = importlib.util.spec_from_file_location(
    "unifiedlaw", os.path.join(ROOT, "scripts", "r1_shp_unifiedlaw.py"))
law = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(law)
# palette fix (t188: game.pal is 6-bit; v*255//63) lives in t182's loader
_spec2 = importlib.util.spec_from_file_location(
    "t182", os.path.join(ROOT, "scripts", "r1_t182_pngdump.py"))
# NOTE: importing t182 executes argparse at import?? No — it guards main()
# under __name__=="__main__"; safe to import for load_palette/find_lib.
t182 = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(t182)

UNDERSIZED = {"planind.shp", "3cfgnew.shp"}
SIMPLE = {"cos_star.shp"}


def find_lib(name):
    return t182.find_lib(name)


def residue():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "extracted", "**", "*.shp"),
                              recursive=True)):
        try:
            d, count, te, tsz, starts, ends = law.parse(p)
        except Exception:
            continue
        for k in range(count):
            if law.rec_state(d, k, starts[k], ends[k]) != "FAIL":
                continue
            rec, nxt = starts[k], ends[k]
            s_off = rec + 8 if k == 0 else rec + 0x18
            avail = max(0, nxt - s_off)
            klass = ("EMPTY" if avail == 0 else
                     "TINY" if avail <= 8 else "ART")
            out.append(dict(path=p, lib=os.path.basename(p), k=k,
                            avail=avail, klass=klass))
    return out


def run_partial(spec_pairs, out):
    """spec_pairs: list of (lib_path, k). -> dict (path,k) -> row-cols."""
    driver = os.path.join(ROOT, "tools", "shp_partialdump")
    lib_a = os.path.join(ROOT, "rewrite", "build", "libascend_core.a")
    if not (os.path.exists(driver) and os.path.exists(lib_a)):
        sys.exit("driver/lib missing — build rewrite/ then g++ -std=c++17 -O1 "
                 "-I rewrite/src -o tools/shp_partialdump "
                 "tools/shp_partialdump.cpp rewrite/build/libascend_core.a")
    os.makedirs(os.path.join(out, "raw_p"), exist_ok=True)
    spec_path = os.path.join(out, "_spec_partial.tsv")
    with open(spec_path, "w") as f:
        for p, k in spec_pairs:
            f.write(f"{p}\t{k}\n")
    proc = subprocess.run([driver, spec_path, out], capture_output=True,
                          text=True, timeout=600)
    if proc.returncode != 0:
        sys.exit(f"driver exit {proc.returncode}: {proc.stderr[:400]}")
    rows = {}
    for line in proc.stdout.splitlines():
        c = line.split("\t")
        if len(c) >= 8:
            rows[(c[0], int(c[1]))] = c
    return rows


def tile_from_plane(path, W, rows, pal, scale=2):
    img = Image.frombytes("P", (W, rows), open(path, "rb").read())
    img.putpalette(pal)
    return img.convert("RGB").resize((W * scale, rows * scale),
                                     Image.NEAREST)


def tile_from_valid(lib, k, pal, scale=2):
    """Full decode via rewrite ShapeLibrary (shp_pngdump driver)."""
    driver = os.path.join(ROOT, "tools", "shp_pngdump")
    os.makedirs(os.path.join(out_global, "raw"), exist_ok=True)
    spec = os.path.join(out_global, "_spec_one.tsv")
    open(spec, "w").write(f"{lib}\t{k}\n")
    proc = subprocess.run([driver, spec, out_global], capture_output=True,
                          text=True, timeout=120)
    c = proc.stdout.strip().split("\t")
    if len(c) < 8 or c[2] != "ok":
        return None
    W, H, sw = int(c[3]), int(c[4]), c[6]
    imgw, imgh = (H, W) if sw == "1" else (W, H)
    plane = open(os.path.join(out_global, c[7]), "rb").read()[:W * H]
    img = Image.frombytes("P", (W, H), plane)
    img.putpalette(pal)
    return img.convert("RGB").resize((imgw * scale, imgh * scale),
                                     Image.NEAREST)


FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
out_global = None


def make_sheet(tiles, path, cols, title):
    """tiles: list of (label, Image|None)."""
    lab_h = 16
    cw = 140
    chh = 140 + lab_h
    n = len(tiles)
    rws = (n + cols - 1) // cols
    W = cw * cols
    H = chh * rws + 22
    sheet = Image.new("RGB", (W, H), (24, 24, 28))
    dr = ImageDraw.Draw(sheet)
    dr.text((6, 4), title, fill=(235, 235, 240), font=ImageFont.truetype(FONT, 13))
    for idx, (label, im) in enumerate(tiles):
        r, c_ = divmod(idx, cols)
        x0, y0 = c_ * cw, r * chh + 22
        if im is not None:
            tw, th = im.size
            if tw > cw - 4 or th > 140 - 4:
                s2 = min((cw - 4) / tw, (140 - 4) / th)
                im = im.resize((max(1, int(tw * s2)), max(1, int(th * s2))),
                               Image.NEAREST)
                tw, th = im.size
            sheet.paste(im, (x0 + (cw - tw) // 2, y0 + (140 - th) // 2))
        else:
            dr.rectangle([x0 + 3, y0 + 3, x0 + cw - 4, y0 + 137],
                         outline=(120, 120, 130))
            dr.text((x0 + 8, y0 + 60), "NOT RENDERABLE", fill=(120, 120, 130),
                    font=ImageFont.truetype(FONT, 9))
        dr.text((x0 + 3, y0 + 141), label[:24], fill=(200, 210, 230),
                font=ImageFont.truetype(FONT, 9))
    sheet.save(path)
    back = Image.open(path)
    back.load()
    return os.path.getsize(path) > 0 and back.size == (W, H)


def main():
    global out_global
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "work", "r1",
                                                  "shp_png"))
    args = ap.parse_args()
    out = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
    out_global = out
    os.makedirs(os.path.join(out, "sheets"), exist_ok=True)
    pal = t182.load_palette()

    res = residue()
    art = [r for r in res if r["klass"] == "ART"]
    counts = collections.Counter(r["klass"] for r in res)

    # ---- render every ART record permissively (one driver batch)
    rows = run_partial([(r["path"], r["k"]) for r in art], out)
    report = ["# t196 residue triage report — structural class per record.",
              "# EMPTY=zero stream bytes, TINY<=8B, ART=rendered partial "
              "(rows_done = frame rows the span physically holds at declared W).",
              "# NO codec grading here (R13); identification lives in "
              "work/r1/shp_png/ids.tsv after the vision passes."]
    ok = True
    render_map = {}
    for r in res:
        c = rows.get((r["path"], r["k"]))
        base = r["lib"]
        if r["klass"] != "ART":
            report.append(f"{base:14s} k{r['k']:<3d} {r['klass']:6s} "
                          f"avail=0x{r['avail']:x}  not rendered")
            continue
        if c is None or c[2] != "ok":
            err = c[8] if c and len(c) > 8 else "no driver row"
            report.append(f"{base:14s} k{r['k']:<3d} ART    RENDER-FAIL {err}")
            continue  # honest negative: dims word invalid -> not guessed,
                      # not sheeted (ok stays True; triage is not a build)
        W, H, rows_done, rel = int(c[3]), int(c[4]), int(c[5]), c[7]
        png = os.path.join(out, "sheets",
                           f"partial--{base.rsplit('.',1)[0]}--k{r['k']}.png")
        tile_from_plane(os.path.join(out, rel), W, max(1, rows_done), pal,
                        scale=1).save(png)
        render_map[(base, r["k"])] = (png, W, H, rows_done)
        report.append(f"{base:14s} k{r['k']:<3d} ART    rows={rows_done}/{H} "
                      f"declared {W}x{H} avail=0x{r['avail']:x}")
    open(os.path.join(out, "sheets", "triage_report.txt"), "w").write(
        "\n".join(report) + "\n")

    # ---- sheet 1: span-undersized ART (planind + 3cfgnew)
    s1 = []
    for lib in ("planind.shp", "3cfgnew.shp"):
        for r in [x for x in res if x["lib"] == lib and x["klass"] == "ART"]:
            png, W, H, rd = render_map[(lib, r["k"])]
            s1.append((f"{lib[:-4]} k{r['k']} {W}x{H} rows={rd}",
                       Image.open(png).convert("RGB")))
    ok &= make_sheet(s1, os.path.join(out, "sheets",
                    "sheet1_span_undersized.png"), 7,
                    "SHEET1 span-undersized residues (partial prefix frames, "
                    "declared dims)")

    # ---- sheet 2: straggler ART + same-lib passed neighbours
    s2 = []
    STRAG = [("14intel.shp", [8]), ("1starmap.shp", [3, 4, 6]),
             ("mouse.shp", [6, 7])]
    for lib, ks in STRAG:
        p = find_lib(lib)
        for k in ks:
            if (lib, k) not in render_map:
                s2.append((f"{lib[:-4]} k{k} no-dims-word", None))
                continue
            png, W, H, rd = render_map[(lib, k)]
            s2.append((f"{lib[:-4]} k{k} {W}x{H} r={rd}",
                       Image.open(png).convert("RGB")))
        # context: two passed records from the same library
        d, count, te, tsz, starts, ends = law.parse(p)
        passed = [k for k in range(count)
                  if law.rec_state(d, k, starts[k], ends[k]) != "FAIL"][:2]
        for k2 in passed:
            im = tile_from_valid(p, k2, pal)
            s2.append((f"{lib[:-4]} k{k2} PASSED", im))
    ok &= make_sheet(s2, os.path.join(out, "sheets", "sheet2_stragglers.png"),
                     7, "SHEET2 straggler residues + PASSED neighbours "
                        "(same lib)")

    # ---- sheet 3: gauge ladders planres / planpro (all 21 each, record order)
    s3 = []
    for lib in ("planres.shp", "planpro.shp"):
        p = find_lib(lib)
        d, count, te, tsz, starts, ends = law.parse(p)
        for k in range(count):
            im = tile_from_valid(p, k, pal)
            s3.append((f"{lib[:-4]} k{k}", im))
    ok &= make_sheet(s3, os.path.join(out, "sheets",
                    "sheet3_ladder_planres_pro.png"), 8,
                    "SHEET3 gauge ladders, record order k0->k20 "
                    "(research / prosperity)")

    # ---- sheet 4: planind passed + planitem + planets + planal00 context
    s4 = []
    p = find_lib("planind.shp")
    d, count, te, tsz, starts, ends = law.parse(p)
    passed = [k for k in range(count)
              if law.rec_state(d, k, starts[k], ends[k]) != "FAIL"]
    for k in passed:
        s4.append((f"planind k{k} PASSED", tile_from_valid(p, k, pal)))
    for lib, step in (("planitem.shp", 4), ("planets.shp", 5),
                      ("planal00.shp", 1)):
        p = find_lib(lib)
        d, count, te, tsz, starts, ends = law.parse(p)
        for k in range(0, count, step):
            s4.append((f"{lib[:-4]} k{k}", tile_from_valid(p, k, pal)))
    ok &= make_sheet(s4, os.path.join(out, "sheets",
                    "sheet4_gauges_context.png"), 8,
                    "SHEET4 manufacturing(passed) + item/planet/alert art "
                    "context")

    print(f"residue={len(res)} {dict(counts)} rendered_art={len(render_map)}")
    print(f"report={out}/sheets/triage_report.txt")
    for s in ("sheet1_span_undersized", "sheet2_stragglers",
              "sheet3_ladder_planres_pro", "sheet4_gauges_context"):
        pp = os.path.join(out, "sheets", s + ".png")
        print(f"  {pp} {'OK' if os.path.exists(pp) else 'MISSING'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
