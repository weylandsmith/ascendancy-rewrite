# tWIN-1 (D32 third leg) — eject-to-title opens a SECOND window; WIP log

## W1 DEFECT LOCATED IN SOURCE (2026-11-27, before any runtime probe)
Candidate cause (1) from the assignment is TRUE verbatim:
- ui.h:34-55 law: `runTitleScreen(..., NewGameSettings* newGameOut = nullptr,
  void* windowIn = nullptr)` — windowIn is the LAST (12th) param.
- main.cpp:676-684 call passes ELEVEN args:
  `runTitleScreen(dataRoot, entryState, frames, &terr, &handedWindow,
  savesDir, audio.get(), camp.get(), &rosterForUi(o), &loreForUi(o),
  &newGame)` — handedWindow is passed as `windowOut` (5th), NEVER as
  `windowIn` (12th). windowIn defaults nullptr.
- Consequence chain (title.cpp:138-143): windowIn==nullptr -> winOwned=true
  -> SDL_CreateWindow("Ascendancy") -> a SECOND live window on every title
  re-entry. The handed-back window W1 survives UNDESTROYED
  (ui.cpp:3841-3843 handOff keeps it alive; title.cpp:1513 only destroys the
  window IT used) -> zombie W1 shows the last campaign frame forever.
- Every eject adds exactly one window: loop iteration 2 = 2 windows, etc.
- The tESC1 witness is blind to this: it greps LOG LINES only; events sent
  to either window land (SDL dispatches events for all the process's
  windows; the title loop does not filter by window id) -> all legs pass
  with two windows. Window COUNT was never asserted.

## W2 Symptom mapping
- "opens a new window" = W1 exactly.
- "UI elements don't get drawn in some windows" = the zombie W1 has NO
  renderer (ui.cpp:3837 SDL_DestroyRenderer runs BEFORE the handOff check);
  X Expose repaints of W1 are never serviced -> stale/garbage content.
  [inferred from cited code sites]
- "hover corner pops escape art in another window" = separate-citable
  symptom, BANKED UNRESOLVED per assignment (fix window count first).
  Note: the campaign corner overlay (ui.cpp:3793-3811) blits into the
  campaign's OWN renderer only; with two windows the user-visible bleed is
  plausibly the unserviced W1, but NO mechanism is claimed yet.

## W3 Fix shape (to apply AFTER repro)
main.cpp re-entry call must pass `handedWindow` in the windowIn slot
(12th arg). Title already handles reuse (title.cpp:138-145 SetWindowTitle
path; renderer is created per visit at 161 so no rebinding skip — candidate
cause (3) is FALSE at source). Then assert ONE window across the whole
session: instrument line 'ui windows N' via SDL_GetNumVideoWindows at the
title + campaign entry points (assignment-sanctioned instrument shape).

## W4 Repro — EXECUTED, DEFECT CONFIRMED (pre-fix)
scripts/tWIN1_window_witness.sh on the pre-fix build:
  CHECKPOINT map: windows=1 (0x200008 "Ascendancy rewrite (P5a)")
  CHECKPOINT title-after-eject: windows=2 -> FAIL
    0x200012 "Ascendancy"                    <- the new window (title's)
    0x200008 "Ascendancy rewrite (P5a)"      <- the zombie (campaign's)
Exactly W1's predicted shape: one extra window per eject, the handed-back
window never destroyed (title.cpp:1513 destroys only the window IT used).

## W5 FIX SHIPPED (main.cpp:684-692)
The re-entry runTitleScreen call now passes `handedWindow` as the 12th
(windowIn) arg. One-line behavioural change + cited comment. Rebuild clean.
POST-FIX WITNESS rc=0: windows=1 at ALL FOUR checkpoints, and the id is
0x200008 at every checkpoint — the SAME X window for the entire session
(title title "Ascendancy" / campaign title "Ascendancy rewrite (P5a)"
alternate on it via SDL_SetWindowTitle). tESC1_eject_witness.sh re-run
rc=0 (candidate cause (2) REFUTED: run carried the tNAME-1 clock seed
190717881, all four legs still pass).

## W6 Pins + mutations
tests/test_windowcount_tWIN1.cpp x2 (CMakeLists entry ADDED):
 (1) eject_reentry_passes_handedWindow_as_windowIn_tWIN1 — balanced-paren
     extraction of the call's ARGS (comments stripped first, tESC-1 M1
     law), handedWindow must be present AND after the last depth-0 comma;
     anti-vacuity: the word occurs >=2x in the file so a file-wide grep
     could not substitute for the extraction.
 (2) title_reuse_and_eject_handoff_chain_intact_tWIN1 — the windowIn cast
     + winOwned gate sits within 400 B of the create (gate-neuter caught),
     and the ui.cpp handOff trio stays wired.
Suite 625 -> 627/0/0. scripts/tWIN1_mutate.sh M1-M3 ALL CAUGHT:
 M1 drop the 12th arg (= the original defect), M2 slot poisoned with
 nullptr (arg count preserved, runtime bug back), M3 winOwned gate ->
 true. TRAP hit+banked: the M1 apply-guard grepped 'handedWindow);' which
 the runCampaignUi call ALSO contains -> false "NOT APPLIED"; guard must
 anchor on '&loreForUi(o), &newGame);'. Trap hit earlier and avoided:
 window-count grep must be PREFIX ('"Ascendancy') not exact-quoted, or
 the zombie's different title escapes the count.

## W7 Disposition of the three candidate causes
 (1) TRUE verbatim — fixed, pinned, witnessed (above).
 (2) REFUTED — tESC-1 witness with the random clock seed passes unchanged.
 (3) FALSE at source — title.cpp creates a FRESH renderer per visit
     (title.cpp:161) even when reusing the window; no renderer-rebind skip.
     The "elements don't get drawn" half is the ZOMBIE WINDOW (alive,
     renderer destroyed at ui.cpp:3837 before the handOff check) whose
     Expose repaints go unserviced — that half is now impossible because
     the zombie can no longer exist.
 Hover-art-in-the-other-window: BANKED UNRESOLVED (the other window no
 longer exists; if the user still sees bleed on a single window, that is a
 NEW defect report, not this one).

## W8 Ledger
No OQ row touched (D32 defect queue; open=[016,019] unchanged, honest
negative for the ledger).
