# t404 WIP — LASER-SOUND REGRESSION + INPUT HYGIENE (D13)

## F1 Root cause (read, cited)
rewrite/src/ui/ui.cpp:343-352 — the map-click branch inside COSMOSWnd plays
`audio->play("laser01")` unconditionally on EVERY left click in the map rect,
star hit or not. audio.md §5 itself labels the laser01-on-map-click pairing a
DOCUMENTED PORT CHOICE (not vendor law); it is now a user-visible regression
(D13: "clicking anywhere in the galaxy map makes a laser-fire sound").

## F2 Sound law already banked (no new probe needed for the silence call)
- audio.md §6.5 + §6.6 (t395): windows.txt SOUNDCHANNEL = {0 x118, -0 x1}
  over 119 records — the shipped table carries NO per-button sound id.
  Which sample the vendor played per button class is UNCITED.
- soundfx.txt: laser01 is manifest name index 2 (line 8), span 45277 B =
  band2 (1 voice) per the header-pair law (audio.md §2.1/§2.2 census).
  Nothing in help.txt/soundfx.txt ties laser01 to map clicks; there is no
  fire-order interaction in the port (no combat UI exists).
- Therefore per the queue row: laser01 loses its play site until a real
  fire-order interaction exists; map clicks play NOTHING (dead-area silence
  is the conservative reading of the all-zero SOUNDCHANNEL census — the
  table gives no id for any map child).

## F3 play( site sweep (grep of rewrite/src, complete: 5 call sites)
1. ui.cpp:209 bang01 iff a NEW event line contains "captured" — keep,
   cited-as-documented-port-choice audio.md §5; event sound, not a click.
2. ui.cpp:305 click08 on NEXTTURN press — keep (user HEARD and accepted
   the click sound, D11 audio line); documented port choice §6.5.
3. ui.cpp:348 laser01 on every map click — REMOVE (this iteration).
4. title.cpp:771 click08 on every title-menu button press — keep, cited
   §6.5 documented port choice.
5. audio.cpp:176 — the definition, not a site.

## F4 Fix shape
Centralise the per-interaction sound choice as a PURE lookup so pins are
headless: `sfxForPress(UiPressSite)` in ui/audio.h — MapClick -> nullptr
(silent), RailButton/NextTurn/TitleButton -> "click08". Rail press gains
click08 per the queue's pin list ("rail click click08") — symmetric with
title buttons, same uncited-id seam, documented port choice.

## F5 Adoption: tools/winpos (ELF binary) untracked; .gitignore lists the
other three tool binaries but not this one (winpos.c tracked in be2cacb).
Add `tools/winpos` to .gitignore in this commit.
