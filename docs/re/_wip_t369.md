# t369 WIP — census tools pre-build (playtest 2026-11-10 evening)

## SITTING CHECK (RING-FIRST, t368 law) — run at session start 13:05
`python3 work/r1/t368_ring_turn.py` -> parsed=20/20 max_turn=1086 min_turn=1086.
Watcher IS alive this time (pid 107679 r1_playcap_watch.py; game pid 107664).
live-timeline.jsonl mtime 2026-11-10 13:06:19, 8,932,396,135 B, tail rows
t=1086. work/r1/game/RESUME.GAM mtime 2026-11-02 21:46:09.004 (UNCHANGED vs
authoring baseline); game dir .SAV set = 01/02/03/04 with mtimes 2026-10-21,
10-26 00:03, 10-19, 10-26 08:37 (all pre-baseline). => NO PLAY YET. Per the
queue row, t369 runs as written (build the tools + zero-hit control); exit
honest-negative on the window, NEXT stays t369.

## BASELINE SNAPSHOT (authoring, 2026-11-10 13:06) — consumed by r369_playwindow.py
RESUME.GAM(work/r1/game)      2026-11-02 21:46:09.004  87663 B
SAV 01.SAV 2026-10-21 01:09:38 | 02.SAV 2026-10-26 00:03:36 |
03.SAV 2026-10-19 14:52:42 | 04.SAV 2026-10-26 08:37:12
timeline                      8,931,163,683 B at authoring (STATE/_wip);
                              8,932,396,135 B at 13:06 (watcher idle-banking)
ring pre-play bank            work/r1/bank-t1086-preplay/ 20 slots t1086
expected first-play marker    turn != 1086 in the tail, OR RESUME.GAM/0*.SAV
                              mtime > baseline

## CITED LAWS CONSUMED (NOT re-derived; all pre-existing)
- Slot/ship array: r1_slot.py — Memory member = guest RAM, base B by anchor
  vote; ship base B+0x82bb0+0x3a095 stride 0x162, count u32@+0x43489>>16 clamp
  0x6b. Turn u32 DAT_00012e10. POINTER LAW OQ-011 (member addr = B+0x82bb0+X).
- Ship order fields (docs/re/pership-spec.md §1 field map):
  +0x54 u32 owner (race = >>16, t273) | +0x56 u8 owner race |
  +0x58 u8 ORDER KIND 0..5 | +0x59 u32 ORDER TARGET ptr (guest-PHYSICAL,
  rebase per save t298/t333) | +0x5d u8 ACT | +0x5e u32 ACT TARGET |
  +0x67 u8 order TYPE (2 = star-target -> FUN_0004ca50; 3 = abs triple +0x6c;
  5 = delayed move) | +0x68 u32 order PAYLOAD (type-1 = ptr to 3-dword coord
  triple, derefs [p],[+4],[+8] @0x49fb9/0x49fd7 — ships.md §10) |
  +0x6c f32[3] kind-3 absolute triple | +0x88 u32 POWER | +0x9e f32[3] pos |
  +0xab gizmo ring 25 slots stride 7 (cidx u8 @+0, 0xFF empty, u16 @slot+1,
  u32 @slot+3) | +0x15a cap | +0x15a/0x15e filled.
- MAGNETRON (cidx 60) landing law ships.md S19 T3 / pership T-3:
  FUN_00021f58 REQUIRES kind==5; pos := star coords + (0,-200,0) + rng%200 on
  the OTHER TWO axes (LIVE -200.0 @B+0x82bb0+0xaee, two FUN_0007824f draws,
  idiv 200); then kind:=4 (0x2202f). st=5 is a same-CALL transient => a landing
  ROW is an st4 row. CENSUS K3b (r265_keeper.py): P(both jittered axes land on
  the 32-grid) ~ (6/200)^2 < 0.1% => any st4 row off-grid in x OR z = hit.
  W2 frame sig (r265_st4_magnetron.py): st->5 + d>300 + y in [-200,0) +
  x/z not both on-grid. st4 on-grid = walk/system-grid signature (control).
- Star table (scripts/r1_star_table.py law): stride 96, name-anchored;
  name-0x14 f32[3] star position triple; name-0x18 u32 system index.
- Churn law (t366, scripts/r366_churn_census.py): same-turn ring pairs churn
  ONLY at +0x58/+0x59/+0x5d/+0x5e and +0x9e..+0xa9 at turn boundaries — so the
  order-diff tool's field set is exactly the churn set + payload/triple/ring.
- OOM LAW: timeline ~8.9 GB; bounded tail-SEEK then one json.loads per line;
  never iterate the whole file. Row = 23,701 B avg (measured, 843-row sample).

## RESULTS (t369 session, 2026-11-10 ~13:10) — TOOLS BUILT, CONTROLS GREEN, NO WINDOW YET

