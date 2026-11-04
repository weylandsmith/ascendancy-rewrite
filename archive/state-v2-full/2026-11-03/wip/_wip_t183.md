# t183 WIP — OQ-019 scale + two-tier turn (static hunt)

Assignment (STATE.md t183): map the day-tick coupling and sub-turn
round-robin per ships.md §16 testimony. Start at the cited per-star
stride-0x60 pass 0x2547c and DAT_00012e10 readers; seek the scale factor
converting drive stat [+0x10] to walk units per sub-turn (walk body
0x533e0 callers), and whether lane transit is a separate law (magnetron
candidate 0x21f58 tie, §16 item 3). Deliverable: tier-specific scale laws
or the measured reason they are runtime-only.

Context carried in (verified, do not re-derive):
- COMMIT LAW: gizmo effects apply ONLY in player-command-exec 0x2547c..0x2559d
  (ah==3 -> 0x49f28(ship,1); ah==2 -> 0x39c10(ship,1)); all AI paths mode-0
  (combat.md S?/t8x).
- MOVES = [ship+0x94] re-granted each turn to drive stat SUM [ship+0x10]
  (@0x49b67, FUN_0004a658; live 32/35 rows). TRAVEL consumes it as RAW float
  distance: fild/fsub/fistp 0x4a30f..0x4a314 under the mode==1 commit gate
  (ships.md S12 t101 block).
- Drives rows 10..15 RANGE=STEP=0 in gizmo table; executor FUN_0004b8e4 has
  NO drive->distance term (S13). x32 unit law applies to gizmo RANGE/STEP
  only.
- Inter-system adjacency exists ONLY in lane matrix S11 (DAT_00045beb
  producer FUN_00023e00), used by AI, never by order execution.
- Walk body 0x533e0 rewrites ship coords per step call (S12/S16 t101).
- Ghidra addresses == docs addresses (obj0 image offsets; FUN names like
  FUN_000255a4 confirm).

## Probes (log)

P1 [verified Ghidra xrefs]: walk body 0x533e0 has EXACTLY 5 callers:
0x49ac2 (FUN_00049aa8), 0x1bd72 (caseD_0), 0x4a2cf (FUN_00049f54),
0x39a95 (FUN_00039a84), 0x1c710. 0x12e10 has 41 xrefs total incl. 3 inside
executor FUN_0004b8e4 (0x4bb8d/0x4c3c8/0x4c539) — day-coupling hunt ahead.

P2 [verified decompile FUN_00049f54 @0x49f54 — THE TRAVEL BODY; scale law
lives HERE, t13/t48's "not in executor" was right, executor isn't where
movement happens]:
- guard: [ship+0x58] must be 4 else runtime error (FUN_0002a428 @0x49f7f).
- target coords by order kind [ship+0x67]: 3=absolute float triple
  +0x6c/70/74; 1=pointer deref *(+0x68) floats [0..2]; 2=int handle +0x68 ->
  [+0x14/18/1c], if [+0x68]->0 == [ship+0x59] uses int fields +2/+3/+4
  instead; else bVar5=0 (no move).
- delta = target - pos([ship+0x9e/9f a2/a6]); d2 = dot(delta,delta);
  d = sqrt(d2) (FUN_00076da0).
- WALK = min(d, MOVES) where MOVES = float [ship+0x94].        <-- no scale
- steps = round(WALK) (FUN_00076e08), CLAMPED >= 1.             <-- floor-1
- FUEL CAP CLAMP: if int[ship+0x88] < steps: WALK := [ship+0x88]*WALK/steps;
  steps := [ship+0x88].  (fuel == step count, integral)
- arrived flag bVar5 |= 8 iff WALK == d (full distance affordable).
- FUN_00052fa0(dir, &out) normalizes delta -> *extraout_EDX (unit vector);
  per-step vector = unit * (WALK/steps) via two magic multipliers
  _LAB_00002603 (0x2603) and _LAB_00002604_3 (0x2604+3=0x2607) — SCALE
  CONSTANTS, raw-image bytes unreliable, resolving from scratch (P3).
- new pos = pos + unit*(WALK/steps)*scale1*scale2 written to +0x78/7c/80
  (destination) and +0x9e/9f/a2/a6 (current when param_2 != 1).
- commit iff param_2 == 1 (the mode==1 gate, matches COMMIT LAW):
  pos[+0x9e..] := walked result; [ship+0x88] -= steps;
  [ship+0x94] := round(remaining) (recomputed via FUN_00076e08);
  if arrived: kind 1 -> FUN_00049880, kind 2 -> FUN_00049a34 (arrival hooks).
