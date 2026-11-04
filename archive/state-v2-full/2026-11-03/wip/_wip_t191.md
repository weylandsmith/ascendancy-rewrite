# t191 WIP — the `l` lane-reveal hunt (started 2026-10-29, session iter-113)

Intake: STATE NEXT = t191. Trigger A "timeline growth" adjudicated as the
2026-10-29 00:12 ingest the probe baseline predates (tail 25MB max turn 1335,
last rows turn-0 new-game, dosbox down) — no new sitting, t85g NOT re-run.
Trigger B delta = idle-report echo only (prompt-112 vs 113 human region is the
report block); no steering note -> STATE NEXT stands.

## FINDING 1 (MEASURED, byte-level): the t85f "STARMAP KEY DISPATCH" IS A
## PRINTF FORMAT PARSER — the t85f keymap leaf addresses are BOGUS.

Disassembly of the full region 0x798de..0x79d26 (Ghidra disassemble_function,
371 instructions) shows AL = byte ptr [ESI+0x15] compared against
`i o u x X d s p e c F E G P` and branches into handlers that CALL 0x797fc /
0x798d7 / 0x7d1e9 / 0x7d14e / 0x7979b, pad a buffer with '0' (0x30), write
'-' 0x2d / '+' 0x2b / ' ' 0x20 sign bytes at [ESI+0x17], track width at
[ESI+0x8] and precision at [ESI+0xc] (`SUB EDX,EAX; MOV [ESI+0xc],EDX`), and
on the unknown-spec path 0x79c62 emit the char itself and set [ESI+0x8]=1.
That is a vprintf format-specifier engine (width/precision/sign/zero-pad),
NOT a keyboard dispatcher. `MOV AL,[ESI+0x15]` = the format-string cursor;
`[ESI+0x14]` = shift/flag state of the parse, `AND [ESI+0x14],0xf9` = clear
flag bits per t85f — same instruction, different meaning.

Consequence: EVERY leaf address in the debugflags.md t85f table
(0x79ace "s REVEAL-ALL", 0x79c35 "c state-of-galaxy sets [esi+0x8]=1",
0x79985/0x799f5/0x799e2/0x79971/0x79b97 region rows) is inside this formatter
and must be REJECTED. The gate-site column of that table (0x273a0, 0x27401,
0x28059, 0x47828, 0x2736f) is independent of the formatter and is grep-from-
the-nougat-gate — it holds up (see Finding 2).

