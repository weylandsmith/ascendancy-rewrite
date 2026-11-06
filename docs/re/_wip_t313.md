# _wip_t313 — OFFLINE CALLER HUNT: who calls fn 0x51b68 (class-grid RAM scan)

## S0. Inputs + steering check
- STATE.md NEXT ACTION = t313 STEP 1 (offline, zero capture). No steering note
  prepended.
- Sitting check (pre-flight): playcap watcher alive (pid 1979), live-timeline
  mtime 19:46, but tail 200MB window AND the 1.5GB window show NO turn beyond
  1255; the newest lines are t=1086 (the restored/looped state the t312 run
  itself drove). NO NEW SITTING => r1_t85g_sitting.py NOT run; t313 proceeds.
- Save dir (most recent capture run): work/r1/t299-leg-20261105-192246/save/
  (41..60); probe used 58.sav. Memory member 17,055,880 B; member offset ==
  guest linear (t310 law).
- P0 = 0x1bf450. Target rebased 0x51b68+P0 = 0x210fb8. Controls: 0x51834+P0 =
  0x210c84 (t310: exactly 1 hit @0x248050).

## S1. Scan results (scripts/r313_class_scan.py, 58.sav, run 192246)
- CONTROL 0x210c84: EXACTLY 1 hit @0x248050 — P0 + scan route re-confirmed
  (4th reproduction).
- TARGET 0x210fb8 (0x51b68+P0): ZERO HITS whole 17 MB member.
- btn_hdlr: t310's '0x32ecf' was a wrong file offset (0x32ecf disassembles
  mid-instr); r299_leg_session.py:162 has btn_hdlr = 0x336B4. Control value
  0x336b4+P0 = 0x1f2b04 pending re-run (non-blocking; the 0x51834 control
  already validates the route).

## S2. THE 18-SLOT RUN = THREE STRIDE-24 CLASS ENTRIES (structure law fix)
Walking code-decoding u32s around 0x248050 finds slots 0x248018..0x24805c
(18 u32s) then garbage 0x3c8efa35. Correct reading (t313):

    CLASS ENTRY = stride 0x18, three (fn, fn) pairs + tail:
      +0x00 fn (slot-0 family: entry/ctor), +0x04 router 0x30d08,
      +0x08 fn (slot-2 msg handler), +0x0c fn (3rd slot),
      +0x10 0x311b8, +0x14 0x316f0, then next entry.

    entry @0x247F9C {4d9a8, 30d08, 4dd50, 4e6f8, 311b8, 316f0}
    entry @0x247FBC {4ef34, 30d08, 2114dc*, 2114f8*, 311b8, 316f0}  <- t310's 'class 0x247FC0'
    entry @0x247FDC {..., 210f54*, 210f70*, ...}
    entry @0x247FFC {..., 210a64*, 210a80*, ...}
  (* = raw dump shows these as byte-shifted u32s; see S3 alignment note)

  => t310's 'grid 0x248040 slot 4' was an 8-BYTE-SHIFTED read. True grids
  (stride 6, slot 0 base):
    A @0x248018 {520a8, 30d08, 528ec, 52160, 311b8, 316f0}
    B @0x248030 {51b20, 30d08, 51cc4, 51b64, 311b8, 316f0}
    C @0x248048 {51630, 30d08, 51834, 51680, 311b8, 316f0}   <- STATUSWND (t310 named)
  fn 0x51834 sits at grid C slot 2 = the MSG-HANDLER slot. The t301/t304
  slot law (slot 0 entry, slot 1 router 0x30d08, slot 2 handler) HOLDS —
  t310's odd 'slot 4' reading was the misalignment, not a law violation.

## S3. Alignment trap (bank carefully)
- The region 0x247F80..0x248014 in 58.sav dumps as byte-shifted u32s
  (e.g. 0x247fe4 reads 0x2114f800 = fn 0x520a8 value << 8). t310 quoted class
  ptr '0x247FC0' with value semantics that match the entry at 0x247FBC —
  consistent: the whole class-entry family here is being read 8 bytes (or 1
  byte in the raw dump above — recheck) off. The GRID region 0x248018+ reads
  clean 4-aligned (all values land code-range, terminator garbage after).
  [unverified] why: could be the sav Memory member itself stores a header
  shifting only part of this region, or my region walk start was off-by-one
  byte. The GRID values are the load-bearing ones and they are clean.

