# WIP t190 — lane-record struct + writer of byte[H+0x23] (OQ-019 residue)

Intake (2026-10-29, session start):
- Steering note in prompt-112 was t189b (merge) — ALREADY LANDED at HEAD 6f4ad8d
  (tree clean, journal sha matches). Assignment = STATE.md NEXT = t190.
- Pre-checks (all negative, same shape as t189):
  - live-timeline tail: turn=0 rows only (wall 00:12:43/44) — ring holds the
    player's new-game saves, no real turns past 1335.
  - dosbox: no procs.
  - grep -o 'sel=[1-9]' watch.out: zero.
  - grep -c 'DAT_482fb=2[5-9]' watch.out: 0.
  -> no live-handle dump possible; static hunt only.

## Findings
(to be appended as probes land)

## F1 (strong, needs byte-level witnesses) LANE RECORD == THE t52 "HELPER CLUSTER WORKING FRAME"
FUN_00023e00 (0x23e00, sole caller FUN_000234a4@0x234c8) builds per-pair
candidate frames ON A RUNNABLE FRAME POINTER (decompiler reads/writes
pfVar8[-2..+10] across calls => walking an ARRAY, not a stack local):
  frame+0x00 u32  star A ptr        (iVar3 = *star_ptr_slot)
  frame+0x04 u32  star B ptr        (piVar5 = candidate ptr)
  frame+0x08..0x10 f32 A.x A.y A.z  (copied from A+8/+c/+10)
  frame+0x14..0x1c f32 B.x B.y B.z
  frame+0x20 f64  squared chord     (double store at pfVar8-2 == frame+0x20)
  frame+0x28 short nearest-idx      (short store at pfVar8+0xc)
  frame+0x2a..   next frame         (frame stride 0x2c)
STRIDE MATH VERIFIES EXACTLY vs the march body FUN_0004a74c's field law:
  H=frame ptr; H[0]=A, H[4]=B; coords A@+8/+c/+10 B@+14/+14+4/+14+8;
  => byte[H+0x23] sits in the f64 squared-chord bytes [0x20..0x27],
  high dword bytes 0x24..0x27; byte 0x23 = LOWEST BYTE OF THE MANTISSA of
  (double)|B-A|, whose LSB == 1 iff |B-A| in [1,2) U [2,4) is odd-interval...
  exact law: mantissa-byte0 LSB of the double.
NB decompiler constants 0x23fad/0x23fb2 tagged near the sqrt calls are
IMAGE ADDRESSES (t52 banked them as call-site tags) — do NOT confuse with
offset 0x23. This hypothesis makes gate1 arithmetic-derived, not authored:
slow lanes would be a MEASUREMENT ARTEFACT of chord length in the double.
BUT: chord ~1100-2500u -> double exponent ~2^11 -> byte0x23 = mantissa bits
[51:44] — NOT LSB-gated; bit0 of byte 0x23 = mantissa bit 51 (the hidden-bit
adjacent MSB+... ) => bit0 fires for ~half of all chord lengths pseudo-
randomly?? NO WAIT: mantissa MSB region: for value V=1.5xx*2^11, high byte
0x23 position holds mantissa bits 51..44 -> bit0 = mantissa bit 44. Fires
for chords whose mantissa bit44 set — ~50% of chords. Corpus: 3 slow handles
vs 15 fast = NOT 50/50 (1/6) but handles are lane-specific, small sample.
RESOLVE: read the actual FUN_0004a74c code for what gate1 does with the
byte (bit test confirmed t189), then compute chord values for the known
SLOW lanes (slot17 handle 0x2589cf lane z=544: endpoints 544 apart? chord
from banked x-saturation ~224 slot13-fast) and FAST lanes, and check the
mantissa-bit44 prediction against them. If chords are e.g. lane z=544 (fast
slot13 saturating 224 = its lane_len L per S22) test bit44 of double(224.0)
etc. If prediction fails, F1 is structure-right/byte-wrong and +0x23 is
padding the producer NEVER wrote (then it is written elsewhere: hunt next).

