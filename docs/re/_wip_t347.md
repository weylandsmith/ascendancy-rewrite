# _wip_t347 — DECISION-SHEET REGENERATION AFTER THE SLIM (STATE.md NEXT ACTION, verbatim row)

## S0 — PREFLIGHT (2026-11-09)
- SITTING CHECK NEGATIVE: tail-seek of work/r1/playcap/live-timeline.jsonl
  (last 200 KB, 8 rows) max turn == 1086, newest file 41..58.sav at t1086.
  No r1_t85g_sitting.py run needed; production :9 untouched.
- INPUTS VERIFY (row's first half): scripts/r1_t278_decision_sheet.py (340 L),
  work/r1/shp_png/index_t278pristine.txt (97 L, 44 RESIDUE rows),
  work/r1/shp_png/ids.tsv (88 L) — all present.
- GENERATOR RUNS POST-SLIM: `~/.hermes/hermes-agent/venv/bin/python
  scripts/r1_t278_decision_sheet.py` -> "wrote ... 161 lines", EXIT=0, and the
  output md5 54f07195806cd8cfe6b30c0d2db37ce9 EQUALS the pre-run copy of
  decision-sheet.md (/tmp/ds_pre_t347.md). So the sheet was already
  generator-produced and NO _wip input leaked into it: the script's only file
  reads are index_t278pristine.txt + ids.tsv (grep of open() confirms); all
  user quotes + citations live IN the script (Q/LAW/RECG tables). No repointing
  of inputs was required. INTERPRETER LAW honored (venv python; PIL unused by
  this generator — stdlib only — so system python3 works too, but venv used).
- PITFALL CONFIRMED LIVE: scripts/r1_t182_pngdump.py writes index.txt on every
  run; index.txt currently holds a pointer header + the sheet copy. Keep the
  hand-authored text in decision-sheet.md only.
- THIN-CHECK: nothing in scripts/ opens docs/re/shp.md or docs/DECISIONS.md for
  writing (grep 'open(.*shp\.md.*w' empty) — both are hand-authored, safe to edit.

## S1 — WHAT THE SHRUNK ASK IS (cited, zero capture)
Census basis: decision-sheet t278 C1..C44 == the 44 RESIDUE rows of
index_t278pristine.txt (verified 1:1, ordering identical).
Classification from shp.md S25 (t328 feasibility table) + S26 (t330 draw-capture)
+ S27 (t344 selector law), counts re-derived from the pristine census:
  - cos_star k40..k51           12  CITED-NO-WITNESS: all-zero 24-B headers,
    blit -1 dims gate @0x5cb2b refuses (S25.2).
  - 25 zero-STREAM ladder slots  25  CITED-NO-WITNESS + UNREACHABLE-BY-CAPTURE:
    span==header 25/25 (8 B k0-variant / 24 B k>=1) => zero stream bytes; every
    lib named in extracted/ascend00/batfx.txt battle-effects => combat class
    (t323 amendment). Members: destroy k14; expl00 k9; expl01 k8,k9; expl03
    k0,k9; expl04 k0,k9; expl05 k9; expl07 k0; expl08 k0,k9; orbex00 k8,k9;
    sg37expl k0,k9; sg45expl k0,k9; sg47expl k0,k9; sg49expl k0,k9;
    sg66expl k0,k9; sg70expl k9.
  - 1starmap k1                  1  CITED-NO-WITNESS: span 24 = zero stream;
    SHAPEITEM selects k3/k4/k5/k7 only (windows.txt 456/477/498/517).
  - sg50expl k9                  1  UNREACHABLE-BY-CAPTURE (batfx line 58) +
    no-witness corroboration (span 27 AT EOF).
  - sg64expl k0                  1  UNREACHABLE-BY-CAPTURE (batfx line 63).
  - 3cfgnew k12                  1  JUNK-CERTAIN: vendor EOF truncation, walk
    short 55/79; SHAPEITEM selects k0 only.
  - mouse k5/k6/k7               3  THE ONLY ADJUDICABLE RESIDUE.
  TOTAL 44 (12+25+1+1+1+1+3). Non-ask = 41, matching the row's framing
  ("41 of 44 C-rows cited-no-witness/junk-certain/unreachable").
  NOTE the t328 arithmetic groups sg50expl k9 with the no-witness set (its
  "39 no-witness" = 38 zero-dims/zero-stream + sg50expl); this sheet states the
  same 41/3 split with per-row reason strings so the count is re-derivable.
- MOUSE RE-CLASSIFICATION (t330 S26 + t344 S27, supersedes the t278 sheet text
  "dims words invalid ... only paint-capture could resolve"):
  draw-time dims = u16 pair at rec+0 stored [H-1,W-1] (MEASURED live, mouse
  k0/k2); k5/k6/k7 = 78x47 VALID; the t328 "zero-component canonical slot" was
  ONE HALF OF A SIGNED BBOX PAIR (k5=(-77,0,0,46) k6=(0,-46,77,0) k7=(-77,-46,0,0),
  k4..k7 = ONE glyph at four corner anchors, 12/12 file-measured).
  SELECTOR IS NOW KNOWN: fn 0x54650 mode chain keys cursor position
  (0,0)->id4, (0,639)->id5, (479,0)->id6, (479,639)->id7; TL/TR live-witnessed
  byte-exact (run dbg-t344d-20261108-161132). Pixels remain CAPTURE-LIMITED
  (zero blit_deref at k5/k6/k7 offsets in the witness window).


## S2 — REBUILD LANDED (zero capture, ~14 tool calls)
- GENERATOR IS NOW THE SINGLE SOURCE for decision-sheet.md AND index.txt:
  scripts/r1_t278_decision_sheet.py writes both (index.txt = pointer header +
  identical bytes), so the t182-dumper-clobbers-index.txt pitfall is repaired
  structurally instead of by discipline — re-running the generator restores the
  sheet view. Verified: 176 lines, EXIT=0.
- SHRUNK ASK IS ASSERTED, not asserted-about. New disposition() law table maps
  every C-row to (CLASS, cited reason); unmapped census rows raise SystemExit so
  a changed corpus fails loudly. MEASURED SPLIT = 40 NO-ASK + 1 JUNK-CERTAIN +
  3 ADJUDICABLE = 44 (41 rows leave the ask).
  FIRST-RUN EVIDENCE THE ASSERTION WORKS: my initial hand-count said 38 NO-ASK
  and the generator FAILED (AssertionError: {'NO-ASK': 40, 'JUNK-CERTAIN': 1,
  'ADJUDICABLE': 3}) — sg50expl k9 and sg64expl k0 are NO-ASK (unreachable),
  not a separate class. The count in the sheet is now machine-checked, and it
  caught the author's own arithmetic before it shipped.
- STALE PREMISES PURGED from the sheet text (all three superseded by cited
  measurement, no re-litigation): "dims words invalid ... only paint-capture
  could resolve" (mouse lib), "W=0 H=46 at canonical slots" (k5 note — half a
  signed bbox pair, S27), "THE HONEST DIMS-UNKNOWN REMAINDER is 16 records"
  (superseded by the per-row dispositions).
