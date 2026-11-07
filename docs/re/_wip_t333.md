# _wip_t333 — ACTIVE SCREEN STATE WALK (zero capture; OQ-016 residue-(1) last named edge)

## S0. Setup
Sitting check NEGATIVE: 400 KB tail-seek of work/r1/playcap/live-timeline.jsonl ->
16 turn-lines, max turn 1086 == corpus (OOM law honoured). Production :9 alive and
untouched (ps: Xvfb 1461, timeout 136357, dosbox-x 136359). Tree clean at start.
Instrument: work/r331_disasm.txt (fresh whole-code objdump of
work/ascend_restored.bin, 139,026 insns, zero badbar) — NOT the t91 segmentation.

## S1. fn 0x31d58 VERBATIM (r331_disasm.txt lines 34372-34387, addrs 0x31d58..0x31de3)
Signature (all four args are registers, no stack args):
  eax = esi = WINDOW record ptr
  edx = edi = STATE ID, matched as `cmp di, WORD PTR [edx_state_table + i*14]` (0x31d84)
  ecx = ebp = destination buffer (14 B) OR 0
  ebx    = value stored when ecx == 0
Body:
  loop 0x31d71: n = [win+0xad] >> 16; if i >= n -> not-found exit
                else if WORD[[win+0xab] + i*14] == di -> hit
  0x31d93: if i >= n (i.e. fell out of the loop) -> `xor eax,eax; ret` = RETURN 0
  hit path: off = i*14 (0x31d97..0x31d9e: shl 3 / sub / add)
  0x31da0 test ebp,ebp:
    ecx != 0 -> `rep movs` copies the 14-byte STATE record to [ecx]; then
                 0x31dd4 `mov eax,0xffffffff` RETURN -1
    ecx == 0 -> 0x31dc5..0x31dd0: `mov edx,[esp]` (=the saved ebx) ;
                 `mov WORD PTR [eax+0xa],dx`  <-- THE +0xa STORE, into the
                 STATE RECORD (base = [win+0xab] + i*14), NOT into the window
                 record; RETURN -1
CONSEQUENCE (binding, corrects the task-text framing): +0xa is a field of the
14-byte PER-STATE record, and fn 0x31d58 is a *lookup-with-side-effect*: it is
the ONLY writer of state-record +0xa in this fn, reached only when the caller
passes ecx=0. It never reads a "current global state" datum — the compared state
id is the CALLER's edx. So the active-state question reduces to the 4 callers.

## S2. fn 0x31d58 caller census (whole-image grep of `call 0x31d58`, exhaustive)
Exactly FOUR call sites (disasm lines 34836, 34850, 82028, 82048):
  A. 0x32284  inside fn 0x32100 (the state-rect-click machine: fn 0x31f30, the
     sole runtime [win+0xb1] switcher, is called at 0x3221b twelve instructions
     earlier — same function per the t323 caller census). Args: eax=esi(win),
     edx=movsx(bx), ecx=0, ebx=edi. Guarded by `cmp ebx,0xffffffff; je` at
     0x32276 — i.e. the found-index path.
  B. 0x322b2  SAME fn 0x32100, the alternative path: loops cl = 0..[esi+0xaf]-1
     with edx = movsx(1<<cl) (0x322a2..0x322ad), ecx=0, ebx=edi.
  C. 0x58ac5  inside the windows.txt composition loader. Args verbatim:
     0x58ab0 `xor ebx,ebx`; 0x58ab2 `xor ecx,ecx`; 0x58ab9 `xor edx,edx`;
     0x58ac3 `mov eax,ebp` -> fn(win, state_id=0, dest=0, val=0) = CLEAR
     state-record(+0xa) for the record whose id == 0.
     Result test 0x58aca `test eax,eax; jne 0x5898e` -> on FOUND (-1) the loader
     jumps back to the per-window loop head (this window is done).
  D. 0x58b19  SAME loader, loop 0x58aff..0x58b3e:
     0x58ae6 `xor ecx,ecx`; 0x58ae8 `mov ax,ds:0x13b98` (GLOBAL state count);
     0x58af6 `test ax,ax; jle 0x57687` exit;
     per iteration: cl=[esp+0x3b8]; eax=1; `shl eax,cl`; ebx=1;
     edx=movsx(ax); ecx=0; eax=ebp -> fn(win, state_id = 1<<k, dest=0, val=1)
     for k = 0 .. ds:0x13b98-1; loop increments k, exits k >= ds:0x13b98.
   => STATE IDS ARE BITMASKS (1<<k), and the loader SETS state-record +0xa := 1
      for every bitmask-id present in THIS window's state table, and CLEARS +0xa
      for the id==0 record. Both are LOAD-TIME. The runtime writer is fn 0x32100
      only (callers A/B).
   [inferred] The +0xa flag therefore means "state is enabled for this window at
      load", NOT "this is the screen currently on" — the task's premise that the
      per-save set of +0xa-set windows "names the active state directly" is
      probably wrong; the OFFLINE CENSUS (S3) is what decides, since it measures
      whether the flag is ever state-SELECTIVE and whether it survives gameplay.

