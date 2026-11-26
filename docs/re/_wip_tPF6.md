# tPF-6 WIP — ORBITAL CLICK + HOVER CPU (D28 items 11+12)

Item 11: orbital squares show hover outline but clicking does nothing; vendor
pops an info/context window (build menu once orbital tech researched).
Item 12: hover unresponsive + CPU 100% while hovering that area.

SITTING CHECK ran FIRST (scripts/r1_t85g_sitting exit 0,
work/r1/tPF6_pre_sitting.out): trusted turn-change rows 45,227, newest t=1335
— identical to tPF-5's check; the 10.4 GB file growth is the watcher's own
rewrites (tPF-2b law). No new sitting; stale assignment stood.

## P0 — starting facts (from closed laws, do not re-derive)
- Orbital slots: 10, origin (13,119), pitch 70, col k%2, row k/2
  (planetview.h orbitalSlotOrigin, FUN_0003b96c loop 2; docs/re/_wip_tPLV2.md).
- Hit law FUN_0003a880 verbatim: x in [14,152] y in [120,468] (1px inside
  paint origin), k=(x-13)/70 + 2*((y-119)/70). Port orbitalSlotHitFor.
- Hover outline law 0x3c546..0x3c5d7: 69x69 box OUTLINE pal 150 iff hovered
  cell == +0xac PER SLOT, slot EMPTY, no pick pending (orbitalHoverOutline).
- Popup law (tPF-2d, closed): button id array + ABSOLUTE band y 337..367,
  x0=160, w=(479-x)/n, n==1 -> label(30) 'OK'; labels via registry
  u32[ds:0x744a0+id*4] (51 Cancel 54 Build 53 Abandon ...).
- Square popup content law (tPF-2): builder key-3 case 0x3de5a..0x3e2c8;
  orbital body getter(90); title getter(89) "<Colour> Square".
- WITNESS TRAP: build BOTH run_tests AND ascendancy before witnesses.

## P1 — CODE READ: both arms traced (ui.cpp @ HEAD 8b33de4)
ITEM 11 (click): the click chain DOES route orbital slots:
  - order leg (pick pending) ui.cpp:1106 and select leg ui.cpp:1174 both call
    orbitalSlotHitFor BEFORE tileHitFor (x<=0x98 vs lattice >=~230: disjoint).
  - select leg sets planetCell = surf+k, arms squareInfoLines (title 'Orbital
    Square' ALWAYS non-empty, getter(83)+(90)) and popupButtonIds(cellItem=0xff
    for an empty slot) -> [54,51] via placementBlock, whose ring legs are the
    cited 0x3830c domain laws (XOR 0x384db: orbital item 22..30 on ring cell
    passes; adjacency 0x385b7 jae skips ring; rock skipped ring-side).
  - Build button -> PLANLIST armed on planetCell -> pick orders via the
    msg-0x1c01 step-2 arms (ui.cpp:1036).
  => [inferred] the click arm may ALREADY work in the current build; the user's
  complaint predates tPL-V2/tPF-2d landing (same day). WITNESS DECIDES — do not
  claim before a live run.
ITEM 12 (CPU): the port loop is SDL_WaitEventTimeout(&ev,16) (ui.cpp:658) =
  60fps-capped; hover outline is computed PER SLOT per frame inside the paint
  (ui.cpp:2690 SDL_GetMouseState + orbitalHoverOutline k-loop) but the PAINT
  runs every frame regardless of hover — hover does NOT add a recompute class.
  The vendor DOES repaint per hover event (hover word +0xac @0x3ac14 -> full
  repaint), so item 12 is plausibly a VENDOR bug inherited by symptom, not a
  port regression. MEASURE, don't assert: sample /proc/<pid>/stat utime+stime
  idle vs orbital-hover vs map-hover on seed-5 Xvfb.
NOTE xsend 'warp' = XWarpPointer pointer-only (no button events) — but SDL
  motion events only fire if the X server delivers them under Xvfb; the tPL-V2
  hover census PASSED via warp, so motion DOES flow. Use rapid warps for the
  hover-leg CPU sampler.

