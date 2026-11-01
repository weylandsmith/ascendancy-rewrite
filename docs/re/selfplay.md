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
t=1086 give systems_any=26. Header == systems_any@1086 EXACT.

### t246 RESOLUTION of the "60 Planets Occupied vs 26" question (was a unit
confusion, NOT a discrepancy):
- Static: header = getter(151) "%s (%d Planet%s Occupied, %d System%s
  Controlled)" (quoted-record #151 of static.txt; call-site region
  0x51685..0x517c0, mov eax,0x97 at 0x51798; sibling getter(152) ship-count
  header at 0x33905). Star table: 0x60-stride at DAT img 0x13bc5, bound WORD
  ds:0x16145, owner BYTE at +0x14 IS A BITMASK (loop tests ==1<<race at
  0x516c5; sole-owner test).
- Measured at t=1092 (scripts/r1_t246_header_law.py, freshest slot):
  owner-byte hist {1:25, 0:8, 4:7, 2:5, 6:2, ...}; sole-owner(1<<race)=25;
  player-bit-set=26; maintained u16 at data 0x131b4 = 60 (ONLY occurrence of
  60 in the race block; race-0 block, likely an incrementally-maintained
  PLANET counter — [unverified] maintenance writer).
- The triple that closes it: loop-count 25 == banked systems_full EXACT;
  bit-set 26 == banked systems_any == header "26 Systems Controlled";
  u16@0x131b4 60 == header "60 Planets Occupied". The header counts
  COLONIZED PLANETS (60, ~2.3/system across the scrollable list) and
  SYSTEMS-any (26). The watcher field named planets_mine actually counts
  player-owned STARS (its law is sum(stars whose owner-set has player)) —
  the t244 note conflated the units.
- Residue [unverified]: which producer feeds which %d (linear-disasm
  argument pairing is desync-limited, t91); the writer of u16@0x131b4.

### t247 CORRECTION + t1254 re-measure (softlock #2 recovered; ring banked
to work/r1/bank-t1254/ BEFORE restart; t1092 RAM frames rotated away):
- SYSTEMS side VERIFIED AT SECOND TIMESTAMP: t=1254 owner-byte hist
  {1:35, 2:5, 4:5, 6:2, 132:1, 129:1, 130:1}; sole-owner=35; player-bit-set
  =36 == header "36 Systems Controlled" == banked systems_any EXACT.
- u16@0x131b4 read 60 at BOTH t1092 and t1254 while the header planets went
  60->102: it is NOT the planets counter (t246 attribution WRONG, corrected
  here; commit 867d3e2 message carries the error).
- NEW LEAD (strong): star-record BYTE +0x5a = per-star colonised-planet
  count (record diff sole-owner-5-planet star idx0 vs co-owned-4-planet
  star idx25 shows +0x5a 5 vs 4, matching visible planet counts; values
  1..5 across the 36 bit-set stars). SUM(+0x5a over bit-set stars) = 104
  vs header 102 — delta exactly 2, and idx25 is the ONE player-co-owned
  star (owner 129 = bits 0|7, 4 planets): hypothesis [unverified] the
  header counts player-OWNED planets and star 25 has 2 of its 4 owned by
  race 7 (per-planet ownership stored elsewhere — candidate region
  +0x56..0x58 zeroed on the co-owned star). Hunt next: locate per-planet
  owner table; then sum-owner-filtered should hit 102 EXACT.
