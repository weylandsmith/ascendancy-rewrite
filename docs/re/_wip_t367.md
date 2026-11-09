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

## S4 t367 EXECUTION FINDINGS (this session; measurements first)

### S4.1 Sitting check NEGATIVE
work/r1/playcap/live-timeline.jsonl 8,884,069,796 B, 400 KB tail-seek, 16
records parsed with json, turn==1086 on 16/16, newest tail files 56/57/58.sav
(ring rotation). r1_t85g_sitting.py correctly NOT run. Production :9 untouched.

### S4.2 The ruling is present (trigger CONFIRMED)
docs/DECISIONS.md L159-164 and L166-171: two content-identical USER blocks
(12:45:01, 12:45:31). Cited verbatim ONCE.

### S4.2b THE PIN md5 b2d049bbf5b5 IS NOT REPRODUCIBLE (honest negative)
Candidate slices tried (extracted/ascend01/data/mouse.shp): plane at bbox dims
78x47 zero-underlay = b700fe532b52; 0xff-underlay = e26f4afd4f5c; swapped 47x78
= c2f37128a9a9; raw 2038-B stream @rec+0x18 = 479ba18ae199; whole record 2062 B
and header 24 B — none md5-prefixed b2d049bbf5b5. A full walk of work/r1/d1page/
every file = no match either; the PNGs themselves are md5 e2a62debb5bd x4. The
generating render script was never committed (grep mouse_k -> only index.html).
CONSEQUENCE: the pin in _wip_t367/STATE cannot be honoured literally. The
BYTE-IDENTITY LAW it stood for is re-measured three independent ways instead
(see S4.3) and the C++ pin asserts THAT. b2d049bbf5b5 is recorded as an
UNREPRODUCIBLE FIGURE, not silently re-anchored.

### S4.3 mouse.shp measured (12 records, len 10,435 B)
k4 rec=0x48b canon dims (77,46) bbox(0,0,77,46)   -> walk OK @77x46
k5 rec=0xc99 canon dims (0,46)  bbox(-77,0,0,46)  -> canonical GATE FAILS
k6 rec=0x14a7 canon (77,0)      bbox(0,-46,77,0)  -> canonical GATE FAILS
k7 rec=0x1cb5 canon (0,0)       bbox(-77,-46,0,0) -> canonical GATE FAILS
bbox dims 78x47 walk completes for k4..k7 (47/47 rows, ends at span end 2062).
THREE independent identity measurements, all 4/4 equal:
  (a) raw RLE stream md5 @rec+0x18, 2038 B: 479ba18ae199 for k4==k5==k6==k7
  (b) painted plane @78x47 zero-underlay md5: b700fe532b52 for all four
  (c) the shipped ruling-page PNGs: e2a62debb5bd for all four
=> ONE glyph, four corner anchors, mechanically confirmed (no vision involved).

