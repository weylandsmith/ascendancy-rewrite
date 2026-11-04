# WIP t192 (2026-10-29) — TRIGGER-A adjudication + lane share law

## PART 0 — TRIGGER A RESOLVED: STALE-BASELINE RE-ARM, NOT A NEW SITTING

Trigger A armed on size/mtime growth of work/r1/playcap/live-timeline.jsonl
(baseline BASE_SIZE=5691796463 / BASE_MTIME_NS=Oct-26 15:44:01 frozen at t116;
current 5702731088 / Oct-29 00:12:44). Adjudicated the NEW BYTES EXACTLY
(offset-filtered, not a whole-sitting replay):

  scripts/r1_t192_window_adjudicate.py RC=0
    indexed=56165 uniq=56165 bad=0 file_size=5702731088
    window_entries=280  trusted_rows=178  stale_echoes=0
    turn_range=1131..1335   wall=23:28:02..23:58:42
    relation STATE transitions: EXACTLY TWO — Chamachies->Orfa 1->3 and
      Orfa->Chamachies 1->3 (the t=1335 reciprocal ALLIANCE write)
    states outside the banked enum {0,1,2,3}: NONE
    attitude |delta|>=10: 14 events, t1254/t1284/t1306/t1335 only (t1335:
      Chamachies->Orfa 595->605, Orfa->Chamachies 613->631 = the §16.1 flip pair)

VERDICT [verified]: the growth IS the 2026-10-28 night sitting (wall 23:28 ->
00:12) already consumed and banked — diplomacy.md §15 (t187 WAR->PEACE) and §16
(t189b state-3 ALLIANCE, OQ-023 CLOSED). The 194 untrusted t=0 tail rows
(in_game=False) are title-slot saves (t82 law) = t190's "ring tail wall 00:12:43".
Nothing un-adjudicated; NO ledger row moves on this trigger.

