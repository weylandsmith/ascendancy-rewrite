# _wip_t336 — windows.txt KEYWORD->STORE MAP + STATE VALUE DISPOSITION (zero capture)

Task: docs/STATE.md NEXT ACTION t336. Methods: static disasm (work/r331_disasm.txt)
+ on-disk windows.txt truth + needle-verified save census (196-save corpus law, t335).
Scripts: scripts/r336_store_map.py (store census), further scripts appended below.

## S0 — Inputs and carried laws
- fn 0x575e4 = windows.txt parser (image offsets; imagebase 0).
- t335 binding: win+0x6d stride-13 = TEXTITEM/SHAPEITEM item array; resident
  windows.txt in .sav is DEAD (truth = extracted/ascend00/windows.txt joined by NAME).
- t333: [win+0xab] control-table ptr / +0xaf count / +0xb1 control index.
- Save-member mapping re-derived per save dir; needle-verify before any ds: read.

## S1 — Store census of fn 0x575e4 (scripts/r336_store_map.py, exit 0)
Disassembly file caveat FOUND: work/r331_disasm.txt contains only 10,113 of
140,824 address lines for the WHOLE file... NO — re-check: the first regex
required >=2-byte encodings; 1-byte insns (nop/int3/push) were dropped. Fixed
pattern in r336_store_map.py -> 2,375 insns in [0x575e4,0x59900), first=0x575e4,
last=0x598ff (contiguous; the fn extends >=0x59900, tail probed separately).

Window/heap-record stores (non-stack bases), grouped by displacement:
  ecx+0x0, ecx+0x1   (2 each: 0x57f8a 0x58023 / 0x57fa1 0x58044) = item record
      byte0 kind + tag writes (t335 item builder, fn 0x31690 call sites)
  edx+0x4  0x5806f;  ecx+0x18 0x5953e/0x59534 (item record tail tail?)
  edx+0x18 0x57cdc; edx+0x1a 0x57cd5; edx+0x1e 0x57e10
  eax+0x3d 0x57d11
  edx+0x59 0x57e7a;  edx+0x63 0x57c27
  eax+0xa7 0x57b36/0x57b64; edx+0xa7 0x57873
  eax+0xab 0x57d56 (imm -1 poison); edx+0xab 0x57e48 (copy parsed u32); ecx+0xab 0x59541
  edi+0x3042/0x3062, edi+0x21d92, eax/ecx+0x48a6/0x48aa/0x48b6/0x48ba = data-segment
      stores (edi = P0-relative data base; NOT window records)
KEY OBSERVATION: the ONLY window-record displacements written inside the parser are
{0x0? none, 0x3d, 0x59, 0x63, 0xa7, 0xab} + the item-array path via ecx (0x0/0x1/0x4/0x18
on the ITEM record base ecx = win+0x6d+13*i). NO stores to the classic header fields
X0/Y0/X1/Y1/TYPE/PARENT/HELPINDEX/SENDMESSAGE/SENDPARAM1/SENDPARAM2/MOUSEFOCUS/
SOUNDCHANNEL/SHAPEFRAME/SHAPEFILE/WINITEMS/CURSORSHAPE/BACKGRNDCOLOR/BUTTONSTATE/
STATENUMBER at their obvious displacements => those keywords are consumed by a
DIFFERENT pass (or the record layout hides them). Need the keyword-comparison chain.

## S1b — CALLING CONVENTION + SCANNER IDENTITY (resolved, verbatim disasm)
- Convention is WATCOM: arg1=EAX, arg2=EDX, args 3+ pushed (objdump displacements
  are esp-relative per-instruction; account for pushes when mapping buffers).
- fn 0x77fe1 = the scanner: wraps engine 0x7a1f7 with reader fn 0x77f64
  (getchar over a stream-state block: [ctx+8] -> {cursor ptr, remaining count};
  EOF sets [ctx+0x10] |= 2). Formats are the ds:0x30xx pool strings
  ('%s %d', '%s', '%d', '%s %d %d %d' — read verbatim from
  work/ascend_restored.bin at 0x82bb0+off, matches the t334 format-string law).
