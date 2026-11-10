# t368 — WAIT-TRIGGER SENTINEL (WIP, hand-authored; no generator writes this path)

Session started 2026-11-10. Assigned task: STATE.md NEXT = t368 sentinel
(branches 1 sitting / 2 ruling / 3 park). Ledger at start: 17 CLOSED / 2 OPEN
(OQ-016, OQ-019 — both user-gated).

## F1 — THE TIMELINE FEED IS DEAD: the standing sitting check was BLIND (new harness fact)

The STATE.md branch-(1) law is "400 KB tail-SEEK of
work/r1/playcap/live-timeline.jsonl; newest turn > 1086 => run
r1_t85g_sitting.py". That check is only valid while the collector is alive. It
is not:

- `live-timeline.jsonl` size 8,917,535,608 B, mtime **2026-11-09 17:26** — zero
  bytes of growth vs the t368 baseline recorded in STATE.md (delta exactly 0),
  and ~14 h stale at this session's start (~07:15 on 11-10).
- 400 KB tail-seek parsed 17 records, turn 1086 on 17/17 — but that only proves
  nothing new was BANKED, not that nothing new was PLAYED.
- `work/r1/loop/GAME_HEALTH_LIVE.txt` (mtime 2026-11-10 07:10) reads
  `UNHEALTHY | W:NOWATCHER(feed not banking)` with `info: ring 50.sav age 6s` —
  i.e. the game is still autosaving every 10 s while nothing ingests it.
- Watcher pid 1575 is GONE (`ps -p 1575` empty); no `r1_playcap_watch` process
  in `ps`. Game pid **1555 alive**, etime 1-06:12:09, `-time-limit 172800`,
  TL expiry 2026-11-11 01:07:10 (~64.6 ks remaining at check time).

Consequence: for the ~14 h window 11-09 17:26 -> 11-10 07:15, any play would
have rolled through the 20-slot ring (10 s cadence => ring covers ~200 s) and
left NO trace in the timeline. The tail-seek law would have reported
"no new sitting" for real play. LAW CHANGE: the sitting check must read the
ring, not the feed, whenever the feed is stale.

## F2 — Ring-direct sitting probe (the new primitive; READ-ONLY)

`work/r1/t368_ring_turn.py` — opens each `work/r1/playcap/save/*.sav`, unzips
`Memory`, resolves the base with the CACHED anchor law (`r1_slot.anchors_cached`
+ `base_of`), reads the turn scalar via `r1_slot.read_slot` (OFF 0x82bb0 +
0x12e10). Reuses the cited law verbatim; invents nothing.

RESULT (real run, 2026-11-10 ~07:2x): **parsed 20/20, max_turn 1086, min_turn
1086.** Ring mtimes 07:16:35 (50.sav) .. 07:19:45 (49.sav) — live autosave,
correct 10 s cadence, ring rotating normally.

=> Branch (1) SITTING CHECK **NEGATIVE** on the strongest available evidence:
the live ring itself says turn 1086, the corpus floor. `r1_t85g_sitting.py` NOT
run (standing law: only on turn > 1086).

## F3 — Branch (2) ruling check, pre-launch (re-confirmed post-poller below)

- `docs/DECISIONS.md` mtime **2026-11-10 06:23:41.040** == the recorded t368
  baseline EXACTLY (not newer).
- `git diff -- docs/DECISIONS.md` empty; `git status --porcelain` EMPTY at
  session start (tree clean at commit 429e807).
- No `*ruling*`/`*reply*` files in the repo except three unrelated
  `work/r1/dbx-build/dosbox-x-master/ref/Apple/MachO/mach/clock_reply.h{,.defs}`
  + `host_notify_reply.defs` — vendored macOS headers, tracked and unmodified,
  not user replies. NOTE: the poller's `grep -iE 'ruling|reply'` runs on
  `git status --porcelain` output only (tracked-modified/untracked), so these
  committed vendored files cannot false-trigger it. Verified.
