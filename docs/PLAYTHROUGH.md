# Headless playthrough record

Regenerated 2026-10-26T16:28:18-04:00 by scripts/record_playthrough.sh from the
current binary. Victory conditions and their vendor files: docs/re/turnloop.md §1.

## Run A — headless, seed 2024

```
$ ./rewrite/build/ascendancy --headless --campaign 1200 --seed 2024
archives: 3 54 328 89  (.bin tables parsed: 7)
SDL 2.32.4 initialised (video driver: (null))
campaign seed=2024 stars=50 lanes=53 ai=6
turn   1 | player stars  1 score   2% techs  3 | ai stars 1 1 1 1 1 1
turn   2 | player stars  1 score   2% techs  3 | ai stars 1 1 1 1 1 1
  ... (869 lines elided)
  [t776] owner 0 colonised Xerxes
  [t777] owner 0 colonised Arcturus
  [t777] VICTORY: Control (end-ctrl.txt)
VICTORY Control via end-ctrl.txt on turn 777 (score 52%)
```

## Run B — headless, seed 42

```
$ ./rewrite/build/ascendancy --headless --campaign 1200 --seed 42
archives: 3 54 328 89  (.bin tables parsed: 7)
SDL 2.32.4 initialised (video driver: (null))
campaign seed=42 stars=50 lanes=53 ai=6
turn   1 | player stars  1 score   2% techs  3 | ai stars 1 1 1 1 1 1
turn   2 | player stars  1 score   2% techs  3 | ai stars 1 1 1 1 1 1
  ... (671 lines elided)
  [t581] owner 3 captured Arcturus
  [t581] owner 3 captured Feculon
  [t581] VICTORY: Extinct (end-xtnc.txt)
VICTORY Extinct via end-xtnc.txt on turn 581 (score 0%)
```

## Run C — Xvfb/X11, seed 13

```
$ xvfb-run -a ./rewrite/build/ascendancy --campaign 1200 --seed 13
archives: 3 54 328 89  (.bin tables parsed: 7)
SDL 2.32.4 initialised (video driver: x11)
campaign seed=13 stars=50 lanes=53 ai=6
turn   1 | player stars  1 score   2% techs  3 | ai stars 1 1 1 1 1 1
turn   2 | player stars  1 score   2% techs  3 | ai stars 1 1 1 1 1 1
  ... (601 lines elided)
  [t503] owner 4 captured Delphinius
  [t503] owner 4 captured Phoebe
  [t503] VICTORY: Extinct (end-xtnc.txt)
VICTORY Extinct via end-xtnc.txt on turn 503 (score 0%)
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
audio ok: 85 sfx chunks, music 8191719 B
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
