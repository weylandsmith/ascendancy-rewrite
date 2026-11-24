# tRSV1 WIP — RESEARCH TREE DRAW: GENERATOR LAW + PORT (2026-11-24)

Task: STATE.md NEXT tRS-V1 (D26 "the tree not being drawn correctly" + the
clickability half of "I can't set any projects"). RE-FIRST: derive
FUN_0004709c's generator branch, port verbatim, node art from restree.shp,
witness, pins.

SITTING CHECK ran FIRST this iteration: `python3 scripts/r1_t85g_sitting.py`
exit 0 (tail rows t>=1240 mid-turn diff report, newest trusted turn class
unchanged, production ring alive) — no new sitting, stale assignment stood.

## P1 GENERATOR LAW — FUN_0004709c (window init, reswin) DERIVED VERBATIM

Sources: work/tNGS_gen1.asm (0x4709c..0x471f8), work/tNGS_gen2.asm
(0x471f9..0x47477), fresh capstone of 0x47d60..0x47e60 / 0x47f00..0x481c0 /
0x481c0..0x48560 (work/tRSV1_proj0.asm, work/tRSV1_proj.asm), rotation
primitives 0x5324c/0x532b8/0x53324/0x53374 (dumped inline).

### P1a Window init (0x470a8..0x47138)
- win = eax (ebp). node table = win+0x143, 100 slots stride 0xc
  (init loop 0x470c1..0x470ed: slot k = {+0: 0.0f, +4: float(k), +8: 0.0f}).
- word [win+0x143+0x898] = word [win+0x9db] = 0xffff  (SELECTION word cleared
  here — the same word the SELECT sub writes; confirms 0x9db is window-relative).
- camera init call 0x203b8 on win+0xab, args (30.0f fov, 1.0f, ds:0x?, 320):
  stores [cam+0x24]=1.0, [cam+0x2c], [cam+0x30]=320, [cam+0x70]=1.0 and
  computes [cam+0x28] = f(fov) (0x203e4: tan-family via 0x77567).
- position struct win+0xdf (= cam+0x34) = (0.0, 0.0, -150.0) (0xc3160000 VERIFIED).
- `push ds:0x24b0; call 0x206c0` = OPEN "reswin.txt" (tNGS cycle-1 VERIFIED
  string). Handle==0 (the shipped tree) => GENERATOR branch 0x471f9.
  Else: fscanf "%d" N; if N != WORD[0x74744] (live tech count) close+return
  UNCHANGED; else read N int triples into the table (int->float, order
  x,y,z at +0/+4/+8 — the file branch is DEAD in the shipped game).

### P1b Depth law (0x471f9..0x472c5) — iterative relaxation, NOT recursion
- A[0..99] (stack) filled 0xff (0x76e30(esp+0x64, 0xff, 100)).
- Repeat passes until a full pass sets no "unmarked prereq" flag [esp+0xf4]:
  for row in 0..N-1 while A[row]==0xff:
    for j in 0..4: p = byte[rec(row)+0x74784+j] (stride 0x4b; 0xFF terminator)
      if p==0xFF: break
      if A[p]==0xFF: flag=0; A[row] stays 0xff (retry next pass); break
      else: eax = max(eax, A[p]+1); esi = max(esi, A[p]+2)
    A[row] = eax   (roots: no prereqs => eax stays 0 => A=0)
- At convergence A[row] = LONGEST prereq-chain depth (same value the port's
  researchDepth computes — the port's depth is CORRECT, only the PLACEMENT
  was invented). esi = maxdepth + 1 (max over non-root rows of depth+1);
  the placement loop runs k in [0, esi).
- Guard: 0x471f9 asserts dword[0x74740]==-1 (error call 0x2a428 otherwise).

