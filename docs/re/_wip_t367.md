# _wip t367 — D1 RULING BANKED VERBATIM + APPLICATION CHECKLIST (queued, not applied)

## S0 Provenance
- Arrived 2026-11-09 12:45:01 and 12:45:31 (TWO identical submits — the user
  double-clicked; apply ONCE) via the ruling page into docs/DECISIONS.md
  ("## USER RULING 2026-11-09 12:45:31 (from ruling page)"). The page->file
  trigger channel is thereby LIVE-VALIDATED (server pid 43067, the /tmp-copy
  handler; submit leg works as banked in _wip_t358.md S1).
- t359 session did NOT apply the ruling (per its own NEXT note: t358 consumed;
  application gets its own row). This file is that row's head start.

## S1 The ruling (verbatim, the authoritative copy lives in DECISIONS.md)
USER: D1 mouse k5/k6/k7 = keep as-is
USER: D1 batch 41 dispositions = accept all 41
USER: D1 A6 keep=True, A7 keep=True, A8 keep=True
USER: D1 B-rows misidentified = none
USER: D1 notes: A series unused but keep (historical curiosity). B series
generally correct. B3 = star-map research menu button icon; B4 unrecognized.
B5-B16 from the new game menu; B17-B29 a subset of the planet-screen
manufacturing indicators; "B5-B29 are drawn wrong here. B5 contains the top
part of the image for B6, B6 contains the top part of the image for B7, ...
B17 contains the top part of the image for B18, B18 contains the top part of
the image for B19, and so on." [verbatim quote ends]

## S2 APPLICATION CHECKLIST for row t367 (order matters)
1. OQ-005 CLOSE strict-close citing the USER block verbatim (verbatim quote
   from DECISIONS.md, not this paraphrase) + shp.md S25/S26/S27 pointers.
   R13 satisfied: the user ruling IS the closer. Update STATE ledger index by
   RE-DERIVING via scripts/ledger_index_check.py (never hand-edit); ledger
   becomes 17 closed / 2 open (OQ-016, OQ-019).
2. work/r1/shp_png/index.txt + decision-sheet.md dispositions -> keep
   (generator r1_t278_decision_sheet.py owns both files — amend the generator's
   disposition() law or append the footer per the t347 tool-land pattern, then
   re-run the generator; do NOT hand-edit the sheet body).
3. keep=(b)-branch CODE: signed-bbox-aware dims read in
   rewrite/src/formats/shp.cpp per docs/re/_wip_d1page.md MEASURED section —
   k4..k7 decode at 78x47, plane md5 b2d049bbf5b5 as the 4-plane pin test;
   the -1 blit gate stays UNTOUCHED.
4. USER NOTE follow-through (NEW information, not in any prior ask): B5-B29
   renders on the ruling page are TOP-PART-OFFSET chain (Bn contains the top
   of Bn+1). Record in shp.md as user testimony; whether the PNG dump tool
   (r1_t182_pngdump.py) or the record walk causes it is UNDETERMINED — open a
   sub-investigation ONLY if the k4..k7 pin work touches the same walk code.
   Do not re-open OQ-005 closure over it (the ruling closed keep/junk; render
   fidelity of already-accepted art is not a ledger row).
5. ledger_audit + ledger_index_check + gate green; DECISIONS.md D1 status line
   -> APPLIED (annotate, never rewrite the USER block).

## S3 Standing caution
- The two USER RULING blocks (12:45:01, 12:45:31) are content-identical; cite
  either, apply once.
- t360 (save parser) does NOT depend on any of this; ordering t367-first is
  cheap-closure priority, not a dependency.
