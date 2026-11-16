# t409 — SPECIAL ABILITY + SPECIES SCREEN (working log)

Brief (STATE.md queue row t409): user "special ability button doesn't even do
anything" + "species screen quite off". Act 1 = windows.txt census for a
special-ability window; disposition per SENDPARAM/help if none. Species:
RACE_1..7 = NEGSCREEN (state 13) clicks per banked law.

## F1 CENSUS windows.txt (extracted/ascend00/windows.txt, 2238 lines, parsed
## record-wise by STATE list) — VERDICT: a special-ability window DOES exist,
## but NOT as a play-state screen.
- STATE-id inventory (TYPE-0/other records, single-state lists): 0,1,3,4,4?,6,
  7,8,9,9,10,12,13,14,16,17,18,18,20 + multi-lists "3 1 7 13" (map controls)
  and "3 2 4 15" (load). NO state id exists for a special-ability screen.
- SPECIALAB record verbatim ln500-516: TYPE 0, PARENT NONE, STATE "1 1",
  474,247-632,277, SENDMESSAGE 5, SENDPARAM1 0, SENDPARAM2 1, HELPINDEX
  1special, TEXTITEM "Special^Ability", SHAPEITEM 1starmap.shp 7. msg 5 is NOT
  a screen switch (t388 table law) — consistent.
- THE FINDING: ln2136 TYPE 22 NAME ABILITYWIN, PARENT NONE, STATE "0" (!),
  60,100-395,355, SHAPEFRAME -1, SENDMESSAGE 0, WINITEMS 0 — plus children
  ABILBUTTON0 ln2152 / ABILBUTTON1 ln2169, both PARENT ABILITYWIN, STATE "0",
  SAME full rect 60,100-395,355, MOUSEFOCUS 1, SENDMESSAGE 50, SENDPARAM1 0.
  Sibling pattern EVENTWIN ln2187 TYPE 23 STATE "0" 60,100-395,355 +
  EVENTBUTTON0/1 msg 50 — the generic code-drawn modal-dialog lib (TYPE 22/23
  = text-modal with 1-2 buttons; same family as HELPWINDOW TYPE 20 +
  HELPBUTTON0..4 msg 50 at STATE 0). STATE "0" is the dialog pool's state tag,
  NOT the intro screen — the dialogs are code-opened overlays (HELPWINDOW is
  opened from play states live, witnessed t-series). [inferred] msg-5 handler
  opens ABILITYWIN as an overlay from state 1.
- msg 50 semantics: every *_BUTTON in the pool family sends 50 p1 0/1.. =
  dialog button N dismiss. HELPWINDOW pattern: N buttons stacked on the same
  rect, button index = item index.
- help 1special VERBATIM (help.txt ln448-463): title "Special Ability"; body:
  "Press the Special Ability button when you want to learn about or use your
  species' special power." button OK msg 0. => the vendor help itself frames
  the button as LEARN-ABOUT-or-USE.
- gizhelp.txt has no per-species ability text (grep 'special' = gizmo items
  only). Species ability TEXT source still to find (race*.dip? static pool?).

