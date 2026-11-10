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
* **+0x88 = POWER (gizmo power budget)** — t101 RE-ATTRIBUTION: this
  section's original label "+0x88 = MOVES" was WRONG; the vendor ship
  panel (0x1da8a..0x1daaf, cdecl pushes into 'POWER %d MOVES %d INTEGRITY
  %d' F 0x831c9) prints [ship+0x88]=POWER, [ship+0x94]=MOVES,
  [ship+0x8c]=INTEGRITY (scripts/r1_t101_field_verify.py leg1, byte-
  pinned). The t85g RAW observations stand unchanged: decrements of 1..2
  per autosave on BOTH sides during the battle (Ungooma 12->11->10->9...,
  player 90->88->85, 40->38->36->35) and RECHARGE at turn boundary
  (slot34 85->90 at t1249, slot21 10->11 mid... design max 90/40/20
  [inferred max per design = the peace-constant]). Distinct from +0x8c:
  +0x88 never feeds death (dying ships show +0x88>=0 with +0x8c=0).
  MECHANISM (t101, cited): the decrements are per-gizmo POWER upkeep
  `[ship+0x88] -= design[+0x36]` @0x4a710 (FUN_0004a658) and the travel
  burn @0x4a307; the boundary RECHARGE is FUN_0004a74c->0x4a76c =
  trunc([ship+0x18] * (1 + clamp((T - [ship+0x52])//100, 0, 10)/10)),
  cap = [+0x18], T = u32 guest X 0x12e10 — verified 25/35 exact + 35/35
  bounded on 60.sav (r1_t101_field_verify.py leg3). MOVES = +0x94 is
  re-granted each turn from the drive stat [ship+0x10] and consumed by
  travel fsub/fistp @0x4a30f..0x4a314. Full probe trail:
  docs/re/_wip_t101.md F2/F4/F5/F7.

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
[t107 CORRECTION: fixed-tool census = 14 image-wide — this section's tool
missed 0x49307 (desync reject): WORD[+0x56]:=0xffff, DWORD +0x90:=0,
+0x8c:=1, BYTE +0x5d:=0, then +0x88:=[+0x90], +0x98:=[+0x8c]. Owner:
FUN_0004929c = init_global_gizmos per ships.md S8 (t15b read in full) —
this is the banked "init ship-object template fields" step, an ADDITIONAL
template-time zeroer beside runtime INIT 0x4a756, not a mid-game writer.
Semantics consistent (fresh template carries +0x90=0); no law change. See
docs/re/census-audit.md S4.]
* INIT 0x4a756 (ship reset/init family): WORD [ship+0x9c]=0 then
  0x4a76c: [ship+0x88] = call 0x4a99c (POWER re-init = trunc([ship+0x18] *
  (1 + clamp((T-[ship+0x52])//100,0,10)/10)) — t101 corrects the earlier
  "(MOVES total from gizmos)" gloss; 0x4a99c never touches gizmos).
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
   power at +0x36, range at +0x3a. +0x88 is the POWER budget itself
   (t101: re-init trunc([+0x18]*(1+age/1000-style multiplier, F7); the
   t86 "MOVES = sum over gizmos (0x4a99c)" tag was wrong — 0x4a99c reads
   only [+0x18]/[+0x52]/ds:0x12e10, no gizmo loop).

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

## 2f. t87 W6-A2: gizmo dispatcher case table, 0x43a4c identity, COLUMN MAP CLOSED

### (c) gizmos.txt column -> design record — CLOSED 76/76 (tool scripts/r1_t87_gizmo_table.py)

Loader FUN_00049074 (gizmos.txt referrer 0x49081) is the law, and its
push/lea idiom 0x49126..0x49165 + `add esp,0x2c` pins the slot arithmetic:
name->rec+0; then col1 Cat->BYTE +0x32 (S+0xc8), col2 Power->+0x36,
col3 Range->+0x3a, col4 Level->+0x3e, col5 NumUses->+0x42, col6 Industry->
+0x46, col7 Special1->+0x4a, col8 Special2->+0x4e, col9 ResReq->BYTE +0x35
(S+0xe8); flag bits -> WORD +0x33 (bits OR'd per listed bitpos, 255-terminated
loop 0x491ff..0x49238). Runtime join (save/50.sav, B=0x1bf4d8 6/6 anchors,
member = B+0x82bb0+X law): ALL 76 names byte-match AND all 10 mapped fields
match the file 76/76 (VERDICT: FULL COLUMN MAP CLOSED, exit 0).
CORRECTION to S2d: +0x4a == FILE Special1 column, NOT Industry (+0x46 is
Industry). The t86 "+0x4a==Industry 75/76" was coincidence — Special1 values
happen to lie in the same 0..100 range. Post-pass 0x4923a zeroes +0x52..+0x66
then the Cat jump table at 0x344b0 copies Level(+0x3e) [cats 0,1,2,3] or
Power(+0x36) [cat 4] into ONE derived slot per row (+0x52 scanner-ish, +0x56
SHIELD strength, +0x5e, +0x62, +0x66=power-supplied) — explains t86's
+0x56==Level for shields. Weapon DAMAGE PER HIT = design[+0x3e] Level
(Mass Barrage 1 .. Nanomanipulator 13), used at the cat-0 path 0x4d075;
special gizmos apply design[+0x4a] Special1 (e.g. Gravity Distorter 65).

### (a) Dispatcher 0x4cd90 = SPECIAL-GIZMO ACTIVATION HANDLER (tree re-read CORRECTS draft + t85g)

Entry law (verified disasm 0x4cd90..0x4ce33): EAX=ship->ESI; EDX=mode arg
(saved +0x73c); cl = BYTE[ [ship+0x63] ] = ACTIVE GIZMO ID (0xff -> assert
0x2a428 msg 0x277d); EDI = 0x7650c+0x6a*cl (design row, t86 law); ebp =
MIN(design[+0x36] Power, ship+0x88 Moves); accumulator (esp+0x72c, entry
value 1-bit family computed 0x4cda4..0x4cdfd) gates everything: bit0==0 ->
return 0x4d680. mode==1 -> 0x4d594 FIRST ([ship+0x88] -= ebp = POWER COST OF
ACTIVATION), then FALLS INTO the case compare-tree 0x4d59a..0x4d680. Tree
decoding trap: each `jbe target` follows `cmp cl,K` + `jb elsewhere` and
therefore captures the SINGLE value cl==K, not a range. FULL CASE TABLE
(every target body disassembled this session; gizmo names from the 76-row
file list above):

| cl | gizmo | target | effect (verified disasm) |
|---|---|---|---|
| 0x24 | Recaller | 0x4d033 | ship+0x59 := dword[[ship-owner-rel*2 + 0x12e1d]] (target-list reset to own-race law); calls 0x220a8, 0x21f58 |
| 0x26 | Smart Bomb | 0x4d274 | loop ships (0x22304); per ship: call 0x4b740 ONLY when relation BYTE [0x12fd6 + att_row + def] == 2 (AT-WAR gate through the diplomacy matrix) — area damage is LAW-GATED, not indiscriminate |
| 0x27 | Gravity Distorter | 0x4d332 | loop ALL ships, skip self (cmp esi,ecx @0x4d360), per-pair f32[3] delta of +0x9e (kinematic field build 0x4d332..0x4d4f6) |
| 0x2e | Gravimetric Catapult | 0x4ce4c | ship xyz +0x9e/+0xa2/+0xa6 := NEGATED f32[3] in place |
| 0x35 | Cannibalizer | 0x4d1e7 | [ship+0x8c] INTEGRITY -= design[+0x4a] (=5); [ship+0x88] += design[+0x4e] (=20); hull<1 -> 0x49d2c death |
| 0x38 | Gravimetric Condensor | 0x4cf05 | loop ships; filter [t+0x58]==4; f64 distance (0x76da0) of t+0x9e vs design[+0x4e]*32 (=10*32) |
| 0x39 | Accutron | 0x4d546 | OR BYTE [ship+0x9c], 4 |
| 0x3a | Remote Repair Facility | 0x4cffb | [ship+0x8c] += design[+0x4a] (=5), CLAMPED at [ship+0x98] (max integrity — first sighting of a +0x98 MAX-INTEGRITY field) |
| 0x3f | Toroidal Blaster | 0x4d50e | 0x49714(ship,2) slot-find (-1 -> exit); 0x496e4 rebuild; OR [ship+0x9c], 2 |
| 0x41 | Replenisher | 0x4d228 | loop own gizmo slots ([ship+0x15a] count, stride 7 from ship+0xab): skip 0xff/0x41; slot[+1] WORD := design[gizmo][+0x42] NumUses — RESTORES PER-GIZMO USE COUNTS |
| 0x45 | Invulnerablizer | 0x4d560 | OR BYTE [ship+0x9c], 0x10 (the t85g flag that NULLS the +0x90 shield absorb at 0x4b7bc — identity now MEASURED: this bit = INVULNERABLE, set by the Invulnerablizer) then slot rebuild (esi+0xab + 7*((ship+0x63 - EAX)/7) via 0x496e4) |
| 0x48 | Self Destructotron | 0x4d075 | THE FIRE LOOP: per-target over ship list, squared dist (double) vs design[+0x3a]Range*32 (=40*32) -> call 0x4b740 hit path |
| 0x4b | Hyperfuel | 0x4d1a9 | [ship+0x88] POWER += design[+0x4a] (=40) (t101: field is POWER, not MOVES — the help.txt "moves" prose conflates the two budgets; the panel prints +0x88 as POWER); slot rebuild/removal via 0x496e4 |

NO CASE (falls to ret): all CAT-0 guns 0x00..0x09, shields, drives,
scanners, generators, and specials 0x25,0x3b..0x3e,0x40,0x42..0x44,0x46..0x47,
0x49,0x4a. => CORRECTIONS: (1) t85g's "function 0x4d075 = the ship-combat
loop" is now scoped — it is the SELF-DESTRUCTOTRON case body (area blast),
not the generic gun path; (2) this dispatcher handles ONLY cat-5 special
activation + power accounting. GENERIC GUN FIRE must live in one of the
OTHER 0x4b740 callers: {0x1a146, 0x39d9f, 0x3a0b3, 0x4bb56} (call-site scan
for rel32 e8 edges this session) — 0x4bb56 is in the same module family
(neighbouring the dispatcher) and is the t88 candidate. Dispatcher's sole
caller in the image: 0x4a3c4 (inside the 0x4a6a6 fire-loop module that also
zeroes/charges +0x90 — t86). FIRING-ORDER: within this dispatcher, mode==1
charges power BEFORE the effect runs (0x4d594 fall-through); per-gizmo
NumUses decrement sites = slot[+1] WORD (writer set 0x4d228 family + the
rebuild helper 0x496e4) — the FULL multi-gizmo ordering is the caller 0x4a3c4
loop, t88 target.

### (b) 0x43a4c — IDENTITY CORRECTED: NOT star defense, the DIPLOMACY-ON-ATTACK handler

Verified disasm 0x43a4c..0x43b0e. Args EAX=obj(relations base), EDX=dx target
race idx (asserts dx>=0 and dx < word[0x13b98] race count 0x21d8; EBX=edi
non-null assert msg 0x84d94). Law: state=BYTE[obj+dx+0x1c0]; if state==2
(AT WAR) -> return 0 (no hostility change needed); else hostility DELTA
d = 10*(word[0x13bc4]+1), DOUBLED if state==3; obj+dx word+0x1b2 ATTITUDE
-= d; if state==3 clamp attitude <= word[obj+0x1cf]-10; then set a bit in the
global "attacked" bitmap: BYTE[[edi+2]sar16 + 0x48304] |= 1<<byte[obj];
return -1 on the bitmap path, 0 on the at-war path. So the t85g hit path's
"star-defense contribution?" call is the ATTITUDE/WRITING-MARK consequence of
firing at a non-at-war power — directly explains the t85g diplomacy observations
(att moves on combat) and is the SAME 0x1b2/0x1c0 law as docs/re/diplomacy.md.

OQ-010 residual after t87: multi-hit/RNG roll still unseen (no roll in any
case body disassembled — damage per call IS deterministic design[+0x3e] or
design[+0x4a]); caller chain 0x4a3c4 (who orders firing, ORDER law); case
0x4cf05 distance-use tail + cl==0x47 routing re-read. NO rewrite code change
(no shipped behaviour claim touched this iteration).

t204 CORRECTION + CLOSURE of this handler (docs/re/diplomacy.md §17,
docs/re/_wip_t204.md): the subtrahend key read at 0x43a99 is MOVSX of the
BYTE at [0x13bc4] (not word), live value 1 in 20/20 playcap saves; the
state-3 clamp is a CEILING (0x43ade JLE skips when att is already <= the
+0x1cf line; slam to line-10 only when still above), not a floor; callers
census EXACTLY {0x39fba,0x3a255,0x4b875}, the combat one fires BEFORE the
shield/hull subtraction (0x4b87a/0x4b888) — the price of firing, so a
repelled attack still pays; global [0x48304]==0 20/20 (zero in-corpus
witnesses). Rewrite MODELLED + pinned (test_diponattack_t204.cpp, gap map
row 13). The "star-defense contribution" question is VOID.

t205 OPERAND CORRECTIONS to the above (docs/re/_wip_t205.md): the handler's
third arg (EBX at 0x4b875) is the STAR record of the engagement location
(chain 0x4b81a mov eax,[esi+0x59] -> 0x4b82c lea 0x13bc5+96*star -> 0x4b868
mov ebx,ecx), not a per-race species record; dword[star_record+2]>>16 == the
star's own row index (20/20 saves), so 0x43afa writes a PER-STAR mark byte
byte[0x48304+star_idx] |= 1<<victim-race. 0x13bc5 stride 0x60 is the runtime
STAR table (t200 vindicated); 0x13bc4 is a scalar global (zero strided refs
image-wide). Rewrite mirror corrected to a per-star vector (campaign.h
attacked_/attackedAt; 129 tests 0 failed, blast radius unchanged).

## 2g. t88 W6-A3: GENERIC CAT-0 GUN PATH + FIRING ORDER + HIT PROBABILITY (all measured, restored image objdump)

Sitting check first: live-timeline.jsonl 238,216 rows, watch.log tail all
t=1254 — NO new turn since t87, assignment stands. Census tool
scripts/r1_t88_caller_census.py re-run GREEN (exit 0): callers(0x4b740) ==
exactly {0x1a146,0x39d9f,0x3a0b3,0x4bb56,0x4d191,0x4d2dd}; callers(0x4a360)
== {0x49f45}; LCG 0x41c64e6d embedded EXACTLY once (0x7825b); zero rel32 rng
edges {0x78249,0x7824f,0x78273} in [0x4a360,0x4f097) — the FULL combat
module family, extended this turn past t86's window.

### Unified gizmo-use dispatcher 0x4a360 (whole body decoded, corrects t87 "shot dispatcher")

EAX=ship, EDX=mode (1 = commit). ecx=[ship+0x63]=ACTIVE slot ptr; edi =
0x7650c+0x6a*gizmo design row. NumUses law 0x4a373..0x4a394: esi=0 iff
slot[+1] WORD==0 (0 = unlimited per gizmos.txt header — VERIFIED consumer);
mode==1 -> DEC WORD[slot+1] at 0x4a390 = THE USE CONSUMPTION SITE. Then
CATEGORY dispatch on BYTE design[+0x32] (0x4a399..0x4a3c4):
cat 0 -> 0x4b8e4 (WEAPONS, below); cat 2 -> 0x4ca50 (drives);
cat 1 -> 0x4c794 (shields + gizmo-0x46 build leg); cat 5 -> 0x4cd90 (t87
specials). Caller 0x49f28 gates on BYTE[ship+0x62]: 0 -> 0x49f54 (movement/
target bookkeeping from +0x67/+0x68), 1 -> 0x4a360; result -> [ship+0x84].
Power accounting: ebp = MIN(design[+0x36], ship+0x88) at entry; charged at
handler tail on mode 1 (e.g. 0x4c614: [ship+0x88] -= cost).

### FIRING-ORDER LAW CLOSED — loop 0x4a55c (stance setter + ordered volley)

0x4a55c (EAX=ship, DL stance arg, ebx=target; callers 0x41b4e/0x421d0/
0x42351/0x42e24/0x43153/0x43301 in the AI-attack module): if [ship+0x88]
MOVES==0 return 0 (t101: [+0x88] is POWER — firing REQUIRES nonzero power,
guns draw the per-shot power the S2h/S2j accounting charges at handler
tail); sets [ship+0x62]:=1 and stance map (verified 0x4a570..
0x4a586): arg 0 -> +0x67=2, arg 1 -> +0x67=1, arg 2 -> +0x67=0 (default
assert 0x2623); [ship+0x68] := target. [t364 CORRECTION, _wip_t364.md C1/C2,
both disassemblers agree: the KEY at the 0x4a399 dispatch is BYTE [ship+0x67]
(handler id), NOT design[+0x32] — the category gate lives in the volley loop
(0x4a5e1); and the arg map is 0->2, 1->1, 2->1, 3->0 (the jbe at 0x4a5a1
captures BOTH 1 and 2). Dispatcher chain: 0->0x4b8e4 gun, 1->0x4c794,
2->0x4ca50, 5->0x4cd90; the 0x4c794/0x4ca50 bodies call NO hit path.] VOLLEY LOOP 0x4a5c1..0x4a5fc: for i in
0..[ship+0x15a) stride 7 over ship+0xab gizmo slots IN STORED ORDER, skip
0xff, gate design[gizmo][+0x32]==0 (CAT==0 weapons ONLY), set [ship+0x63] :=
slot ptr, call 0x49f28 (-> 0x4a360 -> cat0 -> 0x4b8e4); remember slot on
result bit0. => FIRING ORDER = ship slot-array order (build order), EVERY
cat-0 weapon fires per engagement, no interleaving across ships here.
0x4a602 = companion slot-scan (first cat-0 slot with power/uses, -1 none).

### GENERIC GUN HANDLER 0x4b8e4 (t88 primary target; 0x4bb56 call site inside)

Prologue 0x4b8e4 verified (push*5; sub esp,0x50c; EAX=ship -> ebp, mode ->
esp+0x4d0). Law (all disasm-verified this session):
1. active gizmo = BYTE[[ship+0x63]] (0xff assert 0x2a428), EDI design row,
   ebp = MIN(Power, ship+0x88).
2. TARGET = [ship+0x68] (null assert 0x2734); SAME-SYSTEM GATE 0x4b982..
   0x4b99d: BYTE[ship+0x58]==4 && BYTE[target+0x58]==4 && ship[+0x59]==
   target[+0x59] (system-object identity) — guns only hit ships in the
   same system (matches t85g mid-turn frames: combat is per-system).
3. RANGE GATE 0x4b9bd..0x4bab2: 3D distance (f64 0x76da0) of +0x9e f32[3]
   vs design[+0x3a]<<5; flag [ship+0x9c]&4 doubles the limit (fmul const —
   CAVEAT: the const disp32 ds:0x2743/0x2747 land BELOW code start 0x14bb0
   in the restored image (header region unrestored) — value not readable
   statically; the cat-1 twin uses ds:0x85312==2.0 [verified f32], so 2x is
   the [inferred] reading). Gizmo 0x2f has a second tighter gate.
4. DAMAGE ebx = (BYTE design[+0x32]==0) ? DWORD design[+0x52] : 0 — the
   t87-derived derived-Level slot (jump table 0x344b0 copy of +0x3e);
   gizmo 0x2f overrides to design[+0x4a].
5. CALL 0x4b740 hit path (0x4bb56): EAX=target ship, EDX=mode, ECX=
   [ship+0x54]>>16 (ATTACKER race idx), EBX=damage.
6. mode==1 tail 0x4c614: [ship+0x88] -= power cost, then PER-GIZMO
   AFTER-EFFECT TREE on the gizmo id (0x4c623..0x4c777: cases 0x21..0x44 —
   incl the 0x4c70c case zeroing target [esi+0x90] shields + setting +0x9c
   bit8 = shield-strip after-effect).

### HIT PATH 0x4b740 whole-body re-read (t85g partial -> now complete)

Asserts attacker/target race idx < word[0x13b98]. INVULNERABLE gate:
[ship+0x9c]&0x10 -> shield absorb zeroed (t87 flag identity re-confirmed
in-consumer). TWO-LAYER CLAMP: absorb = MIN(damage, shield +0x90) else
remainder spills to hull, set return-flag bit2; hull clamp at +0x8c sets
bit4. mode==1: owner-state word 0x1b2 row via 0x13bc5 star-owner stride-96
index, then CALL 0x43a4c (t87 diplomacy-on-attack). APPLY 0x4b87a: [t+0x90]
-= shield_absorb; [t+0x8c] -= hull_absorb; hull<1 -> CALL 0x49d2c death
(eax=target, edx=[t+0xa7]); if victim owner == DAT_0007458e and
DAT_0007e582>>16 != 0x10 -> event call 0x55a60(0xc, msg 0x7a35c). RETURN =
flags byte (bit0 ok / bit2 shield-overflow / bit4 lethal) — matches
t85g's observed +0x8c volley steps.

### HIT PROBABILITY: MEASURED NEGATIVE — there is NO roll

Full disassembly of 0x4b8e4 + 0x4b740 + all dispatcher/handler bodies shows
NO rng call and NO comparison of a random value against anything; combined
with zero rel32 rng edges across [0x4a360,0x4f097) and the single-image LCG
embedding (0x7825b), combat damage is DETERMINISTIC: every in-range,
gate-passing shot applies design[+0x52] damage split shield-then-hull. The
rng hits at 0x39922/39944/39962 are AI target-position JITTER (rng%1000-500
per axis, clamp 250.0f push 0x437a0000), not a hit roll. OQ-010's
"hit probability" residual is answered by cited absence (scan + full-body
read), consistent with t85g live steps 40>38>36>34 (always-hit, step 2).

REMAINING OQ-010 LEG (next task): rewrite UPGRADE of combatPhase to the now-
cited laws (ordered cat-0 volley, 2-layer clamped absorb, deterministic
damage design-derived, same-system gate, power/uses accounting) — a CODE
task, contract requires a changed code site before the row closes.

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

## 2h. t88a AUDIT of the S2g draft (same-day verification pass, objdump
## work/ascend_restored.bin; census tool scripts/r1_t88_caller_census.py RC=0
## re-confirmed: callers(0x4b740) == 6-set, callers(0x4a360)=={0x49f45}, LCG
## constant unique @0x7825b, zero rel32 rng edges in the three windows)

The t88 draft died mid-session with S2g written but UNCOMMITTED. This pass
re-verified every load-bearing S2g claim instruction-by-instruction and adds
the caller-mode census below.

VERIFIED AS DRAFTED:
* Dispatcher 0x4a360 (disasm 0x4a360..0x4a3cf): ecx=[ship+0x63] slot, edi
  = sx32(slot[0])*0x6a design row; esi=0 iff WORD[slot+1]==0 (unlimited);
  mode==1 -> dec WORD[slot+1] at 0x4a390; dispatch BYTE design[+0x32]
  (0x4a399..0x4a3c4): 0->0x4b8e4, 2->0x4ca50, 1->0x4c794, 5->0x4cd90;
  result -> ebx -> eax. Gate 0x49f28 (0x49f28..0x49f52): BYTE[ship+0x62]
  0 -> call 0x49f54 (movement/target bookkeeping), 1 -> call 0x4a360
  (sole caller edge 0x49f45), result -> [ship+0x84].
* Volley loop 0x4a5c1..0x4a5fc: ebx=i, ecx=&slot(i*7 from ship+0xab);
  gate i < [ship+0x15a]; skip 0xff; skip unless BYTE design[+0x32]==0
  (cmp [eax+0x7653e],0); [ship+0x63]:=slot; call 0x49f28 (0x4a5f1);
  test al,1 -> remember slot. FIRING ORDER = stored slot order, every
  cat-0 gun fires per engagement. Stance setter 0x4a55c verified:
  [ship+0x88]==0 -> return 0; [ship+0x62]:=1; arg->+0x67 map (0->2,
  1->1, 2->0, default assert 0x2623); [ship+0x68]:=target. 0x4a602 is a
  real second function (first cat-0 slot with power/uses, -1 none) with
  ZERO rel32 callers (batmode-table or dead — not load-bearing).
* Gun handler 0x4b8e4 (prologue push*5 sub esp,0x50c verified):
  same-system gate 0x4b982..0x4b99d verified literally ([ebp+0x58]==4 &&
  ==[esi+0x58] && [ebp+0x59]==[esi+0x59]); range: xyz sumsquares -> call
  0x76da0 sqrt, limit design[+0x3a]<<5 (0x4ba57), [ship+0x9c]&4 -> fmul
  ds:0x2743 (header-region const, unrestored — 2x stays [inferred],
  cat-1 twin ds:0x85312==2.0 verified); gizmo 0x2f second tighter gate
  ds:0x2747. DAMAGE 0x4bb2a..0x4bb43 verified: ebx=0; if design[+0x32]==0
  ebx=design[+0x52]; if gizmo==0x2f ebx=design[+0x4a]; ebx==0 -> skip
  (or flag 0x10). Hit call 0x4bb56 verified (eax=target esi, edx=mode,
  ecx=[ship+0x54]>>16, ebx=damage). mode!=1 exits at 0x4bb7a WITHOUT
  charging; mode==1 -> 0x4c614: [ship+0x88] -= MIN(design[+0x36],
  ship+0x88) then per-gizmo after-effect tree 0x4c623.. (verified
  0x4c614..0x4c638).
* Hit path 0x4b740 whole body (0x4b740..0x4b8e3 disassembled this pass):
  two-layer clamp verified literally (shield absorb edi=min(dmg,[esi+0x90])
  else spill ebp, or-flag bit2 at 0x4b7d1; hull clamp at +0x8c sets bit4
  0x4b7e8; [esi+0x9c]&0x10 zeroes edi at 0x4b7bc); apply 0x4b87a..
  0x4b890 (sub then store, shield first then hull); death ebx<1 ->
  call 0x49d2c(eax=target, edx=[t+0xa7]) 0x4b89b..0x4b8a6; victim-owner
  event 0x55a60(0xc) gated on DAT_0007458e && DAT_0007e582>>16!=0x10;
  return flags byte [esp+0xc]. NO rng edge, NO random-compare anywhere in
  0x4b740..0x4b8e3 (hit-probability MEASURED NEGATIVE stands).

NEW THIS PASS — mode census at ALL 13 callers of 0x49f28 (which paths
commit with mode==1):
* mode==0 (probe/no-charge): 0x15cc5, 0x15df0, 0x16ee1 (batmode), 0x415c5,
  0x4240a, 0x4247f, 0x433ba, 0x4342f, 0x438af, 0x439c9 (AI-attack module —
  AI plans with mode 0; several set stance byte +0x67:=5 FIRST, a stance
  value the 0x4a55c setter never writes: 5 = "use gizmo <slot>" mode),
  0x4a5f1 (volley loop itself probes mode 0!).
* mode==1 (commit: DEC uses, charge power, apply damage) — THE ONLY TWO:
  0x25560 and 0x25570, inside the PLAYER command-execution function
  0x2547c (per-system loop over [campaign+0x3335] stride 0x60, ownership
  bits [ship+0x14]|[ship+0x15] masked by 1<<DAT_0007458e, after the
  0x41260 movement resolver returns a command byte ah): ah==3 -> commit
  call 0x49f28(ship,1); ah==2 -> commit call 0x39c10(ship,1) (ability
  use path); ah>=4 -> runtime error 0x2a438(0x8f5, 0xd92) (bounds trap,
  string line 0xd92). => COMMIT LAW CLOSED: gizmo effects apply ONLY in
  the player-command-exec phase via these two edges; all AI/volley paths
  are mode-0 dry-run probes that charge nothing. [verified disasm
  0x2547c..0x2559d this session]
* Self-destruct sites (dispatcher 0x4cd90 case, t87): 0x4d191 and 0x4d2dd
  pass edx=[esp+0x73c] (dispatcher's own mode copy, not a constant);
  0x4d2dd additionally gated on relation byte [edx+0x12fd6]==2 (at-war)
  at 0x4d2ca. Damage ebx=design[+0x4a] at both (0x4d184/0x4d2da) —
  consistent with t86's [edi+0x4a] reading for SPECIALS (column map
  t87: +0x4a = file Special1; cat-0 GUNS use +0x52, NOT +0x4a).
* Orbital/other hit callers: 0x1a146 passes edx=0 (probe; mov edx,1 at
  0x1a112 is stored to the stack at 0x1a12b and edx is re-zeroed at
  0x1a13f — mode-0 dry-run from batmode family; damage ebx=[reg+0x4a] of a
  0x4f48-offset table object; result bit4 (lethal) tested at 0x1a14b);
  0x3a0b3 edx=1, damage = 2*x (add ebx,ebx 0x3a0b1) gated on table byte
  ==0x17; 0x39d9f edx=ebp (variable). These three are the non-gun
  ability/defense fire edges — all also mode-1-capable.

HONEST STATUS: every named OQ-010 residual now has a cited static answer
(firing order = stored slot order 0x4a5c1; hit probability = none,
measured-negative; damage = design[+0x52] guns / [+0x4a] specials; two-
layer absorb + death + power/uses accounting all instruction-verified;
commit law = 0x25560/0x25570 only). Row STAYS OPEN under strict-close:
closure additionally requires the rewrite combatPhase UPGRADE at a cited
code site (contract: closed rows name the changed code site) — NEXT TASK.
Vendor gizmos.txt header (work/r1/game/gizmos.txt lines 15-40) confirms
the semantics lifted: Level=damage(weapons)/strength(shields), Power=cost,
NumUses=uses per turn (0=no limit).

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

## 2i. t89a SCOPING pass for the combatPhase UPGRADE (docs only, no code change — session budget exhausted before the edit; block recorded docs/BLOCKED.md)

SITE CONFIRMED (the STATE "check first" gate PASSED — the rewrite does model
combat): Campaign::combatPhase exists at rewrite/src/game/campaign.cpp:1247
..1322, called from advance() :1376. The upgrade target is the capture
resolution block: the attackScore/defenseScore border walk at :1305..1306
plus the two score functions attackScore :1204 / defenseScore :1226.

STRUCTURAL FACT the upgrade must design around (read this pass):
the rewrite has NO per-ship gizmo inventory anywhere —
* ShipInTransit is {owner, from, target} only (campaign.h:90-94) and
  fleet_ is emptied every turn (expansionPhase, campaign.cpp:929);
* the only gizmo consumers are attackScore (:1212-1218, MAX researched
  weapon Level) and defenseScore (:1231-1237, MAX researched shield Level);
* nothing stores a per-ship slot array, so the original's stored-order
  volley law (0x4a5c1) and the per-hit two-layer clamp (0x4b7c4..0x4b8a6)
  have NO rewrite data structure to be "wired into" as-is.

WHAT THE AGGREGATE MODEL CAN CARRY WITH CITATION (the honest delta):
(a) VOLLEY TOTAL: the cited law fires EVERY researched cat-0 weapon per
    engagement (0x4a5c1..0x4a5fc, S2h-audited), so empire volley damage
    = SUM of researched weapon Levels, replacing the MAX at :1217.
    File values re-verified fresh this pass (extracted/ascend00/gizmos.txt,
    10 cat-0 rows): Level/damage {1,2,4,4,1,4,6,4,10,13}, NumUses
    {1,1,1,1,5,1,2,2,2,3} (0=unlimited per vendor header).
(b) DETERMINISTIC DAMAGE: the shipped uniform noise draws (:1275,
    :1305..1306) are an UNCITED v1 abstraction — the cited law has NO hit
    roll (S2g measured-negative). Removing the draws is the faithful edit
    BUT it re-diverts campaign rng_ and changes ALL timelines: every
    PLAYTHROUGH turn count, the gate 3l 1200-turn budget, and
    campaign_reaches_a_victory. KEEPING the draws keeps timelines but only
    partially matches "deterministic". This is the ONE decision t89 must
    make explicitly (recommend: remove the noise per the cited law and
    regenerate docs/PLAYTHROUGH.md with scripts/record_playthrough.sh,
    then re-verify finite victory on seeds 2024/42/13 + 1/2/2024 — that
    IS the closing measurement).
(c) SHIELD-THEN-HULL: maps to ordering fleetDamage_ subtraction by shield
    absorb first (fleetDamage_ is the rewrite's integrity analogue,
    campaign.h:341); death-at-integrity<1 already maps to the capture /
    Extinct verdict path — cite the mapping, do not invent a hull pool.
ORDERING RATIONALE for t89: (a)+(b) are one edit in one function; do them
together, rebuild, run run_tests (108), record_playthrough.sh, gate.sh.


## 2j. t89 LANDING: rewrite combatPhase UPGRADED to the cited law — OQ-010 CLOSED

CODE SITES (the contract's closing leg, the only thing t88a was missing):
* rewrite/src/game/campaign.cpp attackScore() — volley = SUM of researched
  cat-0 Levels (NumUses!=0 gate), replaces v1 MAX; cites 0x4a5c1 every-weapon
  law + design[+0x52]==Level (t87 map).
* rewrite/src/game/campaign.cpp defenseScore() — HULL layer only (pop/10 +
  fortify 2); the v1 "+best shield level" folded shields into one total,
  which 0x4b740 provably never does.
* rewrite/src/game/campaign.cpp combatPhase() — the uniform(0,10) noise draws
  are REMOVED (decision (b) of S2i, taken explicitly): the measured-negative
  hit roll (S2g, S2h-audited) forbids them. Capture law is now the cited
  two-layer split: volley=attackScore(a), absorb=MIN(volley,
  shieldChargesFor(b)) via Campaign::absorbSplit (campaign.h, mirrors
  0x4b7c4..0x4b7d1), capture iff (volley-absorb) > defenseScore(b,nb).
* rewrite/src/game/campaign.cpp shieldChargesFor() + setAllTechs();
  rewrite/src/game/campaign.h declarations + absorbSplit().
* rewrite/tests/test_campaign.cpp TEST(campaign_combat_law_oq010) — pins file
  sums (10 weapons SUM=49, 6 shields SUM=16 re-extracted), the full-vs-no-tech
  volley delta == 49 (a MAX model gives <49), absorb/clamp/spill edges, and
  seed-determinism across 40 FFA-war turns.

MEASURED CLOSING EVIDENCE (real execution, not plausibility): 109 tests
0 failed; seed re-verification after the rng_ re-diversion the S2i note
predicted — 2024 Control t777, 42 Extinct t581, 13 Extinct t503, test seeds
1/2 Control t842/t677 — ALL FINITE inside the 1200 gate budget; PLAYTHROUGH.md
regenerated by scripts/record_playthrough.sh (its echo-lines carried a stale
literal 600 for runs A/B/C while captures ran 1200 since T41 — fixed same
pass, display-only, no dynamics).

HONEST CAVEATS carried into the CLOSED row (the upgrade is an AGGREGATE
mapping, S2i): per-ship slot arrays, the same-system gate 0x4b982, the range
gate 0x4ba57, power/NumUses per-shot accounting, and the +0x9c flag bits have
NO rewrite data structure and are NOT modelled; they are law-of-the-model
inputs (empire volley/shield sums), documented here and in the code comments.
Per-ship combat, if ever modelled (OQ-019 territory), must re-use S2d..S2h
literally. The t85g live sequence 40>38>36>34 remains the behavioural
cross-check on the split law.

## 5. t261 driven-corpus witness(a) pass (OQ-016 clamp material) [measured, no qualifying event]

Drive t1086->1111 (25 turns, production :9), 88 deduped trusted-order points
(scripts/r261_harvest.py). mine_stream found 20 non-war change-hits
(Chamachies vs Orfa/Ungooma rel=1 streaks <=8; '?' owner-unknown rows) but
ZERO destruction events and ZERO strict engagement-scale hits (min dist2
39441 >> 3600 bound) — the streaks are AI ship-state churn (state-field
changes at range), NOT volleys. No multi-volley-vs-non-war witness landed this
session; OQ-016 STAYS OPEN (t251 cascade witness remains the only one). Raw
hits banked work/r1/t261_witness_a_hits.json for re-vetting.

## S2k (t275) — ENGAGEMENT RESOLVER 0x42c60..0x42e6e VERBATIM + CALLER-SIDE SHIP-ARRAY LAW (capstone 5.0.7 /home/hrethric/tools/revenv/bin/python, listing work/t275_resolver.txt)

Triage first: the t275 queue row names four sub-laws (deterministic damage,
ordered cat-0 volley, shield-then-hull absorb, death at <1) — ALL FOUR are
code-verified LANDED at t89 (S2j): attackScore SUM-volley campaign.cpp:1842,
absorbSplit campaign.h:383, rng_ draws removed campaign.cpp:1956..1966,
capture/Extinct death mapping S2i(c), pin campaign_combat_law_oq010. The row's
actionable remainder is the resolver region itself (t179 P3 banked only a
summary; this is the first verbatim read) + its caller-side filter.

ENCLOSING FUNCTION: 0x41e34 size 6087 (functions_full.tsv line '41e34 6087');
sole rel32 caller 0x41910 inside 0x41260 (the movement resolver; callers
0x16eb0 batmode, 0x2554f player-command-exec 0x2547c — the same function the
t88a commit law sits in). Entry regs: EAX -> [esp+0x2c4] (context obj;
[[eax+7]+2]>>16 = race idx), EDX -> ESI = OBJECTIVE OBJECT, EBX -> [esp+0x394]
(assert 0x840 msg 0x84c84), ECX -> [esp+0x354] = ship COUNT (u16);
[esp+0x380] = ship POINTER ARRAY; [esp+0x398] = result descriptor out-param.

CALLER-SIDE ARRAY BUILD (0x41260, loop 0x41318..0x413b3 over the 0x22304 list):
a ship enters the resolver's array iff ALL of:
  * [[ship+0x54]>>16] == engagement race byte ([edi]) — 0x41340/0x4134c;
    => THE ARRAY IS OWNER-RACE FILTERED: only the acting side's ships are
       visible to the resolver. The defender's ships are NOT in it. Return
       fire is therefore a SEPARATE engagement resolution run (own command-
       exec pass), corroborating S2g "no interleaving across ships here" and
       the t85g §1 observation that return fire lands as discrete small
       steps (player 40>38>36>34), not a simultaneous exchange.
  * DWORD [ship+0x88] > 0 (POWER — 0x4134e; same gate family as 0x4a55c);
  * BYTE [ship+0x58] != 1 (order kind 1 excluded — 0x41357).
Accumulators accumulate: word[esp+0x3a0] += [ship+0x88] (total POWER),
word[esp+0x3ac] += [ship+0x94] (total MOVES). A ship with BYTE [+0x5d] != 0
sets [esp+0x38c] := -1 (flag; consumer elsewhere). Second loop 0x413d5..0x41417
builds the PLANET array ([+0x46] family, count [+0x5a]) filtered on
[planet+0x57] == engagement race. Both-empty -> exit 0x419c0 (return 0).

REGION 0x42c60..0x42e6e (VERBATIM, confirms t179 P3 and adds legs):
* 0x42c60 head: race check (assert 0xbc0 msg 0x217c), out-param
  lea ebx,[esp+0x30c], CALL 0x3a174 (invasion resolution, t207 law) then
  0x396cc; -1 return path 0x42cd7 returns 0xffffffff (no engagement).
* LEG-SELECTION GATE 0x42cea..0x42cf3: CALL 0x39a00(ESI) — per-planet ACTIVE
  -item scan (slot array [+0x10], start word [+0x18], count word [+0x1a],
  4-byte slots, byte+1 == item id (0xff empty), word+2 bit0 == ACTIVE):
  returns -1 iff any ACTIVE slot holds item 0x17, 0x1a or 0x1b. Item map
  [verified income-law.md §6h t25: parsed file order == runtime itemIdx,
  0 Factory .. 23 Ship, 26 Orbital Shield, 27 Orbital Mega Shield; the four
  t201 bit8 shield rows {18,19,26,27} cross-validate the same numbering]:
  0x17=23=Ship, 0x1a=26=Orbital Shield, 0x1b=27=Orbital Mega Shield.
  => GATE LAW: objective planet with an ACTIVE Ship/Orbital-Shield/
     Orbital-Mega-Shield item SKIPS the invasion-carrier leg (jne 0x42dce
     jumps straight to the firepower leg); unshielded objective -> carrier
     leg runs first. [inferred gloss: the engine shoots at defended planets
     rather than waste the Invasion Module — the SKIP/SHOOT structure is
     verified, the intent is not.]
* LEG A (carrier pick) 0x42d09..0x42d5b: first array ship with BYTE [+0x58]
  == 4 AND any stride-7 gizmo slot byte == 0x49 (Invasion Module); stops at
  FIRST match (0x42d54 stores, loop continues only over the no-match tail —
  the t179 "stops at the FIRST match" holds per scan: [esp+0x2d0] != 0 test
  at 0x42d16 halts scanning once set). Descriptor: byte 3 + ship ptr
  (0x42da3/0x42da6); carrier engagement state written [ship+0x62]=0,
  [+0x63]=0, [+0x67]=1, [+0x68]=objective (0x42d9c..0x42dbd).
* 0x42d64 (no carrier found): if objective ownership bits [eax+0x15] AND
  (1<<DAT_0007458e) (local human player, t204 byte) -> RETURN 2; else fall
  through 0x437ee. [t364 POLARITY CORRECTION, _wip_t364.md C7: the verified
  order 0x42d7f..0x42d99 is TEST bits & (1<<local); JNE (IS local) -> 0x437ee
  (outside the banked region); the FALL-THROUGH (NOT local) returns 2 — the
  draft has the branches swapped.] Return-code census for this region:
  0xffffffff = no engagement / unresolved, 2 = "nothing picked" (not-local
  objective per the correction), descriptor kind 3 = engagement actor chosen.
* LEG B (firepower pick) 0x42de0..0x42e34: first array ship with [+0x58]==4
  where CALL 0x4a604 (companion slot scan: first cat-0 slot with power/uses,
  S2h) != 0 AND CALL 0x4a55c(ship, 1, objective) != 0. First match wins
  (0x42e2d + [esp+0x2d0] halt test 0x42ded). 0x4a55c SIDE EFFECT fires here
  (stance setter, S2g): [+0x62]:=1, [+0x67]:=1 (arg 1), [+0x68]:=objective —
  the resolver COMMITS the chosen shooter's firing order, not merely probes.
  No strength comparison, no value ranking, no retreat test anywhere in the
  region (eligibility = order-state + equipment) — t179 verdict re-confirmed.

HONEST NEGATIVES (measured, this pass):
(1) THE REGION NEVER READS +0x59: instruction census over the window touches
    +0x58/+0x5d/+0x62..+0x68/+0x88/+0x94/+0xab/+0x15a and gizmo 0x49 only.
    The queue row's "threat byte +0x59" citation is MISDIRECTED for this
    region: the planet threat byte is t201-closed and wired in buildPhase;
    ship +0x59 (t179 §7 stored order target) is NOT read here either — the
    resolver writes the target to +0x68.
(2) EVERY selection input in the region is per-ship (array membership, order
    kind, gizmo slots, power/moves) or per-planet (ACTIVE item scan) state.
    The rewrite's fleet_ vector {owner, from, target} (campaign.h:90-94)
    carries NONE of it; the aggregate volley/absorb law landed at t89 is the
    complete aggregate-mappable content of the four named sub-laws. Per-ship
    first-eligible wiring = OQ-019/row-16 boundary (accepted permanently
    t256c, S11) — NOT re-queueable as aggregate code.
(3) The PLANET-level laws in/around the region that the rewrite COULD in
    principle see are the leg-selection gate above and the t207-banked
    invasion defense term (0x3a2c9..0x3a325: shieldscore = #{ACTIVE item 18
    Surface Shield} + 2*#{ACTIVE item 19 Surface Mega Shield}; result =
    invmod>shieldscore ? shields+1 : invmod, then up to `result` ACTIVE 19
    slots stripped). DECISION t275: NOT wired. The gate has no rewrite call
    site (the rewrite conflates gunnery+invasion into ONE aggregate
    engagement — t207 S7e documented divergence), and both defense-term
    operands that make it a LAW (invmod = per-ship Invasion-Module count;
    per-slot strip) are per-ship state = OQ-019 boundary (row 16/17
    aggregate accepted permanently t256c). Wiring either would ADD behaviour
    the corpus never witnessed (zero invasion-vs-shield events in 20/20
    saves, t207 corpus witness) with no closable ledger row — churn, not
    progress. The honest delta of this iteration is the verbatim law itself.


## S3l (t364, 2026-11-10) — PER-SHIP COMBAT ROUND LANDED into shipsim
Laws C1..C9 (verbatim windows, both disassemblers) banked at
docs/re/_wip_t364.md; code rewrite/src/game/shipsim.cpp t364 block
(setStance/volleyTail/companionScan/gunEngageFlag/commitShot/engageRound);
pins tests/test_shipsim_t364.cpp x12, run_tests 218/0; MUTATION 6/6 CAUGHT
(M1 stance map — needed a pin re-scope: stance-order sensitivity made the
first version vacuous; M2 volley store-on-hit; M3 mode-gated apply; M4
charge-even-zero-damage; M5 mode-0 DEC; M6 Leg A exclusivity). Zero-witness
legs modelled verbatim and flagged: range-0 unlimited (C9), handler-1/2
returns (C8 named substitution arg3), 0x437ee unmodelled (C7). No OQ row
closes (user-gated per t364 contract); the aggregate engine (campaign.cpp
combatPhase, OQ-010 CLOSED law) stays the oracle until the t365 flip.