- => SUGAR-CUBE ANSWER [inferred pending P3 constants]: drive stat IS
  world-units per tick 1:1 modulo whatever the 0x2603/0x2607 pair encodes;
  no [1,3] hop law exists in this function. Round-to-1 floor means a ship
  with 0 < MOVES always walks >= 1 step.

P3 [verified Ghidra]: f[0x2603] has EXACTLY ONE reference (the FLD at
0x4a1b1 inside FUN_00049f54). Disasm 0x4a161..0x4a23d shows the scalar
chain: unit = FUN_00052fa0(delta); v_i = unit_i * (WALK/steps) * f0x2603
* f0x2607 (d905 03260000 / d905 07260000 moffs loads confirmed verbatim).
Image bytes at 0x25fd.. are relocation-table garbage (not float-encoded),
consistent with t48's runtime-initialized-float finding — the restored
image carries no values for these two slots.
NOTE 0x12e10 xref census: 41 refs, ALL READ + 1 DATA table entry @0x9700,
ZERO WRITES in obj0 code — the "day counter advances daily" testimony
cannot be obj0-direct; writer is elsewhere (obj1/LEA blind per R12) or the
DAT is a config constant read everywhere. Reader set includes executor
FUN_0004b8e4 x3, FUN_00049c14, FUN_0004a96c (tiny getter?), the 0x40xxx
family (8 funcs), 0x44xxx/0x45xxx loose sites.

P4 [verified decompile FUN_0002547c (per-system command exec) + caller
chain FUN_00024f24 -> 0x25400 -> 0x2547c; FUN_000255a4 (AI orders) ->
0x2547c]: FUN_0002547c builds a list of players (of *(short)[campaign+0xd88]
total, skipping -1/AI-slot filter uVar1!=DAT_0007458e unless condition, and
requiring ownership bits [sys+0x14]|[sys+0x15] and (1<<player)), THEN
outer do { inner do { FUN_00041260(); dispatch local_1c: 2->FUN_00039c10,
3->FUN_00049f28, 0/1/other->FUN_0002a438 runtime-error line traps } while
more; } while (uVar5 != 0) -- i.e. REPEATS the whole sweep as long as any
resolver reports activity. ROUND-ROBIN MECHANISM lives in FUN_00041260
(verified decompile): per call it (a) collects this system's ships of the
player with [ship+0x88] fuel > 0 and [ship+0x58] != 1 (not orbital),
(b) picks ONE ship: min [ship+0x88] among ships with [ship+0x5d] != 0
(active order) (strict < keeps first-in-list on ties), (c) switch on order
kind [ship+0x5d] sets [ship+0x67]/[ship+0x68] target fields and emits the
dispatch byte, (d) returns -1 ('more work') while [ctx+0x39e]>>0x10 >= 1.
A ship that moved can be picked again next iteration if it still has fuel +
order => ships interleave one travel-call each per outer sweep, ordered by
REMAINING FUEL (not MOVES).
  LANE LAW IS REAL AND IS THE SAME WALK LAW: case 1 reads lane matrix
DAT_00045beb[starIdx(a) + starIdx(b)*100] (S11 matrix, 100x100) and
requires the chosen intermediate system's matrix entry == target's entry
MINUS 1 ('next hop reduces lane distance by exactly 1'), THEN sets kind 2
target=star object -- travel still happens via FUN_00049f54 raw-float walk.
So inter-system transit = float walk toward the next-hop star chosen under
the lane-distance gradient; NO separate lane speed, but the HOP CHOICE is a
real law (gradient -1 per system, matrix S11).
  MAGNETRON TIE NOW CODE-TRACED [verified, was UNMEASURED s16 item 3]:
inside 0x41260 the emergency branch at 0x415a6 sets [ship+0x62]=1,
[ship+0x63]=ship+0xab+slot*7, [ship+0x67]=5 (order kind 5), then calls
FUN_00049f28(ship,1) = the SAME travel commit entry. FUN_00049f54 kind
dispatch has no case 5 -> placement falls through to handler 0x21f58
(kind==5 go-to-star with rng jitter, kind 5->4). => magnetron transit
BYPASSES the lane-gradient gate and the MOVES walk: direct placement.
NOTE [inferred] the 0x415a6 branch fired for ships where FUN_00049768
returned a slot; whether that slot IS the lane-magnetron gizmo (row cat 5,
NumUses 1) is the remaining link -- FUN_00049768 is the slot finder;
kind==5 here shows kind 5 IS an order the resolver issues itself, matching
the magnetron's 'instant lane' semantics.

