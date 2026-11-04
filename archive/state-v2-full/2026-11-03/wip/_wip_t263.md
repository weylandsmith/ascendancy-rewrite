# WIP t263 — REWRITE POP-PANEL (2026-11-02)

Task: implement the population panel visualization law in rewrite/src/ui/ —
capacity-sized slot array; empty circle (k3) / free-pop yellow front (k2) /
busy-pop sideways red (k1) from 17np.shp. Pure code + pins (t199 house pattern:
planets-ui.md S3/S4 laws landed as no-SDL code in src/ui + tests).
Law sources: docs/re/planets-ui.md S4 (0x3ce39..0x3cef8), docs/re/shp.md S23
(t254 identification), docs/re/_wip_t254.md S5/S7.

## S0. Pre-flight
- git status clean at session start; :9 untouched (zero clicks/turns, no
  loadstate — REFUTED t261 honored). Timeline growth = watcher churn on the
  parked t1236 campaign; r1_t85g_sitting.py NOT run (no new sitting; the
  t262 LANDED block records the drive completed at t1236).

## S1. gwshare.txt entry census RE-MEASURED this session (file half of the
library-identity chain; live-RAM half cited from t254) [verified]
extracted/ascend00/gwshare.txt, cp437, 64 physical lines, blank-line
separators, 0x1a terminator on line 64:
  45 .shp entries (0-based entry index = CACHE SLOT INDEX, t254 law
  "slot == gwshare line - 1" restated precisely: blanks make the PHYSICAL line
  number wrong as an index — entry #44 17np sits on physical line 63).
  Entry #41 = data\14intel.shp  (t254 control: live cache slot 41 -> 14intel)
  Entry #44 = data\17np.shp     (t254 measurement: u16[DAT 0x6fd9c] = 44 ->
                                cache slot 44 verbatim copy == 17np.shp)
  Both entries are .shp; the 46th non-blank line is the 0x1a EOF marker, NOT
  an entry. Pinned by test_poppanel_gwshare_entry44_t263.

## S2. 17np.shp record census this session (V/A law, shp.md S16/S17) [verified]
container: magic '1.10', count=9, tsz=80 == 8*(9+1), filesize 43688.
  k0 639x479 (panel frame)   k1 9x9   k2 7x9   k3 8x8
  k4 625x357  k5 416x316     k6 2x2   k7 2x2   k8 2x2   (k6..k8 = legend dots)
All 9 records walk canonically (H rows; Python walkRows replica).

## S3. CONTENT FIXTURE — palette census on k1/k2/k3 (game.pal 6-bit v*255//63)
[verified, this session; the byte-level icon<->role binding the pins enforce]
  k1 (SEL 1 = BUSY): 41 painted px of 81. Hue classes: red/skin 25 (idx 80-85:
     186,36,56 red body + 234,129,97 skin), blue 9 (idx 105-107: 24,48,109...
     = the "blue tool" t254 vision saw), orange 7, plus idx121 x1.
     -> red-dominant + BLUE TOOL pixels present.
  k2 (SEL 2 = FREE): 30 painted px of 63. NO blue pixels at all; dominant idx89
     x12 = rgb(255,206,24) hue 47 = YELLOW front figure (+ orange shades 92-95,
     red shade 117 x2).
     -> yellow-dominant, zero blue.
  k3 (SEL 3 = EMPTY): 44 painted px of 64 — a RING: the interior (rows 2..5 x
     cols 2..5) is NEVER painted (stream skips it; center pixel untouched =
     transparent). Palette all cool (idx 147-150, green/teal 16,165,36...).
     -> hollow circle law, byte-confirmed.
These counts are the fixture; the role names come from the cited law chain
(planets-ui.md S4 SEL order + t254 vision/player testimony corroboration),
NOT from the pixel classes. The pins make the binding executable: swapping
SEL1<->SEL2 record assignment fails k1's blue-tool test and k2's no-blue test.

