# _wip_t364 — PER-SHIP COMBAT ROUND raw evidence (2026-11-10)

Disassembler: /home/hrethric/tools/revenv/bin/python + capstone over
work/ascend_restored.bin (imagebase 0; file offset == image addr; cross-checked
against objdump -b binary -M intel on the two disputed windows — BOTH backends
agree byte-for-byte). Windows banked in this file; listings also at
/tmp/t364_hitpath.txt /tmp/t364_volley.txt /tmp/t364_gates.txt (session-local —
the verbatim law is BELOW, that is what matters).

## S1 CORRECTIONS to banked combat.md (load-bearing, both backends verified)

C1 DISPATCHER KEY (0x4a399..0x4a3c4): combat.md S2h says "dispatch BYTE
   design[+0x32] (category) 0->0x4b8e4, 2->0x4ca50, 1->0x4c794, 5->0x4cd90".
   WRONG KEY. The instruction is `8a 48 67  mov cl,[eax+0x67]` with eax = SHIP
   (eax untouched since entry 0x4a365). The handler is selected by the SHIP's
   action byte +0x67, NOT the gizmo category column:
     +0x67 == 0 -> 0x4b8e4 (gun handler)
     +0x67 == 1 -> 0x4c794  (shield-family body; rel32 scan of [0x4c794,0x4ca50)
                             finds NO call to hit path 0x4b740 — calls only
                             0x2a428, 0x38840, 0x39f00, 0x496e4, 0x76da0)
     +0x67 == 2 -> 0x4ca50  (drive/lane body)
     +0x67 == 5 -> 0x4cd90  (special tree, t87 table stands)
   The CATEGORY gate still exists — it is INSIDE the volley loop (0x4a5e1
   `cmp byte [design+0x3e650700]... ==0` i.e. design[+0x32]==0, cat-0 slots
   only). Net: volley = walk cat-0 slots, run the handler +0x67 selects.
   Handler-vs-category conflation: +0x67 values mirror category ids (0 gun,
   1 shield, 2 drive, 5 special) — the stance setter WRITES the handler id.

C2 STANCE MAP (0x4a597..0x4a5ae): banked map "arg0->2, arg1->1, arg2->0" is
   WRONG at arg2/arg3. Verbatim: cmp dx,1 / jb ->(dx==0) -> +0x67=2;
   cmp dx,2 / jbe 0x4a579 captures {1,2} -> +0x67=1; cmp dx,3 / je -> +0x67=0;
   else assert (0x3e5, msg 0x2623). MAP: 0->2, 1->1, 2->1, 3->0.
   Caller census (this session, window disasm): 0x41b4e edx=0 (->2, drive);
   0x421d0 edx=3 (->0, GUN); 0x43153 edx=3 (->0, GUN); 0x42351/0x43301 edx=ebp
   (variable, AI paths); 0x42e24 (resolver Leg B) edx=1 (->1).
   Also verified: 0x4a55c sets [+0x62]:=1 at 0x4a591 (mov, verified) BEFORE
   the arg switch; power==0 -> return 0 with NO state change (0x4a561..0x4a56f
   ret path precedes every store).

C3 APPLY IS MODE-GATED (hit path 0x4b740): 0x4b7f1 `cmp [esp+8],1 /
   jne 0x4b8d8` — mode!=1 EXITS BEFORE the star-record leg, the 0x43a4c
   diplomacy call, the APPLY (0x4b87a..0x4b890) AND the death call. A mode-0
   probe computes the clamp chain and sets flag bits 2/4 on the HYPOTHETICAL
   values but applies NOTHING. Damage in the world exists only through the
   two mode-1 edges (0x25560/0x25570, t88a census) — t85g's hull steps
   40>38>36>34 are mode-1 commits, one shot each (see C5).

C4 DEATH FINALIZER (0x49d2c -> 0x249b4): 0x249b4 law (verified disasm
   0x249b4..0x24a30): +0x56 owner := 0xffff; +0x58 kind := 0; +0x34 := 0;
   DEC word [ds:0x3067b] (live-ship count); check ds:0x30679>>16 >= 0.
   CORROBORATES dead-slot laws A3 (owner 0xffff) / A4 (kind 0) with the count
   decrement. Intermediate legs in 0x49d2c (kind switch @0x49d5f jump table
   0x35168 — table contents are relocation-time, unreadable statically):
   kind==1 path releases the transport slot on the target
   ([tgt+0x10 + ax*4]+1 := 0xff, [tgt+0x52] := 0xffff) then kind:=4 +
   [ship+0x59] := star-block index (edx*39*32 + 0x13bc5, K8 law re-confirmed)
   + travel re-issue 0x220a8; kinds 2..5 path calls 0x39894(targetability,
   NON-GOAL N4) + asserts kind==4 + travel re-issue. All moot after the
   finalizer zeroes kind/owner — the sim models DESTROY = owner -1, kind 0.

