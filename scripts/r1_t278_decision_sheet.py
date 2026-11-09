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
  work/r1/shp_png/index.txt  the same bytes behind a pointer header (t278
      convention; scripts/r1_t182_pngdump.py OVERWRITES index.txt with the raw
      dumper census on every run, so decision-sheet.md is canonical).

T347 REGENERATION (2026-11-09, post-slim): the generator was verified to run
and reproduce decision-sheet.md byte-identical from banked inputs only, then
updated to the SHRUNK ASK — every C-row now carries a cited DISPOSITION
(shp.md S25 t328 feasibility table, S26 t330 live draw-capture, S27 t344
selector law), and the script ASSERTS the 41-out-of-ask / 3-adjudicable
split (40 NO-ASK + 1 JUNK-CERTAIN + 3 ADJUDICABLE = 44) on every rebuild. Row ids C1..C44 stay pinned to the
index_t278pristine.txt census order so DECISIONS.md references (C27-C29) hold.

The user-quote and citation tables below are transcribed from:
  - the user's Oct-29 message (session 20261022_024226_01e8e7 msg 40813),
  - docs/re/shp.md S19 (t189b), S20 (t196), S21 (t197), S21 selectedness fold,
  - docs/re/planets-ui.md S5.1 (selection census), S6 (cos_star selector law),
  - docs/BLOCKED.md t68 (the ask).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PK = os.path.join(ROOT, "work", "r1", "shp_png")
# t347: the two banked inputs are ALSO committed under artifacts/ (gitignored
# work/ can be wiped; the sheet the user rules on must stay regenerable).
ART = os.path.join(ROOT, "artifacts", "shp_png_inputs")

def inp(name):
    """Resolve a generator input: work/r1/shp_png first, artifacts/ fallback."""
    for d in (PK, ART):
        cand = os.path.join(d, name)
        if os.path.exists(cand):
            return cand
    raise SystemExit("missing generator input %r (looked in %s and %s)" % (name, PK, ART))

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
"mouse":    ("cursor/button set. k0 drawn on EVERY right-bar panel open "
             "(t330 live witness, shp.md S26); k4..k7 = screen-corner cursors "
             "TL/TR/BL/BR (selector law fn 0x54650 mode chain; TL/TR "
             "live-witnessed byte-exact t344, shp.md S27).",
             "k6 partial in sheets/sheet2_stragglers.png (DARK palette).",
             "KEEP - valid 78x47 art with a KNOWN selector; the t196/t278 "
             "'invalid dims' premise is REFUTED (t330/t344). Your rule needed: "
             "keep valid-but-rarely-drawn corner art as-is?"),
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
   "t344: k4..k7 = ONE 78x47 glyph at four corner anchors (signed bbox pair; "
   "the old 'W=0' read one half of the pair, shp.md S27).", None),
}


# ---------------------------------------------------- t347 C-ROW DISPOSITION LAW
# Why each of the 44 C-rows needs NO shape ruling (or does). Cited sources:
#   S25  = docs/re/shp.md section 25 (t328 feasibility table, measured)
#   S26  = docs/re/shp.md section 26 (t330 live blit witness, run
#          work/r1/dbg-t330b-20261107-080216)
#   S27  = docs/re/shp.md section 27 (t344 selector law + corner witness, run
#          work/r1/dbg-t344d-20261108-161132)
#   t323 = the UNREACHABLE-BY-CAPTURE disposition amendment (combat-art class;
#          every battle lib is named in extracted/ascend00/batfx.txt)
ZERO_STREAM = {  # the 25 slots t328 measured span==header => zero stream bytes
 "destroy|14", "expl00|9", "expl01|8", "expl01|9", "expl03|0", "expl03|9",
 "expl04|0", "expl04|9", "expl05|9", "expl07|0", "expl08|0", "expl08|9",
 "orbex00|8", "orbex00|9", "sg37expl|0", "sg37expl|9", "sg45expl|0",
 "sg45expl|9", "sg47expl|0", "sg47expl|9", "sg49expl|0", "sg49expl|9",
 "sg66expl|0", "sg66expl|9", "sg70expl|9",
}