### P1c Placement law (0x472d4..0x47472) — a SPIRAL, not a grid
- C[0..99] zeroed (stack esp+0); C[d] = count of rows at depth d
  (0x472e6..0x47300: C[A[row]]++). (Count is computed; the placement below
  does not read C — named seam TRSV1-D: C's consumer is elsewhere.)
- cursors: k (slot index) [esp+0xf8]=0; y-angle acc [esp+0xe4]=240.0;
  x-cursor [esp+0xe8]=0; node ptr [esp+0xe0]=table.
- PER DEPTH COLUMN k (loop head 0x47333, exit 0x473a7 when k>=esi):
  - [esp+0xfc] = 4                     (radius candidate)
  - 0x47367 `movzx ebp, byte ptr [esp + ebp]` — NO +0x64 DISPLACEMENT.
    CORRECTED (this iteration, after the first reading assumed A[k] and the
    measured data then implied a SIGFPE): the operand is the array the
    COUNT pass zeroed at esp+0 (0x472d9 `mov eax, esp` + 0x472e6 count loop)
    => ebp = C[k] = NUMBER OF ROWS AT DEPTH k, not A[k]. With that reading
    the divisor is never zero for a non-empty column, which is the only
    reading consistent with the shipped game running.
  - q = k % 2 (0x47346..0x47350 idiv 2). Branches:
      even k (edx==0) -> 0x473b1: if C[k] > 1 then R0 = 23 (else 4); d = C[k]
      odd  k, C[k] > 2 -> 0x47373 `dec ebp`: d = C[k]-1, R0 stays 4
      odd  k, C[k] <= 2 -> 0x473b1: R0 = 23 iff C[k]==2 (else 4); d = C[k]
    => R0(k) = 23 iff (k even AND C[k]>1) OR (k odd AND C[k]==2); else 4.
       d(k)   = C[k] except odd k with C[k]>2 -> C[k]-1  (vendor quirk:
       that column's nodes do not close the circle).
  - angle accumulator [esp+0x100] = float([esp+0xe4]) = 240 + 30*k degrees
    (0x47352 fild [esp+0xe4]; [esp+0xe4] += 30 per column at 0x4738b).
  - PER ROW ecx in FILE ORDER with A[ecx]==k (inner loop 0x473dc..0x47472,
    i = edi = index within column, node ptr ebx = table + 0xc*ecx):
      node+4 = float(30*k + 15*(i & 1))     (0x473fd..0x4741e: x-cursor +
                 15*(i&1); x-cursor [esp+0xe8] = 30*k advances 30/column)
      node+8 = (i==0 ? R_special(k) : 23)   (0x47421 fstp [ebx+8] of
                 [esp+0xfc]; [esp+0xfc]=23 at 0x47458 after the first write)
      node+0 = 0                            (0x47432)
      call 0x5324c(node, angle)             (0x47438)
      then angle += 360 / d  (0x4743d..0x4746b: 0x168 idiv ebp, fild,
           fadd acc; NOTE divisor d = A[k] (even k) or A[k]-1 (odd k) —
           the SAME d as the radius test; LATENT DIV-BY-ZERO if d==0 with a
           non-empty column: named seam TRSV1-A, the port clamps to skip the
           increment (never observable: a column whose first node wrote with
           d==0 would SIGFPE the vendor, so d==0 non-empty columns do not
           occur in the shipped tree — CHECK against the real 66-row data).
- ROTATION PRIMITIVE 0x5324c VERBATIM (degrees; Borland sin/cos pair
  0x7754a/0x77556, pi/180 const ds:0x88b88 = 0.0174532924):
      node+0' = node+0 * sin + node+8 * cos
      node+8' = node+8 * sin - node+0 * cos      (0x53285..0x532ab FPU stack
      traced instruction-by-instruction)
  i.e. rotation of the (+0,+8) pair; with node+0=0 at call time:
      node+0 = R*sin(theta), node+8 = R*cos(theta).
  (0x532b8 is the SIBLING primitive on (+0,+4) — NOT used here.)

### P1d World -> screen (0x47f00..0x48160, same function)
- z-range pass 0x47f0d..0x47fc3: over LEGAL rows (0x46d3c), tracks min/max of
  node+0x147 (== table slot +4 float? NO: 0x147 is unaligned off ebp — reads
  dword [ebp+0x147+k*0xc]... seam TRSV1-E: field identity of +0x147 vs the
  node table stride is UNRESOLVED; the min/max land in [ebp+0xe3]) — NOT
  needed for placement; skip.
- view matrix: call 0x20414 on win+0xeb from cam+0x34 negated (0x20435..
  0x2045f: -pos triple + basis) — the standard look-from camera the tNGS
  cycle-1 law already cites.
- PROJECT LOOP 0x48009..0x480c0 over ALL rows (no legality gate here):
  - 0x53324(eax=win+0xeb matrix, edx=node, ebx=out[3]) = row-major affine:
    out = M * (node+0, node+4, node+8) + t (0x53324..0x53373 VERIFIED:
    out.x = m0*X + m4*Y + m8*Z + m[+0xc], etc.)  => WORLD = (node+0, node+4,
    node+8) = (R sinθ, 30k+15*(i&1), R cosθ). Y IS THE TREE AXIS.
  - depth float stored [win+0x783+4k] (0x4805c).
  - 0x53374 perspective (tNGS S5 law: 1/z divide, +0.5 bias frndint, TWO
    screen words) writes u16 at win+0x5f3+2k (== HIGH HALF of the u32 the
    hit law reads at win+0x5f1+2k, `sar 16`) and u16 at win+0x6bb+2k (==
    high half of win+0x6b9+2k) — POINTER IDENTITY PROVEN by the lea pair
    0x47fe3/0x47fe9 + the +2 stride walk. VIEWPORT CENTRES pushed 240 (0xf0)
    and 235 (0xeb) + pan word [win+0xd3] (0x48069).
  - word [win+0x913+2k] = row (the draw order list source; 0x48544 reads it).
- => THE HIT LAW'S INPUTS ARE EXACTLY THESE PROJECTED SCREEN COORDS. The
  tRS-B1 +-24 square consumes them unchanged. Layout swap must keep
  researchHit reading the PROJECTED centre (it does).

## P2 DRAW LAW (0x48165..0x48560, same function) — shape index + state
- per-row shape-offset word [esp+0x120] (0x481b1..0x48244):
  OWNED (row+0x4b mask >>24 has race bit [0x7458e]) -> 0x14 (20)
  else if row == studied word word[specnum*2+0x76492] (loaded 0x48132..
    0x48141): eax = (word[race*2+0x764a0] * 18) / WORD[0x74782] + 2, clamped
    [-0x11, +0x11]
  else 0.
  Consumed at 0x4838a: if 0 -> skip the PREREQ-LINE block (0x4838a..0x483f7:
  for j in 0..4 prereqs, line blit 0x5d5a1 between the two projected nodes,
  colour 0x6b minus clamp(round(f(depth)+prereq-offset), +-3) — the EDGE LAW
  below); if nonzero -> fetch shape 0x1fc34(0x9f10c, ds:0x48c44-name?, class
  eax=(v<<16)/20) and blit 0x5d5a1 (the STUDY-MARKER chip).
- PREREQ-EDGE LAW 0x48275..0x48383: for j in 0..4 (prereq p=row rec+0x40+j):
  if p==0xFF break; if 0x46d3c(p) legal (i.e. p is a VISIBLE frontier tech?)
  ... line from node(p) to node(row): x = (proj p).x, y = (proj p).y+27,
  x2 = (this node).x, y2 = (this node).y+27 (0x48334 `add edx,0x1b` /
  0x48353 `sub eax,0x1b` — the +27 Y-OFFSET on BOTH endpoints: the line is
  drawn in a field shifted 27 px DOWN relative to the disk centres);
  colour = 0x6b (107) - clamp(round(depthf), -3, +3) where depthf =
  [0x2533]*(win+0xe7 + [win+0x783+4p]) — a z-shaded line palette.
  (0x482ec `inc edi` path = the illegal-prereq leg: skip line, continue j.)
- NODE STATE LAW esi (0x483fa..0x48470), evaluated per row in DRAW ORDER:
  esi = 1 if (row != studied OR row not owned...) — verbatim:
    esi=1; if row==studied-row AND NOT owned(row+0x4b): esi=0 (0x48414..
      0x4842e: the studied-but-not-owned row gets 0 = draws NOTHING? seam
      TRSV1-B: the 0 state's leg at 0x484ce class-0 blit — class 0 IS
      blitted (esi is pushed as the frame), so state 0 = frame 0);
    if owned(row+0x4c dword >>24 bit): esi=3 (0x48452)
    if row == word[win+0x9db] (SELECTED): esi=2 (0x4846b, overrides 3)
  shape: edx = 0x1fe20(lib 0x9f10c, name ds:0x250c) & 0xffff (0x48475..
  0x48484), blit 0x1fc34(lib, edx, frame=esi, x, y) then 0x5caac (selected,
  gold-rim path) / 0x5cf96 (normal) — the SAME 0x1fc34 fetch posture as the
  t442 precedent.
  => THE NODE ART IS ONE SHAPE (restree.shp family) WITH FRAMES 0..3 =
     {studied-unowned?, empty, selected, researched}. Per-row PICTURES
     (help "disks containing pictures") = the restree.shp k-frame CONTENT
     question — decode restree.shp next (P3).

## P3 ART LIBRARIES MEASURED (file-level, container law shp.h S1)
- `data\resring.shp` (ascend01, 4707 B) N=4 records, dims 29x29 each
  (k0 dims at rec+0x00, k1..k3 at rec+0x10 per the V/A law) = THE NODE RING
  SPRITES, four frames. Sole fetch sites: `mov edx, 0x250c` (= pool
  'data\resring.shp' at 0x850bc VERIFIED) at 0x48476/0x4847f (node blit) and
  0x487b6 (the panel/study block) — the ONLY two code refs to that immediate
  in the whole image. So: disk art = resring.shp frame esi (the state law P2).
- `data\restree.shp` (ascend01, 125109 B) N=66 records, dims 24x24 = EXACTLY
  one picture per LIVE tech row (66 = WORD[0x74744] main rows). The pool
  string 'data\restree.shp' exists ONLY as 'restree.txt' at 0x85014 for the
  TEXT loader (0x468d3); NO code immediate references a restree.shp name.
  => the per-row PICTURE consumer is NOT in the reswin function; the visible
  in-disk picture in the t252 capture is either resring frame content or a
  second painter. NAMED SEAM TRSV1-C (frame semantics uncited).
- MEASURED t252 screenshot (work/screens/t252/research_open_game.png, native
  vision, 2026-11-24): three disks visible, one with a PICTURE inside and a
  GOLD RIM, one empty blue-rimmed, thin lines running UP out of the frame to
  the window top; the rest of the 470x430 field is black. CONSISTENT with a
  tree drawn far LARGER than the viewport (see P4 scale) — the vendor screen
  shows a PANNED WINDOW onto the tree, not the whole 66-node field. The D26
  complaint "the tree not being drawn correctly" therefore includes SCALE,
  not just arrangement.

## P4 CAMERA + PROJECTION CONSTANTS (all cited)
- 0x470ef `call 0x203b8` on win+0xab with pushed args (30.0 fov, 1.0 near,
  100000.0 far, 320): 0x203b8 stores [cam+0x24]=fov, [+0x2c]=near,
  [+0x30]=far, [+0x70]=1.0, then 0x203e4 computes
  [cam+0x28] = 320 / tan((fov*pi/180)/2) = 320/tan(15deg) = 1194.19
  (pi/180 const ds:0x5900 -> pool 0x884b0 = 0.0174532924 VERIFIED; 0.5 const
  ds:0x833a4 VERIFIED; fptan helper 0x77567/0x77562 VERIFIED; the trailing
  `fild dword [esp]` re-reads the pushed 320 arg). NOTE 320 is the HALF
  width of 640 — the same convention as the tNGS cycle-1 cosmos camera
  (242.5/tan(17.5deg)), so FOCAL_reswin = 1194.19 px.
- position win+0xdf (= cam+0x34) = (0, 0, -150.0) (0xc3160000 VERIFIED).
- view matrix win+0xeb = 0x20414(cam): negated position triple + basis
  (0x20435..0x2045f) — identity basis at rest.
- 0x53324 = row-major 3x3 affine + translation (VERIFIED instruction by
  instruction): out = M*(X,Y,Z) + t.
- 0x53374 = the tNGS-S5 perspective primitive (fld1/fdiv z, +0.5 bias
  ds:0x2c50 VERIFIED f64 0.5, frndint 0x76e08, TWO u16 screen words, then
  `add word[ebx],ax` / `add word[edx],ax` of the two trailing args).
  Call site 0x48035..0x48076 pushes: esi = &win+0x6bb+2k (screen-Y word),
  edi = &win+0x5f3+2k (screen-X word), 240, 235, dword[win+0xd3] (pan).
  POINTER IDENTITY: +0x5f3/+0x6bb are the HIGH halves of the u32 fields the
  hit law and the draw read at win+0x5f1+2k / win+0x6b9+2k with `sar 16`
  (lea pair 0x47fe3/0x47fe9, +2 stride walk) — CONFIRMED.
- SCALE CONSEQUENCE (arithmetic of the cited law): z_cam = Z_world + 150,
  Z_world = R cos(theta) in [-23, +23] => scale = 1194.19/z in [7.0, 9.2];
  the Y column pitch 30 world units => ~210..275 SCREEN PX per depth column.
  The whole 66-node tree spans ~esi*240 px — FAR bigger than the 470x426
  window: THE VENDOR SCREEN IS A PANNED WINDOW, which the t252 capture
  corroborates (three disks + lines running off-frame).

## P5 DRAW-SCOPE LAW (0x48524..0x48566) — FRONTIER ONLY
The per-row draw loop reads the row list word [win+0x913+2k] (written by the
projection loop at 0x48083) and at 0x48566 calls FUN_00046d3c — the SAME
legality predicate as the hit law — `test eax,eax; je 0x48504` SKIPS the
row. => the vendor draws ONLY rows that are legal-to-study (all prereqs
owned AND not owned): the frontier. Owned/blocked rows are NOT drawn; their
positions still exist in the table (that is how the prereq LINES from an
undrawn ancestor to a drawn frontier node are computed at 0x48275..0x48383,
both endpoints read from the projected arrays, each endpoint shifted +27 px
in Y: 0x48334 `add edx,0x1b`, 0x48353 `sub eax,0x1b` — the line is painted
in a field offset 27 px below the disk centres).
Line colour law (0x482a8..0x482c7 / 0x48576..0x485a5): pal = 0x6b (107) -
clamp(round(f32[0x252f]*(win+0xe7 + [win+0x783+4k])), -3, +3) where 0.25
const ds:0x252f -> pool 0x850df VERIFIED, and [win+0x783+4k] is the stored
camera-space depth (0x4805c) — a z-shaded line palette.
NODE STATE (esi) LAW 0x483fa..0x48470 (drawn per row, in list order):
  esi = 1;
  if (row == studied row word[race*2+0x76492]) AND NOT owned(row rec+0x0b
      dword>>24 bit [0x7458e])  -> esi = 0;
  if owned-rec dword[rec+0x0c]>>24 has the race bit -> esi = 3;
  if row == word[win+0x9db] (SELECTED)              -> esi = 2 (overrides 3).
  Blit: 0x1fe20(lib 0x9f10c, 'data\resring.shp') -> shape id, then
  0x1fc34(lib, shape, frame=esi, x, y) with x,y = projected word sar 16,
  then 0x5caac (esi==2, the SELECTED/gold path) / 0x5cf96 (other frames).
  0x5caac/0x5cf96 are the row-RLE blitters (shp.md S9) = 1:1, unscaled.

## P6 OPEN LEG (the one thing between this law and a port)
0x53374's FPU stack order (which pushed arg is the focal multiplier vs the
pan adds) is NOT yet traced instruction-exactly; the call site pushes five
dwords (esi, edi, 240, 235, [win+0xd3]) for a `ret 0x14` and the body reads
[esp+0x18] as a FLOAT before touching [eax]/[eax+8]. Everything else in the
chain is cited. RESOLUTION PATH (next iteration, cheap): the same primitive
has a known-good consumer in the COSMOS map (0x285bb, whose scale law tNGS
cycle-1 already pinned) — diff the two call sites rather than re-deriving,
or take ONE debugger capture of win+0x143 (world table) + win+0x5f1/0x6b9
(projected) from a live reswin and fit. DO NOT guess the scale.

## P8 MEASURED COLUMN TABLE (restree.txt 66 rows, work/r1/game/restree.txt,
python replay of the P1b relaxation + P1c law, 2026-11-24)
- depths converge in one vendor-pass-equivalent sweep; esi = 18 columns
  (0..17), maxdepth 17 (matches research.md §3 "depth-spread up to 17").
