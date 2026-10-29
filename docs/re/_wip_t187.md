# _wip_t187 — LIVE sitting adjudication (trigger A, 2026-10-28 ~23:40 EDT)

## Trigger reality-check (measured this session, not assumed)
- TRIGGER A GENUINE, sitting LIVE AS OF LAUNCH: dosbox-x pid 260973 alive
  (-time-limit 28800, started ~23:26), watcher 260988 on the SHARED dir
  work/r1/playcap; timeline 5694264263 -> 5695392860 in ~30 s; watch.out
  rows wall-stamped seconds before launch; turns advancing t1255->t1284
  DURING this session. Baseline last row was t1254/tail 1529ab1a.
- The trigger's named dir playcap-20261014-224611 is a STALE Oct-14 per-run
  dir (65 rows ALL turn=0 = title-menu, untrusted t82 law). The real ingest
  is work/r1/playcap (what the trigger's timeline stat itself names).
- Runs: scripts/r1_t85g_sitting.py work/r1/playcap (RC=0) +
  scripts/r1_t187_delta.py work/r1/playcap 1255 (RC=0, 45140 trusted pts).

## FINDINGS (banked 23:4x, before deeper probes)

### OQ-023 — first 2->1 (WAR->PEACE) transition banked; state-3 still UNOBSERVED
- New-window scan: ZERO relation cells holding 3 (t1255..t1284, every row).
- Full sitting diff at t1254: states0 row flips 1->2 toward race idx 2 AND
  states2[0] 1->2 (RECIPROCAL, matches t85b war-decl law), att2[0] drops
  477->437 (-40); at t1255 BOTH cells are back to 1. A war held for
  <1 turn and peace was restored reciprocally — the 2->1 direction had
  NEVER been banked before (prior corpus only had 0->1 contact, 1->2 decl).
  NOTE cross-check vs t85g: t85g's sitting was the t1253 window with the
  Orfa proposal (att1[0] 487->526 at t1254 row = same event); whether the
  war blip toward race-2 was banked then — check diplomacy.md before
  re-reporting as new.
- att[Orfa->Chamachies] (AI side) is DRIFTING UP: 526@1254 -> 529@1261 ->
  532@1271 -> 535@1284 (+3 ticks ~every few turns, likely AI-side trade).
  ACCEPT_ALLIANCE=570; extrapolated crossing ~t1295-1300 IF drift holds.
  PLAYER ASK: propose alliance to Orfa when the in-game diplomacy screen
  shows attitude high (or keep ending turns) — acceptance closes OQ-023.

### OQ-021 — systems_full 68% vs DAT_482fb 21/50, selector still NEVER armed
- New window star series: 1255:14/50 ... 1277:16/50, 1284:21/50 (jumped
  +5 at t1284); selector_byte == 0 in ALL new rows (0/45140 ever armed).
  Player holds systems_full=34, systems_any=36 of T=50 => 68% full-system
  share WITHOUT arming: re-confirms systems_full is NOT the comparator var
  (t85b law), consistent-with >1/2 on DAT_482fb. If DAT_482fb crosses 25
  and the comparator fires, THAT closes the row — sitting not over, watch
  it next iteration.

### OQ-019/010 — SHIPS ARE FLYING: first state-4/state-5 corpus EVER
- New window state census (row-samples): state0 x158 (empty slots,
  owner=65535), state1 x466, state3 x717, state4 x1115, state5 x584.
  t49's "2260 slot-pair obs 0 state-4" zero-corpus argument is now
  SUPERSEDED by positive observation; player authorized flying.
- Per-row displacements (row-granular, NOT yet turn-normalized):
  owner=0 z=1600/352 movers step d=(14,0)/(28,0)/(56,0); owner=1 z=32
  movers d=(4.67,0) then (9.33,0) (exactly 14/3, 28/3 — interpolation?
  or in-system engine rate vs lane rate, t179 testimony!); several
  1200-2500-unit JUMPS (slots 18,28,34,35,36,37 t1256-1259) — instant
  transit candidates (magnetron? [1,3]+immediate-arrival default?).
- Mid-turn raw diffs sitting t>=1240: +0x88 (POWER) x149 owner0 — fuel
  burn IS observed mid-turn (resolver sweeps); owner1/2 now also burn
  (+0x88 x50/x57) = AI ships flying too.
- MEASUREMENT PENDING: turn-boundary per-ship displacement vs drive sum
  [+0x10]/MOVES [+0x94]/fuel [+0x88]/state [+0x58] — the sugar-cube scale
  law probe (scripts/r1_t187_scale.py). THIS is the closure-class item for
  the OQ-019 scale residual.
- OQ-010 bonus: sitting had combat at t1253 (already banked t85g/§).

## Player asks (surface at session end + STATE)
1. Propose alliance to Orfa ~t1295+ (att drifting up through 570) => closes
   OQ-023 if accepted.
2. Keep going until DAT_482fb (percent controlled) passes 50% or press C on
   starmap for the readout => closes OQ-021 when comparator fires.
3. Note WHICH orders were issued for the big-jump ships (magnetron?) — a
   one-line testimony banks the provenance for the jump measurements.