- The OQ-005 decision-sheet baseline is CLOSED (t367) and NOT watched, per
  STATE.md.

## F4 — Poller run

`work/r1/sentinel_t368.sh` (pre-staged by t366; 60 s poll, 2700 s cap; watches
DECISIONS.md mtime > 2026-11-10 06:23:41 epoch, DECISIONS.md content diff, any
git-status entry naming ruling|reply). Launched via
`terminal(background=true, notify=true)` — session `proc_6d442daa5692`,
pid 102048. Waited with `process_manage(action='wait', timeout=180)` chunks
(no foreground tail chunks, per the t356 lesson; no nohup, per t355).

OUTCOME: **exit 0, `TIMEOUT:no ruling after 45min`** (session
`proc_6d442daa5692`, pid 102048; ran ~07:22 -> ~08:07). Wait chunks:
`process_manage(action='wait', timeout=180)` x7 (clamped at 180/call per the
t355 law) + two foreground `tail --pid=102048 -f /dev/null` chunks that hit the
TOOL's own hard cap (420 s regardless of `timeout=`, and a 590 s request is
REFUSED, not clamped) — harmless, the poller was unaffected; both re-trips of
the t356 lesson are why NEXT now says process_manage only.

POST-EXIT RE-CHECK (~08:07, all four negative):
- `docs/DECISIONS.md` mtime still **2026-11-10 06:23:41.040** (== baseline).
- `git diff -- docs/DECISIONS.md` empty; `git status --porcelain` = only
  `?? docs/re/_wip_t368.md` (this session's own bank file — a dirty entry naming
  MY path is not a user edit; the t355 path-audit law applied and held).
- game pid 1555 alive, etime 1-06:50:34.
- Health readout still `W:NOWATCHER(feed not banking)`.

## F7 — Second ring-direct sitting probe AFTER the 45-min poll (closes the gap)

The poller watches rulings ONLY, so the 45-min window itself needed a sitting
re-check — and with the feed dead, only the ring can give one. Re-ran
`work/r1/t368_ring_turn.py` at ~08:07: **parsed 20/20, max_turn 1086, min_turn
1086**; ring mtimes live through **07:57:46** (57.sav), 10 s cadence intact.

=> Branch (1) NEGATIVE both before AND after the poll window, measured on the
live ring rather than the stale feed. This also RETROACTIVELY covers the 14 h
feed-dead window by a different argument than ring coverage: the turn scalar is
monotonic in a running save (turns advance, never regress), so a ring reading of
1086 at 08:07 means the turn never advanced past the corpus floor at any point
since capture began — had the user played, the CURRENT ring would show the
higher turn, not the old one. (Caveat, stated: mid-turn actions that never
cross a turn boundary are invisible to this probe AND to the standing
turn>1086 law, so the law is satisfied as written; the ring's ~200 s window is
NOT what carries the proof here.)

## F5 — Ledger disposition

Strict-close: NO measurement of any open-row constant was produced this
iteration, so **no row moves**. OQ-016 and OQ-019 stay OPEN (both close on USER
ruling only — t323/t329/t332 disposition). Honest negative recorded rather than
a plausible-default close. Ledger stays 17/2.

## F6 — Watcher relaunch: deliberately NOT done

Restarting `r1_playcap_watch.py` on the production capture dir would restore
the feed, but (a) it is not the assigned task, (b) it launches a long-running
writer from a sentinel session, and (c) if the next iteration launches its own,
two writers append to the same `live-timeline.jsonl` — the t85b dedup law
prevents RESTART duplicates but not CONCURRENT writers. Left for the harness /
user. The safe relaunch, if wanted, is
`python3 scripts/r1_playcap_watch.py work/r1/playcap` after confirming no other
watcher is alive (`pgrep -f r1_playcap_watch`), which the F1 check does first.