- C[k] (rows per column) = [3,4,3,5,6,5,3,4,2,4,4,4,4,4,5,3,2,1].
- TRSV1-A RESOLVED by the P1c correction: divisor d(k) = C[k] (or C[k]-1 on
  odd k with C[k]>2) — never 0 for a non-empty column (min C over non-empty
  = 1, and odd-k C==1 keeps d=1). No SIGFPE class exists. The earlier
  A[k]-reading's div-by-zero "seam" was an artifact of MY misread, not the
  vendor's.
- TRSV1-D RESOLVED: C's consumer IS the placement loop (divisor + radius
  gate) — there is no missing consumer.
- Worked example: column 0 (3 roots) -> R0=23, d=3: the three roots sit on a
  23-unit circle at angles 240, 360, 480 deg (pitch 360/3=120). Column 8
  (C=2, k even) -> R0=23, d=2 (180-deg apart); column 15 (C=3, k odd) ->
  R0=4 for node 0 then 23 for the rest, d=2. The vendor's tree is a CHAIN OF
  SMALL CIRCLES (one per depth), tilted 30 deg per column — NOT a spiral and
  NOT a grid.
- PORT NOTE for the next session: implement researchTreeGeometry() as
  (depth relaxation per P1b; C[k]; per column angle acc 240+30k; per node
  X=0,Y=30k+15*(i&1),Z=R0-or-23 rotated by acc + i*(360/d) ACCUMULATED —
  the vendor adds the step AFTER each write (0x4743d..0x4746b), node i's
  angle = acc0 + i*(360/d) as REPEATED float adds, not a multiply (keep the
  repeated-add posture; f32 rounding is observable at +-1 px)). Then the
  camera law P4 + 0x53324 + the frontier-only draw scope P5. THE ONE LEG
  STILL OPEN IS 0x53374's arg roles (P6) — diff against cosmos call site
  0x285bb (tNGS cycle-1 pinned) FIRST; a debugger capture of win+0x5f1 is
  the fallback.
