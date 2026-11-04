# t296 WIP — ship-selection choreography, STATIC-FIRST (OQ-016 r1 + OQ-019 r3 gate)

Session start 2026-11-04 ~13:05 EST. Fresh session; resumed from STATE.md alone.

## Pre-flight (verified this session)
- git clean, main, HEAD = t295 commit b4b0e61.
- Production ring `work/r1/playcap/live-timeline.jsonl`: last rows turn 1086,
  wall 13:04-13:05, file 51.sav, sel=0, rank=65535, in_game True. Idle-daemon
  echoes at the PINNED turn => NO new sitting since the last iteration =>
  r1_t85g_sitting.py NOT required. (Read via tail-BYTES only; file is 7.99 GB.)
- GhidraMCP headless brought up (`scripts/ghidra_headless_up.sh` -> healthy
  7.0.0-headless) but `program_loaded: false` and `list_instances` shows 0 open
  programs, so the decompiler path used this session is the ON-DISK full-image
  disasm `work/t91_code_disasm.txt` (objdump of `work/ascend_restored.bin`).
  FILE-OFFSET IDENTITY VERIFIED this session: sig `89 15 08 35 04 00` sits at
  0x55bcc in BOTH ascend_payload.bin and ascend_restored.bin, and both are
  0x8cc83 bytes => disasm addresses == payload file offsets == image addresses.
- TOOL TRAP (new, bank): `scripts/r290_disasm.py` prints ONLY its header line
  on this host and exits 0. Cause: GNU objdump 2.44 emits NOTHING for
  `-b binary -d` (no `.text` section); it needs `-D`. Confirmed:
  `objdump -D -b binary -m i386 -M intel` disassembles, plain `-d` prints zero
  lines with exit 0. Same silent-zero shape as the t283 `--start-address` trap.
  Workaround used all session: grep the pre-generated t91 dump.
- Ledger at start: 16 closed / 3 open (OQ-005, OQ-016, OQ-019).

## S1. The two selection globals, with their ONLY writers (MEASURED)
Full-image byte-pattern census (`work/ascend_payload.bin`, re.escape'd
little-endian dwords) — these are the complete writer sets, image-wide:

`ds:0x43504` = SELECTED OBJECT POINTER. Writers (`a3 04 35 04 00` x5,
`89 15/2d` x2):
  - 0x28ec2, 0x28ef6 — cosmos star-click handler FUN_00028e70 (ships.md S23
    L9). 0x28ec2 leg verbatim: gate `[esi+0xbb]==0` then `cmp BYTE[[eax]+0x4]`,
    `[esi+0x582]==0`, `sar ds:0x7e582,0x10 == 1`, THEN
    `dl=ds:0x6774; bl=[star+0x17]; test bl,dl; je (no-op)` — the t194 viewer
    mask — then `mov ds:0x43504,eax`. 0x28ef6 leg = the `ds:0x7e582>>16 == 0xd`
    variant, checks `[star+0x16]` (lane-follow) and posts 0xfd8.
  - 0x36b01 — diplomacy row select (`[ebx+0x13000]`, stride-0x1ee diplo table
    at 0x12e16, viewer `ds:0x7458e`).
  - 0x52003 — `mov eax,[esi+0x59]` : select a SHIP's ORDER TARGET.
  - 0x55c52 — `mov ds:0x43504,ebp` where `ebp = [ship+0x59]` of a ship whose
    `[ship+0x58]` order kind == 4 (case at 0x55c17; else assert 0x2a428
    ebx=0x69d edx=0x2daa).
  - 0x55d35 — `mov ds:0x43504,eax` under gate `[esp+0x8]==1`.

`ds:0x43508` = ORDER-DESTINATION PUBLICATION. Writers
(`a3 08 35 04 00` x5 + `89 15` x1): 0x1b5e6, 0x1baa7, 0x51a8e, 0x51fc2,
0x55bbd, 0x55bcc. Its known CONSUMER is the command executor 0x3ca60
(t107 banked): `ship+0x58 := 2 ; ship+0x59 := [ds:0x43508] ; WORD
[edi+0xb0] := 0xffff`.
218 total dword references to 0x43508 image-wide (dense cluster 0x3a8a0..
0x3e4ee = the command/AI-order module family), 76 to 0x43504.