P5 [verified Ghidra xrefs 0x12e10]: 41 refs, ZERO writes in obj0 code (+1
DATA table slot @0x9700). A per-day auto-advancing counter cannot be
obj0-written directly (writer would be obj1/LEA-computed -- R12 blind, do
NOT byte-scan). Also 0x12e10 appears stored INTO a 4-byte field at 0x41d77
(decompiler shows ship+0x67 dword write spanning the order-kind byte; field
aliasing ambiguous; flagged, not banked).
TURN LOOP identified: FUN_00024f24 (sole caller 0x55f06) = campaign turn:
*param_1 (turn u32) incremented at END (verified *param_1 = *param_1 + 1);
runs 0x25400 (player command exec via 0x2547c) + 0x255a4 (AI orders) +
FUN_00038f68 sweep loop + per-race bookkeeping FUN_0003e6e0; day>=5000
endgame block at top. Orders execute INSIDE the turn loop; the testimony
'days advance on their own, one sub-turn per day' is NOT supported by obj0
code -- movement only happens when the turn loop runs.

P6 [MEASURED live-RAM, the scale constants]: restored image has ZERO
relocation/references to the travel-body float slots — method that worked:
anchor on live code (payload bytes at 0x4a161 found in save Memory at
0x209639; mapping law re-verified: code seg m = payload_off + 0x2095d6-...
=> guest-VA of a code byte = payload_off - 0x1d4000 + P0 + 0x14bb0 per the
pointer law), read the TWO LIVE FLD-moffs operands of the travel body
in situ: operands = 0x244603 and 0x244607 (restored-VA + 0x242000 exactly —
data-seg anchor payload 0x82bb0 -> m 0x242088 = payload_off - 0x82bb0 +
0x242088 re-confirmed). Slot values, STABLE across all 20 playcap saves
(41..60):
    m[0x24468b] = float 32.0   (0x42000000)   <- multiplier A
    m[0x24468f] = float  5.0   (0x40a00000)   <- multiplier B
    m[0x244683] = float  0.00625 (= 1/160!)   <- adjacent constant
    (neighbours are '..ship.cpp\0' debug-string bytes — Watcom const pool.)
  FUN_00052fa0 decompiled = pure normalize (v/|v|, guard |v|>0). So the
  travel law FUN_00049f54 (P2) in exact numbers:
    d = euclidean 3D distance (world float units)
    walk_units = min(d, MOVES[+0x94])
    steps = max(1, round(walk_units));  fuel cap: steps=min(steps,[+0x88]),
            walk_units scaled by fuel/steps
    displacement per step = unit_dir * (walk_units/steps) * 32.0 * 5.0
                          = unit_dir * (walk_units/steps) * 160.0
  i.e. ONE MOVES/step unit == 160 WORLD UNITS (32*5 = the same x32 gizmo
  unit law of S13 times 5). Star coords measured live (stride-0x60 star
  records, pos f32[3] @ name-0x14, 25 consecutive valid incl Arcturus idx23)
  span roughly +-500 with median inter-star dist ~500 world units => ~3
  step-units between adjacent-ish stars at drive ~32... [inferred]; the
  drive stat IS in step-units, scale factor to world = 160 EXACT [verified
  constants; product law verified from disasm 0x4a1b1..0x4a200 FMUL chain].
  The 0.00625 = 1/160 is the reciprocal, consistent.
  WALK BODY FUN_000533e0 (decompiled): quantizes the float coord to
  GRID = DAT_000895dc multiples: ((round(v)/g)*g per axis, g signed by
  direction) with g = DAT_000895dc (restored VA 0x895dc). LIVE VALUE
  MEASURED 0 IN ALL 20 playcap saves -> grid divisor 0 = law is degenerate
  no-op in this build/corpus OR DAT_000895dc is a base needing different
  mapping [flag: value 0 would divide-by-zero crash the real function; the
  decompiler's /iVar1 is integer div; a zero grid => the ship position write
  is 'round(v/0)'... actually code computes round(v) first then /g — a live
  g=0 WOULD trap; since no crash in 1250-turn campaign, either the function
  is only called with the quantize result unused (pos written before call)
  or the slot mapping is off. NOT banked; quantize law stays OPEN.]

P7 [verified decompile chain]: FUN_0003ea08 (per-player) loops all ships
of that player -> FUN_0004a658 (the MOVES re-grant law, S: [ship+0x94] :=
drive stat sum). Sole callers of 0x3ea08: 0x412d4 — the FIRST thing
FUN_00041260 does per resolver call (P4). => MOVES refills happen inside
each resolver pass, per ship, before selection: this is the 'sub-turn'
tick. Combined with P4/P2 the full per-call law: refuel-MOVES to drive sum,
pick min-fuel ship with an order, walk min(d,MOVES) units, spend steps of
FUEL (+0x88). Fuel is the cross-day budget (one refill of MOVES per
resolver call; FUEL is never refilled by movement — only by REFUEL order
'0x44 D' executor case, S13). 'If days advance before an order completes,
one sub-turn runs per day until arrival' maps to: each turn loop = 1
resolver cycle per ship; multi-day transit = fuel-limited, not MOVES-
limited. [inferred from verified pieces]

