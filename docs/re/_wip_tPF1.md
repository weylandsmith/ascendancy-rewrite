
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
