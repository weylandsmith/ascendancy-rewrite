# Boot / title-screen law — t385 (2026-11-14)

Hand-authored (NO generator writes this file — verified: `scripts/ui_probe.py`
writes only docs/re/ui.md, species.md, diplomacy.md; gate 3k regenerates
those three, never this one). Source of every number: `extracted/ascend00/
windows.txt` (CRLF, 0x1A-terminated) blocks read directly this iteration,
plus `extracted/ascend00/subtitle.txt` via docs/re/ui.md §4.

## 1. Title-menu button table [verified, windows.txt L34-175 verbatim]

The opening screen is a CONTROL screen (refcap witness: title shot 9.2%
palette-match vs the intro-movie union palette = NOT a movie frame,
docs/re/refcap.md). Seven TYPE-0 buttons share one column:
x0=159 x1=477 (width 318), height 30 (y1-y0), vertical pitch 40, first
button at y=200. All: PARENT NONE, STATE "1 0", MOUSEFOCUS 1, SHAPEFRAME -1,
SOUNDCHANNEL 0, SENDMESSAGE 1 (except EXITTODOS: SENDMESSAGE 2), SENDPARAM2 1.

| NAME        | rect (x0,y0)-(x1,y1) | msg/param1 | our state target | TEXTITEM 0 (verbatim)      |
|-------------|----------------------|------------|------------------|----------------------------|
| INTRO       | (159,200)-(477,230)  | 1/6        | Intro            | `Play^Introduction 3 0 0`  |
| PLAYTUTORIAL| (159,240)-(477,270)  | 1/15       | Tutorial         | `Tutorial 3 0 0`           |
| FRESHGAME   | (159,280)-(477,310)  | 1/3        | RaceConfig       | `New^Game 3 0 0`           |
| RESUME      | (159,320)-(477,350)  | 1/1        | Campaign         | `Return^to^Current^Game 3 0 0` |
| LOAD        | (159,360)-(477,390)  | 1/4        | Load (t387)      | `Load^Game 2 0 4` + `Alt-L 2 0 18` |
| SAVE        | (159,400)-(477,430)  | 1/2        | Save (t388)      | `Save^Game 2 0 4` + `Alt-S 2 0 18` |
| EXITTODOS   | (159,440)-(477,470)  | 2/0        | Quit             | `Exit^to^DOS 2 0 4` + `Alt-X 2 0 18` |

- `^` is the vendor word-join inside TEXTITEM strings (caret -> space for
  display; the trailing ` 3 0 0` / ` 2 0 4 18` fields are item kind/font/slot
  sub-grammar — meanings OQ-015 territory, NOT re-litigated here, NOT used).
- The RESUME button's own label is "Return to Current Game": RESUME resumes
  the in-progress game, it is NOT "load last save" (that is LOAD, msg 1/4).
  Our D8 mapping (Resume-equivalent = boot straight into the campaign) lands
  on the same button the vendor wired to msg 1/1.
- HELPINDEX values (intro/tutorial/newgame/resume/loadgame/savegame/exitdos)
  match the manual's menu list banked in ui.md §3 — the four "menu options"
  of D8 are the first four rows; LOAD/SAVE/EXIT are on-screen too.
- The opening chrome is the TYPE=100 block immediately BEFORE the buttons
  (windows.txt L34-36): `STATENUMBER 0` + `SHAPEFILE DATA\0OPENING.SHP`.
  Button SHAPEFRAME is -1 (no shape frame on the buttons themselves). Which
  0opening.shp record state 0 selects is t386 territory (title ART identity)
  — deliberately NOT guessed here.

## 2. State machine landed (rewrite/src/ui/boot.{h,cpp})

