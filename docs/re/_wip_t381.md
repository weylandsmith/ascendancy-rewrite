# t381 WIP — GIZMO-USE DECREMENT + INVASION CONSUMPTION (FINDINGS->CODE)

Queue row t381. Witness base: docs/re/ships.md S64 M2 (+ the raw word-event
stream work/r1/t370_slot_events_all.txt this session re-read IN FULL — it is
29 lines). No capture; static + banked witnesses only.

## S0 WITNESS RE-READ (raw stream, this session, verbatim details)
The raw event lines carry MORE than the S64 M2 summary banked:

1. s14 Stainer 00:24:08: `power 90->84 | ring {... 13: (9,3,0) ...}` ->
   `{... 13: (9,2,0) ...}` — SAME FRAME: slot-13 cidx 9 use 3->2 AND power
   -6. cidx 9 = Nanomanipulator gizmos.txt:116 row `0 6 50 13 3 100 0 0 56`
   = Cat 0, Power 6, Range 50, Level 13, NumUses 3. NOTE cat 0 (Weapon), not
   a special: the use went through the GUN-handler-shaped path (orderType 0)
   or at least charged design[+0x36]=6 exactly.
2. s34 Gofriller 00:26:59: type 2->1 frame @00:26:48, then 00:26:59
   power 90->84 + slot13 cidx9 use 3->2; 00:27:51 power 84->78 + slot13
   use 2->1 (a THIRD copy slot16/19/22 (9,3,0) untouched — the DEC hit the
   ACTIVE/first-matching slot only).
3. s28 Guandagnini 00:13:50 (M1 magnetron): ring slot14 (60,1,0) REMOVED
   same frame (single-use consumption = clearSlot, S64 M1).
4. s22 Ignatz 00:28:48: ring slots 2 AND 3 (73,0,0),(73,0,0) REMOVED in one
   frame, nothing else on the ship changed that frame (power no change; the
   invasion ORDER was the 00:28:22 frame: kind 4->3 orbit Vernunft, type 2->1,
   power 8->3 = -5). cidx 73 = Invasion Module (pership-spec C1: NumUses-col
   0!). CONSUMPTION = clearSlot x2, NOT a use-word DEC — consistent with
   numUses==0 (dispatcher never DEC-rows numUses==0; the vendor REMOVED the
   slot at invasion launch instead).
5. UNBANKED SIDE-WITNESSES (00:24:08, AI ships own1/own2): s11 (own2)
   power 9->5, charges 20->7, ring slot9 (11,0,0)->(11,0,0xFFFFFFFF);
   s12 (own2) power 9->1, slots 8,9 (13,0,0)->(13,0,0xFFFFFFFF);
   s23 (own2) power 10->6, slot8 (11,0,0)->(11,0,0xFFFFFFFF);
   s2 (own2) type 2->0, power 7->2, slot4 (0,1,0)->(0,0,0) + slots 8,9
   (10,0,0)->(10,0,0xFFFFFFFF). Payload -1 stamping on cat-3/other rows —
   the payload-0xFFFFFFFF law (_wip_t363 S4/S5: 80 slots ALL on upkeep-gate
   rows) — here appearing at a mid-turn frame, not a turn tail. Flagged
   observation; NOT consumed by t381 pins (upkeep-gate rows are cat-1 per
   t363; these rows are cat 3/5 — carry as an honest note).

## S1a CORRECTION TO THE S64 M2 SUMMARY (raw-stream re-read, this session)
The queue row and S64 M2 say "LOST 2x Invasion Module AT INVASION LAUNCH" and
the M1 magnetron analogy suggests all-single-use-consumption. RAW TRUTH:
Ignatz's ring BEFORE the 00:28:48 frame held SIX cidx-73 slots (2,3,4,5,5,7 —
slots 2..7 all (73,0,0)); AFTER it holds FOUR (4,5,6,7). EXACTLY TWO slots
were cleared (indices 2 and 3 = the FIRST TWO in walk order), the other four
SURVIVE. Consumption at invasion launch is therefore COUNT-LIMITED, not
all-or-nothing and not single-use. The t370 tool prints rings as maps, which
is what hid the multiplicity behind "x2" in the summary.

