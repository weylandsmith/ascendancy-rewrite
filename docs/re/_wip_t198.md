# WIP t198 — planet-screen paint-routine census (OQ-005 legs a2)

Trigger triage: live-timeline.jsonl size 5,721,578,066 == frozen TRIGGER-A
baseline (Oct 29 13:22) -> NO new sitting; no steering note in prompt; tree
clean at ab28629 (t197). Worked STATE NEXT ACTION as assigned.

## S0 Method + pitfalls
- Tool: scripts/r1_t198_blit_callers.py (RC=0). Byte-pass over obj0 code span
  [0x14bb0,0x82bb0) for E8 rel32 == FUN_0005caac, enclosing function from
  work/functions_full.tsv (file_off == image addr, base-0 restored image),
  module attributed by the function's references to literal '..\module.cpp'
  debug strings (immediates in the restored image are POOL-RELATIVE:
  S = imm + 0x82BB0, per the STATE datafile-string law caveat 1).
- PITFALL (bank): Ghidra `get_function_callers(FUN_0005caac)` returns only 15
  callers — it is NOT the 75-site truth (unanalysed/dark regions + thunks).
  The byte-pass census reproduces t83's 75 exactly, so USE THE BYTE PASS.
- PITFALL (bank): `run_script_inline` with Java source FAILS in this server —
  pre-existing broken scripts in ~/ghidra_scripts (T66Callsites.java,
  SeedFns.java, Diag.java) poison the whole build ("skipping ..." for every
  script incl. mine). Python+capstone (~/tools/revenv) or stdlib byte passes
  are the working route; do not burn calls fixing third-party script dirs.
- PITFALL: windows.txt keys: only 7 SHAPEITEM lines exist (1starmap/3cfgnew);
  the planet-screen gauges have NO windows.txt shape binding at all.

## S1 BLIT-CALLER CENSUS [verified, 75/75 sites, 53 enclosing functions]
Module vote of every function containing a blit call (full tsv =
`python3 scripts/r1_t198_blit_callers.py`; 29 of 53 functions are single-site
orphans inside unanalysed spans — vote empty):
  gwindow  0x30fb8(2) 0x32318(2) 0x32afc(2)   0x317bc(1, vote-less)
  winmgr   0x156d4 0x55748 0x5a980
  coswnd   0x2925c(1)
  helpwin  0x34a04(2)
  planet   0x37b6c(2)          <-- planet.cpp cluster
  PLANWIN  0x3aa0a..0x3e342 -> SEVEN blit sites   <-- THE PAINT TARGET
  race     0x3d2fe(1) 0x6529d(2)
  shipgiz  0x4c794(1)   shipwin 0x4e63c(4)   sssystem 0x4ff34(7)
DECISIVE STRUCTURAL FACT: the gauge widgets PLRES/PLIND/PLPRO/PLPOP
(extracted/ascend00/windows.txt:1522/1539/1556/1576, all TYPE **29**, PARENT
PLANETALLOC, SHAPEFRAME -1, SENDMESSAGE 50 with SENDPARAM1 = 0/1/2/4
respectively; PLBUILD TYPE 29 SENDMESSAGE 51) are drawn by planwin.cpp code,
NOT by the generic widget pass FUN_00031384 (which only understands descriptor
byte0 types 0/1 with a FIXED desc+5 selector — shp.md S11.1). So per-level
record selection must live in the planwin blit sites: the generic pass is
structurally incapable of it.
NOTE the widget descriptor law still applies to those sites (desc+1 cache slot
index u16, desc+5 selector u32, screen x/y desc+7>>16 / desc+9>>16 — S12.1),
but the DESCRIPTOR IS WRITTEN BY THE PAINTER, so reading the painter's stores
to desc+5 gives the level->record map.

