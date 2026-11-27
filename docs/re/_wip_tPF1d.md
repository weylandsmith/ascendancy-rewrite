# tPF-1d — QUIT-CAUSE INSTRUMENT + CHAMACHI-EXACT SOAK (D31 steering)

STATUS: in progress (2026-11-27).

## Framing (D31, authoritative)
- 9472ac2 / R-tPF1c "Escape at the bottom explains the day-20 exit" is
  REFUTED by user testimony ("mouse never moved from the next day button").
  Third refutation of a closure that explained user behavior away — D30 law:
  close user-reported defects only by REPRODUCTION + FIX, never by
  attributing the symptom to the user.
- Day-20 exit = UNREPRODUCED defect, OPEN. This iteration ships the
  self-diagnosing instrument: every exit path prints its CAUSE before
  "ui ok: turn N", so the user's own next run names the path.
- Then an honest soak at the user-exact config (Begin-built, Chamachi home).
  If the soak survives, SAY SO — do not invent a user-behavior explanation.

## Code facts [verified this session]
- Exit paths in runCampaignUi (rewrite/src/ui/ui.cpp), the ONLY quit=true
  sites (grep census): :684 doEscape else-branch (shared by keyboard Escape
  :703 and corner "Exit <ESC>" popup click :800), :695 SDL_QUIT, :720
  Alt-L load screen kLoadQuit, :1617 harness turn cap (capFired), :1619
  camp.over(). Final print :3775 "ui ok: turn %d".
- Victory enum: campaign.h:33 {None, Control, Captured, Unification,
  Extinct, LastAlive}; victoryName() campaign.cpp:103 (pinned strings).
- Chamachi = specnum 19 (campaign.cpp:211 comment + tPL-D1 law: home ALWAYS
  size idx 3 / 45 cells). --species 19 (main.cpp:99) forces the player
  species at build time => Chamachi-home is law-guaranteed, NO seed reroll
  needed (STATE's "reroll until Chamachi" satisfied by construction).
- Begin wheel triple (menulaw.h:344 NewGameSettings) carries NO species
  field — the in-UI species RING pick reaches only the intro print
  (title.cpp:1393), not the play state. NOTED (separate question; the user's
  launch `--data ROOT --ui` has no --species, so the port's play species is
  the build default, whatever the ring showed. Banked, not chased here.)
- Prior soak scripts: scripts/tPF1c_repro.sh (user flags, factory order,
  45 presses, per-press 'ui click next-turn' assertion, pgrep liveness),
  scripts/tPF1c_escape_test.sh (escape injection). tPF1d soak derives from
  the repro script + --species 19 + 'no quit line' assertion.

## Design
- ui.cpp: `const char* quitCause` beside `bool quit`; every quit=true site
  assigns its cause first (guarded `if (!quit)` where a later check could
  otherwise overwrite: cap/victory). doEscape gains a cause param so the
  keyboard leg and the corner-click leg name different causes.
- Causes: "victory:<ENUM>" (via victoryName), "harness-turn-cap",
  "sdl-window-close", "escape-key-at-bottom", "corner-exit-click",
  "load-screen-quit", fallback "unknown".
- Print "ui quit cause=%s turn=%d" immediately BEFORE "ui ok: turn %d"
  (D31 ordering), single occurrence, console-only, zero gameplay change.
- Pins (test_quitcause_tPF1d.cpp, source-scan pattern of
  test_timecontrols_tPF1): (1) cause print precedes ui-ok print + single
  occurrence; (2) every named cause string present at its path (5 paths);
  (3) victory cause built from victoryName(camp.victory()) — enum named,
  not hardcoded.
- Runtime witnesses: (A) cap witness — --campaign 2 Begin flow, 2 presses,
  expect 'ui quit cause=harness-turn-cap' BEFORE 'ui ok: turn 2'.
  - (B) tPF1d soak — Chamachi, 45 presses, per-press assertion, then
    grep -c 'ui quit cause' == 0 AND alive.

  ## Witnesses
  - (A) CAP WITNESS [PASS 2026-11-27, scripts/tPF1d_cap_witness.sh]:
    --campaign 2 Begin flow, 2 presses => log lines 29-31:
    'ui quit cause=harness-turn-cap turn=2' THEN 'ui ok: turn 2' THEN
    'HARNESS-CAP: ...'. Ordering + cause name confirmed at RUNTIME.
  - (C) ESCAPE WITNESS [PASS 2026-11-27, scripts/tPF1c_escape_test.sh re-run
    on the instrumented HEAD binary]: 20 presses + map-Escape =>
    'ui quit cause=escape-key-at-bottom turn=20' THEN 'ui ok: turn 20'.
    The instrument distinguishes the two candidate paths at runtime.

## CHAMACHI-EXACT SOAK RESULT [measured 2026-11-27]
- scripts/tPF1d_soak.sh: user flags (--data ROOT --ui, NO --campaign, seed
  default 1, Begin wheel defaults 50/5/1) + --species 19 (Chamachies).
  Witnesses: 'newgame live stars 50 owners 5 gov 1'; home size idx 3
  (= Chamachi class per tPL-D1, so Chamachi-home BY CONSTRUCTION); factory
  order placed ('ordered armed cell 10'); 45/45 presses each logged
  'ui click next-turn'; ZERO VICTORY / ui quit cause / ui ok lines; app
  alive at teardown. VERDICT: SOAK SURVIVED.
- HONEST NEGATIVE (D31): the day-20 exit did NOT reproduce at the closest
  config the port can express. The instrument stays in; the user's own run
  now names the path if it ever fires. NO user-behavior theory is offered.
- SOAK NAV FIX: order-phase return-to-map needs TWO escapes (Planet
  Display -> Planets -> map per t410 unwind); the tPF1c_repro.sh single-
  escape nav grep 'Planets -> map' happened to pass there because its
  escape loop differs — the soak loops with per-press screen-line
  assertions (max 3).

## BANKED SEPARATELY (not chased this iteration)
- Begin species ring -> play state GAP: the ring pick reaches ONLY the race
  intro print (title.cpp:1393 'species-pick'; soak log line 20 shows pick
  0 while --species 19 forced the play species). NewGameSettings
  (menulaw.h:344) carries stars/owners/gov but NO species field, so a
  Begin-built port game plays the build-default species whatever the ring
  showed. The user's 'started a game with the Chamachies' (D-row 693) means
  the ring pick MUST reach play state — a real port defect, queue candidate
  behind tESC-1.

## MUTATION CAMPAIGN [scripts/tPF1d_mutate.sh, all RESTORE md5-verified]
- M1 victory cause loses victoryName() -> CAUGHT (names_enum pin :88/:89).
- M2 cause print swapped AFTER ui ok -> CAUGHT (before_ui_ok pin :42).
- M3 sdl-window-close leg neutered -> CAUGHT (census :67 + named-path :69).
- AFTER-RESTORE md5 28db198795767d0f21e25c8bb1f50af2, suite 605/0/0.

  ## Result log
  - Suite 602 -> 605/0/0 (3 new source-scan pins, test_quitcause_tPF1d.cpp;
    census pins quits==5 / quitCause==6 assignments — re-derived from grep -c
    after a first-pass wrong count).
  - ui.cpp edits: quitCause std::string (victory leg composes "victory:<E>"
    — a .c_str() on the temporary dangles; fixed); doEscape(const char*) so
    keyboard vs corner-click legs distinguish; victory leg guarded `&& !quit`
    (cap cause can never be stolen); cause print BEFORE ui-ok, single site.
