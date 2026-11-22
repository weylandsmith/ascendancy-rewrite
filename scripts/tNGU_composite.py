#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tNGU_composite — PHASE-17 tNG-U USER-GRADE PACKAGE ARTIFACT.

Side-by-side composite for the New Game screen: OUR render | vendor refcap,
plus a verdict strip generated from scripts/t441_screen_diff.py's own region
table (the strip re-runs t441 as a subprocess and parses its PASS/FAIL lines,
so the image can never disagree with the harness).

Deuteranopia law (user profile): verdicts are TEXT + SHAPE (P/F glyph in a
box), never colour alone. P-boxes and F-boxes differ in glyph AND fill
luminance, so the strip reads in greyscale.

Usage:
  ~/tools/revenv/bin/python scripts/tNGU_composite.py OURS.png VENDOR.png OUT.png
Exit 0 iff t441 exits 0 (the package ships green or not at all).
"""
import subprocess
import re
import sys

from PIL import Image, ImageDraw, ImageFont

PY = sys.executable
ROOT = "/home/hrethric/projects/ascendancy"

# Law-home map for the strip: region -> (law home, verdict note). Single
# source of truth = docs/re/t423-newgame-law.md section heads; keep in sync.
LAW_HOME = {
    "racelist-row0":            ("SS2/SS9/SS12 ring record", "dims-vs-cited"),
    "racelist-row0-portrait":   ("SS12 stretch site; measured-2x", "scale-source seam named"),
    "racelist-row1":            ("SS2/SS9/SS12 ring record", ""),
    "racelist-row2":            ("SS2/SS9/SS12 ring record", ""),
    "desc-ring":                ("SS6 racering k0", ""),
    "desc-portrait":            ("SS12 stretch site; measured-2x", ""),
    "desc-planet":              ("SS14 smhome k<race row>", "+-2 tol"),
    "playercolor-chiprow":      ("SS15 7 chips + pal ramp", "frame tracks +0xb5"),
    "chrome-topbar-rows1-6":    ("t433 chrome law; tA2 F1 exact-vs-gen", "mineral nuance D19-deferred"),
    "chrome-topbar-row0":       ("t433 chrome law instance", ""),
    "chrome-recess-row7":       ("t433; fam_min 0.89 (tNG-U polish)", "anim dither band"),
    "chrome-recess-col7":       ("t433 chrome law instance", ""),
    "chrome-recess-col493":     ("t433 chrome law instance", ""),
    "chrome-well-row8":         ("t433 chrome law instance", ""),
    "chrome-well-row372":       ("t433 chrome law instance", ""),
    "chrome-ridge-row373":      ("t433 ridge chain (tA2 M11 pinned)", ""),
    "chrome-ridge-row374":      ("t433 ridge chain (tA2 M11 pinned)", ""),
    "chrome-panel-top381":      ("t433 chrome law instance", ""),
}


def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(p, sz)
        except OSError:
            continue
    return ImageFont.load_default()


def run_t441(ours, vendor, log=None):
    cmd = [PY, f"{ROOT}/scripts/t441_screen_diff.py", "--screen", "newgame",
           ours, vendor]
    if log:
        cmd += ["--log", log]
    cp = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    rows = []
    pat = re.compile(r"^\s{2}(\S+)\s+ours\s+(.*?)\s*PASS\s*$|^\s{2}(\S+)\s+ours\s+(.*?)\s*FAIL\s*$")
    for line in cp.stdout.splitlines():
        m = pat.match(line)
        if m:
            name = m.group(1) or m.group(3)
            detail = (m.group(2) or m.group(4)).strip()
            rows.append((name, "P" if m.group(1) else "F", detail))
    return rows, cp.returncode


def main():
    if len(sys.argv) not in (4, 5, 6, 7):
        raise SystemExit(__doc__)
    argv = list(sys.argv[1:])
    checklist_p = None
    if "--checklist" in argv:
        i = argv.index("--checklist")
        checklist_p = argv[i + 1]
        del argv[i:i + 2]
    ours_p, vendor_p, out_p = argv[0:3]
    log_p = argv[3] if len(argv) > 3 else None
    rows, rc = run_t441(ours_p, vendor_p, log_p)
    if not rows:
        raise SystemExit("no t441 rows parsed — harness output shape changed")
    checklist = []
    if checklist_p:
        with open(checklist_p, encoding="utf-8") as fh:
            checklist = [ln.rstrip("\n") for ln in fh if ln.strip()]

    ours = Image.open(ours_p).convert("RGB")
    vendor = Image.open(vendor_p).convert("RGB")
    # normalise both to the 640x480 game rect (browser shots are 643x481)
    if vendor.size == (643, 481):
        vendor = vendor.crop((1, 1, 641, 481))  # == numpy im[1:481,1:641]
    if ours.size != (640, 480) or vendor.size != (640, 480):
        raise SystemExit(f"unexpected sizes {ours.size} {vendor.size}")

    f14, f18, f12 = font(14), font(18), font(12)
    f20 = font(20)
    gut, pad = 10, 12
    strip = 19 * len(rows) + 90
    # D20 usability correction: the PLAIN-LANGUAGE NUMBERED CHECKLIST rides
    # ON the composite (what changed / what to look at / what stays open).
    # wip docs are the machine record, never the grader's interface.
    import textwrap
    wrapped = []
    for ln in checklist:
        wrapped += textwrap.wrap(ln, width=110) or [""]
    list_h = 40 + 26 * len(wrapped) + 16 if wrapped else 0
    W, H = 640 * 2 + gut, 480 + 34 + strip + list_h
    canvas = Image.new("RGB", (W, H), (32, 32, 32))
    d = ImageDraw.Draw(canvas)
    # Checklist first (the grader reads this before the pixels).
    y = 10
    if wrapped:
        d.text((pad, y), "HOW TO GRADE THIS SCREEN (plain language):",
               font=f20, fill=(250, 250, 250))
        y += 34
        for ln in wrapped:
            d.text((pad + 6, y), ln, font=f14, fill=(235, 235, 235))
            y += 26
        y += 10
    img_top = y
    canvas.paste(ours, (0, img_top + 34))
    canvas.paste(vendor, (640 + gut, img_top + 34))
    d.text((8, img_top + 8), "OURS (port render, t412 canonical shot)",
           font=f18, fill=(235, 235, 235))
    d.text((640 + gut + 8, img_top + 8), "VENDOR (refcap crop)", font=f18,
           fill=(235, 235, 235))
    d.line([(640 + gut // 2, img_top), (640 + gut // 2, img_top + 480 + 34)],
           fill=(200, 200, 200), width=2)

    y = img_top + 480 + 34 + 6
    n_pass = sum(1 for _, v, _ in rows if v == "P")
    d.text((pad, y), f"t441 region table  {n_pass}/{len(rows)} PASS   "
                     f"(P = pass box, F = fail box — text+shape, greyscale-safe)",
           font=f14, fill=(235, 235, 235))
    y += 22
    for name, verdict, detail in rows:
        home, note = LAW_HOME.get(name, ("?", ""))
        box_fill = (70, 70, 70) if verdict == "P" else (185, 185, 185)
        glyph_fill = (250, 250, 250) if verdict == "P" else (20, 20, 20)
        d.rectangle([pad, y, pad + 16, y + 16], fill=box_fill,
                    outline=(250, 250, 250))
        d.text((pad + 3, y - 1), verdict, font=f14, fill=glyph_fill)
        d.text((pad + 24, y - 1), f"{name:<24}", font=f12, fill=(225, 225, 225))
        d.text((pad + 210, y - 1), f"{home:<38}", font=f12, fill=(170, 170, 170))
        d.text((pad + 470, y - 1), f"{detail} {note}", font=f12,
               fill=(170, 170, 170))
        y += 19
    canvas.save(out_p)
    print(f"COMPOSITE {out_p} {W}x{H}  {n_pass}/{len(rows)} PASS  t441 rc={rc}")
    sys.exit(rc)


if __name__ == "__main__":
    main()
