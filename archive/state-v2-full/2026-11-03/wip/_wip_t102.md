# t102 WIP — EVENT-24 (SA_) consumer decode

Session start 2026-10-27. Task per STATE.md: what queued event 0x18 on game
object 0x7a35c (producer 0x55a60 from FUN_0003e6e0 tail) does WHEN DISPATCHED;
resolve whether the SA_ bodies re-run via the edx==1 dispatch (0x441c1).
Residue F8b (zero-POWER Ungooma rows) is leg 4; fallback 0x37b6c dx-switch.

Sitting check FIRST: live-timeline.jsonl 5,691,796,463 B mtime 2026-10-26
15:44 — UNCHANGED since t101 (STATE.md figure). No new sitting; assignment
stands. (r1_t85g_sitting.py --status re-run clean, last trusted turn 1254.)

## F1. Producer 0x55a60 fully disassembled (0x55a60..0x55ae4)
Gates + record layout CONFIRM t99 F15 exactly:
  if ds:0x10ba4 == -1 (netplay?) -> return 0, NO push.
  depth = ([obj+0x4758] >> 16 sar); if depth == 32 -> return 0 (queue FULL).
  rec = obj + n*10 + 0x475e : WORD type := edx(si); +0x4760 := ebx(obj arg);
  +0x4764 := ecx (ctx). Counter [obj+0x475a] += 1 (word).
  Return eax = -1 (pushed OK) or 0 (dropped).
NOTE field split: +0x475a LOW word = WRITE index (pusher incs);
+0x475c = READ index (consumer incs at 0x55d7e); +0x4758 hi word = depth
(= count - read? [inferred] — depth sar'd from the SAME dword the pusher
incs its low word of; pinned live below if cheap).

## F2. CONSUMER FOUND: FUN_00055ae8 = the queue pump (0x55ae8..0x55dba)
Entry gates (0x55af3..0x55b20):
  ds:0x7a358 == -1 -> exit (0x7a358 sits 4 bytes below the game object 0x7a35c
    = queue-busy flag; consumer SETS it to -1 at 0x55b7c while pumping).
  [esi+0x4758]>>16 (depth) == 0 -> exit (queue empty).
  [[esi+0x4226]>>16] == 1 required (some mode gate).
  window lookup call 0x56d1c(edx='EVENTWIN' 0x85943) -> ebp; if null,
    call 0x2a428(0x630, 0x2daa) [assert/error-report shape, pinned later].
  record select: eax = [esi+0x475a]>>16 (!!), edx = esi + n*10, call 0x2ab04
    (scratch-buffer copy of the record? pinned). ds:0x7a358 := -1 (ebx).
TYPE SWITCH reads ecx = ([ebp+0x475c] >> 16 sar) — the record TYPE word
  (+0x475c low word is the read index, hi word aliases the type of the
   CURRENT slot? [verify live]) with range-tree:
  <3: 0 / 1-2 -> 0x55bae ; 3..8 -> 0x55c17
  9..16 -> 0x55bc7 region ; 17 -> 0x55bd7+ ; 18-19 -> 0x55bc7
  20..22, 24, 25, >25 -> terminal arms incl. 0x55c17 and 0x55d69(test ecx
  je 0x55bae)
  [reading the arms 0x55bae..0x55c04 next — the KEY question is which arm
   calls FUN_00043b50 with edx==1]
Ring maintenance 0x55d6f: read idx (+0x475c) += 1; if == write idx (+0x475a)
  both reset 0 (circular).
Re-arm: tail calls 0x56ad4(esi, edx=1, ecx=1) when edi != 0 (edi = 0xd/0x10
  per arm = re-dispatch mode?).
