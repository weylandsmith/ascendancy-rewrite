# t284 WIP — rewrite the V (DAT_482fb) semantic

Task: STATE.md NEXT ACTION t284. Mirror the t283-witnessed producer cadence in
the rewrite. Strict-close: OQ-021 stays OPEN (threshold residue).

## Working notes (static decode of the producer, payload file 0x24274..0x243fc)

Disassembled `objdump -b binary -m i386 -M intel -D` from work/ascend_payload.bin.
Mapping sanity: fire EIP 0x1e3803 - (B-0x88 = 0x1bf450) = 0x243b3, and
code-object load 0x1d4000 + (0x243b3 - 0x14bb0) = 0x1e3803 EXACTLY — so payload
file offsets here equal Ghidra (imagebase-0) addresses for the code object.

Frame: prologue 0x24274 `push ebx/ecx/esi/edi/ebp; sub esp,0xc`, epilogue
0x243f4 `add esp,0xc; pop*5; ret`. ONE function; args arrive in eax (object)
and edx; `mov ebp,eax` at 0x2427c. Witnessed ebp=0x254e10 = runtime address of
Ghidra data 0x12e10 (runtime data base 0x242000), so [ebp+0x354eb] ==
runtime 0x28a2fb == DAT_000482fb (t283's arithmetic anchor, re-derived).

KEY DECODE (this iteration, [verified] from the disasm, cross-cited):
* `imul ecx,ecx,0x1ee` + `cmp BYTE PTR [ecx+eax+0x12fd6],3` at 0x2437e..0x2438c
  (and the twin at 0x242a3..0x242bd): 0x12fd6 == 0x12e16 + 0x1c0 where 0x12e16
  is the banked DIPLOMACY race-table base (stride 0x1ee — debugflags.md
  "DIPLO ROW CLONE", _wip_t180 P2). So the cell is
  relation[playerIdx][raceIdx] and the compared value 3 is the OQ-023-closed
  ALLIANCE state (docs/re/diplomacy.md §13/§16: 2=WAR, 1=PEACE, 3=ALLIANCE).
  ecx is built from BYTE ds:0x7458e == CURRENT-PLAYER INDEX (aicode.md §7.3).
  => the predicate t283 left undecoded is an ALLIANCE test against the current
  player, with an explicit self-skip (`cmp eax,ecx; je skip` right before it).
* ship loop bound 0x6b (107) at 0x24347 = ship-slot capacity; live gate
  `cmp dx, WORD ds:0x4348b` = r1_slot.py law (live count = u32@0x43489>>16,
  hi u16 at 0x4348b).
* ship field `[ecx+0x3a0e9] >> 16` (ecx = idx*0x162) is the OWNER word
  (== -1 -> dead/empty, skip); r1_ship_array base = B+0x82bb0+0x3a095 stride
  0x162, so 0x3a0e9 - 0x3a095 == +0x54 = the t273 owner HANDLE u16 (t273 law:
  owner INDEX is byte +0x56, handle u16 +0x54 — check which one this is before
  asserting the semantic).
* `[ecx+0x3a0ee]` (== ship +0x59) is compared against `esi` (the sub-object
  pointer) — a back-pointer identity test, i.e. "this ship belongs to the
  object we are scoring".
* outer loop: `[obj+0x44]` = sub-object count, list at `[obj+0x2c]`
  (u32 array, indexed <<2); `cmp WORD PTR [esi+0x21],0` gates re-processing
  and the store path SETS `[esi+0x21]=1` — a VISITED/processed mark per
  sub-object, so the counter can only grow once per sub-object.
* first block 0x24281..0x242e0: builds a bitmask in [esp+0x8] over ALL races
  r < WORD ds:0x13b98 (race count, 4 in 20/20 saves — _wip_t205) where
  relation[player][r] == 3 (ALLIANCE). Consumed at 0x2431a..0x24337 as
  `(~alliedMask & (obj+0x14 & ~alliedMask | obj+0x15 & alliedMask)) & ~bit`
  must be zero ... (bit = 1<<playerIdx; obj+0x14/+0x15 = byte pair of a u16)
  => a per-object "does this object qualify for the player's score" test that
  mixes the object's own owner-bitmask pair (+0x14/+0x15) with the allied mask.

## VALIDATION — REPLAY OF THE DECODED PRODUCER AGAINST THE BANKED CORPUS
## [measured, scripts/r284_vreplay.py, work/r1/t284_vreplay_all2.out]

The decoded flood was re-implemented in Python and replayed against EVERY
readable banked save (all work/r1/*/save dirs, 409 in-game slots, 20+ runs,
turns 1..1255). Two independent agreements were measured:

1. V VALUE: 295/409 EXACT. All 114 disagreements are `predicted>0, stored 0`
   = saves captured after load but BEFORE the first End-Turn — precisely the
   S10 #2 population ("every session's load turn reads V==0"). ZERO rows with
   V>PRED, ZERO rows where both are nonzero and differ. Nonzero-V EXACT ladder
   (60 rows) spans V=1 (t1..t52 across 13 runs), V=14 at t1255 (t260-loadstate,
   t261-drive) and V=23 at t1087 (t283-wp runs 8,9 — the watched walks' own
   terminal value).
2. LANE-MARK FOOTPRINT: predicted visited set == the save's persisted lane
   +0x21 marks in 409/409 slots (both set differences empty, every slot).
   The marks are the pass's own writes, so this independently confirms the
   flood's PRUNING decisions, not just its count.

CONSEQUENCE FOR S10 #3 [superseding]: "V depends on lineage history, not the
snapshot" is now REFINED — V IS a pure function of the snapshot (visibility
masks + relation cells + ship order pointers), and it is those fields that carry
the lineage. The t1254 V=14-vs-23 pair never needed history: the replay
reproduces 14 at t1255 from the snapshot alone.

GATE CENSUS on the production save (t1086, V=0 stored, 22 lanes visited):
22 PASS, 2 FAIL-presence, 0 FAIL-visibility, 0 FAIL-contest. So at that
operating point the PRESENCE gate is the sole discriminator; the contest gate
has no witness there (its mechanism is nonetheless verified below).

POINTER-CLASS MEASUREMENT OF THE CONTEST INPUT [measured, 6 saves x 107 slots]:
ship+0x59 decoded with the POINTER LAW (X = p - (B-0x88+0x82bb0)) classifies by
order kind byte +0x58: kind 5 -> LANE-POOL records (lane 57 x72, 12, 18, 35,
43, 51, 56, 7), kind 4 -> STAR records (STAR2/12/36), kind 3 -> heap block,
kind 0 -> NULL (924/1284 idle ships). The earlier "not congruent to any pool"
reading was MY OWN 0x88 trap (scripts/r284_contest_census.py / r284_deref.py
decoded pointees against B+0x82bb0 instead of B-0x88+0x82bb0) — the law was in
score.md S2 all along. So the producer's `cmp ship(+0x59), lane` is EXACTLY a
"ship holds an order into this lane" test, and ships transiting a lane DO carry
that lane pointer.

PRESENCE-MASK MEANING [measured, production save]: (star+0x14 | star+0x15) low
7 bits == the set of races owning a planet at that star in 48/50 stars
(owner-any set from the banked planet-record law: byte +0x0c star index, +0x57
owner). The 2 exceptions (stars 2, 12) carry a bit for a race with no planet
record there — partial/captured presence, unmodelled by a single-owner rewrite.

## THE LAW, DECODED (Ghidra FUN_00024274 + FUN_00024f24, cross-checked vs
## objdump of the payload — the two agree instruction-for-instruction)

BASE OBJECT RESOLVED (this is the piece t283 left as an arithmetic coincidence):
witnessed ebp = 0x254e10 == (data base 0x242000) + 0x12e10, and DAT_00012e10 IS
THE TURN COUNTER (selfplay.md:235 "turn X=0x12e10", _wip_t183 P5: 41 xrefs,
ZERO writers in obj0). So the producer's param_1 is THE GAME-STATE OBJECT rooted
at 0x12e10; [ebp+0x354eb] == 0x12e10+0x354eb == 0x482fb exactly (no heap copy
involved). FUN_00024f24 ends with `*param_1 = *param_1 + 1` — the turn increment
— which independently confirms the identity.

FUN_00024f24 = THE END-OF-TURN PASS (AI loop `for r < word[0x13b98]` calling
FUN_0003e6e0 per race, then the player). Its tail, verbatim from Ghidra:

    // clear the per-lane mark: 0x12e10+0x3337 == 0x16147 == LANE POOL base
    // (debugflags.md lane-reveal law: lane_pool[0x16147 + i*0x27 + 0x20]),
    // bound DAT_000177d3 = lane count, stride 0x27:
    for (i < laneCount) *(u16*)(lane(i) + 0x21) = 0;

    if ((*(u8*)(*(u32*)(&DAT_00012e1d + playerIdx*0x1ee) + 0x14) & (1<<playerIdx)) == 0)
        *(u32*)(state + 0x354eb) = 0;          // V = 0
    else {
        *(u32*)(state + 0x354eb) = 1;          // V = 1  (HOME SYSTEM counts as 1)
        FUN_00024274(state, homeStar);         // flood
    }

`&DAT_00012e1d + idx*0x1ee` = field +7 of the race record (race table base
0x12e16, stride 0x1ee — _wip_t180/OQ-023) DEREFERENCED as a u32 pointer, then
byte +0x14 of the thing it points at. So the reset test reads the HOME STAR's
+0x14 mask bit for the player: player's home system no longer marked as his ->
V collapses to 0 and the flood never runs.

FUN_00024274(state, fromStar) = THE FLOOD OVER THE STAR/LANE LINK GRAPH:

    allied = 0
    for (r < word[0x13b98])                       // every race
        if (relation[player][r] == 3) allied |= 1<<r      // 3 = ALLIANCE (OQ-023 CLOSED)
    for (k < fromStar->laneCount /* +0x44 */) {
        lane = fromStar->laneList[k]              // +0x2c = u32 ptr array
        if (lane->mark /* +0x21 */) continue
        far = lane->ep0                           // +0x0
        if (far == fromStar) far = lane->ep1      // +0x4  -> "the other end"
        if ((far->m17 /* +0x17 */ >> playerIdx) & 1
            && (((~allied & (far->m14 | far->m15) & 0x7f) & ~(1<<playerIdx)) == 0)) {
            // CONTEST TEST over the live fleet:
            seen = 0
            for (s < 0x6b && seen < liveShipCount /* word ds:0x4348b */) {
                owner = ship(s)->owner /* +0x54 >> 16 */
                if (owner == -1) { s++; continue }
                seen++
                if (ship->orderTarget /* +0x59 */ == lane
                    && owner != player
                    && relation[player][owner] != 3) break     // CONTESTED
                s++
            }
            if (seen >= liveShipCount) {          // loop completed == no break
                lane->mark = 1
                state->V /* +0x354eb == DAT_000482fb */ += 1
                FUN_00024274(state, far)          // RECURSE into the far star
            }
        }
    }

FIELD IDENTITY CROSS-CHECKS (all banked, none invented):
* lane pool 0x16147 stride 0x27 with +0x20 = lane visibility mask
  (debugflags.md LANE REVEAL law); +0x21 is the byte this pass clears and the
  producer sets — the per-pass VISITED mark. t195 banked laneVis_ == rec+0x20.
* star record stride 0x60 base 0x13bc5; +0x16/+0x17 = the twin visibility masks
  (debugflags.md STAR REVEAL writes 0x13bdb/0x13bdc == base+0x16/+0x17; t193
  census; t195 starLaneVis_/starSelVis_). The producer tests +0x17 (starSelVis_
  analog) on the FAR star and +0x14 on the HOME star.
* ship +0x54>>16 = owner race index (r1_slot law; ships.md:913 "species row idx
  = (dword[ship+0x54]>>16) into stride-0x1ee"); ship capacity 0x6b = 107 slots;
  live count = u32@0x43489>>16 == word@0x4348b (r1_slot.py SHIP dict).
* ship +0x59 = the ORDER TARGET pointer, and it holds a STAR-LANE pointer for
  lane-bound orders (ships.md:729/762/775-776, 0x4cd19 stores a star ptr,
  kind3 = 'Star Lane'); the contest test compares it against `lane`.
* relation cell [0x12fd6 + 0x1ee*player + raceIdx] == 3 = ALLIANCE
  (_wip_t180 P2: 0x12fd6 == 0x12e16+0x1c0 matrix form; OQ-023 CLOSED:
  2=WAR/1=PEACE/3=ALLIANCE; the same `cmp ...,3` twin appears at 0x242b5).

SEMANTIC READING [inferred from the verified shape]:
V = 1 + (number of star systems REACHABLE from the home system through lanes
that pass, this turn, the triple test "far star is in the player's
star-selection visibility mask AND the far star carries no presence bit for any
race that is neither the player nor allied to him AND no live ship of a
non-allied race currently holds an order into that lane"). Each lane can
contribute at most one system per pass (the +0x21 mark), and a FAILING LANE
PRUNES ITS SUBTREE — the recursion never enters it.

WHY THIS FITS EVERY BANKED ODDITY (S6/S10/S13) THAT KILLED the owned-systems
and fleet-census hypotheses:
* subtree pruning => V can jump by whole branches (t912 11->22 with NO systems
  change; t1096->t1255 23->14 during combat) — one lane flipping contested/un-
  contested re-opens or severs a region.
* V is NOT a snapshot function of territory or fleet (S10 #3: same turn read 14
  in one lineage and 23 in another): the flood depends on relation cells +
  order pointers, which do differ by lineage, and the mark-clear/reset happens
  only in the end-turn pass.
* V moves ONLY at turn boundaries (S10 #1) and the value is 0 at load (S10 #2):
  the reset+seed+clear all live in FUN_00024f24, which load never runs.
* the fire EIPs t283 saw at three sites in one body (1e3803 x7, 1e3844, 1e37c2)
  = the recursion re-entering the same loop at different depths.
* t283's walk deltas (from its hex 00,01,03,06,0B,0C,0F,10,12,16,17) =
  +1,+2,+3,+5,+1,+3,+1,+2,+4,+1 — several lanes qualifying inside
  one RUN slice (the monitor reports net old->new across a burst).
