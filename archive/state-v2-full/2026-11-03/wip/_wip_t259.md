# t259 WIP — live-session loss adjudication (2026-11-01, ~16:47 EST start)

## S1 — Assignment and adopted task
STATE.md (t258 commit 7c892d4, 16:44) NEXT ACTION = WAIT-TRIGGER SENTINEL
(queue drained, no offline work). This session was launched by the loop
(tmux ascendloop, MAX_ITERS=14 IDLE_GATE=0). Sentinel adjudication performed
instead of idling, because trigger re-check IS the sentinel's job:

## S2 — MEASURED trigger census (all three re-arm triggers)
- (1) WITNESS: tail -c 400000 of live-timeline.jsonl: `"selector_byte": [1-9]`
  count = 0; distinct score_stars in tail = {14} only. No V>=25 witness.
  No new playcap-* dirs (ls -d work/r1/playcap/playcap-* -> empty).
- (2) USER ASK answer: none prepended in prompt; BLOCKED.md t258 USER ASK
  (A)/(B) unanswered (lines 461-481).
- (3) STEERING note: none.
=> No re-arm from the authored triggers. BUT the sentinel's premise check found
   the environment itself changed — S3.

## S3 — MEASURED: the parked :9 game session is DEAD (dark since 15:45)
- `pgrep -x dosbox-x` -> exit 1 (no process). No dosbox* variant of any kind.
- Xvfb :9 (pid 1196) and x11vnc (pid 1207) still alive — display survives,
  game does not.
- live-timeline.jsonl mtime Nov 1 15:45; last rows t=1255 V=14 sel=0,
  60.sav. Now ~16:50. Timeline dark ~65 min. (Sentinel t258 assumed the
  watcher keeps banking because a dosbox was alive; no longer true — watcher
  lives, ring is empty because the game is gone.)
- Ring savs: newest 60.sav 2,345,605 B at 15:45 (t=1255 V=14 state IS in the
  ring + bank-t251-live1255 intact).
- Cause of death: UNVERIFIED. journalctl --since 2026-11-01 00:00 has ZERO
  'killed process' lines (and appears to return nothing at all — possibly
  no journal access; do not over-read this). dmesg unreadable (exit 1).
  free -h healthy now (13Gi available). Timeline now 7.46 GB (was 6.4 GB at
  the t251 OOM incident).
  [inferred] The t258 session ran r258_vdisc passes 15:34-16:20 (pass-1
  15:34, .pid files banked); a memory spike in that window is the prime
  suspect, consistent with the t251 incident class (streamer reading the
  multi-GB timeline next to the game on a 15 Gi host). NOT proven.

## S4 — Consequence for the USER ASKs
- Ask (A) (drive parked :9 session past V>=25) is now IMPOSSIBLE as literally
  authored — the session it names no longer exists. Its substance survives
  only via a relaunch from a banked/banked-ring sav at/near t1255 V=14.
- Ask (B) (watchpoint dosbox-x) unaffected — it always required a new
  instrumented run anyway.
- Sentinel premise "watcher lives => trigger A structurally always armed" is
  FALSE now: with no game, no new V rows can ever appear without a relaunch.

## S5 — Watcher census (t215 writerhood law: open fd, not process presence)
SEVEN python3 r1_playcap_watch.py processes hold an open fd on
live-timeline.jsonl simultaneously: pids 27774 (Oct 26), 260988 (Oct 28),
290953 (Oct 29), 292085 (Oct 29), 449921 (Oct 31 09:01), 457638 (Oct 31 13:17),
462206 (Oct 31 19:51), 513605 (Nov 1 15:11). Combined RSS ~ 700 MB.
t257 believed it reaped the sitting pair 479981/479983 and left ONE detached
replacement (513605). MEASURED: at least seven co-exist, all fd-censused on
the timeline. MEASURED (fdinfo): ALL EIGHT hold fd 3 with O_APPEND set
(flags 02102001/0102001 family), each at a DIFFERENT stale pos — with
O_APPEND the pos is ignored at write time, so every one of them appends at
EOF. Corroborated by row census: tail -c 400000 of the timeline = 14 non-blank
rows, only 9 UNIQUE (rows ~4-28 KB each with ship_raw) => ~1.5x exact-duplicate
FILE inflation. HONEST CORRECTION mid-session: r258_vdisc.py dedups by
(file, mtime_ns) (scripts/r258_vdisc.py:26,196-199 — watcher copies share
mtime_ns and collapse), and it REPORTED dedup=237,718, so the banked S11
counts (53,412 trusted rows, 38 vs 795 boundaries) are post-dedup and NOT
inflated; the candidicide verdict stands untouched. The real costs of the
8-watcher population are (a) ~7x write bandwidth + 7.4 GB growth rate, (b)
~700 MB RSS, (c) any FUTURE consumer that skips the (file,mtime_ns) key re-
ingests duplicates. t257's reaping of the sitting pair therefore did NOT
converge to one writer; the population grew to eight. Retirement of the seven
pre-t257 orphans: /proc-validated kill is precedent-consistent (t257 did it
to 479981/479983) but STATE's pairing note reserves watcher retirement for
the user — flagged as a user ask, not executed. Harness-hygiene finding
(control-plane, not a ledger fact).

