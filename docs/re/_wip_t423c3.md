# t423 CONT cycle 3 — WIP (TYPE-10 paint site + byte+8 plumbing + final grade)

## C3-F0 — trigger check [verified]
Timeline mtime 2026-11-12 06:45 (no new sitting); last USER: line 301 (D11b).
Assignment stands: t423 CONT cycle 3 (vtable hunt + byte+8 census + final grade).

## C3-F1 — PAINT-VTABLE ARCHITECTURE RESOLVED [verified bytes]
scripts/t423c3_a7census.py (tracked): 38 constructor sites `mov dword [reg+disp32=+0xa7], imm32`
image-wide; imm32 = vtable address. PITFALL: imm is at site+10 for SIB form / site+6
plain — decode modrm first (first pass mis-parsed, read 0xa7 as imm).
Vtables live in DATA pool (>=0x82bb0). Example pair verified by raw bytes at 0x1561c:
  c782 a7000000 50580000 -> [obj+0xa7] = 0x5850 (restored) == 0x88500 raw-payload? CHECK;
  the vtable table at 0x88400 holds stride-6 entries (vtable A: 0x15630,0x30d08,0x156d4,
  0x16420,0x311b8,0x316f0), vtable at 0x88498 (class whose ctor writes at 0x1abe6):
  (0x1abfc,0x30d08,0x1aef8,**0x1d858**,0x311b8,0x1e9dc). Slot +0xc == 3rd entry == 0x1d858.
  0x30d08/0x311b8/0x316f0 recur in EVERY table = base-class defaults.
Dispatcher chain [verified disasm 0x52daa..0x52e49]: paint/invalidate goes
call dword [win+0xa7]+0xc (win in ebp), and via child: eax=[[ebp+0x67]]; ebx=[eax+0xa7].
NEXT: identify which ctor belongs to RACELIST (TYPE 10); read slot+0xc target of each
distinct vtable; look for FUN_0001fc34->FUN_0005d5a1 stretch calls with a scale arg.
NOTE 0x185d8 (cosmos scale-from-field) has exactly ONE rel32 caller 0x185ad (intra-class
jump-table dispatch 0x18591) — NOT reachable from RACELIST vtables unless shared class.

