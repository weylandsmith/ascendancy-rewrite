# combat.md — damage application evidence (t85g, first mid-turn capture)

Source: the t1253 sitting (user actions: alliance proposal #2 to Orfa, war
on Ungooma, one Ungooma fleet destroyed with return fire). Mid-turn
autosaves (10 s ring, watcher-banked) caught the engagement frame-by-
frame for the first time — previous captures sampled turn boundaries only
and saw nothing but deletion results.

## 1. Field law: ship record +0x88 / +0x8c [MEASURED, live both sides]

Per-slot u16 diffs between consecutive autosaves WITHIN turn 1253
(scripts/r1_t85g2_slots.py, window ship_raw stride 0x162):

* **+0x8c = INTEGRITY (hull).** Ungooma design-4 ships baseline 20 at
  t1252 (all 9 live ships of designs 2/4/6/12 census: every design carries
  a CONSTANT integrity at peace: d2/d4/d6=20, d12=40) decrement in
  volley-steps to 0: slot11 20->12->4->0, slot19 20->7->0, slot23
  20->16->12->4->0, slot12 20->13->0, slot2 20->7->3->0.
  Step sizes {8,16,12,4,13,7,3,16,9} — NOT constant => damage per hit is
  variable (design weapon output [unverified which]), and multiple hits
  can land between two autosaves.
* **Death law:** +0x8c reaches 0 while owner byte still set; the record
  becomes owner 65535 (free) at the next autosave the analyzer sees
  (same-turn in-slot flip, else next boundary). t85c presence law holds,
  now with intermediate frames observed. Slots 2,4,11,11,12,15,19,19,21,23
  show owner->free events at t1253; several slots decrement to 0 TWICE
  with DIFFERENT sequences (slot4: 20>16>12>0 then fresh 20>7>0) = the
  t85c freed-record-reuse flip law: a freed record is re-occupied by
  another (undamaged) ship between samples. Wave composition of the
  battle UNVERIFIED.
* **Return fire is REAL and measured:** player design-12 slot14
  integrity 40->38->36->34 during the same t1253 frames (player took 6
  damage across the engagement). No other player +0x8c drop t>=1240
  (census over full stream) — matches testimony "they fired back once or
  twice".
* **+0x88 = MOVES (movement budget).** Decrements of 1..2 per autosave on
  BOTH sides during the battle (Ungooma 12->11->10->9..., player
  90->88->85, 40->38->36->35) and RECHARGE at turn boundary
  (slot34 85->90 at t1249, slot21 10->11 mid... design max 90/40/20
  [inferred max per design = the peace-constant]). Distinct from +0x8c:
  +0x88 never feeds death (dying ships show +0x88>=0 with +0x8c=0).

## 2. Static site: the ONLY integrity subtract in the image [verified disasm]

Byte scan for every write form to [reg+0x8c]: 16 stores, 1 subtract.
The subtract — function 0x4d075..0x4d20e, ship-combat loop:

    4d07c: mov eax,[esi+0x59]        ; count of ships (loop param)
    4d07f: call 0x22304              ; ship-array law fn (banked)
    ...   per-target loop over the ship list at [esp+0x504]:
    4d08c: lea edx,[esi+0x9e]        ; shooter xyz f32[3]  <- confirms
    ...                               ; the banked xyz-at-+0x9e law
          dist2 = (dx^2+dy^2+dz^2)   ; 4d0e6..4d157, double
    4d15f: mov eax,[edi+0x3a]        ; attacker combat-object field
    4d162: shl eax,5                 ; threshold = field*32 (units UNVERIFIED:
                                    ; compared against squared distance)
    4d173: fcompp / jb 0x4d196       ; OUT of range -> skip target
    4d191: call 0x4b740              ; IN range: hit path
                                        (ECX=owner sar 16)
    4d1ea: sub DWORD PTR [esi+0x8c],eax   ; INTEGRITY -= attacker [edi+0x4a]

The only other +0x88 writer nearby (0x4d1a9: +0x88 += [edi+0x4a]) and the
EDX=[esi+0x63]-EAX line are UNDECODED — function body 0x4d075..0x4d20e is
the t85h target for the full firing-order/shield path (shields, if any,
must sit inside 0x4b740 or the [edi+0x4a] attacker snapshot).

