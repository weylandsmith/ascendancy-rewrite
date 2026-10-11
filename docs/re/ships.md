# Ships — hulls, Gizmo loadout, drive range, combat participation

Sources (all read-only): extracted/ascend00/planitem.txt (hull rows),
extracted/ascend00/gizmos.txt (component table; field semantics are the
VENDOR's own header comments, lines 19-49), extracted/ascend02/ship.bin +
ship.tsv (inventory stats in docs/re/tables.md §ship.bin), tutorial text in
ascend00 files (Shipyard definition), docs/re/economy.md (REQUIRES
semantics), docs/re/turnloop.md (where phases run).

## 1. Hull items [verified rows, planitem.txt]

| item       | IND RES PROS MPOP UPOP COST REQUIRES | meaning |
|---|---|---|
| Shipyard   | 1 0 0 0 1 240, REQUIRES 0        | orbital structure that enables building ships (vendor tutorial: "Shipyard, the orbital structure that makes building ships possible") |
| Ship       | 0 0 0 0 1 20,  REQUIRES 1        | the ship hull itself; industry cost 20 plus Gizmo Industry column |
| Orbital^Docks | 1 0 0 0 1 170, REQUIRES 16    | listed, not modelled (P-scope) |

REQUIRES indexes restree rows (economy.md §1). Shipyard req row 0 =
"Orbital Structures"; Ship req row 1 = "Interplanetary Exploration" (both
names verified verbatim in the restree string pool).

## 2. Gizmo loadout [verified table]

Ship-borne components are the Weapon(0)/Shield(1)/Drive(2)/Scanner(3)
categories plus Generator/Special. The Industry column is ADDED to the
Ship hull cost (vendor header, gizmos.txt lines 43-45: "The cost in
industry points added to the cost of building a ship" — note the vendor's
own TODO about a cost hack in Ship::init_global_gizmos(); the exe-side
hack is R1-blocked, so the rewrite uses the file values unmodified).
ResReq gates each device per restree row, exactly like planitem REQUIRES.

## 3. Drive range [verified semantics, inferred composition]

Vendor header (gizmos.txt lines 33-36): "For drives, the maximum distance
that can be travelled, in sugar cube units". ALL FIVE drive rows (Cat 2),
Level then ResReq (column 8, the same layout the gizmo loader uses),
verified: Tonklin Motor 2/2, Ion Banger 4/10, Graviton Projector 6/23,
Inertia Negator 6/46, Nanowave Space Bender 10/54.
(Note: "Hypersphere Driver" is Cat 0 — a weapon despite the name; verified
row `0 6 75 10 2 100 0 0`. A first draft of this section mis-read ResReq
from `r[-2]`, which is flag position 7, not the gate row.)
"Sugar cube" = one map-grid cell: [inferred] — the map coordinate system
is the 0..1023 grid of docs/re/mapgen.md; no extracted file defines the
sugar-cube scale numerically. The rewrite therefore treats drive Level as
LANE HOPS per turn [inferred default], one ship = best researched drive
per owner (no per-ship design UI exists statically; OQ-019).

## 4. Combat participation [inferred model delta on turnloop.md §5]

The static data names every input but never the arithmetic (OQ-010):
- attack of a ship = best researched Weapon Level (damage per vendor
  header line 29: "For weapons, damage"),
- defence of a target = best researched Shield Level (header: "For
  shields, strength") + garrison term,
- NumUses (uses per turn, 0 = unlimited) limits how many attack actions a
  fleet performs per turn per owner.
The shipped capture model (turnloop.md §5) is: attack = owned-pop/10
reserve + highest RESEARCHED weapon Level, defence = garrison + highest
RESEARCHED shield Level, small seeded noise. The gizmo levels are the
data-cited inputs [verified distinct Level values]: weapons {1,2,4,6,10,13}
(verified rows; note "Hypersphere Driver" is a weapon), shields
{1,2,3,4,5}. The linear composition (pop/10, additive) is the documented
default — the exe arithmetic stays OQ-010. No rebalance multiplier was
invented in this pass: when R1 lands, replace composition, not inputs.

## 5. Implementation mapping

- Campaign::buildPhase: a star builds Shipyard when REQUIRES row 0 is
  researched (one per star, existing quota behaviour); a Ship hull may
  then be LAUNCHED from that star — Shipyard is the launch precondition
  (tutorial text §1), hull industry cost 20 charged at launch as today.
- Launch distance: owner's best researched drive Level /2, clamped to
  [1, 3] lane hops (documented default for the sugar-cube scale; a unit
  test pins the five drive levels).
- Campaign::combatPhase: attackScore/defenseScore keep §4's research-gated
  gizmo levels (already shipped).
- Gate: campaign smoke still reaches VICTORY with the gates active;
  test_ships.cpp pins the Ship/Shipyard rows, all five drive rows, and the
  no-Shipyard = no-launch invariant.
NOT modelled (stated): ship design screen, per-ship inventories,
Orbital Docks effects, the vendor cost hack (R1), fleet stacking.

## 6. Gizmo loader + record law (OQ-019 t15, 2026-10-08) [verified static]
- gizmos.txt unique code referrer: pool imm 0x2538 @0x49081 inside
  FUN_00049074. POOL-BASE LAW TRIPLE-CONFIRMED: pool offset = image offset
  - 0x82bb0 (soundfx.txt 0x2a08->0x84bb8...; RACE%02d.DIP 0x21f0->0x84da0 ✓;
  gizmos.txt 0x2538->0x850e8 ✓ literal verified).
- Record: stride 0x6a, LOOP COUNT 76 (`CMP EBP,0x4c @0x490ed`), record base
  = PTR_DAT_0007650c table. Parse: '%s' (name, '^'->' ' substitution loop
  @0x4916x family) then EIGHT %d then a 255-terminated bit list:
  +0x32 cat (byte), +0x36/+0x3a/+0x3e/+0x42/+0x46/+0x4a/+0x4e/+0x35 = the
  eight fixed columns in file order, +0x33 u16 RESREQ BITMASK (bits set
  from the list until value 0xff — v1's "column 8 ResReq" is this list,
  refined: multi-node capable).
- Derived slots (init to 0 @0x4923a..0x49250, then category switch):
  cat 0 weapon -> +0x52 = Level[+0x3e]; cat 1 shield -> +0x56 = Level;
  cat 2 drive -> +0x5e = Level; cat 3 scanner -> +0x62 = Level;
  cat 4 generator -> +0x66 = POWER[+0x36] (matches vendor header "power
  supplied by the generator"); cat >4 -> vendor error 0x2a438 (EBX=0x190?
  msg pool 0x2567). Jump table RAW at 0x49060 (encoded disp 0x344b0 is the
  usual 143-class fiction; REAL table sits BEFORE the function entry,
  second instance of the t11 pattern — bank the pattern, stop re-scanning).
  Switch default falls through to next-record path @0x490e6 (INC/ADD/CMP).
- This switch is the DOCUMENTED per-category parameter interpretation, NOT
  the JJTTODO cost hack. Cost-hack hunt = writers of +0x46 (Industry,
  5th fixed col) OUTSIDE FUN_00049074, or build-cost sites reading +0x46.
- Design-screen assets/edges banked: name-table idx 61 `data\8shipdes.tmp`,
  74 `data\8shipdes.shp`, plus shipicon + 21 smshipNN + dkship shps;
  strings SHIPDESIGN@0x83a69 (refs 0x26fcb,0x31da4,0x52630),
  SHIPDESSCREEN@0x83aae (ref 0x27bba), shipdesx@0x83ac7 (ref 0x27c05),
  owner coswnd.cpp. ship.bin (386)/ship.tsv (393) in table.
## 7. NEXT residues (open, do not re-derive §6)
cost-hack location; per-ship inventory record (ship.bin table law?);
sugar-cube numeric scale (drive Level in hop math at move code);
Orbital Docks effect readers.

## 8. init_global_gizmos located — and it is NOT the cost hack (t15b)
- FUN_0004929c = sole caller of the loader; vendor owner string pool 0x2567
  `..\ship.cpp` (verified verbatim in banked RAM pool). One-time guard
  DAT_00076508. What it does: init ship-object template fields, copy 8
  species names into 0x14-stride slots via FUN_00021a20, CALL the gizmo
  loader, then compute a QUOTA-DISTRIBUTION bitmask over gizmo tables
  (research-bit masks DAT_0000685c/DAT_0000686c, 14 columns) writing bytes
  at &PTR_PTR_000764cc — the "available gizmos by level" spread using
  fVar3 = count/(levels-1) float rounding with epsilon pool 0x2573.
- ZERO writes to record+0x46 (Industry) here or in the loader. So the
  JJTTODO "hack in Ship::init_global_gizmos()" is EITHER (a) this quota
  spread changing *effective* acquisition cost semantics, or (b) removed by
  ship date while the comment stayed. [unverified] which. DECISIVE cheap
  probe queued NEXT: readers of +0x46 (build-cost sites) — if every reader
  uses +0x46 unmodified, the shipped engine charges file values and the
  rewrite ALREADY matches (file values unmodified, §2 v1 default stands,
  closure cites the reader census).

## 9. COST LAW CLOSED — Industry value is never modified (OQ-019 t16)
Decisive probe per §8: image-wide access census of disp 0x46 (mod=1/2,
direct+SIB, stack-ESP/EBP bases excluded as false positives): 26 non-stack
accesses total. THE ONLY WRITE into a gizmo-table record (+0x46, base chain
from PTR_DAT_0007650c) is the loader's own parse store `MOV [EDX+0x46],EAX
@0x491b5` inside FUN_00049074. Every other non-stack access is a different
struct: 0x23a83/0x37f4x/0x38edx write [reg+0x46] of ship/template copies
(the 0x7b-stride ship record and design-screen temp), and the READS at
0x46b6f/0x46b81 are u16 [rec+0x46] of the stride-0x7b SHIP record (owner
byte [+0x57] == DAT_0007458e gate, per-owner stack tally), not gizmos.
x87 sweep (0xd8..0xdf, mod1/2, non-stack): single hit 0x24297 `db7e46` =
FNSTSW [ESI+0x46] — standard FPU-status idiom, not a field access.
Three "ADD [reg+0x46]" candidates (0x2bc06/0x2bc6c/0x34837) verified as
byte-boundary false positives of an INC ECX;INC ESI (`41 46`) string-
sanitizer loop (tab->newline, '@'/'_'->space per Ghidra dump 0x2bbb0..
0x2bc45) — recorded so nobody re-chases them.
Writes into a gizmo record: (1) the loader parse store, (2) `MOV
word ptr [ESI+0x46],AX @0x37f41` with AX=0 inside an ERROR/cleanup path in
ship.cpp (owner string `..\planet.cpp` region; wipes fields 0x42..0x66 to
0 — a bail-out reset, NOT a cost alter). FUN_0004929c (init_global_gizmos
§8) zero +0x46 writes (read in full t15b). => gizmo-record Industry is
NEVER altered post-parse. JJTTODO fork resolves to (b) stale-comment.
Design-total sub-question CLOSED-BY-CENSUS (t21): three exhaustive
sweeps found NO summation code anywhere in the image — (1) t16 w16/disp
census of gizmo record fields: writers = parse-store @0x491b5 + error
zero-wipe ONLY; (2) t18 callee list of design-screen owner FUN_0004b068
= operators only; (3) t21 full 370-instruction dump of FUN_0004ae24
(the function containing 0x4b068): pure design-record (de)serializer —
0x162-byte stack buffer <-> record via MOVSD.REP @0x4af84/0x4b2e7,
pointer-relocation switch on [rec+0x59] (constants 0x13bc5 species
stride, 0x16147, 0x2b057), no gizmo reads, no accumulator. The @0x23a83
store is `MOV word ptr [iVar8+0x1a],0` — a stride-0x7b SHIP-slot field
(t16 correction), and the 20000-cap @0x23b7d reads the accumulated
CELL-count u16 at +0x18245+iVar5 (sVar4 = FUN_00037d80 return = rec
+0x1a capacity), not any money total. LAW [closed by census; positive
form inferred]: per-gizmo values charge as file values at use sites
(t16 reader census, 26 non-stack readers of +0x46); no code in the image
materialises a design cost total. (Example reader shape, range/power not
industry: AI strike eval FUN_0004aa84 reads stride 0x6a +range/+0x6e and
multiplies locally [verified t18].) Rewrite status: ALREADY MATCHES (file Industry used
unmodified, §2 v1 default vindicated — measured no-op, not
plausibility).

## 10. Starting-ship generation law (OQ-019 t17) [verified static]
FUN_000238e8 (scenario init, per empire; ship slot chain param+0x18247
stride 0x7b; design table stride 0x1ee, count [table+0xd86]>>16):
- per design slot: gizmo count g = RNG()%5 + 1, cap 5 (@0x23a03-ish);
  if a matching owned design exists (match by name ptr [designRec+0xd])
  AND its stored count field ==0 -> g=1; then if design exists g =
  RNG()%g (uniform 0..g-1).
- g==0 slot ships get the TWO STARTER TEMPLATE LISTS copied verbatim:
  DAT_000063e0 (84 bytes) + DAT_00006434 (84 bytes) verbatim (copy loops
  21 dwords each). Banked as low-byte sequences ck005:
  A=4 4 3 4 3 4 3 3 4 3 3 3 4 4 4 3 4 3 2 3 3, B=5 1 1 6 3 2 8 6 4 4 10 2
  7 8 9 7 3 5 3 7 9. Semantics [unverified]: 21 dwords = race count, but
  B max 10 too small for gizmo indices (76 exist) — likely per-race
  default design parameters, NOT a gizmo index list. Docs-only landing
  (rewrite models launches, not per-ship gizmo loadouts).
- per-gizmo ship fields: [ship+0xc]=special1,[+0xe]=special2,[+0x1a]=0,
  [+0x10]=0,[+0x5a]=0; gizmo table idx tracked at &DAT_00018245 stride 2;
  error if per-design total >20000 (0x4e20) at @0x23b7d.
- ship speed-ish field: [tmp+0xe0] = 0x168/g (360/g).
- fleet tally per species short &DAT_00027283 += g; vendor error >499.
- design name render: sprintf pool 0xb54/0xb68/0xb7c + `DATA\SMSHIP%02d
  .SHP`(0xb81)/`DATA\DKSHIP%02d.SHP`(0xb90) referrers FUN_00023388 +
  0x6ba86 (cosmos.cpp) — SM = small/standard, DK = deck/design-keeper
  model set names; ACE%02d.SHP (0xb5c) zero direct refs (143-class or
  data-only), do not re-scan blindly.

## 10. ORDER/ARRIVAL CHAIN (t46 increment; cost-hack RE-CONFIRMED closed)

Cost-hack sub-item re-verified with the generalized t45 sweep (every
memory-writing encoding incl. 80-group/XCHG/POP, non-stack filter): 17
non-stack [X+0x46] accesses, 8 writes — NONE in gizmo-record context
except the §9 pair (parse store @0x491b5 + error zero-wipe @0x37f42;
the 0x38ed8 write is the PLANET recalc store +0x44..0x4c run covering
+0x46 = RES word, the 0x306cc/0x46a44 byte-stores are other structs, the
0x7f038 pair is data-region noise). §9 conclusion STANDS verbatim.

NEW [verified raw disasm + decompile]:
- Ship order fields (record stride 0x7b): +0x5d order-state byte,
  +0x67 order TYPE byte, +0x68 order PAYLOAD (type-1 move: pointer to a
  3-dword coordinate/planet triple — @0x49fb9/@0x49fd7 dereference
  [payload],[payload+4],[payload+8]; type-2 reads payload+0x14..; the
  dispatch switch @0x4a322/@0x4a333 routes type 1 -> FUN_00049880,
  type 2 -> FUN_00049a34).
- MOVE COMPLETION FUN_00049880 (EAX=ship, EDX=payload coords):
  1. ORDER BOOKKEEPING — FUN_00049768 scans the ship's queued-order list
     (count dword +0x15a, stride 7, order-type byte +0xab) for a matching
     type; when found and its turn word +0xac != 0 it DECREMENTED (and a
     float poison write lands at +0x88 — animation timer [inferred]).
     Queued orders with remaining turns SUPPRESS the move [verified shape].
  2. LANDING ATTEMPT FUN_00039810 (EAX=destination planet, EDX=ship):
     gate = (planet+0x57 owner != ship+0x54>>16) requires FUN_00039a00
     (combat/capture check) != 0 else FAIL; scans the orbital RING slots
     u16 +0x18..+0x1a for slot byte1 == 0xFF; on find: ship +0x58 := 3,
     +0x59 := planet record, ring slot byte1 := 0x17 (item 23 Ship) and
     word2 := 1 (ACTIVE), FUN_00039760, return -1 = LANDED. A landed ship
     IS an active item-23 entry of the destination planet — the first
     MEASURED answer to the per-ship-inventory sub-question: the inventory
     lives on the PLANET record's slot array, not a parallel ship table.
  3. NO LANDING (return 0): ship +0x58 := 4 and THREE RNG draws
     (FUN_0007824f %1000 - 500 each) seed a scatter offset handed to
     FUN_00052ff4/FUN_00049aa8 (position setter, writes float triple
     +0x9e/+0xa2/+0xa6 then FUN_000533e0) — the state-4 ship is removed
     from play at a jittered position [state semantics: vanished/
     destroyed-at-sea inferred from the scatter; the exact rule that a
     ship arriving with NO FREE ORBITAL SLOT does not land is VERIFIED].
- SUGAR-CUBE SCALE STILL OPEN: +0x5e reads are all bookkeeping — the
  order-issuer FUN_00041260 writes/copies it (warning compare @0x41be1
  against [DAT_0007e582] pair, low word 0x12 constant across 32/32
  runtime samples, high word {0,1,3,12,17} — scenario/session tag
  [unverified], NOT a distance table), completion clears it to 0, and the
  gizmo-sum @0x49b67 ADDs drive +0x5e into ship stat dword +0x10 (with
  shields +0x52 -> +0x4, scanners +0x62 -> +0x20, power +0x66 -> +0x18).
  NO distance/hop arithmetic anywhere in the completion chain. NEXT ROUTE:
  order-ISSUE section of FUN_00041260 (0x41260..0x41c10) for the range
  test, else FUN_000533e0. Rewrite launch law (Level/2 clamp [1,3]) stays
  a documented default — strict-close NOT met, do not bank as law.

## 11. LANE DISTANCE MATRIX + ORDER-ISSUE GATES (t47 increment; scale still open)

LANE MATRIX BANKED [verified disasm + runtime RAM]: DAT_00045beb, byte
grid indexed 100*x + y from planet coord pair dword [planet+0x2] (two
i16 halves). Index math verbatim @0x41e61..0x41e7f: y from EDX=coord,
LEA*4;SUB -> 3y; SHL 3 -> 24y; ADD y -> 25y; SHL 2 -> 100y; + x. Static
image bytes are CODE (stale-DAT trap, t43 law) — runtime copy at
B + 0x82bb0 + 0x45beb. MEASURED runtime values: small non-negative
integers 0..25 plus 0xFF markers, zero where no lane path, 1-count ~110-
168 per save (lane-pair symmetry), i.e. a PLANET-TO-PLANET LANE DISTANCE
grid recomputed per scenario. 7 read sites: 0x3fa0d, 0x3fd65 (AI scoring),
0x41a84/0x41b03 (issuer), 0x41e7f (FUN_00041e34 multi-ship task planner),
0x45cb6 (AI objective eval), 0x4aa74 (helper returning dist of ship's
planet).
- ISSUER RESOLUTION LAW (raw decompile FUN_00041260 case state-1
  @0x41adf..0x41b60): with A = ship's pending target ([ship+0x5e]) and
  B = the new focus, the code computes D0 = MAT[hi16(A+2)+100*hi16(B+2)],
  scans B's lane list ([B+0x2c] pointer array, count w16 [B+0x44]) and
  sets a flag when some lane-end N satisfies MAT[hi16(A+2)+100*hi16(N+2)]
  == D0-1 (strict gradient along the lane graph), THEN issues the order
  with payload +0x68 := [ESP+0x390] = a LANE-ENTRY pointer — i.e. the
  order target is the graph neighbour on the descending-distance path,
  not the far planet [verified structure; "one hop per issue, re-issued
  until arrival" is [inferred] from the cancel-at-destination branch
  @0x41a0b..0x41a4a which clears +0x5d when +0x5e == focus]. Failure of
  the gradient scan hits vendor assert FUN_0002a428.
- AI cost model @0x3fa0d: penalty (3-D)*2 when D < 3 (closer = cheaper);
  @0x3fd65: time budget by distance class {0->200, 1->225, <4->300, else
  400} divided by (turn - DAT_00012e10).
- QUEUE-TURN LAW: queued orders live in the ship record (count dword
  +0x15a; slot entries stride 7: type byte +0xab, turn w16 +0xac). The
  ONLY writer of a queued slot turn-word is @0x3ac1c inside the EVENT
  handler (word store [EDX+0xac] where EDX = ship+99+idx*7 — the pending
  slot pointer set at @0x415ca/@0x416?? in the issuer; ship+0x67 := 5) =
  the delayed-move (N-turn wait) issue path.
- AUTO-ORDER LAW (FUN_00040178 @0x40178): every ship with NO active order
  at turn start: if +0x28 == -1 (target slot empty) -> FUN_0004105c picks
  a target: unowned planets (+0x57 == 0xFF) scored by FUN_00039b28;
  threshold local_18 = 0x1e (30), reduced to 0xf (15) when the empire is
  at war / enemy home visible (lane state 2/3 rules over war table
  DAT_00012fd6 stride 0x1ee); best score > threshold -> +0x5d := 2
  (ENGAGE), +0x5e := target. Else min-distance helper FUN_0004aa10 over
  empire planets (lane-adjacency test reads the SAME matrix @0x4aa74).
- SCALE STATUS [still OPEN, strict-close held]: the drive Level (+0x5e is
  the ISSUED TARGET here, NOT the drive value — correction of the t46
  note: drive levels are summed into ship stat dword +0x10 @0x49b67 per
  §10) NEVER appears in a distance compare on the issue/completion paths;
  NO range reject exists in the issuer. NEXT ROUTE: turn-advance code
  (0x4c4xx family reads +0x15a list per ship; FUN_0004a6b6/0x4a766 walk)
  for the move-points consumption math (stat +0x10 vs matrix distance) —
  that is where the sugar-cube scale must land. Rewrite [1,3] launch
  default stands (NOT contradicted, NOT upgraded this turn).


## 12. GIZMO FUEL / PROPULSION LAW (t47, static CLOSED + runtime MEASURED; hop-scale consumer still open)

FUN_0004a658 @0x4a658 (per ship, per turn) [verified verbatim, full
decompile]: if ship status w16 +0x9c bit0 set -> design-list pointer
+0x94 := 0; else +0x94 := [ship+0x10] (direct, or PTR_DAT_00077f6c +
[ship+0x10] when bit2 clear). Speed accumulator dword +0x90 := 0 ALWAYS.
Then for EVERY queued order slot i < dword [ship+0x15a] (stride 7 from
ship+0xab): if slot type byte != 0xFF AND (w16[row+3] AND 0x20) AND slot
dword +3 == -1 (row = type*0x6a + gizmo table base): THEN if dword
[row+6] <= dword[ship+0x88]: dword[ship+0x88] -= dword[row+6]
(MAINTENANCE BURN from movement budget +0x88), and IF IN ADDITION
byte[row+2] == 1: dword[ship+0x90] += dword[row+0x26] (PROPULSION BONUS
-- note the nesting: a propulsion bonus ONLY accrues when the upkeep
gate bit is set AND the burn was payable). Finally bit3 of +0x9c zeroes
+0x90 again.
RUNTIME MEASURED 484/484 saves (scripts/r1_gizmo_fuel_table.py, base =
B + 0x82bb0 + 0x7653c): EXACTLY rows 10..15 carry BOTH the upkeep gate
bit and the propulsion flag -- the six drive gizmos. Upkeep costs
dword[row+6] = 0,1,2,2,3,4 ascending; propulsion dwords @+0x26 =
1,2,1,3,4,5. All other 60+ rows: no upkeep, no propulsion.
CONSUMER STILL OPEN: which of +0x88 (budget minus upkeep) or +0x90
(speed accumulator incl. design base at +0x10) feeds the per-turn
advance, and against WHICH distance measure -- the sugar-cube scale
turn. NEXT ROUTE (round-capped 2): readers of +0x88/+0x90 in the turn-
advance family (0x4c4xx walk per S11). S11 assert polarity RE-CONFIRMED
raw: gradient-not-found falls through to FUN_0002a428 ("..\race.cpp"
string @0x84cb4); found-flag 0xffffffff @0x41b15 skips it @0x41b28.


## 13. SCALE-LAW INCREMENTS (t48): x32 gizmo units, +0x88/+0x8c budgets; drive-hop conversion NOT in executor — BLOCKED route recorded

SWEEP COMPLETENESS [verified, generalized method]: dword[rec+0x88] has
exactly 9 instruction sites, dword[rec+0x90] exactly 4; ALL within
0x4b0xx-0x4c7xx (walk snapshot @0x4b376/@0x4b390 copies the ship record
fields to a local shadow; executor FUN_0004b8e4; bookkeeping @0x42447,
@0x4dbce). The scale law CAN only live there.
FUN_0004b8e4 @0x4b8e4 order executor (param_1=issuer, iVar6=[ship+0x68]
target, row=slot type*0x6a) [verified verbatim]:
- x32 UNIT LAW: gizmo RANGE = dword[row+0x0a] << 5 world-float units
  (ranged orders fire only if sqrt-sq-distance(target,ship) <= that;
  status +0x9c bit2 scales the compare); gizmo STEP arithmetic
  dword[row+0x1a] << 5 floats appears in case 0x34 (@0x4be05:
  distance(iVar6,ship) minus step, floor float 64.0f via written
  0x42800000, coordinate triple [iVar6+0x9e..] rewritten through
  FUN_00052ff4) and case 0x28 (@0x4c2b8: scans ALL ships, applies the
  same step-clip to coordinate triples of ships within range). WHICH
  gizmo rows 0x34/0x28 belong to is identity-resolvable but the
  who-moves-whom semantics are NOT banked here. Runtime MEASURED (32
  saves, extended r1_gizmo_fuel_table.py fields): range dwords nonzero
  on weapon/scanner/special rows (25..1000); STEP dwords on rows
  0x26..0x4e (5..255). The two float multipliers
  _DAT_00002743/_DAT_00002747 are NOT image-constant floats (image
  bytes decode as denormals/garbage) — runtime-initialized floats,
  values [unverified] here.
- BUDGETS: +0x88 fuel pool (capacity dword +0x18): upkeep burn per S12;
  executor 0x44 'D' REFUEL transfer min(step, cap - cur) target += /
  issuer -= (@0x4c1b0..0x4c1c5); 0x23 '#' drain-to-zero; AFFORD GATE at
  entry: [ship+0x88] < dword[row+0x06] -> order power field zeroed.
  +0x8c parallel budget (capacity dword +0x98): per-gizmo steps case
  0x3b ';' clamped by dword[row+0x1a], default letter-family decrements
  by per-queue class counts, pool < 1 -> FUN_00049d2c cancel.
- IMMOBILISE case 0x30 '0'/'8' family: [rec+0x90] := 0, status |= 8.
DRIVES DO NOT PARTICIPATE IN THE EXECUTOR [verified runtime]: rows
10..15 (the six drives, S12) have RANGE=STEP=0 dwords — no x32 term.
Their entire static footprint is: stat +0x10 sum @0x49b67 (S10) and the
S12 upkeep/propulsion bookkeeping into +0x90. No consumer of +0x90 as a
per-turn distance was found in the executor, the walk-snapshot family,
or anywhere the +0x88/+0x90 sweep reaches. WHERE A TURN OF FLIGHT
CONSUMES FUEL/COMPUTES POSITION REMAINS OPEN — closing route recorded
in BLOCKED.md (t48): consecutive-save trajectory diff of in-flight ships
([+0x9e] float delta per turn vs drive-Level sum + design base).
AI-vs-EXECUTION SPLIT [inferred from verified pieces]: inter-system
adjacency exists ONLY in the lane matrix S11, used by AI targeting and
time budgets — never by order execution. Rewrite [1,3] launch default:
NOT contradicted (execution layer has no hop term; AI prefers <4 but
does not forbid), held unchanged.


## 14. CORPUS CONTAINS ZERO SHIP ACTIVITY (t49 negative census; scale route needs NEW capture)

Two independent probes over the full banked corpus (484 saves):
1. SHIP SLOT ARRAY probe (runtime ship-table read, stride 0x162 per
   FUN_00022304 law, count word at runtime DAT_00043483 family):
   EVERY save exposes 5 slots, ALL owner 0xFFFF, state 0, coords
   (0,0,0); 2,260 consecutive-save slot-pair observations: ZERO state-4
   (in-flight), ZERO coordinate movement. [caveat banked: the count
   dword DAT_00043489>>16 read 200 uniformly (wrong mapping — image-
   span vs heap-span trap); the word read giving 5 internally-
   consistent empty slots is what this census reports; whether a
   populated array would decode cleanly under this mapping is UNTESTED,
   no populated save exists.]
2. ORBIT-RING probe (verified slot-array law [planet+0x10]+0x88 stride
   4, byte1 = gizmo id): active rows across all 484 saves contain ids
   {1: 327, 5: 777} — runtime item table names verified id1 Agriplot,
   id5 Colony Base — and ZERO id-0x17(23) rows. Per §10 landing law (a landed
   ship IS an active item-23 ring entry), NO SHIP HAS EVER LANDED IN
   THE CORPUS. Consistent: no ship launched either (array empty).
CONSEQUENCE for the sugar-cube scale: the t48 BLOCKED regression route
CANNOT run against the existing corpus — there is no flight to regress.
The one-run closing route is REFINED (docs/BLOCKED.md): a NEW R1
capture that ISSUES A MOVE ORDER (scripted map click sequence — click
ship at home orbit, click destination star, End-Turn x2) then reads
ring item-23 rows + ship coords across the saves. That is a capture-
capability extension, not a static or refuted route. Until then scale
stays OPEN under the standing default [1,3] AI-preference adjacency +
immediate arrival (unchanged, still not contradicted).
Idle-corpus meta-lesson banked: EVERY prior corpus law (income,
placement, governor inertness) shares this scope limit — the 511:67
End-Turn deep schedule never interacts; laws about interaction states
(ships, combat, abilities) are structurally uncapturable from it.
