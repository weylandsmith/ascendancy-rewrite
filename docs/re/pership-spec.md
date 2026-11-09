# pership-spec.md — PER-SHIP SIM BUILD CONTRACT (t359, 2026-11-09)

Commissioned by user ruling D2=(b) (docs/DECISIONS.md USER RULING 2026-11-09
block): per-ship becomes THE engine once the pinned-seed suite passes; no
permanent toggle; aggregate demotes to test oracle. This dossier is the build
contract for queue rows t360-t365. ZERO new measurement was taken to write it:
every line either carries a docs/re pointer (the durable law files, all
cited-measurement themselves) or is marked INFERRED. Where two banked readings
conflict, both citations are kept and the row is marked DISPUTED.

EPISTEMIC KEY (project-wide): [verified]=instruction/census-cited in the
pointer file; [MEASURED]=live-RAM/save census cited; INFERRED=reasoned from
cited facts, not itself witnessed. Strict-close governs the LEDGER; this file
is a model spec, so it may carry INFERRED lines — the t360+ tests must not
close OQ rows on them.

## 0. ARRAY LAW (where ships live)

A1 The ship array: stride 0x162 bytes, runtime base = B + 0x82bb0 + 0x3a095
   (data-segment offset 0x3a095 under the pointer law OQ-011, STATE.md POINTER
   LAW), live count = u32 ds:0x43489 >> 16, cap 0x6b (107 slots).
   [verified: scripts/r256c_shipstate.py header (base/count/cap), combat.md §1
   (stride 0x162 window), dosbox-wp-t283.md L73-75 (imul 0x162 + live-count
   gate cmp dx,ds:0x4348b).]
A2 A ship is identified by its RECORD ADDRESS (record pointer), not a slot id;
   the ship-list helper fn 0x22304 converts (array law fn) — callers cite
   combat.md §2 (0x4d07f) and combat.md L629 (resolver array build loop).
   [verified]
A3 Free/dead records: owner reads 65535 (0xffff) and the record is re-occupied
   by a different ship between samples (freed-record-reuse flip).
   [MEASURED: combat.md §1 death law (t85c presence law + t1253 frames).]
A4 62,762-row trusted census (25 sessions, turns 240..1335) is the corpus
   invariant base for parser tests; live kind set observed exactly {1..5},
   kind 0 only on dead slots. [MEASURED: scripts/r256c_shipstate.py via
   ai-dossier.md §gap-row-16 / STATE t256c.]

## 1. SHIP-RECORD FIELD TABLE (offsets into the 0x162 record)