## S4. Paint-origin detail from the raw case-3 prologue (work/t198_planwin.asm,
re-read this session) [verified asm, semantic part inferred]
0x3ce39: esi = widget field; eax = 0xf2 (242) if esi!=0 else 0x96 (150);
push eax; push desc+4; CALL 0x5e940 — a per-case setup call planets-ui.md S4
did not record (clip/origin class [unverified semantics]). THEN EBP=EDI=0 and
the loop blits (cache 0x9f10c, [0x6fd9c], sel, EDI, EBP) with EDI += 0x0a per
slot, idiv-10 remainder==9 -> EDI=0, EBP += 0x0a. EDI/EBP enter the blit as the
x/y args; they start at 0,0, so the coordinates are widget-relative AFTER the
0x5e940 call [inferred] — the t254 live pixel census (grid inside the PLPOP
panel region, rows of ten) corroborates panel placement. Modelled as an
explicit origin parameter; default = panel-local (0,0).
Belt-and-braces on the loop (verbatim from this session's objdump):
  0x3ce81 mov [PL+0x4a],dx; cmp esi,dx; jge 0x3d1bc      ; cap exit
  0x3ce8d mov [PL+0x4c],ax; cmp eax,esi; jne; incl sel   ; used increment
  0x3cea3 mov [PL+0x42],ax; cmp eax,esi; jne; incl sel   ; pop increment
  0x3ceb8 mov 0x6c(%esp),ax (selector); 0x3cec0 mov [0x6fd9c],dx; cache
  0x3cee5 idiv 10; 0x3cef2 cmp edx,9; 0x3cef4/6 EDI=0; EBP+=10
=> SEL(i) = 1 + [i>=used] + [i>=pop] over i < cap — matches
Campaign::popBands (campaign.h:319) exactly.

## S5. Panel capacity arithmetic [verified from windows.txt + campaign.cpp]
PLPOP rect (windows.txt:1587..1594): X0 355 Y0 7 X1 454 Y1 106 -> 100x100 px.
Pitch law: 10 slots/row x 10 px -> the panel holds EXACTLY 10 rows = 100 slots.
storedCapFor clamps cap to 0..100 (campaign.cpp:811, income-law.md S10 t33).
So the +0x4a clamp bound == the panel's physical slot capacity — the paint
never overflows the panel, and cap=100 exactly fills it. Live corroboration
(t254 Vega IV): cap=39 -> rows of 10,10,10,9 with cell index 39 (row 3 col 9)
NEVER painted = the cap-exit branch observed live.

## S7. SHIPPED (this session)
- rewrite/src/ui/poppanel.{h,cpp} — popSlotRecord (identity law), popSlotRoleOf,
  popPanelCells (pitch grid, vendor order), popPanelRows (ceil(cap/10)),
  popPanelFor (campaign compose), popSlotLibraryConforms (9-rec + k1/k2/k3
  dims gate), kPlPopRect/kPopSlot* constants. No SDL.
- rewrite/CMakeLists.txt: poppanel.cpp -> ascend_ui AND run_tests (layout.cpp
  precedent); tests/test_poppanel_t263.cpp added.
- rewrite/tests/test_poppanel_t263.cpp — 4 pins:
  poppanel_gwshare_entry44_t263 (S1: 45 entries, #41=14intel, #44=17np,
  last=17np, 0x1a not an entry);
  poppanel_17np_library_census_t263 (S2/S3: dims census, conformance gate +
  14intel rejection, k1 red>0 AND blue>0, k2 yellow>0 AND blue==0, k3 centre
  16/16 untouched, identity selector 1..3 + out-of-range -1, role map);
  poppanel_grid_geometry_t263 (S5: rect 355,7..454,106 == 100x100 == 10 rows
  x pitch; rows law incl. cap<=0 -> 0, 39 -> 4; cell positions incl. row-wrap
  and origin offset);
  poppanel_campaign_integration_t263 (seed 2024, every star: cells ==
  popBandsFor, selector == vendor formula, positions == pitch law, all inside
  the panel).
- RESULT: 141 tests 0 failed (137 -> 141).
- MUTATION PROBES (suite is load-bearing, both measured then reverted):
  (a) swap SEL1<->SEL2 record assignment -> 103 failures across three pins
      (census identity, geometry record binding, integration per-star);
  (b) swap k1/k2 dims in the conformance table -> popSlotLibraryConforms
      fails on the real 17np file (1 failure). Reverted; final gate rebuild
      re-verifies.

## S8. Honest notes / non-claims
- The role NAMES (busy/free/empty) remain the cited law chain
  (planets-ui.md S4 band order + t254 vision/player corroboration). The pixel
  census is corroboration made executable, NOT an independent semantic proof
  that SEL 1 means "working" — that ordering law is the asm (used <= pop).
  R13 respected: no self-grading of renders claimed as ground truth.
- The 0x5e940 setup call's semantics (clip vs origin) stay [unverified]; the
  layout law is origin-parameterised so the default (0,0) is the widget-local
  frame the loop demonstrably uses (EDI=EBP=0 at 0x3ce59/0x3ce67), and the
  t254 live census placed the painted grid inside the PLPOP region.
- No sprite is DRAWN anywhere: ui.cpp untouched; OQ-005 scope (no vendor
  shapes on screen yet, ui-runtime.md §2) unchanged. This module is the
  selection/geometry layer the blit will consume — exactly the t199 pattern
  for the gauges.
- NO OQ CLOSED (strict-close): t263 is rewrite-wiring of already-cited law.
  OQ-005/016/019/021 untouched; OQ-005 needs the USER's index.txt ruling and
  this session neither sought nor needed it.
- PENDING in this task: ui-runtime.md §2a amendment (it still speaks of the
  pop panel only via t199's popBands; done below in the docs step).
