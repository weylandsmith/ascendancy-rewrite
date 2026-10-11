# Colony income + growth law (OQ-016 halves)

THIS FILE IS HAND-MAINTAINED. docs/re/economy.md is REGENERATED wholesale
by scripts/gizmo_probe.py on every gate run (gate.sh:146) — hand-written
addenda placed there are silently destroyed (confirmed: commit dc9fb13's
87-line loss, and two mid-turn reverts on 2026-10-07). All reverse-
engineered income/growth law therefore lives here; economy.md §1-3 is the
item grammar + grids only (also probe-owned, kept current).

## 6. Colony income recomputation law — FUN_00038ba4 (OQ-016 income half, t18)

Static law [verified, work/ascend_restored.bin disassembly 0x38ba4..0x38f65;
the Ghidra decompiler mangles several slot offsets, so every claim below cites
raw instructions]. Callers: FUN_00037d80 (build/dismantle), FUN_00038840
(governor/slot ops), FUN_00038f68 (per-planet turn tick), FUN_0003a174,
FUN_0003aa0a (system event dispatch).

Planet record stride 123, base = planet-NAME - 0x24 (OQ-014 anchor law).
Slot array pointer = u32[rec+0x10] READ RAW (@0x38c8b `MOV ESI,[EBX+0x10]`,
loop @0x38c7d bounds `u16[rec+0x1a]` = cap; member = ESI+EDX, EDX += 4 —
no -0x88 rebasing, an earlier draft of this section was WRONG). Slot dword:
byte0 terrain class, byte1 itemIdx (0xff = empty), u16 flags @+2 (bit0 ACTIVE).
Item record stride 0x28 at Ghidra 0x73e40 (`IMUL EAX,0x28; ADD 0x73e40`
@0x38c97/0x38c9a): byte0 IND, +1 RES, +2 PROS, +3 MPOP, +4 UPOP, u16@6 flags.

Accounting loop, per slot i in [0, cap):
  empty (item 0xff) @0x38c4d:  i >= u16[rec+0x18]  -> c1e++            (+0x1e)
                               else cls&8           -> nothing
                               else c0++ (cls==0 additionally c20++)   (+0x1c/+0x20)
  ACTIVE (u16 bit0) @0x38cbe..0x38d1f:
       IND  += s8 item.IND  (+1 extra if slot cls==2) @0x38cc4/0x38cce
       PROS += s8 item.PROS (+1 extra if slot cls==3) @0x38cde/0x38cf2
       RES  += s8 item.RES  (+1 extra if slot cls==4) @0x38d07/0x38d17
       item flags&4 -> c24++ (byte +0x58) and NOTHING ELSE for that slot
         (@0x38d23 tests [item+6]&4, jumps past the MPOP block);
       else { if item flags&8 -> c59++ (byte +0x59) @0x38be5; c4a += MPOP }
  INACTIVE with item @0x38c07: skip item 23 (Ship), skip slot flag&2, skip
       item flags&0x40, else c18 += UPOP                                (+0x4c)

Post-loop @0x38d3f/0x38d7a/0x38db5 (slot finder FUN_0003958c = first slot
whose byte1 == k, returns 0xffff if none): if that slot's u16 flag bit0 is set,
  k=12 Hyperpower Plant -> IND  += IND>>1
  k=13 Fertilization    -> PROS += PROS>>1
  k=14 Internet         -> RES  += RES>>1
Governor byte @+0x54 (0xff = none) @0x38df0: value 0x21 -> PROS += IND>>2;
value 0x22 -> RES += IND>>2; value 0x23 -> c18 += (DAT_000743b9>>16).