### Verification matrix (every code path exercised for real)
| path | input | result |
|---|---|---|
| r369_playwindow.py | live tree | exit 1 NO WINDOW (honest negative) |
| r369_magnetron_hit.py --dir | bank-t1086-preplay | C1=0 C2=0 C3=0 (zero-hit CONTROL PASS) |
| r369_order_diff.py --selftest | synthetic 2-click | PASS (two_click=1, cls XY/Z) |
| r369_order_diff.py --dir | bank-t1086-preplay | 0 witnesses (CONTROL PASS) |
| both --dir | work/r1/t369-fixture (synthetic edits) | C1=2 C2=2 C3=1 decrements=1 two-click logic fires |
| both --window FLOOR..-1 | real timeline (814 idle samples) | all counters 0; kinds {0,3,3:2442,4:1628,5:17094} |

### Fixture law learned (instrument truth, not game law)
- A dest-triple edit at a SHARED payload ptr (bank: ships 3+25 both p=0x26d339)
  fires the change on BOTH slots -> interleaved events -> two_click adjacency
  correctly stays 0. Real issued orders allocate per-ship triples (bank p68
  values differ per ship), so adjacency is meaningful live; single-slot case
  proven by --selftest.
- magnetron --dir dedups on (turn, st+pos+ring) only — a dest-only edit
  dedups away BY DESIGN (census doesn't deref); order_diff --dir signature
  includes the derefed triple + ring + pos, so nothing witnessable dedups.
- TIMELINE STALE-ECHO TRAP (t369 caught it live): the Nov-3 drive epoch
  (turns 1086->1236) lives in the SAME live-timeline.jsonl; a turn!=1086 scan
  WITHOUT an mtime floor hits it (first false hit: turn 1150 wall 14:09:29
  mtime_ns 1793732967676000000 = 2026-11-03). r369_playwindow now floors at
  2026-11-10 11:18 (pre-play bank time). t251 rewind caveat, re-confirmed.

### Design decisions (consumed by t370)
- Window = mtime-selector (r265 law) over file_mtime_ns in [lo_ns, hi_ns],
  dedup (file,mt), in_game AND turn>0; bounded 200 MB tail-seek (~22 h of
  10 s rows); hi bound is a FILTER not a seek target.
- tl mode cannot deref payload ptrs -> two-click witnesses in tl mode come
  from type-3 (+0x6c f32) triples + PAYPTR-change candidates; the FULL
  derefed measurement is r369_order_diff.py --dir on a .sav dir. RING
  ROTATION LAW (~200 s): t370 MUST bank the play dir immediately after the
  session (like bank-t1086-preplay) before running --dir, or the play slots
  roll off.
- Counters: C1 carriage cidx 60 (+use u16 @slot+1), C2 off-32-grid st4 (K3b,
  P(false-neg)<0.1%), C3 W2 frame (st->5, d>300, y in [-200,0), x/z not both
  grid). y-mod-32 histogram printed (placement = star_y-200.0 pre-jitter).
- Exit codes: playwindow 1=no window (NEXT stays t369, rerun); censuses 0
  always (honest negatives are findings), 2=harness.

### GATE RACE FOUND + FIXED (mid-iteration; the gate went RED once)
First gate run this session FAILED: shipsave_writeback_idempotent_t366
line 128 `ok == saves.size()` — zero "diverged" lines, so a ring slot was
caught MID-REWRITE by the live 10 s autosave rotation (torn ZIP -> inflate/
base-vote fails -> `continue` skipped it while it stayed in the denominator).
Three consecutive direct run_tests runs passed => pure race, not regression.
FIX (tests only; game/ untouched):
- test_shipsave_t366.cpp: torn slots counted separately, idempotence measured
  over parsed slots, CHECK(parsed>=10) + ok==parsed.
- test_shipsave_t360.cpp reader test: same torn-skip shape (was hard CHECKs
  over all 20 rotating slots); determinism of the reader still pinned on every
  whole slot.
- test_shipsave_t360.cpp frozen-ring test: was re-listing ringSaves().front()
  per record (front == oldest-mtime == the slot being rewritten NOW, and slot
  identity drifted mid-test). Now pins ONE slot captured in the loop, read
  once. Law-neutral: the byte pins held on ALL 20 slots (_wip_t360 S2).
LAW: any test reading work/r1/playcap/save while production runs MUST be
torn-tolerant; the durable substitute is a banked dir (preplay bank).

### NEXT-SESSION RUNBOOK (also written into STATE queue)
1. python3 work/r1/t368_ring_turn.py  (sitting check, ring-first)
2. python3 scripts/r369_playwindow.py -> exit 1: not played, NEXT stays t369.
   exit 0: read lo_ns; BANK the ring NOW: cp work/r1/playcap/save/*.sav
   work/r1/bank-play-<date>/ (rotation law), then:
3. python3 scripts/r369_magnetron_hit.py --window LO -1  and  --dir bank-play-*
4. python3 scripts/r369_order_diff.py --window LO -1  and  --dir bank-play-*
5. Land witnesses per t370 row (annotate OQ-019 residue-(1) measurement-wise
   ONLY on a real witness; user-gated closes stay closed to user ruling).
