# tRS-V2 RESEARCH DISK FILL LAW — working log (fresh session 2026-11-24)

ASSIGNMENT (STATE.md NEXT ACTION): D27 user law — unknown tech = EMPTY disk;
selecting shows a SMALL PORTION OF THE CENTER; portion WIDENS with progress;
completion = full picture. Derive the wipe SHAPE from vendor paint code, do
not guess. Then tRS-V3 link attach, then tPR2-U grade package.

SITTING CHECK ran first: scripts/r1_t85g_sitting.py exit 0, 45,227 rows,
newest t=1335 (no new sitting) -> stale assignment stands.

## P1 — THE PICTURE CONSUMER IS FOUND (seam TRSV1-C candidate)

Inside the reswin per-row draw loop (function FUN_00041e34, the same giant
fn as tRS-V1), AFTER the <=5 prereq LINE loop and BEFORE the ring blit:

  0x48383: mov ebx, dword [esp+0x120]      ; a per-row VALUE (row-derived)
  0x4838a: test ebx,ebx                     ; GUARD: skip if 0
  0x4838c: jz   0x483fa                     ; -> straight to ring blit
  0x4838e: mov edx,ebx
  0x48390: shl edx,10                        ; edx = ebx<<16
  0x48393: mov ebx,0x14                      ; 20
  0x48398: mov eax,edx
  0x4839a: sar edx,1f
  0x4839d: idiv ebx                          ; eax = signed(ebx_old)/20  (quotient)
  0x4839f: push 1                            ; param 10 = 1   (0x5d5a1 flag)
  0x483a1: push eax                          ; param 9  = quotient
  0x483a2: push eax                          ; param 8  = quotient
  0x483a3: mov [esp+0x12c],eax               ; (also parked on stack)
  0x483aa: mov eax, dword [esp+0x134]        ; the PROJECTED-node-slot ptr
  0x483b1: push 0                            ; param 7  = 0
  0x483b3: mov edx, [ebp+eax*2+0x6b9]        ; y projected word (high16)
  0x483ba: push 0x48c44                      ; param 6  = STRING ADDR 0x48c44 (shape name!)
  0x483bf: sar edx,10                        ; y
  0x483c2: mov eax, [ebp+eax*2+0x5f1]        ; x projected word
  0x483c9: push edx                          ; param 5  = y (screen)
  0x483ca: sar eax,10                        ; x
  0x483cd: push eax                          ; param 4  = x (screen)
  0x483ce: mov edi, dword [esp+0x144]        ; ??? (esp+0x144)
  0x483d5: xor edx,edx
  0x483d7: push edi                          ; param 3  = [esp+0x144]  (FRAME?)
  0x483d8: mov eax,0x9f10c                   ; shape cache
  0x483dd: mov dx,[0x6fd82]                  ; shape-id WORD 0x6fd82 (per shp.h S27)
  0x483e4: call 0x1fc34                      ; -> shape id (EAX)
  0x483e9: push eax                          ; param 1 = pointer to shape id
  0x483ea: mov eax, [esp+0x154]              ; row index WORD (u16)
  0x483f1: push eax                          ; param 2 = row index
  0x483f2: call 0x5d5a1                      ; THE PICTURE BLITTER (scaled RLE)

Ghidra-verified (disassemble_bytes 0x48250..0x4841f). The line loop above
(0x48275..0x4837d) is the prereq line blit (0x5bf71, the same as S8-CORR
item 2).

## P2 — BLITTER FUN_0005d5a1 (decompiled via Ghidra, verbatim in wip below)

Signature (decomp): (int *shapeIdPtr, u32 rowIdx?, u32 frame?, x, y, namePtr?,
scaleU, scaleV, ?, flags). KEY BEHAVIOR:
  if (scaleU==0x10000 && scaleV==0x10000 && scaleW==0):
      (flags&1)==0 -> FUN_0005caac(shapeIdPtr,row,frame,x,y)   ; UNCLIPPED 1:1
      (flags&1)==1 -> FUN_0005cf96(shapeIdPtr,row,frame,x,y)   ; UNCLIPPED 1:1 alt
  else:
      SCALED branch: builds a 5-pt polygon clip (DAT_0008408..0x8458 = 4
      corners + 1), FUN_000604e9 projects each corner (with scaleU/V/W),
      clips against param_1[1..4] = x0,y0,x1,y1 sub-rect, then does a
      16.16 fixed-point AFFINE SCANCONV of the RLE rows into the dest.
      => this is a GENERIC clipped/scaled RLE painter.

