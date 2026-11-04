# WIP t200 — cos_star selector semantics (0x2925c), OQ-005 residue adjudication

Trigger triage: live-timeline.jsonl size 5,721,578,066 == frozen TRIGGER-A
baseline, mtime 2026-10-29 13:22:12.10, dosbox-x not running -> NO new sitting.
Tree clean at d88371f (t199). No steering note. Worked STATE NEXT ACTION.

## S0 Scope + facts carried in
- Task per STATE.md:256-281. Target = the STAR_SHAPES record-index selector
  (DATA\COS_STAR.SHP, extracted/ascend00/windows.txt:208).
- functions_full.tsv: 0x2925c is a FUNCTION START (span 0x2925c..0x29731,
  1237 B) [verified], not a mid-function site. t198 census attributed exactly
  1 blit site (FUN_0005caac) inside it, module vote coswnd.
- Prior context: cos_star.shp n=55 records; V1 + A42 + FAIL12 (t196/t197
  numbers); the FAIL12 = k40..k51, dims word 0 at the V slot, span 0x1b each
  (shp.md S16/S22, _wip_t197.md S:27).
- Method per t198: objdump span listing + r1_t198_site_context.py pool-string
  annots; E8 byte-pass for callers (NOT Ghidra get_function_callers).

## S1 Enclosing function + blit sites [verified]
- functions_full.tsv sizes are HEX (t83 trap; my first bisect used decimal and
  got a wrong span — re-ran with int(p[1],16)).
- 0x2925c = start of **FUN_0002925c**, body 0x2925c..0x2a493 (tsv: 2925c/1237),
  module vote coswnd, exactly TWO blit (FUN_0005caac) sites: 0x298dc, 0x2a223
  [verified byte pass, 75-site census reproduces].
- Ghidra decompile of FUN_0002925c is unhelpful (unaff_EBX == -1 dispatch,
  huge field-copy block): it is a state load/serialize-ish routine whose
  prologue copies ~60 fields into [param+0xc0..0x16e]/0x57a/0x58a; the blit
  sites live deeper than the decompiler's view of the entry. objdump listing
  banked: work/t200_cos_star.asm (0x2925c..0x29731).

## S2 Site anatomy (r1_t198_site_context.py, capstone via ~/tools/revenv)
SITE 0x298dc (blit args per shp.md S12.1 law: [desc-copy, payload, sel, x, y]):
    0x298cc  mov eax,[esp+0x48]
    0x298d0  mov ebx,[eax+0xab]      <-- SELECTOR := u32 word [objA+0xab]
    0x298d6  push ebx
    0x298d7  mov ecx,[esp+0x10]      (payload from cache handle)
    x = [esi+3]>>16, y = [esi+5]>>16 (esi = [esp+0x14] ptr -> desc)  [verified]
  Guard above it: edx (a signed coord/state?) in (-0xdc, 0xdc] picks sel
  classes 0/1/2 into [esp+0x38] (0xdc=220 pool-string collision "con.cpp" is
  an annot artifact; the immediate is 0xdc==220).
SITE 0x2a223:
    0x2a208  mov eax,0x9f10c
    0x2a20d  mov dx,[0x6fd96]        <-- cache global slot pair (t198 family)
    0x2a214  call 0x1fc34            (cache lookup -> eax = slot ptr)
    0x2a21d  push ebx                <-- SELECTOR ebx = 3 default; 9 if
              [esp+0x48]==3; 8 if ==2; -1 => SKIP DRAW (je 0x2a22b)
    0x2a1ab  mov ecx,[ebp+0xa9]; sar ecx,0x10; cmp with byte [0x7458e] ->
              equality SKIPS the draw.
  => 0x2a223 selector is a SMALL ENUM (3/8/9), not a star-level ladder.

## S2b Blit arg law RE-VERIFIED from the prologue (not memory) [verified
0x5caac..0x5cb5b]: arg1 [ebp+8]=shape-struct ptr ([s]=hdr ptr, hdr=[pixptr]
[W-1][H-1], s+4..+0x10 clip rect clamped); arg2 [ebp+0xc]=PAYLOAD BASE;
arg3 [ebp+0x10]=SELECTOR; arg4/5 +0x14/+0x18 screen x/y (both += rect min).
Cursor @0x5cb4d: ESI = u32[payload + 8 + 8*sel] -> stream = entry+0x18.
Generic-pass reference push order 0x3143a..0x31462 (y,x,sel,payload,desc)
confirms right-to-left mapping. PITFALL: esp-relative reads between pushes
must be re-based per push — hand ESP math here produced a contradiction, so
control flow into 0x2986d must be established before reading args.