States: Title, Intro, Tutorial, RaceConfig, Load, Save, Campaign, Quit.
Transitions (click-routing table is a PURE function `bootClick(state, pt)`,
headless-unit-testable, no SDL):

    Title  --INTRO click------> Intro        Intro  --movie exit--> Title
    Title  --PLAYTUTORIAL-----> Tutorial     (seam: tutorial driver absent)
    Title  --FRESHGAME--------> RaceConfig   (seam: t387 NEWGAMEWND)
    Title  --RESUME-----------> Campaign     (the D8 boot path)
    Title  --LOAD-------------> Load         (seam: t387 4loadgam chrome)
    Title  --SAVE-------------> Save         (seam: t388 STATUSWND save)
    Title  --EXITTODOS-------> Quit          (terminal; no click leaves Quit)
    RaceConfig --RESUME-------> Campaign     (raceconfig->campaign edge;
                                              full race-picker UI is t387)
    any click outside a live button -> no transition (no-op, never clamps)

Code site: rewrite/src/ui/boot.h (rects/labels/pure machine) +
boot.cpp (SDL title loop) + rewrite/src/ui/ui.cpp (runTitleScreen) +
main.cpp `--ui` (campaign entry is now ONE transition out of the title
loop, not the constructor path; `--resume` pre-selects Campaign so the
autoplay/gate path is preserved). Intro movie = intro65a.flc
(dataRoot/extracted/ascend02/data, media.md §1), played via the existing
playIntro decoder; any key/quit ends it back at Title.

## 3. Honest scope / seams
- Title ART (the dinosaur figure, t386 decides source: 0opening.shp vs movie
  frame): NOT rendered this row; the band + text are geometry-verified, the
  art is a named seam. No vendor sprite is faked (R13 / lookalikes-banned law).
- Tutorial has no driver in the rewrite: selecting it prints the transition
  and returns to Title (named seam), it does not silently do nothing.
- TITLERECT 0,379-639,419 is a subtitle.txt key (ui.md §4) that governs the
  caption band DURING movie playback; the title screen draws its own band
  there and renders the game name in BIGFONT — placement measured, font-face
  choice cited (windows.txt manifest LARGEFONT, ui.md §2), exact vendor glyph
  layout of the title logo awaits t386.
- Verification instrument: run_tests TEST boot_* group (geometry + routing,
  synthetic points, no display) + gate 4c-2 title smoke (xvfb, frame-capped
  exit 0). Self-graded VISION of our renders is still banned (R13).

## 4. MEASURED SDL/Xvfb fact (t385b): first synthetic click on a NEW window
is dropped; state transitions must REUSE the window. Evidence: with the
title loop destroying its window and runCampaignUi creating a new one, the
gate's injected NEXT TURN click after Title->Campaign never printed
(measured 2026-11-14 with throwaway debug scripts, since removed): click #1
on the new window lost, click #2 landed; single-window boots (--resume)
never lost a click. The regression instrument now lives as
scripts/title_input_check.sh (no-op click -> FRESHGAME -> RESUME -> NEXT
TURN; greps the whole chain in the app log). Fix
landed: runTitleScreen hands the live SDL_Window over (ui.h `windowOut`),
runCampaignUi reuses it (`window` param, owns destruction only when it
created it). Gate 4c-b now drives Title->RESUME->NEXTTURN through ONE
window and greps BOTH 'ui title click RESUME -> campaign' and
'ui click next-turn' — the full boot chain is gate-pinned.

LANDED 2026-11-14 t385: boot state machine (boot.{h,cpp}) + title screen
(title.cpp, runTitleScreen) + --resume flag + VendorText hoisted to
ui_internal.h/vendortext.cpp (shared renderer, behavior verbatim) +
test_boot_t385.cpp (5 tests: rects/names/messages verbatim windows.txt,
routing table, inclusivity/no-clamp law, reachability, vendor labels).
Suite 270 -> 275, 0 failed; gate ALL PASS incl. the new two-click 4c-b.
Honest negatives: title ART not rendered (t386 decides source); Tutorial/
Load/Save are named seams that print and return to Title (no silent
no-ops); the RaceConfig overlay is placeholder text, not 3cfgnew chrome
(t387).