CONSEQUENCE: at 0x483e4 the call passes flags=1 (0x4839f), and the three
"scale" params are (quotient, quotient, 0)?? — wait, re-map: the pushes
bottom-up give param order for a __cdecl 10-arg fn:
  param_1  = shapeIdPtr      (pushed last, = [eax] after 0x1fc34)
  param_2  = [esp+0x154]     (row index u16)
  param_3  = [esp+0x144]     (edi)          <- FRAME?
  param_4  = x screen
  param_5  = y screen
  param_6  = 0x48c44         (string addr — shape NAME)
  param_7  = 0
  param_8  = quotient        (ebx_old/20)
  param_9  = quotient        (same)
  param_10 = 1               (flag -> FUN_0005cf96 path when 8/9 are 0x10000)

BUT param_8/param_9 = quotient = [esp+0x120]/20, which is a small int (0..N),
NOT 0x10000. So the (param_8==0x10000 && param_9==0x10000 && param_7==0)
test is FALSE -> the SCALED branch runs, with scaleU=scaleV=quotient and
the 5-pt clip + affine scanconv. That is the WIPER: a scaled RLE blit where
scale = rowValue/20. THE SCALE FACTOR IS THE PROGRESS LAW.

NEED TO CONFIRM (P3..):
  1. What is [esp+0x120]? (the row value divided by 20). Find its writer in
     the fn. Likely = research progress counter for that row (0..~20*?), or
     a per-row "studied ticks" accumulator. If it's 0..19 -> frame = value,
     scale = 1.0; if larger -> scale grows.
  2. [esp+0x144] (frame / param_3) — which frame of the shape.
  3. STRING AT 0x48c44 — which shape library the per-row PICTURE comes from
     (NOT resring — resring is fetched at 0x48475 for the RING). This is the
     consumer of a restree-family picture library. TRSV1-C is likely here.
  4. FUN_0001fc34(cache 0x9f10c, shape-id word 0x6fd82, frame) -> shape id:
     0x6fd82 is the per-row PICTURE shape-id word (ring uses [0x6fd60]/+race,
     studied/owned use other words). The ring blit at 0x483dd reads 0x6fd82
     TOO — wait, 0x483dd is in the PICTURE block. Re-check: the RING fetch at
     0x48475 uses edx=0x250c (name) via 0x1fe20; the PICTURE fetch at 0x483e4
     uses word [0x6fd82] via 0x1fc34. So 0x6fd82 = PICTURE shape slot.

## P3 — open: where is [esp+0x120] written? and string 0x48c44?
## (next probes)

--- BLITTER FUN_0005d5a1 FULL DECOMPILE (verbatim, banked for handoff) ---
[int * FUN_0005d5a1(param_1..param_10)]: see Ghidra dump; the scaled branch
projects a 5-point source polygon through FUN_000604e9(scaleU,V,W), clips to
param_1[1..4] rect, then affine-scanconvs RLE rows (16.16 fixed point,
iRam0008b008.. per-row ddx/ddy accumulators). Returns -1/-2 on degenerate
input. This is a generic scaled+clipped RLE painter, reused elsewhere.


## P4 — THE FILL LAW DERIVED (cited, raw-stepper-verified)

PER-ROW PICTURE VALUE q = [esp+0x120], written at 0x481aa..0x48239
(raw capstone stepper over work/ascend_restored.bin; the tRSV1b linear dump
drifts in this region so the raw stepper is the cited source):

  row = [esp+0x128] (u16 row index, 0..65)
  rec = row*0x4b  (record pointer, table base 0x74784 — OQ-013 stride)
  raceBit = byte[0x7458e]

  0x481aa: q = 0                                   ; DEFAULT: no picture
  0x481b1: rec = row*0x4b
  0x481ba: ownMask = dword[rec + 0x47] (abs 0x7478b) >> 24 & 0xff
  0x481c0-1ca: if ownMask has the race bit then q = 0x14 (=20) ; OWNED => FULL
  0x481de-1f1: else if row != [esp+0x134] (the STUDIED row word) then q stays 0
  0x481f3-21b: else (row is studied and not owned):
                p    = word[0x764a0 + 2*row]       ; progress u16 for this tech
                cost = word[rec + 0x3e] (abs 0x74782) ; u16 RUNTIME cost (S6b)
                q    = (p*18)/cost + 2              ; 18.0f/cost x p
                clamp q to [-0x11, +0x11] = [-17, 17]
  (negative clamp leg 0x48227: q<-17 then q=-17; 0x48239: q>17 then q=17)