- ART: resring.shp k0..k3 = 29x29 rings (state frames 0..3 per the P5 esi
  law); restree.shp k0..k65 = 24x24 per-row pictures whose consumer is NOT
  in the reswin fn (TRSV1-C stays open — hunt the 0x487b6 block's sibling
  painter or the 0x1fe20 census around 0x488xx next).

## P9 ITERATION STATUS
Derivation iteration: generator + camera + draw-scope + art libraries cited;
projection-arg leg (P6) and picture-consumer (TRSV1-C) open; NO code shipped
(this session's budget went to the derivation + one self-correction;
shipping the layout without P6 would put an uncited scale on the user's
screen — refused under strict-close).


## P6 CLOSED 2026-11-24 (tRS-V1b) — 0x53374 ARG ROLES DERIVED (RAW-BYTE x87)
## Disasm: work/ascend_restored.bin via ~/tools/revenv/bin/python
## scripts/t442_disasm.py (capstone lives in ~/tools/revenv, NOT .venv); raw
## hex of 0x53374..0x533db hand-decoded (the linear capstone dump desyncs on
## this body; the stepping script is clean).

STACK (ret 0x14, callee frame push ebx/edx/sub 0xc): last-pushed = [esp+0x18]
= P0 float; +0x1c = P1 int; +0x20 = P2 int; +0x24 = OUT-X ptr (ebx);
+0x28 = OUT-Y ptr (edx). eax at the CALL = the affine OUT triple (0x48062
`lea eax,[esp+0xec]` = the [esp+0xdc] scratch 0x53324 wrote — survives the
five pushes; the 0x48036 `mov eax,[esp+0xe8]` is an EARLIER use, overwritten).