P8a [verified disasm 0x4159a..0x415c5]: the kind-5 emergency branch calls
FUN_00049768(ship, EDX=0x24) — slot-finder for gizmo INDEX 36. Over the
restored image, 0x415a1 is the ONLY call site of 0x49768 with a MOV EDX
immediate. Item 36 in the vendor gizmo list (extracted/ascend00/gizmos.txt,
row order Cat/Power/Range/Level/NumUses/...) = Line 268 'Lane^Magnetron'
(Cat 5 Special, NumUses 1). => the order-kind-5 branch IS the Lane Magnetron
consumer: it sets [ship+0x62]=1, [ship+0x63]=slot ptr, [ship+0x67]=5, then
FUN_00049f28(ship,1) — magnetron activation goes through the TRAVEL COMMIT
entry, and the walk body's kind dispatch (kinds 1/2/3 only) skips the walk,
landing in the go-to-star placement (0x21f58 law, rng jitter). §16 item 3
tie: CODE-TRACED now (static), live observation still absent.
P8b [MEASURED]: grid quantizer DAT_000895dc (used by walk body FUN_000533e0
as integer grid: coord := round(coord/g)*g per axis, g signed by direction)
= 32 in ALL 20 playcap saves (slot m = payload_off 0x895dc + 0x1bf4d8;
mapping re-verified by the 32.0 float at VA 0x244603 -> m+0x88). NOTE my
first read (0) used m = va+0x242088 for a CODE-seg-adjacent DAT — wrong;
DAT restored-VAs are payload offsets (m = DAT_va + 0x1bf4d8 this run);
the +0x242088 law is for data-seg VAs >= 0x82bb0. Both slots re-read clean.
  QUANTIZE LAW: live g=32 => ship position snapped to multiples of 32 world
  subunits (matches the x32 gizmo RANGE unit law S13: gizmo dwords <<5).
P8c UNIT-SYSTEM CAVEAT (honest, blocks full closure): the travel body walks
in [ship+0x9e] units and needs MOVES >= d(+0x9e units) to ARRIVE; live MOVES
= 32-35 (t101) while star-record pos f32[3] (name-0x14, stride 0x60) has
median inter-star ~499 (measured 25 stars, Arcturus idx23 anchor). If +0x9e
were the same unit as the star table, a drive-32 ship could never arrive
anywhere — so either +0x9e is the 32-subunit grid (star table in coarse
units) or placement (kind 5 / arrival) re-projects units. The 32.0/5.0/
0.00625(=1/160) triple multiplies the walk DELTA, and FUN_000533e0 quantizes
by 32 — consistent with: +0x9e grid == subunit/32, one MOVES point == 5
grid steps? [UNRESOLVED]. The decisive measurement is a consecutive-save
position delta of an in-flight ship (BLOCKED t48 route: zero flights in all
passive corpora; needs a played capture with an order given).
DELIVERABLE VERDICT: scale CONSTANTS measured with citation (160 = 32*5
delta multiplier, 1/160 reciprocal, grid g=32); the tier/tick structure is
CODE-MAPPED (P4/P7: round-robin min-fuel resolver, MOVES refill per
resolver call at 0x3ea08<-0x412d4, turn loop FUN_00024f24 turns += 1 at
end, no autonomous day-tick in obj0 — 0x12e10 has 0 writers); lane transit
is the SAME walk law under a lane-matrix -1 gradient (verified in
FUN_00041260 case 1); magnetron is kind-5 placement bypass (P8a). Row OQ-019
STAYS OPEN: unit-system tie + live flight observation missing; per-ship
redesign inventory also still open.

P9 [CORRECTION to P8a, verified]: gizmo index order check (t46 file-order
law, gizmos.txt row count 76) puts index 36 = 'Disarmer', Lane Magnetron =
row 59. Slot census 60.sav: 15/35 ships carry idx36, 0 carry idx59, and
magnetron presence does NOT predict off-grid positions. => the kind-5
immediate-0x24 branch is NOT proven to be the Magnetron; ships.md S17 T6
carries the corrected statement. LESSON: check vendor file-order identity
BEFORE banking a gizmo-name tie.
FINAL: ships.md S17 written; OQ-019 STATUS t183 appended (row OPEN);
STATE.md NEXT=t184 (build/redesign inventory path — last offline leg);
gate 0, LEDGER AUDIT OK.
