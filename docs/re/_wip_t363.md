# _wip_t363.md — GIZMO INVENTORY + CARRIER/CARGO INTO SHIPSIM (queue row t363)

Session: fresh, 2026-11-09 ~19:22 EST. Build contract docs/re/pership-spec.md
§3 (G1..G9) + §4 (C1..C5). Named gaps STATE.md:228-231 owns: (i) FUN_0004a658
upkeep burn +0x88 -= design[+0x36] (the t361/t362 refill-without-burn seam),
(ii) turn-tail slot-refresh loop 0x4a77c..0x4a7a4, (iii) FUN_00049a34 colonise
leg. Sitting check NEGATIVE before start: live-timeline.jsonl mtime 17:26:31
(= t362's own baseline; newest 8,917,535,608 B), turn 1086 standing law —
r1_t85g_sitting.py NOT run (only on turn > 1086). Tree clean at launch.

## S1 VERBATIM READS (work/r331_disasm.txt, this session)

### S1a FUN_0004a658 @0x4a658..0x4a74a — the UPKEEP body (t363 seam (i))
Per ship, per CALL (not per boundary — see S1b for call sites):
  0x4a65e  dx = w16 [+0x9c]; dl &= 1
  0x4a66f  bit0 SET  -> DWORD [+0x94] := 0; jmp 0x4a727 (skip ring scan)
  0x4a67d  else bit1 test:
           bit1 SET -> edx = ds:0x77f6c + [+0x10]
           bit1 CLR -> edx = [+0x10]
           0x4a6a0  [+0x94] := edx        (MOVES re-grant)
  0x4a6a6  DWORD [+0x90] := 0             (ALWAYS)
  0x4a6b0  ebx = &ring[0] (ship+0xab); ecx = [+0x15a] (cap); loop i=0..cap-1
           (0x4a6c8 inc esi / add ebx,7 / cmp esi,[+0x15a] jge 0x4a727)
  0x4a6d6  cidx = BYTE[ebx]; cidx == 0xFF -> next slot
  0x4a6e0  edx = cidx*0x6a + 0x7650c      (RAW design record base)
  0x4a6e9  w16 [edx+0x33] & 0x20 == 0 -> next slot        (upkeep gate bit)
  0x4a6f9  DWORD [ebx+0x3] != -1 -> next slot             (slot payload == -1)
  0x4a6ff  ecx = [+0x88]; edi = DWORD [edx+0x36]          (cost = raw +0x36)
  0x4a70a  jl (cost > power) -> next slot                 (PAYABLE gate only)
  0x4a710  [+0x88] := ecx - edi                           (MAINTENANCE BURN)
  0x4a716  BYTE [edx+0x32] != 1 -> next slot              (cat == SHIELD)
  0x4a71c  [+0x90] += DWORD [edx+0x56]                    (shield charges;
           NESTED under affordability — verbatim, matches spec G9)
  0x4a727  bit3 of [+0x9c] set -> [+0x90] := 0
MEASURED corroboration already on disk (ships.md §12 + t101 corrections):
exactly design rows 10..15 (the six shields) carry gate bit AND cat==1;
costs 0,1,2,2,3,4; [+0x90] is SHIELD CHARGES (t86 closed), [+0x56] = shield
Level. So the burn is a SHIELD-MAINTENANCE burn off the POWER budget.
NEW FROM THIS READ (not in spec G9's wording): the payable gate is a plain
`cmp power, cost / jl` — cost > power skips the burn ENTIRELY (no partial
burn, no clamp), and the slot then contributes NOTHING (not even charges).

### S1b CALL SITES of 0x4a658 (grep `e8 .* 0x4a658`): exactly two
  1. 0x3ea40 inside FUN_0003ea08 (0x3ea08..0x3ea51): builds the ship list via
     0x22304, walks it, for every ship with ([ship+0x54]>>16) == race byte
     (arg al) calls 0x4a658. => PER-SHIP loop over the RACE.
  2. 0x4a95b inside FUN_0004a74c (the turn tail), at the very END, after the
     kind-5 march body and the 0x4a942 kind==4 assert (0x4a948 mov ebx,0x48b /
     edx 0x262f / call assert 0x2a428).
  FUN_0003ea08's own caller (t362 S3): 0x412cf = INSIDE the executor
  FUN_00041260 prologue, i.e. BEFORE the eligibility scan and the pick.
  => CONSEQUENCE (the seam t363 must encode): per sweep, per race, the upkeep
  burn lands on [+0x88] BEFORE the MIN-POWER pick of that sweep. The burn
  therefore changes both the pick ORDER and the drain rate; a ship with an
  unaffordable shield keeps full POWER (gate skips), and a ship whose burn
  brings POWER to 0 fails the 0x4134e POWER>0 gate for the rest of the
  boundary. t361/t362 modelled the re-grant with NO burn — that asymmetry is
  the named gap.

### S1c Turn tail FUN_0004a74c prologue 0x4a74c..0x4a7a6 (t363 seam (ii))
  0x4a756  WORD [+0x9c] := 0
  0x4a75f  call 0x4a99c (the clamp formula: (ds:0x12e10 - [+0x52]) idiv 100,
           clamp [0,10]; 0x4a96c..0x4a99b verbatim — same law combat.md §1
           t101 leg3, re-confirmed this session as a standalone fn)
  0x4a76c  DWORD [+0x88] := eax            (refill, UNGUARDED)
  0x4a772  eax = &ring[0]; ebx = [+0x15a]; loop i=0..cap-1:
  0x4a78c    ch = BYTE[eax]; ch == 0xFF -> next
  0x4a793    ebx = ch*0x6a
  0x4a799    bx = WORD PTR [ebx + 0x7654e]      <=== OPERAND
  0x4a7a0    WORD [eax+0x1] := bx               (use-count refresh)
  0x4a7a6  cmp BYTE [+0x58],5 -> else exit (march body follows for kind 5)
*** CORRECTION (measurement): 0x7654e - 0x7650c (raw design base, t101 law) ==
0x42. The refresh operand is RAW design[+0x42], NOT design[+0x4e] as
STATE.md:230 and _wip_t362.md:56 word it. +0x42 is the SAME column the G7
replenisher restores (spec G7: "word := design[+0x42]") and the same column
whose ==0 means "no decrement" in the dispatcher guard (spec G7). So:
the turn tail refreshes every non-empty slot's u16 use-count to design[+0x42].
Queue wording is an off-by-convention artifact; the disasm constant is the
record. Build the +0x42 law; do NOT invent a +0x4e operand.
NB the refresh loop runs for EVERY ship (no kind gate before 0x4a7a6).

## S2 SCOPE DECISION (recorded before coding)
t363 builds, into shipsim: (a) the design row table (only the columns the
cited laws read: cat +0x32, upkeep-gate w16 +0x33 bit 0x20, cost +0x36,
uses +0x42, shield level +0x56, carrier flag), (b) the inventory ring on Ship
(25 slots stride 7 = cidx u8 / use u16 / payload u32 — parser already reads
the cidx bytes, shipsave.h), (c) FUN_0004a658 verbatim as an UPKEEP step
wired at its two call sites (per-sweep inside the executor, once at the tail),
(d) the tail use-count refresh, (e) carrier/cargo FIELDS per spec C1-C4 with
NO new chooser (C5 is a named non-goal), (f) magnetron/Phase-Bomb residue
HOME = which ship carries which cidx, measured from the production ring via
shipsave (measurement, not a close). OQ rows stay open (user-gated).

## S3 VERBATIM READS, SECOND PASS (this session, work/r331_disasm.txt line refs)

### S3a FUN_00049acc 0x49acc..0x49c10 — THE RECALC (ships.md section 18, byte-level)
Zeroes [+0x0],[+0x4],[+0x20],[+0x24],[+0x18],[+0x1c],[+0x28],[+0x2c],[+0x30];
[+0x10] := [+0x14] (hull base drive, read at 0x49ae4 BEFORE the zeroing of
the others). Then per slot i=0..cap-1 (ebx walks +0xab stride 7; cidx read as
sar24 of dword[ebx+0xa8] == the slot byte):
  +0x00 += row[+0x52]  (weapon level)      0x49b52
  +0x04 += row[+0x56]  (shield level)      0x49b5c
  +0x10 += row[+0x5e]  (drive level)       0x49b67
  +0x20 += row[+0x62]  (scanner level)     0x49b72
  +0x18 += row[+0x66]  (generator power)   0x49b7d
  row[+0x32]==2 -> +0x1c += row[+0x36]     0x49b85
  cidx==0x47 (Colonizer) -> +0x28 := -1    0x49b9b
  cidx==0x2b (Star Lane Drive)      -> cntA++  0x49bb6 (local esp+0x4)
  cidx==0x2c (Star Lane Hyperdrive) -> cntB++  0x49bc0 (local esp+0x0)
  cidx==0x2a (Cloaker)              -> +0x24++ 0x49bc9
After the loop: [+0x08] = fistp(cntA * ds:0x2583); [+0x0c] = fistp(cntB *
ds:0x258b)  (0x49bce..0x49c04).
NEW SYNTHESIS [inferred from cited law + cited MEASURED pairs]: the live
(+8,+c) pairs are exactly (14,0) and (0,28) (pership-spec section 1 field
table, ships.md S22 L2) => ds:0x2583 == 14.0 and ds:0x258b == 28.0, i.e. ONE
Star Lane Drive contributes lane-step X 14 and ONE Hyperdrive contributes
lane-step Z 28 — which is where the S22 "step CONSTANT 14 base units" honest
residue comes from. The march reads step0 = float([+8]+[+c]); the CARRIER law
that produces it is this recalc. The pool values themselves are not in the
image dump (data pool, t43 stale-DAT law) — the values are DERIVED from the
measured pairs, not read.

### S3b FILE-vs-RAM cross-validation of the upkeep gate (NEW measurement)
Parse of extracted/ascend00/gizmos.txt (76 rows; work/r363_gizmo_rows.json)
reproduces the RAM-measured census EXACTLY:
  flag_list bitmask & 0x20 -> rows {10,11,12,13,14,15}, all cat==1 (the six
  shields) — identical to ships.md section 12 t47/t101 "EXACTLY rows 10..15".
  +0x36 multiset over those rows = {1,2,0,2,4,3} == t47's "0,1,2,2,3,4
  ascending". +0x3e (Level) = 1,2,1,3,4,5 == t47's "propulsion dwords
  1,2,1,3,4,5" == t86's six shield Levels at raw +0x56.
=> the rewrite's Gizmo parse (economy.cpp loadGizmos) IS the design table for
every column the cited laws read; no RAM table needed inside shipsim. Flag
bit 5 (GZ_TOGGLEABLE per the vendor header) is the upkeep gate.
Census: cat counts {0:10, 1:6, 2:5, 3:6, 4:5, 5:44}. Key cidx verbatim from
the file: 0x2a Cloaker, 0x2b Star Lane Drive, 0x2c Star Lane Hyperdrive,
0x3c Lane Magnetron, 0x3f Toroidal Blaster, 0x41 Replenisher, 0x46 Phase
Bomb, 0x47 Colonizer, 0x49 Invasion Module (Cat 5 Power 10 NumUses 0 —
matches spec C1). NumUses(+0x42) is nonzero on 41/76 rows incl. every weapon
and every cat-5 row with a range; ZERO on Cloaker / Colonizer / Invasion
Module / Hyperfuel.

### S3c CORRECTION to pership-spec G9 (bit polarity of the MOVES addend)
G9 words it "or PTR_DAT_00077f6c + [ship+0x10] when bit2 clear". VERBATIM
(0x4a67d..0x4a6a0): `and dl,0x2; je 0x4a69d` — the GLOBAL IS ADDED WHEN
status bit 0x2 IS SET; when clear the plain [+0x10] is used. _wip_t363 S1a
already had it right; G9's parenthetical is inverted. ds:0x77f6c identity is
UNMEASURED (ships.md:365) — the sim models the addend as a sim-level
per-sim constant, never a record offset.
NB the 0x4a658 body is the SAME charge law t86 cites at 0x49f15 (combat.md
S2 CHARGE: +0x88 -= gizmo[+0x36]; if cat==1 then +0x90 += gizmo[+0x56]) and
at 0x4a71f (fire loop). Three sites, one law. The affordability gate is
`cmp ecx,edi; jl next` — cost > power skips the slot ENTIRELY (no partial
burn, no charges).

### S3d FUN_00049a34 0x49a34..0x49aa4 — kind-2 completion, NOW FULLY BANKED
  arg eax=ship, edx=lane-record ptr (stored to [+0x59] at 0x49a82; its first
  dword compared against the old target at 0x49a85 == S22 L1's "A :=
  ptr[H]"). Sole caller 0x4a33d, immediately before the gizmo-use dispatcher
  0x4a360.
  1. call FUN_000499f8(ship, lane) -> 0 => RETURN (no transition).
     0x499f8 verbatim: edx = [+0x8]+[+0xc]; if edx > 0 goto CHECK; else
       race = [+0x54]>>16; if BYTE[0x12fb3 + race*0x1ee] != 0x12 -> return 0;
     CHECK: byte[lane+0x23] & 0x2 == 0 -> return 0; else return -1.
     => TRANSIT ADMITTED IFF (lane carries the 0x2 flag) AND (the ship's
     lane-step words are set OR its species row col == 0x12). The species
     gate is the SAME col-0x12 gate as S22 L5 march gate 2 (never witnessed,
     zero census — spec N4: keep the FORM, do not fire it).
  2. kind == 3 -> target := 0x13bc5 + ([[lane+0xa]>>16) * 96)  (system-object
     table stride 0x60) ; else target := existing [+0x59].
  3. call FUN_000220a8(target, ship) — THE TRAVEL ISSUER (T-4).
  4. [+0x58] := 5 (the 4th kind-5 store, S61 item 4); [+0x9e] := 0 (lane-local
     x reset); [+0x59] := lane; [+0xa2] := (oldTarget == [lane] ? 1.0f :
     0.0f) — a DIRECTION flag (travelling from the lane's A end).

## S4 CORRECTIONS TO EARLIER WIP SECTIONS (raw disasm adjudication)

1. S1a line "bit0 SET -> DWORD [+0x94] := 0; jmp 0x4a727 (skip ring scan)" is
   WRONG. 0x4a67b is `eb 29` -> target 0x4a6a6 (shields +0x90 := 0), and the
   RING SCAN STILL RUNS (0x4a6b0 loop). So status bit0 zeroes MOVES but does
   NOT exempt the ship from the maintenance burn or the shield recharge.
   0x4a727 is the loop-EXIT target (the `jge 0x4a727` at 0x4a6d4), not a
   bit0 branch.
2. S1b stands (two call sites), but S1c's tail ORDER refines: FUN_0004a74c
   runs refill -> refresh loop -> kind-5 march body -> call 0x4a658 at
   0x4a95b for EVERY ship (both the march path and the `jne 0x4a959` skip
   path converge on the upkeep call). Status is zeroed at 0x4a756 BEFORE
   that call, so within the tail the upkeep bit tests always see 0.
3. S3d lane gate polarity CORRECTION: FUN_000499f8 CHECK leg is
   `test BYTE[lane+0x23],0x2; jne 0x4a2e(return 0)` — bit 0x2 SET means
   DENIED (closed lane), CLEAR means admitted. SimLane field named `closed`.
4. Executor internal (new): commit entry FUN_00049f28 (0x49f28..0x49f4a)
   dispatches on [+0x62]: 0 -> walk FUN_00049f54; 1 -> gizmo-use FUN_0x4a360;
   result stored [+0x84]. The completion switch (type1->0x49880,
   type2->0x49a34, flag 0x8 = arrived) lives at the TAIL of the walk body
   (0x4a31a..0x4a33d), so a kind-2 arrival TRANSITIONS TO KIND 5 INSIDE the
   commit — the executor's assert check at 0x419df then sees kind 5, which
   the RAW sequence treats as an assert-0x93e call (the dossier's "3 or 4
   tolerated" reading keeps kind 3 alive via the 0x39894 gate leg). Sim
   follows t361: count, never fatal.
5. SAVE MEASUREMENT (scripts/r363_gizmo_census.py RC=0, work/r363_gizmo_census.out,
   20 saves / 2140 live rows / 5940 real ring slots):
   - REFRESH LAW CORROBORATED: every slot whose design NumUses(+0x42)==0
     (4960 slots) carries use-word 0; every slot with NumUses==1 (860) or
     ==3 (120) — the 980 "match" bucket is exactly NumUses==1 slots; ZERO
     below/above examples. Autosave lands post-tail, so word == design[+0x42]
     holds 5940/5940. The refresh operand reading +0x42 is now MEASURED
     save-side, not just disasm-derived.
   - RESIDUE HOME: Invasion Module 0x49 on 500 slots / 260 distinct ships;
     Colonizer 0x47 on 960 slots / 140 ships; Star Lane Drive 0x2b 980/500;
     Hyperdrive 0x2c 200/100; Lane Magnetron 0x3c ZERO slots; Phase Bomb 0x46
     ZERO slots in this corpus (consistent with t326b/t329 zero-censuses —
     the HOME is the ring field; the carriers exist only as data rows when
     scenario data puts them there).
   - SLOT PAYLOAD dword: 5860/5940 == 0x0; 80/5940 == 0xFFFFFFFF and ALL 80
     sit on upkeep-gate rows (the six shields 10..15). The 0x4a658
     `cmp DWORD[slot+3],-1` eligibility gate is therefore SELECTIVE in real
     data, and exactly 80 shield slots are burn-eligible at the sampled
     states. Payload identity itself remains UNMEASURED (no consumer law
     beyond the -1 test).
   - Duplicate cidx across slots LEGAL re-confirmed: 600 rows carry repeats.

## S5 SESSION OUTCOME + NEXT-SESSION CODE CONTRACT (budget stop; code REVERTED clean)

All static + measurement evidence for t363 is banked above (S1-S4). A full
implementation was drafted mid-session (shipsim.h/.cpp: SimDesign/InvSlot,
recalcShip, upkeep, refreshUseCounts, setSlot/clearSlot/fillFirstEmpty,
carriesCode/firstCarrier, starArrivalComplete + laneToB + laneStepX/Z pools +
orderPayloadLane/speciesLaneTravel + BoundaryReport.laned) but the run-time
budget expired before the advanceBoundary wiring, digest extension, pins,
and build. The draft was REVERTED (git checkout — tree clean at
shipsim.{h,cpp}); nothing half-edited is on disk. RE-LAND CONTRACT (one
session, ~30 probes):

1. Header (shipsim.h): add `struct InvSlot {uint8 cidx; uint16 use; uint32
   payload;}` + `struct SimDesign {int cat; int32 power,range,level,numUses,
   industry; bool upkeepGate; + rowWeapon/rowShield/rowDrive/rowScanner/
   rowGenPower = cat==0/1/2/3?level:0, cat==4?power:0}` (derived-slot law
   ships.md §18 init-zero + category switch); Ship += weaponLevel/shieldLevel/
   scannerTotal/specialCount/cat2PowerCarry/targetSlot(-1 law)/hullBaseDrive/
   shields(+0x90)/inv[25]/invCap/invFilled/laneToB/orderPayloadLane/
   speciesLaneTravel; SimLane += `closed` (byte[lane+0x23]&0x2 == CLOSED —
   POLARITY S4 item 3); kCidx* constants (S2f/S3b); laneStep pool constants
   kLaneStepXPool=14.0f kLaneStepZPool=28.0f (DERIVED, S3a); ShipSim +=
   designs_/driveAddend_ + API setDesigns/recalcShip/upkeep(->int32 burn)/
   refreshUseCounts/setSlot/clearSlot/fillFirstEmpty/carriesCode/
   firstCarrier + private starArrivalComplete; BoundaryReport += laned.
2. Implementations: EXACTLY as written in this session's revert (bodies are
   law-annotated in _wip S1a/S3a/S3d + the header comments above; the git
   stash is GONE — rewrite from this contract, do not hunt for the draft).
   Key gates: setSlot idx>cap REJECT / idx==cap ADMIT phantom-inert; same-
   cidx-same-slot REJECT; upkeep order = moves(0|drive+addend) -> shields:=0
   -> per-slot(gate&payload==-1&cost<=power)->burn, cat1->charges NESTED ->
   bit3 zero; refresh word:=numUses; recalc window i<invCap EXCLUSIVE.
3. advanceBoundary wiring (THE ORDER, S4 item 2): tail per ship per race:
   status:=0 -> power:=powerRefill -> refreshUseCounts -> (kind5 laneMarch,
   endpoint = laneToB? star(l->b): star(l->a) — CURRENT code uses l->b
   unconditionally; make it laneToB-driven, default laneToB=true pins keep
   the t361 golden jitter test green: mkLane A==B in that test anyway) ->
   upkeep(s) [burn AFTER refill = the t361/t362 refill-without-burn seam
   CLOSED verbatim]. Sweep loop: replace the bare moves:=driveStat re-grant
   with upkeep(s) (0x3ea08 body = re-grant + burn BEFORE the MIN pick).
   commitMove orderType-2 arrival: call starArrivalComplete (kind 2 -> 5
   inside commit; assert leg then sees kind 5 -> rep.asserts++ per t361
   counted-not-fatal; pin asserts==1 for that shape, kind==5, laneId set,
   laneX==0, laned=={id}).
4. digest(): mix shields, weaponLevel, shieldLevel, inv (per slot cidx/use
   low16/payload), invCap, laneToB. Existing determinism test stays
   green (deterministic either way).
5. fromRecord: import inv cidx bytes (Record::ringCidx), invCap, filled
   VERBATIM (phantom +1 preserved), recalc-owned fields verbatim from Record
   (weaponLevel/shieldLevel/scannerTotal/specialCount/cat2PowerCarry exist
   in the parser; targetSlot too). NO recalc on import (recalc zeroes +0x18
   = powerMax — generator-sum only; stored powerMax would be destroyed.
   Named asymmetry, WIP S3a note).
6. PINS test_shipsim_t363.cpp (~8): (a) upkeep burn changes MIN-pick ORDER
   (two ships, one shielded: unshielded-now-poorest picks first) + burn
   lands before pick; (b) unaffordable shield = NO burn AND NO charges
   (nesting mutant); (c) payload gate: shield with payload 0 burns nothing;
   (d) status bit0 -> moves 0 but burn STILL runs (S4 item 1 — the mutant
   that skips the ring scan must fail); (e) refresh: use words := numUses
   incl. 0-for-unlimited; (f) recalc carrier law: 1x LaneDrive -> stepX 14,
   1x Hyperdrive -> stepZ 28, Colonizer -> targetSlot -1, Cloaker ->
   specialCount; (g) setSlot phantom: idx==cap admitted, filled+1, stats
   UNCHANGED (inert); (h) firstCarrier C2 shape: list order, InSystem-only,
   Invasion Module 0x49; magnetron/PhaseBomb HOME = carriesCode accessors
   (fields exist; NO chooser — C5 non-goal; OQ rows stay open).
7. MUTATION CAMPAIGN: burn-after-pick ordering swap; skip-ring-on-bit0;
   charges-unnested; refresh operand +0x3e instead of +0x42; recalc window
   inclusive; phantom-not-inert. All must be caught.
8. Bank ships.md S62 (law prose + census corroboration incl. the 5940/5940
   refresh measurement + 80-eligible-payload datum); pership-spec G9 bit-
   polarity correction IN PLACE (S3c); C3/C4 note: sim-level HOME shipped,
   chooser still open; LEDGER 17/2 UNCHANGED (honest negative — the census
   corroborates laws already credited to t47/t86/t89/t101/t184; no OQ row's
   named closer was touched: OQ-019's sugar-cube-flight-delta residue is
   unchanged, magnetron/Phase-Bomb remain zero-carried in the corpus).