## S2c DISPATCH OF FUN_00029788 (the COSMOS child-paint loop) [verified
objdump 0x29788..0x2a240 + Ghidra decompile of the created function]:
  iterates children of [win+0x400] (count) via &children[i]; per child:
  v = round(fld [child+0xd] + const@0x105e); al = low byte of v; child+4 =
  TYPE byte? (dispatch): al==0 -> 0x29e71 -> big block 0x2986d (blit 0x298dc,
  payload = [obj+0xab]); al==1 -> 0x29bb0 (8-class range ladder ->
  FUN_0005bf71 selector = cls + 0x30/0x68/0x70 family); al==2 -> 0x29cc6
  (FUN_00053e58 text/label); al>=3 -> 0x29845 loop-advance, NOTHING drawn.
  Ladder thresholds in the al==1 block: >=0xdd:0, >=0x94:1, >=0x4a:2, >=1:3,
  >-0xdc:6? (chain: <0xdc... verified chain 0/1/1/2/2/3/3/4/4/4/5/5/6/6) —
  RE-DERIVE before banking (context; see planets-ui.md S3 for the gauge analog).
FUN_00029fa8 (separate handler, same class): blit 0x2a223 SELECTOR =
  relation-state byte [esp+0x48] (loaded from table 0x12fd6 + idx*2 stride
  0x1ee = the t189 diplomacy table): state 3 (ALLIANCE) -> sel 9; state 2
  (WAR) -> sel 8; else -> -1 = NO DRAW; also -1 (no draw) when
  [esp+0x34] (table 0x12e19 ptr) != 0. Payload = cache 0x9f10c slot [0x6fd96].
  x=0xe, y=3 fixed. Gate 0x2a1ab: ([ebp+0xa9]>>16 == byte[0x7458e]) -> skip
  (i.e. skips drawing for the player's own race index 0? [0x7458e] read).
0x2a2b4 (message-handler case, jump table 0x2a25c): WORD [esi+0xab] =
  byte[esi+0x25] - 0x31 then compared to [0x13b98] — CONFLICTS with [obj+0xab]
  being a dword payload pointer at 0x298dc => either different class or a
  union; MUST resolve (this is the crux for "which library + which selector").

## S3 Selector-field writer census (pending) — [r+0xab] has 71 writers / 229
## S6 CORRECTED ARG MAP (real anchor: P = esp after `sub esp,0x58`; my earlier
ESP table mis-anchored by 0x58 because the tracker's `sub esp,` test tested
op_str only — PITFALL BANKED; arg roles below re-derived by hand with the
5-push sequence, and they agree with the Ghidra regparm decompile):
  0x298dc blit args: arg1 shape-struct = wnd+4 ([P+0x10] slot, init @0x29809)
    arg2 PAYLOAD = [wnd + 0xab]   (0x298cc reads [P+0x3c] = edx-in window obj)
    arg3 SELECTOR = 4*[child] + cls  ([child] = dword at child record +0)
    arg4 x = [child+3]>>16 ; arg5 y = [child+5]>>16  (16.16 fixed, unaligned)
  cls ladder on v = frndint(fld [child+0xd] + ds:0x105e):
    v >= 0xdc -> 0 ; 1..0xdb -> 1 ; -0xdc..0 -> 2 ; < -0xdc -> 3
  child dispatch byte [child+4]: 0 -> STAR blit path above;
    1 -> 0x29bb0 LANE/ladder path: cls7 chain (verified cmps 0xdc->7,
       0x93->1? RE-DERIVE: mov ecx defaults downward: 7 default, 1,2,3,4,4,5,5,
       6 by cmps 0xdc/0x93/0x49/../0xffffffb7/0xffffff6d/0xffffff24) then
       SEL = (cls7<<2) + 0x10 with branches +0x30/+0x68/+0x70 (decompile) ->
       FUN_0005bf71 (different draw helper, own payload);
    2 -> 0x29cc6 text/label (FUN_00053e58); >=3 -> loop advance, no draw.
  [child] is read as INDEX in the al==0 path but as POINTER in al==1/2 paths
  (esi[0]+0x21/+0x23/+0x54/+0x58/+0x59, +0x59 -> owner-race record w/ t195
  visibility mask bit test) => heterogeneous child struct (union at +0).
  => RESIDUE ADJUDICATION hinges on K_max = max [child] over star children:
     SEL = 4K+cls reaches k40..k51 iff K reaches 10..12. cos_star has 55 recs
     (k0..k54; FAIL12=dims0 at k40..k51; 13 types x 4 classes = 52 exactly
     covers k0..k51 — suggestive, NOT proof). Next probe: star-record writer
     of the +0 type field (anchor: `fld [reg+0xd]` readers -> writer fstp).