Independent byte census (work/ascend_payload.bin, imagebase 0 verified: raw
bytes at 0x273a0 = 833da00b010000 == Ghidra's listing) over ALL compare forms:
  `3c 6c` (cmp al,'l') ......... 0 hits  (re-confirms t85f's anomaly)
  `3d 6c 00 00 00` (cmp eax,'l') 0
  `66 3d 6c 00` (cmp ax,'l') .... 0
  `81 f8|fb|f9|fa 6c 00 00 00` .. 0 (eax/ebx/ecx/edx)
  `83 f8 6c` .................... 0
  `68 6c 00 00 00` (push 'l') ... 0
  full `[3c-3f] + printable` census: `l` appears 9x, none a compare-immediate
  (0x6198e..0x6fd63 are string/other data); uppercase `L` 4x (0x216f3,
  0x4a483, 0x55069, 0x55163) — none in a key-handler neighbourhood.
So there is NO immediate-encoded comparison against 'l'/'L' anywhere in the
576 KB payload. Any 'l' dispatch must be table- or variable-indexed, or the
observed effect has a non-key cause (see FINDING 3 — that is the live lead).

## FINDING 2 (MEASURED): the nougat.lf LANE-EXPOSE site writes t190's
## "unattributed" rec+0x20 field.

`objdump`-grade listing at 0x273a0 (Ghidra disassemble_bytes 0x27390..0x2741b):

  0x273a0  CMP  dword ptr [0x00010ba0],0x0   ; nougat.lf flag, JZ exit 0x271d1
  0x273ad  MOV  CX, word ptr [0x000177d3]    ; lane count
  0x273b6  MOV  EAX, 0x16147                 ; LANE POOL base (see below)
  0x273bb  CMP  BX, CX / JGE 0x273dd
  0x273c0  MOV  DL, 0x1
  0x273c2  MOV  CL, byte ptr [0x0007458e]    ; shift amount
  0x273c8  SHL  DL, CL
  0x273ca  OR   byte ptr [EAX + 0x20], DL   ; <== WRITES rec+0x20 (OR-sticky)
  0x273cd  INC  EBX
  0x273ce  MOV  DI, word ptr [0x000177d3]
  0x273d5  ADD  EAX, 0x27                    ; stride 39 == t190 record size
  0x273d8  CMP  BX, DI / JL 0x273c0
  0x273dd  ... CALL 0x28fc0; CALL 0x284bc; vtable [ESI+0xa7]+0xc call

Cross-checks that make the identification non-coincidental:
 - imm 0x16147 == t190's lane-record member offset B+0x82bb0+0x16147
   (physical 0x258147 this run) — ships.md S23;
 - stride 0x27 = 39 == t190's MEASURED lane record size;
 - count source [0x177d3] (lane count) vs the star loop at 0x27401 which uses
   count [0x16145] — the two loops are the LANE family and the STAR family,
   exactly as t85f's gate column described (lane |= 0x20 at rec+0x20 with
   0x27 stride; star family 0x60 stride).
 - t190 measured rec+0x20 values are powers of two {1,2,4,8,16}, zeroed at
   allocator 0x248ab — consistent with `1 << [0x7458e]` per-lane OR.

## FINDING 3 (MEASURED): the two `cmp CL,'l'` sites are PRINTF LENGTH-MODIFIER
## parsing, not key handling — and the WIP's earlier census was incomplete.

Corrected census (linear-decode decode of 0x80/0x81/0x83 /7 imm8 + 3c/3d forms
over the code region 0x14bb0..0x82bb0 — the WIP's regex missed the `80 /7`
and `83 /r` forms entirely): comparisons against 0x6c/0x4c EXIST:
  0x79694 `CMP CL,0x6c`, 0x796b4 `CMP CL,0x4c`, 0x7a4b1 `CMP CL,0x6c`,
  0x7a4bf `CMP CL,0x4c`, plus 0x1af1b, 0x48b7b, 0x490ea, 0x4e8cb, 0x6ee56 ...
Context disasm 0x79640..0x79753: a binary-search chain over 'N'(0x4e), 'F',
'L'(0x4c), 'l'(0x6c), 'w'(0x77), 'h'(0x68), digits, '-', '#', '+', ' ', '0'
OR-ing bits 0x10/0x20/0x40/0x80 into [EBX+0x14], with 0x796f9 zeroing
[EDX+0x14] first. 'h/l/L/w/N/F' = printf LENGTH MODIFIERS (h=short bit0x10,
l/w=long bit0x20, L/long-double bit0x40, N=near 0x80) — the front-end of the
SAME vprintf family WIP Finding 1 identified at 0x798de. So: `cmp al,'l'` is
still ZERO (t85f anomaly intact), and every existing comparison against 'l'
is inside printf/scanf parsing. No key handler anywhere compares 'l'.

## FINDING 4: the reveal block has NO static referrer — structural, not a gap.
dword census over the whole payload for 0x2736f/0x273a0/0x27401/0x27476 and
0x270c9: ZERO hits; `jmp [idx*4+disp32]` sites: 34, none with tables
containing these values. Watcom DOS-extender cross-segment pointers resolve
via fixup records at load, so a data-segment dispatch/menu table pointing at
0x273a0 would read as unrelocated bytes in the file image — the static
file-only search CANNOT find the key binding. The runtime RAM (autosave full
linear dump) CAN: patched dwords == P0+0x273a0 form.

## CLOSURE NOTES (t191, this doc is banked to debugflags.md t191 + ships.md
## S23 L5 + OPEN-QUESTIONS OQ-019 STATUS t191 — all landed 2026-10-29).

Deliverable A (the assigned hunt): CITED KEY->FLAG CHAIN achieved:
  'l' AT scancode 0x26 -> cosmos msg handler 0x26b34 (runtime slot member
  0x247adc == P0+0x26b34, 60.sav) -> DX==3 keydown -> 0x27e15 -> cascade
  0x27614 CMP ECX,0x26 / JBE -> 0x273a0 -> nougat gate [0x10ba0] -> OR
  1<<[0x7458e] into lane rec+0x20 (pool 0x16147 stride 0x27) -> repaint.
  Why zero `cmp al,'l'` (t85f anomaly): the handler keys RAW SCANCODES in
  ECX; char compares exist only in the printf front-end (Finding 3).
Deliverable B (secondary): rec+0x20 writers/readers closed (Finding 5d).
Method lesson (BANK): window-class dispatch tables live in the obj1 DATA
segment as UNRELOCATED code offsets in the file image and relocated ones in
RAM; a static dword hunt for a handler address is structurally dead — search
BRANCH EDGES (cheap linear decode) or scan RAM with the OQ-011 pointer law.
Residue kept open / flagged: (i) 0x46354 share-loop semantics INFERRED;
(ii) 0x22074/0x22e60/0x22f28 base-struct identity unproven; (iii) paired mask
byte store 0x21aa6: payload imm 0x6774 vs restored-image 0x89324 (t43 law) —
live read not done; (iv) whether DX==2 (0x27e0b) is mouse-move vs release —
not needed for the chain. The 'c' overlay scancode 0x2e now has a leaf
(0x2736f handler + 0x28059 displayer) — OQ-021's `c`-press ask is now fully
statically specified: press C on the starmap with nougat.lf, read PERCENT
CONTROLLED.