## P2 — LIVE WITNESS RUN 1 (scripts/tPF6_witness.sh, seed 5, Xvfb :99, build aaa2818d)
- ITEM 11 CORE **WORKS TODAY**: click (48,154) -> log 'ui planet tile 23
  selected (Orbital Square ids=54,51)' -> Build band click -> 'ui planet popup
  build cell 23' -> PLANLIST 'opts n=8 [0,1,2,20,21,22,23,26]'.
- REMAINING DEFECT CAUGHT: pick row 0 (Factory, SURFACE item) on the armed
  ORBITAL cell -> 'ui planet project Amoroso I Factory (rejected armed cell
  23)' — placementBlock SurfaceVsRing is CORRECT (item 0 < 22 surface), but the
  LIST offered it anyway. Vendor law (t43 banked, placementBlock comment): the
  PICKER filters by the checker. => port fix: filter PLANLIST options by
  placementBlock(armedCell) when armed. PORT UX decision under D30, not a
  vendor-pixel claim.
- ITEM 12 MEASURED (/proc stat utime+stime, 5s windows, planet screen):
  idle 41.2% / orbital-hover 46.2% / lattice-hover 47.4% of one core.
  Hover is NOT the cost driver on THIS host; the planet screen's CONSTANT
  full repaint at 60 fps is (41% idle!). The loop is one-event-per-frame
  (ui.cpp:658 WaitEventTimeout(16)); with a motion FLOOD each event can
  trigger its own repaint (unthrottled). User's 100% on slower hardware is
  consistent with the constant-repaint floor + flood amplification.
  MECHANISM TEST owed: flood warps with NO sleep -> if CPU >> 47%, per-event
  repaint confirmed.
- HARNESS: 'window died before release' stderr = known red herring (t439).

## P3 — ITEM 12 MECHANISM CLOSED (measured, negative for the hover hypothesis)
scripts/tPF6_cpu_probe.sh (seed 5, planet screen, /proc stat utime+stime):
  idle 37.0% / slow-hover(1 warp/s) 47.2% / FLOOD-hover(3 warps back-to-back)
  41.2% / idle-after 42.2%.  FLOOD >= idle within noise => MOTION IS NOT A
  COST DRIVER. Code corroboration (draw block ui.cpp:1491-3562): the paint is
  UNCONDITIONAL full-screen every loop iteration (SDL_RenderClear + full
  blit-set + RenderPresent) — the loop never skips a repaint, so hover cannot
  add a repaint class; motion events only update projectHover (ui.cpp:690-702)
  and the per-frame SDL_GetMouseState reads.
  VERDICT [measured this host + cited code path]: the user's "CPU jumps to 100%
  while hovering the orbital area" is the PLANET SCREEN'S CONSTANT ~40%-of-a-
  core full-repaint floor (60 fps, accelerated renderer, fast host) saturating
  slower hardware, NOT a hover-specific bug. The vendor likewise repaints on
  hover (hover word +0xac @0x3ac14 -> repaint), so there is no vendor hover
  economy to port. SEAM TPF6-CPU-A named-open: what makes the planet paint
  37% idle-cost (candidates: chrome/strip blit set, tile lattice) — perf
  optimisation is a PORT decision, not vendor law; no fix shipped this
  iteration (honest negative on item 12).
## P4 — ITEM 11 SHIP SPEC (the remaining gap witness run 1 caught)
popupButtonIds ALREADY passes the cell-aware checker (ui.cpp:1203-1208) => the
popup's ids=54,51 for an empty ORBITAL slot is the vendor law working (checker
0x3830c item-arg passes for orbital items on ring cells: XOR leg 0x384db both-
non-surface OK; adjacency 0x385b7 jae skips ring; rock skipped ring-side).
THE BUG: PLANLIST itself offers surface items on an armed ring cell -> pick ->
'rejected armed cell 23'. Vendor corroboration: the 54-append loop 0x3d550..
0x3d58e calls checker 0x3830c(item, cell) PER ITEM before appending Build —
the vendor NEVER offers a Build it would refuse. Port fix (D30-legal, cited
via the t43 picker law docs/re/income-law.md S13 + _wip_tPLB1.md:281):
projectOptionsFor(camp, star, armedCell) drops items with a non-None
placementBlock for the armed cell; call sites ui.cpp:1006/1027/2763 pass
planetCell when planetCellArmed.

