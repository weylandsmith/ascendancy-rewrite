# _wip_t309 — RING-0x10/0x11 CONSUMER WINDOWS (0x55a60 family witness)

Assigned: STATE.md NEXT ACTION t309. STEP 1 offline caller map -> ships.md S35;
STEP 2 capture run arming consumer legs + btn_hdlr, NEXTTURN inside armed
window + post-disarm baseline discriminator.

## S0. PRE-FLIGHT
- No new sitting: live-timeline.jsonl last rows turn=1086 wall 15:03 (watcher
  pid 1979 alive, production dosbox pid 1957 alive). t309 stands un-steered.
- Ghidra headless HTTP alive on :8089 (404 on /status = server up).
- HARNESS BUG FIXED (t309): scripts/r290_disasm.py objdump fallback used -d on
  a raw binary -> ZERO instructions printed, every window empty (capstone is
  NOT importable in system python3 3.13.5 here). Patched to -D. Any prior
  'empty window' reading from this tool was this bug, not missing code.

## S1. STEP 1 — 0x55a60 ENTRY + CALLER MAP
(payload = work/ascend_payload.bin, imagebase 0, file offsets == obj0 offsets)

S1.1 0x55a60 IS THE RING POST, NOT A CONSUMER (disasm verbatim):
  entry gates: ds:0x10ba4==-1 -> ret 0; ([eax+0x4758]>>16)==0x20 (ring full,
  32 slots) -> ret 0. Writes record at stride 10 (u16 code @+0x475e+i*10,
  u32 param @+0x4760+i*10, u32 extra @+0x4764+i*10 — i = count>>16), then
  0x55acc: inc WORD [eax+0x475a] (write index) and returns eax=-1.
  => matches t308's follow-on bytes at 0x28ec7.. (calls 0x56ad4 -> 0x55a60).

S1.2 THE CONSUMER = fn 0x55ae8 (prologue push ebx..ebp; sub esp,0x10):
  gates at entry: ds:0x7a358==-1 -> out; ([esi+0x4758]>>16)==0 -> out
  (ring count zero); ([esi+0x4226]>>16)!=1 -> out.
  Reads record via [esi+0x475a] (write index) at 0x55b46, dispatches on
  ecx = code>>16 through a compare-tree 0x55cdc..0x55d6f. THE 0x10/0x11 ARMS
  ARE THE t296 CENSUS LEGS THEMSELVES:
    0x55cdc: mov ecx,[ebp+0x475c]; mov eax,[ebp+0x4760]; mov edx,[ebp+0x4764]
    0x55cf1 (0x9<=ecx<=0x14) -> tree; 0x55d17: cmp ecx,0x10 / 0x55d1c cmp
    ecx,0x12 -> 0x55d25: cmp DWORD [esp+0x8],0x1 jne-out;
    0x55d30: mov edi,0x10; 0x55d35: mov ds:0x43504,eax   <-- leg w43504_55d35
    0x55d3c: cmp ecx,0xf -> arm shared with 0x11? (0x55d3f je -> 0x55bb8
      region) ; 0x55bb8: mov edi,0x11; 0x55bbd: mov ds:0x43508,eax  <-- leg
      w43508_55bbd ; 0x55bc7/0x55bcc: mov edi,0x11; mov ds:0x43508,edx
      (extra-field variant).
  So code 0x10 stores the record PARAM into DAT_43504; 0x11 stores into
  DAT_43508 — SELECTION STATE IS RING-DRIVEN, the t296 reading holds
  statically. Consumer leg 0x55bbd is mid-block (reachable only via the tree);
  0x55ae8 entry is the block-top arming candidate.

S1.3 PUMP MAP: E8 callers of 0x55ae8 = exactly ONE site 0x54b74, gated:
    0x54b51: cmp WORD [esi+0x475a],0 ; je out      (ring write-index nonzero)
    0x54b5b: cmp ([esi+0x4226]>>16),1 ; jne out    (same mode gate)
    0x54b69: cmp DWORD [esi+0x489e],0 ; jne out
    0x54b74: call 0x55ae8
  Sibling 0x55df4 (ring SHADOW COPY, called once from 0x54b4a in the same
  parent fn, gated ([esi+0x44aa]>>16)>0): memcpy [esi+0x422c..0x436c] (0x140
  B) -> [esi+0x436c], then zeroes WORD [esi+0x44ac]. NOTE 0x54b4a sits on the
  0x54b4f jmp-out path of the same block ladder.
  Parent-fn entry: candidates by c3 boundary {0x54650 callers 0x217b3,
  0x555f9; 0x546b1; 0x546d9} — resolve next probe.