## S2. BatModeWnd message handler = 0x1aef8 (windows.txt + dispatch verbatim)
windows.txt VERBATIM: `TYPE 4 / NAME BatModeWnd / PARENT NONE / STATE 1 16 /
X0 7 Y0 7 X1 465 Y1 472 / BACKGROUNDCOLOR 0 / CURSORSHAPE 2 / HELPINDEX
batmode`. Related: `BatControlWnd TYPE 19` (rect 0,0-0,0 — runtime-sized),
`BatListWnd TYPE 10 PARENT BatControlWnd rect 474,142-632,394 SHAPEFRAME 7`,
`SHAPEFILE DATA\16BATTLE.SHP` (STATENUMBER 16 entry).
r1-savestate.md already banked 0x1aef8 as one of the five batmode/batcon E1
functions (0x14bc0, 0x156d4, 0x1aef8, 0x1b91c, 0x1ce1c) — corroborates the
attribution independently.

Dispatch head 0x1aef8 verbatim:
```
1aefe mov ebp,eax        ; EAX = window object
1af00 mov esi,edx        ; EDX = MESSAGE ID
1af02 mov [esp+0x10],ebx ; EBX = param (x / code)
1af06 mov edi,ecx        ; ECX = param (y)
1af0a cmp dx,0x3a ; jb 0x1b82b ; jbe 0x1b513
1af1a cmp dx,0x4c ; jb 0x1b7ed ; jbe 0x1b620
1af2a cmp dx,0x52 ; jb 0x1b7cd ; jbe 0x1b66e
1af3a cmp dx,0x53      ; jbe 0x1b684
1af44 cmp dx,0x54      ; je  0x1b738
1af4e (default) -> call 0x336b4 generic
```
MESSAGE TABLE DERIVED (each target reached iff the id matches — every edge
traced, no guessing):
| msg | handler | meaning (from the body) |
|---|---|---|
| 3  | 0x1afe1 | key-ish switch on ecx (0xc zoom-in float, 0xd zoom-out float on ds:0x9f108, 0x1c/0x39 -> 0x1af65 clears [win+0x5036]) |
| 4  | 0x1b070 | **LEFT CLICK** in-window: bounds-check `ebx in [win+0x8..0x10]`, `edi in [win+0xc..0x14]`, then route on selection state |
| 5  | 0x1b017 | window ACTIVATE: `call 0x56d1c(0x7a35c, edx=0x82fa7)` -> `[win+0xab] = <bat object>`, relay 0x3a, `call 0x1d268`, generic 0x336b4, `[win+0x4f2f]=0` |
| 0x3a..0x4b | 0x1b513 | overlay-flag handling: bits of `[win+0x4f2f]` (1/2 -> 0x1ca00 rotate +-2, 4/8 -> 0x1ce68 zoom +-10) |
| 0x4c | 0x1b578 | clear overlay bit, repaint |
| 0x4d,0x4e,0x4f,0x51 | 0x1b7cd -> 0x1b7dd | **`mov BYTE PTR [win+0xb7],0x1` = ARM ORDER MODE** |
| 0x50 | 0x1b7cd -> 0x1b7d7 -> 0x1b5ba | **PUBLISH ORDER TARGET** (see S4) |
| 0x52 | 0x1b66e | **CLICK-ON-HIT**: copies the 5-byte pending-hit payload and resolves the clip |
| 0x53 | 0x1b684 | **SELECTION** (see S3) |
| 0x54 | 0x1b738 | reset: `call 0x1be60`, `0x5669c(0x7a35c, ctx+0x41, ebx=4, ecx=8, edx=0, push 0)` |
NOTE: msg 0x52 (0x1b66e) and 0x53 (0x1b684) both begin by consuming
`[win+0xab]`; 0x1b66e's body is `mov esi,[ebp+0xab]; lea edi,[esp+0x8];
lea esi,[esi+0xab]; movsd; movsb` = copy 5 bytes (byte kind + dword id) of the
BAT OBJECT's pending hit into the local, whereas 0x53 goes on to resolve +
select. `0x1b696 cmp BYTE PTR [esp+0x8],0x0; jne ok` else assert 0x2a428
(ebx=0x39a edx=0x414) = "no object under the cursor".

## S3. THE SHIP-SELECTION PREDICATE (MEASURED, msg 0x53 = 0x1b684..0x1b737)
```
1b684 mov esi,[ebp+0xab]      ; bat object
1b68a lea edi,[esp+0x8]; lea esi,[esi+0xab]; movsd; movsb   ; 5-byte pending hit
1b696 cmp BYTE PTR [esp+0x8],0x0 ; je assert(0x39a,0x414) "no object"
1b6ae mov edx,[esp+0x9]       ; hit id (dword after the kind byte)
1b6b4 call 0x17694            ; CLIP RESOLVER (below)
1b6b9 mov [ebp+0xb3],eax      ; hovered clip record
1b6bf..1b6f1 SCREEN-BOX leg: reads clip [+0x25],[+0x27] with `sar ..,0x10`
      (signed coords) and compares against [win+0x8],[+0xc],[+0x10],[+0x14];
      outside -> 0x1ca38(win, clip) clears the hover triple at [win+0x1d1e]
      and selection is SKIPPED.
