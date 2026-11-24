# _wip_tPLB1.md — PLANET BUILD LOOP: tile-click ORDER LAW (derive + port)

Task: STATE.md NEXT ACTION tPL-B1 (D26: "double-clicking a square doesn't do
anything, so I can't build anything"). RE-FIRST discipline: the STATE text
asserts a "content-dependent POPUP" at the tile click; the vendor msg-map
says otherwise (below) — recorded as a correction, not silently followed.

## F1 — THE TILE CLICK IS NOT A POPUP: IT IS ORDER STEP 2 (msg 0x1c01)
[verified work/t198_planwin.asm head 0x3aa4c..0x3aaa + branch 0x3b3b6..0x3b50d]

Command fn 0x3aa0a(EAX=widget/planet-edit obj, DX=msg, EBX=msg*3 stride,
ECX=param, EDX high word carries the sub-id). Dispatch tree legs
0x3aa4c..0x3aa9b: msg<7 | 7..0x32 | <0x1c01 | 0x1c01 -> 0x3b3b6 |
0x1c02 -> 0x3b50e | default -> 0x336b4.

windows.txt (work/r1/game/windows.txt ln1620-1712): PLSQUARE has SIX TYPE-0
children PLSQBUT0..5 (MOUSEFOCUS 1, SENDMESSAGE 0). A click on a
MOUSEFOCUS child sends the PARENT's SENDMESSAGE (1) -> 0x3aa0a msg 1... the
0x1c01/0x1c02 sub-ids are the winmgr-composed forms (msg | window-slot<<8
[inferred]; 0x3aa77 EBX = obj + msg*3 proves the stride, slot byte identifies
the sending record).

BRANCH 0x3b3b6 (msg 0x1c01 — the tile click) VERBATIM:
  al := BYTE[rec+0xb2] -> rec+0xab   (copy current-item into pending field)
  ebx := WORD[rec+0xae]             (the CELL field)
  IF ebx == 0xffff (NO CELL SELECTED):
      IF al == 0xff -> 0x3b4ab refresh only (nothing pending: click does
        NOTHING — exactly the user's experience on our build)
      ELSE flags := WORD at 0x73e46 + (al*5)*8, mask 0x2   [item-table flags]
        IF flags&2 == 0 -> 0x38840(cmd ecx=2, edx=0xffff, ebx=al): order
          lands WITHOUT a cell (orbital/no-cell class); rec+0xab := 0xff
        ELSE -> 0x3b4ab (item needs a cell; click alone does nothing)
  ELSE (CELL SELECTED, ebx != 0xffff):
      0x3830c(planet=0x43508, item=rec+0xab, cell) -> legal?
      IF legal (eax == -1):
          0x38840(ecx=2, edx=cell rec+0xae, ebx=item rec+0xab)  <- ORDER
          rec+0xab := 0xff; rec+0xac := 0xffff; rec+0xae := rec+0xac
      IF illegal: reset fields only (0x3b487) — REFUSED silently
  tail 0x3b4ab: 0x56ca4(0x7a35c, win rec-0x18+0x41, msg 2, 0, 0) repaint.

BRANCH 0x3b50e (msg 0x1c02): reads BYTE[obj+0xb2]; if != 0xff queues event
0x56ad4(0x7a35c, code 5, ecx 5) — the "cell picked" notification.

CONSEQUENCE (the real law D26 asked for): the vendor build loop is the
documented two-step (planet.txt info04 ln174-177 "choose it from the list,
and then click on the colored square"):
  step 1 selects the ITEM (writes rec+0xab analog),
  step 2 (tile click) CHECKS legality (0x3830c = the build checker incl. the
  F3 adjacency leg 0x385b7..0x3870d) and WRITES the order (0x38840 reserve
  writer, t341 S1: +0x52 cell / +0x54 item).
No popup window is popped by the tile click in this handler. The
"content-dependent" reading in STATE t428 traced to the SENDMESSAGE-1 leg
never being ported. Hover-highlight law (info02 "Valid locations ... will be
hilighted with a solid color as you move the mouse") is SEPARATE and stays
open (the paint body 0x3b96c lattice loop is where it must live; not needed
for the build loop to CLOSE).

## F2 — GATE-WORD/FLAG IDENTITY CLOSED (income-law.md corroboration)
- 0x73e46 = item-table base 0x73e40 + 6 = the u16 FLAGS word (stride 0x28:
  income-law.md L345-348 "byte0 IND, +1 RES, +2 PROS, +3 MPOP, +4 UPOP,
  +5 REQUIRES, u16 +6 FLAGS, u16 +8 COST"). The code's "5*idx then *8"
  = idx*40 [verified income-law L2432]. FLAG tokens in planitem.txt are
  BIT INDICES (loader SHL accumulation @0x381a6 L784; runtime control: item
  26 word 0x8 == token "3" => 1<<3, item 0 word 0x0 == no tokens, L2435).
- So the 0x3b3f5 leg masks FLAG BIT1 (value 2). Bit1 SET rows CENSUSED from
  extracted/ascend00/planitem.txt (scripts: /tmp/tplb1_flags.py, 39/39 rows):
  {31 Alien Hospitality, 32 Interstellar Trucking, 33 Endless Party,
  34 Scientist Takeover, 37 Lush Growth Bomb} = the NO-CELL items; t341 S1
  independently: "item flag bit1 clear -> +0x52 = cell arg" (reserve writer
  0x38840). Consistent: click-without-cell orders ONLY a bit1 no-cell item,
  else does nothing. Bit2 rows {17 Tractor Beam, 28 Orbital Missile Base,
  29/30 Whoppers}; bit3 rows {18,19,26,27 shields}.
- Checker 0x3830c placement legs [verified income-law L364-375]: FLAG bit0
  item-specific cell ban; occupied cell refuses unless item FLAG bit2; XOR
  law for item<31: (cell < +0x18 surfaceCells) != (item < 22) refuses —
  indices 31..38 EXEMPT from XOR; adjacency legs
  0x385b7..0x3870d = F3 (orderCellBlock, already ported t418b).

## F4 — GHIDRA RE-READ OF FUN_0003830c (tPL-B1, decompile_function 0x3830c)
The full pseudocode CONFIRMS verbatim: (a) the XOR veto leg
`if (item<0x1f && (cell < +0x18) != (item < PTR_DAT_00073e3c==22)) iVar9=0;`
(items 31..38 exempt); (b) the four-probe adjacency block (0x3965c/0x395c4
x4, any neighbour word+2 bit0 set => iVar9=0 refuse) == F3 as ported;
(c) item 38 Xeno Dig exempt from adjacency (`bVar7 != 0x26` leg), item 5 too.
AMBIGUITY [honest]: the two "enable" legs (flag bit0 || race-state==2;
slot byte0 != 0 || item==0xff || flag&2) print as SETTING iVar9=-1 inside a
block that starts iVar9=0 — read literally they would refuse EVERY fresh
surface placement, contradicting t341 S5 (Factory item 0, flag 0, cell 43
RESERVED live) and t340 (Shield completion). Ghidra short-circuit polarity
suspect; the port implements the income-law.md S4 VETO reading (occupied
refuses UNLESS bit2) and marks it [inferred]; bit0's cell-ban is NOT
modelled (race-exception arm unverified, no witness).
UI WIRING (ui.cpp): PLANLIST row click => SET pick (planetPickItem), close
list, NO order (0x1c02 step-1 shape); tile click WITH pick =>
placementBlock + projectOrderable then orderProject; pick cleared after the
attempt either way (0x3b487); tile click WITHOUT pick => tile-select
affordance unchanged. No-cell items (flag bit1 rows 31..34,37) order on the
list pick alone via the 0x3b402 leg — but every bit1 row is REQUIRES-gated
(req 20/254/41/32/62), so early game the leg is inert; pinned in the unit
suite, not the UI witness.

## F5 — ADJACENCY POLARITY IS INVERTED IN THE PORT (tPL-B1, DECISIVE)
Raw asm work/r331_disasm.txt 0x38666..0x386fc (four probes inside FUN_0003830c):
each probe `test bit0; jne 0x386fe` — an ACTIVE neighbour EXITS THE BLOCK
WITHOUT executing 0x386fc `xor edi,edi`; EDI stays -1 = LEGAL. Only when ALL
four probes are inactive/absent does 0x386fc zero EDI = ILLEGAL.
=> LAW (restated): a new surface item MUST ADJOIN an ACTIVE item (CB item 5
and Xeno Dig item 38 exempt, 0x385f6/0x385ff). This is what t43 already
concluded statically (scripts/r1_built_cell_law.py header: "BUILT ITEMS MUST
ADJOIN AN ACTIVE ITEM") and what vendor help says (planet.txt info02 ln54-56
"Squares adjacent to existing structures are larger and indicate valid
locations for new construction").
THE t418b PORT (rewrite/src/ui/planetview.cpp orderCellBlock + its header
comment + test planetgrid_adjacency_t418b "each neighbour REFUSES") encodes
the OPPOSITE polarity. t418b State-B pins pass because they pin the port's
own reading, not the vendor's. THIS ITERATION: an attempted flip + placement
law was REVERTED (git checkout) to keep the suite green — the flip must
change code + enum meaning + the adjacency pins + the ui.cpp report strings
TOGETHER (pins cite "refuses: active neighbour" text in the log line).
NEXT ITERATION (tPL-B1b): flip orderCellBlock polarity (ActiveNeighbour =
LEGAL/adjoins-active; refuse = all-inactive), re-derive the two adjacency
tests from the raw-asm law above, wire the two-step UI (list pick sets item,
tile click = placementBlock+orderProject, clear after attempt, cell-less
items flag-bit1 order without a tile), update ui.cpp list-dim report, witness
scripts/tPLB1_buildloop_witness.sh (pick Factory -> non-adjacent tile
REFUSES; adjacent tile ORDERS).
cmd-identity note [verified raw asm 0x388ba..0x388cc]: the UI calls 0x38840
with ecx=2 = CMD2 (dispatch jb/jbe tree; cmd0=0x388e2 is the governor-buy
path with the queue-empty gate). The cmd2 writer 0x38a9f..0x38b26 is t341 S1
verbatim (flag bit1 clear => +0x52 := cell arg; +0x54 := item). The port's
orderProject models the cmd2 effect; the cmd0 gates cited in planetview.h
belong to the 0x38818 chain, not to the tile-click call — keep both, label
correctly while editing.

## F6 — OUTCOME (honest negative)
No OQ row closed this iteration (strict-close): the build-loop law is
derived and banked (F1-F5) but NOT shipped — code reverted, pins unchanged,
witness not run. tPL-B1 REMAINS OPEN as tPL-B1b with the complete port spec
in F5.

## F3 — PORT LAW (what tPL-B1 ships)
THE TWO-STEP, verbatim from the msg map — the vendor pops NO menu at the
tile click (the t428 "content-dependent popup" premise is VOID for the
build path; it conflated the SENDMESSAGE-1 blit leg with an order popup):
  1. PROJECT LIST row click sets the SELECTED ITEM (rec+0xb2 analog) and
     closes the list. NO order lands yet (orderProject is NOT called here).
  2. TILE CLICK with an item selected: run the placement checker
     (XOR law + occupied-unless-bit2 + F3 adjacency); allowed =>
     orderProject (cmd0 gates 1-3 inside: queue empty 0x388e2, item<39
     0x388ec, free pop 0x388f7..0x38922) => order recorded; refused =>
     SILENT refuse + clear the selection (vendor resets +0xab/0xac/0xae on
     the refuse leg 0x3b487, SOUNDCHANNEL 0).
  3. TILE CLICK with NO item selected: tile-select affordance only (the
     vendor does nothing for orders; our grey hover law already matches,
     per D26 — kept unchanged).
  4. ITEM SELECTED but no cell + item FLAG bit1 (specials 31..34): order
     lands cell-less (0x3b402 leg); bit1-clear items wait for the tile.
Field semantics map: rec+0xab working item / +0xae cell / +0xb2 list pick
[verified sites above + decompile work/coswnd_decomp/3aa0a.c L535-566 which
confirms the branch verbatim]; the port keeps ONE pending-pick variable (the two
copies are a vendor repaint artifact [inferred]). CORRECTION (decompile):
+0xab/+0xac/+0xae are cleared on BOTH the accept and the refuse leg (the
clear at 0x3b487 is unconditional after the 0x3830c test) — the port clears
the pick after every order attempt.
WITNESS: scripts/tPLB1_buildloop_witness.sh — seed 5 home planet: open list
-> pick Factory (row 0) -> click SURFACE tile => ordered line (positive);
re-pick -> click a tile ADJACENT to the ordered one => refused line (the F3
leg). XOR-refuse of orbital items has NO UI witness early-game (every
orbital row is REQUIRES-gated, planitem.txt) — pinned in the unit suite
instead, honestly.

## F7 — tPL-B1b RE-DERIVATION FROM RAW ASM (this iteration, work/r331_disasm.txt)
Full leg chain of checker 0x3830c read raw (0x38444..0x38714), EDI!=0 == LEGAL,
return 0x38706 mov eax,0xffffffff when EBP==0 || (EBP&&EDI):
  - rule A 0x38446: item FLAG bit0 ban SKIPPED when bit0 set... [leg reads
    `flags&1 jne 0x3848e(set)` — ban arm + race-state==2 exception; NOT
    modelled port-side (race-exception arm unverified, tPL-B1 F2 stands)].
  - rule B 0x38493: slot byte0 != 0 sets EDI:=-1; item 0xff exempt; item
    FLAG bit2 skips the leg. POLARITY AMBIGUITY BANKED (drawCbCell comment
    reads B as a zeroing rule, t43 reads it as enabling; F5's decisive
    reading + the steering leg-list "occupied-unless-bit2" keep B as
    occupied-REFUSES-unless-bit2. B never fires in the witness fixtures
    (all-clicked-cells-empty), so it cannot flip the closure either way).
  - rule C 0x384db XOR leg VERBATIM raw (0x384e5..0x38517): only item<31
    (0x384e0 cmp 0x1e ja skips the leg); `setb al = cell<+0x18`,
    `setl dh = item<ds:0x73e3c(22)`, then `cmp eax,ecx; je 0x38519` skips
    the veto, fallthrough `xor edi,edi` zeroes. => booleans DIFFER = REFUSE,
    EQUAL = pass (domain check: surface item on surface cell = true==true
    pass; orbital item on ring = false==false pass; cross combos refuse —
    income-law.md S4 "!= refuses" agrees verbatim).
  - rule D 0x38519: slot word+2 bit3 (rock) zeroes EDI unless item==38.
  - rule E 0x38554: item 36 requires fully-empty slot.
  - rule F 0x38576: item 35 (Automation) leg — NOT modelled (named).
  - rule G 0x385b7 ADJACENCY: cell>=+0x18 jae exit (0x386fe = legal tail);
    own slot word+2 bit0 !=0 -> jne 0x386fe; item 5 je-exit; item 38 je-exit;
    FOUR probes via 0x395c4 (row+1,row-1,col-1,row,col+1 order 0x38624..
    0x38661): each existing neighbour with word+2 bit0 set -> `jne 0x386fe`
    exits WITHOUT executing 0x386fc `xor edi,edi`; fallthrough 0x386fc ZEROES
    EDI. => ACTIVE neighbour = LEGAL; ALL-inactive = REFUSE (F5 confirmed
    independently from raw bytes). COROLLARY THE PORT MISSES: the own-active
    jne-exit is NOT a benign skip — it BYPASSES rule G, so clicking an
    OCCUPIED cell with a non-bit2 item must REFUSE (the t418b port returned
    None there and State-B pinned that wrong reading).
  - cmd arm 0x38a3a (ecx==2, the tile-click writer path): flags&2 -> SKIP
    checker 0x38a65 entirely (bit1/cell-less items go straight to writer);
    checker==0 -> silent refuse 0x38b92. NOTE the dispatch numbering: the
    gates at 0x388e2 (queue empty/item<39/free-pop) sit in the arm reached
    at 0x388ba `jb 0x38b8a` — the raw cmp-chain says they are NOT the cmd2
    arm [honest label correction: planetview.h calls them "cmd0 gates";
    cmd2 = 0x38a3a; keep the gates port-side as the queue-dedup law and
    relabel, per tPL-B1 F5 "keep both, label correctly"].

## F8 — PORT WIRING SHIPPED (tPL-B1b)
planetview: OrderCellBlock {None, Occupied, NoActiveNeighbour} — enum renamed
from ActiveNeighbour (the old name encoded the inverted polarity). Chain now
implements C (XOR), B (occupied-unless-bit2), G (active-neighbour LEGAL,
own-active REFUSES, items 5/38 + ring + no-active-exempt... note: NO active
items at all => rule G zeroes => refuse; the home planet's first build is
Colony Base (exempt) or requires an active CB cell). ui.cpp: PLANLIST row
click SETS planetPick (no order); tile click WITH pick runs
placementBlock+projectOrderable then orderProject, pick cleared after every
attempt (0x3b487); tile click WITHOUT pick keeps tile-select. Report strings
updated to the new polarity.

## F9 — tPL-B1b CORRECTIONS + FINAL SHIP LAW (raw-asm decisive, this iteration)
- ADJACENCY EXEMPT SET IS {5, 35}, NOT {5, 38}: raw 0x385ff `cmp dl,0x23`
  (0x23 = 35 Automation). The F5 line "CB item 5 and Xeno Dig item 38 exempt,
  0x385f6/0x385ff" mis-set 38; income-law.md T42 drawCbCell comment already
  had it right ("Rule G adjacency is SKIPPED for items 5/35"). Xeno Dig 38's
  real exemption is the ROCK leg 0x38546 `cmp dl,0x26`.
- FLAG WORD CENSUS re-run against the RUNTIME table (39 rows; the quick file
  parse that dropped Transport^Tubes shifted indices — loader/loader-test
  39/39 byte-exact stands, OQ-014): bit0 {5,21,35,36,38}, bit1 {31,32,33,34,
  37}, bit2 {17,28,29,30}, bit3 {18,19,25,26,27} (file rows; runtime bit3
  set per income-law S4 "cell FLAG bit3 unbuildable terrain" is the CELL's
  class byte, distinct from the item flag — the port models it via
  cellClasses[cell] & 8, T36).
- cmd DISPATCH NUMBERING settled raw: 0x388ba `cmp cl,1; jb 0x38b8a` ->
  `test cl,cl; je 0x388e2` — the queue-empty/item<39/free-pop gates at
  0x388e2..0x38922 are the CMD0 arm ONLY; cl==1 (demolish) -> 0x389be;
  cl in {2,3} -> 0x38a38; the tile-click UI calls CMD2 which gates on the
  CHECKER (0x38a65) + the bit1 skip (0x38a5a `and al,0x2` = BIT1, cell-less
  items bypass the checker) — NOT on queue emptiness. The port keeps
  projectOrderable's cmd0 gates as its one-project-per-planet law (t406
  pins, planet.txt info04) — label stands [inferred for the UI path].
- SHIPPED orderCellBlock chain (veto reading; enum {None, Occupied,
  SurfaceVsRing, Rock, NoActiveNeighbour}):
  occupied-unless-bit2/0xff (0x38493, income-law S4 verbatim) ->
  XOR item<31 (0x384db) -> rock unless 38 (0x38519/0x38546) ->
  adjacency (ring skip 0x385b7; own-active skip 0x385ee; exempt {5,35};
  FOUR probes, ACTIVE=legal jne-exit, all-inactive = refuse 0x386fc).
  AMBIGUOUS re-grant arms 0x3848e (bit0||race-state==2) and 0x384d6 NOT
  modelled; the veto reading is the only one consistent with t341 S1 (fresh
  Factory reserved legal) AND rule-G zeroing (0/362 census).
- UI miss leg 0x3b3f5/0x3b402: click WITH pick, NO cell -> orders cell-less
  iff FLAG bit1, else refresh-only (pick persists in +0xb2). Port helper
  ordersCellLessWithoutCell; miss + bit1-clear keeps the pick.

## F10 — GRANT/VETO ACCUMULATOR RESOLVED (tPL-B1b, THE decisive correction)
Full EDI trace of FUN_0003830c (raw work/r331_disasm.txt): 0x3831f EDI:=EBI
(-1), but 0x38444 `xor edi,edi` RESETS EDI=0 at the placement-region entry
(ALL paths reach 0x3843a->0x38444). Return 0x38706 = -1 (legal) iff
EBP!=0 && EDI!=0. So the placement region is a GRANT ACCUMULATOR:
  - GRANTS: rule A 0x38446 `mov edi,-1` when item FLAG bit0 OR
    ds:0x12fb3[owner*0x1ee]==2; rule B 0x38493 `mov edi,-1` when slot
    BYTE0 != 0 (THE CELL-CLASS BYTE, T36 — NOT occupancy; occupancy lives in
    word+2 bit0, read only by own-active 0x385ee and rules E/F) OR
    item==0xff OR flags bit2.
  - VETOES (all `xor edi,edi`): C 0x384db XOR (item<31, booleans DIFFER);
    D 0x38519 veto iff (byte0 bit3) != (item==38) — Xeno Dig legal ONLY ON
    ROCK (0x38546 sete/dig arm; normal items refuse on rock);
    E 0x38554 item 36 Terraforming requires byte0==0 AND byte1==0xff
    (barren AND empty; ring slots forced class 1 by T36 -> veto);
    F 0x38576 item 35 requires own-ACTIVE w/ word+2 bit1 [UNMODELLED —
    port Automation is the governor path];
    G 0x385b7 adjacency (polarity per F5: active neighbour = jne-exit =
    NO veto; all-inactive = 0x386fc veto).
  - A is ALWAYS granted for observed play: the t43 barren-build census
    (campaign.h:745: items on barren 263/892 == terrain rate 31.6%) is
    impossible unless the checker grants normal items on class-0 cells, and
    the picker (FUN_0003875c, t43 law) filters by THIS checker. So the port
    models A as always-granted [inferred from measurement] and implements
    only the vetoes.
CONSEQUENCES SHIPPED (supersede F7 rule-B line and F8 chain):
  1. NO OCCUPIED VETO in the checker for the tile click. An occupied target
     passes C, passes D (rock law only), passes E (unless 36), and SKIPS G
     via own-active 0x385ee -> legal. (t43's "built items land on EMPTY
     cells" is a PICKER law, not a UI refuse; the port's queue is
     item-only and completion re-picks a cell, so no overwrite risk.)
     The Occupied enum value is DELETED; Occupied-shape fixtures now pin
     None ("occupancy never vetoes").
  2. Rock veto is RockMismatch (rock XOR dig), not "rock refuses unless 38":
     dig on NON-rock also refuses (0x38519 raw). Ring cells skip D (port
     ring byte0 forced 1 == dig-equal reading agrees with T36).
  3. TerraformSite veto for item 36 unless barren+empty+surface.
  4. 38 Xeno Dig is NOT adjacency-exempt (F9); 35's adjacency exemption is
     real (0x385ff cmp dl,0x23) but its rule F is unmodelled (named seam).