- fn 0x575e4 opens windows.txt (0x206c0), then main loop 0x57687: scan
  "%s %d" -> keyword string buffer + integer token [esp+0x378]; -1 => EOF exit
  (0x59788 -> 0x773be close -> ret).
- DISPATCH IS ON THE PARSED INTEGER ebx=[esp+0x378] (cmp-chain 0x576c4..):
  ebx==0 skip(0x5770f->default tail 0x57892); 1 -> 0x58077; 3 -> 0x586c6;
  4 -> 0x58b40; 5..7 -> 0x5770f; 8 -> assert 0x59772; 9 -> 0x5770f;
  0xa,0xd -> assert 0x593b7; 0xb,0xc -> 0x5770f; 0xe..0x1b -> 0x5770f;
  0x1d..0x20 -> 0x5770f; 0x64..0xc8 -> 0x591fa; 0xc9..0x12c -> 0x5927b;
  else -> assert. The 0x5770f sub-dispatch re-reads [esp+0x378] and matches
  {0,5,6,7,9,0xb,0xc} to window-CLASS CREATION calls 0x78b4c with class-name
  literals from the pool: 0x3022 'GW', 0x3025 'RW', 0x3028 'RSW', 0x85bdc 'NT',
  0x302f 'LW', 0x3032 'IW', 0x3035 'RW'(dup), plus tail others 'PSW','SW','FW',
  'NG','BC','HW','NW' (pool dump verbatim). => the integer token is a
  KEYWORD-ID/TYPE code, and the keyword string is interned/validated via
  0x53d8c / 0x1f95c (name->id; 0x1f8cc allocates its 0x674-byte table).
  The keyword literals themselves are NOT in the RE image (t333 reproduced:
  STATE/WINITEMS/... zero hits in work/ascend_restored.bin; only 'STATE%02d'
  help-string at 0x8598b), consistent with a keyword table supplied from
  OUTSIDE the image (game/ascend00.cob per t333) — dispatch never string-compares
  them in-image.

## S1c — window-record store sites by dispatch block (from S1 grouping)
All stores to the window record inside fn 0x575e4 (bases = window ptr regs):
  +0x3d  0x57d11                      (0x5770f class-table family)
  +0x59  0x57e7a                      (same family)
  +0x63  0x57c27 (and 0x5961d/0x5972b store [parent-window+0x63]=found win +0x41
                       after name-lookup 0x56d1c — PARENT plumbing)
  +0xa7  0x57873 (imm 0x5eb0), 0x57b36, 0x57b64
  +0xab  0x57d56 (poison -1), 0x57e48 (copy parsed u32)   [t333 control-table]
  +0x18  0x57cdc, 0x59534 (word; 0x59534 after 0x1f95c name->id + 0x57400)
  +0x1a  0x57cd5, +0x1e 0x57e10
  item array (ecx = record base): +0x0 kind, +0x1 tag, +0x4, +0x18  [t335]
GLOBAL (non-window) stores by the dispatch blocks:
  0x5927b: mov eax,0x484f8; mov dx,[esp+0x378]; call 0x3031c  — single-value
      store into the pool-relative table at P0-ish 0x484f8 (dispatch range
      0xc9..0x12c).
  0x592b1 LOOP (reached from the 0x591fa path tail 0x592f4? NO — 0x592b1 is its
      own loop head, backward target of the only backward jump in the fn):
      scans fmt 0x34f5 repeatedly into [esp+0x100] buffer, ecx counter, calls
      0x30350(eax=0x484f8, ecx=index) per value — a COUNT-DRIVEN MULTI-%d LOOP
      writing the 0x484f8 table. PRIME CANDIDATE for the STATE line: `STATE
      <count> <ids...>` = count + N integers.
  edi+0x3042/0x3062 zero stores (0x59356/0x59391) = help-text slots (0x2f5f0
      lookup on strings at 0x350f/0x3515 pool).

