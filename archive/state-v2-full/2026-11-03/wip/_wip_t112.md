# t112 WIP — sitting watch (idle turn #2), run 2026-10-27 ~21:20 EDT

Assignment (STATE.md t111 handoff): sitting watch ONLY; check (1) new
capture dir or shared-timeline mtime advance, (2) user decision on
stop-report §3, (3) else gates + commit.

## Observations (all measured this session)

1. NO NEW CAPTURE. Newest work/r1/playcap-<ts>/ dir is still
   2026-10-14 22:46 (playcap-20261014-224611). Only other artifact:
   work/r1/selftest-t111-playcap (t111 self-test, correctly excluded).
2. SHARED TIMELINE UNCHANGED. work/r1/playcap/live-timeline.jsonl
   mtime 2026-10-26 15:44:01.304, size 5691796463 B — byte-identical
   stamp to the t111 check. No new sittings => r1_t85g_sitting.py
   correctly NOT run.
3. NO dosbox-x process. Watch infra alive: Xvfb :9 (since Oct 16),
   x11vnc :5910, r1_playcap_watch.py --no-exit (pids 1196/1207/27774).
   Negative is trustworthy.
4. VNC TRAFFIC: x11vnc.log (work/r1/vnc/x11vnc.log) bursts today at
   08:02, 08:07, 10:21, 10:26, 10:27, 11:26, 12:10, 12:11, 13:49,
   13:52, 17:30 (resolution-change chatter 2560x1325 / 3000x1573 vs
   800x600). Log ENDS 17:30:18 — i.e. every burst predates the t111
   DISPLAY-autodetect fix (self-test ran 21:09). ZERO VNC attempts seen
   against the FIXED harness so far.
5. FILESYSTEM SANITY (new check, cheap): disk 30% used, 64 G avail —
   rules out "captures fail because the ring filled the disk" as a
   residual defect behind the t111 :0 bug.
6. t111 SELF-TEST ARTIFACT RE-READ (harness-quality, not game
   behaviour): watch.out shows 9 slots 41-49, wall 21:09:27..21:10:45,
   t=1131 flat, DAT_482fb=0/50, rel_nonzero_cells=12 — an unplayed boot
   of a mid-game position, consistent with the t111 hygiene law (idle
   boot => flat turn/score; movement, not in_game, proves a sitting).
   Hygiene law also retro-illuminates the OLD shared timeline: Oct-26
   run shows slots 49-60 all t=1254 flat — idle autosave churn, same
   signature.

## Conclusion

Empty watch (#2 of max 2 per t111 rule). No measurement of game
behaviour => NO ledger row closed (strict-close honest negative). No
banked law falsified. The event the loop waits on is a capture sitting
LAUNCHED AGAINST THE FIXED SCRIPT — user is demonstrably active today
(VNC bursts), so the ball is on stop-report §3: run
`bash scripts/r1_playcap.sh` (picks :9 itself) or hand back the
decision-list answer.
