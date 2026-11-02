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

### t257 WATCHER SCHEMA: "day" ALIAS IMPLEMENTED (harness plumbing, not a law)
Working log docs/re/_wip_t257.md S1..S5.
- scripts/r1_playcap_watch.py process() now emits d["day"] = d["turn"] (pure
  alias per the t249b law above — no second RAM read). Schema 16->17 keys;
  module docstring records that pre-t257 rows lack the key, so consumers read
  j.get("day", j["turn"]). Scratch-validated (--once on banked
  bank-t251-live1255 savs): day==turn==1255 on every row.
- r214_triage tail_shape: canonical_shape() folds "day" out so 16-key orphan
  rows and 17-key new rows count as ONE schema for multiplicity math; the
  raw-shape census + day/turn agreement counters are printed separately.
  (Honest correction banked in the triage docstring: it never ASSERTED one key
  shape, it censuses them — the STATE queue text was imprecise.)
- LIVE MIXED-SHAPE WINDOW IS EXPECTED until the user retires orphan watchers
  (STATE.md pairing note: retirement is the user's call): post-relaunch tail
  census showed 7 rows with day (all agree) + 393 without, from the seven
  still-alive pre-t257 processes. The current-sitting pair 479981/479983 was
  /proc-validated and reaped; replacement runs detached (ppid 1, own session,
  pid in work/r1/playcap/watch-t257.pid).
- STARTUP-COST LAW (t257, measured): a watcher relaunch streams the whole
  live-timeline.jsonl line-by-line to rebuild the dedup `seen` set (~2-3 min
  at 7.4 GB, RSS stays ~100 MB) BEFORE its first emit — absence of new rows
  in the first 30 s is normal; the "watch: start" line in watch.out is the
  liveness signal.

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
- SPECIES-MENU STACK (t252, all zero turn drift): RACES (553,301) opens the
  species sidebar overlay; race row click opens NEGSCREEN; "Intelligence"
  (553,311) opens INTELSCREEN. Escape unwinds ONE level per press
  (intel -> species menu -> galaxy; measured by pixel-diff vs baseline:
  82k -> 3.4k). Negotiation option rows are ~29px pitch starting y~334 —
  row 1 (Goodbye) verified safe-closing; rows 2/3 are declare-war/alliance,
  NEVER click without user sign-off. Full dossier ui-runtime.md §6a/6b.
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

---

## t251 (2026-11-01) — DRIVE 1086->1255 + FIRST POSITIVE ATTACK-PRICE CASCADE WITNESS + WITNESS (b) LANDS

Drive (scripts/r1_t250_turndrive.py, hermes venv, --target 1150
--max-presses 75): presses 1-10 advanced 1086->1096 (34 popups drained);
presses 11-13 zero advance (probe input ALIVE 306,624 px; drains 0,0,2);
press 14 ring JUMPED 1096->1255 in <=22 s (08:17:36 -> 08:17:58) and the
drive exited 0 (target exceeded). Run log
work/r1/t250_drive_20261101-081121.log. Zero softlocks; recovery never
fired. Vision on work/screens/t2/drive_final_t250.png: healthy galaxy
screen, readout 01255, no popup. MECHANISM OF THE JUMP UNATTRIBUTED
[honest]: one NEXTTURN click cannot advance 159 turns, so a LOAD occurred
in the modal window the drains were closing; candidate (unconfirmed) = the
popup chain confirmed a resume-from-save dialog into the Oct-29 t1254-era
state. Ring banks: bank-t251-predrive (20 slots @1086), bank-t251-live1255
(20 slots @1255). Live copy work/r1/game/RESUME.GAM md5 5b382afb
UNCHANGED (mtime Oct 29 13:20) — user save intact.

WITNESS MINING (scripts/r1_t251_mine.py; trust=True per t214 law;
watermark caveat: the timeline holds turns to 1335 so new-session rows
below the watermark are dropped by trust — the passes below run over the
TRUSTED corpus as assigned).

1. FIRST POSITIVE ATTACK-EVENT WITNESS IN THE CORPUS (t887, wall
   15:12:56 -> 15:18:03): att[Minions][Chamachies] 324->284 EXACTLY -40
   with relation state 1(PEACE)->2(WAR) in the same autosave window, and
   NO other state/attitude transition in the pair. This is the t204
   attack-price + t208 chooser cascade observed end-to-end in live data:
   the victim's row took the -20-per-committed-weapon price (t210 stacking
   law: -40 == two committed weapons between two 10 s autosaves), the
   value crossed the DECLARE_WAR threshold (290, t208 pin), and the
   chooser flipped the pair to WAR. Direction (victim row = Minions) says
   the FIRING party was Chamachies (owner 0, the player of the old
   session) — MINUS: Minions self-declaring war with an attitude slam of
   exactly -40 in their own row is not fully excluded from stream data
   alone (no ship-window damage event co-located; see 2). Mark-window
   cross-check: bank-t1254 (same campaign, t1254) holds
   byte[0x48304+38]==0x1 — FIRST nonzero mark byte ever seen — bit 0 =
   the contact latch (t206 law: never written by the attack handler), so
   the VICTIM-BIT side of the window is still zero across every bank: if
   the player fired at t887, the t205 per-star victim mark (1<<3 for
   Minions) is NOT present anywhere — either the fire path used was not
   0x43a4c, or the mark law has an unmapped clear. BOTH readings banked;
   clamp witness (att slamming exactly to DECL-10=280) still ABSENT
   (284 != 280: this is the PRICE, not the clamp). OQ-016 row ANNOTATED,
   stays OPEN (strict-close).

