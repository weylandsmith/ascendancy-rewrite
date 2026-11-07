# _wip_t334 — CONTROL-TABLE ATTACH SITE WALK (zero capture; OQ-016 residue-(1))

## S0. Setup
Sitting check NEGATIVE: 400 KB tail-seek of work/r1/playcap/live-timeline.jsonl ->
16 turn-lines, ALL turn 1086 == corpus max (OOM law honoured, never json-loaded).
Production :9 alive and untouched (ps: Xvfb 1461, timeout 136357, dosbox-x 136359).
Tree clean at start (HEAD 1daa17e = t333).
Instruments: work/r331_disasm.txt (whole-code objdump 0x0..0x826a5, 140,902 lines)
plus a FRESH region dump work/r334_disasm_57c00.txt
(objdump -D -b binary -m i386 --start-address=0x57c00 --stop-address=0x58000, 266
lines, rc=0) per the task's "re-dump to be safe" clause.

## S1. The attach sites live in ONE function: entry 0x575e4, frame 0x3bc
Function boundary evidence (r331_disasm.txt): 0x575e3 is the `ret` of the previous
fn; 0x575e4 falls through to `sub esp,0x3bc` at 0x575e9. The only in-image call of
0x575e4 is `call 0x575e4` at 0x575da (a tail call from the immediately preceding
fn); there is NO other `call 0x575...` into this body (whole-image grep of
`call +0x575*`: only 0x21545->0x57530, a different fn).
=> 0x57d56 and 0x57e48 are in the SAME parse function; the "allocate/attach pair"
is a guard-then-store on one stack-parsed value, not an allocator.

## S2. Both +0xab sites VERBATIM (fresh dump + r331 agree byte-for-byte)
ABORT branch (0x57d18..0x57d5d):
```
57d18: mov  eax,DWORD PTR [esp+0x3a6]
57d1f: sar  eax,0x10            ; high half of the parse status dword
57d22: cmp  eax,0x19            ; == 25
57d25: jne  0x57d60             ; not 25 -> skip the abort entirely
57d27: lea  eax,[esp+0x378]     ; out-param (the parsed value)
57d2e: push eax
57d2f: lea  eax,[esp+0x338]     ; parse cursor ctx (0x3bc-frame local)
57d36: push eax
57d37: push 0x85c69             ; keyword/string id A
57d3c: push esi                 ; source text pointer
57d3d: call 0x77fe1             ; THE PARSE HELPER (4-arg)
57d45: cmp  DWORD PTR [esp+0x378],0x0
57d4d: je   0x57d60             ; parsed 0 -> no write
57d4f: mov  eax,DWORD PTR [esp+0x37c]     ; eax = WINDOW record ptr
57d56: mov  DWORD PTR [eax+0xab],0xffffffff   ; POISON the table ptr
```
ATTACH branch (0x57e14..0x57e48):
```
57e14: mov  eax,DWORD PTR [esp+0x3a6]
57e1b: sar  eax,0x10
57e1e: cmp  eax,0xf             ; == 15
57e21: jne  0x57e4e
57e23: lea  eax,[esp+0x378]  ; out-param
       ... push 0x85c8d ... call 0x77fe1     ; keyword/string id B
57e41: mov  eax,DWORD PTR [esp+0x378]        ; the PARSED value
57e48: mov  DWORD PTR [edx+0xab],eax         ; edx = window ptr -> ATTACH
```
So the SAME field [win+0xab] is (a) poisoned to -1 under one keyword when the
status high-half is 25, and (b) loaded from a text-parsed value under another
keyword when the status high-half is 15.

