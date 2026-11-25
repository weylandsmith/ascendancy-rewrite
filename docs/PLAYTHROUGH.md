# Headless playthrough record

Regenerated 2026-11-25T01:07:29-05:00 by scripts/record_playthrough.sh from the
current binary. Victory conditions and their vendor files: docs/re/turnloop.md §1.

## Run A — headless, seed 2024 (t295 home draw: Extinct t285 — uniform homes put real lethal neighbours on the player; the old spread-BFS never could)

```
$ ./rewrite/build/ascendancy --headless --campaign 1600 --seed 2024
archives: 3 54 328 89  (.bin tables parsed: 7)
SDL 2.32.4 initialised (video driver: (null))
campaign seed=2024 stars=50 lanes=53 ai=6
turn   1 | player stars  1 score   2% techs  3 | ai stars 1 1 1 1 1 1
turn   2 | player stars  1 score   2% techs  3 | ai stars 1 1 1 1 1 1
  ... (331 lines elided)
  [t302] owner 6 captured Algol
  [t303] owner 6 captured Cambria
  [t303] VICTORY: Extinct (end-xtnc.txt)
VICTORY Extinct via end-xtnc.txt on turn 303 (score 0%)
```

## Run B — headless, seed 23 (Control exemplar t1406 under the t295 home draw; t291's seed-1 exemplar re-drew to Extinct t266)

```
$ ./rewrite/build/ascendancy --headless --campaign 1600 --seed 23
archives: 3 54 328 89  (.bin tables parsed: 7)
SDL 2.32.4 initialised (video driver: (null))
campaign seed=23 stars=50 lanes=53 ai=6
turn   1 | player stars  1 score   2% techs  3 | ai stars 1 1 1 1 1 1
turn   2 | player stars  1 score   2% techs  3 | ai stars 1 1 1 1 1 1
  ... (1722 lines elided)
  [t1583] owner 0 colonised Bob
  [t1583] Shared star-lane intelligence with FLUDENTRI (2 lanes)
  [t1583] VICTORY: Control (end-ctrl.txt)
VICTORY Control via end-ctrl.txt on turn 1583 (score 68%)
```

## Run C — Xvfb/X11, seed 13

```
$ xvfb-run -a ./rewrite/build/ascendancy --campaign 1600 --seed 13
archives: 3 54 328 89  (.bin tables parsed: 7)
SDL 2.32.4 initialised (video driver: x11)
campaign seed=13 stars=50 lanes=53 ai=6
turn   1 | player stars  1 score   2% techs  3 | ai stars 1 1 1 1 1 1
turn   2 | player stars  1 score   2% techs  3 | ai stars 1 1 1 1 1 1
  ... (539 lines elided)
  [t486] owner 5 captured Menthol
  [t486] owner 4 captured Ajax
  [t486] VICTORY: Extinct (end-xtnc.txt)
VICTORY Extinct via end-xtnc.txt on turn 486 (score 0%)
```

## Run D — UI under Xvfb, autoplay 3 turns (gate 4c)

```
$ xvfb-run -a ./rewrite/build/ascendancy --ui --campaign 3 --autoplay --seed 9
archives: 3 54 328 89  (.bin tables parsed: 7)
SDL 2.32.4 initialised (video driver: x11)
ui ok: turn 3
```

## Run E — audio boot (gate 4d): all 86 vendor SFX + theme00 via SDL2_mixer

```
$ SDL_AUDIODRIVER=dummy xvfb-run -a ./rewrite/build/ascendancy --ui --audio --campaign 1 --autoplay --seed 4
archives: 3 54 328 89  (.bin tables parsed: 7)
SDL 2.32.4 initialised (video driver: x11)
audio ok: 86 sfx chunks, music 8191719 B
ui ok: turn 1
```

## Run F — injected X input drives a real turn (gate 4c-b)

```
$ ./rewrite/build/ascendancy --ui --campaign 1 --seed 5 &
$ ./tools/xsend "Ascendancy" 510 66   # NEXT TURN button rect
archives: 3 54 328 89  (.bin tables parsed: 7)
SDL 2.32.4 initialised (video driver: x11)
ui click next-turn
ui ok: turn 1
```
No --autoplay in F: the ONLY way the turn count advances is the injected click.

## What this shows / does not show

- SHOWS: seeded turn loop advances; mapgen, economy, research, production
  (planitem items incl. Shipyard), ship launch (gated on Shipyard +
  researched drive, docs/re/ships.md), combat-capture, diplomacy war
  table, victory files end-ctrl/end-xtnc both fire on real runs; same
  seed => byte-identical trace; boots under Xvfb x11; UI takes real
  injected input; audio loads every vendor sample.
- DOES NOT SHOW: original combat arithmetic (OQ-010 — capture model is
  documented-inferred), alliance-victory end-unit / home-world-capture
  end-capt (need R1 accept/capture bookkeeping), original AI build order,
  original sprites (OQ-005) and font (OQ-017), headerless sample-rate
  ground truth (OQ-006). Those stay open in docs/OPEN-QUESTIONS.md.