## S1 STATIC: THE INVASION-LAUNCH CONSUMPTION SITE — FUN_0003a174 (VERIFIED)
work/r331_disasm.txt lines 45148..45400 (0x3a174..0x3a45c). FUN_0003a174 =
the invasion/capture resolver (ai-dossier row 13, diplomacy.md §19; callers
EXACTLY {0x3d951, 0x42c8e} — re-confirmed this session: grep 'call 0x3a174'
-> 2 hits only). ABI eax=planet, edx=orbital slot index, ebx=ecx out-param.
Structure (verified instruction-level):
  prologue 0x3a174..0x3a1c5: assert slot < [planet+0x1a]; assert ring-slot
    byte1 == 0x17 (landed-ship item type — pership-spec C3); FUN_000396cc ->
    ebp = transport ship ptr; assert transport owner ([ship+0x54]>>16) ==
    planet owner ([planet+0x57]) unless owner==0xff.
  GUARANTEE-WAR clamp 0x3a25a..0x3a291 (t207 law, already modelled in
    diplomacy.cpp guaranteeWarOnInvasion).
  LOOP1 COUNT 0x3a2a2..0x3a2c5: walk transport invCap ([ship+0x15a]) slots
    stride 7, count BYTE[+0xab]==0x49 -> [esp+0x10] = MODULE COUNT (ALL six
    for Ignatz).
  LOOP2 DEFENDER-DEFICIT 0x3a2f1..0x3a327: walk planet item array
    ([planet+0x10], u16 [planet+0x18] entries, stride 4): byte1==0x12 AND
    word2 active -> +1; byte1==0x13 AND active -> +2 -> [esp+0x4] = DEFICIT
    (defender units: item 0x12 = 1 unit, 0x13 = 2 units).
  CAP 0x3a327..0x3a33e (re-read verbatim, CORRECTION of my first trace):
    need := count; if (count > deficit) need := deficit + 1  — i.e.
    need = min(count, deficit+1). Ignatz: count 6, consumed 2 -> deficit+1=2
    -> the objective had ONE active shield item (item 18 Surface Shield,
    +1 unit; item 19 Surface Mega Shield counts +2 — ids per
    income-law.md:565-566, NOT my planitem.txt re-count which misaligns).
  RACE OVERRIDE 0x3a342..0x3a356: ebx := [esp] set at 0x3a208/0x3a215 from
    `cmp BYTE [0x12fb3 + owner*494], 0` — table byte ZERO -> ebx -1 -> need
    := 1. FILE BYTES MEASURED this session (ascend_restored.bin): owners
    0..6 = {6,157,226,1,39,24,7} all NONZERO; owner 7 = 0. The override is
    the neutral/owner-7 leg — sim divergence: NOT modelled (no neutral
    transport witness; flagged, do not invent semantics).
  LOOP3 CONSUME 0x3a360..0x3a38b: walk transport slots AGAIN i < invCap,
    `cmp BYTE[slot+0xab],0x49` -> `call 0x496e4` (clearSlot) while
    consumed < need — FIRST-MATCH WALK-ORDER CONSUMPTION, STOPPING at need.
    *** THIS IS THE t381 SITE. It explains the witness EXACTLY: need=2
    (one active Surface Shield + 1) -> slots 2,3 cleared, 4..7 survive. ***
  post 0x3a38d call 0x49acc (recalc ONCE after the loop — the sim's
    per-clearSlot recalc lands the same zero-then-sum totals); 0x3a394..0x3a3f5 planet item-0x12
    ACTIVATOR legs call 0x38840 (per-slot activator, ecx=1, ebx=0xff);
    0x3a3f7..0x3a45c item-0x13 legs (add edi,2 / jg guard = the +2 units).
CONSUME GATE (mode): the resolver's caller edge 0x42c8e sits in the per-ship
command-exec region (ai-dossier t210: mode-1 multipliers incl. 0x25560/
0x25570 family; 0x42c8e region = the engagement resolver Leg-A tail — see
combat.md:653 "lea ebx,[esp+0x30c], CALL 0x3a174 (invasion resolution, t207
law)"). No mode arg INSIDE 0x3a174 (the consumption runs unconditionally once
the resolver runs; the mode gate lives at the CALLER). Flag: the caller's own
mode gating is t364-banked region, NOT re-derived here.

## S1c STATIC DETAIL PACK (constants + gate mask, all VERIFIED this session)
- ds:0x85312 = f32 2.0 and ds:0x85316 = f64 0.75 MEASURED from
  work/ascend_restored.bin (struct.unpack at those offsets) — the handler-1
  status-bit0x4 range DOUBLER is the same constant as the gun's (now
  [verified]). FP scratch law (0x4c8b7..0x4c8f0): [esp+0x38] := dist
  (0x76da0 return), [esp+0x3c] := f32(design[+0x3a]<<5), DOUBLED when
  [ship+0x9c]&4. The cidx-0x2f leg 0x4c908..0x4c919 is VACUOUS: it computes
  dist*0.75 and fcompp-compares it against dist itself (never pushes a new
  operand against the limit) — jbe always taken for dist>=0, edi never
  cleared there. NOT modelled as a gate (honest: dead leg).
- HANDLER-1 COMMIT GATE 0x4c91d..0x4c942 (exact): eax := 1 iff
  affordable([esp+0x30]) AND in-range(edi) AND (design[+0x33] & 0xc) — the
  0xc mask is TARGETORBIT(bit2)|TARGETSURFACE(bit3) per the gizmos.txt vendor
  flag table (extracted/ascend00/gizmos.txt lines 74-75). FIRST cited
  consumer of that mask as a COMMIT GATE (t377 established TARGETLANE bit1 is
  a return-flag in the magnetron path; the 0xc gate is a different leg).
  Nanomanipulator flag_list `0 1 2 3 255` -> mask 0xF -> gate admits it.