Post-switch arms seen 0x55c17..0x55caf:
  0x55c17 region: cmp dl,4 je 0x55c32 else call 0x2a428(0x69d, 0x2daa)
  0x55c32: eax:=[esp+0xc]; ebp:=[ebp+0x59]  <- the queued OBJ +0x59!
  4/8 + [esp+8]==2 -> ds:0x43504 := ebp; mode edi=0x10.
  else: ship-record index math eax*166 (shl5-sub-shl3-sub-add-add) onto ebp
    -> 0x12e16 base; call 0x45d4c(...); sets BYTE [rec+0x12fff]:=1 /
    DWORD [rec+0x13000]:=ebp — ship-availability-table family [0x12e16 =
    data-intra? pinned from t-something].

## F3. QUEUE INDEXING RESOLVED (live 60.sav + static, byte-exact)
Record = 10 bytes: TYPE word at obj+10n+0x475e, queued-obj u32 at +0x4760,
ctx u32 at +0x4764. Cursors share dwords with the fields:
  dword[+0x4758] = (low word +0x4758 misc) | WRITE-cursor<<16
  dword[+0x475a] = READ-cursor? NO: word(+0x475a)=WRITE cursor (pusher incs
  at 0x55ad9), word(+0x475c)=READ cursor (pump incs at 0x55d7e); when
  read catches write BOTH are zeroed (0x55d8a..0x55d9a, circular sync).
  So sar dword[+0x4758],16 = write cursor; sar dword[+0x475a],16 = word
  at +0x475c = READ cursor = the slot the dispatch processes.
Push (0x55a60): bail (ret 0, NO push) if ds:0x10ba4 == -1, or if write
cursor == 32 (queue full); else rec[write] := {type,ebx,ecx}; write++.
Consumer pump FUN_00055ae8 (ONLY caller 0x54b74 inside FUN_00054650):
  gates: ds:0x7a358 == -1 (busy flag) exit; write cursor == 0 exit (empty);
  [[obj+0x4226]>>16] == 1 required (live 60.sav = 7 -> gate FAILS mid-turn).
  then EVENTWIN window lookup (0x56d1c, str 'EVENTWIN' 0x85943);
  0x2ab04(window, -1, 0, &type word) = announce/log the event [shape];
  if edi==0: call 0x5526c(eax=obj, edx=ebp, ebx=0, ecx=0) -> eax gates
  the switch (test eax; jne 0x55cbc); ds:0x7a358 := 0 (re-arm).
TYPE SWITCH arms (ecx = sar dword[ebp+0x475c],16 = the record TYPE;
ebp = obj + 10*read-cursor; eax = queued obj; edx = ctx):
  0     -> 0x55bae  edi=0x14
  1,2   -> 0x55bb8  edi=0x11; ds:0x43508 := eax (queued obj)
  3..9  -> 0x55c17  (dl=BYTE[eax+0x58]; ebp:=eax; then 0x55c32:
          ebp:=[ebp+0x59]; if ecx in {4,8} && [esp+8]==2 ->
          ds:0x43504:=ebp, edi=0x10; ELSE ship-availability write:
          idx=eax*166 onto 0x12e16 base, call 0x45d4c(...), then
          BYTE [rec+0x12fff]:=1 / 0, DWORD [rec+0x13000]:=ebp; ds:0x6775
          := al; edi=0xd)
  10..14-> NOTHING (0x55d6f ring maint only, edi=0 no re-arm)
  15    -> 0x55bb8  (as 1,2)
  16,17 -> 0x55bc7  edi=0x11; ds:0x43508 := edx (ctx)
  18,19 -> 0x55bd7  if ctx==7: call 0x56ad4(obj, edx=ctx>>16, ecx=0,ebx=0)
          else obj[+0x24d9c] := -1
  20    -> 0x55c17  (as 3..9)
  21,22 -> NOTHING ; 23 -> 0x55c04 edi=0xd; ds:0x6775 := ctx&0xff
  24,25 -> NOTHING  (0x55d69: test ecx,ecx je 0x55bae else ring maint)
  Tail 0x55d6f: read++; if read==write both :=0; if edi!=0 call
  0x56ad4(obj, 1, 1) (redraw/invalidate family, 44 callers).
