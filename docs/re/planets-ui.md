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
  pow(53,0.75)=19.64 -> round 20 [t199 recompute; the t198 line said 20.2 —
  wrong arithmetic, same conclusion]; IND max 77 -> clamped), RES reaches 19
  at 52 and would hit 20 above ~57. Non-uniform histogram (e.g. IND sel0 x820,
  sel2 x640) — the map COMPRESSES exactly like the vendor's 21-record ladder
  (header dword[1]=21 for planres/planpro, t196) while the PLAYER SEES ~60
  levels of IND/RES growth. The "~60-levels-vs-21-records" question is
  ANSWERED: pow(0.75) + round + clamp0..20 is the compression map.
  Cross-check vs the rewrite's own field law (campaign.cpp:768 "+0x44 IND,
  +0x46 RES, +0x48 PROS" — income-law.md): consistent.

T199 RECOMPUTE + LANDINGS [verified]: the full first-level-per-selector table
(k=0..20 -> L=) is
  0,1,2,4,6,8,10,13,15,18,21,23,26,30,33,36,39,43,46,49,53
(unclamped 21 from L=57, so clamp20 is a REAL branch at IND>=57). Exact .5
ties are IMPOSSIBLE: L^0.75=(2n+1)/2 requires 16*L^3=(2n+1)^4, whose 2-adic
valuations differ (even vs odd), so C++ lround == the x87 frndint-nearest
result on every integer input. The laws are now CODE in the rewrite:
ui::gaugeSelector / ui::prosSelector (src/ui/layout.{h,cpp}, pinned by
tests/layout_planet_gauge_selector_law_t199 over the corpus anchors 52/53/77
plus both-side boundary-exactness at all 21 selectors) and
Campaign::popBands/popBandsFor (src/game/campaign.h, pinned by
tests/campaign_pop_band_law_t199 incl. the independent band-histogram check
count1==used / count2==pop-used / count3==cap-pop over a seeded campaign).
Rendering stays blocked on OQ-005 (ui-runtime.md §2/§2a).

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
follows the used<=pop ordering law but the icon identity per SEL value needed
the [0x6fd9c] library's art — RESOLVED t254 [verified live-RAM]:
u16[0x6fd9c] = 44 (bank-t251-live1255/41.sav) -> cache slot 44 verbatim
content-match = 17np.shp (gwshare.txt:45; slot == gwshare line - 1, control
slot 41 = 14intel.shp). Records: SEL1 k1 = sideways red humanoid (busy),
SEL2 k2 = front-facing yellow figure (free), SEL3 k3 = hollow green ring
(empty); dims 9x9/7x9/8x8 fit the 0x0a pitch (planets/planitem/planalNN are
EXCLUDED by min-dims 11/24/47). Full chain + live pixel census:
docs/re/shp.md S23.
The 0x3b9df trio (header strip: 3 blits incl. an overlay gated by
byte[widget+0x18b]&4 at fixed (0x198,0x128)) and the 0x3be7d quad (4 x
FUN_0005bf71 rect fills gated by byte[widget+0xab]==0xff) are the panel
frame/backdrop draws — cache slots from widget fields, no level logic.

T199 LANDING [verified]: the band law is CODE in the rewrite as
Campaign::popBands (pure, src/game/campaign.h) + popBandsFor (operates on
usedPopFor()/pop/storedCapFor = the +0x4c/+0x42/+0x4a analogs), pinned by
tests/campaign_pop_band_law_t199: synthetic shapes for all four edge classes
(used<pop<cap, all-empty, all-busy-full, all-free, zero-cap) plus the corpus
invariant used<=pop<=cap checked against the rewrite's own seeded state, and
band HISTOGRAMS counted independently of the formula (count1==used,
count2==pop-used, count3==cap-pop). Vendor-formula fidelity past the corpus
law (used>pop input -> values still in 1..3 per verbatim increments) is
pinned too.

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

## 6. COSMOSWnd STAR-PIP SELECTOR LAW (t200) [verified static + measured census]

Scope: the STAR_SHAPES library (DATA\COS_STAR.SHP, windows.txt:208; file
extracted/ascend01/data/cos_star.shp, 55 records k0..k54, t196/t197 dims-zero
residue = k40..k51). Listings: work/t200_cos_star.asm (0x2925c..0x29731),
work/t200_coswnd2.asm (0x2976c..0x2a493).

