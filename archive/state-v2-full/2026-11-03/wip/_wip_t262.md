# _wip_t262 — OQ-021 CENSUS DISCRIMINATOR (per-owner ship census vs V-change
# turns) on the DRIVEN corpus. Working log, hand-authored.

## S0. Pre-flight (2026-11-01 ~23:31)
- t261 re-drive ALIVE and healthy: work/r1/playcap/drive_t261b.out shows
  presses advancing every ~10 s, turn 1198 at 23:30:53, target 1236
  (dosbox-x PID 535172 under a `timeout -s KILL` wrapper PID 535170 — the
  timeout-wrapper-pid caveat from t261: pgrep -x dosbox-x is the liveness test,
  not the wrapper).
- Ring writing normally (53..60.sav at 10 s cadence through 23:30:40).
- DO-NOT-LOAD law honored: no loadstate of bank-t251-live1255 (REFUTED t261,
  input-dead on load). Nothing on :9 clicked by this session.

## S1. What this iteration must actually add (scope discipline)
t258 already ran per-owner order-kind candidicide over the FULL corpus and got
SURVIVORS=NONE (score.md S11.2). Re-running that on a subset is worthless. The
new information here is the TRIGGER question on a corpus t258 never had: a
CONTINUOUS monotone drive (1086->1236, one session, one lineage, turn advancing
every 10 s). In the parked corpus, ring re-sampling made "sticky_kept" huge and
mixed load artifacts into both legs; in a drive, every turn boundary is a real
end-turn and every census delta is a real game-state delta.

Discriminator = 2x2 contingency over turn boundaries of the driven session(s):
  leg A: V changed -> did the per-owner ship census change? (necessity)
  leg B: census changed -> did V change? (sufficiency)
Controlled for the t251/t258 pitfalls: mtime-epoch corpus gate (r261_harvest
drive_rows law), (file,file_mtime_ns) dedup, per-session trust.

## S2. Instrument + first-run pitfalls
- r262_census_disc.py v1 collapsed all rows to "<2 snaps": (a) pending last
  snapshot never flushed at segment close (fixed: close_seg flushes cur);
  (b) LO epoch built without *1e9 in one edit — mt is NANOSECONDS.
- A rejected terminal call (nohup wrapper) had ALREADY applied its sed —
  grep the file after any partially-rejected compound command before editing on
  top of it.
- Full-corpus single pass (7.56 GB, rows never buffered) runs ~4 min clean;
  the 300 MB tail covers only ~10 h of stream (~180 MB/day).
- Outputs: work/r1/t262_census_full.out (Oct-29+ window), 
  work/r1/t262_census_early.out (Oct-01..Oct-29 window, 808 boundaries),
  r262_legA.py stdout (27 leg-A boundaries: targets moved 27/27, kinds 24/27,
  systems_*/planets NEVER, nothing-banked-moved 0).

## S3. Result (banked to score.md S13 + OQ-021 annotation)
- Census/inventory trigger DEAD both legs; functionality kill 18/149 sigs
  multi-V; worst sig carries 6 distinct V values across driven turns
  1255..1335. Doubling t911->912 and halving t1140->1141 fire with inventory
  byte-identical — S11.5's factor-2 shape clue is NOT fleet inventory.
- Residue sharpened: per-End-Turn recompute over NON-FLEET state; watchpoint
  ask stays. Driven max V=22@t1301 (decayed 21@t1335) — threshold still
  unobserved, row OPEN.

## S4. Environment state at finish
- t261 re-drive COMPLETED: TARGET REACHED t1236 23:37:12, banks
  bank-t261-t1236 + bank-t261-final-1236; game alive (PID 535172), ring
  parked at 1236. No clicks by this session; no loadstate (REFUTED honored).
- NEXT = t263 (pop-panel rewrite, pure code) per queue order; t265/t269 also
  have corpus in hand now (drives 1087->1236 + Oct-28 late run).
