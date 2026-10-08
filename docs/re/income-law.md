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
