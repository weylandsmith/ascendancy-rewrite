# t412 WIP — NEW GAME FIXES + RACE INTRO

Session base: fresh; no new sitting (live-timeline.jsonl mtime 2026-11-12
06:45, max turn 1254 == t392..t411 value); tree clean at de7725c; no new
USER: lines in DECISIONS.md past the 11:37 D11 block / D13 quote.

## F0 — task scope (STATE.md queue row t412 + D11 L298 verbatim)
1. species-row squares EMPTY (no portraits) — re-derive after t411 blend fix
   (t401 wired smraceNN scaled 2x; the t411 blitShapeScaled blend-mode fix
   may change what lands on screen — measure FIRST before touching law).
2. bottom-row wheels small/greyish.
3. RACE INTRO screen MISSING between RaceConfig-Begin and the map: content
   law = extracted/ascend00/history.txt per-race blocks (VERIFIED on disk:
   `// Minions / specnum 0 / power..endpower / intro..endintro / peace /
   neutral / hostile / text..` CRLF, 899 lines, 31525 B).
4. Begin robustness: sequence Begin -> intro -> map (the ~3 s mapgen is
   exposed BECAUSE the intro doesn't exist; queue note 2026-11-15).

## F1 — evidence census (done pre-capture)
- history.txt EXISTS extracted/ascend00/history.txt; per-race blocks keyed
  `// Name` + `specnum N`; sections power/endpower, intro/endintro,
  peace, neutral, hostile, text. The `intro` section is the opening scroll
  content candidate.
- smraceNN.shp x21 present in extracted/ascend01/data + /tmp/uishow mirror
  (22 files incl raceflag? no: 21 smrace + count artifact) — portraitFor()
  in title.cpp loads dataRoot + /extracted/ascend01/data/smrace%02d.shp.
- 7racesel.shp = MAP-screen species menu strips (t401 S2 correction), NOT
  the New Game list. New Game rows = RACELIST TYPE 10 SHAPEFRAME 7 code
  rows + smrace portraits (t401 law).
- t401 witness script pattern scripts/t401_newgame_witness.sh (xsend bare
  x y = click; FRESHGAME centre 318,295 per boot.md L22 rect
  (159,280)-(477,310)).

## F2 — CURRENT-STATE CAPTURE (scripts/t412_newgame_shot.sh, native vision)
Shot /tmp/t412_shots/t412-newgame.png (Xvfb :97, --data /tmp/uishow, seed 5):
- SPECIES ROWS: PORTRAITS RENDER (3 slots show smrace art: teal robot /
  brown creature / red-lava). Defect #1 (empty squares) was the t411
  BLEND-MODE BUG all along — the D11 grade predates the fix. NO portrait
  law change needed.
- DESC PANEL: solid black, green ring + portrait, planet disc + green
  crest, green lore text — all present.
- BEGIN BOX: starfield dot cluster + portrait emblem + label — present.
- REMAINING DEFECTS (measured from this shot):
  a) WHEELS CLIPPED: wheel content starts y=408 and the 3cfgnew face is
     79-80 tall -> bottom ~7 rows cut at window edge 480. The Species
     wheel's icon ring is visibly truncated at the bottom.
  b) PLAYER COLOR panel (379,381)-(493,419) OVERLAPS the Atmosphere panel
     (255,381)-(370,472) region visually: the chips row sits high, the
     panel interior is the mottle texture, and the wheel below (Atmosphere
     k10) crowds the colour chips.
  c) wheels read SMALL vs the vendor (t401 S10 measured content circle 55
     px at native 84x79 face — matches our blit; the vendor screenshot
     comparison pending).
- CONCLUSION: queue item "species-row squares EMPTY" is CLOSED BY THIS
  CAPTURE (t411 fix); the real remaining work is the RACE INTRO (item 3/4)
  + wheel clipping/polish. Intro first (bigger defect), wheels second.

## F3 — VENDOR RACE-INTRO LAW [verified, Ghidra ascend_restored.bin]
The census site "history 0x2b4d5" (datafiles.md §2) is the immediate of
MOV EDX,0x1190 at 0x2b4d4 inside FUN_0002b48a (function boundary verified
by disassembly walk; created in Ghidra this session). Pool-relative law:
0x82BB0+0x1190 = payload 0x83d40 = "history.txt" [verified bytes].
FUN_0002b48a = THE RACE INTRO LOADER+RENDERER:
- Opens history.txt; scans lines (FUN_000340e8 = read-line) for literal
  "SPECNUM" + sscanf "%s %d" until specnum == DAT_0007458e (the player
  specnum word); missing race -> "Species %d not found in history file."
  (pool 0x83d71) + error FUN_0002a428.
