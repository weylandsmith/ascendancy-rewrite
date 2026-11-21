#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""t441_screen_diff — PHASE-17 G2 MECHANICAL REGION HARNESS (built tA1-CONT).

Per named region, in ONE pass over OUR render (640x480 Xvfb root grab, G5)
and the vendor refcap crop for the same screen (G1):

 1. DRAWN-DIMS-VS-CITED (the tA1 gate term). The port prints a one-shot
    line at every gated blit:  "ui dimscheck <name> W H x y"  where W,H are
    the record's CITED bbox dims (parsed under the bbox-diff law) and x,y
    the blit anchor law's destination (anchor + (L,T)). The harness crops
    that exact rect from our render and asserts the measured content bbox
    FILLS it: dims >= 0.85*cited and <= cited+2. The D19 quadrant signature
    (top-left slice of a 2x render, the port's old truncated dims read)
    measures ~0.5*cited and FAILS by construction.
 2. ART PRESENCE MASS on BOTH sides (vendor crop = ground truth that the
    region has art at all; ours = the render actually blits something).
 3. CITED-LADDER WITNESS on the vendor side for ladder regions (suns,
    planets size classes): the vendor's drawn bbox must sit on the cited
    ladder rung +- tol — evidence the SCALE law holds on the original.
    Cross-side dims EQUALITY is NOT asserted: the vendor crops come from
    different campaign states (resume.gam / user browser shots), so the
    CONTENT differs by design; content-index laws are tNG-C/tPL-C rows.

Region table below is the single home (later phase-17 rows EXTEND it).
Detectors are vendor-independent (same code both sides):
  greys  low-chroma mid-luminance (racering ring band)
  green  G-dominant (green selection ring)
  warm   R>G+25, G>=B-10 (suns discs)
  content opaque vs the flat base (navy panel / black interior)

Usage:
  ~/tools/revenv/bin/python scripts/t441_screen_diff.py --screen newgame \
      OURS.png VENDOR.png [--log app.log]
Exit 0 = every region PASS (gate green). --list lists regions.
"""
import argparse
import re
import sys

import numpy as np
from PIL import Image

# ---------------------------------------------------------------- ladders
# Cited record dims under the tA1 bbox-diff law (measured headers this
# session, scripts/ta1c_record_census.py over extracted/ascend01/data):
SUNS = {0: (127, 133), 1: (130, 127), 2: (128, 127), 3: (139, 142),
        4: (115, 114), 5: (113, 113), 6: (113, 110), 7: (113, 113),
        8: (107, 107), 9: (93, 94), 10: (78, 77), 11: (86, 89),
        12: (76, 77)}
PLANETS_SIZE = [24, 38, 52, 71, 95]  # size-axis ladder (tA1 F5)
RACERING = (109, 109)                # all 8 colour records
SMRACE = (100, 100)                  # content bbox of every smrace rec0

NAVY = np.array((12, 32, 48))
BLACK = np.array((0, 0, 0))


def load640(p):
    im = np.array(Image.open(p).convert("RGB"))
    if im.shape[:2] == (480, 640):
        return im
    if im.shape[0] == 481 and im.shape[1] == 643:  # browser shot +1,+1 rect
        return im[1:481, 1:641]
    if im.shape == (600, 800, 3):  # dosbox 800x600 root, game rect t417 F1
        return im[100:580, 80:720]
    raise SystemExit(f"{p}: not a 640x480 source ({im.shape}) — G5: Athens "
                     "512x384 shots are never pixel-scale evidence")


def bbox_of(mask, x0, y0):
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return (x0 + int(xs.min()), y0 + int(ys.min()), x0 + int(xs.max()),
            y0 + int(ys.max()), int(mask.sum()))


def detect(im, kind, x0, y0, x1, y1):
    reg = im[y0:y1 + 1, x0:x1 + 1].astype(int)
    mx = reg.max(axis=2)
    mn = reg.min(axis=2)
    if kind == "greys":
        return (mx - mn < 25) & (mx >= 35) & (mx <= 200)
    if kind == "green":
        return (reg[:, :, 1] > reg[:, :, 0] + 30) & \
               (reg[:, :, 1] > reg[:, :, 2] + 20) & (reg[:, :, 1] >= 60)
    if kind == "warm":
        return (reg[:, :, 0] > reg[:, :, 1] + 25) & \
               (reg[:, :, 1] >= reg[:, :, 2] - 10)
    if kind == "content":
        base = NAVY if _zone_base(im, x0, y0, x1, y1) else BLACK
        return (np.abs(reg - base).sum(axis=2) > 60) & (reg.sum(axis=2) > 30)
    raise SystemExit(f"unknown detector {kind}")


def _zone_base(im, x0, y0, x1, y1):
    c = np.array([im[y0 + 1, x0 + 1], im[y0 + 1, x1 - 1], im[y1 - 1, x0 + 1],
                  im[y1 - 1, x1 - 1]], int)
    return float(np.abs(c - NAVY).sum(axis=1).mean()) < 96.0


def ladder_ok(dims, tol=6):
    lad = [(s, s) for s in PLANETS_SIZE]
    return any(abs(dims[0] - w) <= tol and abs(dims[1] - h) <= tol
               for w, h in lad)


# ---------------------------------------------------------------- regions
# kind, vendor-rect (x0,y0,x1,y1), cited dims mode, per-side min mass,
# dimscheck name (ours side; None = vendor-witness-only region).
REGIONS = {
    "newgame": [
        # RACELIST rows: racering k7 ring + smrace disc, centre x559,
        # row centres y=107/215/323 (greys x506..511/608..612, t401 S8).
        dict(name="racelist-row0", vkind="greys", rect=(504, 52, 614, 162),
             cited=("fixed", RACERING), mass=(1200, 1200),
             dimscheck="racelist-row0-ring"),
        dict(name="racelist-row0-portrait", vkind="content",
             rect=(510, 58, 608, 156), cited=("fixed", SMRACE),
             mass=(1200, 1200), dimscheck="racelist-row0-portrait"),
        dict(name="racelist-row1", vkind="greys", rect=(504, 160, 614, 270),
             cited=("fixed", RACERING), mass=(1200, 1200),
             dimscheck="racelist-row1-ring"),
        dict(name="racelist-row2", vkind="greys", rect=(504, 268, 614, 378),
             cited=("fixed", RACERING), mass=(1200, 1200),
             dimscheck="racelist-row2-ring"),
        # DESC panel: green racering ring + portrait centre (409,97).
        dict(name="desc-ring", vkind="green", rect=(353, 41, 465, 153),
             cited=("fixed", RACERING), mass=(400, 400),
             dimscheck="desc-ring"),
        dict(name="desc-portrait", vkind="content", rect=(359, 47, 459, 147),
             cited=("fixed", SMRACE), mass=(1200, 1200),
             dimscheck="desc-portrait"),
        # DESC planet zone centre (401,218) on the size ladder. Content
        # index (which husk/biome) is tNG-C; scale is tA1.
        dict(name="desc-planet", vkind="content", rect=(377, 190, 427, 246),
             cited=("planets",), mass=(150, 150), dimscheck="desc-planet"),
        # ---- tA2-CONT CHROME-BAND REGIONS (tA2 law, docs/re/_wip_tA2.md
        # F3/F5/F7). kind="band": mean-lum window + census-family presence
        # on BOTH sides (vendor crop = ground truth). Windows are MEASURED
        # this session (scripts/r1_tA2c_bandprobe.py): ours vs vendor means
        # recess-row7 22.5/24.3, ridge373 64.4/64.5, ridge374 103.1/102.9,
        # panel-top381 29.5/31.6, rows1-6 60.5/72.3. Family = within
        # <=10/channel of a cited census top colour; fam_min = share of the
        # band covered by the TOP-3 census families (summed, so ridge rows
        # with 3 grey + 3 teal rungs score up to ~1.7). NO band region may
        # re-home the harness: rects are the cited well geometry
        # (kNewgameCosmosRect {8,8,492,372} + recess/ridge law).
        dict(name="chrome-topbar-rows1-6", kind="band",
             rect=(7, 1, 493, 6), mean=(66.4, 15.0), fam_min=None),
        # Row 0 excluded from the mean window ON PURPOSE: per-instance
        # chrome law (t433) — newgame instance vendor row0 mean 39.0 vs the
        # pinned map refcap 104.5; a mean window here would grade instance
        # noise, not law. Geometry-only: it must not be pure black.
        dict(name="chrome-topbar-row0", kind="band",
             rect=(7, 0, 493, 0), mean=(20.0, 220.0), fam_min=None),
        dict(name="chrome-recess-row7", kind="band",
             rect=(7, 7, 493, 7), mean=(23.4, 3.0),
             fam=[(24, 24, 24), (10, 10, 10), (21, 42, 35)], fam_min=0.90),
        dict(name="chrome-recess-col7", kind="band",
             rect=(7, 8, 7, 372), mean=(6.5, 2.5), fam_min=None),
        dict(name="chrome-recess-col493", kind="band",
             rect=(493, 8, 493, 372), mean=(21.0, 3.5), fam_min=None),
        dict(name="chrome-well-row8", kind="band",
             rect=(8, 8, 492, 8), mean=(0.0, 0.5), fam_min=None),
        dict(name="chrome-well-row372", kind="band",
             rect=(8, 372, 492, 372), mean=(0.0, 0.5), fam_min=None),
        dict(name="chrome-ridge-row373", kind="band",
             rect=(7, 373, 493, 373), mean=(64.5, 6.0),
             fam=[(61, 61, 61), (53, 78, 78), (48, 71, 73)], fam_min=1.40),
        dict(name="chrome-ridge-row374", kind="band",
             rect=(7, 374, 493, 374), mean=(103.0, 6.0),
             fam=[(97, 97, 97), (85, 125, 125), (77, 113, 117)],
             fam_min=1.30),
        # Panel-inset census band (tA2 inset law top line): GALAXY_MORE +
        # chips + Begin panels all show the dark inset family at row 381.
        dict(name="chrome-panel-top381", kind="band",
             rect=(7, 381, 493, 381), mean=(30.5, 4.5),
             fam=[(12, 24, 34), (12, 24, 36), (18, 31, 40)], fam_min=2.20),
    ],
    "planetslist": [
        # Row 0 (t427 laws): sun centre (80,121) suns ladder; planet
        # centre (215,110) planets ladder; x<=245 excludes the text col.
        dict(name="row0-sun", vkind="warm", rect=(8, 49, 152, 193),
             cited=("suns",), mass=(3000, 3000), dimscheck="row0-sun"),
        dict(name="row0-planet", vkind="content", rect=(165, 80, 245, 160),
             cited=("planets",), mass=(400, 400), dimscheck="row0-planet"),
    ],
}

DIMSCHECK_RE = re.compile(
    r"ui dimscheck (\S+) (\d+) (\d+) (-?\d+) (-?\d+)")


def parse_dimscheck(log_path):
    out = {}
    try:
        with open(log_path, errors="replace") as f:
            for line in f:
                m = DIMSCHECK_RE.search(line)
                if m and m.group(1) not in out:
                    out[m.group(1)] = tuple(int(g) for g in m.groups()[1:])
    except FileNotFoundError:
        pass
    return out


def run_screen(screen, ours_p, vendor_p, log_path):
    ours, vendor = load640(ours_p), load640(vendor_p)
    checks = parse_dimscheck(log_path) if log_path else {}
    ok = True
    print(f"== screen {screen}: ours={ours_p} vendor={vendor_p}")
    for rg in REGIONS[screen]:
        x0, y0, x1, y1 = rg["rect"]
        fails = []
        if rg.get("kind") == "band":
            # tA2-CONT chrome band: mean-lum window + census-family share
            # on BOTH sides. No dimscheck (chrome has no blit record).
            def band_stats(im):
                px = im[y0:y1 + 1, x0:x1 + 1].reshape(-1, 3).astype(int)
                m = float(px.mean(axis=1).mean())
                f = None
                if rg.get("fam"):
                    f = 0.0
                    for c in rg["fam"]:
                        d = np.abs(px - np.array(c)).sum(axis=1)
                        f += float((d <= 30).sum()) / len(px)
                return m, f
            mo, fo = band_stats(ours)
            mv, fv = band_stats(vendor)
            lo, tol = rg["mean"]
            if not (lo - tol <= mv <= lo + tol):
                fails.append(f"vendor mean {mv:.1f} outside cited "
                             f"{lo}+-{tol} (law witness broken?)")
            if not (lo - tol - 1.0 <= mo <= lo + tol + 1.0):
                fails.append(f"ours mean {mo:.1f} outside window "
                             f"{lo}+-{tol} (+-1 shot noise)")
            if rg.get("fam_min") is not None:
                if fv < rg["fam_min"]:
                    fails.append(f"vendor fam share {fv:.2f} < "
                                 f"{rg['fam_min']} (crop misaligned?)")
                if fo < rg["fam_min"]:
                    fails.append(f"ours fam share {fo:.2f} < "
                                 f"{rg['fam_min']} (census tables not "
                                 "drawing the family)")
            ok &= not fails
            print(f"  {rg['name']:<24} ours {mo:6.1f}/{'' if fo is None else f'{fo:.2f}'} "
                  f"vendor {mv:6.1f}/{'' if fv is None else f'{fv:.2f}'} "
                  f"{'PASS' if not fails else 'FAIL: ' + '; '.join(fails)}")
            continue
        # --- ours: dims-vs-cited via dimscheck declaration
        dv = None
        n_ours = 0
        dc = checks.get(rg["dimscheck"])
        if log_path:
            if dc is None:
                fails.append("no dimscheck line (render site not "
                             "instrumented / screen not reached)")
            else:
                W, H, bx, y = dc
                bb = bbox_of(detect(ours, "content" if rg["vkind"] !=
                                    "warm" else "warm", bx, y,
                                   bx + W - 1, y + H - 1), bx, y)
                if bb is None:
                    fails.append(f"declared rect {W}x{H}@({bx},{y}) EMPTY")
                else:
                    dv = (bb[2] - bb[0] + 1, bb[3] - bb[1] + 1)
                    n_ours = bb[4]
                    if dv[0] > W + 2 or dv[1] > H + 2:
                        fails.append(f"drawn {dv} OVERFLOWS cited {W}x{H}")
                    elif dv[0] < 0.85 * W or dv[1] < 0.85 * H:
                        fails.append(f"drawn {dv} QUADRANT/class slice of "
                                     f"cited {W}x{H}")
        # --- vendor: presence + ladder/fixed witness
        mv = detect(vendor, rg["vkind"], x0, y0, x1, y1)
        bb = bbox_of(mv, x0, y0)
        vv = None if bb is None else (bb[2] - bb[0] + 1, bb[3] - bb[1] + 1)
        if bb is None or bb[4] < rg["mass"][1]:
            fails.append(f"vendor art mass {bb[4] if bb else 0} < "
                         f"{rg['mass'][1]}")
        if bb is not None:
            mode = rg["cited"][0]
            if mode == "fixed":
                cw, chh = rg["cited"][1]
                if abs(vv[0] - cw) > 6 or abs(vv[1] - chh) > 6:
                    fails.append(f"vendor dims {vv} off cited {cw}x{chh}")
            elif mode == "suns":
                if not any(abs(vv[0] - w) <= 6 and abs(vv[1] - h) <= 6
                           for w, h in SUNS.values()):
                    fails.append(f"vendor sun dims {vv} not in suns ladder")
            elif mode == "planets":
                if not ladder_ok(vv):
                    fails.append(f"vendor planet dims {vv} off size ladder")
        # --- ours presence floor (independent of dimscheck)
        if n_ours < rg["mass"][0] and log_path:
            fails.append(f"ours art mass {n_ours} < {rg['mass'][0]}")
        ok &= not fails
        print(f"  {rg['name']:<24} ours {dv} n={n_ours:<6} vendor {vv} "
              f"n={bb[4] if bb else 0:<6} "
              f"{'PASS' if not fails else 'FAIL: ' + '; '.join(fails)}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--screen")
    ap.add_argument("--log")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("shots", nargs="*")
    a = ap.parse_args()
    if a.list:
        for k, v in REGIONS.items():
            print(k, [r["name"] for r in v])
        return 0
    if not a.screen or len(a.shots) != 2 or a.screen not in REGIONS:
        ap.print_help()
        return 2
    return 0 if run_screen(a.screen, a.shots[0], a.shots[1], a.log) else 1


if __name__ == "__main__":
    sys.exit(main())
