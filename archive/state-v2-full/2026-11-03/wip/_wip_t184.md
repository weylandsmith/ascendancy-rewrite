# t184 WIP — OQ-019 build/redesign inventory path (last offline leg)

Assignment: STATE.md NEXT t184 — how a design's gizmo list is committed to
the ship record at build/redesign time; writers of the [ship+0xab]+i*7 slot
array law and the [ship+0x15a] count.

## Finding 1 [MEASURED this session] — the ONLY +0x15a dword writers (census)
scripts/r1_t86_write_census.py 0x15a -> candidates=3 verified=3 rejected=0:
  0x49569 [FUN_00049534] mov DWORD [ecx+0x15a],eax
  0x4b0e3 [FUN_0004ae24] mov DWORD [ebp+0x15a],eax   (save-restore path, see F4)
  0x4dc87 [FUN_0004da1c] mov DWORD [ebp+0x15a],eax   (save/serialization, see F4)
No add/sub/inc-family writers. FUN_0004a74c (the t47 upkeep-side edge) does
NOT write +0x15a (it only reads the list per t101 bank).

## Finding 2 [MEASURED] — FUN_00049534 IS the build-time ship-init law
Full asm 0x49534..0x49622 decoded (objdump /tmp/ascend_all.txt; Ghidra
decompile concurs). Verbatim law (EAX=ship rec, DL=kind byte):
  byte [ship+0xaa] := kind  (assert FUN_0002a438 fires if kind >= 4)
  HULL := byte3 of dword [ship+0xa7]  (i.e. dword >> 0x18)   [hull index]
  dword [ship+0x15a] := (word at 0x6842 + HULL*2) >> 16      [CAP TABLE,
      16-bit hi word per hull — so +0x15a is a HULL-DERIVED CAPACITY/COUNT,
      NOT a gizmo count and NOT copied from the design]
  if byte3[ship+0x31]==0 or hi16[ship+0x54] != BYTE ds:0x7458e (player race):
      copy NULL-terminated WSTRING from DAT_00078484 + HULL*0x14 stride-2
      into [ship+0x34]  -> hull NAME string; player-designed ships get NO
      name copy [structure verified]
  dword [ship+0x8c] := (HULL+1)*10; if race-table DAT_00012fb3 row(equipee
      empire hi16[ship+0x54]) == 1 (0x1ee stride) -> DOUBLE;
  dword [ship+0x98] := [ship+0x8c]; dword [ship+0x14] := 0.
CALLERS (rel32 call census, all 5):
  0x40441 + 0x40492 in FUN_00040358  (two distinct call sites — scenario
      build/instantiation loop context [to pin next])
  0x49059 in FUN_0004904c
  0x4982a in FUN_000497a8            (FUN_000497a8 also touches +0x15a/+0x15e
                                      AND +0xa7 — prime redesign candidate)
  0x49d06 in FUN_00049c14
Runtime corroboration owed: dump hi-word table 0x6842.. per hull and compare
to live [ship+0x15a] across playcap saves (save RAM base B+0x82bb0 law).

## Finding 3 [MEASURED] — +0xa7 (dword) is the DESIGN POINTER
Every UI-dialog writer (0x2683f, 0x29e8d, 0x30ac3, 0x4d8e4, 0x5161c, 0x57873,
0x5b265 ... ~55 sites) stores an immediate pointer to a design-record image
(e.g. 0x5a4c, 0x5cb8, 0x88ac4) at [rec+0xa7]; the ship-side writer
0x49359 [FUN_0004929c] `mov DWORD [ebx+0xa7],ecx` copies a computed design
pointer into a ship record. So the design identity lives as ONE DWORD at
+0xa7, and hull/gizmos are read through it. +0xaa = kind byte (gate <4),
+0xab.. = stride-7 slot ring (order queue per ships.md §10/§11).

