# t386 WIP — TITLE ART IDENTITY (the "dinosaur-looking guy")

Started 2026-11-14 (fresh session). Task: STATE.md NEXT ACTION t386.
Instrument rule (phase 10): no self-graded vision of OUR renders; cited
geometry + palette-law sampling + decode hashes + honest negatives. The
pinned VENDOR screenshot docs/assets/refcap/original-title-menu.png is the
external-grader artifact (user is the grader; refcap.md 4f) — reading it is
in scope, reading our own renders is not.

## 0. Structural facts measured THIS iteration

### 0.1 0opening.gif is a real, complete, single-frame 640x480 image [verified]
`extracted/ascend01/data/0opening.gif`, 45,092 B, md5 e2c5fb66a57595fc550bbb90cc8a0952.
Hand-walked GIF87a (byte offsets): magic `GIF87a` @0; LSD 640x480, packed
0xd7 -> GCT present, 256 entries @13..780, bgcolor 0; @781 ONE Image
Descriptor, rect (0,0)-(639,480), packed 0x00 (no LCT, not interlaced),
LZW min-code 8, 174 sub-blocks, 44,124 B payload; trailer 0x3b @45091.
=> exactly ONE frame, full-screen. Not an animation, not a stub.
- (measurement trap banked: my first hand-walk read packed 0xe0 because I
  started the descriptor one byte late — always anchor the walk at 13+3*(2<<(packed&7)).)
- PIL decodes the plane (640x480 P); my stdlib-only GIF-LZW desyncs at
  output index 6096 (code 368/next 369 then 743/512) — REPORTED, not used as
  data. ffmpeg's pal8 plane comes back 308,224 B (1024 B of extra data per
  frame), so it is not directly comparable. Plane instrument = PIL.

### 0.2 The exe NAMES 0OPENING.GIF from the startup cluster [verified, prior bank]
docs/re/datafiles.md §2 "Media:" line: `DATA\0OPENING.GIF (referrers in the
0x2183x startup cluster)`; also in the 26 DATA\ path templates
(docs/re/loader.md §5, alongside `data\logo.gif`, `scr%03d.gif`, `game.pal`).
The vendor opens the GIF by name at boot — independent of windows.txt.

### 0.3 windows.txt says the opening CHROME is 0opening.SHP state 0 [verified]
windows.txt L34-36 (TYPE=100 block immediately before the seven menu
buttons): `TYPE 100 / STATENUMBER 0 / SHAPEFILE DATA\0OPENING.SHP`.
Button windows (L38+) all carry `SHAPEFRAME -1` (no per-button shape).

### 0.4 0opening.shp is BUTTON STRIPS ONLY — it cannot be the figure [verified]
Documented container (docs/re/shp.md §1, 208/208 files: magic "1.10", u32
count, table 8*(N+1)) parsed THIS iteration:
  0opening.shp  7,223 B, N=7, record dims (318,0) + SIX x (30,318); zero
  records >= 150x150. 318/319 x 30/31 is exactly the menu-button rect
  (159,Y)-(477,Y+30). => the SHP library holds the button/menu STRIP SET,
  not a full-screen figure. The dinosaur is NOT in 0opening.shp.

### 0.5 Chamachies lead (D9) measured — race art cannot compose it [verified]
Chamachies = specnum 19 (docs/re/species.md roster row 19 SA_FreeResearch;
docs/re/ai-data.md 'race19.dip | Diplomacy text for Chamachies').
  lgrace19.shp (ascend02) 51,416 B, N=1, record header (296,0), 0 records >=200x200
  smrace19.shp (ascend01)  7,653 B, N=1, record header (49,0)
  lgrace19.shp is ABSENT from ascend01.
A 51 KB single-record library and a 49-px sprite cannot compose a 640x480
title figure. The Chamachies hypothesis is NOT supported by the asset
inventory; the figure's colour family in the vendor shot is brown/gold/tan,
which is what the title GIF itself is drawn in (§0.7).

### 0.6 Palette-membership law is BLIND at the title screen [verified, honest negative]
scripts/t386_colour_witness.py (same law as refcap_match.py: bit-exact d0,
far d4 dist^2>96, 1-in-3 grid): every candidate scores IDENTICALLY d0=9.2%
against the vendor title shot — 0opening.gif GCT(256), GIF used indices(53),
game.pal(256), logo.pal(256), subfont.pal(16), logic.flc union, intro65a
union (d4 differs: 66.9/72.7/73.4/73.1/73.8 vs intro65a 3.8%). The only
exactly-shared colour is black; the shot's dominant colours
([215,138,56] x8135, [0,0,8], [85,44,4], [203,130,52], ...) are NEAR misses
(nearest d2 64..750) in every palette. So "whose palette is the title drawn
in" CANNOT discriminate candidates — the shot is a re-coloured/quantised
render. (Also refutes using the banked 30.5% title-menu number as an
identity test; it only separates movie-vs-menu.)

### 0.7 The GIF is full-bleed art with a reserved BLACK MENU PANEL [verified]
scripts/t386_title_art.py: index plane 307,200 B, sha256[:16] 85310df45be96aeb,
palette sha256[:16] aa78b73219b6cbe9, 53 distinct indices used of 256,
non-background density 0.9996 (background index = 0), content spans the full
x-extent 0..600+. Luminance sketch (64x45 cells, luminance ramp — no colour
encoding) shows: art fills rows 0..19, and from row ~19 down there is a
VERTICAL BLACK BAND at columns ~32..46 (x ~320..460) running to the bottom —
i.e. the GIF reserves a dark rectangle where the menu is drawn.
Frame-identity test vs both vendor movies: EXACT index-plane match count = 0
(1144 intro65a frames + 226 logic.flc frames scanned). The GIF is NOT a movie
frame.

### 0.8 Vendor screenshot read (EXTERNAL GRADER artifact, pinned refcap pin) [verified-as-read]
Vision read of docs/assets/refcap/original-title-menu.png (640x480):
top-centre = large reptilian/reptile HEAD, scaly, brown/gold/tan, one small
bright red eye; below it the word "ASCENDANCY" in stylised serif,
orange-gold gradient with dark outline; a dark blue-to-black menu panel with
light-blue border containing white labels (read: Play Introduction, Tutorial,
New Game, Return to Current Game, Load Game Alt-L, Save Game Alt-S — six;
Exit to DOS below the crop, matching the D9 seven-button law); background =
rendered alien landscape, hazy orange-yellow sky, brown rock formations.
Native geometry measured from the pixels: light-row bands (40,243) then text
rows at 251-257, 313, 353, 393, 433, 473 => 40 px pitch == windows.txt
button pitch (step 40); the dark panel occupies x ~352..484.
The GIF's own black panel sits at x ~320..460 (width ~140 vs shot ~132).
=> same composition, TRANSLATED. scripts/t386_remap_test.py pixel-wise
single-valued map test at zero shift: only 4/53 GIF indices map to one shot
colour => zero-shift identity is REFUTED; the translation is what remains.