## F2 msg-5 HANDLER DECODED [verified disassembly, work/ascend_restored.bin
## base-0, Ghidra x86:LE:32:default+gcc import]. The special-ability button IS
## WIRED in the vendor: msg 50 (the ABILBUTTON dismiss family) and the rail
## path land in a handler at 0x37b14..0x37b69 that OPENS THE PLAYER'S ABILITY
## HELP PANEL:
##   0x37b1e  MOV DL,[0x7458e]            ; player species byte (specnum)
##   0x37b24..0x37b30 EAX = ((DL*31)*8 - DL)*2   ; == specnum*494 record stride
##   0x37b32  ADD EAX,0x12e16             ; race-record base
##   0x37b37  MOV EAX,[EAX+0x19a]         ; race record word @+0x19a
##   0x37b3d  SAR EAX,0x18                ; -> ability INDEX (top byte)
##   0x37b40  PUSH EAX                    ; arg: number
##   0x37b41  PUSH 0x1c8f                 ; pool #7311 = "abil%02d" (file
##                                         0x8483f; the SAME format string the
##                                         gizmo/planitem help openers use)
##   0x37b46..0x37b4a stack scratch buffer -> PUSH EAX  ; topic out
##   0x37b4f  CALL 0x76c79                ; sprintf-style formatter
##   0x37b57  MOV EDX,0x84848             ; pool "help.txt"
##   0x37b5c  CALL 0x33f40                ; open-topic-panel (HELPWINDOW path —
##                                         winmgr.cpp pool context @0x85975:
##                                         "EVENTWIN","ABILITYWIN","HELPWINDOW"
##                                         adjacent literals)
## => LAW: the Special Ability button opens ABILITYWIN — a code-drawn text
## modal (windows.txt ln2136 TYPE 22 STATE "0" 60,100-395,355 + ABILBUTTON0/1
## msg 50) showing help topic "abil%02d" for the PLAYER SPECIES, i.e. the
## help.txt abilNN block verbatim ("<Race> Special Ability" title + body).
## The dialog family (HELPWINDOW TYPE 20 / EVENTWIN TYPE 23 / ABILITYWIN TYPE
## 22, all STATE "0", all buttons msg 50) is the vendor's generic modal lib —
## ABILITYWIN is its dedicated ability instance. The rail button is NOT dead
## in the vendor; the rewrite's NO-OP is the defect.
## NOTE 0x37baf CALL 0x43b50 (the ability-cadence fn) sits in the NEXT
## function 0x37b6a.. (dispatcher on DX: 1 -> 0x43b50 probe; 50 -> 0x37c9c
## leg) — that is the AI/turn path, distinct from this opener.
## ALSO [verified, CORRECTION]: "ABILITYWIN" (file 0x85975) IS statically
## referenced — at 0x55ffb: `MOV EDX,0x85975` (FULL 32-bit address immediate,
## not pool-relative) + `MOV EAX,EBP` + `CALL 0x56d1c` (window-by-name lookup
## in the winmgr dispatcher 0x55xxx), result stored [ESP+0x518], THEN
## `CALL 0x37b14` at 0x56010 (the opener above), then a wait-check
## [EBP+0x489e] and a 0x5526c cleanup call with the handle. THAT is the
## complete msg-5 path: LOOK UP ABILITYWIN BY NAME -> POPULATE it with the
## sprintf'd "abil%02d" help topic for the player species -> wait -> close.
## The earlier my-scan found zero pool-rel immediates because the site uses
## the absolute encoding. The rail button is WIRED in the vendor, cited
## end-to-end.


## F3 SPECIES SCREEN content law [verified, banked sources]:
- Header: static.txt #11 "%d of %d Species Known" (coswnd.cpp pool block,
  extracted/ascend00/static.txt ln50); t252 LIVE witness: species menu
  rendered "3 of 3 Species Known" (ui-runtime.md §6b).
- Rows: race rows with race-colored names + flag icons (t252 vision);
  RACE_1..7 windows.txt rects 474,7-632,37 pitch 39 (ln725..); t252 measured
  DRAWN bands y 61/100/139 pitch 39 (header occupies the top) — campaign-
  state dependent top, pitch stable.
- "Extinct" row text: static.txt #12 "Extinct" (ln53); t252 third row printed
  Extinct = eliminated race (help.txt:775 contact-refused; clicking it only
  highlights, never opens NEGSCREEN).
- Race flag faces: raceflag.shp 21 x EXACTLY 14x24 (t400 §2, already loaded
  in ui.cpp for the rail flags, indexed by specnum).
- Intelligence item: STATE "1 7" (windows.txt ln845) — active in state 7 only
  (railActive already implements this).
- Four large race portraits over the map (t252 vision): art source unmapped
  (lgraceNN class) = NAMED SEAM, do not invent.