### S4.4 GENERALISATION CENSUS (decisive against a blanket bbox dims read)
Corpus extracted/*/data/*.shp, 208 libs, 1,349 records k>=1:
  canonical-dims == bbox-diff(R-L+1,B-T+1): 3 records ONLY
  canonical valid but != bbox-diff:         1,313 records
  canonical dims gate FAILS:                33 records
(The t344 "12/12 mouse records agree" law is mouse-libral only; a blanket
signed-bbox dims read would corrupt 1,313 good records. shp.cpp dims reading
stays canonical; the bbox reading is a GATE-ONLY FALLBACK.)

### S4.5 Fallback blast radius — why the fallback must be narrow
Naive rule "if canonical dims gate fails, use bbox dims + walk" rescues 17:
  mouse k5/k6/k7 (78x47)                       <- WANT
  cos_star k40..k51 -> 1x1 (12)                <- MUST NOT: t328 S25 all-zero
                                                   24-B headers, zero stream;
                                                   vendor blit -1 gate @0x5cb2b
                                                   cannot draw dims<=0
  1starmap k1 -> 3x3                           <- MUST NOT: zero-stream, no
                                                   selector (accepted NO-ASK)
  sg50expl k9 -> 1x1                           <- MUST NOT: t328 NO-ASK/unreach-
                                                   able class
16 records still fail (destroy k14, expl00/01/03/04/05/08, orbex00 k8/k9,
sg37/45/47/49/66/70expl k9 — bbox 3x3 but walk desyncs; plus 3cfgnew k12 EOF
truncation) = the accepted JUNK/NO-ASK residue, unchanged.

### S4.6 THE GATE SHAPE THAT ADMITS EXACTLY mouse k5/k6/k7
Fallback fires iff ALL of: canonical pair fails the (1..4096)x(1..4096) gate;
signed bbox (L,T,R,B) at rec+0x08/0xc/0x10/0x14 gives W=R-L+1, H=B-T+1 both in
1..4096 AND >=2; AT LEAST ONE of L,T is NEGATIVE (the corner-anchor signature —
t344 S27: k4..k7 are one glyph at four corner anchors, the negative half is what
the unsigned gate threw away); the row walk completes.
Measured on the whole corpus with this rule: admitted = mouse k5,k6,k7 ONLY
(cos_star rejected: no negative component and 1x1; 1starmap k1: no negative;
sg50expl k9: 1x1; the 16 expl-class: walk fails). Zero collateral.

## S4.7 PIN RESOLVED — b2d049bbf5b5 IS REPRODUCIBLE (supersedes S4.2b)
My scratch reference walk (S4.2b probes) had a pixel-position bug: the
literal-copy branch never advanced p, so writes clustered at row start. The
CORRECTED walk (p += n after literal copy, per shp.h S9 grammar — exactly what
shp.cpp walkRows does) yields, for the k5/k6/k7 plane at bbox dims 78x47, zero
underlay:
  md5 = b2d049bbf5b571bfc4ea3b97db7a4fa7   <- EXACTLY the d1page pin
  census 543287, nonzero 3666, fnv64 3ba44ef8c0c54974, k5==k6==k7 planes.
The C++ decoder plane byte-compares EQUAL to the corrected Python walk
(/tmp/cpp_plane_k5.bin == corrected walk output). The d1page author's figure
was right all along; S4.2b's "not reproducible" was MY instrument error —
retracted, and the C++ pin test asserts census/nonzero/fnv of those exact
bytes (no md5 helper exists in the codebase). k4 canonical 77x46 plane: md5
a67550d3e270b9b02c0b3892c8aeee95, census 536292, nonzero 3542.

## S4.8 CODE + TEST LANDED (rewrite)
shp.cpp: dims gate restructured — on canonical-gate failure for k>=1, the
SIGNED corner-anchor fallback (S4.6 rule) runs; canonical pass path bit-identical
to before. shp.h header law updated. test_shp.cpp: TEST(shp_corner_anchor_
fallback_t367) = decode 78x47 x3, plane identity, census/nonzero/fnv pins,
determinism, NEGATIVE CONTROL (cos_star k40..51, sg50expl k9, 1starmap k1 stay
rejected), k4 canonical size assert. shp_span_free_t197 clause (3) amended
(mouse k6/k7 reject-asserts removed). Parity floors 1513/187 -> 1516/188.
MEASURED: run_tests 176 tests, 0 failed; corpus line "208 libs, 1557 records,
1516 decode-pass, 188 clean libs" = Python-FAIL-44 minus exactly mouse x3.
PYTHON VALIDATOR DELIBERATELY UNCHANGED (gate 3c-2 still pins the t197 law):
it models the FUN_0005caac blit -1 consumer; the fallback models the OTHER
vendor consumer (cursor geometry fn 0x61058 reads the bbox, t344 S27). The
3-record C++/Python divergence is intentional, two-consumer, documented in
shp.md S28 + the test comment.


