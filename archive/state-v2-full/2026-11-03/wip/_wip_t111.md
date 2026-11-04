# t111 working notes — sitting watch + capture-launch readiness

## W1 Sitting watch (the assigned task) — NEGATIVE, honest
Measured this session (fresh, not inherited):
- `work/r1/playcap/live-timeline.jsonl` mtime `2026-10-26 15:44:01.304` size
  5691796463 — byte-identical to the t110 reading. NO new sitting.
- `work/r1/playcap-*` newest dir `playcap-20261014-224611` (unchanged; no
  dir created since 2026-10-14).
- `ps`: no `dosbox-x` process anywhere on the host. Running: `Xvfb :9`
  (11 d), `x11vnc -display :9 -localhost -rfbport 5910` (11 d),
  `scripts/r1_playcap_watch.py work/r1/playcap --no-exit` (1 d 13 h, pid
  27772/27774) — the collector is alive and would have caught a sitting.
=> `scripts/r1_t85g_sitting.py` NOT run (nothing to adjudicate). Idle watch
   count = 1 (t110 was a stop-report deliverable, not an idle watch).

## W2 NEW SIGNAL the watch infrastructure produced — user is trying to reach the capture display
`work/r1/vnc/x11vnc.log` (mtime 2026-10-27 17:30) shows EIGHT client
connect bursts TODAY: 08:02, 08:07, 10:21, 10:26, 11:26, 12:10, 12:11,
13:49, 13:52, 17:30 — each burst is the client requesting
2560x1325 / 3000x1573 against the 800x600 Xvfb ("resize prohibited").
Same pattern exists on earlier days in the same log.
Cross-checks, all NEGATIVE for a play attempt:
- no `playcap.conf` / `dosbox.out` newer than 2026-10-26 16:00 anywhere
  under /home/hrethric, /tmp, /var/tmp (maxdepth 3). A
  `scripts/r1_playcap.sh` launch would have created `work/r1/playcap-<ts>/`.
- `~/.bash_history` mtime 2026-10-13 (not written since; not conclusive).
- no new slots under `work/r1/playcap/save/` (newest 60.sav 10-26 15:43).
[inferred] Someone is opening the capture DISPLAY but the game is never
launched. This is the shape of a failed launch, not of a refusal to play.

## W3 LAUNCH DEFECT (measured) — the script's DISPLAY default cannot work on this host
`scripts/r1_playcap.sh:24` is `DISPLAY="${DISPLAY:-:0}"`.
Host facts (measured, this session):
- `/tmp/.X11-unix/` contains EXACTLY ONE socket: `X9` (Oct 16 15:38).
- `DISPLAY=:0 xdpyinfo` -> "unable to open display :0". `DISPLAY=:9` -> OK
  (X.Org 12101016, 800x600).
- `dosbox-x` IS on PATH (/usr/bin/dosbox-x); scratch
  `work/r1/game/ascend.exe` present (587475 bytes) — the script's two
  preflight checks pass, so a bare invocation proceeds and then dies inside
  dosbox with no slots and no diagnostic the user would connect to the game.
- docs side: `docs/re/stop-report.md:84` says only "DISPLAY defaults to :0 —
  run on your own screen"; `docs/BLOCKED.md:347` says "user's own DISPLAY".
  Neither records that :0 does not exist here and that the working display is
  `:9` fronted by x11vnc on `localhost:5910`.
Fix applied (scripts/ only; game/ untouched): probe `/tmp/.X11-unix/X*` when
DISPLAY is unset instead of assuming :0, and print the VNC endpoint.
Verification: see W4.

## W4/W5 RESULT — harness self-test PASSED (real run, 2026-10-27 21:09-21:10)
`TL=90 bash scripts/r1_playcap.sh` (no DISPLAY env) executed for real on
Xvfb :9 under the t111 DISPLAY-autodetect. Verified from actual output:
- banner printed `display=:9` (autodetect resolved the single socket; the OLD
  script would have used :0 and died).
- 9 ring slots captured to $OUT/save; live watcher wrote 213 KB
  live-timeline.jsonl; offline analyzer ran: `41.sav t=1131 T=50 score=0
  sel=0x00 rank=65535 in_game=true`.
- dosbox exited on -time-limit (90 s), `timeout+30` wrapper held, watcher
  reaped, scratch ring files work/r1/game/[0-9][0-9].SAV mtimes UNCHANGED
  (selftest dir = the game's savedir under captures; pristine scratch ring
  never touched). Shared work/r1/playcap/live-timeline.jsonl mtime UNCHANGED.
- artifact kept for forensics but RENAMED `work/r1/playcap-20261027-210912`
  -> `work/r1/selftest-t111-playcap` so a future sitting-watch cannot mistake
  an agent self-test for a user capture (watch signal #1 is playcap-<ts>/).
WATCH-HYGIENE LAW (measured): an IDLE boot still yields slots with
`in_game=true` and `T=50` (resume-to-title defaults; score=0, sel=0).
`in_game`/`T>0` alone does NOT prove a sitting; the durable signal is mtimes
advancing + score/star movement across slots.
CONCLUSION [inferred from W2+W3+W4]: the capture harness is now launch-ready
end-to-end; the likely reason no capture landed since 10-14 despite VNC
clients connecting today is the :0 default. User-side fix:
  VNC to localhost:5910, then in the repo run: bash scripts/r1_playcap.sh
