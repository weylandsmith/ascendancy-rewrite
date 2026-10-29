# planets-ui.md — planet-screen paint routine: gauge + population LAWS (t198)

Scope: the PLANETALLOC screen (extracted/ascend00/windows.txt:1485 TYPE 7
NAME PLANETALLOC, WINITEMS 0; five TYPE-29 panels L->R at windows.txt:1535
PLRES / :1552 PLIND / :1569 PLPRO / :1586 PLPOP / :1603 PLBUILD). All asm
from work/ascend_restored.bin (base-0: image addr == file offset). Full
listing banked: work/t198_planwin.asm (objdump -b binary -m i386
0x3aa0a..0x3e342). Method + pitfalls in docs/re/_wip_t198.md.

## 1. WHERE THE PAINTING HAPPENS [verified]
Paint body entry **0x3b96c** (push ebx/ecx/esi/edi/ebp; sub $0x380,%esp;
MOV EBP,EAX = widget ptr; __regparm). Blit sites inside: 0x3b9df, 0x3ba1e,
0x3ba4a, 0x3c0c2, 0x3c13e, 0x3c1ab, 0x3c82d, 0x3cd2e, 0x3cdc2, 0x3ce2c,
0x3ced7 (+0x3dbd5 next function). Every gauge blit obeys the banked S12.1
blit arg law (arg1 = descriptor copy LEA ESI,[EBP+4]; arg2 = cache payload
from FUN_0001fc34(cache 0x9f10c, slot idx); arg3 = u32 selector; arg4/5 =
screen x/y).

STRUCTURAL FACT: the gauge widgets carry SHAPEFRAME -1 and windows.txt has
only SEVEN SHAPEITEM lines (1starmap x4, 3cfgnew x3) — there is NO
windows.txt shape binding for planres/planind/planpro, and the generic
widget pass FUN_00031384 only understands descriptor byte0 types 0/1 with a
FIXED desc+5 selector (shp.md S11.1). Level->record selection is therefore
100% code-side in this routine. [verified]

## 2. THE SELECTOR DISPATCH [verified 0x3cc15..0x3cca6]
```
3cc15  mov 0x47(%eax),%eax        ; key = widget byte +0x47 (SENDPARAM1 area)
3cc18  mov %eax,0x4c(%esp)
3cc1c  cmp $0x4,%eax / je -> key:=3          ; PLPOP-style param -> key 3
3cc30  sar/mov +0x43(%eax)>>16 == 0x33 -> key:=4
3cc73  cmpl $0x2,key / jg -> switch
3cc94  cmp $0x4,key ; ja default
3cc9f  jmp *cs:0x27fe8(,key,4)
```
Switch table content VERIFIED LIVE (the table is RELOCATED at runtime;
image bytes at 0x27fe8 are code — t43-class law): in 41.sav at member
image_off 0x3cb98 the five entries are exactly
[0x3cca7, 0x3cd3b, 0x3cdcf, 0x3ce39, 0x3cefd].
Key semantics fully resolved against windows.txt: the switch byte is the
widget's SENDPARAM1-slot byte (+0x47) with two code-side remaps —
0x3cc1c maps value 4 -> 3 (= PLPOP, whose SENDPARAM1 is 4), and 0x3cc29 maps
ANY widget whose +0x43 dword >>16 (SENDMESSAGE) == 0x33 (=51, i.e. PLBUILD,
whose SENDPARAM1 1 would otherwise fall into the IND-gauge case) -> 4.
Hence: key 0 = PLRES, 1 = PLIND, 2 = PLPRO (SENDPARAM1 0/1/2), 3 = PLPOP
population grid (0x3ce39), 4 = PLBUILD current-project panel (0x3cefd);
key > 4 -> default 0x3d1bc (unreachable).

## 3. LEVEL->RECORD LAW (the gauge compression map) [verified]
Common tail of cases 0/1/2 (verbatim, case 0 at 0x3cca7):
```
66 a1 90 fd 06 00   MOV AX,[0x6fd90]      ; CACHE SLOT INDEX global
8b 15 08 35 04 00  MOV EDX,[0x43508]      ; PL = current planet object ptr
66 8b 42 46        MOV AX,[PL+0x46]       ; LEVEL word (u16)
68 00 00 e8 3f     PUSH 0x3fe80000        ;  ; second half of the double
6a 00              PUSH 0x0               ; 0.75 (f64, hi=0x3fe80000 lo=0)
db 44 24 64        FILDLL level           ; double conversion
call 0x78a90                             ; FUN_00078954 = pow() (decompile:
                                         ;  log2/ABS/exp path; 2 doubles in)
call 0x76e08                             ; x87 ROUND-TO-NEAREST (fldcw $0x1f
                                         ;  + frndint, restores cw) — NOT trunc
db 5c 24 5c        FISTP selector
clamp: test EAX,EAX / jge / ->0 ; cmp $0x14 / jle / ->20
then PUSH 0; PUSH 0; PUSH selector; PUSH slot; PUSH 0x9f10c; CALL FUN_0001fc34;
PUSH payload; PUSH desc+4; CALL FUN_0005caac
```
So, for planet record PL (word fields per income-law.md/income-law census):

| panel | slot global | level field | record index |
|---|---|---|---|
| PLRES (research)      | [0x6fd90] | u16 [PL+0x46] RES | clamp0..20( round( RES **0.75 ) ) |
| PLIND (manufacturing) | [0x6fd92] | u16 [PL+0x44] IND | clamp0..20( round( IND **0.75 ) ) |
| PLPRO (prosperity)    | [0x6fd94] | u16 [PL+0x48] PROS | clamp0..20( PROS ) — identity |