## S3. THE PARSER'S IDENTITY AND ARGUMENT DOMAIN (measured, kills a trap)
fn 0x575e4 is the WINMGR windows.txt parser: its string pool (read verbatim out
of work/ascend_restored.bin 0x85b82..0x85d3c) contains `windows.txt` (0x85bac),
`WMGR MAPRACES`, `%s bad parent`, `..\winmgr.cpp` x8, `FLIC`, `NONE`, and the
scan templates `%s %d`, `%s %s`, `%d`, `%s %d %d %d`.
ENTRY: the only in-image call of 0x575e4 is 0x575da in the immediately preceding
fn, which is the winmgr INIT: it builds a 0x100-byte byte table at [edx] (loop
0x575b2..0x575bb), calls 0x5b587(eax=0x80, edx=0x2ffc) and stores the result to
[esi+0x3006], sets [esi+0x3012]/[esi+0x3022], then `mov eax,esi; call 0x575e4`.
ARGUMENT DOMAIN — the third push is NOT an in-image pointer for the small
constants: 0x30b3/0x30c5/... ARE OFFSETS INTO THE RESIDENT windows.txt TEXT
(windows.txt is 42,478 B; ascend_restored.bin at 0x30b3 is CODE bytes
`91 0e 02 94 12 07`, so the constant cannot address the image). Resolving each
referenced offset against extracted/ascend00/windows.txt:
  0x3008 -> mid `SOUNDCHANNEL`/`SENDMESSAGE` region
  0x30b3 -> the TEXTITEM value token ` Species`
  0x30c5/0x30cb/0x30d1 -> `TYPE` keyword region
  0x30d7 -> `NAME` keyword region
  0x30e3/0x30e9/0x30ef -> the NAME value `DIFFICULTYMORE`
  0x30f5 -> `PARENT` keyword
  0x3101 -> the PARENT value `NEWGAMEWND`
  0x32f9/0x32ff/0x3305/0x330b -> the control-record geometry region (`Y1`,
     `SHAPEFRAME`) used by the composition loop 0x5898e..0x58b3e
The big constants (0x85c69, 0x85c8d, 0x85eb2, 0x85ebe = `%s %d` / `%d`) ARE
in-image addresses. So 0x77fe1(text_ptr, template, cursor_ctx, out) takes either
an in-image format string or a windows.txt-resident template position.
0x77fe1 VERBATIM (r331 lines 124758-124766) is a 6-instruction wrapper:
`push ebx; push edx; sub esp,4; lea ebx,[esp+0x18]; mov eax,[esp+0x10];
 mov edx,[esp+0x14]; mov [esp],ebx; mov ebx,esp; call 0x77fba; add esp,4; pop
 edx; pop ebx; ret` -> the real scanner is 0x77fba.

## S4. THE COMPOSITION LOOP IS THE RACEnCONTROL ENABLEMENT PATH (not a STATE path)
0x5898e..0x58b3e sits INSIDE fn 0x575e4 (same 0x3bc frame). Verbatim key sites:
  0x589c3 / 0x589e8 / 0x58a0d / 0x58a32 / 0x58a57 / 0x58a7c / 0x58aa1
     call 0x77fe1  — parses the control-record fields (`%d` templates 0x85eb2,
     0x85ebe), staging them at [esp+0x368..0x374] (the 14-byte record on stack)
  0x58ac5 call 0x31d58 (ecx=0)  — per-parsed-id flag write; on failure
     0x58ad2 `mov ebx,0xdc9; mov edx,0x85ec1(=..\winmgr.cpp); call 0x2a438`
     = the vendor assert at winmgr.cpp line 0xdc9 (3529)
  0x58ae6..0x58b3e — the SECOND loop: `mov ax,ds:0x13b98` (0x58ae8) as the bound,
     `mov cl,[esp+0x3b8]; mov eax,1; shl eax,cl; movsx edx,ax` (0x58aff..0x58b12)
     => val = 1<<i, `call 0x31d58` with ecx=0, loop while i < WORD ds:0x13b98.
     THIS is t333 caller D and it is the ONLY place ds:0x13b98 gates 0x31d58.
NO `imul *,0xe` (14) exists anywhere in the parse function (grep of the whole
0x575e4 body) — the 14-byte stride is NOT computed by the parser; the only
allocator-shaped calls are 0x78b4c (e.g. 0x58b4f: ebx=0x331f, eax=0x504e, edx=2).