=> HEADLINE: TYPE 24 HAS NO UI-DISPATCH ARM. The SA_ effect therefore does
   NOT run through this pump. AI ability effects run SYNCHRONOUSLY via
   FUN_00043b50(edx=1) at 0x3eb3c (cadence gate INSIDE 0x43b50:
   cad > counter -> 0x44017 skip bodies, t101-pinned).

## F4. PRODUCER GATE CORRECTS t99 F7 (0x3e7cf..0x3e815, cited byte-wise)
  ebx := row+0x19e; +1; row+0x19e := ebx                     (ALL rows)
  al := BYTE[row+0]; dl := ds:0x7458e
  if al != dl -> exit            <-- event-24 ONLY for the row whose race
                                     byte == ds:0x7458e (NOT 'every AI
                                     race' as t99 F7 stated)
  if ebx == 0 -> exit
  if cad[WORD,row+0x19a>>24] != ebx -> exit   (exact equality)
  else push event 0x18 type, obj-arg=0, ctx=0 on 0x7a35c.
ds:0x7458e identity + ds:0x10ba4 semantics = next probes.
Live 60.sav T=1254 queue: write=0 read=0 (EMPTY mid-turn; +0x4226>>16==7
also blocks the pump), slots stale type=1 records with heap objs
0x26dcd5/0x26dec1/0x26f2ef (phys -> member = ptr-0x88), ctx 35/6.
ds:0x7a358=0, ds:0x10ba4=0, ds:0x6775=2, ds:0x43504=0x256da5,
ds:0x43508=0x270a57.
=> QUEUE PROVES NOT DEAD structurally but EMPTIES fast; a capture at a
   turn boundary with a due cadence would catch it (player row0 cad 89 —
   t99 F9 row0 +0x19e=8; NOT due at 1254).

## OPEN sub-questions (probe queue)
Q1 dump 0x55b80..0x55c1c (pre-switch setup + arms 0x55bae/0x55bb8/0x55bc7/
   0x55c04) — find the call to 0x43b50 (edx==1 per t101).
Q2 rel32 caller census of 0x55ae8 (who pumps the pump; expect turn loop
   0x3e6e0-adjacent or main loop).
Q3 what is [obj+0x59] per queued obj + which arm serves type 24.
Q4 live queue state on playcap/save/60.sav (B via r1_sav_scan.find_base;
   member idx = B+0x82bb0+0x7a35c? NO — 0x7a35c is CODE (aicode.md 743);
   0x7a35c immediates are the game-object POINTER value at runtime P0=...
   CAREFUL: t99 says '0x7a35c = GAME-OBJECT base (299 immediate sites)'.
   In the restored image base-0 space data lives in BSS 0x73e40+... so the
   game object at image addr 0x7a35c -> member B+0x82bb0+0x7a35c? that is
   PAST BSS start, still within corollary range. Verify by sanity values
   (write/read idx words small < 32).

## F5. TYPE SWITCH EXHAUSTIVELY PINNED (objdump 0x55cbc..0x55d69, all arms)
ecx = sar word(+0x475c of slot) = record TYPE; eax = queued obj (+0x4760);
edx = ctx (+0x4764); t[esp+8] = 0 from 0x55b74 (only ever 0 singleplayer —
set at 0x55b74 xor ecx;ecx->stack; never written again before switch):
  0        -> 0x55bae edi=0x14
  1,2,15   -> 0x55bb8 edi=0x11; ds:0x43508 := eax
  3..9,20  -> 0x55c17 (dl=[obj+0x58]; require dl==4 else assert 0x2a428(
             0x69d,0x2daa); ebp:=[obj+0x59]; if type in {4,8}&&t[esp+8]==2
             -> ds:0x43504:=ebp edi=0x10 [DEAD: t[esp+8]==0 always];
             ELSE row=(ctx==eax*166)*2 base 0x12e16; call 0x45d4c(row,2,0,
             ebp); set BYTE [0x12fff+rowoff]:=1/0, DWORD [0x13000+rowoff]:=
             ebp; ds:0x6775:=al; edi=0xd)
  10..14   -> ring-maint only, edi=0 (NO re-arm)
  16,17    -> 0x55bc7 edi=0x11; ds:0x43508 := edx
  18,19    -> 0x55bd7 (if t[esp+8]low==7: call 0x56ad4(obj,sar ctx16,0,0);
             else obj[+0x24d9c]:=-1) [18: t[esp+8]==0 -> else-branch ONLY]
  21,22    -> 0x55d67/0x55d69 fallthrough; 24,25 -> 0x55d69
  23       -> 0x55c04 edi=0xd; ds:0x6775 := BYTE ctx-low (0xc(%esp) al)
  >=26     -> 0x55d69
=> TYPE 24 (0x18, the SA_ producer event): 0x55d02 cmp 0x17 jb->0x55d12;
   0x55d12 cmp 0x16; jmp 0x55d69 -> test ecx (nonzero) -> ring maintenance
   ONLY. NO EFFECT ARM. The event is consumed as a NULL/refresh event with
   edi=0 (0x55d69 path leaves edi untouched=0 from 0x55b99? NO — edi set
   0x55b99 xor edi,edi BEFORE switch; 24 keeps edi=0) -> tail skips the
   0x56ad4 re-arm (0x55d9f test ebx,ebx je 0x55db1).
CONCLUSION (binding for the SA_ chain): queued event 24 does NOTHING but
advance the ring. SA_ effects NEVER run through this pump. The t99 bodies
(FUN_00043b50 edx==1 jump table) are the ONLY SA_ effect path; the queue
entry is a bookkeeping/refresh signal for the EVENTWIN UI.


## F6. SA_ SYNC DISPATCH + 0x7458e IDENTITY (0x37b6c/0x3eb3c gates, cited)
FUN_00043b50 rel32 callers = EXACTLY {0x37baf, 0x37cb1, 0x3eb3c}.
  0x37baf (in FUN_00037b6c, dx-switch switch 0x37b90): dx<=2 case
    dx==1/2: eax=esi, edx=0 -> call; result -1 -> 0xccb(%ebp):=2. (edx=0:
    never dispatches bodies — cadence-gate probe only, returns -1 at 0x43b9c)
  0x37cb1 (0x37c9c gate `cmp $1,%ebx; je 0x37cad`): THE ONLY UI-path edx==1
    call: eax=esi, edx=ebx=1.
  0x3eb3c (in FUN_0003ea54): 0x3eb22 mov ds:0x7458e,%dh; cmp (%ecx),%dh
    (race-byte vs 0x7458e); if NOT equal -> 0x3eb35 edx=1 call; if EQUAL ->
    0x3eb2c cmpl $-1,ds:0x10ba4; jne skip (0x3eb41): local race calls ONLY
    when 0x10ba4 == -1.
  => CALL LAW: 0x43b50(edx=1) runs per-race; the race byte stored at
     ds:0x7458e skips unless ds:0x10ba4 == -1. Live 60.sav: 0x10ba4==0
     (t102 F4) -> the 0x7458e race skips the sync call and instead takes
     the event-24 queue path (producer gate = same 0x7458e equality).
     [inferred] 0x7458e = local player's race byte; the event-24 consumer
     (F5: NO effect arm) means the local race's SA_ bodies run via a path
     NOT yet found => the pump event is an EVENTWIN UI/turn-ready refresh,
     and the human race's special ability is invoked through the UI (the
     DIP 'special ability' button family; 0x37b6c is the UI cmd executor).
0x7458e STORE SITES (image-wide verified opcode scan on 8e 45 07):
  0x21aa0 (FUN_00021a82): al=idx; al==0xff -> dh=0,dl=0xff; else dh=al,
    dl=1<<al; 0x7458e:=idx, 0x89324:=bitmask. 0 rel32 callers (overlay/
    callback entry [inferred]).
  0x52cc6: dl=0 -> 0x7458e:=0, 0x12e17:=0 (reset-family site).
  Readers: 179x mov-form + cmp-form incl. 0x3e746 gate below.
0x3e746 (in FUN_0003e6e0 leg (a)) gates the EVENT-11 push on race==0x7458e.

## F7. FUN_0003e6e0 = PER-RACE TURN TAIL (extent 0x3e6e0..0x3e826, cited)
ebp = RACE ROW. Gates/legs:
  0x3e6ee [row+0x3] == -1 -> exit (eliminated race).
  legs over the ship list from call 0x40ec0(race):
  (a) if call 0x402d8(race) < 0 (0x3e704 jge skips): per SHIP call 0x49d2c
      gated [ship-owner race]==0x7458e; pushes EVENT 11 (edx=0xb,
      ctx=[obj+0xa7]>>24) on 0x7a35c per ship 0x3e74e..0x3e763.
  (b) list empty && 0x40f7c(race)==0 -> EVENT 10 (edx=0xa, ctx=bl=race
      byte) + row+0x3 := -1 (race-death notice) 0x3e786..0x3e79c.
  (c) per-ship loop 0x3e7aa..0x3e7b7: call FUN_0004a74c (RECHARGE, t101
      F7) on every ship — THE per-turn recharge pass driver.
  (d) tail 0x3e7c0..0x3e815: event-24 producer. NOTE 0x3e7c3: al := BYTE
      [[row+0x7]+0x14]; and 0x80 -> je exit: producer requires the
      pointer at row+0x7 to carry flag-bit 0x80 [inferred: automated/AI
      race flag on the race's AI-controller block].
CALLERS 0x3e6e0: {0x25083, 0x250a5} (per-turn driver).
FUN_0003ea54 (the SA_ sync-caller) is called FROM FUN_0003e6e0 at 0x3e7bb
— sync dispatch and the race turn-tail are the SAME pass.

## F8. ORDER-EXECUTOR DRAIN LEGS (F8b candidates) PINNED
FUN_00041260 entry gate 0x412be: bit-test (order[+0x14]|[order+0x15])
mask 1<<[edi] -> je 0x419c0 exit (order not armed for this ship).
State dispatch 0x41e1e: al := [ship+0x5d] order-state; dec; cmp 6; ja
0x41ded; jmp *cs:0x41244(,%eax,4) — jump table at FILE 0x41244 SEVEN
entries verified [0x419cf,0x41cc6,0x41bb3,0x41ded,0x41ded,0x41ded,0x41c56]
(cs==file flat here; the t96 +0x14bb0 law applies to the other table shape).
THE DRAIN LEG = 0x41ded..0x41e19 (cases state 4,5,6 + jcc 0x419ba from
the POWER-affordability select loop 0x4199f `cmp [edx+0x88],%eax; jge
skip`): ebx := [esp+0x3a0]; ax := WORD [ship+0x88]; [ship+0x94] := 0;
ebx -= ax; [ship+0+0x88] := 0; [esp+0x3a0] := bx. => order completion
ZEROS MOVES AND POWER, folds the delta into a stack budget word. 0x41d80
`decl [esi+0x88]` = arrival leg after call 0x496e4 (one-power decrement).
State-clear legs write [ship+0x5d] := 0 at 0x41c98/0x41ca7/0x41ced (why
live zero-power rows show b5d=0).
LIVE 60.sav zero-power rows: b5d=0 ALL FIVE, b63=2606112/0 (queue ptr),
b67=0x279BFFFF-family. b52 AHEAD of T: consistent with a ship BUILT after
the recharge pass (c) ran for its race, then issued a 0-power-finish order
leg. Mechanism CANDIDATE, not yet measured live — see verify below.