All offsets below are record-relative. Recalc fn FUN_00049acc
(0x49acc..0x49c10 verbatim) owns the stat block; cited ships.md §18 (t184).

 off  w   name                     law
 +0x00 u32 weapon-level total      recalc += gizmo row[+0x52]; ships.md §18
 +0x04 u32 shield-level total      recalc += row[+0x56]; ships.md §18
 +0x08 u32 lane-step X source      recalc: cidx 0x2b/0x2c/0x2a count *
                                   ds:0x2583 fistp; MEASURED live pairs
                                   (+8,+c) = (14,0) or (0,28) = step0;
                                   step0 = float([+8]+[+c]) in the march body
                                   FUN_0004a74c; ships.md S22 L2 (t189)
 +0x0c u32 lane-step Z source      same, ds:0x258b; ships.md S22 L2, §18
 +0x10 u32 drive-stat total        hull base [+0x14] + SUM row[+0x5e] over
                                   cat-2 gizmos @0x49b67; ships.md §10/§18;
                                   MOVES refills from THIS (S17 T4)
 +0x14 u32 hull base drive         :=0 at build; ships.md §18
 +0x18 u32 POWER max               recharge cap trunc([+0x18]*(1+clamp((T-
                                   [+0x52])//100,0,10)/10)); combat.md §1
                                   (t101 leg3, 25/35 exact 35/35 bounded)
 +0x1c u32 cat-2 power carry       recalc: byte[row+0x32]==2 ->
                                   dword[row+0x36] -> +0x1c; ships.md §18
 +0x20 u32 scanner-level total     recalc += row[+0x62]; ships.md §18
 +0x24 u32 special-item count      cidx 0x2b/0x2c/0x2a count; ships.md §18
 +0x28 u32 target-slot marker      := -1 when cidx 0x47 present (recalc);
                                   -1 read as "target slot empty" by the
                                   auto-order law FUN_00040178; ships.md §18,
                                   §11 AUTO-ORDER LAW
 +0x2c u32 zeroed by recalc        ships.md §18 (status zero list)
 +0x30 u32 zeroed by recalc        ships.md §18
 +0x31 u8  player-design flag      gates hull-name copy (byte3 test + owner
                                   hi16 == DAT_0007458e); ships.md §18
 +0x34 --  hull name string        stride-2 copy from DAT_00078484+hull*0x14;
                                   ships.md §18
 +0x52 u32 route handle / ETA      reads as route handle in the march/gate
                                   law (S21 item 3 discriminator; S22
                                   supersedes the "+0x52 route handle" for the
                                   MARCH target, see +0x59) and as ETA
                                   day-stamp in the recharge law (combat.md
                                   §1). DISPUTED dual-use — keep ONE field,
                                   both consumers. aicode t101 per S22 IDENTITY
                                   TIE paragraph.
 +0x54 u32 owner handle            race index = value >> 16; r256c header;
                                   t273 law: the LOW u16 pair is NOT the race
                                   index (selfplay.md t273 harness bug (1))
 +0x56 u8  owner race index        == watcher ships[].owner; used by EVENT 4
                                   as the transport byte (income-law.md
                                   §13.5); t273 (selfplay.md)
 +0x58 u8  ORDER KIND (0..5)       ai-dossier.md §5 field map (t94+t107)
 +0x59 u32 ORDER TARGET ptr        kind-5: lane-record ptr (march reads
                                   ptr[H], ptr[H+4] endpoints; ships.md S22
                                   L1); kind-2: star/star-target; combat
                                   same-system gate compares ship+0x59 ==
                                   target+0x59 (ai-dossier §6); values are
                                   guest-PHYSICAL pointers — rebase per save
                                   (t298 POINTER-VALUE LAW, STATE.md; t333
                                   delta-not-constant law)
 +0x5d u8  ACT enum                0=none(re-decide), 1=congregate, 2=engage;
                                   ai-dossier §5 (t179 P1: cmp BYTE [+0x5d],0
                                   at 0x41970; clear at 0x41a30), ships.md §11
                                   AUTO-ORDER (+0x5d:=2 ENGAGE)
 +0x5e u32 ACT TARGET OBJECT       ai-dossier §5; NOT a drive value (t47
                                   correction in ships.md §11 SCALE STATUS)
 +0x62 u8  resolver fire flag      :=1 in emergency-recall branch 0x4159a and
                                   engagement leg A (+0x62:=0 reset);
                                   ships.md §19 T2, ai-dossier §6 Leg A
 +0x63 u32 gizmo slot ptr          := slot ptr in the same branches; ships.md
                                   §19 T2 (NB distinct from the planet-record
                                   parent-slot [w+0x63] law — different struct,
                                   t339 STATE.md standing laws)
 +0x67 u8  order TYPE / stance     0x4a55c maps stance arg -> +0x67 (0->2,
                                   1->1, 2->0); dispatcher FUN_0004a360 routes
                                   [+0x67]==2 (star-target) to FUN_0004ca50;
                                   issuer sets +0x67:=5 for delayed moves;
                                   combat.md S2g, ships.md §19 T3, §11
                                   QUEUE-TURN LAW
 +0x68 u32 order PAYLOAD           type-1 move: ptr to 3-dword coord/planet
                                   triple (derefs [p],[+4],[+8] @0x49fb9/
                                   0x49fd7); type-2 reads payload+0x14;
                                   dispatch switch @0x4a322/0x4a333 ->
                                   FUN_00049880 (type1) / FUN_00049a34
                                   (type2); ships.md §10
 +0x6c f32[3] kind-3 absolute triple  ships.md S17 T1 (order kinds read at
                                   +0x67: 3=abs triple +0x6c)
 +0x88 u32 POWER (fuel)            multi-turn budget; ONLY refuel orders
                                   restore it; upkeep burn [ship+0x88] -=
                                   design[+0x36] @0x4a710 (FUN_0004a658),
                                   travel burn @0x4a307; min-fuel tie-break in
                                   the round-robin; combat.md §1 (t101),
                                   ships.md §12/S17 T4
 +0x8c u32 INTEGRITY (hull)        build := (hull+1)*10, doubled when race-war
                                   byte DAT_00012fb3+empire*0x1ee==1 (ships.md
                                   §18); death at hull < 1 -> CALL 0x49d2c
                                   (combat.md §2b 0x4b896, S2g); the ONLY
                                   subtract in the image is 0x4d1ea
                                   `sub DWORD [esi+0x8c],eax` (combat.md §2)
 +0x90 u32 shield charges          combat LAYER-1 store 0x4b88a, clamped;
                                   +0x9c bit4 nulls this layer (flag -> edi=0
                                   @0x4b7bc); ALSO zeroed ALWAYS as "speed
                                   accumulator" by FUN_0004a658 at upkeep
                                   (ships.md §12) — DISPUTED dual-use, keep
                                   ONE field, two consumers; t273 harvest
                                   "18 shield-only hits" corroborates a real
                                   per-ship shield (selfplay.md t273 LEG A)
 +0x94 u32 MOVES                   per-call budget; re-granted each turn from
                                   drive stat [ship+0x10] (combat.md §1 t101;
                                   S17 T4 refill at 0x412d4 -> FUN_0004a658);
                                   consumed by travel fsub/fistp @0x4a30f..
                                   0x4a314; ships.md §12's "design-list
                                   pointer" label on +0x94 writes the SAME
                                   value [ship+0x10] — reading difference, not
                                   field difference [inferred]
 +0x98 u32 MAX integrity           clamp for repair (Remote Repair Facility
                                   0x4cffb clamps at [+0x98]); build sets
                                   [+0:98]:=[+0x8c]; combat.md gizmo table,
                                   ships.md §18
 +0x9c u16 status flags            bit0 -> kills design-list use (+0x94:=0,
                                   ships.md §12); bit 0x10 gates shield null
                                   (combat.md §2b); OR |=2 (Toroidal Blaster),
                                   OR |=4 (Accutron) (combat.md gizmo table)
 +0x9e f32 position X              position setter FUN_00049aa8 writes the
                                   triple; walk commits [ship+0x9e]; grid
                                   quantizer FUN_000533e0 snaps to
                                   DAT_000895dc=32 (MEASURED 20/20);
                                   combat.md §2 (0x4d08c lea confirms),
                                   ships.md S17 T1/T3
 +0xa2 f32 position Y              same triple; ships.md S17
 +0xa6 f32 position Z              same triple; ships.md S17
 +0xaa u8  hull kind               redesign no-op test new-kind == [rec+0xaa];
                                   hull = byte3 dword[rec+0xa7] feeds cap;
                                   ships.md §18
 +0xab ring gizmo inventory        25 physical slots stride 7 {cidx u8 (0xFF
                                   empty), u16 @slot+1 (use counter), u32
                                   @slot+3}; 0xab+25*7 = 0x15a; ships.md §18
                                   (t184, supersedes the t46 "queued-order
                                   list" label — the ring IS the inventory,
                                   order fields are +0x5d/0x67/0x68)
 +0x15a u32 inventory CAP          scenario-loaded table dword_live(0x6842 +
                                   2*hull)>>16; MEASURED cap==table 1234/1234,
                                   caps {10:956,15:20,25:258}; ships.md §18
 +0x15e u32 FILLED count           counts cidx!=0xFF over slots 0..cap
                                   INCLUSIVE (phantom-slot off-by-one,
                                   MEASURED 100/1234 rows; gizmo at idx==cap
                                   is inert for stats/upkeep yet counted);
                                   ships.md §18 PHANTOM-SLOT
 stride 0x162 record size          A1 above
UNKNOWN fields (do not model, do not invent): +0x0e? gap between +0x0c and
 +0x10; +0x1e..+0x1f; +0x32..+0x33; +0x55; +0x57 (planet-record field, NOT
 ship); +0x64..+0x66; +0x69..+0x6b; +0x70..+0x87; +0xa8..+0xa9; +0xb0..+0x159
 (ring tail); +0x160..+0x161. Marked from the gap list between cited fields —
 INFERRED absence of law, not measured absence of meaning.

## 2. ORDER-STATE ENUM + TRANSITION TABLE

Kind enum (+0x58), end-to-end verified values {0..5} with the verbatim
store-site census (ai-dossier.md §5):
  kind 0 = NO ORDER / command-clear. imm0 store 0x24a00 (also WORD +0x56 :=
    0xffff on clear per §5); live kind 0 only on dead slots (A4).
  kind 1 = MOVE (coord payload). imm1 store 0x3fb3e; issuer issuer-leg;
    completion FUN_00049880 (ships.md §10).
  kind 2 = STAR-TARGET (colonize/land path). imm2 store 0x3ca60 (the
    player-command issuer; AI holds kind 2 ZERO times — ai-dossier row 16);
    completion FUN_00049a34 (ships.md §10 dispatch switch).
  kind 3 = ENGAGE/act state. imm3 stores 0x39859 / 0x49cd6; targetability
    gate FUN_00039894 at 0x419da path (ai-dossier §5, §t179 P2: 8 callers).
  kind 4 = IN-SYSTEM (arrived/positioned). imm4 stores 0x2202f / 0x22127 /
    0x49db9 (0x2202f = placement handler tail, ships.md §19 T3).
  kind 5 = PLACEMENT (transit-to-star). imm5 stores 0x22243 / 0x2228f (inside
    travel issuer FUN_000220a8, aicode.md L526); consumed by FUN_00021f58.

Transitions (trigger -> effect, all cited):
 T-1 no-order -> kind 2 (AI auto-order): FUN_00040178 decider, no active
     order at turn start, +0x28==-1 target empty -> FUN_0004105c target pick,
     score threshold 0x1e (15 when war/enemy-home-visible) -> +0x5d:=2 ENGAGE
     + target; ships.md §11 AUTO-ORDER LAW. ACT is set; the ORDER kind follows
     when the executor issues it (INFERRED sequencing; both sites cited).
 T-2 ACT -> issued order: command executor FUN_00041260 (exactly two callers
     0x16eb0, 0x2554f — ai-dossier §t179 P2). Lane-gradient law: target =
     graph neighbour with MAT[A+100*N] == MAT[A+100*B]-1, payload +0x68 :=
     lane-entry ptr; "one hop per issue, re-issued until arrival" INFERRED
     from the cancel-at-destination branch 0x41a0b..0x41a4a; ships.md §11
     ISSUER RESOLUTION LAW. Failure hits vendor assert 0x2a428.
 T-3 kind 5 -> kind 4 (arrival placement): FUN_00021f58 REQUIRES
     byte[+0x58]==5; position := star coords + (0,-200,0) + rng%200 on the
     other two axes (LIVE -200.0 at B+0x82bb0+0xaee; two FUN_0007824f draws,
     idiv 200); commit via FUN_00049aa8; then byte[+0x58]:=4 (0x2202f).
     ships.md §19 T3 PLACEMENT LAW.
 T-4 kind 4 -> kind 5 (lane entry): travel issuer FUN_000220a8 validates
     order kind in {1,2}, lane-connect via 0x39894, sets kind 5 + target
     (0x22243/0x2228f); observed symmetry kind4<->kind5 416/416 in self-play
     (ai-dossier row 16); magnetron path also uses this pair (ships.md §19 T3
     case 0x3c).
 T-5 {3,1,2} -> 4 (retreat-to-system downgrade): 0x220f2 when the target
     stops being targetable (FUN_00039894 test); fired 143x both owners
     [MEASURED]; ai-dossier §5 "retreat to system" law.
 T-6 kind 1 completion -> LAND or DWELL: FUN_00049880 -> landing attempt
     FUN_00039810 (gate: planet owner != ship race requires FUN_00039a00
     combat/capture check; orbital ring slot byte1==0xFF found -> ship
     +0x58:=3, +0x59:=planet rec, slot byte1:=0x17 word2:=1 ACTIVE; return
     -1 LANDED). NO free slot: +0x58:=4 + THREE rng draws (%1000-500) scatter
     via FUN_00052ff4/FUN_00049aa8 — ship "vanishes at sea" [state semantics
     INFERRED]; ships.md §10 MOVE COMPLETION.
 T-7 lane march (kind 5, per turn): FUN_0004a74c guard byte[+0x58]==5;
     H := dword[+0x59] (lane-record ptr); step0 = float([+8]+[+c]); gate 1
     byte[H+0x23] bit0 -> step *= 0.333333 (pool word MEASURED live); gate 2
     species row col 0x12==0x12 -> step=max(step,1)*2.0 (pool word MEASURED;
     NEVER seen firing — zero witnesses, ships.md S22 L5); x := min(x+step,
     lane_len) at [ship+0x9e] ALIAS (float position write), y/z untouched;
     lane-end saturates then flip/turn-around (S21 item 5). SHIP-RECORD
     x-field vs alias: S22 L1 records the clamp store at [ship+0x9e] — the
     march writes the position triple, lane-local frame (S21 item 4: st5
     coords are lane-local, big movers = frame switches, not flights).
 T-8 in-system dwell (kind 4): resolves within ONE turn boundary at ring
     granularity — net displacement 0.00 and constant order byte end-to-end
     over 150-turn st4 runs; every big mover is a 4<->5 frame switch, never
     st4->st4 (healthy regimes); ships.md S24 item 1 [MEASURED]. Model law:
     kind-4 ships do not march between turn rows; displacement happens inside
     the boundary.
 T-9 walk law (kind 1/2/3 in the executor): FUN_00049f54 (guard +0x58==4):
     d = sqrt(|target3-[+0x9e]|) * 0.00625 (1/160 = world->sugar);
     walk = min(d, MOVES[+0x94]); steps = max(1, round(walk)); if POWER[+0x88]
     < steps: walk *= POWER/steps, steps := POWER; arrived := (walk==d) flag8;
     per-step displacement normalize(delta)*(walk/steps)*32.0*5.0; COMMIT
     (param_2==1 only): pos := new, [+0x88] -= steps, [+0x94] := round(rem);
     hooks kind1->FUN_00049880, kind2->FUN_00049a34; ONE SUGAR CUBE == 160
     WORLD UNITS (constants 0x25ff/0x2603/0x2607 MEASURED live); ships.md S17
     T1/T2. Lane transit is the SAME law under the gradient, EXCEPT the st5
     march body (T-7) which spends NEITHER MOVES nor POWER [MEASURED-negative,
     ships.md S21 item 1].
 T-10 order queue suppressor: queued orders (delayed-move, N-turn wait)
     live in the record; the ONLY writer of a queued slot turn-word is
     @0x3ac1c (event handler); a matching queued type with turn word != 0
     SUPPRESSES the move and decrements it (float poison write at +0x88 =
     animation timer INFERRED); ships.md §10 item 1 + §11 QUEUE-TURN LAW.
     NOTE: the t46 field labels on this law (type byte +0xab / turn word
     +0xac) collide with the inventory ring (t184 supersession) — model the
     SUPPRESSION BEHAVIOUR; field home DISPUTED, resolve at t360 against the
     0x3ac1c write site before encoding it.
 T-11 death: INTEGRITY < 1 -> 0x49d2c (death handler, esi=ship, edx=owner,
     ebx=[+0xa7]>>24) (combat.md §2b); record owner -> 0xffff free (A3).

Turn frame (sequence the skeleton must reproduce; ai-dossier §1 turn frame +
ships.md S22 IDENTITY TIE): per-race turn tail FUN_0003e6e0 -> FUN_0004a74c
per ship (zero [+0x9c]; POWER refill [+0x88]; slot refresh loop); upkeep
FUN_0004a658 per ship per turn (maintenance burn + propulsion bonus, nested:
bonus only when upkeep affordable — ships.md §12); command executor
FUN_00041260 round-robin: repeat sweeps while any ship reports work; each
sweep refills MOVES from drive sum, collects fuel>0 && kind!=1 && ownership,
picks MIN POWER [+0x88] (strict <, first-in-list ties) with act set, commits
its move; ship list pre-sorted DESCENDING design power (FUN_00040ec0 +
comparator 0x40eb4) — strongest ships get first call (ai-dossier §5).
Assert law: after movement kind must be 3 or 4 else assert 0x93e at 0x2a428
(ai-dossier t179 P1).

Determinism law: single-image LCG FUN_0007824f is the ONLY rng in the ship
region (combat.md S2g "hit probability does not exist — measured negative");
draw shapes: scatter %1000-500 x3 (T-6), placement %200 x2 (T-3), design
shuffle %remaining (ships.md §18 DESIGN-APPLY). Commit law: mode==1 only
(0x25560/0x25570 inside player-command-exec 0x2547c; every AI volley path is
a mode-0 dry run — ai-dossier §6, OQ-010 row).

## 3. GIZMO INVENTORY LAW (build contract for t363)

G1 Design (gizmo) table: stride 0x6a, 76 records, base PTR_DAT_0007650c
   (loaded row order == gizmos.txt file order, MEASURED 1368 members, 0
   mismatches — ships.md §19 T1). Columns: +0x32 cat byte, eight fixed
   %d cols (+0x36/+0x3a/+0x3e/+0x42/+0x46/+0x4a/+0x4e/+0x35), +0x33 u16
   RESREQ bitmask from the 255-terminated list; derived slots by category:
   cat0 weapon +0x52=Level, cat1 shield +0x56=Level, cat2 drive +0x5e=Level,
   cat3 scanner +0x62=Level, cat4 generator +0x66=POWER(+0x36), cat>4 vendor
   error; ships.md §6 (t15, verified static).
G2 The ship carries ONLY cidx bytes in its ring (no gizmo record copied in);
   stats re-materialized on every mutation by FUN_00049acc; ships.md §18.
G3 Mutators (all call recalc): FUN_00049698 set-slot(EBX=idx, EDX=cidx) —
   rejects idx>cap (idx==cap ADMITTED -> phantom slot), rejects only
   same-cidx-in-target-slot (duplicates ACROSS slots LEGAL, live rows carry
   1d 1d / 47 47 / 49 49); FUN_000496e4 clear-slot (NO index bound);
   FUN_00049624 fill-first-empty (scans all 25); FUN_0004929c init-clear;
   ships.md §18.
G4 Build: FUN_00049534 — cap := dword_live(0x6842+2*hull)>>16 (hull =
   byte3[rec+0xa7]); INTEGRITY := (hull+1)*10 doubled-if-race-war-byte;
   [+0x98]:=[+0x8c]; hull base [+0x14]:=0; MEASURED 1234/1234 cap==table;
   ships.md §18.
G5 Design-apply (starter fill): FUN_00040d1c filters a 22-entry list at
   DAT_0x67ec by race knowledge (bit test in live 0x7478b + class*0x4b) and
   fills slots to cap in RNG-SHUFFLED order (% remaining, 0x40d7b..0x40daf);
   class handlers hardcode starter-kit cidx adds; ships.md §18.
G6 Redesign: FUN_000497a8 (sole caller 0x4e6d2): no-op if new kind ==
   [rec+0xaa]; REFUSE iff new_cap < FILLED [+0x15e]; else sweep remove+re-add
   compacting into low slots, re-init, copy hull name unconditionally;
   ships.md §18.
G7 Per-slot use counter: slot u16 @+1; dispatcher 0x4a360 prologue guard:
   design[+0x42]==0 -> no decrement; slot word==0 -> block; else dec word
   when mode==1. Replenisher (cidx 0x41) restores word := design[+0x42];
   what the column numerically MEANS is NOT banked ("do not read NumUses as
   proven until its consumer law is cited" — ships.md §19 T3); model the
   counter, keep the semantics open.
G8 COST side: per-hull cost table live 0x687c (4 dwords) via FUN_0004a41c ->
   FUN_0004a3d4; production loop multiplies by CAP at 0x40454
   (imul edx,[esi+0x15a]); per-gizmo Industry NEVER modified post-parse
   (writers = parse store 0x491b5 + error zero-wipe 0x37f41 only — ships.md
   §9 CLOSED-BY-CENSUS; no design-cost total is ever materialised).
G9 Upkeep/propulsion (per turn, FUN_0004a658 verbatim): status +0x9c bit0 ->
   +0x94 := 0 else +0x94 := [ship+0x10] (or PTR_DAT_00077f6c + [ship+0x10]
   when bit2 clear); speed accumulator +0x90 := 0 ALWAYS; then per ring slot:
   type != 0xFF AND w16[gizmo row+3] & 0x20 AND dword[row+3]==-1 -> if
   dword[row+6] <= [+0x88]: [+0x88] -= row[+6] (maintenance burn); IF ALSO
   byte[row+2]==1: +0x90 += dword[row+0x26] (propulsion bonus, NESTED under
   affordability); ships.md §12.
   NB the t46-era "queued order slot" wording = the inventory ring per t184
   supersession; keep behaviour, ring semantics.

## 4. CARRIER / CARGO LAW (build contract for t363)

C1 Invasion Module = gizmo cidx 0x49 (gizmos.txt row 73 of 76: Cat 5, Power
   10, Range 0, Level 0, NumUses-col 0, ResReq 0; parsed with the loader
   column order). Carriers exist in RAM: 480 distinct ships carry it
   [MEASURED]; ai-dossier §6 Leg A + row 16.
C2 Invasion eligibility: engagement resolver loop 0x42d09..0x42d5b accepts the
   FIRST ship (list order) with BYTE[+0x58]==4 (in-system) AND one stride-7
   gizmo slot == 0x49; result descriptor byte 3 + ship ptr; target engagement
   flags written (+0x62:=0, +0x63:=0, +0x67:=1, +0x68:=esi); no strength
   comparison — eligibility is order-state + equipment; ai-dossier §6 Leg A
   [verified objdump 0x42c60..0x42e6e].
C3 Landing = planet slot occupancy, NOT a parallel ship table: a landed ship
   IS an active item-23 entry of the destination planet's slot array
   (ring slot byte1 := 0x17, word2 := 1); ships.md §10 (first MEASURED answer
   to per-ship inventory sub-question). Orbital ring scan u16 +0x18..+0x1a on
   the PLANET record (ships.md §10 item 2).
C4 Cargo/colonisation chain (income-law.md §13.5, t44): command-object field
   triple +0xab pending item byte ('05' Colony Base, '17' automation, 0xff
   none) / +0xac CHOSEN slot / +0xae CARGO slot / +0xb0 follow-up / +0xb2..
   candidate queue (stride 5). These fields are on the COMMAND OBJECT
   (FUN_0003aa0a family), not the ship record. EVENT 8: +0xac :=
   FUN_0003a880(coords) — PURE coordinate->slot converter (orbital-direct
   13<X<153, 119<Y<469: slot = surfaceCells + 5*((X-13)/70) + (Y-119)/70;
   else decode FUN_0003a820 + FUN_000395c4; no RNG). EVENT 4 (colonisation
   0x3af4c..0x3af6d): +0xae := +0xac; nothing unless +0xae < 0xffff; legality
   re-runs FUN_0003830c; item '05': owner := transport byte [ship+0x56],
   pop := 2, +0x67 := turn, explicit-slot activator FUN_00038840 @0x3b0d6.
C5 OPEN, do NOT invent the picker: WHO chooses the AI's landing coords
   (EVENT 8 dispatch site) is unrecovered — handler reached only via a
   data-resident table (docs/BLOCKED.md OQ-CARGO, income-law.md §13.5 "NOT
   recovered"). The rewrite's standing default (uniform non-rock picker draw,
   campaign.cpp seedColonyBaseColony) stays; the per-ship model gets the
   FIELDS, not a new chooser.

## 5. PER-SHIP COMBAT ROUND LAW (build contract for t364)

K1 Same-system gate: ship+0x58==4 && target+0x58==4 && ship+0x59 ==
   target+0x59 — combat is strictly per-system-object; ai-dossier §6 [S2g/
   S2h cited].
K2 Firing order: fn 0x4a55c — refuses if POWER==0; stance map arg->+0x67
   (0->2,1->1,2->0); [+0x68] := target; volley loop 0x4a5c1..0x4a5fc walks the
   gizmo ring IN STORED ORDER stride 7 and fires EVERY cat-0 weapon (slot
   eligibility via companion scan 0x4a604: first cat-0 slot with power/uses);
   ai-dossier §6, combat.md S2g.
K3 Range gate: design[+0x3a]<<5 vs distance (0x4d15f/0x4d162 shl 5 against
   squared distance at the 0x4d075 loop; combat.md §2; and the star-target
   path Range*32 < lane-d at 0x4ca50, ships.md §19 T3 GATE 1). Units: world
   units vs the 32/160 system [inferred consistent].
K4 Damage: design[+0x52] (file Level column; gizmo 0x2f overrides to
   design[+0x4a]); NO hit roll — measured negative (no rng in the gun/hit
   path); ai-dossier §6, combat.md §2/§2b.
K5 Two-layer absorb (hit path 0x4b740): LAYER-1 shield [+0x90] clamped
   (0x4b7c4 clamp, 0x4b88a store), LAYER-2 hull [+0x8c] clamped (0x4b7e0,
   0x4b890); [+0x9c] bit 0x10 nulls the shield layer (edi:=0 @0x4b7bc);
   hull < 1 -> 0x49d2c death (0x4b896); which absorb maps to which clamp term
   unresolved INSIDE the fn, but the two-layer clamped structure is verified;
   combat.md §2b. Aggregate rewrite law (capture iff volley - MIN(volley,
   shieldChargesFor) > hull) stays the ORACLE; per-ship redistributes losses,
   does not change the victory comparator (STATE t364 row; OQ-021 law
   score.md S18-S20 untouched).
K6 Commit law: resource-consuming commit mode==1 ONLY at 0x25560/0x25570
   (player-command-exec 0x2547c); AI paths are mode-0 dry runs; ai-dossier §6
   (t88a).
K7 Combat objects: damage reads attacker COMBAT-OBJECT fields ([edi+0x4a],
   [edi+0x3a]) — ship records read 0 at turn boundary; combat objects are
   BUILT at battle entry; the per-ship sim must build per-engagement attacker
   snapshots, not read record fields; combat.md §2 CAVEATS.
K8 Target star record via [[target+0xa]>>16 *39*32 + 0x13bc5] (star-block
   stride law cross-confirmed) then 0x43a4c (star-defense contribution,
   UNDECODED); combat.md §2b tail.
K9 Gizmo combat tree (dispatcher 0x4cd90 kind-5 branch + 0x4ca50 star-target
   branch): per-cidx cases banked verbatim in combat.md gizmo table (Recaller
   0x24, Smart Bomb 0x26 AT-WAR-gated area damage via diplomacy matrix byte
   [0x12fd6+att+def]==2, Gravity Distorter 0x27, Catapult 0x2e xyz negate,
   Cannibalizer 0x35, Condensor 0x38, Accutron 0x39, Repair 0x3a clamped at
   +0x98, Blaster 0x3f, Replenisher 0x41) + ships.md §19 T3 (Magnetron 0x3c,
   target[+0x23]|=2 for 0x20, owner-bit OR for 0x3e). Model what t364 needs;
   full tree is reference, not required scope.
K10 Engagement resolver caller-side array is OWNER-RACE FILTERED (only the
   acting side's ships); return fire is a SEPARATE resolution run (discrete
   small steps, player 40>38>36>34 observed); combat.md L629-637.

## 6. SAVE / LOAD (build contract for t360 read-side, t366 write-side)

S1 The ship array lives in the data segment at guest-phys
   B + 0x82bb0 + 0x3a095 (A1). Under the pointer law (OQ-011 CLOSED,
   STATE.md): SAVE-ZIP member index for runtime data at X = B + 0x82bb0 + X;
   member byte -> physical = member - 0x88 (H=136 for dfsg 2025.02.01,
   re-derive B via scripts/r1_sav_scan.py, NEVER hard-code).
S2 Pointer-valued fields inside records (+0x59 order target, +0x63 slot ptr,
   +0x68 payload) are guest-PHYSICAL values: read targets at member index
   value+0x88 (t298 POINTER-VALUE LAW, STATE.md). The save-member-to-linear
   delta is NOT constant across save dirs — re-derive per save and validate
   with a needle before any ds: read (t333 law, STATE t333 item 8).
S3 Count gate: live count = u32 ds:0x43489 >> 16 (A1) — parse exactly that
   many slots, cap 0x6b; dead slots read owner 0xffff (A3) and are skipped.
S4 Ring-sourced test corpus (READ ONLY, streaming — OOM law: tail-seek <=400
   KB or r1_stream, never iterate the whole 8.8 GB timeline):
   work/r1/bank-t1086* banked production frames and the production ring
   work/r1/playcap/*.sav (10 s cadence, turn floor 1086); r256c_shipstate.py
   is the proven reader to mirror (its 62,762-row census is the invariant
   base: owner attribution law +0x56 == race index, kind set {1..5} on live
   rows, cap/filled law §18: filled==count cidx!=0xFF over 0..cap INCLUSIVE
   incl. the 100 phantom rows).
S5 Window law for per-slot diffs: consecutive autosaves WITHIN one turn give
   per-slot u16 diffs (combat.md §1 method); adjacent-row pairing must guard
   stale echoes: require prev_turn in {turn, turn-1} AND mtime gap <= 120 s
   (selfplay.md t273 harness bug (2)); bucket by mtime_ns/datetime, never
   lexicographic wall strings (ships.md S24 harness lesson).
S6 What is NOT in the save: window records are not persisted at all (zero
   window-record strings/magic in saves 41..49 — REFUTED-ROUTES t339(3));
   the ship array IS persisted (every save read above). The .gam packed-
   entropy band is session-memory copy, not a format field (OQ-003 CLOSED
   t181 disclaim, docs/re/savegame.md §t181) — ship records do NOT live in
   the band.
S7 Write-side (t366): emit records back at member index B+0x82bb0+0x3a095 +
   slot*0x162 with guest-physical pointer values rebased to the TARGET run;
   byte-compare against a vendor-written save only if one can be produced
   headlessly, else round-trip-through-rewrite tests + honest note (queue
   row t366 wording verbatim).

## 7. EXPLICIT NON-GOALS (do not model, do not close, do not re-hunt)

N1 Nuke law (Phase Bomb gizmo 70): capture-gated, default NOT modelled
   (docs/BLOCKED.md "Nuke law" block); per-ship fields exist but the use law
   is user-gated (t329 packet; D2 residues).
N2 AI landing-site coord chooser: BLOCKED-static (docs/BLOCKED.md OQ-CARGO);
   standing rewrite default stays (C5).
N3 Magnetron runtime witness: zero-census twice instrumented (ships.md S24
   item 4); use-site stays static-cited; do NOT re-hunt (t49/t58/t265 closed
   the corpus-mining class three times, docs/BLOCKED.md scripted-move block).
N4 Lane-step constant 14-base mapping and gate-1/gate-2 attribution: residue
   explicitly banked unresolved (ships.md S21 HONEST RESIDUE, S22 L4/L5);
   model step0 from [+8]+[+c] + the cited gate FORMS only.
N5 SO_ functional-name tie (A5 residual): the SO_ block's 10 entries != 6
   kinds; use functional descriptions, never SO_ labels (ai-dossier §5).
N6 Gizmo column +0x42 semantics ("NumUses") — model the counter, leave the
   meaning open (G7, ships.md §19 T3 explicit warning).
N7 Orbital Docks effect readers + per-cell terrain/nuke wiring: OQ-016
   residues, user-gated (STATE ledger; t342 "residue list EXHAUSTED" note).
N8 Click-selection / order-placement UI choreography repair: cited-broken
   (xsend "window died before release", STATE standing notes; t293 budget
   spent NEGATIVE); the sim is driven headlessly from record state, not UI.
N9 Star-field / mapgen / diplomacy / economy laws: already closed rows — the
   per-ship sim CONSUMES them (lane matrix law ships.md §11 DAT_00045beb
   100*x+y index, relation matrix byte [0x12fd6+att+def] == 2 == AT WAR), it
   does not re-derive them.
N10 Aggregate engine removal: demote to oracle at t365; REMOVAL only after
   seeds agree (user ruling D2 wording, docs/DECISIONS.md USER RULING block).

## 8. GAP SUMMARY FOR THE BUILD (what the dossier does NOT answer)

G-a T-10 queued-order field home (ring vs separate tail region) — resolve at
    t360 by instrumenting the 0x3ac1c write against banked saves before
    encoding suppression. INFERRED behaviour is cited; the field is not.
G-b +0x90 dual-use (shield vs speed accumulator) and +0x52 dual-use (route
    handle vs ETA) — keep single fields with two consumers; if a test
    contradicts, the DISPUTED rows are the first place to look.
G-c The 100-row phantom-slot origin is INFERRED (loaded scenario committed
    via idx==cap add); model the count law as measured, origin not needed.
G-d st5 lane-local frame -> galactic frame conversion at lane end: S21 item 4
    establishes the frames and that flips carry the switch; the coordinate
    transform itself is NOT cited — the sim may keep lane-local progress
    (x, lane_len, endpoint ptrs) and re-place via star coords on arrival
    (cited T-3) without ever inventing a transform. Mark INFERRED in code.