[verified] The exponent constant is the double 0.75 (=3/4), built from the
push pair 0x0 / 0x3fe80000; FUN_00078a90 is the two-double pow trampoline
(FUN_00078954 uses log2/ABS per its decompile); FUN_00076e08 is round-to-
nearest (fldcw trick), so the law ROUNDS, it does not floor.

CORPUS MEASUREMENT [verified, 2900 planet records over the 20-save playcap
corpus, locator law = STATE cells-in-{7,11,23,45,73} AND cap==cells+10 AND
slot-ptr sane; DAT_00043508 pointer law member = ptr+0x88 verified 20/20,
60.sav target = "Icarus II", law-valid]:
  +0x44 IND max 77, +0x46 RES max 52, +0x48 PROS max 16 (never saturates);
  pow-0.75 selectors span 0..20 (IND rec 20 reached from level >= 53:
  pow(53,0.75)=20.2 -> round 20; IND max 77 -> clamped), RES reaches 19 at
  52 and would hit 20 above ~57. Non-uniform histogram (e.g. IND sel0 x820,
  sel2 x640) — the map COMPRESSES exactly like the vendor's 21-record ladder
  (header dword[1]=21 for planres/planpro, t196) while the PLAYER SEES ~60
  levels of IND/RES growth. The "~60-levels-vs-21-records" question is
  ANSWERED: pow(0.75) + round + clamp0..20 is the compression map.
  Cross-check vs the rewrite's own field law (campaign.cpp:768 "+0x44 IND,
  +0x46 RES, +0x48 PROS" — income-law.md): consistent.

## 4. POPULATION SLOT LAW [verified 0x3ce39..0x3cef8, key 3 = PLPOP]
```
loop ESI = 0 .. u16[PL+0x4a] (CAP)          ; exit jge when ESI >= cap
  EDX counter starts 1;  incl EDX when ESI == u16[PL+0x4c]; incl EDX when
  ESI == u16[PL+0x42]                        ; 0x3ce96 / 0x3ceae
  selector = EDX
  slot idx = [0x6fd9c]; cache 0x9f10c; FUN_0001fc34 -> FUN_0x5caac
  column EDI += 0x0a per slot; when ESI%10 == 9 (idiv 10, CMP EDX,9 at
  0x3cef2) column resets to 0 and row EBP += 0x0a (ebx := 0xa at 0x3cedc)
```
=> SEL(i) = 1 + [i >= used(+0x4c)] + [i >= pop(+0x42)], drawn over
i = 0..cap(+0x4a)-1, TEN slots per row. Census 2900/2900 records satisfy
used <= pop <= cap, so exactly three band shapes occur:
  slots 0..used-1            -> SEL 1  (pop that is PUT TO WORK: "busy")
  slots used..pop-1          -> SEL 2  (pop not working: "free/idle")
  slots pop..cap-1           -> SEL 3  (beyond population: EMPTY slot icon)
This is the player's testimony (capacity-sized array; empty circles; two
pose classes) arriving as a CITED law; the assignment SEL1=busy / SEL2=free
follows the used<=pop ordering law but the icon identity per SEL value needs
the [0x6fd9c] library's art — the slot-index globals' WRITERS were NOT found
by direct-encoding census (A3/89 05/C7 05 forms over the whole image, zero
hits), so WHICH library feeds 0x6fd9c (planets.shp? planalNN? planitem?
unlisted) stays OPEN [honest negative; gwshare.txt:35-37 lists planets.shp +
planitem.shp as the planet-screen-adjacent libraries].
The 0x3b9df trio (header strip: 3 blits incl. an overlay gated by
byte[widget+0x18b]&4 at fixed (0x198,0x128)) and the 0x3be7d quad (4 x
FUN_0005bf71 rect fills gated by byte[widget+0xab]==0xff) are the panel
frame/backdrop draws — cache slots from widget fields, no level logic.

## 5. CONSEQUENCES BANKED
1. OQ-005 SELECTION CENSUS (partial, cited): the planind library's records
   are addressed by selector values 0..20, so the 13 span-undersized
   (X-class, t196/t197: dims canonical, frames complete) records k0..k12 are
   ALL inside the drawable range — the "never-drawable placeholder" reading
   is REFUTED for planind. 1starmap: windows.txt SHAPEITEM lines select
   records 3,4,5,7 (two of the t196 EXACT-H residue k3/k4 are SELECTED;
   k6 not per those lines). 3cfgnew: SHAPEITEM selects record 0 only;
   k1..k12 unselected by windows.txt. cos_star (COSMOSWnd STAR_SHAPES,
   windows.txt:208) selector site 0x2925c reads ship/star state — its
   residue k40..k51 selection NOT adjudicated this pass [open].
2. The bottom "past-span bands" question (t197 S3) is ANSWERED by the law
   for the gauges: the blit gets NO clip rect (clip fields = the caller's
   widget widget-rect, shp.md W3.2) and every gauge draws exactly ONE
   complete record — the desynced tail band exists in the cache bytes but is
   never addressed (selector picks record k's own stream start via the
   runtime table, t197/S17).
3. PITFALLS (see _wip_t198.md S0): Ghidra get_function_callers under-reports
   (15 of 75 blit sites — use the E8 byte-pass census
   scripts/r1_t198_blit_callers.py, which reproduces t83's 75/53 exactly);
   run_script_inline is POISONED by pre-existing broken scripts in
   ~/ghidra_scripts (T66Callsites/SeedFns/Diag compile errors make the whole
   build skip every script); switch tables are relocated (image bytes at the
   jump-table symbol are code — read the table from a save member).