## F4 [MEASURED] — 0x4ae24 / 0x4da1c are SAVE/LOAD serialization
Ghidra: FUN_0004ae24 = save-to-buffer then reload fixups (FUN_00078ac4 /
FUN_00078aa0 relocation pair; converts +0x59 pointer<->index by rec size:
/0x7b ship, /0x60, /0x27 — the t181 multi-block save law's per-record arm);
FUN_0004da1c = ship->slot-template copy (+0xab..+0x177 fieldwise, "clone to
design slot" shape [inferred]). Neither is a build-time gizmo writer.

## Finding 5 [MEASURED, full asm decode] — THE SLOT-ARRAY LAWS
Slot ring: slot i base = ship+0xab+i*7, i < dword[ship+0x15a] (CAPACITY);
slot layout byte0 = gizmo CIDX (0xFF = empty), word1 (+0xac abs slot0) =
per-slot u16. dword[ship+0x15e] = FILLED-SLOT COUNT (inventory size).
Writers of these (all verified asm):
  FUN_00049624 "fill-first-empty": scans for cidx==0xff, writes it,
      +0x15e++, recalc FUN_00049acc, ret -1 (0 = no empty slot).
  FUN_00049698 "set-slot(i=EDX? no: EDX=cidx, EBX=slot idx)": guards
      ebx<=cap, refuses same-cidx dup, if old slot empty +0x15e++, writes
      slot cidx, recalc, ret -1. [asm 0x49698..0x496de verbatim]
  FUN_000496e4 "clear-slot(i=EDX)": if already 0xff ret 0; else +0x15e--,
      slot:=0xff, recalc, ret -1.
  FUN_0004929c "ship-init/clear" (caller 0x4904f FUN_0004904c): zeroes all
      stat dwords, +0x15e:=0, clears slot window cidx=0xff word=0
      (loop [ship+0xab] step 7 to [ship+0xaf] stop via param-EBX, ~25
      slots) [stop-condition exactness half-verified].
FUN_00049acc = RE-MATERIALIZE (the ONLY stat rollup, callers = the 4
mutators above): zeroes ship +0x0,+0x4,+0x10,+0x18,+0x1c,+0x20,+0x24,+0x28,
+0x2c,+0x30; [ship+0x10] := [ship+0x14] (hull base); per non-empty slot:
row = cidx*0x6a + 0x7650c (t101 +0x30 base artifact -> live-named gizmo
table): +0x52->ship+0x0, +0x56->+0x4, +0x5e->+0x10, +0x62->+0x20,
+0x66->+0x18, if byte[row+0x32]==2 dword[row+0x36]->+0x1c; special cidx
0x47 -> ship+0x28:=-1; 0x2b/0x2c counted -> ship+0x8/0xc = fistp(count *
float ds:0x2583/0x258b); 0x2a -> ship+0x24++. So NO gizmo record is ever
copied into the ship — the ship holds only cidx slots; gizmo data is read
through the static/live gizmo table on every mutation. t46 §10's
"queued-order list" label on this ring conflates order-queue semantics;
the ring IS the inventory (gizmo-cidx law measured here).

## Finding 6 [MEASURED] — REDESIGN LAW FUN_000497a8 (sole caller 0x4e6d2
in FUN_0004e63c): if new-kind == [ship+0xaa] -> no-op(-1). new_cap = hi
word word[0x6842+2*new_hull]; REFUSE (-1) if new_cap < filled [+0x15e] —
REDESIGN BLOCKED WHEN INVENTORY EXCEEDS NEW HULL CAPACITY [verbatim
0x497da cmp/jl]. Else: sweep slots, remove+re-add compacting into slots
0.., re-init via FUN_00049534 (new cap/name/budget), name re-copied
UNCONDITIONALLY from DAT_00078484+hull*0x14 (bypassing the player gate
inside 0x49534 — [verified 0x4982f..0x49867]), recalc.

## Finding 7 [MEASURED] — BUILD-TIME COMMIT IS EXPLICIT PER-SLOT ADDS, TWO ROUTES
(a) SCENARIO/PRODUCTION PATH FUN_00040358 (sole caller 0x3f86d in
FUN_0003f758; turn gate DAT_00012e10/250 clamp [1,8]): init FUN_00049534
x2, then race-known queries FUN_0004a448 (highest-priority gizmo of
category via byte[cidx*0x6a+0x76541]*0x4b race-known dword
0x7478b-bit) and FUN_0004a4e0 (is-gizmo-known), then jumptable
cs:[cls*4+0x2b798] (cls 0..3 from scenario DATs 0x747d6/0x74d1c/0x750a0)
-> FUN_000405f8/0x40674/0x407f4/0x40a6c which call FUN_00049698 ~10-30x
each with cidx values — hardcoded starter kits per ship class.
(b) DESIGN-APPLY FUN_00040d1c (callers 0x40a5c, 0x40d0e inside (a)'s
class handlers): walks a 22-entry list at DAT_0x67ec, filters by race
known (FUN_0004a4e0), fills slots up to cap with RNG-SHUFFLED placement
(FUN_0007824f % remaining, 0x40d7b..0x40daf verbatim).
(c) INTERACTIVE UI: FUN_0004dd50's 0x4e425 (add: EAX=[ebp+0xab] ship ptr,
cidx=[ebp+0xb8]>>24, slot cursor ds:0x6974 object + vtable call
[ds:0x6974+0xc]) and 0x4e4f9 (remove), success stamp [ebp+0xbd]:=-1.
Cost side stays t46 §9 (design parse store), + FUN_0004a41c per-hull cost
table 0x687c x4 dwords -> FUN_0004a3d4 (production loop multiplies by CAP
at 0x40454 imul edx,[esi+0x15a]).

