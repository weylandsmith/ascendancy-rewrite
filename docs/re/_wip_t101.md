# t101 WIP — +0x88 vs +0x94 SHIP-FIELD RE-ATTRIBUTION PASS (LANDED)

VERDICT (all legs green, tool scripts/r1_t101_field_verify.py RC=0):
  +0x88 = POWER   (gizmo power budget; panel-confirmed, ability-confirmed)
  +0x94 = MOVES   (per-turn movement budget = drive stat [ship+0x10];
                   panel-confirmed, travel-consumption-confirmed)
  +0x8c = INTEGRITY, +0x98 = MAX INTEGRITY (t85g/t86 STAND)
  +0x90 = SHIELD CHARGES (t86/t85g STAND; the t47 "propulsion accumulator"
          label is a base-convention artifact of the same bytes — see F5)
  +0x18 = POWER CAPACITY (feeds the recharge multiplier)
  +0x52 = ship BIRTH DAY (recharge base = (T - [+0x52])/100 clamped 0..10)

## 0. The conflict being adjudicated (three banked positions)

| iteration | +0x88 | +0x90 | +0x94 | source |
|---|---|---|---|---|
| t47 §12 / t48 §13 (ships.md) | fuel/maintenance pool (capacity +0x18) | speed accumulator | design-list pointer | ships.md:312-323 |
| t85g S1 (combat.md) | MOVES | shield charges | (not read) | combat.md:36 |
| t86 S2d (combat.md) | gizmo-POWER sum | shield charges | (not read) | combat.md:121-132 |
| t96 panel law | fmt-arg 1 of POWER/MOVES/INTEGRITY | — | fmt-arg 2 | aicode.md:531 |
| t99 §6.3 NOTE | POWER (doubled/zapped by abilities) | — | MOVES candidate | aicode.md:952-956 |

## 1. Static findings (raw objdump over work/ascend_restored.bin, base-0)

F1 [verified 0x43be0..0x43cc3] BODY BOUNDARIES ADJUDICATED — t90 §2e is
   REFUTED as to BOTH "race maintenance leg" claims:
   * 0x43c3f..0x43c77 is a self-contained case body: call 0x40ec0 (ship
     list) -> jle exit 0x4400a -> loop 0x43c5b: `mov esi,[edx+0x88];
     add esi,esi; mov [edx+0x88],esi` (<<=1) over the pointer array.
     0x43c3d is `jmp 0x43bf9` (profile-6 loop) — NO fallthrough; 0x43c3f
     is reachable ONLY via the edx==1 jump table.
   * The "attitude floor 0x43c0a" loop is the profile-6 SA_ForcePeace body
     0x43bf0..0x43c3d (matches t99 §6.3 verbatim). Also NOT a per-turn leg.
   * 0x43bd0..0x43bee `mov [edx+0x8c],ebx(=[edx+0x98])` = profile-5
     SA_HealShips body — integrity heal, also ability-gated, not a leg.
   CONSEQUENCE: t90's "the t85g boundary recharge is THESE TWO sites"
   COLLAPSES (no shipped race in the live campaign has profile 7; live rows
   0..3 = 19/2/11/0). The per-turn producer is FUN_0004a74c (F4/F7).

F2 [verified 0x1da83..0x1daaf, bytes pinned by the verify tool] PANEL LAW
   SETTLES THE TRIPLE — kind4/5 display arm pushes cdecl args R-to-L:
     mov ecx,[eax+0x8c]; push ecx    -> 3rd arg INTEGRITY
     mov esi,[eax+0x94]; push esi    -> 2nd arg MOVES
     mov edi,[eax+0x88]; push edi    -> 1st arg POWER
     push 0x831c9                    -> 'POWER %d MOVES %d INTEGRITY %d'
       (pool string re-dumped byte-exact; the ONLY 'MOVES' string image-wide)
   => +0x88 = POWER, +0x94 = MOVES, +0x8c = INTEGRITY per the vendor UI
   itself. t99 NOTE CONFIRMED; t85g '+0x88=MOVES' label REFUTED (raw
   observations stand — battle volley steps and boundary recharge hit +0x88,
   but the vendor calls that field POWER); t47 '+0x94 = design-list ptr'
   REFUTED for ship records (integer display + integer consumers).