## 5. t385b D9 GAP CHECK (same day). The queue amendment (D9, DECISIONS.md
2026-11-14) demanded seven buttons + Alt-L/Alt-S + "Return to Current Game"
label + Exit-to-DOS = clean exit. Audit vs what t385 landed:
- SEVEN buttons, exact rects, block order: ALREADY MET (kTitleButtons is
  the windows.txt census; test boot_title_rects_match_windows_txt).
- "Return to Current Game" label (not "Resume"): ALREADY MET
  (test_boot_labels_are_vendor_strings).
- Exit to DOS = clean process exit: ALREADY MET (Quit -> runTitleScreen
  returns -> main prints 'ui title exit: quit', return 0).
- Alt-L / Alt-S hotkeys: GAP — t385 wired mouse only. FIXED: pure
  bootHotkey law in boot.{h,cpp} + SDL Alt-chord decode in title.cpp +
  pin boot_d9_hotkeys_t385b. Suite 275 -> 276, 0 failed.

## 6. Menu windows landed (t387, 2026-11-14): NEWGAMEWND + LOAD

Source: extracted/ascend00/windows.txt L575-717 read verbatim this
iteration (full block dump in docs/re/_wip_t387.md).

COORDINATE SPACE LAW [inferred, geometry-decisive]: every rect in
windows.txt is an ABSOLUTE screen coordinate; PARENT names containment,
NOT a coordinate offset. Witness: the state-3 bottom row
GALAXY_MORE/PLAYERS_MORE/DIFFICULTYMORE/Player^Color spans x 7-122,
131-246, 255-370, 379-493 in absolute space — equal 115-px widths, 9-px
gutters, disjoint; read relative to NEWGAMEWND (334,12) they would land
mutually overlapping and partly off-screen, and RACELIST would sit at
x=836. Impossible. This law binds every future windows.txt consumer.

Tables (rewrite/src/ui/menulaw.{h,cpp}, pure/no-SDL; pin
test_menulaw_t387.cpp x5):
- NEWGAMEWND TYPE 18 (334,12)-(488,364) STATE "1 3" SHAPEFRAME 0.
- Children TYPE 0 STATE "1 3", SHAPEITEM 1 data\3cfgnew.shp 0 0 0:
  GALAXY_MORE (7,381)-(122,472) msg 501 "Star Density"; PLAYERS_MORE
  (131,381)-(246,472) msg 503 "Species"; DIFFICULTYMORE
  (255,381)-(370,472) msg 505 "Atmosphere". Player^Color (379,381)-
  (493,419) is PARENT NONE msg 0 -> NOT a rewrite control.
- RACELIST TYPE 10 (502,45)-(632,372) SHAPEFRAME 7 (frame only; the
  state-7 RACE_n rows are the racesel screen, t388 seam).
- LOADSCREEN TYPE 11 (7,7)-(632,37) + LOADLIST TYPE 10 (7,46)-(632,472),
  STATE "3 2 4 15". Row law [inferred — no cited LOADLIST row rect
  exists]: pitch 39 from y0=46, band 30, gutter dead — verbatim the only
  list census in windows.txt (RACE_1..7, y 7/46/85/124/...).