- Softlock #2 law refinement: signature recurred WITHOUT any popup (user's
  t1254 planet-list session) -> engine-state bug >> mouse-grab hypothesis.
  ALWAYS bank ring slots (cp save/*.sav bank-dir) BEFORE restarting: the
  ring rotates and unsaved turns are otherwise lost forever.
  dosbox-x SIGTERM -> pops its own "Quit DOSBox-X warning" xmessage +
  in-game "Are you sure to quit" dialog with (Yes) DEFAULT: never press
  Enter near it; SIGKILL is the clean exit for a softlocked session.

### t248 PER-PLANET OWNER TABLE FOUND + t247's +0x5a LEAD REFUTED
Tools: scripts/r1_t248_planet_owner.py (census), r1_t248_verify.py /
r1_t248_final.py (structural proof), r1_t248_pred.py + r1_t248_pred2.py +
r1_t248_pop.py (header-filter sweeps, all negative), r1_t248_counter.py
(maintained-counter intersection), r1_t248_orphan.py (table extent).
- THE LAW: the 123-byte (0x7b) stride PLANET TABLE record holds the owner at
  NAME+0x33 (byte) == race index; 0xFF == unowned. Table anchored by name
  run (r1-savestate.md name law; name field 19 B): bank-t1254/48.sav rec0
  "Vega I" member idx 0x26d103 = phys 0x26d07b (pointer law H=0x88, same base
  in the live-ring t1086 slots). NAME+0x65 == planet index within system.
- PROOF 1 (structural, decisive): at BOTH t1086 (live ring 46.sav) and t1254
  (bank 48), every one of the 50 star records keys by name to its planets,
  and star-record owner byte +0x14 satisfies (star & 0x7f) == OR(1<<planet
  owner) with ZERO violations — 104 colonised planets @t1086, 124 @t1254. A
  field that reproduces the star bitmask bit-for-bit across 50 systems x 2
  timestamps is the owner (scripts/r1_t248_final.py).
- PROOF 2 (the 102): count(NAMED && NAME+0x33 == race0) = 102 at t1254 ==
  header "102 Planets Occupied" EXACT (owner hist {0:102,1:11,2:11,255:21};
  the 6 blank-named slots k=145..150 hold a stale 0 — law is NAMED-filtered).
  At t1086 the same count = 80 while the t1092 screenshot (work/screens/t2/
  planets_header_t1092.png, re-read this session) says 60: the header's
  planets number is a MAINTAINED counter, not the table count (PROOF 3).
- PROOF 3 (Ghidra, this session): FUN_00051684 (planet-list header producer,
  region 0x51685..0x517c0) loops the 0x60-stride star table (0x5168d MOV
  EAX,0x13bc5; bound WORD [0x16145] @0x51692; sole-owner CMP ESI,EDI,
  EDI=1<<[0x7458e] @0x516c5; home-star exclusion CMP EAX,[ECX*0x1ee+0x12e1d]
  @0x516d7) — that loop-count feeds the SYSTEMS number (35 sole + home = 36
  @t1254 EXACT). The PLANETS number is a stored u16 read through
  *(u16*)(*(int*)(obj+0xab) + 0x8c7) — a HEAP-WINDOW slot, not a data-seg
  counter. Format fetch MOV EAX,0x97 (static.txt record 151) at 0x51798.
- PROOF 4 (static init signature): game/resume.gam (vendor 2008, 151 recs,
  name@0x9b1a, stride 123) at NAME+0x33: hist {0:1,1:1,2:1,3:1,4:1,5:1,6:1,
  255:144} — exactly seven records hold 0..6 (each race's HOME planet), all
  else 0xFF. Owner-field initialisation.
- REFUTED (t247 lead): star byte +0x5a is NOT the colonised-planet count — it
  is the TOTAL planet SLOTS in the system (sum(+0x5a) over all 50 stars ==
  145 == named record count @t1254; per-system len(planets)==+0x5a for every
  keyed system at both timestamps; the colonised reading matches 3/5). So the
  "104 vs 102" delta was never a co-ownership split: the only non-player
  planet inside a player-bit-set star @t1254 is Fomalhaut II (0xFF unowned,
  star byte 0x1); co-owned stars (Sarsaparilla 132, Arcturus 6, Oslo 129,
  Philadelphia 130, Amoroso 6) each have every planet owned by a party whose
  bit is in the star byte (player owns 4/4 Oslo).
- HONEST NEGATIVE (header filter @t1086): no record predicate explains
  60 @t1086 AND 102 @t1254. Sweeps over all 123 offsets x 256 values, bit-k,
  u16/u32 !=0/==0xFF, and owner-AND forms: only 5 single-bit hits at 60
  (@+5 bit4 -> 60@1254 but that is a coincidence class, @+48 bit4 -> 65,
  @+51 bit1 -> 32, @+89 bit3 -> 80, @+101 bit0 -> 57) — none hits 102.
  CAVEAT on r1_t248_counter.py: its u16-intersection (60 in the t1086 ring
  slot AND 102 in t1254 -> 0 offsets) compared a turn-1086 slot against a
  turn-1254 slot, but the "60" header belongs to t1092 (t246's slot rotated
  away) — the zero is NOT a refutation of a plain-u16 counter; redo with a
  same-turn pair. The "occupied == populated" hypothesis (owner flag set but
  pop==0 at t1086) is the best [unverified] default and is testable once the
  population-slot library (t254) lands.

### t249 HEADER-PLANETS COUNTER FOUND — SCREEN-OPEN SNAPSHOT LAW (MEASURED)
Tools: scripts/r1_t249_listwalk.py / _inspect.py / _raw.py / _content.py /
_sigscan.py / _validate.py / _items.py / _entry131b4.py / _freeze.py; full
working log docs/re/_wip_t249.md (S1..S11). Evidence bank:
work/r1/bank-t249-live-open/{59,60}.sav + work/screens/t3/
planets_header_t1086_after_open.png.
- THE LAW (static + 3 measured timestamps): the planet-list header's PLANETS
  number is u16[list+0x8c7], the ITEM COUNT of a generic scrollable-list
  object; the list is RESET (count zeroed, +0x8c9 stamped 0x8d) and REFILLED
  with exactly the planets whose NAME+0x33 == player race on EVERY open of
  the Planets screen (FUN_00051834 case 1: alloc iff widget+0xab==0; bound
  u16@dsx0x3a093; filter DAT_0002b0ae = rec0+0x33). Between opens the number
  is FROZEN — the only +0x8c7 writers program-wide are the list add (0x32eb6
  in FUN_00032d1c) and reset (0x325b5, 0x33015) routines; FUN_00051834 has
  no turn-driven case.
- OBJECT SHAPE: entries inline at obj+0xc7 stride 8 (companion dword +4 is
  mutated post-add — selection/bookkeeping, 101/102 nonzero); entries are
  LIST-ITEM HANDLES in their own 0x7b-stride run (base = rec base - 0xac),
  and SET EQUALITY {entry+0xac} == {records with NAME+0x33==race} verified
  EXACT at t1254 (102/102) and t1086-live (80/80). Signature for memory
  hunts: [o+0xab]==0 && byte[o+0xc5]==0 && [o+0xbb]==0xffffffff &&
  u16[o+0x8c9]==0x8d.
- MEASUREMENTS: bank-t1254 (user softlocked session): ONE sig-obj 0xfda074
  count=102 == header 102 EXACT, stable across all 20 bank slots. Live :9
  session BEFORE click: ZERO sig-objs in 20 slots (screen never opened);
  after window-rel click (553,145) on the sidebar "Planets" button
  (windows.txt rect 474,130-632,160): sig-obj 0xfda074 count=80 in every
  sampled slot AND the screen header renders "80 Planets Occupied,
  26 Systems Controlled" — count == count(NAMED && owner==race0) == 80.
- t248's 60-vs-80 ANOMALY: it was a STALE SCREEN-OPEN SNAPSHOT (the t1092
  header read a list populated at an earlier open). "occupied==populated"
  hypothesis REFUTED by the live experiment (all 80 owner-flag planets
  counted, no population filter). WHY the earlier open saw 60 while t1086
  owner-count is 80: UNRESOLVED (t1092 RAM rotated away; candidates mid-turn
  population, [unverified]).
- REFUTED/CLOSED SIDE-QUESTS: u16@data 0x131b4 = 60 at THREE timestamps
  (t1092, t1254, live t1086-after-open) and ZERO instructions reference
  absolute 0x131b4 (disp32 census over code [0x14bb0,0x82bb0)) — a
  race-block-relative field (blk stride 0x1ee, intra 0x1ac), NOT a header
  counter (t247's refutation now triple-confirmed). FUN_00051684/0x51b68
  have zero E8 callers and zero u32 refs (pure indirect dispatch);
  FUN_00051834 referenced once, data-seg handler table file 0x88b78. The
  widget that held OBJ was torn down (24 sites zero [reg+0xab]; zero pointer
  sites of OBJ in RAM) — heap object survives as last-open snapshot.
- HARNESS LESSON: t248's fixed-member-offset u16 intersection across two
  sessions could NEVER hit (heap layout is session-specific; the counter
  lives in a heap list object). Correct instrument = content/signature scan
  per slot, plus (decisive) a controlled live experiment.
- LIVE-SESSION SIDE EFFECT (disclosed): this iteration opened the Planets
  screen on :9 (read-only navigation; zero turns advanced, ring turn still
  1086; user save untouched — no in-game Save). xsend REQUIRES
  DISPLAY=:9 in env ("no display" otherwise); a stale "Quit DOSBox-X
  warning" blocker window briefly re-appeared and self-cleared (xsend
  refused one click during it — its blocker guard works).

### t249b DAY-COUNTER PINNED: DAY == TURN (DAT_00012e10), MEASURED
Tools: scripts/r1_t249b_dayscan.py; working log docs/re/_wip_t249b.md S1..S6.
- THE LAW: the big green 7-segment readout at the top of the UI panel (what
  the user read as "day 1254") is the TURN COUNTER rendered zero-padded to 5
  digits. At live turn 1086 it reads "01086" (vision on
  work/screens/t3/resumed_t247.png — external-display reading, R13-clean);
  it is the ONLY number-bearing string on the planet/galaxy screen.
- CENSUS PROOF no separate day scalar exists: dword==turn in bank-t1254
  (20 slots, all t=1254) intersects to exactly THREE sites — member 0x254e98
  == turn X=0x12e10 plus two heap addresses (0xfd7268 in a per-entity block;
  0x100141c inside a sequential-id dword array 1238,1239,...,1254,1255,).
  ZERO data-seg sites besides the turn. Re-run cross-session on the live ring
  at t=1086: same shape (u32 intersection {0x254e98,0x270248,0x100117c}, last
  two heap; u16==turn: ZERO data-seg hits in BOTH sessions at both values).
  A maintained day dword would sit at a fixed data offset in both sessions
  like turn/T/score — there is none.
- SEMANTIC LEG: the vendor itself equates day==turn: t244 verbatim gauge
  popup "Research: 52 per day / ... will be discovered in 37 days" while
  research accrues per turn.
- "Day %d" forensics: string is NOT in the exe payload; it is static.txt
  (ascend00.cob blob 20 @0x269d0, entry "// 17", loadwin.cpp block) loaded
  VERBATIM into the RAM pool at member 0x253032. ALL-RAM u32 referrer census
  (calibrated on restree.txt -> known site 0x468d3): ZERO genuine referrers;
  the one nominal hit (member 0x252c74) is ASCII "\xaa/%\0" of locale
  date-format fragments — false positive. Formatter reaches the pool via
  runtime-computed pointers (OQ-021-writer class instrument).
- WATCHER (t257 input): no new field needed — timeline "turn" IS the day;
  any literal "day" key is a pure alias of turn, no second RAM read.
- No ledger row moved (not an OQ). Session side effects: none on :9 (zero
  clicks, zero turns; screenshot analysis used EXISTING banked pngs).

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

## 10. t250 TURN-DRIVER v4 (scripts/r1_t250_turndrive.py) + PROBE LAW
Tools: r1_t250_turndrive.py (v4 = v3 laws + softlock detect + auto-recovery +
run log work/r1/t250_drive_<ts>.log); working log docs/re/_wip_t250.md.
- INPUT-PROBE LAW (measured, kills the task text's literal design): the 'c'
  relation overlay is GALAXY-SCREEN-ONLY, so a c-only pixel probe reads
  ZERO-CHANGE ON A HEALTHY GAME parked on a modal sub-screen (planet list:
  c -> 0 px, Escape -> 153,672 px; then galaxy screen: c -> 1,152 px). v4
  probes Escape FIRST (backs out of modals, no-op on galaxy), then c.
- SOFTLOCK = input-dead (both probes) AND ring ring-tail frozen except
  {wall,file,file_mtime_ns} over a 20 s gap. Popup presence is LOGGED but NOT
  required (t247: signature recurred with no popup); the safety the popup-check
  stood in for comes from sequencing: the interrogate only runs after TWO
  consecutive NEXTTURN presses with zero advancement and drain_popups()==0.
- RECOVERY PATH: bank save/*.sav -> work/r1/bank-t250-recovery-<ts>/, SIGKILL
  pidfile pid then leftovers by exact comm (never SIGTERM), relaunch
  r1_playcap_vnc.sh start, click Return-to-game (318,333) polling in_game,
  resume toward the SAME absolute target. work/r1/SELFPLAY.marker (1 byte)
  written at drive start, removed on clean exit 0 — presence brackets
  self-play timeline growth for future sitting probes.
  HONEST STATUS: the recovery branch has NEVER fired (no softlock occurred);
  only its primitives are individually verified (SIGKILL+relaunch+resume =
  t245/t247 manual recoveries; bank = this session's cp -p x20).
- VALIDATION (live :9, 01:41-01:45): --target 1096 from ring 1086 = 10/10
  presses advanced, drains 4,7,7,4,3,3,3,5,2,2 (34 popups total), TARGET
  REACHED, exit 0, marker removed, run log written. Drive rate ~17-25 s/turn.
  Screenshot law reconfirmed: pre-drive screen was the t249 planet-list view
  ("60 Planets Occupied" stale snapshot header — t249 snapshot law visible
  again in the wild).