- Section keywords (pool 0x83d5f..0x83e09, verbatim): SPECNUM/END/POWER/
  ENDPOWER/INTRO/ENDINTRO/PEACE/ENDPEACE (+ census continues: the hostile
  pair). Section selection chain:
  * POWER block -> prefix "%s: " (pool 0x83dbd) into a 204-B stack buffer
    -> the HEADER line.
  * INTRO block -> concat lines into a 204-B buffer (cap 0xc3=195, error
    over 300).
  * TEXT block -> concat into a 1000-B buffer (cap 0x3e3=995).
  * PEACE / NEUTRAL / HOSTILE blocks -> appended to the SAME body buffer
    gated on DAT_00013bc4 == 0 / 1 / 2 (a 3-way setting — the New Game
    ATMOSPHERE control's value maps here [inferred mapping; the 0/1/2
    gating itself is verified code]).
  * FINAL block -> concat into a 3000-B buffer (cap 0xbb3=2995) — a
    second buffer, role unclear (non-displayed remainder).
- TRANSFORM LAW [verified tail of FUN_0002b48a]: over the header and body
  buffers: '@' -> '\n'; '_' -> ' '; '\n' -> ' '. So the file's "@@" marks
  a PARAGRAPH BREAK and "_____" is indent-space filler — exactly the
  opposite of a naive read.