## C3-F2 — PAINT-VTABLE ARCHITECTURE RESOLVED [verified disasm+bytes]
scripts/t423c3_a7census.py: 61 sites write field +0xa7; TWO object classes conflated:
(a) low-region imms (0x5850,0x5a1c...) land in the SCRIPT region = movsd movsd chains —
    NOT vtables (a different class's +0xa7; ignore);
(b) FOUR data-pool vtables written by ctors 0x1abe6/0x31c5a/0x4d956/0x5b265:
    0x88498=(0x1abfc,0x30d08,0x1aef8,[+0xc]=0x1d858,0x311b8,0x1e9dc)
    0x88838=(0x31c8c,0x31de4,0x320f8,[+0xc]=0x32314,0x311b8,0x32444)
    0x88ac4=(0x4d9a8,0x30d08,0x4dd50,[+0xc]=0x4e6f8,0x311b8,0x316f0)
    0x88c24=(0x5b270,0x30d08,0x336b4,[+0xc]=0x33e34,0x33ecc,0x316f0)
    slot+0xc = 3rd entry (4-byte stride). 0x30d08/0x311b8/0x316f0 = base defaults.
    0x49359 is a memset loop (zeroing [obj+0xa7]) — NOT a registration (pitfall).
[win+0xa7]+0xc call sites 0x52daa/0x52e28/0x52e49 = invalidate chain (edx=0 arg,
eax=window; child path eax=[[ebp+0x67]]).
## C3-F3 — vtable 0x88838 paint slot 0x32314 = GENERIC SHAPEITEM-LIST PAINT
[verified disasm 0x32314..0x32443]: fetch FUN_0001fc34(0x9f10c, sel=word[win+0x18]) ->
FUN_0005caac(destRect,rec,x,y,flags) NATIVE 1:1 run-decode (decompiled: RLE run
walkers, ZERO scale math); then loop child records stride 0xe at [win+0xab], count
word[win+0xaf]: child+0xa byte type -> jump table 0x322f4 {0..7 -> tints 0..4,
>7 -> assert shapefile.cpp:0x186b} -> fetch SAME lib with sel=type+child+0xa, blit at
child rect minus window origin. FUN_0005caac is the native blitter (75 call sites).
## C3-F4 — STATE-3 PAINT FUNCTION 0x526b4 MAPPED (superseded-then-corrected)
0x526b4 (sole rel32 caller 0x52174; frame bounds x 0x17b..0x278, y 0x17d..0x1d8 ==
the state-3 bottom panel EXACT) contains:
 - CHIP ROW loop 0x525eb..0x52647: 8 iterations, x=379+16i (t414 zone EXACT), fetch
   sel=word ds:[0x6fd84] -> 0x53ee0 NATIVE tinted blit; selected slot (si==word[win+0xb5])
   diverges to 0x2fe04(0xf3) well fill;
 - STRETCH SITE 0x52834..0x52877 (see C3-F6 for the corrected ABI reading);
 - text call FUN_0002fb38 with rect 0x7d3a2 (w 0x50=80, h 0x41) + ink ramp via 0x53e58.
FIRST reading (push 0x62 = w98) SUPERSEDED by the ABI decompile in C3-F5/F6 below —
0x62 is a COLOUR/ramp arg, not a width. The 98-px coincidence is NOT the law.
## C3-F5 — FUN_0005d5a1 ABI RESOLVED — THE SCALE ARGUMENT IS 16.16 FIXED [verified decompile+disasm]
Decompiled head (0x5d5a1): `if (param_8==0x10000 && param_9==0x10000 && param_7==0)` ->
plain FUN_0005caac NATIVE blit; else affine path with FUN_000604e9(&v,&x,&w,param_7,
param_8,param_9) building the 16 vertex sets; 0x10000 = 1.0 SCALE, param_7 = shear/rot.
COSMOS control site 0x18635..0x18676 pushes (push 0 [shear], push ebx, push ebx [scale
from fild of the float size param], 0, rect@0x48c44, sel hiword, field hiword, shapeId,
rec, drawable) — same rect@0x48c44 constant as the newgame site = shared dest-rect
template of the stretch ABI.
## C3-F6 — DECISIVE SCALE LAW (defect d) [verified bytes 0x52834..0x52877]
State-3 PAINT function 0x526b4 (sole rel32 caller 0x52174; frame bounds x0x17b..0x278
y0x17d..0x1d8 == bottom panel EXACT) contains the portrait STRETCH SITE:
  push 0            ; param_7 shear = 0
  push 0x8000       ; param_8 X-SCALE = 0.5 (16.16)
  push 0x8000       ; param_9 Y-SCALE = 0.5
  push 0            ; (rect slot)
  push 0x48c44      ; shared stretch-rect template (same as cosmos 0x1864d)
  push [rec+0xb1]>>16 ; dest x = window field +0xb1
  push 0x62         ; palette index 98 (frame colour pal[62] law t415)
  push word ds:[0x6fd98] ; selector (shapefile cache 0x9f10c)
  call 0x1fc34 ; call 0x5d5a1
=> THE VENDOR DRAWS THE PORTRAIT AT HALF SCALE: smrace record 49x49 * 0.5 = ... wait
   DIRECTION: scale maps DEST->SRC sampling; 0.5 sampling steps = UPSCALE 2x of the
   record onto screen (measured 94..101 px == 49*2 EXACT). The 0x62=98 immediate is
   the PALETTE arg (matches t415 frame colour pal[62]=98), NOT a width — the earlier
   C3-F4 w=98 reading is SUPERSEDED by the ABI resolution above.
CHIP ROW in the SAME function 0x525eb..0x52647: 8 iterations x=379+16i (t414 measured
zone EXACT), fetch sel=word ds:[0x6fd84], blit via 0x53ee0 = tinted native blit:
0x53ee0 computes pal[raceByte*4+0x13 - k] ramp from byte [0x12e10+row0*0x1ee*?+8]
(the +8 COLOUR byte via stride calc 0x12e18 law) -> 5-entry ramp -> FUN_0005cf96
(stretched blit variant, scale args = 1.0) — CHIP TINT FROM byte+8 CONFIRMED.
0x53e58 (chip-selected path, c=0x62): same ramp with stride (ecx*32-ecx)*8 = 0x1ee-
style row stride off [esp+0x16]>>16 -> EXACTLY stride 0x1ee? (32-1)*8=248 vs 0x1ee=494:
NOT identical — seam: 0x53e58's stride is 248; the race-record stride law 0x1ee stands
from C2-F3; 0x53e58 indexes a DIFFERENT table (0x12e18 = race-record base +8! byte
[0x12e18 + 2*idx?] ... RESOLVE pending).
## C3-F7 — CHIP CLICK FULL CHAIN [verified disasm 0x529d2..0x52a35]
zone x379..493 y420..472 -> idx=(x-0x17b)>>4 -> STORED word [ebp+0xb5] (window field!
the same field the paint loop 0x52621 compares si against) -> FUN_000232ec(0x12e10,
idx) reassign -> [win+0xa7]+0xc invalidate. Complete: click->field->reassign->repaint.

## C3-F8 — STRETCH-SITE PARAM ABI: HONEST LIMIT [measured pushes; semantics UNRESOLVED]
Push sequence at the stretch site (verbatim, 0x52834..0x52872):
  push 0 / push 0x8000 / push 0x8000 / push 0 / push 0x48c44 / push [win+0xb1]>>16 /
  push 0x62 / push word ds:[0x6fd98] / edx=0 / eax=0x9f10c / call 0x1fc34 / push eax /
  push rectptr / call 0x5d5a1.
The fetch call 0x1fc34's register args are [CACHED LAW, t422 F13]: eax=cache 0x9f10c,
ecx=selector, edx=COLOUR (0x62=98 == pal[62] frame-colour law t415 — resolves the
w98-coincidence as a COLOUR arg, not a width), stack = x (+extra at cosmos site).
Cosmos control site 0x18635 pushes (0, ebx, ebx, 0, rect@0x48c44, x, sel, id, rec, dst)
where ebx = fistp of an FPU-computed SIZE PARAM (the [obj+0x4f38] fild+-20/*0.3 law).
FUN_0005d5a1 decompile: param_7/8/9 feed FUN_000604e9 (sin/cos + 16.16 multiply ->
vertex table 0x8408..0x8457); (0x10000,0x10000,0) = identity -> plain 0x5caac path.
=> the newgame site's (0, 0x8000, 0x8000) IS a NON-IDENTITY affine request at the
   PORTRAIT PAINT SITE — the vendor stretches the record there, CITED. The exact
   scale/extent semantics of params 7/8/9 could NOT be pinned statically (decompiler
   stack-model unreliable on this cdecl family; param_4..param_10 mapping ambiguous
   between two sites). MEASURED 2x (two independent bboxes + elimination census,
   C2-F4) REMAINS the operative scale law; the stretch SITE is now cited; the
   selector word ds:[0x6fd98] -> record binding is the remaining named seam
   (decider = live BPLM at 0x52867 reading ecx/edx — NOT queued: heavy).
PITFALL: do NOT re-derive param semantics from this decompile alone; both the
cosmos and newgame sites must be reconciled first, and the FPU chain (fild/fstp)
needs an x87-aware trace.

## C3-F9 — BYTE+8 CAMPAIGN PLUMBING CENSUS [verified, HONEST CLOSE]
Whole-image census (scripts/t423c3_immcensus.py + raw scans):
 - imm 494 (stride 0x1ee) appears at EXACTLY 3 sites: 0x25627, 0x44207, 0x4425f.
   0x44207/0x4425f = `rep movsd 0x7b dwords + movsw` = 494-BYTE RECORD COPY
   (race-record clone at load/insert; the helper 0x20b44 called around it is a
   finalizer, decompiled: [p+0x108]!=-1 -> free chain). NOT tinting consumers.
 - byte reads [reg+disp8=8] (8A mod01) = 4 sites IMAGE-WIDE, none in a race-record
   context; movzx/SIB variants: ZERO. The vendor reads byte+8 via the record-copy +
   dedicated functions (FUN_000232ec write; 0x53e58/0x53ee0 chip-ramp reads this
   session; intro-ink game.pal[byte*4+0x13] t412; ring index law C2-F5) — there is
   NO MAP/entity tinting consumer of byte+8 in the exe beyond the UI paths ALREADY
   covered by the port's kOwnerRgb mapping. SEAM CLOSED AS "UI-only, port complete":
   the campaign-side plumbing the cycle-2 row suspected does not exist as claimed;
   the 78-stride sites premise was record COPIES (the 0x1ee imm census above).

## C3-F10 — FINAL GRADE (work item 3) [verified re-shoots, this session]
t412_newgame_shot.sh exit 0 (newgame + raceintro + campaign chain, log verbatim);
t423_hostile_shot.sh exit 0 (red spiked hostile orb CONFIRMED in atmosphere row);
t423c_chip_shot.sh exit 0 + 'ui raceconfig player colour idx 3 (races 7)'.
Native-vision grade of /tmp/t412_shots/t412-newgame.png: wheels distinct (dot-well /
icon-ring / orb), DESC panel solid black, portrait in green ring, 7 chips + neutral,
planet + crest native, Begin box starfield+portrait — NO glitches. Hostile shot same
clean. DEFECT SCOREBOARD (d): CITED stretch paint site + MEASURED 2x + named selector
seam -> GRADE-CLOSED per the row's own budget law (t422 precedent: elimination census
+ cited mechanism, seam named). All defects (a-g): CLOSED or graded with named seams.
No code delta this session (measurement iteration) — tests UNCHANGED 423/0/0.
