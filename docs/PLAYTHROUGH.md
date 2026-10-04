# headless playthrough — contract evidence

Binary: `rewrite/build/ascendancy`. Model: docs/re/turnloop.md (verified/inferred
split + citations there). Victory condition names are the vendor `end-*.txt`
comments (docs/re/turnloop.md §1). All output below is real captured stdout
from the exact commands shown; re-run any of it to reproduce byte-identically
(determinism asserted by test `campaign_deterministic_same_seed`).

## Run A — headless, seed 2024: CONTROL victory on turn 51

```
$ ./rewrite/build/ascendancy --headless --campaign 600 --seed 2024
archives: 3 54 328 89  (.bin tables parsed: 7)
SDL 2.32.4 initialised (video driver: (null))
campaign seed=2024 stars=75 lanes=83 ai=6
turn   1 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn   2 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn   3 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn   4 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn   5 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn   6 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn   7 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn   8 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn   9 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn  10 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn  11 | player stars  2 score   3% techs  0 | ai stars 2 2 2 2 2 2
turn  12 | player stars  2 score   3% techs  0 | ai stars 2 2 2 2 2 2
turn  13 | player stars  2 score   3% techs  0 | ai stars 2 2 2 2 2 2
turn  14 | player stars  2 score   3% techs  0 | ai stars 2 2 2 2 2 2
turn  15 | player stars  2 score   3% techs  0 | ai stars 2 2 2 2 2 2
turn  16 | player stars  2 score   3% techs  0 | ai stars 2 2 2 2 2 2
turn  17 | player stars  2 score   3% techs  0 | ai stars 2 2 2 2 2 2
turn  18 | player stars  3 score   4% techs  0 | ai stars 3 3 3 3 3 3
turn  19 | player stars  3 score   4% techs  0 | ai stars 3 3 3 3 3 3
turn  20 | player stars  3 score   4% techs  1 | ai stars 3 3 3 3 3 3
turn  21 | player stars  3 score   4% techs  1 | ai stars 3 3 3 3 3 3
turn  22 | player stars  3 score   4% techs  1 | ai stars 3 3 3 3 3 3
turn  23 | player stars  3 score   4% techs  1 | ai stars 3 3 3 3 3 3
turn  24 | player stars  4 score   5% techs  1 | ai stars 4 4 4 4 4 4
turn  25 | player stars  4 score   5% techs  1 | ai stars 4 4 4 4 4 4
turn  26 | player stars  4 score   5% techs  1 | ai stars 4 4 4 4 4 4
turn  27 | player stars  4 score   5% techs  1 | ai stars 4 4 4 4 4 4
turn  28 | player stars  5 score   7% techs  1 | ai stars 5 5 5 5 5 5
turn  29 | player stars  5 score   7% techs  1 | ai stars 5 5 5 5 5 5
turn  30 | player stars  5 score   7% techs  1 | ai stars 5 5 5 5 5 5
turn  31 | player stars  5 score   7% techs  1 | ai stars 5 5 5 5 5 5
turn  32 | player stars  6 score   8% techs  1 | ai stars 6 6 6 6 6 6
turn  33 | player stars  6 score   8% techs  1 | ai stars 6 6 6 6 6 6
turn  34 | player stars  6 score   8% techs  1 | ai stars 6 6 6 6 6 6
turn  35 | player stars  7 score   9% techs  1 | ai stars 7 7 7 7 7 7
turn  36 | player stars  7 score   9% techs  1 | ai stars 9 7 7 7 7 5
turn  37 | player stars  8 score  11% techs  1 | ai stars 11 8 8 8 8 5
turn  38 | player stars 10 score  13% techs  1 | ai stars 14 8 8 8 6 2
turn  39 | player stars 12 score  16% techs  1 | ai stars 16 8 8 8 4 1
turn  40 | player stars 17 score  23% techs  2 | ai stars 17 9 9 9 0 0
turn  41 | player stars 18 score  24% techs  2 | ai stars 17 11 9 7 0 0
turn  42 | player stars 17 score  23% techs  2 | ai stars 18 13 10 8 0 0
turn  43 | player stars 14 score  19% techs  2 | ai stars 16 16 15 7 0 0
turn  44 | player stars 12 score  16% techs  2 | ai stars 15 19 19 5 0 0
turn  45 | player stars 10 score  13% techs  2 | ai stars 13 21 25 3 0 0
turn  46 | player stars 12 score  16% techs  2 | ai stars 7 21 29 4 0 0
turn  47 | player stars 15 score  20% techs  2 | ai stars 5 19 29 6 0 0
turn  48 | player stars 24 score  32% techs  2 | ai stars 4 11 31 4 0 0
turn  49 | player stars 29 score  39% techs  2 | ai stars 4 6 32 4 0 0
turn  50 | player stars 36 score  48% techs  2 | ai stars 2 3 27 7 0 0
turn  51 | player stars 41 score  55% techs  3 | ai stars 0 0 25 9 0 0
  [t11] owner 0 colonised Oslo
  [t11] owner 1 colonised Atropos
  [t11] owner 2 colonised Willy
  [t11] owner 3 colonised Intransigent
  [t11] owner 4 colonised Paragon
  [t11] owner 5 colonised Arvedui
  [t11] owner 6 colonised Parsimony
  [t18] owner 0 colonised Sirverei
  [t18] owner 1 colonised Hannibal
  [t18] owner 2 colonised Syntor
  [t18] owner 3 colonised Freblinsee
  [t18] owner 4 colonised Aglarond
  [t18] owner 5 colonised Verithil
  [t18] owner 6 colonised Ungridge
  [t20] owner 0 researched INFORMATION SYSTEMS
  [t20] owner 1 researched BIO RESEARCH
  [t20] owner 2 researched ION POWER
  [t20] owner 3 researched BIO RESEARCH
  [t20] owner 4 researched ION POWER
  [t20] owner 6 researched BIO RESEARCH
  [t24] owner 0 colonised Bindacia
  [t24] owner 1 colonised Vernunft
  [t24] owner 2 colonised Albireo
  [t24] owner 3 colonised Tonklinus
  [t24] owner 4 colonised Gasball
  [t24] owner 5 colonised Pindentry
  [t24] owner 6 colonised Xerxes
  [t28] owner 0 colonised Trovaricon
  [t28] owner 1 colonised Tonsberg
  [t28] owner 2 colonised Brilliance
  [t28] owner 3 colonised Gravitus
  [t28] owner 4 colonised Panacea
  [t28] owner 5 colonised Bob
  [t28] owner 6 colonised Alpheratz
  [t32] owner 0 colonised Pulveran
  [t32] owner 1 colonised Aquila
  [t32] owner 2 colonised Arcturus
  [t32] owner 3 colonised Sagitta
  [t32] owner 4 colonised Discordia
  [t32] owner 5 colonised Sarsaparilla
  [t32] owner 6 colonised Zoroaster
  [t35] owner 0 colonised Shlupp
  [t35] owner 1 colonised Stella
  [t35] owner 2 colonised Rhovid
  [t35] owner 3 colonised Cambria
  [t35] owner 4 colonised Flammifer
  [t35] owner 5 colonised Sentril
  [t35] owner 6 colonised Ignatius
  [t36] owner 1 captured Ignatius
  [t36] owner 1 captured Alpheratz
  [t37] owner 1 captured Zoroaster
  [t37] owner 0 colonised Lanesend
  [t37] owner 1 colonised Elwyssen
  [t37] owner 2 colonised Syzygifer
  [t37] owner 3 colonised Quercus
  [t37] owner 4 colonised Tensoric
  [t37] owner 5 colonised Icarus
  [t37] owner 6 colonised Masticon
  [t38] owner 1 captured Xerxes
  [t38] owner 0 captured Icarus
  [t38] owner 0 captured Sentril
  [t38] owner 1 captured Masticon
  [t38] owner 1 captured Ungridge
  [t39] owner 0 captured Sarsaparilla
  [t39] owner 0 captured Bob
  [t39] owner 1 captured Parsimony
  [t39] owner 1 colonised Highbeam
  [t40] owner 0 researched BIO RESEARCH
  [t40] owner 2 researched ORBITAL STRUCTURES
  [t40] owner 4 researched ORBITAL STRUCTURES
  [t40] owner 0 captured Verithil
  [t40] owner 0 captured Pindentry
  [t40] owner 1 captured Chloros
  [t40] owner 0 captured Stavern
  [t40] owner 0 captured Arvedui
  [t40] owner 0 colonised Ribulon
  [t40] owner 2 colonised Corpuscle
  [t40] owner 3 colonised Vega
  [t40] owner 4 colonised Almaviva
  [t41] owner 2 captured Almaviva
  [t41] owner 2 captured Discordia
  [t41] owner 0 colonised Smorgasbord
  [t42] owner 2 captured Flammifer
  [t42] owner 4 captured Smorgasbord
  [t42] owner 4 captured Shlupp
  [t42] owner 0 colonised Millitrin
  [t42] owner 1 colonised Algol
  [t42] owner 2 colonised Chippendale
  [t42] owner 3 colonised Gridsor
  [t43] owner 2 captured Tensoric
  [t43] owner 3 captured Algol
  [t43] owner 2 captured Panacea
  [t43] owner 2 captured Gasball
  [t43] owner 3 captured Pulveran
  [t43] owner 4 captured Sirverei
  [t43] owner 4 captured Millitrin
  [t43] owner 3 captured Bindacia
  [t43] owner 3 captured Highbeam
  [t43] owner 3 captured Masticon
  [t43] owner 0 colonised Fletcher
  [t43] owner 1 colonised Mira
  [t44] owner 3 captured Oslo
  [t44] owner 4 captured Zilker
  [t44] owner 3 captured Zoroaster
  [t44] owner 0 captured Shlupp
  [t44] owner 4 captured Fletcher
  [t44] owner 2 captured Paragon
  [t44] owner 3 captured Alpheratz
  [t44] owner 2 captured Terpsichore
  [t44] owner 2 captured Smorgasbord
  [t44] owner 1 colonised Crell
  [t44] owner 3 colonised Hope
  [t45] owner 3 captured Trovaricon
  [t45] owner 1 captured Ribulon
  [t45] owner 2 captured Aglarond
  [t45] owner 3 captured Ignatius
  [t45] owner 3 captured Elwyssen
  [t45] owner 3 captured Tonsberg
  [t45] owner 0 captured Sirverei
  [t45] owner 2 captured Millitrin
  [t45] owner 1 captured Icarus
  [t45] owner 3 captured Stella
  [t45] owner 3 colonised Amoroso
  [t45] owner 4 colonised Bodkin
  [t46] owner 4 captured Oslo
  [t46] owner 4 captured Bindacia
  [t46] owner 4 captured Pulveran
  [t46] owner 0 captured Zilker
  [t46] owner 3 captured Aquila
  [t46] owner 3 captured Xerxes
  [t46] owner 1 captured Sentril
  [t46] owner 3 captured Hannibal
  [t46] owner 2 captured Fletcher
  [t46] owner 3 captured Hurble
  [t46] owner 3 captured Vernunft
  [t46] owner 0 captured Smorgasbord
  [t46] owner 2 captured Bodkin
  [t46] owner 0 captured Tensoric
  [t46] owner 3 captured Ungridge
  [t46] owner 4 captured Gridsor
  [t46] owner 3 captured Atropos
  [t46] owner 3 colonised Pendulon
  [t47] owner 4 captured Trovaricon
  [t47] owner 1 captured Sarsaparilla
  [t47] owner 1 captured Bob
  [t47] owner 0 captured Icarus
  [t47] owner 0 captured Ribulon
  [t47] owner 0 captured Flammifer
  [t47] owner 3 captured Parsimony
  [t47] owner 0 captured Millitrin
  [t47] owner 0 captured Crell
  [t47] owner 4 captured Hope
  [t47] owner 3 colonised Phoebe
  [t48] owner 0 captured Oslo
  [t48] owner 0 captured Bindacia
  [t48] owner 0 captured Mira
  [t48] owner 0 captured Pulveran
  [t48] owner 1 captured Pindentry
  [t48] owner 3 captured Chippendale
  [t48] owner 0 captured Discordia
  [t48] owner 0 captured Sentril
  [t48] owner 3 captured Chloros
  [t48] owner 0 captured Panacea
  [t48] owner 0 captured Fletcher
  [t48] owner 0 captured Gasball
  [t48] owner 4 captured Vega
  [t48] owner 3 captured Syzygifer
  [t48] owner 4 captured Amoroso
  [t48] owner 0 captured Bodkin
  [t48] owner 0 captured Gridsor
  [t48] owner 3 captured Rhovid
  [t48] owner 1 captured Arvedui
  [t49] owner 0 captured Trovaricon
  [t49] owner 1 captured Verithil
  [t49] owner 0 captured Sarsaparilla
  [t49] owner 4 captured Pendulon
  [t49] owner 0 captured Bob
  [t49] owner 3 captured Arcturus
  [t49] owner 0 captured Almaviva
  [t49] owner 1 captured Stavern
  [t49] owner 0 captured Paragon
  [t49] owner 0 captured Terpsichore
  [t49] owner 4 captured Quercus
  [t49] owner 0 captured Hope
  [t49] owner 3 captured Corpuscle
  [t49] owner 3 captured Syntor
  [t49] owner 2 colonised Synthos
  [t50] owner 0 captured Aglarond
  [t50] owner 4 captured Phoebe
  [t50] owner 0 captured Pindentry
  [t50] owner 4 captured Chippendale
  [t50] owner 4 captured Cambria
  [t50] owner 0 captured Vega
  [t50] owner 4 captured Synthos
  [t50] owner 0 captured Amoroso
  [t50] owner 4 captured Gravitus
  [t50] owner 3 captured Philadelphia
  [t50] owner 0 captured Chloros
  [t50] owner 0 captured Arvedui
  [t50] owner 0 captured Parsimony
  [t51] owner 0 researched ION POWER
  [t51] owner 0 captured Verithil
  [t51] owner 0 captured Pendulon
  [t51] owner 3 captured Almaviva
  [t51] owner 4 captured Brilliance
  [t51] owner 0 captured Ungridge
  [t51] owner 3 captured Willy
  [t51] owner 0 captured Stavern
  [t51] owner 0 captured Xerxes
  [t51] owner 4 captured Syzygifer
  [t51] owner 4 captured Tonklinus
  [t51] owner 3 captured Albireo
  [t51] owner 0 captured Quercus
  [t51] owner 0 captured Alpheratz
  [t51] owner 4 captured Rhovid
  [t51] owner 3 captured Discordia
  [t51] VICTORY: Control (end-ctrl.txt)
VICTORY Control via end-ctrl.txt on turn 51 (score 55%)
```

