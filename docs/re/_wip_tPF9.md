# tPF-9 WIP — RESEARCH-SCREEN STRAY TEXTS (D28 item 13)

Task: D28 item 13 — "no 'click set project' text in the upper right frame,
and no 'Esc return to galaxy' text in the lower left". Port strings:
ui.cpp:2784 ("click: set project", upper-right) and ui.cpp:3495
("Esc: return to galaxy", bottom-left). Escape ROUTING behaviour stays
(ui.cpp:1829 comment cites t252 behaviour); item 13 is about the LABEL.

SITTING CHECK ran FIRST: scripts/r1_t85g_sitting.py exit 0, 45,227 trusted
rows, output byte-identical to tPF8_pre_sitting.out (newest t=1335) — no new
user sitting, assignment STOOD.

## P1 — CITATION LEG (vendor frame + paint chain)
(in progress)

## P1 CITATION LEG — CLOSED, ALL THREE LEGS AGREE (DELETE is the law)

LOCATING THE PAINT SITES (brace-depth verified, not eyeballed):
- ui.cpp:2784 "click: set project" — depth 6, inside the kScreenPlanet
  branch, PROJECT-slot panel block (the sibling states in the SAME draw
  call are "picked: <name> ..." and "list open: pick one").
- ui.cpp:3493-3495 "Esc: return to galaxy" — depth 4 = OUTSIDE the
  per-screen if/else-if chain (kScreenSystemView branch header is depth 5,
  ui.cpp:3381) => painted on EVERY screen with a non-empty interior,
  research included. The user's item-13 complaint (filed against the
  planet-screen composite) catches both.

LEG 1 — VENDOR FRAME (433 composite = the item's own evidence):
scratchpad/planet-screen-iter-433-v-original.png (1642x617; LEFT=PORT,
RIGHT=VENDOR). Full-frame vision: port half shows 'click: set project'
under the 'No Project' panel (~595..690,114 full-frame) and 'Esc: return
to galaxy' at its bottom-left (~5..95,590). Vendor half shows 'No Project'
(panel ART text) and NOTHING at upper-right below it, NOTHING at
lower-left. Full-res zoom crops (1150,40)-(1642,150) and
(821,480)-(1320,617) of the vendor half: zero text fragments [vision,
2 crops]. t252 research frame (work/screens/t252/research_open_game.png)
corners: upper-right and lower-left EMPTY [vision].

LEG 2 — PAINT CHAIN: draw-loop window 0x48165..0x485b5 has exactly 13
calls (work/t91_code_disasm.txt): 0x5cf77, 0x46d3c x2, 0x76e08 x2,
0x5bf71, 0x1fc34 x3, 0x5d5a1, 0x5caac, 0x5cf96 — ALL shape fetch/blit/line
primitives per research.md S-laws (0x1fc34 fetch, 0x5caac/0x5cf96 row-RLE
blit, 0x5d5a1 line blit). ZERO text-primitive callsites inside the loop.

LEG 3 — STRING PRESENCE IN THE SHIP: 'click: set project' / 'set project'
/ 'return to galaxy' are ABSENT from game/ascend.exe AND all three .cob
data files (grep -c -i 'set project' game/* -> only setsound.exe 7 +
ascend00.cob 10 binary byte-hits, and strings shows NO 'set project'
phrase in ascend00.cob; 'return to' hits are tutorial PROSE only
('We'll return to the Planetary Display...')). 'Esc: return to galaxy'
exists NOWHERE in the vendor ship [verified game/].

HISTORY: 'click: set project' entered at t406 (git log -S, commit
d521e38) as a PORT AFFORDANCE ("the click affordance stays at the panel
bottom (port affordance)") — never cited to vendor art/paint. 'Esc:
return to galaxy' entered at t388/t409 era as chrome hint. Both are
inventions; D30 POPUP/DERIVATION LAW says an uncited visible property
must go or be named-open — the user has now RULED it must go (D28 item
13). DELETE is the law; the Escape ROUTING behaviour (ui.cpp:1829 area,
cited to t252) stays.

## P2 SHIP (ui.cpp, both sites)
- SITE 1 (idle hint): the three-state txt.draw collapsed to a GUARDED
  transient draw: `if (projectOpen || planetPick >= 0)` paints "list open:
  pick one" / "picked: ..." — the IDLE "click: set project" arm is GONE.
  Rationale banked in-code: user ruling + strings-negative vendor ship +
  zero text callsites in the draw loop; transient feedback kept because
  D28 items 19/20 separately demand visible set-project state.
- SITE 2 (chrome label): the `if (interior.x1 > interior.x0)` block
  painting "Esc: return to galaxy" on EVERY screen is DELETED, replaced by
  a citation comment. Escape ROUTING (ui.cpp:675 KEYDOWN handler) untouched.
- grep confirms no live draw of either string remains (only the comment
  naming the deletion).

## P3 PINS + MUTATION + WITNESS
- PINS tests/test_strays_tpf9.cpp (CMakeLists entry ADDED — tPF-4 trap):
  stray_hints_deleted_tpf9 (statement-window scan: no txt.draw( statement
  takes either label as argument — comments quoting the deletion can't
  false-fail it); transient_project_feedback_kept_tpf9 (anti-vacuity: both
  transient strings + the guard exist); escape_routing_behaviour_kept_tpf9
  (SDL_KEYDOWN + SDLK_ESCAPE + the t252 citation comment survive).
  SUITE 583 -> 586, 0 skipped, 0 failed.
- MUTATION scripts/tPF9_mutate.sh: 4/4 CAUGHT, md5-verified restore,
  final tree green.
  M1 idle hint re-introduced -> 1 FAIL; M2 guard kills feedback too -> 1
  FAIL; M3 Escape routing broken (ESCAPE->TAB) -> 1 FAIL; M4 Esc label
  re-painted -> 1 FAIL.
- WITNESS scripts/tPF9_witness.sh + tPF9_witness_census.py VERDICT PASS:
  planet-idle UR ink=0 BL ink=0; list-open CONTROL UR ink=172 (census
  sees text where text legitimately paints); research BL ink=0. Vision
  overlay on research.png: three root disks, zero corner text (consistent
  with tPF-8 rest law).
  CENSUS TRAP BANKED: the RESWIN frame border is neutral gray (120,120,120)
  at x=7, INSIDE the kDim/kText +-40 tolerance — a BL box starting at the
  interior x0 scoops 24 border px = false FAIL. Box starts x=16 (the label
  painted at x0+8=15 and spans right; x16 still covers every glyph column).