F3 [verified 0x43b50..0x43bae + FILE 0x43b10] t99 cadence-engine decode
   re-confirmed end-to-end: cad gate WORD[0x6780+2*ability] vs [row+0x19e],
   jg -> 0x44017 counter-store exit; edx==1 -> 0x441c1 `jmp cs:[eax*4+
   0x2ef60]` on (row+0x19d)-5; 16/16 table entries re-resolve to t99's body
   addresses exactly (pins 7=0x43c3f, 9=0x43d33 in the verify tool).
   NOTE the gate polarity: 0x4400a stores [esp+0x6c8]; the fire path stores
   (counter-cad) at 0x44003 first — both consistent with t100's one-reset
   model since counter==cad exactly at fire.

F4 [verified raw FUN_0004a658 0x4a658..0x4a74a, FUN_0004a74c 0x4a74c..
   0x4a968] THE TWO PER-SHIP RE-INIT FUNCTIONS (raw disasm; t47's Ghidra
   offsets shifted by the +0x30 record-start convention — VALUES stand):
   FUN_0004a658 (EAX=ship) MOVES leg:
     if WORD[+0x9c] bit0: [ship+0x94] := 0
     elif bit1:           [ship+0x94] := ds:0x77f6c + [ship+0x10]
     else:                [ship+0x94] := [ship+0x10]
     [ship+0x90] := 0 ALWAYS; then per gizmo slot (stride 7 @+0xab, count
     [+0x15a], design row = type*0x6a + 0x7650c, slot dword+3 == -1,
     design[+0x33]&0x20): IF [ship+0x88] >= design[+0x36] -> [ship+0x88] -=
     design[+0x36] (POWER UPKEEP); AND IF BYTE design[+0x32]==1 ->
     [ship+0x90] += design[+0x56] (shield charges — cat byte at [row+0x32]
     ==1 rows ARE the shield family per t86 S2d; t47 called the same sum
     'propulsion' because their base sat 0x30 lower: their row+0x26 ==
     design+0x56, their row+6 == design+0x36 — SAME BYTES, mislabelled
     semantics, no numeric contradiction).
     Finally WORD[+0x9c] bit3 -> [ship+0x90] := 0.
   FUN_0004a74c (EAX=ship) POWER leg + travel tail:
     WORD[+0x9c] := 0; [ship+0x88] := call 0x4a99c (F7); tail 0x4a7a6..:
     for order kind==5 re-places/advances at target ([+0x9e] f32 walk with
     0.333/2.0 float constants, relation[+0x12fb3]==12 gate); exit ALWAYS
     calls 0x4a658 at 0x4a95b. CALLERS (rel32 census): 0x4a74c <- {0x3e7b0
     (inside FUN_0003e6e0 per-turn ship loop), 0x49d0d}; 0x4a658 <- {0x3ea40
     region, 0x4a95b}. => BOTH re-inits run per-turn-per-ship.

F5 [verified 0x4a2d4..0x4a314, commit-gated `cmp edi,0x1` == S2h mode law]
   TRAVEL CONSUMES BOTH BUDGETS: after the step walk (call 0x533e0 rewrites
   xyz @+0x78): fild [ship+0x94]; fsub travel-float; fistp [ship+0x94]
   (MOVES -= distance); AND [ship+0x88] -= int arg (POWER burn per order).
   0x41df4/0x41dfb/0x41e07 (order-complete leg): MOVES := 0 and POWER
   drained to 0 with the delta folded into a build-queue word — the last
   day of a long move lands the whole remainder.
   Live float constants (item-table-anchored 60.sav): 0x263b=0.333333,
   0x263f=2.0, 0x2647=2.0, 0x851f3=0.1 [verified live].

F6 [census obj0 full, /tmp/t101_obj0.asm] +0x94 SITE LIST: 31 raw hits;
   ship-record sites = {178fb cmp 0; 1da91 panel; 41dfb store 0;
   4a0a6/4a2f0/4a314 travel fild/fistp; 4a671/4a6a0 re-init; 4b068/4b39d
   walk shadow; 4b691 record copy; 4c5ee store 0; 4dbf8/4e1f9 reads};
   [esi+eax*4+0x94] (6bdcd/6c34e) unrelated array. All reads integer.
   +0x88 writers: re-init 0x4a76c, upkeep 0x4a710, travel 0x4a307,
   0x41d80 dec / 0x41e07 zero (order leg), ability bodies 0x43c69/0x43dcd,
   gizmo-activation costs 0x49ebe/0x49f06 + design grants 0x4932c/0x4999f,
   Hyperfuel +40 0x4d1a9, Cannibalizer +20 0x4d1e7 (combat.md S2f STAND).