1. THE PAINT LOOP IS FUN_00029788 (coswnd.cpp; enclosing function of the
   t198 census site listed as 0x2925c — t198's "one blit site" was actually
   the FUNCTION START; the real site is 0x298dc, second cosmos site 0x2a223)
   [verified: functions_full.tsv hex-size span 2925c+0x1237=0x2a493 + E8
   byte-pass]. Iterates a dword cursor of DISPLAY NODES (starts at the
   handler's eax object, step +4, count [wnd+0x400]); each node: +0 POINTER
   to the stride-0x60 RUNTIME STAR RECORD (static base 0x13bc5; list built
   by FUN_00028fc0 at 0x2903a: stores 0x13bc5+0x60*i into [w+0xb3] storage,
   count word [w+0xb7]), +4 dispatch tag (zeroed for stars at 0x2904f),
   +3/+5 x/y 16.16, +0xd float. The star record matches ships.md S11
   (coords +0x08/+0x0c/+0x10, stride 0x60, +0x59 owner ptr).

2. STAR DISPATCH on BYTE [entry+4] (zeroed for stars at 0x2904f):
   0 -> star-pip blit (below); 1 -> lane line FUN_0005bf71 with its own
   7-class ladder (0x29bd5 chain: >=0xdc->7 else cmps 0x93/0x49/... with
   bases 0x10/0x30/0x68/0x70; SEPARATE LAW, banked not closed); 2 -> label
   FUN_00053e58; >=3 -> nothing drawn.

3. STAR-PIP SELECTION LAW [verified 0x2986d..0x298dc; arg map checked with a
   per-instruction esp walk]:
       SEL = 4*K + cls
       K   = u32 [star_record + 0x00]  (star type index)
       cls = 4-band ladder on v = frndint(f32[star+0xd] + f32@ds:0x105e):
             v >= 0xdc -> 0 ; 1..0xdb -> 1 ; -0xdc..0 -> 2 ; v < -0xdc -> 3
       payload base arg = [wnd + 0xab]  (the preloaded cos_star buffer; t198
       right on this arg) ; x = s16 hi([child+3]), y = s16 hi([child+5]).
       CORROBORATION [measured 60.sav]: guest RAM holds exactly TWO '1.10'
       lib buffers; the one at member 0xfd2934 matches cos_star.shp
       byte-for-byte over its header+directory first 24 B (0x4078e8 is a
       different lib — directory differs at +0x10).
   K MEANING [measured]: census over 20 saves x 50 stars
   (scripts/r200_kcensus.py RC=0): K in {0,1,2,4,5,6,7,8,9,11,12}, a subset
   of {0..12} — matches starstat.txt's 13 types (mapgen.md S1); types 3/10
   absent from these 20 new-game saves (10 is the 1.48%-weight type).

4. RESIDUE ADJUDICATION [cited measurement, strict-close grade]:
   SEL reach = 4*max(K)+3 = 4*12+3 = 51 -> k40..k51 ARE ADDRESSABLE by the
   vendor selector law (need K in 10..12); k52..k54 are NOT reachable by any
   K <= 12 (would need K >= 13, outside the 13-type domain — a STARMAP
   selector can never address them). The dims-zero k40..k51 slots are the
   TYPE 10/11/12 x cls 0..3 cells of the 13x4 = 52-selector grid (k52..k54 =
   3 spares). FILE MEASURED t200: k40..k51 = the complete dims-zero set of
   cos_star.shp (dims u32 pair (0,0) at the law slot; span 0x1b each,
   file_offs 0x8f2..0xa1b contiguous). MECHANISM [inferred]: a dims-zero
   record walks zero rows, so the pip draw paints nothing; the blit's -1
   @0x5cb2b dims check is against the WINDOW shape-struct ([arg1]+4/+8,
   verified 0x5cabd..0x5cad4), NOT the record — no error code fires.
   => OQ-005 SHRINKS for cos_star: 12 residue records are now provably
   addressable-and-empty (rare star types' pips), 3 (k52..k54) are provably
   UNADDRESSABLE. What REMAINS OPEN is WHY the slots are empty (vendor data
   defect vs a dims-location unknown) — still player/vision territory, row
   stays OPEN. NOTE the payload arg [wnd+0xab] must be the TRANSFORMED
   runtime table (S12 decisive negative: verbatim file bytes would make
   payload+8+8*sel read the u64 directory and desync at sel=2; t64 already
   proved raw payloads are never drawn against) — which table holds the
   cos_star runtime entries keeps the slot-identity residue alive.
   HONEST NEGATIVE [measured 20/20 saves]: zero dwords anywhere in guest RAM
   equal member 0xfd2934 — no COSMOSWnd object existed in the corpus (ring
   = title/new-game states), so [wnd+0xab] itself is a live-capture-class
   residue like the t198 cache globals; the SEL LAW (the selector ARG) is
   fully static-verified regardless.
5. SITE 0x2a223 IS NOT STAR ART [verified]: cache 0x9f10c slot u16 [0x6fd96],
   SEL in {9 ALLIANCE state, 8 WAR state, -1 skip} from the t189 relation-
   state byte (table 0x12fd6 + 0x1ee stride), fixed x=0xe y=3, gate skips
   own-race. A relation-badge blit in the cosmos window, not STAR_SHAPES
   (STAR_SHAPES is drawn ONLY via [wnd+0xab] at 0x298dc). Slot library
   identity stays in the t198 honest-negative family (zero direct writers).
6. PITFALLS (t200 session): functions_full.tsv sizes are HEX (int(x,16)) —
   a decimal read silently yields wrong spans; heredoc-with-unquoted-
   delimiter eats $var inside python (write scripts to files instead);
   in the installed capstone o.mem.base==41 does NOT mean ESP (resolve via
   ins.reg_name) and cdecl CALL preserves ESP — scripts/r200_espmap.py is
   fixed for both; invoke it with LO AFTER the prologue's `sub esp,N` (base
   P = esp right after that instruction).

## 7. WINDOW COMPOSITION LANDED AS CODE (t276, 2026-11-02)

The S1-S4 laws are now wired in rewrite/src/ui/planetwin.{h,cpp} (pure, no
SDL; module template hudlayout.h t264). Working notes docs/re/_wip_t276.md.

1. PANEL TABLE [verified windows.txt lines 1536/1553/1570/1587/1604, joined
   against the SHIPPED file by the test]: kPlanetPanels[5] carries
   (rect, SENDMESSAGE, SENDPARAM1, HELPINDEX) verbatim — PLRES 7,7..114,106
   (50,0,plres), PLIND 123,7..230,106 (50,1,plind), PLPRO 239,7..346,106
   (50,2,plpro), PLPOP 355,7..454,106 (50,4,plpop), PLBUILD 463,8..632,106
   (51,1,plbuild). File order == left-to-right (disjoint X-bands, uniform
   9 px gutter from x=7; PLPOP 100 px INCLUSIVE = the t254 grid anchor;
   PLBUILD Y0=8 is the only off-grid edge). Parent PLANETALLOC TYPE 7
   0,0..639,479 msg 3; children PLANLIST (10) and PLSQUARE (14) are NOT
   panels — planetPanelFor returns nullopt inside them.
2. DISPATCH [verified S2]: ui::paintKey(msg,param) implements the two
   remaps (param 4 -> 3; msg 51 -> 4). THE REMAP IS LOAD-BEARING: PLBUILD's
   SENDPARAM1 is 1, which without the msg-51 override collides with PLIND's
   key 1 — mutation-proved catcher: deleting `if (sendMessage == 51) key = 4;`
   fails planetwin_dispatch_key_law_t276 (the five panels must key 0..4
   exactly once each, and key == enum index == file order).
3. HEADERS [verified static.txt, joined byte-exact by the test]: #147
   'Under Construction at %s', #148 'Being Refitted at %s', #149
   '\\nMoving to Planet', #150 '\\nMoving to Starlane' (FILE bytes carry a
   literal backslash-n; module constants carry a real newline — loader-
   interprets law [inferred], both forms pinned), #151 '%s  (%d Planet%s
   Occupied, %d System%s Controlled)' and #152 '%s  (%d Ship%s, %d more
   allowed)' (DOUBLE SPACE byte-exact, asserted directly), #153 'Player
   Species', plural pair #28 ''/#29 's'. PLURALIZATION for #151/#152 is
   singular-iff-==1 [inferred — the pair's ==1 use is cited only for the
   ability countdown, aicode.md §8.2]; live witnesses are plural only
   ("(60 Planets Occupied, 26 Systems Controlled)", "(25 Ships, 12 more
   allowed)"). The planets count fed to #151 must be the MAINTAINED counter
   (PROOF 3: heap-window u16, NOT the table count — 80 vs 60 @t1086);
   formatPlanetHeader takes it as an argument, nothing derives it.