LOAD slot law (implementation menulaw.cpp, live-verified
scripts/t387_menu_check.sh): slots = *.sav/*.SAV in a SUPPLY-YOUR-OWN dir
(--saves DIR; default <data>/saves when present; NEVER game/), sorted by
name ascending; day = u32@0 (Observer::rawDay, 4/4 corpus); a file
shorter than 4 B is TORN — listed, marked, and REFUSED on pick
(refusal-not-clamp; out-of-range index also refuses). Live witness
(2026-11-14, one-window Xvfb run): 'ui load open slots=4 backdrop=
4loadgam.shp k0' / 'ui load pick 07.sav day 300' / 'ui load refuse
43.sav (slot is torn (partial autosave))' / 'ui load cancel' -> Title ->
RESUME -> campaign still works (gate 4c-c pins the open/cancel/resume
chain).

Backdrop census (extracted/ascend01/data, V/A dims law): 4loadgam.shp
N=1 k0 639x479; 2savegam.shp N=1 k0 639x479; 3cfgnew.shp N=13
(84x79/80; k12 = known EOF truncation); 7racesel.shp N=8 all 158x30.
4loadgam.shp is referenced by NO TYPE 100 block (STATENUMBER census has
no 2/4) — the engine opens it by name like 0opening.gif; its backdrop
role is [inferred] from name + the single full-screen record.

Blit law (title.cpp blitShape): decode TWICE into differently-prefilled
buffers (0xAA/0x55) and diff — a pixel identical from both prefills was
WRITTEN; a differing one was skipped -> alpha 0 (vendor
untouched-destination semantics, formats/shp.h). Mechanical; no guessed
transparent-index value.

PALETTE [t398 CLOSED — was the named seam above]: the menu/game chrome
renders through DATA\game.pal (exe-named, payload 0x83579/0x84207; every
pixel of the three pinned in-game refcap shots lies inside it under the
DOSBox 6->8 conversion; 1starmap rail records register through it at the
cited rects). Full law: docs/re/palette.md. The title screen KEEPS the t386
TSV (game.pal covers it at 8.79% only — title-art.md §4 stands). The ramp is
the data-less-clone degradation path, announced on the console.

Honest negatives / seams:
- An accepted slot prints its pick but does NOT import into a live
  Campaign: the rewrite has no campaign-state importer (Observer is
  read-only by contract, t382). The screen returns to Title.
- The three state-3 wheel buttons ACKNOWLEDGE (print name+msg); setting
  wheel values feeds a campaign-seed seam that does not exist yet.
- RACELIST rows (state-7 RACE_n TYPE 6) are t388 chrome.
- No OQ ledger row moved (queue work; strict-close ledger untouched).

## 7. t392 TITLE TEXT BASELINE + HOTKEY-HINT LAW (2026-11-14, D10 grade)

User grade of the pushed build: "text is a tad too high in the boxes" +
"Alt-L/Alt-S/Alt-X second lines are missing on the last three buttons".
Both closed with measurement; implementation `title.cpp` draw loop +
`TitleButton::hint` (boot.h/cpp); pins `test_titletext_t392.cpp` x4.

- TABLE LAW [verified, windows.txt L128-170]: LOAD/SAVE/EXITTODOS are
  WINITEMS 2 with a second TEXTITEM whose display string is VERBATIM
  "Alt-L" / "Alt-S" / "Alt-X" (dy fields 4 and 18); the first four
  buttons are WINITEMS 1 (`... 3 0 0`). Alt-X is table-cited, not only
  user testimony.
- PIXEL LAW [measured on docs/assets/refcap/original-title-menu.png,
  capture shift shot_row = logical + 40]: single-line labels ink rows
  dy8..17/18 (draw TOP y0+8); pair buttons ink dy4..13 (label) and
  dy18..27 (hint) — the TEXTITEM dy fields land exactly on the ink tops
  (draw TOPs y0+4 / y0+18). Both lines centred on rect centre 318
  (measured spans: "Load Game" 289..346, "Alt-L" 305..331).
- FACE [measured decisive]: hint ink span 27 px == bigfont no-gutter 28
  (smfont 22 — refuted). The vendor draws BOTH lines with the big face;
  the TEXTITEM font field 2-vs-3 distinction is not a size difference
  visible at the title.
- PORT DELTA [measured]: pre-t390 our title ink rows were the vendor
  profile shifted EXACTLY -4 (we drew y0+4; vendor y0+8) — the user's
  "tad too high" was this. Post-fix witness /tmp/t392_shots/title.png
  (= work/r1/loop/t392-title-after.png) is row-for-row identical to the
  vendor profile on all seven buttons (btn0 8:11 9:7 10:7 11:39 ...,
  btn4/5/6 pairs at dy4..13 + dy18..27).
- UNDERLINE NEGATIVE [verified, refutes the external vision read]: the
  3x-zoom vision readout claimed the 'L' of "Load" is underlined. Inside
  the button rect the colour census holds EXACTLY {fill (0,0,8), ink
  (215,215,215)} — no third colour — and dy14 white-count is 0 (no
  underline row at any x). '^' is the word joiner (S1/boot.md §1), NOT a
  rendered hotkey underline. The port draws NO underline.
- HOTKEY LAW: bootHotkey gains 'x' -> Quit (the EXITTODOS twin; same
  Title-only shape as 'l'/'s'). Live-loop witness scripts/
  t392_title_witness.sh proves the input path (Esc -> "ui title esc" ->
  process exits); the Alt-chords themselves are unit-pinned only —
  tools/xsend sends one keysym with no modifier state (banked pitfall).
## 8. t393 NEW GAME FULL SCREEN (2026-11-15, D10 "garbled and unusable")

SCREEN LAW: RaceConfig is a full-screen SWITCH, not an overlay (t387 drew it
over the live title frame -> title art bled through the gaps = "garbled").
The draw loop is now `if (st == Title) {title frame} else {newgame frame}`;
mechanical witness: the title button fill (0,0,8) appears 0 times on the
New Game screenshot (scripts/t393_witness.py, our own Xvfb render).

STATE-3 TABLE (windows.txt, re-parsed mechanically — every record whose
STATE field contains token "3"): NEWGAMEWND TYPE 18 (334,12)-(488,364);
GALAXY_MORE/PLAYERS_MORE/DIFFICULTYMORE TYPE 0 msg 501/503/505 (bottom row
7-122/131-246/255-370, y 381-472); Player^Color (379,381)-(493,419) MSG 0;
RACELIST TYPE 10 (502,45)-(632,372) SF 7; COSMOSWnd TYPE 2 STATE "4 1 3 7
13" (the map viewport is REGISTERED in state 3 -> the starfield backdrop is
the window table's own law, drawn with the campaign's starScreenPos
projection over the live built galaxy); LOADSCREEN also lives in 3. The
rail children list 3 too but DO NOT PAINT on this screen (user-supplied
original shows no rail): STATE-list membership = registration, not paint.

BEGIN NEW GAME: NOT windows.txt (STARTGAME TYPE 30 is STATE "1 12" — cited
negative). Rect (494,373)-(639,472) is a CITED MEASUREMENT off the
user-supplied original capture (capture->screen = minus 1; anchors:
GALAXY_MORE x0=7 lands exactly on the bevel boundary, bevel census row
y=430 hits screen 123/247/371/493 at every windows.txt child right edge).

RACELIST ROW LAW [measured]: THREE-slot scroll window (silver-ring bands
screen 49-153/157-262/266-372, pitch 108, full-pitch hit slots) + 16x16
arrow squares (616,47)-(631,62) / (616,356)-(631,371). PORTRAITS = named
seam (t391 7racesel witness still weak): grey disc + dipName stands in.

TEXT LAW: species name green (0,142,69) rows 18-27 centred NEWGAMEWND;
"Player Species" (static.txt //153) white rows 16-25 centred RACELIST;
lore = static.txt //154 "The %s %s" x newgame.txt line N+1 (specnum order,
21 fragments, EOF 0x1a; loadNewgameLore refuses otherwise), greedy wrap
into (334,258)-(488,330); summary = static.txt //168 template words 155-
167, lines at y 327/340/353 pitch 13 centred x 170. dipName leading "the "
is stripped ("for the Minions" header + //154's article would render "The
the Minions are ...").

WORD->VALUE LAW: density words 155-159 ride the t78 MEASURED ladder
(Average 50 / Dense 75 / Very Dense 100 / Vacuous 15 / Sparse 25, cycle
order mapgen.md OQ-012(a)); species words Three..Seven (3..7); atmosphere
Peaceful/Neutral/Hostile (0..2, default Neutral = measured on the original
capture). Wheel click = advance one rung (*_MORE semantics, SENDMESSAGE).
APPLYING settings to the live campaign is the named SEAM (buildCampaign
already ran; Begin prints density/species/atmosphere/species-pick and
enters play with the built galaxy).

DIAGNOSTIC: runTitleScreen prints `ui window WxH (logical 640x480)` (+
" <- SCALED") — the Athens report's 512x384 window (0.8x) is what made the
bottom row clip; the law rects all FIT 640x480 (pinned). Scale LAW = t394.

PINS: tests/test_newgame_t393.cpp x7 (fit-640x480 assert, cited rects,
slots/arrows, ladder+words, //168 template, REAL newgame.txt read incl.
refusal paths, wrap law). Witness: scripts/t393_newgame_witness.sh (click
path Title->New Game->wheels->select->arrow->Begin->campaign, stdout
routing lines) + scripts/t393_witness.py (13 mechanical checks, RUN WITH
~/tools/revenv/bin/python — repo .venv has no PIL). Screenshots graded by
the USER: work/r1/loop/t393-{title,newgame,newgame-set,after-begin}.png.


## tSPEC-1 BEGIN-PRESS PLAYER-SPECIES LAW (2026-11-27; full derivation
## docs/re/_wip_tSPEC1.md S1-S5)
SUPERSEDES the "APPLYING settings ... named SEAM" paragraph above (stale since
tNG-B B4): the Begin handoff (NewGameSettings) is stars/owners/gov PLUS
species, and main.cpp rebuilds play from it.
VENDOR LAW [verified disasm]: word[win+0xb3] (hiword alias of dword[win+0xb1])
is the SELECTED RACE ROW; window-init 0x52c8c sets it to 0 (Minions). The
RACELIST click arm 0x52d6c stores the clicked row and calls FUN_00022ce4
(state=0x12e10, ebx=row, edx=count); inside, the PLAYER branch (k==0, 0x22f8d
mov bl,[esp+0x10]) uses that word with NO rand - AI k>0 draw rand%21 with a
distinctness scan vs byte[raceRow+7] (0x22fba..0x22fed). FUN_0003e6bc stores
the specnum at race-row+7 (state+6+k*0x1ee; row+0 = owner idx). Begin's
worldgen FUN_000238e8 (call 0x52a67; per-star loop 0x23a2a..0x23d22) indexes
the home TABLES 0x88f90/0x88fe4 with byte[race-row+7] (0x23aeb mov dl,[eax+7]
-> T1/T2 picks 0x23aee/af1) = the tPL-D1 home size/terrain law (income-law.md
85/85). The species-COUNT arm 0x52e58 passes the SAME word[+0xb3]: count
clicks never move the player's species.
PORT [shipped tSPEC-1]: title.cpp Begin press feeds scrollOffset+selSlot into
newGameSettings(..., playerSpecies); main.cpp buildCampaign prefers
apply->species on the handoff leg (CLI --species stays authority elsewhere);
live line prints species + new "newgame home <star> cells N row R".
PINS tests/test_species_pick_tspec1.cpp x4; mutations M1-M3 scripts/
tSPEC1_mutate.sh ALL CAUGHT (restore md5-verified x3). WITNESS scripts/
tSPEC1_species_witness.sh rc=0: default run species 0 home 73/row5 (Minions),
RACELIST-click run species 19 home 45/row7 (Chamachies) - same seed, same
star, different TYPE. Residues (documented defaults): AI species draw stream
(port roster-first mapping vs vendor rand%21 - same distinctness law, tables
key on specnum only); race-row stat nudges 0x22ff8.. unmodelled (no consumer
identified).
