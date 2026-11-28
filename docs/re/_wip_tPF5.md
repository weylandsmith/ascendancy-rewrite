# tPF-5 — INDICATOR POPUP FRAMES + INDUSTRY TILE ART (D28 items 9+10) — WIP

Task (STATE.md NEXT 2026-11-25). User witness verbatim
(scratchpad/t433-build-feedback.txt):
 - item 9  (line 9): "On the planet screen, clicking the frames along the top
   should pop up a window that's the same size and shape (again with the same
   mineral framing) as the window that pops up when a planet tile is clicked."
 - item 10 (line 10): "The art on the Industry indicator tile is not drawn
   correctly - it's too high in the frame, with the top cut off. On the bottom
   there is either an empty black band, or the top of the next image in the
   series (not sure which)."

PRECONDITIONS CHECKED THIS SESSION:
 - Sitting adjudication ran FIRST (scripts/r1_t85g_sitting.py, exit 0):
   45,227 trusted turn-change rows, newest t=1335 — IDENTICAL to the tPF-4
   iteration. No new sitting; stale assignment stands.
 - tPL-B2 content law is ported and witnessed (docs/re/_wip_tPLB2.md P8/P9):
   rewrite/src/ui/indpopups.{h,cpp}, popupLinesFor(), indicatorPopupRect(),
   pins test_indpopups_tplb2 x6, seed-5 witness text-exact. WHAT IS OWED is
   the FRAME leg (item 9), not the text leg.

TWO LEGS:
 L1 (item 10, measurable first): vertical placement law of the indicator-strip
     record inside its panel — planres/planind/planpro record bbox vs the drawn
     frame. Expect a Y-offset / clip-window bug in the port.
 L2 (item 9): which SHAPEFRAME/frame resource the popup widget carries
     ("mineral framing") + the popup rect size law, cited from windows.txt +
     the widget-frame blit path.

## P1 — INDUSTRY-TILE VERTICAL LAW MEASURED [verified, scripts/tPF5_strip_bbox.py]

The bbox census over the three gauge libs (port loader law: signed quad at
`stream-0x10`, W=R-L+1, H=B-T+1 — rewrite/src/formats/shp.cpp:176-179, tA1)
against the windows.txt rects PLRES 7,7..114,106 / PLIND 123,7..230,106 /
PLPRO 239,7..346,106 (all 108x100):

  LIB        L    T         R    B     W     H      records
  planres    0    0        107   99   108   100     ALL 21  (full-bleed)
  planpro    0    0        107   99   108   100     ALL 21  (full-bleed)
  planind    0   {23,20,11,5,1} 107 99   108   {77,80,89,95,99}

planind is the ONLY lib whose records are not full-bleed, and its top edge
steps by gauge level: rec 0-1 T=23 (H=77), 2-5 T=20 (H=80), 6-7 T=11 (H=89),
8-12 T=5 (H=95), 13-20 T=1 (H=99). R=107 and B=99 on ALL 63 records: the
content is anchored to the BOTTOM-RIGHT of the 108x100 box.

THE BUG (port, cited site rewrite/src/ui/ui.cpp:2356-2358 pre-fix):
  blitShape(ren, gl, sp.gauges[gi].rec, sp.gauges[gi].rect.x0, rect.y0)
passes the RECT ORIGIN as the blit anchor and drops the record's (L,T). So the
port paints planind rec k at screen y in [7, 7+H) — the content sits at the
TOP of the frame and leaves a bottom band of 100-H = 23/20/11/5/1 px of
whatever was underneath (the 17np starfield k4 covers y 115..472, so above
y=115 the band is the panel backdrop = black). The cited vendor placement law
is dest = anchor + (L,T) (P2), which paints y in [7+T, 7+T+H) — bottom-aligned,
band at the TOP, exactly the complement. User verbatim (item 10): "too high in
the frame, with the top cut off. On the bottom there is either an empty black
band, or the top of the next image in the series" — the port-half symptom of
the dropped T, and the "or the top of the next image" alternative is the user
seeing the band expose neighbouring art. HEIGHTS WERE ALREADY CORRECT IN THE
PORT (the census matches the tA1 note in planetstrip.cpp); ONLY THE ANCHOR WAS
WRONG.

