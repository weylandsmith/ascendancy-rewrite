# WIP t199 — rewrite wiring of the t198 planet-UI vis laws + pop-band pin

Trigger triage: live-timeline.jsonl size 5,721,578,066 == frozen TRIGGER-A
baseline (mtime 2026-10-29 13:22:12.10), dosbox down -> NO new sitting; tree
clean at d3b7ee6 (t198); no steering note. Worked STATE NEXT as assigned.

## S0 Law pre-verification (pure math, before touching code)
Recomputed the t198 compression map independently (python round() == x87
nearest-even like frndint cw 0x1f):
  first level reaching selector k:
  {0:0, 1:1, 2:2, 3:4, 4:6, 5:8, 6:10, 7:13, 8:15, 9:18, 10:21, 11:23,
   12:26, 13:30, 14:33, 15:36, 16:39, 17:43, 18:46, 19:49, 20:53}
  RES 52 -> 19 [matches planets-ui.md S3 corpus line], IND 53 -> 20 [matches
  "rec 20 from level >= 53"], IND 77 -> clamped 20, unclamped 21 from L=57
  (corpus IND max 77 -> the clamp branch is REAL, not decorative).
TIE SAFETY [proved]: an exact .5 tie needs L^0.75 = (2n+1)/2 i.e.
16*L^3 == (2n+1)^4; LHS has even 2-adic valuation, RHS odd => NO integer
ties exist, so C++ lround == x87 frndint on every input and the law is
tie-proof as coded.
MISREAD CAUGHT: planets-ui.md S3 says "pow(53,0.75)=20.2 -> round 20"; the
actual value is 19.643 -> round 20. Conclusion unaffected; doc corrected.

## S1 Design decisions
- gaugeSelector (IND/RES pow-0.75 + clamp0..20) and prosSelector (identity
  clamp0..20) live in src/ui/layout.{h,cpp}: pure no-SDL UI law, already
  compiled into run_tests; ui-runtime.md S2 keeps rendering blocked on OQ-005
  (no vendor sprites drawn, lookalikes banned), so the LAW lands as pinned
  pure functions + a note at the planet-panel site — the task's sanctioned
  "pin ONLY the map law" option, documented why.
- popBandsFor(star) lives on Campaign (campaign.h): the three operands
  already exist there (+0x42 pop double, usedPopFor() +0x4c, storedCapFor()
  +0x4a). Formula implemented VERBATIM SEL(i)=1+[i>=used]+[i>=pop] over
  i<cap; the used<=pop<=cap corpus law (2900/2900) is pinned as a separate
  CHECK over a seeded campaign's every planet, band histograms counted
  independently of the formula (count1==used, count2==pop-used,
  count3==cap-pop only asserted when the invariant holds).
- fold t196/t198 ids into shp.md S22 pointer line.