1b6f6 cmp BYTE PTR [eax],0x2  ; *** CLIP KIND 2 == SHIP *** ; jne 0x1b726
1b701 mov eax,[eax+0x1]       ; SHIP RECORD POINTER
1b706 mov ebx,[eax+0x54]; sar ebx,0x10    ; = byte [ship+0x56] (t273 OWNER INDEX)
1b709 mov dl,BYTE PTR ds:0x7458e          ; viewer/player index
1b712 cmp ebx,edx ; jne 0x1b726           ; NOT MY SHIP -> NO SELECTION
1b716 cmp DWORD PTR [eax+0x88],0x0        ; MOVES (t86/t295 field)
1b71d jle 0x1b726                         ; NO MOVES -> NO SELECTION
1b71f mov BYTE PTR [ebp+0xb7],0x2         ; *** WINDOW MODE := SHIP SELECTED ***
1b72a call 0x1d7dc(win,0)                 ; repaint
```
CLIP RESOLVER 0x17694 verbatim: scans the window's CLIP LIST
`[win+0x1d2a]` (count `[win+0x1d32]`, **STRIDE 0x35**) for the entry whose
`+0x1` equals the hit id, returns it (asserts 0x122/0x165 on null arg,
0x12f/0x172 on not-found). So the hit id is a key, NOT a pixel position.
CLIP KIND MAP (from the sibling consumer 0x172a8, which switches on
`[[obj+0xab]+1]`'s kind byte): kind 3 = the PLANET branch (0x172e8), and
inside it the planet's `[+0x62]` byte selects a cursor shape by comparing the
planet record's first byte against literals 0x34,0x37,0x20,0x38/0x4a,0x3a,
0x2e,0x3c,0x3b/0x44,0x2d,0x28/0x27,0x24,0x48,0x26 -> frames 3..15; anything
else indexes `WORD [0x7650c + planetType*0x6a + 0x33] & 0x40`.
=> KIND 2 IS EXCLUSIVELY THE SHIP CLIP.

SELECTION LAW IN WORDS: a click selects a ship iff (a) the engine's hit-test
returned a clip of kind 2, (b) `ship[+0x56]` owner-index == `ds:0x7458e`
viewer index, and (c) `ship[+0x88]` MOVES > 0. Pixel brightness plays NO part.
THIS EXPLAINS t293 COMPLETELY: the bright orbital dots are the PLANET clips
(kind 3). Three launches clicked kind-3 clips, so `cmp BYTE [eax],0x2; jne`
always took the skip leg and `[win+0xb7]` never became 2 — which is exactly
why the arm at 0x1b5ba (which reads the SELECTED object) never fired and no
kind-2 order ever appeared. DO NOT re-try dot-clicking; the route must land
the cursor on the SHIP SPRITE clip.

## S4. The order-arm chain (the link t293 could not reach), msg 0x50
```
1b5ba cmp ebx,0x1 ; jl 0x1af7c                 ; param >= 1
1b5c3 mov eax,ds:0x43504                       ; SELECTED OBJECT
1b5c8 mov edx,[eax+0x58]; sar edx,0x10         ; its ORDER KIND byte
1b5ce cmp edx,ebx ; jl 0x1af7c                 ; kind >= param
1b5dd mov eax,[eax+edx*4+0x42]                 ; index the selection's target table
1b5e1 mov ebx,0x11
1b5e6 mov ds:0x43508,eax                       ; PUBLISH ORDER DESTINATION
1b5ed mov eax,0x7a35c; edx=ecx=1
1b5f2 call 0x56ad4                             ; engine post
```
0x56ad4 verbatim head: `mov eax,[esi+0x44aa]; sar eax,0x10` (slot index,
asserts 0x9aa/0x85a9a if == 0x20) then `mov WORD [esi+idx*2+0x422c],dx` and
`mov DWORD [esi+idx*2+0x422e],edi` — i.e. it writes a 6-byte {u16 code, u32
param} COMMAND RING entry at `[game+0x422c] + slot*6`, slot from
`[game+0x44aa]>>16`. So msg 0x50's effect is: code 0x11 with param = the
order target, queued into the per-player command ring. (t291 banked the
sibling slot `[+0x24d9c]`/rank `[+0x24d9f]` family; this is the COMMAND ring,
a different table.)
FULL LIVE CHAIN, one line: click ship sprite -> msg 0x52/0x53 -> kind 2 +
owner + MOVES gate -> `[batwin+0xb7]=2` -> msg 0x51 arms (`mode=1`) -> msg
0x50 publishes `ds:0x43508` from `ds:0x43504` and queues command 0x11 ->
command executor 0x3ca60 burns `ship+0x58 := 2`, `ship+0x59 := 0x43508`.

## S5. The [win+0xb7] MODE enum and the deselect path
Stores (census 0x1a000..0x1c400, all verbatim): 0 at 0x1ad41 0x1b114 0x1b138
0x1b20f 0x1b9b4 0x1ba5e 0x1bafb 0x1bb02 0x1bf74; 1 (ARMED) at 0x1b7dd; 2
(SELECTED) at 0x1b71f and 0x1ba39; 3 at 0x1b103. Readers testing 4 at 0x1af65
0x1b070 0x1b232 0x1b89f 0x1b8d2 (mode 4 = a transient/animating state; no
store of 4 found in this window's zone).
0x1ba39 store context (the SECOND click of a two-click order, on an already
selected object): gate `cmp BYTE [eax],0x2` (clip kind ship) then owner
`[ship+0x54]>>16 == ds:0x7458e` then `[ship+0x88] > 0`, mode := 2.
0x1baa7 store context (order ISSUE): gate `[win+0xb3] == eax` (hovered clip
still the selected one) and previous mode ch==0, then
`mov eax,[[ebx+0x1]]` -> `mov ds:0x43508,eax`, `[win+0xaf] := -1`, mode 0.
0x1b91c is the SELECTED-OBJECT click dispatcher (`[win+0xaf]` = the selected
object; ecx!=0 means "click with modifier"): ecx==0 -> `call 0x1ca38`
DESELECT; mode==1 -> computes an action byte from the selected object's kind
(2->3, 1->2, 3->4) and relays code 0x322; the 0x1bafb leg relays 0x326 with
mode := 0 (issue + clear).
`[win+0xaf]` (SELECTED OBJECT) WRITER = 0x1bdb4: three-tier lookup
`call 0x1a3b8(win + 0x1d36 | 0x253a | 0x2d3e, edx, ecx, ebx)` — three parallel
clip tables, first non-null wins (0x1bdc3 -> 0x1bdd0 -> 0x1bde5 -> 0x1bdf4).

## S6. HONEST NEGATIVES (what this iteration did NOT close)
1. WHO SETS THE PENDING-HIT BYTE `[batobj+0xab]` TO 2: the writer region is
   the sibling batmode window 0x156d4 (0x15f1e `mov BYTE PTR [ebp+0xab],0x2`
   inside the `test eax,0x80000000` leg of `call 0x32f34(win,[esp+0x84])`,
   with the else-leg storing kind 3 and `[ebp+0xb9]` toggling 3/2). The
   hit-SLOT ARRAY `[win + idx*8 + 0xc7]` (reader 0x32fa4) and
   `+0xcb` (reader 0x32f34) is FILLED at 0x32e90/0x32ea0 (append: store the
   record ptr, zero the second word, `inc WORD [win+0x8c7]`) and CLEARED at
   0x32fdc/0x32ee0. I did NOT finish proving which clip kind the ship sprite
   registers as in THAT array (the 0x80000000 sign test is the discriminator
   and its producer is upstream of 0x32e90). So: the SELECTION PREDICATE is
   cited; the exact pixel geometry that makes the engine return kind 2 is
   NOT yet cited.
2. THE SCREEN->SHIP MAPPING (camera/centre/zoom fields) is unmapped, so the
   live-session coordinates in S7 are DERIVED-FROM-RING, not measured.
3. NO LEDGER ROW CLOSED. Strict-close: OQ-016 residue 1 (nuke law) and
   OQ-019 residue 3 (magnetron witness) both still need a live witnessed use;
   this iteration supplies the missing CHOREOGRAPHY but not the witness.

## S8. THE DECISIVE PRECONDITION: a ship is only CLICKABLE when kind == 4
The clip list consumed by 0x17694 is BUILT by 0x1d39c (rebuild: clears every
entry's flag byte `+0x33` in a loop bounded by `[win+0x1d2e]`, sets
`[win+0x1d32] = 0`, then appends; appender tail 0x1d6a0..0x1d712 verbatim):
```
1d6b8 mov ebp,[esp+eax*4]            ; candidate object ptr
1d6bb cmp BYTE PTR [ebp+0x58],0x4    ; *** ORDER KIND == 4 (IN-SYSTEM) ***
1d6bf jne 0x1d6a9                    ; else: NO CLIP AT ALL for this ship
1d6c1 mov eax,[win+0x1d32] ; cmp eax,[win+0x1d2e] ; jl ok
                             ; else assert 0x2a428 ebx=0x750 edx=0x5dc (overflow)