## Route status
Static route DONE (law above is the cited answer to "how the gizmo list is
committed at build/redesign": per-slot cidx adds + re-materialize, never a
record copy; capacity from 0x6842 hi-words; redesign capacity-refusal).

## Finding 8 [MEASURED runtime, 20/20 playcap saves, 1234 owned ship rows]
scripts/r1_t184_inv_law.py RC=0. Cap law confirmed EXACT: for every owned
row, dword[rec+0x15a] == dword_live(0x6842 + 2*hull) >> 16 where
hull = byte3 dword[rec+0xa7] — 1234/1234 (cap histogram {10:956, 15:20,
25:258}; hull1->10, hull3->25). The 0x6842 table is SCENARIO-LOADED DATA:
static-image bytes there do NOT equal runtime values (t43 stale-DAT law,
re-confirmed — first script leg wrongly tested the static image, RC=2).

## Finding 9 [MEASURED] — filled-counter law is EXACT; the residue is a
## vendor off-by-one, not a counter bug
filled dword[rec+0x15e] == count of slot cidx != 0xFF over slots 0..cap
(INCLUSIVE of slot index == cap) on 1234/1234 rows: 1134/1234 within
0..cap-1, and all 100 "residue" rows have slot[cap] OCCUPIED giving
scan(cap+1)=11=filled (100/100). Mechanism cited: FUN_00049698's bound is
`cmp ebx,[eax+0x15a]; jg reject` (0x4969b) — slot index EQUAL to cap is
admitted, writing one gizmo into the first dword of the cap field's
neighbourhood at rec+0xab+cap*7. Consequences [verified asm]: every i<cap walker misses slot[cap] —
recalc FUN_00049acc (bounds 0x49b23/0x49ba3 both reload +0x15a, strict
jl/jge), per-turn upkeep FUN_0004a658, order scans FUN_00049714/0x49768 —
so the overflow gizmo inflates [+0x15e] and is dereferenced by NONE of
them: a phantom slot. It was written either via FUN_00049698 (idx==cap
admitted, 0x4969b) or FUN_000496e4-family paths with NO index bound at
all (0x496e7 has no cmp). 4 designs carry it {0x143b000, 0x1440000,
0x1448c00, 0x144ac00}, identical in all 20 saves. CORRECTION to Finding 5 wording: FUN_00049698's dup-check
rejects only the SAME cidx IN THE TARGET SLOT (0x496b4 cmp), not global
duplicates — live rows carry dup cidxs (1d 1d, 47 47, 49 49 in playcap 41
row 1).

## Finding 10 — record-region geometry
Slot ring occupies rec+0xab..+0x153 = exactly 25 slots (0xab + 25*7 = 0x15a,
the cap dword abuts it) — matches FUN_0004929c's ~25-slot init loop; cap
maxes observed 25. So cap is a SOFT limit enforced only at add-time idx
check (ebx <= cap at 0x4969b) while the ring physically holds 25.
