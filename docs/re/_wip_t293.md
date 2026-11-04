# t293 WIP — scripted move-order capture (sugar-cube scale, OQ-019)

Session start 2026-11-03 ~21:55 EST. Fresh session; resumed from STATE.md alone.

## Pre-flight state (verified this session)
- git clean at session start, branch main, HEAD = docs slim commit.
- Production :9 pid 660167 alive; live-timeline.jsonl mtime 21:54:05 (same
  minute as `date`) -> ring writer healthy, turn PINNED 1150, V=23/50, sel 0.
  Rows are idle-daemon echoes (56.sav/58.sav identical ship tables), NOT a new
  sitting -> r1_t85g_sitting.py NOT required (no new sitting since last iter).
  OOM LAW respected: timeline read via tail only (file is 7.9 GB).
- Ledger at start: 16 closed / 3 open (OQ-005, OQ-016, OQ-019).
- Inherited pointer STALE confirmed in docs: cost hack CLOSED t16 (§9), so the
  +0x46 census is NOT re-run.

## The question this task discriminates
ships.md §17 T1/T2 [verified static + measured constants]: FUN_00049f54 walks
walk = min(d/160, MOVES[+0x94]) sugar units, steps = max(1,round(walk)),
per-step displacement = normalize(delta)*(walk/steps)*32.0*5.0, commit
[+0x9e] := new pos, [+0x88] -= steps. 1 sugar cube == 160 world units.
The open residue is the LIVE witness: does one End-Turn pass move a ship by
the RAW walked float distance (continuous, quantized only to the 32-grid at
arrival), or does it show a hop/waypoint abstraction? One witnessed flight with
per-autosave coordinates settles it. Secondary: does the issued order survive
into an in-transit state (OQ-016 setup-draw family).

## Route (per STATE.md t293 + BLOCKED.md §Scripted-move capture)
SCRATCH session only: own ring dir, Xvfb, Oct-29 t1086 RESUME.GAM, TL=172800,
kill-by-recorded-PID, production :9 untouched. Click own ship (owner 0, state
5, slot 16/22/26/27 at home star per ring lineage), click lane-adjacent visible
destination, End Turn x2. Drive laws: assert_on_map before any click; 2 no-
advance presses = STOP-AND-LOOK; NEVER Escape.
BUDGET: 3 scratch launches MAX that reach the map-and-click phase
(BREAK-lottery losses don't count, t292 accounting law).

## Choreography findings (pre-launch, all from on-disk vendor evidence)
- help.txt:1146 (help batmode, System Display) VERBATIM: "You can move a
  selected ship by clicking on a desired destination. If necessary, you can
  set the destination altitude with another click. @@You can view a selected
  planet by clicking it again." => IN-SYSTEM move = select ship + click dest
  in the SYSTEM VIEW (orbital grid), NOT the galaxy map.
- help.txt:185 (help coswnd, Galactic Display): clicking a discovered star
  ENTERS THE SYSTEM. No galaxy-map move-order sentence exists in help.txt.
- help.txt:1648-1659 (fleetwin): FLEET row LEFT-click jumps to the ship's
  location; RIGHT-CLICK shows contents. selfplay.md §4 [t244 measured]:
  RIGHT-CLICK (Button3) on the orbital grid = ORDER MODE (green target marker
  appears); red-slash cancel icon sits in the console cluster.
- STATE semantics CLOSED already (aicode.md, r1_t94/t107 census): ship
  [rec+0x58] kind 0=none/cleared, 2=move order (reg-form writer 0x3ca60),
  4=in-system/after-arrival (holds owning STAR record at +0x59), 5=travel-to-
  star (issuer 0x220a8 -> 0x21f58 consumed into 4 on arrival processing).
  Travel-order store sites 0x22243/0x2228f.
- MEASUREMENT TARGET (ships.md §17 T1/T2 static law): walk body
  FUN_00049f54: walk=min(d/160, MOVES[+0x94]), steps=max(1,round(walk)),
  fuel gate [+0x88]; per-step disp = normalize*(walk/steps)*32*5; commit
  [+0x9e]+=, [+0x88]-=steps, [+0x94]:=round(remaining); quantizer g=32 via
  FUN_000533e0. Discriminator at ring granularity: st4 in-system move
  resolves within ONE turn boundary (t265 dwell law) -> net endpoint ==
  min(d,MOVES)*160 AND on the 32-grid => walk law CONFIRMED live; endpoint
  != that (e.g. raw d = instant hop, or off-grid raw float) => hop model.
  Read MOVES/FUEL from the ring's OWN ship_raw window (u16[+0x94], u16[+0x88],
  stride 0x162) — no debugger needed.
