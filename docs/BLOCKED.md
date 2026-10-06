# BLOCKED.md — v2 (decision history in archive/ralph-v1/BLOCKED.md)

## Standing decision (NOT re-openable)
Option C hybrid, B-priority, chosen by the user 2026-10-04: data-first work
plus R1 runtime capture via dosbox-x save states, no cadence limit (abolished
2026-10-05). Full rationale and the refuted A/B fork: archive/ralph-v1/BLOCKED.md.

## Current blocks
### OQ-021 — Control-victory threshold: >1/2 or >=2/3? (user decision; default in force: >1/2)
The vendor's own artifact contradicts itself: extracted end-ctrl.txt line 2
(header comment, the condition's own title) says "over half the galaxy",
while its enddesc/congrat prose says "spans over two-thirds" / "more than
two-thirds of the stars" (verified 2026-10-06g by direct read). The threshold
is code-side (numeric constant in the end-condition evaluator); the .txt has
no numeric grammar, filename refs exist only as runtime stack strings
(eventwnd.cpp region; static xref of the data string = 0 hits), and locating
the comparator statically needs obj1 call-edge recovery — long horizon, not
this loop. DEFAULT IN FORCE: rewrite keeps `mine * 2 > total`
(rewrite/src/game/campaign.cpp:738), citing the header-comment title over
display prose. What would settle it: (a) user ruling that
marketing prose or the code comment wins, or (b) Ghidra obj1 call-edge
recovery finding the evaluator, or (c) a capture where the player crosses
50-66% and the game does/doesn't fire end-ctrl. Item STAYS OPEN per strict-
close policy; other workstreams unaffected.

## R1 runbook (mandatory safety invariants — a run without them is a bug, not research)
Route: scripts/r1_savestate.sh (+ r1_sav_scan.py per-run base; never hard-code
B). Deep capture: scripts/r1_deepcapture.sh. Invariants (enforced statically
by gate 3n):
- dosbox NEVER mounts pristine game/ — scratch copy under work/r1/ only
- headless-safe config: output=x11 under Xvfb for captures needing vblank
  autosave (host-clock autosave is checked at vblank — dummy video = no
  saves); nosound=true; stdin=/dev/null
- -time-limit always; all output bounded (head -c); DOSBOX RULE in STATE.md
- kill ONLY pkill -x dosbox-x
- CADENCE LAW (measured 2026-10-06m, 19 runs): host-clock autosave period is
  a CONSTANT 10 s (median gap 10 s in every run's save dir). Turn advance is
  NEVER automatic: 14 idle runs (zero landed clicks) hold turn constant for
  the whole run. Each NEXTTURN click that lands ON THE STRATEGIC MAP advances
  exactly +1 turn (r1ad-144225: 0->1->2; r1deep-230146: 8 scheduled clicks ->
  7 boundaries, the missing one landed while a modal screen was open — modal
  views SWALLOW clicks, see 06f/06j). Schedule by TIME and verify by TURN
  number in checkpoints, never by counting slots: at 10 s autosaves a turn
  may straddle 1-3 slot copies and slots rotate 41..60 cyclically.
- exit codes: 0 = base derived / upgrade formulas; 1 = normal negative,
  record ONE line in STATE.md, no in-turn retry; 2 = harness bug, fix it

## Closed-as-dead capture routes (do not resurrect; full trail in
## docs/REFUTED-ROUTES.md)
- external ptrace tracer: dosbox-x 2025.02.01 makes itself untraceable
  (ATTACH/SEIZE EPERM, maps EACCES by t+2 s) — dead on this box
- dosbox-x -break-start: superseded by save states AND carries the EOF-spam
  trap; do not pilot
- static absolute-base schemes: four refuted, fifth forbidden — the runtime
  pointer law (OQ-011 CLOSED) is the answer