## S4. HEADLINE: fn 0x51b68 IS NOT AN ENTRY — 0x51b64 IS
- Disasm (r290_disasm.py 0x51b64 48): 0x51b64 = `push ebx; push ecx; push
  esi; push edi;` then 0x51b68 = `push ebp; mov ebp,esp; sub esp,0x58` — i.e.
  fn 0x51b68 was a MID-BODY address; the real function entry is 0x51b64, and
  0x51b64 IS A CLASS-TABLE MEMBER: grid B slot 3.
- E8 census (scripts/r313_call_census.py, whole payload): ZERO direct calls to
  0x51b68, and ZERO to controls 0x51834/0x51630/0x51b64 — table-member family
  re-confirmed (t309 law holds).
- So the t312 writer pair {0x52003 DAT_43504, 0x51fc2 DAT_43508} lives inside
  the body of a class-table fn (grid B slot 3 entry 0x51b64), NOT dead
  orphan code. The t310 'span fix' conclusion "orphan blocks live past fn
  0x51b68's ret in a further fn" is superseded: 0x51b68 never had a ret at
  its start; the enclosing fn is 0x51b64, a TABLE MEMBER.

## S5. NAMING DONE — GRID B IS FLEETWND (scripts/r313_name_entries.py +
## r313_name_b.py, run 192246 58.sav)
- LAWS CALIBRATED VERBATIM: window rec magic 0x12345678 at rec+0x00, NAME at
  rec+0x20, CLASS PTR at rec+0xa7 (control: ref 0xfda063 -> rec 0xfd9fbc
  'STATUSWND', reproduces t310 exactly). CLASS PTR -> vtable tail at cp+0x88
  /+0x8c/+0x90 = (entry, router 0x30d08, handler): cp 0x247fc0 -> 0x248048
  {51630,30d08,51834} = grid C. So the earlier 'stride-0x18 entry' reading was
  the vtable TAIL region; grids are the canonical tables and cp = grid_base -
  0x88. t310's 'grid 0x248040 slot 4' remains an 8-byte-shifted read; true
  handler slot = 2 (law holds).
- FULL WINDOW CENSUS (115 magic+name recs, 31 class ptrs) is BANKED in
  scripts/r313_name_b.py output — every window class + vtable tail trio.
  Highlights: cp 0x247cb8 btn class (60 wins, tail 30ad8/30d08/336b4);
  cp 0x247fa8 = GRID B {51b20,30d08,51cc4,...} NAMED 'FLEETWND' (1 win, ref
  0xfe7b37, rec 0xfe7a90); cp 0x247f90 grid A = 'NEWGAMEWND'; cp 0x247fc0 =
  'STATUSWND' control OK.
- HEADLINE CHAIN (offline, cited): fn 0x51b64 (entry; 0x51b68 was mid-body) is
  vtable slot 3 of the FLEETWND class; FLEETWND's msg handler (slot 2) is fn
  0x51cc4; the t312 writer pair {0x52003 DAT_43504, 0x51fc2 DAT_43508} lives
  in slot-3 code of FLEETWND. The window whose messages drive the DAT writes =
  FLEETWND. t313 STEP 1 CONDITION MET (class named = FLEET-window).
- fn 0x51834 (STATUSWND handler) default TAIL-CALLS btn_hdlr 0x336b4 (t310),
  and 60 windows share the btn class — consistent with every observed stop.
## S6. WRITER BLOCKS ARE TAIL-CALL CONTINUATIONS OF THE FLEETWND HANDLER
- Block map (scripts/r313_fleetwnd_map.py, objdump -D law): fn 0x51cc4 (FLEETWND
  msg handler, vtable slot 2) = `sub esp,0x1bc` frame; msg chain: cmp dx,2
  (jb/jbe table), cmp dx,0x1c01 -> je 0x51f3b; default tail-calls btn_hdlr
  0x336b4. THE t312 WRITER STORES live in continuation blocks sharing the SAME
  0x1bc frame + epilogue (add esp,0x1bc; pop ebp/edi/esi; ret): block
  [0x51fb5..0x51fb4-ret] holds `mov ds:0x43508,eax` (0x51fc2) + ring post
  ebx=0x11 (call 0x4b0d family); block [0x51ff6..0x52036] holds `mov
  ds:0x43504,eax` (0x52003) + post ebx=0x10; a third block 0x52037 exists.
  SAME SEMANTICS AS STATUSWND fn 0x51834's 0x1c01 path (DAT_43508+ring0x11 /
  DAT_43504+ring0x10) — FLEETWND has its OWN 0x1c01 destination path.