## S2 — DISPATCH RESOLVED: THE TOKEN IS THE TYPE KEYWORD; KEYWORD LINES ARE
## PARSED IN TYPE-BLOCK ORDER (grammar order == file order, NOT keyword lookup)
Verbatim chain 0x57687..0x5770a: scan `"%s %d"` (fmt 0x85bcc) -> string buf
[esp+0x338] + dword [esp+0x378]; -1 = EOF -> 0x57704 -> close (0x773be) -> ret.
cmp-chain on ebx=[esp+0x378]: 0 skip; 1 -> 0x58077; 3 -> 0x586c6; 4 -> 0x58b40;
5,6,7 -> 0x5770f; 8 -> assert 0x59772; 9 -> 0x5770f; 0xa -> (0x576cd jbe-chain)
assert 0x593c9 'DBGWND'; 0xb,0xc -> 0x5770f; 0xd -> assert 0x593c9; 0xe..0x1b ->
0x5770f; 0x1c -> assert; 0x1d,0x1e -> assert (0x593a0/0x593ac->0x59772); 0x1f,
0x20 -> 0x5770f; 0x64..0xc8 -> 0x591fa; 0xc9..0x12c -> 0x5927b; else assert.
File evidence (extracted/ascend00/windows.txt): TYPE values are exactly
{0,1,2,3,4,5,6,6,6,7,8,9,10x10,11,12,13,14,15,15?..,31,32} subset of 0..32 plus
STATE counts {0,1,3,4} and STATE ids <=31 — i.e. the dispatch domain matches
TYPE values, and every keyword line with a numeric token OUTSIDE the domain
(e.g. NAME has no number; HELPINDEX/SENDPARAM values up to 0x12c region) —
the grammar law: after `TYPE <t>` the parser reads the window's remaining
keyword lines SEQUENTIALLY in file order, the TYPE-selected sub-parsers each
consuming one line; the "keyword string" read by each line's `%s` is scanned
into a scratch ([esp+0x334]) and mostly NOT compared (values are what get
stored). Sub-dispatch 0x5770f (and tail 0x57892..) = CLASS CREATION: for each
type value it calls 0x78b4c(class-name, size, 2) — class literals verbatim from
the pool: GW RW RSW NT LW IW PSW SW FW NG BC HW NW AW EW TW MW GSW COSW CTW BM
LB DBGWND EVENTWIN (pool 0x3022..0x3484 + 0x85be8/0x85bf5/0x85c01/0x85c0d/
0x85fb9/0x86034) — then 0x2a4ec alloc + 0x30c08 init, record base ebp=win+0x20.