## S5. THE STATE LINE HAS A PARSE-TIME CONSUMER: A PER-WINDOW ARRAY AT win+0x6d,
## STRIDE 13, WRITTEN BY THE LOOP 0x57f3e..0x57ff5 (VERBATIM, kills the
## "parse-time-only, no runtime home" hypothesis in its stated form)
0x57ef6 push 0x3107-region kw, call 0x57efe -> [esp+0x378] = parsed STATE COUNT
(0x57f09 stores it to [esp+0x3ac] as the loop bound; 0x57f1e `test ax,ax; jle
0x58062` = skip when count<=0). Then:
```
57f06: lea ecx,[edx+0x6d]        ; edx = window record ptr (loaded 0x57e02 from
                                  ;   [esp+0x37c]; 0x77fe1's push/pop edx preserves
                                  ;   it across every parse call — that is WHY the
                                  ;   wrapper saves edx)
57f27: lea eax,[ecx+0xb]  -> [esp+0x394]   ; per-record cursor (win+0x78 + i*13)
57f2a: lea ebp,[ecx+0x9]                    ; win+0x76 + i*13
loop 57f3e: call 0x77fe1 (kw 0x3107)        ; parse the STATE id at the cursor
57f63: test edx,edx / jne 0x57ffa           ; id != 0 -> branch B
  branch A (id==0): 57f8a kw 0x310d, call 0x77fe1 (parses the NAME token),
     0x57f9c call 0x315c4 -> 0x57fa1 `mov DWORD PTR [ecx+0x1],eax`  ; entry u32
  branch B (id==1): 0x58018 kw 0x3119, call 0x77fe1, 0x58035 eax=0x9f10c,
     call 0x1fe20, 0x5803f `and eax,0xffff` -> 0x58044 `mov [ecx+0x1],eax`
advance: 0x57fb9..0x57fd8 add 0xd to ebp/ebx/eax; 0x57fcd `add ecx,0xd`;
     0x57ff0 cmp dx,bx / jge exit / 0x57ff5 jmp 0x57f3e
```
=> THE STATE LIST BECOMES RUNTIME MEMORY: base = win+0x6d, stride 13, entry u32
   at +0x1 (a resolved handle from 0x315c4 / 0x1fe20), loop count = the parsed
   STATE-line count. This is DISTINCT from [win+0xab] (control table, stride 14,
   t333) — adjacent fields, different structures. t333's STATE-line "no runtime
   home" claim must be corrected to: no home in the CONTROL structure, and no
   global datum; the home is the per-window win+0x6d array.
0x77fe1/0x77fba VERBATIM: wrapper chain into 0x7a1f7(0x77f64, 0x63402, fmt, ...)
— 0x77f64 is the %d/line handler: `mov edx,eax; mov eax,[eax+0x8]` (fmt+8 = cursor
struct: [0] char ptr, [4] remaining, [0xc] flags; treats *ptr==0x0d or 0x1a as
EOL/EOF and calls 0x7b2be to advance the line).

## S6. THE TWO [win+0xab] SITES ARE REACHABLE ONLY BY FALLTHROUGH (measured)
Whole-body control-flow scan (0x575e4..0x597ff, every jmp/jcc target): NO branch
lands on 0x57d18 (before poison) or 0x57e14 (before attach) — both blocks are
entered by fallthrough from the preceding field store (0x57d11 poison [+0x3d],
0x57e10 store [+0x1e]). The only edges into 0x57c00..0x57e5f are 0x57bfc,
0x57c5b, 0x57c61, 0x57c6e, 0x57ca3, 0x57cb9, 0x57ce0, and the two self-skips
0x57d25->0x57d60 / 0x57e21->0x57e4e. So the poison/attach pair is SEQUENTIAL
parse code governed solely by the [esp+0x3a6] status word — and NOTHING in the
body writes [esp+0x3a6] (grep of all 2328 insns: only the two reads at 0x57d18
and 0x57e14). The status is left there by the scanner (caller-inherited stack
slot reused by 0x7a1f7's varargs machinery), values 25 vs 15 = scan outcome.

## S7. SELF-CORRECTION: THE PUSHED CONSTANTS ARE FORMAT STRINGS IN TWO SEGMENTS,
## NOT windows.txt OFFSETS (the S3 "text offset" reading is REFUTED by a save probe)
Probe (scripts path, save 41.sav, needle-verified B=0x1bf4d8, member law
addr = B + 0x82bb0 + X):
```
ds:0x03008 -> b'%s %d\x00..\\winmgr.cpp\x00%s %d\x00GW\x00RW\x00RSW...'
ds:0x030b3 -> b'%s %d\x00%s %d\x00%s %d...'          (run of fmt strings)
ds:0x0310d -> b'%s %d %d %d\x00%s %d %d %d\x00..\\winmgr.cpp\x00FL'
ds:0x85c6f -> zeros (NOT where the code-image rodata lives in RAM under this law)
```
and work/ascend_restored.bin at file offsets 0x85c69/0x85c8d/0x85eb2/0x85ebe =
`%s %d` / `%s %d` / `%d` / `%d` (read verbatim this iteration). So BOTH constant
families passed as the 3rd arg of 0x77fe1 are SCAN FORMAT STRINGS — the small
(0x3000-range) ones live in the loaded image's DATA segment (readable at
B+0x82bb0+X), the big (0x85000-range) ones are code-image rodata addresses. The
windows.txt-offset coincidences in S3 (readable ASCII at 0x30b3 etc.) were that:
coincidences. The keyword literals themselves (PARENT/STATE/NUMCONTROLS) are
matched by the scanner machinery (0x7a1f7 + handler 0x77f64 + table 0x63402),
consistent with t333's finding that they are absent from the code image.

