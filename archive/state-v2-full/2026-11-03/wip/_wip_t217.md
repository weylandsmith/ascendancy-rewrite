# _wip_t217 — sitting adjudication (idle, fourth consecutive)

Date 2026-10-31 (session t217). Task per STATE.md: sitting adjudication ONLY
(r214_triage.py as the single triage call + one save-axis find by ns). No
other axis was censused (t212 law); no static route re-trod (t213 S7).

## S1 — TRIGGER-A: NO SITTING (fourth consecutive byte-identical adjudication)
scripts/r214_triage.py RC=0:
  ns_mtime 1793294532100000000 == baseline: True
  size     5721578066          == baseline: True
  tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee == baseline: True
  => sitting delta: False
Zero dosbox/ascend.exe comm-class processes. Therefore
scripts/r1_t85g_sitting.py was correctly NOT run (t152 trap: running the
sitting adjudication without a new sitting is net-negative).

## S2 — SAVE AXIS: idle, exactly reproducing the t216 ns-precision numbers
find /home/hrethric -xdev for *.sav/*.gam sorted by %T@ (t215 law + t216
precision fix — newest named by full ns, never wall-minute):
  1793294530.1080000000  work/r1/playcap/save/41.sav   (newest anywhere)
  1793294520.0400000000  work/r1/playcap/save/60.sav
  1793294510.0040000000  work/r1/playcap/save/59.sav
Newest save ns 1793294530.108 < timeline baseline ns 1793294532.1 — both are
the last sitting's end saves (2026-10-29 13:22); zero saves newer anywhere,
so the "watcher died and hid a sitting" gap stays closed on this independent
signal. Values are BIT-IDENTICAL to the t216 measurement.

## S3 — Watcher population unchanged (incidental observation from the triage
script's own census — NOT a new census; r214_triage prints it as part of its
fixed RC=0 pass): same five processes as t215/t216 — wrapper 27772 (bash,
ppid 1) + writer child 27774, orphans 260988/290953/292085. No new orphans;
no retirements. Orphan-retirement remains a standing supervised-session user
ask (research iterations must NOT kill them).

## S4 — HONEST NEGATIVE (strict-close)
No sitting => no new witness class => NO ledger row moved. OQ-016 (clamp
witnesses) and OQ-021 (comparator firing + write-site) stay open unmodified;
OQ-005 (index.txt ruling + dims residue) and OQ-019 (per-ship/commit
conversion ruling) stay BLOCKED-USER. The static corpus is formally exhausted
(t213 S7); three axes (timeline ns/size/tail-md5, save-newest-by-ns, process
class) have now agreed "idle" across t214, t215, t216, t217 — four
consecutive identical adjudications. Loop is steady-state idle: only (a) new
play, (b) a user ruling, or (c) a supervised dosbox-x watchpoint session moves
the ledger. An idle t218 would add nothing beyond re-printing S1..S3.

## Standing user asks (restate; unchanged since t216)
1. Play a few turns attacking a non-at-war power mid-campaign + save —
   kills the OQ-016 clamp-witness ask and the OQ-021 comparator-firing ask.
2. OQ-019 ruling: may the rewrite model per-commit attack pricing?
3. Watcher-retirement hygiene: retire orphan watcher pids before the next
   capture (supervised-session decision).