- RENDER: FUN_0005caac(&DAT_0004850c, FUN_0001fc34(0,7,0x2e)) sets up a
  text draw; three FUN_0002fb38 calls, args (0, racecolor, 0xff, 599),
  (0, 0xf3, 0xff, 0x294), (2, racecolor, 0xff, 0x602) [verbatim immediates].
  ARG ROLES UNMAPPED (screen/colour/0xff/?) — do NOT read them as rects;
  the on-screen geometry of the vendor intro is UNCITED (port layout is a
  documented choice; decider = a live vendor capture). INK colour arg =
  (&DAT_00012e18)[specnum*494] *4 + 0x13 — the RACE COLOUR byte from the
  race table stride 494 (t409's 0x12e16 + specnum*494 table — SAME table;
  the intro text is drawn in the race's own colour).
- CALL SITE: no direct E8 call and no image-absolute pointer to 0x2b48a
  exists in the payload [verified scan] -> invoked via a table/offset the
  static scan didn't resolve. Entry-point evidence for Begin->intro->map
  therefore rides on the USER WITNESS (queue row t412: "race introduction
  screen that appears after the new game screen and before the galaxy map
  display") — cited as user testimony, not static law.
- Art seam: FUN_0002fb38 draws TEXT only (no shape blit inside
  FUN_0002b48a); no race-portrait load in this function. The intro is
  TEXT-ONLY in a box — the "art" the queue asked to census does not exist
  in the loader. NAMED SEAM stays: whether a portrait accompanies it.

## F4 — RACE COLOUR LAW [verified bytes] + DISPLAY PLAN
INK = game.pal[ racebyte*4 + 0x13 ] where racebyte = byte at
0x12e18 + specnum*494 (race/diplo table stride 0x1ee, aicode.md; +2 off
0x12e16 base). game.pal is 6-bit 768 B (palette.md). Sample: Orfa
(specnum 2) byte 0 -> pal idx 19 -> (0,170,81) 8-bit — THE vendor lore
green already banked as kLore (0,142,69 was measured off a screenshot;
pal 19 is the palette-exact value — keep kLore for existing screens, use
the TABLE for the intro). Minions byte 16 -> pal 83 -> (223,61,53) red.
DISPLAY PLAN (port; seams named):
- BootState::RaceIntro between RaceConfig-Begin and Campaign.
- Pure module ui/raceintro.{h,cpp}: parseHistoryIntro(text, specnum,
  atmosphere) -> {header (POWER via "%s: "), body = INTRO + TEXT +
  atmosphere-gated (PEACE/NEUTRAL/HOSTILE per DAT_00013bc4 == 0/1/2 —
  the New Game Atmosphere word matches Peaceful/Neutral/Hostile exactly
  [inferred binding])}; transform '@'->'\n', '_'->' ' (verified);
  wrapParagraphs(text, width) -> lines (port choice: wrap at ' ', indent
  0; the vendor box law 7..639 with word-wrap is the cited part).
- Render: black screen, header line at (7,7) box, body lines from
  (7,246)-width-632 at font pitch; ink = race colour; click OR any key
  dismisses -> Campaign (minimum ship per queue: "text panel +
  click-to-continue").
- Begin robustness: the ~3 s "Begin->map" is process-start mapgen —
  buildCampaign runs BEFORE runTitleScreen (main.cpp:523), so by Begin
  time the galaxy EXISTS; measure with a witness (Begin click -> first
  map frame) and report honestly. Pre-generating behind the intro would
  mean moving buildCampaign behind the intro = a main.cpp restructure
  (campaign seed known before Begin? NO — species/atmosphere are chosen
  ON the config screen, so generation CANNOT precede Begin; the vendor's
  3 s sits between Begin and the map for the same reason [inferred].

## F5 — INTRO RENDER GEOMETRY [verified immediates, 0x2bc73..0x2bd55]
The FUN_0001fc34(0,7,0x2e) font-open + FUN_0005caac(draw-context @0x4850c,
font) + FUN_0002fb38 draw-call struct fills, verbatim:
- draw #1 (HEADER buffer): x0=7, y0=261, x1=639 (0x278), y1=465 (0x1d1);
  colour = racebyte*4 + 0x13 (SHL 2 + ADD 0x13 re-confirmed in the raw
  bytes at 0x2bcff..0x2bd2d); mode 10 (0xa), 0xff, screen 0.
- draw #2 (BODY buffer): x0=7, y0=246 (0xf5), x1=639, y1=312 (0x138);
  colour 0xf3 (243), mode 10, 0xff, screen 0.
- draw #3 (third buffer @0x48c44): x0=7, y0=37 (0x25), x1=639,
  y1=599 (0x257); colour = race colour again; mode 2 (0x2).
Field roles (which of the four is y-top vs y-bottom) follow the t408
text-rect convention [inferred]; the two race-coloured draws sandwich the
body: header zone rows ~261..465, body zone rows ~246..312 [unverified
orientation — seam decider: a live vendor capture]. PORT LAYOUT (documented
choice): header line at (7,7) centred-left, body paragraphs from (7,60)
wrapped to 632 px, ink = game.pal[racebyte*4+0x13], click/any-key -> map.

## F6 — IMPLEMENTATION + WITNESS + MUTATION (landed)
- Module ui/raceintro.{h,cpp} pure law (no SDL): parseHistoryRace (SPECNUM
  block, POWER/INTRO/PEACE/NEUTRAL/HOSTILE/TEXT sections, next-SPECNUM is
  the block terminator — census: 126 ENDxxx lines, NO bare `end` before
  each specnum), introTransform ('@'->'\n', '_'->' ', '\n'->' '),
  buildIntroPanel (header=POWER, body=INTRO+TEXT+ONE atmosphere-gated
  section; atmosphere out-of-range REFUSES the gated section, never clamps),
  wrapIntroLine (pixel budget, over-long word stands alone), introPalIndex
  (racebyte*4+0x13) + kIntroRaceBytes[21] static-table census.
- Real-file census [measured]: all 21 specnum blocks parse with non-empty
  power/intro/text; specnum 1 (Snovemdomas) is the ONLY race with non-empty
  PEACE/NEUTRAL/HOSTILE blocks (107/76/108 chars); the other 20 carry empty
  pairs, so atmosphere NEVER changes their body (pinned both ways).
- Wiring: title.cpp Begin -> runRaceIntro DIRECT call (pitfall: the Begin
  `continue` re-tests while(Title||RaceConfig); `st = RaceIntro` alone
  EXITED the loop — witness caught it as "ui title exit: raceintro").
  runRaceIntro (vendortext.cpp): black screen, header y7, body wrapped at
  kIntroBodyWidth, ink chromePaletteArgb(introPalIndex(byte)), click/key
  dismiss -> Campaign. boot.h BootState::RaceIntro added (state 8 enum
  value; boot.cpp overlay-exit law + bootStateName).
- WITNESS scripts/t412_newgame_shot.sh: FRESHGAME -> BEGIN -> intro ->
  click -> map. stdout chain verbatim: "ui raceconfig begin density 50
  species 7 atmosphere 1 species-pick 0" / "ui raceintro specnum 0
  atmosphere 1 ok" / "ui raceintro dismiss -> campaign" / "ui home star
  Amoroso at 254,438". Native vision on /tmp/t412_shots/t412-raceintro.png:
  heading "Supreme Planet Invaders" + full Minion body in RED ink, no
  clipping/overlap, bottom prompt "Click or press a key to continue";
  after-dismiss shot = the campaign map. SEAM kept honest: vendor draw
  immediates (599 > 480) unmapped -> port layout documented, not claimed.
- MUTATION 6/6 CAUGHT (restore-guard trap, /tmp/t412_mutate.sh): M1 drop
  SPECNUM terminator (3 fail), M2 '@'-marker mapped to space (6), M3
  atmosphere-2 clamp-away (2), M4 ink law *4->*8 (2), M5 wrap truncates
  long word (2), M6 error wording (2). AFTER-RESTORE 401/0.
- Suite 394 -> 401 (+7 raceintro pins, 1 REQUIRE_DATA real-history test);
  test_boot_t385 state loop 7->8.