def disposition(lib, k, span):
    """Return (CLASS, reason) for one C-row. Raises if a census row is unmapped,
    so a changed corpus cannot silently slip into the sheet."""
    key = "%s|%s" % (lib, k)
    if lib == "mouse":
        return ("ADJUDICABLE",
                "valid 78x47 corner-cursor art, selector KNOWN (S26/S27); drawn "
                "pixels capture-limited — your rule is keep/junk, not decode")
    if lib == "3cfgnew" and k == "12":
        return ("JUNK-CERTAIN",
                "vendor truncated it at FILE EOF (walk short 55/79, S20/S21); "
                "windows.txt SHAPEITEM selects k0 only")
    if lib == "cos_star":
        return ("NO-ASK",
                "all-zero 24-byte header, dims zero in EVERY slot -> the blit's "
                "own -1 gate @0x5cb2b draws nothing (S25.2, S12)")
    if key in ZERO_STREAM:
        return ("NO-ASK",
                "zero stream bytes (span==header, 25/25 measured) + battle-effects "
                "lib named in batfx.txt => UNREACHABLE-BY-CAPTURE (S25.2, t323)")
    if lib == "1starmap":
        return ("NO-ASK",
                "zero stream bytes (span 24) AND no selector names k1 "
                "(SHAPEITEM k3/k4/k5/k7, windows.txt 456/477/498/517) (S25.2)")
    if lib == "sg50expl":
        return ("NO-ASK",
                "combat art => UNREACHABLE-BY-CAPTURE (batfx line 58, t323); "
                "span 27 sits AT EOF (near-empty + truncated, S25.2)")
    if lib == "sg64expl":
        return ("NO-ASK",
                "combat art => UNREACHABLE-BY-CAPTURE (batfx line 63, t323); "
                "variant dims word class (S3)")
    raise SystemExit("unmapped C-row in census: %r (span %s) — classify it "
                     "before regenerating the sheet" % (key, span))

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
    src = inp("index_t278pristine.txt")
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
    for line in open(inp("ids.tsv")):
        if line.startswith("#") or not line.strip(): continue
        p = line.rstrip("\n").split("\t")
        if len(p) >= 5: ids[(p[0], p[1])] = p[4]

    out = []
    w = out.append
    w("# OQ-005 RESIDUE DECISION SHEET (t278; t347 REBUILD 2026-11-09 - SHRUNK ASK)")
    w("")
    w("How to use: read the RECOMMEND column; overrule anything you disagree with")
    w("(reply per row id, e.g. 'C1 junk, B13 keep'). Your Oct-29 verdicts are")
    w("quoted verbatim where they apply; where a row says 'not shown', the item")
    w("never reached you as an image. R13: nothing here rules for you - the ledger")
    w("row closes only on your ruling or a drawn-frame capture.")
    w("")
    w("THE LIVE ASK (t347): 41 of the 44 C-rows now carry a CITED DISPOSITION -")
    w("the vendor itself draws NOTHING for them, or the bytes are junk-certain -")
    w("so they need no ruling; batch-accept them with one word if you like.")
    w("Actually adjudicable: B1..B29 (confirm/correct the identifications),")
    w("C27-C29 (mouse k5/k6/k7 - valid 78x47 corner-cursor art, selector known;")
    w("keep as-is?), and the A6-A8 triad you called 'possibly junk data' (rule")
    w("from the thumbnails: keep as unused menu art, or junk). ~2 minutes.")
    w("")
    w("Scope (measured from index_t278pristine.txt, the t197-era census): 88 records =")
    w("5 CONTROL + 10 RESTORED-V (t182 validator false-FAILs, already rendered")
    w("bright - brightness complaint fixed per shp.md S19) + 29 SPAN-FREE (t197:")
    w("full frames at canonical dims, our old span bound was the bug) + 44 FAIL")
    w("(t278 rows C1..C44). The t278 'dims-location' framing is SUPERSEDED: t330")
    w("MEASURED the vendor's draw-time dims slot (u16 pair at rec+0, stored")
    w("[H-1,W-1]; shp.md S26) and t344 dissolved the mouse zero-component dispute")
    w("(the pair is a SIGNED bbox; S27). Every C-row now carries its own cited")
    w("disposition (feasibility table shp.md S25 + S26/S27): 12 cos_star k40..k51")
    w("zero-dims (blit -1 gate), 25 zero-stream ladder slots, 1starmap k1")
    w("zero-stream + no selector, sg50expl k9 + sg64expl k0 combat-unreachable,")
    w("3cfgnew k12 vendor-truncated = 41 rows out of the ask (40 no-ask + 1")
    w("junk-certain); mouse k5/k6/k7 = the 3 adjudicable rows. The script")
    w("ASSERTS the 41/3 split on every rebuild.")
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

    # Section C: FAIL rows with t347 cited dispositions (shrunk ask)
    w("## C. FAIL CLASS (44 records) - t347 DISPOSITIONS; only 3 rows need you")
    w("")
    w("Every row carries a cited disposition (law table in")
    w("scripts/r1_t278_decision_sheet.py; sources shp.md S25/S26/S27 + the t323")
    w("combat-unreachable amendment). NO-ASK = the vendor's own code draws")
    w("nothing for it (zero dims -> blit -1 gate @0x5cb2b, or zero stream bytes)")
    w("or the class is unreachable by any capture we can stage; batch-accepting")
    w("them costs one word. JUNK-CERTAIN = vendor-truncated bytes. ADJUDICABLE =")
    w("real art you can rule keep/junk on.")
    w("")
    w("| # | record | span | DISPOSITION | why [cited] | RECOMMEND |")
    w("|---|--------|------|-------------|-------------|-----------|")
    counts = {"NO-ASK": 0, "JUNK-CERTAIN": 0, "ADJUDICABLE": 0}
    n = 0
    for cls, name, status in rows:
        if not cls.startswith("RESIDUE"): continue
        n += 1
        libfile = name.split("--")[0]
        lib = libfile[:-4] if libfile.endswith(".shp") else libfile
        k = name.split("--")[1]
        m = re.search(r"span=(\d+)", status)
        span = int(m.group(1)) if m else -1
        dclass, dwhy = disposition(lib, k, span)
        counts[dclass] += 1
        ov = RECG.get("%s|%s" % (lib, k))
        note = ov[2] if ov else ""
        if ov and ov[3]:
            reco = ov[3]
        elif dclass == "ADJUDICABLE":
            reco = LAW[libkey(cls, lib)][2]
        else:
            reco = "no ruling needed (batch: accept disposition)"
        w("| C%d | %s | %s B | %s | %s%s | %s |"
          % (n, name, span, dclass, dwhy, (" NOTE: "+note) if note else "", reco))
    # SHRUNK-ASK ASSERTION: the sheet's headline numbers are measured facts; a
    # corpus change that shifts them must fail loudly, not silently re-framing.
    assert n == 44, "C-class census changed: %d rows (expected 44)" % n
    assert counts == {"NO-ASK": 40, "JUNK-CERTAIN": 1, "ADJUDICABLE": 3}, \
        "disposition split changed: %r (expected 40/1/3 = 41 rows out of the ask)" % (counts,)
    w("")
    w("Count (asserted on every rebuild): 40 NO-ASK + 1 JUNK-CERTAIN = the 41")
    w("rows that leave the ask, plus 3 ADJUDICABLE (C27-C29 mouse k5/k6/k7) = 44.")
    w("")
    w("## D. WHAT EACH ANSWER BUYS (ledger mechanics, for your planning)")
    w("")
    w("- A ruling on B1..B29 + C27..C29 (batch or per-row) is the OQ-005 closer")
    w("  the BLOCKED t68 ask names ('human-verifiable drawn frame' - for")
    w("  k5/k6/k7 that bar is now measured CAPTURE-LIMITED, so your word is the")
    w("  practical closer). If you accept the 41 dispositions in one word, the")
    w("  only residues needing per-row text are the B identifications.")
    w("- A answers are restatement only; they cost you nothing and change no row")
    w("  EXCEPT A6-A8 (the 10status/2savegam/4loadgam triad you called 'possibly")
    w("  junk data') - that is a live keep/junk call from the thumbnails.")
    w("- The population-slot icon library IDENTITY (17np.shp content-match")
    w("  planets-ui.md S4) is NOT part of this sheet - it is tracked separately.")
    w("")
    w("Generated by scripts/r1_t278_decision_sheet.py from index_t278pristine.txt +")
    w("ids.tsv; quote/citation/disposition tables live in the script. Rebuild any")
    w("time: venv python, zero capture. t347 rebuild 2026-11-09.")

    # If work/ was wiped the inputs still resolve (artifacts/), but the OUTPUT
    # needs a directory — create it rather than die confusingly.
    os.makedirs(PK, exist_ok=True)
    dst = os.path.join(PK, "decision-sheet.md")
    body = "\n".join(out) + "\n"
    open(dst, "w").write(body)
    # index.txt = pointer header + the same bytes (t278 convention). The dumper
    # scripts/r1_t182_pngdump.py clobbers it with the raw census on every run;
    # re-running THIS script restores the sheet view (t347: made part of the
    # generator so the pair can never drift apart silently).
    hdr = ("# ===========================================================================\n"
           "# index.txt IS THE DECISION SHEET (canonical copy: decision-sheet.md,\n"
           "# same bytes). scripts/r1_t182_pngdump.py OVERWRITES this file with the raw\n"
           "# dumper census on every run; the pre-rebuild raw census is banked verbatim\n"
           "# as index_t278pristine.txt. Restore the sheet view any time:\n"
           "#   python3 scripts/r1_t278_decision_sheet.py\n"
           "# ===========================================================================\n")
    open(os.path.join(PK, "index.txt"), "w").write(hdr + body)
    print("wrote", dst, len(out), "lines (+ index.txt pointer copy)")

if __name__ == "__main__":
    main()