F7 [verified 0x4a96c raw + 0x4a99c raw] RECHARGE LAW CLOSED:
   0x4a96c(ship) = b = clamp((ds:0x12e10 - [ship+0x52]) / 100, 0, 10) (idiv
   100; negative -> 0 via `test eax,eax/js 0`; cap 10).
   0x4a99c RAW (operand order verified instruction-by-instruction):
   mult = clamp(b*0.1f + 1.0, 1.0, 2.0) (fmul applies to the BASE returned
   by 0x4a96c; the two fcomp clamps are defensive since b is pre-clamped);
   result = trunc(cap * mult) (fild [ship+0x18], fmul mult, 0x76e08, fistp
   — truncation proven live: Orfa slot1 cap 4 b 9 -> 4x1.9=7.6 stored 7).
   CLOSED FORM: POWER_init = trunc([ship+0x18] * (1 + clamp((T-[+0x52])//
   100, 0, 10)/10)), i.e. +10% per 100 days held, max x2 — a mature ship
   refuels to full POWER capacity each turn. CALLERS (rel32 census):
   0x4a74c <- {0x3e7b0 (FUN_0003e6e0 per-turn ship loop), 0x49d0d (build
   completion, caller 0x391ba)}; 0x4a658 <- {0x3ea40 (in FUN_0003ea08,
   UI/redesign side), 0x4a95b (tail of 0x4a74c — always runs)}.

F8b [live, 60.sav] THE FIVE ZERO-POWER ROWS [unverified mechanism]: all
   owner=2 (Ungooma, at war), [rec+0x52] 1257..1264 AHEAD of T=1254
   (negative age -> b=0 -> law gives init=cap=12, NOT 0 — so re-init alone
   does not explain the zeros). Candidates: post-re-init drains in the
   AI command-exec tail (0x2554f FUN_00041260 region; the 0x41d80 `dec
   [+0x88]` / 0x41e07 `mov [+0x88],0` sites sit in an unattributed jump
   region reached via jmp 0x41b8f) or a build-side init ordering. NOT
   SapAlienPower: no shipped race in this campaign carries ability 9
   (rows = 19/2/11/elim). Residue explicitly open; verify tool asserts
   only the bounded 0 <= POWER <= init.

## 2. Live findings (playcap/save/60.sav, B anchored at item-table
## b"\x1e\x00Factory" == B+0x82bb0+0x73e40+8; T = u32 X 0x12e10 = 1254)

F8 [verified 35 active ship rows] LAW CHECKS (r1_t101_field_verify.py):
   * +0x8c == +0x98 on 35/35 (boundary integrity law, t85g STAND);
   * +0x94 == +0x10 (drive) on 32/35 — the 3 exceptions (MOV 2<4, 10<12)
     are same-day travel/bump partials, consistent with F5;
   * +0x88 <= recharge-init on 35/35; exact init on 25/35; the ten
     below-init rows decompose into per-turn burns (upkeep/travel), e.g.
     slot3 init 56 obs 52 == one type-15 gizmo upkeep 3 plus travel 1;
   * the five ZERO-power rows are all owner=2 (Ungooma, at war) with
     [+0x52] > T (birth stamps days AHEAD of the clock — AI war-fleet
     spawns), i.e. base 0 ships: recharge base clamp(0)=0 -> POWER 0.
     SapAlienPower alternative stays open; base-0 arithmetic explains it.
   Ring slots 56-60 byte-identical (held turns, no new sitting): the
   t85g sitting remains the only move-differential evidence; no new
   boundary frame contradicts it and none re-tests it this iteration.

F9 [adjudication summary for downstream consumers]
   The event-24 CONSUMER decode (next candidate task) must read ship
   POWER at +0x88, MOVES at +0x94, INTEGRITY at +0x8c/+0x98. Ability 7/9
   are POWER effects (DoublePower/SapAlienPower) on +0x88 — help.txt text
   and asm agree; there is NO MOVES-targeting ability in the 16 bodies.
   Rewrite: no code delta — the rewrite models neither per-ship power nor
   moves (OQ-019 territory); fleetDamage_/aggregate law unaffected (S2j
   caveats already say per-ship = OQ-019). OQ-016/OQ-019 get annotations.

## 3. Corrections to make in permanent docs
   combat.md S1 header + S2d: +0x88 label -> POWER (observation text kept);
   S2f case table unaffected. aicode.md §2e: REFUTED marker on the
   'per-ship moves doubling leg' + 'integrity restore leg' claims; §6.4
   NOTE -> adjudicated. ships.md §12/§13: base-convention note (+0x30),
   +0x94 pointer claim retracted, fuel-label -> POWER upkeep, and the t47
   'CONSUMER STILL OPEN' is CLOSED by F5 (travel consumes +0x94 AND +0x88).