## S3. OFFLINE CENSUS RUN 1 + LAYOUT CONTRADICTION (scripts/r333_state_census.py, exit 0)
Ran over 332 saves (work/r1/playcap/save 20 + dbg-t332 run 20 + 22 bounded
t299-leg-* dirs). Headline numbers were NOT trustworthy: the [win+0xb1] histogram
peaks at 13398 = 0x3456 and 65535, which are the magic word 0x12345678's OWN byte
pair and an all-ones dword => the field reads landed on pointer halves.
Root cause, MEASURED on 41.sav (B=0x1bf4d8 via the r329 Factory needle, 1 hit)
raw record dump at member 0xfd2398 (NAME='COSMOSWnd'):
   +0xa0: 00 00 00 ff ff ff ff | 4c 7a 24 00 | ac 28 fd 00 | 74 35 fd 00 | f8 3a fd 00 | ...
   => u32@+0xa7 = 0x247a4c (class grid region, t313 law) CORRECT
      u32@+0xab = 0xfd28ac, u32@+0xaf = 0xfd3574, u32@+0xb3 = 0xfd3af8
      = THREE CONSECUTIVE POINTERS. u16@+0xaf = 13684 is NOT a record count.
   And member 0xfdbebc (NAME='BatControlWnd') holds +0xab=+0xad=+0xaf=+0xb1=0
   (t331's "state-table NULL" reproduces), while NEXTTURNCONT (0xfd62c8) has
   +0xab=0 with +0xb3 = the NEXT magic word => the following record starts at
   +0xb3, i.e. the runtime record is ~0xB4 bytes and +0xb3.. is NOT my field.
CONCLUSION (binding for any future state-field read): the magic-0x12345678 runtime
record and the structure fn 0x31d58 consumes DO NOT SHARE THE +0xab/+0xad/+0xb1
READING t323 derived statically. t323's offsets are correct FOR fn 0x31d58's
argument (verified verbatim this iteration, S1); applying them to the magic record
is a CATEGORY ERROR that produces exactly the garbage above. Do not re-run this
census shape without first pinning which record fn 0x31d58 is handed at runtime.
SECOND MEASUREMENT THAT SURVIVES (state-record +0xa semantics, real table):
member 0xfd5d84 (NAME='RACECONTROLS') region +0x30 holds a genuine 14-byte
state-record array: ids 1,2,4,8,16,32,64 (POWERS OF TWO = bitmasks, corroborating
loader caller D's `shl eax,cl` id construction at 0x58b0b), each 14 B =
{id u16, x0 u16, y0 u16, x1?, y1?, FLAGS u16@+0xa, SIZE u16@+0xc}:
   id=1  fA=5   id=2  fA=5   id=4 fA=5   id=8 fA=5
   id=16 fA=0   id=32 fA=0   id=64 fA=0
So +0xa is a per-state FLAGS word whose SET values are 5 = bit0|bit2 and whose
CLEAR value is 0, and the census-wide +0xa histogram {0:52.9%, 5:23.5%} plus four
garbage modes confirms: +0xa is a FLAGS field, NOT an "active screen state" marker.
=> THE TASK PREMISE ("the set of windows whose +0xa is set names the active state")
   IS REFUTED BY MEASUREMENT. +0xa is load-time state ENABLEMENT (loader D sets
   val=1 for id=1<<k; fn 0x31f30 manipulates bit1/bit2; bit0 comes from the file).

## S4. ADOPTION + CORRECTION OF S3: THE "LAYOUT CONTRADICTION" WAS A WRONG-FIELD
## READ, NOT A CATEGORY ERROR. (adopted an interrupted session's uncommitted
## _wip_t333.md S0-S3 + scripts/r333_state_census.py; this block supersedes S3's
## conclusion and re-opens its measurement)
S3 concluded the magic-0x12345678 record and fn 0x31d58's argument "do not share
the +0xab/+0xad/+0xb1 reading". That is REFUTED by the disassembly S1 re-read
verbatim, which pins the SAME object carrying BOTH the class table and the state
machinery: fn 0x32100 uses [esi+0x8/0xc/0x10/0x14] (rect), [esi+0x41], [esi+0x57],
[esi+0x63], [esi+0xa7] (CLASS TABLE, `call DWORD PTR [esi+0xa7 -> +0xc]` at
0x321bc/0x32235) AND [esi+0xab] (state table) AND [esi+0xb1] — one structure, no
room for two layouts.
THE ACTUAL BUG: r333_state_census.py:72-73 takes `cnt = u16@+0xaf` and
`cnt_hi = u32@+0xad >> 16` and requires them to agree. On little-endian those two
expressions are the SAME 16 bits read at different alignments only when the value
is a pointer; the fields are:
  +0xab u32 STATE TABLE PTR (fn 0x31d58 0x31d7e, fn 0x31e74 0x31e94, fn 0x31f30
        0x31f75/0x31f91, fn 0x32100 0x3224c — five independent verbatim reads)
  +0xad u16 RECORD COUNT (fn 0x31d58 `mov ebx,[esi+0xad]; sar ebx,0x10` at
        0x31d71..0x31d77 = read the dword, arithmetic-shift to the HIGH half)
  +0xaf u16 SINGLE-RECORD INDEX / alt count (fn 0x31e74 fast path 0x31e7c
        `[edi+0xaf]>>10`-style index; fn 0x32100 0x3228d/0x322bc uses it as a
        loop bound for the bitmask path — two different consumers, hence S3's
        "three consecutive pointers" is +0xab, +0xaf, +0xb3 each being a dword
        whose low half is a real value and whose high half is the NEXT field)
For COSMOSWnd 0xfd2398: u16@+0xab=0x28ac + u16@+0xad=0x00fd => the dword 0xfd28ac
IS a pointer INTO THE SAME REGION (0xfd2398+0x514) exactly as the t298
pointer-value law predicts, and the record count is 0xfd=253, NOT the 13684 S3
computed from the misaligned u16@+0xaf. The prior "magic word 13398=0x3456 /
65535 histogram" garbage traces to reading +0xb1 in windows whose count/index
fields were never validated.
CONSEQUENCE: the census shape is sound; the FIELD MAP was wrong. Measurement
re-opened as S5 with the verbatim map, plus a self-validating predicate the
previous run lacked: a state table is ACCEPTED only if its first records decode as
14-byte entries whose id WORD is a small bitmask (popcount<=4, id<64) AND the
window's class table (u32@+0xa7 -> member) is a real code-region pointer table.

## S4b. windows.txt STATE-LINE PAIR CENSUS (fresh parse of
## extracted/ascend00/windows.txt, 131 STATE lines, latin-1)
`STATE <a> <b>` value pairs, count-ordered:
  1 16 -> 20 | 1 17 -> 14 | 3 1 | 12 | 1 8 -> 9 | 1 1 -> 8 | 1 7 -> 8 | 1 0 -> 7
  | 1 3 -> 6 | 1 20 -> 5 | 1 13 -> 3 | 1 10 -> 2 | 1 14 -> 2 | 1 18 -> 2
  | 3 2 -> 2 | 1 6 -> 1 | 1 9 -> 1 | 1 12 -> 1 | 4 1 -> 1
So the SECOND number is the state id (0..20) and 16 is the largest single family
(20 windows, t332's battle-map set, name list re-derived identically:
BatControlWnd, BatListWnd, BatModeWnd, TOGGRID, BATROTLEFT, BATROTRIGHT,
BATZOOMIN, BATZOOMOUT, RECENTER, TOGELEV, ABANDON, My^Items, Other^Items, Repeat,
Pass, Auto, W, S, Z, I). t332's "19-window" count is off by one: MEASURED 20.

## S4c. RUNTIME STATE-WRITER CENSUS OF [win+0xb1] (whole-image, clean regex on
## work/r331_disasm.txt, 7 sites — supersedes t323's "14 sites, all classified"
## by naming every one with its instruction)
  0x31c79  mov WORD PTR [eax+0xb1],0xffff   constructor, "no state"
  0x31faf  mov WORD PTR [ecx+0xb1],si       fn 0x31f30 = THE SWITCHER
  0x33787  mov WORD PTR [eax+0xb1],0x0      constructor, state 0
  0x339a4  mov WORD PTR [esi+0xb1],ax       char-input state cycler (t323)
  0x33c73  mov WORD PTR [esi+0xb1],cx       constructor family
  0x33d1b  mov WORD PTR [eax+0xb1],0xf3     constructor, 243 (not a windows.txt id)
  0x364d2  mov WORD PTR [edx+0xb1],ax       writes a TABLE record, not a window
=> ZERO WRITERS OF A GLOBAL ACTIVE-STATE DATUM. Confirmed independently:
`grep -nE "mov (WORD|BYTE|...) PTR ds:0x13b98"` on the whole disasm returns
NOTHING — the windows.txt loader's loop bound ds:0x13b98 (0x58ae8, 0x58b26) has
NO WRITER IN THE IMAGE, so it is a load-time/file-derived constant, and the
"global active-screen-state id" the t332 amendment (3) pointed at DOES NOT EXIST
AS A MEMORY LOCATION. Active state is per-window [win+0xb1] only.
NOTE on the value at 0x13b98 in work/ascend_restored.bin: bytes
07 10 41 0f 01 84 a3 03 ... = u16 0x1007 — the low byte 7 is plausible as a
state-count and the high byte 0x10 is the adjacent field; consistent with the
same interleaved u16-pair layout as the window record. Not a state id.

## S4d. fn 0x31f30 VERBATIM (0x31f30..0x31fb9) — the switcher's exact semantics
fn(win eax, state_id edx):
  0x31f37 if si == [win+0xb1] -> RETURN (already in that state)
  0x31f44 if si >= [win+0xaf]  -> BOUNDS ASSERT (mov ebx,0x396; mov edx,0x183e;
                                  call 0x2a428)  <-- t331's setter-bounds law
  0x31f5e idx = [win+0xad as hi-half of dword @+0xa7... verbatim: mov edx,
          [ecx+0xaf]; sar edx,0x10] ; if idx != -1:
             and BYTE [[win+0xab] + idx*14 + 0xa], 0xfd   CLEAR bit1 of OLD rec
  0x31f80 if si != -1: rec = [win+0xab] + si*14 ; if WORD[rec+0xa] & 1 (PRESENT)
             -> or BYTE [rec+0xa], 0x2                    SET bit1 of NEW rec
  0x31faf mov WORD [win+0xb1], si
So bit0 = "state exists for this window" (windows.txt/FILE-authored, and the
loader at 0x58b19 sets val=1 for id=1<<k), bit1 = "state is CURRENT" (runtime,
fn 0x31f30 only). This CONFIRMS S3's +0xa semantics conclusion (flags, not an
active-screen marker) by a second, independent route: the runtime CURRENT bit is
bit1 of the per-state record and is maintained in lockstep with [win+0xb1].

## S5. THE CONTROL-TABLE DECODE (scripts/r333b_state_layout.py, exit 0, ZERO
## capture; 372 saves, 42,780 window records, 5,208 state/control records)
### S5a. RAW 14-BYTE RECORD DECODED BYTE-FOR-BYTE AGAINST windows.txt
RACECONTROLS member 0xfd5d84, table u32@+0xab=0xfd5db4 -> member 0xfd5e3c, count
u16@+0xaf=7, current u16@+0xb1=0xffff:
  rec[0] 01 00 | df 01 ef 01 | c1 01 d1 01 | 05 00 | 14 00
  windows.txt:429 `RACE1CONTROL   1 479 449 495 465 0 20`
  => +0x00 id=1   +0x02=0x1df=479   +0x04=0x1ef=495   +0x06=0x1c1=449
     +0x08=0x1d1=465   +0x0a flags=5   +0x0c size=0x14=20
  The file's five numbers 1,479,449,495,465 are id,x,y,x,y in COLUMN-MAJOR order
  in RAM (479,495 | 449,465 = x-pair then y-pair). size 20 = the file's 7th field.
  rec[1..6] ids are 2,4,8,16,32,64 = the RACEnCONTROL bitmasks VERBATIM
  (`RACE2CONTROL 2 ...` ... `RACE7CONTROL 64 ...`).
=> [win+0xab] IS THE PER-WINDOW CONTROL TABLE (NUMCONTROLS entries), NOT the
   windows.txt STATE list. fn 0x31d58 = "find control by bitmask id, write its
   +0xa flags"; fn 0x31e74 = rect-contains hit over controls; fn 0x31f30 = set
   [win+0xb1] = current control INDEX (asserts idx < [win+0xaf] = control count).
### S5b. MEASURED RARITY: ACROSS 372 SAVES ONLY RACECONTROLS HAS A DECODABLE
### CONTROL TABLE (7 records/save), and its flags are
   ids 1,2,4,8 -> +0xa=5 (bit0|bit2)   ids 16,32,64 -> +0xa=0
   i.e. EXACTLY THE FIRST FOUR RACES ENABLED — the control +0xa bit0 is
   ENABLEMENT, set by the loader loop 0x58aff..0x58b3e (`shl eax,cl`, val=1) for
   k < ds:0x13b98. This is the loader enabling one control per PLAYER-RACE slot.
   NEXTTURNCONT, BatControlWnd, BatModeWnd, COSMOSWnd, TOGLANES, TOGEMPIRE,
   STATUSWND, GIZLIST, RACELIST, LOADLIST ... = table u32 NULL in 372/372 saves
   (report [6]). BatModeWnd member 0xfdc924 measured +0xab=0, +0xaf=0, +0xb1=0.
### S5c. THE FALSE POSITIVE THE CENSUS CAUGHT: report [3] "RACECONTROLS|inert 372"
   is a sid==16 hit meaning RACE5CONTROL's bitmask, NOT the battle-map state 16.
   Any future "state 16 resident" claim must first prove the table is a control
   table by id-popcount/mask structure, else it is this same collision.
### S5d. [win+0xb1] IS AN INDEX, MEASURED: histogram over 42,780 records is
   dominated by 0 (14,392) and 13398=0x3456 (22,692 — the 0x12345678 magic's own
   byte pair where the reader lands past a short record) plus pointer-half modes.
   NEVER read [win+0xb1] as a state id. t332's "save axis holds [+0xb7]=0" style
   readings are unaffected (byte reads), but any earlier doc that called +0xb1 a
   "CURRENT STATE ID" (t323 S4 wording) is WRONG in meaning: it is the current
   CONTROL RECORD INDEX, and for windows with no controls it is 0 or 0xffff.

## S6. CONCLUSION (binding): THE t332 AMENDMENT-(3) EDGE IS NOT THE ACTIVE-STATE
## WRITER. There is no global active-screen-state datum in the image.
1. fn 0x31d58's ONLY store is 0x31dd0 `mov WORD PTR [eax+0xa],dx` into a CONTROL
   record (verbatim S1 + raw decode S5a). Its two loader callers pass id=0/val=0
   (clear) and id=1<<k/val=1 (enable per race slot). It cannot select a screen.
2. `grep -nE "mov (WORD|BYTE|...) PTR ds:0x13b98"` over the 139,026-insn r331
   disasm (which spans 0x14bb0..0x826a5, NOT 0x0..0x14bb0 — see S8a): NO writer,
   and S8a closes the low range with a fresh objdump. Cite S8a with S6. The loop bound ds:0x13b98 is written by no instruction in
   the image (data-segment rebasing law C5 applies to its file counterpart).
3. The seven writers of [win+0xb1] (S4c) are constructors, a char-input cycler,
   a table write, and fn 0x31f30 — and fn 0x31f30 bounds-asserts when
   idx >= [win+0xaf]. MEASURED: BatModeWnd and BatControlWnd have count=0 and
   table=NULL in 372/372 saves, so fn 0x31f30 CAN NEVER BE CALLED SUCCESSFULLY
   on them. The control machine is structurally incapable of naming them.
=> OUTCOME per assignment: (B)-class. The named edge is now fully characterised
   and is NOT an activator; residue (1) keeps its UNREACHABLE disposition, row
   stays OPEN strict-close, and the route text must point at the STATE-LINE
   PARSE SITE (payload string pool), not at fn 0x31d58 and not at a capture.

## S7. UNINFORMATIVE PROBE (recorded so nobody re-runs it): STATE-MASK SCAN
Swept every 123 windows.txt-named window record in 60.sav for the byte encodings
of mask = OR(1<<id) (u16 low, u16 high, u32). Result: 1-2 "hits" for EVERY
window, scattered over ~60 offsets each (e.g. COSMOSWnd u16hi 0x2082 reported at
0x9,0xa,0xd,0xe,0x12,...). A 2-byte pattern in a 0xc0-byte record full of small
ints matches by construction. EMPTY-SIGNAL, not evidence either way: the windows.txt
STATE list is NOT locatable by mask-value search in the window record. If it is
pinned at runtime it lives in a per-window bitfield table elsewhere (or as a
compiled visibility predicate), and finding it needs a different handle than
value-search. Do not re-run this shape.
ONE CLEAN SUB-MEASUREMENT FROM THE SAME RUN: BatControlWnd (member 0xfdbebc) and
BatModeWnd (member 0xfdc924) both show mask 0x8000 (bit 15) at +0xa0..+0xa6 region
as part of the constant dword pattern `00 00 00 ff ff ff ff` = the record's own
-1-filled header, NOT a state mask. Confirms S5b: no state list in these records.

## S8. FULL-IMAGE COVERAGE FIX + TWO SELF-CORRECTIONS (both measured)
(a) COVERAGE: work/r331_disasm.txt spans 0x14bb0..0x826a5 (140,824 addresses,
total inter-line gap 476 bytes, max gap 66 B) — it OMITS 0x0..0x14bb0. So the
S4c/S6 "no writer of ds:0x13b98 in the image" claim was range-limited. Fresh
objdump of the low range (objdump -D -b binary -mi386 -M addr32,intel
--start-address 0x0 --stop-address 0x14bb0 work/ascend_restored.bin, 32,385 lines):
9 references to 0x13b98, ZERO of them a store form. => THE NEGATIVE NOW COVERS
0x0..0x826a5, the whole code image. Claim stands on cited evidence.
(b) SELF-CORRECTION, THE LOADER CANNOT EXPLAIN THE MEASURED FLAGS, SO THE
ENABLEMENT READING IS ONLY PARTLY MINE. Caller D (0x58aff..0x58b3e) passes
ebx=1 and fn 0x31d58's store 0x31dd0 is a MOV, not an OR — so post-loader the
enabled ids hold flags EXACTLY 1, and ids 16/32/64 keep their file value 0.
Measured 5 = 1|4, and bit2 is set at RUNTIME by fn 0x32048 (0x320bf `and BYTE
[eax+0xa],0xfb` / 0x320c5 `or BYTE [eax+0xa],0x4`). So: bit0 = loader enablement
(COUNT-CAPPED), bit2 = fn 0x32048 runtime toggle, bit1 = fn 0x31f30 CURRENT.
Only 4 of the 7 RACECONTROLS controls carry bit0, which [inferred] means the
loader loop bound ds:0x13b98 == 4 at play time (k=0..3 => ids 1,2,4,8), not 7 —
i.e. enablement is per PLAYER SLOT, not per control. NOT MEASURED: the runtime
value of ds:0x13b98. Reading it as member 0x13b98+0x88 gives 7554=0x1d82, which
is garbage, and the same +0x88 probe on the t332 jump table (member 0x1d4b8c)
returns 0x1d5349/0x1d543d/0x1d55d1 instead of t332's 0x15ef9/0x15fed/0x16181 —
so the save-file-to-linear delta is NOT a constant 0x88 across save dirs; it must
be re-derived per save (r1_slot.base_of) before ANY fixed-address ds: read.
LAW: never read a ds:-segment global at a hard-coded member offset across save
dirs; validate the mapping with a known needle in the same save first.
NEXT-ITERATION HANDLE (found this iteration, unexploited): writers of [x+0xab]
are 47 image-wide; the two inside the windows.txt loader region are 0x57d56
`mov DWORD PTR [eax+0xab],0xffffffff` and 0x57e48 `mov DWORD PTR [edx+0xab],eax`
— the control-table ALLOCATE/ATTACH site, immediately upstream of the
composition loop 0x5898e..0x58b3e. That is where the STATE/NUMCONTROLS lines
become a table, and therefore the only remaining place the STATE-16 list could
acquire a runtime home.

## S9. FINAL DISPOSITION (t333)
Outcome (B)-class, strict-close: NOTHING closed. The assignment's premise (that
the +0xa set names the active screen state) is refuted by measurement, and the
edge t332 named (a global active-state writer) does not exist as a memory
location. Residue (1) keeps its OPEN status with SIX named unreachable legs; the
route text now points at the loader-side control-table site, not at fn 0x31d58.
Zero capture; production :9 (136357/136359, Xvfb 1461) untouched; game/ read-only
throughout (ascend00.cob grepped, never modified).
