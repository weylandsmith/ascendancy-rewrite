# t285 WIP — LONG DRIVE + WITNESS HARVEST III (started 2026-11-03 ~04:20 EST)

## S0 — Intake / pre-flight (MEASURED, before any click)
- r1_game_health.py RC=0: HEALTHY, game pid 636955, TL expiry 2026-11-04 22:33:42
  (152612 s left at 04:10), watcher 636970, ring 57.sav age 0 s.
- cmdline (MEASURED via /proc/636955/cmdline): `dosbox-x -conf
  work/r1/vnc/session.conf -nogui -time-limit 172800` — TL=172800 per the t277
  standing rule; wrapper `timeout -s KILL 172830` pid 636953.
- Window (MEASURED xwininfo :9): "DOSBox-X 2025.02.01: ASCEND - 100%" 640x480+80+100
  => MENUBAR=0 (-nogui), XOFF/XOFF 80/100, NEXTTURN window-rel (511,67). Same
  geometry the Nov-1 production drive used (drive_20261101-230713.log: 152/152
  presses moved, target reached).
- Hazard scan: xwininfo -root -tree | grep -i warning|confirm|xmessage => EMPTY
  (t253 pre-sweep law satisfied).
- RESUME.GAM md5 5b382afbb789186c3654f3cec085b2e2 == user-oct29 backup (production
  lineage lineage anchor intact).
- Ring lineage (tail 200 KB, 8 rows): turn 1086, in_game True, planets_mine 26,
  DAT_482fb=0/50 (parked campaign: V derived 0 until first end-turn pass).
- VNC client ESTAB on :5910 present — per the PAIRING-SESSION NOTE the user
  granted ("Don't worry about my save games or a VNC grabbing the session") this
  no longer HELD drive-class work (t279/t287 rows treat the grant as superseding
  the t273 release conditions).
- No new sitting: tail max turn 1086 == baseline; r1_t85g_sitting.py NOT run
  (assignment stands).
- Production drive dir reuse: work/r1/playcap (save/, live-timeline.jsonl) — the
  same BASE the Nov-1 production drive used with T261_* envs; single-writer ring
  law respected (only pid 636955 writes this ring; no scratch dosbox launched).

## S1 — Plan
- Pre-drive bank bank-t285-predrive, then r1_t261_drive.py (env-parameterized,
  the sanctioned production driver) T261_DISPLAY=:9 T261_BASE=work/r1/playcap
  T261_MENUBAR=0 T261_RECOVER=resume, target 1250, presses<=170, softlocks<=1
  (Nov-1 witness: 152 presses 1086->1236 at ~10 s/press => ~28 min).
- Drive runs in background with notify; harvest legs (a)/(b)/(c) run OFFLINE on
  the driven corpus afterwards (t273 pattern), using the t273 attribution fixes
  (+0x56 owner INDEX byte; r273_vet.py engagement vet) and r284_vreplay.py as
  the per-slot V mine-check.
- Leg (b) REFRAMED per STATE: gap to V=25 is a gap of LANES ADMITTED at the
  end-turn pass (V == admitted lanes + 1; production baseline 22 lanes @t1086
  historical, 58 lanes exist). For every logged V the replay must reproduce it.

## S2 — TWO launch failures banked (both harness, ZERO clicks sent, verified)
- FAIL 1 (04:19:16): driver started with SYSTEM python3 -> died silently right
  after "dosbox pids alive" with no traceback surfaced in the log. ROOT CAUSE =
  the t283-banked trap: system python3 has NO PIL (grab() imports PIL inside the
  function). MEASURED: `python3 -c "import PIL"` -> ModuleNotFoundError;
  ~/tools/revenv/bin/python AND ~/.hermes/hermes-agent/venv/bin/python both have
  PIL 12.3.0. LAW: drive-class scripts must run under a PIL-bearing interpreter
  (use ~/tools/revenv/bin/python).
- FAIL 2 (04:31:00): launched with `~/tools/revenv/bin/python` but WITHOUT the
  T261_* env prefix -> module defaulted BASE to work/r1/t261-drive (the stale
  Nov-1 scratch ring, turn 1255) and printed "TARGET REACHED at ring turn 1255"
  immediately, zero presses, zero clicks. HONEST NOTE: this is the driver's
  max-press/target check behaving as designed on a stale BASE, not a bug, but the
  "TARGET REACHED" string on zero presses is a MISLEADING tell — future drive
  pre-flight must assert the logged ring turn == the production ring turn before
  believing any later TARGET line. The spurious bank work/r1/bank-t261-final-1255
  (copies of the stale scratch ring) was deleted; production ring re-verified
  turn 1086 after both failures (16-row tail census, all turn 1086, in_game True).
- DRIVER PATCH (keeper): drain_popups() now gated by new ring_in_game() — the
  t273 title-menu law is now ENFORCED IN CODE, not just documented. Guard logs
  "popup drain SKIPPED — ring not in_game". Screen check at 04:30: white-band px
  in the popup region at the current parked campaign = 32 (threshold 120, so no
  live popup; drain closes 0).