- docs/DECISIONS.md D1 REWRITTEN to the t347 shape: 3 adjudicable rows
  (C27-C29 keep/junk) + one batch word for the 41 + optional B-row ID confirm +
  the A6-A8 triad named as a LIVE keep/junk call (it was filed "restatement
  only" while the user had called it "possibly junk data" — a real ask we had
  been not-asking). D3's OQ-005 line got the t344/t347 addendum.
- NO LEDGER CLOSE. Strict-close: this iteration produced NO new measurement —
  it re-expressed already-cited measurement and repaired the tooling. R13 also
  bars self-grading: OQ-005 closes on the user's ruling (or a drawn-frame
  capture), and no ruling arrived. Row STAYS OPEN with the honest negative:
  "t347 moved no row; the ask shrank on paper only, the blocker is USER TIME."
  16 closed / 3 open unchanged.
- HONEST LIMIT OF THE ASK-SHRINK: 41 rows left the ask because the vendor's
  DRAWING behaviour is known, not because the records are understood. If a
  future capture ever derefs k5/k6/k7 (the pixels), C27-C29 close on evidence
  rather than on a word — that route is open, unbudgeted, and NOT refuted.


## S3 — INPUT DURABILITY (the row's real point, landed after the rebuild)
- The two banked inputs lived ONLY in gitignored work/ — the sheet was
  regenerable today, not durable. Copied to tracked artifacts/shp_png_inputs/
  (+ README provenance) per the t343 copy-into-tracked-dir route:
  index_t278pristine.txt md5 ed0e3acfd2956870ec11c22f6242b5c4 (13,510 B),
  ids.tsv md5 42787120fa657fd8b75f4f19650e18e6 (11,324 B, 82 data rows).
- Generator now resolves inputs via inp(): work/r1/shp_png first, artifacts/
  fallback, SystemExit naming both dirs if absent; makedirs(PK) so a wiped
  work/ regenerates instead of dying. FALLBACK TESTED, not asserted: module
  imported with PK=/nonexistent resolved both inputs and raised on a missing
  name. Post-rebuild sheet md5 10989b4d52e30a4939928a52e4de8da4, stable across
  back-to-back runs (176 L).
- TWO SELF-CAUGHT ERRORS banked as honesty, not hidden: (1) the README first
  claimed the fallback existed BEFORE the code did and garbled an md5 — both
  fixed by implementing and re-measuring; (2) the 38-vs-40 disposition
  miscount (S2). Lesson: never document a mechanism in the same breath as
  planning it.