- COSMOSWnd (windows.txt TYPE 2, rect 7,7-465,472) is the galaxy map; map
  dot-finder scripts/r1_mapdots.py exists (bright-dot clusters, game coords
  x 40-470 y 40-460 on a 640x480 CROP).
- t292 PROVED the scratch skeleton works WITHOUT the debugger for input:
  xsend 'DOSBox-X' click 318 333 (DISPLAY=:96) entered the campaign from the
  title of a fresh private Xvfb (motion-warp click updates hover; the stale-
  hover law bit only where a VNC user had hovered). Session ran ~4 min:
  boot->title ~60 s, settle 60 s, End-Turn AI pass ~3.5 min.
- ENV FACTS (measured this session): production pid 660167 alive TL=172800
  (etime 17:17, expires ~Nov 5 ~14:40); Xvfb :9 only (scratch needs its own,
  e.g. :96 free); x11vnc :5910 serves :9 ONLY; gate 3n2 audits only scripts/
  *.sh with a MOUNT line (a new scripts/*.py must still follow the invariants:
  SCRATCH under work/, -time-limit, kill-by-recorded-PID, never game/).
- Manual PDF is 23 scanned pages, no text layer, no pdftotext/tesseract on
  box — help.txt is the authoritative in-game text (already banked above).

## LAUNCH AUTOPSY (t293, launches against the 3-run budget)
L1 (231538) NOT budget-counted (t292 accounting: never reached map-and-click —
my own assert_on_map inversion aborted at the title; FIXED: enter_campaign now
REQUIRES the title screen, the (318,333) click is the deliberate t292-proven
exception).
L2 (231623) budget-counted #1. Result: NO order issued; script's POSITIVE exit
was SPURIOUS and is retracted below. What it proved/measured:
1. FLEET sidebar (553,184) opened (diff 122420, t253 rails 188); row-1
   left-click (200,93) JUMPED to the orbital/system view (diff 112652). The
   route title->campaign->FLEET->orbital is RELIABLE and fast (~75 s).
2. click3 (xsend button3 verified compiled+sent) at 4 grid points: each AFTER
   shot differs from the orbital baseline by EXACTLY 1359 px, pairwise 120 px
   — a ~120 px artifact TRACKING the cursor position (cursor sprite), NOT the
   green order-mode marker. NO green-pixel increase (34->34 constant), NO ring
   order-byte change. READING [inferred]: right-click order mode did NOT arm —
   most likely because batmode help requires the ship SELECTED first ("move a
   selected ship..."), and nothing was selected. The t244 order-mode witness
   was made on the PRODUCTION session where a ship may already have been
   selected.
3. ORDER WITNESS INSTRUMENT WORKS: owner-0 kind census across all 20 ring
   samples = kinds {3,4,5} only, NEVER 2 (move order). kind2 appearing is a
   clean, unambiguous issued-order signal.
4. SPURIOUS POSITIVE: my verdict fired on t1086->t1087 movers slot 5 dx=28.0,
   7 dx=14.0, 16/22/26/27 dx=4.6667, 24 dx=14.0 — ALL exactly the t189/t265
   LANE-MARCH steps (step0 or step0/3), kind stayed 5, MOVES/FUEL unchanged —
   pre-existing AI-side... no: owner-0 lane traffic that was ALREADY ordered
   before the session. Verdict law fix: a flight counts ONLY if (a) an order
   was WITNESSED (kind2 or kind 5->4 flip on a watch slot) or (b) the moved
   ship's kind CHANGED or (moves/fuel changed); constant-kind constant-budget
   dx == lane step is background traffic, NEVER a witness.
   SECONDARY BONUS (honest, keep as observation): t1087 lane dx values
   {28,14,4.6667} re-confirmed the t189 lane-step law live for owner-0 ships
   on a THIRD independent campaign point — but this closes nothing new.
5. TURN BEHAVIOUR: press 1 on the (assumed) map advanced 1086->1087 in 14 s.
   Presses 2 and 3 at (511,67) did NOT advance in 90 s each. The escape ladder
   had landed at esc2 with diff_vs_map=320 (near-baseline) — but rails=170
   nonzero there, so "map" state was not cleanly re-established; OR a
   serialized turn-end popup (t245 law) swallowed presses 2-3 and my
   white-band popup detector (band y 330-470, x 170-486) missed it. Screenshots
   24-30 banked; NEXT LAUNCH must drain popups after EVERY press and use a
   wider detector.
6. Autosave cadence 10 s confirmed again on the scratch ring (20 slots,
   41..60 rotation); ring base vote worked every slot (B=0x1bf4d8 class).

## L3 AUTOPSY (233751, budget-counted #2 of 3) — NEGATIVE, honest
Route rode perfectly AGAIN: title orange 0.679 -> (318,333) -> ring t=1086 30
ships -> FLEET (553,184) diff 122420 rails 188 -> row-1 (200,93) jump diff
112652 -> orbital view in 75 s. Deterministic. Reproducible.
FAILURES (all mine, all fixable):
1. ORBIT DOT CLICKS NAVIGATED, NEVER SELECTED: bright-dot candidates
   [(442,346),(442,312),(442,278),(442,244),(374,312),(374,278)] — 34px column
   grid; each left-click diff_vs_sys ~65k (view changed big) then Escape
   returned to orbital (diff_vs_sys back down). The detector found bodies/
   planets or opened detail windows, not ship selection. Right-click order
   mode NEVER armed (green constant 34 baseline; click3 diffs 1368 = cursor
   sprite only; ring order bytes never moved).
2. POPUP SWALLOWED PRESSES 2-3 (again, t245 serialize law): EVENTWIN
   "Construction of Industrial Megafacility is complete on Cornucob I" —
   vision-verified bbox [83,118,417,362], buttons Go to Planet (86-250) / OK
   (250-414) at y 322-358. windows.txt VERBATIM: EVENTWIN rect 60,100-395,355;
   EVENTBUTTON0 70,320-180,345; EVENTBUTTON1 275,320-385,345 (both
   SENDMESSAGE 50). My light-bg detector FIRED correctly (white px 804->2689)
   but OK clicks at (330,332) did NOTHING (pre/post diff 204 then 0 — popup
   pixel-identical across 3 clicks). selfplay.md ALREADY LAWS THIS: "in-game
   OK-button clicking was unreliable for synthetic Button1 — Escape is the
   robust path." FIX: close EVENTWIN with key Escape (verify STATE: orange
   band must stay ~0 and popup-area white drop back to baseline, else t285
   title risk => abort).
3. LUCKY WITNESS OF THE LIFECYCLE (observation, closes nothing): slot 8
   t1086->t1087 kind 5->4 with xyz [196,0,1120]->[-480,-2080,-960] — a travel
   order CONSUMED INTO in-system on arrival, live, matching the static
   0x220a8->0x21f58 law. The verdict correctly refused it (I didn't order it).
4. Press 1 from a clean-ish map advanced 1086->1087 in 7 s. Presses 2-3
   blocked 90 s each by the popup (rc=1 NEGATIVE exit, witnesses=0).
NEXT-ITERATION CHOREOGRAPHY (t294, 1 launch budget left, fixes ready):
a) drain popups with ESCAPE not OK clicks; b) selection: click ship dot ->
if a detail window opens, Escape ONCE (selection likely persists per
selfplay.md list-handle law) -> THEN click3 destination; c) keep ring kind2
witness (kinds observed {3,4,5}, never 2 — clean signal).
