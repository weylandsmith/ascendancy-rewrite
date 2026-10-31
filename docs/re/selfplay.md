# selfplay.md — the agent drives the ORIGINAL game headless (t244, 2026-10-31)

Capability, method, and the findings a 20-minute self-session produced. Input:
tools/xsend (click + KEYSYM injection, both VERIFIED working on dosbox-x).
Eyes: `DISPLAY=:9 import -window root` screenshots + vision_analyze (the
routing change the user made today; read_file refuses PNGs, so vision_analyze
is the viewing path). Session stack: scripts/r1_playcap_vnc.sh start (title
menu -> "Return to Current Game" click at window-rel 318,333).

## 1. SAFETY LAW (measured, this session)
RESUME.GAM (work/r1/game, the game's own title-menu resume file) is written
ONLY at in-game Save/quit points — NOT continuously. Measured: the ring holds
t=1335 (the user's final unsaved turns) while RESUME.GAM sat at t=1086 for 2
days; md5 5b382afb... stable across my entire session because I never pressed
in-game Save. Consequences: (a) the user's "I forgot to save" testimony is
CORROBORATED by the file itself; (b) an agent session can advance turns
FREELY — the watcher banks live RAM every 10 s regardless — and killing
dosbox without Save leaves the user's resume point byte-identical; (c) the
game a resume loads can be FAR behind the ring (1086 vs 1335 here): always
read the in-game turn counter from a screenshot before trusting stream tails.
Backup taken anyway: work/r1/game/RESUME.GAM.user-oct29 (md5-verified).

## 2. THE 'c' OVERLAY IS THE GAME'S OWN RELATION DUMP — and it corroborates
the state ENUM a third time (OQ-023 law; OQ-021 readout law)
Verbatim at t=1086 (galaxy screen, nougat armed, my own keypress):
    O Biorythm (Neutral)
    R0 Unknown 0
    R1 Peace 600
    R2 Peace 318
    R3 War 318
    STARS CONTROLLED 0
Cross-checks against watcher-banked RAM at the same turn (41.sav, t=1086:
DAT_482fb=0/50; player row att0/states0 law from sitting dumps):
- R-index = race index (names [Chamachies, Orfa, Ungooma, Minions]):
  R1 Peace 600 == Orfa att 600 (sitting value at t=1250, drift-plausible at
  1086); R3 War 318 == Minions att 318 EXACT + states0[3]=2.
- STATE WORDS match the enum law independently: cell 2 -> "War", cell 1 ->
  "Peace", cell 0 -> "Unknown" (never-contacted, Chamachies at t=1086).
  Third independent corroboration of 0=none/1=PEACE/2=WAR after t85b
  (declaration) and t188b (alliance flip to 3).
- STARS CONTROLLED 0 == DAT_482fb==0 banked at t=1086 EXACT. Combined with
  the player's 14->21 testimony == score_stars 14..21 trajectory t1255..1301,
  the overlay is a DIRECT READOUT of DAT_482fb, not a recomputed formula.
  OQ-021 residue sharpens further: pin what WRITES DAT_482fb (oscillates
  while systems_any=36/full=34 dead flat), the display side is now settled.
- 'c' is TOGGLE-LIKE: second press on the PLANET screen did nothing (planet
  screen is modal; overlay is galaxy-screen-only — consistent with t191's
  cosmos msg handler 0x26b34).
- Title screen verbatim (new keymap datum): buttons carry Alt-L Load /
  Alt-S Save / Alt-X Exit hotkey labels (title-menu hotkeys, distinct from
  galaxy-screen 'l' lane reveal).

## 3. PLANET SCREEN FIVE-PANEL LAW VERIFIED LIVE (windows.txt law + player
testimony, now agent-observed): top strip L->R = crystal lattice (PLRES/
research), factory (PLIND), green plant (PLPRO), rows of person figures
(PLPOP — all RED, all SIDEWAYS = all busy, zero yellow idle on a maxed
planet), construction panel (PLBUILD: "Automation / 2 days until completion"
+ item art, confirming planitem.shp = current-project item art hypothesis).
Planet LIST view (first click on sidebar Planets) is a SEPARATE mode: header
"Chamachies (60 Planets Occupied, 26 Systems Controlled)" + per-planet rows
(star art, system name, planet art, type, construction text, 3 mini-gauges).
Header "26 Systems Controlled" vs ring systems_any=36 (t=1335): RESOLVED by
turn alignment — the resume game is at t=1086, and banked score fields at
t=1086 give planets=26 / systems_any=26 (r1_stream over the ring). Header
"26 Systems Controlled" == systems_any@1086 EXACT (label says Systems,
matches ANY, not full). NEW DISCREPANCY BANKED: header "60 Planets Occupied"
vs banked planets=26 same turn — 60 may be the map's total colonizable
planets, or a different ownership definition; hunt = find the header-format
sprintf in the binary (candidate: same cluster as t212's TRUNC(100*score/T)).

## 4. PLANET-SCREEN INTERACTION LAWS (agent-observed, t244)
- NAVIGATION STACK: galaxy -> SYSTEM VIEW (orbital grid: blue wireframe plane,
  bodies on yellow stalks, right panel = planet name + art, orbital structure
  + art, icon console; planet-icons row selects planet) -> PLANET DETAIL
  (five-panel strip) -> popups. Planet LIST is a separate sidebar mode, not
  in this stack.
- PLANET DETAIL IS MODAL: sidebar sidebar clicks (Planets at 553,145 etc.)
  are SWALLOWED while it is open.
- POPUPS CLOSE WITH ESCAPE (research popup + building dialog both closed by
  key Escape; in-game OK-button clicking was unreliable for synthetic
  Button1 — vision-estimated coords kept missing; Escape is the robust path).
- GAUGE CLICK = ECONOMY READOUT POPUP (VERBATIM): clicking the PLRES gauge
  popped "Vega IV Research: 52 per day / Megagraph Theory will be discovered
  in 37 days. / OK". => the original DISPLAYS current per-day research rate
  and ETA for the in-flight tech: a direct verification target for the
  rewrite's research model (rate + ETA two numbers per planet per tech).
  Same pattern presumed for PLIND/PLPRO (untested).
- RIGHT-CLICK (Button3) on the orbital grid = ORDER MODE: green target
  marker appears on the grid. A red-slash cancel icon sits in the console
  cluster. CAUTION: red pixel-scanning finds the MISSILE-BASE art's red
  parts too — a misaimed console click opened "Are you sure you want to
  abandon Vega II?" (answered NO; planet intact, md5 still 5b382afb). Blast
  radius lesson: in the system/planet views, click only icon centers
  confirmed by zoomed crop, never red-pixel guesses.
- Order mode cleared by dialog-No; no turn advanced during all popup work.

## 5. SELF-PLAY FEASIBILITY: demonstrated at input+observation level.
Open questions for any future supervised run: click precision on small
widgets (50px buttons, worked first try on Planets + NEXTTURN band),
scrollbar/list navigation untested, combat UI never entered yet.
Campaign safety record this session: RESUME.GAM md5 unchanged (5b382afb)
throughout; zero turns advanced (NEXTTURN clicks landed on the modal planet
screen); zero in-game Saves; user save backed up to RESUME.GAM.user-oct29.

## 6. T245 TURN-DRIVE LAWS (scripts/r1_t245_turndrive.py)
- windows.txt rects are EXACT and in game coords == window coords: NEXTTURN
  474,52-548,82 (center 511,67 window-rel FIRES turn advance, ring-verified);
  NEXTTURNCONT 557,52-632,82 (double-arrow = fast-forward, untested); the
  clock-arrow buttons BELOW the counter are turn-history scrubbers.
- Turn-end popups SERIALIZE; while ANY popup is open, NEXTTURN and EVERY
  other input is swallowed (6 presses, zero ring movement).
- Construction popups: Escape does NOT close them; OK click does. MEASURED
  hit-rect law: drawn button spans y 429-472, working clicks land at y~440-
  443 (label-row TOP minus ~3); label baseline (y 455+) MISSES. Detector
  aims label-top-3.
- Popup detection: white-text pixel count in the popup band (box is dark
  with cyan trim — grey-run detectors are blind).
- After a firing press, AI processing takes ~10-20 s before the ring banks
  the new turn; drain popups again after.
- journal tail-scan ONLY (multi-GB): tail -c 400000.

## 7. SOFTLOCK INCIDENT (13:14Z, evidence work/r1/softlock_evidence.png)
At t=1089 with a construction popup on screen the game became input-dead
(sidebar, keys, both popup buttons — verified by pixel-diff after each) with
RAM frozen (25 s apart, journal changed field: 'wall' only) while dosbox-x
pinned 90-100% CPU (caveat: idle Ascendancy also runs hot, so CPU alone is
NOT hang evidence). Recovery: kill dosbox, relaunch, Return to Current Game
-> back at RESUME.GAM turn 1086; the unsaved turns 1087-1089 lost from the
GAME but banked FOREVER in the ring. Two candidate causes, unresolved
[unverified]: (a) engine popup-state bug; (b) the user's real mouse hovering
the window (SDL grabs real motion; synthetic events may be ignored while
grabbed). The user DID run their mouse across the window mid-session, though
that message arrived BEFORE the input-dead phase began. LESSON: for long
unattended drives, warn the user not to touch the VNC window, and treat
"popup open + input-dead + RAM-frozen" as the softlock signature -> restart.