## P5 — SHIPPED: ARMED-CELL PLANLIST FILTER (item 11's real gap)
- rewrite/src/ui/{planetview.h,planetview.cpp}: projectOptionsFor(camp, star,
  armedCell=-1); when armedCell >= 0, drop items placementBlock refuses for
  THAT cell. -1 keeps pre-tPF-6 membership EXACTLY (plain PLBUILD path).
- rewrite/src/ui/ui.cpp: all THREE call sites (scroll clamp, row pick,
  painter) pass planetCellArmed ? planetCell : -1.
- Vendor corroboration [verified asm tPF-2d D6]: the 54-append loop
  0x3d550..0x3d58e calls checker 0x3830c(item, cell) per item BEFORE
  appending Build — the vendor never offers a Build it would refuse. [inferred
  bridge, D30-legal]: therefore the item list behind a Build button on an
  armed cell holds only checker-pass rows. (The vendor PLANLIST's own
  per-cell filtering site is unrecovered — seam TPF6-B named.)
- PINS tests/test_optionsfilter_tpf6.cpp x2 (CMakeLists entry ADDED — the
  tPF-4 silent-ship trap): kept-set law ring/surface both directions +
  non-emptiness anti-vacuity + wiring pin (all 3 ui.cpp call sites carry
  planetCellArmed). Suite 570 -> 572/0/0.
  Fixture traps banked: (1) item 5 Colony Base is NOT in the seed-2024 base
  list (REQUIRES) — fixed-item CHECKs must use base-list members; (2) the
  scenario home CB lands on cell 0 of the seed-2024 fixture, so the
  ACTIVE/armed pair must be DERIVED via gridRowCol/gridCellFor (an adjacent
  pair found from the grid law), not hard-coded.
- MUTATION 3/3 CAUGHT (scripts/tPF6_mutate.sh): M1 drop filter block -> 24
  fails; M2 polarity inversion -> 32; M3 one call site unwired -> 1 (wiring
  pin); after_restore 0. INCIDENT re-witnessed the banked trap: restore()
  must COPY BACK from the snapshot then md5-verify — verify-only left M1 on
  disk when M2's patch assert fired mid-campaign (the old_string had been
  mutated). Script fixed; skill rule updated.
## P6 — WITNESS VERDICT (scripts/tPF6_witness.sh, seed 5, fixed build)
- ITEM 11 CHAIN PASS end-to-end: click slot0 (48,154) -> 'ui planet tile 23
  selected (Orbital Square ids=54,51)' -> Build band (200,352) -> 'ui planet
  popup build cell 23' -> 'ui planlist opts n=3 [22,23,26,]' (orbital rows
  ONLY — the fix; pre-fix was n=8 [0,1,2,20,21,22,23,26]) -> row pick ->
  'ui planet project Amoroso I Shipyard (ordered armed cell 23)'.
- D1 CONTROL PASS: PLBUILD open (unarmed) -> n=8 full list — filter does not
  leak.
- D2 surface-armed leg: list n=0 on cell 11 — EXPLAINED, not vacuous: the
  popup's 54 there came from the checker-EXEMPT item 35 Automation (0x385ff;
  popupButtonIds skips 5, scan reaches 35), which the REQUIRES gate drops
  from PLANLIST. Faithful to the vendor's two-gate split (54-loop placement-
  only vs REQUIRES-gated list) => SEAM TPF6-A named: vendor may likewise show
  a Build whose list holds no buildable row; unrecovered whether the vendor's
  list is per-cell-filtered at all (TPF6-B).
- NOT claimed: vendor pixel-identity of the orbital popup (no 1:1 vendor
  orbital capture exists).
## P7 — ITEM 12: HONEST NEGATIVE, NO FIX SHIPPED
Measured (P3): hover adds NO measurable CPU class on this host (idle 37-42%,
flood 41.2%); the cost is the planet screen's constant ~40%-core 60fps full
repaint, which the user's slower hardware reads as 100%. The vendor repaints
on hover too (+0xac law), so there is no vendor hover economy to port. A port
repaint-throttle (skip RenderPresent when nothing changed) is a PORT decision
outside vendor law — named-open TPF6-CPU-A, NOT shipped this iteration.
Item 12 stays OPEN as a user symptom; the measurement attributes it, which is
all strict-close allows without inventing a fix.
