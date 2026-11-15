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

### 2a. Planet-panel selection LAWS are landed (t199)

While the SPRITES stay blocked, the cited level->record selection math from
docs/re/planets-ui.md S3/S4 is implemented and pinned as pure no-SDL code:
`ui::gaugeSelector` (clamp0..20(round(L^0.75)), IND/RES words +0x44/+0x46),
`ui::prosSelector` (identity clamp, +0x48) and
`game::Campaign::popBands/popBandsFor` (SEL(i)=1+[i>=used]+[i>=pop] over
i<cap, ten per row) — tests `layout_planet_gauge_selector_law_t199` and
`campaign_pop_band_law_t199`. When OQ-005 unblocks drawing, the planet panel
feeds these selectors to ShapeLibrary record indices directly; no law work
remains on that screen.

### 2b. Pop-panel LANDED as code (t263, 2026-11-02)

The population panel's full visualization law now lives in
`src/ui/poppanel.{h,cpp}` (no SDL; pinned by 4 tests `poppanel_*_t263`, 141
total 0 fail): selector->record is IDENTITY on 17np.shp (t254 selector table
9/9), the pitch grid is (i%10)*10 x (i/10)*10 from a widget-local origin
(asm 0x3ceed/0x3cef6, PLPOP rect windows.txt:1587 = 100x100 px = exactly 10
rows x 10 slots x 10 px — and `storedCapFor`'s clamp to 100 equals that
capacity, so the paint cannot overflow the panel), rows = ceil(cap/10), and
`popSlotLibraryConforms` gates the library on the t254 census (9 records;
k1 9x9 busy sideways-red + blue tool, k2 7x9 free front-yellow zero-blue,
k3 8x8 hollow ring — the icon<->role pixel binding is pinned, and swapping
k1/k2 measurably fails the suite). gwshare slot law pinned too: cache slot ==
0-based index among NON-BLANK lines (entry #44 = 17np, #41 = 14intel control).
Working log docs/re/_wip_t263.md. Drawing itself stays OQ-005-scoped.

### 2c. HUD rail + ship-design tabs LANDED as code (t264, 2026-11-02)

The t252/t253 measurements (§6a/§6c) plus a fresh primary-source re-parse
of windows.txt/gizmos.txt (docs/re/_wip_t264.md S1/S2) are now code + pins
in `src/ui/hudlayout.{h,cpp}` (pure, no SDL; 146 tests 0 fail, +5
`hud_*_t264`; CMake wires it into ascend_ui AND run_tests):

- `kRail[6]` — the six x-band-474 controls with verbatim rect +
  (SENDMESSAGE, SENDPARAM1): STATUS 474,130-632,160 (1,10), FLEET
  474,169-632,199 (1,18), RESEARCH 474,208-632,238 (1,20), SPECIALAB
  474,247-632,277 (5,0), RACES 474,286-632,316 (1,7), Intelligence
  474,303-632,333 (1,14). `railButtonFor(Pt)` is the inclusive hit map; the
  14 px RACES/Intelligence overlap resolves to Intelligence ([inferred]
  z-order — the file gives no draw order; pinned as law). NEW fact beyond
  the dossier: SENDPARAM1 == target STATE number holds for all four
  window-openers (10/18/20/14 = STATUSWND/FLEETWND/RESWIN/INTELSCREEN).
- `sidebarIcon()` — the SHAPEITEM law: 1starmap.shp frames 3=Research
  4=Ships 5=Planets 7=Special; RACES (WINITEMS 1) and Intelligence
  (WINITEMS 0) return nullopt — buttons WITHOUT icons are representable.
  Drawing the shapes stays OQ-005-scoped (ui-runtime.md §2 unchanged).
- `gizmoCatForShipTab()` — THE TABLE, 6/6 (51->0 52->1 54->2 53->3 55->4
  57->5; HULL 50 -> -1; msg 56 -> -1) with `shipTabForGizmoCat()` inverse
  and `gizmoListForTab()` == `game::gizmosByCategory` (file-order law,
  gizmos.txt categories contiguous 0..5, counts 10/6/5/6/5/44 of 76).
  Non-derivability is pinned combinatorially: the naive rule cat==msg-51
  holds ONLY for 51/52/55 — deviations EXACTLY {53,54,57} (t253's swapped
  pair plus the msg-56 gap at SPECIAL; a stronger witness than the
  dossier's prose). Mutation probe this session: flipping 53->2 in the
  module fails 11 checks across 3 tests, then reverting restores green.

Honest scope: no OQ closed (strict-close — wiring cited law; 005/016/019/
021 stay open); no sprite is drawn anywhere (ui.cpp untouched); the
overlap-z-order and the SENDPARAM1-law generalization carry [inferred].

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

## 6a. LIVE SCREEN SWEEP 1 dossier (t252, 2026-11-01, display :9 turn 1255)

Harness: scripts/r1_t252_screen.py (click/key + root screenshot + 640x480 crop
at root offset (80,100) + pixel-diff vs previous step + ring turn check; run
with the hermes venv python — PIL is only there). Screens:
work/screens/t252/. Baseline verified healthy galaxy screen, ring turn 1255,
zero turn drift across every step of this sweep (NEXTTURN never clicked).

Sidebar geometry CONFIRMED from windows.txt (game coords == window-rel, t245
law) and matched by live clicks at rect CENTERS:
- STATUS "Planets" 474,130-632,160; FLEET "Ships" 474,169-632,199;
  RESEARCH 474,208-632,238; SPECIALAB "Special Ability" 474,247-632,277;
  Intelligence 474,303-632,333 (STATE '1 7' — hidden until Species menu?);
  RACES 474,286-632,316 "Species" (help 1races: "access the Species menu,
  where you can contact other species or access the Intelligence Screen").
- Each button is WINITEMS 2: TEXTITEM 0 + SHAPEITEM 1 from data\1starmap.shp
  (icon frames 3=Research, 4=Ships, 5=Planets, 7=Special) — the sidebar icons
  are 1starmap.shp records, a concrete lead for OQ-005 identification.
- [t388 CORRECTION] the RACES/Intelligence 14-px overlap does NOT need a
  z-order rule: the STATE field is an id-LIST ("<count> <id>..." — the count
  equals the number of ids in 123/123 records) and Intelligence's list is
  "1 7" — active in the species menu ONLY, never on the map. t264's
  [inferred] last-hit z-order reading is superseded by ui/statuslaw.h.

RESEARCH SCREEN (RESWIN TYPE 9, rect 7,46-476,472, help reswin; children
RESROTLEFT 524,442-539,472 msg 50, RESROTRIGHT 540,442-554,472 msg 51,
RESMOVEUP 563,442-593,457 msg 52, RESMOVEDOWN 563,458-593,472 msg 53):
- Click RESEARCH center (553,223) opened it, 93688 px diff vs galaxy, ring
  unmoved. Header renders "Chamachies Knowledge" (race name + " Knowledge").
- LAYOUT IS A NODE GRAPH, not a list: tech nodes = circles connected by lines
  on black; discovered node renders blue-outlined, current project gold/brown.
  Right info panel: "Current Project:" + tech icon + name ("Accel Energy
  Replenishment") + "(15 days)" + "Allows" + unlock name ("Lush Growth Bomb")
  + its icon. => the original shows ETA in DAYS and the unlock list per tech
  — same two-number law as the t244 gauge popup, now on RESWIN.
- Pan widgets CONFIRMED BY PIXEL-DIFF: click (570,455) (RESMOVEUP/DOWN column
  center) changed 472 px confined to bbox x 552-593 y 222-469 — i.e. the MINIMAP
  column, not the main field; second click changed 0 px (viewport already at
  the map edge / same position). The pan buttons themselves draw as minimap
  insets with red-white double arrows (vision, z_research_arrows.png).
- NEGSCREEN (320,0-639,479) + ALIENDIP (336,215-632,316) + PLAYERDIP
  (336,325-632,472): NOT reachable from the galaxy sidebar directly — help
  1races routes diplomacy through the Species menu (RACES button). See 6b.

## 6b. Species menu, NEGSCREEN negotiation, INTELLIGENCE (t252 cont.)

PATH MAP (measured, ring turn 1255 held through every step, zero drift):
- RACES "Species" (553,301) from galaxy -> SPECIES MENU: right sidebar renders
  "3 of 3 Species Known" + race rows (Orfa/Ungooma/Extinct, race-colored
  names + flag icons) + home-nebula viewport + "Intelligence" item; the
  galaxy map stays visible and four large race portraits overlay the map
  (vision). Escape returns to galaxy (back2 vs baseline diff = 161 px, just
  cursor/star blink noise).
- Clicking a race row (Orfa row at y~93) opens NEGSCREEN: right half of the
  screen replaces the sidebar. [t287 CORRECTION: row y's are campaign-state
  dependent — fresh t1086 campaign rows measured y 61/100/139 (pitch ~39);
  ALWAYS re-measure bands per sitting. The third row prints "Extinct"
  (= eliminated race, help.txt:775 contact-refused; clicking it only
  highlights, never opens NEGSCREEN — diplomacy.md §21.3). Menu clicks MUST
  go through scripts/r287_vncinput.py (XTEST motion; xsend warped clicks
  fire the stale hovered row — diplomacy.md §21.5).] Layout VERIFIED against windows.txt rects by
  pixel-band analysis (bright-text row detection, z_dip_full.png):
  ALIENDIP 336,215-632,316 = alien portrait band + ONE text line (bright band
  y 252-262); PLAYERDIP 336,325-632,472 = player option list (three option
  bands measured at y 329-339, 358-367, 387-396 — ~29 px row pitch); the
  region ABOVE ALIENDIP (y 40-206) is image content (the Third Party / cosdip
  miniature-galaxy region per help tinyrace/cosdip).
- Option set rendered at war-adjacent posture: "Goodbye. I trust we'll speak
  again." / "We declare war on you. Prepare to die." / "We propose an alliance
  between our peoples." — the emitter menu is posture-dependent (the Ungooma
  greeting "How can we little %m help you?" is DR_NoDipResponse in
  race11.dip:173 verbatim, i.e. dialogue lines come from the raceNN.dip
  DR_* sections with %m/%y species-name substitution [verified file match]).
- SAFETY: clicked option #1 (Goodbye) at (480,334) — first row center computed
  from the measured band. Negotiation CLOSED, returned to the species menu,
  zero turn drift, no war declared, no proposal sent. NEVER click option rows
  2/3 (declare-war/alliance) without explicit user sign-off.
- "Intelligence" item (553,311) opens INTELSCREEN (7,7-632,34 header) +
  INTELLIST (7,46-632,472): header "Chamachies Intelligence"; rows = every
  known species incl. SELF; columns Fleet/Colonies/Discoveries rendered as
  RELATIVE symbol counts (triangles/squares-or-circles/diamonds, race-colored)
  — help intscr verbatim: "symbols represent relative magnitude rather than
  specific sizes"; relation flags at row right (help: "species flags ...
  indicate the diplomatic relations"). Observed: Chamachies 10/12/6, Orfa
  8/8/4, Ungooma 6/6/5 [vision-read, unverified counts — R13 pitfall: trust
  generated numbers, and none exist here; treat as posture, not data].
- OQ-005 LEAD (not a closure): sidebar buttons embed SHAPEITEM records from
  data\1starmap.shp (frames 3=Research 4=Ships 5=Planets 7=Special), NEGSCREEN
  window-class art = DATA\13NEGOT.SHP, RESWIN era art = DATA\20RES.SHP, ship
  design = DATA\8SHIPDES.SHP, opening = DATA\0OPENING.SHP, race select =
  DATA\7RACESEL.SHP (windows.txt SHAPEFILE keys, 9 total). Identification of
  specific records against these live screens is the sanctioned W3 eyeball
  route once the codec exists; the codec itself stays blocked (R2).

## 6c. LIVE SCREEN SWEEP 2 dossier: FLEETWND + ship design (t253, 2026-11-01, :9 turn 1255)

Harness scripts/r1_t253_screen.py (t252 primitive, OUT -> work/screens/t253/;
run with ~/.hermes/hermes-agent/venv/bin/python — PIL lives only there). Ring
turn HELD 1255 through all 20 steps; NEXTTURN never clicked; no war, no
proposal, nothing sold or dismissed. Working notes docs/re/_wip_t253.md.

FLEETWND (TYPE 17, STATE "1 18", rect 7,7-632,472, help fleetwin) opened by
sidebar FLEET "Ships" 474,169-632,199 (SENDMESSAGE 1 / SENDPARAM1 18 — the
param IS the target window's STATE number, same shape as RESEARCH p1 20 ==
RESWIN STATE 1 20; measured click at rect centre, 116404 px diff).
- Header renders `<owner> (<N> Ships, <M> more allowed)` — vision read
  "Chamachies (25 Ships, 12 more allowed)". The allowance is shown as
  HEADROOM, the live form of help shipdes' "number of ships you can maintain
  is proportional to the number of star systems you control".
- STATSHIPLST (child, rect 7,46-632,472) pages 4 rows for 25 ships via the
  right-rail scroll pair, MEASURED by blue-pixel detection at centres
  (620,63) and (620,453) (bands y 59-68 / 450-457, x 606-635).
- Row columns: ship render | NAME (green) | gizmo/cargo icons | chevron chain |
  column of blue spheres | LOCATION (cyan). Location forms observed:
  "Orbiting <Planet>" and "In Starlane to <System> System ETA - <N> Days" —
  ETA in DAYS, the third screen with that unit law (RESWIN t252, t244 gauges).
- BEHAVIOUR LAWS CONFIRMED end-to-end (help fleetwin verbatim): LEFT-CLICK a
  row (200,93) JUMPED to that ship's location (orbital view, red shield sphere,
  109479 px, ring unmoved) and Escape returned to the LIST; RIGHT-CLICK a row
  (tools/xsend `click3`) opened the ship contents display.
- Escape unwinds ONE level (fleet list <- design screen; galaxy <- fleet list).
  Parked back on the galaxy screen: 3471 px vs baseline == t252's 3452 blink
  noise floor.

THE SHIP CONTENTS DISPLAY IS THE SHIPDESSCREEN WINDOW CLASS (geometric
identification): measured panel edges x 6/7, 307-330, 477-484, 633-634 and y
2/4, 96-111, 283, 337-342, 473-477; the tab grid occupies x 478-639 y 0-81,
i.e. windows.txt's tab rects 485,7-632,76 + GIZLIST from y 86. Panels: ship
identity `Chamachies "Sparrowhawk"` + 3 spheres + 3 bars | selected-item detail
(name + large render) | tab grid (3 tiles row 1, 4 tiles row 2) | equipped-slot
column | cargo band | GIZLIST (name + icon rows, scroll arrows for 44-item cat).

TAB -> GIZMO-CATEGORY MAP, MEASURED 6/6 EXACT against gizmos.txt (cr-stripped)
category field and FILE ORDER (one tab per step; each category-tab press
redrew 17.8k-185k px incl. the GIZLIST):
  WEAPONS(msg 51)=cat0 weapons (Mass Barrage Gun, Fourier Missiles, Quantum
  Singularity Launcher, Molecular Disassociator, Electromagnetic Pulser,
  Plasmatron...); DEFENSES(52)=cat1 shields (Ion Wrap, Concussion Shield, Wave
  Scatterer, Deactotron, Hyperwave Nullifier, Nanoshell); ENGINES(54)=cat2
  drives (Tonklin Motor, Ion Banger, Graviton Projector, Inertia Negator,
  Nanowave Space Bender); SENSORS(53)=cat3 scanners (Tonklin Frequency
  Analyzer, Subspace Phase Array, Aural Cloud Constructor, Hyperwave Tympanum,
  Murgatroyd's Knower, Nanowave Decoupling Net); ENERGY(55)=cat4 generators
  (Proton Shaver, Subatomic Scoop, Quark Express, Van Crees Hypersplicer,
  Nanotwirler); SPECIAL(57)=cat5 specials (Lane Blocker, Molecular Tie Down,
  Intellect Scrambler, Brunswik Dissipator, Recaller, Disarmer, +scroll).
- THE MAP IS NOT THE MESSAGE ORDER: ENGINES(msg 54)=cat2 while
  SENSORS(msg 53)=cat3 — the middle pair is swapped, msg 56 belongs to no tab.
  A rewrite that derives category from message number or tab index is WRONG;
  it must carry this table. Independently corroborates ships.md §6's category
  dispatch (cat4 generator -> +0x66 = POWER) without Ghidra.
- HULL (msg 50, SHAPEFRAME 3) is NOT a gizmo category: pressing it changed
  1973 px confined to bbox x 524-632 y 7-76 (tab rows only; GIZLIST starts
  y 86, changed 0 px, selected name stayed "Lane Blocker"). Every tab press
  repaints the grid so the pressed tile draws darker. Consistent with help
  hull ("select a different hull size... larger hulls provide more space,
  are more durable, take longer to build"); STATE "1 8" has no other child
  window, so where the size choices render is UNPROVEN (noted, not claimed).
  windows.txt has SEVEN tabs, not eight — the "8" in 8SHIPDES.SHP is the
  library's name-table index prefix.
- gizmos.txt IS the vendor gizmo table: my parse = 76 records (cat 0:10, 1:6,
  2:5, 3:6, 4:5, 5:44), matching combat.md S2's runtime census (76 rows at
  0x7650c stride 0x6a, names Mass Barrage Gun..Hyperfuel).
- OQ-005 ANCHOR (annotation, row STAYS OPEN): SHAPEFRAME pins the tab tiles to
  8SHIPDES.SHP frames 2=WEAPONS 3=HULL 4=DEFENSES 5=ENGINES 6=SENSORS 7=ENERGY
  8=SPECIAL (GIZLIST frame 7, SHIPDESSCREEN frame 0), and the live art in grid
  order is explosion / ship silhouette / blue orb | green crystal / magenta
  vortex / gold cylinder / pink beam-with-green-tip — seven frames with pinned
  semantic roles for the W3 eyeball route. Codec itself stays R2-blocked.
- SPELLING DISCIPLINE: live renders read "Van Crees"/"Brunswick" where
  gizmos.txt says "Van^Creeg"/"Brunswik" (vision is the noisiest instrument —
  R13). The FILE is the data authority; do not edit files toward a projector
  read.

HAZARD (control-plane, banked in _wip_t253.md): an ORPHANED
`xmessage -buttons Yes:1,No:0 -default Yes` "Quit DOSBox-X warning" (PID
461872, PPID 1, started Oct 31 19:40 — 14 h before the current dosbox PID
479968) sat MAPPED on :9 with Yes as default. `xwininfo -root -tree | grep -i
warning` is the pre-sweep check; xsend's "REFUSING blocker window" line warns
about a DIFFERENT window and still sends to the game window. Killed the orphan
by PID only.

## 6d. LIVE SCREEN SWEEP 3 dossier: NEGSCREEN flow, INTELLIGENCE depth, RESWIN dossiers (t268, 2026-11-02, :9 turn 1236)

Harness scripts/r1_t268_screen.py (t253 primitive, OUT -> work/screens/t268/).
Pre-flight r1_game_health.py RC=0 (game 535172, watcher 535187, ring fresh);
no warning windows. Ring turn HELD 1236 through all 15 steps; NEXTTURN never
clicked. NOTE the relaunched production campaign plays at t1236 (lower turn
than t252/t253's 1255 — different campaign state, so re-measurement of the
option list was mandatory, not redundant).

NEGSCREEN (Orfa, opened from species-menu race TEXT line (553,73); clicking
between rows at (553,173) did NOTHING — hit target is the text line, ~10 px
tall, rows at game y ~73/~140/~207):
- Option list rendered FIVE rows (t252 rendered THREE — posture/campaign
  dependent list CONFIRMED across campaigns). PLAYERDIP bright-text bands
  MEASURED y 329-339 / 361-367 / 390-396 / 416-425 / 446-454 (~29 px pitch);
  ALIENDIP single text band 252-261.
- DIALOGUE PROVENANCE EXACT [verified file match]: alien line "Uh oh.  What's
  wrong now?" == race02.dip:172 DR_NoDipResponse (file header "Diplomacy text
  for Orfa"); player rows verbatim player.dip ACTIONS strings — DA_NoDipAction
  (Goodbye, :67), DA_DeclareWar (:31), DA_ProposeAlliance (:34),
  DA_TradeStarlanes (:37), DA_TradeStars (:40). Rendered order == file order
  MINUS filtered rows, EXCEPT Goodbye is HOISTED to row 1 (file-last).
  Not rendered at this posture: DA_TradeResearch, DA_OfferPeace,
  DA_BreakAlliance, every %t third-party action.
- player.dip base DIPVALUES captured verbatim: DECLARE_WAR 70 ACCEPT_PEACE 100
  PROPOSE_PEACE 150 BREAK_ALLIANCE 170 ACCEPT_ALLIANCE 200 PROPOSE_ALLIANCE
  250 START_ATTITUDE 100 SHIP_PATIENCE 100 — base table; race files override
  (Orfa ACCEPT_ALLIANCE 570 live, diplomacy.md), so the rewrite must load
  per-race values, never this table alone.
- Third-party region (y 40-206 above ALIENDIP) renders race art (Orfa
  creature/volcanic scene) — 13NEGOT.SHP lead stands; no readout there.
- Goodbye row click (480,334, band-measured) CLOSED the negotiation directly
  to the species menu (202 px blink), no alien-reply screen. DA_NoDipAction
  terminates the flow.

INTELLIGENCE (from species menu (553,311)):
- Header "Chamachies Intelligence"; columns Fleet/Colonies/Discoveries as
  RELATIVE symbols (help intscr); self row included; relation-flag icons at
  row right. This campaign vision-read Chamachies 10/12/4, Ungooma 10/6/4,
  Orfa 8/6/4 [UNVERIFIED counts, R13 pitfall — posture not data].
- NEGATIVE (measured): race-row click (230,370) changed 204 px == blink floor
  -> rows are NOT clickable; NO intel detail view exists. Manifest-level IS
  the terminal intel depth; no buttons/tabs on the screen (vision). Escape
  unwinds intel -> species menu.

RESWIN dossier-level (open state: panel EMPTY, no gold ring — this campaign
had NO current project at t1236; t252 opened with one, so the panel is
state-driven, not layout-driven):
- CLICK LAWS = help reswin verbatim, confirmed end-to-end: clicking an EMPTY
  disk (72,327) SETS it as current topic — panel became "Repulsion Beam Tech
  / (33 days) / Allows: Fleet Disperser", 900 px change CONFINED to the
  clicked disk bbox (41-100 x 299-358; other nodes 0 px), NO confirm popup.
  STATE CHANGE MADE (honest): the :9 game's study topic is now Repulsion Beam
  Tech (was none); no in-game cancel control exists to revert — autoplay
  campaign only, ring banks unaffected.
- DISCOVERED/filled disk = dossier read, no state change: (213,88) -> "Energy
  Focusing / Allows Myrmidonic Carbonizer, Accutron"; red-ringed node
  (362,462) -> "Megagraph Theory / Allows / Internet". The "(N days)" line
  renders ONLY for the in-progress topic.
- ALLOWS LAW PROVEN 3/3 [verified]: restree.txt row N -> tech idx N-3; Allows
  list = REVERSE JOIN {gizmo + planitem records whose tech field == idx}.
  Energy^Focusing row 42 = idx 39 -> gizmos.txt:230 Myrmidonic^Carbonizer
  field 39 + :260 Accutron field 39 (exactly the two rows rendered);
  Repulsion^Beam^Tech row 45 = idx 42 -> gizmos.txt:209 Fleet^Disperser field
  42; Megagraph row 62 = idx 59 -> planitem.txt:100 Internet field 59.
  restree's own trailing numbers are PREREQS (research.md), not Allows.
- DAYS DATA POINT (not a law): cost 110 -> "(33 days)" here vs cost 120 ->
  "(15 days)" (t252) — days not a function of cost alone (rate-dependent);
  n=2, do not derive.

SAFETY: 15 steps, zero turn drift, no PROPOSE/DECLARE/ABANDON/END-TURN click;
the Goodbye row was clicked only from a per-sweep MEASURED band. Game parked
on the galaxy screen: final vs baseline 242 px (blink noise floor).

## 6. Explicitly NOT in P5a (no fakery)

pan/zoom/layer toggles (children exist in windows.txt but their exe
behaviour is unverified), the 132-window chrome (SHAPEFRAME frames need
OQ-005), audio mixing of headerless rates (OQ-006), save/load (OQ-003).
Vendor fonts were on this list until OQ-017 closed (§3). Each remaining item
is a listed open question, not a silent omission.

## 7. t388 CAMPAIGN SCREEN LAW LANDED (2026-11-14)

The campaign loop (ui.cpp) is now a set of vendor SCREENS keyed by the
windows.txt STATE ids, with the rail as the switch. Pure law module:
`rewrite/src/ui/statuslaw.{h,cpp}` (no SDL; 8 pins
`statuslaw_*_t388`, 289 tests 0 fail). Full working log + the 10status.shp
census: docs/re/_wip_t388.md. Distilled facts:

- STATE IS AN ID-LIST [verified 123/123]: "STATE 1 10" = active in state 10
  only. Rail "1 1" = map only; Intelligence "1 7" = species menu only;
  COSMOSWnd "4 1 3 7 13" = the map stays visible under the species menu
  (t252 vision corroborates); STATUSWND "1 10" only — an independent
  full-screen screen, NOT a bottom bar (the t388 task prose "bottom bar" is
  refuted by the rect 7,7-632,472 + the STATE lists).
- SWITCH LAW: msg 1 + param1 (a known screen id) switches; msg 5/7/8 and
  unknown ids (13 NEGSCREEN, 17 PLANETALLOC) are NO-OPS — never a clamp.
- ESCAPE: inside a screen -> map (t252 live); on the map -> quit (standing).
- 10status.shp [measured t388, scripts/r388_status_census.py]: 2 records,
  k0 639x479 V FULLY OPAQUE (306081 painted px = W*H, zero skip rows) —
  the full-backdrop class (same as 4loadgam/2savegam k0); k1 32x31. The
  backdrop is blitted full-frame via the two-buffer prefill-diff mask;
  palette stays the named luminance-ramp seam (title-art.md §4).
- Screens landed with chrome: map(1), species(7, race-row frames over the
  map), Planets(10), Intelligence(14), Ships(18), Research(20) — the last
  five FRAME + TITLE only; content is a named seam per screen.
- HONEST NEGATIVES [verified over all 132 windows.txt records]: no button
  named Galaxy/Production/Design exists anywhere; SAVE/LOAD exist ONLY in
  state 0 (title). Campaign Alt-L (opens the t387 load window) / Alt-S
  (prints the no-writer seam) are LABELLED PORT ADDITIONS.
- LIVE WITNESS (Xvfb :81, xsend): map->Planets->map->Species->Intelligence
  ->map->NEXTTURN turn 1, every step logged; wired as gate 4c-d.

## t391 PRESENTATION SWEEP — every screen art-backed-or-honestly-vector (2026-11-14)

Task: audit the campaign screens for vector chrome where the vendor has ART.
Verdict table below; instruments scripts/t391_screen_shot.sh (one-window Xvfb
tour, shot per screen, app-log names the screens) + scripts/t391_screen_mass.py
(mechanical class census: per-shot dominant colour = bg; mass >50k art,
<5k vector, between = vector-content) + scripts/t391_registration.py (t386
conflict-count law re-applied to the .shp backdrops through OUR luminance-ramp
blit). Witness shots work/r1/loop/t391-{title,load,map,status,fleet,research,
species,intel}.png; census VERDICT PASS 8/8.

- STATUS state 10 ART-BACKED [measured]: 10status k0 639x479 blits at (0,0);
  registration shift(+0,+0) 295,063 ramp-matching px / 0 map-conflicts, and
  mass 53,438 over the dominant grey. The t388 FULL-BACKDROP test stands
  (k0 IS the backdrop, not a strip — task question (a) answered).
- LOAD state 4 ART-BACKED [measured]: 4loadgam k0, shift(0,0) 50,296 px /
  0 conflicts, mass 59,803. (The dominant (163,163,163) is the ramp value of
  the backdrop's dominant index — expected, not a wash: conflicts 0 proves
  per-index fidelity.)
- MAP state 1 honestly-vector [verified]: 1starmap k0 158x75 element art;
  NO backdrop record; rail icons ARE cited art (SHAPEITEM law below).
- FLEET state 18 honestly-vector [verified, decisive]: FLEETWND SHAPEFRAME 0
  (ln1722) but NO 18*.SHP exists among the 165 data .shp files and no
  SHAPEFILE names one — the vendor has no fleet backdrop art to skip.
- INTEL state 14 honestly-vector [verified]: 14intel.shp 10 records max
  28x28 (element art only, unused = named seam).
- RESEARCH state 20 honestly-vector backdrop [verified]: 20res 6 records
  15x30-ish = the RESROT/RESMOVE arrow faces (rect 524,442-539,472 = 15x30
  exact); restree.shp = tech-tree content art (named seam, not chrome).
- NEWGAME state 3 frame honestly-vector + wheel faces cited art [verified]:
  TYPE-18 census = EXACTLY ONE record (NEWGAMEWND ln579); 3cfgnew 13 records
  max 88x80, no backdrop-size record for the 154x352 window.
- SPECIES state 7 named seam [inferred only]: RACE_1..7 + Intelligence all
  carry SHAPEFRAME -1 (no table citation), yet 7racesel.shp k0..k7 are EIGHT
  records of EXACTLY the 158x30 row size — size-match witness, NOT cited;
  do NOT blit without a stronger witness (palette seam compounds).
- SAVE state 15 art-in-hand seam [verified]: 2savegam k0 639x479 exists;
  our port has no save screen (no campaign writer, t382 seam).
- STATE 17 (PLANETALLOC, not implemented): 17np.shp k0 639x479 + k4 625x357
  are the backdrop-per-prefix candidates — banked for whoever implements it.

STRUCTURAL LAW [verified ln34..1756]: the eight TYPE-100 blocks sit at the
HEAD of their state's window section (0 title, 1 star map, 3 cfgnew, 7 race
menu, 8 ship design, 13 negotiation, 16 battle, 20 research). FIVE screen
sections have NO TYPE-100 header (states 2/4/15 load-save, 10 status, 14
intel, 17 planet-alloc, 18 fleet): windows.txt CANNOT name their backdrop;
only the numeric-prefix file + the engine's by-name open can (10status/
4loadgam/2savegam/14intel/17np exist on disk; 18 does NOT). The port's
screenShapeLib naming law is therefore the correct instrument for the four
headerless screens that have art, and no other screen is missing art.
SHAPEITEM census [verified 7/7]: rail buttons -> 1starmap k3/k4/k5/k7;
NEWGAME child buttons -> 3cfgnew k0 — the port implements every cited
SHAPEITEM; item-level art gaps: NONE.
HONEST NEGATIVE: no engine change landed (the sweep found ZERO screens where
the vendor has backdrop art and the port paints vector — nothing to fix);
the 7racesel strip role stays a named seam; chrome COLOUR stays the
luminance-ramp palette seam (title-art.md §4) — geometry is what registers.