- REACHABILITY (whole-image, all zero, controls valid): E8 callers of
  0x51f3b/0x51ff6/0x51b64/0x51cc4 = 0; rel32 jcc(E9/0F 8x) into {0x51fb5,
  0x51ff6} = 0; short eb/66-e9 = 0; indirect call [reg+disp] with disp32
  {0x88..0x98} = 0 (DISP32 PROBE DEFECT — the real law uses disp8: `ff 55 0c`
  call [ebp+0xc] exists exactly 2x: 0x2a37f, 0x30d4d).
- ROUTER LAW FIXED (r290_disasm 0x30d08): 0x30d08 is the RECT-MOVE slot fn
  (adds dx/bx to win+8/0xc/0x10/0x14); the DISPATCHER is 0x30d37: `mov
  [eax+0x39],-1; mov ebp,[eax+0xa7]; call [ebp+0xc]` — class ptr + 0xc = the
  msg-handler slot. (t301 'slot 1 router' = rect-move member, not the
  dispatcher.)
- RUNTIME HEAP DISPATCH TABLE FOUND (58.sav RAM 0x211188..0x211198): five u32
  {0x211405 x3 = fn 0x51fb5, 0x211446 = fn 0x51ff6, 0x211487 = fn 0x52037}
  sitting right after a compiled stub whose body CALLS rebased targets
  (call 0x2132b0 -> file 0x53e60, call 0x1f0980 -> file 0x51530) then epilogue
  pop ebp/edi/esi/ecx/ebx. ZERO refs to 0x211188 in RAM; ZERO file branches to
  0x51fb5. => the blocks are reached by a COMPUTED/composed dispatch that only
  exists at runtime — offline reachability is EXHAUSTED; a live ret_stack
  witness at the writer store is the only remaining route (t309 law re-derived
  independently: 'name their callers from ret_stack at a stop, not offline').
## S7. FINAL DECODE (probe defects fixed, edge CONFIRMED)
- rel32 arithmetic corrected (raw hex at 0x51cf5 = `66 81 fa 01 1c` cmp
  dx,0x1c01; `0f 84 3b 02 00 00` je rel=0x23b -> TARGET 0x51f3b EXACTLY). The
  S6 'zero branches into the writer blocks' was a WRONG-BASE probe defect for
  this edge; the jb 0x5206f target stands.
- FULLY DECODED CHAIN (file offsets, cited):
    router 0x30d37: mov ebp,[win+0xa7]; call [ebp+0xc]
    -> FLEETWND handler fn 0x51cc4 (frame sub esp,0x1bc):
       cmp dx,2 -> jb 0x5206f / jbe 0x51f0c
       cmp dx,0x1c01 -> je 0x51f3b   <-- DESTINATION MSG, FLEETWND HAS ITS OWN
       (je@0x51cfa rel32 0x23b, next-insn 0x51d00+0x23b = 0x51f3b exact;
        raw 0x51cf5 = 66 81 fa 01 1c | 0f 84 3b 02 00 00)
    -> block 0x51f3b: eax=[win+0xab]; call 0x32fa4; esi=eax; cmp ecx,5
       je  -> 0x51f5d: string 0x2b6b 'order?' call 0x56d1c; call 0x51a1c;
              ecx=1 ebx=8 eax=0x7a35c call 0x56ad4;
              [win+0xaf] = [[win+0xab]+0x8cd]; ret
       ne  -> 0x5205d: DAT_43508 = esi; post ebx=0x11 (0x51fc2 store!)
       (0x51ff6 block: DAT_43504 = [esi+0x59]; post ebx=0x10; same epilogue)
  ecx (msg arg 3 from handler prologue [esp+0x1ac]) == 5 selects the
  CONFIRM-POPUP leg; !=5 writes DAT_43508 directly. The two DAT stores are
  the two legs of ONE msg-0x1c01 continuation, not two independent sites.
  stub (epilogue pop ebp/edi/esi/ecx/ebx + ret @0x211185) followed by a 5-entry
  jump table {0x51fb5, 0x51fb5, 0x51fb5, 0x51ff6, 0x52037} — RAM-resident code
  NOT a rebased file copy; zero u32 refs to 0x211188 in the whole 17 MB member
  AND the whole-RAM stride-4 scan for ANY u32 decoding into 0x51fb5..0x52058
  finds EXACTLY these 5 (no second dispatch table exists in RAM). Slot =
  state-1 (states 1..5): states 1/2/3 -> 0x51fb5 (DAT_43508 writer), state 4 ->
  0x51ff6 (DAT_43504 writer), state 5 -> 0x52037 (post ebx=3, eax=-1).
  [unverified] fix-up mechanism: file 0x3d100 bytes are NOT pointers
  (0x80, 0x6650d231, ...) — the jmp's disp is patched or the table composed at
  runtime; runtime state is the only witness route.