## S7 FINAL ARG MAP at 0x298dc [verified by careful manual esp walk reusing
the S2c instruction stream; the r200_espmap.py annotation pass was BROKEN
(o.mem.base==41 never matches in this capstone; tool needs operand-TEXT
matching — fix or delete before reuse)]:
Base: P = esp after `sub esp,0x58`. At 0x298dc (5 body pushes done)
esp = P-0x14 -> callee argk = [P-0x18+4k]:
  arg1 shape-struct = ecx = [P+0x00] = edx-in + 4 (0x297a1 lea, 0x29809
        slot, 0x298d7 read at esp=P-0x10 of [esp+0x10]) -- WINDOW SHAPE STRUCT
  arg2 PAYLOAD BASE = ebx = [edx-in + 0xab] (0x298cc at esp=P-0x0C reads
        [esp+0x48]=P+0x3c = edx-in store @0x29794)  <-- t198 was right
  arg3 SELECTOR     = 4*K + cls where K = *([P+0x14]) and [P+0x14] = the raw
        dword at child+0 (0x2986d mov eax,[esi]; 0x2986f store; 0x298bc read
        [esp+0x1c] at esp=P-8 -> P+0x14; 0x298c0 mov eax,[eax] = DEREF;
        shl 2; + [esp+0x40] at that point = P+0x38 = cls)
  arg4 x = [child+3]>>16 ; arg5 y = [child+5]>>16 (16.16 unaligned)
  cls ladder on v = frndint(f32[child+0xd] + ds:0x105e): v>=0xdc->0;
  1..0xdb->1; -0xdc..0->2; v<-0xdc->3.  [verified 0x29873..0x298ad]
Lane path (al==1) selector = 4*cls7 + {0x10 base, plus 0x30/0x68/0x70
  conditionals} -> FUN_0005bf71 (different helper); 0x10=4*4 shows the SAME
  4-records-per-class ladder family, class bases offset by 4*4.
## S8 STRUCT CORRECTED (r200_espmap.py verified; tool now annotates correctly
when invoked with LO AFTER the prologue sub): the paint loop iterates a
dword-pointer cursor ([P+8], starts at param_1, step +4, count [w+0x400]);
each ENTRY esi is a DISPLAY NODE: +0 POINTER to the stride-0x60 star record
(base 0x13bc5 static; ships.md star coords +0x08/0x0c/0x10), +4 dispatch tag,
+3/+5 x/y 16.16 (unaligned), +0xd float. Blit arg1 shape-struct = [P+0] =
edx-in + 4 = WINDOW+4 (not node+4 — re-checked at 0x298d7: esp=P-0x10,
[esp+0x10]=P+0). FUN_00028fc0 (0x2903a) stores the star-record pointer into
[w+0xb3]-based storage and zeroes tag [rec+4] (0x2904f). K law VERIFIED with
the tool: 0x298bc mov eax,[P+0x14] (= node+0 = star ptr); 0x298c0 mov eax,
[eax] (= u32 star+0 = K); shl 2; + [P+0x38] cls.
  MEASUREMENT VALIDATED: the census read u32 at star_record+0 DIRECTLY —
  which is exactly the deref target (node+0 IS the star record base; the
  census walked 0x13bc5+0x60*i). K in {0,1,2,4,5,6,7,8,9,11,12}, subset of
  the 13 starstat types. (Node-array location/stride in the window object
  stays unmodelled — not law-bearing.)
  +0x59 pointer, stride 0x60 base 0x13bc5) => same dword read as INT K in
  the al==0 path is the star record's OWN +0 FIELD => SEL = 4*[starrec+0]+cls.
