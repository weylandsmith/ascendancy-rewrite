# UI runtime — layout anchors and the P5a scope [anchors verified; rest stated]

Implementation: `rewrite/src/ui/ui.{h,cpp}` (SDL2 + SDL2_ttf), driven from
`main.cpp` by `--ui [--campaign N] [--seed S] [--autoplay]`. Gate 4c boots it
under Xvfb. This file separates the geometry taken verbatim from
`extracted/ascend00/windows.txt` from the documented defaults the P5a pass
needs to be functional. Line numbers below are on the CRSTRIPped file
(`tr -d '\r'`) — re-check with that filter before citing.

## 1. Verified anchors (windows.txt line numbers, cr-stripped)

- `COSMOSWnd` (line 200): TYPE 2, PARENT NONE, rect X0 7 Y0 7 **X1 465
  Y1 472**; keys STAR_SHAPES `DATA\COS_STAR.SHP`, SHIP_SHAPES
  `DATA\COS_SHIP.SHP`, NUM_STARS 100, NUM_LANES 100, BACKGRNDCOLOR 0;
  HELPINDEX `coswnd`. The 100x100 pair is the cosmos window's display
  capacity (docs/re/ui.md), NOT a map-size option (corrected in STATE).
- `NEXTTURN` (line 540): PARENT NONE, rect **474,52 — 548,82**,
  MOUSEFOCUS 1, SENDMESSAGE 7, HELPINDEX `1next1`. It lives OUTSIDE the
  COSMOSWnd rect — the original HUD is a right-hand rail beside the map.
- Child controls under COSMOSWnd (PARENT COSMOSWnd at lines 225,242,...):
  ROTRIGHT/ROTLEFT/ROTUP/ROTDOWN, ZOOMIN/ZOOMOUT, TOGLANES/TOGEMPIRE/
  TOGSHIPS/TOGCOLONIES — the cosmos map supports pan, zoom, and four layer
  toggles. P5a implements none of them (recorded below), so pan/zoom are not
  silently half-faked.
- Global display keys: cX0 7 cY0 7 cX1 327 cY1 274 (one-off control rect),
  FONTS 300, SMALLFONT/LARGEFONT point at `DATA\SMFONT.FNT`/`BIGFONT.FNT`.

## 2. Display mode

The original ran 640x480x8 (FLIC intro measured, docs/re/media.md). The
rewrite opens a 640x480 window and maps star coordinates (generator grid
1024x1024, mapgen.md §4) into the COSMOSWnd rect; scaling that way is a
[documented default]. NO original .shp sprites are drawn: the pixel codec is
OQ-005 and fabricating lookalike sprites is banned (STATE rule). Stars are
filled circles (r=4 owner fill, r=6 white ring when selected-free), lanes are
lines — shape vocabulary is a placeholder until OQ-005.

## 3. Text

Vendor faces are LIVE since 2026-10-05f: the UI renders with the game's own
`DATA\SMFONT.FNT` / `DATA\BIGFONT.FNT` (windows.txt:30-32 mapping) decoded per
docs/re/fnt.md — 1 byte per pixel, 0xFF background, solid 0xF3 ink, advance ==
width. `VendorText` in ui.cpp packs each face into one white-with-alpha atlas
tinted per draw call (`SDL_SetTextureColorMod`); sm/big ink is binary
[verified corpus-wide] so no intensity ramp is invented. Face load failure is
a hard error (broken data tree), never a silent fallback. SDL2_ttf and the
LiberationSans substitute are removed from the build. The earlier state of
this section ("vendor faces NOT decodable") described pre-OQ-017 reality and
is kept only here as history.

## 4. Colour

BACKGRNDCOLOR 0 [verified key] references palette index 0 of the .haz tables
(docs/re/ui.md §2 lists the 23); the .haz->semantic mapping is undocumented,
so P5a ships a documented substitute: background rgb(16,16,24), lanes
rgb(120,120,120), event text white, seven owner colours + neutral from
`ui/layout.cpp` (`kOwnerRgb`). User constraint: never encode meaning in
colour alone. Implementation (searched, not hand-picked; min hue spread
45 deg):

- Owner pairs: perceived (deuteranopia-SIMULATED) luminance gap >= 32, OR
  simulated chroma distance >= 90 with perceived gap >= 12.
- Neutral rgb(40,40,40) also draws at radius 2 vs 4 — ownership is coded by
  SIZE redundantly, so its rule accepts chroma-only separation.
- LESSON (2026-10-04, caught by its own unit test): a ladder built on RAW
  luminance still collided under simulation (raw-blue vs raw-cyan perceived
  gap 1.6). All separability math must run on the simulated colours;
  `simulateDeuteranopia()` is shared between layout.cpp and the test so they
  cannot drift.
- VERIFIED ON RENDERED PIXELS (screenshot of a live Xvfb run, pixel clusters
  read back): 0/42 owner-pair checks fail under BOTH deuteranopia and
  protanopia transforms (the first palette was deuteranopia-only: a
  protanopia transform clashed on 4 pairs, so the set was re-searched to
  pass both, min hue spread 45 deg).

## 5. Input model

- Mouse click inside the NEXTTURN rect (verified, §1) or Enter/Space advances
  one turn (the original SENDMESSAGE 7 semantics are exe-side; "next turn"
  is the documented meaning of the vendor NAME itself).
- Left-click on an owned/neutral star selects it and the status line shows
  name + planets + owner — read-only inspection.
- ESC or window close quits. `--autoplay` advances every 250 ms for
  recording/screenshots; `--ui --campaign N` exits 0 printing `ui ok: turn N`
  after N turns (gate 4c).
- Every accepted action prints one line (`ui click next-turn`,
  `ui click map (x,y) -> Star`, `ui key next`) so automation can verify real
  input WITHOUT reading pixels.
- Synthetic-input facts [verified 2026-10-04 on this host]: no xdotool /
  libXtst-dev / python-xlib exist, so gate 4c-b uses `tools/xsend` (raw
  libX11). SDL2 DOES accept XSendEvent Button events, but re-reads the
  pointer position for them — synthetic coords alone arrived as (320,240);
  XWarpPointer + XSync before the send makes coordinates exact
  (`ui click map (140,160) -> Burphee`). WM-less Xvfb: SDL_CreateWindow's
  WM_NAME is set and findable via XQueryTree + XFetchName.

## 6. Explicitly NOT in P5a (no fakery)

pan/zoom/layer toggles (children exist in windows.txt but their exe
behaviour is unverified), the 132-window chrome (SHAPEFRAME frames need
OQ-005), audio mixing of headerless rates (OQ-006), save/load (OQ-003).
Vendor fonts were on this list until OQ-017 closed (§3). Each remaining item
is a listed open question, not a silent omission.