SECONDARY FINDING — the stale doc claim: rewrite/src/ui/planetstrip.h:9-13
asserted "each hold EXACTLY 21 records, ALL 107x99" and the conformance gate's
error string still said "!= 107x99 (rect-fill)". Both FALSE under the bbox law
(width is 108, planind heights vary). The gate CODE was already relaxed to
width-only at planetstrip.cpp:54 — the DOC was never updated. Item 10's fix
must not re-tighten the gate on height, since planind heights are law.
(Corrected this iteration; P4.)

ANCHOR-BLINDNESS OF PRIOR WITNESSES [verified]: 17np quads are L=0,T=0 for
k0,k4,k5,k6,k6,k7,k8 (the field/pop records the port registers), so the t428c
"registration of k4 at exactly screen (7,115), 158/269 tol-8" CANNOT confirm
or deny the (L,T) term — a zero anchor is invisible to a position census.
planind is the first lib in the project whose painted records have T != 0,
which is why the dropped anchor survived every prior pixel witness.

## P2 — VENDOR ANCHOR LAW CLOSED AT RAW BYTES [verified work/ascend_restored.bin]

FUN_0005caac prologue disassembled this iteration (capstone via
~/tools/revenv, region 0x5caac..0x5cb90) — the S12 arg-map note said the entry
rect fields are read "+screen"; the bytes now say exactly how:

  0x5cb41 mov eax,[ebp-0x4c]      ; clipL of the CALLER shape-struct (clamped >=0)
  0x5cb44 add [ebp+0x14], eax     ; screen_x += clipL
  0x5cb47/0x5cb4a                  screen_y += clipT (same shape)
  0x5cb4d..0x5cb59  esi := payload + [payload + 8 + 8*sel]   (record entry)
  0x5cb61  dest_x = [esi+0x8]  + [ebp+0x14]     <-- RECORD L ADDED
  0x5cb6a  dest_y = [esi+0xc]  + [ebp+0x18]     <-- RECORD T ADDED
  0x5cb73  right  = [esi+0x10] + [ebp+0x14]
  0x5cb7c  bottom = [esi+0x14] + [ebp+0x18]
  0x5cb85  add esi,0x18            ; stream = entry+0x18 (S12 confirmed)
  0x5cb8b  cmp right,dest_x -> 0x5cea5 (error -3 fully outside)
Widget pass FUN_00031384 shape-blit arm 0x3143a..0x31467 pushes
[desc+9]>>16 then [desc+7]>>16 as the x/y, so the descriptor supplies an ANCHOR
and the record's bbox corner is added on top. CONCLUSION: dest = anchor + (L,T)
is LAW, not inference.

## P3 — BLAST AREA [measured scripts/tPF5_anchor_census.py]

Every lib the port draws through blitShape, counting records with L!=0 or T!=0:
  planres 21 recs  0 anchored      planpro 21 recs  0 anchored
  planind 21 recs 21 anchored  (0,1)x8 (0,5)x5 (0,11)x2 (0,20)x4 (0,23)x2
  17np k1,k2,k3 anchored (1,1)/(2,1)/(1,1); k4 (field) (0,0)
  planitem all 40 NEGATIVE anchors (L,T ~ -34,-17) — the port centres these
    deliberately (structure art is centre-anchored), NOT touched this task
  smship19 recs negative (-66,-41) etc — ship-row art, tPF-4, NOT touched
  planal* 55/55 records negative ((-47,-48) x11, (-75,-75) x11 ...) — the
    planet disc, port centres by gcx-W/2, NOT touched
Rationale for the narrow fix: positive-T records are the strip's; the negative
anchors are centre-anchored art the port already positions by its own centre
law, and adding (L,T) there would shift 95 already-witnessed pixels for no
cited reason. Fix scope = the three strip panels ONLY.