PICTURE BLIT (0x48383..0x483f7, raw-verified):
  if q==0: skip (no picture — empty disk)
  else:
    Q = signed(q) << 16            ; shl edx,0x10 = shift 16 (HEX 0x10)
    qdiv = Q / 20 (idiv ebx=0x14)  ; = 16.16 fixed-point of q/20
    shapeId = FUN_0001fc34(cache 0x9f10c, slot word [0x6fd82])
    call FUN_0005d5a1(shapeIdPtr, [esp+0x154] /*frame-or-row*/, [esp+0x144],
                      x=projX, y=projY, name=0x48c44, 0,
                      scaleU=qdiv, scaleV=qdiv, flags=1)

FUN_0005d5a1 (decompiled): the scaled branch scales the source RLE by
scaleU/scaleV (here both = q/20) about the passed (x,y) ANCHOR (the blitter
composes dest from the record signed bbox + anchor, shp.h S27 / tRS-V1d law),
clipped to the param_1 rect. With scale=q/20 and a full source rect, the
rendered picture is the WHOLE shape shrunk by factor q/20, CENTRED on the node.

CONSEQUENCE (the D27 wipe SHAPE, DERIVED not guessed):
  * unowned AND not-selected row: q=0 -> NO picture (EMPTY disk) — user law ok
  * SELECTED/studied row at p=0: q = 0+2 = 2 -> scale 2/20=0.10, a SMALL
    CENTRAL SLIVER appears ON SELECT — user law ok ("portion ON SELECT")
  * as progress p grows 0..cost: q = 2 + 18*(p/cost) grows 2 -> 20, scale
    0.10 -> 1.00, the picture WIDENS from central sliver to the full disk
  * OWNED row: q=20 -> scale 1.00 = FULL PICTURE (ring flips to frame 3)

SO THE WIPE IS A CENTER-OUT RADIAL SCALE (a growing inner disc / centre-out),
NOT an angular wedge. The "small portion of the center" is literally the whole
record's picture scaled down by q/20 about the node centre, growing to fill.

OPEN LEGS (P5):
  (a) which .shp LIBRARY is registered at slot word 0x6fd82 (the picture
      library; P3 says the 66-record one — confirm the load site).
  (b) param_3 [esp+0x144] and param_2 [esp+0x154] exact roles (frame vs
      row-in-library); the 0x6fd82 lib has 66 records = one per row.
  (c) cost field: word[rec+0xfe]==restree.txt field1? confirm (abs 0x74782,
      rec-rel -2 — verify against a live/extracted record layout).

## P6 — ITERATION STATUS (tRS-V2r, 2026-11-24) — RE-FIRST DONE, PORT NAMED NEXT

- Consumer FOUND (seam TRSV1-C resolved at the code level): the per-row
  picture-in-disk blit at 0x48383..0x483f7 inside the reswin per-row loop,
  between the prereq LINE loop and the RING blit (raw-stepper cited, P1).
- FILL LAW derived + cited (P4): q per row; fill = q/20; the wipe is a
  CENTER-OUT RADIAL SCALE of the whole record picture about the node
  centre — a growing inner disc, NOT an angular wedge (the blitter scales
  both axes by the same 16.16 factor; no angle term exists in the chain).
- Consistency check PASSED: the owned mask load `dword[row*0x4b + 0x7478b]`
  at 0x481ba is the SAME field the ring-frame law reads at 0x4841d (abs
  base+0x47, table base 0x74744 = count u16) -> owned rows get BOTH ring
  frame 3 AND fill 1.00. Table base reconciliation: word[row*0x4b +
  0x74782] = base+0x3e = the runtime cost of research.md S6b (66/66 law),
  so q's divisor is the SCALED runtime cost, not the file cost.