## S3 — THE DRIVE SELF-HARMED: Escape-AT-GALAXY -> TITLE MENU -> DRAIN CLICKS
##      "Load Game" -> A DIFFERENT CAMPAIGN ENTERED RAM (WITNESSED, MEASURED)
Drive log work/r1/playcap/drive_20261103-043353.log: presses 1-6 advanced
1086->1092 (real, ring-verified). Presses 7-8: NEXTTURN clicks at the MEASURED
(511,67) did NOT advance (watch.log holds t=1092, V=23, 26 systems 04:37:52 ->
04:39:15; drained=0 both — no popup on screen). SOFTLOCK-CLASS STRUCK (input-dead
clicks; fastest incidence on record: 6 presses). Then the driver's own probe +
old-style drain did the damage, fully reconstructed from banked screenshots:
- probe_a_043811.png (vision-verified): CAMPAIGN, turn 01092, bare galaxy map.
- driver sent ONE Escape (old input_alive). probe_b_043813.png (vision-verified):
  TITLE MENU ("Play Introduction / Tutorial / New Game / Return to Current Game /
  Load Game Alt-L / Save Game Alt-S / Exit to DOS"). LAW: ESCAPE AT THE BARE
  GALAXY MAP EXITS THE CAMPAIGN TO THE TITLE MENU. Escape is NOT inert.
- The probe's "ALIVE changed_px=306624" was the t266-banked FALSE POSITIVE
  (starfield animation), not evidence Escape worked — the ALIVE verdict then
  reset the stall counter and press 9 clicked NEXTTURN AT THE TITLE MENU.
- drain_popups at the title menu closed 2 clicks (press 9 drained=2). The
  ring_in_game() guard PASSED because the ring KEEPS AUTOSAVING the RAM campaign
  while at the title menu (watch rows stayed in_game=True the whole time) — a
  RING-BASED title-menu guard is STRUCTURALLY INSUFFICIENT; only the SCREEN
  distinguishes title menu from campaign. The 2 clicks land on the white title
  menu rows: "Load Game" then a save row -> THE GAME'S OWN LOAD LOADED A
  DIFFERENT CAMPAIGN INTO RAM.
- FINGERPRINT MEASUREMENT (scripts/r285_fp.py, keeper; md5 over sorted
  (planet-name, owner-byte) pairs via the r1_income_law locator; equality-only
  variant of the t266 fp law): pre-drive bank ALL 20 slots turn=1086 V=0
  owned=104 fp=3a189896; flip bank ALL 20 slots turn=1255 V=14 owned=124
  fp=39614c7c. NO interleave, NO oscillation — one clean swap. The loaded
  profile (t1255, V=14, mine_any=36 systems) EXACTLY matches the Nov-1
  "restored-t1255 lineage" that appeared in production RAM at 21:38 (t261/t266
  incident, fp e1d3bdc128 under t266's star-join hash).
- CONSEQUENCE FOR t261/t266 (major): the Nov-1 production flip t1111->t1255 at
  21:38:12 happened while drive_20261101-213051.log was ACTIVE with the OLD
  Escape-first input_alive. The mechanism t261 called "[unverified]" and t266
  attributed (for the RAM content) to a stray second dosbox is now WITNESSED in
  reproduction: driver Escape -> title menu -> drain clicks Load Game. The
  two-writer RING law stands for ring corruption; the RAM CAMPAIGN SWAP is
  driver self-harm via the title menu, not a second process. (Corroborate vs the
  Nov-1 log probe lines before shipping this claim — see next step.)
- Press 10 clicked NEXTTURN on the now-campaign t1254/5 screen -> advanced to
  1255 -> driver printed "TARGET REACHED" — a FALSE SUCCESS on MIXED LINEAGE.
  Corpus rows after 04:39:45 are the LOADED campaign, not the production t1086
  lineage. Rows 04:34-04:39 (~30 rows) are genuine production 1087-1092.
- PRODUCTION SURVIVES: RESUME.GAM md5 5b382afb (t1086) UNCHANGED (no in-game
  Save was clicked); bank-t285-predrive = full 20-slot t1086 production ring;
  bank-t285-flip1255 = the loaded campaign + the two probe screenshots.
- DRIVER PATCHES SHIPPED (this session, in scripts/r1_t261_drive.py):
  (1) drain gate ring_in_game() [insufficient alone, kept as cheap first line];
  (2) input_alive REWRITTEN Escape-last: 'c'-overlay FIRST (self-reverting,
      title-menu no-op), Escape ONLY as last resort AND gated by ring_in_game();
      docstring carries the witnessed screenshot law.
- TODO REMAINING: corroborate Nov-1 log; harvest legs on the real window;
  restore RAM to production t1086 via Return-to-Current-Game (two targeted
  clicks: Escape -> (318,333)) + fp-verify + bank; then finish sequence.