## F2 [verified disasm] THE t52 "mapping tension" IS CLOSED: DAT_00045beb == matrix base
0x23e15: `LEA EAX,[ECX+0x32ddb]` (ECX=DAT_00012e10 runtime ptr, FUN_00076e30
wrapper) — Ghidra folds the seg base and reports the DATA ref at DAT_00045beb
(0x12e10+0x32ddb = 0x45beb EXACTLY). 0x23e3a WRITE: byte [DAT_00045beb +
100*s + s] = 1 -> the "101-stride" t52 saw == 100-linear matrix DIAGONAL in
the SAME buffer the consumer @0x41b03 reads `[100*x+y+0x45beb]`. ONE padded
no — ONE LINEAR 100x100 lane-adjacency matrix; t52's two-buffer question:
answered (single buffer), and the runtime location is DAT_00012e10-base
relative, i.e. it lives inside the scenario object, NOT a static DAT — which
is also why the t52 raw-sample read at member B+0x45beb contradicted the law
(wrong window, tension explained).

## F3 [verified disasm 0x23ef4..0x23f23] producer skip-gate order
per (i,j): skip iff adjacency byte[DAT_00045beb + 100*row_i + j] != 0
(pre-seeded lanes / diagonals), THEN skip iff owner-name short compare
word[star+0x44] == word[DAT_000063c6 + *starptr*2] — i.e. the producer only
probes NON-adjacent pairs => FUN_00023e00 computes nearest-NON-NEIGHBOUR,
the t52 text "skip-gate (==0 -> candidate)" had the polarity BACKWARDS
disasm: CMP byte[..],0 / JNZ skip -> candidate requires byte == 0. [re-read:
JNZ 0x23ee6 = continue loop when byte != 0, so byte==0 IS the candidate — t52
wording stands.]

## F4 [DECISIVE, verified disasm] byte[lane+0x23] bit0 WRITER FOUND
0x247dd CALL FUN_00021ad8 -> EAX=lane record ptr -> 0x247e2 MOV ESI,EAX ->
0x247f7 `OR byte ptr [ESI+0x23], 0x1` (bytes 804e2301). Context disasm
0x247c8..0x24832 verbatim. Site = inside FUN_0002446c (the t52 "helper
cluster" was really this family; FUN_0002446c is the SECOND producer run by
FUN_000234a4 after FUN_00023e00). So bit0 is SET at lane-creation time by
the builder, on the record FUN_00021ad8 just linked. Also every other
+0x23 site census (search_instructions '0x23]'): FUN_0004ca50 AND 0xfd
(0x4cbfd) / OR 0x2 (0x4cc0e) — bit1 churn (magnetron territory t185);
FUN_000499f8 + FUN_00041b42 TEST bit1; march body reads bit0 (0x4a837/42).
bit0 WRITERS: only 0x247f7 (OR 1). bit1 writers: 0x4cbfd/0x4cc0e. NO site
clears bit0 -> ONCE A LANE IS FLAGGED IT STAYS 1/3-SLOW FOREVER.
## F5 FUN_00021ad8 = LANE-RECORD ALLOCATOR+LINKER (structure CLOSED)
decompile: validates both stars' kind word (+0x42>>0x10 in [0,5]); if
neither endpoint is "last-connected" (short compare vs DAT_00088f76/
DAT_000063c6 tables), calls FUN_00024834 (ALLOCATOR, only 2 callers:
0x21d2b? inside 21ad8 + check) then registers: starA.slotarray[+0x2c +
kindA*4] = rec; starA.count[+0x44]++; starB.slots[+0x2c+kindB? word
param_2[0xb]+..]; rec floats: +8/+c/+10 = B-A, +14/+18/+18 = A-B (EXACT
NEGATES). Matches the march body reading ptr[H]=A ptr[H+4]=B? NB allocator
writes rec+8 = B-A coords; the march reads [H+0] and [H+4] as STAR PTRS.
=> rec[0x00] = starA ptr, rec[0x04] = starB ptr (set inside FUN_00024834
presumed -- verify next probe). LANE RECORD STRIDE? allocator answers.
## F6 FUN_000234a4 = MAP-LANE BUILD PIPELINE (scenario init):
matrix-diag seed (0x23e00 via 0x23e15 LEA [ECX+0x32ddb], ECX=DAT_00012e10;
0x45beb = same buffer, t52 tension CLOSED: one linear-100 matrix inside the
scenario object at DAT_00012e10+0x32ddb) -> loop {FUN_00024018; FUN_0002446c}
while [obj+0x32dcf]>>0x10 > 1. FUN_0002446c picks per star the nearest star
NOT ALREADY ADJACENT (byte [mat +100*a + b]==0 gate at 0x246..), connects it
via FUN_00021ad8, sets bit0 on the NEW LANE + byte[star+0x18]|1 on both ends.
SO: bit0 == "this lane is a GENERATED NON-NEIGHBOUR link" i.e. NOT a real
authored starlane -- it is the long-haul filler lane the MST-ish builder
added. x1/3 multiplier on NON-NEIGHBOUR lanes = gameplay SENSE (long
hyperspace-style links are slow). Semantics CANDIDATE but must cite the
AUTHORED-lane path: who else calls FUN_00021ad8 WITHOUT the OR (then bit0=0
=> fast). Callers of 0x21ad8 = exactly {0x23feb in FUN_00023e00, 0x247dd in
FUN_0002446c}. 0x23feb site = FUN_00023e00's "not-found path" (nearest
non-adjacent star failed? no: runs when best found); does IT set +0x23?
check bytes after 0x23feb. IF the 0x23feb path leaves bit0 = allocator-init
value, the allocator's zeroing decides. NEXT: FUN_00024834 (zero fill?) +
0x23feb post-bytes.