## S8. THE STATE-LINE PARSE LOOP VERBATIM (0x57ee6..0x57ff5 + 0x5804c) — RUNTIME
## HOME IS win+0x6d, INLINE, STRIDE 13, COUNT = THE PARSED STATE COUNT
```
57ef6: push fmt(0x3101); call 0x77fe1        ; parses the STATE line's COUNT ->
                                            ;   [esp+0x378]; 0x57f09 copies it to
                                            ;   [esp+0x3ac] as the loop bound
57f1e: test ax,ax / jle 0x58062              ; count<=0 -> NO array work at all
57f06: lea ecx,[edx+0x6d]                    ; edx = window record ptr [esp+0x37c]
loop 57f3e: call 0x77fe1 (fmt 0x3107 '%s %d'); -> [esp+0x378] = entry token
57f63: test edx,edx
  id==0: 57f8d call (fmt 0x310d '%s %d %d %d'), 0x57f9c call 0x315c4,
         0x57fa1 mov DWORD PTR [ecx+0x1],eax    ; u32 handle
         0x57fb4 call 0x31690 (win ptr in eax [esp+0x37c], edx=cursor)
  id==1: 57f8a `mov BYTE PTR [ecx],0x0` / 0x58023 `mov BYTE PTR [ecx],0x1`
         58026 call (fmt 0x3119), 0x58035 eax=0x9f10c, call 0x1fe20,
         0x5803f and eax,0xffff -> 0x58044 mov [ecx+0x1],eax   ; u16 INDEX
  else : 0x5804c `mov ebx,0xcd6; mov edx,0x3125; call 0x2a428` = vendor ASSERT
advance: `add ecx,0xd` (0x57fcd), bound cmp 0x57ff0, `jmp 0x57f3e`
```
0x315c4 VERBATIM head: null-check assert @0x226 then a walk (esi=arg);
0x31690 head: `mov eax,[eax+0x9f]; sar 0x10; cmp 4` — asserts window-type >= 4;
0x1fe20 head: walks [edi+0x7d0] stride 0x32, count [edi+0x2ede]>>0x10, returns an
index (caller masks 0xffff).
CONSEQUENCE: residue-(1)'s "STATE consumed purely at parse time, no runtime
structure" is NOT the case: the STATE line WRITES a per-window inline array at
win+0x6d (up to 4 slots x 13 B: byte tag + u32 handle/index), and the values are
RESOLVED (name->handle via 0x315c4, or an index via 0x1fe20). What it is NOT,
equally measured, is a CONTROL table ([win+0xab] stride 14, t333) or a global
datum (t333: zero writers of a global state word).

## S9. OFFLINE CENSUS (scripts/r334_state_array.py, RC=0, 196 needle-verified
## saves, turns 1086..1087) — ONE HARD NUMBER + ONE MODEL FAILURE
(a) ds:0x13b98 = WORD 4 in 196/196 saves (needle: DAT_00012e10 turn 1086/1087,
    115 magic+NAME records; mapping law r1_slot addr=B+0x82bb0+X — an earlier run
    of mine used B+X and rejected 196/196, MY error, corrected in the script).
    This MEASURES t333's [inferred] claim: the caller-D enablement loop
    0x58aff..0x58b3e is bounded by 4 = the player count (relation n=4 in every
    timeline row) — enablement ids 1,2,4,8 set / 16,32,64 clear is now cited, not
    inferred.
(b) THE win+0x6d FLAG-ARRAY MODEL FAILS THE CROSS-CHECK: 17,836/18,816 window
    records read (0,0,0,0) at +0x6d; the nonzero ones are adjacent-text garbage
    (INTRO flags=(0,0,255,208)) EXCEPT two clean families RESEARCH/FLEET-like
    flags=(0,1,0,0) n=784 and (1,0,0,0) n=588 whose "handles" are small ints
    (0x75, 0x2e) not pointers; resident-text agreement text_count==set_slots is
    708/708 but ONLY on text=0/set=0 (19 zero-STATE windows x saves) — zero
    positive cases matched. Handle->magic delta scan: empty for every K<0x200.
    So the S8 loop's slots are NOT what these production-save records hold at
    +0x6d: either the array is consumed-and-cleared after window construction, or
    [esp+0x37c] at parse time is a BUILDER record distinct from the saved runtime
    record (0x31690's `type>=4` assert hints the parse-time record is a
    different/later object). UNRESOLVED — do not re-run this census unchanged.

