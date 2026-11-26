
# tPF-1 TIME CONTROLS (D28 P7) — working log
## P1 DIAGNOSIS (2026-11-25, this iteration)
(b) "game exits after 20 single-day advances" = THE FLAG PATH, MEASURED:
  - scripts/tPF1_repro_exit.sh: README-exact interactive launch (`--ui`, NO
    --campaign => turns=0), seed 5, 30 NEXT TURN clicks at (511,67):
    VERDICT ALIVE, 30 clicks logged. The cap (ui.cpp:1215
    `turns>0 && played>=turns`) CANNOT fire with turns=0.
  - headless --campaign 60 seeds 1/5: "no victory after 60 turns" — no
    hidden game-over at day 20 either.
  - => the user's build was launched with `--ui --campaign 20` (the repo's
    own witness scripts all use `--ui --campaign 1`; PLAYTHROUGH.md:76 shows
    that shape). The cap is a HARNESS instrument, not play law. Fix: the cap
    must announce itself (never an anonymous exit) and stay OFF in normal
    play. REPRO script kept as the pin-backing witness.
(a) "advance until something happens" = NEXTTURNCONT (windows.txt ln556-569
  VERBATIM: TYPE 25, rect 557,52-632,82, SHAPEFRAME 66, SENDMESSAGE 8,
  BUTTONSTATE 0). VENDOR LAW text verbatim (help.txt help 1next2, ln496-509):
  "This button is used to advance time continually until an event requiring
  your attention occurs. When such an event occurs, time advancement will
  automatically stop, and you will be notified of the event."
  The t394 port shipped this button INERT (ui.cpp:1018 seam line). The
  vendor msg-8 handler internals (which events count) are NOT captured ->
  the attention predicate is a NAMED SEAM (TPF1-A): stop iff a NEW event
  line is player-relevant ("VICTORY" prefix or contains "player") or has a
  notification sfx per the cited t404 sfxForEvent law (audio.md §5).
## P2 PORT (this iteration)
- ui.{h,cpp}: nextTurnContAttends(text) free fn (the seam predicate, cited);
  click kNextTurnCont -> contMode latch ON (pump advanceOnce at the banked
  250 ms autoplay cadence, ui.cpp:1211); pump stops on attends/victory/over
  with printf lines "ui cont advance start|stop <turn> <reason>"; a manual
  NEXT TURN press cancels contMode.
- cap notice: the ui.cpp:1215 exit path prints "ui turn cap N reached" so a
  --campaign N launch never dies anonymously.
- ui.h: nextTurnContAttends exported (seam TPF1-A documented there).
- PINS rewrite/tests/test_timecontrols_tPF1.cpp x5 (rect vs windows.txt +
  no-hit-overlap; VICTORY-prefix-not-substring; player-relevance incl the
  "owner 0 " prefix leg and the owner-10 negative; sfx leg bang01/"captured";
  source-text wiring: latch, cancel, pump predicate+cadence+no-spin, cap
  notice, t394 seam printf gone). SUITE 538 -> 543, 0 failed.
- MUTATIONS (work/tPF1_mutations.py, sequential + md5-verify after every
  revert): M1 prefix->substring / M2 drop owner-0 / M3 owner-0 loosened to
  "owner" / M4 drop sfx leg / M5 cont cadence 250->500 (2nd occurrence) /
  M6 cancel removed / M7 cap notice removed — ALL 7 CAUGHT, md5 restored.
  M1 first sweep SURVIVED because the counter-example said lowercase
  "Victory" (find can't match it either); lesson: a case-sensitive prefix
  pin needs an UPPERCASE mid-string counter-example. Fixed pin, re-swept.
- WITNESS scripts/tPF1_witness.sh VERDICT PASS (seed 5, plain --ui, Xvfb :99
  killed BY PID): 3 manual clicks logged, NO pump lines before the
  NEXTTURNCONT click at (594,67); 16 "ui cont advance tN" ticks with no
  further clicks and the app ALIVE; manual NEXT TURN -> "ui cont advance
  cancelled" and tick count frozen (16->16 over 2 s).
- REPRO scripts/tPF1_repro_exit.sh (part b): plain --ui seed 5, 30 manual
  NEXT TURN -> ALIVE, 30 clicks logged. The D28 "exits after 20 days" was
  a `--ui --campaign 20` launch hitting the harness cap; cap now prints
  "ui turn cap N reached (harness instrument, not game law)" before exiting.
- NO OQ ROW TOUCHED (the time controls track no OPEN-QUESTIONS row; D28 is
  a defect queue, not the ledger) — honest negative under strict-close;
  open=[016,019] unchanged.

## tPF-1b LANDED 2026-11-26 (D28 P7(b) CLOSED AS LAUNCHER-FLAG, MEASURED
END-TO-END ON THE BEGIN PATH; cap line re-ordered + prefixed; no OQ row
touched — D28 is a defect queue; open=[016,019] unchanged)

