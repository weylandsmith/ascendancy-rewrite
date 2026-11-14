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

PALETTE [named seam]: no cited palette exists for the menu .shp libs —
their index sets are disjoint from the t386 title palette TSV (4loadgam
k0: 19 distinct, all 19 absent; 3cfgnew k0: 44 distinct, 31 absent) and
game.pal/logo.pal/subfont.pal are refuted for the title
(title-art.md §4). Chrome renders through a deterministic luminance ramp;
COLOUR fidelity is a named seam, geometry is not. Instrument to close it:
the t386 registration conflict-count method needs a vendor SCREENSHOT of
the load/newgame screens (user-grader artifact) — none is pinned.

Honest negatives / seams:
- An accepted slot prints its pick but does NOT import into a live
  Campaign: the rewrite has no campaign-state importer (Observer is
  read-only by contract, t382). The screen returns to Title.
- The three state-3 wheel buttons ACKNOWLEDGE (print name+msg); setting
  wheel values feeds a campaign-seed seam that does not exist yet.
- RACELIST rows (state-7 RACE_n TYPE 6) are t388 chrome.
- No OQ ledger row moved (queue work; strict-close ledger untouched).
