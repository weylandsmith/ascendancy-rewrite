# Palette law (t398) — DATA\game.pal IS the in-game palette; the title keeps its own

Hand-authored (grep-verified: no script or gate stage writes this file).
Session evidence trail: docs/re/_wip_t398.md S0..S6.

## 1. The file and who loads it [verified]
- `extracted/ascend01/data/game.pal` — 768 B = 256 RGB triples, every channel
  byte <= 0x3f (6-bit VGA DAC; max = 63). media.md §6 has the shape census.
- The exe names it verbatim, NUL-delimited, at TWO payload sites:
  `work/ascend_payload.bin` 0x83579 (`DATA\game.pal`, in the corn.cpp
  title/init cluster beside `resume.gam`, `GIF SCRATCH`, `DATA\0OPENING.GIF`)
  and 0x84207 (`DATA\game.pal`, flicwin/font cluster beside `FONT
  TRANSLATE`). loader.md §5 lists it among the DATA\ load templates.
- `logo.pal` pairs with `data\logo.gif` (site 0x834c6) — the logo path, NOT
  chrome. `subfont.pal` (48 B, 16 entries) belongs to the subfont path.

## 2. The conversion [measured law, t189b + t398]
DOSBox converts 6->8 bit as `c = (v<<2)|(v>>4)` (saturating low-bit refill).
Raw 6-bit values render everything at 25% brightness (t189b player verdict
"all too dark"); `v*4` differs from the law at every v>=16 (e.g. 16 -> 65 vs
64) and is pinned wrong-vs-right in test_gamepal_t398.cpp.

## 3. Membership law [verified, three pinned shots]
Every pixel of the three pinned in-game refcap shots lies inside the
converted table (docs/assets/refcap/, self-captured vendor runs):
  original-strategic-map.png    307200/307200 (logo.pal-conv 75.43%)
  original-species-research.png 307200/307200 (logo.pal-conv 90.53%)
  original-planet-view.png      307200/307200 (logo.pal-conv 82.06%)
The title screen lies inside it at 8.79% only — the title is a DIFFERENT
palette (the t386 TSV, title-art.md §4). The old boot.md seam prose
("no cited palette exists for the menu .shp libs") conflated the TITLE
refutation with the chrome question; the chrome was never tested before t398.

## 4. Registration law [verified]
Rendering the 1starmap rail records through the converted table and sliding
over the rail band of the pinned strategic-map shot (game coords = root rows
- 40, refcap.md §1), colour-match (mean |RGB diff| over painted px):
  k5 44x27 mean 3  at (585,130) 97% px within 12  (Status row, y exact)
  k4 44x23 mean 6  at (585,175) 93%               (Fleet row)
  k3 43x22 mean 6  at (584,213) 93%               (Research row)
  k7 45x30 mean 36 at (585,248) 64%               (Ability row; y exact — the
      Intelligence row's fill overlaps its lower half, degradation expected)
Icon x = 584/585 = RIGHT of the label (vendor geometry; our port paints at
rr.x+4 — the D11 "wrong side" complaint, t400 scope, NOT the palette law).
The rail fill teal (12,32,48) == converted idx 242 exact.

## 5. Code law (rewrite)
- `rewrite/src/formats/gamepal.{h,cpp}` (ascend_core): GamePalette —
  load/parse 768 B refuse-not-clamp, conversion table, rgb()/argb() (index
  wraps &0xff, alpha forced 255).
- `blitShape` (vendortext.cpp) colours through GamePalette when loaded; the
  t387 luminance ramp survives ONLY as the documented degradation when the
  file is absent, announced once by
  `ui palette: <err> (degraded: greyscale ramp)`; success prints
  `ui palette: game.pal (256 entries, 6->8 bit)`. loadChromePalette is
  once-per-process (title + campaign loops both call; silent-degrade law:
  never aborts).
- Title art (0opening.gif via the t386 TSV) is UNCHANGED — §3 refutes
  game.pal for the title.

## 6. Witness + pins
- scripts/t398_palette_witness.sh (Xvfb :97 tour title/load/newgame/map) +
  scripts/t398_witness_census.py VERDICT PASS: palette line present; rail
  icon zone (x474..540, our placement) 131 chromatic colours, 130 inside
  game.pal; the single outside colour is (40,40,56) = the port's OWN rail
  fill (t264 choice, not art). The ramp path yields EXACTLY 0 chromatic
  pixels — the census mechanically separates the paths (self-graded vision
  untouched, R13-safe).
- Degraded witness (scratch data root minus game.pal, archives present):
  boot prints the named degraded line and still reaches the title
  (`ui title art ok`, exit clean). Never mounts game/.
- Pins test_gamepal_t398.cpp x4 (shape+conversion triples incl. the v=16
  right-vs-v*4 discriminator + whole-table FNV 0xe366ecb79ed61fc2; argb
  layout incl. wrap; refuse-not-clamp sizes; title-colours-NOT-in-table
  refutation half). MUTATION 3/3 CAUGHT: conv->v*4 (5 named fails),
  argb-alpha-removed, size-gate-><3 (4 named fails); clean revert 322/0.
- Screenshots for USER look-grading (D11 re-test):
  work/r1/loop/t398-{title,load,newgame,map}.png.

## 7. Residues (named, none blocking)
- Frame->button icon identity: registration matched k3/k4/k5/k7 by POSITION
  and palette; whether the vendor Ships row paints k4 (or another frame)
  stays t400 (SHAPEITEM lines cite Research/Fleet/Status/Ability per
  hudlayout.cpp; the shot's Ships icon shows ship silhouettes per vision —
  k4's content match is unconfirmed).
- The t387 ramp is dead code when data is present; kept deliberately as the
  data-less-clone path (publish law: builds+runs without vendor data).
- 7racesel/3cfgnew per-record colour verification rides on t401 (same
  palette law, per-screen witnesses).