2. DAMAGE CHANNEL NEGATIVE, NARROWED: over 45,227 trusted points,
   named-owner ship disappearance events = 0; shield-agg (+0x4) decreases
   = 10, and the t1253->1254 "3 ships lost shields" pair resolves as SLOT
   REMAP (owner high-u16 0xffff->2 = slot reassignment, t29b aliasing
   class), not damage. Offset churn census (coords+state+day skipped):
   high-frequency offsets {0xa8,0x5a,0x88,0x7a,0x82,0x7e,0x5e,0x84,0x68,
   0x5c,0x60} = bookkeeping/pathing; multi-volley-vs-non-at-war witness (a)
   NOT observed. Multi-volley proxy (streak) is INVALID for raw window
   diffs (every live ship's day byte +0x67 changes every turn — t213);
   streak counts are bookkeeping churn, banked as a trap trap-down.

3. WITNESS (b) LANDS (score.md S4 was corpus-blind): t212's roots
   (r1sav-*/r1deep-*/playcap ring) MISSED work/r1/bank-*. Scanning banks:
   bank-t1254 ALL 20 slots turn 1254 V=23 with NINE byte[star+0x15]
   nonzero rows [2,6,12,16,21,21..44]; bank-t251-live1255 all slots turn
   1255 V=14 with TEN nonzero rows. SEMANTIC NON-JOIN MEASURED on real
   mid-campaign slots: V != ownP (23 vs 9; 14 vs 9), V != occ (14 vs 10),
   V==systems_full in 238/45,227 trusted slots (0%), V==systems_any in
   4,970 (10%). P7 label settled: star row 2 holds +0x15==0x3 (two races)
   at both turns — +0x15 is NOT a single-owner bit; t206's vision-byte
   reading stands. OQ-021 residue shrinks to the writer law ONLY (row
   stays OPEN, strict-close). V trajectory over the trusted run:
   {0,1,2,2..23} — the t85b oscillation class reproduces; the 9 intra-turn
   V->0 dips all coincide with session-boundary slots (wall gaps; the
   07:43:50 dip precedes the 07:44 relaunch), i.e. LOAD artifacts, not
   writer oscillation — feeds t255.

CORPUS LAW BANKED (watermark): after any mid-campaign LOAD to a LOWER
turn, trust=True is blind to the new session (watermark = historic max).
Mining a post-rewind window needs trust=False + wall-clock pairing
(r1_stream's own caveat) — used correctly in the --window pass design.

## t253 (2026-11-01) — LIVE SWEEP 2: FLEET + SHIP DESIGN INTERACTION LAWS

All at turn 1255 on :9, ring turn HELD every step (20 steps, NEXTTURN never
clicked; parked parked back on the galaxy screen, 3471 px vs baseline == blink
noise). Full dossier docs/re/ui-runtime.md §6c; harness scripts/r1_t253_screen.py.
- FLEET sidebar button (553,184) opens the ship list; header shows
  "<race> (<N> Ships, <M> more allowed)" (headroom form). 4 rows page 25 ships.
- FLEET ROW CLICK LAWS (help fleetwin confirmed live end-to-end): LEFT-click a
  row = camera jump to the ship's location (planet/orbital view opens; Escape
  returns to the LIST, not the galaxy); RIGHT-CLICK (tools/xsend `click3`) =
  ship contents display (the SHIPDESSCREEN window class).
- DESIGN-SCREEN TAB LAW: every tab press repaints the tab grid (pressed tile
  darker); the GIZLIST changes ONLY for the six gizmo-category tabs (HULL
  changed 1973 px, all inside bbox x524-632 y7-76 = tab rows only). Tab->gizmo
  category measured 6/6 exact vs gizmos.txt; NOT message order (SENSORS msg 53
  = cat3, ENGINES msg 54 = cat2).
- HAZARD LAW (new, control-plane): before EVERY sweep run
  `DISPLAY=:9 xwininfo -root -tree | grep -i warning`. An orphaned
  `xmessage -buttons Yes:1,No:0 -default Yes` quit-confirm (from a DEAD dosbox,
  PPID 1) was sitting mapped on :9 for 14 h with Yes default — one stray
  root-coord click and the game dies. xsend prints "REFUSING blocker window"
  but STILL SENDS to the game window (the message names a different window);
  it is a warning, not a refusal. Remediation: kill the xmessage PID only
  (never pkill, never touch dosbox-x). Retired: PID 461872.

## t260 (2026-11-01) — LOADSTATE RESTORE IS REAL AND GUI-ONLY: t1255 BACK IN A LIVE PROCESS
THE HEADLINE (MEASURED, isolated display :8, zero production blast radius):
a banked dosbox-x savestate ZIP loads into a fresh dosbox-x process and the
GAME RESUMES MID-CAMPAIGN. Sequence verbatim from work/r1/vnc/t260-experiment2.log:
  LOG: Loading state from slot: 60
  LOG: [20:19:13]: Loaded. (Slot 60)
Screenshot: campaign map (lanes + colonies), turn readout reads 01255.
STRUCTURAL VERIFICATION (the authority, not vision): from the loaded process,
Capture-menu "Save state" wrote a fresh ZIP (Save_Remark b'' — menu-saves carry
no remark, vs b'Auto-save' in ring copies), and the watcher decoder on that
round-trip ZIP (work/r1/bank-t260-roundtrip-1255/60.sav, md5 e23b20c9) reads
turn=1255 and V=14 — identical to the frozen t1255 timeline row (V=14). The
bank work/r1/bank-t251-live1255/60.sav is UNTOUCHED (md5 0024340d re-verified
afterwards; RESUME.GAM still 5b382afb == Oct-29, the game never wrote it).

MENU CENSUS (dosbox-x 2025.02.01 SDL2, no -nogui): menu bar Main CPU Video
Sound DOS Drive Capture Help; save/load-state lives ONLY under Capture:
  Take screenshot | Take raw screenshot | Capture format | Record video AVI |
  Record audio WAV | multi-track AVI | FM (OPL) | MIDI | network traffic |
  Save state (F12+S) | Load state (F12+L) | Save/load options > | Select save
  slot > | Auto-save settings... | Browse save file... | Display state info.
No CLI loadstate flag (--help verbatim), no autoexec command, no [hotkeys]
section in the reference conf; mapper_loadstate/mapper_savestate exist as
MAPPER ACTION names (strings on the binary) bindable via the Mapper editor —
but the editor refuses while a program runs ("Another program is already
running." dialog observed). => headless (=-nogui) restore remains IMPOSSIBLE;
with the GUI menu it is fully scriptable via xsend clicks.

WHY THE PAIRING-SESSION F12 ATTEMPT FAILED (two independent reasons, both
measured): (1) bare F12 is the hostkey and the load chord is F12+L —
tools/xsend sends keys with state=0 (no modifier support, xsend.c comment
"synthetic modifiers unverified"), so the chord was never deliverable as-is;
(2) the earlier conf-only route (saveslot=60 + forceloadstate=true) only sets
the ACTIVE SLOT — forceloadstate is documented (reference conf L182) as
"load even if version/machine/program/memory MISMATCH", a bypass flag, not a
trigger. Synthetic BUTTON events via xsend DO drive the SDL2 menu (dropdowns
opened and screenshotted repeatedly), so menu clicks are the reliable path.

TL-TIME-BOUNB EXPULSION LAW (measured, mechanism partially unverified):
attempt 1 ran the loader WITH `-time-limit 1800` and loaded the t1255 state;
"Loaded." logged, then the process exited within seconds. Attempt 2, identical
minus `-time-limit`, loaded and STAYED ALIVE (verified >7 min, healthy window,
re-save round-trip). Raw-u32/u64 scans (28800 and x1000) of Dos/CPU/Dosbox-x/
IntTimer10 members of the state found NO carried deadline value, so the exact
carrier is [unverified] — but the OPERATIONAL LAW is clean: NEVER pass
-time-limit to a process you intend to loadstate INTO; the deadline belongs to
the loading process only. (The production ring keeps TL on the writer side,
which is unaffected.)

SAVEDIR LAW: slot files resolve to <savedir>/NN.sav; savedir defaults to
cwd-relative "save". The experiment used explicit -savedir
work/r1/t260-loadstate/save holding ONLY the clean t1255 copy, so the
production ring (work/r1/playcap/save) was never addressable. For t261: load
the t1255 copy from a scratch savedir copy, NEVER from the ring dir.

TOOLING: scripts/r1_t260_menulocate.py — opens the Capture menu via xsend,
screenshots the window (ID resolved by name via xwininfo), finds the dropdown
panel by NEUTRAL-DARK pixel census (ImageMagick txt:- is 16-bit: thresholds
are against 65535, an 8-bit threshold silently matches nothing), prints text-
row segment centers (~16 px pitch). Window IDs CHANGE per launch (0x600009 ->
0x200009); resolve by name, never hardcode. pkill -f matched this session's
own shell again (known footgun re-triggered, harmless) — targeted PIDs only.

CONSEQUENCE FOR THE QUEUE: t261 base = t1255 (restored state), NOT t1086. The
restored process must be launched GUI-style (no -nogui, no -time-limit) on a
free display; the production :9 t1086 session keeps running until t261
decides otherwise (t261 owns that blast-radius call). The t1255 death-frame
ZIP loss (324d2d75, overwritten by autosave churn per the pairing note) does
NOT block t261: the bank copy is the load source and the round-trip above
reproduces t1255 V=14 from it.

## t261 (2026-11-01) — SOFTLOCK-CLASS CENSUS REACHES 4 INCIDENTS; THE SAVE ITSELF CARRIES IT
(1) :8 restored-t1255 session: input-dead ON LOAD (see REFUTED-ROUTES t261;
screen md5-frozen, core-state identical across ring slots, SDL menu responsive,
90% CPU). The engine was already input-dead when the t1254-era autosave was
written — softlock is a SAVEABLE state, which retro-reads bank-t251-live1255
as a softlock artifact, not a healthy snapshot.
(2) production :9 at 21:38: mid-drive the RAM went from a HEALTHY t1111
(banked, V=23) to a t1255/V=14 profile within ONE 10 s slot (53->54), then to
the TITLE MENU (vision), then input-dead there too (arrows 0 px). dosbox.log
has ZERO loadstate lines; no in-game on-disk SAV decodes to t1255; the VNC
"client" is a zombie from Oct 16 (bytes_acked frozen). MECHANISM [unverified] —
candidates: drain-popup misclick chain on the bare galaxy screen (t244
precedent that misclicks act), or an engine-side fault that self-exits to the
title. NEW TELL for t266: ring rows OSCILLATE t1254<->t1255 while input-dead
(turn site 0x12e10 toggling with no input) — the game loop is ALIVE (89.7%
CPU) and mutating the turn counter; only input handling is dead. Evidence:
work/r1/bank-t261-prod-titlesoft/ (20 slots), prod-softlock-title.png.
RECOVERY EXECUTED per SOP (bank -> SIGKILL recorded pid 524517 ->
r1_playcap_vnc.sh start -> Return-to-Game click): resumed t1086 V=0 at
23:05:11, re-drive running toward 1236 (base+150). HONEST LOSS: the live t1111
RAM image is gone (ring-banked slots survive; RESUME.GAM never advanced past
t1086 all day — the game only writes it at an in-game Save, and the drive must
NOT click Save unattended since a misclick there could hit adjacent dialogs).

## t266 (2026-11-02) — SOFTLOCK-CLASS FORENSICS: THE t261 "PRODUCTION SOFTLOCK" IS A TWO-WRITER RING COLLISION; I3 IS TL EXPIRY; THE OSCILLATION IS A ~150 s CYCLE
Campaign fingerprint law (NEW, MEASURED): a slot's campaign identity = md5 of
the (star -> sorted owner-multiset) table from r1_income_law.find_records.
Distinct campaigns measured: production-drive-Nov1 f8bf068b76 (t1086-1111,
V23, 26 systems); restored-t1255 lineage 47d063a23e (:8 soft1255 bank 21:22,
t251-live1255 08:21) -> e1d3bdc128 (prod-titlesoft 22:47, live-advanced point
of the SAME campaign); Oct-31 t1254 bank 7391e3f8d6 (V23); re-drive lineage
9710dec431 (t1101-1236, V23). Memory-md5 differs within a lineage (RAM
advances); the planet table does not. ALWAYS fingerprint before trusting rows.
1. I4 (t261 "production :9 soft-locked at 21:38") CONTENT REFUTED. The flip
   slot-pair is banked: bank-t261-t1255 slot 53 mtime 21:38:12 fp f8bf068b76
   t1111 V23 -> slot 54 mtime 21:38:22 fp e1d3bdc128 t1255 V14 (36 systems).
   A different campaign cannot appear in a -nogui process's RAM without a
   loadstate; production dosbox.log has ZERO "Loading state from slot" lines
   (n=0, re-verified this session over 5.8M lines; NOTE "Extracting:" lines
   n=3.89M are the SAVE-path slot-metadata churn, NOT load evidence — do not
   misread them). The post-flip ring holds ONLY the restored campaign (no
   interleave), so production's own autosave went SILENT at 21:38:12 while a
   second writer with savedir=playcap/save and restored-t1255-campaign RAM
   began writing 10 s slots at 21:38:22. Production's own contribution to the
   bug class: a SILENT guest hang (input-dead + md5-frozen screen, measured
   t261 22:05-22:16) — distinct from the restored campaign's noisy oscillating
   churn. The second writer's process identity is [unverified] — log-gap
   anchors show launches 20:08 (= t260 experiment, t260-dosbox.pid 20:08) and
   ~21:01 (t261_session.sh, explicit -savedir t261-drive/save, churned there
   21:01->21:22:21 then stopped = that process's last rites); no surviving
   cmdline shows who redirected to playcap/save at 21:38:20. REFUTED ROUTE
   filed: do not attribute playcap rows 2026-11-01 21:38-23:06 to production.
2. THE OSCILLATION IS QUANTIFIED (restored campaign, shared-ring witness):
   21:41-23:03 window = 511 rows -> 11 state-runs. Pattern: single-row
   t1254 run with CONSTANT ship-state hash ede612 at 21:44:12 / 21:49:02 /
   21:56:23 (~150 s = 15-slot spacing), each immediately followed by a 14-row
   t1255 run with a NEW ship hash each cycle (c15523->5480fc->db7cf2->051e29
   ->cd5885->dcc09f). Reading: the engine completes a turn-TAIL movement pass
   every ~150 s and toggles the turn counter 1255->1254 once per cycle without
   a fresh commit — t265's slot-30 d=32/64/160 displacements are these
   between-cycle movements in RESTORED-campaign RAM (the t265 feed stands as a
   bug witness, but NOT as a production event). At 21:58:33 the churn STOPS
   into a single frozen run (403 rows to 23:03, hash 3fb209ad) = the title-
   menu transition t261 saw via vision.
3. I3 (15:45 process death) ROOT CAUSE MEASURED: production was launched
   07:46:21 (watch.out marker) with -time-limit 28800; 07:46 + 8 h = 15:46 —
   the RUNAWAY GUARD expired mid-drive and killed the game. Watch.out gap
   15:45 -> 18:35 brackets the unnoticed window. HARNESS LAW for t267: a
   morning launch makes TL a play cap; compute TL from wall-clock to a fixed
   deadline (or stop passing it for supervised-daytime sessions).
4. PROBE LAW AMENDMENT (t250 law stress-failed): the drive log's periodic
   "input ALIVE (changed_px=306544)" during the whole stuck window is
   ANIMATION, not input — 306,544 of 307,200 px = full-frame starfield churn
   between the two grabs. The Escape-leg diff is meaningless on an animating
   screen. Liveness must be judged by the c-leg (overlay toggle, ~1k px,
   local) or a RAM needle, never by full-frame diff. t261's mid-window ALIVE
   readings were false positives; the later arrows-probe (0 px) was correct.
5. CROSS-INCIDENT TRIGGER CLASS (honest status): I1 popup-present hang,
   I2 planet-list-modal hang (no popup), I4-silent production guest hang at
   21:38:12 (cause on disk unresolvable; last driver action was press 19 +
   drain 2, popup OK-bands overlap the galaxy screen per t244 misclick law —
   [unverified]), I5 input-dead-on-loadstate (save-carried). NO single common
   engine state identified from disk evidence (popup queue depth is not
   ring-visible; I2 had no popup). The restore-lineage sub-class (I4 content,
   I5) is save-carried and already REFUTED as a drive route (t261). Rewrite
   robustness note: the vendor engine can hang with the emulator alive; a
   rewrite watchdog should detect input-dead + RAM-frozen per the t250 law
   (c-leg version) rather than CPU.

## t267 (2026-11-02) — HARNESS SELF-HEAL: DEATH/TL/WATCHER DETECTION SHIPPED; THE 3-WRITER COLLISION WAS CAUGHT LIVE AND KILLED

CONTEXT (queue verbatim): the t266-measured 15:45 death (dosbox-x
-time-limit expiry) went unnoticed ~1.5 h because production runs
loop_one_task.sh with IDLE_GATE=0 — r1_idle_probe.py never fires between
iterations and nothing polls work/r1/vnc/dosbox.pid.

MEASURED THIS SESSION (pre-flight, 04:24-04:26):
- THREE r1_playcap_watch.py writers alive on playcap (524207 since 18:40,
  524532 since 18:49, 535187 since 23:03 = current), each holding an open fd
  on live-timeline.jsonl (t215 writerhood law re-applied). Duplication
  MEASURED in the last-400 KB tail: 16 rows = 6 distinct (file, mtime_ns)
  keys, reps {3x5, 1x1} — every ring write landed THREE times because each
  watcher's `seen` dedup is per-process (jsonl-derived at start only). The
  t266 oscillation forensics read data with this 3x amplification live.
- Ring current (slots at exact 10 s spacing), game 535172 alive, TL expiry
  hand-computed 23:03:57+28800 = 07:03:58.

SHIPPED (all stdlib/shell, no new deps):
1. scripts/r1_game_health.py — exit 0 HEALTHY / 1 UNHEALTHY / 2 broken;
   checks G (recorded pidfile + comm == dosbox-x; ADOPTION rule: pidfile
   lost but exactly one harness-launched dosbox-x in /proc (cmdline carries
   $RUNDIR) => record it, do NOT call it death; zero => G:DEATH + write
   work/r1/loop/GAME_DEAD.txt; >1 => G:MULTI-DOSBOX, checked EVEN with a
   valid pidfile — t261's class is production+stray both harness-launched),
   T (TL expiry from /proc/PID ctime + its own -time-limit arg; T:WARN at
   WARN_AHEAD default 600 s BEFORE expiry — the t266 ask; T:EXPIRED after),
   W (watcher census on OUT; 0 => NOWATCHER, >1 => MULTI-WRITER naming the
   reaper), F (newest save/*.sav mtime age > FEED_MAX_AGE 60 s => FEED-STALE;
   NEVER opens live-timeline.jsonl — OOM law), B (BRINGUP=1 env: ring row
   within VERIFY_WINDOW 30 s). Artifacts: loop/GAME_HEALTH_LIVE.txt (atomic
   tmp+rename), loop/game_health.tsv (append-only history).
   VERIFIED: production run HEALTHY at 04:31 and 04:59 (TL line matches hand
   computation); fixture battery (dirs via R1_VNC_DIR/R1_PLAYCAP_DIR/
   R1_LOOP_DIR env, fake dosbox-x compiled in /tmp): DEATH+GAME_DEAD.txt,
   adopt-sole (pidfile written), MULTI with valid pidfile, stale-pidfile +
   expired-new game, T:WARN, PIDSTALE, foreign-dosbox note, zombie exclusion
   (a defunct child still reads comm=dosbox-x — MEASURED trap), instrument-
   broken RC=2. E2E sandbox (/tmp/t267sb: copied scratch game — game/ never
   mounted — display :10, TL=120): start -> BRINGUP OK; T:WARN 100 s BEFORE
   expiry while alive; TL KILL at 04:57:44 -> next health run G:DEATH +
   GAME_DEAD.txt naming the pid; production :9 untouched throughout (foreign
   census noted it correctly).
2. scripts/r1_watch_reaper.py OUT [--keep N] [--dry-run] — /proc-enumerated,
   per-PID verified (comm python* AND cmdline has script name AND OUT dir),
   keeps newest-started N, SIGTERM only, never pattern-kills (pkill -f
   self-match footgun honored). LIVE RUN on production: REAPED 524532 +
   524207, KEPT 535187 (dry-run first; victim set matched t266's recorded
   stale pair exactly). POST-REAP MEASURED: timeline tail 10 rows / 10
   distinct keys, reps all 1 — duplication gone.
3. scripts/r1_playcap_vnc.sh: 'status' runs the health pass; 'start' runs
   the /proc reaper with --keep 0 (dosbox is dead in that branch, so every
   surviving watcher is stale — keep>=1 would spare the newest stale one and
   recreate the class), then BRING-UP-VERIFY (poll ring for a row newer than
   30 s; prints BRINGUP OK/FAIL); and a t267 ADOPTION GUARD closes the ROOT
   of the t261 collision: if dosbox.pid is lost while a harness dosbox
   (cmdline carries $RUNDIR/session.conf) still lives, old 'start' judged
   "no sitting" and launched a SECOND game on the same ring — the guard
   adopts+records instead, reaps to one watcher, relaunches the watcher if
   missing. VERIFIED in sandbox: rm dosbox.pid + live game -> 'ADOPTED live
   dosbox pid ... nothing launched', census shows exactly one sandbox
   dosbox; rm pidfile + dead game -> clean relaunch + BRINGUP OK.
4. scripts/loop_one_task.sh: runs r1_game_health.py EVERY iteration before
   the pre-flight gate and logs one GAME-HEALTH line (advisory, non-fatal —
   relaunching the game is research-schedule policy, not scheduler work), so
   a death is wall-stamped in loop.log even under IDLE_GATE=0. NOTE: bash
   reload semantics MEASURED this session (two /tmp probes, bash 5.2.37):
   in-place truncate+rewrite of a RUNNING script corrupts the survivor at
   its parse offset (syntax error mid-loop); tmp+rename (what patch/
   write_file tools use — _atomic_write, file_operations.py) leaves the
   survivor reading the old inode. loop edits therefore take effect at the
   NEXT loop relaunch, never mid-flight — safe by construction.

BANKED LIMITS / honest negatives:
- The detector DETECTS and STAMPS; it does not relaunch. An unattended
  relaunch would overwrite the softlock evidence state (t261 law: bank
  before restart), so GAME_DEAD.txt + the loop.log stamp + the next
  iteration's own pre-flight are the designed response chain.
- T:WARN fires UNHEALTHY (rc=1) while the game is alive — deliberate: the
  whole t266 failure was silence-before-expiry. Consumers that grade
  "process up" only should read the G: reason codes, not rc alone.
- FEED-STALE cannot distinguish "game at title with autosave off" from
  "watcher wedged" if autosave ever stops while the process lives; under
  the current autosave=10 41-60 conf the ring churns even at the title, so
  staleness means trouble. A future conf change must re-check this row.
- TL is read from the process cmdline only; a game launched WITHOUT
  -time-limit reports no TL line (invariant says always pass it).
- No OQ row touched: this is control-plane work (harness), ledger stays
  14 closed / 4 open.

### t267 INCIDENT (self-inflicted, caught by the new detector, recovered)
The sandbox cleanup line in this session included `pkill -x dosbox-x
-u $USER` — exact-name, but production :9 IS dosbox-x: the pattern matched
PID 535172 and SIGTERM'd it at 04:58:58 (last ring row 48.sav). dosbox-x
popped its quit-confirm ("Quit DOSBox-X warning", xmessage window
0x1000025 @ +197+253, (Yes) default — the banked law exactly); the GUEST
FROZE MODAL for ~17 min. The game never died.
DETECTION: r1_game_health.py run 04:59:00 was still HEALTHY (ring row 3 s
old — SIGTERM had just landed); the 05:04:28 run printed F:FEED-STALE
(331 s) — the ring-stall signal fired on a REAL incident within minutes of
the first post-event check. (Not automatic: the live loop runs the pre-edit
inode until relaunch — the t267 wiring lands next loop start.)
RECOVERY: xwininfo -root -tree located the blocker (t245 law stays valid:
its point is xsend TARGET CONFUSION — the blocker title matches 'DOSBox-X',
and xsend refuses 'warning' titles, which is exactly why tclick-by-ID was
needed here; import -window root did show this dialog, do not infer
blockers are invisible in general). xsend REFUSES
"warning" titles by design (t245), so scripts/tclick.c (new; compile:
gcc -O1 -o tclick scripts/tclick.c -lX11 -include string.h) clicks a window
by EXPLICIT ID — clicked the "No" child (0x1000027, 31 px = "No"; Yes is
the 35 px child 0x100002a) at (15,12). Dialog closed 05:15:51, ring resumed
(49.sav age 2 s at 05:15:53), campaign readouts byte-identical across the
freeze (t=1236 mine_any=26 full=25 DAT_482fb=23/50) — no reload happened.
LAW BANKED: production cleanup NEVER pattern-kills dosbox-x (exact-name is
NOT sufficient — there is exactly one production process with that name);
kill ONLY PIDs recorded in work/r1/vnc/dosbox.pid, verified via /proc
cmdline (sandbox conf path). Sandbox teardown = vnc.sh --stop + reaper on
the SANDBOX out dir, nothing else.

## t268 (2026-11-02) — LIVE SWEEP 3: NEGSCREEN FLOW, INTEL DEPTH, RESWIN DOSSIERS
Full dossier docs/re/ui-runtime.md §6d; screens + _state.json
work/screens/t268/; harness scripts/r1_t268_screen.py (t253 primitive). 15
steps, ring turn HELD 1236, zero drift, NEXTTURN never clicked, parked on
galaxy (242 px vs baseline = blink floor). Pre-flight r1_game_health.py RC=0.
SWEEP LAWS BANKED (interaction-class, this file's remit):
- Species-menu race rows: hit target is the TEXT LINE (~10 px; game y ~73/
  ~140/~207), NOT the divider-bounded cell — a click between rows is a no-op
  (164 px blink). Re-measure bands per campaign state; do not reuse t252's.
- NEGSCREEN option list is posture-AND-campaign-dependent (3 rows t252/t1255,
  5 rows t268/t1236): always re-read rendered bands (bright-pixel detection,
  x336-632) before clicking any row; only the Goodbye row (band 1, hoisted)
  is safe by construction, and DA_NoDipAction closes directly to the species
  menu with no alien-reply step.
- INTELSCREEN rows are NOT clickable (204 px blink on row click) — the list
  IS the terminal intel depth; no detail screen exists behind it.
- RESWIN empty-disk click SETS the study topic with NO confirm popup (900 px
  confined to the disk). This is a STATE-CHANGING click: a sweep must not
  click empty disks unless changing the campaign's research is intended
  (t268 did ONE such click — Repulsion Beam Tech — recorded honestly;
  no in-game revert exists).

## t273 (2026-11-02) — DRIVE LEG LOST TO A TITLE-MENU MISCLICK (LAW) + FULL-CORPUS WITNESS HARVEST

DRIVE FAILURE AND ITS LAW. The t250 v4 driver's pre-drive popup drain closed 1
"popup" at 11:35:14 EST and 2 s later the ring lineage flipped 1086/4-power
(Chamachies/Orfa/Ungooma/Minions) -> 645/3-power (Nimbuloids/Hanshaks/Chronomyst):
the vendor TUTORIAL campaign (screen: "Terpsichore / Orange Medium", Explorer I +
Defender I, modal "Do you wish to exit this tutorial?" —
work/screens/t273/now_1156.png). CAUSE [inferred, strong]: the popup detector
(white-text rows in root band y 330..470 == game y 230..370; click = rightmost
label of the lowest row at ytop-3) fires on the TITLE MENU — refcap.md measured
title rows 252/293/333 and ui.md PLAYTUTORIAL rect (159,240)-(477,270), so the
game-y=237 target lands inside Tutorial. dosbox.log corroborates ("Active save
slot: 1 [Empty]" then tutorial autosaves). LAW: popup drain must never run while
the game sits at the title menu; recovery/drive clicks must be band-measured per
screen, never detector-derived. The t251 "popup chain confirmed a resume dialog"
load is the SAME class. A remote VNC client was connected during part of the
window (ss [::1]:53822<->x11vnc pid 1207, no local owning process), so a human
click is not fully excluded; both readings recorded. Driver killed at 11:49, zero
further input; RESUME.GAM md5 5b382afbb789186c3654f3cec085b2e2 UNCHANGED; the
1086 campaign is preserved in work/r1/bank-t273-predrive (20 slots) and the
tutorial ring in bank-t273-tutorial645.

HARNESS BUGS EXPOSED IN THE t251 MINE (both measured this session):
(1) mine_stream reads owner as the u16 pair at +0x54 = the owner HANDLE
(196608/131072...), not the race INDEX byte at +0x56 (verified at t1253: byte56
maps to relation names exactly and equals the watcher's ships[].owner). Its
`relv != 2` filter therefore never filtered: the "252 non-war candidates" are
not witnesses. (2) Stale-echo rows (an old session's turn 692 landing between
live 1037/1038) pass a plain adjacent-row pairing and mint phantom attitude
deltas (-38/-52 "Ungooma->Orfa"); guarded by requiring prev_turn in
{turn, turn-1} plus an mtime gap <= 120 s. (3) Nearest-other-owner != attacker:
scripts/r273_vet.py prints, per damage hit, min distance to a WAR power vs a
PEACE power.

FULL-CORPUS HARVEST (scripts/r273_harvest.py; 72,327 deduped rows, 72,128
guarded same-lineage pairs; work/r1/t273_harvest_full4.out + t273_legA.json):
- LEG A (OQ-016): 50 damage hits (32 hull-decrease, hist -13:5 -12:1 -11:1
  -10:1 -8:10 -7:1 -4:10 -2:3; 18 shield-only -10/-6/-5:8/-2:5/-1:3); 26 hull
  hits AT_WAR, the 3 PEACE-labelled and 3 state-0 rows all FAIL the vet (min
  distance 363..1854 u, no ship of either class within the 60 u reach) =>
  UNATTRIBUTED. Damage against a NON-at-war owner: STILL ZERO corpus-wide.
  MULTI-VOLLEY: 12 (turn,slot) pairs with >=2 hits across consecutive rows, all
  in the t1253 Chamachies-vs-Ungooma AT-WAR battle (slot 14 six hits; slot 23
  hull steps -4,-4,-8) + one at t908 state-0 — the filter reproduces the known
  battle, so its zeros elsewhere are meaningful. SECOND price+cascade witness:
  Ungooma->Chamachies 477->437 EXACTLY -40 with state 1->2 in the adjacent pair
  at wall 00:35:35 t1253 (plus its bank duplicate 08:22:52); t887 (t251)
  re-confirmed as an adjacent-pair event. A -28 price (Chamachies->Orfa
  618->590) fired with NO war flip (state 1->1). Clamp target DECL-10=280 still
  never hit. OQ-016 annotated, STAYS OPEN.
- LEG B (OQ-021): ZERO rows V>=25 corpus-wide (V max 23); selector census
  {0: 71,679} outside the tutorial lineage. THE FIRST NONZERO SELECTOR IN THE
  CORPUS: the tutorial lineage (648 rows) reads selector_byte=2 and rank=1 at
  the relocated DATA base (verified in guest RAM: P+0x43510==2, P+0x4350c==1)
  while the player owns 3/50 systems and V=0 — i.e. the byte is NOT the
  end-ctrl threshold reading. Presenter arms measured by push-imm scan at
  payload file 0x2c03a default / 0x2c04d end-xtnc / 0x2c064 end-dest / 0x2c07a
  end-capt (score.md S3 missed this one) / 0x2c092 end-unit / 0x2c0a9 end-ctrl;
  dispatch `jmp dword[0x10173e0+eax*4]` @0x2c033, table not locatable by
  arm-dword search (3 stray dwords in range only) => selector->arm MAPPING
  [unverified]. The five end-*.txt strings sit at identical static addresses in
  tutorial AND production slots (image content, not an event trace). STAYS OPEN.
- LEG C (OQ-019): magnetron USE frames ZERO (st5 control-class 160,747 rows,
  other 0). STAYS OPEN.

## t277 (2026-11-02) — TL EXPIRY CONFIRMED AS THE PRODUCTION DEATH MODE; DOSBOX-X LOGS NO FAREWELL; SOP FIXED
Pure-offline forensics over logs already on disk (no drive, no :9 touch —
production 576895 was left running and HEALTHY throughout). Full per-session
census table + honest negatives: docs/re/_wip_t277.md. Method: session
boundaries = the 33 `LOG: DOSBox-X version` banner line numbers in
work/r1/vnc/dosbox.log (290 MB, awk pass); session lifetime = first..last guest
timestamp `LOG: [hh:mm:ss]`; autosaves = count of `Saving state to slot`.

LAW 1 (MEASURED, n=18 of 33): a dosbox-x run under `-time-limit N` dies at
28810-28820 s wall (N=28800). 17 of those 18 banked exactly N/CADENCE =
2880 ring saves (+1 for the slot landing in the final second); the exception
S31 banked 2780 (row-suppression window, see RESIDUES). The ring save COUNT is
the TL counter read out through the autosave cadence law (10 s), so on a
healthy-cadence session the death cause is diagnosable from the ring alone:
2880 saves == TL expiry. All THREE deaths the t273 handoff note called
"unexplained" are TL expiries: S21 ends 15:43:56 (28816 s wall, 2880 saves —
the "+15:45 pattern" leg), S28 ends 15:45:08 (28811 s, the Nov-1 incident), S31
ends 07:04:27 (28819 s, the Nov-2 incident). NOT an engine crash. The other 15
sessions ended short of TL (manual stop / kill / short interactive sittings),
so the signature is specific, not universal.
  Caveat kept [inferred]: whether dosbox-x's internal exit or the
  `timeout -s KILL $((TL+30))` wrapper is the proximate killer is NOT separable
  from wall clock (measured lifetime sits between TL and TL+30). The help text
  says the emulator kills itself; either way the session ends at the configured
  TL, which is all the SOP depends on.

LAW 2 (MEASURED, NEGATIVE — the queue asked for the "exact farewell line"):
there is NO farewell line. `grep -c 'Shutting down'` over the 290 MB production
log == 0; `grep -c -i 'kill'` == 0; the only time-limit strings in
/usr/bin/dosbox-x are the help text ("Kill the emulator after 'n' seconds") and
the conf variable name. Golden witness ON DISK:
work/r1/selftest-t111-playcap/dosbox.out (the t111 TL=90 self-test, launched
21:09:12, first guest stamp 21:09:22, 9 saves == 90 s, last line
`LOG: [21:10:42]: Saved. (Slot 49)`, EOF after the slot-list refresh
`LOG: Active save slot: 1 [Empty]`). Same silent tail in
work/r1/playcap-20261013-001711/dosbox.out and
work/r1/playcap-20261014-214407/dosbox.out.
  CONSEQUENCE (binding for every future drive row): TL-death is
  undetectable-by-log-line. Liveness must be POLLED from /proc (recorded pid +
  comm), which is exactly what scripts/r1_game_health.py does. Do not author
  another task that hunts a log marker for this.

LAW 3 (MEASURED, n=198 iteration gaps from work/r1/loop/journal.tsv): the loop
samples health ONCE PER ITERATION (loop_one_task.sh:185, before the pre-flight
gate) and iteration gaps run p50 1502 s / p75 3435 s / p90 6206 s / p95 8682 s /
max 15156 s. t267's pre-expiry warn window (WARN_AHEAD=600 s) is therefore
~4-11% likely to be sampled at all — the warn existed but was structurally
unobservable. Confirmed empirically: the Nov-2 07:04 death was reported at
07:39:24, 35 min AFTER the fact (loop.log `G:DEATH`), and no `T:WARN` row for it
exists anywhere in loop.log.

SHIPPED (this iteration):
1. scripts/r1_game_health.py WARN_AHEAD default 600 -> 14400 s (covers p95 of
   the sampling interval). VERIFIED BOTH DIRECTIONS on a /tmp fixture (fake
   dosbox-x compiled with gcc, own vnc/out/loop dirs, TL=1200): default
   -> `T:WARN(expiry ... in 1199 s)` RC=1; WARN_AHEAD=600 -> no warn (old
   behaviour reproduced); production re-run HEALTHY RC=0 (146798 s left, no
   false warn); after killing the fixture by its RECORDED pid -> G:DEATH +
   GAME_DEAD.txt. Production :9 was never signalled (health reports it as a
   "foreign" pid from the fixture's point of view, and vice versa).
2. scripts/r1_playcap_vnc.sh TL default 28800 -> 172800 (48 h runaway guard)
   with the measurement cited inline. A guard that fires mid-sitting costs a
   sitting; 48 h exceeds any realistic one while still bounding a forgotten
   process. Production is ALREADY running TL=172800 (launched 10:07, expiry
   2026-11-04 10:07:01) — this change makes the default match what the t273
   hand-relaunch used, so a future relaunch cannot regress to 28800.
3. scripts/gate.sh stage 3n3 (static, side-effect-free): asserts the TL=172800
   default, the WARN_AHEAD=14400 default, and that loop_one_task.sh still
   samples health every iteration. MUTATION-VERIFIED: reverting either constant
   in a copy makes the stage fail (MUT1/MUT2 CAUGHT); positive path OK1-OK3;
   `bash -n scripts/gate.sh` clean.

SOP — PRE-EXPIRY RESTART INTO A FRESH TL (verbatim, the procedure t277 was
asked to document; use it whenever r1_game_health.py prints T:WARN, or proactively
before a long unattended drive):
  0. Preconditions: bank the ring first — `cp -a work/r1/playcap/save
     work/r1/bank-tNNN-preTLexpiry`. NEVER loadstate (input-dead-on-load, t261).
     NEVER overwrite work/r1/game/RESUME.GAM by hand.
  1. Check nobody human holds the display: `ss -tn | grep 5910` must show no
     ESTABLISHED client (BLOCKED.md t273 release condition).
  2. Graceful end of the sitting: `bash scripts/r1_playcap_vnc.sh stop`
     (SIGTERM to the RECORDED pid only; SIGKILL leaves a quit-confirm modal —
     BLOCKED.md law). Wait for the watcher to flush (the script sleeps 7 s).
  3. Relaunch into a fresh clock: `bash scripts/r1_playcap_vnc.sh start`
     (TL now defaults to 172800; the adoption guard t267 prevents the t261
     two-dosbox-on-one-ring class). The game resumes from its own title-menu
     resume file, so the in-game turn may LAG the ring (S1 law) — read the
     in-game turn counter from a screenshot before trusting stream tails.
  4. Verify: `python3 scripts/r1_game_health.py` must print HEALTHY with the
     NEW expiry (start + 172800), and `BRINGUP OK` from the start output.
  Why restart rather than raise the limit in place: dosbox-x has no runtime
  command to extend -time-limit (no such string exists in the binary), so the
  only lever is the launch-time argument.
RESIDUES (kept open, strict-close):
  - S31 banked 2780 saves in 28819 s (1019 s of the window produced no ring
    row). Not re-litigated: the t266 ~150 s oscillation and modal-freeze windows
    both suppress rows, and the lifetime verdict rests on wall clock, not the
    save count. [unverified] which suppression applied.
  - TL-death of a session whose ring is NOT 10 s cadenced (paused, modal,
    tutorial) will NOT show 2880 saves; Law 1's diagnostic works only on a
    healthy-cadence session.