## F7 [verified disasm 0x248ab..0x248bb] ALLOCATOR INIT (FUN_00024834)
rec = scenario_ptr + 0x3337 + count*39 (IMUL 0x27 form at 0x24895..0x248a7;
count u16 at scenario+0x49c3 folded = DAT_000049c3; CAP = 0x94 = 148 lanes
(guard 0x2485f CMP EBX,0x94)). INIT WRITES:
  0x248ab MOV byte [rec+0x20], 0x0      <-- ONLY init touching the +0x20..0x27
                                             window; byte +0x23 NEVER written
                                             here (stale-pool byte!) [see F8]
  0x248af MOV [rec+0x00] = starA ptr
  0x248b1 MOV [rec+0x04] = starB ptr
  symmetric matrix-set byte[matrix + 100*a + b] = byte[+100*b + a] = 1.
RECORD LAYOUT CONFIRMED vs march body: [0]=A ptr [4]=B ptr, floats +8..;
STRIDE 39 BYTES. HANDLE LAW UPGRADE: t189 handles
0x258933-0x2589cf = 234 = 6*39 and 0x2589cf-0x2589f6 = 42 = 2*39 EXACT —
the three SLOW handles are CONSECUTIVE lane records (idx k, k+2, k+6... same
parity class); 0x25820a (fast) sits (0x2589cf-0x25820a)/39 = 57.0 records
earlier. POOL base = scenario DAT_00012e10 + 0x3337 -> linear ~0x2580xx
window in saves MATCHES the t189-observed 0x258xxx pointer window exactly
(pool lives there; STATE's 0x258000..0x258FFF guess now has a producer).
NB FUN_00021ad8's float fill (+8..+1c = B-A / A-B negates) — allocator's
rec+8 floats are OVERWRITTEN per-creator; march reads them as coords, fine.

## F8 [verified disasm + arithmetic tie] SCENARIO-OBJECT LAYOUT DECODED
FUN_00024834 uses raw [ECX+0x49c1]/[ECX+0x49c3] (unrelocated) and
[ECX+0x32ddb] (folded to DAT_00045beb) on the SAME ECX => ECX = scenario
runtime base S where S+0x49c1 == DAT_00045beb - 0x12e10 + ... resolving:
  S(linear) = DAT_00012e10_base + (relocated 0x45beb - 0x12e10) ... = 0x254cc9
  CHECK (independent): species table t189 relocated base 0x254fb3 ==
  S + 0x2ea, and DAT_00012fb3 = 0x12e10 + 0x2ea. EXACT.
LAWS FROM FUN_00024834 disasm:
  lane pool base = S + 0x3337 = 0x258000 (linear)  <-- the t189/STATE
    0x258xxx window IS THE LANE POOL, now with a producer;
  lane stride 0x27 = 39 bytes (IMUL chain 0x24895..0x248a7);
  count u16 S+0x49c3, cap guard CMP 0x94 = 148 lanes;
  rec+0x00 = star-A OBJECT ptr; rec+0x04 = the lane's ENTRY IN THE OTHER
    ENDPOINT'S LIST (rec+4: [rec+4]=B obj ptr, [rec+8..]=B-A;
    FUN_000241fc walks rec[0]->idx then (rec[1])[0]->idx, idx=-1 sentinel);
  rec+0x20 byte ZEROED at alloc (0x248ab); byte +0x23 NOT initialized by
    the allocator;
  adjacency matrix set SYMMETRIC byte[S+0x32ddb + 100*a + b] = 1 both ways.