x87 trace from EMPTY stack (depth-checked every op; first-pass error was
missing that `fmul st(1)` leaves st1=P0 and that `fstp st(2)` re-stores):
  s0=X*P0 (X=[eax]); fld1; s0=1/Z (Z=[eax+8]); fld st(1)=X*P0; ->X*P0/Z;
  fstp st(2) -> stack (1/Z, X*P0/Z, P0); fld Y -> (Y,1/Z,Xf/Z,P0);
  fmulp st(3): P0*Y, pop; fmulp st(2): (P0*Y)/Z, pop -> (Xf/Z, Yf/Z);
  fld 0.5; fxch; fadd -> Xf/Z+0.5; 0x76e08 (fldcw RC=round, frndint VERBATIM
  0x76e08..0x76e24); fistp -> word[ebx] = round(X*focal/Z + 0.5);
  faddp st(1): the SAME 0.5 lands on Yf/Z (vendor quirk — one bias constant
  serves both legs); frndint; fistp -> word[edx] = round(Y*focal/Z + 0.5).
  THEN word[ebx] += P1; word[edx] += P2. Net FPU balance 0 (reentrant).

RESWIN SITE LAW (0x48009..0x480c0 loop, all dwords cited above):
  view = M*world + t  (0x53324 row-major, M = win+0xeb = 0x20414(cam win+0xab)
  output at cam+0x40; camera pos win+0xdf = (0,0,-150))
  AXIS MAPPING (hit law 0x474fd/0x47514 arbitrates: +0x5f1 compared vs mouse
  X ds:0x484ec FIRST, +0x6b9 vs mouse Y ds:0x484f0; blit site 0x48496 pushes
  +0x6b9 sar16 as y THEN +0x5f1 sar16 as x):
    word win+0x5f3+2k (HIGH half of +0x5f1) = screen X = round(focal*vX/Z+0.5)+235
    word win+0x6bb+2k (HIGH half of +0x6b9) = screen Y = round(focal*vY/Z+0.5)+240
  (call-site lea esi=+0x6bb lands in [esp+0x24]=ebx=OUT-A=Y leg; edi=+0x5f3
  = [esp+0x28]=edx=OUT-B=X leg — the FIRST draft of this note had them
  swapped; the hit-law comparison direction above is the authority.)
  P0 = dword[win+0xd3] = cam+0x28 = FOCAL = 320/tan(15deg) = 1194.19
  (0x203b8/0x203e4 VERBATIM; win+0xab+0x28 = win+0xd3 POINTER IDENTITY — the
  "pan word" reading is REFUTED, there is NO pan term in the projection).
  depth word: win+0x783+4k = view.Z (0x4805c). COSMOS site 0x285bb passes the
  SAME shape (P0=[cos+0x102]=its focal) — roles transfer by diff, CONFIRMED.
  *** BOTH X AND Y ARE PERSPECTIVE-DIVIDED (the "Y orthographic" first-draft
  reading is WRONG; raw-byte trace above is the authority). ***
  Z' = Z_world+150 in [127,173] => scale 6.9..9.4; Y up to 30*17+15=525 world
  => ~3600 px column span: the reswin is a WINDOW onto a huge field (t252
  corroborates). Scroll/rotation of win+0xeb-basis is OUT OF SCOPE (no writer
  of win+0xdf outside init 0x4710e in the reswin fn; camera basis law =
  0x20414 verbatim, identity-at-rest ported).

