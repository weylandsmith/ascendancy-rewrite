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
threshold DAT_000066e4=50 at 0x39337 -> upkeep+1 (+1 active-Hyperpower
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
counter >= 50 -> pop += 1 (+1 more if FIRST slot itemIdx 12 Hyperpower
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
 COST (u16 item+8) is NOT deducted in this handler: deduction site is
 the resource-budget path, still open (image-wide read census of the
 item-table +8 offset finds only the stride-8 growth-cap table at
 0x73e48 — COST must be read via base+stride forms).