CAVEATS: [edi+0x4a] is an attacker COMBAT-OBJECT field (every ship record
reads 0 for +0x4a at turn boundary — combat objects are built at battle
entry). Shield subtract-vs-absorb: NOT yet seen. Hit probability: not
seen as a roll at THIS site (range check is deterministic; a roll may sit
inside 0x4b740).

## 2b. Hit-path 0x4b740 (t85g, same scan) — TWO-LAYER ABSORB STRUCTURE

Full body 0x4b740..~0x4b8d8 (args: EAX=shooter, EDX=mode[esp+8],
ECX=target idx, stack=[shooter-owner?]). Decoded spine:

    4b7a7: ax = [esi+0x9c]; al &= 0x10       ; a ship FLAG bit
    4b7c4: edi = [esi+0x90]; if edi <= [esp] -> edi clamped (bit |=2)
    4b7e0: ecx = [esi+0x8c]; if ebp < ecx clamped (bit |=4)   ; both
                                            ; deductions CLAMPED at fields
    4b88a: mov [esi+0x90], edx               ; LAYER-1 store (clamped)
    4b890: mov [esi+0x8c], ebx               ; LAYER-2 store (clamped)
    4b896: cmp ebx,1 / jge 0x4b8d8           ; hull < 1 -> call 0x49d2c
                                            ; (esi=ship, edx=owner,
                                            ;  ebx=[+0xa7]>>24) = STATIC
                                            ; DEATH HANDLER (candidate:
                                            ; record-free path)

So each hit deducts from +0x90 AND +0x8c as clamped layers — structurally
consistent with shields(+0x90)-then-hull(+0x8c), though WHICH deduction
maps to which layer (and what +0x9c bit 0x10 does — flag nulls edi to 0
at 4b7bc, i.e. SKIPS the +0x90 layer) is not yet resolved. Supporting
law in same fn: target star record located via [[target+0xa]>>16 *39*32
+ 0x13bc5] (star-block stride law CROSS-CONFIRMED, docs/re/r1-savestate)
then call 0x43a4c (star-defense contribution?). ASSERT strings 0x852a8/
0x852b7/0x852c6 = range guards (same 0x2a428 reporter as raceneg).
CAPTURE NOTE (corrected same session): the +0x90 LAYER IS LIVE in the
t1253 fight — charge/discharge cycles 0->10->5->0 (player slots 0,14),
0->5->0 (slot 3), 0->2->1->0 (Ungooma slot 2), 0->6->0 (slot 12), with
DIFFERENT charge values per side (10 player vs 2-6 Ungooma) consistent
with design-based shield capacity. It reads 0 at every turn boundary
(recharges/disables out-of-combat), which is why no boundary sample ever
showed it. The two-layer absorb (0x90 first, then 0x8c hull — store order
4b88a then 4b890) is now MEASURED ACTIVE on both sides. OQ-010 residual
narrows to: hit probability (no roll seen), firing ORDER, the exact split
of [edi+0x4a] into shield-hit vs hull-hit amounts, and the +0x9c bit-0x10
flag identity (skips the 0x90 layer at 4b7bc).

## 2d. t86 W6-A1: [reg+0x90] writer census + attacker-object ID (CORRECTS S2)

Tool: scripts/r1_t86_write_census.py (byte scan for mov/sub/add store forms,
disp8 mod=01 + disp32 mod=10, plain + SIB scale00; every candidate boundary-
verified with objdump -D -b binary -M intel; R12 trap handled). Control:
finds the known 0x4d1ea +0x8c subtract + 9 more writers, 10 verified / 4
rejected.

+0x90 writers, ship-record class (13 verified image-wide; 0x6f540/0x70c9d are
UI-struct, [ebp] ones are stack locals):
* INIT 0x4a756 (ship reset/init family): WORD [ship+0x9c]=0 then
  0x4a76c: [ship+0x88] = call 0x4a99c (MOVES total from gizmos).
* CHARGE 0x49f15 (0x49e78, per-gizmo loop step 7 over ship+0xab, count
  [ship+0x15a]; gizmo rec = idx*0x6a + 0x7650c; gate gizmo[+0x33]&0x20):
  ship+0x88 -= gizmo[+0x36] (POWER cost); if gizmo[+0x32]==1 (CAT_SHIELD)
  ship+0x90 += gizmo[+0x56] (SHIELD STRENGTH).
* FIRING 0x4a71f same law in the fire loop 0x4a6a6..0x4a725; 0x4a6a6 zeroes
  +0x90 at fire-loop entry; 0x4a73a: flag [ship+0x9c]&8 -> +0x90=0.