S1.4 PARENT-FN IDENTITY + PUMP CALLERS (t309 session, payload census):
  parent fn 0x54650 (size 0x1734) has exactly TWO E8 callers, BOTH invoked as
  `mov eax,0x7a35c; call 0x54650` (rebased core-state ptr law, t307):
    0x217b3 in fn 0x20fd4 (0x2104) — fn 0x20fd4 called ONLY from 0x7b817 in
      fn 0x7b7d7 = PROGRAM ENTRY TRAMPOLINE (stack alloc via ds:0x97e0, calls
      0x5b5f init, sets ds:0x97e4, then 0x7b817; epilogue mov esp,ebp;ret).
      => 0x20fd4 = MAIN GAME LOOP.
    0x555f9 in fn 0x5558c (0x177) — same shape (0x555ea calls 0x4849c-fn,
      0x555f9 calls 0x54650 on core ptr, gates ds:0x7ec06/ds:0x660c) = a
      secondary/sub loop over the same core.
  fn 0x5526c (the fn containing pump-call 0x553f3 -> 0x5558c) is called from
  10 SITES {0x1bf32,0x27c1e,0x548f7,0x54e09,0x5573b,0x55a0c,0x55b8a,0x56029,
  0x59a8d} incl. INSIDE the consumer 0x55ae8 itself at 0x55b8a and inside the
  shadow-copy 0x55df4 at 0x56029 — a widely-shared sub-pump.
S1.5 CONSUMER GATE SEQUENCE (0x55ae8 verbatim, disasm):
  ds:0x7a358==-1 -> out (re-entrancy guard; SET to ebx=-1 at 0x55b76 AFTER the
  ring-slot fetch, CLEARED to 0 at 0x55b9b/0x55b84 paths);
  ([core+0x4758]>>16)==0 -> out (ring COUNT zero — the 0x55a60 post incs WORD
  [core+0x475a] write-index AND count lives at +0x4758 per post-fn gate
  ([eax+0x4758]>>16)==0x20 full);
  ([core+0x4226]>>16)!=1 -> out (mode gate, same as pump gate 0x54b5b).
  Then: fetch slot via 0x202c-call(0x2d93), record ptr ebp; read [esi+0x475a]
  write-index, slot addr = [esi+0x475e] + (idx*10); dispatch tree on
  code=ecx>>16; THE 0x10 ARM: 0x55d17 cmp ecx,0x10 -> 0x55d25 gate
  cmp [esp+0x8],1 -> 0x55d30 edi=0x10 -> 0x55d35 mov ds:0x43504,eax.
  THE 0x11 ARMS: 0x55bb8/0x55bbd (param) and 0x55bc7/0x55bcc (extra edx).
  0x55d3c: code 0xf je -> 0x55d55 region (the 0x11 tree shares the 0xe-0xf
  branch target 0xfffffedc).
S1.6 PARENT GATE AT THE CALL (0x54b51..0x54b74 verbatim): write-index
  [esi+0x475a]==0 -> skip; mode !=1 -> skip; [esi+0x489e]!=0 -> skip; THEN
  call 0x55ae8. POST-CALL 0x54b79: if [esi+0x24d9c]==-1 AND ring count
  [esi+0x4758]==0 AND [esi+0x489e]==0 -> msg 0x7 posted via 0x56ad4 — i.e.
  THE PUMP ITSELF POSTS msg-7 WHEN THE RING DRAINS. Sibling 0x54b4a shadow
  copy runs when ([core+0x44aa]>>16)>0.
S1.7 INSTRUMENT AUDIT (CORRECTED SAME PROBE — my first reading was WRONG):
  census_click(x=None) DOES arm all legs (the x-is-None branch only skips
  close_eventwin; arm_census(self.legs) runs regardless, r299_leg_session.py:
  880-899). So t308's baseline windows WERE hot 15s. The REAL blind spot is
  the BETWEEN-WINDOW choreography (legs cold) and the fact t308 never armed
  THE CONSUMER ENTRY 0x55ae8 AT ALL — the t308 legset was 8 mid-block store
  legs + btn_hdlr; a zero at 0x55d35/0x55bbd cannot distinguish 'consumer
  never ran' from 'consumer ran, dispatch never took the 0x10/0x11 arm'.
  FIX THIS ITERATION: arm cons_entry 0x55ae8 (block-top fn entry) +
  resolver 0x55df4 + pump call-site 0x54b74 alongside the store legs.