CONTEXT LAW RE-INFORCED: a `tail -c 400000 live-timeline.jsonl | sort | uniq -c`
piped the raw 28 KB rows into tool output (~150 KB, mostly ship_raw) — the
census must be run with `cut -c1-200` / awk field extraction BEFORE the output
reaches the terminal. Banked as a probe-hygiene rule.

## S6 — Offline residue that survives the game's death (what the next loop task CAN do)
- scripts/r1_playcap_watch.py reads the sav as a ZIP and pulls member "Memory"
  (:178) = FULL guest RAM. Therefore bank-t251-live1255/*.sav + ring
  work/r1/playcap/save/*.sav are RAM-frozen at t1255 V=14 — the producer's
  INPUT state is preserved offline even though the process is gone.
- [inferred] A new offline discriminator is now possible WITHOUT any relaunch:
  diff the guest RAM around 0x482fb (and candidate input structures) across
  two banked states with DIFFERENT V at the SAME turn-class (e.g. S14 t1167
  V=14/full=27 vs S15 t1167 V=14/full=29 pair is same-V; the useful pair class
  is same-turn-different-V, e.g. the t1169-71 14->12->14 replay exists in TWO
  banked session lineages if their savs were ring-captured). A byte-diff of
  16 MB zipped savs is cheap and bounded. This does NOT re-trod t212 (which
  censused the STATIC candidate space for the store site and got a zero) —
  it hunts the READ side: which guest structures differ between a V=12 and a
  V=14 snapshot of a deterministic replay. Sized ~1 loop task IF the sav pairs
  exist on disk; census of available pairs = first probe.
- If no same-turn-different-V sav pair exists on disk, this route is EMPTY
  (record the negative; do not synthesize).
- MEASURED t259 (scripts/r259_savpair_census.py KEEPER, work/r1/t259_savpair.out):
  ALL 122 savs across bank-t1096 / bank-t1254 / bank-t251-live1255 /
  bank-t251-predrive / ring playcap/save censused (bounded RSS, one Memory
  member at a time): PAIRS = NONE. Every bank is internally one frozen state
  (20 slots same t/V); the cross-bank turn set is {1086 V=0 (predrive), 1096
  V=23, 1254 V=23, 1255 V=14} — no two savs share a turn with different V.
  The t1169-71 14->12->14 replay exists ONLY in timeline rows, never as sav
  ZIPs (the ring is 20 slots deep; the replay turns were overwritten long ago).
  Cross-bank diffs (t1254 V=23 vs t1255 V=14) are CONFOUNDED — territory moved
  between those turns too, exactly the candidicide failure class — so they are
  NOT a substitute. S6 route CLOSED as measured-negative; the producer residue
  is fully play/watchpoint-gated (t258 USER ASK + t259 ADDENDUM). Corroborates
  the V==0 LOAD-CLASS fact: predrive bank = t1086 V=0 across all 20 slots.

## S7 — What this session's verdict is
No authored trigger fired (S2), but the sentinel's ENVIRONMENT PREMISE died
(S3): the witness pipeline is DARK. Passive trigger A (watch for V>=25 rows)
can never fire until the game runs again. Per GOAL.txt "stop when blocked"
this is written to BLOCKED.md as t259 USER ASK with the best default
(no relaunch; banks intact; loop re-arms on user answer or a new sitting),
and the harness instruction flips from "relaunch IDLE_GATE=1" to "DO NOT
relaunch" — burning 14 fresh sessions re-adjudicating a dead pipeline is the
t214..t243 pattern re-run. NEXT ACTION = sentinel v2 (runs
scripts/r1_t259_sentinel.sh, ~4 tool calls, exits).
