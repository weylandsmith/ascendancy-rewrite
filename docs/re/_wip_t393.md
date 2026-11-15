# t393 WIP — New Game screen rebuild (D10 "garbled and unusable")

## Cited data facts (established this iteration)

1. STATE-3 WINDOW TABLE (extracted/ascend00/windows.txt, re-parsed
   mechanically — every record whose STATE field contains token "3"):
   - L575 TYPE 100 STATENUMBER 3 SHAPEFILE DATA\3CFGNEW.SHP  (state header)
   - L579 TYPE 18 NEWGAMEWND (334,12)-(488,364) PARENT NONE SF 0 STATE "1 3"
   - L596 TYPE 0 GALAXY_MORE (7,381)-(122,472) PARENT NEWGAMEWND SF -1
     MSG 501, WINITEMS 2: SHAPEITEM 1 data\3cfgnew.shp 0 0 0 +
     TEXTITEM 0 "Star^Density 2 0 10"
   - L615 TYPE 0 PLAYERS_MORE (131,381)-(246,472) MSG 503, TEXTITEM "Species"
   - L634 TYPE 0 DIFFICULTYMORE (255,381)-(370,472) MSG 505,
     TEXTITEM "Atmosphere"
   - L653 TYPE 0 Player^Color (379,381)-(493,419) PARENT NONE SF -1 MSG 0
   - L670 TYPE 10 RACELIST (502,45)-(632,372) PARENT NEWGAMEWND SF 7
   - L199 TYPE 2 COSMOSWnd (7,7)-(465,472) STATE "4 1 3 7 13" — THE MAP
     VIEWPORT IS LIVE IN STATE 3 => the starfield behind the config panels
     is the vendor's own window table, not an inference.
   - L686 LOADSCREEN STATE "3 2 4 15" (title strip 7,7-632,37) also live.
   - Rail children ROT*/ZOOM*/TOG*/RACECONTROLS STATE "3 1 7 13" are also
     listed for 3 — but the user-supplied original shows NO rail on this
     screen; see measurement below (STATE field = registration, not paint).

2. SUMMARY STRING LAW (extracted/ascend00/static.txt, verbatim):
   - L429(//153) "Player Species"
   - (//154) "The %s %s"  <- lore template: species name + newgame.txt line
   - (//155-159) "Vacuous" "Sparse" "Average" "Dense" "Very Dense"
   - (//160-162) "Peaceful" "Neutral" "Hostile"
   - (//163-167) "Three" "Four" "Five" "Six" "Seven"
   - (//168) "%s Star Cluster\n%s Species\n%s Atmosphere"  <- the three
     summary lines the original shows ("Average Star Cluster / Five Species
     / Neutral Atmosphere")
   - (//169) "Begin New Game"

3. LORE TEXT (extracted/ascend00/newgame.txt, 21 lines + 0x1a EOF):
   line N+1 = specnum N fragment, lowercase "are ..." —
   e.g. L1 "are a mysterious group of robot creatures controlled by an
   unknown extra-galactic super force. They are hideously strong and quick."
   (Minions specnum 0). Template static.txt 154 "The %s %s" completes the
   sentence: "The Minions are a mysterious group..." == the green text in
   the user-supplied original EXACTLY (word "extra-galactic" vs vision's
   paraphrase "otherworldly" — the FILE is authoritative).

4. ROOT CAUSE of "garbled" [verified in code]: title.cpp:143 loop draws the
   RACECONFIG state as an OVERLAY on top of the title frame (title art +
   seven button rects + fallback band still drawn under it). The task's
   screen-switch law (t388) says NEWGAMEWND replaces the screen. Also the
   user's shot is 512x384 = 0.8x of 640x480 while kDisplayW=640 — window
   size diagnostic line lands with this task (t394 owns the scale law).

5. STARTGAME (windows.txt L1866 TYPE 30, STATE "1 12", (0,0)-(639,400)) is
   NOT state-3 => the "Begin New Game" click zone is NOT in windows.txt.
   Its rect must come from measurement of the user-supplied original
   (allowed evidence) and is then a cited-measurement seam, not a windows.txt
   citation.

## MEASURED from the user-supplied original (scratchpad/newgame-original.png,
## 643x481 capture = 640x480 + 1px window border: screen_coord = capture-1;
## anchor proof: left bevel capture x1..7, navy starts capture x8 ==
## windows.txt GALAXY_MORE x0=7 EXACT)
6. CAPTURE->SCREEN GEOMETRY [measured]: bevel census row y=430: screen x0..6
   bevel, x7 navy (GALAXY_MORE x0=7 match), bevels at capture x124/248/372/494
   -> screen 123/247/371/493 == the windows.txt child right edges 122/246/370
   +gutters. RACELIST right bevel capture 633-640 -> screen 632.. x1=632 match.
7. STATE-3 PAINT SET (original): starfield + NEWGAMEWND panel + RACELIST +
   bottom bar (4 cited panels + Begin) + summary + name + header. NO rail
   (x 474-632 y 364-433 shows bar/Begin content) => STATE-list membership =
   registration, NOT paint, for the rail children. Confirms expectation.
8. BEGIN NEW GAME rect [measured]: screen (494,373)-(639,472) — navy field
   right of PlayerColor right bevel (screen 493), top bevel screen rows
   373-379, bottom bevel rows 473-479; green ink rows 391-456 x 573-629
   (capture) inside. NOT windows.txt (STARTGAME STATE "1 12" cited negative).
9. TEXT PLACEMENTS [measured, screen coords]: species name green ink rows
   18-27 x 395-429 (centre 412 ~= NEWGAMEWND centre 411); "Player Species"
   white rows 16-25 x 530-606 (centre 568 ~= RACELIST centre 567); lore green
   row bands 266-273/277-293/297-313/317-324 inside NEWGAMEWND; summary white
   rows 327-336/340-349/353-363 (pitch 13) centred x ~= 170 (centre of the
   visible starfield zone 0..340). All faces small (<=10 ink rows).
10. COLOURS [measured]: panel navy (12,32,48); lore/name green (0,142,69);
    bevel grey (97,97,97). White uses pinned kInk (215,215,215) — capture is
    lossy.
11. RACE ROWS: RACELIST interior (502,45)-(632,372); row law from the
    RACE_n census (rows 30 of pitch 39): rows 45+39i .. +29, i=0..6 fits
    (last row 279..308 <= 372). Portraits ~30px at x~560 (capture samples).
12. DENSITY WORD->COUNT LAW [cited mapgen.md t78 + static.txt 155-159]:
    cycle Average 50 -> Dense 75 -> Very Dense 100 -> Vacuous 15 -> Sparse 25;
    species words Three..Seven (static 163-167), atmosphere Peaceful/Neutral/
    Hostile (160-162). Original shows Average/Five/Neutral (screenshot).
13. LORE SOURCE: extracted/ascend00/newgame.txt line N+1 = specnum N
    fragment; names via raceNN.dip header (species.cpp DipFile displayName,
    already parsed by loadAbilities). static.txt 154 "The %s %s" template.
14. ROOT CAUSE of garble [verified code]: title.cpp:143 draws RaceConfig as
    OVERLAY under the live title frame; bottom row y 381-472 fits 640x480 —
    the user's clipping came from their 512x384 window (0.8x of logical);
    lands a `ui window WxH` diagnostic line with this task (scale law = t394).