1d6e0 add esi,0x35                   ; stride 0x35 (matches 0x17694's scan)
1d6e3 mov [esi+0x1],ebp              ; entry id/ptr = THE SHIP RECORD
1d6e6 mov BYTE PTR [esi],0x2         ; *** CLIP KIND := 2 (SHIP) ***
1d6e9 mov eax,[ebp+0x54]; sar eax,0x10          ; owner index
1d6f7 mov ax,WORD [eax*2+0x6fd60]               ; owner -> colour/sprite table
1d6f1 mov ebx,[ebp+0xa7]; sar ebx,0x18          ; shape/frame selector
1d707 call 0x1a270(win=edi, clip=edx, ecx, ebx) ; position + draw the clip
1d70c inc [win+0x1d32]
```
Sibling legs in the SAME rebuild: 0x1d745 `mov BYTE PTR [esi],0x4` for a
different object class (table `0x4348d + i*0xd`, count `WORD ds:0x43502`);
0x1d3d8 first entry kind 6 with `WORD [clip+5] = 0xffff`; 0x1d3fb kind 0xff
fillers; 0x1d417 kind 0 entry carrying `ds:0x43504`.
Selection highlight: 0x1d662 `or BYTE PTR [esi+0x33],0x1` fires iff the
candidate `== ds:0x43504` (i.e. the clip of the currently-selected object gets
flag +0x33 bit 0; 0x1d3b8 clears it on every rebuild).

SELECTION LAW, COMPLETE AND CITED (four gates, all measured):
  G1 (clip existence, 0x1d6bb): the ship must have order kind `[+0x58] == 4`
     (IN-SYSTEM). A kind-5 travelling ship or a kind-3/1/2 ship has NO clip,
     therefore CANNOT be clicked at all — in any view.
  G2 (kind, 0x1b6f6): the hit clip's kind byte == 2 (ship) — planets are 3.
  G3 (ownership, 0x1b712): `[ship+0x54]>>16 == ds:0x7458e` viewer index.
  G4 (mobility, 0x1b716): `[ship+0x88]` MOVES > 0.
  Effect: `[batwin+0xb7] := 2`; the ship's clip then carries flag +0x33|1.

## S9. VERIFICATION PASS (second context window, EVERY quoted block re-dumped
from `work/t91_code_disasm.txt` — 140,824 instrumented lines, 0x14bb0..0x826a5):
VERIFIED VERBATIM: S3 predicate 0x1b6f6..0x1b737 (kind byte==2 @0x1b6fc, owner
`ds:0x7458e` @0x1b709, MOVES `[+0x88]>0` @0x1b716, mode `+0xb7:=2` @0x1b71f);
S8 clip build 0x1d6b8..0x1d712 (`cmp BYTE [ebp+0x58],0x4` @0x1d6bb, stride
0x35, `mov BYTE [esi],0x2` @0x1d6e6, `mov [esi+0x1],ebp` @0x1d6e3, overflow
assert 0x2a428 ebx=0x750 edx=0x5dc @0x1d6cf..0x1d6db, owner colour table
WORD[eax*2+0x6fd60] @0x1d6f7); S2 dispatch head 0x1aef8..0x1af4e verbatim incl
msg-table edges; S1 writer sets: ds:0x43504 stores EXACTLY {0x28ec2, 0x28ef6,
0x36b01, 0x52003, 0x55d35} (a3 form; the two `89`-form writers S1 claimed were
NOT re-found this pass — treat S1's 0x55c52 entry as UNCONFIRMED), ds:0x43508
stores EXACTLY {0x1b5e6, 0x1baa7, 0x51a8e, 0x51fc2, 0x55bbd} + claimed 0x55bcc
(not re-found) — 5 confirmed each.
CORRECTIONS (binding):
 C1. Owner global is `ds:0x7458e` (BYTE, viewer index) — NOT 0x7458c.
 C2. `0x1aef8` has ZERO immediate references image-wide: the handler is reached
     via window-object registration, not an address reference. Attribution to
     BatModeWnd rests on windows.txt + the INDEPENDENT r1-savestate E1 list
     (0x14bc0/0x156d4/0x1aef8/0x1b91c/0x1ce1c) — solid but note the kind.
 C3. THE MOUSE ROUTE IS MSG 4, NOT MSG 0x53. msg 4 (0x1b070): bounds-check
     `ebx,edi in [win+0x8..0x14]`, then IF `[win+0xaf]!=0` -> `call 0x1b91c`
     (batcon handler) which at 0x1b9f4..0x1ba40 re-tests the hit clip: kind==2,
     `[esi+0xb7]==0` (idle mode), owner `ds:0x7458e`, `[+0x88]>0` -> stores
     clip ptr `[esi+0xb3]` @0x1ba08 and `mov BYTE PTR [esi+0xb7],0x2` @0x1ba39
     — SAME four-gate predicate as the msg-0x53 leg. msg 0x53 is the INTERNAL
     relay: posted by the 0x156d4 family at 0x15f3c (`mov ebx,0x53; eax=ebp;
     edx=0; call 0x16cf0`) after the hit-test sets `[ebp+0xb9]`; both 0x52
     (0x1b66e) and 0x53 (0x1b684) begin by copying the 5-byte pending-hit at
     `[win+0xab]+0xab` (movsd+movsb).
 C4. MODE-2 FOLLOW-UP CLICK (0x1b0d6..0x1b114, still msg 4): reads
     `WORD [win+0xbc]`; if == 0xffff -> `mode := 0` (CLICK CLEARS SELECTION);
     else -> `mode := 3` @0x1b103 + `call 0x1bd80(win, dx=x-[win+0x8],
     bx=y-[win+0xc])` = route-preview/drag leg. mode 3 next click @0x1b11d:
     resets mode 0 and consumes `[ebp+0x1d0a]` region with ecx=5 ebx=0x326.
     => A SELECTED SHIP'S DESTINATION IS NOT SET BY A PLAIN MAP CLICK in
     BatModeWnd; publication of `ds:0x43508` comes from msg 0x50 (0x1b5ba:
     `cmp ebx,1; jl out` then reads `ds:0x43504`, gate `WORD [obj+0x58]>>16 >=
     ebx`, `ds:0x43508 := [obj + 0x42 + ebx*4]` @0x1b5dd/0x1b5e6 + refresh
     0x56ad4(0x7a35c,1)) — i.e. msg 0x50 indexes the SELECTED OBJECT's own
     destination list `[+0x42..]` by ebx; and from 0x51a8e (gate
     `ds:0x484ec > 0x96` = turn number, publishes 0x51a73 `call 0x32fa4`
     result) and 0x51fc2 (`eax=[edx+0x59]` — order-record target re-publish).
 C5. msg 0x52 relay sites: 0x17243 sets `[eax+0xb7]=4` (ROUTE-EDIT mode) then
     posts 0x52 via 0x56374(0x7a35c, edx=[win+0x41]); 0x17639 sets mode 0 and
     posts 0x52 via 0x56434 then `call 0x1d39c` (CLIP REBUILD) @0x17654 —
     confirms 0x1d39c is THE clip rebuild invoked on order edits.
CHOREOGRAPHY, STATIC-DERIVED (for t297 capture; every edge cited):
 1. Ship must be kind 4 (`[ship+0x58]==4`, in-system) to HAVE a clip at all
    (0x1d6bb). Idle/orbited ships qualify; lane-travelling (5) do not.
 2. BatModeWnd left-click at the ship's CLIP position (screen coords inside
    client rect 7,7..465,472; clip screen pos computed at draw 0x1a270) with
    mode==0 -> msg 4 -> 0x1b91c -> mode 2 iff kind2+owner+MOVES>0.
 3. VERIFY selection: `ds:0x43504` non-null AND `[batwin+0xb7]==2` (ring-read
    via pointer law; 0xb7 is inside the window object the pointer law reaches).
 4. Destination: NOT a plain click (C4). Route = msg 0x50 family / the order
    UI (BatListWnd, SHAPEFILE 16BATTLE.SHP) — t297 must discover the msg-0x50
    trigger (likely a BatListWnd button or right-click menu; 0x1b5ba gate
    `ebx>=1` = order-slot index).
 5. Commit: executor writes `ship+0x58:=2, ship+0x59:=[ds:0x43508]` (t107
    0x3ca60 banked); witness = owner-0 kind-2 census.
HONEST LIMIT: the msg-0x50 TRIGGER (which button/widget posts it) is NOT
identified statically this iteration — the WIDGET-SIDE poster searches for
immediates 0x52/0x53 found only batmode-family relays (0x15f3c, 0x1724a,
0x1762c) and two assert sites (0x1f971, 0x4b83a), no cosmos-map poster. A
plain map click in mode 2 CLEARS selection (C4) — so t293's dot-clicks
failing is EXPLAINED: they either hit mode 0 (no clip: wrong pixel) or mode-2
clear. The remaining unknown is the destination-entry widget, NOT selection.

## S7. Live-session choreography note (for t297; derived, to be tested)
*** SUPERSEDED BY S9 + scripts/r296_selection_note.py — DO NOT FOLLOW THIS
BLOCK. Its click coordinates were guessed from the cosmos centre before the
verification pass; the mouse route is msg 4 via 0x1b91c (S9/C3), a plain
mode-2 map click DESELECTS (C4), and the pointer-law note below (B+0x88) was
wrong in kind: ds:0x43504 is plain RAM at B+0x43504, not a slot-array offset
(r1_slot.py OFF=0x82bb0 is the ship-record array). Kept for history. ***
Per t293's budget law this iteration spent ZERO launches, so t297 owns the
live attempt. Route (all game coords; scratch scratch copy, Xvfb, background
=true notify=true — the 420 s foreground cap law):
1. title -> (318,333) Return to Current Game; assert_on_map FIRST (t285 law).
2. FLEET sidebar (553,184) -> row for a ship whose ring record has owner 0 AND
   `[+0x88]` MOVES > 0 (S3(c) is a HARD gate — a ship with 0 moves can never
   be selected, so PICK BY THE RING, not by eye).
3. Row left-click (200,93) jumps to that ship's SYSTEM view (t293 proven).
4. The view is now BatModeWnd (rect 7,7-465,472). Do NOT click bright dots
   (planets, kind 3). The target is the ship sprite: it is at the SYSTEM
   CENTRE on arrival (t293 L3 witnessed slot 8 landing; the cosmos placement
   law 0x21f58 places at star coords + (0,-200,0) jittered rng%200). Centre
   of the BatModeWnd client = game ((7+465)/2, (7+472)/2) = (236, 239).
5. Click (236,239). VERIFY SELECTION BEFORE PROCEEDING — the ring has no mode
   byte, so the verification is the ARM side-effect: after the click, read
   `ds:0x43504` via the pointer law (B + 0x88-relative offset 0x43504 - the
   slot base used by scripts/r1_slot.py `OFF`) and check it is non-null and
   points at a ship record whose +0x56 == 0. If 0x43504 stays null, the click
   hit a planet: step the cursor along the arrival jitter (+-200 world units)
   and re-test; do NOT click3 blindly.
6. Only then: right-click / the arm msg family, then click the destination,
   then End Turn x2 with Escape popup draining (t245/t293 law).
WITNESS INSTRUMENT unchanged: owner-0 kind census, kind 2 == issued move
order (kinds observed {3,4,5} baseline, never 2 — clean signal, t293).