S1.8 RING SEMANTICS CORRECTION + PUMP GATE CHAIN (disasm verbatim):
  0x55a60 record write is INDEXED BY CODE (0x55a8b: edx=5*code -> slot @
  [core+0x475e+code*10]); the u32 param/extra stores at 0x55aa3/0x55abc use
  index ([core+0x4758]>>16); write-index WORD [core+0x475a] inc'd at 0x55acc,
  NEVER reset inside 0x55a60. Gate ([core+0x4758]>>16)==0x20 rejects code>=32
  (or full-32 count — ambiguous offline; the 0x56ad4 sibling uses [core+
  0x44aa] count + [core+0x44ac] index + slot base +0x422c — the FIFO shape
  ships.md S24/S33 describes). TWO RINGS: RING-A (0x56ad4 post, FIFO
  {u16 edx, u32 ebx, u32 ecx} @+0x422c, consumed by SHADOW-COPY fn 0x55df4
  gated ([core+0x44aa]>>16)>0) vs RING-B (0x55a60 post @+0x475e, consumed by
  0x55ae8 gated write-index!=0). t308's 'ring 0x10 posted via 0x56ad4' =
  RING-A; the consumer family 0x55ae8 drains RING-B — THE t308 ASSIGNMENT
  CONFLATED THE TWO RINGS. w43504_28ec2 posts ring-A code 0x10; whether it
  ALSO posts ring-B is UNTESTED (fn 0x28e70 span shows one post at 0x28ed8).
S1.9 PUMP RUN GATE (fn 0x20fd4 @0x21786 verbatim): path to the 0x54650 call
  at 0x217b3 requires ds:0x660c == -1 (jne skips the whole block otherwise);
  ds:0x7ec06 value selects an extra 0x4849c-call but BOTH branches reach
  0x217ae. COUNTER-EVIDENCE: fn 0x55df4 case at 0x55ebe does
  `xor edx,edx; mov ds:0x660c,edx` = CLEARS the pump gate (0 != -1 -> pump
  stops running). Resolver 0x55df4 is a jmp-table dispatcher (0x55e86
  `jmp DWORD PTR cs:[eax*4+0x41220]` — table bytes at 0x41220 are RELOCATED
  in-RAM, file-image reads are garbage, do NOT decode offline).
S1.10 MODE GATE HYPOTHESIS [inferred from verified gates]: consumer 0x55ae8 +
  pump 0x54b74 + shadow 0x54b4a ALL require ([core+0x4226]>>16)==1. If the
  galaxy-map idle state is mode != 1, the consumer CAN NEVER run at t=1086
  idle regardless of ring contents — which fits every zero so far. The
  witness experiment arms cons_entry so the census DATA decides, not the
  hypothesis.

S1.11 TWO-RING CENSUS (whole-image E8 caller decode of BOTH post fns, t309):
  RING-B post 0x55a60 (record @ [core+0x475e+code*10], u16 edx=code, u32
  ebx->+..60, u32 ecx->+..64; write-index WORD [core+0x475a] INC, count gate
  ([core+0x4758]>>16)==0x20 rejects): 19 call sites, edx code constants
  {0x1,0xb,0xc,0xc?,0xd,0xf,0x10 x2,0x12,0x13 x2,0x15,0x16,0x17,0x18,0x19} +
  5 sites with edx from memory/unknown. THE CODE-0x10 POSTS ARE EXACTLY TWO:
    0x41c17 in fn 0x41260 (size 0x2010) — `edx=0x10, ebx=esi, ecx=[esi+0x5e]`
    0x499e0 in fn 0x49880 (size 0x376)  — same shape
  CONSUMER 0x55ae8 (sole E8 caller = pump site 0x54b74 in main-loop fn
  0x54650) dispatches RING-B records; its 0x10 arm stores [esp+0x8]==1-checked
  param -> DAT_43504; 0x11 arms -> DAT_43508.
  RING-A post 0x56ad4 (FIFO slot [core+0x44aa]>>16 at +0x422c, index inc
  [core+0x44ac]): 45 call sites incl. w43504_28ec2's follow-on 0x28ed8 with
  `mov edx,ecx` (ecx=1 at that site — code 1, NOT 0x10!). t308's 'ring 0x10
  posted via 0x56ad4' READING IS WRONG: the 0x10 at 0x28ebd goes to ebx (the
  u32 PARAM field per 0x56b2e `mov [esi+idx*2+0x422e],edi` where edi=ebx),
  and edx=ecx=1 is the u16 CODE. RING-A is consumed by SHADOW-COPY fn 0x55df4
  (jmp-table 0x55e86 on code<=8; code 0x10 -> `ja 0x56336` = DEFAULT: error
  report 0x7cc + loop-continue, NO DAT WRITE). => a star-click ENTER posts
  RING-A code 1 param 0x10; NOTHING about it can make the DAT-writing
  consumer 0x55ae8 run. THE t308 CLOSE CONDITION TESTED THE WRONG RING.