## S10. DISPOSITION (t334)
CLOSED by measurement: nothing (strict-close).
MOVED FORWARD: OQ-016 residue-(1) — (i) ds:0x13b98=4 CITED; (ii) the STATE-line
consumer is LOCATED (0x57ee6..0x57ff5 -> win+0x6d stride 13, resolvers 0x315c4/
0x1fe20/0x31690) — the edge is no longer "no mechanism"; (iii) the mechanism does
NOT reach production saves as modelled, so the remaining question is SHARPENED to:
is the builder record (0x575e4's [esp+0x37c]) the same object the saves snapshot,
and what consumes win+0x6d slots at runtime? Next-session handle: find READERS of
[win+0x6d] outside 0x575e4 (whole-image scan for +0x6d with a window-record base)
and the builder-vs-runtime identity via 0x31690's callee census.

## S11. fn 0x31690 FULLY DECODED — IT IS THE STATE-ARRAY COMPACTING WRITER, AND
## [win+0xa1] IS ITS SLOT COUNTER (verbatim, r331 lines 33761-33778)
```
31694: mov ebx,eax            ; ebx = window record ptr
31696: mov esi,edx            ; esi = source cursor
31698: mov eax,[eax+0x9f]; sar 0x10; cmp eax,4; jl ok
316a6: (assert winmgr.cpp:0x241 when type < 4)
316be: mov cx,WORD [ebx+0xa1]        ; n = slot counter
316c5..316d5: eax = 13*n  (lea [edx*4]; sub; shl 2; add); inc ecx;
316d7: mov WORD [ebx+0xa1],cx        ; counter++
316de: lea edi,[ebx+eax+0x6d]        ; dst = win + 0x6d + 13n
316e7: movs DWORD x3 + movs BYTE     ; copy EXACTLY 13 BYTES from [esi]
```
Callers of 0x31690 image-wide: EXACTLY ONE, 0x57fb4 (the STATE parse loop, id==0
branch). Whole-image operand census of +0x6d: ONLY 0x57f06 (parse fn) and 0x316de
(this fn); a fresh low-range objdump 0x0..0x14bb0 shows NO +0x6d operand at all
(six -0x6d hits are `add -0x6d(%eax),%r8` code bytes) — but SEE S13: the array
IS read, via `add ebp,0x6d` + `add ebp,0xd` pointer arithmetic in fn 0x31384
(no literal +0x6d operand there, which is why the operand census alone said
"write-only"). The honest disposition: the STATE line's runtime home IS a real
structure (win+0x6d, stride 13, counter [win+0xa1]) — correcting t333 — and it
HAS an in-image consumer (S13), but production saves measure the counter ZERO
on every battle window, so residue-(1)'s core claim (no runtime STATE SELECTION
in play) survives on the census of [win+0xa1], not on write-only-ness.
[win+0xa1] CENSUS (6 saves, 690 records, needle-verified): {0:600, 1:30, 2:60};
agreement(text STATE count, a1): (0,0)=84, (1,0)=420, (1,1)=30, (1,2)=60,
(3,0)=84, (4,0)=6 — the counter is NONZERO only for the 15 text windows whose
STATE entries take the id==0 branch (INTRO/PLAYTUTORIAL/FRESHGAME/RESUME/LOAD/
SAVE/EXITTODOS/RACES family, a1=1 or 2); ROTRIGHT/ROTLEFT/ROTUP/ROTDOWN
(STATE 3 1 7 13) measure a1=0 — the id!=0 (index) path does not compact.

