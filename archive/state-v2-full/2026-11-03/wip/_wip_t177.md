# t177 WIP — IDLE re-check #64 + INFRA-leg adjudication fix (probe prints a frozen conclusion)

Session start 2026-10-28 07:41:25, HEAD c924ebe (t176), clean tree.

## F1 (measured) — `python3 scripts/r1_idle_probe.py` RC=0 at 07:42:25: (A) NEGATIVE
and adjudicated (A4 watcher ALIVE pid 27774), (B) NEGATIVE, prompt-99 vs prompt-98
digit-stripped delta 0. Timeline mtime_ns=1793043841304000000 / size=5691796463 ==
frozen baseline on both fields (66th consecutive byte-identical reading t111..t177).
So NO trigger fired this session and no sitting exists to adjudicate;
r1_t85g_sitting.py correctly NOT run (t152 law moot).

## F2 (measured, DEFECT) — the INFRA leg asserts a conclusion it never measures
`scripts/r1_idle_probe.py:494-495` prints unconditionally, as a string literal:

    (unchanged 2026-10-27 17:30:18/30114 since t112 => zero connects
     against the t111-FIXED launch path)

while the line ABOVE it (line 491-493) prints the live mtime/size. This session the
two printed lines contradict each other:

    x11vnc.log mtime=2026-10-28 07:37:29 size=30597
      (unchanged 2026-10-27 17:30:18/30114 since t112 => zero connects ...)

Measured from loop logs: iter-97 (07:27:18) and iter-98 (07:33:37) both printed
mtime=2026-10-27 17:30:18 size=30114; iter-99 (07:41:25, THIS session) printed
2026-10-28 07:37:29/30597. So the literal became false ~4 minutes before this session
started and the probe kept printing "unchanged ... zero connects" over it. Same shape
as t156's hole A6 (a rule that lives only in prose/the string, not in code): the leg
TOUCHES the log (os.stat) but does not ADJUDICATE it (no comparison, no baseline,
no accept-count). Verdict-wording risk: a session that trusts the parenthetical
instead of the number reads a changed infra state as steady-state.

## F3 (measured) — what the log churn actually IS, and it is NOT a connect
`work/r1/vnc/x11vnc.log`, 410 lines, x11vnc 0.9.17 pid 1207 (banner line 3,
started 16/10/2026 15:38:35). Normalized event census (sed date-stripped,
`sort | uniq -c`):

    128  Sending rfbEncodingExtDesktopSize for size (800x600) resize prohibited
    128  Client requested resolution change to (WxH)
     10  idle keyboard: turning X autorepeat back on
     10  active keyboard: turning X autorepeat off
      1  incr accepted_client=1 for ::1:53822  sock=11      <- line 90, 16/10 15:39:20
      1  Normal socket connection                            <- line 85, same second

`grep -c 'incr accepted_client'` == 1 for the WHOLE 12-day log, and
`awk '/incr accepted_client/{print $1}' | sort | uniq -c` == `1 16/10/2026`.
Per-day dated-line census: 16/10=119, 17/10=2, 18/10=8, 19/10=2, 22/10=2,
23/10=33, 24/10=19, 25/10=21, 26/10=132, 27/10=50, 28/10=6.

[inferred from those counts] One RFB client accepted on 16/10 15:39:20 and never
disconnected; the 128 resolution-change pairs are that persistent viewer's
ExtDesktopSize chatter (2560x1325 / 3000x1573 — a large desktop window), not new
sessions. The t112 "zero connects" claim is therefore still TRUE as a fact
(accepts==1, all before the idle era) — but it has been true for a reason the probe
never measured, and the probe's stated evidence for it is now falsified on its face.

## F4 (latent hazard) — work/r1/vnc/* can FALSE-ARM trigger (A)
The (A) find sweep (`r1_idle_probe.py:187-201`) arms on ANY file under work/r1 newer
than session start except `work/r1/loop/` and TOOL_ARTIFACTS (`work/r1/.anch-cache.json`).
`work/r1/vnc/` is neither. Its contents are all infra, never a sitting:
dosbox.log, dosbox.pid, playcap.log, session.conf, watch.pid, x11vnc.log,
x11vnc.pid, xvfb.log, xvfb.pid (ls -l, and both capture launchers pin their out-dir
under work/r1/playcap*, not vnc/ — r1_playcap.sh:22 / r1_playcap_vnc.sh:30).
The log churns every few hours (26/10 22:16, 23:25; 27/10 08:02, 08:07, 10:21, 10:26,
11:26 ... 17:30; 28/10 07:37), so a resize landing between the harness writing
prompt/iter-<ts>.log (the cutoff source, lines 172-186) and the sweep running
arms (A) with "capture-side file newer than session start: work/r1/vnc/x11vnc.log"
-> a fresh session hunts a sitting that does not exist. Same class as the t149
.anch-cache.json self-arm. Blinding cost of excluding vnc/: none that matters —
a real play session is caught by the dosbox-proc leg (:161-165), the timeline
content leg (:120-158), and the new-capture-dir leg; a vnc/ log can never carry a
turn-boundary sitting.

## FIX (in progress)
1. infra(): compare against pinned base mtime/size, print accepts (grep -c
   'incr accepted_client') and the last accept timestamp, and state the CHURN-vs-
   CONNECT distinction as measured. Never print an unconditional conclusion.
2. (A) sweep: classify foreign paths; vnc/ infra logs => CAUTION naming what they
   are, NOT armed; any other foreign path still arms.