## P10 SCROLL + LEGALITY + ROUNDING LAWS (tRS-V1b, all cited this iteration)
- FUN_00046d3c(exe=0x74744 table, edx=row, ebx=0xffff|raceIdx) VERBATIM
  (0x46d3c..0x46dde): returns -1 (TRUE) iff OWNED (dword[rec+0x47]>>24 has
  race bit — if owned it JUMPS to return true WITHOUT the prereq loop) OR all
  prereqs (bytes rec+0x40..44, 0xFF term) owned; else 0. => THE DRAW SCOPE IS
  OWNED + FRONTIER (blocked rows are not drawn); the tRS-B1 note "legality =
  all-prereqs AND not-owned" was imprecise — the not-owned gate lives in the
  COMMIT chain (0x47d99), not in 0x46d3c.
- ROUNDING 0x76e08 VERBATIM: saves cw, forces HIGH byte 0x1f (RC=11 = chop/
  toward zero), frndint, restores. With the +0.5 bias: positive values round
  to nearest; NEGATIVE values chop asymmetrically (-2.7+0.5=-2.2 -> -2). The
  port replicates trunc(v+0.5f) in f32 and stores the low 16 bits (u16 word).
- win+0xe7 == camera pos.z (pos triple win+0xdf/+e3/+e7 = (0,0,-150) — the
  0x4710e init writes +8 = win+0xe7). The line-colour float law is therefore
  fully cited: k = clamp(chop(0.25f*(depth_p + posz)), -3, +3) with posz=-150,
  depth_p in [127,173] => k in 0..6 (palette-line offset), pixel index 0x6b.
- MSG LAW (window fn 0x47b41..0x47d65, DAT_0x764c4 key-flag byte):
  msg 50 (RESROTLEFT) sets/clears bit4, msg 51 bit8, msg 52 bit1, msg 53 bit2
  (press-when-idle sets BOTH bits of the pair: 0xc / 0x3 — the toggle logic at
  0x47b44..0x47c42; release clears). PER-EVENT (0x47c88..):
  ROTATE: if bit4: angle = +3.0f, if bit8 too: -3.0f; fmul ds:[0x9f108]
  (RUNTIME float — NOT in the restored image (file ends < 0x9f108); [unverified
  value, port default 1.0f, seam TRSV1b-A]); call 0x53504 on win+0x11f =
  cam+0x74 = the camera ORIENTATION basis: rotates the pair at +0x18/+0x20 of
  that block by angle (0x53504 VERBATIM -> 0x5324c + rebuild 0x536f4).
  MOVE: if bit1: delta = -1.0f, if bit2 too: +1.0f; fmul [0x9f108];
  win+0xe3 (pos.z!) += delta*scale — THE MOVE PAIR MOVES CAMERA Z (dolly),
  not Y. fld [esi+0xe3]; fadd; fstp [esi+0xe3] VERBATIM 0x47d03..0x47d12.
  => SCROLL LAW: RESMOVEUP = camera z -= 3?/tick (dolly IN: tree grows),
  RESMOVEDOWN = z += (tree shrinks). RESROTLEFT = basis yaw +3deg/tick.
  Repaint via [win+0xa7 vt +0xc] after each event.
- NODE FRAME LAW re-verified verbatim 0x483fa..0x48470 (esi): 1 default; 0 iff
  row==studied(word[race*2+0x76492]) AND NOT owned(rec+0x0b>>24 bit); 3 iff
  owned(rec+0x0c>>24 bit — NOTE dword +0x0c here vs +0x47 in 0x46d3c: the
  frame law reads rec+0x7478b/+0x7478c = rec+0x07/+0x0c of the 0x4b record —
  seam TRSV1b-B: which of the two ownership dwords is authoritative; the
  DRAW-path 0x48566 gates with 0x46d3c (+0x47), so +0x47 is authoritative for
  scope; frame 3 uses +0x0c); 2 iff row==word[win+0x9db] (selected, overrides).
  Blit: 0x1fc34(lib 0x9f10c, resring shape, frame=esi, x=word+0x5f1 sar16,
  y=word+0x6b9 sar16) then 0x5caac (esi==2) / 0x5cf96 — 1:1 UNSCALED 29x29.
  => the port blits resring.shp frames, NOT vector r30 circles.

## P11 LAWS FROZEN FOR THE PORT (tRS-V1b; raw-byte x87 + Ghidra double-check)
- 0x5324c RAW VERBATIM (bytes 53252.. decoded by hand; Ghidra agrees):
  X' = X*cos + Z*sin ; Z' = Z*cos - X*sin (angle f32 deg * pi/180 -> f64;
  0x7754a = fcos LOOP (fprem range-reduce 0x7751e VERIFIED), 0x77556 = fsin).
  With X=0 at call time: X'=Z*sin(acc), Z'=Z*cos(acc). WIP P1c line stands.