## P4 — FIX SHIPPED + PINNED [build+suite green]

 - NEW pure law fn ui::stripGaugeBlitPos(rect, recLeft, recTop) in
   rewrite/src/ui/planetstrip.{h,cpp} -> {x0+L, y0+T}. ui.cpp strip call site
   now composes it (blitShape(ren, gl, gr.rec, gp.x, gp.y)); planres/planpro
   unaffected (L=T=0).
 - STALE DOC CLAIMS CORRECTED (they asserted a law that is false under the bbox
   law, and would have been re-tightened into a fabricated gate):
   planetstrip.h header block, planetstrip.h gate comment, planetstrip.cpp gate
   error string ("!= 107x99 (rect-fill)" -> width-108 + varying-height law).
 - PINS rewrite/tests/test_stripanchor_tpf5.cpp x6 (CMakeLists entry ADDED —
   tPF-4's silent-zero-tests trap avoided): (1) planind is the only anchored
   lib + the exact T ladder {23,23,20x4,11x2,5x5,1x8} + H==100-T + anti-vacuity
   assert; (2) bottom-right pinning for all 63 records THROUGH the shipped fn;
   (3) dropped-anchor-is-the-bug: shipped y == y0+T on all 21, old band == T,
   new band-below == 0, differ==21; (4) ui.cpp call-site wiring (source-text
   pin, tngs_s29 precedent — anchorless form must be ABSENT); (5) pure-law
   synthetic args (added after mutation round 1, see P6); (6) gate accepts
   varying heights, rejects 17np on count.
 - SUITE 564 -> 570, 0 skipped, 0 failed. Build both ascendancy AND run_tests.

## P5 — LAW LINE + PORT WITNESS [measured 2026-11-25, seed 5]

ui.cpp strip paint now logs once per (lib,rec):
`ui strip <lib> rec <k> bbox(L,T) rect(x0,y0) blit(x,y)`. Seed-5 planet view
(scripts/tPF5_port_witness.sh, Xvfb :99, 640x480, PID-only kill law):
  ui strip planres.shp rec 0 bbox(0,0) rect(7,7)   blit(7,7)
  ui strip planind.shp rec 1 bbox(0,23) rect(123,7) blit(123,30)   <-- ANCHOR LIVE
  ui strip planpro.shp rec 1 bbox(0,0) rect(239,7) blit(239,7)

DIFFERENTIAL PIXEL CENSUS (scripts/tPF5_witness_census.py, fixed-vs-mutant
builds of the identical rig; mutant = stripGaugeBlitPos -> {x0,y0}):
  FIXED  band rows 7..12 mean (0,0,0) non-black 0.000 | foot 100..106 (116.7,71.1,50.8) nb 1.000
  MUTANT band rows 7..12 mean (28.6,19.7,21.4) nb 0.958 | foot 100..106 (0,0,0) nb 0.000
  C1 fixed band backdrop PASS; C2 fixed foot art PASS; C3 MUTANT band art
  PASS; C4 MUTANT foot black PASS; C5 differential in-rect 0.942, outside
  0.000 PASS -> VERDICT PASS. The mutant build reproduces the user's exact
  words: art high in the frame + black band at the bottom; the fixed build
  bottom-anchors the art. First census draft used PLPOP rows 7..12 as the
  backdrop control — WRONG (the pop grid paints there); replaced by the
  mutation-control differential. Second draft thresholded the band on
  luminance >40 — WRONG too (the art's own top rows are dark ~28,20,21);
  non-black-fraction is the valid discriminator. Both traps banked.
NOT claimed: pixel-identity with the vendor (no vendor planet-screen capture
at 1:1 exists; the claim is law-conformance + bug-shape reproduction).

## P6 — MUTATION CAMPAIGN [scripts/tPF5_mutate.py; final 5/5 CAUGHT]

Round 1 (before the synthetic pin): 4/5 CAUGHT.
  M2 drop-T CAUGHT / M3 sign-flip CAUGHT / M4 swap-L-T CAUGHT /
  M5 ui.cpp call-site neutralised CAUGHT (named FAILs in
  stripanchor_tpf5_bottom_right_pinning + dropped_anchor_is_the_bug).
  M1 drop-L MISSED — EQUIVALENT MUTANT ON DATA: every strip record carries
  L==0 (P1 census), so no data-driven pin can see an L-term mutation. Fixed
  per skill rule 6 by adding stripanchor_tpf5_pure_law_synthetic (pure-fn
  args the data never produces: (7,-3), (5,23), axis-independence). Standalone
  re-run of M1 after the pin: CAUGHT (3 failed tests). Round-2 suite 570/0/0
  green after restore (md5-verified).
HARNESS INCIDENTS (all mine, all recovered, all banked as skill traps):
  (a) ROOT CAUSE OF THE POISONED ROUND 1: the campaign was NEVER dead — its
      stdout was BLOCK-BUFFERED, so the log stayed empty while it ran and
      mutated files. I read "empty log" as death, pgrep'd only the wrapper PID,
      and restored target files under the still-live python child, corrupting
      round-1 verdicts (and the SIGTERM'd child's late reap landed its finally-
      restore after my commit — tree verified clean post-hoc, suite 570/0/0).
      Lesson: pgrep -f is the ONLY liveness test; launch line-buffered
      (sys.stdout.reconfigure) so an empty log stops being ambiguous. Round 2
      ran fully detached, line-buffered, and completed 5/5.
  (b) an execute_code decorator edit nearly turned main() into a print-call —
      caught by re-reading before building.
  (c) FILE-APPEND TRAP: `open(p,"w").write(open(p).read()+append)` truncates p
      BEFORE the inner read (Python evaluates the target expression first), so
      the append silently REPLACED the file — P1..P4 of THIS file were lost
      once and reconstructed from the session record. Append correctly: read
      into a variable FIRST, then open("w"); or open(p,"a").

## P7 — ITEM 9 (POPUP FRAME) STATUS: CLOSED 2026-11-27 BY tPF5-A

[CLOSED: the named-open seam — "which lib the 0x9f10c cache path resolves
for the INDICATOR widgets" — was MEASURED: ds:0x6fd8e == id 37 ==
'data\\help.shp', frame record 0, blitted by the builder itself at the
WIDGET ORIGIN before the key switch (live-RAM 60/60 saves). Same answer as
the tile popup, three-way-verified on PLSQUARE's rect. Shipped + pinned +
mutation 5/5 + runtime witness PASS: docs/re/_wip_tPF5A.md P0-P7, law
planets-ui.md S18. The D1-gate sentence below was STALE (OQ-005 CLOSED
t367; research.md S14(f)).]

Item 9 asks the top-frame popups to carry "the same mineral framing" as the
tile-click popup. What exists: tPF-2d D8 MEASURED help.shp k0 (336x256, bbox
(0,0,335,255) — measured this session with the port loader law) as the popup
frame pixelwise (extents == popup rect, cut-out rows 217..247 == button-band
constants 0x151/0x16f), and D9 closed the frame-word writer law (windows.txt
SHAPEFRAME -> 0x57e10; PLSQUARE carries SHAPEFRAME 0 = record 0 of the popup
lib). The indicator popups (tPL-B2) currently draw the port's vector frame
(ui.cpp dim fill + outline, ~line 2871). The remaining unknown is the ONE
thing D9 named open: which lib the 0x9f10c cache path resolves for the
INDICATOR widgets (the tile popup answers help-by-three-way-agreement;
PLIND/PLPRO/PLPOP/PLRES records in windows.txt carry no SHAPEFRAME word of
their own — re-verify before shipping). Per D1 the help.shp-k0 FRAME ART SHIP
is gated on the user's OQ-005 ruling, so item 9 cannot close this iteration
by strict-close: the frame art is the only closing evidence and it is
user-gated. Named-open seam recorded as TPF5-A.

## P8 — LEDGER

tPF-5 tracks NO OQ row (like tPF-4: the D28 build-feedback items are not OQ
rows). HONEST NEGATIVE: no row closed this iteration; open=[016,019]
unchanged. Suite 564 -> 570 (stripanchor x6). Gate + ledger audit in STATE.md.