S1.12 JUMP RESOLVER LAW (t309 tool trap): objdump -b binary prints jump
  targets as dump-relative dummies ('je 0x3e'); resolve by hand from the raw
  bytes (eb/70-7f: 8-bit; e9/0f8x: 32-bit rel from next-insn addr). Data
  immediates of jmp tables (e.g. 0x41220 for 0x55e86) are RELOCATED IN RAM —
  the file-image reads decode garbage; never trust them.
S1.13 EXPERIMENT RE-SPEC (STEP 2, replaces the t308-shaped battery):
  legs = cons_entry 0x55ae8 (block-top, sole entry) + ringB_post 0x55a60
  (19 sites -> any ring-B activity) + ringB_w10_41c17 + ringB_w10_499e0 (the
  ONLY code-0x10 writers) + ringA_resolver 0x55df4 (positive control: fires
  whenever ring-A drains, and the star click DOES post ring-A -> guaranteed
  witness expected after the ENTER click) + w43504_28ec2 (t308 witness leg,
  regression) + btn_hdlr (NEXTTURN control). Windows: baseline 15s; star
  ENTER click 60s; POST-CLICK HOT HOLD 60s (census_click(None) re-arms the
  SAME legs leg-hot with no click — the blind-spot fix); control_nextturn 60s
  + POST-TURN HOT HOLD 60s. Oracle extended with pump-gate ds:0x660c (the
  0x55df4 case at 0x55ebe CLEARS it to 0; fn 0x20fd4 pump path requires -1)
  and re-entrancy guard ds:0x7a358; TURN DELTA via existing rd(0x12e10) pair
  around control_nextturn settles t308 close-condition branch (b) (did the
  turn actually advance?).
  PREDICTIONS (falsifiable): (P1) ringA_resolver fires after the star ENTER
  (ring-A post happened; pump gate 0x54b4a only needs ([core+0x44aa]>>16)>0);
  (P2) cons_entry fires IFF ring-B write-index [core+0x475a]!=0 at some pump
  iteration — if ring-B is empty all game at t=1086 idle it stays zero and
  the datum is 'consumer never runs, ring-B dormant' (mode-gate hypothesis
  S1.10 is then NOT separable — say so); (P3) turn delta>0 after NEXTTURN iff
  no modal swallowed it.

## S3. RUN t299-leg-20261105-161711 (rc=0, attempt 2; attempt 1 = BREAK-lottery
### loss at 16:17:10, retry loop as designed). 7 legs BPLIST-verified armed in
### EVERY window (session.log 16:19:00 'BPLIST 7 entries').
S3.1 POSITIVES: star click (182,284) ENTERED again (diff 94712) and the WITNESS
  DELTA REPRODUCED: DAT_43504 0x256825 'Icarus' -> 0x255bc5 'Vega' (4th
  reproduction of the t308 datum). btn_hdlr fired 1x at control_nextturn
  (eip file 0x336b4, ret0_file_off 0x56cdd via pump site 0x56cda, wrec_eax
  name NEXTTURN, EDX=EDI=7, EAX=0xfd6190).
S3.2 THE MEASUREMENT (pty whole-log census, ALL windows incl. both HOT HOLDS):
  cons_entry 0, ringB_post 0, ringB_w10_41c17 0, ringB_w10_499e0 0,
  ringA_resolver 0, w43504_28ec2 0, btn_hdlr 1. A whole-table sweep of the
  pty log over EVERY LEGS entry returned ONLY btn_hdlr — the writer legs
  (unarmed this run) counted 0 correctly (no stop without armed BP; instrument
  law self-consistent).
S3.3 ORACLE GATE SNAPSHOT (identical at star0_before, hold_post_star,
  nextturn_before, nextturn_after; star0_after is the SYSTEM-VIEW moment):
  mode4226=0x1, ringB_count=0x0, ringB_widx=0x0, ringA_count=0x0,
  ringA_idx=0x0, pump_gate_660c=0xffffffff, guard_7a358=0x0, turn=1086.
  star0_after: mode4226=0x10 (SYSTEM VIEW IS MODE 0x10 — NEW datum: mode
  values are view/phase ids). nextturn pair: turn 1086->1086 UNRESOLVED —
  the sav ring is 10 s granular (REFUTED-ROUTES t260 law), so the after-sav
  may predate the click; do not claim either way.