- COMMIT TAIL 0x4c947: `cmp [esp+0x2c],0x1; jne 0x4ca43` — charge + effect
  are MODE==1-gated; gate-fail exits WITHOUT charge (the DEC already ran
  dispatcher-side — magnetron-C7 shape holds: DEC paid, charge not).
- 0x4c966 cat-switch: cat!=0 returns after the charge (charge is NOT cat-
  gated; only the 0x39f00 effect call is).
- RANGE POLARITY (0x4c8f4..0x4c901): limit := f32(design[+0x3a]<<5), doubled
  if [ship+0x9c]&4; dist > limit -> edi := 0 (TOO-CLOSE-OK, too-far fails) —
  same polarity as the magnetron C1 correction, NOT the t185 inversion.
- Handler-1 reads the TARGET TRIPLE by derefing [+0x68] (0x4c802..0x4c80f:
  [t+0x0/+0x4/+0x8] -> ship [+0x78..0x80] scratch). The sim's surrogate is
  Ship::targetPos (the same field the type-1 chase law uses); null-target
  divergence = the assert-call 0x2a428 site — sim refuses with zero state
  change (named divergence, same shape as commitShot's 0xad stand-in).

## S1b STATIC: HANDLER-1 0x4c794 CHARGE LAW (VERIFIED — the M2 path)
Dispatcher 0x4a360 (full window re-read this session, lines 64672..64733):
prologue NumUses law + mode-1 DEC BEFORE the handler (0x4a373..0x4a397,
verbatim as shipsim models it), then KEY [+0x67]: 0->0x4b8e4 gun,
2->0x4ca50, 1->0x4c794, 5->0x4cd90. The M2 witnesses ran with type 1
(Gofriller's 00:26:48 frame set type 2->1 the frame BEFORE the decrement;
Stainer's active-slot DEC + power -6 at 00:24:08) = HANDLER-1.
Handler-1 0x4c794..0x4c990 structure (fresh read, lines 67215..67390):
  0x4c7a4..0x4c7c2: esi := design row (stride 0x6a) of ACTIVE slot [+0x63].
  0x4c7c9: ebp := power [+0x88]; 0x4c7cf..0x4c7e2: cost := MIN(design[+0x36],
    power); affordable flag [esp+0x30] := (design[+0x36] <= power) ? 1 : 0.
  0x4c7ea..0x4c7ef: [+0x68] target null -> assert call 0x2a428.
  0x4c802..0x4c82e: target triple -> ship [+0x78..0x80] scratch.
  RANGE GATE 0x4c831: `cmp DWORD[esi+0x3a],0x0; je 0x4c91d` — Range==0 SKIPS
    the distance math (unlimited, same shape as the gun C9 leg); else
    dist(target, [ship+0x9e triple]) via 0x76da0, compared to design range
    (0x4c8e4 je-leg; the in-range/fail polarity banked below).
  0x4c903: cmp cl,0x2f / jne 0x4c91d — the cidx-0x2f Carbonizer leg.
  COMMIT GATE 0x4c91d..0x4c952: [esp+0x30]==0 (NOT affordable) -> result-flag
    leg; then `test BYTE[esp+0x40],0x1; je 0x4ca43` (bit0 = affordable AND
    rangeOK — magnetron-C2 shape) and `cmp [esp+0x2c],0x1; jne 0x4ca43` —
    MODE==1 GATE on the commit tail.
  CHARGE 0x4c958..0x4c960: `sub DWORD[edx+0x88], eax` with eax := cost ->
    POWER -= MIN(design power, power). *** The M2 -6 EXACT: Nanomanipulator
    gizmos.txt:116 row `0 6 50 13 3 100 0 0 56` = Cat 0, Power 6, Range 50,
    NumUses 3 — matches slot use 3->2 DEC (dispatcher) AND power -6
    (handler-1 charge) in the SAME frame, twice (Gofriller), exactly. ***
  0x4c966: `cmp BYTE[esi+0x32],0x0; jne 0x4ca3a` — cat!=0 -> return WITHOUT
    the effect call; cat==0 -> call 0x39f00 (the effect; ai-dossier row 13:
    honest NO-DELTA bombard-shaped effect — NOT modelled, named no-op).
NOTE the DEC/charge split: DEC is dispatcher-side (every handler, mode-1,
numUses!=0); the CHARGE is per-handler (gun tail 0x4c614, handler-1 0x4c958).
The sim's commitShot currently returns EARLY for orderType!=0 with NO charge
(shipsim.cpp ~line 585 "Named no-op legs — and NO charge") — that reading is
SUPERSEDED for handler 1 by this window: handler-1 DOES charge (witnessed
-6 twice). Handler 2 charge: the magnetron leg charges at 0x4cbe3 (t377
banked, modelled in useMagnetron); handlers 5: unbanked, stays no-charge.

## S2 STATIC: INVASION-LAUNCH SLOT CONSUMPTION SITE
(PENDING)

## S3 CODE CONTRACT
(PENDING)