## S3 — THE STATE KEYWORD'S STORE IS FOUND: fn 0x57194 = STATE-STATE TABLE
## REGISTER (window-pointer lists per state id), NOT a window-record field.
Block 0x58f67 (dispatch value 0xa... NO — value 0xa asserts; block 0x58f67 is
reached from 0x593b7's `cmp ebx,0xb; jb 0x58f67` i.e. VALUES <=0xa that fell
through 0x576c4's tree = value 0xa path corrected: 0x593b7 dispatches {<0xb ->
0x58f67}; file STATE counts are 0..4 which land here via the 0x64..0xc8 branch?
NO — see grammar: THIS block parses the STATE LINE (count-driven):
  0x58f67: class 0x3409 'LB' creation (0x902 size) for the block context;
  0x58fac..0x58fd0: scans `'%s %s'`(0x340c), `'%s'`(0x3412), `'%s'`(0x3415) into
      [esp+0x334]; 0x58fd8: 0x76ce0 compare [esp+0x334] vs 0x3418 "NONE"; if not
      NONE: 0x56d1c window-lookup -> [ebp+0x63] = parent-handle (PARENT plumbing,
      win+0x41 field) — THIS IS THE PARENT BLOCK, value 0xa = PARENT.
  THE STATE BLOCK IS 0x59021..0x59099 (reached via the same chain at value 0xb:
  `cmp ebx,0xb; jb 0x58f67; jbe 0x5770f` — value 0xb goes to 0x5770f class-creation
  'LW'?? — see S3b correction below).
  STATE parse loop VERBATIM (0x59021):
    scan `'%s %d'` (0x85fdb/0x342b) -> [esp+0x3a0] = COUNT (word);
    loop 0x5905c: scan `'%d'` (0x3431) -> [esp+0x378]; eax=edi(winmgr base),
      ebx=state id ([esp+0x376]>>16), edx=[ebp+0x41] (this window's handle)
      call 0x57194; failure -> assert winmgr.cpp:0xe5d.
  fn 0x57194 (verbatim): asserts id in [0,0x20) (:0xb37) and handle<0x400
      (:0xb38); slot base edx = eax + (id*39)*8 = winmgr + id*0x11c; STATE-ID
      TABLE at winmgr+0x3066: [id*0x238 + 0x3066] u16 count; if count==0 ->
      first slot (store [slotptr+0x3068]=1, [..+0x306a]=handle, counter++ at
      [ecx]); else scan up to 0x20 slots for empty ([edx+0x306a]==0), store
      handle, inc count (:0xb5a on overflow). 32 slots x u32 handles.
  REMOVER fn 0x57284 mirrors it (clears slot, decs count). Companion helpers
  0x57464/0x574a1 set winmgr+0x30ec/0x30f0 per-id u32s; 0x57400 sets
  winmgr+0x30ea word (skip if 0xffff).
=> STATE ids are stored in the GLOBAL winmgr state-entry table
   (winmgr + 0x3066 + id*0x238: u16 count + 32 u32 window-handles), NOT in the
   window record. Residue-(1) STATE-line sub-question closes parse-CONSUMED-by-
   0x57194; census S4 must MEASURE it in saves.
## S3b — GRAMMAR ORDER LAW (which block reads which line) — dispatch value ==
## file KEYWORD position within the TYPE-selected grammar, NOT the keyword name:
## the outer chain routes the FIRST line after TYPE (always `TYPE n` itself has
## value n -> class creation 0x5770f/tail 0x57892 with class per value), and the
## SUBSEQUENT lines are consumed INSIDE the type block by fixed sub-parsers.
## The count-driven blocks are: 0x58f67 (PARENT via NONE-compare), and the loop
## at 0x59021 (STATE: count then N ids -> 0x57194). The 0x592b1 loop scans
## `'%s %s'` (0x34f5) into [esp+0x100] and calls 0x30350(eax=0x484f8, ecx=index)
## per value = a DIFFERENT table (0x484f8 = pool-relative data, dispatch
## 0xc9..0x12c = the RACEnCONTROL/NUMCONTROLS family per t333).

## S4 — STATE STORE VERBATIM (corrects S3's stride arithmetic) + MEASURED CENSUS
The STATE line is parsed by block 0x59021, which is the CONTINUATION of the
PARENT block (0x58f67 ends 0x5901c `call 0x30c20` then FALLS THROUGH): one
block parses PARENT then STATE for a window. VERBATIM 0x59021..0x59099:
  scan fmt 0x342b='%s %d' (abs 0x85fdb) -> [esp+0x3a0] = COUNT;
  loop 0x5905c: scan fmt 0x3431='%d' (abs 0x85fe1) -> [esp+0x378];
  eax=edi (winmgr base), ebx=[esp+0x376] sar 0x10 (the state id),
  edx=[ebp+0x41] (this window's HANDLE) -> call 0x57194;
  failure -> assert winmgr.cpp:0xe5d (string 0x85fe4).
fn 0x57194 VERBATIM geometry (dumped 0x57194..0x57281):
  asserts id in [0,0x20) (:0xb37) and handle < 0x400 (:0xb38);
  edx = ecx + (((id*9)*8 - id) * 2) = winmgr + id*142 = id*0x8e;
  count = WORD [edx+0x3068] (dword read at +0x3066, sar 0x10 takes high half);
  count==0 -> global [ecx+0x4226]++ ; [edx+0x3068]=1 ; [edx+0x306a]=handle;
  else scan t<0x20 for empty slot [edx+0x306a+4t]==0, store handle, inc count
  (:0xb5a on overflow). REMOVER fn 0x57284 mirrors it.
  (S3's 0x11c/0x238 arithmetic was WRONG; 0x8e is what the lea/add/shl chain
  computes and what the census found in saves.)
Pool strings read verbatim from work/ascend_restored.bin at 0x82bb0+rel:
0x3409 'LB', 0x340c '%s %s', 0x3412/0x3415 '%s', 0x3418 'NONE',
0x341d '..\winmgr.cpp', 0x342b '%s %d', 0x3431 '%d', 0x34f5 '%s %s'.

CENSUS scripts/r336d_state_census.py (exit 0), 196 needle-verified saves across
playcap save/ + dbg-t332/t299-leg/dbg-t331 dirs, truth = ON-DISK
extracted/ascend00/windows.txt, window HANDLE = byte @ record+0x41 (unique):
- STATE table located by exact-membership fingerprint: W = 0x2bc3e4 in 196/196
  saves (identical address in every save dir).
- 16/18 state ids: EXACT file-order handle list in 196/196 saves — including
  id 16 = the 20-window battle family verbatim (single-char windows 'W','S',
  'Z','I' included; an earlier 0/196 for id 16 was my name-length filter).
- id 1 APPENDED in 16 saves: file list is a strict PREFIX; runtime-created
  windows (EVENTWIN, Go^to^Planet, OK) joined group 1 via the same 0x57194 path.
- id 17 SUBSTITUTED in 22 saves: slots 8..10 hold 'Leave Orbit','Abandon',
  'Cancel' where the file says PLSQBUT0..2 (runtime reuse of registration slots).
- GLOBAL COUNT CHECKS: sum(counts, id 0..31) = 135 = file STATE token count;
  winmgr+0x4226 = 18 = number of distinct file STATE ids. (41.sav.)

=> STATE VALUE DISPOSITION CLOSED BY MEASUREMENT: the STATE ids are stored in
the GLOBAL winmgr per-id window-handle table winmgr + 0x3068/+0x306a + 0x8e*id,
fill order = windows.txt file order at load; the table is LIVE runtime state
(accepts runtime joins and slot reuse), NOT a window-record field. OQ-016
residue-(1) STATE sub-question CLOSED (stored, located, counts reproduce); the
row stays open on the mode-1 arming witness alone. NEXT question = who READS
winmgr+0x3066/0x3068/0x4226 (t337 reader walk).
KEYWORD->STORE MAP (t336 deliverable, consolidated from S1c/S2/S4):
  TYPE n            -> class creation 0x78b4c(class-literal, size, 2) + 0x2a4ec
                       alloc + 0x30c08 init; record base ebp = win+0x20.
  NAME              -> interner 0x1f95c path; win word +0x18 (0x57cdc/0x59534).
  PARENT / STATE    -> block 0x58f67->0x59021 (above): parent handle->win+0x63;
                       state ids -> GLOBAL table (0x57194).
  NUMCONTROLS family-> win+0xab control table (t333), poison -1 at 0x57d56.
  WINITEMS/TEXTITEM/SHAPEITEM -> win+0x6d stride-13 item array (t335).
  0xc9..0x12c block -> table 0x484f8 via 0x3031c single / 0x30350 loop.
  help slots        -> edi+0x3042/0x3062 zeroed (0x59356/0x59391).
  keyword string    -> scanned to [esp+0x334]/[esp+0x338] scratch; dispatch is
                       on the TYPE integer, never a string compare in-image.