## Run B — headless, seed 42: player EXTINCT on turn 55 (end-xtnc reachable too)

```
$ ./rewrite/build/ascendancy --headless --campaign 600 --seed 42
archives: 3 54 328 89  (.bin tables parsed: 7)
SDL 2.32.4 initialised (video driver: (null))
campaign seed=42 stars=75 lanes=82 ai=6
turn   1 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn   2 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn   3 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn   4 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn   5 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
  ... (47 more turns)
turn  53 | player stars  4 score   5% techs  3 | ai stars 0 0 67 0 0 0
turn  54 | player stars  2 score   3% techs  3 | ai stars 0 0 69 0 0 0
turn  55 | player stars  0 score   0% techs  3 | ai stars 0 0 71 0 0 0
  [t55] VICTORY: Extinct (end-xtnc.txt)
VICTORY Extinct via end-xtnc.txt on turn 55 (score 0%)
```

## Run C — Xvfb/X11, seed 13: CONTROL victory on turn 50 (boot contract path)

```
$ xvfb-run -a ./rewrite/build/ascendancy --campaign 600 --seed 13
archives: 3 54 328 89  (.bin tables parsed: 7)
SDL 2.32.4 initialised (video driver: x11)
campaign seed=13 stars=75 lanes=83 ai=6
turn   1 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn   2 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn   3 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn   4 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
turn   5 | player stars  1 score   1% techs  0 | ai stars 1 1 1 1 1 1
  ... (42 more turns)
turn  48 | player stars 26 score  35% techs  2 | ai stars 5 0 0 0 0 35
turn  49 | player stars 35 score  47% techs  3 | ai stars 0 0 0 0 0 32
turn  50 | player stars 51 score  68% techs  3 | ai stars 0 0 0 0 0 17
  [t50] VICTORY: Control (end-ctrl.txt)
VICTORY Control via end-ctrl.txt on turn 50 (score 68%)
```

## What this shows / does not show

- SHOWS: seeded turn loop advances; every system in the loop (mapgen,
  economy, research, production via items, expansion, combat-capture,
  diplomacy war table) mutates state each turn; BOTH vendor victory
  conditions (end-ctrl control-share, end-xtnc extinction) fire on real
  runs; same seed => byte-identical trace; boots under Xvfb x11 driver.
- DOES NOT SHOW: original combat arithmetic (OQ-010 — capture model is
  documented-inferred), alliance-victory end-unit / home-world-capture
  end-capt (need R1 accept/capture bookkeeping), original AI build order,
  graphics/audio. Those remain open items in docs/OPEN-QUESTIONS.md.
