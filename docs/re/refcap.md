# Reference capture — the ORIGINAL game under dosbox-x, compared to the port

Closes the last non-R1 subitem of P5 ("dosbox screenshot comparison — needs a
reference capture harness"). Captures are real: `ascend.exe` boots in
dosbox-x 2025.02.01 under Xvfb and is driven by synthetic input.

## 1. Harness [verified by execution]

- `scripts/ref_capture.sh` — builds the scratch copy (`work/r1/game`, NEVER
  a mount of `game/`; same rule as `r1_attempt.sh`), generates a conf with
  `[sdl] output=x11` (key + value verbatim in the dosbox-x generated conf
  `~/.config/dosbox-x/dosbox-x-2025.02.01.conf:82`), boots
  `ASCEND.EXE` headless-of-sound (`nosound=true`), stdin=/dev/null,
  `-time-limit` bounded (flag verified in `dosbox-x -help` output),
  screenshots the Xvfb root with ImageMagick `import` at fixed intervals.
  Kill ONLY via `pkill -x dosbox-x` (STATE.md invariant).
- Geometry [measured]: window title
  `"DOSBox-X 2025.02.01: ASCEND - 100%"` sits at root +0+40; the title
  screen is 640x400 centred in the 480-tall window, so ROOT row = emulator
  row + 40. Title menu buttons (root coords, band centres from pixel
  measurement): Play Introduction y=252, Tutorial y=293, New Game y=333,
  Return y=373, Load y=413, Save y=453, x=318. A click at window-relative
  (318, 212) = root (318, 252) starts the intro movie. A first attempt at
  root y hit Tutorial (one band low) — caught by vision-checking the
  capture, not by assuming.
- `scripts/refcap_gate.sh` — end-to-end: capture run, then score the
  pre-click shot as NOT-movie and every post-click shot as movie. Exit 0
  = all directions as expected. Last real run: title 9.2% / movie shots
  97.3–100.0% -> PASS.
- The gate (stage 4f) scores FOUR PINNED shots in `docs/assets/refcap/`
  (no emulator at gate time): title-menu control + three movie shots
  (starfield, caption+starfield, galaxy+caption). Pinned sha256:
  title c0eb3958…, movie 1660fb89…, caption 5713330b…, galaxy e73587e6…

## 2. What the original's movie path does [measured from captures]

The game does NOT blit intro65a 1:1. It composites each frame into a
letterboxed band (~root x 32..608, y 240..452; bbox measured per shot) and
draws its own caption text under the band ("OF THREE HUNDRED BILLION
STARS.", "THIS GALAXY CONSISTS" — vision-read off captures). The captions
are NOT in the FLIC: all 1144 decoded frames have ZERO content pixels in
rows 400..480 (measured), and the strings appear in no extracted file
(grep, all of extracted/).

## 3. The comparison law and why the alternatives died [measured]

`scripts/refcap_match.py` — T1: fraction of sampled screenshot colours
(3-px grid, whole window) that are BIT-EXACT members of the intro65a union
palette over all 1144 frames (719 colours), plus the far fraction
(dist^2 > 96). PASS iff exact >= 0.85 and far < 0.02.
Measured exact/far: movie shots 90.6–100.0% / <=0.8%; title menu 30.5% /
33.9% (pilot run) and 9.2% / 3.8% (gate run) — the title screen varies
between runs/seconds (cause not investigated); tutorial menu 11.1% / 2.3%.
Every non-movie measurement is far below the movie population; thresholds
sit in the gap, not at a data point.

Refuted alternatives (do not re-try without new evidence):

1. 1:1 blit row-exact search at every offset: the first version looked like
   0.64 PASS but was BLACK-ROW DOMINANCE — uniform rows match trivially
   across any pair of dark images; the content-aware version scores 0
   matching rows on every shot (the game scales the movie). [refuted]
2. control palette = logic.flc union: VACUOUS — both vendor videos share
   the engine palette; identical 99.5% scores on the same movie shot.
   The live control is the in-run menu shot obeying the law's negation.
   [refuted]
3. bbox-normalised luminance signature vs all 1144 frames (find WHICH
   frame): best 8.9 vs median 23.9 MAD; top candidates temporally
   scattered (286, 621, 3) — the mostly-black intro gives too little
   signal per frame and the caption strip pollutes the bbox. Fine-grained
   frame identity on the original's movie path is NOT achievable this way.
   Script kept at work/refcap/bbox_match.py (negative-result tooling).

## 4. What this proves, honestly

Chain: original's on-screen movie pixels obey the exact palette law of the
intro65a decode (T1) while non-movie screens (menu controls) do not
(in-run control, measured) -> the original is displaying this FLIC file's
content, unmodified palette-wise -> the same decode is golden-pinned to
`rewrite/src/formats/flic.cpp` (flc_intro_golden, all 1144 frame hashes)
-> gate 4e proved the port's on-screen render is pixel-exact vs that
decode. Therefore: original movie == reference decode == port render, on
identical screenshot machinery. What it does NOT prove: the original's
composite geometry (scale, band rect) or its caption text — port geometry
differences in the movie presentation remain cosmetic and are recorded
here, not in code. Gameplay-screen comparison (map/planet views) remains
R1 territory (save state to reach them reproducibly = OQ-003); the menu is
state-free, which is exactly why it was chosen as the control.