- 0x53324 RAW VERBATIM + Ghidra: eax = MATRIX+TRANSLATION block (12 floats,
  rows [m0 m1 m2 t]); edx = POINT triple; ebx = out. out = M*P + t.
  0x20414 writes the reswin view block win+0xeb: rows = basis, t = -pos.
  Rest: identity, pos (0,0,-150) => view = (X, Y, Z+150).
- ANGLE STEP 0x4743d VERBATIM: eax=360; INTEGER idiv d; fild; fadd acc;
  fstp acc — the step is int(360/d) THEN repeated f32 adds. For the measured
  C table every d divides 360 exactly (1,2,2,3,3,4,4,5,5,6) — no residue.
- EDGE LAW CORRECTION (raw bytes 0x48343/0x483aa): the line runs from
  (this.x, this.y - 27) to (prereq.x, prereq.y + 27) — MINUS 27 on the
  CURRENT node, PLUS 27 on the PREREQ (disk-top to disk-bottom connector;
  the P5 note's "+27 both endpoints" is REFUTED). Colour = 0x6b - k with
  k = clamp0x76e08(0.25f*(0.5f*(z_this+z_prereq) + posz)), posz = -150
  (f32 chain 0x482a8..0x482c7 VERBATIM: fld z_row; fadd z_p; fmul 0.5;
  fadd posz; fmul 0.25); prereq == selected word => colour 0xf3 (243)
  VERBATIM 0x48314..0x48321. Palette INDEX space (game.pal).
- SCOPE 0x48566 + 0x46d3c VERBATIM: draw iff legal = OWNED OR (all prereqs
  owned) — 0x46d3c returns TRUE for owned rows WITHOUT the prereq loop
  (0x46d88 jne->0x46dd5) and true iff all prereqs owned otherwise. Blocked
  rows are NOT drawn and NOT hittable (hit sub gates 0x46d3c first).
  The study MARKER chip block 0x4838e runs only when [esp+0x120] != 0
  (owned 0x14 / studied progress class) — port skips the chip (runtime-only
  shape word 0x6fd82; seam stands).
- SCROLL STATE MACHINE (DAT_0x764c4 bit pairs, 0x47b44..0x47c42 VERBATIM):
  ROT pair bits 4=A(msg50) 8=B(msg51); states (bit4,bit8): S0 none,
  L=(1,0) => +3.0 deg, R=(1,1) => -3.0 deg, DEAD=(0,1) no motion.
  msg50: bit4==0 -> (1,0); bit4==1 -> bit4=0 (from L -> DEAD, from R -> DEAD
  ... re-trace: msg50 always clears bit4 when set; sets (1,0) when clear).
  msg51: bit4==0 -> (1,1); bit4==1&&bit8==0 -> (1,1); both -> (1,0).
  MOVE pair bits 1=A(msg52 RESMOVEUP) 2=B(msg53 RESMOVEDOWN); delta law
  0x47cdb..0x47d12: (1,0) => -1.0, (1,1) => +1.0, (0,1) DEAD; posZ(win+0xe3)
  += delta * f32[0x9f108] (RUNTIME factor NOT in the restored image — seam
  TRSV1b-A, port default 1.0). ROT path 0x47c88: angle +-3.0 * [0x9f108] ->
  0x53504(win+0x11f = basis vec0) = world-Y yaw + rebuild 0x536f4. Motion is
  APPLIED on phase ebp==4 events (button-hold re-posts msg 0x38 via 0x5669c
  0x47c51..0x47c7a); the port applies per pump tick (cosmos cadence
  precedent, documented deviation).
- BLIT COORDS: 0x48496..0x484c4 pushes (y=word+0x6b9 sar16, x=word+0x5f1
  sar16) to 0x1fc34/0x5caac; the HIT law tests the SAME words as CENTRES
  (+-24 square around them) => the vendor blitter CENTRES the sprite
  [inferred from that identity]; port draws 29x29 resring at (x-14, y-14).


## P12 tRS-V1c PORT DESIGN (frozen before first edit, 2026-11-24)
- API (researchview.{h,cpp}): ResearchGeom researchTreeGeometry(tree) =
  per-row WORLD triple (f32 posture: angle acc REPEATED float adds per P11;
  sin/cos via libm double, documented deviation from x87 fprem fsin), depth,
  column k, slot i; C[0..esi-1]; esi. researchDepth() keeps its law (P1b
  equivalence already measured). researchNodeScreen(geom, nodes, cam) =
  vendor chain: v = Ry(yaw)*world + t(posZ) (0x5324c mixing VERBATIM on the
  (X,Z) pair, t=(0,0,-posZ), posZ rest -150); screen X = truncTowardZero(
  focal*vX/vZ + 0.5f) + 235, Y likewise +240 (0x76e08 CHOP + 0.5 bias);
  focal = 320/tan(15deg) computed at runtime per 0x203e4. vZ < 1.0 => row
  NOT drawn (port guard vs div-by-zero; vendor word-wraps — documented).
- SCOPE: draw + hit ONLY rows legal per 0x46d3c = OWNED or all-prereqs-owned
  (Blocked excluded from BOTH). researchHit keeps its signature (pan args
  stay additive screen offsets, labelled port affordance); vendor SELECT
  semantics: click sets selection ALWAYS (resSel session), commit only if
  Available (setStudy) — ui.cpp updated.
- FRAME esi (P10 verbatim): 1 default; 0 iff row==studied && !owned; 3 iff
  owned; 2 iff row==selected (override). resring.shp frames 0..3 blitted 1:1
  centred (x-14, y-14); lib joins kLibFiles.
- EDGES: only for DRAWN rows, from (this.x, this.y-27) to (prereq.x,
  prereq.y+27), only when prereq is also DRAWN; colour chromePaletteArgb(
  0x6b - k), k = clamp(chop(0.25f*(0.5f*(z_this+z_p) + posz)), -3, +3);
  prereq==selected => 0xf3.
- SCROLL: ResCam {yawDeg, posZ, latchRot, latchMove} replaces the t419
  Camera3d pressSpin reuse. Latch state machine (dat_764c4 bit pairs P11):
  enc pair as 2 bits; ROT msg: none->L(1,0), L->off, R->DEAD(0,1); ROTR:
  none->R(1,1), L->R, R->L, DEAD->R. MOVE pair same transitions; deltas:
  L/(1,0) rot +3deg, R/(1,1) rot -3; move (1,0) posZ -= step (dolly IN,
  tree GROWS), (1,1) posZ += step, (0,1) DEAD. step=1.0 (seam TRSV1b-A).
  Pump cadence kSpinTickMs precedent (documented deviation).
- PINS tests/test_researchgeom_trsvc.cpp: C[k] census + esi=18; column-0
  worked triple; R0/d parity rules; chop asymmetry (-2.7+0.5 -> -2); scope
  law (blocked not hittable); latch table. t419/t408 coordinate pins
  RE-DERIVED to the new law (updated, supersede note, not deleted).
- WITNESS: ui.cpp logs 'ui research center <row> <x> <y> <state>' ONCE on
  screen entry; tRSB1_witness.sh RE-DERIVES the click point by grepping the
  first Available centre (never hard-code), re-runs the tRSB1 census.

## P13 tRS-V1c LANDED (2026-11-24) — PORT + PINS + WITNESS ALL GREEN
Port (rewrite/src/ui/researchview.{h,cpp} + ui.cpp kScreenResearch):
- ResCam (posZ rest -150, yawDeg, dat_764c4 latches, press law P11 verbatim,
  tick() one delta/pair/tick; cadence kSpinTickMs = documented deviation).
- researchTreeGeometry(): P1b/P1c chain replayed verbatim (repeated-f32-add
  angle acc += int(360/d), Y=30k+15*(i&1), R0 rules, esi=18 C-vector pinned).
- researchNodeScreen(): 0x53324 affine + 0x53374 roles (P6): chop(focal*v/vZ
  +0.5) via resVendorRound (0x76e08 asymmetric chop), +235/+240, int16 word
  wrap, RESWIN map. Focal = 320/tan(15deg) = 1194.256 f64 (the doc's 1194.19
  was the f32 tan value — fixture bug caught, corrected here).
- researchHit(): P5 legality gate 0x46d3c FIRST, +-24 square, scan HIGH row
  index -> LOW (painter order z2 desc; nearest wins overlaps).
- Painter: frontier-only draw (P5), resring.shp lib index 8 KEPT OUT of
  libFor's 8-entry scan, gold rim via shp frames (vector-rim RGB probe DEAD),
  edges +27px-Y z-shaded 0x6b-clamp (k=clamp(round(0.5*(z2+pc.z2)/… -posZ…))
  — round not chop, 0x76e08 cite; mutation -4 caught x3 tests).
- P1a window-init: screen!=kScreenResearch clears resSel/resCenterLogged.
TESTS: suite 515 -> 523, 0 failed. New tests/test_researchgeom_trsvc.cpp
(gen fixture, latch pump, press law, round chop-vs-round, edge clamp, scan
order, overlap geometry). MUTATION-VERIFIED: rotstep 3->2 CAUGHT; focal
tan15->tan17.5 CAUGHT; clamp -3->-4 CAUGHT (3 tests); scan low->high CAUGHT
(scan_order pin; first attempt was MY test bug — forgot to pass cam).
t419 coordinate pins re-derived from extracted/ascend00/restree.txt replay
(same chain, 66/66 converge esi=18); t408 round-trip leg + trsb1 fixture
comments updated to the new law.
WITNESS tRSB1 VERDICT PASS on the vendor-law render (seed 5): dolly-out x2
presses kResMoveUp (578,449) -> app re-logs "ui research center 6 397 240
available" -> click re-derived from log (NEVER hard-coded) -> "ui research
study Xenobiology"; panel-green 0->690; local leg 563 changed px within 40
of the centre. Census rewritten: gold-rim RGB probe replaced by local-change
leg (the old probe measured the dead vector rim).
NEW AFFORDANCE LAW (port addition, labelled): the frontier disk is OFF-FRAME
at rest (row 3 y=684 seed 5) — the vendor rest camera shows NO clickable
disk at game start?! [unverified vs vendor; seam TRSV1c-D] The witness
dolly-outs to make one visible. resCenter re-log fires on (row,x,y) CHANGE;
"offframe" line when no visible Available centre.
OPEN SEAMS carried: TRSV1b-A (dolly step f32[0x9f108] unrecovered, pinned 1.0),
TRSV1c-D (rest camera shows no clickable frontier disk — vendor may dolly-in
on entry or the frontier geometry differs; hit law itself is cited), restree
.shp consumer (TRSV1-C, unchanged).