- Row click -> NEGSCREEN (msg 1 p1 13) stays a NO-OP (state 13 chrome not in
  the port; t388 known-set law). Honest.

## F5 BUILD STATUS: ui/abilitylaw.{h,cpp} + ui/speciesmenu.{h,cpp} landed;
## Campaign gained ownerCount()/playerKnows()/ownerName() (display-only);
## ui.cpp: SPECIALAB msg-5 opens the ABILITYWIN modal (draw after the
## screen, before RenderPresent; modal swallows Esc/Return/Space/Alt-chords
## and all left-clicks — inside rect dismisses, outside inert); species
## screen replaced: static #11 header centred in RACE_1 slot, known-owner
## rows in kRaceRows[1..6] with raceflag faces + owner-colour names or
## static #12 "Extinct"; species row click logs the NEGSCREEN seam. Suite
## 376->384/0 (test_speciesmenu_t409.cpp x7: parse census 21/14/7 with the
## {0,1,2,3,4,15,18} passive set + Use Ability msg1/Cancel msg0 vs OK msg0;
## titles + abil00 verbatim; rect 60,100-395,355 + full-rect hit incl 6
## boundary probes; charge-line %d/%s incl negative clamp; static #11/#12
## markers via the marker-driven reader; membership/header agreement over
## seeded 2024 x12 turns (flag==specnum law); extinct law (strip owner 2's
## stars -> row reads extinct); read-only accessors no-state-delta x30
## turns two-campaign diff). Seed regression + witness NEXT.

## F6 MUTATION CAMPAIGN: scripts/t409_mutate.py (anchor count==1, revert by
## FILE COPY from /tmp/t409-snap, verdict = run_tests exit code):
## M1 passive-block-gains-use-button CAUGHT; M2 index-census-dropped CAUGHT;
## M3 rect-x1-widened CAUGHT; M4 hit-exclusive-interior CAUGHT;
## M5 plural-law-inverted CAUGHT; M6 negative-clamp-dropped CAUGHT;
## M7 unknown-owner-rows-emitted CAUGHT (membership FAILs :261/:264);
## M8 extinct-law-dropped: first run MISSED — VACUOUS FIXTURE (seed 11 had
## no known owner at turn 1, so the extinct assertion never executed).
## Re-scoped the pin (drive to a known owner — seed 5, contact by ~t9 per
## the witness — strip its stars, require the row FLIP + still exist) ->
## re-run CAUGHT (:298). M9 specnum-skip-law-broken CAUGHT (flag==specnum
## FAILs :268). FINAL: 9/9 CAUGHT, restored suite 384/0.


## F4 IMPLEMENTATION PLAN (as executed):

1. ui/abilitylaw.{h,cpp} pure: parse help.txt abilNN blocks (title text +
   body text + pos) -> AbilityPanel{title, body}; abilityPanelFor(species)
   maps the PLAYER SPECIES to its panel (vendor chain: specnum -> race
   record +0x19a>>24 -> abil%02d -> help.txt; the port's species.cpp roster
   already binds specnum -> SpeciesAbility -> help title).
2. ui/speciesmenu.{h,cpp} pure: speciesMenuHeader(campaign) -> static #11
   format; speciesMenuRows: contacted AI owners in order, dipName colored
   kOwnerRgb[owner], raceflag face specnum-indexed, "Extinct" when the owner
   holds 0 stars.
3. ui.cpp: SPECIALAB press on the map opens the modal overlay (ABILITYWIN
   rect 60,100-395,355, title/body drawn, OK = msg 50 dismiss; click/Esc
   closes; modal eats clicks while open). Species screen: replace the frame-
   only stub with header + rows; keep Esc law.
4. Campaign read-only accessors: playerKnows(owner), aiDipName(owner) or
   expose aiDip_ displayNames — display-only, zero rng (t408 posture).
5. Pins test_speciesmenu_t409.cpp; witness t409_species_witness.sh; seed
   regression; gate + ledger audit. LEDGER: expect honest negative (D13
   chrome rows have no OQ owner).