## S2 THE PLANET-SCREEN GAUGE PAINTER FOUND [verified asm]
Function region 0x3aa0a..0x3e342 is a Ghidra mega-block; the REAL paint body
starts at **0x3b96c** (prologue push ebx/ecx/esi/edi/ebp; sub $0x380,%esp;
MOV EAX,EAX=widget ptr — __regparm; every blit site 0x3b9df/0x3ba1e/0x3ba4a
reads arg1 = LEA ESI,[EBP+4] = the widget's own descriptor copy, matching the
S12.1 blit arg law, and slot index DX from a stack copy of widget fields).
Full listing banked: work/t198_planwin.asm (objdump -D -b binary -m i386
0x3aa0a..0x3e342 of work/ascend_restored.bin).

### S2.1 THE LEVEL->RECORD LAW [verified 0x3cc9f jump table + cases]
Switch dispatch @0x3cc90..0x3cca6: `MOV EDI,[ESP+0x4c]; CMP EDI,4; JA default;
JMP *cs:0x27fe8(,EDI,4)` — a FIVE-WAY switch on the widget's SENDPARAM1
(PLRES=0/PLIND=1/PLPRO=2/PLPOP=4 per windows.txt:1535-1610; the gauge widgets
are TYPE 29, SHAPEFRAME -1, so NO windows.txt shape binding exists — selection
is 100% code-side, which is why the windows.txt census found nothing).
Cases (verbatim asm):
  case 0 @0x3cca7: slot idx u16 = [0x6fd90]; LEVEL = u16 [STATEPTR+0x46];
      SELECTOR = clamp0_20( round(LEVEL * 1.8f) )  -- [push 0x3fe80000 = 1.8f;
      call 0x78a90 (fmul) / 0x76e08; fistp; clamp <0 -> 0, >0x14 -> 0x14]
  case 1 @0x3cd3b: slot idx = [0x6fd92]; LEVEL = u16 [STATEPTR+0x44];
      SELECTOR = clamp0_20( round(LEVEL * 1.8f) )
  case 2 @0x3cdcf: slot idx = [0x6fd94]; LEVEL = u16 [STATEPTR+0x48];
      SELECTOR = clamp0_20( LEVEL )   -- NO multiplier
  then all three: PUSH 0; PUSH 0; PUSH selector; PUSH slot; PUSH cache-base
      (0x9f10c); CALL 0x1fc34; PUSH payload; PUSH desc+4; CALL 0x5caac.
  STATEPTR = dword [0x43508] (the current-planet object; +0x57 = owner byte
  per the FUN_0003aa0a decompile comparisons vs DAT_0007458e = player idx).
=> **THE COMPRESSION MAP IS *1.8 WITH A 0..20 CLAMP** for the two multipliers,
   identity+clamp for the third. 21 vendor records (0..20) cover the whole
   gauge; the player's "~60 levels" testimony maps through x1.8 + clamp.
   [unverified which of +0x44/+0x46 is research vs manufacturing — S3 ties
   them via the t45 governor law writes.]

### S2.2 POPULATION SLOT LAW [verified 0x3ce39 case]
@0x3ce39..0x3cef8: loop ESI = 0 .. u16[STATEPTR+0x4a] (CAPACITY), step:
  free-slot counter EDX@esp+0x64 starts 1, INCREMENTED when ESI ==
  u16[STATEPTR+0x4c] OR ESI == u16[STATEPTR+0x42];
  blit per slot: PUSH EBP(row), PUSH EDI(col), PUSH selector(=counter),
  PUSH slot [0x6fd9c], cache base; CALL 0x1fc34/0x5caac;
  column advance EDI+=0x0a per 5 slots, row EBP+=? when remainder != 9 (idiv 10,
  CMP EDX,9 / JNE) => a 10-per-row grid of slot icons sized to CAPACITY —
  exactly the player's "array sized to planet capacity" testimony, now cited.
  Field +0x4a = capacity u16; +0x42/+0x4c = the two exception positions.

## S3 (next) tie +0x42/+0x44/+0x46/+0x46/+0x48/+0x4a/+0x4c to named stats via
the t45 governor-law writes (0x38df0 PROS+=IND>>2 / 0x38e?? RES+=IND>>2) and
the cache-slot globals 0x6fd90/92/94/9c writers (library names).