4. GAUGES + POP + ICON [wiring, laws cited upstream]: planetGaugesFor =
   {gaugeSelector(res +0x46), gaugeSelector(ind +0x44), prosSelector(pros
   +0x48)} over Campaign::channelWordsFor (seed-2024 campaign: selectors
   match per-star and sit on the S3 ladder bounds); popPanelFor composed
   with origin (355,7) keeps every cell + 9 px sprite inside the PLPOP rect
   (the t33 cap<=100 clamp is what guarantees it); plbuildIcon =
   data\\planitem.shp identity, CITED only for 34 -> k34 (shp.md S23.4),
   domain 0..39 (40 recs, shp.md S23.3), boundary edges tested.
5. TESTS: tests/test_planetwin_t276.cpp, 8 cases, suite 158/0. No OQ row
   moved (composition of already-cited laws; the planitem identity extension
   for 39 items stays an OQ-005 contact-sheet fold, the pluralization stays
   [inferred] — strict-close unaffected).

## 8. STATUS-SIDE PLANETS LIST LANDED AS CODE (t402, 2026-11-15)
The rail-opened PLANETS LIST (state 10 STATUSWND child STATPLANLST, windows.txt
ln1019/1504) is now a real screen in the rewrite: rewrite/src/ui/statuslist.{h,cpp}
(pure law, compiled into run_tests per the planetwin precedent) + the ui.cpp
status painter/click branch. Laws, all cited in statuslist.h headers:
- ROW STRING (0x50647..0x5091f): line1 = "%s (%s %s Planet)" (#136) with size
  word table static.txt #41-45 (Tiny..Enormous) and type word table #46-56
  (Husk..Cornucopia) — the vendor reads them via pointer tables indexed by the
  planet-record +0x14/+0x16 WORDs; the rewrite indexes its own sizeIdx/terrainRow
  (content-anchor census scripts/r402_sizetype_census.py PASS: slot order ==
  runtime table order). Self-Managed substitution (#137) at 0x5077f.
- LINE2 (0x507fc..0x508d5): "Building %s%s" (#140); suffix " - No Progress"
  (#138) on the 0xffff sentinel leg, else " - %d day%s until completion" (#139,
  singular iff days==1, pair #28/#29 cited 0x5084e/0x50855); no-project leg
  "No Project" (#141) + "   (No Free Population)" (#142, THREE leading spaces,
  appended iff pop==used, 0x508da).
- DAYS LAW = FUN_0x47010 verbatim shape: ind<=0 -> 0xffff sentinel, else
  (cost-acc-1)/ind+1. Automation x3 leg (FUN_0x394d8) NOT modelled — named seam.
- MEMBERSHIP t249 law (owner==player planets only); HEADER = #151 via
  planetwin::formatPlanetHeader (t248 PROOF 3 maintained counter); row pitch 112
  + three visible rows MEASURED on work/screens/t3/planets_header_t1086_after_open.png
  (selection markers native y-centres 135.6/248.8/360.8).
PINS: tests/test_statuslist_t402.cpp 7 cases (word tables joined vs SHIPPED
static.txt; both templates byte-exact; days law; membership+window clamp;
header counts; row geometry). MUTATION 8/8 CAUGHT (M0 word-table content,
M1 days division, M2 singular law, M3 self-managed leg, M4b zero-ind wrong
sentinel — original M4 ind<0 mutant was a SIGFPE crash not a clean catch,
skill rule 7 re-scope —, M5 scroll overrun, M6 hit off-by-one, M7 header
systems). Driver scripts/t402_mutate.py reverts by FILE COPY (/tmp snapshot) —
the land was uncommitted, git checkout would have destroyed it (skill rule 1).
WITNESS scripts/t402_status_witness.sh (Xvfb): rail STATUS opens the screen,
scroll x2 lands ("ui status scroll down 2"), row click selects ("ui status
select Amoroso"); shots /tmp/t402_shots/ show "Amoroso I (Small Husk Planet)"
/ "No Project" rows and the #151 header "(2 Planets Occupied, 1 System
Controlled)" with correct singular/plural — D11 "planets list screen is wrong
and unusable" is no longer true of the rewrite. D11 ITSELF stays open until
the USER ruling (strict-close).

## 9. PLANET VIEW (STATE 17) + PROJECT-SET LAW LANDED AS CODE (t406, 2026-11-16)
The status row click now OPENS the planet display (planet.txt info05), and
the PLBUILD panel opens the project list whose click SETS the project
(planet.txt info04). Laws, citations in rewrite/src/ui/planetview.h:
- MEMBERSHIP UPGRADE: the list holds ONE COLONISED planet per owned star
  (t248 PROOF 1/2 owner-byte law; the port's PlanetState is per star). The
  old per-star-record-NAME loop fabricated uninhabited rows — the machine
  form of D13 "displays planets I don't own".
- ORDER LAW fn 0x38840 cmd0 (r331_disasm verbatim): queue-empty 0x388e2 &&
  item<39 0x388ec && (pop-used) >= UPOP 0x388f7..0x38922; reject stores
  NOTHING (silent, SOUNDCHANNEL 0); acc word untouched (resets 0x39290);
  the cell stays the t43 completion picker. The 0x3892a leg is UNRESOLVED
  and unexercised (honest negative).
- ROWS TOP MEASURED 117 (t3 capture table border native 116.8; art header
  cells y 48..85 on 10status k0) — kills the t405 "na" clip; text columns
  follow the art cells (icon 136..167, text from ~200).
Full working log: docs/re/_wip_t406.md F0-F9. Pins test_planetview_t406
x4 (suite 360/0); witness scripts/t406_planetview_witness.sh PASS.

## 10. STATUS BACKDROP + ROW GEOMETRY — MEASURED CORRECTION (t417, 2026-11-17)
Two S8/S9 claims are REFUTED by cited measurement on the very capture S8
cited (work/screens/t3/planets_header_t1086_after_open.png); full numbers
docs/re/_wip_t417.md F1-F5:
- THE BACKDROP IS NOT 10status k0. Registration of the decoded k0 index
  plane (game.pal colour space, scripts/t417_k0_register.py) against the
  t3 vendor capture = 4.5% exact; k0's navy interior (idx 242, 12,32,48)
  vs the vendor's BLACK interior. windows.txt binds no SHAPEFILE to state
  10 (TYPE-100 census: only 0,1,3,7,8,13,16,20,TESTDLG). The vendor status
  screen is CODE-DRAWN chrome: black interior, perimeter mottled texture
  band (x0..6/x633..639/y0..6/y472..479), per-pixel dark header speckle
  y8..36, divider ramp y38..46 to solid (33,56,57) at y46, left border x7
  (33,56,57), NO row separator lines. The port's ui.cpp full-frame k0 blit
  is the D15 "background uses an unused image" defect (k0 = the D1
  "A-series historical curiosity" asset).
- ROW GEOMETRY: rows top 57 (flag-box bands 57/198/339), pitch EXACTLY
  141 (column-profile autocorrelation, single peak 0.634; user original
  agrees ~140), exactly 3 visible rows (57+3*141=480). The t402 pitch 112
  was fit to the surface-THUMBNAIL art-centres (135.6/248.8/360.8 = row
  top + ~78), not row tops. Selection marker: RED x16..69, top+2, h~24.
Fix implementation (constants + backdrop law + pins) = STATE t417b — LANDED
2026-11-17 (t417b): ui/statusbg.{h,cpp} pure law + pins; witness
scripts/t417b_statusbg_witness.sh + t417b_witness_census.py VERDICT PASS
(including the census-caught weights/modulus bug: first-draft weights summed
119 vs modulus 98, starving the rare teals — rekeyed to sum EXACTLY 98);
suite 413/0. Working log docs/re/_wip_t417.md F8-F9.

## 11. PLANET-VIEW GRID + ISOMETRIC + ADJACENCY LAWS MEASURED (t418, 2026-11-17)
Implementation deferred to t418b; full derivations docs/re/_wip_t418.md F1-F5:
- GRID (FUN_000395c4/0x3965c, work/r331_disasm.txt): 15 row-slots per size
  class; valid cols B[size][row]..B+C; cell = cumWidth(size,row)+col-B.
  B = grid B tokens 45..119 (DAT 0x7445c) + C = grid C tokens 120..194
  (DAT 0x744a8) of planitem.txt (loader FUN_00037fc0, t294). The t294
  loader skipped grid B "no consumer" — grid B's consumer is NOW CITED.
- ISOMETRIC (paint body 0x3b96c, work/t198_planwin.asm 0x3bb2c..0x3c26d):
  center = origin + col*(34,17) + row*(17,-34); x-cursor 110 +17/row (end
  365), y 410 -34/row; tile diamond 68x34; hit |dx|/34+|dy|/17<=1; bare
  fill pal[150]; per-class colour table 0x892ac UNRESOLVED (named seam).
  [SUPERSEDED t421 — see §12: the per-class reading was a MISPARSE; uniform
  pal[150] IS the vendor law.]
- ADJACENCY (checker 0x385b7..0x3870d): four probes (row±1,col),(row,col±1)
  via 0x395c4; ACTIVE (word+2 bit0) neighbour refuses an inactive new item;
  skips cell>=+0x18, own-ACTIVE, item 5, item 38.
- DISC: vendor provenance inside 0x3b96c UNRESOLVED (0x3b98b = 17np k4/k5
  backdrops); port default planal[terrainRow].record(sizeIdx) [inferred].
  [t428c RESOLVED for k4: k4 IS blitted — registration anchor screen (7,115)
  = the 0x3b9c0 pushes; scripts/t428c_field_register.py z-test + shuffle
  control; docs/re/_wip_t428c.md F2. k5 registers too (screen (224,107),
  z=18.6) but only 14.6% — widget/selector open. The lattice index law is
  15*[planet+0x14] + row for BOTH B and C reads (_wip_t428c F1) — the port's
  rowOffset[psize][row] at ui.cpp:1767 already matches.]

## 12. THE 0x892ac 'PER-CLASS COLOUR TABLE' IS REFUTED (t421, 2026-11-17)
Full derivation docs/re/_wip_t421.md F1-F5; probes scripts/
r1_t421_referrer_census.py + r1_t421_c3_runtime.py (RC=0).
- COPY SITE (ascend_restored.bin 0x3c274..0x3c2d9): mov $0x960000 stores the
  SAME immediate into ALL FOUR vertex colour slots (esp+0x268/0x280/0x298/
  0x2b0 of the 24B-stride diamond record), then mov $0x892ac,%esi is an
  UNINDEXED immediate copy of 8 bytes to esp+0x310 (movsd x2). The only esi
  write in the 13-insn window is the load itself. A per-class table cannot
  be addressed by a constant; the t418 "selects per-something-per-class"
  reading was a misparse.
- CENSUS: capstone detail-mode operand walk over the whole code span finds
  EXACTLY ONE referrer of 0x892ac in the image (0x3c2a3); zero data-region
  pointers point into the block. esp+0x310 has exactly two refs in the
  painter (the copy target; overwritten at 0x3c5b4) and callee 0x61770 never
  reads the caller stack — the 8 bytes {00 00 01 03 01 03 02 02} are a
  fixed draw-parameter artifact with no per-class consumer.
- RUNTIME: mem[B+0x892ac] byte-verbatim in 178/178 independent saved runs
  (+ deepest slot 60); no writer in any captured state.
- CONSEQUENCE: the port's uniform pal[150] fill (t418b) MATCHES the cited
  law; no rewrite delta; the seam leaves the live re-check list.

## 13. THE FOURTH PAINT-BODY BLIT: 17np k5, PLANLIST-GATED (t428e, 2026-11-19)

Full working log: docs/re/_wip_t428e.md (E0-E7). Durable laws:

- SITE [verified work/t198_planwin.asm 0x3c7bc..0x3c82d]: after the lattice
  row loop exits (0x3c4ed jle; bound WORD[planet+0x1a]), the body looks up
  widget 0x1f06 via 0x56d1c(game obj 0x7a35c) and, IFF DWORD[widget+0x35]==-1,
  fetches 17np (lib slot esp+0x370 = WORD[0x6fd9c] = 44) RECORD 5 (immediate
  push $0x5) and blits via 0x5caac with struct {112, stale, 528}. No ret
  exists between the head (0x3ba5e) and this site: every paint reaches it.
- WIDGET IDENTITY [measured]: 0x1f06 + 0x82bb0 = 0x84ab6 = "PLANLIST"
  (adjacent ..\planwin.cpp). Control: RESWIN imm 0x2c0c + 0x82bb0 = 0x857bc
  = "RESWIN" — the pool-relative law (REFUTED-ROUTES t344) holds for 0x56d1c
  name immediates.
- ORIGIN [open]: 0x5caac composes x = p4 + struct[+4] + *(payload+0x10), y
  twin (work/combat_decomp/5caac.c:58-64), and this site pushes ONLY p1,p2 —
  p3/p4/p5 are frame leftovers; payload rect fields are runtime cache state
  (shp.md S12.2). Witness B: k5 peak 1566/10748 (14.6%) at screen (224,107)
  (permute control ~360), but (112,120)=56, (120,120)=43, (408,296)=28,
  (0,0)=436 [scripts/t428e_k5_origin.py]. NOT ported (strict-close).
- BLIT-2 CENSUS NEGATIVE [measured]: no size-class record registers at
  (408,296) on B (rect 71% pure black) -> blit-2 stays unported; law stands
  (t428d F4).

## 14. THE k5 BLIT IS GATED OFF LIVE — ORIGIN QUESTION CLOSED AS A
## NON-QUESTION; (224,107) PEAK = FALSE POSITIVE (t428f, 2026-11-19)

- LIVE GATE WITNESS [measured, run work/r1/dbg-t428f-20261119-210504, tool
  scripts/r428f_k5_session.py]: BP at 0x3c7cd fired on the planet-detail paint
  (Oct-29 RESUME.GAM t1086, Planets click -> row click; blit1 control fired
  same paint). eax = 0xfe6814 = widget head (magic 0x12345678, NAME@+0x20
  "PLANLIST"); DWORD[widget+0x35] == 0 -> cmpl $-1 FAILS -> 0x3c835; the k5
  fetch+blit NEVER executed (k5_blit leg armed, 0 fires). Offline corroboration
  [measured]: bank-t251-live1255 20/20 slots PLANLIST+0x35 == 0; 0/126
  magic-records in RAM hold -1 there.
- ARG-COUNT CORRECTION to §13/E6 [verified asm + live]: the k5 site pushes
  FIVE args explicitly — $0 (y), $0 (x), $5 (sel) before the 0x1fc34 fetch
  (Watcom clobber discipline), then handle + &struct; `add $0x14,%esp` proves
  it. "p3/p4/p5 are frame leftovers" RETIRED (the composition law
  5caac.c:58-64 itself stands).
- CONSEQUENCE: the t428c (224,107) registration peak (1566 px, z=18.6) is a
  FALSE POSITIVE — lattice/pop-art pixels sharing k5's speckle palette; the
  vendor draws NO k5 on this screen class. k5 STAYS UNPORTED (porting it would
  add art the original does not draw). Seam T428c-A CLOSED.
- RESIDUAL (banked, unchased): what sets widget+0x35 == -1 — writers of -1:
  0x3ab24 (bulk init after the 0x56ce4 widget loop, also +0x39=-1, +0xab=0xff,
  +0xac=-1), 0x3d3a7 (button-handler branch); 0x3d765 clears +0x35/+0x39 to 0.
  k5 would paint at (0 + struct[+4] + dir[+0x10], 0 + struct[+8] + dir[+0x14])
  in such a state — no witness of that state exists in any captured screen.
- HARNESS LAW [measured]: cold-leg censuses must POLL-BY-BREAK (BREAK -> EV
  eip -> attribute -> bank; resume = BPDEL fired-index only + RUN) — the stock
  resume_and_rearm BPDEL * releases a pending halt at the NEXT cold leg
  unbanked (t428f attempt 1 lost exactly the gate stop this way).

## 14. THE TILE LATTICE PITCH + EDGE-COLOUR LAWS (tPL-V1, 2026-11-23)
Full working log docs/re/_wip_tPLV1.md F0-F4. Durable laws:

- PITCH [verified asm work/t198_planwin.asm 0x3bb19..0x3c274 + witness]:
  the paint record's SYMMETRIC +-0x22-offset field is X, the 0/+0x11/+0x22
  field is Y => centre(row,col) = (410 + 34*(col-row), 127 + 17*(col+row));
  col step (34,17), row step (-34,17), |det| = 1156 == the 68x34 diamond
  area => EXACT edge-to-edge tiling, NO gaps. The t418 F2 shorthand
  "origin + col*(34,17) + row*(17,-34)" TRANSPOSED the two cursors
  (|det| 1445, 80% coverage = the D26 "rows have gaps" complaint).
  VENDOR WITNESS scripts/tplv1_lattice_witness.py on
  work/r1/screens/t254/02_planet_detail.png: 100.0% edge support for the
  corrected law vs 26.0% for the transposed one; shifted-fit controls
  <=52.9%, baseline edge density 0.6%.
- EDGE COLOUR [verified asm 0x3bbd6..0x3bc52 + 0x3bd3a]: EXACT compares on
  the slot CLASS byte (BYTE[rec+0x10]+0): 0 -> pal 0 black, 2 -> 117 red,
  3 -> 146 green, 4 -> 255 blue, default 12 white (game.pal conv:
  (0,0,0) (190,44,16) (44,195,12) (0,0,255) (203,203,203)); a rock-flagged
  byte (class|8) matches NO compare -> white. The companion grey-ramp fill
  selector (7/8/9/10/13) is gated by widget byte +0x18b bit0 (0x3bbcb je
  0x3be53) and drew ZERO pixels in the witness. BOTH former seams CLOSED at
  bytes/bank-saves tPF-3d (docs/re/_wip_tPF3.md F15): bit0 is SET AT
  CONSTRUCTION (ctor 0x3a7cf `mov BYTE PTR [ecx+0x18b],0x5`, sole alloc chain
  0x577b5->0x3a750->0x3a7b0; the only other writers are an interactive
  `xor [eax+0x18b],0x1` toggle at 0x3ae66 and a set/clear helper pair via
  0x3ca85), and the [0x48c33]+idx*0x100 blocks ARE the fill MAPS — runtime
  heap 256-entry colour-translation tables read from banked saves (idx 0: 39
  distinct; idx 7/8/9/10/13: 103/92/80/83/112 distinct; filler 0x62d15 law
  `screen := MAP[old]` at 0x63023/0x63026; the fill INDEX is the ramp slot at
  [esp+0x364], NOT the class colour). The tile
  FILL stays the cited uniform 0x96=150 (t421).
- PORT: tileCenter corrected; tileEdgePaletteIndex new pure law; painter
  fills-then-outlines two passes so shared edges stay visible; the t418b
  invented (24,24,32) outline + rock-darker fill DELETED (no vendor basis).
  Pins planetgrid_lattice_t418b RE-DERIVED + planettile_edge_colour_tPLV1;
  suite 502/0/0. FORMAL PORT CENSUS CLOSED tPL-V1f (2026-11-24): census v2
  scripts/tplv1f_census_v2.py VERDICT PASS on a clean geometry grab
  (winpos + root-crop; the name grab failed because the window title flips
  "Ascendancy" -> "Ascendancy rewrite (P5a)" at RESUME). size-1 fill 11/11,
  adjacency 12/12 (3px-inside probes; the v1 "midpoint non-black" premise
  was invalid — class-0 tiles draw BLACK edges per 0x3bbd6, so the gap
  signature is a black INSIDE point, not a black midpoint), and an
  anti-vacuity control (law-A centres outside the painted union all black;
  mutant M-T1 re-transposing tileCenter -> census FAILS,
  scripts/tplv1f_mutate_census.sh). The v1 >=200-white-px premise is also
  invalid for the seed-5 home planet (all surface classes 0). Details
  docs/re/_wip_tPLV1.md F5.

## 15. THE PLANLIST FILL LAW 0x3b6f3 + THE CHECKER IS FULL ORDERABILITY (tPF-6b, 2026-11-26)
- SITE RECOVERED [verified]: fn 0x3aa0a is the PLANLIST widget's message
  handler (t428e E3 widget 0x1f06; entry eax=widget, dx=msgid, ecx=param).
  msg 0x33 (51) handler 0x3b6f3 FILLS the rows: gate byte DAT_0007458e ==
  byte[DAT_00043508+0x57] (fill runs only for the owner race); param 1 ->
  word[widget+0xae] := 0xffff FIRST; loop ecx 0..0x26 with UNCONDITIONAL
  skip of item 5 (0x3b76a je); append iff checker 0x3830c(item=dl, cell=
  word[widget+0xae] in ebx) nonzero; row record stride 5 (byte item @+0xb2,
  u32 0 @+0xb3); repaint 0x314e8+0x56ca4 iff count > 0 (count==0 leaves the
  PREVIOUS rows on screen — TPF6-A witness note).
- THE CELL IS ALWAYS -1 FOR HUMAN PLAY [verified]: the only msg-51 producer
  in the planet window is PLBUILD, SENDPARAM1 1 (windows.txt ln1615; the
  other msg-51 widgets ROTRIGHT/WEAPONS/BATROTRIGHT/RESROTRIGHT live in
  other windows — msg-id space is per-window, tPF-7a law). The armed value
  msg 5 writes into +0xae never reaches a fill. So vendor list membership =
  item<39 AND item!=5 AND REQUIRES AND FREEPOP, cell legs inert.
- CHECKER 0x3830c IS NOT PLACEMENT-ONLY (full body audit): LEG-A REQUIRES
  0x3835d (req!=0xFF -> race-mask word[0x74744] > req AND tech bit
  (1<<race) at req-UPOP row 0x7478b sar 0x18); LEG-B FREE-POP 0x383b3
  (acc = word+0x42 - word+0x4c + SBYTE UPOP(pending@+0x54) when pending
  != 0xff; pass acc >= UPOP(item); item 23 -> 0x39a9c replaces the verdict
  at 0x38422 — seam TPF6-SHIP: 0x39a9c = first-empty-cell word+2 bit0 AND
  0x402d8(race*160+0x12e16) > 0, semantics unrecovered); item==5 -> pop-leg
  exempt 0x38435; LEG-C cell 0x3843a (cell >= word[+0x1a] cell-count jumps
  to the final AND at 0x386fe — THE SENTINEL: cell -1 runs ONLY legs A+B).
  Flags word 0x73e46 = stride-0x28 item table +6 (bit0/race-table 0x12fb3
  grant, occupancy/bit2 grant, XOR surface-ring + rock + terraform +
  adjacency vetoes as banked tPL-B1/F10). Return -1 on PASS.
- PORT SHIPPED (planetview.{h,cpp}): projectOptionsFor now skips item 5
  always and applies freePop = pop - usedPopFor(star) >= upop for item != 23
  on EVERY open (armed and unarmed). Vendor acc nets to pop - ACTIVE-used
  because usedPopFor stores ACTIVE items only (pending addback cancels).
  The tPF-6 armed placementBlock filter REMAINS (port tile-first flow,
  justified by popup D6, not by the fill law). THE POPUP LEG TOO: the
  54-loop 0x3d579 calls the SAME full checker, so the ui.cpp popupButtonIds
  buildable-lambda now runs freePop + requiresAvailable + placementBlock
  (item 0xff demolish + item 23 exempt) — previously placementBlock only.
  Pins planlist_fill_law_tpf6b (3 legs: skip-5 both paths; free==0 keeps
  only upop<=0 + item 23; pop-up anti-vacuity) + planlist_popup_leg_wiring_
  tpf6b (source-text: lambda carries all three legs); fixture pop 0 -> 50
  (the old zero-pop premise was invalid under the new law — it emptied the
  list and made the filter checks vacuous). Suite 598 -> 600/0/0; MUTATION
  3/3 CAUGHT (M1 skip-5 removed: 2 fails; M2 free-pop leg disabled: 34
  fails; M3 popup lambda reverted to placementBlock-only: wiring pin 2
  fails).