CAUSE (harness, not RE): the sitting landed but the probe's frozen baseline
stayed at the Oct-26 value, so every later iteration re-arms on ALREADY-CONSUMED
bytes. The probe comment sanctions the fix ("re-freeze only when a sitting
legitimately lands (the sitting-adjudication task)") — this iteration IS that
task; baseline re-frozen to the adjudicated state (r1_idle_probe.py).

## PART 1 — LEG (a): FUN_00046354 IS MUTUAL LANE-VISION SHARING [verified, asm]
(FINAL STATE: closed; canonical write-up = ships.md S23 L6 + OQ-019 STATUS t192.)

Raw listing (Ghidra 0x46354..0x46424, 61 insns shown of 73) OVERRIDES the
decompiler in two ways: (i) decompiler conflates the incoming EBX (a caller flag
stored to [ESP] at 0x4635f BEFORE EBX is zeroed at 0x46365) with its reuse as a
counter; (ii) it hides the per-lane re-test of that flag at 0x46402.

__regparm3 signature: EAX=param_1 (diplo/AI base block), EDX=param_2 (empire
index, MOVSX at 0x46362/0x4639f), ECX=invisible third (unused), EBX=flag (0 =>
bidirectional, nonzero => RECEIVE-ONLY for party-1).

  0x46367 MOV DL,[ECX+EAX+0x1c0]   ; state byte: block[param_1 + 0x1c0 + param_2]
  0x46370 CMP DL,0x3               ; ==3 == ALLIANCE (t189b enum)
  0x46375/0x46383 CALL 0x7824f     ; RNG; IDIV EBP(6 or 3); INC EDX
        => N = (rand % (state==3 ? 6 : 3)) + 1     [0x4638f..0x46395]
  0x46399 MOV DH,1 / 0x4639b MOV CL,[ECX] / 0x4639d SHL DH,CL
        => PARTY-1 MASK  DH = 1 << byte[param_1 + 0x00]
  0x463a2..ac EAX = ((p2<<5)-p2)<<3 - p2 = 247*p2 ; *2 in the disp =>
  0x463b7 MOV CL,[EAX*2+0x12e16]  => index = 0x12e16 + 0x1ee*param_2
  0x463c3 SHL DL,CL
        => PARTY-2 MASK  DL = 1 << byte[0x12e16 + 0x1ee*param_2]
  0x463b0 DI = word[0x177d3] = LANE COUNT;  0x463be EAX = 0x16147 = LANE POOL
        base (payload imm; folds to data-seg+0x3337 = t190's 39-byte lane rec,
        stride 0x27 = 39 — SAME pool the 'l' cheat 0x273ca ORs)

LANE WALK (ECX = lane index, EAX += 0x27, while ECX < word[0x177d3]):
  dispatch 0x46402 CMP dword [ESP],0 (the incoming EBX flag, re-tested per lane)
    flag!=0 -> 0x463d2 (receive-only branch)
    flag==0:
      0x46408 test rec+0x20 & DH ; if ZERO -> 0x463d2 (party-2 lends to party-1)
      else 0x46413 CMP ESI,[ESP+4]=N; 0x4641c test rec+0x20 & DL;
           0x46420 INC ESI; 0x46421 OR rec+0x20,DL   ; party-1 LENDS to party-2
  0x463d2 (receive branch): 0x463d5 test rec+0x20 & DL; if ZERO -> next lane
      0x463dd CMP EBX,N ; 0x463e6 test rec+0x20 & DH; if SET -> next lane
      0x463ea INC EBX; 0x463eb OR rec+0x20,DH        ; party-1 RECEIVES party-2's lane
  0x463ee next lane -> 0x46402

LAW (asm-grounded): one call to FUN_00046354 performs a MUTUAL TRACT OF LANE
REVEALS between empire1 (= byte[param_1+0]) and empire2 (= species-block byte at
0x12e16+0x1ee*param_2): for up to N lanes party-1 already sees, party-2 gains the
bit; for up to N lanes party-2 sees and party-1 does not, party-1 gains the bit.
N = 1..3 normally, 1..6 when the relation byte block[param_1+0x1c0+param_2] == 3
(ALLIANCE) => ALLIANCE DOUBLES THE LANE-SHARE BUDGET. Both counters are per-call
(not persisted), and grants are OR-only => sticky (t191 stickiness law holds).
CALLERS (Ghidra get_xrefs_to 0x46354, UNCONDITIONAL_CALL): 0x45778 and 0x55f6e
(get_function_callers returns 0 — the t191 caller-discovery caveat again).

ARGUMENT PINNING (get_assembly_context, 25 insns each side):
  SPECIES/DIPLO ROW LAW [verified from 0x55f55..0x55f69]:
    0x55f55 XOR EAX,EAX / MOV AL,[0x7458e] / IMUL EAX,EAX,0x1ee / ADD EAX,0x12e16
    => param_1 = 0x12e16 + 0x1ee*idx is a DIPLO ROW (0x1ee=494 row stride;
       row+0x1c0 = relation-state bytes (0x46367), row+0x1b2 = attitude u16s
       (0x4577d ADD word[ESI+EBP*2+0x1b2],0xa)).
    byte[param_1+0x00] = that row's OWN empire index (0x4639b MOV CL,[ECX]).
    party-2's empire index = byte[0x12e16 + 0x1ee*param_2] — so param_2 is a
    TABLE ROW INDEX, and DH = 1<<own_idx / DL = 1<<other_idx: both parties are
    species-table empires. t191's "species 'lanes-shared-at-contact' column"
    hypothesis for [0x12e16] is DEAD: 0x12e16 is the diplo-row table base, and
    the byte read is that row's empire index, not a per-scenario gate column.
  CALL SITE 1 = 0x45778 (inside the ALLIANCE-FORMATION handler; the +10/+5
    attitude bumps at 0x4577d/0x4578a and the state==3 test at 0x457c3 sit in
    the same basic-block chain; 0x45722 writes row+0x1c0 state bytes):
    EAX=ESI (actor's diplo row), EDX=EBP (other index, unpacked from a packed
    u32 [ESP+0x1c2] with SAR 0x10), EBX=0 (XOR EBX,EBX @0x45774) => BIDIRECTIONAL
    lane share fires the instant an alliance is made.
  CALL SITE 2 = 0x55f6e (event-dispatch family; same block also calls the STAR
    twin 0x46524 immediately before, and 0x55a60/0x56b5c/0x55020 after):
    loop 0x55f1b..0x55f2e walks ESI=0..word[0x13b98]-1 over every race, and per
    race: EBX=-1 (MOV EBX,0xffffffff @0x55f44/0x55f62) => RECEIVE-ONLY mode;
    param_1 = CURRENT PLAYER's row ([0x7458e]), param_2 = the looped race.
    With EBX!=0 the dispatch 0x46402 JNZ 0x463d2 pins the receive branch:
    grants the PLAYER lanes the other empire already sees (capped N/call).
  STAR TWIN FUN_00046524 (same law, star pool): base LAB_00013bc5 stride 0x60,
    count DAT_00016143._2_2_ (= word 0x16145 = t190's star count), the
    visibility pair bytes +0x16/+0x17 (vs lane rec's single +0x20), modulus 4 if state==3
    else 2 (=> N=1..4 star reveals alliance vs 1..2 otherwise — HALF the lane
    budget's max but the alliance DOUBLING law is the same shape). The 's' cheat
    0x27401 writes the same star field [0x13bdc+i*0x60] (+0x17) — consistent.

## PART 2 — LEG (b): THE 0x22074/0x22e60/0x22f28 GROUP IS A LANED-ENDPOINT VISION
## PROPAGATOR OFF A PER-RACE SUB-OBJECT (static), POOL IDENTITY PENDING MEASURE

Raw context (get_assembly_context):
  sub-object addressing form (all three sites):
    row   = [ESI + 0x1ee*idx + 0x0d]        (dword pointer in the diplo row!)
    rec_i = [sub + 0x2c + 4*i]              i < word[sub + 0x44]
  0x2205b..0x22092 (GRANT): BL = 1<<byte[ESI+0x56]; OR [rec+0x20],BL  and then
    EBX=[rec+0x00] -> OR [EBX+0x16],CH  and  EAX=[rec+0x04] -> OR [EAX+0x16],BL
    => it ORs the mask into the record's +0x20 AND into BOTH endpoint objects'
    +0x16. t190 established lane rec+0/+4 = the two star OBJECT pointers
    (allocator 0x248af/0x248b1), and FUN_00046524 uses star-obj+0x16/+0x17 as
    the star visibility bytes — so rec+0 and rec+4 dereferencing into +0x16
    is EXACTLY the lane-pair -> endpoint-stars reveal shape.
  0x22e45..0x22e6a (CLEAR): BL=0 (XOR BL,BL @0x22e4d); sub+0x14=0, sub+0x17=0,
    then per rec: [rec+0x20]=0, [objA+0x16]=0, [objB+0x16]=0.  << A CLEAR OF
    rec+0x20 EXISTS — via this pointer-array path.
  0x22f0e..0x22f37 (MERGE): BH=[rec+0x20] | BL -> [rec+0x20]; CH=[rec+0x17]|BL
    -> and ORs into endpoint obj+0x16s (an accumulate/copy form).

CONSEQUENCE FOR THE t191 STICKINESS LAW [flagged, decision pending measurement]:
if the [sub+0x2c+4*i] pointers ARE lane-pool records, t191's "no lane-pool-scoped
clear exists => reveals sticky" is FALSIFIED in the strict form (0x22e60 clears
+0x20, and clears the endpoint stars' +0x16 too). If they point at a DIFFERENT
pool (a per-race contact/contact-list of lane handles), the sticky law stands.
MEASUREMENT RESULT (scripts/r1_t192_share_mask_scan.py rev2, RC=0, 20 saves):
 220/220 pointers lane-pool congruent; race r's list == EXACTLY {lanes with
 rec+0x20 == 1<<r} 100/100; pool census {0:940,1:40,2:60,4:40,8:40,16:40} =
 zero shared lanes in the NEW-GAME corpus (share path unwitnessed — needs a
 mid-game save). LEG C: paired mask byte = member B+D+0x6774 (payload
 0x21aa6 = 88 15 74 67 00 00; Ghidra DAT_00089324 == payload 0x6774) ==
 1<<[0x7458e] 20/20 but WEAK (idx==0 in every new-game save). The rev1 read
 at B+D+0x89324 was a DOUBLE-OFFSET error (0x89324 is already the absolute
 image addr; member addr = B+D+0x6774) — caught by validating race names at
 B+D+0x74590. Stickiness: t191 law CONDITIONAL (0x22e60 clears via per-race
 list under FUN_00022ce4 (single caller 0x2271e inside FUN_000226e4, whose
 four callers 0x2142e/0x214b0 (FUN_00020fd4), FUN_00024f24 0x24f8f and
 0x52cb6 all read as setup; mid-play firing
 UNMEASURED). Canonical caveat text in ships.md S23 L6.

ORIGINAL MEASUREMENT PLAN (kept for provenance):
 for each save resolve B,
pool_base=B+0x82bb0+0x16147, lane count word@0x177d3; for each race row read
[sub+0x2c+4*i] and report (p - pool_base) mod 39 congruence + whether word[sub+0x44]
equals the lane count. That is the same congruence method t190 used for handles.
