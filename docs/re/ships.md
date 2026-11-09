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
LIVE CORROBORATION t253 (do not re-measure): the six SHIPDESSCREEN gizmo tabs
map onto §6's categories EXACTLY (measured 6/6, docs/re/ui-runtime.md §6c), and
the tab->category map is NOT the tab order nor the SENDMESSAGE order
(ENGINES msg 54 = cat 2 while SENSORS msg 53 = cat 3; msg 56 has no tab; HULL
msg 50 selects hull SIZE, not a category — pressing it repaints only the tab
grid, 1973 px bbox x524-632 y7-76, GIZLIST unchanged). gizmos.txt record census
76 = cat0 10 / 1 6 / 2 5 / 3 6 / 4 5 / 5 44 matches combat.md S2's runtime
table. Consequence for any future design-screen code: carry an explicit
tab->category TABLE; deriving the category from message or index is wrong.
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

*** t101 CORRECTIONS + CLOSURE [verified raw objdump; trail
docs/re/_wip_t101.md F4/F5; tool scripts/r1_t101_field_verify.py RC=0]:
(1) RECORD-START CONVENTION: this section's "row" base 0x7653c sits
0x30 ABOVE the raw design-record start 0x7650c (t87 map) — every quoted
[row+K] here == raw design[+0x30+K]: row+6 == +0x36 (POWER COST), row+2
== +0x32 (category byte), row+0x26 == +0x56 (SHIELD level, CAT==1 rows).
The VALUES were measured on the RIGHT BYTES; the semantics were not: the
row+2==1 gate == design[+0x32]==1 == the shield family (combat.md S2d
CAT_SHIELD), [ship+0x90] is SHIELD CHARGES (t86 closed), and the
"propulsion dwords 1,2,1,3,4,5" are EXACTLY t86's six shield Levels at
raw +0x56 — same bytes, so rows 10..15 are shields by the raw table
[LIVE-NAMED 60.sav: Ion Wrap, Concussion Shield, Wave Scatterer,
Deactotron, Hyperwave Nullifier, Nanoshell; drives are cat2 rows 16..20
Tonklin Motor..Nanowave Space Bender], and t47's "gizmo fuel" law IS the
shield-power/shield-charge law t86 independently closed at 0x49f15;
drives' entire footprint remains the stat +0x10 sum @0x49b67.
(2) "+0x94 design-list pointer" label VOID: +0x94 is the per-turn MOVES
budget (integer; panel 'POWER %d MOVES %d INTEGRITY %d' 0x1da8a..0x1daaf);
re-granted EVERY turn to [ship+0x10] (drive stat sum, S10), optionally
+ ds:0x77f6c (identity UNMEASURED — a global addend read only here) by
status bit1, zeroed by bit0 — FUN_0004a658 raw.
(3) THE OPEN CONSUMER IS CLOSED: travel consumes BOTH budgets at the
commit-gated site 0x4a2d4..0x4a314 (`cmp edi,0x1` = S2h mode law):
fild [ship+0x94]; fsub travelled-float; fistp [ship+0x94] AND
[ship+0x88] -= int arg (POWER burn). Order-completion leg 0x41df4..
0x41e07 drains +0x94/+0x88 to 0 folding the remainder into a build word.
The "sugar-cube scale" question becomes: distance is the RAW float world
distance walked per step call 0x533e0 — no hop/turn abstraction exists.
The +0x88 recharge law (trunc([+0x18]*(1+clamp((T-[+0x52])//100,0,10)/
10))) is F7/F4. Rewrite: still no delta (aggregate model; per-ship fields
= OQ-019). ***


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


## 15. DISTANCE-MATRIX PRODUCER LAW (t52, static) — FUN_00023e00 fills DAT_00045beb; OQ-021 threshold NOT found (round 2 dead, see BLOCKED t52)

Method note first: t51's R12 says direct-reference scans are blind; this
round used an arith-motive scan instead (IMUL-imm100 encodings 6B /r 64 and
69 /r 64 00 00 00 over the whole code span) — 12 sites total, ALL verified
against the Ghidra listing before use (5 of 12 were mid-instruction false
positives, 'No instruction at address' — R7 trap re-confirmed, discarded).

PRODUCER [verified verbatim, FUN_00023e00 decompile]:
- Star coordinate floats live at star-record +0x08/+0x0c/+0x10 (x,y,z,
  float); star-record stride 0x60 (index math `idx*0x60 + base`).
- Pairwise loop: for star i vs every star j, dx/dy/dz = coord_i - coord_j,
  squared-sum -> sqrt (FUN_00076da0/FUN_00076e08 return-address-tagged call
  pattern @0x23fad/0x23fb2) -> INT(ROUND(...)) kept as MIN against running
  gate initialized 5000; nearest neighbour index stored (short).
- DAT_00045beb diagonal law [verified at its write site]:
  `(&DAT_00045beb)[sVar2 * 0x65] = 1` for sVar2 in [0, starCount) —
  stride 0x65 = 101. NOTE the producer's pair-fill bytes are written by
  the FUN_00023e00 helper cluster at DAT_00032ddb offsets `row + coord*100`
  (linear 100); whether the 101-stride writes and the 100-linear consumer
  read (@0x41b03 byte `[100*x + y + 0x45beb]`) address ONE padded matrix or
  two overlapping buffers is [unverified] — not resolvable from this
  decompile alone.
- Lane availability byte matrix DAT_00032ddb indexed `y_row + 100*x`,
  consulted by the producer as a skip-gate (`== 0` -> candidate), and an
  owner/name short-compare via table DAT_000063c6 (`+ owner*2`) gates
  self-pairs; a not-found path runs FUN_00021ad8 with FUN_0002a428 as the
  error stub (FUN_0002a428 measured this turn: 3-line `if (param_1==0)
  FUN_0002a4cc(param_2)` — NOT an endgame check; t51 STATE lead closed
  as method-dead, one round spent).

RAW RUNTIME SAMPLE [unverified — mapping tension banked, do not cite as law]:
reading 100x+y-linear bytes at member B+0x45beb (41.sav, r1deep slot) gives
1113 nonzero pairs, 1192 asymmetric pairs, 79 cells 0xFF, diagonal values
{0,1,2,...} NOT all-1. This CONTRADICTS the producer diagonal law under the
B+VA mapping — either obj0 DAT runtime placement needs the pointer-law
translation (P0 + payload-offset, OQ-011 form, not B+VA) or the sampled
region is a different consumer buffer. Deliberately NOT resolved this turn
(one probe each way printed above; naming the tension beats guessing).

OQ-021 status: threshold comparison (over-half vs two-thirds) NOT located.
Static leads exhausted within budget (FUN_0002a428 dead; arith scan aimed at
score% not threshold; string xrefs R12-blind). Closing route: t51
consolidated capture session adds step 4 — reach/view the victory screen or
score screen in the scripted run and correlate. Default >1/2 (vendor comment,
turnloop.md S1) stands.

## 16. PLAYER TESTIMONY t179: two-tier turn structure + lane transit (attribution: player, UNVERIFIED until code-mapped)

The player (who has ~1250 turns of play in the captured campaign) reports:
1. TWO TURN TIERS. Within a day there are sub-turns governing ship movement:
   with multiple ships holding orders in a system, each ship executes ONE
   move per sub-turn, round-robin (ship A's second move waits until every
   other ship has had one). If days advance before an order completes, ONE
   sub-turn runs per day until the ship arrives. Consistent with the cited
   per-star stride-0x60 command-exec pass 0x2547c (a campaign+0x3335 loop per
   docs/combat S2h) — but the day-tick coupling (DAT_00012e10 advancing daily
   independent of player End Turn) and the round-robin cursor are NOT yet
   code-mapped. Hunt = queue t183.
2. TWO ENGINE CLASSES. Within-system engines vs star-lane drives are distinct
   gizmo categories with different speeds; MULTIPLE lane drives stack to
   increase speed. Consistent [inferred] with the cited MOVES law
   [ship+0x94] := sum([ship+0x10] drive stat sum) re-granted per processing
   tick (FUN_0004a658) — a SUM naturally stacks.
3. LANE MAGNETRON = one-shot instant lane transit: vendor text verbatim
   (gizhelp.txt:1173-1181 'slip through the star lane almost instantly...
   can be used only once'; gizmos.txt row 'Lane^Magnetron 5 10 50 0 1 50 0 0
   50 1 255', category 5, NumUses 1). Candidate consumer: the cited kind==5
   go-to-star placement handler 0x21f58 (places at star coords with rng%200
   jitter, then kind 5->4) — UNMEASURED tie; do not bank as law until the
   magnetron's use-site reads it. UPDATE t185: USE-SITE FOUND AND MEASURED
   — the magnetron rides the kind-2 target path into FUN_0004ca50, case
   cl==0x3c at 0x4cd5c: Range*32 + flag-bit gates, Power burn, placement
   via FUN_000220a8 + kind-5 handler FUN_00021f58 (star coords + (0,-200,0)
   + rng%200 on the other two axes, jitter const LIVE -200.0 @B+0x82bb0+
   +0xaee), slot rebuild 0x496e4. docs/re/ships.md §19 T3 SUPERSEDES this
   item; the resolver branch at 0x4159a is the RECALLER (literal 0x24),
   not the Magnetron (0x3c) — t183's off-by-one naming corrected.
Implication for the sugar-cube scale question: scale must be sought per tier
(within-system walk units per sub-turn; lane transit as its own law), not as
one global hop count. The [1,3] default is likely tier-blind.

## 17. TRAVEL + SCALE LAWS CLOSED-EXCEPT-UNITS; ROUND-ROBIN RESOLVER CODE-MAPPED (t183)

Method: Ghidra headless over work/ascend_restored.bin (load_program;
project work/ghp5) + live float reads from the const pool IN SITU (read the
FLD-moffs operand inside the save's copy of the function, then resolve
operand VA -> m = VA + 0x88; cross-checked 20/20 playcap saves).

T1 TRAVEL LAW FUN_00049f54 (sole caller FUN_00049f28 = the mode-gated
commit entry; guard [ship+0x58]==4) [verified disasm 0x4a034..0x4a23d +
decompile]:
  delta   = target3 - [ship+0x9e]                      (world f32 units)
  d_w     = sqrt(dot(delta,delta))                     (FUN_00076da0)
  d       = d_w * 0.00625                              (= /160; f@0x25ff)
  walk    = min(d, float[ship+0x94])                   (MOVES is SUGAR units)
  steps   = max(1, round(walk))                        (never zero)
  if int[ship+0x88] < steps: walk := walk*[+0x88]/steps; steps := [+0x88]
  arrived := (walk == d)                               (flag 8)
  per-step displacement = normalize(delta) * (walk/steps) * 32.0 * 5.0
      (f@0x2603, f@0x2607 — decompiler's double-multiply is REAL: two
       separate FMUL moffs verified; 32*5 = 160 inverts the /160)
  commit (param_2==1 only — the standing COMMIT LAW): [ship+0x9e] := new
  pos; [+0x88] -= steps; [+0x94] := round(remaining walk); arrival hooks
  kind1->FUN_00049880, kind2->FUN_00049a34. Order kinds read at +0x67:
  3=abs triple +0x6c, 1=ptr f[0..2], 2=handle (star ptr f0/1/2 or int
  fields), other (incl 5) -> no walk (placement elsewhere).
T2 SCALE CONSTANTS [MEASURED, stable 20/20 saves 41..60]:
  restored RVA -> live VA + 0x88 -> m; pool sits in DATA seg right before a
  '..\ship.cpp' debug string:
    0x25ff -> 0.00625 (= 1/160, world->sugar)
    0x2603 -> 32.0 ; 0x2607 -> 5.0  (sugar->world per-step pair, product 160)
  => ONE SUGAR CUBE == 160 WORLD UNITS; MOVES budget is spent 1 sugar unit
  per step. Vendor gizmos.txt 'Level: drives = max distance in sugar cube
  units' now has its numeric meaning.
T3 GRID QUANTIZER: walk body calls FUN_000533e0 which snaps coords to
  g=DAT_000895dc multiples: coord := round(coord/g)*g (sign-directed).
  DAT_000895dc = 32 MEASURED (20/20 saves; m = RVA + 0x1bf4d8 law).
  LIVE CORROBORATION: 35 ship records (t101 locator, stride 0x162),
  23/35 on the 32-grid exactly; the 12 off-grid ships are ALL order-kind-2
  (star-targeted, mid-transit) with deviations {149.333=160*14/15 x3, 42,
  28 x4, 14, 1 x4} — raw walk/place offsets, not quantized. Grid law reads
  [verified] for stationary positions, [inferred] as arrival-time-only.
T4 ROUND-ROBIN / SUB-TURN STRUCTURE [verified decompile FUN_0002547c +
FUN_00041260 + FUN_0003ea08]: per-system exec builds the eligible-player
list, then REPEATS sweeps while any ship reports work; each resolver call
(1) refills MOVES [ship+0x94] := drive stat sum for all player ships
(FUN_0003ea08 @0x412d4 -> FUN_0004a658), (2) collects ships with fuel>0,
[ship+0x58]!=1, ownership bits, (3) picks the ONE with MINIMUM fuel [+0x88]
(strict <, first-in-list on ties) that has an order [+0x5d]!=0, (4) commits
its move, returns 'more work'. => interleaving is by REMAINING FUEL; FUEL
(+0x88) is the multi-turn budget (only REFUEL orders restore it — S13 case
'D'), MOVES is the per-call budget. Player testimony 'one sub-turn per day'
maps to one sweep per turn-loop run; the day counter (*campaign u32 in
FUN_00024f24, incremented at end, sole caller 0x55f06) has NO autonomous
advancement in obj0: DAT_00012e10 (campaign+? cached turn) has 41 xrefs,
ZERO writers in obj0 (R12: do not byte-scan for the writer).
T5 LANE TRANSIT IS THE SAME WALK LAW UNDER A GRADIENT [verified in
FUN_00041260 case 1]: hop target only accepted when lane matrix
DAT_00045beb[srcIdx + dstIdx*100] of chosen neighbour == target entry
MINUS 1; order then kind 2 (walk to star coords). No separate lane speed
term: two engine classes exist only as gizmo categories feeding the SAME
[ship+0x10] drive-stat SUM (stacking explained). Testimony item 2 'different
speeds' is not contradicted (different Level values feed one stat sum) but
no lane-specific multiplier exists in the walk body.
T6 KIND-5 EMERGENCY BRANCH (0x4159a): FUN_00049768(ship, 0x24) slot-finder
(sole immediate call site image-wide; FUN_00049768 = first slot with
[ship+0xab+i*7]==edx), then [ship+0x62]=1, [ship+0x63]=slot ptr,
[ship+0x67]=5, FUN_00049f28(ship,1) — no walk, placement-type order.
MAGNETRON TIE NOT ESTABLISHED: if gizmo index == file row order (t46
census law), immediate 36 = 'Disarmer', not 'Lane Magnetron' (file row 59);
slot census: 15 of 35 ships carry idx36, ZERO carry idx59. The kind-5
branch is therefore SOME one-shot placement gizmo, identity UNVERIFIED;
§16 item 3 stays UNMEASURED — do not bank magnetron law.
[t185 CORRECTION: this block's row map was off by one — idx36 == RECALLER
(loaded table 76/76 verified, gizhelp help tag gizmo36), idx59 ==
Sacrificial Orb, Magnetron == 60. The 0x4159a branch is the Recaller
emergency recall; the Magnetron's own use-site is in FUN_0004ca50 case
0x3c. See §19 — this paragraph's conclusion is SUPERSEDED.]
UNIT-SYSTEM STATUS: travel distance, MOVES spend, and the 160/32 constants
are CITED; the remaining unit question (ship +0x9e units == star-table f32
units, both world, vs a coarser star unit) is RESOLVED by T2/T3 reading as
one consistent system (nearest-star distances 123-2278 world units / 160 =
0.8-14.3 sugar per hop vs drive 2-12 live — plausible in-system/lane hops;
[inferred]). Closure of OQ-019 still requires the live consecutive-save
flight delta (BLOCKED t48 — zero flights in every passive corpus) plus the
per-ship redesign inventory path; row stays OPEN.

## 18. BUILD/REDESIGN INVENTORY COMMIT LAW (t184; static decode + runtime 1234/1234)

The ship record's gizmo ring at rec+0xab, stride 7, 25 physical slots
(0xab+25*7 = 0x15a where the cap dword abuts). Slot layout {cidx u8
(0xFF=empty), u16 @+1, u32 @+3}. dword[rec+0x15a] = CAPACITY,
dword[rec+0x15e] = FILLED COUNT. NO gizmo record is ever copied into the
ship — the ship holds only cidx bytes; stats are re-materialized on every
mutation by FUN_00049acc (0x49acc..0x49c10 verbatim): zeroes ship
+0x0/4/10/18/1c/20/24/28/2c/30, [ship+0x10] := hull base [+0x14], then per
non-empty slot row = cidx*0x6a+0x7650c adds row+0x52->ship+0x0,
+0x56->+0x4, +0x5e->+0x10 (drive), +0x62->+0x20, +0x66->+0x18,
byte[row+0x32]==2 -> dword[row+0x36]->+0x1c; cidx 0x47 -> +0x28:=-1;
0x2b/0x2c/0x2a -> counts at +0x24 and (count*ds:0x2583/0x258b fistp) at
+0x8/+0xc. This SUPERSEDES the t46 §10 "queued-order list" label on the
ring: it is the INVENTORY (gizmo cidx law measured); the order fields are
+0x5d/0x67/0x68, untouched by any of these writers.

BUILD/INIT FUN_00049534 (kind arg asserted <4; 5 callers: 0x40441, 0x40492
in production builder FUN_00040358; 0x49059; 0x4982a in redesign; 0x49d06):
CAP := dword_live(0x6842 + 2*hull) >> 16 with hull = byte3 dword[rec+0xa7]
(design pointer; UI dialogs store design-image pointers there, ship-side
writer 0x49359). RUNTIME MEASURED [MEASURED 20/20 playcap saves, 1234
owned rows, scripts/r1_t184_inv_law.py RC=0]: cap == table[hull] EXACTLY
1234/1234, caps {10:956, 15:20, 25:258}. The 0x6842 table is
scenario-LOADED data (static image bytes there are code — t43 stale-DAT
law re-confirmed). NAME: hull-name string DAT_00078484+hull*0x14
stride-2 copy into rec+0x34, SKIPPED for player-designed ships
(byte3[rec+0x31]!=0 && owner hi16 == player race DAT_0007458e); INTEGRITY
[+0x8c] := (hull+1)*10, doubled when race-war byte
DAT_00012fb3+empire*0x1ee==1; [+0x98]:=[+0x8c]; hull base [+0x14]:=0.

MUTATORS (all call recalc): FUN_00049698 set-slot(EBX=idx, EDX=cidx) —
rejects idx>cap (0x4969b jg: idx==cap ADMITTED, see phantom law below),
rejects same-cidx in the target slot only (0x496b4 — duplicates across
slots LEGAL, live rows carry 1d 1d / 47 47 / 49 49); FUN_000496e4
clear-slot(EDX=idx) — NO index bound at all; FUN_00049624 fill-first-empty
(no bound either — scans all 25); FUN_0004929c init-clear (zero stats,
cap-window 0xff/0/0).

DESIGN-APPLY FUN_00040d1c (callers inside the class handlers
FUN_000405f8/0x40674/0x407f4/0x40a6c, reached via jumptable cs:[cls*4 +
0x2b798] from production builder FUN_00040358, cls 0..3 from scenario DATs
0x747d6/0x74d1c/0x750a0): filters a 22-entry list at DAT_0x67ec by race
knowledge (FUN_0004a4e0 tests bit in dword live 0x7478b + known-gizmo
class*0x4b) and fills slots up to cap in RNG-SHUFFLED order (FUN_0007824f
% remaining, verbatim 0x40d7b..0x40daf). The class handlers additionally
hardcode starter-kit cidx adds (FUN_00049698 call census: ~10-30 per
handler). UI add/remove: FUN_0004dd50 arms 0x4e425/0x4e4f9 (ship ptr
[ebp+0xab], cidx [ebp+0xb8]>>24, success stamp [ebp+0xbd]:=-1).

REDESIGN FUN_000497a8 (sole caller 0x4e6d2): if new kind == [rec+0xaa]
no-op(-1); new_cap := table[new_hull]; REFUSE -1 iff new_cap < FILLED
[+0x15e] (0x497da) — redesign blocked when inventory exceeds the new
hull's slots; else sweep remove+re-add compacting into low slots, re-init
via FUN_00049534, then copy the hull name UNCONDITIONALLY (bypasses the
player-name gate, 0x4982f..0x49867).

PHANTOM-SLOT OFF-BY-ONE [MEASURED 100/1234 rows, stable 20/20 saves]:
filled == count of cidx!=0xFF over slots 0..cap INCLUSIVE on ALL rows;
100 rows (4 designs {0x143b000,0x1440000,0x1448c00,0x144ac00}, cap 10)
carry an occupied slot AT INDEX == cap, counted by +0x15e but missed by
every i<cap walker (recalc 0x49acc, upkeep FUN_0004a658, scans
FUN_00049714/0x49768) — the gizmo is inert for stats/upkeep yet inflates
the filled count; reachable because 0x49698 admits idx==cap and 0x496e4/
0x49624 take no bound. Origin of the 100 loaded rows [inferred]: loaded
scenario/design data committed through an idx==cap add.

COST SIDE: per-hull cost table live 0x687c (4 dwords) via FUN_0004a41c ->
FUN_0004a3d4; production loop multiplies by CAP at 0x40454
(imul edx,[esi+0x15a]). Design-parse cost store stays t46 §9.

STATUS vs OQ-019: this closes the row's named residue "the build/redesign
inventory path" with cited measurement (static law + 1234/1234 runtime).
Row itself STAYS OPEN — sugar-cube flight-delta closure still blocked per
t48/BLOCKED (needs a capture window with actual flight).

## 19. KIND-5 PLACEMENT CONSUMERS: MAGNETRON USE-SITE FOUND; RESOLVER BRANCH = RECALLER (t185)

Task t185 (last fully-offline OQ-019 residue). Tools:
scripts/r1_t185_magnetron_census.py (RC=0) + Ghidra headless disasm bytes.

T1 LOADED TABLE == FILE ORDER, MEASURED: across 1368 save members under
work/r1, all 76 loaded design-row names at B+0x82bb0+0x7650c+0x6a*g match
extracted/ascend00/gizmos.txt row order EXACTLY (0 mismatches). Row 36 =
Recaller, row 37 = Disarmer, row 60 = Lane Magnetron. t183's §17-T6
parenthetical ("index-36 == Disarmer, Magnetron = file row 59") was an
ad-hoc row map off by one; the t87 parser (and gizhelp.txt's own
help tags: gizhelp.txt:695-699 '#Recaller ... help gizmo36',
gizhelp.txt:1173-1176 '#Lane^Magnetron ... help gizmo60') give the correct
indices. Slot census over owned ship rows (t101 locator): cidx 36 present
129 occurrences, cidx 60 present 360 — ships carry BOTH.

T2 THE RESOLVER'S KIND-5 BRANCH IS THE RECALLER, NOT THE MAGNETRON
[verified bytes 0x4159a: ba 24 00 00 00 = literal MOV EDX,0x24]:
FUN_00041260 calls FUN_00049768(ship, 36) = first slot whose cidx==36
(decompile 0x49768: scan 0..cap[+0x15a], stride 7 from +0xab), then sets
[+0x62]=1, [+0x63]=slot ptr, [+0x67]=5, calls FUN_00049f28(ship,1). The
0x4a360 dispatcher routes kind-5 to 0x4cd90 whose tree case cl==0x24
(combat.md §(a) table row, already banked) IS the Recaller:
ship+0x59 := own-race target-list dword, then calls 0x220a8 + 0x21f58 = the
travel issuer + placement handler. Vendor law (gizhelp.txt:699-701):
"creates an unstable shunt through star lane space to a ship's home
system... arrives immediately at its home system." An EMERGENCY RECALL
fires automatically inside the movement resolver — semantics consistent
with the branch sitting in FUN_00041260. NOTE the magnetron tie §16 item 3
asked about was NEVER in question for THIS branch once indices were fixed;
§16 item 3's "candidate consumer 0x21f58" survives but for the MAGNETRON
via a different path (T3).

T3 MAGNETRON USE-SITE FOUND — §16 item 3 NOW MEASURED [verified disasm
0x4ca50 body + 0x4cd05..0x4cd2f bytes]: the unified gizmo dispatcher
FUN_0004a360 (combat.md §286) routes order-kind [+0x67]==2 (star-target)
to FUN_0004ca50 (0x4a3ac). Inside 0x4ca50:
  lane-d = sqrt(|target_star.pos - ship[+0x9e]|^2)   (pos = star rec f32
      at +8/+0xc/+0x10, alternate triple +0/+4 used when ptr[0]==ship+0x59)
  GATE 1 (range): if design[+0x3a]Range != 0 and Range*32 < lane-d:
      power spend 0 -> activation fails (decompile 0x4ca50:
      `(FUN_00076544+iVar4+2 != 0) && (<<5 as float < local_38)` -> local_28=0)
  GATE 2 (flag): bit1 of WORD design[+0x33] must be set
      (decompile: `(*(ushort *)(iVar4 + 0x7653f) & 2)`; 0x7653f = raw
      +0x33 flag word per t101 convention)
  on commit (mode==1): [+0x88] -= min(Power, fuel)
  CASE TREE on slot cidx (0x4cd51..0x4cd66; each `jc/jbe` pair captures a
  single value): 0x20 -> OR target[+0x23],2 ; 0x33 -> loop ships,
  recompute-distance bookkeeping for other kind-5 orders sharing the same
  target ptr (decompile writes the float distance into [s+0x9e] —
  position-field aliasing flagged, NOT banked as law); 0x34..0x3b -> ret;
  0x3e -> OR target[+0x17], 1<<(ship+0x56) ; 0x3c = LANE MAGNETRON
  (cmp cl,0x3c @0x4cd5c; jc ret; jbe 0x4ccfe):
        0x4cd0d FUN_000220a8(ship,star)   (travel issuer: validates order
            kind in {1,2,2-ish}, lane-connect check via 0x39894)
        0x4cd16 byte [ship+0x58] = 5      (order kind PLACEMENT)
        0x4cd19 dword [ship+0x59] = star ptr
        0x4cd1f FUN_00021f58()            (THE SHARED PLACEMENT HANDLER)
        0x4cd24.. slot-index recompute then FUN_000496e4 slot rebuild at
            0x4cd3f (bytes 29 d0 / 89 c2 / bb 07 / idiv ebx / call 0x496e4)
  USE-ACCOUNTING GUARD (0x4a360 prologue, bytes 0x4a373-0x4a390): reads
      dword design[+0x42]; if 0 -> no decrement; if slot word [slot+1]==0
      -> block; else dec word [slot+1] when mode==1. Recaller's col5 == 0
      and Magnetron's == 1 per gizmos.txt; what col5 numerically MEANS is
      NOT re-derived this session (t87 mapped the COLUMN, not the
      semantics) — do not read "NumUses" as proven until its consumer law
      is cited.
  PLACEMENT HANDLER FUN_00021f58 (body 0x21f58..0x22034 fully read):
      EBX!=0 -> assert 0x2a428 ('..\\ship.cpp' 0xfc); requires
      byte[ship+0x58]==5 (kind 4 at 0x22035 just re-points +0x59);
      target = ptr [ship+0x59]; f32 triple chosen = target[+8..+0x10] if
      EDI==target[0], else target[+0x14..+0x1c] if EDI==target[4], else
      assert 0x2a438 (0x109/0xae0); y := y + f32 DAT_00000aee — LIVE
      VALUE -200.0 MEASURED at B+0x82bb0+0xaee (static payload bytes at
      0xaee are code — t43 stale-static law applies to const pool too);
      TWO rng draws via FUN_0007824f (the single-image LCG, combat.md),
      each reduced idiv 200 (%200) and ADDED to the other two slots of the
      triple (third @0x21ffc..0x22008, first @0x22018..0x22027); commit
      via FUN_00049aa8 (EDX=triple ptr) then byte[ship+0x58] := 4.
      => PLACEMENT LAW = star coords + (0,-200,0) + rng%200 on the other
      two axes (axis naming assumes the triple is (x,y,z) like the
      +0x9e/+0xa2/+0xa6 ship triple) — §16's "rng%200 jitter" CONFIRMED
      with addresses; no distance clamp inside the handler.
=> LAW: Lane Magnetron = player-activated, star-targeted (kind-2 order)
   gizmo, gated by Range*32 lane-distance + design flag bit1, burns Power
   into [+0x88], places the ship via the shared kind-5 placement handler
   0x21f58, then rebuilds the slot (0x496e4). t183's "MAGNETRON TIE NOT
   ESTABLISHED" is SUPERSEDED; combat.md's tree-table "NO CASE" gap list
   did not cover 0x3c because 0x3c lives in the OTHER dispatcher (0x4ca50,
   target-order path), not 0x4cd90.

CORPUS NOTE (corrects t184's "20/20 saves" phrasing): the cap-law corpus is
1234 owned rows spread over 49 save FILES across work/r1 run dirs (t184's
own print says saves_with_ships=49); empty-scenario probe boots
(dword@0x43489>>16 == 0) are headless thread-probe runs, not corrupt saves.

## S20 — t187 FIRST FLIGHT CORPUS EVER (live sitting 2026-10-28, t1255..1335)

The BLOCKED-USER premise is DEAD: with the player flying ships, state-4
rows are OBSERVED (new-window census: state3 x717, state4 x1115, state5
x584; scripts/r1_t187_delta.py). t49's "2260 obs 0 state-4" and t58's
zero-flight corpora are superseded as *arguments* (still valid as what
idle play yields). Full dump: work/r1/t187_scale_dump.txt (scripts/
r1_t187_scale.py, RC=0). Raw regularities banked BEFORE law extraction —
the extraction itself is the t188 task, nothing here closes OQ-019:
1. state5 steady movers step EXACTLY 14/28/56 world-units per turn along
   a pure-x lane line (slots 10,13,16,22,22,26,30,34: d=(14|28|56,0),
   z frozen). Pairing: MOVES[+0x94]=12 -> 28/day; MOVES=6 -> 14/day;
   owner-1 MOVES=4 -> 4.67/day (= 14/3, THREE sub-steps? interpolation
   across autosave rows). 14 = 160/11.43 no clean sugar tie; 28 = 14x2.
2. state4 <-> state5 flips coincide with the [+0x59] order byte changing
   (e.g. 244->165->244, 27->69->27) and with position DISCONTINUITIES of
   1100-2500 units at turn boundaries (slots 17,20,29: 5->4 jump -1905,
   then 4->5 back +1732 one turn later, z small deltas). DO NOT read
   these as instant 1200-unit flights — the working reading (UNVERIFIED)
   is coordinate reframe between system-local and lane frames; t188 must
   disambiguate (magnetron would show kind-5->4 via 0x220a8, not a 5->4->5
   round trip one turn apart).
3. mid-turn POWER [+0x88] diffs now span ALL THREE AI owners (x149/x50/
   x57 sitting window t>=1240): AI ships burn fuel per resolver sweep,
   corroborates t183 round-robin FUN_00041260 min-fuel pick law live.
4. slot13 series shows a lane FLIP mid-window (z=1824 -> z=-1824 at
   t1277->1280, xy reset 224 -> 28): same lane line opposite direction —
   turn-around or re-order; k59 stays 244.

## S21 — t188 LANE-MARCH LAWS FROM THE FLIGHT CORPUS (word trace, cited)

Tools: scripts/r1_t188_speedword.py RC=0, r1_t188_words_dump.txt +
work/r1/t188_words_dump.txt, r1_t188_frame.py (star-grid extent probe);
corpus = trusted first-row snapshots t1250..1340 (r1_t85g_sitting.py re-run
RC=0, 45227 rows — NO new turns past 1335; the +2.9MB timeline growth is the
new-game save ring re-reading, see STATE t188 intake).

1. THE ST5 LANE MARCH IS NOT THE T1 WALK LAW. MOVES [+0x94] and FUEL
   [+0x88] are FROZEN for the whole march (all consecutive-turn deltas
   measured 0; slot10 12/90 while x+=28/turn x6 rows; slot13 4/12 while
   x+=14/turn x14 rows). T1 (FUN_00049f54 commit, 0x4a034..0x4a23d) spends
   both. MEASURED-NEGATIVE: lane transit does not run the walk-commit path.
2. LANE POSITION IS A STEP COUNTER: x = k*step exactly, k = turns since
   lane entry (entry row x == step: slot13 x=14.0000@t1252, slot10
   x=28.0000@t1262, slot17 x=4.6667@t1262). Steps observed {14.0000,
   28.0000, 14/3=4.6667} to 4dp; t187's "4.670" and "28/56 pairing vs
   MOVES" are rounding + missing-turn artifacts. No tie to 160/sugar:
   d/step independent of MOVES (10,14,21,7.005 across rows).
3. STEP IS LANE/ROUTE-SCOPED, NOT A SHIP STAT [verified two ways]:
   (a) slots 13 vs 17 same owner, 23-turn whole-record diff: the ONLY u16
   stable-within-slot yet differing-between-slots is +0x52 (629 vs 770,
   the route handle); (b) ONE ship (slot 13) marched step=14 on lanes
   z=1824 and z=-1824, then step=14/3 on lane z=544 (t1301 x=28.0000 ->
   t1306 x=51.3333) with d10=4/MOVES=4/POW=12 unchanged. The 3:1 speed
   factor lives with the lane/target record, not drive sum or species.
   NB owner-1 = Snovemdomas (SA_DoubleHull) — NO speed ability exists in
   the species table, species hypothesis dead on arrival anyway.
4. TWO COORDINATE FRAMES, SWITCH = THE STATE FLIP [verified geometry]:
   st4 (in-system) coords are EXACT multiples of 32 in x AND z (-1376,
   416, 1600, 2272) — the DAT_000895dc=32 quantizer law holds there;
   st5 lane coords are pure-x with y EXACTLY 0 or 1 and z an exact multiple
   of 32 (1824=57*32, 544=17*32, 352=11*32), lane z OUTSIDE the galactic
   star extent (new-game map read live from ring save: extent ±402/±430,
   star-star med 515 max 880) — st5 xyz is a LANE-LOCAL frame. All 27
   big-mover (>300u) rows in the corpus are state-flip rows (5->4 x14,
   4->5 x11, 4->4 x2), ZERO on st5->5 rows: the t187 "1100-2500u
   discontinuities" ARE the frame switches, not instant flights. None of
   the observed step values matches any star-star distance (nearest-pair
   check: all |d|>158u). MAGNETRON EXONERATED for these rows: 0x21f58
   placement adds rng%200 jitter which would put ships OFF the 32-grid;
   no observed st4 row is off-grid. CENSUS DIRECTION: every state flip
   observed in the corpus is also a frame switch (25/27 big-mover rows are
   5->4/4->5); the converse (frame switch => state flip) rests on the
   slot10 case study (t1253 st5 -> t1254 st4 -> t1255 st5, each with a
   frame jump), NOT a census — st4->st5 may persist across turns untested.
5. LANE-END HANDLING: x saturates at ~224 then the next sampled turn is the
   opposite lane at x=step (slot13 t1277 z=+1824 x=224 -> t1280 z=-1824
   x=28): lane change/turn-around at lane end, k59 unchanged.
HONEST RESIDUE (OQ-019 stays OPEN, strict-close): the lane step CONSTANT
(14 base units) and which lane word carries the 1/3 divisor are UNMAPPED
in code (static hunt needs the st5 order-executor / route-record writer —
NOT the walk body); galactic-frame per-turn displacement for lane transits
is not measurable from this corpus (st4 spans are single-turn, re-entry
erases them); campaign star table overwritten by the ring rotation.

## S22 — t189 THE STATE-5 LANE MARCH BODY FOUND (FUN_0004a74c)

Tools: Ghidra bridge (ascend_restored.bin) decompile+disasm 0x4a74c..
0x4a968; scripts/r1_t189_lawcheck.py RC=0 (first-row snapshots t1250..1340,
slots 10,13,16,17,20,22,26,29,30,34); save reads 41..60.sav.
IDENTITY TIE: this is the SAME function t101 cited for the POWER-recharge
law ([ship+0x88] := FUN_0004a99c() at 0x4a76c — verbatim in the prologue;
t101's 0x3e7b0 citation is the CALLER FUN_0003e6e0 turn-tail into it).
Callers: exactly FUN_0003e6e0 (AI/local turn tail) and FUN_00049c14.
Prologue does three things every call: zero [ship+0x9c]; POWER refill
[+0x88] := FUN_0004a99c(); slot-refresh loop (cidx -> design word
0x7654e+cidx*0x6a into slot+1). S21's "POW frozen" is EXPLAINED: the burn
happens mid-turn elsewhere and the refill restores it before the autosave
row — first-row sampling cannot see the dip.

L1 LANE MARCH IS A CHORD-ADVANCE [verified disasm 0x4a7a6..0x4a8af]:
  guard byte[ship+0x58]==5; handle H := dword[ship+0x59] (kind-5 order
  target = LANE-RECORD pointer; NB t188's S21 "+0x52 route handle" is
  SUPERSEDED — +0x52 is the ETA day-stamp per aicode t101, ETAs differ
  between lanes trivially; the +0x59 pointer is what the law reads);
  A := ptr[H], B := ptr[H+4] (two endpoint objects, star-rec layout
  +8/+c/+10 f32); lane_len = |A - B| (FUN_00076da0 after explicit dot);
  step0 = float(int32[ship+0x8] + int32[ship+0xc]);
  (gate 1) if byte[H+0x23] bit0: step *= moffs 0x263b (relocated operand
  in the save copy = 0x24463b; pool word = operand+0x88 LIVE 0.333333 —
  THE DIVISOR BELONGS TO THE HANDLE GATE);
  (gate 2) species row idx = (dword[ship+0x54]>>16) into stride-0x1ee
  table (relocated base 0x254fb3 = DAT_00012fb3+seg): iff col byte 0x12
  == 0x12: step = max(step,1.0); step *= moffs 0x263f (relocated
  0x24463f; pool word LIVE 2.000000 — the species gate is a DOUBLE);
  x := min(x + step, lane_len) at [ship+0x9e] (FADD then clamp MOV);
  y/z untouched (S21's pure-x law = structural, not coincidental).
L2 BASE LAW MEASURED EXACT (r1_t189_lawcheck.py): every consecutive-turn
  st5 delta equals float([+8]+[+0xc]) or that value x 0.333333(3) —
  BASE-LAW-EXACT tags on all lanes with handles outside
  0x258933/0x2589cf/0x2589f6; every delta under those three handles is the
  1/3 ratio (63+186+5 slow pairs, ZERO fast pairs; 15 other handles all
  fast, ZERO slow). Ship words measured (+8,+0xc) = (14,0) or (0,28):
  S21's 14 and 28 ARE THESE RECORD FIELDS, not derived from MOVES/drive.
  Slot13 (handle 0x25820a, FAST 14.0) vs slot17 (0x2589cf, SLOW 4.6667)
  are BOTH owner-1 ships with byte-identical records at 0x00..0x27 —
  species alone cannot gate; the handle is the discriminator in play.
  Lane-end behavior: x saturates at lane_len (slot13 saturating ~224 = L
  computed from that lane's endpoint pair) — S21 item 5 confirmed.
L3 BOTH MULTIPLIERS ARE RUNTIME CONSTS, MEASURED LIVE: save-linear pool
  word = relocated operand + 0x88 (t183 law; control 32.0 verbatim at
  0x24468b = 0x2603+0x242000+0x88); in ALL 20 SAVES 41..60: 0x263b word =
  0.333333, 0x263f word = 2.000000. ASSIGNMENT BY CONSTRUCTION: operand
  0x24463b sits in the byte[H+0x23] branch, 0x24463f in the species branch
  -- handle gate is x1/3, species gate is x2. CONSISTENT with the corpus
  (slow steps are handle-keyed). Gate-2's max(step,1) clamp matches the
  0x3f800000 store bytes at 0x4a87c.
L4 GATE ATTRIBUTION NOT SEPARATED (honest): gate 1 (handle byte) vs gate 2
  (species col) — corpus confound: every SLOW window also had its handle
  change (re-order) or owner-1 status at the boundary; the ONLY save set
  (41..60) is POST ring-rotation (new game t=0 overwrote the old world), so
  live values of byte[H+0x23] and the species col cannot be read for any
  old-game lane. In 41..60 the species col byte == 0 for rows 0..23, but
  those saves cannot prove that column was ever live, so the zero is NOT
  evidence gate 2 is dead. WHAT IS PINNED: the divisor word (pool slot
  0x263f, live 1/3), the two gate FORMS with cited bytes, and step0's
  record fields. RESIDUE: which gate fires in play + what byte[H+0x23] /
  col 0x12 mean (lane-class flag vs species-table semantic id) — needs ONE
  watcher run that also dumps the handle window (ptr+0x20..+0x28) while a
  known ship marches.
L5 THE x2 (species) GATE HAS NEVER BEEN SEEN FIRING: no old-corpus delta
  equals 2*step0 where step0 came from a single record pair (t187's "56"
  rows pair with record (0,28) directly at 2x-gap artifacts). UNVERIFIED
  whether any shipped species row hits col 0x12 == 0x12.
L6 ATTRIBUTION UPGRADE (still not separation-grade): with gate1 pinned as
  the x1/3 handle gate, the SLOW-handle corpus (0x258933/cf/f6 x 254 pairs,
  zero fast) plus slot13-fast/slot17-slow same-owner is now consistent with
  gate 1 ALONE explaining every observed slow row; gate 2 has NO observed
  witness. The remaining doubt is only whether byte[H+0x23] also varies
  within the three slow handles mid-march (unreadable post-rotation).
CORPUS CAVEAT: 41..60.sav handle bytes read at 0x258xxx are dead old-game
  residue in new-game saves — never cite them as lane state.

## S23 — t190 LANE-RECORD STRUCT CLOSED; byte+0x23 bit0 = BRIDGE-LANE MARKER

Tools: Ghidra disasm verbatim (ascend_restored.bin) + scripts/
r1_t190_lane_pool.py RC=0 over 20/20 saves (dump work/r1/t190_pool_dump.txt).
Working detail: docs/re/_wip_t190.md F1..F11.

L1 LANE RECORD == 39-BYTE POOL RECORD [verified disasm + live save]
  Pool base = data-segment + 0x3337 (0x248a1 `LEA EDX,[ECX+0x3337]`,
  ECX=data base — see F9: every "scenario object" offset folds onto the
  obj0 DATA SEGMENT; S+0x49c1 == folded DAT_00045beb region, S+0x2ea ==
  DAT_00012fb3 species table, exact). Member form: B + 0x82bb0 + 0x16147;
  physical 0x258147 in saves 41..60 (run base B=0x1bf4d8).
  rec+0x00 u32 star-A OBJECT ptr, rec+0x04 u32 star-B obj ptr
  (allocator writes 0x248af/0x248b1 verbatim); rec+0x08..+0x1c f32[6] =
  B-A then A-B negates (FUN_00021ad8 fill); rec+0x20 u8 ZEROED at alloc
  (0x248ab); rec+0x23 u8 the gate byte (NEVER initialized); stride 0x27
  (IMUL chain 0x24895..0x248a7). Cap guard 0x2485f `CMP EBX,0x94` = 148;
  lane count u16 = data+0x49c3 (image 0x177D3), star count u16 image 0x16145.
  LIVE PROOF: rec[0]/rec[4] congruent to star-table base (B+0x82bb0+
  0x13bc5-0x88, stride 96): rec0.b idx 39.0, rec1 29.0, rec2 27.0, rec3
  16.0, rec4 37.0 — all integral, 20/20 saves (58 recs each).
  t189 handle congruence: old-game fast 0x25820a and slow 0x258933/9cf/9f6
  are ALL pool-congruent mod 39 (deltas to 0x258147 = 39x{5,52,56,57};
  pairwise +47/+51/+52). Handle == lane-record pointer CONFIRMED. (Old
  absolute idx [inferred]: slow handles lie fast+47..+52; with the old map
  50-star the NN prefix is ~50 recs => the +51/+52 handles ARE bridge recs.)

L2 PRODUCER CHAIN (FUN_000234a4 = scenario map-build pipeline):
  FUN_0002351c (from loader FUN_00020fd4 + turn loop 0x24f24 re-run):
  zeroes the 100x100 matrix at data+0x32ddb, loads AUTHORED 39-byte lane
  records from the SAME pool base (piVar13 = S+0x3335+2; count image
  0x177D1 — 0 in random-map new games), sets matrix pair=1 both dirs, then
  BFS-fills SHORTEST-PATH HOP COUNTS 2,3,... (0xFF unreachable). t52's
  raw-sample oddities (diagonal not 1, 79x 0xFF, 1192 asymmetric) = wrong
  base window over this buffer; BUFFER IDENTITY QUESTION CLOSED (one matrix;
  0x45beb folded == data+0x32ddb == the 0x41b03 consumer buffer).
  FUN_00023e00 (nearest-neighbour phase): per star picks nearest star with
  matrix==0, calls FUN_00021ad8->FUN_00024834 (alloc + symmetric matrix set)
  — this creator NEVER touches byte+0x23.
  FUN_00024018/FUN_0002446c (bridge phase, looped while components>1):
  per star-GROUP (S+0x30701 stride 0x19e, centroid f32[3] at +0x192) picks
  nearest star PAIR with matrix==0 across components, creates the lane and
  at 0x247f7 `OR byte ptr [ESI+0x23], 0x1` (bytes 804e2301) — the ONLY
  writer of bit0 image-wide (instruction census '0x23], 0x': writer set =
  {0x247f7 OR 0x1}; no site ever clears bit0 => a flagged lane stays
  1/3-speed forever).

L3 byte[H+0x23] bit0 SEMANTICS CLOSED WITH MEASUREMENT (S22 L4/L6):
  New-game live census (both pipelines ran at scenario init): nlanes=58,
  +0x23 == {0x00: recs idx 0..49, 0x01: recs idx 50..57} in ALL 20 SAVES
  EXACTLY; matrix off-diagonal one-pairs = 58 = lane count; star count 50.
  The flag is precisely the NN-phase / BRIDGE-phase split: bit0 = "lane
  added by the connectivity-bridge phase, not a real (authored/NN) starlane".
  The march gate 0x4a842 (x moffs 0x263b = LIVE 0.333333, t189) therefore
  slows BRIDGE lanes to 1/3 — gameplay-coherent (long filler links are slow)
  and it EXPLAINS the t189 corpus entirely: slow handles were the bridge
  recs (L1 congruence), fast the NN recs; slot13-fast/slot17-same-owner-
  slow needs no species difference at all.
  bit1 of the same byte is magnetron territory: writers 0x4cbfd AND 0xfd /
  0x4cc0e OR 0x2 (FUN_0004ca50), readers TEST bit0x2 at 0x41b42, 0x49a21,
  0x1d621 — NOT re-derived here, attribution only (t185 chain).

L4 GATE 2 (species col 0x12 -> x2) NEGATIVE MEASUREMENT STRENGTHENED:
  table image 0x12fb3 stride 0x1ee (0x4a867 `CMP byte ptr [EAX*2+0x12fb3],
  0x12`), rows 0..23, col byte +0x12: values {0 x17, 27, 38, 40, 110, 115,
  116, 172} — NO row equals 0x12 in ANY of the 20 LIVE new-game tables
  (t189's zero could not exclude dead residue; this one is live scenario
  data). x2 branch has zero shipped-campaign witnesses in this scenario;
  non-claim: cannot generalize to all vendor scenarios.

L5 t191 CLOSED (was UNEXPLAINED SIDE-FOUND): lane rec+0x20 = PER-EMPIRE
  LANE-VISIBILITY MASK (bit e = 1<<empire-index). Cited writers:
  0x273ca (nougat.lf 'l' cheat: OR 1<<[0x7458e] over all lanes — debugflags.md
  t191 scancode cascade ECX==0x26), 0x463eb/0x46421 (normal-play SHARE loop
  in function 0x46354: masks DL=1<<byte[ECX], DH=1<<species-table byte
  [0x12e16+2*idx], gated by a count arg — grant semantics INFERRED, flagged),
  0x22074/0x22e60/0x22f28 (base = [reg+0x2c+4*i] pointer arrays walked off
  species rows stride 0x1ee — shape says same mask concept on related
  structs; lane-pool identity of these bases NOT proven, flagged).
  Reader = the lane-paint path itself: loop 0x25aa2..0x25b6d copies
  rec+0x20/+0x21/+0x23 into the painter 0x20c48 record (stride 0x27, pool
  base data+0x3337). NO CLEAR SITE against the lane-pool addressing form
  (pool imm 0x16147 / base+0x3337, stride 0x27) exists image-wide (t191
  census over 88/89/c6/c7/81/83 disp8 stores); pool-create zero 0x248ab is
  the only lane-pool-scoped clear => reveal sticky, matching the player
  testimony. CAVEAT: 0x22e60 clears +0x20 via [reg+0x2c+4*i] pointer arrays
  (identity to lane recs UNPROVEN); 0x30b95 zeros +0x20 of the SHIP record
  (sets ship+0x59=0xffff — different struct, not a lane clear).
  rec+0x24..0x26 tail still unwritten by any cited site.

L6 t192 CLOSED (was L5 "semantics INFERRED / base structs UNPROVEN"):
FUN_00046354 = MUTUAL LANE-VISION SHARE between two empires, and the
0x22074/0x22e60/0x22f28 group walks PER-RACE LANE-POINTER LISTS.
  __regparm3: EAX = diplo row base (image 0x12e16 + 0x1ee*idx -- the law
  reads [row+0x1c0+target] state bytes and [row+0x1b2+2*target] attitudes,
  docs/re/diplomacy.md S7), EDX = OTHER empire's row index, EBX = mode flag.
  0x46367/0x46370 state = byte[row1 + 0x1c0 + p2]; if == 3 (ALLIANCE,
  diplomacy.md S16.3) the RNG modulus is 6 else 3 => N = rand%(3|6)+1 GRANTS
  PER CALL (0x4638f..0x46395). ALLIANCE DOUBLES THE LANE-SHARE BUDGET.
  PARTY-1 MASK 0x46399..0x4639d DH = 1 << byte[row1 + 0x00] (row's OWN empire
  index); PARTY-2 MASK 0x463a2..0x463c3 DL = 1 << byte[0x12e16 + 0x1ee*p2].
  t191's "[0x12e16] = species lanes-shared-at-contact COLUMN" hypothesis is
  DEAD: 0x12e16 is the diplo-row table BASE and the byte is that row's empire
  index (verified 60.sav: rows 0..4 hold empire idx 0,1,2,3,4).
  LOOP 0x463d0..0x46424 over word[0x177d3] lanes at 0x16147 + 0x27*i:
  dispatch 0x46402 tests the INCOMING EBX (stored 0x4635f before EBX is zeroed
  -- the decompiler conflates it with its counter reuse; raw listing governs):
    EBX != 0 (receive-only): if rec+0x20 & DL and not rec+0x20 & DH and EBX<N
      -> 0x463eb OR rec+0x20, DH   (party-1 RECEIVES a lane party-2 sees)
    EBX == 0 (bidirectional): the same test mirrored at 0x46408/0x4641c
      -> 0x46421 OR rec+0x20, DL   (party-1 LENDS a lane to party-2)
  Both counters are per-call (stack), grants are OR-only.
  CALLERS (get_xrefs_to; get_function_callers returns 0 -- t191 caveat):
    0x45778 EBX=0 BIDIRECTIONAL, inside the alliance-formation handler
      (same block chain writes row+0x1c0 state 0x45722 and the +10/+5 attitude
      bumps 0x4577d/0x4578a) => lane share fires WHEN AN ALLIANCE IS MADE.
    0x55f6e EBX=-1 RECEIVE-ONLY, inside the per-race event loop 0x55f1b..0x55f2e
      (bound word[0x13b98]), party-1 = current player row ([0x7458e] set up
      0x55f35/0x55f55) => the PLAYER receives lanes from each race in turn.
  STAR TWIN FUN_00046524 (same shape): base LAB_00013bc5 stride 0x60, count
    u16 0x16145, mask pair bytes +0x16/+0x17, modulus 4 if state==3 else 2.
  MEASURED (scripts/r1_t192_share_mask_scan.py rev2, 20/20 new-game saves):
    per-race lane list = [dword(0x12e1d + 0x1ee*r) + 0x2c + 4*i], i <
    u16[sub+0x44]; 220 pointers, 220 lane-pool congruent (mod 39 == 0), ZERO
    star-slot, ZERO other => leg (b) base structs ARE lane-pool records.
    race r's list == EXACTLY {lanes with rec+0x20 == 1<<r}: 100 of 100
    race-lists across the 20 saves, 0 disagreements (60.sav race1 -> lanes
    14/54/56, masks 0x2/0x2/0x2, bridge bit +0x23 0x0/0x1/0x1).
    pool +0x20 census over 20 saves x 58 lanes: {0:940, 1:40, 2:60, 4:40,
    8:40, 16:40} -- ALL single-bit => in a fresh campaign NO lane is visible
    to two empires: the 0x46354 share path has ZERO witnesses in the
    new-game corpus (honest negative; needs a mid-game/alliance save).
    PAIRED MASK BYTE: member B+0x82bb0+0x6774 == 1<<[0x7458e] in 20/20 saves
    (payload bytes 0x21aa6 = 88 15 74 67 00 00 = mov byte [0x6774],DL --
    Ghidra's restored-image DAT_00089324 IS payload 0x6774; reading
    B+0x82bb0+0x89324 double-offsets and is meaningless). Corroboration is
    WEAK by construction: [0x7458e] == 0 in 20/20 new-game saves, so only
    the idx=0 case is witnessed. Spectator branch writes DL=0xff (0x21a94).
  STICKINESS CAVEAT ON t191's "NO CLEAR IMAGE-WIDE" (now CONDITIONAL):
  0x22e60 DOES clear rec+0x20 (and both endpoint stars' +0x16) for every lane
  in a race's list -- the clear exists but is only reachable through
  FUN_00022ce4 <- FUN_000226e4, whose 4 callers are 0x2271e/0x22878-path,
  FUN_00020fd4 x2, FUN_00024f24 (0x24f8f, the new-game/galaxy builder region
  -- the call sits between RNG setup and the authored-lane loader 0x2351c)
  and 0x52cb6 (adjacent to the [0x7458e] new-game reset 0x52cc6). All four
  read as SETUP paths; whether any fires during play is UNMEASURED (the ring
  no longer holds mid-game states). t191's stickiness law therefore holds for
  the CHEAT and SHARE paths (0x273ca / 0x463eb / 0x46421 have no inverse),
  which is what the player testimony observed.

L7 t193 MEASURED (mid-game witnesses; supersedes the L6 new-game negative):
  THE SHARE PATH HAS FIRED — rec+0x20 IS A LIVE MULTI-BIT PER-EMPIRE MASK.
  Corpus: the Oct-29 12:30..13:03 LIVE sitting (user played; shared timeline
  grew 5,702,731,088 -> 5,721,578,066 B; all 20 save/*.sav re-written, game
  at t=1086 wall-clock save cadence; 4 empires Chamachies(player, idx0)/
  Orfa/Ungooma/Minions, states peace x5 + war Chamachies<->Minions, no
  state-3 cell in the captured rows). Probe scripts/r1_t193_midgame_witness.py
  (addresses/PTR2OFF law identical to r1_t192_share_mask_scan.py rev2):
    pool +0x20 census (20 saves x 58 lanes = 1160 recs):
      {1:160, 3:80, 6:180, 7:220, 11:260, 15:260} -- ZERO zeros, 100/1160
      MULTI-BIT. 11=0b1011 (player+Orfa+Minions), 15=all four, 6=bits1+2
      (no player bit: AI-only-visible lanes EXIST). Per-empire lane FOG:
      bit0 visible 49/fogged 9; bit1 50/8; bit2 33/25; bit3 26/32 -- every
      empire holds fogged lanes mid-game; the player's fog is the SHALLOWEST
      [inferred: AI<->AI sharing outpaces AI->player at this attitude
      profile]. Star twin +0x16 {1:160,6:180,7:160,11:240,15:260} /
      +0x17 {1:260,6:240,7:180,11:220,15:100} (byte views of the u16 pair):
      FUN_00046524 share witnesses TOO.
    MASK STATIC across the whole sitting: md5 of the 58-byte +0x20 vector =
    4ca8c5c6 and of +0x21 = 99522cd0 in 20/20 saves -- no grant fired during
    the captured window (consistent with the t192 caller law: bidirectional
    grants fire at ALLIANCE formation 0x45778 and the receive leg 0x55f6e at
    race-event boundaries; no state-3 transition inside the window).
    t192's LIST=={mask==1<<r} LAW IS SUPERSEDED (0 ok / 80 bad mid-game):
    [sub+0x2c] lists hold exactly 2 lanes per race (r0 25,50 / r1 27,55 /
    r2 18,54 / r3 2,57 -- all four second entries are t190 BRIDGE lanes
    50..57), every list a STRICT SUBSET of the nonzero-mask pool. RE-READ:
    the per-race list is the race's OWN claimed lanes, not the visibility
    mirror; t192's 100/100 equality was a new-game artifact (own lanes ==
    only reveals).
    rec+0x21 NOT all-zero mid-game: {0:720, 1:440}. Pairs (mask,b21):
    (1,1)x8 (3,1)x4 (6,0)x9 (7,0)x11 (11,0)x3 (11,1)x10 (15,0)x13 -- mask 11
    occurs with BOTH b21 values => b21 is NOT a function of +0x20; semantics
    and writer still OPEN (t191 flag stands).
  L8 t193 STATIC (leg a): the t191 "lane-paint loop 0x25aa2..0x25b6d ->
  painter 0x20c48" LABEL IS DEAD. FUN_00020c48 decompiles to an ALLOCATION
  wrapper (stack-link walk, FUN_00077b40 alloc, 0x20c84 continuation,
  FUN_00077b47 free) -- not a painter. The cited loop sits in FUN_00025604,
  a GAME-STATE SNAPSHOT writer: it serialises the lane pool (data+0x3337
  stride 0x27, fields rec+8..+0x23 incl. +0x20/+0x21 u16/+0x23 u32 and
  endpoint obj *rec+2>>0x10), diplo rows (stride 0x1ee, 100 dwords + tail
  +0x192), star refs, count words 0x49c3/0x32dd1/0x3067b -- save/AI-scan
  shape, not drawing. Consequence: the CONSUMER that would HIDE a fogged
  lane is STILL UNMAPPED. Instruction-wide census (Ghidra
  search_instructions, 98,819 scanned): TEST byte [reg+0x20],imm = 4 hits
  (0x80cc8/0x80cdf/0x80d1b/0x80d37, EBP-frame runtime region); CMP *0x20],imm
  = 18 hits, NONE on lane-pool addressing (0x7a11e CMP byte [EAX+0x20],DL is
  the vprintf engine). The mask is consumed via regpair/shift forms not yet
  enumerated. Fog-of-war EXISTENCE in the UI therefore remains UNPROVEN --
  but the mask is now PROVEN live per-empire game data with real fog bits
  (above), which the rewrite does not model at all: ledger row OQ-026
  visibility layer OPENED; abilities.md L40/L52 parentheticals "no fog of
  war (UI draws every star)" REPLACED with the measured mask facts +
  UNPROVEN-consumer status (GOAL.txt: a false justification must not stand
  as the cited reason; the FILED NO-OP disposition stands pending OQ-026).
L9 t194 STATIC+RAM (CONSUMER MAPPED — supersedes L8's "consumer UNMAPPED" and
  retires its regpair/shift enumeration plan): THE LANE-VISIBILITY FILTER IS
  THE COSMOS LIST BUILDER ITSELF. FUN_00028fc0 (decompiled verbatim) builds
  the cosmos display list (obj+0xb3 entries base, stride 0x15, entry {ptr,
  kind u8 @+4}, count obj+0xb7, cap obj+0xb9, FUN_0002a428 grow). Its lane
  loop (bound word [0x177d3]=nlanes): entry admitted IFF
  `byte[lane_pool 0x16147 + 0x27*i + 0x20] & DAT_00089324 != 0`, kind=1 —
  a lane without the viewer bit gets NO ENTRY => never drawn (FUN_000284bc
  iterates exactly this list: kind 0 star sprite, kind 1 lane line via both
  endpoint stars, kind 2 encounter), never clickable. All 5 call sites of
  FUN_00028fc0 (0x26f67, 0x273df, 0x27454, 0x2758e, 0x2771c) are cosmos
  repaints in the t191 cascade => filter applies to EVERY repaint.
  VIEWER MASK LAW (0x89324, image segment): exactly one writer
  FUN_00021a84 (0x21aa6 `MOV byte [0x89324],DL`) and exactly one reader
  (0x2914e, the filter) — instruction census agrees with xrefs (2 refs).
  FUN_00021a84(idx): mask = (idx==0xff ? 0xff : 1<<(idx&0x1f)); ALSO sets
  DAT_0007458e = idx — THE t193 X_CUR IS THE VIEWER INDEX (t192(c) weak
  witness mask==1<<[0x7458e] EXPLAINED: same setter). Callers: boot 0x21408
  in FUN_00020fd4 (init/bootstrap; arg value [unverified] — regparm loss)
  and 0x2754f (cosmos cascade debug species-toggle: AL=[ESP+0x2c]-4 bounded
  by dword[0x13b96]>>16==nraces, or 0xff = reveal-everything viewer).
  STAR SIDE: stars are ALWAYS listed/drawn (builder kind-0 adds un-
  conditionally; the star+0x16/+0x17 masks are NOT consumed there), but
  FUN_00028e70 (cosmos star-click handler) gates INTERACTION: select needs
  star+0x17 & DAT_00006774, lane-follow needs star+0x16 & DAT_00006774 —
  DAT_00006774 == the t192(c) data-segment paired mask byte (0x82bb0+0x6774):
  same viewer mask seen from the data seg. Invisible star = unselectable.
  LIVE WITNESS (Oct-29 mid-game saves 20/20, scripts/r1_t194_viewer_mask_
  witness.py): runtime mask byte at B+0x89324 == 0x01 (race-0 Chamachies),
  X_CUR == 0, law mask==(xcur==0xff?0xff:1<<xcur) 20/20 (weak: idx==0),
  filter admits 49/58 lanes => 9 AI-only lanes (census value 6 = 180/20 per
  save, the only bit-0-free value) WERE BEING WITHHELD from the cosmos
  window during real play. OQ-026 ANSWERED AFFIRMATIVE: the UI withholds
  fogged LANES (draw+click) and gates fogged STARS (click); closure route is
  now rewrite-side implement+pin, NOT more RE (abilities.md SA_KnowHomeWorlds
  / SA_KnowStarLanes: real effects exist -> the FILED NO-OP disposition must
  be revisited when the rewrite models the layer).
L10 t195 REWRITE SURFACE LANDED (OQ-026 CLOSED — implement+pin, the row's own
  closure bar): rewrite/src/game/campaign.{h,cpp} models the layer 1:1 with
  the cited fields — laneVis_ (rec+0x20), starLaneVis_/starSelVis_ (obj
  +0x16/+0x17; kept SEPARATE because the t193 censuses of the twin bytes
  differ, so they are not one value), viewerMaskFor() == FUN_00021a84 law
  verbatim, laneVisibleTo/cosmosLanesFor == the 0x2914e filter over pool
  order, cosmosStarsFor == unconditional (L9 honest negative pinned),
  shareLaneVision == FUN_00046354 shape (N=rand%(3|6)+1, receive prefix leg
  + mirrored lend leg, OR-only), shareStarVision == FUN_00046524 twin
  (modulus 4|2). Fire sites: BIDIRECTIONAL at alliance formation (cited
  caller 0x45778, wired in diplomacyPhase's ProposeAlliance branch);
  RECEIVE-ONLY one-shot per empire pair on first lane-adjacency contact
  (cited shape 0x55f6e; rewrite-site [documented default]). Seeds: an empire
  sees EXACTLY its own claim at init (t192 new-game law + t193 re-read);
  unowned lanes fogged for all (t193 {0:940} census). SA_KnowStarLanes =
  owner bit on EVERY lane; SA_KnowHomeWorlds = owner bits on both twin bytes
  of every alien HOME star (help.txt laws; vendor flag consumer unmapped —
  flagged [documented model]). Separate LCG stream visLcg_ (REFUTED-ROUTES
  RNG discipline: campaign rng_ untouched; gate-relevant seeds reproduce).
  PIN: TEST(campaign_visibility_law_oq026_t195) (tests/test_campaign.cpp) —
  mask law, init law, fog, spectator AND-behaviour (mask-0 lanes stay hidden
  even for 0xff: AND at 0x2914e has no spectator bypass), receive-only
  directionality, N envelope, sticky monotonicity over turns, alliance
  bidirectional share incl. star twin, both ability routes (player species +
  race token). 111 tests 0 fail; gate green. ability_probe 3m no-op count
  4->2; species.cpp kNotes rows rewritten; abilities.md §2 rows WIRED.
  Honest residues carried (row CLOSED per its own bar = implement+pin; the
  residues are documented-model flags, not open laws): the init PATH writing
  the first 1<<r bits is still unidentified; the twin's caller pairing at
  both share sites is [unverified]; AI-AI share has NO rewrite producer (the
  dip model has no AI-AI relations), so the t193 mask-6 AI-only class has no
  rewrite analog.

## S24 — t265 DRIVE-CORPUS FLIGHT-MINING RESULTS (st4 dwell law; t189 law re-confirmed; magnetron zero-census)

Corpus: the t261 production drive (:9, 2026-11-01 21:24 -> 2026-11-02 01:27,
turns 1086->1236, ~150 real turn advances; regimes A 21:24-21:37 and B
23:07-01:27 healthy, softlock window 21:38-23:06 EXCLUDED from law censuses).
Selection law: file_mtime_ns inside the epoch + dedup (file, mtime_ns) +
in_game + turn>0, bounded 420 MB tail (OOM law). Tools: scripts/
r265_st4_magnetron.py, r265_pass2.py, r265_pass3.py (output
work/r1/t265_pass3.out), KEEPER scripts/r265_keeper.py RC=0. Harness lesson:
lexicographic wall-string bucketing silently drops post-midnight ranges
("23:07:00" <= "01:59:00" is False) — bucket by mtime_ns/datetime.

1. ST4 IS A DWELL STATE AT RING GRANULARITY — the t193 premise is
   MEASURED-DEAD. 21 multi-row st4 runs that SPANNED >=1 turn advance
   (longest slot 13: t1086..t1236, 1014 autosave rows, 150 turns) have net
   displacement 0.00 and a CONSTANT order byte [+0x59] (69/133/197/101/229)
   end-to-end (pass3 section F). st4 row-level coords: 9360 samples, 100% on
   the 32-grid in x AND z, y mod 32 == 0 in ALL 6184 keeper-pass samples.
   Every big mover in the corpus is a 4<->5 frame switch (boundary classes
   (4,5,True) x60, (5,4,True) x67), NEVER st4->st4 in a healthy regime
   ((4,4,True) x6, all inside the softlock window). CONCLUSION [inferred
   from these legs]: the in-system march cannot be observed between autosave
   rows — a ship that enters st4 with a move order resolves its displacement
   and leaves st4 (or dwells at rest) within one turn boundary; the missing
   witness is NOT a matter of corpus size.
2. THE t189 LANE-STEP LAW RE-CONFIRMED ON A SECOND INDEPENDENT CORPUS, ZERO
   VIOLATIONS: consecutive-turn st5 pairs (t == pturn+1, same slot) have
   |dx| == step0 or step0/3 EXACTLY (1e-3 tol), step0 = float(u16[+0x8] +
   u16[+0xc]) read from the same window (keeper K1: 27 handle groups,
   2,400+ pairs, violations 0). The /3 branch is LANE-scoped (t190: bridge
   lanes), NOT handle-value-scoped: pure-slow handle values (0x13b, 0x209,
   ...), pure-fast (0x285, 0x31a, 0x3a8), and SIX MIXED values
   (0x301/0x302/0x34c/0x35d/0x3af/0x3fa) coexist — expected, since [+0x52]
   is the ROUTE handle which re-points per lane leg (t187 slot13: one ship,
   step 14 on lanes z=+/-1824, step 14/3 on z=544), and lane pool records
   are recycled (allocator FUN_00024834, t190). t189's "gate2 zero witnesses"
   residue is UNCHANGED (every pair landed on step0 or step0/3, so no third
   speed value exists in this corpus to attribute to gate2).
3. TURN-ATOMICITY AT SAMPLING GRANULARITY: same-turn consecutive-row st5
   x-deltas EXACTLY 0.0 in 17,595 pairs (keeper K2, zero exceptions). t187's
   "owner-1 4.67 = 14/3 THREE sub-steps?" reading is DEAD — one step per
   turn boundary; 4.6667 is the single step value (2554+ boundary pairs).
   Lane entry-x values {4.6667, 14, 42, 56, 84, 163.3333, 196, 224} are all
   exact multiples of the run's step — S21's x = k*step law corroborated.
   The 25-step apparent jump at the 23:05 relaunch is the re-drive REWIND
   (t1111 -> t1086 reload), not a flight (keeper drops non-adjacent pairs).
4. MAGNETRON ZERO-CENSUS (honest negative, now instrumented): W2 frame hunt
   (st->5, d>300u, y in [-200,0), x/z off-grid) = 0 candidates over the whole
   epoch incl. softlock windows; the stronger landing census K3b (any st4 row
   off-grid in x or z — P(false negative) < 0.1% per landing since BOTH
   jitter axes must land on-grid, 0x21f58 rng%200 law S19 T3) = 0 of 6184.
   AI ships held cidx-60 slots across 150 driven turns and never fired the
   device; no player was present. The magnetron use-site stays STATIC-CITED
   (S19 T3) with zero runtime witnesses; gizhelp's player-activation framing
   is consistent.
5. t266 FEED (bug class): the ONLY st4 mid-turn displacement in the corpus is
   slot 30 inside the softlock window (walls 21:41:44..21:54:06, d = 32/64/
   160/64 while the turn readout was FROZEN at 1255, and the t1254<->t1255
   oscillation repeats identical (dx,dy,dz) triples x3 across slots) — the
   engine ran turn-tail movement WITHOUT advancing the turn counter:
   turn-frozen-but-tail-running is a new bug-class tell.
OQ-019 STATUS: stays OPEN (strict-close). What this iteration kills is the
ROUTE ("mine st4 mid-turn displacement from autosave corpora"), not a law.
Remaining runtime residues all need an instrument finer than the 10 s ring
(runtime watchpoint class) or a human/player-driven magnetron use.

## t293 — scripted move-order capture (OQ-019 residue 1) — BUDGET SPENT, NEGATIVE
Four scratch launches on Oct-29 t1086 RESUME.GAM, Xvfb :96, own ring dir
(work/r1/t293-move-2026110{3,4}-*; production :9 pid 660167 untouched, healthy
t1150 throughout). Scripts/r293_move_session.py (drives the whole session;
compile-clean, fixes banked in-file). Full autopsy docs/re/_wip_t293.md.
MEASURED / PROVEN:
1. SCRATCH NAV ROUTE DETERMINISTIC (2/2 repro): title orange 0.679 -> click
   (318,333) Return-to-Game -> ring t1086 30 ships -> FLEET sidebar (553,184)
   diff 122420 rails 188 -> FLEET row-1 left-click (200,93) JUMPS to that
   ship's system view (diff ~113k) in ~75 s. Reusable skeleton for ANY future
   capture task.
2. ORDER MODE NEVER ARMED (3 launches, the negative): in-system orbital view,
   bright-dot candidates form a 34 px column grid [(442,346),(442,312),
   (442,278),(442,244),(374,312),(374,278)]; every left-click on them changes
   the screen ~65k px (NAVIGATES — planet detail/body view, not selection) and
   Escape unwinds back to orbital; subsequent click3 (and click, batmode
   order) at offsets: green count CONSTANT 32-34 (= baseline), ring order bytes
   (+0x58 kind etc.) NEVER move, no kind-2 ever appears (owner-0 census across
   all samples: kinds {3,4,5} only). READING [inferred]: those dots are planet/
   body art, not ship clips; ship SELECT never happened, so help.txt:1146
   "move a selected ship by clicking on a desired destination" never had a
   referent. DO NOT re-try dot-clicking in the orbital grid.
3. POPUP LAW RE-CONFIRMED (t245 serialize): EVENTWIN "Construction of
   Industrial Megacity complete on Cornucob I" (vision-verified bbox
   [83,118,417,362]; windows.txt VERBATIM EVENTWIN 60,100-395,355,
   EVENTBUTTON0 70,320-180,345, EVENTBUTTON1 275,320-385,345, both
   SENDMESSAGE 50) swallowed End-Turn presses 2-3 in L3: OK clicks at the
   windows.txt button centre did NOTHING (pre/post popup diff 204 then 0).
   selfplay.md law stands: synthetic Button1 on popups is unreliable — close
   with key Escape (script now does; verify title guard first, t285).
4. VERDICT INSTRUMENT (reusable law): a ring mover is a flight witness ONLY if
   the ORDER-ISSUED slot itself moved (order_bytes delta logged at issue time);
   constant-kind constant-budget dx == t189 lane step {28,14,4.6667} is
   background lane traffic ordered long before the session — a t293 L2 spurious
   POSITIVE on exactly that pattern is retracted. Bonus honest observation:
   L3 witnessed slot 8 kind 5->4 with position snap t1086->t1087 — a travel
   order CONSUMED INTO in-system on arrival, live, matching static
   0x220a8->0x21f58 (corroborates existing law, closes nothing new).
5. TURNS: press 1 from the (near-clean) map advanced 1086->1087 in 7-14 s
   both runs. L4 press 2 was in flight when the HARNESS 420 s foreground cap
   killed the session (no verdict; scratch reaped, kill-by-recorded-PID path
   confirmed dead). FOREGROUND CAP LAW: a full t293-class session is ~9-12 min
   > 420 s foreground max — next capture must run background=true notify=true.
OQ-019 STATUS t293: residue (1) STAYS OPEN (strict-close — no flight witnessed,
no order issued). Scripted-capture route is NOT refuted (the route rode
flawlessly; the SELECTION step is the unsolved sub-problem), but its 3-launch
budget is spent; any re-ask needs a NEW selection choreography candidate (e.g.
FLEET row RIGHT-click contents menu, or ship-window button) banked first.


---

## S24 t296 (2026-11-04) — SHIP-SELECTION CHOREOGRAPHY, STATIC (OQ-019 r1 gate)
Full evidence + verification pass: docs/re/_wip_t296.md (S1..S9). Every block
below was re-dumped verbatim from work/t91_code_disasm.txt (140,824 lines,
0x14bb0..0x826a5) in an independent pass.

SELECTION PREDICATE (BatModeWnd handler 0x1aef8, msg 0x53 leg 0x1b6f6..0x1b737
AND the mouse msg-4 leg 0x1b9f4..0x1ba40 — same four gates twice):
  G1 CLIP EXISTS: the ship has an entry in the window's clip list
     [win+0x1d2a] (count [win+0x1d32], stride 0x35) iff BYTE [ship+0x58] == 4
     (IN-SYSTEM) — builder 0x1d6bb `cmp BYTE PTR [ebp+0x58],0x4; jne skip`,
     entry kind := 2 @0x1d6e6, ship ptr @0x1d6e3, overflow assert
     0x2a428(ebx=0x750,edx=0x5dc). Kind 3 = planet clip, 4/6/0xff = other
     classes (0x1d745 leg, table 0x4348d stride 0xd, count WORD ds:0x43502).
  G2 KIND: cmp BYTE [clip],0x2 (0x1b6fc / 0x1b9f6) — SHIP ONLY.
  G3 OWNER: [ship+0x54]>>16 == BYTE ds:0x7458e (viewer index) @0x1b709/0x1ba16.
  G4 MOBILITY: DWORD [ship+0x88] MOVES > 0 @0x1b716/0x1ba2c.
  EFFECT: [batwin+0xb7] := 2 (0x1b71f msg-0x53 leg, 0x1ba39 mouse leg);
  selected clip gets flag BYTE [clip+0x33] |= 1 @0x1d662 iff its record ==
  ds:0x43504 (cleared for all clips on every rebuild 0x1d39c).

MODE ENUM [batwin+0xb7] (store census, all verbatim): 0 idle (0x1ad41,
0x1b114, 0x1b138, 0x1b20f, 0x1b9b4, 0x1ba5e, 0x1bafb, 0x1bf74, 0x17639),
1 ARMED (0x1b7dd, reached by msgs 0x4d/0x4e/0x4f/0x51), 2 SELECTED (0x1b71f,
0x1ba39), 3 ROUTE-DRAG (0x1b103), 4 transient/animating (0x17243).

MOUSE ROUTE IS MSG 4 (0x1b070): bounds-check ebx,edi in [win+0x8..0x14]; if
[win+0xaf] != 0 dispatch to 0x1b91c (batcon selected-object handler, in the
r1-savestate E1 list) which applies G2..G4; else mode 2 + WORD [win+0xbc]
== 0xffff -> mode := 0 (A PLAIN MAP CLICK CLEARS SELECTION), else mode := 3 +
call 0x1bd80(win, x-[win+0x8], y-[win+0xc]).

ORDER PUBLICATION: ds:0x43504 = SELECTED OBJECT (image-wide `a3 04 35 04 00`
store census = EXACTLY {0x28ec2, 0x28ef6 cosmos star-click, 0x36b01 diplomacy
row, 0x52003 ship order-target, 0x55d35}); ds:0x43508 = ORDER DESTINATION
(stores EXACTLY {0x1b5e6, 0x1baa7, 0x51a8e, 0x51fc2, 0x55bbd}). msg 0x50 leg
0x1b5ba: gate ebx >= 1 and [sel+0x58]>>16 >= ebx, then
ds:0x43508 := [sel + 0x42 + ebx*4] (the SELECTED object's own target table)
+ command-ring post 0x56ad4(0x7a35c, code 0x11) — 0x56ad4 writes 6-byte
{u16 code,u32 param} at [game+0x422c]+slot*6, slot = [game+0x44aa]>>16.
0x51a8e publishes only while DWORD ds:0x484ec > 0x96 (turn gate — READING DEAD per S36: 0x484ec = last mouse X).

WHY t293 FAILED, now explained (not merely observed): the bright orbital dots
are kind-3 PLANET clips, so G2 always took the skip leg; and even a correct
ship clip in mode 2 answers a plain click by CLEARING selection. Selection is
therefore NOT the unsolved sub-problem any more; the remaining unknown is the
DESTINATION-ENTRY WIDGET that posts msg 0x50 (no widget-side poster of
immediates 0x50/0x52/0x53 found outside the batmode family: 0x53 imm-load
census = {0x15f3c batmode relay, 0x1f971, 0x3df34, 0x4b83a asserts};
0x52 = {0x1724a, 0x1762c batmode, 0x3decc}).

NO LEDGER ROW CLOSED t296 (strict-close): choreography is static-cited, the
live witnesses for OQ-016 residue 1 (nuke) and OQ-019 residue 1/3 (arrival
granularity, magnetron) still require a capture.

## S25 t297 (2026-11-04) — LIVE ORDER-WITNESS SESSION #1: NEGATIVE, with two
binding instrument corrections (full autopsy docs/re/_wip_t297.md S3).
Run work/r1/t297-order-20261104-152048 (scratch game-wp, private Xvfb :97,
production :9 verified untouched). Drive class scripts/r297_order_session.py
(subclasses the r293 session; adds full-RAM XOR byte-run diff, cluster
flood-finder, ship-record pointer scan). Turns advanced 1086->1088; NO kind-2
ship EVER appeared; no order issued. HONEST NEGATIVE, rows stay open.

CORRECTION T297-A (MEASURED, production ring 52-54.sav + scratch run, both
agree): ds:0x43504 and ds:0x43508 live at guest-phys B + 0x82bb0 + X — the
r1_slot.OFF data-segment base, like every other DAT scalar. The t296 pin sheet
(r296_selection_note.py "plain RAM at B + 0x43504") is OFF BY 0x82bb0 and
reads garbage (constant 0x1de8c031). Correct readings, production idle t=1086:
ds:0x43504 = 0x256825 NON-NULL WHILE IDLE (target bytes all zero) and
ds:0x43508 = 0x26fe77 -> 0x26f00d CHANGING WITHOUT INPUT — both globals are
written outside the selection/order path (the 0x51a8e/0x51fc2 writers t296
cited), so NEITHER is a clean standalone selection/order witness; use them
only as baseline-vs-delta pairs around a click.

CORRECTION T297-B (MEASURED): the batmode/batcon window INSTANCE is not
findable by handler-pointer scan: u32 0x1aef8 occurs ZERO times in payload and
RAM; u32 0x1b91c occurs in RAM only at 0x22cac1/0x22eb3b, whose B-relative
offsets equal their PAYLOAD FILE offsets (0x6d5e9/0x6f663) — that region is a
verbatim payload-image copy (window-class TEMPLATE table), not the live
object. [win+0xaf]/[+0xb3]/[+0xb7]/[+0xbc] remain UNPINNED in guest RAM;
t298 route = walk the template-record neighbourhood for a heap-pointing u32
(instance pointer), or title-vs-in-system RAM delta.

INSTRUMENT LAW (t293 lesson REINFORCED): the FLEET row-1 row-jump lands on the
FIRST-LISTED ship, which may fail the owner gate (this run's ring-picked
"target" was an OWNER-1 ship — the candidate filter tested kind==4 & MOVES>0
but NOT owner==0, G3 — so selection was impossible BY LAW and the battery was
dead on arrival). Destination clicks on the planet blob did nothing
observable (3340 RAM runs identical to the animation baseline band
0x4f4/0x57a/0xa4xx/0xa6xx — the ONLY idle churn). Ship-sprite targeting must
use COLOUR CLASSES (tan/gold hull R>150,G>110,B<90), exclude the top icon
strip y<112, and the target must be RING-VERIFIED owner-0 kind-4 MOVES>0
(r293.ring_mem_rows recs are keyed by TRUE ship-array index; the owner==0
filter belongs in the PICKER — fixed in r297_order_session.py same session).

NO LEDGER ROW CLOSED t297 (strict-close): OQ-016 residue 1, OQ-019 residues
1/3 stay open pending a witnessed order.

## S26 t298 (2026-11-04) — LIVE ORDER-WITNESS #2: HARNESS NEGATIVE + four
binding measurement corrections (full autopsy docs/re/_wip_t298.md).
Three launches on scratch game-wp / Xvfb :97 (scripts/r298_order_session.py):
run 1 KeyError (own), run 2 post-turn EVENTWIN swallowed every click (r293
drain is white-text-only and BLIND to EVENTWIN — LAW: after ANY turn advance
close_eventwin() before any click that must land), run 3 full clean battery
(End Turn t1086->1087, system-view route, S1-S7 click battery, End Turn x2
to t1089) with NO kind-2, NO order-region delta, NO attributable movement.
The run-3 negative does NOT refute the mouse route — the battery never saw
the target ship. MEASURED CORRECTIONS:
1. POINTER-VALUE COORDINATE LAW: values stored in RAM are GUEST-PHYSICAL;
   read target at member index value+0x88. Cross-checked against relocated
   code immediates (dumped in-RAM bytes at 0x1ba16/0x1baa7/0x1baae carry
   0x7458e+0x242000 etc.; data-segment X physical = X+0x242000 = member
   X+0x242088 = B+OFF+X — t297-A's scalar law CONFIRMED). Proof case:
   ds:0x43504 = 0x256825, and member 0x256825+0x88+0x1c reads "Icarus" —
   ds:0x43504 is the CURRENT-SYSTEM STAR record pointer while in a system
   view (a cheap system-identity oracle). t297-B's "batwin not findable via
   handler-ptr scan" used member-coordinate patterns: the PHYSICAL pattern
   (B+0x1aef8-0x88) has exactly ONE RAM hit (member 0x247978) — the zero-
   refs negative is REFUTED; the batwin instance hunt resumes with the right
   coordinate system (clip pool stride 0x35 {u8 kind, u32 phys objptr}
   found NO candidates even with correct pointers in system-view saves —
   the pool is rebuilt per-frame or lives outside the Memory member;
   selection state stays debugger territory).
2. FLEET LIST ORDER IS NOT SHIP-ARRAY ORDER (vision on run-3 23_fleet.png:
   rows = Sparrowhawk/Erebor/Erchamion/Ignatz = slots 18/7/16/22; header
   "Chamachies (14 Ships, 13 more allowed)"). The list sort law is UNKNOWN.
3. ship_array_law count (0x43489>>16 = 30) UNDERCOUNTS: named owner-0
   records exist at indices 31/32/33 (Eregion B, Ereinion B, Escutcheon B);
   14 named owner-0 records == the FLEET header count exactly. Pickers must
   scan past 30 (n>=52) — the count word is NOT the fleet census.
4. BatModeWnd CLIENT RECT x 7..465 is a HARD bound for screen finders: the
   sidebar is tan-coloured AND bright; unbounded finders return chrome
   (run-3 "sprites" (597,140),(612,259) were sidebar). With the bound, the
   Icarus view has NO ship-sized tan blob (Enterprise B was in another
   system — wrong row, per correction 2). Validated offline: the tan class
   DID find the real sprite at (48,151) in t297's 11_orbital.png (vision
   (48,148)) — the finder works, the navigation to it failed.
5. COMMAND RING (game obj B+OFF+0x7a35c, widx u16 @+0x44ac, entry stride 10
   {u16 code, u32 param, u32 extra} — 0x56ad4 writes [esi+slot*5*2+0x422c])
   churns entry0 from NON-order activity in scratch sessions ([[7,0,0]] ->
   [[1,18,1]] after an empty right-click); codes 1/3/5 small-int params are
   NOT the publish-leg 0x11/pointer shape. Ring is delta-only and NOT an
   order oracle at this granularity.
DECISION: the blind-guess mouse-launch route is spent (STATE t297/t298
"do NOT launch a third mouse session" honoured — run 3 WAS the third).
t299 = debugger witness: BPLM {0x1ba39 SELECT-success, 0x1ba5e dl==1 order
relay, 0x1baa7 PUBLISH, 0x1bad3 planet-order leg, 0x1b114 mode-2 deselect}
in the r290 poke skeleton — one launch answers whether a click EVER selects
and what the hit-test returns per pixel. NO LEDGER ROW CLOSED t298
(strict-close): OQ-016 residue 1, OQ-019 residues 1/3 stay open.

## S27 t299 (2026-11-04) — DEBUGGER LEG WITNESS: PARTIAL (harness-negative)
Runs work/r1/t299-leg-{201408,201757,202146} (scripts/r299_leg_session.py NEW,
r299_relaunch.sh; dbg build work/r1/bin/dosbox-x-dbg; production :9 untouched).
MEASURED, instrument healthy in all 3 attempts: pmode arm window won first try
(cs=0160, EIP in-image), 6 code legs armed (BPLIST confirmed), End Turn 1
landed t1086->1087, FLEET opened, row-93 jump -> Icarus system view, tan sprite
found at the VALIDATED (48,151) class, clicks sprite/planet/empty delivered —
ZERO fires at batcon/select/dl1relay/publish/planet/deselect, ZERO stops, ring
kept autosaving (game never froze). UNATTRIBUTABLE as written: every armed leg
sits BEHIND the msg-4 router 0x1b070, so zero-fires is equally consistent with
hit-test-null and with msg-4 never reaching BatModeWnd. Run 4 (armed handler
0x1aef8 + router 0x1b070 ADDED to LEGS, script patched+compiles) separates
them; NOT RUN this iteration (budget). Deliverable (iii) (batwin instance law)
also awaits a register-bearing stop. NO LEDGER ROW CLOSED (strict-close):
OQ-016 r1, OQ-019 r1/r3 stay open. INSTRUMENT LAWS BANKED (docs/re/
dosbox-debugger.md + _wip_t299.md): code-BP arming is mode-bound (GetAddress
evaluated at arm time -> arm AFTER campaign load, gate P0<=EIP<image end);
AddBreakpoint does not Activate (arm while stopped, RUN once); MEMDUMPBIN
rejects '/' in filenames (expression parser) AND uppercases the filename;
MEMDUMPBIN 0000: dumps selector-0 junk; EXEC answers WHILE RUNNING on this
build (t282's stopped-socket law extended: a reply does NOT imply stopped —
fire detection must watch the pty code-view line CS:%04X:linear:%08X).
UPDATE t299 RUN 4 (same session, same day) — RUN 4 WAS RUN, 3 attempts
(work/r1/t299-leg-20261104-205111/205500/205849), handler 0x1aef8 + router
0x1b070 ARMED with the 6 legs (8 total, BPLIST-confirmed identical x3,
control MEMDUMPBIN MATCH=True x1). Result: ZERO fires x3 on
sprite(48,151)/planet(439,331)/empty(236,200) clicks in the Icarus system
view — WHILE IN THE SAME SESSION the FLEET-button, row-jump and End-Turn
clicks all PRODUCED game effects (ring diffs 122756 / view change / t+1).
ATTRIBUTED NEGATIVE: system-view ship/map clicks NEVER EXECUTE the
batmode msg layer (handler entry, router, or any of the six legs) — the
t297 claim '0x1ba8c = MOUSE-REACHABLE order publication' is REFUTED for
synthetic clicks on these pixels. windows.txt law verified verbatim: all
click points lie INSIDE BatModeWnd 7,7-465,472 and NO child button covers
them (children all x>=479), so no child stole the clicks. Static: 0x1aef8
and 0x1b070 have ZERO E8 callsites and ZERO u32 refs in the payload image
(the only live ref is the heap member+0x88 window-instance slot). Open
disambiguation (t301): TOGGRID control-click (inside BatModeWnd, SENDMESSAGE
74) while handler armed — FIRE means msg dispatch alive but map clicks
bypass it (polled hit-test); ZERO means the 0x1aef8 handler attribution is
dead and the leg map must be re-derived from the live instance.
NO LEDGER ROW CLOSED (strict-close); OQ-016 r1, OQ-019 r1/r3 stay open.

## S28 t301 (2026-11-04) — TOGGRID CONTROL-CLICK: INVALID-CONTROL NEGATIVE +
## WINDOW-CLASS DISPATCH LAW (full detail docs/re/_wip_t301.md)
Runs work/r1/t299-leg-20261104-{213540,214042} (2 full choreographies + 1
lottery loss). The t301 control click at (572,418) ZERO-FIRED in both sessions
— but pixel census PROVES THE CONTROL INVALID: rect 557,403-587,433 is black
in the Icarus view (uniq colors=2, mean RGB~0; BatModeWnd content rect
7,7-465,472 has uniq=222), and windows.txt shows the rect is claimed by TWO
sibling windows (TOGGRID/BatModeWnd sm=74 AND TOGSHIPS/COSMOSWnd sm=58) — the
t300 "children all x>=479" note inherited that ambiguity. The disjunction was
VOID AS RUN; the t300 map-click negative stands.
DISPATCH LAW (offline, run 59.sav B=0x1bf4d8 P0=0x1bf450, + code byte-pattern
census of work payload image):
 1. Live window records enumerate via magic u32 0x12345678 (126 hits, 2 noise):
    +0x08 rect (== windows.txt VERBATIM), +0x20 NAME, +0xa7 CLASS-TABLE phys.
    COSMOSWnd 0xfd2398 table 0x247a4c; BatModeWnd 0xfdc924 table 0x2478e8;
    BatControlWnd 0xfdbebc table 0x247850; type-0 buttons (FLEET/NEXTTURN)
    0x247cb8; type-25 toggles 0x247ca0.
 2. msg dispatch = `mov ecx,[win+0xa7]; call [ecx+4]` (ff 51 04 x5;
    mov-rm-a7 x20). TABLE SLOT 1 is the universal dispatcher thunk file
    0x30d08 (phys 0x1f0158) — verified identical slot-1 in ALL sampled tables;
    zero E8 callsites to 0x30d08 (reached ONLY via the tables).
 3. Class tables (slots 0,2,3,3-shape verified as code prologues):
    COSMOS [0x26818,0x30d08,0x26b34,0x27e80,0x311b8,0x2925c];
    BATMODE [0x1abfc,0x30d08,0x1aef8,0x1d858,0x311b8,0x1e9dc];
    BTN0    [0x30ad8,0x30d08,0x336b4,0x30fb4,0x311b8,0x316f0];
    BATCTRL [0x15630,0x30d08,0x156d4,0x16420,0x311b8,0x316f0].
    Installers write the table phys as imm32 into +0xa7 (batmode img+0x1abe6/
    0x1ac21 static placeholder 0x58 -> RAM +P0; cosmos img+0x2683f).
 4. CONSEQUENCE: t299/t300/t301 armed NEITHER slot-1 NOR the active class's
    slots — zero-fires were an ATTRIBUTION FAILURE, not a bypass law. The
    clicks that WORKED (FLEET/NEXTTURN, type-0 class 0x247cb8) ran legs nobody
    armed. Icarus-view dispatching window is one of {COSMOSWnd, BatModeWnd,
    BatControlWnd} (vision: 'Scientist Takeover' panel = battle chrome) — the
    router stop + record-NAME adjudicates.
SCRIPT: r299_leg_session.py RE-ARMED (LEGS router/cos_*/btn_*/batmode_dead;
bank_stop dumps 48-byte record head -> stop NAMES the window; --control-click
default 0; MEMDUMPBIN control at router). NEXT = one debugger run, then the
selection/order witness on whichever class the stops name. NO LEDGER ROW
CLOSED (strict-close); OQ-016 r1, OQ-019 r1/r3 stay open.

## S29 t302 (2026-11-05) — CLASS-DISPATCH LIVE WITNESS: DISPATCH LAW
### CONFIRMED, POSITIVE CONTROL CONFIRMED, MAP-CLICK LEGS REFUTED
Run work/r1/t299-leg-20261105-004605 (rc=0, 3 stops; full narrative
docs/re/_wip_t302.md S1-S5). MEASURED (regs verbatim in hits.json):
1. `mov ecx,[win+0xa7]; call [ecx+4]` DISPATCH LAW IS LIVE: cos_hdlr
   (COSMOS table phys 0x247a4c slot 2, file 0x26b34) stopped with
   eax=0xfd2310 window record magic 0x12345678 NAME='COSMOSWnd', esi=class
   table, edx=0x3b — a PERIODIC msg (3 samples: runs 225819, 230846, 232859
   all fire it within ~1 s of RUN, no click).
2. POSITIVE CONTROL CLOSED: End-Turn click -> btn_hdlr (type-0 table 0x247cb8
   slot 2, file 0x336b4) eax=0xfd6190 NAME='NEXTTURN' edx=0x7 == windows.txt
   NEXTTURN `SENDMESSAGE 7` VERBATIM. Working synthetic clicks DO execute the
   class msg layer => t299/t300/t301 zero-fires were wrong-legs + a
   DETECTOR BUG (fire-line pattern never matched this build's DrawCode form
   '1E5F84 56 push esi' — bare 6-hex EIP), NOT any bypass law.
3. The End-Turn click that ADVANCED the turn (t1086->1087) also fired cos_s3
   (COSMOS slot 3, file 0x27e80) eax=esi=0xfd2310 NAME='COSMOSWnd' edx=0x0.
4. NEGATIVE (live guest, un-witnessed legs cos_entry/cos_s5/btn_entry/router/
   batmode_dead armed through the whole battery): sprite (48,151), planet
   (439,331), empty (236,200) clicks in the Icarus view fire NONE of them
   (pty fire census 0 each). Map-click entry is NOT a class-table slot hit —
   [inferred] it branches INSIDE cos_hdlr (slot 2, the only COSMOS leg that
   fires) without re-consulting the table. t303 probe: BP cos_hdlr entry +
   the five `call [ecx+4]` sites (img 0x26eda/0x30d02/0x7a7eb/0x7aa3e/0x7b020),
   census edx per click.
5. BatModeWnd stays INACTIVE in the system view for dispatch purposes
   (batmode_dead armed, zero fires; consistent with t301 S4 record-state).
INSTRUMENT LAW (this build, dosbox-x-dbg + C_HEAVY_DEBUG + MCP EXEC):
multi-stop code-BP protocol = BPDEL the fired index -> RUN -> prove liveness
by autosave growth -> BREAK -> re-arm UN-witnessed legs ONLY -> RUN (a
re-armed hot leg re-freezes the guest on the next 0x3b pump). codified in
scripts/r299_leg_session.py (witnessed set, resume_and_rearm).
NO LEDGER ROW CLOSED (strict-close): OQ-016 r1, OQ-019 r1/r3 stay open — the
map-click selection witness (which handler + what it writes) is still
uncited; this iteration names the ENTRY CLASS (COSMOSWnd) but not the
selection WRITER.

## S30 t303 (2026-11-05) — MSG-CENSUS AT THE DISPATCH ENTRY: SLOT-1 ROUTER
## LAW REFUTED; MAP-CLICK ENTRY STILL UNKNOWN (runs t299-leg-20261105-
## {015611,020416} rc=1 x2 identical, docs/re/_wip_t303.md S0-S6).
MEASURED: (1) CENSUS INSTRUMENT WORKS and never froze: per-click arm ->
click -> bank-window -> BPDEL * -> liveness cycle (scripts/r299_leg_session.py
--census, scripts/r303_relaunch.sh); MEMDUMPBIN control MATCH=True x5; autosave
cadence unbroken (zipfile 'Memory' B+OFF+0x12e10 = 1086 across 20 saves/run).
(2) WHOLE-LOG PTY CENSUS {cos_hdlr:15, disp_26eda:0, disp_30d02:0, disp_7a7eb:0,
disp_7aa3e:0, disp_7b020:0}: the msg-0x3b pump delivers to cos_hdlr (COSMOS
slot 2) WITHOUT executing ANY `call [ecx+4]` (slot-1 router) site — combined
with t302's own BPLIST log (btn_hdlr fired while router armed, silent), the
t301 S6.2 "every msg walks slot1 0x30d08" law is DEAD (REFUTED-ROUTES t303).
(3) A WORKING sprite click (48,151; 66717 px change; vision: modal "Ship
'Sparrowhawk'" Leave Orbit/Abandon/Cancel) fired NONE of the 6 armed legs in
its window: map-click entry is NEITHER cos_hdlr NOR slot-1. (4) Control
defects (instrument, not game): no close_eventwin between census clicks (t298
law re-broken — planet/empty/NEXTTURN clicks hit the modal, diffs 225/207 px);
NEXTTURN control un-witnessable with btn_hdlr unarmed. (5) Static: indexed
ff14 modrm calls ZERO; mov r32,[r32+0xa7] = 21 sites (0x14de8-0x14f14 x6
cluster); dialog strings not payload plaintext. t304 = [esp] caller-witness at
cos_hdlr stops (bank_stop PATCHED: ret_stack.ret0 -> file offset).
NO LEDGER ROW CLOSED (strict-close): OQ-016, OQ-019 stay open.

## S31 t305 (2026-11-05) — CLICK->DISPATCH MAP MEASURED UNDER THE CORRECT CORE
Run work/r1/t299-leg-20261105-061825 (rc=0; --witness 3 --census; close_eventwin
pre-arm; FIXED fire detector FirePat, docs/re/dosbox-debugger.md t305 block;
full detail docs/re/_wip_t305.md S4-S5). Witness phase 3/3 ret0=0x21612d -> call
site file 0x56cda re-confirmed under [cpu]core=normal. Per-window per-leg fires
(whole-log census): baseline {0x56cda:15, cos_hdlr:15} msg 0x3b COSMOSWnd;
sprite(48,151) {0x56cda:2, btn_hdlr:1} banked msg 0x8 NAME='PLIND';
planet(439,331) {0x56cda:1} msg 0x8 'PLANETALLOC'; empty(236,200) {0x56c74:1}
(render-only, autosave-gap proven); NEXTTURN {0x56cda:2, btn_hdlr:1} msg 0x8
'PLSQUARE'. 20 other slot-2 sites ZERO in every window. READS: clicks dispatch
msg 0x8 to the clicked/repainted WINDOW RECORD via the same generic pump site
0x56cda; empty-map clicks route through the sibling site 0x56c74 only. The
selection-store WRITER (DAT_000482fb) remains unnamed: msg 0x8 is repaint/
dispatch, not the selection write. NO LEDGER ROW CLOSED (strict-close): OQ-019
stays open. Instrument law: FirePat regression suite = runs 033648/052925/
061825 known-fire counts (41/3/60+20+1).

## S32 t306 (2026-11-05) — BATMODE SELECTION SITES NEVER REACHED BY MAP CLICKS
Run work/r1/t299-leg-20261105-101054 (rc=0 attempt 1; --census --legs
batmode_dead,bat_router,bat_s53,bat_mouse,btn_hdlr --target-kinds sprite;
scripts/r306_relaunch.sh; full autopsy docs/re/_wip_t306.md S2-S3). FirePat
regression re-passed pre-arm (5/5 exact). MEASURED (whole-log pty census +
banked stops): working sprite click (48,151) -> btn_hdlr msg 0x8 win[esi]
NAME='PLIND', ret0 file 0x3cb8d = DIRECT E8 call 0x336b4 at file 0x3cb88 (one
of 51; enclosing fn 0x3cb00 is a window-family dispatcher with a sibling
`call [ecx+0xc]` at 0x3cb6e, u32-refs-to-entry ZERO = table-member); the four
t296 batmode sites {entry 0x1aef8, msg-4 router 0x1b070, effect 0x1b71f,
effect 0x1ba39} fired ZERO with the positive control ALIVE (btn_hdlr 2 fires
same session, census-ctl MATCH x3, liveness x2). Selection oracle pairs
(sel43510/DAT_43504/DAT_43508 before/after, census.json["oracles"]): NOTHING
attributable moved (43504 stable = Icarus star; 43508 churns without input per
t297-A). CONSISTENT with the gating fact (t=1086 owner-0 has no kind-4 ship ->
G1/G2 unpassable) but the ENTRY+ROUTER zeros are pre-gate: the map click's msg
0x8 does not walk the BatModeWnd handler layer at all. READ: batmode
static-gate route for the live selection witness is CLOSED AS A NEGATIVE; the
writer hunt re-scopes to the non-batmode members of the t296 store census
(DAT_43508 {0x51a8e stores eax gated ds:0x484ec>0x96 [mouse-X per S36] ring 0x11, 0x51fc2
stores [edx+0x59] ring 0x11, 0x55bbd} and DAT_43504 {0x28ec2, 0x28ef6 cosmos
star-click, 0x36b01 diplomacy row, 0x52003 ship order-target stores [esi+0x59]
ring 0x10, 0x55d35}) (disasm verbatim this session + S24). NEXTTURN control this run hit
the 'Cancel' record msg 0x4 via pump 0x56c74 (modal residue class, t304
pattern) — turn-advance witness stands from t305's PLSQUARE stop, no delta.
NO LEDGER ROW CLOSED (strict-close): OQ-019 selection WRITER unnamed; t306
note appended to the row.

## S33 t307 (2026-11-05) — FIRST LIVE FIRE AT A STORE-CENSUS MEMBER:
## w43504_28ec2, EAX=0x256825. Run work/r1/t299-leg-20261105-112859 (rc=0,
### attempt 1; scripts/r307_relaunch.sh; full autopsy docs/re/_wip_t307.md).
Armed the eight non-batmode t296 census legs + btn_hdlr from the GALAXY MAP
(new --star-click N: r293 enter_system pip law, screen-diff>15000 = entered,
escape ladder between clicks). PTY census: {w43504_28ec2:1, others 0,
btn_hdlr:5}. THE FIRE: HL render mcp-pty.log byte 34151, IP=E8312=P0+0x28ec2,
EAX=0256825 (Icarus star record, T298-A), between REQ 111 RUN (resume after
the star1 (238,282) click's btn_hdlr msg-4 stop; click ENTERED the system —
14_star1_screen.png vision-verified 'Icarus / Red Dwarf') and REQ 112 BREAK.
Follow-on render bytes match disasm 0x28ec7..0x28ed8 verbatim (ring post code
0x10 via 0x56ad4). Function 0x28e70 (sole caller 0x27332, COSMOS msg chain):
gates [[win+0xbb]+4]==0, [win+0x582]==0 (EMPTY clip list = fallback branch),
(ds:0x7e582>>16)==1, test [obj+0x17],ds:0x6774 -> STORE ds:0x43504=eax.
t306 REFINED: map clicks never reach BatModeWnd (stands) but DO reach the
COSMOS fallback selection writer. SELF-RELOCATION LAW (MEASURED, binding):
RAM code bytes at P0+0x28ec2 = a3 04 55 28 00 — data-segment immediates are
REBASED +0x242000 IN CODE at load (0x7a35c->0x2bc35c in the same render);
census-ctl byte-compare vs payload reads False at such legs (arms still
valid; BPLIST proves). DAT-BASE CORRECTION CANDIDATE (bytes verified,
resolution OPEN): true DAT_43504 physical = 0x285504 (B+SL.OFF-0x88+X, since
B=P0+0x88), where the scratch sav reads 0xff at idle = SELECTED-NONE fits
the semantics; the t297-A oracle address B+SL.OFF+X = 0x28558c holds the
stable Icarus star ptr (grep: ds:0x4358c has ZERO disasm refs — a DIFFERENT
variable). If confirmed, the oracle has been reading the wrong u32 and the
43504 delta test was never real. NO LEDGER ROW CLOSED (strict-close): the
fire is the STAR fallback writer, not the per-ship selection writer;
OQ-019 residue untouched; t307 note on the row.

## S34 t308 (2026-11-05) — DAT_43504 STAR WRITER FULLY WITNESSED (Icarus->Vega
### delta); DAT-BASE QUESTION CLOSED (oracle always correct: member+0x88 =
### linear); GREEN-ANNULUS pip law replaces the dead bright-dot law.
STEP 1 (offline, docs/re/_wip_t308.md S1): the sav Memory member is +0x88 off
guest LINEAR (dosbox-debugger.md t286b law re-proved directly: debugger dump
of linear 0x1e8312 == member bytes at 0x1e839a in run 112859). Oracle reads
member B+SL.OFF+X = linear mem_base(obj1)+X = EXACTLY the rebased store target
("mov [00285504],eax" == member 0x28558c). The t307 "true DAT_43504 = 0x285504
reads 0xff idle" datum is VOID (member read as if linear; linear 0x28547c is a
different variable, 0xff constant across 18 oracle reads in two runs). t297-A
needs NO restatement. Disasm: ds:0x43504 38 refs, ds:0x43508 109, ds:0x43510 3,
ds:0x4358c/0x43590 ZERO.
PIP LAW DEFECT (run t299-leg-20261105-140250, rc=0): sum(r+g,b)>380 nearest-
first picks purple UI-text fragments (all 12 "compact" clusters were
(158,81,174) at y 79-149); 5/6 clicks repaints, the 6th ENTER was Icarus
AGAIN (same-value store invisible). System pips are GREEN ANNULI of {(0,85,40),
(0,113,56),(0,142,69)} (offline census of the run's own map shot; Icarus's
annulus centroid (237,288) is 6px from its pip (238,282)). NEW LAW (patched,
run-validated): BFS 8px-link green-family clusters >=10px, centroid, drop
<50px from the known Icarus pip, nearest-first -> 23 candidates ALL distinct
systems by construction.
STEP 2 WITNESS (run t299-leg-20261105-143815 rc=0, attempt 1, same 9 legs):
click #1 (182,284) ENTERED (diff 94712); w43504_28ec2 FIRED (pty census
{28ec2:1, btn_hdlr:3, others 0}) render "E8312 A304552800 mov [00285504],eax"
register panel EAX=0x255BC5, REQ 59 RUN..REQ 60 BREAK correlated; follow-on
bytes = disasm 0x28ec7..0x28ed8 (ring post code 0x10). ORACLE PAIR:
DAT_43504 0x256825 'Icarus' -> 0x255bc5 'Vega' (name-bearing oracle, first
real delta ever). CROSS-CHECKS: 0x255bc5 = 0x255be1-0x1c = star-record base
k=0 (r1_star_table 'Vega'); 0x256825 = k=33 name-0x1c; screenshot
11_star0_screen.png vision 'Vega / White Dwarf', planets Vega I/II/III ==
star table. DAT_43508 UNCHANGED (0x26fe77) — order-destination semantics
consistent. Fire REPRODUCED 3/3 (t307 x1 same-value, t308 b1 x1 same-value,
b2 x1 delta).
READINGS: fn 0x28e70 (caller 0x27332) is THE witnessed DAT_43504 star-select
writer: entered galaxy-map click -> store clicked star-record base + ring 0x10.
Still open (strict-close, OQ-019 residue): per-SHIP selection writer (no
kind-4 owner-0 ship at t=1086) and the msg-0x50 destination widget; ring-0x10
CONSUMER family (0x55a60 incl. 0x55bbd/0x55d35) has never run inside an armed
window even across a witnessed NEXTTURN msg — consumer timing unresolved.

## S35 t309 (2026-11-05) — TWO-RING MAP: 0x55a60 IS THE RING-B POST, THE
### CONSUMER IS 0x55ae8 (SOLE PUMP SITE 0x54b74), AND THE STAR CLICK POSTS
### RING-A CODE 1 — THE t308 CLOSE-CONDITION TESTED THE WRONG RING.
Static (work/ascend_payload.bin, objdump -D windows, jump targets hand-
resolved per S1.12 law; full detail docs/re/_wip_t309.md S1):
- RING-B: post fn 0x55a60 (19 E8 sites; record {u16 edx code, u32 ebx, u32
  ecx} at [core+0x475e+code*10]; write-index WORD [core+0x475a] inc; reject
  when ([core+0x4758]>>16)==0x20). Consumer fn 0x55ae8 (gates ds:0x7a358!=-1,
  count!=0, ([core+0x4226]>>16)==1) dispatches code>>16 through a compare
  tree; code 0x10 -> cmp [esp+8],1 -> mov ds:0x43504,eax (leg w43504_55d35);
  codes 0xe-0xf arms -> mov ds:0x43508 (legs w43508_55bbd/0x55bcc). Sole E8
  caller = 0x54b74 inside fn 0x54650, gated write-index!=0 / mode==1 /
  [core+0x489e]==0; post-call 0x54b79 posts msg 0x7 when the ring drains.
- fn 0x54650 = core-state pump (called as `mov eax,0x7a35c; call` from
  exactly TWO sites: 0x217b3 in fn 0x20fd4 = MAIN GAME LOOP (its sole caller
  0x7b817 sits in program-entry trampoline 0x7b7d7), and 0x555f9 in fn 0x5558c
  = secondary loop over the same core). Pump path requires ds:0x660c==-1;
  resolver 0x55df4 case 0x55ebe CLEARS it to 0.
- RING-A: post fn 0x56ad4 (45 E8 sites; FIFO slot ([core+0x44aa]>>16) at
  +0x422c stride 10, index WORD +0x44ac inc); consumed by SHADOW-COPY+resolver
  fn 0x55df4 (called from 0x54b4a gated ([core+0x44aa]>>16)>0; memcpy 0x140B
  +0x422c->+0x436c, zero index, jmp-table 0x55e86 on code<=8 — table data is
  RAM-relocated, do not decode the file image). code>8 (incl. 0x10) -> ja
  0x56336 default = error-report path, NO DAT write.
- CORRECTION (binding): the t307/t308 star-select site 0x28ec2 posts RING-A at
  0x28ed8 with edx=ecx=1 (CODE 1) and ebx=0x10 (the u32 PARAM) — NOT ring-B
  code 0x10. RING-B code-0x10 has exactly TWO posters in the image: 0x41c17
  (fn 0x41260) and 0x499e0 (fn 0x49880), both `edx=0x10, ebx=esi,
  ecx=[esi+0x5e]`. Instrument lesson: a whole-log zero at consumer-arm legs
  0x55d35/0x55bbd cannot distinguish 'consumer never ran' from 'consumer ran,
  arm not taken' — arm the fn ENTRY (0x55ae8) too; and post-disarm execution
  is invisible to the pty census (a stop needs an armed BP) — hold windows
  must stay leg-hot (census_click(None) re-arms all legs).
### S35b t309 RUN (run t299-leg-20261105-161711 rc=0, docs/re/_wip_t309.md S3):
### RING DORMANCY MEASURED — post-fn ENTRY legs zero whole-log (ringB_post
### 0x55a60 gate-free prefix, consumer cons_entry 0x55ae8, ringA_resolver
### 0x55df4, both 0x10 posters 0x41c17/0x499e0); ringB_count/widx snapshots 0
### in EVERY window; star-click RING-A post body never ran (idx 0 throughout).
### mode4226 = VIEW ID (map 1, system 0x10 — star0_after snapshot). Witness
### delta reproduced 4th time (182,284 ENTER Vega, Icarus->Vega). btn_hdlr
### control fired msg 7 NEXTTURN (ret0 0x56cdd via pump 0x56cda) with NO ring
### involvement. WRITER INVENTORY FINAL (a3 + 89/15 whole-image): DAT_43504
### six {0x28ec2,0x28ef6,0x36b01,0x52003,0x51ac9,0x55d35}, DAT_43508 six
### {0x1b5e6,0x1baa7,0x51a8e,0x51fc2,0x55bcc,0x55bbd}; fn 0x51b68 owns three
### (densest); fns 0x51b68/0x51834 have ZERO E8 callers and ZERO u32 refs =
### table-member family — name their callers from ret_stack at a stop, not
### offline. REFUTED-ROUTES t309 amendment is binding.

## S36 t310 (2026-11-05) — THE DESTINATION WRITER'S CLASS IS STATUSWND;
## fn 0x51834 IS ITS MSG HANDLER; THE 0x1c01 GATE IS MOUSE X, NOT THE TURN.
Full evidence docs/re/_wip_t310.md S1-S5; run t299-leg-20261105-173627 rc=0.
- fn 0x51834 block map (file offsets, objdump window-relative targets
  resolved): cmp dx,2 -> jb 0x51AF3 / jbe 0x51A2A; cmp dx,0x1c01 je 0x51A67;
  default 0x51863 TAIL-CALLS btn_hdlr 0x336b4 (verified rel 0x51878-0x1e1c4).
  0x51A67 (msg 0x1c01): eax=[[win+0xab] system rec]; gate cmp ds:0x484ec,0x96:
  >0x96 -> DAT_43508=eax + RING-A post 0x11 (0x51A8E); <=0x96 -> edx =
  0x13bc5 + ([sysrec+0xa]>>16)*96 (star-record addr; +0x242000 = 0x255bc5 =
  the t308 witness value) -> DAT_43504=edx + RING-A post 0x10 (0x51AC9).
  SPAN FIX vs t309 STATE: BOTH stores are inside fn 0x51834; fn 0x51b68 is a
  star LABEL builder (string ids 0x2b13/0x2b14, format call 0x250bb) and the
  orphan blocks 0x51FB5/0x51FF6 (DAT stores of [edx+0x59]/[esi+0x59]) live
  past fn 0x51b68's ret in a further fn (add esp,0x1bc epilogue).
- GATE MEASURED 2/2: ds:0x484ec = LAST MOUSE X (0x30 after the x=48 sprite
  click, 0x1b7 after the x=439 planet click). The t296 'turn gate' reading is
  DEAD: 0x1c01's branch select is screen-X>150.
- SENDER CENSUS (whole image): mov edx,0x1c01 exactly 2x — 0x16168 (fn
  0x160xx, class-relay call [ebx+0xc]) and 0x35696 (DIGIT-KEY handler, gate
  ASCII '1'..'9', call [esi+8] on the KEY-FOCUSED window). cmp dx,0x1c01 8x
  (consumers incl. 0x51858). No push/mov-ecx/mov-eax/cmp-eax/cmp-ecx form.
- CLASS TABLE VIA RAM SCAN (the t309 route, first EXECUTION): sav Memory
  member scanned for REBASED entry ptrs — fn 0x51834+P0 exactly 1 hit (RAM
  0x248050), cos_hdlr+P0 1 hit (0x247adc), btn_hdlr+P0 4 hits; the same
  values in the FILE image: ZERO hits (relocation blindness CONFIRMED — RAM
  scan is the route, do not re-run file u32 scans for class tables). Grid at
  0x248040 {0x311b8,0x316f0,0x51630,0x30d08,0x51834,0x51680}; the constructor
  fn 0x51630 stores instance [win+0xa7]=0x5fc0 (rebased -> RAM 0x247FC0);
  refs to 0x247FC0: exactly ONE window-magic record, NAME 'STATUSWND'
  (rec 0xfd9fbc in that sav). => fn 0x51834 = STATUSWND msg handler.
- RUN RESULT (honest negative, control alive): order battery (pre-turn
  1086->1087, fleet rowjump, sprite 48x151, planet 439x331, digit keys 1..9,
  NEXTTURN) — whole-log {w43508_51a8e:0, w43508_51fc2:0, w51ac9:0,
  w43504_52003:0, s2_1616f:0, btn_hdlr:4}. Digit keys DID enter the msg
  dispatcher (stop ret0 file 0x56c77, ret1=0x31='1') but the FOCUSED window
  was the 'Cancel' popup (class slot-2 = btn_hdlr), not STATUSWND — the
  battery has no close-popup-immediately-before-keys step (defect, fixed
  route banked). fn 0x51834 never received anything on this battery.
- NEXT (t311): digit keys with STATUSWND focused — close_eventwin to bare map
  immediately before the key window (map focus is the STATUSWND candidate;
  verify by a stop at fn 0x51834 ENTRY 0x51834 with ret0 = the dispatch site
  and dx = the msg id), then the 0x1c01 path is witnessed or refuted in ONE
  run. Entry-leg 0x51834 IS the right instrument; the store legs alone cannot
  distinguish 'class never messaged' from 'msg 0x1c01 never sent'.


## S37 t311 (2026-11-05) — STATUSWND RECEIVES NO MSG TRAFFIC AT ALL ON THE
## MAP/KEY BATTERY (entry-leg measured, branch (c)); bare-map key focus =
## 'NEXTTURNCONT' button class, NOT STATUSWND.
- INSTRUMENT (new, reusable): LEGS["fn51834_entry"]=0x51834 — ENTRY of the
  STATUSWND msg handler. A BP at a fn entry fires regardless of caller
  (class-table slot, direct E8, tail-call), so entry-zero whole-log = the fn
  was NEVER entered. Put it FIRST in a legset: the census-ctl probe compares
  RAM vs FILE bytes at leg[0], and a code-entry leg matches (MATCH=True 7/7
  this run) where a store-imm leg cannot (t310 lesson).
- RUN t299-leg-20261105-182822 (rc=0, attempt 1): battery = baseline -> hold
  -> pre-turn 1086->1087 -> close_eventwin + assert_on_map on the BARE MAP ->
  digit keys 1..9 in one armed 60 s window (post-arm popup reguard) -> fleet
  rowjump -> sprite 48x151 -> planet 439x331 -> NEXTTURN -> hold. WHOLE-LOG
  {fn51834_entry:0, w43508_51a8e:0, w51ac9:0, s2_1616f:0, btn_hdlr:4}.
- THE t310 FOCUS DEFECT IS FIXED AND MEASURED FIXED: bare-map keys now hit
  btn_hdlr on window name='NEXTTURNCONT' (eax=0xfd6240, edx=0x3, ret0 file
  0x3177d) instead of the 'Cancel' popup. Datum: the key-focused window on
  the bare campaign map is a BUTTON-family class — STATUSWND never holds
  keyboard focus at the map, so the digit-key sender's call [esi+8] can
  never reach fn 0x51834 from this composition.
- CONSEQUENCE (REFUTED-ROUTES t311 amendment): "STATUSWND-focus + digit keys
  sends 0x1c01 to the destination writer" is DEAD as a live trigger. The
  destination-widget hunt moves to the ORDER-PLACEMENT choreography (t298-B:
  select ship mode 0->2, click planet clip dl==3 @0x1bad3 relay 0x326 ecx=4)
  with fn 0x51b68's TWO writer legs armed (0x52003 DAT_43504, 0x51fc2
  DAT_43508; 0x51ac9 belongs to fn 0x51834 per the t310 span fix — fn 0x51b68
  is table-member-called, name the caller from ret_stack). t306 refuted the
  BATMODE legs, not these.
- Oracle pair law re-confirmed: DAT_43504 'Icarus' constant all run,
  DAT_43508 churns 0x26fe77<->0x26f00d across autosaves with NO armed writer
  firing (writer-less churn = the t298-C datum re-observed; do not read a
  DAT_43508 delta as a witnessed store).

## S38 t312 (2026-11-05) — ORDER-PLACEMENT WRITER RUN: fn 0x51b68's
## DESTINATION-WRITER PAIR UNREACHED WHOLE-LOG (branch (b), second honest
## negative); sprite-pixel click DOES NOT SELECT (sel43510=0 x4 runs); both
## msg-0x1c01 senders proven never-firing. Full autopsy docs/re/_wip_t312.md.
- RUN t299-leg-20261105-192246 (rc=0, attempt 1, BREAK lottery won first try;
  scripts/r312_relaunch.sh NEW, zero script delta otherwise — all five legs
  already in LEGS). Battery = t298-B order shape the existing census path
  drives: baseline -> hold -> pre-turn 1086->1087 -> bare-map digit keys 1..9
  -> fleet rowjump -> sprite 48x151 -> planet 439x331 (separate armed windows)
  -> NEXTTURN -> hold. WHOLE-LOG {fn51834_entry:0, w43504_52003:0,
  w43508_51fc2:0, s2_356a5:0, btn_hdlr:4}; census-ctl MATCH=True x7 (entry
  leg[0] law).
- THE DECISIVE DATUM: sel43510 = 0 in EVERY oracle snapshot (pre/post turn,
  digit, sprite before AND after, planet before and after, nextturn) and
  mode4226 moves 0x1->0x11 only as the map->system VIEW id (t309 law). The
  t298-B choreography's first step — select ship, mode 0->2 — NEVER HAPPENS:
  the sprite click at validated (48,151) dispatches msg 0x8 to 'PLIND'
  (repaint, t305 law) and selects nothing. Measured identically in t305,
  t306, t311, t312: the sprite-pixel IS NOT A SELECTION TRIGGER in this
  game's system view (REFUTED-ROUTES t312 amendment).
- CONSEQUENCE: the two open OQ-019 residues (destination-widget fire +
  per-ship select) are ONE hole — without selection no order exists, so
  fn 0x51b68's writers {0x52003 DAT_43504, 0x51fc2 DAT_43508} stay dark and
  re-arming them against this battery shape is spent. Next route is the
  CALLER hunt, not another battery: sav class-grid RAM scan for 0x51b68+P0
  (t310 route — scan the grid slot index FIRST, then infer which table the
  game consults), or a FLEET-window selection path (keyboard/UI inside the
  fleet list, not the map pixel).
- SENDER-SCOPE FREEBIE CLOSED (negative): s2_356a5 (digit-key sender's own
  call site, 0x35696 gate ASCII 1..9) fired ZERO even though digit keys
  demonstrably reached a window (btn_hdlr 'NEXTTURNCONT' edx=0x3 stop —
  reproduced t311 datum). With s2_1616f zero (t311), NEITHER in-image sender
  of msg 0x1c01 ever fires in ANY session shape tried (t310 battery, t311
  bare-map keys, t312 order battery).
- Control/stops verbatim: digit 'NEXTTURNCONT' ret0 0x3177d ecx=0x2 edx=0x3;
  sprite 'PLIND' ret0 0x3cb8d ecx=0x97 edx=0x8; planet 'Cancel' ret0 0x56c77
  ecx=0x14b edx=0x4; nextturn 'PLSQUARE' ret0 0x3d391 ecx=0x43 edx=0x8.
  DAT_43504 'Icarus' constant; DAT_43508 churns 0x26fe77<->0x26f00d with zero
  armed writers (t298-C re-observed, 3rd time).

## S39 t313 (2026-11-05) — fn 0x51b68's WRITERS BELONG TO FLEETWND: FULL
## OFFLINE CHAIN msg-0x1c01 -> handler 0x51cc4 -> runtime state table -> DAT
## stores. Offline caller hunt EXHAUSTED at the runtime dispatch table.
Full evidence docs/re/_wip_t313.md S0-S8; zero capture, save dir of run
t299-leg-20261105-192246 (58/41/50.savs), scripts/r313_class_scan.py,
r313_name_entries.py, r313_name_b.py, r313_fleetwnd_map.py,
r313_writer_callers.py, r313_handler_chain.py.
- CLASS STRUCTURE FIXED: t310's 'grid 0x248040 slot 4' was an 8-BYTE-SHIFTED
  read. True class grids are stride-6 u32 {entry, router-fn 0x30d08, msg
  handler, slot3-fn, 0x311b8, 0x316f0}; the class ptr (stored at window rec
  +0xa7, magic 0x12345678 at rec+0x00, NAME at rec+0x20 — all re-calibrated
  verbatim on STATUSWND rec 0xfd9fbc) points at grid_base-0x88. The dispatcher
  is 0x30d37 (`mov ebp,[win+0xa7]; call [ebp+0xc]`), NOT 0x30d08 (that's the
  rect-move slot fn). FULL WINDOW CENSUS banked: 115 magic+name recs, 31 class
  ptrs incl FLEETWND cp 0x247fa8, NEWGAMEWND 0x247f90, STATUSWND 0x247fc0,
  button family 0x247cb8 (60 wins).
- fn 0x51b68 was NEVER a function entry: 0x51b64 is the entry (push
  ebx/ecx/esi/edi at 0x51b64, push ebp at 0x51b68) and 0x51b64 = FLEETWND
  grid slot 3. t310's 'orphan blocks live past fn 0x51b68's ret' SUPERSEDED.
- FLEETWND msg handler fn 0x51cc4 (frame sub esp,0x1bc; raw-verified chain):
  cmp dx,2 -> jb 0x5206f (msg 1 sub-dispatch) / jbe 0x51f0c; cmp dx,0x1c01 ->
  je 0x51f3b EXACT. Block 0x51f3b: eax=[win+0xab] (system rec), call 0x32fa4,
  ecx==5 -> confirm-popup leg 0x51f5d (string 0x2b6b); ecx!=5 -> jne 0x52059:
  al = [[win+0xab]+0x58]-1; cmp al,4; ja ret-0; jmp cs:0x3d100(,eax,4) — a
  SYSTEM-STATE jump table. RAM instance found (41/50/58.savs identical, whole-
  RAM unique): runtime-composed stub 0x211160..0x211185 + 5-entry table
  0x211188 {0x51fb5 x3, 0x51ff6, 0x52037}: states 1/2/3 -> block 0x51fb5
  (DAT_43508=esi + ring post 0x11), state 4 -> 0x51ff6 (DAT_43504=[esi+0x59] +
  post 0x10), state 5 -> 0x52037 (post 0x3, eax=-1). File bytes at 0x3d100 are
  NOT pointers (file scan blindness PROVEN again; fix-up is runtime).
- t312's dark writers explained OFFLINE: digit sender 0x356a5 `call [esi+8]`
  edx=0x1c01 hits the KEY-FOCUSED window; that focus was 'NEXTTURNCONT' (btn
  class 0x247cb8, slot-2 btn_hdlr) in every run tried, so 0x1c01 NEVER reached
  FLEETWND. FLEETWND holds its OWN 0x1c01 destination path — the STATUSWND
  route was the wrong window family all along.
- REACHABILITY CENSUS (all cited): E8 callers of 0x51cc4/0x51b64/0x51f3b/
  0x51ff6 = 0; branches into 0x52059 = {0x51f57 only}; whole-RAM u32 decoding
  into 0x51fb5..0x52058 = exactly the 5 table entries. Offline is EXHAUSTED at
  the dispatch table; the next witness must be LIVE (fn51cc4 entry leg + the
  two writer legs, FLEET-window focus composition).

## S40 t314 (2026-11-05) — FLEETWND-FOCUS LIVE TEST: FLEETWND RECEIVES NO
## MSG AT ALL; the digit-key handler is its own window family. Runs
## t299-leg-20261105-{210255 (invalid), 212402 (valid)} both rc=0;
## docs/re/_wip_t314.md S0-S7; scripts/r314_relaunch.sh + r299_leg_session.py
## --fleet-keys phase (NEW leg fn51cc4_entry = 0x51CC4).
- DRIVE LAW (run 1, measured): the fleet rowjump click (200,93) CLOSES the
  FLEET window (t253 rails detector 188 -> 0). Any phase needing FLEET-window
  focus MUST run BEFORE rowjump and MUST re-assert fleet_open at arm — the
  --fleet-keys reguard now gates on popup-closed AND rails>0 and logs rails.
- VALID TEST (run 2, rails=188 at arm, keys 1..9, no popup after): whole-log
  census {fn51cc4_entry:0, w43508_51fc2:0, w43504_52003:0, btn_hdlr:4},
  ctl MATCH=True, liveness True. FLEETWND's msg handler (armed 10x across all
  windows) NEVER fired — no msg of any kind reaches FLEETWND via keyboard
  under the FLEET sidebar shape. The t313 "one digit key away" narrative is
  REFUTED (REFUTED-ROUTES t314 amendment).
- The single fleet_keys stop: btn_hdlr win='STATSHIPLST' edx=0x3 ecx=0x2
  eax=0xfe7ac0 ret0 file 0x32943 (call [esi+8] inside STATSHIPLST's slot-2
  fn; cp 0x247c70 grid tail {0x324f4,0x30d08,0x32664} read from RAM). Key
  focus with the FLEET window open belongs to the STATSHIPLST family. CAVEAT:
  s2_356a5 not armed run 2 — sender-zero under FLEET focus is extrapolated
  from t312, not measured.
- SENDER BRANCH (objdump verbatim 0x35675..0x356a5): digit in ebx, bail if
  <0x30/>0x39; eax=9; if BYTE [ebp+0xaf]==1 eax=10; bail if eax >= ebx-0x30;
  then edx=0x1c01, esi=[ebp+0xa7], eax=ebp, ecx=0, call [esi+8]. The msg goes
  to the KEY-HANDLER'S OWN window — which window that is = t315 offline hunt
  (fn containing 0x35696 -> class grid -> magic rec).
- ACCESSOR fn 0x32fa4 (0x51f4b, also 0x51a73 STATUSWND path — 9 E8 callers):
  idx=msg arg (0..0xff bound, else fn 0x2a428), returns
  [[win]+0xc7 + idx*8]. The writer-block gate byte [eax+0x58] (0x52059: mov
  al,[eax+0x58]; dec al; cmp 4; ja ret0; jmp cs:0x3d100(,eax,4)) is a field of
  a TABLE-SELECTED record — t313's "system record" label UNPROVEN, not
  disproven. STATSHIPLST[+0x58]==0 in 40/40 saves (both runs) = rec datum;
  the gate was never evaluated live (msg never arrived). Payload-wide store
  census [r+0x58] (c6/88/89/c7 disp32) = ZERO sites: writers use computed
  offsets, file scan blind (t313 law re-confirmed on a new target).

## S41 t315 (2026-11-05) — THE DIGIT-HANDLER WINDOW IS LOADSCREEN: THE KEY
## ROUTE TO msg-0x1c01 IS A MENU MECHANISM, DEAD BY CONSTRUCTION FOR IN-GAME
## SELECT (offline, zero capture; docs/re/_wip_t315.md S0-S6 +
## scripts/r315_handler_scan.py; run dirs 212402 + 192246 saves).
- fn containing the digit sender 0x35696 = fn 0x354f8 (prologue `56 57 55 81
  ec 44 01` unique 2-site shape; sibling 0x1cf23 has ZERO RAM hits). ZERO E8
  callers (table-dispatched like every window handler).
- RAM grid scan: fn 0x354f8+P0 EXACTLY 1 hit @0x247db0, grid base 0x247da8
  stride-6 slot 2, cp = 0x247d20, magic rec 0xfd705c NAME='LOADSCREEN'
  (3/3 saves both runs; controls fn 0x51834 1-hit @0x248050 5th reproduction,
  fn 0x51cc4 1-hit @0x248038). Payload pool corroborates: 'loadscr',
  'LOADLIST', '%02d.sav', '..\\loadwin.cpp'. The dx==0x1c01 receiver INSIDE
  fn 0x354f8 formats + displays a save-slot pick. Digit keys talk to the
  load/save screen family — FLEETWND can NEVER receive 0x1c01 from keys
  (t314's zero EXPLAINED).
- WHOLE-PAYLOAD 0x1c01 literal census = exactly 5 sites: 0x16169 relay
  (t311-dead shape), 0x1642c receiver inside fn 0x16420 = 'BatControlWnd'
  grid slot 3 (named this session), 0x33375 msg-emit builder via fn 0x56ca4,
  0x35697 LOADSCREEN sender, 0x1756b FALSE POSITIVE (E8 rel32 operand). No
  in-game-window sender exists.
- GATE RECORD MEASURED (chain law exact): caller 0x51f3b: eax=[win+0xab] ->
  fn 0x32fa4 returns [win+0xc7+idx*8] DIRECTLY; gate 0x52059 reads rec[+0x58]
  (1..5 else ret0); writer arms copy rec[+0x59..5c] to DAT_43508/43504.
  FLEETWND rec 0xfe7a90 -> win 0xfe7ac0 -> slot0 0x600000: gate byte GUEST
  0x600058 == 0 and datum 0x600059..c == 0 in 212/212 valid-chain saves
  (221 more hold [win+0xab]==0 -> accessor error path). WATCHPOINT TARGET =
  0x600058. CAUTION banked: 0xfe7ac0 is the INSTANCE (name 'fleetwin'), the
  magic rec is 0xfe7a90 — base mix-ups land on name-string bytes.
- P0 RE-DERIVATION LAW (new): payload BYTES map to B+off (B=0x1bf4d8 both
  runs); u32 CODE POINTERS carry P0=B-0x88; runtime data absolutes must be
  read from patched CODE bytes (DAT_7e582 -> 0x2c0582 verified at B+0x35561),
  never guessed as P0+off.

## S42 t316 (2026-11-06) — THE DYNAMIC 0x1c01 EMIT TARGETS FLEETWND BY SLOT
## ID: CHAIN CONTINUOUS STATICALLY (ship-list click -> registry -> fn 0x51cc4)
Full evidence docs/re/_wip_t316.md S1-S5; scripts/r316_registry_dump.py +
r316_registry_probe.py (offline, zero capture; 685-save corpus = all
t299-leg-*/save + playcap/save).
- OWNER NAMED: emit-builder fn 0x33320 (span [0x33320,0x33456), prologue
  56 57 55 83 ec 08; the sole `bb 01 1c 00 00` at 0x33374) has EXACTLY ONE
  E8 caller: 0x32778 inside STATSHIPLST's slot-2 fn 0x32664 (in-rect msg-0xc
  branch; t314 run-2 witnessed msg stops in this same fn). Not a map/HUD
  pump. 0x1c01/0x1c02 are a PAIRED emit (road chosen by global 0x9f100,
  runtime 0x2e1100, measured 0 -> 0x1c01 road).
- TARGET LAW (static-cited + corpus 685/685): fn 0x33320 passes edx=
  [w+0x63]; STATSHIPLST rec 0xfe7b48 [+0x63] == 95 in 685/685 saves;
  FLEETWND rec 0xfe7a90 [+0x41] == 95 (60.sav). rec+0x41 = registry slot-id
  PROVEN: ctor fn 0x3264c `mov $0x7a35c,%eax; call fn 0x5712c; mov %eax,
  0x41(%ebx)` (all four fn 0x5712c callers pass obj 0x7a35c). fn 0x56ca4 win
  = [obj+edx*12+4] -> FLEETWND magic rec -> call [rec+0xa7+8] = FLEETWND
  dispatch slot-2 = fn 0x51cc4 -> 0x1c01 path 0x51f3b -> gate 0x600058 ->
  writer pair DAT_43508/43504. FIRST measurement-based in-game link from a
  0x1c01 producer to FLEETWND.
- REGISTRY SAVE-TIME BLINDNESS (honest negative): [obj+0x4226]==0 AND
  [obj+0x3000]==0 in 685/685 saves (u32 and u16 reads) while 126 magic recs
  persist; whole-RAM pointer census finds NO u32 pointing at the FLEETWND rec
  (3 rec-ptr hits total: TOGGRID, 'I'). Registration fn 0x5712c (sole
  0x12345678 writer 0x57173) runs in-session => registry table is rebuilt
  post-load / not persisted: SAVE SCANS CAN NEVER WITNESS DELIVERY — third
  mechanism class after t313 runtime jump table and t314 computed offsets.
  t317 = LIVE shape (arm fn 0x56ca4 entry + fn51cc4_entry + writer legs,
  click STATSHIPLST rect 7,46..632,472 with FLEET open, NO rowjump).
- CORRECTION: t315 S6's `[[obj+0x4226]] = 0x23c7969f` was a mis-parse of the
  cmpl disp32 at 0x33356 (bytes +3..+6); re-measured 0x0. Other t315 S6
  numbers stand.

## S43 t317 (2026-11-06) — THE GUTTER-CLICK LIVE WITNESS: VENDOR CLICKS
## ARRIVE AS MSG 8 ON STATSHIPLST'S OWN ENTRY; NO 0x1c01 EVER FIRED; THE
## REAL msg-0xc/4 INTAKE IS THE BROADCAST PUMP fn 0x56b5c (s2_56c74).
LIVE run work/r1/t299-leg-20261106-012002 (rc=0, 9 census windows, 96 stops;
scripts/r299_leg_session.py --shipclick 4 phase NEW, scripts/r317_relaunch.sh,
scripts/r317_gate_probe.py; full detail docs/re/_wip_t317.md S0-S8).
- MEASURED: 4 clicks at x=620 (gutter; strip law 632-28=604 corroborated by
  saves: [w+0xb3]=-1, [w+0xbf]=28) each fired EXACTLY ONE s2_56cda stop with
  edi=edx=0x8, eax=0xfe7ac0 wrec NAME='STATSHIPLST', ebx=0x26c, ecx=ebp=Y
  verbatim; baseline window 0 stops; fn51cc4_entry/w43508/w43504/btn_hdlr
  ZERO WHOLE-LOG (pty census). gate 0x600058=0 datum=0 after every window;
  oracles unmoved. THE t316 CHAIN INTAKE ("in-rect msg-0xc click") IS
  LIVE-REFUTED: no click posts msg 0xc to STATSHIPLST.
- STATIC (verbatim): fn 0x32664 msg switch 0x3266f.. (8 -> 0x32720 fn 0x33058
  row bookkeeping; msg-8 gutter sub-branch 0x33158 self-sends 0x193 then
  calls row-table CLEARERS fn 0x56730/fn 0x56434 — decoded, NOT dispatchers);
  fn 0x33058 full road incl. row-half self-sends 0x191/0x192 (0x332ad..).
- NEW LAW (t318 seed): fn 0x56b5c = BROADCAST msg pump (mode-masked table
  family obj+0x3068 stride 0x8e; per-entry slot-2 dispatch call *[tgt+0xa7+8]
  @0x56c74; suppression flags ds:0xa2024; sole msg-0xc/4 posters 0x54aa9/
  0x54ab2 driven by click record ds:0x484ec/0x484f0). t317 armed s2_56cda
  only — msg-0xc/4 deliveries were structurally invisible; NEXT = s2_56c74
  leg run (_wip_t317 S8 shape). [w+0x4f] census CLOSED: single direct store
  movb $0,[r+0x4f] @0x30bdb (disp8+disp32, all widths) — 0x66 is copy-written;
  msg 4 never tests it, so t318 is independent of it.

## S44 t318 (2026-11-06) — THE BROADCAST PUMP DISPATCH 0x56c74 IS COLD LIVE:
## NO MSG ID OF ANY KIND REACHED FLEETWND (2nd confirmation); THE POSTER GATE
## IS THE NAMED BLOCKER. Full detail docs/re/_wip_t318.md S0-S6 (run
## work/r1/t299-leg-20261106-021602 rc=0, 9 census windows, 540 s armed,
## legs {s2_56c74, s2_56cda, fn51cc4_entry, w43508_51fc2, w43504_52003,
## btn_hdlr}). pty-whole-log-census: s2_56c74 0 | s2_56cda 26 | fn51cc4 0 |
## writers 0 | btn_hdlr 1. s2_56cda 26 = 18x msg 0x3b COSMOSWnd (periodic) +
## 4x msg 8 STATSHIPLST at x=620 gutter clicks (t317 VERBATIM reproduction)
## + msg 8/6 PLIND (sprite) + 2x msg 8 PLANETALLOC. Literal 0x1c01/0x1c02
## appears NOWHERE in any banked reg/stack (0/26). Oracles: gate 0x600058=0
## datum 0; DAT_43508/43504 unmoved across all four click before/after pairs;
## mode4226 0x12 shipclick phase / 0x11 sprite-planet / 0x1 post-NEXTTURN.
- SCOPE LAW (honest boundary): legs are DELETED between census windows and
  during each fire-cycle's BPDEL->re-arm gap, so this measures "0x56c74
  delivered nothing observable", NOT "fn 0x56b5c was never called". The
  caller-vs-mask separation is t319.
- STATIC POSTER-BLOCK RE-READ (t91_code_disasm 77195-77245 verbatim): the
  4-vs-0xc choice at the pump call 0x54ac5 is gated by TWO u32 equalities —
  0x54a3f cmp edi,ds:0x484a4 (equal road = 0x5be9b query + msg-0x3f1
  dispatch @0x54a83, pump only if [[esi+0x21d92]+0x39]!=0); jne road 0x54a88
  cmp edi,[esi+0x24da4] (equal + [esi+0x489e]==0 -> msg 0xc, else msg 4).
  fn 0x56b5c has NINE E8 callers (0x53fa3 d, 0x54976 3, 0x54ac5 4/0xc,
  0x54b36 5, 0x5531e f, 0x5548c e, 0x55f82 d, 0x56f0f 2, 0x57003 1).
- HARNESS: bank_stop esp dump widened 8->16 B (esp_p8/esp_p12 banked — the
  pump dispatch carries msg=[esp+8] BEFORE the return push; unexercised this
  run, harmless). scripts/r318_analyze.py NEW (offline hits.json census).

## S45 t319 (2026-11-06) — THE POSTER ROAD FIRED LIVE: CALL SITE 0x54ac5,
## MSG 4 (NOT 0xc). THE BLOCKER IS THE NAMED EQUALITY [core+0x24da4]==-1.
## Full detail docs/re/_wip_t319.md S0-S5 (run work/r1/t299-leg-20261106-030727
## rc=0 attempt-1, legs {pump_entry_56b5c, p54a47, p54a88, s2_56c74, s2_56cda},
## proven --shipclick 4 + standard tail). pty-whole-log-census: pump_entry 1 |
## p54a47 0 | p54a88 1 | s2_56c74 1 | s2_56cda 106 (102x msg 0x3b COSMOSWnd,
## 4x msg 8 STATSHIPLST gutter VERBATIM, 1x msg 0x193 self-send). The banked
## EV stop (03:19:09, 6 s after gutter click y=453, armed window): edx=0x4
## MSG-4, esi=eax=0x2bc35c core obj, edi=0xffffffff (=[obj+0x24da8], set at
## 0x549de), ret0 file 0x54aca = E8 site 0x54ac5 THE POSTER, esp_p8=0 (4th
## push @0x54aa6). p54a88/s2_56c74 fires were re-arm-gap pty renders (t305
## census law; render contexts verified verbatim). VERDICT: caller-never and
## pump-entry-never REFUTED; gate-never-equal CONFIRMED — msg 0xc requires
## [obj+0x24da4]==-1, measured 0 (scripts/r319_gate_read.py NEW, oracle-law
## addressing, cross-checks t318 gate_484ec=0x1ff exact); [obj+0x489e]==0
## already true; ds:0x484a4=0 so the equal road needs -1 too. Block-entry key
## ds:0x484dc==-1 AND ds:0x484d0!=0 set by mouse-state recorder fn 0x2a7a4
## (0x2a7a8-0x2a7bb) — happened ONCE in 28 min, right after a gutter click.
## NO 0x1c01 anywhere: the msg-4 poster is NOT the destination road; OQ-019
## residue stays open (strict-close). NEXT t320 (offline): writer census of
## core+0x24da4 + ds:0x484a4; what msg 4 does in FLEETWND fn 0x51cc4.

## S46 t320 (2026-11-06) — THE MOUSE-ACTIVE POSTER-PASS RUN: 27/27 POSTER
## FIRES, ALL MSG 4 — THE CLICK-PULSE LEVER IS DEAD; ds:0x484ac RECLASSIFIED
## AS THE BIOS BUTTON-HELD WORD (run work/r1/t299-leg-20261106-041522 rc=0
## attempt-1, legs {pump_entry_56b5c} + --shipclick 4 + NEW --pulse-clicks 30
## + standard tail). pty-whole-log-census pump=27 (t319: 1 in 28 min — click
## traffic DRIVES the poster block; baseline windows 0, idle law holds; 1/20
## run saves froze the entry conjunction d0=1/dc=-1 verbatim). EVERY banked
## stop edx=0x4, esi=eax=0x2bc35c, edi=0xffffffff, ret0 file 0x54aca = POSTER
## 0x54ac5, esp_p8=0; 0x1c01/0x1c02 absent all stops; DAT oracles unmoved.
## STATIC RE-READ (t91_code_disasm 24853-24866): fn 0x2a5f0 = BIOS int 16h
## AH=2 mouse poll — 484ac=-1 @0x2a629 iff (AL&1)||(AL&2) (LEFT/RIGHT HELD at
## poll), else store (AL&1)=0 @0x2a635; so 484ac is the raw BUTTON-HELD state,
## cleared by the next ms-scale poll. A 50-ms pulse press every ~20 s (bank
## cascades eat the 1.5 s cadence) CANNOT cover the poster pass: DEAD SHAPE.
## xdotool absent + SDL rejects synthetic MotionNotify (xsend.c header law):
## the mousemove lever is dead on this host. t321 LEVER (deterministic if the
## premise holds): press-only Button1 verb in xsend.c (press_only machinery
## exists for keys) — HOLD the button across the armed window so every int16
## poll sees AL&1, 24da4=-1 persists, poster cmp 0x54a88 EQUAL -> msg 0xc;
## MUST pair a release before the run tail. NO LEDGER ROW CLOSED (strict-
## close: no live 0x1c01/DAT_43508 store, no msg-0xc stop).

## S47 t321 (2026-11-06) — fn 0x51cc4 FULLY DECODED: msg 4 AND msg 0xc ARE
## DEFAULT-HANDLED (fn 0x336b4), THE DAT STORE ROAD IS MSG-0x1c01-ONLY IN
## THIS WINDOW; fn 0x1b91c RE-VERIFIED VERBATIM; THE BATCON WRITER LEGS WERE
## NEVER ARMED. Offline decode (work/t91_code_disasm.txt; full detail
## docs/re/_wip_t321.md S0-S7). Key measurements (all verbatim addresses):
- DISPATCH (0x51cc4 prologue 56 57 55 81 ec bc 01): cmp dx,2 @0x51ce5 (jb
  0x5206f -> msg1 gate 0x51d29; jbe 0x51f0c -> msg2 sets [win+0xaf]=
  [[rec]+0x8cd]); cmp dx,0x1c01 @0x51cf5 je 0x51f3b; EVERYTHING ELSE
  (incl. 4, 0xc) falls through 0x51d00 -> call fn 0x336b4 tail. No msg-4/0xc
  dedicated branch EXISTS.
- fn 0x336b4 TREE (0x30f55/0x30de2/0x30f46/0x30dbb/0x30dd2/0x30fa9/0x30f26):
  msg 4|5 -> 0x30e0e rect hit-test -> ring post OR registry dispatch fn
  0x56ca4(edx=[win+0x63]); msg 0xc -> 0x30edc rect hit-test -> ring post
  fn 0x56ad4(code 5, ebx=&[win+0x4f]); ZERO DAT_43508/43504 stores in fn
  0x336b4. Scope law: the registry forward CAN hand msg 4 to another window
  (t316 slot-id law) — "no store" is proven for this window + fn 0x336b4,
  [inferred] beyond; t318 census (msg 4 never reached FLEETWND live) keeps
  it theoretical.
- 0x1c01 HANDLER 0x51f3b: fn 0x32fa4 accessor; ecx==5 -> popup leg (fn
  0x56d1c 0x2b6b + ring 8); ecx!=5 -> 0x52059 u8 [rec+0x58]-1 jump table
  cs:[0x3d100] (FILE BYTES UNRELOCATED — verified garbage {0x80,
  0x6650d231,...}; RAM instance {0x51fb5 x3, 0x51ff6, 0x52037} t313 S8
  stands); state 1-3 -> 0x51fb5 *** mov ds:0x43508,[rec+0x59] @0x51fc2 ***
  + ring 0x11; state 4 -> 0x51ff6 *** mov ds:0x43504 @0x52003 *** + ring
  0x11; state 5 -> 0x52037 ring code 3, no store.
- WRITER CENSUS RE-CONFIRMED (literal a3): DAT_43508 {0x1b5e6, 0x1baa7,
  0x51a8e, 0x51fc2, 0x55bbd} + 89 15 variant 0x55bcc; DAT_43504 {0x28ec2,
  0x28ef6, 0x36b01, 0x52003, 0x55d35}. fn 0x1b91c (batcon click, callers
  0x1b0cc/0x1b1de BOTH inside fn 0x1aef8 = BatModeWnd slot 2, class table
  0x88498) re-verified byte-for-byte against t296 S5: kind-2 arm gate
  ([ship+0x54]sar16==ds:0x7458e current viewer, [ship+0x88]>0) -> [win+
  0xb7]=2; kind-1 + stored-equal + mode ch==0 -> 0x1baa7 publish + ring 0x11.
- msg-0x50 SENDER HUNT (fresh, closes a loose end): whole-image `mov edx,
  0x50` census = 3 sites, ALL false positives (0x1519d `sub edx,eax`
  immediately after; 0x3a9e7, 0x71af3 not msg-call sites; none precedes a
  call [reg+8]/ring post). The ONLY msg-0x50 consumer is fn 0x1aef8's own
  cmp @0x1b7cd; sole branch into the publish block [0x1b5ba,0x1b600) is
  jbe 0x1b7d7. t296's "no widget-side poster outside the batmode family"
  RE-CONFIRMED image-wide.
- HARNESS BLIND-SPOT (decisive for t322): scripts/r299_leg_session.py arms
  w43504_{28ec2,28ef6,36b01,52003,55d35}+w43508_{51a8e,51fc2,55bbd} — the
  batcon-family stores 0x1b5e6/0x1baa7 were NEVER ARMED in ANY capture
  t307..t320 (grep: zero hits in scripts/, logs only discuss them offline).
  t307 live-validated the instrument catches census stores. t322 = batcon
  two-click capture, legs {batmode_dead 0x1aef8, fn1b91c_entry,
  w43508_1b5e6, w43508_1baa7} + btn_hdlr control + Icarus-view battery,
  recorder-first state-byte reads; decision tree in _wip_t321 S7. The
  Button1-HOLD-for-pump branch is DEAD (S1/S2: pump msgs cannot reach the
  store road from FLEETWND at all).

## S48 t322 (2026-11-06) — BATCON CLICK-ROAD LEGS ARMED LIVE FOR THE FIRST
TIME: BatModeWnd receives ZERO msgs in-view (branch (b), composition-shielded).
Run work/r1/t299-leg-20261106-055549 rc=0 attempt-1 (scripts/r322_relaunch.sh,
analyzer scripts/r322_analyze.py; legs batmode_dead/fn1b91c_entry/
w43508_1b5e6/w43508_1baa7/btn_hdlr; battery pre-turn 1086->1087 + fleet open
rails=188 + rowjump + sprite 48x151 + planet 439x331 + NEXTTURN):
- PTY WHOLE-LOG {batmode_dead:0, fn1b91c_entry:0, w43508_1b5e6:0,
  w43508_1baa7:0, btn_hdlr:3}; census-ctl MATCH=True. Banked btn stops: sprite
  -> 'PLIND' msg 8 (t312 law re-observed), planet -> 'Cancel' msg 4 (EVENTWIN
  popup ate the click — harness defect banked _wip_t322 S5), nextturn ->
  'PLSQUARE' msg 8.
- sel43510=0 in 9/9 oracle snapshots; DAT_43504 'Icarus' constant; DAT_43508
  0x26fe77->0x26f00d across the turn with zero armed-writer fires (writer-less
  law, t298-C/t311, re-observed — never read as a store).
- LAW: with the entry leg armed and alive-instrument verified, NO msg reached
  fn 0x1aef8 the whole session (t306 = second independent zero). The batcon
  selection/publish stores 0x1b5e6/0x1baa7 are UNREACHABLE from any captured
  in-view composition — the blocker is window ACTIVATION (windows.txt line
  1178 BatModeWnd TYPE 4 STATE 1 16), not the click layer and not the code.
  OQ-019 select/destination residues: mouse route CLOSED as a live route;
  next move = offline activation decode (_wip_t322 S6), capture ONLY after it
  names an activator.

## S49 t323 (2026-11-06) — OFFLINE ACTIVATION DECODE: BatModeWnd ACTIVATION
HAS NO IN-SESSION TRIGGER. The t322 "blocker = activation" resolves to an
HONEST NEGATIVE: OQ-019 select/destination residues are UNREACHABLE-BY-
CAPTURE (zero-capture iteration; full evidence docs/re/_wip_t323.md S0-S6).
- STATE 1 16 is NOT a show/activate flag: the STATE line builds the
  per-window state-RECORD table at windows.txt load (14B records: rect
  u16s, flags u16@+0xa bit0 present/bit1 current, size WORD@+0xc =
  frame*5+0x14 via fn 0x32000; loader helper fn 0x31d58). Runtime state =
  WORD [win+0xb1] current-record id, [win+0xaf] = count.
- COMPLETE [win+0xb1] writer census (image-wide grep, 14 sites, all
  classified): constructors fn 0x31c54 (=0xffff)/fn 0x3377c/fn 0x33d08/
  fn 0x33c34 (=strlen(name)-1, construction-time); char-input state-cycler
  fn 0x339a4 (gated on ASCII ranges; BatModeWnd msg tree has NO char
  handler per t296 S5 + t321 -> unreachable); fn 0x364d2 (store target is
  [tbl+0xb1] of the state TABLE, not a window field — excluded); and the
  ONLY runtime switcher fn 0x31f30 (store @0x31faf; callers EXHAUSTIVE =
  0x321ad + 0x3221b, both inside fn 0x32100).
- fn 0x32100 = generic state-rect-click msg handler (msgs 0..8, jump table
  cs:[0x1d524], default -> fn 0x336b4): fn 0x31e74 hit-test -> fn 0x31f30
  -> repaint. NOT in the cited BATMODE class table (t296: BATMODE =
  [0x1abfc,0x30d08,0x1aef8,0x1d858,0x311b8,0x1e9dc]); its static-image
  reference is a misaligned jump-table byte FALSE POSITIVE (0x603ea).
- Every runtime naming of "BatModeWnd" is inert or foreign (pool-relative
  OQ-004 immediates decoded verbatim): fn 0x2351c (image-wide name->layout
  bookkeeping @ds:0x48c44 + [wmgr+0x32dda]; the name arg is a DEAD
  assert-string overwritten @0x23558; callers 0x21530 boot-gated by
  fn 0x78283("resume.gam"), 0x24f96, 0x52a76); fn 0x528ec right-panel
  deselect block 0x52a44 (result unused, registry clears only); fn 0x156d4
  BATCTRL msg handler stores the fn 0x56d1c(imm 0x5e="BatModeWnd") result
  UNREAD and resets BatListWnd (imm 0x77) state table instead
  ([BatListWnd+0xab]=0, fn 0x32c5c viewport realloc, BYTE+0xc5=0).
- fn 0x1d7dc + fn 0x1be10 (t322's activation-adjacent candidates) are NOT
  activators: fn 0x1d7dc = repaint/teardown (fn 0x1a338/0x1a8dc/0x1bfa4/
  0x1a39c + esi==0 virtual [ecx+0xc] hide-call); fn 0x1be10 = cursor code
  chooser keyed on ds:0x7d35e == [win+0x41] -> fn 0x5a1e4.
- MSG 0x53/0x50 RE-PROBE inside the activation-candidate set: fn 0x32100's
  jump table covers msgs 0..8 only; no 0x50/0x53 poster exists in any
  candidate (fn 0x31c54/0x3377c/0x33c34/0x33d08/0x31f30/0x32048/0x314e8/
  0x32c5c) — consistent with t296 (sole msg-0x50 consumer = fn 0x1aef8's
  own publish block) and t321 S6 (image-wide sender hunt closed).
- LAW (binding candidate for REFUTED-ROUTES): NO mouse click, key, or
  message reachable from the campaign/system-map session can switch or
  activate BatModeWnd's state; its state is PINNED at construction. This
  EXPLAINS t322 branch (b) (armed-zero with MATCH=True instrument) as
  design, not as an untried activator. Corollary: the OQ-019
  select/destination residues (destination widget posting msg 0x50, live
  DAT_43508/0x43504 stores through fn 0x1b5e6/0x1baa7) can NEVER be closed
  by capture; law stands static-cited (t296 S5 gates, t321 S1-S4).
  Re-open condition: a RAM census showing fn 0x32100 (or any fn writing
  [rec+0xb1]) installed in BatModeWnd's RAM class table at [rec+0xa7] —
  static tables are RAM-relocated (t303(5)), so static absence alone is
  cited-but-indirect; t322's armed-zero is the live corroboration.

## S49 t326b (2026-11-07) — MODE-1/MSG-0x4d..0x51 FAMILY RESOLVED: THE
"ARMING MSGS" WERE TABLE INDICES; THE REAL POSTER POSTS 81 ELSEWHERE
Full walk work docs/re/_wip_t326b.md S1-S8 (scripts/r326b_extract.py pad-run
segmentation; objdump range-decode law banked there). Cited results:
- fn 0x17b2c (caller 0x1750c in a per-record loop over [[esi]+0x5032]>>16)
  writes stack [esp+0x54] := 0x4c/0x4d/0x4e keyed on BYTE[design-rec+0x1] in
  {0x1c,0x1d,0x1e}; consumer 0x17cf8 uses it as INDEX into [[esi]+0x1a92+edi*4]
  (WORD, bounds fn 0x1ce1c count [eax+0x1a8e]) + [esi+0x1bcc+edi*4]. Call
  census = NO POSTERS. 76/77/78 = gizmo-index space (0x7650c+0x6a*i law; code
  corroboration 0x17bca 0x76546+0x6a*idx = rec+0x3a RANGE). NOT messages.
- fn 0x16147 site = class-0x5850 msg handler (ctor 0x15630 stores [eax+0xa7]=
  0x5850; msg tree @0x156ec cmps {0x327,0x32b,0x32d,0x1c01,0x1c02}). Path to
  the post (fresh objdump, straight-line): gizmo gate WORD[rec+0x33]: bit0x80
  -> abort; bit0x20 set -> call 0x49e78 + return; bit0x20 CLEAR -> je 0x16147:
  ebx=0x51, call 0x56ca4 (eax=ds:0x7a35c, edx=[[ebp+0xbb]+0x41]) = POST msg 81
  to [[0x7a35c+edx*3+4]] (game-object child table, 12-byte slots; edx in
  {0,0x20}). 0x56ca4 LAW (banked S3): gate sar16([obj+0x4226])>=0; slot =
  [[obj+edx*3+4]]; call [[slot+0xa7]+0x8](obj, msg16, sar16(edx)).
- BatModeWnd handler fn 0x1aef8 dispatch compares dx ONLY in {0x6,0xd,0x3b,
  0x46,0x47,0x4a,0x50} (sed 7390-8010 census) => msg 81 falls to default
  0x1af7c EVEN IF targeted there; mode-1 setter 0x1b7dd entry requires
  dx in (0x50..] via cmp dx,0x50 @0x1b7cd jbe 0x1b5ba — 0x51 would hit the
  PUBLISH leg 0x1b5ba NOT mode-1 (publish = DAT_43508 store + ring 0x11,
  t296 S5 cited). Actual image-wide 0x51 consumers: fn 0x4709c @0x47ac0
  (je 0x47a53: [esi+0xe3]:=-100.0 float; sibling +1000000.0; gauge/score
  family, window UNNAMED — class table RAM-relocated t303(5)) and fn 0x6f600
  @0x6f7f9 (packet-parse family, NOT a window msg).
=> OQ-016 RESIDUE 1 (Phase Bomb launch/arming road) = UNREACHABLE-BY-CAPTURE
   cited (4 independent legs, see _wip_t326b S8.4). 4-launch forced capture is
   VACUOUS (no citable arming trigger; research leg vacuous per S-T326) — DROP.
   The batmode activation blocker (STATE 1 16, t322 armed-zero x2) stands as
   the sole live-movement obstacle; row stays OPEN strict-close.

## S50 t331 (2026-11-08) — BATCONTROLWND CHAIN: THE MODE-1 ARMING ROAD IS
## ALIVE-IN-IMAGE (t326b consumer-leg REFUTED; fresh objdump + live-record law)
- Window identity law (measured): class tables live at FILE 0x88xxx; installer imm
  = pool-relative data offset (imm+0x82bb0=file; RAM=P0+file). BATMODE table file
  0x88498 (imm 0x58e8, sole installer fn 0x1ac21); BATCTRL file 0x88400 (ctor
  fn 0x15630 `mov [eax+0xa7],0x5850`); live records: BatControlWnd runtime
  0xfdbe34 slot 61, BatModeWnd 0xfdc89c slot 63, registry [0x2bc35c+4+slot*12]
  MATCH both; NAME is RAW ASCII at rec+0x20 (magic u32 0x12345678 at rec+0x00).
- BatModeWnd STATE pinned: state-table ptr [+0xab]=NULL and count [+0xaf]=0 in
  20/20 t=1086 saves; setter fn 0x31f30 asserts (0x2a428 ebx=0x396) for any
  id>=0 when count=0; sole caller pair {0x321ad,0x3221b} inside fn 0x32100 which
  is NOT in the class table (t323 stands). ACTIVATION of the window itself stays
  dead — but activation was the WRONG question.
- THE ROAD (every edge cited in _wip_t331 S7): msg 0x1c01 -> BatControlWnd slot-2
  fn 0x156d4 (tree 0x156ec; 0x1c01 branch 0x15ebf: reject iff [BatModeWnd+0xb7]==4;
  al=BYTE[+0xb9]-1; jmp cs:[eax*4+0xb04] REBASED, live table member 0x1d4b04:
  [0]=0x15ef9 [1]=0x15fed [2]=0x16181 [3]=0x15ef9). Gate block 0x15fed: gizmo rec
  via fn 0x32f34/0x32fa4 accessors on [ebp+0xb5]=BatListWnd; WORD[rec+0x33]
  bit0x80 abort / bit0x20 set -> fn 0x49e78 shield-charge / CLEAR -> 0x16076 +
  je 0x16147 POST 0x51; bit0x40 set -> 0x16181 block POSTS 0x51 too (0x161d1).
  Both posters: eax=ds:0x7a35c, edx=[[ebp+0xbb]+0x41]=63 -> fn 0x56ca4 law ->
  fn 0x1aef8 -> 0x1b7dd BYTE[+0xb7]=0x1 = MODE-1 ARMED (fallthrough of cmp dx,0x50).
- b9 state machine: msg 0x320 param al {0->b9=1 @0x15b51, 2->3 @0x15b48, 3->2
  @0x15b1e}; msg 0x1c01 legs also set b9 2/3 (0x15f1e/0x15f25/0x15f35) AND post
  msg 0x53 to BatModeWnd (0x15f3c/0x15f75). fn 0x1aef8 back-posts 0x320/0x326 to
  [[win+0xab=BACKPOINTER-BEFORE-INIT? no: its OWN state-table slot] -> 0x1b164/
  0x1b202/0x1b127 (mouse legs).
- Gizmo flags FILE-LOADED: sole WORD[rec+0x33] writer fn 0x49074 (gizmos.txt
  flag_list sscanf loop, 0x491ec/0x49221); enum gizmos.txt L67-76: 32 TOGGLEABLE,
  64 NOTARGET, 128 PASSIVE. Phase^Bomb flag_list {3} => 0x80/0x20/0x40 CLEAR.
- NOT YET CITED: any poster of imm 0x1c01 targeting slot 61 (imm census 5 sites,
  road law fn 0x33320 edx=[win+0x63]; STATSHIPLST road 95). t332 capture legs:
  fn156d4_entry/tbl15ef1/gate15fed/post1615d/post161d1/mode1_1b7dd + My^Items
  click screen (593,218).

## S51 t332 (2026-11-08) — BATCONTROLWND CHAIN LIVE WITNESS: THE FIFTH LEG IS
## MEASURED, AND THE OBSTACLE IS THE ACTIVE SCREEN STATE, NOT A WIDGET
One scratch debugger session (work/r1/dbg-t332-20261107-124717, rc=0 attempt 1,
tool scripts/r332_batctrl_session.py; production :9 untouched, ps-verified).
Legs armed {fn156d4_entry 0x156D4, tbl15ef1 0x15EF1, gate15fed 0x15FED,
post1615d 0x1615D, relay1616f 0x1616F, post161d1 0x161D1, mode1_1b7dd 0x1B7DD,
backch_1b180 0x1B180} + btn_hdlr control, in TWO sub-batteries (A downstream-only,
B entry-alone) because an armed entry leg consumes the census window (t330 law).
- CENSUS (pty whole-log): ALL EIGHT legs 0; btn_hdlr 8 (instrument alive). 8/8
  banked stops attributed to btn_hdlr. Save axis (19 oracle reads): BatControlWnd
  rec 0xfdbe34 and BatModeWnd rec 0xfdc89c (both located by NAME+magic) hold
  [+0xb7]mode=0 AND [+0xb9]=0
  in every save before/after every click. OUTCOME C of the assignment.
- NEW MECHANISM FOUND PRE-RUN (fresh objdump 0x16060..0x16200): the handler's own
  SHARED TAIL 0x16162..0x1616f is a msg-0x1c01 SELF-RELAY — `mov ebx,[ebp+0xa7]`
  (BatControlWnd's own class table) / `mov edx,0x1c01` / `mov eax,ebp` /
  `call [ebx+0xc]` (class-table slot 3). Reached from the 0x16071 shield jmp, the
  0x16145 jmp AND the fallthrough of the 0x51 post at 0x1615d. This is why t331's
  immediate census found "no poster": the delivery is a TABLE CALL, not a registry
  post, and it is internal to fn 0x156d4. Site = r299 leg s2_1616f (zero in
  t310/t311/t312, whose batteries never clicked these rects). It never fired here
  either => no 0x1c01 pass ever reached the handler at all.
- WINDOW OWNERSHIP MEASURED AT THE PIXEL (banked stop names, magic+NAME@+0x20):
  (513,118)/(591,118) on the strategic map -> NEXTTURNCONT msg 4/8 ret0 0x3177d;
  (513,118) in the rowjump view -> PLIND msg 8 ret0 0x3cb8d; (553,200) and
  (593,218) -> PLBUILD msg 4 ret0 0x3cb8d. The t253 FLEET rowjump enters the
  PLANET/orbital state (PLIND/PLBUILD/PLANETALLOC), NOT a battle screen.
- STATE-16 CENSUS (fresh windows.txt parse): STATE 1 16 is EXCLUSIVELY the
  battle-map family — 19 windows {BatControlWnd, BatListWnd, BatModeWnd, TOGGRID,
  BATROTLEFT, BATROTRIGHT, BATZOOMIN, BATZOOMOUT, RECENTER, TOGELEV, ABANDON,
  My^Items, Other^Items, Repeat, Pass, Auto, W, S, Z, I}. States witnessed in
  captures: NEXTTURN/NEXTTURNCONT 1, PLIND/PLBUILD/PLANETALLOC 17, FLEETWND 18,
  COSMOSWnd {1,3,7,13}. ZERO overlap with 16.
- DISPOSITION: the arming road is alive in-image (t331) and dead in-capture for a
  STRUCTURAL reason now measured: the family is composed only while the game-level
  ACTIVE SCREEN STATE == 16. t323 closed the per-window [win+0xb1] route; the
  never-decoded edge is the GLOBAL active-state writer (the id consumed by the
  windows.txt STATE-line composition law fn 0x31d58 / loop 0x5898e..0x58b3e). That
  is a ZERO-CAPTURE question. OQ-016 residue (1) STAYS OPEN strict-close: the
  mode-1 store 0x1B7DD has still never been witnessed firing, and no nuke effect
  has ever been observed.
- INSTRUMENT LAWS (see _wip_t332.md S8): clicks are windows.txt-space, grabs are
  root-space (XOFF,YOFF 80,100) — never add the origin to a click target; the
  `census control MATCH` probe is FALSE for legs containing a relocated immediate
  (judge arming by BPLIST + fires); window-record fields +0xb0/+0xb7/+0xb9 are
  BYTES interleaved with DWORD pointers at +0xb5/+0xbb, so byte-granular reads are
  mandatory; a class-table ebp (btn_hdlr: 0x247ca0) yields table data, not a record.
- JUMP-TABLE SPACE FIX: t331's "member 0x1d4b04" is the LINEAR disp32 read out of
  the live instruction; the .sav member is 0x1d4b04+0x88 = 0x1d4b8c, where the
  table reads [0]=0x15ef9 [1]=0x15fed [2]=0x16181 [3]=0x15ef9 (entries 4/5 =
  0x1624d/0x161e5, unreachable: the b9 dispatch bounds al<=3). Structure CONFIRMED
  as data for the first time.

## S52 t333 (2026-11-08) — THE "GLOBAL ACTIVE SCREEN STATE" IS A CATEGORY ERROR:
## [win+0xab] IS THE CONTROL TABLE, fn 0x31d58 IS A CONTROL-FLAG WRITER, AND THE
## BATTLE-MAP WINDOWS HAVE NO CONTROL TABLE AT ALL
Zero-capture iteration (static disasm + offline .sav census; production :9 pids
136357/136359 + Xvfb 1461 never signalled). Instruments: work/r331_disasm.txt
(139,026 insns) read verbatim; census scripts/r333b_state_layout.py over 372 saves
(42,780 window records, 5,208 control records). Full working notes:
docs/re/_wip_t333.md S0-S7.
- WINDOWS.TXT STATE-LINE GRAMMAR, MEASURED 123/123 LINES, ZERO EXCEPTIONS:
  `STATE <count> <id> [<id> ...]`. RACECONTROLS:418 `STATE 3 1 7 13` = THREE states
  {1,7,13}; BatModeWnd:1180 `STATE 1 16` = ONE state, id 16. Distinct ids in the
  file: 0,1,2,2,3,4,6,7,8,9,10,10,12,13,14,15,16,16,18,20-class (max 20). The
  state-16 family is 20 windows (t332 said 19 — off by one; list re-derived
  identically: BatControlWnd, BatListWnd, BatModeWnd, TOGGRID, BATROTLEFT,
  BATROTRIGHT, BATZOOMIN, BATZOOMOUT, RECENTER, TOGELEV, ABANDON, My^Items,
  Other^Items, Repeat, Pass, Auto, W, S, Z, I).
- THE RECORD LAYOUT, FROM FIVE INDEPENDENT VERBATIM READS (not inference):
  [win+0xab] u32 TABLE PTR (fn 0x31d58 0x31d7e; fn 0x31e74 0x31e94; fn 0x31f30
  0x31f75/0x31f91; fn 0x32100 0x3224c) · [win+0xaf] u16 COUNT (fn 0x31f30 0x31f44
  bounds compare; fn 0x31d58 reaches it as the high half of the dword @+0xad via
  `mov ebx,[esi+0xad]; sar ebx,0x10`) · [win+0xb1] u16 CURRENT INDEX (fn 0x31f30
  0x31faf writes it; fn 0x31e74 0x31ec3 returns it). The prior t323 wording that
  called +0xb1 a "CURRENT STATE id" is WRONG IN MEANING: it is the current CONTROL
  RECORD INDEX, and 0/0xffff when the window has no controls.
- BYTE-FOR-BYTE CONTROL-RECORD DECODE (the proof the table is CONTROLS, not the
  STATE list). RACECONTROLS member 0xfd5d84, table -> member 0xfd5e3c, count 7,
  current 0xffff. rec[0] = `01 00 | df 01 ef 01 | c1 01 d1 01 | 05 00 | 14 00`
  against windows.txt:429 `RACE1CONTROL 1 479 449 495 465 0 20`:
  +0x00 id=1 · +0x02=479 · +0x04=495 · +0x06=449 · +0x08=465 · +0x0a flags=5 ·
  +0x0c size=20. Ids across rec[0..6] are 1,2,4,8,16,32,64 = the RACEnCONTROL
  bitmasks verbatim. The loader's `shl eax,cl` id construction (0x58b0b) builds
  THESE, and fn 0x31d58's only store 0x31dd0 `mov WORD PTR [eax+0xa],dx` sets
  THEIR enable flags.
- MEASURED FLAGS, 372/372 SAVES: RACECONTROLS control +0xa = 5 (bit0|bit2) for
  ids 1,2,4,8 and 0 for ids 16,32,64 — exactly the first four race slots enabled.
  This is the loader loop 0x58aff..0x58b3e writing val=1 per player-race slot.
- RARITY, THE HEADLINE: RACECONTROLS IS THE ONLY WINDOW IN THE ENTIRE CORPUS WITH
  A DECODABLE TABLE at [win+0xab]. NEXTTURNCONT, COSMOSWnd, BatControlWnd,
  BatModeWnd, TOGLANES, TOGEMPIRE, STATUSWND, GIZLIST, RACELIST, LOADLIST,
  SHIPDESSCREEN, NEGSCREEN, INTELSCREEN ... table u32 = 0 in 372/372 saves.
  BatModeWnd member 0xfdc924 measured +0xab=0, +0xaf=0, +0xb1=0; BatControlWnd
  member 0xfdbebc identical.
- CONSEQUENCE FOR fn 0x31f30 (the sole runtime switcher): it bounds-asserts
  (`mov ebx,0x396; mov edx,0x183e; call 0x2a428`) whenever idx >= [win+0xaf]. With
  count=0 measured, it CANNOT be called successfully on either battle window. The
  control machine is structurally incapable of naming them — independently
  confirming t323's construction-pinning conclusion by a measurement route.
- THE t332 AMENDMENT-(3) EDGE IS DISSOLVED, NOT ANSWERED. (a) fn 0x31d58 cannot
  select a screen (it writes control flags). (b) There is NO global
  active-screen-state datum: `grep -nE "mov (WORD|BYTE|...) PTR ds:0x13b98"` over
  the whole image returns NOTHING — the loader's loop bound ds:0x13b98 has no
  writer in the image. (c) All seven [win+0xb1] writers (0x31c79, 0x31faf,
  0x33787, 0x339a4, 0x33c73, 0x33d1b, 0x364d2) are constructors / a char-input
  cycler / a table write / the bounds-asserting switcher — none is a screen
  selector. So residue (1) does NOT get an activator, and the route text must stop
  pointing at fn 0x31d58: the STATE line is consumed at windows.txt PARSE TIME and
  its runtime home is not in the window record.
- NEGATIVES WORTH BANKING: the windows.txt keyword literals (PARENT, NUMCONTROLS,
  SHAPEFRAME, HELPINDEX, MOUSEFOCUS, X0, BACKGRNDCOLOR) appear ZERO times in
  work/ascend_restored.bin, ascend_payload.bin, ascend_raw.bin and t73c_obj1slab.bin;
  they exist only in the data archive game/ascend00.cob (NUMCONTROLS n=1 @0x2aefb,
  PARENT n=123, STATE n=139). The sole "STATE"-prefixed string in the image is
  `STATE%02d` @0x8598b, sitting in the HELPWINDOW/gizhelp string run — a help-topic
  name formatter, NOT a windows.txt keyword. => the windows.txt parser is
  keyword-table-driven from data the RE image does not contain; do not hunt the
  STATE-line consumer inside work/ascend_restored.bin on keyword evidence.
- FALSE-POSITIVE LAW: "state 16 resident" measured by id==16 in a decodable table
  is meaningless unless the table is first PROVEN to be a control table — the only
  such table in the corpus hits 16 because RACE5CONTROL's bitmask is 16.
- UNINFORMATIVE SHAPE (do not re-run): scanning window records for the byte
  encodings of OR(1<<id) yields 1-2 spurious hits for every one of 123 windows at
  ~60 candidate offsets; two-byte patterns match a record of small ints by
  construction.

## S53 t334 (2026-11-08) — THE CONTROL-TABLE ATTACH SITE IS WALKED: THE STATE
## LINE DOES HAVE A RUNTIME HOME (win+0x6d, stride 13, counter [win+0xa1]) — ITS
## ONLY IN-IMAGE CONSUMER IS PAINT fn 0x31384; ds:0x13b98 = 4 MEASURED
Zero-capture (static disasm + offline census; tools scripts/r334_parse_map.py
exit 0, scripts/r334_state_array.py exit 0, fresh region objdump
work/r334_disasm_57c00.txt 0x57c00..0x58000; working doc
docs/re/_wip_t334.md S0-S13). Production :9 (136357/136359, Xvfb 1461) never
signalled; game/ read-only.
- ATTACH-SITE IDENTITY: 0x57d56/0x57e48 are both inside fn 0x575e4 (the winmgr
  windows.txt PARSER — its string pool at 0x85b82..0x85d3c holds `windows.txt`,
  `WMGR MAPRACES`, `%s bad parent`, `..\winmgr.cpp` x8). Sole entry: tail call
  0x575da from the winmgr init fn. Both +0xab blocks are reached ONLY by
  fallthrough (whole-body branch-target scan: zero jumps land on 0x57d18/0x57e14;
  only self-skips 0x57d25->0x57d60, 0x57e21->0x57e4e). The guards read the STACK
  SLOT [esp+0x3a6] high half (==25 -> poison -1 when parsed!=0; ==15 -> copy the
  parsed u32 verbatim into [win+0xab]); NOTHING in the 2,328-insn body writes
  [esp+0x3a6] — it is scanner-status left by 0x77fba's machinery. So "who
  allocates the control table" = the SCANNER's parsed value, copied verbatim;
  there is no allocator call at the attach site and no imul-14 anywhere in the fn.
- FORMAT-STRING DOMAIN LAW (self-correction, save-probe cited): the constants the
  parser pushes to 0x77fe1 are SCAN FORMAT STRINGS in TWO segments — small ones
  (0x3000-range) live in the loaded DATA segment (ds:0x3008 reads
  `%s %d\0..\winmgr.cpp\0...` at B+0x82bb0+X in save 41.sav), big ones
  (0x85000-range) are code-image rodata (`%s %d` verbatim at file 0x85c69).
  They are NOT windows.txt offsets — S3-era "text offset" coincidences are dead;
  keyword matching lives in the scanner machinery (0x7a1f7 + handler 0x77f64).
- THE STATE-LINE CONSUMER IS FOUND (corrects t333 S6/S9 wording): parse loop
  0x57ee6..0x57ff5 parses `STATE <count>` then per id: id==0 branch parses a NAME,
  resolves via 0x315c4, stores u32 handle at [ecx+0x1], then calls 0x31690;
  id==1 branch stores tag byte + u16 INDEX via 0x1fe20 (walks [edi+0x7d0] stride
  0x32, count [edi+0x2ede]>>16); any other id hits the vendor assert
  winmgr.cpp:0xcd6 (0x5804c). dst base = win+0x6d, stride 13 (`lea ecx,[edx+0x6d]`,
  `add ecx,0xd`). fn 0x31690 VERBATIM: asserts window type ([win+0x9f]>>16) >= 4
  (winmgr.cpp:0x241), n = WORD [win+0xa1], dst = win + 13n + 0x6d, copies EXACTLY
  13 BYTES (movs 3xDWORD + 1xBYTE), [win+0xa1]++. So [win+0xa1] IS the state-slot
  counter — the compacting writer, and its ONLY caller is the parse loop.
- CONSUMER LAW (exhaustive census, two passes): literal `+0x6d` operands in the
  whole RE image are ONLY 0x57f06 (parse fn) and 0x316de (0x31690); fresh
  low-range objdump 0x0..0x14bb0 adds NONE. But the array IS read via pointer
  arithmetic: fn 0x31384 (`mov bx,[win+0xa1]` guard, `ebp=win+0x6d+13i`, 3-way
  branch on slot byte0: 0 -> text format 0x7d3aa, 1 -> handle-resolve fn 0x1fc34
  via format 0x9f10c, >1 -> assert winmgr.cpp:0x1df) — its EXACTLY-2 callers
  0x3117f/0x3135a are inside paint fn 0x30fb8 (reads [win+0x39]/[+0x3d],
  compares [win+0x41] to ds:0x7d35e active-window ptr, draws via 0x5bf71).
  NO LE pointer to 0x30fb8 exists in ascend_restored.bin (0 hits; control fns
  0x1aef8/0x156d4 each have 1) — 0x30fb8 is reachable only through an
  outside-image table. STATE slots therefore feed PAINT-TIME text/handle
  rendering, never a screen selector; battle windows measure [win+0xa1]=0 so the
  loop is a no-op for them. (fn 0x315c4/0x31660 ds:0x6fda8 is a 0x400-byte NAME
  INTERNER pool with counter ds:0x701a6 — string handles, NOT stride-13 records;
  an interim S12 reading, retracted, _wip_t334 S13.) [win+0xa1] appears 5x:
  0x30bf3 (ctor clear), 0x313b9/0x31488 (the 0x31384 walker),
  0x316be/0x316d7 (the compactor).
- SAVE CENSUS (r334_state_array.py, 196 needle-verified saves t1086-1087):
  WORD ds:0x13b98 = 4 in 196/196 (cites t333's [inferred] per-player-slot bound;
  4 = player count, relation n=4). win+0x6d slot flags: 17,836/18,816 records
  (0,0,0,0); clean nonzero families (0,1,0,0) n=784 / (1,0,0,0) n=588 carry small
  ints (0x75, 0x2e) not pointers; text-vs-slots agreement 708/708 but ONLY on
  count==0 cases (zero positive matches); handle->magic delta scan empty for all
  K<0x200. [win+0xa1] histogram {0:600, 1:30, 2:60} over 690 records x6 saves;
  nonzero ONLY for the id==0-branch family (INTRO/PLAYTUTORIAL/FRESHGAME/RESUME/
  LOAD/SAVE/EXITTODOS/RACES), ROT* (STATE 3 1 7 13) = 0 — the index path does not
  compact. CONCLUSION: the array exists and the counter matches the branch
  structure, but in production saves the slots are zero/garbage — the parse-time
  builder's resolved handles do NOT persist as pointers. The STATE line is
  therefore STILL not a runtime screen-selection mechanism in this image; residue
  (1) keeps its disposition with the mechanism now fully named.
- MAPPING LAW REFINED: r1_slot addr = B + 0x82bb0 + X for obj1 DATA offsets is
  the correct ds: read law (a run using B+X rejected 196/196 saves — harness
  error, not law change; the t333 "+0x88 not constant" warning is about
  pointer-value->member conversions, a different transform).

## S54 t335 (2026-11-08) — THE win+0x6d STRIDE-13 ARRAY IS THE WINDOW-ITEM ARRAY:
## t334'S "STATE-LINE CONSUMER" IS RETRACTED AND THE id-16 ASSERT PARADOX
## DISSOLVES (ZERO CAPTURE)
Full working detail: docs/re/_wip_t335.md S0-S4; tools scripts/r335_state_records.py
(run 1, join failure) and scripts/r335b_item_array.py (decisive, RC=0), fresh
verbatim reads from work/r331_disasm.txt + 41.sav data segment. Sitting check
NEGATIVE (max turn 1086 == corpus); production :9 never signalled; game/
read-only. MEASURED (196/196 needle-verified saves, 22,398 window instances,
truth side = on-disk extracted/ascend00/windows.txt):
- [win+0xa1] == count of TEXTITEM+SHAPEITEM lines in the window's file block:
  22398/22398 EXACT; the same test vs the STATE-line count FAILS (eq 3844 /
  neq 18554). Slot byte0 == item kind (0=TEXTITEM, 1=SHAPEITEM): 4900/4900
  positional agreement. tag==0 u32@+1 resolves verbatim through the interner
  pool ds:0x6fda8 to the file item's literal name: 3528/3528 hits ("Play^
  Introduction", "Load^Game"+"Alt-L", "Species", ...). Windows ever having
  records == exactly the 15 file windows with item lines, both directions.
- CODE IDENTITY: parse block 0x57ee6..0x58062 (entry fn 0x575e4) is the
  WINITEMS/TEXTITEM/SHAPEITEM builder: 0x3101 "%s %d" scans WINITEMS (loop
  bound), 0x3107 "%s %d" scans the item kind (file values only {0,1}), 0x310d/
  0x3119 "%s %d %d %d" scan the name+int triple; fn 0x31690 = item appender
  (gate "[eax+0x9f]>>16 >= 4" is the u16 counter at +0xa1 — a max-4-items cap,
  NOT a window-type check); fn 0x31384 = paint-time item renderer.
- THE PARADOX: assert 0x5804c (-> 0x2a438 with eax=0 -> 0x76c79 -> int3 0x2a424)
  is reachable only for item kind > 1, which shipped windows.txt never contains;
  `STATE 1 16` never touches this block. t334's STATE-array reading was a
  mis-attribution of the item builder; its census families (0,1,0,0)/(1,0,0,0)
  WERE item records (t334's own S9 flagged them as non-pointers).
- t333 CORRECTION: "windows.txt text IS resident in saves (member 0x39db51)"
  does NOT reproduce — NUMCONTROLS occurs in 0 of 284 save dirs' Memory members;
  only C-literal fragments ("BatModeWnd\0" next to "..\batcon.cpp") are resident.
  File-vs-RAM diffs must use the on-disk file as truth, joined by window NAME.
CONSEQUENCE FOR OQ-016 residue-(1): the STATE line has NO parse-time consumer in
fn 0x575e4 at all (that block builds items); the residue question is now purely
"who reads the STATE ids", with the control-table ([win+0xab], t333) and item
array (win+0x6d, t335) both ruled out by measurement.

## S55 t336 (2026-11-08) — THE STATE IDS LIVE IN THE GLOBAL WINMGR PER-ID
## HANDLE TABLE (winmgr+0x3068/+0x306a + 0x8e*id), WRITTEN BY fn 0x57194 FROM
## PARSE BLOCK 0x59021; CENSUS 196/196 SAVES AT W=0x2bc3e4
Zero capture (static disasm + offline census). STATE line = count + N ids
(fmts '%s %d' 0x85fdb then '%d' 0x85fe1), parsed in the PARENT block's
fallthrough 0x58f67->0x59021; per id call 0x57194(winmgr, id, handle=[ebp+0x41]).
Geometry verbatim: stride id*0x8e, u16 count @+0x3068, 32 u32 handle slots
@+0x306a, global distinct-id counter winmgr+0x4226; asserts :0xb37 id<0x20,
:0xb38 handle<0x400, :0xb5a slot overflow; remover 0x57284 mirrors.
MEASURED 196/196 saves (scripts/r336d_state_census.py, exit 0): table at
W=0x2bc3e4 in every save dir; 16/18 ids EXACT file-order (incl. id 16 battle
family verbatim); id 1 prefix+appended by runtime windows (EVENTWIN, Go^to^
Planet, OK) in 16 saves; id 17 slot-substituted (Leave Orbit/Abandon/Cancel
over PLSQBUT0..2) in 22 saves; sum(counts)=135=file tokens; +0x4226=18=
distinct file ids. The table is LIVE runtime state, not a file mirror.
CONSEQUENCE OQ-016 residue-(1): STATE-line value disposition CLOSED by
measurement (global per-id table, located and count-reproducing); the row's
remaining edge is the mode-1 arming witness AND the table's READERS (t337).

## S56 t337 (2026-11-08) — THE STATE TABLE'S READERS ARE THE SCREEN ROUTING
## MACHINERY: CURRENT-STATE WORD core+0x4228 FOUND AND MEASURED {0,1,16,17},
## STATE SWITCHING = RING-A CODE-1 PARAM=STATE, NO BROADCAST EVER TARGETS
## GROUP 16, t333'S "NO GLOBAL ACTIVE-STATE DATUM" SUPERSEDED
Zero-capture iteration (static whole-image walk + offline census; tools
scripts/r337_state_readers.py exit 0, scripts/r337_state_word.py exit 0;
working doc docs/re/_wip_t337.md S0-S7). Sitting check NEGATIVE (newest turn
1086 == corpus). PROVED:
1. GEOMETRY: dword core+0x4226 is TWO u16s — LOW = distinct-group count
   (`inc WORD` 0x57207 / `dec WORD` 0x5711e only), HIGH = core+0x4228 = CURRENT
   STATE ID. +0x4228 has exactly THREE touchers image-wide: writers 0x56f66
   (`mov WORD PTR [esi+0x4228],di`, fn 0x56e10 SET-STATE) and 0x570c2 (=0xffff,
   fn 0x57094 clear-group), plus reads 0x56e20/0x56f39/0x570b9. t336 read the
   dword as one word; the sar-0x10 idiom at all 17 other +0x4226 sites reads
   the CURRENT STATE, not the count.
2. READER INVENTORY (16 functions touch +0x3066/0x3068/0x306a/0x4226/stride-0x8e;
   bodies verbatim work/r337_fnbodies.txt): fn 0x56e10 SET-STATE(core,edx=new
   state) — leave/enter broadcasts msg 2/1 via 0x56b5c, per-group LEAVE cb
   +0x30f0 / ENTER cb +0x30ec calls, 16-deep history ring core+0x4736, focused-
   handle msg 6; fn 0x57020 POP-STATE; fn 0x56b5c BROADCAST-TO-GROUP (walks 32
   slots of group edx, window vtable [win+0xa7]+8, re-entrancy byte 0xa2024+g);
   fn 0x56ca4 POST-TO-HANDLE (the t331 msg path); fn 0x56890 HIT-TEST (mouse
   ds:0x484ec/0x484f0, item rects [win+0x67]/count+0x69, focus core+0x3002,
   current-state fallthrough walk at 0x569d9); fn 0x56d8c FIND-BY-NAME-IN-STATE
   (callers 0x24fdc 0x2670b 0x27565 0x276f3 0x27ebb 0x28f00 0x363bd 0x3643e
   0x36476 0x52742); fn 0x574a4 window-record free (`dec WORD [core+0x3000]` —
   the t316 +0x3000 law home).
3. SET-STATE CALLERS (arg-traced verbatim): boot 0x21733 edx=0 (fn 0x20fd4,
   program-entry trampoline 0x7b7d7; same fn wires ENTER cbs for groups
   {0,1,2,3,4,7,8,9,a,c,d,e,f,10,12,14} via 0x57464 — NO group-16 cb);
   hotkey 0x54d92 edx=2 / 0x54dba edx=4 (fn 0x54d18 keyed WORD ds:0x484c4,
   guarded current!=8); RING-A resolver arm 0x55ea3 edx=record param.
4. RING-A LAW: poster fn 0x56ad4(core, edx=CODE, ebx=PARAM) 44 sites; the
   resolver's code-1 arm's edx IS the record's u32 param — STATE SWITCHING IS
   A CLICK-POSTED RING RECORD. Static param-0x10 (=state 16) posters: 0x28ed8
   (star-select fn 0x28e70), 0x51ad1 (fn 0x51674), 0x5200f (fn 0x51b04),
   0x36b0b (fn 0x36a90); all prime ds:0x43504 first.
5. MEASURED (scripts/r337_state_word.py, 537 saves, base fingerprint = t336's,
   B=0x2bc3e4 537/537, group count 18 everywhere): CURRENT STATE histogram
   {0:122, 1:236, 16:5, 17:174}; group[state] residency 537/537. The 5
   state-16 saves: work/r1/t299-leg-20261105-112859/save/43..47.sav. THE GAME
   DOES ENTER THE BATTLE SCREEN STATE IN RECORDED PLAY.
6. ALL 9 fn 0x56b5c broadcast sites name FIXED groups {1,2,3,4,5,d,e,f,e}: NO
   IN-IMAGE BROADCAST EVER TARGETS GROUP 16. The mode-1 arming chain (t331) is
   not state-table-gated; t332's zero-witness now has a measured candidate
   explanation — every t332-leg save sat in states {0,1,17}, so state-16
   hit-testing of BatControlWnd never ran in that capture. NEXT = live drive
   on the resident state-16 save, not another static walk.
NOTE BatControlWnd magic-rec bytes in state-16 saves: +0xb7=253/+0xb9=1
(identical in all saves; accessor-rec vs magic-rec base distinction from t316
law (3); the STATE word itself is base-unambiguous).

## S57 t338 (2026-11-08) — STATE-16 LIVE DRIVE: THE MODE-1 CHAIN IS ZERO IN
## BATTLE STATE TOO (SECOND INDEPENDENT ZERO); THE STATE-16 TRIGGER IS THE
## GALAXY-MAP ICARUS PIP CLICK; SET-STATE edx=0x10 WITNESSED LIVE
ONE scratch debugger session work/r1/dbg-t338-20261107-224027 (rc=0 attempt 1,
tool scripts/r338_state16_session.py composing r332_batctrl_session.BatSess;
private Xvfb :97, own ring, core=normal, tl 7200; teardown SIGKILL recorded
pids dosbox 200239 / xvfb 200235; production :9 136357/136359 + Xvfb 1461
ps-verified untouched; sitting check NEGATIVE turn 1086).
(1) TRIGGER FOUND FROM EXISTING DATA (zero-capture, _wip_t338 S1): the five
    state-16 saves of t299-leg-20261105-112859 (43..47.sav) sit EXACTLY inside
    the star1 census window — click (238,282) ENTERS the Icarus system view =
    state 16 (save mtimes 11:32:59..11:33:39; Escape exits, 48.sav state 1).
    Reproduced THIS run: enter diff=94504 (t307 verbatim), STATE-ORACLE
    sav=56.sav state=16 groups=18; 13 consecutive oracle reads held 16 through
    the whole A battery + B_pre.
(2) STATE-SWITCH EDGE WITNESSED (t337 law corroborated live): leg
    setstate_56e10 fired once, STOP eip=0x216260 eax=ebp=0x2bc35c (core)
    edx=0x10 ecx=0x10 — SET-STATE fn 0x56e10 entered with new-state 16 seconds
    after the enter click. ringa_55ea3 census x1 (pty whole-log; banked stop
    attributed to setstate — the call-site stop and the entry stop collapsed
    into one banked event; both legs fired per whole-log census).
(3) STATE-16 HIT ROUTING WITNESSED: hit_test_56890 fired x2 (eax=0x2bc35c,
    edx = click Y 0x76/0xc8); btn_hdlr fired 17x on the state-16 family rows
    with window names My^Items/Other^Items/Auto/Pass/TOGGRID/BATZOOMIN — the
    SAME pixels t332 measured as NEXTTURNCONT-owned in state 1. focus_56aa4
    zero (xsend sends ButtonPress+Release at the same coordinate; the
    [esp+4]==-1 clear-focus arm never took the clicked path — unattributed
    beyond that).
(4) THE HEADLINE (OUTCOME C): with the game MEASURED in state 16, the pty
    whole-log census at all eight t332 chain legs {fn156d4_entry 0x156D4,
    tbl15ef1, gate15fed, post1615d, relay1616f, post161d1, mode1_1b7dd,
    backch_1b180} is ZERO; control btn_hdlr x17; BatModeWnd magic-rec
    +0xb7==1 in 0 oracle reads (batrec.json, before/after every click). t337's
    candidate explanation for t332's zero (wrong screen state) is REFUTED as
    the cause: state-16 hit-testing DID run and fn 0x156d4 (BatControlWnd,
    registry slot 61) STILL received no message of any id. SECOND independent
    zero-witness. The arming question now moves INSIDE fn 0x156d4: the
    msg-0x1c01 branch 0x15ebf was never entered because no 0x1c01 was ever
    delivered — and t332's self-relay tail 0x16162..0x1616f is downstream of
    that branch, so the sole live edge is who posts 0x1c01 to slot 61 given a
    click that DOES reach the window family (rows route to child button
    records, never to the BatControlWnd parent record itself).
(5) BATTERY NOTE (banked law): every state-16 row click hit a CHILD record
    (My^Items/Other^Items/W..I/Pass/Auto/Repeat interior) — the parent
    BatControlWnd (0,0-0,0, TYPE 19) has no own rectangle to receive a hit;
    a mouse-road click can therefore NEVER stop at fn156d4_entry via these
    rows. Entry would require the self-relay or another window posting 0x1c01
    to slot 61 — consistent with zero x two runs.
LEDGER: nothing closed strict-close (16/3); OQ-016 residue-(1) REWRITTEN: the
state-16 hypothesis is spent, closure-class = fn 0x156d4 internal-gate decode
(zero-capture) or user ruling D2-c. Tools: scripts/r338_state16_session.py
(exit 0; --offline replay supported). Working notes docs/re/_wip_t338.md S0-S4.

## S58 t339 (2026-11-07) — BatControlWnd INTAKE DECODED (ZERO CAPTURE): NO
## POSTER OF 0x1c01 TO SLOT 61 EXISTS; THE MODE-1 CHAIN IS UNREACHABLE BY
## CONSTRUCTION; THE 804..813 SENDMESSAGE VALUES ARE DORMANT DATA
Static iteration over work/r331_disasm.txt (140,824 insns) + windows.txt +
saves. Tools: scripts/r339_intake_census.py (exit 0, work/r339_intake.out),
scripts/r339_cfg156d4.py, scripts/r339_xreach.py (work/r339_xreach.out),
scripts/r339_dump.py, scripts/r339_rec_census.py (exit 1 = instrument
negative, S7). Working notes docs/re/_wip_t339.md S0-S7.
(1) THE PARENT-SLOT LAW (verbatim x3 parser sites 0x59012-0x59017 /
    0x59618-0x5961d / 0x59726-0x5972b): after PARENT-name lookup fn 0x56d1c,
    `mov eax,[parent+0x41]; mov [child+0x63],eax` + fn 0x30c20 links the child
    into [parent+0x67] (20-slot pointer array). So My^Items w+0x63 == 61 =
    BatControlWnd's slot BY CONSTRUCTION (t316 measured the same field for
    STATSHIPLST==95 live; t316 amendment clause (1) forbids any save-axis
    registry witness — confirmed directly in S7 below).
(2) THE GENERIC ROUTER (fn 0x30c9c span, reached via the 0x336b4 dx-chain;
    sole caller 0x30b57 inside ctor-path fn 0x30ad8): msg 4/5 arm 0x30e0e and
    msg 0xc arm 0x30f46->0x30edc rect-test then POST [w+0x63] the child's
    SENDMESSAGE WORD ([w+0x45]) + SENDPARAM1 ([w+0x47]) verbatim (0x30ecb);
    msg 7/8 arms (0x30de2/0x30dbb) NEVER parent-post (self msg 3 only when
    [0x39]&&[0x35]&&[0x3d]). t302's "msg 0xc -> 0x30edc" law fully explained.
(3) THE ROAD IS STRUCTURALLY BLOCKED FOR THE BATTLE FAMILY: (a) pump
    parent-priority fn 0x56b5c 0x56c34 verbatim — `[w+0x63]!=0 && msg>2` ->
    child SKIPPED (msg bubbles to parentless windows; the only 4/0xc posters
    0x54aa9/0x54ab2 feed through the pump, t318); (b) the parent BatControlWnd
    rect is 0,0-0,0 so fn 0x336b4's rect-test fails every real click; (c) the
    children (TYPE 0/32) have no custom code (class slot 2 = fn 0x336b4).
    => 804/805/807..813 can never reach fn 0x156d4 from observable traffic.
(4) THE 0x1c01 ANSWER (assignment headline): whole-image literal census
    0x1c01/0x1c02 = 18 sites = 14 receiver cmps + 4 senders {0x16168 self-post
    inside fn 0x156d4's OWN gate tail, 0x33374/0x3338e STATSHIPLST emit ->
    slot 95 (t316), 0x35696 LOADSCREEN (t315)} — t315's inventory reproduced
    exactly, NO new poster. windows.txt SENDMESSAGE full census: 39 distinct
    values, MAX 1006 — no file value >= 0x1c01. The only posts of 0x1c01 into
    slot 61 are the gate tail's own re-posts (self-bootstrap).
(5) CFG PROOF OF UNREACHABILITY (scripts/r339_cfg156d4.py + whole-image
    j-edge index): in-edges to the gate block {0x15fed, 0x16147, 0x16181} are
    ONLY 0x1608e je + 0x16071/0x16145 jmp (all INSIDE the block); entry to the
    block is ONLY the rebased 0x15ef1 jump table from the 0x1c01 branch
    (members [0]=0x15ef9 [1]=0x15fed [2]=0x16181 [3]=0x15ef9, t331 live).
    External first arrival: ctor fn 0x15630 zeroes b9 (0x15a0 store), so
    al=b9-1=0xffffffff >3 -> default exit 0x15b39. The b9 2/3 writers
    0x15f1e/0x15f25/0x15f35 are INSIDE the gate block (bootstrap-only). The
    msg 0x320 posters (which CAN set b9 2/3 via arms 0x15b48/0x15b1e) are all
    BatModeWnd back-posts {0x1b164, 0x1b202, 0x1bb5e, 0x1bf80} targeting
    [[BatModeWnd+0xab]+0x41] = the STATE-TABLE slot — and BatModeWnd's state
    table is NULL at t=1086 (t331: 20/20 saves), so those posts never executed
    (they sit on b7-clearing paths — consistent with b7==1 ZERO in t332+t338).
    t331's open question ("which branch flows into the gate block; 0x16181 has
    NO direct j-edge") is CLOSED: 0x1c01 branch via table member; 0x16181 is
    table-only.
(6) WHAT 0x324/0x325 DO (data-matched receiver legs): 0x324 My^Items ->
    0x158c0 {if b9!=1: b9=1, fn 0x16cf0 child shape-redraw (string-id 0x13e),
    self-post msg 0}; 0x325 Other^Items -> 0x158f3 {same, b9=4}. 807..813 have
    NO branch (sub-tree 0x162ac arms only 0x322/0x323/0x324/0x325 then
    0x163f4/0x16410 arms 1/0xd/0x320; default 0x1573b -> fn 0x336b4 generic).
(7) SAVE-AXIS NEGATIVE (S7): 41..49.sav contain ZERO occurrences of
    My^Items/BatControlWnd/STATSHIPLST/FLEETWND/COSMOSWnd/magic 0x12345678 —
    window records are NOT persisted at all (t316 clause (1) corroborated for
    the whole family); assignment step (1) (save census of [w+0x63]) is dead-
    by-law, not instrument bug.
LEDGER: nothing closed strict-close (16/3); OQ-016 residue-(1) REWRITTEN —
EIGHTH cited-dead leg (no-poster + unreachable-by-construction); closure-class
= user ruling D2-c alone. REFUTED-ROUTES t339 amendment (3 binding clauses).

## S59 t360 (2026-11-09) — SAVE-SIDE SHIP-ARRAY LAW (t360, MEASURED 2026-11-09, production ring
work/r1/playcap/save/41..60.sav, turn 1086, 20/20 base-verified via the
anchor vote; full detail docs/re/_wip_t360.md S2):
  L1 The reader stack is live in the rewrite: rewrite/src/formats/shipsave.
     {h,cpp} (ZIP Memory-member inflate, findImageBase anchor-vote port,
     parseShipRecords full-window). Cited fields only; UNKNOWN gaps unmodelled.
  L2 The count word (ds:0x43489>>16 == 30 here) is NOT the fleet census:
     4 live records sit at indices >= 30 (slot indices 1..33 live). Full-window
     scan + dead-marker filter is the parse law (confirms fleet-list item 3
     save-side: named Eregion/Ereinion/Escutcheon B rows were the witness).
  L3 Dead/free marker: u32@+0x54 == 0xffff0000 (NOT 0xffffffff; the low u16
     is 0), race byte 0xff, uniform (kind,cap,filled) == (0,5,0) on 1540/1540.
     Live attribution (handle>>16 == byte@+0x56): 600/600 (t273 re-confirmed).
  L4 FILLED-LAW ARTIFACT RESOLVED (supersedes the DISPUTED flag in
     pership-spec §1 +0x15e): filled == count(cidx!=0xFF over 0..cap-1) on
     600/600 rows here, while §18 measured INCLUSIVE 1234/1234 on the t184
     campaign. Both are consistent: the 25-slot ring ends exactly at +0x15a
     where the CAP dword begins, so a stride-7 probe at slot index == cap on a
     cap==25 row reads the cap word's low byte (==25, never 0xFF) — a self-read
     that inflates every cap==25 row by 1. On cap<25 rows index==cap is a real
     ring slot (the genuine 100 phantom rows live there). Consumers must treat
     probe(idx==cap) as inventory ONLY when cap < 25.
  L5 PORT TRAP (binding for any future Python->C++ port of r1_sav_scan):
     build_anchors' zero law is w.strip(b"\x00")==w — strip trims END bytes
     only; middle zeros pass. An anywhere-zero port gets 0 anchors.
  Corpus pin (frozen turn-1086 ring, self-skips when the game advances):
     B==0x1bf4d8; per-save live 30 / dead 77 / 4 beyond count; kinds
     {3:4,4:3,5:23}, owners {0:14,1:7,2:9}, caps {10:25,15:1,25:4}; window
     md5 54bea6e3e9cd66236dd3ff0d6ba34738 / FNV-1a64 0x3acb4b625a289f54 over
     0x6b*0x162 B. Test: rewrite/tests/test_shipsave_t360.cpp (x3 cases,
     run_tests 179/0). Census tool: scripts/r360_save_shipcensus.py.