## S12. THE REAL STATE-LINE RUNTIME HOME IS A GLOBAL ARRAY ds:0x6fda8, COUNT
## ds:0x701a6 (fn 0x315c4/0x31660 verbatim; S11's win+0x6d reading CORRECTED)
Reading fn 0x31690's neighbours verbatim (r331 lines 33690-33741):
```
315ed: mov eax,ds:0x701a6            ; count
31612: mov edi,ds:0x701a6
3161e: add edi,0x6fda8               ; GLOBAL ARRAY base + 13*count-ish walk
31665: mov eax,ds:0x701a6 ; sar 0x10 ; cmp ecx,eax ; jl ok   (assert winmgr.cpp
3167b: -> 0x2a428, id 0x237 line 0x1817)                     ; -ish bounds check)
31682: mov eax,0x6fda8 ; add eax,ecx                          ; slot ptr
```
CORRECTION: the 13-byte record 0x31690 copies does NOT land win+0x6d — `lea
edi,[ebx+eax+0x6d]` was misread; the STRIDE-13 RECORDS live in the GLOBAL array
at ds:0x6fda8 (index ds:0x701a6), and win+0x6d is only the parse-scratch cursor
(`add ebp,0x6d` @0x313c0, fn 0x30fb8 — a PAINT/draw fn: calls 0x5e940 x?, reads
[win+0x39]/[+0x3d]/[+0x41]==ds:0x7d35e active-window ptr). The STATE-array
accessors 0x315c4..0x31682 are the ONLY code touching ds:0x6fda8/0x701a6
(image-wide grep: 6 sites, all in 0x315ed..0x31682). fn 0x31384 (the other
stride-13 walker, callers 0x3117f/0x3135a inside fn 0x30fb8) iterates the
win+0x6d scratch array and BRANCHES ON slot byte0 (0 -> text branch 0x7d3aa
format, 1 -> id-resolve via fn 0x1fc34 [eax+0x2eec], >1 -> assert winmgr.cpp
0x1df/0x17cc) — i.e. the scratch array IS consumed, by the paint fn.

## S13. THE CONSUMER IS fn 0x31384 (called from paint fn 0x30fb8) — S12's
## "GLOBAL ARRAY ds:0x6fda8" CLAIM IS REFUTED BY ITS OWN BODY (STRING INTERNER)
fn 0x315c4 verbatim (r331 lines from grep '^ *315c4:'): `repnz scas` over [esi]
-> strlen; bounds `count+strlen < 0x400` (assert winmgr.cpp:0x229); store byte
at `ds:0x6fda8 + (ds:0x701a6>>16)`; if byte==0 also bumps WORD ds:0x701a8 by
strlen+1. That is a NAME->HANDLE STRING INTERNER writing a 0x400-byte string
pool — NOT a stride-13 record array. S12 OVERREACHED; withdrawn. The stride-13
records stay where S11 put them: win+0x6d, counter [win+0xa1].
fn 0x31384 (the stride-13 WALKER; callers EXACTLY 2: 0x3117f, 0x3135a, both
inside fn 0x30fb8) verbatim: `mov bx,[eax+0xa1]; test bx,bx; jle done` then per
slot `ebp = win+0x6d + 13*i` and a 3-way branch on BYTE[ebp]:
  0 -> format `0x7d3aa` (13-byte movs copy of the slot into a temp at 0x7d3aa,
       then varargs fn 0x2fb38 with tag 0xf3/0xff — TEXT path),
  1 -> `mov dx,[ebp+1]` handle -> fn 0x1fc34(eax=arg?, edx=0x9f10c format) ->
       fn 0x5caac — HANDLE-RESOLVE path (0x1fc34 reads [eax+0x2eec], asserts
       winmgr.cpp 0xa2 when zero),
  >1 -> assert winmgr.cpp:0x1df (0x3146c).
Loop tail: `add ebp,0xd; inc ecx; cmp cx,[edx+0xa1]; jl loop`.
fn 0x30fb8 ITSELF: eax=msg-type-in (cmp 3/cmp 2 branches), reads [win+0x39]
(early-out when 0), [win+0x3d], compares [win+0x41] to ds:0x7d35e (the
active-window pointer — same datum t331/t332 banked), calls the draw fn
0x5bf71 with rects from [win+0x8/0xc/0x10/0x14]. NO LE 32-bit POINTER to
0x30fb8 exists anywhere in work/ascend_restored.bin (struct.pack census: 0
hits; control fn 0x1aef8 has 1 @0x884a0, fn 0x156d4 has 1 @0x88408) and no
direct call — 0x30fb8 is REACHABLE ONLY THROUGH A TABLE OUTSIDE THE IMAGE
(class table in a data file, or the low segments r331 does not cover).
DISPOSITION: the STATE slots ARE consumed in-image (paint-time text/handle
rendering of the window's STATE list), never as a screen selector; the selector
question now reduces to: WHO DISPATCHES TO fn 0x30fb8 (outside-image table) and
DOES THE PAINT PATH GATE CONTROL BEHAVIOUR. The battle windows' [win+0xa1]=0
(690-record census) means the paint loop is a NO-OP for them regardless.