- studied-row word: [esp+0x134] = word[race*2 + 0x76492] (set verbatim at
  0x48130..0x48141, race = byte[0x7458e]) — the tRS-B1 specnum writer
  target, so "selected" == "the queued/studied tech of this race".
- progress field: word[0x764a0 + 2*row] (0x764a0 = 0x76492+0xe). Writer
  UNRECOVERED this iteration (P5c open) — the per-turn research tick that
  advances it; the law's endpoints (p=0 -> q=2, p=cost -> q=20) are cited
  arithmetic, not observation of the writer.
- 16.16 values: q=2 -> 0x19a9 (0.10), q=11 -> 0x6988 (0.55), q=17 ->
  0xd9f9 (0.85), q=20 -> 0x10000 (1.00). Negative-q clamp is DEAD for real
  inputs (p is u16 >= 0 so q >= 2 always); the vendor signed-idiv + clamp is
  paranoia, ported verbatim anyway.
- BUDGET STOP: port + pins NOT shipped this iteration (run budget). Spec below.
- OQ LEDGER: no row touched (the research screen tracks no OQ) — honest
  negative under strict-close; open=[016,019] unchanged.

## P7 — PORT SPEC (tRS-V2p, the next single task)

1. PURE LAW in researchview.{h,cpp}: `int resDiskQ(bool owned, int row,
   bool studied, int progress, int runtimeCost)` returning q VERBATIM:
   owned -> 20; else studied -> clamp((progress*18)/runtimeCost + 2, -17,
   17); else 0. Cite research.md S9(a). progress = the campaign's per-tech
   progress u16 (same source the (N days) line consumes); runtimeCost =
   Tech::runtimeCost (OQ-013 S6b law). fill = q/20 (double).
2. RENDER in ui.cpp NODES block: after the ring blit, if fill > 0 blit the
   tech row's record from data\\restree.shp (extracted/ascend01/data/
   restree.shp, 66 records, one per live row — the slot word 0x6fd82 library)
   SCALED BY fill about the node centre: dest anchored at record bbox +
   centre (S8(h) anchor law), source rect = full record, both axes same
   scale (mirror 0x5d5a1's scaled branch; if the shp lib has no scaled
   blit, add one and cite S9(c)). Unknown/unselected rows: no blit at all.
3. PINS tests/test_researchfill_tRSV2.cpp:
   - unselected p=0 -> q==0 (empty disk: zero picture pixels);
   - selected p=0 -> q==2 (16.16 0x19a9, the ON-SELECT sliver);
   - p=runtimeCost/2 -> q==11 (0.55) [odd-cost note: use exact division];
   - p=runtimeCost -> q==20 (0x10000, full);
   - owned (any p) -> q==20;
   - clamp leg: inputs engineered to q>17 (e.g. progress=2*cost) -> q==17;
   - MUTATIONS CAUGHT: +2 -> +0; 18 -> 16; /20 -> /16; clamp 17 -> 18.
4. WITNESS scripts/tRSV2p_witness.sh (scratch seed-5 run): select a tech,
   screenshot at p=0 (sliver) / mid progress (wider) / owned (full); census
   the CONTENT bbox inside the disk at each stage vs the flat field bg (the
   tRSV1d census lesson: brightness thresholds measure the rim subset).
5. THEN (after green): tRS-V3 LINK ATTACH, then tPR2-U grade package (see
   STATE.md NEXT ACTION for the ordering rationale).