STEERING NOTE (user evidence: launcher console prints "ui ok: turn 20"):
that line is ui.cpp runCampaignUi clean return; reachable via the cap ONLY
when turns>0, which on the Begin path is exclusively o.campaign
(main.cpp:665). Two-branch repro executed WITHOUT the user.

REPRO scripts/tPF1b_ab_repro.sh (Xvfb :96, Begin-built both legs: neutral
click 320,60 -> FRESHGAME 318,295 -> BEGIN 566,422 (kBeginNewGameBtn
menulaw.h:72 494,373-639,472) -> intro dismiss 320,450; log lines
"ui raceintro dismiss -> campaign" + "newgame live stars 50 owners 5 gov 1"
present in BOTH app logs — the Begin path is genuinely exercised):
 - A: --ui --campaign 20, xsend NEXT TURN (kNextTurnBtn 474,52-548,82) x20
   -> 20 clicks logged, process EXITED exit_code=0 at press 20, log carries
   "ui ok: turn 20" then (post-fix) "HARNESS-CAP: turn cap 20 reached
   (harness instrument, not game law; play = --ui without --campaign)" as
   the LAST line.
 - B: --ui ALONE, 40 presses -> ALIVE at turn 40, 40 clicks logged, ZERO
   cap lines, no game-over/victory line.
VERDICT: A prints + B survives => the day-20 exit IS the launcher flag,
not game law. The steering's third branch (B also dies at 20 => instrument
quit paths) did NOT trigger; no quit-path instrumentation needed.

SHIP: ui.cpp — cap arm now LATCHES capFired=turns (ui.cpp:1568 capFired
assignment; declaration ~:337); the announcement prints ONCE after
"ui ok: turn %d" at the return site (~:3698) with the HARNESS-CAP: prefix
and names the fix ("play = --ui without --campaign"). "ui ok: turn N" is
KEPT — gate.sh greps it at 5 sites (562,593,632,670,721). README.md Run
section: PLAY = --ui callout added.

PINS test_timecontrols_tPF1.cpp timecont_wiring_tPF1 extended: cap arm
window (1200 chars — the 500-char window was the round-1 FAIL: the tPF-1b
comment body pushed the assignment past 500; widen-the-window trap) pins
"capFired = turns;" + "quit = true;"; ui-ok tail window pins
"HARNESS-CAP:" + "capFired > 0" + "txt.release()" (last-print-before-
teardown); single-occurrence pin src.find==rfind("HARNESS-CAP") bars a
second in-loop print (comments must NOT contain the literal — round-1 trap:
a comment word tripped it, de-literalized). SUITE 590/0/0 (count unchanged;
pins extended in place). MUTATION scripts/tPF1b_mutate.sh M1 latch-removed
/ M2 mid-run-print re-added / M3 prefix-stripped ALL CAUGHT, md5-verified
restore 2939be4df673c5812b53410425c4e018.

--campaign 20 NAME AUDIT (step 3(iii)): NO repo script hardcodes
--campaign 20 (grep across scripts/ tools/: witnesses use 1/3/4/40/65/1200/
1500/1600; ui_vendor_shot.sh 40, ui_input_check.sh 4, tRSV2p 30, tRSV2w
400, record_playthrough 3/1200/1600, gate 1/3/65/600-path/1500/1600). The
literal existed only in docs prose (DECISIONS.md:799, STATE.md:960) and my
new repro. => the user's "--campaign 20" is NOT copied from a repo script;
it is hand-typed or from a private run-config. The user should check his own
launcher/desktop-entry; repo-side, every --ui witness pairs a --campaign N
that exits after N days, so copying one of those lines into a launcher
reproduces the class at whatever N it carries.