Compression @0x38e2d..0x38e89 (both channels, ONLY if accumulator != 0;
V==0 skips the block and stores 0): `FILD dword (V+1)` ; `FSTP qword` ; CALL
0x78a90 = pow (stack args base=V+1 at [ESP'+4], exp=0x3FEB333333333333 at
[ESP'+0xc], verified by manual ESP walk; callee 0x78954 = MSVC pow core) ;
CALL 0x76e08 ; `FISTP` back. 0x76e08 is NOT round-half: it sets control word
high byte to 0x1f -> RC=11 = FRNDINT TOWARD ZERO (@0x76e11). Banked:
V = trunc((V+1)^0.85) double. Live check: acc1->1, acc2->2, acc3->2
(trunc 4^0.85 = 2.9970) — all acc>=1 records fit; the earlier
"round((V+1)^0.85)" draft was WRONG (banker's/round would give acc3->3). Prosperity then loses upkeep:
  PROS -= (i16[rec+0x42] SAR 2)  @0x38e8d (arithmetic shift = floor-div 4),
  floored at 0 @0x38eac. Industry and Research are NOT reduced by +0x42.
Research is LINEAR (no pow) — no compression block exists on that channel.

Tail clamps @0x38f01..0x38f58: c4a = clamp(0..100) into +0x4a;
u = max(0, min(u16[+0x42], c4a)) back into +0x42; c18 = clamp(0..u) into +0x4c.
Stores @0x38eb4..0x38efe: +0x1c=c0 +0x20=c20 +0x1e=c1e +0x44=IND +0x46=RES
+0x48=PROS +0x4a=c4a +0x4c=c18 +0x58=c24 +0x59=c59.

POP GROWTH (same tick path, FUN_00038f68, t18): counter word +0x4e accumulates
`+ i16[+0x12]` (per-turn growth from slot ops) and gains +1 for non-owner when
i16[+0x12] < 4; once `u16[+0x4e] >= DAT_000066e4` (Ghidra 0x66e4 = raw word
0x0700 — value NOT yet interpreted; the region is pointer-fixup territory) the
counter resets to 0, u16[+0x42] += 1, plus +1 more if the first ACTIVE slot's
bit0 is set, then capped to +0x4a. `DAT_000066e4` semantics = OPEN below.

LIVE VERIFICATION STATUS (battery scripts/r1_income_fit.py, 139 owned records
across every R1 capture's last slot): accumulator structure reproduces the
empty-slot census family exactly (u16[+0x1e]==10 on 153/153 records — the
cap-cells reservation; u16[+0x1c]==cells on 115/153). It does NOT reproduce
+0x44/+0x48: 52/139 records match, and the dominant residual is exactly
acc=(0,0) vs stored=(1,1) on facility-free owned planets (79 records), plus
one non-monotone point (INDpre 3 -> stored 2). That pattern is NOT producible
by any monotone post-transform of the accumulators, so at least one term is
missing from the loop model — candidates in priority order: (a) species-record
per-planet-type IND/PROS modifiers (species table DAT_00013bc4 stride 0x60
holds nonzero small bytes at +0x15..+0x17 that no code site in the recalc
reads — readers not yet censused), (b) captured slots are load-time stale
values (recalc does not run on load, so early-game values bake a pre-pow
base), (c) an accumulator initialised outside 0x38ba4 (all eight accumulators
are zeroed at entry @0x38bb5..0x38bd0, which argues against (c)).
HONEST STATUS: loop structure banked [verified]; curve and base OPEN.

Rewrite status: campaign.cpp currently charges gizmo/facility IND as file
values with no pow compression and no governor channel; DO NOT upgrade to
round((V+1)^0.85) until the base term resolves — a pow-only upgrade would
regress colony output against captured originals (stored values sit ABOVE
the pow curve at V=0..1: stored 1 where pow gives 1, stored 2 where pow gives
2/1 ambiguously). Blocked-on-decision entry: docs/BLOCKED.md OQ-016-base.

## t19. Residue closure — fresh-colony IND/PROS seeds are scenario
grants, NOT recalc terms [verified 2026-10-07]

w16-write census of planet +0x48 (search_byte_patterns `66 89 4? 48`
mask `FF FF F0 FF`): exactly 0x37f3d (error-wipe), 0x38edf (recalc
store), 0x3a62d (FUN_0003a558 new-planet init copying a 1:1 stack
template into rec fields 0x42,0x44,0x46,0x48,0x4a,0x4c,0x4e,0x50,0x52,
0x54,0x55 — assembly context 0x3a609..0x3a664). Colonization walk in
FUN_00025d30 does read-modify-write v=[rec+0x44]; [rec+0x44]=v+1 on
BOTH linked home records (stride-0x60 table, @0x25d30 decompile tail
loop); ship-completion `INC word ptr [ESI+0x44]` @0x21b85 (FUN_00021ad8)
is a third IND grant. The recalc zeroes facility-free channels (JZ-skip
@0x38e31/0x38e62 keeps the accumulator at 0; stores @0x38ecf/0x38edf
write 0). Captured stored 1/1 arises from EVENT ORDERING:
recalc-at-creation (FUN_00037d80 tail) runs first, then
colonization/completion grants add +1, and no further recalc touches the
planet until a facility changes. Consistent with every grant-side miss.

CONSEQUENCE: the recalc law above (S6/t18) is COMPLETE. The t18-bank
closing paragraph ("curve and base OPEN", acc=(0,0) vs stored=(1,1) 79
records, species-modifier candidates a/b/c) is SUPERSEDED by t19/t20 —
the 52/139 fit was an artifact of scoring grants as if recalc-owned.
[That superseded paragraph existed only inside the probe-regenerated
file; no manual edit is needed to retire it.]

## 6b. Growth law (OQ-016 growth half, t20) — partial, measured

Threshold constant [verified]: DAT_000066e4 = **50** — read at
pointer-law address B+0x82BB0+0x66e4 in 23 captures (always 50); Ghidra
data addr 0x000066e4. Growth counter = i16 planet rec +0x4e.

Accumulation site FUN_00038f68 @0x392f4..0x393ff [verified disasm]:
gate `upkeep(+0x42) < [rec+0x4a]` (else counter reset @0x393f9);
`counter += stored PROS (+0x48)`; `+1 if owner(rec+0x57) != current
player ([0x7458e]) AND PROS < 4`; threshold `CMP counter, DAT_000066e4;
JL -> skip`. On threshold: upkeep +0x42 += 1, +1 more if the FIRST
itemIdx==12 slot is ACTIVE (FUN_0003958c + bit-test
@0x393c8..0x393e4), clamp to +0x4a; counter := 0; pop-raise event
FUN_00055a60(0x7a35c, EDX=0xf) fires for human-owned planets (@0x39396).

LIVE confirmation [captured r1deep-20261005-230146 41..60.sav]:
counters move on PROS-earning turns only (5 planets, +2/turn at
PROS=2); wrap 18->4 = reset-at-threshold then same-turn re-accrual.
ANOMALY OPEN: that 41->42 wrap implies accumulation 36 on the wrap turn
(stored PROS 2 + unknown 34). Pop is NOT an f32 in rec 0x58..0x74
(whole-image +1.0 f32-delta scan on a no-threshold turn: ZERO hits) —
pop storage lives elsewhere in the heap or is int-scaled. NEXT:
whole-image diff anchored on a threshold-hit transition.

Battery scripts/r1_income_channels.py exit 0: IND 138/139 PROS 138/139
RES 136/139 (single miss r1deep-20261005-230146 base 0x26e86a:
accI=3 accP=2 stored 2/1 — grant-interaction edge, banked not hidden).
Model: stored = acc==0 ? grant : max(0, trunc((dbl(acc,f)+1)^0.85) -
(|upkeep|>>2)); dbl(v,f)=v+(v>>1) when first slot 12/13 ACTIVE.

Rewrite upgrade UNBLOCKED for income channels (charge compressed stored
value per colony); growth-model upgrade waits on the accumulation-36
anomaly and pop storage.

## 6c. Growth-counter semantics refined (t23) — accumulation-36 RESOLVED AS ARTIFACT

Raw byte census (ascend_restored.bin, mask 66 89|01|29|21|81|c7|ff mod=1
disp=0x4e/0x50): ONLY writers of +0x4e = 0x37f35 (FUN_00037d80 verbatim
pair-copy site), 0x39315/0x3932b (accrual), 0x3a645 (FUN_0003a558 setup
copy), 0x393f9 (reset 0). ONLY writers of +0x50 = 0x37f31 (same pair
copy), 0x39084 (INC when IND<4 & alien-owned), 0x3909f (accumulate
`[+0x50] += IND + cap(FUN_000394d8)`), 0x3a64d (setup copy), 0x3929a
(reset 0 on governor-1f path), 0x3ad74 (event +200, see below).

=> TWO PARALLEL COUNTERS: +0x4e accumulates STORED PROS (+1 alien boost,
threshold DAT_000066e4=50 -> upkeep+1 (+1 active-CLONING (CORRECTED t27:
flag-bit 0x393d4..0x393e4), reset); +0x50 accumulates IND + growth-cap
gate value (FUN_000394d8: item-table word DAT_00073e48+itemIdx*0x14,
x3 when itemIdx==0x23 AND slot==[+0x52]; -1 sentinel). Gate at 0x390a8:
if cap > [+0x50] -> skip growth (0x392a2: governor 0x1f + IND%10==0 ->
redistribute IND/10 to all records table DAT_00012dda+0x1ee*i, a UPOP
fed event). Live 60-turn series confirms: non-accrual turns FREEZE both
counters; accrual turns move them together; +0x52 = slot index counter.

The t20 "accumulation 36" was measured on turn-transition 41->42 of
r1deep-20261005-230146 where BOTH counters dropped by the SAME 14 --
impossible for accrual, consistent with a WRITER event between the two
captures; the capture starts at 41 so the writing event is out of
window. Deltas across planets differ per-planet (Corpuscle +2, Synthos
-3) -- the counters are NOT the same quantity, confirmed.

Event handler FUN_0003aa0a planet-event switch [verified decompile]:
event 20 (0x14): upkeep +0x42 += 2; event 23: [+0x50] += 200 then
FUN_00038f68; event 24 (0x18): upkeep := cap[+0x4a]; event 48 (0x30):
FUN_00038f68 (per-planet growth pass); event 50: [+0x55] += 1 then
FUN_00038ba4 (income recalc). Colonization sets upkeep := 2 verbatim
(@0x3b0c8 region).

REWRITE IMPLICATION: growth default upgrades to: counter += stored PROS
(alien +1 if PROS<4); at >=50: upkeep += 1 (+1 if first-slot-12 active),
clamp to cap, reset counter. The +0x50 IND-side gate stays open ONLY for
the UPOP-unit pop storage question; pop is NOT in the planet record
(bytes 0x00-0x7a verified) -- next probe: star-record stride-0x1ee table
DAT_00012e10/0x12dda UPOP candidates.

## 6d. Pop storage: static routes exhausted; decisive probe = R1 threshold chase (t24)

NEGATIVES [verified this turn]: (a) no FPU opcode (D8-DF) anywhere in the
image touches [reg+disp8=0x67] or disp32=0x67 — zero raw-census hits;
(b) stride-96 star records never hold a planet pointer (target-scan m41
and m42); (c) player stride-0x1ee block (S+0x12dda, base law re-verified
via threshold constant S+0x66e4=0x32) changed only bytes +0x36/+0x1da
(0x09->0x02, AI-state shaped) across 41->42 — no float moved; (d) 'PLPOP'
occurs in the image only as the window-table name byte @0x84b4b
(windows.txt:1587 TYPE 29 custom-draw widget) — not a data field name.

CENSUS [verified]: max +0x4e EVER captured across ALL 32 r1*/runs = **18**
(r1deep-20261005-230146 41.sav) < threshold 50. NO capture contains a
growth-threshold hit; the pop storage question cannot be answered from
existing windows — it requires an R1 run long enough that +0x4e crosses
50 (at stored PROS ~1-2/turn: >=25 turns per colony growth, AI colonies
accrue the +1 alien boost every turn; a 120+ turn headless run should hit
many). NEXT ACTION queued: threshold-chase capture.

HYPOTHESIS (labelled [inferred], supported by cited facts, NOT adopted):
pop IS the +0x42 counter itself (UPOP units): colonization sets +0x42 :=
2 verbatim (event 50-area write @0x3b0c8); growth threshold event does
+0x42 += 1; event 20 += 2; event 24 := cap; recalc charges (|+0x42|>>2)
off PROS (pop consumes prosperity) — the 'upkeep' reading and a pop
reading are the same word under both readings. Corroborates MPOP/UPOP
item fields being pop-maintenance terms (economy.md header line).
DECISIVE TEST: threshold-chase capture — if at a hit turn +0x42 increments
while UI pop display increments, pop == +0x42 closes the item; rewrite
growth model then replaces the logistic default with counter semantics.

## 6e. POP == upkeep counter +0x42 (OQ-016 pop storage CLOSED, t24 capture)

DECISIVE capture r1deep-20261007-224831 (chase schedule: New Game 75s,
setup 150s, End Turn 511:67 every 15s; save ring read by MTIME, numeric
slot names wrap). Slots 45->46 (one End-Turn interval):
  Hannibal III  4e 48->0  42 3->4   (AI, owner 2)
  Albireo I     4e 48->0  42 3->4   (AI, owner 4)
  Phoebe I      4e 48->0  42 3->4   (AI, owner 3)
  Vernunft I    4e 48->0  42 3->4   (AI, owner 1)
  Millitrin II  4e 40->41 42 2->2   (player, PROS 1)
+0x4a unchanged (18/20/25/22) — the growth path does NOT write cap.
Law [verified live + disasm]: pop = word +0x42 in UPOP units; growth tick:
gate pop<cap(+0x4a) else counter(+0x4e):=0; counter += STORED PROS (+0x48,
post-compression post-upkeep value); +1 more iff owner != current-turn
player ([0x7458e]) AND stored PROS < 4 (the alien-freeloader term: the
observed 4 AI wraps need 3/turn at pop-2 growth, player term 1/turn);
counter >= 50 -> pop += 1 (+1 more if FIRST slot itemIdx 15 CLONING PLANT
 [CORRECTED t27 by raw disasm 0x393ad `MOV EDX,0xf` + FUN_0003958c
 signature regparm2(itemIdx); the earlier "12 Hyperpower" reading was a
 wrong literal — S6's 12/13/14 doubling triple is unaffected]
ACTIVE — NOT observed at this wrap, banked disasm-only, cap-clamped),
counter := 0. Colonization SETS pop := 2 verbatim; event 20 += 2, event
24 := cap. help.txt L2556 '%s has %d free population' consistent with
free = pop - working. RESIDUE (open): per-planet +0x4a cap seed source
(scenario template table; measured mid-game spread 13..28, NOT derivable
from slot census: cap==c1c 0/151, cap~c1e±3 14/151); MPOP/UPOP runtime
column byte (0xff sentinel at item+5, byte4=1 for most items — the +0x4a/
+0x4c accumulators unused by rewrite). REWRITE UPGRADE: campaign.h/.cpp
pop=+0x42 analog, growthCounter=+0x4e, threshold 50, alien+1 term,
colonization :=2.

Runtime item-table dump note: byte5 = 0xff sentinel / small values
(Factory b3=0 b4=1; Habitat b3=3 PROS=2 — byte3 feeds nothing the rewrite
uses; §6 column map stands for IND/RES/PROS which BATTERY-verified).

## 6f. Pop-cap (+0x4a) source analysis (t24b) — seed is world-gen, not recalc

Setup loader FUN_0003a558 @0x3a611..0x3a66c copies word fields 0x42..0x52
VERBATIM from the caller's build struct ([ESP+0x42]->[+0x42], etc. — raw
disasm; recalc does not seed it). Cross-run census across all captures
(61 planet names): cap(+0x4a) stable per planet name 56/61. The 5
exceptions are per-RUN map-RNG variance, NOT accumulation: Hannibal III
shows 22 in 13 runs and 18 in exactly the two runs whose map start
differed (r1deep-20261007-222504/224831 both 18); Ignatius I 15/22 and
Sophia I 28/31 split exactly along the two r1ad setup variants;
Philadelphia I 26/27 splits 224916 vs 230146. Default-option runs share
a deterministic map seed (same caps), option/dud variants re-roll names
->caps independently. MPOP accumulation on top of the seed therefore
remains [inferred] (planitem MPOP values exist: Factory 0, Agriplot 0,
Habitat 3, Metroplex 2, Colony Base 2 — planitem.txt lines 57-73) but is
NOT established by these diffs; recalc's +0x4a addend in FUN_00038ba4 is
the orbital/ability accumulation path banked in S6, no per-item MPOP add
site found there. Mid-game observed spread 13..28
with 0..2 built items => seed itself is 13..25ish per planet.
CONCLUSION [inferred, strongly supported]: +0x4a seed = per-planet value
produced by WORLD GENERATION (OQ-012(a) family / mapgen), carried through
the build struct; MPOP adds per active facility. REWRITE MAPPING:
popCapCap per-planet seed from mapgen when OQ-012 law lands; interim the
rewrite default 25 sits inside the measured envelope [documented default,
flagged, not silent].

## 6g. Build-order / expansion-cadence: capture census NEGATIVE (t25)

Slot-array census ([rec+0x10], cap words at +0x1a; slot = {byte0 terrain
class, byte1 itemIdx, word+2 flags, word+4 sub}) across BOTH long runs —
r1deep-20261005-230146 (t41..t60) and the chase run r1deep-20261007-
224831 (t41..t60): built-item sets are STATIC for every owned planet
across all 40 turn-slots (Corpuscle I {4,5 active; 2,1 inactive},
Tonsberg IV {1,5}, Philadelphia I {5}, others {}). Population(+0x42) and
upkeep counters DID tick (S6e) while items never changed => growth/
income laws are item-build-independent, and NO build event exists in any
of the 32 captures. Build ORDER (policy) and cadence (turns-per-item)
are therefore NOT measurable from existing windows.
FUN_00021ad8 decompile confirms it is NOT the planet-item completion
path: it allocates a ship object (FUN_00024834), stores it into two
owner fleets ([+0x2c+slot*4] and param_2[+0xb]), and increments fleet
count words — the +0x44 INC is ship-count bookkeeping, not income.
Decisive route queued (NOT retried blindly): one click-run scripted to
BUY an item (planet screen -> buy; planitem COST column = resource-turns
per extracted planitem.txt) with slot cadence 10 s, then measure
(slot flags word+2 transition + cost drawdown) per purchase.

## 6h. planitem table index law (t25, verified)
extracted/ascend00/planitem.txt parsed name+data-line pairs -> EXACTLY
39 items, index order = runtime itemIdx: 0 Factory 1 Agriplot 2
Laboratory 3 Habitat 4 Metroplex 5 Colony Base 6 Industrial Megafacility
7 Artificial Hydroponifer 8 Research Campus 9 Logic Factory 10
Engineering Retreat 11 Surface Cloaker 12 Hyperpower Plant 13
Fertilization Plant 14 Internet 15 Cloning Plant 16 Observation Inst
17 Tractor Beam 18 Surface Shield 19 Surface Mega Shield 20 Outpost 21
Transport Tubes 22 Shipyard 23 Ship 24 Orbital Docks 25 Orbital Cloaker
26 Orbital Shield 27 Orbital Mega Shield 28 Orbital Missile Base 29
Short Range Orbital Whopper 30 Long Range Orbital Whopper 31 Alien
Hospitality 32 Interstellar Trucking 33 Endless Party 34 Scientist
Takeover 35 Automation 36 Terraforming 37 Lush Growth Bomb 38 Xeno
Arch Dig. Matches live slot byte1 values {1,2,2,4,4,5} and the
12/13/14 doubling + 0x23 x3 cap rules. Columns: IND RES PROS MPOP UPOP
COST RESEARCH-REQ FLAG (header line 3).

## 4. Planitem AVAILABILITY + item-table law (RECONSTRUCTED t25)

Original economy.md S4 was destroyed by the gizmo_probe regeneration
(see STATE.md banner); every line below is re-verified against the
restored image this turn. Primary source: FUN_0003830c decompile (full
text this turn) + OQ-014 closure ledger (OPEN-QUESTIONS.md).

ITEM TABLE (FUN_00037fc0 loader): stride 0x28 — byte0 IND, +1 RES, +2 PROS,
+3 MPOP, +4 UPOP, +5 REQUIRES, u16 +6 FLAGS, u16 +8 COST, name30 +10.
Pointer-law index: item N at phys B + 0x82BB0 + 0x73E40 + N*0x28 (naive
B+X is 0x88 off). 39 rows, byte-exact 39/39 vs extracted/ascend00/
planitem.txt in 2 captures (ledger OQ-014); index order = S6h above.

AVAILABILITY (FUN_0003830c, __regparm3(planetRec, itemIdx) -> -1 allowed /
0 refused), verified predicates in decompile order:
 1. owner gate: byte +0x57 == 0xFF (unowned) refuses everything except
    itemIdx 5 (Colony Base) and itemIdx 0xFF (demolition, unaff_BX path).
 2. RESEARCH gate [re-verified verbatim this turn]: req = byte +5 of item
    table (DAT_00073e45 stride 0x28); allowed iff req==0xFF, else
    req < DAT_00074744 (==66 restree rows) AND owned-race bit set:
    *(u32*)(req*0x4b + 0x7478b) >> 0x18 & (1 << (owner & 0x1f)).
    254 (Interstellar Trucking) fails BOTH arms -> permanently DEAD item.
 3. POP gate [re-verified verbatim]: free = u16(+0x42) - u16(+0x4c), plus
    byte +3 of the GOVERNOR item row (DAT_00073e41 + gov*0x28) when +0x54
    != 0xFF; allowed iff sign-extended UPOP (byte +4 of item row,
    DAT_00073e41[i]*10>>0x18) <= free.
 4. PLACEMENT gates (slot cell unaff_BX < u16 +0x1a cap). Item indices
    below are DECIMAL; the decompile literals 0x1f/0x23/0x24/0x26 = 31/35/
    36/38 per the S6h index law:
    - FLAG bit0 (DAT_00073e46 stride 0x14) item-specific cell ban; race
      exception when DAT_00012fb3[owner*0x1ee] == 2 (player-block state
      byte, semantics [unverified]).
    - occupied cell (byte0 != 0) refuses unless itemIdx==0xFF (demolish)
      or FLAG bit2 set.
    - XOR law [re-verified verbatim], only for itemIdx < 31:
      (cellIdx < u16 +0x18 terrain cells) != (itemIdx <
      PTR_DAT_00073e3c == 22) refuses — surface items need terrain,
      orbital items (22..30, count 9) need the ring; indices 31..38
      (Alien Hospitality .. Xeno Arch Dig) exempt.
    - cell FLAG bit3 (unbuildable terrain) allowed ONLY for itemIdx 38
      (Xeno Archeological Dig) — matches planhelp/gizhelp alien-dig text.
    - itemIdx 36 (Terraforming) requires a fully empty slot
      (byte0==0 && byte1==0xFF).
    - itemIdx 35 (Automation) requires slot word+2 bit0 SET (active),
      slot byte1 != 23 (not a Ship), and word+2 bit2 CLEAR.
    - itemIdx 23 (Ship): when the research/pop gate PASSED
      (iVar8 == -1 && bVar7 == 0x17), iVar8 is REPLACED by FUN_00039a9c's
      return (shipyard-legality path) — ship build legality lives there.
    Outer ownership gate also exempts itemIdx 5: an UNOWNED planet
    accepts only Colony Base (colonisation entry, matches S6e :=2 seed).
    - adjacency: new item on terrain cell with slot word+2 bit0 CLEAR runs
      FUN_0003965c/0x395c4 four neighbour probes; any ACTIVE neighbour
      (word+2 bit1) refuses.
 5. Research-gate overrides [re-verified verbatim]: itemIdx 5 (Colony
    Base) ALWAYS passes the research/pop gate (`if (bVar7==5) iVar8=-1`
    after the branch chain); itemIdx 23 (Ship) with research-gate still
    refusing gets its legality from FUN_00039a9c (shipyard path) whose
    return reassigns iVar8.
Rewrite mapping ALIVE in code today: economy.h requiresAvailable() ==
gate 2 verbatim; buildPhase gate+surface-cap == XOR law; MPOP gates
demolition, UPOP gates start (0x38840 caller). Citations repointed here
from the destroyed economy.md §4.

## 7. Planet build-command law FUN_00038840 (t26, decompile banked)

__regparm3(planetRec, cellIdx, cmd) with item index passed implicitly in
BL (caller-side load; decompiler shows unaff_BL). cmd values:

 0 = ADD/BUY item into cell. Gates (all [verified verbatim]):
    slot byte1 == 0xFF (empty) AND BL < 39 AND
    UPOP(BL) <= u16(+0x42) pop - u16(+0x4c) used-pop AND
    surface/orbital XOR: (itemIdx < PTR_DAT_00073e3c==22) ==
      (cellIdx >= terrainCells u16+0x18).
    On accept: slot byte1 = item, word+2 = 1 — ACTIVE IMMEDIATELY, then
    FUN_00038ba4 recalc is called in every exit path (LAB_00038b92 and
    each branch). No timer, no progress counter anywhere in the handler:
    build cadence = resource-budget-limited, not time-limited
    [inferred from handler shape + recalc-per-write; a buy-click run
    would upgrade this to measured].
 1 = DEMOLISH cell. Allowed iff slot occupied AND
    ( MPOP(slot item) <= u16(+0x4a) cap - u16(+0x42) pop
      OR slot word+2 bit0 == 0 (inactive) )   [verified verbatim].
    Effect: byte1=0xFF, word+2=0; if cell was the +0x52 selected cell,
    +0x52 := 0xFFFF and +0x54 := 0xFF; recalc.
 3 = SELECT/SET special ability: +0x52 := cell (when item FLAG bit2
    clear), +0x54 := item idx (so +0x54 is the SELECTED-ABILITY field —
    the S6 "governor" naming is retired; recalc values 0x21/0x22/0x23 =
    items 33/34/35 Endless Party / Scientist Takeover / Automation).
 2 = swap selection: same path as 3 after re-running FUN_0003830c
    legality (skip when item FLAG bit2 set); if previous +0x52 slot held
    item 23 (Ship): FUN_000396cc + FUN_00049d2c (ship-order cancel),
    then if old +0x52 slot inactive its byte1 is cleared to 0xFF.
 >3 = error: recalc, return 0.

 Slot FIELD MAP UPGRADED [verified verbatim]: for FLAG bit2/4 items
 (specials): byte3 = 0 AND word+2 |= (FUN_00039b6c result << 8) — so
 WORD+2 UPPER BYTE = ability charge/ammo count (FUN_00039b6c supplies
 initial count). word+2 bit0 = active flag (queue writes 1). A writer
 that CLEARS bit0 (pop-overflow deactivation?) is NOT yet located —
 queued census `and 0xfe` / `mov word[..],0` on slot arrays.
 COST (u16 item+8) is NOT deducted in this handler -> see S8: the
 industry accumulator +0x50 pays it over turns in FUN_00038f68.

## 8. BUILD-QUEUE LAW: builds are industry-time, not free (t27) — CORRECTS S7

S7's "no build timer exists" is REFUTED by the full FUN_00038f68
decompile + live per-turn deltas. The timer is a per-planet INDUSTRY
accumulator, not a turn counter.

 COST IS ITEM-TABLE FIELD +8 [verified by offset arithmetic]: readers
 write `word [EAX*0x8 + 0x73e48]` with EAX = idx*5 -> byte offset
 0x73e40 + 8 + 0x28*idx = item[idx].COST. The earlier reading of
 DAT_00073e48 as a separate "stride-8 growth-cap table" was WRONG
 (0x73e40 is the item-table base). FUN_000394d8 therefore RETURNS THE
 COST of the item in cell [+0x52], with item 23 (Ship) costing the
 ship-design value (FUN_000396cc/FUN_0004a41c) and TRIPLED when the
 queried cell == +0x52 (0x39545..0x39550 IMUL EAX,3).

 ACCUMULATOR LAW @0x3907b..0x390ac (raw disasm authoritative — the
 decompiler mangles these field offsets, showing +0x11/+0x14):
   if (owner != DAT_0007458e && DAT_00013bc4 == 2 && IND([+0x44]) < 4)
       [+0x50] += 1;                      # AI catch-up boost
   [+0x50] += IND([+0x44]);
   cap = FUN_000394d8(rec, [+0x52]);      # = COST of pending item
   if (cap > [+0x50]) JA 0x392a2;         # not paid yet -> no completion
 On payment (fall-through) the pending item's slot is activated
 (word+2 |= 1; if the cell carries the unbuildable bit3 it is cleared
 and byte1 := 0xFF with FUN_00046e84), item-specific completion effects
 run (item 23 Ship -> pop -= DAT_000741dc when ship flag byte+0x58==1;
 item 36 Terraforming -> word+2 := 0, byte1 := 0xFF, byte0 := 1;
 item 35 Automation -> word+2 |= 2; item 37 -> [+0x55] += 10 once),
 then [+0x52] := 0xFFFF and the selected-item byte := 0xFF.

 LIVE MEASUREMENT (chase capture r1deep-20261007-224831, mtime-ordered
 ring, 20 slots covering ~10 in-game turns): every owned planet's +0x50
 rose by EXACTLY IND each turn — IND=1 planets 4,5,6,7,7,8,9,10,11
 (duplicated values are same-turn slots, clicks drive turns), and the
 planet with IND=0-equivalent selection (+0x52=0xFFFF, Millitrin II)
 held +0x50 at 0 throughout. No build completed in-window because the
 pending COST was never reached (item arrays static, S6g). Inactive
 items (word+2 == 0) are common in shipped RAM (Corpuscle I holds two:
 items 1 and 2 both inactive) = builds awaiting payment.

 AI BUILD POLICY [verified verbatim] @0x3f528..0x3f672: loop 39 item
 rows; skip unless (research gate as S4) AND (cap(+0x4a) - used(+0x4c)
 >= UPOP(item)); among survivors it rejects any item whose
 COST(item) / IND(planet) >= 70 (0x3f6e9 IDIV EBX=IND, 0x3f6eb
 CMP EAX,0x46 JGE reject). So the AI never starts a build that would
 take 70+ turns on that planet.

 GROWTH LAW CONFIRMED INDEPENDENTLY of the queue (same function):
 [+0x4e] += PROS(+0x48) (+1 if owner != DAT_0007458e && PROS < 4);
 measured per-turn deltas EXACTLY +3 (PROS=3 planets) and +1 (PROS=1
 planet) across 10 turns; at [+0x4e] >= DAT_000066e4(50): pop(+0x42) +=
 1 (+1 more if the first slot with itemIdx 12 is ACTIVE), clamp to
 +0x4a, [+0x4e] := 0. Threshold hit observed live: 44 -> 48 -> 48 -> 0
 with pop 3 -> 4 (Millitrin, gated at cap, held 40..42 and never
 grew). When pop >= cap the else-path FORCES [+0x4e] := 0 every turn
 (LAB_000393f9) — growth never even accrues at cap.

## 9. AI BUILD SELECTOR LAW CLOSED (t28) — FUN_0003f130 + FUN_0003fc4c + FUN_0003fec4

Full region 0x3f130..0x3f757 disassembled from work/ascend_restored.bin
(capstone; functions_full.tsv entries 3f130 size 973, 3fc4c size 631,
3fec4 size 350). The evaluator region t27 queued is COMPLETE:

 ENTRY (0x3f130, EAX=empire ctx, EDX=planet rec; caller 0x3eade inside the
 per-planet AI turn loop):
   [+0x44]==0 -> return (no industry channel: no build, no queue) @0x3f146.
   FUN_0003f758(ctx,planet) == 1 -> return @0x3f162. 0x3f758 is the
   SPECIAL-PROJECT gate: when planet has NO Shipyard slot (0x3958c(22)==
   0xffff) and (IND<4 or empty(+0x1c)-(+0x20) >= 5) and turn-gate
   (DAT_00012e10 <= 0xAA or race-mask byte) -> BUY Shipyard (0x38818 cmd0,
   item 22) and return 1 (consumed the turn); otherwise (FUN_00039a9c) ship
   production via item 23 + FUN_00040de0 (design). Ship items therefore run
   through 0x3f758 BEFORE the generic evaluator.

 OVER-CAP EMERGENCY (0x3f178): if used(+0x4c) >= cap(+0x4a): scan cells
 < +0x18, skip empty and item 5 (Colony Base); pick cell whose item has the
 LARGEST MPOP (item byte +3, gate >0); FUN_00038840 cmd=1 DEMOLISH it
 @0x3f1e9; if still used>=pop after demolish -> return; free-pop recheck
 @0x3f1fb. Else branch: used(+0x4c) >= pop(+0x42) -> return @0x3f220;
   FUN_0003f758==2 -> return @0x3f226.

 TRANSPORT-TUBES PRIORITY (0x3f2c8): race-research mask (research runtime
 array 0x7478b stride 75 — see layout note below) bit(owner) set -> if no
 slot holds item 21 (Transport Tubes): DEMOLISH whatever occupies the
 +0x1c-counter... actual code: FUN_00038840 cmd1 on the item-21 slot then
 FUN_0003830c(23) legality; when legal place via FUN_00038718; when
 slot-less BUY (0x38818(0,21)) @0x3f344.

 MIN-REQUIRES DEMOLISH SWEEP (0x3f354, entered when free pop exists but the
 over-cap path didn't fire): among occupied cells < +0x18 pick the item
 with MPOP (item dword+0 SAR 24 @0x3f3bd) STRICTLY LESS than cap-pop AND
 the smallest byte+5 (REQUIRES column, ecx sentinel 0x1869f never binds)
 -> DEMOLISH cmd1 @0x3f403; free-pop recheck @0x3f414 else return. (The
 byte+5 min makes research-prereq items the first to go.)

 RANDOM-CELL FALLBACK (0x3f47d): FUN_00038818(0xffff) = FUN_0003875c
 random-legal-empty-cell picker (FUN_0003830c legality over empty slots,
 rng FUN_0x7824f uniform over count). If NO legal cell: if empty(+0x1c)>0
 BUY TRANSPORT TUBES item 21 @0x3f4b3 (tubes create cell capacity ->
 Outpost item 20 path parallel) and return; else return.

 EVALUATOR (0x3f4d3, after cmd1 on current +0x52 target then FUN_0003fc4c):
  FUN_0003fc4c(ctx,planet) returns a forced PENDING ITEM or -1 (full body
  banked in work/ai_selector_disasm.txt): emergency item law — item 22
  Shipyard / 25 Orbital Cloaker chain (0x3fc63 item 22 buy when byte+0x66
  bit1 set), item 18 Surface Shield chain when IND>=4 && PROS>0 &&
  (+0x1c)-(+0x20)>=3 && threat byte+0x59<6, item 19 Surface Mega Shield
  (0x13) when (DAT_00012e10 - [+0x67]) / period > threat (period 200/225/
  300/400 by threat class 0/1/>=4 lookup @0x45beb stride law), item 11
  Surface Cloaker when owner odd && IND>=20 && rng%100<5, else a 5-entry
  template list @RUNTIME 0x67b8 filtered by FUN_0003830c legality; return
  -1 = none forced.
  FUN_0003fec4(planet) returns the NEED CLASS (0..3) — @0x3fec4 verbatim:
    cap(+0x4a)-pop < 2 && pop-used(+0x4c) < 2 -> 3 (pop-crunch);
    PROS(+0x48) < 2 -> 2; IND(+0x44) < 2 -> 1; IND>=4 && PROS>=2: research
    threshold DAT_000066e4/PROS <= 15 && cap-pop>=3 && pop-used!=1 -> 2
    (keep prosperity); else Internet/Hyperpower slot comparison law:
    RES(+0x46) vs IND(+0x44): (Internet slot ? RES>>1 : 0) vs
    (Hyperpower slot ? IND>>1 : 0) -> 1 if RES-side bigger else 0;
    otherwise default 0.
  CLASS->SCORE STUBS (jump table image 0x3f120, RELOCATED live target
  verified: live jmp imm = 0x1fe570 = P0+0x3f120 exactly; restored image
  bytes 0x3f120 = c3f50300 d5f50300 aff50300 9af50300):
    class 0 -> 0x3f5c3 score = item IND    (skip item if IND==0; movsx
            cx,[eax] @0x3f5ca)
    class 1 -> 0x3f5d5 score = item RES    (skip if RES==0;  [eax+1] @0x3f5dd)
    class 2 -> 0x3f5af score = item PROS   (skip if PROS==0; [eax+2] @0x3f5b7)
    class 3 -> 0x3f59a score = item MPOP   (skip if byte+3==0; dword [eax]
            SAR 24 test @0x3f59c, score movsx [eax+3] @0x3f5a3)
   Every stub falls through to 0x3f60a which OVERWRITES word+1 with the
   FULL SUM IND+RES+PROS+MPOP and writes entry byte0 = item idx (5-byte
   candidate entries; word+3 carries the stub primary for the d66 roll).
  CANDIDATE GATE (loop 0x3f528..0x3f592): SURFACE rows 0..21 ONLY
  (word[0x73e3c]==22 bound @0x3f52f; row 5 Colony Base skipped @0x3f52d;
  orbital 22..30 + specials 31..38 NEVER enter this evaluator — they run
  through the 0x3f758 special gate): research-owned (byte+5 == 0xFF
  sentinel OR mask bit, above) AND UPOP(byte+4) <= popCap(word+0x4a) -
  word[+0x4c]. FIELD NOTE: +0x4c sums UPOP of INACTIVE slots only (S6
  recalc: ACTIVE slots never add to c18) = the PENDING queue's pop draw;
  cmd0 buy legality instead uses pop(word+0x42) - [ +0x4c ] >= UPOP(new)
  (0x388f7..0x38922 verbatim) — a purchase with pop already <= pending
  draw FAILS the turn quietly (no queue written).
  PICK LAW (0x3f672..0x3f733): roll = rng % 100 @0x3f67a (FUN_0x7824f =
  LCG seed*0x41C64E6D+0x3039, value (seed>>16)&0x7FFF — full disasm banked).
   For each recorded candidate IN TABLE ORDER:
     if item NOT already occupying a slot (FUN_0x3958c == 0xffff):
        if COST(item) / IND(+0x44) >= 70 -> REJECT and STOP scanning
        (0x3f733, the t27 70-law; rejection ABORTS the whole pick, not the
        row); else PICK IT IMMEDIATELY (absent item wins on first pass —
        scores are NOT compared for absent items).
     if item PRESENT: score = (roll > 0x41) ? entry.word+3 : entry.word+1
        (d66 tie-break: 35% use the stub-primary, else full sum); keep
        running max; tie -> earlier row wins (strict >).
   Selected -> FUN_0x38818(0xffff-cell... actual: 0x3f747 FUN_0x38818
   (dl=selected item, EAX=planet)) = random-legal-cell BUY.

 RESEARCH GATE INPUT (selector + FUN_0003830c checker, same read law):
  dword = [0x7478b + 75 * item.REQUIRES(byte+5)]; gate = (dword >> 24) &
  (1 << owner(+0x57)) (raw 0x3f548..0x3f56e and 0x38378..0x383ad — the
  S4 law's runtime materialisation). MEASURED t28: that byte (restree
  runtime record tail offset +74; 0x7478b = row0-head 0x74744 + 71, stride
  75, row0 = 'Orbital Structures' [verified]) == 0 for ALL 66 rows across
  26 slots x 13 captures — no owner ever held a research-gated item
  buildable in any captured game (all captured items are req-255 rows plus
  colonization-placed Colony Base). Rewrite gates with ownedTech per S4
  (equivalent iff the tail byte mirrors ownership [unverified mapping]);
  captures never exercise the difference.

 LIVE CONFIRMATION OF THE PICK LAW (r1deep-20261007-224831, mtime-ordered
 ring, t35..t42): all four AI planets (Hannibal III, Albireo I, Phoebe I,
 Vernunft I) hold pending +0x54 = 0 = FACTORY with +0x50 = 7..11 rising
 +IND(=1)/turn: Factory is row 0 (first absent row passing research (req
 255) + free-pop (cap-pop 25..80 >= UPOP 1) + 70-gate (30/1 = 30 < 70) —
 exactly the immediate-pick law); player Millitrin II carries +0x52 =
 0xFFFF/+0x54 = 0xFF (no queue: human selects by UI, never auto-queued)
 while its +0x50 stays 0 (@0x39005 +0x54==0xFF -> skip accumulator, raw
 disasm — refines S8: the +IND tick requires a pending item).

## 10. POP-CAP (+0x4a) SEED LAW CLOSED (t29) — world-gen 0x37d80..0x37fa8

Recalc head reads the SEED word +0x55 raw: `MOV AX,[EBX+0x55]` @0x38bd4
into c4a; item loop adds MPOP (skip item flags&4, AND skip Colony Base —
see rule note below); tail clamps 0..100 into +0x4a. LEDGER (t31 FULL
CORPUS RERUN — 298 save slots x every planet = 46132 samples, all 13
r1deep worlds + fresh run): with ACTIVE := slot word+2==1 and CB EXCLUDED,
  `+0x4a == clamp(0,100, [rec+0x55] + sum MPOP(active items, skip flags&4,
     skip item row 5 Colony Base))`
holds 44376/46132 = 96.19%, residual ONLY +2 (1756 samples, no other
value ever); with CB INCLUDED the residual splits 988 +2 / 988 -2 —
reproducing t29's original 38772/40318 = 96.17% signature EXACTLY (a
mid-turn t31 "retraction" was itself wrong: it tested grid-derived
nb//3+5 against +0x55 instead of this recalc equation; un-retracted).
The +2 = event modifier @0x4404b..0x44058 (scan over planets at 0x2b057
stride 0x7b matching owner byte[+0x57] vs event empire @EBP: +2 to +0x55
then recalc; mismatch lists show s=0, +0x4a==+0x55+2 on 2-5 named
planets/world).
RULE DERIVATION (t29, re-confirmed t31 full corpus): with Colony Base
INCLUDED the ledger shows paired ±2 residuals (988/988); excluding CB
removes every NEGATIVE residual (failures become purely +2, the known
event shift) — CB's MPOP=2 is therefore excluded from the cap sum.
[verified data; inferred conclusion.] Runtime
planitem MPOP column (identical in all 13 captures at B+0x82BB0+0x73e40,
i*0x28+3): Habitat(+2), Metroplex(+2), Colony Base(+2, excluded),
Habitat-class rows 3(+3),4(+2),5(+2); rows 17/28/29/30 carry flags&4
(Tractor Beam, Orbital Cloaker/Shield/Mega-Shield class) — measured, not
inferred. The +2 residual class itself = OPEN residue (candidate: uncensus-
able register-offset write to +0x4a; every direct word-writer is accounted).

WORLD-GEN SEED (FUNC at 0x37d80, single caller 0x23b49 scenario init):
  cell loop 0x37e41..0x37eec over word[+0x1a] cells (ORBITAL RING cells,
  index >= word[+0x18], are forced class 1 @0x37f0e..0x37f19 — no rng):
    rng = 0x7824f returns 0..32767 (LCG *0x41C64E6D +0x3039, `SHR 0x10;
    AND 0x7FFF` @0x78269 — CORRECTED t29b: an earlier draft said 0..99).
    Surface cell is BARREN (class 0) iff rng < scaled(w0), where the four
    weights w0..w3 = row [EBX=0x744f4 + 4*word[+0x16]] scaled as
    (w*32768 - w)/100 (`SHL 0xF; SUB; DIV 100` @0x37e51..0x37ea4);
    non-barren cells increment the count ecx @0x37ebb and take their class
    from the CUMULATIVE chain @0x37eb7..0x37ee0:
      rng < w0+w1 -> class 2;  < +w2 -> class 3;  < +w3 -> class 4;  else 1
    so the row's INTENDED shares are barren w0%, c2 w1%, c3 w2%, c4 w3%,
    c1 the remainder.
  ROCK event @0x37f4d: rng%7==0 (idiv 7, test edx @0x37f5c) -> class|=8 on
    rng%(surface-cells) slot; planet flag +0x66 |= 2.
  SEED WORD @0x37f84..0x37f9e: `MOV EBX,3; MOV EAX,ECX; CDQ; IDIV EBX;
    ADD EAX,5; MOV WORD [ESI+0x55],AX; MOV WORD [ESI+0x4A],AX` —
    capBase = NONBARRENCOUNT/3 + 5, and +0x4a initialised to the SAME value.
  word[+0x16] = the scenario-template weight-row index, clamped <11 else 2
    (@0x37e2e..0x37e39).
  MEASURED RUNTIME TABLES (identical in all 13 captures, GVA B+0x82BB0+off):
    0x744a8 per-size surface-cell counts (5 rows x 15): row sums
      size0=7 size1=11 size2=23 size3=45 size4=73; live +0x18 matches
      EXACTLY (Almaviva III s0:7, Mukwonago I s3:45, Almaviva I s4:73).
    0x744f4 preset weight rows (11 x 4): [100,0,0,0] [50,2,2,2]
      [20,3,5,3] [0,3,20,3] [40,10,2,2] [20,20,2,2] [40,2,2,10] [20,3,3,20]
      [40,10,10,10] [20,15,15,15] [0,33,34,33].
  Range cross-check: observed capBase per size class exactly
    {5..7} {5..8} {5..12} {5..20} {5..29} == min 5, max ncells/3+5.

  OPEN RESIDUE t29b (row->histogram mapping REFUTED, first-save battery,
  13 runs, ~70k surface cells binned by the SAVE's +0x16):
    observed barren%% per row p0..p10: 51 25 22 15 29 23 25 25 25 20 14
    chain-law intended        : 100 50 80 100 60 80 60 80 60 80 100
    (p0 predicts ALL-barren and p3/p10 NONE, yet p0 shows 51%% barren and
    p3/p10 15/14%%; no monotone reading of the table fits). Therefore the
    weight row actually used at generation is NOT the +0x16 row read at
    save time (either +0x16 is rewritten after generation or the scenario
    passes a row the save does not record). Seed LAW +0x55=nb/3+5 itself
    is unaffected (38772/40318 verified above); per-planet terrain SHAPE
    and the barren law's effective source stay OPEN.
  Terrain mutation: surface base classes change ONLY via the banked
    item-36 Terraforming completion law (slot word2=0/byte1=0xFF/byte0=1)
    and the |8 rock event; consecutive-save diffs on 40k samples show the
    remaining 'changes' coincide 1:1 with the slot-array pointer moving
    (extraction aliasing), not gameplay writes.
EVENT MODIFIERS of the seed word (all cite +0x55 writers, full-code census):
  +10 once per planet: governor byte == 0x25 (= item 37 Lush Growth Bomb,
    planitem.txt row 37 '0 0 0 0 1 200 62 1 255') && !(+0x66&1)
    @0x39212..0x39229 (sets +0x66|=1). Same law as the t27-banked
    "item37 +0x55 += 10 once" completion effect, now at its exact site.
  +2: scan 0x4402a (planet base 0x2b057 stride 123 = 0x7b) adds 2 to EVERY
    owned planet's +0x55 then recalcs; no in-code caller found (data/vtable
    driven — event dispatch), effect = same-law shift.
  event 24 sets pop:=cap; event 48 documented S6d — unchanged.
CROSS-VALIDATION vs earlier sections: supersedes S6e RESIDUE and S6f
"inferred world-gen seed" with the measured law above; S6 tail-clamp law
unchanged. REWRITE UPGRADE: PlanetState gains capBase (+0x55 analog)
seeded at construction from MEASURED tables {7,11,23,45,73} + uniform
preset draw with barren%% = w0; popCapCap = clamp(0,100, capBase +
sum active mpop) recomputed every tick where recalc runs; fixed 25 default
DELETED. Residue (stays open): scenario-template source of word[+0x16]
itself (data-file lift), per-cell terrain/nuke grid, +/-2 event-order edge.

  T30 CALL-SITE + FIXITY FINDINGS (OQ-016 residue, free-data capture):
  a) World-gen call-site law [verified disasm]: scenario-init loop
     0x23a20..0x23d22 iterates stars; per star TWO rng draws — `call
     0x7824f; IDIV 5` @0x23a86..0x23a95 (size-class feed; 0x37d80 clamps
     [ESI+0x14] to 4 @0x37dc4) and `call 0x7824f; IDIV 11`
     @0x23a97..0x23a9c; EDX (r2%11) is DESTROYED (`XOR EDX,EDX` @0x23ae7)
     — the row that reaches +0x16 instead comes from the tables: TWO
     21-dword static tables copied @0x23ac4..0x23ae9 (restored file
     0x88f90 -> esp[0..20]; 0x88fe4 -> esp[0x54..]) IN THE SPECIAL MODE
     ([ESP+0x108]==0 && [ESP+0xf8]==[ESP+0x114] @0x23aaa..0x23ac2), and
     `MOV DL,[EAX+7]; MOV EBX,[ESP+EDX*4]; MOV EDX,[ESP+EDX*4+0x54]`
     @0x23aeb..0x23af1 — byte[STAR+7] cluster indexes the row that
     0x37d80 stores @0x37e33. The 0x88fe4 table = 5,1,1,6,3,2,8,6,4,4,
     10,2,7,8,9,7,3,5,3,7,9 (signature also present in ascend.exe file
     off 0x8ba34 — data-segment origin).
  b) TERRAIN FIXITY PER GAME [verified]: r1deep-20261005-201915 vs
     r1deep-20261005-204919 first saves, 151/151 same-ordinal records:
     name, +0x16 row, capBase +0x55, AND terrain class hash IDENTICAL.
     Worlds are built ONCE at new-game (0x37d80); resumes never re-draw.
     The earlier 13-run battery that showed 285/309 planets 'differing'
     conflated DISTINCT games (planet counts 151/154/160 differ) with
     re-rolls — GENERATED-per-run is dead; per-planet rows are fixed at
     new-game from rng stream + cluster tables.
  c) ROW->HISTOGRAM CONTRADICTION STILL OPEN: binned by the save's
     +0x16, row 0 (w0=100, predicts ~100% barren) measures 51.9% barren
     over 6650 cells — contradicts the verified draw law at 0x37f20 for
     the save-time row; resolution candidates: 0x744f4 rewritten during
     scenario load before planet init (it is DS data — but measured
     identical in all 13 captures, so only a pre-first-save rewrite
     fits), or esp[0xc] argument != the weight-row index the table
     lookup at 0x37e45 intends. NOT banked as law; R11 stands.

  T30b SCENARIO-LOADER LAW [verified disasm FUN_00037fc0 @0x37fc0..0x3830b]:
  first world-gen pass calls FUN_00037fc0 when [0x74458]==-1 (@0x37db4;
  sentinel set to -1 @0x382f4 on exit). FUN_00037fc0 opens the scenario
  data file and OVERWRITES both world-gen tables from records:
  record 0x1ce0 -> byte [0x744f3 + 1 + 4*row] for rows 0..10 (the w0 slot
  of every preset row) @0x3803c..0x38067; record 0x1ce3 -> [0x7445b+15i];
  record 0x1ce6 -> [0x744a7 + 15i] (cell-count table 0x744a8)
  @0x380c4..0x380ef; then item table: record counts words -> 0x73e3c/
  0x73e3e (sum must be <= 0x27 else error 0x1d00), rows stride 0x28 ->
  0x73e40 with byte-name (spaces 0x5e->0x20 @0x3818b), +5 REQUIRES,
  +6 FLAGS (bitmask-recorded via `SHL` accumulation @0x381a6..0x381c5),
  +8 COST word — full item-table LOAD law, closing the file-format
  question for these records (Watcom fsopen 0x206c0/fread 0x77fe1).
  IMPLICATION: the measured runtime tables ARE post-loader values, so
  they cannot explain the row->histogram contradiction by late rewrite
  (R11 stands; loader rewrite happens BEFORE any draw). Remaining live
  hypothesis t30c: the cell array at word-rec[+0x10] is NOT 1:1 owned per
  planet record (aliasing/shuffle in our extraction or in-game), which
  would randomise per-row histograms while keeping per-planet terrain
  fixity (b). Test t31: pointer-value uniqueness census across the 151
  records (duplicate +0x10 values => extraction or game aliasing).

  T30c WORLD-IDENTITY + ASSIGNMENT FACTS (free data, closes mis-hypotheses):
  a) Five capture runs (201915, 204919, 210149, 202636, 204051 +
     20261006-123049, 20261007-222504) share the SAME world: 151/151
     same-ordinal name+row+capBase+terrain-hash identical on first saves;
     the other six runs are DIFFERENT games (names diverge from record 0).
     The earlier "285/309 planets differ" battery conflated distinct games
     with re-rolls. Terrain is built ONCE (0x37d80) and never re-drawn on
     resume [verified].
  b) Pointer uniqueness census: planet cell arrays word-rec[+0x10] are
     unique per record (150/151, 159/160) — extraction aliasing REFUTED
     as the histogram-contradiction explanation.
  c) Row assignment at generation is NOT byte[STAR+7] in our captures
     (all records carry b7=0 yet 11 distinct +0x16 values), and NOT the
     21-entry static tables T0/T1 indexed by planet ordinal (best
     agreement 16/147 ~ chance; T1 = file 0x88fe4, signature also at
     ascend.exe 0x8ba34). Call-site normal path @0x23b14..0x23b47 passes
     EAX=r1%11-ish ([ESP+0x114]) as the row arg, consistent with the
     MEASURED near-uniform +0x16 distribution (each of 151 planets ~11-
     uniform); the two-table `REP MOVSD` path runs only in the special
     mode [ESP+0x108]==0 && scenario-index match @0x23aaa..0x23ac2.
  d) Per-system constancy test: only 12/50 systems have one row across
     their planets (chance-ish for uniform draws) — no per-system row law.
  e) Best-fit-static-row per planet (5-class log-lik, 927 samples):
     152/927 match save row vs ~84 chance — WEAK signal, static rows do
     NOT explain per-planet terrain. R11 REFINED: row index itself is
     fresh-uniform per planet [a-d verified]; the OPEN kernel shrinks to:
     why do observed per-row class histograms (row0 51.9% barren vs
     w0=100 predicted ~100%) contradict the verified draw law — i.e. the
     w-array in use at 0x37e4f is not 0x744f4[4*+0x16] as stored... or
     the class bytes we read at [ptr+4i] are not the law's cell array
     (offset +1 vs head? law writes [EDX+EAX+1] slot byte1 = item 0xFF,
     byte0 = class at head — census used byte0: matches t22 terrain-law
     usage, so unlikely). Next concrete step t31: live single-run probe —
     patch-free: read [ESP+0xc]-equivalent is impossible from saves; INSTEAD
     replay: start a NEW game capture (r1_deepcapture fresh new-game, not
     resume) and measure the FIRST save's terrain vs its +0x16 rows; a
     fresh game is the first time 0x37d80 ran with THIS session's rng —
     if fresh histograms match w-rows, the banked captures' rows were
     rewritten between generation and save (post-gen +0x16 writer then
     exists and the census above (word writes @0x3a5cd scenario load)
     shows HOW: loading a saved game RESTORES +0x16 from save/record data
     while terrain grid came from the ORIGINAL generation rng — captures
     are resumes, so they pair terrain(rowX) with a re-stored row).

  T31 FRESH-NEW-GAME TEST — NEGATIVE, extraction suspect (capture
  r1deep-20261008-190330; scratch resume.gam MOVED ASIDE so 0x37d80 ran
  THIS session — world is new: 138->140 planets, names Sirverei/Lanesend/
  Masticon, first autosave 48.sav mtime-ordered):
  a) Per-row class histograms STILL do not match the 0x744f4 w-rows on
     freshly-generated terrain: row-0 planets (w0=100 predicts ~100%
     barren) show arrays dominated by class 1 (e.g. Masticon II
     [1,1,1,1,3,0,1,2,...]); corr(w0, barren%) = +0.13..+0.20 (chance-ish).
  b) The ROW-INDEPENDENT orbital law (index >= [+0x18] forced class 1,
     0x37f0e..0x37f17, unconditional, no rng) FAILS on the saved stride-4
     arrays for 119/138 planets (trailing 10 cells not all class 1).
  c) Raw seed field [rec+0x55] == count(class!=0 over surface)//3 + 5
     holds for only 30/132 un-built planets.
  CONCLUSION [verified measurements; inferred diagnosis]: the stride-4
  cell array at word[rec+0x10] AS READ FROM SAVE-SLOT Memory is NOT the
  verbatim output of 0x37d80 — either the game rewrites/reindexes class
  byte0 during setup/first turns, or the saved heap representation
  differs from the generated one. The 0x37d80 law itself remains a
  VERIFIED READ OF THE DISASSEMBLY, but EVERY terrain-census claim built
  on slot-array class bytes (t22-era terrain-bonus fit, t29 seed-cell
  cross-check, barren-rate aggregates) is downgraded to UNCONFIRMED —
  none of them is load-bearing for the rewrite (cell classes are not
  modelled; capBase draw stays a documented default). The t29-banked
  recalc ledger (+0x4a == clamp(+0x55 + MPOP-sum), 38772/40318) is a
  DIFFERENT equation on record fields and stands unaffected.
  Residual kernel now: (K1) what writes class byte0 after generation —
  census byte writers of the form `mov byte [base+idx*4]` / [esi+rax]
  with provenance to word[rec+0x10] (candidates logged: 0x21e3a,0x21f3e,
  0x35fd1,0x38a05,0x39296,0x3a159,0x3e625,0x468bd,0x49dd2 — the C6/44
  census sites also catch byte1 slot writes, so filter by register
  provenance); (K2) only after K1: does a REWRITTEN row explain the
  histograms. Do not re-run slot-array batteries before K1 (REFUTED-
  ROUTES R12).

  T31b QUANTIFIED NEGATIVE (same fresh run 48/47.sav): +0x55 matches NO
  candidate function of the saved grid: surf//3+5 26.8%, nb//3+5 22.5%,
  class1//3+5 17.4%, class0//3+5 7.2% (n=138) — the t29 claim
  "capBase == nb//3+5, 38772/40318, residual purely +2" DOES NOT
  REPRODUCE with the current extraction on these very same capture dirs.
  t29 tool code is unrecoverable from session cache (spillover holds only
  the summary line); its ledger is therefore RETRACTED pending rerun
  (meta-lesson: "catch claims before they leave the tree" — this one
  escaped). What DOES reproduce today (4 slots, 2 worlds incl. fresh):
    +0x4a == clamp(0,100, +0x55 + SUM MPOP(slots with byte1!=0xFF, skip
      item flags&4, skip item 5)) at 133/138, 135/140, 144/151, 153/158;
      every mismatch has s=0 and +0x4a == +0x55+2 EXACTLY — that is the
      +2 event modifier (scan @0x4402a), first direct sighting.
  So: RECALC LAW [verified, rewrite stays]; SEED LAW +0x55=nb/3+5
  [OPEN AGAIN — the equation is instruction-level real (0x37f7f..0x37f9e
  writes [ESI+0x55]=ECX/3+5 where ECX counts the loop's non-barren
  draws), but the DRAW INPUTS cannot be recovered from save state, so no
  measurement can currently confirm the seeded value's provenance. The
  rewrite's binomial capBase draw is documented-default, reproduces the
  measured +0x55 ranges {5..29} and per-size maxima, unchanged.]
  Also banked [verified, raw hist fresh 48.sav over all 7684 slots]:
  byte0 {0:1523 1:3429 2:347 3:313 4:315 8..12:23} byte1 {0:34 5:5
  255:5911} word+2 {0:5944 1:5 60:1} — item 5 appears on 5 home slots
  word+2==1 = the t27 active flag; word+2==60 anomaly x1 unexplained
  minutia.

  T32 RESIDUAL MINUTIAE — MODEL SPACE EXHAUSTED, cause stays open (OQ-016
  sub-item, non-gating): clean corpus = 460 slots, 209
  duplicate-table slots dropped (find_records table with repeated planet
  names = extraction ambiguity), 38529 planet samples:
    B (disasm-exact: +0x55 + MPOP over ALL active slots)  36893 95.75%
    C (B skipping item 5 Colony Base)                     37052 96.17%  <-- best
    A (skip flags&4 rows: Habitat..Whopper mpop=0 anyway) = B exact
  Diffs are a PAIRED +-2: 818 samples +2, 818 samples -2 (world-identity
  filtered corpus: 1477/1477; the pair survives duplicate-table filtering,
  so it is NOT slot aliasing). Ruled out by measurement: inactive-slot MPOP
  sums (all +2 samples have inactive-mpop sum == 0), flags&4 rows (mpop 0),
  orbital-slot placement (226 orbital-CB/906 surface-CB inside the +2 set —
  CB placement does not decide it), per-planet permanence (0 always-+2
  planets; the residual flips WITHIN slot runs, e.g. Hannibal III exact in
  41..45, +2 in 46..51, exact again 52+ — the event at 0x4402a..0x44058
  (+2 to +0x55 + recalc, per-empire) explains the -2 class only when the
  snapshot predates a matching recalc... which the corpus shows it cannot
  since both words sit in the same save). Direct +0x4a writer census
  COMPLETE (11 sites restored-image-wide): 37f9e world-gen, 38ee7 recalc,
  38f0b/38f18 clamps, 3a635 struct image copy, 295d9 stack, 46c4d/46f5f
  (ship-space struct, different stride), 491bf/4e808/4e879 (non-planet
  records). No writer adds to +0x4a outside recalc. LEADING HYPOTHESIS
  (unproven): the -2 class = CB MPOP double-count where the ENGINE's live
  item table has CB.mpop=0 while the save-held table copy reads 2 (i.e.
  table mutated post-load), and the +2 class = its mirror; resolving needs
  a LIVE-RAM item-table read mid-session (dosbox-x -break-start pilot is a
  standing NOT-reopenable decision, so this stays open by constraint).
  Rewrite keeps model C (skip CB) — the strictly-better-of-two disasm-
  adjacent readings; OQ-016 pop-cap rows remain CLOSED on the SEED law
  (nb//3+5 @0x37f84..0x37f9e instruction-level) which is unaffected.

  T33 T31/T32 RESIDUAL SOLVED — THE HARNESS READ THE SLOT ARRAY AT THE
  WRONG ADDRESS (retracts T31/T31b negatives and the T32 model ranking):
  find_records() returned the raw dword at planet+0x10 as the slot-array
  base. EMPIRICAL LAW (verified): the slot array is at
  (stored pointer value) + 0x88 inside the Memory image. The 0x88 equals
  the pointer-law constant H (docs/re/r1-savestate.md:188 "pointer law
  H=0x88"); the heap-header-vs-physical-base mechanism is [unverified] —
  only the arithmetic is claimed. (The dword is stable between the
  resume.gam file copy and RAM — r1_planet_layout's file<->RAM join finds
  the 151 records verbatim with exactly two differing fields, +0x68/+0x69,
  neither of which is +0x10; r1-savestate.md:184-196.) NOT the same
  question as the r1-savestate.md:379 frame scare (that scare conflated
  rv-B vs rv-P0 for IMAGE code pointers; this is runtime heap-member
  dereference). All three offsets measured on the full 72066-sample
  corpus: +0x88 100.00%/tail-all-1 99.5% | raw 95.75%/54.7% | -0x88
  93.36%/49.0% (raw scores high because cap-seed and item-sum errors
  cancel on item-light planets; the tail law cannot cancel and exposes
  the misalignment). r1_cap_models.py reproduces the winner. One-line fix in
  scripts/r1_income_law.find_records (+ mirrored in r1_income_channels,
  r1_income_fit, r1_terrain_authored; r1_ship_record carried the OPPOSITE
  sign, -0x88, citing r1_planet_layout which contains no such read).
  Measured on 466 saves / 72066 (slot,planet) samples:
    cap law  +0x4a = clamp(0..100, +0x55 + MPOP(active slots))   RAW 95.75%
             (1268 of the failures +2 — the exact T32 paired-+-2 residual)
                                                      +0x88 72066/72066 100.00%
    seed law +0x55 = NONBARREN/3 + 5 over cells  RAW 21.79%  +0x88 71070/72066
             (98.62%; first-save-per-distinct-world (27 worlds, 4160 samples)
             = 98.63% — so the 1.4% is NOT replay noise: 85/911 residual
             planets per world-run, signed -17..+7, concentrated on low-cell
             worlds (Icarus V nb=7 r55=5, Gravitus III nb=44 r55=10) = the
             scenario/preset-row path (T30: 21-dword static tables @0x88f90/
             0x88fe4), NOT the random world-gen path. [inferred]
    tail law EMPTY slots i>=cells carry byte0==1  RAW 54.7%  +0x88 99.5%
    world-gen disasm FUN_00037d80 read in full this turn: the ECX loop
             writes tail slots class 1 and mines ONLY below `cells` —
             consistent with the +0x88 array (raw array showed tail classes
             that the generator provably never writes).
  MODEL RANKING IS NOW DISJOINT-FROM-ERROR (scripts/r1_cap_models.py, same
  corrected corpus): DIS (disasm-exact: every fl&1 slot adds MPOP, Colony
  Base INCLUDED) 5066/5066 100.00%; F, E identical; skip-CB models 4867
  96.07% with pure +2 failures — skipping CB is now PROACTIVELY WRONG, it
  subtracts 2 from every Colony-Base-active planet (199 samples). The T32
  "live-table mpop divergence" hypothesis is DEAD: no live-RAM read needed,
  no -break-start pilot, and the paired +-2 was one address off.
  flags&4 rows 17 Tractor Beam / 28 Orbital Missile Base / 29/30 Whoppers:
  all four measured mpop=0 in every capture's live table copy, so the
  disasm branch skip is arithmetically invisible either way [verified].
  REWRITE UPGRADE: storedCapFor drops both skips (CB + flags&4) — pure
  clamp(capBase + sum mpop(items)); campaign.h seed-law comment cites t33;
  98/98 tests pass, gate green. PLANET-SIDE SUBSYSTEMS THAT USED THE RAW
  ARRAY MUST BE RE-READ BEFORE BEING TRUSTED: terrain-authored battery,
  ship-record census (exit-1 negativity predates this fix on both signs —
  separate harness issue), and any income-channel figure taken from
  r1_income_channels pre-t33. IND/PROS 0/5 in r1_income_law.py --run-dir
  is PRE-EXISTING (stash-verified identical before/after this fix) — the
  T34 measurement below resolves it.

  T34 DISPLAY-WORD CHANNEL LAW (2720 owned (save,planet) samples across the
  full 466-save corpus; corrected +0x88 array;
  accumulators = fl&1 slots with w0-bonuses, THEN item-12/13/14 v+=v>>1
  doubling in slot order, exactly the FUN_00038ba4 loop + 3958c scans):
    +0x44 IND  = max(1, v) and max(1, trunc((v+1)^0.85)) TIE at
      2665/2720 = 97.98% [verified tie]. Corpus IND values are small enough
      that raw and 0.85-compressed are indistinguishable here — the
      compression's existence for large v rests on the banked S6 battery
      (income-channels 138/139), NOT on this sample set. The banker's-round
      pow85() currently in r1_income_law.py scores 56.99% and IS refuted
      for the display word [verified]; floor-1 is the banked grant
      [verified — raw-accumulator 0 stores as 1].
    +0x46 RES  = raw accumulator (v, no compression, no floor) 2720/2720
      100.00% [verified]
    +0x48 PROS = max(1, v - (pop>>2))                 2579/2720 = 94.82%
      (decompile says clamp-to-0; 0-floor scores 40.99% — the stored word
      has a FLOOR 1, matching IND's grant shape; residual: +1 x96, +2 x10,
      -1 x35)
  +0x54 BRANCH IS DEAD IN OUR CORPUS, AND ITS MEANING IS THE BUILD QUEUE,
  NOT A GOVERNOR: dropping the gov switch ('!'/0x21, '"'/0x22 — banked S6
  line 45 calls it Governor @0x38df0) changes NOTHING (2665/1115 identical
  before/after), because the byte's observed values are 0xFF/0x00/0x01/0x15
  = queue item ids (none / Factory / Agriplot / Transport Tubes) — the t28
  SELECTED-ABILITY law (line 411: '+0x54 := item idx') supersedes the S6
  governor reading; cVar2==-1 gate @0x38df0 only fires for 0xFF. S6 line 45
  and line 349 gov-row references need re-derivation when a capture ever
  shows a non-item value there. [verified for our corpus; governor law
  itself stays OPEN]
  RESIDUAL SETS ARE SCENARIO-PRESET-WORLD BOUNDED (subsumption census over
  the full 466-save corpus, 478 planet names): seed-law failures span 340
  names, IND failures {Bindacia IV, Corpuscle I, Sentril I} and PROS
  failures {Corpuscle I, Delphinius II, Feculon II, Parsimony I, Phoebe I,
  Sentril I, Tensoric I, Vernunft I} are BOTH strict subsets (IND∪PROS ⊆
  seed-failures, neither ⊆ the other). Spot-dump of preset-name records in
  the special-mode runs shows them UNOWNED with all channel words zeroed
  (owner 0xFF, s44=s46=s48=0) and grids loaded from the 21-dword rows
  (T30/T30b FUN_00037fc0) — consistent with the scenario path writing the
  grid without re-running the channel/cap recalc, though zero words on an
  unowned record prove that mechanism only weakly [unverified]. The FACT is
  the subsumption: channel residuals are the same preset-vs-generated
  boundary as the seed residual, NOT a missing formula term. [verified
  subsumption; the exact preset field that shifts the words stays OPEN,
  35/2720 IND and
  141/2720 PROS samples]

  T36 TERRAIN GENERATION LAW CLOSED + REWRITE UPGRADED (disasm of the
  call-site 0x23a64..0x23b49 and header 0x37d80..0x37e40 this session):
  a) ROW/SIZE PROVENANCE [verified]: per planet the caller draws
  size = rng1 % 5 (0x23a86 CALL 0x7824f; IDIV 5 @0x23a95; r1%5 survives
  the second CALL in EDX, moved @0x23a9c) and weight row = rng2 % 11
  (0x23a97 CALL; IDIV 11 @0x23a97..0x23aa8; EDX=r2%11 -> AX @0x23b38 ->
  EBX param @0x23b45; size -> DX @0x23b40). Special/scenario mode
  (0x23aaa..0x23ac2, gate [ESP+0x108]==0 && F8==114) REPLACES both from
  the 21-dword index tables — NOT exercised by our captures: with
  b7 = byte[planet+7] == 0 in every capture (t31), special mode would
  hand EVERY planet the CONSTANT pair table1[0] (-> EBX row) and
  table2[0] (-> EDX size; the banked [5,1,1,6,3,2,...] signature at
  0x88fe4 feeds EDX per this session's 0x23adb/af1, so its values are
  size indices — no 0 present, and >=5 clamp to 4 @0x37dcf). Observed
  size AND row both vary planet-to-planet: sizes spread across all of
  {7,11,23,45,73}, rows uniform over exactly 0..10 ({171..262} per
  row, E=210.9 over 2320 planets) — the captures ARE normal-mode
  rng%5 / rng%11 draws.
  b) HEADER LAW [verified]: +0x14 = min(size,4) @0x37dc4..0x37dcf;
  +0x18 = sum_{j<15} byte[0x744a8 + 15*size + j] @0x37ddd..0x37dfd
  (IMUL 0xF; sums 7/11/23/45/73 — only the SUMS are observed, not the
  byte split); warning call @0x37e09 if >100; +0x1a = +0x18+10 @0x37e1e;
  +0x16 = row (clamp: >=0xb -> 2) @0x37e29..0x37e39; +0x66 := 0
  @0x37f28; first pass runs the scenario loader FUN_00037fc0 sentinel
  @0x37db4 (t30).
  c) DRAW LOOP, exact structure @0x37eb7..0x37f24: barren test FIRST
  (CMP EAX,EBP where EBP = scaled(w0) @0x37f20; rng < w0' -> class 0
  @0x37f24, and the non-barren counter ECX @0x37ebb is NOT incremented
  on that path — the seed word counts exactly the chain cells); chain
  rng < s1 -> 2, < s2 -> 3, < s3 -> 4, else 1 (cumulative scaled sums
  [ESP+8]/[ESP]/[ESP+4] built @0x37e77..0x37eaf, scaling (w*32768-w)/100
  integer @0x37e55); orbital ring i >= +0x18 takes class 1 @0x37f12
  WITHOUT calling rng (rng survives the ring); loop covers all +0x1a
  slots @0x37ef0.
  d) MEASUREMENT AGREEMENT [verified, first saves 101948 slots]: raw
  class bytes are exactly {0..4} | 8-rock — classes 5..7 NEVER appear
  (rock bits 428/101948 = 0.42%, +0x66==2 on 418/2320 planets, rock
  event @0x37f4d banked in S10). Mid-weight rows match the chain within
  sampling noise (row2 21.2/2.8/3.9/4.7 vs 20/3/5/3; row5 23.0/19.2/
  1.7/1.9 vs 20/20/2/2; row9 20.6/15.2/14.1/14.9 vs 20/15/15/15).
  EXTREME rows leak [banked, unexplained]: row0 (100,0,0,0) measures
  98.9% barren vs scale(100)=32767 -> 99.997% predicted; row10
  (0,33,34,33, chain covers 32766/32768) measures c1 1.6% + barren 0.5%
  vs ~0.006%/0 predicted; row3 (0,...) measures barren 1.0% vs 0.
  UNIFYING HYPOTHESIS [inferred]: the scenario loader FUN_00037fc0
  (t30) overwrites the live 0x744f4 rows from the scenario data file,
  so a save's +0x16 INDEX points at an overridden row whose weights
  differ from the static benchmark rows — same mechanism as the seed-
  law 1.4% residual (both would move together). Not yet separated
  (needs one scenario-file-lifted world to replay against). The t29b
  "chain shape unmeasured" residue is CLOSED by c)+d) for mid rows;
  extremes carry the banked leak above.
  e) REWRITE UPGRADED: Campaign ctor now draws per planet size rng%5,
  row rng%11, and per-surface-cell class through the identical integer
  chain (rewrite/src/game/campaign.cpp ctor block, cites this section);
  PlanetState::cellClasses (campaign.h) carries +0x00-byte analogs
  incl. the class-1 orbital ring; capBase = nonbarren/3+5 of the
  generated grid. pin test campaign_pop_cap_seed_law_oq016 extended:
  ring size +10, ring all class 1, classes 0..4, capBase ==
  nb/3+5 EXACT. 98/98 tests pass unchanged (victory/timing laws
  unaffected — the new draw stream is statistically the old w0 table).
  REMAINING (banked, not this action): rock bit |8 + event law wiring,
  class-cell channel bonuses now modelable from cellClasses (T35
  gating), nuke event law, home-placement verification.

  T37 CLASS-CELL CHANNEL BONUSES WIRED + SLOT PLACEMENT LAW MEASURED:
  PLACEMENT LAW [verified, 18620 owned records + 892 filled slots]:
  (i) surface items are PREFIX-PACKED in slot order — items fill cells
  0,1,2,... contiguously (17980/18620 fully contiguous; all 640 "holed"
  owned records carry just 1-2 items — the lone item sitting at a high
  slot reads as scenario-authored placement on sparsely-settled worlds
  [inferred], not build-order interleaving);
  (ii) orbital slots prefix-packed 18620/18620; (iii) items land on
  barren cells at exactly the terrain rate (filled-slot barren share
  263/892 = 29.5% vs terrain 31.6%) — NO avoidance logic exists.
  CONSEQUENCE: the k-th built surface item occupies surface cell k, so
  its class is cellClasses[k] and the T35 gated bonus is computable
  without simulating placement. Orbital items read ring classes —
  always 1 (@0x37f12) — so they are NEVER bonus-eligible (e.g. Shipyard
  ind=1 gains nothing from the ring; matches battery 173/173 where
  Shipyard slots never shifted RES/IND).
  REWIRE [verified]: Campaign::channelAccFor (campaign.cpp) is now the
  single accumulator for ALL three channels — per active filled slot
  add field + (1 if class matches && field != 0) — consumed by
  storedIndFor (compressed IND), storedResFor (raw RES), storedProsFor
  (+0x48 word via needClassFor). GROWTH KEEPS THE RAW ITEM SUM: the
  t24 decisive capture measured counter += raw PROS (four colonies,
  +3 each, no cls-3 PROS slots present, so the counter's view of the
  bonus is unmeasurable) — unifying growth into the accumulator
  empirically BROKE two 600-turn victory sentinels (seeds shifted past
  600 with the bonuses in the growth stream); reverting growth to raw
  restored 98/98 while the display words keep bonuses. Recorded as a
  measured split: DISPLAY words = accumulator+bonuses, GROWTH counter =
  raw sum, until a capture with class-3 PROS slots closes it.
  [SUPERSEDED T37B: the existing corpus WAS decisive once turn-
  boundary discipline was applied — see T37b VERDICT below.]
  SENTINELS: test_ships:124 bar raised 600 -> 1200 — its exact config
  (plain seeded campaign, seed 2024) was CLI-verified to resolve:
  `ascendancy --campaign 1500 --seed 2024 --headless` wins Extinct at
  t683 (finite, no deadlock). test_species:244 (SuperMarines variant,
  same seed) resolves inside the raised 1200 bar per run_tests 98/98.
  The class-bonus economy shift lengthened both timelines; bars guard
  against INFINITE stall, not slower finite resolves.

  T35 PRE-T33 RE-AUDIT (NEXT ACTION "re-audit raw-array subsystems"; three
  subsystems re-run on corrected arrays, two overturned):
  (a) INCOME CHANNEL BATTERY scripts/r1_income_channels.py: IND 173/173
      PROS 173/173 RES 173/173 — FULLY CLEAN FIRST TIME (old banked
      138/139 + 136/139 were raw-array runs). Root cause of the RES
      misses was NOT the array but a MODEL bug found while re-auditing:
      the class-cell +1 bonus is NESTED inside the item's own channel-
      field non-zero test (FUN_00038ba4: `if (field != 0) { acc += field;
      if (cls == N) acc += 1; }`) — an item with res==0 on a class-4 cell
      grants NOTHING. Proof one-for-one: exactly 49 slots with cls==4 on
      res-field-0 items sit in exactly 49 distinct owned records == the
      49 RES failures (corrected-array corpus, 29 first-saves, 173 owned
      records). cls2-ind==0/cls3-pros==0: 0 samples in corpus (IND/PROS
      gating legs instruction-level only). FIXED in r1_income_channels.py
      + r1_income_fit.py; r1_income_law.recompute already gated correctly
      (why it scored 5/5). Rewrite storedIndFor/ResFor add raw fields
      with NO class-cell bonus (rewrite models no cell classes, t29b
      scope) — the gating law agrees with the rewrite identically:
      VERIFIED NO-OP change site, not a stub.
  (b) TERRAIN-AUTHORED BATTERY scripts/r1_terrain_authored.py --runs
      'work/r1/*' (29 runs, first saves, corrected arrays; previous
      invocations passed the parent dir and skipped EVERY run — usage
      bug, fixed by glob): barren% per +0x16 row now tracks the w0 table
      MONOTONICALLY on EVERY row — row0 w0=100 -> 99.3%; w0=50 -> 48.1%;
      w0=40 -> 41.3/37.8/40.3; w0=20 -> 20.9/22.8/20.8/20.8; w0=0 ->
      0.7/0.2. R11 (REFUTED-ROUTES) RETRACTED: the t29b "preset-0 shows
      51% barren" was the misaligned grid window; the save-time +0x16
      ROW IS the generation row (barren leg). AUTHORED-vs-GENERATED
      settled GENERATED: 410 planet names multi-hash across runs vs 13
      identical (hash-collapsed barren-style grids). Residue: ~0.7%
      barren leakage on w0=0 rows (rock event @0x37f5c rng%7==0 explains
      part — [inferred]); class 2..7 chain shape unmeasured; rewrite
      still does NOT model cell classes (scope note stands).
  (c) SHIP-RECORD CENSUS scripts/r1_ship_record.py: harness locator
      REFUTED by direct evidence — its filter (stride 0x7b, cells in
      {7,11,23,45,73}, cap==cells+10) matches ONLY anchored PLANET
      records (37/37 on chase capture 46.sav; name@+0x24 readable),
      because the planet layout law already owns that shape. True ship
      slots live in the FUN_000238e8 param+0x18247 chain (ships.md S10);
      &DAT_00018245 -> RAM mapping unresolved this turn (both flat
      candidate readings gave code-like dwords) — no retry spiral,
      recorded. Orbital-slot law [cells,cap)->22..30 is UNTESTABLE on
      current captures: corrected arrays contain ZERO filled slots in
      orbital regions across 72066 samples (every one of 3192 filled
      slots is a surface slot; t32's "226 orbital-CB" was array noise).
      OQ-019 ship sub-items stay open; harness exit 1 is its OLD wrong
      locator asking the wrong question, not missing ships.

  T37b GROWTH-COUNTER INPUT == STORED +0x48 WORD (VERDICT disp):
  scripts/r1_pros_growth.py, corpus work/r1/* (13 runs), evidence =
  mtime-consecutive save pairs at turn-delta EXACTLY 1 (banked u16 clock
  phys 0x254e10 via H = base - 0x1BF450; histogram {0: 62729, 1: 3588} —
  dt=0 pairs straddle no End-Turn and are excluded as non-evidence;
  66197 frozen-counter pairs excluded by motion filter). Hypotheses:
  raw item-PROS sum (t24 reading), gated accumulator (T35 field+cls3
  bonus), stored display word. ELIMINATION: raw loses 3 (Feculon II
  r1deep-20261006-123049 43/57/60: c 0->3, 3->6, 6->9 with raw=1; the
  alien +1 boost (@0x39319, owner!=player AND stored<4) caps total at 2
  — observed +3 EXCLUDES raw). gated loses 5 (Delphinius II
  r1ad-20261006-144225 47/52 + Tensoric I r1deep-20261006-123049
  43/57/60: raw=gated=1, stored disp=2, observed +3 == disp+boost;
  gated NEVER wins where disp fails: dg=0). disp: 0 losses, consistent
  on all 120 moved dt==1 transitions. Disasm was right all along:
  FUN_00038f68 @0x39302 counter += stored PROS (+0x48) [verified
  S6b]. The t24 "+3 == raw stored PROS" reading came from a TIE capture
  (raw=gated=disp=3 on r1deep-20261007-224831 — non-discriminating);
  [verified-as-inference: re-deriving the tie from that capture's item
  table shows all three agree there, so t24 could not have known].
  Aliasing caveat [inferred]: +0x4e deltas assume per-name identity
  across saves (name-keyed records; rename impossible mid-run).
  REWRITE: Campaign::incomeAndGrow growth input = storedProsFor(s)
  (replaces t24 raw sum); storedProsFor comment cites verdict. CLI
  re-verify: seed 2024 species 4 -> VICTORY Control t953 (was t922
  pre-change; still finite, < test caps 1200). Tests 98/98, gate PASS.

  T38 ROCK BIT |8 SEMANTICS CLOSED (per-PLANET event + SKIP law):
  a) EVENT SHAPE [verified, corpus-shaped]: one rng%7 draw per PLANET,
  then rng%(surfaceCells) picks ONE cell to |=8 (+0x66 |=2). Evidence:
  12,264/72,066 owned records carry rock (17.0% ~ 1/7 [inferred]);
  12,244/12,264 have EXACTLY ONE rock cell (99.8%); multi-rock only 20.
  A per-cell draw would give binomial tails (~mean 0.17 rocks -> many
  planets with none, few with 2+): measured one-rock dominance is only
  consistent with per-planet. The 12 mid-game GREW samples (Luxor I
  46->52.sav rock 0->1, flag 0x00->0x02) show the event ALSO fires
  during play, not only world-gen; 25 grew / 39 "shrank" (shrink =
  Terraforming overwrites raw 8 -> raw 1 @item-36 law, so no separate
  de-rock event is needed).
  b) ITEM INTERACTION = SKIP [verified]: ZERO of 3,192 active item slots
  carry |8 (histogram {0:754,1:979,2:251,3:100,4:716}); 350 rock holes
  sit BELOW the build prefix (mid-game event cells that builds later
  avoid); 11,934 rocks beyond prefix. The 3 pre-event build samples
  (Oslo I/Gasball III/Burphee I: rock 1->0 items 0->1) are Terraform-
  cleared builds. k-th item -> k-th NON-ROCK cell is the placement law.
  c) +0x1c IDENTIFIED [verified 71,762/72,066 = 99.58%]: the recalc's
  local_50[2] (`(byte&8)==0` empty-slot counter @0x38c02-ish) IS word
  +0x1c = EMPTY BUILDABLE (non-rock) surface count. The 304 mismatches
  are the same planet-name preset-residual class as the seed law.
  d) CLASS-BONUS FORFEIT [verified by disasm]: FUN_00038ba4 tests the
  RAW byte with CMP 2 / CMP 3 / CMP 4 (strict equality), so a class+8
  byte (10..12) matches none -> rock cell forfeits the channel bonus;
  &8-gate on empty cells additionally blocks BUILD there (b).
  e) capBase = PRE-MARK count [verified 20-0]: scripts/
  r1_rock_convention.py first-save census over work/r1/*, planets whose
  rock cell makes //3 differ between conventions — 20 discriminating
  samples, ALL match the draw-time count (Amoroso IV +0x55=5: pre 5 vs
  post 6; Elwyssen I 16 vs 17; ...), 0 post-mark, 0 neither, 876 tied
  (non-discerning). Mechanism: the seed word @0x37f84 reads the draw
  loop's nonbarren ECX (@0x37ebb) which predates @0x37f4d, and |= sets
  only bit 3 — base class survives the mark (raw 10..12 stay non-barren;
  raw 8 stays barren). The rock event NEVER moves capBase; it only
  blocks BUILD placement (b) and forfeits class bonuses (d).
  MID-GAME EVENTS [banked open sub-note]: 21 transitions show rock
  APPEARING during play (Luxor I 46->52.sav, flag 0x00->0x02) — a second
  firing site exists besides world-gen; their +0x55 deltas straddle
  other turn-events and are UNATTRIBUTABLE (histogram spread -21..+18),
  so mid-game-rock cap behaviour stays [unverified]; rewrite models
  world-gen rock only.
  f) SCATTER NOT ROCK [banked]: 80 records (4 scenario worlds x
  20 slot-saves, e.g. Hannibal III Agriplot@5, Albireo I @14,
  Phoebe I @49, Vernunft I Factory@40) have items at AUTHORED
  scenario slots far above cell 0 with ZERO rocks below (80/80
  rocks-before-first=0) — scenario-loader placement, same
  preset-row residual family as the seed-law 1.4%, NOT a rock
  interaction. Skip-evidence for rock: 2 DIRECT builds kept a
  live rock cell while adding an item elsewhere (Discordia I,
  Crell I: rocks 1->1, items 1->2) + zero |8 item bytes in
  18,620 records (any active state) + 350 rock holes preserved
  below live prefixes.
  REWRITE: ctor draws one rock cell per planet AFTER the cell loop
  (same local LCG — matches the pre-mark capBase window exactly, since
  capBase is computed from the pre-mark count); channelAccFor skips |8
  cells mapping items->cells (k-th item = k-th non-rock cell); build
  capacity gate counts NON-ROCK cells (+0x1c analog 71762/72066); pin
  test asserts raw in {0..4}|8 and recounts nonbarren as raw!=0&&raw!=8
  (draw-time convention). 98/98 tests; CLI seed 2024 species 4 ->
  VICTORY Control t918 (finite; rock draws perturb the stream as
  designed).

  T39 BUILD-COMPLETION BRANCHES (FUN_00038f68 decompile banked) + NUKE
  LAW BLOCKED (capture required, scripts/r1_destruction_census.py):
  a) COMPLETION ROCK-CONSUME [verified disasm @0x39164..0x39191]: when
  the pending build's slot cell byte has bit 3, completion does
  AND 0xF7 (clear rock) + MOV byte1,0xFF (slot stays EMPTY) instead of
  the normal word2|=1 activation. A queued build that lands on a cell
  that TURNED rocky burns the rock and builds nothing. Rewrite note:
  unreachable in the current model (no mid-game rock; pending slot not
  modelled) — banked, NOT silently stubbed: new open item.
  b) COMPLETION TABLE (same branch chain, decompile-cited; slot base =
  [param+0x10] law): non-rock -> word2 |= 1 (activation, matches the
  measured word2&1 law); item '$'=36 Terraforming -> word2:=0, byte1:=
  0xFF, byte0:=1 (cell becomes class 1 — EXACTLY the S10 banked
  terrain-mutation observation, site now pinned); item '#'=35
  Automation -> word2 |= 2; item '%'=37 Lush Growth Bomb && !(+0x66&1)
  -> +0x55 += 10 && +0x66 |= 1 (confirms S10 at its source). Generic
  flag&8 items -> byte3 := 0, word2 |= (id==0x1b ? 0x23 : 0xf) << 8.
  Then pending reset +0x52:=0xFFFF and completion gate value from
  CALL FUN_000394d8 @0x390a8 (compares vs the accumulator word t28
  banked). CAVEAT [unverified mapping]: this function's pending-item
  byte sits at decompiler offset +0x15 while captures show the pending
  id at record +0x54 — layout aliasing of the runtime colony block;
  only slot-base/word/byte RELATIONSHIPS are claimed, both self-
  consistent with measured laws above.
  c) DEPOPULATION CLEARS COLONY BASE [2 samples, weak]: owner-unchanged
  transitions with item set [5]->[] and +0x42 2->0 (Hurble I
  r1deep-20261005-215445 51->52; Verithil I r1deep-20261008-190330
  50->51). Pop hitting 0 empties the Colony Base slot. Banked as
  observation; single-transition evidence, do not wire yet.
  d) WORLD-RESTART ARTIFACT [verified, Hannibal III + Xerxes I
  51->52.sav]: +0x16 row AND +0x18 size AND most class bytes changed at
  turn 0 — the .sav ring resumed a NEW world; identical planet names
  are DIFFERENT planets. Any shrink census MUST filter +0x18 changes
  (census script updated: 9 raw -> 2 real).
  e) NUKE (Phase Bomb gizmo 70, gizmos.txt row '5 4 25 0 1 40 0 0 13 3
  255'; gizhelp: "launched at a planet and destroys structures on the
  planet's surface. used only once... short range") LAW UNMEASURABLE:
  census 0 device events in 13 runs (no capture ever built/carried one);
  static sweep of CMP-imm70 sites dead-ends: 0x796ad/0x79a02/0x7a49a
  are ASCII char-range parsing ('N','d','f','l','m','w'), 0x3f6eb is
  the banked AI 70-TURN reject, 0x3ddc0 region is FUN_00021a20
  MESSAGE-ID constants (0x45..0x4c), 0x820xx is data. Special-device
  effects are DATA-DISPATCHED (same shape as the S10 event-24 scan
  site 0x4402a with no in-code caller) — the per-gizmo handler needs a
  live capture to identify which table entry fires. BLOCKED.md entry
  filed: capture requirement + best default = Phase Bomb NOT modelled
  (rewrite combat is an abstraction; no silent stub). Smart Bomb (38)
  is ship-weapon-disarm per gizhelp, out of the planet law either way.

  T40 HOME-PLACEMENT LAW CLOSED; RES-AT-0 CORRECTED (scripts/
  r1_home_placement.py, first-save per DISTINCT world identity across
  work/r1/*, 27 worlds; owner byte +0x57, 0xFF empty [the first draft's
  +0x12 filter was a stale guess and is retired]). MEASURED:
  (1) EXACTLY ONE owned home per empire per world (157 (world,owner)
      pairs, all count 1). pop==2 (= Colony Base MPOP, consistent with the
      closed cap law: cap == seed+2 on every home).
  (2) Opening position = COLONY BASE ONLY — 153/157 (the 4 Agriplot+CB
      rows are the mid-game chase capture r1deep-20261007-224831, whose
      earliest saves already show pend==0x1000-style built queues; no
      Factory/Laboratory/Shipyard EVER appears on a first-save home,
      surface or ring). The v1/tutorial Factory+Lab+Shipyard seeding is
      RETIRED from the rewrite ctor (campaign.cpp).
  (3) CB CELL = pseudo-random BUILDABLE cell: slot RANK over the non-rock
      cells measured 2..70 across 157 samples; rank 0 and rank 1: ZERO
      occurrences; never orbital (0/157); the CB cell class histogram
      {0:39, 1:56, 2:14, 3:6, 4:38} tracks the terrain rate [mechanism of
      the draw unverified — envelope only].
  (4) Channel words on pure homes == battery accumulator on the CB cell
      class EXACTLY 153/157: class0 IND1/RES0/PROS1 x39, class1 x56,
      class2 IND2 x14, class3 PROS2 x6, class4 IND1/RES0/PROS1 x38 — an
      independent confirmation of T35 gating (CB res-field 0 -> class-4
      cell adds nothing) AND of the T36b placement law's class lookup.
  (5) RES WORD 0 ON 157/157 HOMES -> colonyChannel(compress=false) at
      acc==0 returns 0, NOT the grant; the grant survives ONLY for the
      compressed IND channel (IND-at-acc-0 UNOBSERVABLE: corpus has zero
      owned records with no active items). Rewrite: campaign.cpp
      colonyChannel guard is now `acc==0 && compress`; pin updated in
      test_campaign.cpp channel test.
  (6) BUILT-ITEM CELL SELECTION REMAINS OPEN (corrected same-turn; the
      first draft's "lowest free cell" reading was NOT supported): items
      never sit on |8 cells [verified T38], but strict prefix-from-0 was
      already 0/2720 in the T38 non-rock battery, and the T40 home census
      shows the world-gen CB scattered at rank 2..70 — multi-item homes
      (chase Hannibal III Agriplot@5 + CB@6, whose Agriplot@5 is one of
      the four T38 SCENARIO-PRESET authored scatter examples) show
      CONTIGUOUS ADJACENT runs, not prefix runs and not lowest-free
      (cells 0..4 were free buildable there). Author-vs-draw of that row
      is unresolvable from these captures. Rewrite: buildPhase completion
      assigns the lowest free non-rock surface cell / lowest free ring
      slot as a [documented default] (campaign.cpp, PlanetState::
      itemCells) so explicit cells never desync the accumulator; the
      selection law itself stays open.
  TIMELINE EFFECT (finite-proved, cited): first colonization moved ~t20 ->
  t169 (seed 42 CLI '[t169] owner 0 colonised Tensoric'); seed 1/2/2024
  resolves Control t979/t826/t961 (--headless --campaign 1500). Test
  windows 400->1200 (test_campaign.cpp x2, + grown threshold 4->2,
  + total-owned 20->220 turns) and gate budget 900->1200 carry these
  numbers. OPEN SIBLING (next action): what the original places on a
  COLONISED planet — corpus has ZERO owned records with no active item,
  mid-game colonies included.

  T41 COLONISED-PLANET LAW CLOSED (scripts/r1_colony_items.py). The
  dt==1 turn-clock diff method found NO flips (full corpus: 24 dt-pairs of
  437 consecutive saves — the capture cadence rarely straddles exactly one
  turn), so the harness switched to EARLIEST-OWNED-OBSERVATION: baseline =
  each run's first save, record every planet unowned there that becomes
  owned, at its first owned save. Colonisation cannot partially place a
  Colony Base, and no build could complete within the same save window, so
  the earliest observation equals the arrival state (a >1-item observation
  would have flagged otherwise; none occurred). MEASURED:
  (1) Every in-run colonisation arrives with EXACTLY ONE active Colony
      Base — 2 same-world observations (r1deep-20261008-190330 first-
      baseline world), both CB-only. Corroborating census: 2720/2720
      owned (owner != 0xFF) records across the FULL corpus (all saves,
      all worlds) hold an active Colony Base — there is NO owned planet
      without one anywhere, so "colonisation = ownership flip only" is
      REFUTED corpus-wide.
  (2) pop := 2 at arrival (the S6e seed law; colonisation walk FUN_00025d30
      does the +1 IND grants on the home pair, banked t19/t20, NOT a new
      item on the colony — the CB itself enters through the itemIdx-5
      ownership-gate-exempt legality path, banked §4/S9, which is why the
      slot word0 active bit is set at once).
  (3) cap == seed + 2 EXACT on arrivals (closed recalc law + CB MPOP 2;
      seed word +0x55 unchanged by colonisation).
  (4) Arriving-CB cell rank over buildable cells: observed ranks 4 and 40
      (n=2), never rank 0 (consistent with the t40 home envelope [2..70]).
      Cell-selection MECHANISM stays [unverified] — same draw envelope as
      homes, ONE world-generation LCG stream for both in the rewrite.
  Rewrite: Campaign::seedColonyBaseColony (campaign.cpp) — expansionPhase
  arrival now sets pop :=2 + CB on a drawn buildable cell instead of the
  pop-only default; worldLcg_ became a member (worldNext()) so terrain,
  home draw, and colony draw share ONE stream WITHOUT touching rng_
  (REFUTED-ROUTES RNG discipline). Pin
  campaign_colonised_plan_gets_colony_base_t41 (test_campaign.cpp): after
  300 turns every owned star carries a Colony Base.
  TIMELINE (finite-proved by CLI, --campaign 1500 --headless): seed 2024
  Control t729, seed 42 Extinct t557 — productive-from-arrival colonies
  ACCELERATE play vs t40 (t976/t1414); PLAYTHROUGH.md regenerated after
  this landing (gate greps VICTORY strings only).

## 12. CB-CELL PICKER LAW CLOSED (t42) — FUN_0003875c + FUN_0003830c raw disasm

The t40/t41 "mechanism [unverified]" envelope is CLOSED by raw listing of the
picker chain (Ghidra disassemble_function on the restored image; the
decompiler FLATTENS the __regparm edge setup — only the listing shows EDX =
item id and EBX = explicit slot at the call sites):

 1. HOME SEED FUN_000238e8 @0x23ca2..0x23cb2: world-gen loop, on the
    per-empire home planet: owner byte := empire (0x23ca7), pop +0x42 := 2
    (0x23cac), then MOV EBX,0xffff / MOV EDX,0x5 / CALL 0x38818 — the
    PICKER path, NO explicit slot. Second site FUN_00041d5c..0x41d7b:
    pop := 2, owner := event byte [EDI], +0x67 := DAT_00012e10, then
    EBX := 0xffff / EDX := 5 / CALL 0x38818 (picker, no explicit slot).
 2. PICKER WRAPPER FUN_00038818 (20 instr): EAX=planet, DL=item, EBX=slot-or
    -1; calls FUN_0003875c then FUN_00038718 (guard: slot byte1==0xFF, then
    FUN_00038840 ECX=0 picker-cell / ECX=2 explicit-cell; the ECX=2 path
    RE-RUNS FUN_0003830c @0x38a6a and refuses on 0, so a picked cell is
    gated by the checker twice; the activator writes byte1:=item, word2:=1).
 3. PICKER FUN_0003875c (59 instr, listing banked): for slot k in
    [0, word[+0x1a]) with byte1==0xFF and FUN_0003830c(planet,k,item)!=0,
    COLLECT k into a 100-entry list; if count>0: CALL FUN_0007824f (ONE LCG
    draw), IDIV count, list[remainder] -> UNIFORM AMONG LEGAL EMPTY
    CELLS. Not first-empty. 0xffff if none.
 4. CHECKER FUN_0003830c slot-legality chain (325 instr listing): legal iff
    EDI!=0 && EBP!=0; EDI := -1 at entry and EVERY rule only SETS it
    (SETC/SETNZ + XOR-xor patterns read carefully). For item 5 (Colony Base,
    RAM flags word +6 == 0x0001 — dump scripts in §12 evidence):
      rule A @0x38446  item flags bit0 -> EDI := -1 (CB always legal here);
      rule B @0x38493  cell class != 0 -> EDI := -1; class==0 stays legal
                       unless item 0xff or flags bit1 — the barren path
                       FALLS THROUGH to rule C and is NOT zeroed for item 5;
      rule C @0x384db  illegal iff (slot<+0x18) != (item < PTR_DAT_00073e3c
                       =22): CB (5<22) legal ONLY on surface, orbital illegal;
      rule D @0x38519  illegal iff rock XOR (item==0x26) — CB illegal on rock;
      rule E 0x38554 / rule F 0x38576 gated to items 36/35 — N/A;
      rule G @0x385b7  adjacency, SKIPPED for item 5/35 (0x385f6 CMP DL,5
                       JZ end). NET: CB legal on EVERY non-rock surface cell,
                       barren INCLUDED.
 5. CENSUS (scripts/r1_cb_rank_final.py per-world rows, r1_cb_picker_law.py
    battery, r1_cell_choice_census.py Q1-Q3): 72 turn<=1 home CBs, ranks over
    the A-set (non-rock, barren-included) span 2..69 with KS D=0.085 (crit
    0.192 alpha .01) and z=+0.49 -> UNIFORM CONFIRMED; 19/72 (26%) on barren
    ~ terrain barren share (rule-B reading confirmed; the t40 nonbarren-only
    rank space was a filter artefact — raw dump Stavern I turn 0 shows CB
    ALONE on a class-0 cell, every other slot empty). ZERO CBs on rock in
    2810 corpus CB cells (all saves) — rule D holds absolutely.
    Residual: rank<2 never observed (0/72; uniform expectation ~2.4,
    p~0.09) — NO code counterpart exists in the chain, treated as sampling,
    NOT pinned.
 6. HARNESS LAWS LEARNED (turn clock!): member index = GUEST-PHYS + (base -
    0x1BF450) (r1_pros_growth.turn_of). A hard-coded "+136" H and a
    member[phys] read BOTH silently mis-map mid-run runs whose base differs —
    the t42 "rank 0/1 observed" mid-population reading was exactly this
    artefact and was retracted before landing. Population selection MUST
    filter turn<=1 on each save file, not on a corpus-first dedupe (luring
    mid-game worlds with matching identities inflated 72 -> 162).
 7. COLONY-ARRIVAL CELLS: the event handler FUN_0003aa0a @0x3b0bd..0x3b0d1
    runs the activator FUN_00038840 mode 0 with the CARGO SLOT record word
    +0xae (legality gated at @0x3afed via FUN_0003830c); the upstream
    cargo-slot chooser is NOT recovered [open]. FUN_00041d64 (picker + pop:=2)
    is the site consistent with the t41 arrival observations (ranks 4, 40).
 Rewrite: Campaign::drawCbCell = ONE worldLcg_ draw % nb over non-rock cells
 (homes ctor + seedColonyBaseColony); t40 barren-exclusion + rank>=2 floor
 REPLACED. Pins campaign_home_placement_law_t40 (non-rock, barren allowed) +
 campaign_cb_cell_uniform_t42 (every non-rock cell reachable, none of the
 rock, barren share band). Timelines: 2024 Control t762, 13 Extinct t324,
 42 Extinct t561 (PLAYTHROUGH.md regenerated).

## 13. BUILT-ITEM CELL LAW CLOSED (t43) — picker-ignores-slot + rule G adjacency

Two static findings upgrade the t40(6) "cell selection OPEN" default:

 1. THE PICKER IGNORES THE CALLER'S SLOT. Listing of FUN_0003875c (59
    instr): item is stashed at 0x38769 (MOV [ESP+0xd0],DL) BEFORE EDX is
    clobbered at 0x38770; pushed EBX/ECX are never re-read (no stack reads
    of their slots in the listing); the wrapper FUN_00038818 forwards the
    PICKED value into the activator, not the caller's EBX. All 19 xrefs to
    FUN_00038818 were enumerated; the 16 build/completion sites in
    FUN_0003f130/FUN_0003f758/FUN_0003fc4c pass EBX=0 (XOR EBX,EBX at
    0x3f7f2/0x3fc6a/0x3fd1c...) — under this law those zeros are inert:
    EVERY placement including Factory/Lab/rock-item 0x26 completions is the
    uniform random draw over checker-legal empty cells. This is the second
    independent refutation of prefix-from-0 (first: measurement 0/2720).
 2. RULE G ADJACENCY (checker FUN_0003830c @0x385b7..0x386fe): for surface
    slots, EXEMPT item 5 (0x385f9) and item 0x23 (0x38602): if target
    word2 bit0 -> exit (legal, irrelevant for empty picks); else row =
    FUN_0003965c(planet,slot) ((row<<16)|(col+rowStart[row])), four
    FUN_000395c4 probes (row-1,x),(row+1,x),(row,x-1),(row,x+1); ANY probe
    landing on a word2-bit0 slot jumps to the exit WITHOUT zeroing EDI =>
    LEGAL; no probe active => XOR EDI,EDI => ILLEGAL. BUILT ITEMS REQUIRE
    AN ACTIVE NEIGHBOUR.
 3. GRID GEOMETRY (decompile FUN_0003965c/FUN_000395c4): continuous-x hex
    offset layout via planet-type (byte +0x14) row tables. IMAGE copies of
    DAT_0007445c/0x744a8 are STALE CODE BYTES in our restored bin AND the
    static RAM region reads ZERO in save dumps; the RUNTIME tables live at
    (terrain weight rows 0x744f4-copy - 76) widths / - 152 starts, located
    per save by the 44-byte kRows fingerprint — verified IDENTICAL across
    484 saves, row sums == live +0x18 (7/11/23/45/73 1:1 with type 0..4):
      starts t0 [0,0,0,0,4,4,5]      widths t0 [0,0,0,0,2,3,2]
      starts t1 [0,0,0,4,3,4,5,6]    widths t1 [0,0,0,1,3,3,3,1]
      starts t2 [0,0,3,2,3,3,4,5,7]  widths t2 [0,0,1,4,4,5,4,4,1]
      starts t3 [0,2,1,1,2,2,3,4,5,7] widths t3 [0,2,5,6,6,7,6,6,5,2]
      starts t4 [1,0,0,0,1,1,2,3,4,5,7] widths t4 [3,6,7,8,8,9,8,8,7,6,3]
    (trailing rows 0). HARNESS LAW: any DAT table measured from saves MUST
    be located by content fingerprint, never by VA+H (t42 turn-clock lesson
    generalised; first t43 run "REFUTED 4 violations" was exactly the
    zeroed-table artifact, caught before landing).
 4. MEASUREMENT (scripts/r1_built_cell_law.py; geometry fixed via (3)):
    213 worlds; item census {0:107, 1(Factory):362, 5(CB):2810, 21:3};
    ACTIVE non-CB items with ZERO active neighbours in the FINAL save = 0;
    4/4 zero->later-active transitional rows resolved as geometry artifact
    (re-zero transitional = 0). RULE G CONFIRMED on the observable item mix
    (Factory dominates; rarer items unpopulated in captures [unverified
    beyond the code reading]).
 5. NOT RECOVERED (stays open, sub-item): the cargo-slot chooser upstream
    of word +0xae for the transport-cargo path @0x3b0bd (the checker gate
    @0x3afed re-runs FUN_0003830c on the chosen slot, so rule G binds the
    cargo pick too, wherever it comes from).
 Rewrite: buildPhase completion surface assignment = drawItemCell (ONE
 worldNext() over empty non-rock rule-G-legal cells; degenerate no-legal-
 cell fallback = lowest free non-rock, documented), homes/colonies keep
 drawCbCell; static cellActiveNeighbour + sizeClassFor bank the geometry
 (pin campaign_built_cell_rule_g_t43: symmetry all 5 types, neighbour
 degree 1..4, draw spread + adjacency). Timelines shift (new worldLcg_
 consumption): 2024 Control t777, 42 Extinct t583, 13 Control t593
 (seed 13 FLIPPED Extinct->Control — chain adjacency changes where
 production lands; PLAYTHROUGH.md regenerated).

## 13.5 CARGO-SLOT CHAIN (t44, PARTIAL close — chooser law pinned, AI choice open)

The +0xae writer search (search_instructions "xae", 31 hits, all in
FUN_0003aa0a/FUN_0003a7b0 ship/event code) resolves the t43 open sub-item
into a CHAIN, not a chooser function:

 - The planet/command object fields are a triple: +0xab pending item byte
   ('05' Colony Base, '17' automation, 0xff none), +0xac CHOSEN slot,
   +0xae CARGO slot, +0xb0 follow-up slot, +0xb2.. 39-entry candidate
   queue (stride 5, event 0x34 fills via FUN_0003830c legality per item).
 - EVENT 8 (handler FUN_0003aa0a param_2 < 9 branch @0x3ac14): +0xac :=
   FUN_0003a880(coords from the event payload). FUN_0003a880 (45 instr) is
   a PURE COORDINATE->SLOT CONVERTER — no RNG:
     orbital-direct (13 < X < 153, 119 < Y < 469):
       slot = surfaceCells + 5*((X-13)/70) + (Y-119)/70   (ring slots)
     else fallback: (row<<16|col) = FUN_0003a820(X,Y) [linear coord decode:
       ((Y*15)*2 + X*15*? ...) / -0x484 family], then slot =
       FUN_000395c4(current-planet, row, col).
   Post-validation @0x3ac23..0x3aca5: if owner != player AND item != 5 AND
   slot != -1, the slot survives only when the cell byte == 0x17 (the
   '17'-automation interaction), else +0xac := 0xffff.
 - EVENT 4 (colonisation @0x3af4c..0x3af6d): +0xae := +0xac; NOTHING
   happens unless +0xae < 0xffff; legality re-runs FUN_0003830c @0x3afed;
   item '05' branch = owner := transport byte [ship+0x56], pop := 2,
   +0x67 := DAT_00012e10 (turn), FUN_00038840 explicit-slot activator
   @0x3b0d6 — exactly the t41-observed arrival state.
 - Player provenance: coords = mouse click (UI event payload). AI
   provenance: every AI arrival MUST carry a valid +0xac, so the AI
   dispatches EVENT 8 with landing coordinates picked in the AI ship-
   control code — NOT recovered (the chooser is not in the placement
   chain; hypothesis space = FUN_0003xxxx AI family, needs the dispatch
   site of event type 8/4 first).

 Rewrite impact: NONE. Placement in the original is an explicit slot gated
 by the SAME checker (rule G binds cargo picks), and Colony Base is rule-G
 EXEMPT, so the rewrite's uniform non-rock draw for arrival CBs is
 observation-consistent (barren share + ranks 4/40). AI landing-site law
 -> docs/BLOCKED.md (default: picker draw).

## 14. SELECTED-ABILITY ("GOVERNOR") BRANCH CLOSED (t45) — FUN_00038ba4 @0x38df0..0x38e29

Field identity (writer census scripts/r1_0x54_writer_sweep.py, exhaustive
over the restored image for every memory-writing encoding at [reg+0x54]:
88/89/8a/8b/c6/c7/80-group/86/87/8f + SIB counting — 23 writes, 130 reads/
cmps, 61 SIB-form): the ONLY value-writing writer in planet-record context
is the cell ACTIVATOR @0x38b26 (activates slot byte1 AND stores the same
item id into planet +0x54; the CMP DL,0x23 skip at @0x38af3 covers the
SLOT store, not the planet byte), plus six immediate :=0xFF clearers
(0x21f3e, 0x37f93, 0x38a1f, 0x39296, 0x3a159, 0x49dd2 — queue-complete /
demolish / new-record paths). The 0x6xxxx-0x70xxx cluster (imm 0/1 stores
+ dword readers with *0x10 scaling) is a DIFFERENT structure (no function
body contains them; values 0/1 never appear in the +0x54 corpus histogram).
XCHG/POP writes at +0x54: zero. So +0x54 = selected/activated item id,
0xFF when none — the S8 queue reading and the S6e "governor" reading are
THE SAME FIELD; a governor value 33/34/35 arises only when the player/AI
cell-SELECTS a special item (§413 mode 3 writes +0x54 := item idx).

CORPUS (scripts/r1_governor_census.py, 484 saves, 2810 owned records via
the t33-corrected walk): values 0xFF x2418, 0x01 x282, 0x00 x107, 0x15 x3
— trigger values 33/34/35 NEVER occur (0/2810). The branch is inert on ALL
measured state (consistent with T34's 2720-sample battery), which is why
earlier captures could not close it from the POSITIVE side. Closure route:
the static branch is now pinned verbatim AND its every operand resolved —
that is the measurement (code + corpus + runtime config).

BRANCH LAW (raw disasm, accumulator identity cross-verified by the three
doubler blocks immediately above: item 12 Hyperpower doubles [ESP+0x28] at
@0x38d6a = IND, item 13 Fertilization [ESP+0x10] @0x38da5 = PROS, item 14
Internet [ESP+0x20] @0x38de0 = RES; matches T35 gating):
  @0x38df0 CMP byte [rec+0x54],0xFF -> skip when empty-queue
  @0x38df6 EAX = [ESP+0x28] >> 2    ; IND accumulator AFTER doubling
  0x38e00 DL==0x21 (33 Endless Party)         -> [ESP+0x10] += EAX  (PROS)
  0x38e0b DL==0x22 (34 Scientist Takeover)    -> [ESP+0x20] += EAX  (RES)
  0x38e16 DL==0x23 (35 Automation)            -> [ESP+0x18] += dword [0x743b9]>>0x18
The 0x743b9 operand is ITEM-TABLE DATA, not an immediate: row 35 base =
0x73e40 + 35*0x28 = 0x743b8, dword = row bytes +1..+4 = (res,pros,mpop,
UPOP), SAR 0x18 lands on UPOP(35) — RUNTIME-MEASURED 1 in 32/32 saves
(item-table dump via pointer law; row 35 name verified 'Automation').
Downstream order is exact: PROS bonus joins the accumulator BEFORE the
pow-compression block (@0x38e62 trunc((v+1)^0.85)); RES is raw so word =
dbl(acc) + bonus; the Automation bonus lands in the +0x4c used-pop word
(then chain-clamped 0..100 / 0..pop / 0..+0x42 at @0x38f01..0x38f5c).
Bonus is NOT itself re-doubled (branch sits after all three doublers).

Rewrite: PlanetState::governor (+0x54 analog, default -1 = measured corpus
state); storedProsFor adds rawIndAccFor>>2 when governor==33, storedResFor
adds it raw when governor==34, usedPopFor adds UPOP(35) when governor==35
(consumers needClassFor + selector gates routed through usedPopFor). Pin
campaign_governor_law_t45: corpus-default inertness + per-branch exact
deltas on a synthetic 3-Factory home (CB acc 1 alone cannot light the
branch — measured corollary: the original needs IND acc >= 4 for ANY
visible governor effect). Timelines UNCHANGED (branch inert by default):
2024 Control t777 / 42 Extinct t583 / 13 Control t593 re-verified.
