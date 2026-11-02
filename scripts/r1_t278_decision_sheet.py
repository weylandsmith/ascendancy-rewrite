#!/usr/bin/env python3
"""t278 OQ-005 RULING PACKAGE — build the DECISION SHEET.

Inputs (all on disk, nothing regenerated from binaries):
  work/r1/shp_png/index_t278pristine.txt  the t197-era evidence-dump index,
      banked verbatim as the record census this iteration (the t182 dumper
      scripts/r1_t182_pngdump.py WRITES index.txt on every run, so the sheet's
      canonical copy lives in decision-sheet.md; index.txt keeps only a pointer).
  work/r1/shp_png/ids.tsv            t196 per-record vision identifications.

Output:
  work/r1/shp_png/decision-sheet.md  one row per record the user must rule on
      (or that is restated for completeness), with cited identification, the
      user's Oct-29 verdict verbatim where it applies, and a one-line
      keep / junk / re-render recommendation. R13: the recommendation is a
      RECOMMENDATION — the user rules; nothing here closes a row by itself.

The user-quote and citation tables below are transcribed from:
  - the user's Oct-29 message (session 20261022_024226_01e8e7 msg 40813),
  - docs/re/shp.md S19 (t189b), S20 (t196), S21 (t197), S21 selectedness fold,
  - docs/re/planets-ui.md S5.1 (selection census), S6 (cos_star selector law),
  - docs/BLOCKED.md t68 (the ask).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PK = os.path.join(ROOT, "work", "r1", "shp_png")

# ---------------------------------------------------------------- user quotes
Q = {
"all_real": '"As for the OQ-005 items - it\'s a mixed bag. They are all real '
            'images with varying degrees of recongnizability." (Oct-29 msg 40813)',
"dark":     '"They\'re all too dark, including the controls." (Oct-29 msg 40813)',
"dkship":   '"Screenshot_2026-10-28_23-54-59.png - CONTROL--dkship20--rec3--'
            '314x222.png displayed next to a similar picture in the game, a ship '
            'in the shipbuilder interface" (Oct-29 msg 40813)',
"lg_corr":  '"Screenshot_2026-10-29_00-03-17.png - RESTORED--lgrace10--rec0--'
            '296x199.png displayed next to the same picture in the game, the '
            'Govorom race image, with the color curve approximately corrected" '
            '(Oct-29 msg 40813)',
"lg_plain": '"Screenshot_2026-10-29_00-03-36.png - RESTORED--lgrace10--rec0--'
            '296x199.png displayed next to the same picture in the game, the '
            'Govorom race image, no correction" (Oct-29 msg 40813)',
"triad":    '"RESTORED--10status--rec0--639x479.png, RESTORED--2savegam--rec0--'
            '639x479.png, RESTORED--4loadgam--rec0--639x479.png - an interface '
            'I\'ve never seen in-game, it\'s a different style than what the game '
            'gives. Possibly junk data." (Oct-29 msg 40813)',
"lg07":     '"RESTORED--lgrace07--rec0--296x199.png - Swaparamans race image." (Oct-29 msg 40813)',
"lg09":     '"RESTORED--lgrace09--rec0--296x199.png - Shevar race image." (Oct-29 msg 40813)',
"lg10":     '"RESTORED--lgrace10--rec0--296x199.png - Govorom race image." (Oct-29 msg 40813)',
"lg_places":'"(The race images are displayed in 2-3 places I can think of offhand '
            '- in the race description screen when you start a new game, in the '
            'diplomacy screen, and a cropped version is displayed in a circle in '
            'the new game screen - I\'m not sure if that\'s a crop of these images, '
            'or if there is a separate cropped version used for the new game '
            'screen.)" (Oct-29 msg 40813)',
"planpro":  '"RESTORED--planpro--rec0--107x99.png - seems to be some kind of '
            'nature image? I don\'t recognize it, but it\'s pretty nondescript, I '
            'might not notice something like that in the game." (Oct-29 msg 40813)',
"planres":  '"RESTORED--planres--rec0--107x99.png - seems like another background '
            'image, maybe space or a nebula? Again pretty nondescript." (Oct-29 msg 40813)',
"sm11":     '"RESTORED--smship11--rec0--45x30.png - as the filename implies, is a '
            'small image of a ship." (Oct-29 msg 40813)',
"sm15":     '"RESTORED--smship15--rec0--39x6.png - is so small and low-res as to '
            'be unrecognizable. There\'s something there. The filename implies '
            'that it\'s another small ship image." (Oct-29 msg 40813)',
"revoked":  'SUPERSEDED by the same user Oct-29 (shp.md S19/S20, t193 update): '
            'planpro/planres recognition REVOKED-then-RESTORED - they are planet-UI '
            'gauge BACKDROPS (planres nebula = research gauge, planpro nature = '
            'prosperity gauge).',
}

# ------------------------------------------------- per-library law + citations
# fields: (identification with citations, user-status, recommendation base)
LAW = {
"CONTROL": (
  "control set - libraries whose decode is RAM-table-verified (shp.md S17); "
  "rendered bright (6-bit palette fixed, shp.md S19).",
  "shown Oct-29; verdicts above apply.",
  "KEEP - controls; decoder-correct on this evidence."),
"10status": (
  "menu/interface panel 639x479; genuine filename+decode (shp.md S19 style "
  "anomaly note).",
  "user triad quote: never seen in-game, different style, 'Possibly junk data'.",
  "KEEP pending one confirmation - do NOT delete on non-recognition alone "
  "(shp.md S19 explicit law); re-check the SVGA/unused-menu-art candidate."),
"2savegam": ("menu/interface panel 639x479 (same class as 10status).",
  "user triad quote (above).",
  "KEEP pending confirmation - same rule as 10status."),
"4loadgam": ("menu/interface panel 639x479 (same class as 10status).",
  "user triad quote (above).",
  "KEEP pending confirmation - same rule as 10status."),
"lgrace07": ("race-07 portrait = Swaparamans (species.md law, user-verified).",
  Q["lg07"], "KEEP - user-identified."),
"lgrace09": ("race-09 portrait = Shevar (species.md law, user-verified).",
  Q["lg09"], "KEEP - user-identified."),
"lgrace10": ("race-10 portrait = Govorom (species.md law, user-verified).",
  Q["lg10"] + " Comparison shots: " + Q["lg_corr"] + "; " + Q["lg_plain"],
  "KEEP - user-identified; comparison shots corroborate match in-game."),
"planpro":  ("prosperity-gauge BACKDROP + ladder k0..k20 (gaugeSelector(PROS); "
             "shp.md S20 vision MONOTONIC bare-grass->flowering-bush).",
             Q["planpro"] + " " + Q["revoked"],
             "KEEP - identified as prosperity gauge art."),
"planres":  ("research-gauge BACKDROP + ladder k0..k20 (gaugeSelector(RES); "
             "shp.md S20 vision MONOTONIC triangle->dense faceted sphere).",
             Q["planres"] + " " + Q["revoked"],
             "KEEP - identified as research gauge art."),
"smship11": ("small ship sprite 45x30.", Q["sm11"], "KEEP - user-recognised."),
"smship15": ("small ship sprite 39x6.", Q["sm15"],
             "KEEP - user verdict 'all real'; nothing to act on."),
"planind":  ("MANUFACTURING gauge ladder CONFIRMED (shp.md S20: factory on red "
             "soil, +1 grey tank per level k8->k12, vision); addressed by "
             "gaugeSelector(IND) 0..20 (planets-ui.md S5.1) - ALL of k0..k12 "
             "ARE drawn in play (placeholder reading REFUTED).",
             "not shown individually as full frames; partials in "
             "sheets/sheet1_span_undersized.png (Oct-1, DARK palette).",
             "KEEP + needs your ruling - these 13 are real drawn gauge frames; "
             "confirm they look like the manufacturing gauge."),
"3cfgnew":  ("new-game/race-configuration art (sheets/vision: dot-wheel menus "
             "k0-4,k7-9; heraldic shields k5-6; glowing orbs k10-12); windows.txt "
             "SHAPEITEM selects k0 only (planets-ui.md S5.1).",
             "not shown individually; partials in sheets/sheet1_span_undersized.png.",
             "KEEP - real UI art; k12 is the one EXCEPTION, see its row."),
"1starmap": ("star-map sprites + buttons (vision: k3 green ship, k4 blue ship, "
             "k6 golden canisters; PASSED neighbours carry 'NEXT TURN <ENTER>'); "
             "windows.txt SHAPEITEM selects k3,k4,k5,k7 (planets-ui.md S5.1).",
             "not shown individually; partials in sheets/sheet1_span_undersized.png.",
             "KEEP + needs your ruling on k3/k4/k6 (k3/k4 are SELECTED in play)."),
"14intel":  ("intel-panel sprite set (ids.tsv: neighbours = mood faces; this rec "
             "= red spark partial).",
             "not shown individually; partials in sheets/sheet1_span_undersized.png.",
             "KEEP - needs your glance only."),
"cos_star": ("star-map pip library, COSMOSWnd STAR_SHAPES (windows.txt:208). "
             "SELECTOR LAW t200 (planets-ui.md S6): SEL = 4*star_type + cls at "
             "0x298dc; star_type census 0..12 => k40..k51 addressable-but-"
             "dims-zero; k52..k54 unreachable. Blit on dims 0 hits error -1 "
             "missing dims @0x5cb2b (shp.md S12).",
             "no render possible (dims word 0); never shown.",
             "KEEP as never-drawn placeholder slots - do NOT junk the records; "
             "rule only whether 'never drawn' is acceptable to close the class."),
"mouse":    ("cursor/button set (vision: arrows on PASSED k0/k1; k6 shows an "
             "'Exit <ESC>'-style button panel).",
             "k6 partial in sheets/sheet2_stragglers.png (DARK palette).",
             "RE-RENDER candidate - dims words invalid (W=0/H=0 at canonical "
             "slots, shp.md S20); only paint-capture could resolve."),
"destroy":  ("ship-destruction animation family (name; shp.md S3 variant dims "
             "word 0x7FFFFFBB-class).",
             "no render possible (0 stream bytes); never shown.",
             "KEEP - zero-byte ladder placeholder; nothing to render, nothing "
             "to rule on shape."),
"orbex00":  ("orb-explosion animation family (name; same variant dims class).",
             "no render possible (0 stream bytes); never shown.",
             "KEEP - zero-byte ladder placeholder; no shape ruling possible."),
"expl":     ("explosion animation ladders (shp.md S3: the 0x7FFFFFBB variant-"
             "dims family spans expl00/01/03/04/05/07/08 + sgNNexpl libs).",
             "no render possible (0 stream bytes); never shown.",
             "KEEP - zero-byte ladder placeholder; no shape ruling possible."),
"sg50expl": ("explosion ladder; span 27 B (TINY class, ids.tsv).",
             "no render produced (walk fails); never shown.",
             "KEEP - dims word 0x7FFFFFFC-class invalid (shp.md S20 honest "
             "remainder); part of the 16-record unknown-dims set."),
}

RECG = {  # record-level overrides: (lib_key, quote_or_None, rec_note, rec_override_or_None)
 "3cfgnew|12": ("3cfgnew", None,
    "ONLY genuinely truncated record in the residue set: short 55/79 rows AT "
    "FILE EOF (shp.md S20/S21) - broken vendor data outright.",
    "JUNK candidate (measured EOF truncation) - your call; windows.txt only "
    "selects k0, and no law depends on k12."),
 "1starmap|1": ("1starmap", None,
    "IN THE HONEST REMAINDER, not a benign empty slot: dims word invalid "
    "(0-class), not walkable at any tested slot (shp.md S20.3).", None),
"sg64expl|0": ("expl", None,
    "dims W=18 H=0xfffffffb — invalid component, demoted FAIL by the t197 "
    "dims-gate unification (shp.md S21.2); bytes exist, dims-location unknown.",
    None),
"mouse|5": ("mouse", None,
    "dims W=0 H=46 at canonical slots; old validator walked swapped anyway "
    "(t197 dims-gate demotion, shp.md S21.2).", None),
}

def libkey(cls, lib):
    if cls == "CONTROL": return "CONTROL"
    if re.match(r"^sg\d+expl$", lib): return "sg50expl" if lib == "sg50expl" else "expl"
    if lib.startswith("expl"): return "expl"
    for k in ("10status","2savegam","4loadgam","lgrace07","lgrace09","lgrace10",
              "planpro","planres","smship11","smship15","planind","3cfgnew",
              "1starmap","14intel","cos_star","mouse","destroy","orbex00"):
        if lib == k: return k
    raise SystemExit("unmapped library in census: %r (%s)" % (lib, cls))

def png_for(cls, name):
    # dumper naming: RESTORED--<lib>--rec<k>--WxH.png / XREC--... ; FAIL rows have none
    p = os.path.join(PK, name)
    if cls.startswith("RESIDUE"): return None
    return name if os.path.exists(p) else None

def main():
    src = os.path.join(PK, "index_t278pristine.txt")
    rows = []
    for line in open(src):
        line = line.rstrip("\n")
        if not line or line.startswith("#"): continue
        f = line.split(None, 4)
        if len(f) < 4: continue
        cls, name, status = f[0], f[1], " ".join(f[2:])
        rows.append((cls, name, status))

    # ids.tsv ids
    ids = {}
    for line in open(os.path.join(PK, "ids.tsv")):
        if line.startswith("#") or not line.strip(): continue
        p = line.rstrip("\n").split("\t")
        if len(p) >= 5: ids[(p[0], p[1])] = p[4]

    out = []
    w = out.append
    w("# OQ-005 RESIDUE DECISION SHEET (t278, 2026-11-02)")
    w("")
    w("How to use: read the RECOMMEND column; overrule anything you disagree with")
    w("(reply per row id, e.g. 'C1 junk, B13 keep'). Your Oct-29 verdicts are")
    w("quoted verbatim where they apply; where a row says 'not shown', the item")
    w("never reached you as an image. R13: nothing here rules for you - the ledger")
    w("row closes only on your ruling or a drawn-frame capture.")
    w("")
    w("Scope (measured from index_t278pristine.txt, the t197-era census): 88 records =")
    w("5 CONTROL + 10 RESTORED-V (t182 validator false-FAILs, already rendered")
    w("bright - brightness complaint fixed per shp.md S19) + 29 SPAN-FREE (t197:")
    w("full frames at canonical dims, our old span bound was the bug) + 44 FAIL")
    w("(no render possible). The honest dims-unknown remainder after t197 is 16")
    w("records: cos_star k40..k51, mouse k5/k6/k7, sg50expl k9, 3cfgnew k12")
    w("(shp.md S20.3). 26 of the 44 FAIL rows are ZERO-byte ladder slots - they")
    w("render nothing on any law, so they need no shape ruling (batch row below).")
    w("")
    w("Standing law for every row (shp.md S19): 'Do NOT delete rows on")
    w("non-recognition alone.' The Oct-29 blanket verdict: " + Q["all_real"])
    w("")
    w("Visual aids already in place (all Oct-1, DARK palette - regenerate on")
    w("request for bright versions): sheets/sheet1_span_undersized.png,")
    w("sheets/sheet2_stragglers.png, sheets/sheet3_ladder_planres_pro.png,")
    w("sheets/sheet4_gauges_context.png, sheets/sheet5_planind_partial_tail.png,")
    w("sheets/partial--*.png; your own shots in comparison/Comparison/.")
    w("")

    # Section A: shown + quoted rows (CONTROL + RESTORED-V)
    w("## A. ALREADY SHOWN TO YOU OCT-29 (restated verbatim; restate-only)")
    w("")
    w("| # | record | thumbnail (under work/r1/shp_png/) | identification [cited] | your Oct-29 status [verbatim] | RECOMMEND |")
    w("|---|--------|------------------------------------|----------------------|-------------------------------|-----------|")
    n = 0
    for cls, name, status in rows:
        if not (cls == "CONTROL" or cls == "RESTORED-V"): continue
        n += 1
        lib = name.split("--")[1].split("--")[0]
        lk = libkey(cls, lib)
        law, ustat, rec = LAW[lk]
        thumb = png_for(cls, name) or "(none)"
        w("| A%d | %s | %s | %s | %s | %s |" % (n, name, thumb, law, ustat, rec))
    w("")
    w("Context you added Oct-29: " + Q["lg_places"])
    w("")

    # Section B: SPAN-FREE (the real decision load)
    w("## B. SPAN-FREE FULL FRAMES (t197: complete at canonical dims) - DECIDE")
    w("")
    w("These 29 previously-failed records now decode as full frames. Per shp.md")
    w("S21 their BOTTOM BANDS are desynced bytes, not vendor art - judge shape on")
    w("the upper rows. Thumbnails are the bright-palette renders on disk now.")
    w("")
    w("| # | record | thumbnail | identification [cited] | user status | RECOMMEND |")
    w("|---|--------|-----------|----------------------|-------------|-----------|")
    n = 0
    for cls, name, status in rows:
        if cls != "SPAN-FREE": continue
        n += 1
        lib = name.split("--")[1].split("--")[0]
        m = re.search(r"rec(\d+)", name)
        k = m.group(1) if m else "?"
        law, ustat, rec = LAW[libkey(cls, lib)]
        w("| B%d | %s | %s | %s | %s | %s |" % (n, name, name, law, ustat, rec))
    w("")

    # Section C: FAIL rows, grouped; zero-byte batched
    w("## C. FAIL CLASS (44 records, no render possible)")
    w("")
    w("| # | record | span | identification [cited] | user status | RECOMMEND |")
    w("|---|--------|------|----------------------|-------------|-----------|")
    n = 0
    for cls, name, status in rows:
        if not cls.startswith("RESIDUE"): continue
        n += 1
        libfile = name.split("--")[0]
        lib = libfile[:-4] if libfile.endswith(".shp") else libfile
        k = name.split("--")[1]
        lk = libkey(cls, lib)
        law, ustat, rec = LAW[lk]
        ov = RECG.get("%s|%s" % (lib, k))
        note = ov[2] if ov else ""
        reco = ov[3] if (ov and ov[3]) else rec
        m = re.search(r"span=(\d+)", status)
        span = int(m.group(1)) if m else -1
        if not note and span > 100:
            note = ("real stream bytes present but dims WORD invalid "
                    "(t197 dims-gate demotion, shp.md S21.2) — dims-location "
                    "question still open for this slot.")
        w("| C%d | %s | %s B | %s%s | %s | %s |" % (n, name, span, law, (" NOTE: "+note) if note else "", ustat, reco))
    w("")
    w("Batch framing for the span-8/span-24 rows (expl*/sg*expl/destroy/orbex00):")
    w("25 of them are the t196 EMPTY class with ZERO stream bytes and the S3")
    w("variant dims word (0x7FFFFFBB-class, shp.md S20.1). They are not junk and")
    w("not recoverable art: the file simply holds an empty slot. If you accept")
    w("that framing they close as a batch with one word. (1starmap k1 also shows")
    w("span 24 but its dims word is invalid, so it sits in the remainder below,")
    w("not this batch.) THE HONEST DIMS-UNKNOWN REMAINDER is 16 records (shp.md")
    w("S20.3): mouse k6/k7, 1starmap k1, sg50expl k9 (invalid dims, not walkable")
    w("at any tested slot) + cos_star k40..k51 (dims word 0; the t200 selector law")
    w("makes them addressable-but-blit-refused placeholders). Separately:")
    w("3cfgnew k12 is broken vendor data outright (EOF truncation) and mouse k5 +")
    w("sg64expl k0 are t197 dims-gate demotions (shp.md S21.2) — real bytes,")
    w("invalid dims component. Those three plus the 16 are what your ruling (or a")
    w("draw-capture) has to land for the dims-location question to close.")
    w("")
    w("## D. WHAT EACH ANSWER BUYS (ledger mechanics, for your planning)")
    w("")
    w("- A ruling on B rows + the 16-record dims-unknown set (cos_star/mouse/")
    w("  sg50expl/3cfgnew-k12) is the OQ-005 closer the BLOCKED t68 ask names")
    w("  ('human-verifiable drawn frame'). Answer per row, or blanket.")
    w("- A answers are restatement only; they cost you nothing and change no row.")
    w("- The population-slot icon library IDENTITY (17np.shp content-match")
    w("  planets-ui.md S4) is NOT part of this sheet - it is tracked separately.")
    w("")
    w("Generated by scripts/r1_t278_decision_sheet.py from index_t278pristine.txt +")
    w("ids.tsv; quote/citation tables live in the script. Rebuild any time.")

    dst = os.path.join(PK, "decision-sheet.md")
    open(dst, "w").write("\n".join(out) + "\n")
    print("wrote", dst, len(out), "lines")

if __name__ == "__main__":
    main()