S3.4 GATE + WRITER INVENTORY (re-verified 2nd pass after catching two reading
  errors — jne-target direction and an ignored store form; everything below is
  byte-level re-checked):
  (i) RING-A post fn 0x56ad4 gate 0x56ae0: `mov eax,[eax+0x44aa]; sar 0x10;
      cmp 0x20; jne 0x56b02 (NORMAL)` — equal 0x20 = ERROR path (report code
      0x9aa line 0x2eea at 0x56aff, then fall-through writes the slot ANYWAY).
      So the post is NOT gated shut at idle (count!=0x20 passes).
  (ii) RING-B post fn 0x55a60 gate 0x55a76 is the mirror (`cmp edx,0x20;
      jne 0x55a92 normal; equal -> ret 0`): full-32 rejects. Also gate
      0x55a66 ds:0x10ba4==-1 -> ret 0.
  (iii) WHOLE-IMAGE WRITER CENSUS (scripts/r309_ring_writer_census.py,
      mod=10 disp32 + SIB base=disp32 sweeps, sanity-matched against known
      sites): [core+0x475a] written ONLY by post fn 0x55ad9 + consumer-arm
      zero 0x55d93; [core+0x44ac] written ONLY by post fn 0x56b4e + resolver
      zero 0x55e3b; count dwords [core+0x4758]/[core+0x44aa] ZERO direct
      writers (loader-initialized or written via a base register I can't
      enumerate statically — [inferred]).
  (iv) DAT DIRECT-STORE INVENTORY FINAL (a3 + 89 /15 both swept whole-image,
      4-byte LE compare): DAT_43504 = 6 writers: a3 {0x28ec2, 0x28ef6 (fn
      0x284bc), 0x36b01 (fn 0x36a90), 0x52003 (fn 0x51b68), 0x55d35 (fn
      0x55ae8)} + 89-15 {0x51ac9 (fn 0x51b68) `mov ds:0x43504,edx`, edx =
      0x13bc5+32*k star-record address (shl 5) — the 6th writer the t296
      census missed}. DAT_43508 = 6 writers: a3 {0x1b5e6, 0x1baa7 (fn
      0x1acd0), 0x51a8e (fn 0x51834), 0x51fc2 (fn 0x51b68), 0x55bbd (fn
      0x55ae8)} + 89-15 {0x55bcc (fn 0x55ae8, the extra-field variant)}.
      fn 0x51b68 owns 3 of 12 (0x52003, 0x51ac9 DAT_43504; 0x51fc2 DAT_43508)
      — the densest selection writer; t310 arms it.
S3.5 CHAIN STATE AT t=1086 MAP IDLE (what the run PROVES vs LEAVES OPEN):
  PROVEN: RING-B is dormant — leg ringB_post (post-fn ENTRY, gate-free
    prefix) fired ZERO whole-log across baseline+star+hold+nextturn+hold
    windows => the 19 RING-B post sites are never CALLED at idle (a zero at
    an entry leg cannot be gate-blind); snapshots ringB_count=0/widx=0 in
    every window agree; consumer 0x55ae8 zero consistent (pump gate1
    widx==0 blocks unconditionally).
  PROVEN: star-click witness delta reproduces a 4th time (Icarus->Vega) and
    mode4226 IS A VIEW/MODE ID: 1 at map, 0x10 inside the system view — the
    consumer's mode==1 gate means it can only run on the GALAXY MAP.
  NOT PROVEN (S3.4-i kills the old argument): whether the RING-A post BODY
    runs at the star click. The idx-0 snapshots are BLIND: the post body
    itself zeroes nothing but the resolver (0x55e3b) zeroes idx right after
    copying, and the first snapshot (hold_post_star) postdates a full pump
    iteration. t310 discriminator: arm ringA_post_entry 0x56ad4 + a leg at
    0x56b4e (post-body inc) — called-but-not-run vs run is then a census
    count>=1 question; arm dump of EAX at 0x56ad4 = the core pointer value
    (settles the core-base identity live: member 0x7a35c vs linear).
  UNRESOLVED: turn advance across NEXTTURN (turn 1086->1086 but the 10 s
    sav ring can predate the click — REFUTED-ROUTES t260 granularity law;
    claim neither way). t308 branch-(b) stays open.
  CONTROL DEFECT (honest): ringA_resolver 0x55df4 as designed is VACUOUS at
    map idle — its caller gate 0x54b44 requires ([core+0x44aa]>>16)>0 while
    nothing at idle ever increments it; a zero there is not evidence the
    pump skipped work. t310: snapshot rd(0x7e5aa) ([core+0x44aa]) +
    rd(0x7e89e) ([core+0x489e]) directly.
