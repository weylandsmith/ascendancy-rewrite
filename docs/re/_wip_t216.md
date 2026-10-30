# _wip_t216 — sitting adjudication ONLY (honest idle-wait)

## S1. TRIGGER-A: byte-identical a THIRD consecutive iteration
scripts/r214_triage.py RC=0 (single triage call), plus an independent stat+md5
pass in-session (different code path, same numbers):
  ns_mtime   1793294532100000000 == baseline  (True)
  size       5,721,578,066       == baseline  (True)
  tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee == baseline (True)
  => sitting delta: False.
Zero dosbox/ascend.exe comm-class processes (grep of /proc/*/comm — the t214
pgrep -f self-match trap avoided a second way). work/r1/caps absent. No game
mount. Sitting script scripts/r1_t85g_sitting.py correctly NOT run (t152 trap).

## S2. Save-axis corroboration (t215 law) — idle confirmed, with a precision fix
`find /home/hrethric -xdev for *.sav/*.gam` (1409 files), newest by %T@:
  1793294530.108  2026-10-29 13:22  work/r1/playcap/save/41.sav
  1793294520.040  2026-10-29 13:22  work/r1/playcap/save/60.sav
  ... (59/58/57 at 13:21/13:22)
PRECISION FIX to t215 S1: the newest save by ns is **41.sav** (13:22:10.108),
not 60.sav (13:22:00.040) — t215's claim was minute-resolution-imprecise.
The law's conclusion is unchanged: both saves sit at the last sitting's end,
BELOW the timeline baseline ns (1793294532.1 == 13:22:12.1), zero saves
modified since 2026-10-29 18:00. The save axis shows no play the capture
pipeline could have hidden. Future no-sitting reports should name the save by
full ns, not wall-minute.

## S3. Writer-population census reproduced (fd-level, t215 method)
/proc/<pid>/fd grep for live-timeline.jsonl, same five processes:
  27772 (bash wrapper, ppid 1)      writer_fd=0
  27774 (python3 child of 27772)    writer_fd=1
  260988 (ppid 1, up 1-19h)         writer_fd=1
  290953 (ppid 1, up 1-06h)         writer_fd=1
  292085 (ppid 1, up 1-05h)         writer_fd=1
EXACTLY four writer fds, stable across two independent iterations — the writer
population is not drifting (no new orphans spawned since t215). Orphan
retirement remains a standing USER ASK (supervised-session decision; research
iterations must NOT kill watchers).

## S4. Ledger outcome — nothing closed (strict-close honored)
No sitting => no new witness class => OQ-016 clamp witnesses and OQ-021
comparator firing remain unobservable. Per the t212 law nothing was
re-censused beyond the two adjudication axes above, and per t213 S7 no static
route was re-trod. No OPEN-QUESTIONS row touched this iteration (the t215
STATUS lines stand); no re-statement of any banked number (t214 claim-safety
audit unaffected). Honest negative: THIS ITERATION PRODUCED NO EVIDENCE
AGAINST IDLE AND NO NEW EVIDENCE FOR ANY LEDGER ROW.
