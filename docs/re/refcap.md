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
  (no emulator at gate time; the dir is UNTRACKED vendor-copyright media —
  self-captured from your own copy via `scripts/refcap_gate.sh`, so the
  stage self-skips when absent). Title-menu control + three movie shots
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

## 4. Golden-save tour [verified by capture, 2026-10-05e]

"Return to Current Game" (title button 4; root (318,373) -> window (318,333))
loads `resume.gam` straight from the scratch root — gameplay screens are
reachable WITHOUT R1, one click from boot. Captures pinned:

- `docs/assets/refcap/original-strategic-map.png` — cosmos view: green turn
  counter reads `00069`; sidebar = Planets / Ships / Research / Special
  Ability / Species + 2x3 command wheel.
- `docs/assets/refcap/original-planet-view.png` — header "Minions (1 Planet
  Occupied, 1 System Controlled)"; "Xerxes I (Enormous Supermineral Planet)",
  "No Project". The strings assemble from the vendor pools EXACTLY as
  modelled: `Xerxes` = names.txt line 32 and present in resume.gam at
  0x2146 (30-byte field); `Enormous` = static.txt size list, `Supermineral`
  = static.txt type list (ids 164/172 region). Species name comes from the
  dip/history pool, not the save — corroborates OQ-004 string-pool reading.
- `docs/assets/refcap/original-species-research.png` — research dialog title
  "Minions Knowledge" = static.txt line 354 `"%s Knowledge %s"` with %s =
  species display name [verified first instance]; three empty tech rings for
  the specnum-0 (Minions, SA_SuperMarines) ability screen.

OQ-003 NARROWING (first-pass readings were WRONG twice — alignment and a
mislabelled offset; exact bytes recorded instead of interpretation):
turn counter 69 appears EXACTLY ONCE in resume.gam as LE u32, and only
UNALIGNED at byte 62290 (0 hits at every 4-aligned offset) — not a plain
aligned field. Planet record: `Xerxes` at 0x2146; raw bytes name+12..+24 =
`00 00 00 00 7F C2 1F 00 A1 C4 1F 00 E5 C8 1F 00` -> three ASCENDING
u3s 0x001FC27F, 0x001FC4A1, 0x001FC8E5 (gaps 0x222 then 0x444 — NOT equal
spacing; second gap is exactly 2x the first) —
plausibly flat-model pointers (≈2 MB, far beyond the 81,647 B file) which
would need the R1 runtime base to confirm; +30 region is zeros then 0x30000.
Meaning still open.

Coordinate law for future pilots: import screenshots are ROOT coords;
tools/xsend takes WINDOW coords = root - 40 (window sits at +0+40, 640x480
mode after the 640x400 title screen). Every pilot miss this session came
from mixing these two frames.

## 5. What this proves, honestly

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
here, not in code. Gameplay screens ARE reachable (the golden save loads
with one click — §4), but pixel-exact comparison of THOSE screens against
the port additionally needs the .shp codec (OQ-005); the string/label
layer of map/planet views is verified (§4).