HANDLE ARITHMETIC (old-game handles, t189): (0x258933-0x258000)/39 = 37.0
fast 0x25820a -> idx 13.0; 0x2589cf -> 40.0; 0x2589f6 -> 41.0 — ALL FOUR
lane-pool-congruent (mod 39) — HANDLE = LANE RECORD PTR CONFIRMED.
SLOW idx {37,40,41} low-mid pool vs FAST idx 13. FUN_00023e00 (bit0-never
-set caller of 0x21ad8) runs BEFORE FUN_0002446c (the 0x247f7 OR-or site)
in FUN_000234a4's pipeline, so pool-phase attribution ALONE predicts the
OPPOSITE (low idx = 23e00 = bit0 clear = fast) — therefore EITHER the
authored/pre-loaded pool content carries bit0 (loader-sourced), OR my
phase order assumption about WHICH lanes 23e00 vs 2446c allocate is wrong
(2446c's outer loop also allocates from the shared counter). RESOLVE by
reading the pool bytes 41..60.sav (labeled OLD-GAME RESIDUE, valid as a
snapshot of the old scenario's lane table per t189 CORPUS CAVEAT).
FUN_00024018 (pipeline step 1): stars with idx==-1 (unconnected) get
connection blocks; FUN_000241fc recursion over lane lists. Pipeline:
{matrix seed} FUN_00023e00 -> [obj+0x32dd1]=2 -> loop{FUN_00024018;
FUN_0002446c} while ([obj+0x32dcf]>>16)>1.

## F9 [verified] SEGMENT ARITHMETIC UNIFIES THE WHOLE STRUCT (S = data base)
0x23e09 `MOV ECX, 0x12e10` hard-coded = DATA-SEGMENT window base: image addr
X < 0x14bb0 maps to linear P0 + X + ... law: mem = image + 0x12e10 within
obj0 (code mem base 0x1d4000 = P0+0x14bb0 -> 0x1d4000-0x14bb0 = 0x12e10).
So "scenario object" == THE DATA SEGMENT ITSELF:
  S(linear) = P0 + 0x12e10;
  adjacency/distance matrix = S + 0x32ddb = P0 + 0x45beb (folded DAT_00045beb);
  star table (slot objects stride 0x60) = S + 0xdb5 = P0 + 0x13bc5 (folded
    LAB_00013bc5 -- the 0x13bc5 xref list t190 probed = THIS table);
  star count u16 = S + 0x3335 = P0 + 0x16145 (0x23e20 verbatim [0x00016145]);
  LANE POOL = S + 0x3337 = P0 + 0x16147, stride 0x27=39, count u16 S+0x49c3
    = P0+0x177D3, cap 148 (0x2485f CMP EBX,0x94), byte[rec+0x20]=0 init
    (0x248ab), byte +0x23 NEVER initialized by allocator.
MEMBER FORMULA (pointer-index corollary): member = B + X for image offset X;
physical/linear = member - 0x88. HANDLE ARITHMETIC FIXED (F7 had sloppy
division): old-game handles congruent mod 39:
0x2589cf-0x258933=156=39*4; 0x2589f6-0x2589cf=39; 0x2589cf-0x25820a=1989=
39*51 -- ALL FOUR ARE LANE-POOL POINTERS, same pool; absolute idx lost with
P0_old. Fast idx = K, slow = K+51, K+55, K+56.

## F10 [verified disasm] FUN_0002351c = PHASE-1 MAP LOAD: loads 39-byte
AUTHORED lane records from the SAME pool (piVar13 = param+0x3335+2 =
pool base; stride 0x27; count = [param+0x49c1]>>16), sets matrix pair=1 both
directions for each, then BFS floods matrix with SHORTEST-PATH HOP DISTANCES
(2,3,4...; 0xFF unreachable) -- explains t52's raw sample {0,1,2,...}
diagonal + 79 cells 0xFF: t52 sampled NEIGHBOURHOOD of this matrix with the
wrong base; buffer identity question CLOSED (one matrix, hop distances).
FUN_000234a4 (pipeline): zeroes lane count (0x234d0 [S+0x49c3]) AFTER
FUN_00023e00 -> then allocators RE-USE pool from idx 0?? -- OR THE PHASE-1
LOAD NEVER FILLS THE POOL for random maps (authored-pool scenarios only).
DISCRIMINATOR = the new-game t=0 saves (both pipelines ran at scenario init):
dump pool +0x23 bytes. H1: lanes split flag0 (23e00 nearest-neighbour
creator, 0x23feb CALL with NO OR site) vs flag1 (2446c creator 0x247f7 OR
0x23,0x1). FUN_0002446c read fully: per GROUP (S+0x30701 + e*0x19e record,
count u16 +0x190/+400, star ptrs +0, centroid f32[3] +0x192) picks nearest
star PAIR with matrix==0; loop {24018 (group unconnected stars idx==-1,
centroids), 2446c} until components==1 -> 2446c lanes are CONNECTIVITY
BRIDGES between star clusters. FLAG1 = bridge lane = x1/3 SPEED. Corpus
consistency [inferred]: 50-star map -> 23e00 lanes idx 0..~49, bridges idx
50..; old-game slow handles K+51/K+55/K+56 BEAT ABOVE the fast idx K --
DIRECTION EXACTLY AS PREDICTED.

## F11 [MEASURED r1_t190_lane_pool.py RC=0, 20/20 saves, dump work/r1/t190_pool_dump.txt]
NEW-GAME LANE POOL LIVE (both pipelines ran at scenario init):
  star_count=50 (B+D+0x16145), nlanes(u16@0x177D3)=58, pool recs at
  member B+0x82bb0+0x16147 (physical 0x258147 in this run);
  rec[0]/rec[4] = STAR OBJECT LINEAR PTRS congruent to star base
  (0x255bc5 = B+D+0x13bc5-0x88, stride 96): rec0 b-idx 39.0, rec1 29.0,
  rec2 27.0, rec3 16.0, rec4 37.0 ALL INTEGRAL -- struct identity PROVEN on
  live data.
  +0x23 CENSUS: {0x00: 50 recs (idx 0..49), 0x01: 8 recs (idx 50..57)} in
  ALL 20 SAVES EXACTLY. The split IS the phase split: FUN_00023e00 nearest-
  neighbour phase created exactly n=50 lanes (one per star; its 0x23feb
  caller never sets the flag), FUN_0002446c bridge phase appended 8 lanes
  (components-1) and 0x247f7 OR'd bit0 on EXACTLY those 8. SEMANTICS OF
  byte+0x23 bit0 := "lane added by the connectivity-BRIDGE phase" (not an
  authored starlane). x1/3 speed applies to BRIDGE lanes.
  OLD-GAME HANDLE TIE: fast 0x25820a and slow 0x258933/cf/f6 are ALL
  congruent to the pool base mod 39 (deltas 195=39*5, 2028=39*52, 2184=39*56,
  2223=39*57 EXACT) -- handle == lane-record pointer CONFIRMED; old pool base
  (old P0) unrecoverable (saves overwritten) so old-game ABSOLUTE idx order
  can't be read directly; the new-game census proves the mechanism and the
  50/8 shape (a 50-star old map predicts the same split).
  SPECIES col0x12 (gate 2): rows 0..23 at image 0x12fb3 stride 0x1ee: values
  {0 x17, 27, 38, 40, 110, 115, 116, 172} -- NO 0x12 IN ANY ROW, 20/20 LIVE
  saves (this time LIVE tables, not dead residue). Gate 2 has ZERO shipped-
  campaign witnesses -> x2 branch dead code for the banked scenario set.
  ships=0 in all 20 (new game fleetless) -- no st5 handles readable now.
