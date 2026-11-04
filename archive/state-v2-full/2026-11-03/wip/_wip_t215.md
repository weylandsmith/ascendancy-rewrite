# t215 — SITTING ADJUDICATION ONLY (the assigned task) — working notes

Task per docs/STATE.md "## NEXT ACTION": run scripts/r214_triage.py as the one
triage call; if any TRIGGER-A baseline differs, run r1_t85g_sitting.py and mine
the two named witnesses; if NO sitting, write the honest idle-wait line and STOP
(t212 law: re-running a censused instrument without new inputs is net-negative).

## S1 — TRIGGER-A: NO SITTING (verified, scripts/r214_triage.py RC=0)
All three baselines byte-identical against the STATE.md frozen values:
  ns_mtime   1793294532100000000 == 1793294532100000000  True
  size       5721578066          == 5721578066           True
  tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee == same  True
  => sitting delta: False
Corroboration (independent signals, all comm-class / direct-inspection):
  - dosbox/ascend.exe processes: 0 (r214_triage.py + ps -eo comm re-check)
  - caps/ directory does not exist (work/r1/caps: No such file or directory)
  - no vfat/msdos mount (findmnt -t vfat,msdos: empty)
  - INDEPENDENT AXIS (new this session, not part of TRIGGER-A): newest .sav/.gam
    anywhere under /home/hrethric (no date filter, 1409 files) is
    playcap/save/60.sav at 2026-10-29 13:22 — the SAME save the last sitting
    ended on. A find for saves modified since 2026-10-29 18:00 returns ZERO.
    A player who advanced the game would have produced a newer autosave slot
    even if the timeline writer were dead, so this closes the "watcher died and
    hid a sitting" alternative independently of the timeline file.
=> scripts/r1_t85g_sitting.py correctly NOT run (t152 trap: running the sitting
   script on a stale dir fabricates a sitting). No witness mining possible.

## S2 — WRITER-POPULATION FACTS MEASURED (upgrades the t214 hygiene ask)
t214 inferred 4 writers from process presence. Verified this session via
/proc/<pid>/fd (which process actually holds live-timeline.jsonl open):
  pid 27772  bash wrapper, writer_fds=0        (the t115 wrapper, ppid 1)
  pid 27774  r1_playcap_watch.py --no-exit, writer_fds=1  <- 27772's child
  pid 260988 r1_playcap_watch.py --no-exit, writer_fds=1  <- ppid 1, up 1-18:55
  pid 290953 r1_playcap_watch.py --no-exit, writer_fds=1  <- ppid 1, up 1-05:52
  pid 292085 r1_playcap_watch.py --no-exit, writer_fds=1  <- ppid 1, up 1-05:27
=> EXACTLY FOUR processes hold the capture file open for append (the wrapper
   holds none — it is not a writer). This is the direct measurement behind
   t214's 4.26x inflation figure: the writer population IS four right now, and
   all four carry --no-exit, so they persist across sittings and the next
   capture inherits them. Consequence for the next sitting, stated precisely:
   per-EVENT mining stays correct (r1_stream dedupes on (file,mtime_ns), zero
   content conflicts per t214 audit), but four writers on one dir is a capture-
   HEALTH problem — if one of them is ever mid-rotation or holds a stale offset,
   rows interleave in ways dedup cannot repair. Retirement is a supervised-
   session decision; research iterations must NOT kill them (t214 law).

## S3 — LEDGER: NO ROW MOVED (strict-close honored)
Nothing in this iteration touches a law. Both witness classes remain gated:
  - OQ-016 multi-volley-vs-non-at-war-owner clamp witness: needs new play.
  - OQ-021 mid-campaign slot (V>1 AND some byte[star+0x15] nonzero) settling
    the S6 semantic non-join + P7 label question: needs new play.
  - OQ-021 write site: watchpoint class (needs a supervised dosbox-x session;
    tooling present at /usr/bin/dosbox-x — the blocker is supervision, not tools).
  - OQ-019 per-ship/commit conversion + OQ-005 index.txt ruling: BLOCKED-USER
    decisions.
Static corpus formally EXHAUSTED at t213 S7; t214/t215 added no static route.
Per the t212 law I did NOT re-run any censused instrument looking for new
inputs, and did not re-verify t214's collapse factor (no new sitting to
re-measure it against).
