# t218 WIP — sitting adjudication only (static corpus EXHAUSTED at t213 S7)

Session assignment (docs/STATE.md t217 NEXT ACTION): run scripts/r214_triage.py
as the single triage call + ONE save-axis check. No static route exists to
invent (t213 S7 exhaustion law; t212 law: re-censusing an instrument with no
new inputs is net-negative). No trigger report was prepended to this session's
prompt, which per the t217 note is itself the signal to run the two axes ONCE,
write the idle line, and finish.

## S1 — TRIGGER-A: NO SITTING (FIFTH consecutive byte-identical adjudication)

`python3 scripts/r214_triage.py` → RC=0, all three baselines equal the recorded
values (work/r1/playcap/live-timeline.jsonl):

    ns_mtime 1793294532100000000 == 1793294532100000000: True
    size     5721578066          == 5721578066:          True
    tail md5 9054cc6c66802e6f80431d4ffa1416ee == 9054cc6c66802e6f80431d4ffa1416ee: True
    => sitting delta: False

So the timeline is byte-identical to the t214/t215/t216/t217 readings — a fifth
reproduction, same tool, same code path (t216 already cross-checked a second
independent stat+md5 path; do not add a third).

Game-process census inside the same triage pass: `dosbox/ascend.exe processes:
0`. No dosbox-x and no ascend.exe anywhere in /proc/*/comm, corroborating the
negative from the process side rather than the file side.

scripts/r1_t85g_sitting.py was CORRECTLY NOT RUN (docs/BLOCKED.md trap: running
the sitting adjudicator against an unchanged dir fabricates a bogus "sitting"
report and mounts scratch paths for nothing — the t152 trap).

## S2 — SAVE AXIS: idle, reproducing the t216 ns-precision numbers exactly

Independent axis per the t215 law (a player who advances the game leaves a
newer save regardless of watcher health — this closes the "watchers died and hid
a sitting" gap):

    find /home/hrethric -xdev \( -name '*.sav' -o -name '*.gam' \) -printf '%T@ %p\n'
      1793294530.1080000000  work/r1/playcap/save/41.sav   <- newest anywhere
      1793294520.0400000000  work/r1/playcap/save/60.sav
      1793294510.0040000000  work/r1/playcap/save/59.sav
      1793294500.0040000000  work/r1/playcap/save/58.sav
      1793294489.9880000000  work/r1/playcap/save/57.sav
    total *.sav/*.gam files under HOME: 1409   (same population as t215/t216)

Newest save == playcap/save/41.sav at ns 1793294530.108 — BIT-IDENTICAL to the
t216 and t217 readings, and still 1.892 s OLDER than the timeline baseline ns
1793294532.1. Nothing on the save axis post-dates the baseline, therefore there
is no hidden sitting and the watchers are not concealing play. Both top saves
(41.sav, 60.sav) are the last sitting's end-of-session saves from 2026-10-29
13:22.

## S3 — Watcher population unchanged (incidental to the triage call, not a
re-census)

The triage script's watcher section reports the same five processes as
t215/t216/t217 — no new orphans appeared and none retired in the ~13 h since
t217:

    pid 27772  ppid 1      [bash]     up 4-11:05   wrapper (holds NO writer fd)
    pid 27774  ppid 27772  [python3]  up 4-11:05   child of the wrapper
    pid 260988 ppid 1      [python3]  up 1-19:20   orphan (--no-exit)
    pid 290953 ppid 1      [python3]  up 1-06:18   orphan (--no-exit)
    pid 292085 ppid 1      [python3]  up 1-05:53   orphan (--no-exit)

fd-level writerhood (exactly FOUR open append fds on live-timeline.jsonl:
27774 + the three orphans) was measured at t215 and reproduced at t216; per the
t212 law it is NOT re-opened here without new inputs, and this iteration
performed no new fd census. Research iterations must NOT kill these watchers
(supervised-session decision — see the standing ask below).

## S4 — HONEST NEGATIVE (strict-close)

NO ledger row moved. No new evidence was obtained beyond the fifth reproduction
of an already-measured idle state:

- OQ-021 (attack-order comparator firing + writer watchpoint) — play-gated /
  watchpoint-class; unobservable without a sitting. Stays OPEN.
- OQ-016 (clamp witnesses: multi-volley battle vs a non-at-war owner) — the
  zero-witness residue needs an actual battle against a power that is not at
  war; no sitting, therefore no witness. Stays OPEN.
- OQ-019 (per-commit attack-pricing modelling) and OQ-005 (index.txt ruling +
  dims residue) — BLOCKED-USER decisions, not measurement-gated. Stays OPEN.

Under strict-close policy a plausible default never closes a row, and this
iteration deliberately measured nothing new because there was nothing new to
measure: the static corpus was formally EXHAUSTED at t213 S7, and t214..t218
have added only instrument health. Five consecutive byte-identical
adjudications is the strongest possible idle confirmation.

## S5 — Process-level consequence (new this iteration, stated as inference)

[inferred from S1..S4, all verified measurements above] The idle-adjudication
task shape is now itself exhausted as an information source. An idle t219 adds
nothing beyond re-printing S1..S3 of this file. The loop's remaining open rows
are exclusively (a) play-gated, (b) BLOCKED-USER, or (c) watchpoint-class — none
of which an unsupervised research iteration can advance. The productive next
step is therefore NOT another adjudication iteration but one of the three user
decisions below; until one lands, the harness should re-arm a trigger rather
than cadence (the trigger already exists: r214_triage.py against the three
baselines in STATE.md). This is a recommendation about loop scheduling, not a
new research route, and it opens no refuted route.

## Standing user asks (restate; unchanged since t216)

1. PLAY: a few turns mid-campaign attacking a NON-AT-WAR power, then save. This
   single action kills the OQ-016 witness ask and the OQ-021 comparator-firing
   ask at once (witness classes named in STATE.md t217 NEXT ACTION).
2. RULE on OQ-019: may the rewrite model per-commit attack pricing?
3. HYGIENE: retire the three orphaned watchers (260988/290953/292085) before the
   next capture — measurement-stable across t215..t218 (four open append fds,
   wrapper 27772 holds none). A supervised-session decision; this iteration
   killed nothing.