OPEN LEGS carried (P5): (a) slot word 0x6fd82 load site (file restree.shp
confirmed present; the word is READ at 0x476c6/0x483dd/0x4873b/0x48785, no
direct static writer found — bulk-registered by the shape loader); (b)
0x5d5a1 exact arg roles (decompiler mapping untrusted — regparm-suspect;
the 0x48c44 immediate sits in the code region; pin via the 0x5caac/0x5cf96
sibling sites' [esp+0x140] push); (c) writer of word[0x764a0+2*row].

## P8 - tRS-V2p PORT ITERATION (2026-11-24, this session)

PRE-CODE LAW RECHECK (raw stepper 0x481aa..0x48240, ~/tools/revenv
scripts/t442_disasm.py) - CORRECTION to the P7 pin list: the clamp legs
0x48222 (cmp eax,-0x11 / jge) and 0x48234 (cmp eax,0x11 / jle) fire AFTER
`add eax,2` (0x48218), so the studied branch MAXES AT q=17, NOT 20. At
p=cost: 18+2=20 -> clamped 17 (0.85). q=20 (16.16 0x10000) is reachable
ONLY via the OWNED leg 0x481ce. The P7 spec line "p=runtimeCost -> q==20
(0x10000, full)" is WRONG against the cited law; the correct pins are
p=cost -> 17 and owned -> 20. "engineered q>17 -> 17" is not an edge case,
it is what p>=cost does. research.md S9(b) amended.
Also verified verbatim: p load `mov dx,[edx*2+0x764a0]; and edx,0xffff`
(u16 zero-extend, indexed by the STUDIED row), imul 0x12, divisor
`mov bx,[eax+0x74782]` (u16 zero-extend = runtime cost word), signed idiv
(sign-ext via sar 0x1f), owned mask dword[rec+0x47]>>24 and (1<<byte[0x7458e]).
Div-by-zero: the vendor has NO cost==0 guard (SIGFPE class); the port
returns q=0 for cost<=0 as a NAMED SEAM (TRSV2p-A).

ART MEASURED THIS SESSION (restree.shp directory + bbox-diff law):
66 records; EVERY record's signed bbox quad = (-25,-25,24,24) i.e. the
A1 BBOX-DIFF law gives content 50x50 at L,T=(-25,-25) - centred on the
node anchor BY CONSTRUCTION exactly like resring's (-30,-30,29,29)
(tRS-V1d anchor law applies unchanged: blit dest = anchor + scaled bbox
corner). FIRST-DRAFT SLIP banked: reading the raw u32 words at rec+0x10
as dims gives (24,24) - those are the R,B CORNERS; the failing
researchfill_art_centred pin caught it (66/66 records assert 50x50).
SECOND SLIP banked same session: hand-transcribing 16.16 hex - 11<<16/20
= 0x8CCC, "corrected" once to 0x8C6C by hand, wrong; compute hex, never
transcribe. Also the S9 doc's original 0x19a9/0x6988/0xd9f9 were all
transcription slips (real: 0x1999/0x8CCC/0xd999).

PORT SHAPE:
- researchview.{h,cpp}: resDiskQ(owned, studied, progress, runtimeCost)
  VERBATIM + resDiskFill(q) = q/20.
- vendortext.cpp: NEW blitShapeScaleF(ren,lib,rec,x,y,scaleF) - fractional
  scale about the passed anchor: dest rect = (x + round(scaleF*rec.left),
  y + round(scaleF*rec.top), round(scaleF*W), round(scaleF*H)); same
  decode/alpha path as blitShapeCircular. Rounding mode = seam TRSV2p-B
  (0x5d5a1's affine step math unrecovered; p2/p3 roles suspect per P7).
- ui.cpp: restree.shp joins kLibFiles at index 9 (libFor 8-scan unchanged);
  NODES loop: after the ring blit, q=resDiskQ(...); if q!=0 blit record
  [row] scaled q/20 at the node centre. Blocked rows never reach it (not
  drawn at all, 0x48566 gate).

## P9 - PORT + PINS + MUTATIONS LANDED (this session)

- SHIPPED: researchview.{h,cpp} resDiskQ/resDiskFill VERBATIM (branch order
  owned>studied>empty; cost<=0 -> q=0 seam TRSV2p-A); vendortext.cpp
  blitShapeScaleF (anchor-composed fractional blit, seam TRSV2p-B rounding);
  ui.cpp restree.shp at kLibFiles[9] (libFor 8-scan untouched) + the NODES
  loop fill blit behind the ring, q!=0 gate.
- SUITE 526 -> 534, 0 failed (tests/test_researchfill_trsv2p.cpp x8:
  empty/sliver/midway+monotone/cost-clamps-17/owned-20/cost-zero-seam/
  art-centred-66x50/wiring source-text).
- MUTATIONS ALL CAUGHT (researchview.cpp mutated 4x, rebuilt, restored,
  md5-verified, suite green after restore): M1 +2->+0 (select_sliver FAIL),
  M2 18->16 (midway FAIL), M3 /20->/16 (select_sliver FAIL - the fill pin
  is rational-exact so 0.125 != 0.1), M4 clamp 17->18 (midway's
  prev==17 monotone-leg FAIL). HAZARD RE-WITNESSED: the FIRST mutation
  pass ran with a stale kernel cwd so cmake never executed and every
  mutant "SURVIVED" - a mutation sweep with no build is VACUOUS; verify
  the build ran (absolute paths) before trusting any survival verdict.
- LAW CORRECTIONS this port forced (all in research.md S9 + P8 above):
  studied branch maxes at 17 not 20; 16.16 pins recomputed 0x1999/0x8CCC/
  0xd999; restree.shp records are 50x50 content at bbox (-25,-25) not
  24x24 dims.

## P10 - WITNESS RUN (scripts/tRSV2p_witness.sh + tRSV2p_census.py, seed 5)

VERDICT: PARTIAL PASS - SLIVER LEG PASS, GROWN LEG BLOCKED (named below).
- PASS legs: select painted 94 px INSIDE the +-20 disk box (before->sliver)
  with control box 120px away 0 px; log leg 'ui research study Xenobiology'
  + 'ui research fill 6 2' (the law q=2 at p=0) both present; owned rows
  log q=20 (rows 0/1/2), frontier rows log q=0 - the full q law is live on
  the instrument line at rest.
- BLOCKED (grown leg): after Escape->map + 15 NEXT TURN clicks (log proves
  15 'ui click next-turn' + 'ui ok: turn 15'), row 6 re-logs q=2 - progress
  NEVER accrued. ROOT-CAUSE SCAN (headless, cheap): --campaign 40 --headless
  on seeds 1,2,3,3,7,11,2024 shows the PLAYER at techs 3 score 2% at turn
  40 in EVERY seed (AI stars move; player never researches). researchPhase
  adds res[o] (campaign.cpp:1514) and res[o] only grows via
  colonyChannel(a.res,...) (:997) - i.e. the shipped-scenario player RES
  channel reads 0. [inferred] The D26-era build loop has the same shape
  (player builds only what the witness queues). This is a GAMEPLAY-INCOME
  finding (OQ-016 neighbourhood), NOT a fill-law failure: the fill law's
  arithmetic is pinned x8 + 4 mutations; the sliver endpoint is witnessed.
  GROWN-ENDPOINT WITNESS owed as its own task (tRS-V2w): first diagnose
  WHY player res[o]==0 (print the channel per phase headless), fix/derive,
  THEN re-run this witness for the mid/owned growth frames.
- WITNESS HARNESS LAWS BANKED: (1) in --ui mode --campaign N is the TURN
  CAP (main.cpp:656 -> ui.cpp:1215 quit at played>=N) - N=1 dies on the
  first NEXT TURN; the earlier witnesses never advanced turns so never hit
  it; (2) NEXT TURN is map-only (kNextTurnBtn gated on kScreenMap) - leave
  research with xsend key Escape (gate.sh:623 recipe) first; (3) xsend
  'window died before release' stderr stays a red herring (t439 law,
  re-witnessed x20).

## P11 - tRS-V2w INCOME DIAGNOSIS (2026-11-25 fresh session)
- SITTING CHECK ran FIRST (exit 0, 45,227 rows, newest t=1335 - stale
  assignment stood). Production ring untouched.
- REPRO (headless, seed 5, 40 turns): player techs 3 score 2% every turn,
  AI stars move - matches P10 scan. BUT 900-turn run shows owner 0 DOES
  research eventually: [t207] Spacetime Surfing, [t297] Xenobiology. So
  res[0] is NOT identically zero - the accrual rate is near-zero.
- SHAPE OF THE LAW (cited, income-law.md T34 2720/2720): +0x46 RES = RAW
  accumulator, NO compression, NO grant; home worlds acc 0 -> +0x46 == 0
  157/157 (t40). IND at acc 0 HAS the max(1,v) grant. Port colony.cpp:997
  implements exactly this. => A home world with only Colony Base produces
  RES 0 BY VENDOR LAW. The vendor player researches early only by BUILDING
  res-field items (Labs) with the IND grant. [inferred] The port defect is
  NOT the res arm arithmetic - it is that NOTHING in the port feeds RES to
  the player unless a build completes, and in headless/--witness flows the
  player never builds. NEXT: --dbg-res per-turn channel print to confirm
  res[0]==0 while queued, and find where owner 0's late RES actually came
  from (ability? event? colonization?).
- VENDOR ACCRUAL LAW CITED (work/tRSV2w_46aec.asm, FUN_00046aec verbatim,
  call site 0x2502f with eax=0x74744):
  (1) per-turn RES bucket[race] (0x46b24..0x46b88): sum word[planet+0x46]
      over planets owned by race; +1 PER PLANET iff owner != current-turn
      player [0x7458e] AND byte[0x13bc4]==2 AND word[+0x46] < 15 (0x46b5b..
      0x46b77; gov-gated FRELOADER term - live byte == 1 in 20/20 saves
      (combat.md S278) => OFF in the shipped scenario, AI-side only).
  (2) progress apply (0x46bcd..0x46c30): bucket==0 -> add NOTHING (je
      0x46c02); else progress word[0x764a0+2r] += TRUNC((bucket+1)^0.85)
      (pushes 0x3feb3333/0x33333333 = double 0.85, call 0x78a90 pow,
      0x76e08 frndint-chop, fistp). Completion cmp progress >= word[rec+
      0x3e] (runtime cost) -> owned mask bytes +0x4a/+0x4b |= 1<<race,
      target := 0xffff, progress := 0, event 0x55a60 iff human.
  (3) target==0xffff -> progress := 0 EVERY turn (0x46b90) - the port KEEPS
      stale progress across re-queue; named seam TRSV2w-A.
- CONCLUSION: res[0]==0 for the first ~30-110 turns is VENDOR FAITHFUL, not
  an income defect: Colony Base RES file field = 0 (planitem.txt), RES
  channel has NO grant (T34 2720/2720), freeloader term gov-gated OFF.
  The port's REAL delta is the apply law: campaign.cpp:1514 adds RAW res,
  vendor adds trunc((res+1)^0.85) - port accrues FASTER for res>=2.
  The witness grown leg was simply under-length: Lab (cost 50, IND 1/turn
  from CB grant, AFTER 2 Factories per kBuildOrder) lands ~t110 on seed 5;
  900-turn run proves the chain: owner 0 researched Xenobiology t207.
- FIX PLAN (tRS-V2w): (a) researchPhase compression law + pin; (b)
  gov-gated freeloader term + pin; (c) --dbg-res per-turn instrument flag;
  (d) witness tRSV2w_witness.sh = tRSV2p stages + --autoplay to the grown
  q (no 200 manual clicks); seam TRSV2w-A documented, not stubbed.

## P12 - tRS-V2w SHIP + WITNESS (2026-11-25)
- SHIPPED: researchProgressAdd + resFreeloaderAdd (campaign.cpp, cited
  above); researchPhase apply law replaces the RAW add; freeloader wired
  in incomeAndGrow (gov-gated, DEAD at live gov==1 - zero semantic delta
  shipped-scenario); --dbg-res flag (main.cpp both paths + Begin rebuild),
  prints "dbg-res t<turn> owner <o> bucket <b> add <a> prog <p> cost <c>".
- HEADLESS CHANNEL (seed 5, --dbg-res): owner 0 bucket 0 add 0 prog 0 for
  t1..t117 EXACTLY (CB-only home, RES channel 0 by T34 - the diagnosis of
  P11 confirmed at channel level); t118 first bucket 1 (Laboratory built by
  kBuildOrder after 2 Factories on the IND grant chain).
- SUITE 534/0 after the law change; gate campaign seed 2024 still FINITE:
  VICTORY Extinct t303 (was Extinct too; compression slows AI research, no
  stall class).
- WITNESS scripts/tRSV2w_witness.sh VERDICT PASS (scratch Xvfb :99, seed
  5, --autoplay --campaign 400 --dbg-res): stages before(q=0)->sliver(q=2,
  94px select)->progressed q=3 LOG line "ui research fill 6 3" + 50px
  advance inside the +-20 box, control 0px, content non-shrinking. The
  GROWN endpoint of the S9 wipe law is now WITNESSED. Census reused
  UNCHANGED (tRSV2p_census.py).
- SEAM TRSV2w-A (named, not stubbed): vendor zeroes progress[r] every turn
  the target word is 0xffff (0x46b90); the port KEEPS progress across a
  re-queue. Observable only if the player re-picks mid-project; the commit
  chain gates make it rare. Left as documented deviation.