## S8. FINAL CHAIN DECODE — HANDLER FALLS INTO A RUNTIME STATE TABLE
- 0x51f57 `jne` rel32 0xfc -> TARGET 0x52059 EXACT (raw-verified; the ONLY
  branch reaching 0x52059 whole-image — e8/e9/jcc32/eb census). ecx==5 ->
  popup leg 0x51f5d; ecx!=5 -> 0x52059:
  `al = [[win+0xab]+0x58]; al--; cmp al,4; ja 0x52089(ret 0);
  jmp cs:0x3d100(,eax,4)` — a STATE jump table indexed by system-record byte
  +0x58 minus 1 (valid states 1..5).
- FILE bytes at 0x3d100 do NOT decode as pointers (0x80, 0x6650d231, ...) =
  UNRELOCATED table (t307 self-relocation law's mirror: jump tables live in
  obj1 data and are fixed up at load; file scan blindness PROVEN again).
  The RAM instance of the mechanism was found at 0x211188: runtime-composed
  stub (calls rebased 0x53e60/0x51530, epilogue pop ebp/edi/esi/ecx/ebx,
  ret) + 5-entry table {0x51fb5, 0x51fb5, 0x51fb5, 0x51ff6, 0x52037} —
  identical in 41/50/58.savs. Slot = state-1: states 1,2,2,4,5 map onto
  blocks; the DAT_43508 writer block (0x51fb5) holds states 1-3, the
  DAT_43504 writer block (0x51ff6) state 4, the 'post ebx=3 + eax=-1' block
  (0x52037) state 5. [inferred] the 0x211188 table IS the RAM-fixed-up
  instance of the 0x3d100 file table (same 5-slot count, same block targets).
- msg-1 sub-dispatch: jb 0x5206f -> cmp dx,1 je 0x51d29 (reads
  [[win+0xab]+0], string 0x2b16) else jmp 0x51d00 (default btn tail path).
- FULL LAWFUL CHAIN (cited): digit sender 0x356a5 `call [esi+8]` edx=0x1c01
  on KEY-FOCUSED window -> router [cp+0xc] -> FLEETWND handler 0x51cc4 ->
  je 0x51f3b -> [sysrec+0x58] state table -> writer block. THE t312 dark
  writers are ONE msg away from a FLEET-window-focused digit key. The reason
  they stayed dark (t312): digit focus was the NEXTTURNCONT button class
  (0x247cb8), whose slot-2 is btn_hdlr — msg 0x1c01 went to a BUTTON, never
  to FLEETWND.
- STEP 1 CONDITION MET: class named FLEETWND -> STEP 2 capture shape is
  earned. DESIGN (for t314, in STATE.md): legs = fn51cc4_entry (NEW; entry of
  FLEETWND handler — fires for ANY msg to the FLEET window, census leg[0] per
  t311 law) + w43508_51fc2 + w43504_52003; phases: open FLEET window (t310
  battery route: fleet view -> rowjump), click a ship row, then the KEY
  COMPOSITION WITH FLEETWND HOLDING FOCUS: digit key (sender 0x356a5 fires
  call [esi+8] edx=0x1c01 on the KEY-FOCUSED window — t311 proved map focus
  routes elsewhere; FLEET-window focus is the UNTESTED carrier), plus a map
  click x>150 variant. Oracle: DAT_43504/43508 + sel43510 + mode4226.
