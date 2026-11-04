# WIP t182 — OQ-005 shape-PNG dumper (session 2026-10-28, HEAD 27fea50)

## Assignment
STATE.md t182 (no steering note; trigger A NEGATIVE). Build
scripts/r1_t182_pngdump.py rendering residue + controls to work/r1/shp_png/,
self-validating PNGs, NO self-grading (player's ruling closes OQ-005).

## SHIPPED SO FAR
- tools/shp_pngdump.cpp — C++ driver over the rewrite's OWN ShapeLibrary
  (links rewrite/build/libascend_core.a; builds clean). decode() gained an
  optional bool* swapped out-param (shp.h/.cpp; 110 tests 0 fail) so the
  front-end knows plane stride/orientation honestly.
- scripts/r1_t182_pngdump.py (~/tools/revenv/bin/python; PIL 12.3.0) —
  selects CONTROLS (17np k0 639x479, dkship20 k3 314x222, racering k0 53x53,
  listbox k1 24x24, bullet04 k0 10x11 — all from every-record-passing libs,
  racering/listbox/bullet04 also S17 RAM-verified) + residue re-derived LIVE
  via r1_shp_unifiedlaw.rec_state, grouped span-undersized/simple-format/
  straggler. Palette extracted/ascend01/data/game.pal (768B, labelled
  UNVERIFIED default). First run EXIT 0: sets=86 rendered=15 validated=15
  decode-fail=71 residue=81. Law snapshot {'V':187,'A':1289,'FAIL':81}.

## MEASURED FINDING (t182 core): VALIDATOR V-TRIAL OFF-BY-8 ARTIFACT
scripts/r1_shp_unifiedlaw.py:49 `trials.append(("V", rec, rec))` starts the
k==0 row-walk at `rec`, while the script's OWN docstring (line 5), shp.md S16
law text, the S17 live-RAM table law (sel0 -> rec0+8, 43 selectors zero
exceptions), and rewrite shp.cpp:106 (rec+8) all say the V stream is rec+8.
Cross-check evidence, this session:
  - The 10 rendered residue records are EXACTLY the k==0 stragglers:
    10status/2savegam/4loadgam rec0 (639x479), planpro/planres rec0 (107x99),
    smship11 rec0 (45x30), smship15 rec0 (39x6), lgrace07/09/10 rec0
    (296x199). All render CANONICAL (swapped=0) from rec+8 and reopen as sane
    PNGs with nonbg >= 8358.
  - Direct rowwalk probe: 10status rec0 canonical walk ends 0x5499 < budget
    0x54a8 (inside span); swapped walk fails. planpro 0x2c97<0x2d05;
    smship15 0xf6<0x542; lgrace07 0xd051<0xd154. Same pattern all four.
  - git: r1_shp_unifiedlaw.py UNCHANGED since 4f11708 (t67c) — the bug shipped
    with the t67c commit and contradicts its own banked law text.
=> These 10 records are NOT dims-location-unknown; they satisfy the CLOSED
   S16/S17 V/A law. Residue class corrects 80/81 -> 71 genuine records.
   planind/3cfgnew STAY genuine (3cfgnew k0 walk from rec+8 does NOT complete
   — verified; they are span-undersized per S16 class a).
   NOT a codec sweep (GOAL rule intact): no new grammar searched; the law is
   the CLOSED RAM-measured one; only the validator's off-by-8 corrected.
- Count reconciliation: banked t67c text says FAIL 80 with "B/F1 ~2"; live
  same-script corpus says V187 A1289 FAIL81 (sum 1557 exact, B tag absent).
  Bank the honest measured 81; note the banked 80 as unreplicable rounding.

## REMAINING (finish plan)
1. Patch rec_state V trial to ("V", rec+8, rec); re-run r1_shp_unifiedlaw.py;
   confirm V=197/FAIL=71 or report the true delta (records that V-passed
   vacuously from rec may now drop — measure, don't assume).
2. Re-run dumper post-fix (re-derives residue -> 5 controls + 71 FAIL rows);
   keep pre-fix run's 10 ex-artifact PNGs on disk, cite by name in shp.md S18.
3. Bank shp.md §18 (t182) + amend BLOCKED t68 counts; OQ-005 row stays OPEN
   (71 genuine residue; strict-close — nothing closes today).
4. gate.sh 0 + ledger_audit OK + commit "t182: ...".