C5 ONE COMMITTED SHOT PER RESOLUTION (volley + dispatcher composition):
   the volley loop (0x4a5c1) calls 0x49f28 with EDX=0 (verified 0x4a5ec
   `xor edx,edx`) — the volley is ALWAYS a mode-0 probe. It leaves
   [+0x63] := the LAST cat-0 slot scanned (0x4a5ee stores per slot, before
   the call, whatever the per-slot result). The mode-1 commit edges re-enter
   0x49f28(ship,1) on the ACTIVE slot (+0x63) only. => per-ship damage rate
   = one gun's design[+0x52] per resolution run — matches t85g discrete
   2/step steps. The volley's return value = last successful slot ptr (edi,
   remembered on result bit0), 0 when none succeeded (Leg B's !=0 test).

## S2 VERBATIM LAW WINDOWS (this session)

Dispatcher 0x4a360 entry/ammo law: edi = cidx*0x6a; ebp = design[+0x42]
  NumUses (0x4a373 [edi+0x7654e]); esi := -1; if NumUses != 0: read slot use
  WORD [+1]; use==0 -> esi := 0 (OUT OF AMMO); mode==1 -> DEC use (0x4a390);
  esi != -1 -> SKIP handler, return 0. => slot eligible iff
  numUses==0 (unlimited) OR use>0.
Companion scan 0x4a604 (returns -1 eligible / 0 none): first i < [ship+0x15a]
  with design cat==0 AND (design[+0x42]==0 OR slot(i) use WORD != 0).
  Quirk verified: reads cidx via dword [ship+0xa8+i*7] sar 0x18 (byte-overlap
  of slot(i-1) payload — equals slot(i)[0]) and use via [ship+0xaa+i*7]
  sar 0x10 — equivalent to the direct slot reads; the sim reads slots direct.
Gun handler 0x4b8e4 gates (fresh full read 0x4b8e4..0x4bb7a): prologue
  mode->[esp+0x4d0], flags acc [esp+0x4e0]:=0, active cidx [esp+0x504],
  MIN(design[+0x36], power) -> [esp+0x4d4] (0x4b951..0x4b961); target :=
  [+0x68] (null assert 0xad); SAME-SYSTEM 0x4b982..0x4b99d verbatim
  (kind==4 both + [+0x59] equal); design[+0x3a]==0 -> skip-to-0x4bad4 (range
  0 never fires: 0x4b9a3 je); distance = sqrt(f64) of +0x9e delta triple
  (0x76da0); limit = design[+0x3a]<<5, [ship+0x9c]&4 -> fmul ds:0x2743
  (header-region const, UNRESTORED — 2x stays [inferred], cat-1 twin
  ds:0x85312==2.0); IN-RANGE == dist <= limit (0x4baae jbe skips the fail);
  gizmo 0x2f second tighter gate (fmul qword ds:0x2747, unrestored);
  ENGAGE flag bit0 = in-range AND target!=self AND design[+0x33] bit 0
  (GZ_TARGETSHIP, gizmos.md §1 flag table) — 0x4bad4..0x4bafc; bit0 clear ->
  exit 0x4c780 (returns acc, NO charge); damage ebx = cat0 ? design[+0x52] :
  0; cidx==0x2f -> design[+0x4a] (0x4bb36..0x4bb43); ebx==0 -> or flag 0x10,
  skip hit; hit call 0x4bb56 (eax=target, edx=mode, ecx=[atk+0x54]>>16,
  ebx=damage); mode==1 -> 0x4c614 charge [ship+0x88] -= MIN + after-effect
  tree (0x2f NOT in t87 case list; SPECIAL1 column +0x4a override = model
  field, non-goal K9 otherwise).
Hit path 0x4b740 absorb chain verbatim (0x4b7a7..0x4b896): flags := 0;
  [t+0x9c]&0x10 -> absorb edi := 0 (shield NULL, invuln); edi > shield
  [+0x90] -> spill ebp := dmg - shield, absorb := shield, flags |= 2;
  hull layer: ebp > hull [+0x8c] -> hull_absorb := hull (CLAMPED, no
  negative hull), flags |= 4; mode!=1 -> return flags (C3); mode==1 ->
  star-record K8 leg + 0x43a4c (diplomacy-on-attack, closed row, sim hook =
  no-op noted) + APPLY [t+0x90] -= absorb, [t+0x8c] -= hull_absorb +
  hull < 1 -> 0x49d2c death + victim-owner event leg (DAT_0007458e gated,
  campaign-side, non-claim).
Resolver Leg A/B (0x42d09..0x42e34, S2k stands; this session re-verified the
  Leg-B halt tests): array OWNER-RACE FILTERED (caller-side 0x41318..0x413b3:
  race match, power>0, kind!=1); Leg A first kind==4 carrying gizmo 0x49 ->
  carrier engagement state [ship+0x62]:=0, [+0x63]:=0, [+0x67]:=1,
  [+0x68]:=objective (0x42d9c..0x42dbd); Leg B first kind==4 with
  companionScan != 0 AND stanceSetter(ship,1,objective) != 0 (SIDE EFFECTS
  COMMIT on the winner); winner halt test [esp+0x2d0] != 0 at BOTH leg loop
  heads (0x42d16 / 0x42ded).

## S3 SIM MODEL DECISIONS (t364 build)

M-a Model the GUN path (0x4b8e4+0x4b740) as THE per-slot shot law — it is the
    only cited damage path; handlers 1/2 run no hit call (C1) and are
    engagement no-ops in the sim (named, not silently dropped: report
    records handler id chosen).
M-b Sim exposes BOTH legs separately (probe/commit) exactly like the vendor:
    probeVolley() (always mode 0, mutates +0x62/+0x63/+0x67/+0x68 + flags
    only) and commitShot() (dispatcher on ACTIVE slot: ammo DEC law, gun
    gates, mode-gated apply+death, MIN-charge). engageRound() composes
    Leg A + Leg B (mode from caller; K6: player edges pass 1, AI 0).
M-c Ship gains activeSlotIdx (+0x63 surrogate, int, -1 none) and SimDesign
    gains targetShip flag (+0x33 bit0). +0x67 reuses Ship::orderType (single
    byte, two consumers — G-b precedent).
M-d destroy = owner -1, kind NoOrder, act 0 (C4; corpse travel-reissue moot,
    planet-slot release is planet-side non-goal).
M-e Carrier-leg skip gate (planet ACTIVE Ship/Orbital-Shield items, S2k) =
    caller-supplied bool (operands are planet state, shipsim has none).

## S4 LEG A/B CONTROL FLOW (raw 0x42cd7..0x42e6e, this session)

C6 Leg A COMMITS AND RETURNS: carrier found -> descriptor byte 3 + ship ptr,
   engagement state [+0x62]:=0, [+0x63]:=0 (NULL slot, activeSlot none),
   [+0x67]:=1, [+0x68]:=objective, RETURN -1 (0x42dc0). NO firepower leg runs
   in the same resolution — Leg A is exclusive, not additive.
C7 OWNERSHIP SUB-LEG POLARITY (0x42d64..0x42d99): no-carrier path reads cl =
   DAT_0007458e (local race), tests [obj+0x15] & (1<<cl): JNE (nonzero ==
   objective IS the local player's) -> jmp 0x437ee (OUTSIDE the banked
   region, return value unknown); the FALL-THROUGH (objective NOT the local
   player's) returns 2. S2k's gloss "2 = objective is the player's, nothing
   picked" has the POLARITY BACKWARDS (the verified instruction order is
   above). Sim models: no-carrier + not-local-player -> no engagement; the
   IS-local branch 0x437ee is an UNMODELLED seam (name it, do not guess).
C8 Leg B verbatim (0x42de0..0x42e34): eligible iff kind==4 AND
   0x4a604(ship) != 0 AND 0x4a55c(ship, 1, objective) != 0; winner stored at
   [esp+0x2d0] and the loop-head halt test stops the scan (first-eligible).
   NOTE arg==1 -> [+0x67] := 1 (shield-handler stance, C1/C2), so the
   resolver's OWN volley probe routes to 0x4c794 (no hit call, C1) and its
   return value is UNDECODED. The sim's engageRound therefore picks the
   shooter on the three DECIDABLE tests (kind/companionScan/power) and runs
   the cited GUN law for the damage step — named substitution: the resolver's
   firepower leg is the cat-0 gun path (S2k Leg B companion-scan IS the
   first cat-0 slot scan), the handler-1 body's return semantics are not
   banked. Player-command-exec (ah==3, 0x25560) is the mode-1 edge that
   commits a stance-0 ship's ACTIVE gun slot verbatim.

## S5 BUILD STATUS

C9 RANGE-0 LEG POLARITY (gun handler 0x4b9a3 `cmp design[+0x3a],0 /
   je 0x4bad4`): the branch SKIPS the distance math with the in-range
   sentinel ecx still -1 (init 0x4b910 mov ecx,-1) => Range 0 = UNLIMITED
   RANGE, not never-fire. Zero-witness (all 10 cat-0 file rows Range 25..100;
   gizmos.txt 76-row census this session) — modelled verbatim, flagged.

Items: header fields (dispatcherGate/activeSlot/fireTarget/systemId,
SimDesign.targetShip/special1) DONE; setStance (verbatim stores + volley tail
0x4a5c1 inside it, returns edi-truthiness), companionScan, volleyTail (public
seam), gunEngageFlag (C9 range-0 unlimited leg), commitShot (dispatcher ammo
law + DEC order + gun gates + charge-even-on-zero-damage + mode-gated apply +
C4 destroy), engageRound (C6 exclusive Leg A, C7 polarity, C8 Leg B with the
stance-volley test in-loop), digest extended with the engagement quadruple —
see shipsim.cpp t364 block; pins test_shipsim_t364.cpp; mutation campaign.