* ABSORB 0x4b88a (hit path, known).
=> SHIELD-LAYER IDENTITY CLOSED: +0x90 is shield charges; capacity/charge
   comes from CAT==1 gizmos' Level field (+0x56, == file Level for the 6
   shields: 1/2/1/2/4/3/5 [verified design table dump, slot-48 t1254]),
   power at +0x36, range at +0x3a. +0x88 MOVES = sum over gizmos (0x4a99c).

CORRECTION to S2 [verified disasm 0x4cd90..0x4cde3]: EDI is NOT a battle-
built attacker snapshot. Dispatcher 0x4cd90 sets
  EDI = 0x7650c + 0x6a * byte[ [ship+0x63] ]   (gizmo/design table),
so [edi+0x4a] = attacker's CURRENT FIRING GIZMO damage field, [edi+0x3a]
its range, [edi+0x4e] a second range-ish field. The static table reads
(76 rows, names byte-verified Mass Barrage Gun..Hyperfuel): weapons
+0x36=Power +0x3a=Range +0x3e=Level(=damage per gizmo semantics per vendor
gizmos.txt header) +0x4a=15..100 (== file Industry column VALUES at my parse
offset — COLUMN MAP NOT SETTLED, see caveat) +0x56=Level (shields).
0x4d075 is a JUMP TARGET of dispatcher case cl==0x38 family (0x4d5bb) — the
function is a gizmo-mode dispatcher, each case a firing/effect mode; case
mode==1 routes 0x4ce33 -> 0x4d594 (sub [ship+0x88], ebp) which reaches
0x4b740. Damage per hit = design[+0x4a] (single gizmo per call — the t1253
variable step sizes {8,16,12,...} [inferred] = different shooter gizmos /
multi-call sums, NOT a random roll at 0x4d1ea).

CAVEATS (honest): (1) file<->design-record column mapping only PARTIALLY
aligned in the t86 check (f36/f3a/f3e == file cols 2/3/4 for weapons,
f56 == Level for shields, but f4a matched Industry 75/76 with one row off —
row-74/75 parse slip; the exact gizmos.txt column -> +0x4a identity and the
0x4cde3 prologue guard law stay OPEN); (2) hit probability, firing ORDER,
star-defense call 0x43a4c contribution still unseen; (3) no rewrite code
change this iteration (no shipped-behaviour claim touched). OQ-010 stays
OPEN (strict-close): residual = order + 0x43a4c + column map + in-battle
multi-hit verification.

## 2e. The t86-remaining queue (static, no capture needed)
1. Writers of ship [reg+0x90] (u16/u32 stores; subtract census done for
   +0x8c only) + init sites -> shield-layer identity test.
2. Rest of 0x4d075..0x4d20e (the +0x88 MOVES write at 0x4d1a9 pairs with
   [edi+0x4a] again — verify the moves-cost-vs-damage branch).
3. Ship TARGETING law: consumers of the SOAttack/SODefendPlanet order
   names (pool 0x88e60 block has zero direct refs — find the order
   dispatch via the SOPatrol table at the ref site near 0x27d-offset
   family and the battle-control module).
4. Named-key AI parameters: SHIP_PATIENCE (+0x1b0) readers.

## 3. Cross-effects banked same sitting (diplomacy)

* Player PROPOSE_ALLIANCE moved BOTH cells at t1253->1254:
  att[Orfa->Chamachies] 487->526 (+39), att[Chamachies->Orfa] 600->590.
  t85c said proposals do NOT move the AI-side cell — CORRECTED: they do
  (+39 here); acceptance law unchanged (526 < Orfa ACCEPT_ALLIANCE 570,
  no alliance, state stays 1).
* Player DECLARE_WAR on Ungooma: reciprocal state 1->2 both cells,
  att[Ungooma->Chamachies] 477->437 (-40). Second independent
  reproduction of the t85b reciprocity law.

## 4. Score datum (OQ-021) — systems_full hypothesis FALSIFIED

DAT_482fb trajectory (turn-change trusted rows): t1151=10, t1157=8,
t1158=14, t1170=12, t1171=14, t1186=15, t1238=12, t1247=15, t1251=13,
t1252=15, t1253=14, t1254=14 — while systems_full is flat 26->28->32.
score_stars == systems_full matched 0/786 rows t>=1250. The variable is
NOT a system count; it MOVES (up and down) with no matching system
change. See docs/re/score.md S9.
