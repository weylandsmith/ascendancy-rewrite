# _wip_tPF10 — RESEARCH HOVER/SELECT VISIBILITY (D28 items 19/20)

Working log, 2026-11-26. Control: STATE.md NEXT ACTION.
Sitting check ran FIRST (scripts/r1_t85g_sitting.py exit 0,
work/r1/tPF10_pre_sitting.out): byte-identical (mod path line) to
tPF9_pre_sitting.out — no new sitting, stale assignment stood.

## P0 — what is already in hand (do NOT re-derive)
- Frame law (docs/re/research.md L357-359): resring.shp 4 records = frames
  by state law 0x483fa..0x48470: 1 default; 0 iff row==studied AND not
  owned; 3 iff owned; 2 iff row==word[win+0x9db] (path 0x5caac).
- Hit/select sub 0x47478 banked verbatim (work/tRS_reswin_fn.asm L6274+).
- Port: resNodeFrame researchview.cpp:302; ui.cpp resSel set on CLICK
  (:960), cleared on screen re-entry (:3595); frame call site ui.cpp:3229.
- tPF-8 zero-start law + tPF-9 stray-text law CLOSED; D28 file
  scratchpad/t433-build-feedback.txt items 19/20 (verbatim): click
  highlights but no set-project indication + no persistence; correct =
  hover BLUE, click YELLOWISH.

## P1 — THE HOVER LEG (measured from the banked disasm, this session)
work/tRS_reswin_fn.asm 0x47478..0x47564 VERBATIM: the select sub reads the
GLOBAL mouse words [0x484ec]/[0x484f0] (minus window origin [win+8]/[win+0xc]),
hit-tests the legality-gated projected table, and at 0x47533..0x47555
STORES the hit row (or 0xffff when nothing is under the cursor) into
word[win+0x9db] on CHANGE. The sub is called from EVERY arm of the message
switch (call sites 0x477b4, 0x477f8, 0x47892, 0x4791b, 0x47997, 0x479d3,
0x47a0e, 0x47a45, 0x47a6c, 0x47a93, 0x47ac7, 0x47aeb, 0x47b1a, and the
DEFAULT fallthrough 0x47b33) — and the fire-loop pump msg 0x3a (self-
registered interval-0 at 0x47713, tPF-7 law) drives that switch ~29x/s.
=> word[win+0x9db] is a HOVER-TRACKED word: it equals the legal row under
   the cursor, or 0xffff when the cursor is off any disk. It is NOT a
   click-latched selection. The tRSB1 label "SELECTED row word" is a
   MISNOMER (corrected here; commit leg 0x47d99 merely READS it at click).
Consequences (pending frame-law raw confirmation P2):
- vendor frame 2 (0x5caac path) paints WHILE HOVERING, not after click;
- moving the mouse off the clicked disk removes frame 2;
- re-entry clears it (0x476f2 word=0xffff) — the vendor does NOT persist
  any ring highlight across screens either; what PERSISTS after commit is
  the studied row DAT_00076492 (frame 0 + disk fill q + panel text).

## P2 — FRAME LAW RAW (work/tPF8_gate.asm 0x483fa..0x48504, re-read this session)
esi=1 default; studied&&not-owned -> 0 (0x48410..0x4842e); owned -> 3
(0x48430..0x48452); THEN row==word[win+0x9db] -> 2 LAST-WRITE WINS (0x48460
..0x4846b) — so a HOVERED owned row draws frame 2, and a hovered studied
row draws frame 2 (frame 0 only visible when not under the cursor).
Blit split: esi==2 -> FUN_0005caac (0x484c4), else FUN_0x5cf96 (0x484fc).
EDGE LOOP (work/tPF10_edge.asm, fresh disasm 0x48275..0x48340): per-prereq
leg; colour 0x6b - clamp(chop(...),+-3) (0x48308); `cmp prereq, word
[win+0x9db]` -> 0xf3 (0x48314..0x48321) — the EDGE highlight is keyed on the
SAME hover word, not on a click state. The port's edge 0xf3 arm (ui.cpp
:3187) and frame arm (ui.cpp:3229) both read resSel — so BOTH symptoms the
user reports are ONE word's lifetime: the port latches it on CLICK (:960)
and never updates it on MOTION; the vendor tracks it on HOVER (pump-driven
0x47478, cleared to 0xffff off-disk) and never latches it on click.
NOTE frame 2 is LAST so hover overrides owned/studied visuals; the commit
leg (0x47d99, click dx>3) only READS the word -> DAT_00076492[race]=row.

## P3 — RING FRAME COLOURS MEASURED (resring.shp k0..k3, this session)
Method (authority = the PORT'S OWN decoder, the same code path the screen
uses): ShapeLibrary::decode plane 29x29, 828 non-zero px (the exact n the
tRSV1d pixel witness counted on screen), x game.pal under the port's 6->8
law c=(v<<2)|(v>>4) (gamepal.h). Ring-mean RGB (pinned in
tests/test_hoverselect_tpf10.cpp +-6):
  k0 STUDIED-not-owned  mean (170,108, 75)  WARM/WHEAT
  k1 default            mean ( 63, 99,145)  dim blue-grey
  k2 word==row          mean ( 76,157,198)  BRIGHT BLUE, brightest frame
  k3 owned              mean (171,104, 99)  warm red-brown
TRAP BANKED: tools/shp_pngdump's raw .idx plane for resring is a PARTIAL
walk (197 px, mean k2 (69,149,192)) — it disagrees with the port decode
and with the on-screen witness; measure planes through formats/shp, not
the dump tool, when the numbers become pins.
USER-RULE (scratchpad/t433-build-feedback.txt 19/20 verbatim): hover ->
"highlighted blue" = k2 EXACTLY [verified]; click -> "kind of yellowish"
maps to the WARM k0 studied ring (the post-commit visual of the vendor
model), NOT to any frame-3 gold — the old research.md "gold path 0x5caac"
label was a MISREAD (0x5caac is merely the frame-2 blitter; frame 2 is
BLUE at pixels). [inferred] bridge: the user's memory collapses the
hover-blue flash + post-click warm settle into "click turns yellowish";
the two-word model (hover word k2 / studied word k0) reproduces BOTH
halves without any yellow frame existing in the lib. Vendor day-20 repro
stays user-time-gated (D30) — not claimed as pixel identity.
=> THE FIX: word[win+0x9db] semantics = HOVER (pump/motion hit-test,
0xffff off-disk), never click-latched; the port's resSel (click latch) is
the defect. Commit reads the hover word; studied-row visuals ride the
DAT_00076492 analog (already ported as queuedRow).
