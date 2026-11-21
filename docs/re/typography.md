# Vendor TYPOGRAPHY LAW (tA3, PHASE-17 Stage A row 3)

Hand-authored (no probe regenerates this file; docs/re/text.md is a
different, generated file). Every measurement is script-witnessed; full
working detail + fit tables: docs/re/_wip_tA3.md. Witness:
scripts/r1_tA3_capture.sh + scripts/r1_tA3_witness.py. Pins:
rewrite/tests/test_textlaw_tA3.cpp (+ test_titletext_t392.cpp for the
title), mutation campaign scripts/r1_ta3_mutate.py. Faces/codec:
docs/re/fnt.md (gate 3p).

## 1. Faces [verified from the .fnt containers]

- smfont h=8: cap ink rows 0..6 (7 rows), descenders 2..7.
- bigfont h=11: cap ink rows 0..9 (10 rows), descenders 3..10.
- advance == width, no side bearings; ink alphabet exactly {0xF3}
  (solid faces). Caps draw-TOP = ink-top (cap ink begins at cell row 0).

## 2. FONT-FIELD LAW: every TEXTITEM face field renders BIG

All 18 TEXTITEMs carry face field 0, 2, or 3. Measured decisive at
sites of all three fields:

| field | site                       | evidence |
|-------|----------------------------|----------|
| 3     | title singles (t392)       | hint ink span 27 == bigfont no-gutter 28 (sm 22 refuted) |
| 2     | title hints, newgame control labels | "Star Density" big fit 0.815-0.85 vs sm 0.21-0.30; "Alt-L" span (t392) |
| 0     | rail labels                | 11-row ink bands + per-glyph extents == bigfont exactly (sm 7-row caps refuted); fit iou 1.000 vs sm 0.24-0.37 on the palette-exact map refcap |

smfont IS used — for body text (newgame lore block: 8-row bands, 'the'
sm fit 0.63 > big 0.47).

## 3. Baseline + placement law

- TEXTITEM sites: draw TOP = rect.y0 + dy VERBATIM (map refcap rail
  dy=2 hit EXACTLY under root = window + 40); draw x: rail labels cell
  origin x0+2 ('S' cell 476 in rect 474; bigfont 'S' inks at cell
  column 1); centred sites cell x = (x0+x1)/2 - adv/2 (integer div —
  NOT (x0+x1+1)/2; fits 5/6 measured exactly, all within 1px).
- Capture drift law [banked]: browser shots drift per-window (newgame
  +1 on three independent labels; galaxymap -1 on three rails). Never
  derive a law constant from one browser row; the palette-exact refcap
  or multi-site agreement is the law.
- Athens 512x384 shots are NEVER pixel-scale evidence (D19/G5).

## 4. Site table (screen coords; newgame rows under crop law screen = image-1)

| site | face | draw | ink |
|------|------|------|-----|
| rail labels (5) | BIG | x0+2, y0+2 | (255,255,255) |
| control labels Star Density/Species/Atmosphere | BIG | centred, y0+10 | (255,255,255) |
| Player Color label | BIG | centred, y0+12 | (255,255,255) |
| species name (green) | BIG | centred NEWGAMEWND, top 17 | (0,142,69) family |
| "Player Species" header | BIG | centred RACELIST, top 15 | (255,255,255) |
| summary block (3 lines) | BIG | centred x 170, tops 326/339/352 pitch 13 | (255,255,255) |
| lore block | SM | centred kLoreBox, top 265 pitch 11 | (0,142,69) |
| Begin New Game label | BIG | centred panel 502..632, top 455 | (255,255,255) |
| title buttons | BIG | y0+8 single / y0+4+y0+18 pair (t392) | (215,215,215) title palette |

Colour classes [measured]: the map refcap (palette-exact) rail core is
exactly (255,255,255) (260 px); browser-shot cores are also (255,255,255)
with blended edges (225,227,229)/(164,171,177) — the CORE is the class.
Title white is the TITLE palette's (215,215,215) (t392 band-closure:
inside a button rect only fill (0,0,8) + ink (215,215,215) exist) — do
not unify the two whites.
