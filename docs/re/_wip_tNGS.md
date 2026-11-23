# tNGS — starfield volume + rotation faithful RE (working notes, streaming)

## S0. Assignment (D21)
Derive L1 star table / L2 projection / L3 rotation pump from the vendor painter
chain 0x52114 head + 0x526b4 body, port faithfully, pin vs refcap, re-package.
Budget <=3 cycles. Refcap ground truth: /tmp/tNGF_begin_ref.png + newgame ref.

## S1. CITED FROM THE BANKED DISASM DUMPS (work/tNGC_paint_head.asm,
## work/tNGC_paint526b4.asm — verbatim, addresses are payload-relative, obj0 code)

### L1 STAR TABLE (partial, cited)
- 0x52762: `esi = obj + 0x172` (obj = window-record-ish global? no: eax arg saved
  at [esp+0x14]; 0x52759 path asserts on null). Table base = arg+0x172.
- 0x52768: `ax = WORD [eax + 0x572]` = STAR COUNT (gate `test ax,ax; jle` skip).
- Loop: `mov ebx,[esi]` stride 4 => TABLE = u32 POINTER array, count at +0x572.
- STAR RECORD fields read by the painter:
  * +0x00: u32 (loaded at 0x52822 region? no — `mov ebp,[ebx]` value unused for
    blit; candidate id)
  * +0x04: BYTE visibility flag (0x52807 `mov ah,[ebx+4]`; 0x52813 `test ah,ah;
    jne skip` — flag SET => star NOT drawn)
  * +0x0d: FLOAT x-offset relative to field centre (0x527fe `fld [ebx+0xd]`)
- Sprite lib handle: `0x56d8c(0x7a35c, edx=0x2bdb)` — 0x2bdb is a pool-relative
  string immediate (imm = str_off - 0x82bb0 law => str_off = 0x8596b) = the .shp
  lib name. Assert string 0x2be5 right after = assert file/name string.
- Shape index per star = class via lookup `[ebp*4]` where ebp = class selector
  (0..3) — sprite shape 0/1/2/3 in that lib.

### L2 PROJECTION (cited)
0x527fc..0x5282f verbatim:
    mov ebx,[esi]            ; star rec
    fld dword [ebx+0xd]      ; x = rec float
    fadd dword [ds:0x2bf3]   ; + centre constant (read it: data-seg float)
    mov ah, byte [ebx+4]     ; vis flag
    call 0x76e08             ; float->round (banked? verify = FIST helper)
    fistp [esp+0x20]
    test ah,ah ; jne next
    mov ecx,3
    mov eax,[esp+0x20]
    mov ebp,[ebx]            ; rec u32 low (class source candidate)
    cmp eax,0xdc             ; 220
    jle 0x52787              ; -> class 1 / class 2 arms
    xor ecx,ecx              ; x>220 => class 0
  0x52787: eax>0 => class 1 ; eax<=-220 (0xffffff24) => class 2 ; else class 3
  => SCREEN X = round(rec.x + C2bf3) (NO perspective divide); the value also
  selects the sprite class by |x| bands: (0,220]->1, >220->0, <=-220->2,
  [-220,0]->3. 220 = half of the 440-wide field (field rect x380..0x278=632?
  see rect census below) — bands = inside-left / outside-right etc.
  Y: candidate rec u16 @+0xf or +0x11 (0x52801 `fadd` consumed float at +0xd;
  the class cmp uses the SAME float+delta). NOT yet: where Y comes from.
  KEY SHAPE FACT: the animation value is added INSIDE fld [ebx+0xd] + fadd —
  see L3: [esp+?] = animation delta added to x => rotation is an x-shift?? No:
  re-read — 0x527fe adds [ds:0x2bf3] only. The animation word feeds the
  SPRITE/TEXT path at 0x52834+ (blit of lib 0x9f10c text). VERIFY.

### L3 ROTATION PUMP (cited)
- Event arm at 0x528eb (dispatcher head `cmp dx,0x1f5` cascade):
  * msg 0x1f6 (0x52db9): `inc WORD [eax+0xb7]`; if ([eax+0xb5]>>16)==5 then
    [ebp+0xb7]:=0. Then fn 0x226e4(0x12e10,...) + repaint call [ebx+0xc] +
    fn 0x28fc0 on player obj (0x6a50-indexed).
  * msg 0x1f7 (0x52e58 via 0x52f49): `inc WORD [eax+0xb9]`; if ([+0xb7]>>16)==8
    then [+0xb9]:=0; fn 0x22ce4; posts fn 0x28fc0.
  * msg 0x1f9 (0x52eec): `inc WORD [eax+0xbb]`; if ([+0xb9]>>16)==3 then 0.
- Timer: fn 0x28fc0 = one-shot re-poster (posts msg 0xc at 0x52b65 context;
  called at 0x52e19 for the 0xb7 counter with object ds:0x6a50*4*... + 0x7a360).
  => pump = self-reposting one-shot timer per counter. RATE = the delay arg of
  fn 0x28fc0 (read its body).
- Three counters +0xb7/+0xb9/+0xbb = three animated fields (big field uses
  which? the msg ids differ per window instance; both fields share painter
  0x52114/0x526b4 per tNG-C).

## S3. MEASURED (probe 1) — payload strings + float constants (file law:
## ds:X -> payload file 0x82bb0+X; VERIFIED against work/ascend_payload.bin)
- ds:0x2bdb = 'COSMOSWnd'; ds:0x2be5/0x2b85/0x2b93/0x2bb1/0x2bcd = '..\status.cpp'
- ds:0x2bf3 = float -1500.0 (bytes 00 80 bb c4 VERIFIED)
- ds:0x2ba1 = 'DATA\smhome.shp'; ds:0x2b79 = 'newgame.txt'
- ds:0x88b88 = float pi/180 (0.017453292); ds:0x88b8c = 180/pi (57.29578)
- Ghidra decompile FUN_000526b4 CONFIRMS the asm: table = [COSMOSWnd+0x172]
  (u32 pointer array), count = WORD [COSMOSWnd+0x572] (SOLE read in image).

## S2. (initial open list, superseded by S5-S7)
- Q1: what is [ds:0x2bf3] float value (centre constant)?
- Q2: does the star x get the animation delta (where does +0xb7 enter the x
  math)? The painter body above never reads +0xb7 — so either the GENERATOR
  bakes angle per star per frame, or a fn called per-paint mutates rec+0xd.
  Candidates: fn 0x226e4 / 0x22ce4 (called right after each inc) = the ANGLE
  ADVANCERS writing the table.
- Q3: star record full layout (y at which offset; stride).
- Q4: generator: writer of obj+0x572 count / +0x172 table.
- Q5: pool string at 0x8596b (lib name) + assert strings 0x2bdb/0x2be5 decode.


## S5. tNGS CYCLE 1 MEASURED — THE MODEL IS 3D PERSPECTIVE, NOT A 2D FAKE.
## All cited from work/ascend_restored.bin (Ghidra FUN_* + capstone chains).

### L1 STAR TABLE — CLOSED (painter side)
- Painter FUN_000526b4 (status.cpp) resolves COSMOSWnd by name (call 0x56d8c,
  imm ds:0x2bdb='COSMOSWnd'), reads count = WORD [COSMOSWnd+0x572] (sole read
  0x52768) and table = [COSMOSWnd+0x172] (u32 pointer array, 1024 slots).
- Records are 21-byte (0x15) CLIP records — stride proven by the clip BUILDER
  FUN_000284bc loop tail `piVar11 += 0x15`. Fields (builder writes / painter
  reads, all cited):
    +0x00 u32 shape-bank index (painter: shape = 4*rec[0] + class)
    +0x04 u8  flag (nonzero => painter SKIPS the star)
    +0x05 u16 screen X ; +0x07 u16 screen Y (PRECOMPUTED; painter maps v/5+5)
    +0x0d f32 depth channel ; +0x11 u32 (0 in the star arm, -1 sentinel othr.)
- Blit: FUN_0005caac(surface=COSMOSWnd+0xab, shape, y, x).

### L2 PROJECTION — CLOSED
- Projection fn FUN_00053374: perspective divide (fdiv dword [eax+8], eax =
  camera/view block), frndint via helper 0x76e08, +0.5 bias (qword ds:0x2c50
  = 0.5 VERIFIED as double 0.5? -> raw bytes 000000000000e03f = 0.5), then
  += viewport offsets from [COSMOSWnd+0x574]/[+0x576] >>16 (call sites
  0x285c0/0x286ba/0x28a3a inside FUN_000284bc).
- Camera init FUN_00026a9c (VERBATIM call chain in banked dump
  work/tNGC_paint526b4.asm 0x52aa1..0x52aad: mov edx 0x2c02 'COSMOSWnd', call
  0x56d1c, call 0x26a9c):
    [cos+0x57a] = 35.0f                       ; FOV
    FUN_000203b8(35.0, 1.0, 100000.0, [cos+0x574]>>16, ...)   ; view setup
    result+0x10e/+0x112/+0x116 = 0,0,-1500.0  ; CAMERA POSITION z=-1500
    result+0x14e..+0x16e = identity 3x3       ; ORIENTATION MATRIX
  (0xc4bb8000 = -1500.0, 0x3f800000 = 1.0 — decoded from the decompile's raw
  immediates.)
- Painter class law (sprite variant per star), cited asm 0x52817..0x5282f +
  0x52787..0x5279e, Ghidra agrees:
    v = round(rec.depth - 1500.0)   ; ds:0x2bf3 = -1500.0
    v > 220        -> shape bank +0
    1 <= v <= 220  -> bank +1
    -219 <= v <= 0 -> bank +2
    v <= -220      -> bank +3
=> 'Volume of stars in a rotating sphere' = 3D points + perspective camera at
   z=-1500, FOV 35. NOT a 2D fake. Rewrite's shell/clip samplers are the bug.

### STAR GENERATOR (L1 other half) — STRONG LEAD, one decode short
- FUN_0004709c builds 100 entries x 3 floats (x,y,z) at param+0x143: init
  (0, k, 0) for k=0..99, then rotates entries by FUN_0005324c (2D rotation in
  DEGREES: DAT_00088b88 = pi/180 VERIFIED) with 360/n steps; a colour/band
  census loop over DAT_00074744 records (stride 0x4b=75). ALTERNATE path loads
  from FILE via FUN_00077fe1 with format imm ds:0x24bb (DECODE NEXT ITER:
  payload file offset 0x82bb0+0x24bb). This is the 100-star table D21 names.

### L3 ROTATION PUMP — PARTIAL (honest)
- Event arms (dispatcher at 0x528eb, banked dump): msg 0x1f6 @0x52db9 incs
  WORD [win+0xb7] (wrap to 0 when [win+0xb5]>>16==5), calls FUN_000226e4 on
  game obj 0x12e10, repaints via call [win+0xa7 class table +0xc], and
  FUN_00028fc0(player obj) = one-shot timer RE-POST (self-sustaining pump).
  msg 0x1f7 @0x52e58 -> [win+0xb9] wrap 8, FUN_00022ce4. msg 0x1f9 @0x52eec
  -> [win+0xbb] wrap 3.
- FUN_000226e4 = {0x22878, 0x22728, 0x234a4, 0x22ce4}. FUN_00022728 rebuilds
  a 13-byte-stride table at game+0x3067e (count word game+0x306f2; max 9
  entries; rng: y=rng%600-300 rotated, x spread mod 360/n) — NOT the star
  clips (9 << 100); candidate 9-race home markers [unverified].
- OPEN HOLE (named, not guessed): who mutates the camera ORIENTATION matrix
  ([cam+0x14e], heap block from FUN_000203b8) to spin the field, + rate.
  FUN_0005324c callers = {0x22728, 0x238e8, 0x38f68, 0x4709c} — none is a
  per-frame spin. Right instrument: dbg-build BP at FUN_000284bc entry, dump
  [cam+0x14e] twice ~2s apart => angle delta + axis cited; plus timer delay
  arg inside FUN_00028fc0 body.

## S6. FAITHFUL PORT SPEC (from S5)
1. 100 stars x,y,z floats (source law pending P1); 2. camera pos (0,0,-1500),
FOV 35, near 1, far 1e5; 3. perspective divide + 0.5-bias round + viewport
centre offset; 4. sprite = bank*4 + depth-class bands (>220 / 1..220 / -219..0
/ <=-220); 5. self-reposting timer pump; 6. NO sphere clip — containment is
intrinsic to the 3D positions (our clip is the bug D21 sees).

## S9. CYCLE 2 P1 — FUN_0004709c GENERATOR: NOT THE STAR SOURCE (REFUTED)
[measured, asm work/tNGS_gen1.asm + work/tNGS_gen2.asm, 0x4709c..0x47464]
- The 0x471f9 "generator" body is the TECH-TREE layout generator, not a star
  generator. Evidence: it iterates the tech census WORD[0x74744] over records
  stride 0x4b at 0x74784 (the RESTREE record law, OQ-013), reads the 5
  child/prereq slots (0x74784+rec, bytes 0xFF-terminated), builds a
  child-after-parent ORDER array (0x47240..0x472c0), rng-permutes it
  (0x472d4..0x47300), then places each star record at y = 240 + 30*step +
  15*(step&1) (0x473e0..0x47428: fild [esp+0xdc], fstp [ebx+4]), z-degrees =
  0 or 23 (0x473b6), x=0, then rotates by angle = 360/(childSlot-1) + 0.1*i
  (0x4743d..0x47464, idiv 0x168=360, fadd [esp+0x100]). Camera fov30/z-150/
  320-wide = the research-tree view. The cycle-1 note "rotate loop ... via
  FUN_0005324c degrees" was a misread: 0x4743d is INSIDE this body, not a
  separate star loop.
- File branch 0x4713e..0x471e3 reads N records x 3 ints (fmt ds:0x24bb,
  3x ds:0x24be) gated on WORD[0x74744]==file-count — also tech-tree (count
  must equal the tech census), and its file is absent anyway.
=> CONSEQUENCE: the COSMOSWnd star table source ([COSMOSWnd+0x172], count
   WORD +0x572) is STILL UNNAMED. P1 re-scoped: find who allocates/fills it.
   Clue: records are 21-byte CLIPS with PRECOMPUTED screen x/y at rec+5/+7 —
   so the rotator writes clip coords every tick; the clip builder FUN_000284bc
   + its callers is the direct hunt (this also serves P2).
## S10. CYCLE 2 P1 CONT — CLIP BUILDER FUN_000284bc DECOMPILED (VERIFIED)
- Sole caller 0x2745b (GAP fn; also sibling tail 0x273e6) — both legs:
  call FUN_00028fc0 (pump re-post) then FUN_000284bc(win) then vtable
  [win+0xa7]+0xc repaint. So the builder runs right before each repaint.
- Body law [verified decompile]: cursor piVar11 = *(win+0xb3), start
  adjusted -0x15, loop stride +0x15 (21B). WIN IS param_1+0xb3 POINTER —
  NOT +0x172 (cycle-1 said table=[COSMOSWnd+0x172] from the painter;
  reconcile: +0x172 is the painter-side array, +0xb3 the builder cursor —
  may be same block via different fields, UNRESOLVED, name it).
- Per-record kind byte = byte[rec+1] (piVar11+1):
  0 = STAR: FUN_00053324 (point x 4x4 matrix -> vec3, VERIFIED decompile:
  out = m[0..3]*v etc incl translation column m[3]/[7]/[11]) then near/far
  gate (win+0x106/+0x10a) then FUN_00053374 perspective -> writes rec+5=x,
  rec+7=y, rec+0xd=depth, rec+0x11 = 0 (visible) or -1 (skip). MATRIX ARG
  = the transform operand of 0x53324 at 0x28552 (register-passed; identify
  which = THE rotation question).
  1 = LINE segment (two 0x53324 + two 0x53374, writes rec+5/7/9/b).
  2 = object sprite (ship): byte[src+0x58]==5 special 3D; else copies
  src+5/+7 coords with owner-bitset x-offset +2 per owner (0x28b0x loop
  over 7 bits of [src+0x14] & [win+0xd8]) — MAP objects, not stars.
- Loop exit: win+0xb5>>16 <= counter -> FUN_0002976c, return.
- NEXT: identify the matrix operand at the 0x28552 star site (disasm
  0x28540..0x28560); xref FUN_0005324c 4th caller 0x38f68; find writer of
  rec+0/+4 (world xyz) for kind-0 records; find allocation of the +0xb3
  block (count + 3D coords).
## S11. CYCLE 2 P2 PREMATURE WIN — ROTATION LAW FOUND STATICALLY (VERIFIED asm)
THE COSMOSWnd message-handler GAP fn (0x27100..0x27ad7 region; esi=win)
CONTAINS THE ROTATION PUMP + WRITER. Cited verbatim:
- WINDOW-INIT leg (msg==3 @0x27107): sets rect fields +0x8/+0xc/+0x10/+0x14,
  viewport words: [win+0x576]=((y1-y0)>>1) (0x27147), [win+0x578] via x
  (x1-x0)>>1; [win+0x57a]=0x420c0000=35.0 (FOV, 0x2716c); camera re-init
  FUN_000203b8(win+0xda, fov=[win+0x57a], near 1.0, far 5e4, w) @0x27187.
- ROTATION WRITER FUN_000283e4(win, edx, f32 angle_deg) [asm 0x283e4..0x28422]:
  fmul [0x9f108] (radian factor, VERIFY) -> edx==-1 ? FUN_00053584 :
  FUN_00053554 on MATRIX lea eax,[win+0x14e]. THE ORIENTATION WRITER, NAMED.
- FUN_00028428 [0x28428..0x284b9]: guard [win+0x57a] vs consts [0xfb0]/[0xfb4];
  [win+0x57a] += int * [0x9f108] (0x28477); camera re-init 0x203b8;
  invalidate via FUN_00029740. ZOOM/FOV control, not the spin.
- DISPATCHER leg (0x27a18..0x27acb, esi=win), gates on byte [win+0xc0]:
  bit0 -> FUN_000283e4(angle = bit1 ? -2.0 : +2.0, edx=-1)  @0x27a4b
  bit2 -> FUN_000283e4(angle = bit3 ? +2.0 : -2.0, edx=0)   @0x27a80
  bit4 -> FUN_00028428(edx = bit5 ? +1 : -1)                @0x27aa3
  any(bit0|bit2|bit4) -> FUN_000284bc (rebuild clips) + vtable +0xc repaint
  @0x27ab7..0x27ac6. NONE -> ret.
=> ROTATION LAW: each pump tick with a direction bit set rotates the
   [win+0x14e] orientation matrix by 2.0 DEGREES about one of THREE axes
   (edx selector), then rebuilds the clip table and repaints. The three
   counters +0xb7/+0xb9/+0xbb (wraps 5/8/3) are the carousel indices; WHO
   sets [win+0xc0] bits is the remaining sub-question (auto-spin vs key
   press — keys 0x1f6/0x1f7/0x1f9 arms in the painter dispatcher 0x528eb
   inc those counters; [win+0xc0] setter hunt next).
- Clip builder FUN_000284bc CONFIRMED CONSUMER: cursor [win+0xb3], radian
  matrix ops via FUN_00053324 (4x4 affine point transform, VERIFIED).
## S12. t416 SUPERSEDURE + FIELD RECONCILIATION (VERIFIED)
- THE ROTATION LAW IS ALREADY CLOSED by t416 (docs/re/_wip_t416.md F1/F2 —
  banked 2026-11-17, port cam3d.cpp implemented F3): COSMOSWnd msg pairs
  0x32/0x33 (L/R latch bits0/1), 0x34/0x35 (U/D bits2/3), 0x36/0x37 (zoom
  bits4/5) on [win+0xc0]; pump msg 0x3b (~1/s, t302 MEASURED) applies
  delta = +-2 DEG per latched pair: L/R -> FUN_00053584 (mixes x,z = WORLD
  Y), U/D -> FUN_00053554 (mixes y,z = WORLD X) on basis [win+0x14e]
  (eye (1,0,-1500), up (0,1,0), fwd (0,0,1) — FUN_00026a9c immediates),
  right=cross(up,fwd) recomputed FUN_00053804; NO clamp; toggle-latch press
  semantics. S11 this-session = INDEPENDENT RE-DERIVATION of the same law
  (dispatcher 0x27a18, writer 0x283e4, radian mult via 0x531dc/0x5324c ->
  DAT_00088b88 pi/180) — CORROBORATION, not new law. P2's debugger witness
  is CONFIRMATORY ONLY; the axis+rate citation for P4 = t416 F2 + t302.
- f32[0x9f108] = bss delta-scale, runtime value measured ~0 in bank-41.sav
  (reads denormal, effectively 0 => delta degenerates to +-2 immediates;
  t416 S-d law 'port documents scale 1.0' stands).
- FIELD RECONCILIATION: runtime window fields = static + 0xbf (runtime
  +0xb3 == static +0x143 'camera basis'?? NO — cycle-1 painter read static
  +0x572 == runtime +0x4b3; builder reads RUNTIME +0xb3/+0xb5/+0xc0/+0x57a
  (0x57a appears with the SAME role in both t416 and 0x2716c init 35.0).
  UNRESOLVED which address system each doc used; the BUILDER asm is ground
  truth: cursor ptr runtime[win+0xb3], count runtime[win+0xb5]>>16, latches
  runtime[win+0xc0], zoom runtime[win+0x57a]. Name it; do not blend.
## S13. CYCLE 2 P1 CLOSED — THE STAR SOURCE IS THE CAMPAIGN GALAXY TABLE
[verified: work/coswnd_decomp/28fc0.c + 268d4.c + fresh asm 0x284d8..0x28570,
 0x26a13..0x26a86; measured: bank-t438-ring-2200/41.sav via
 scripts/t441_race_table_census.py coordinate law]
- FUN_00028fc0 IS THE CLIP-TABLE PRODUCER (cycle-1 called it only a pump
  re-post — WRONG; correction banked). Three append loops, each writing at
  ([win+0xb3] + ([win+0xb5]>>16)*0x15): rec+0 = SOURCE POINTER, rec+4 = KIND:
  kind 0 = STARS: &LAB_00013bc5 + k*0x60, k < DAT_00016143._2_2_ (star count);
  kind 1 = LINE segs: &PTR_DAT_00016147 + k*0x27 gated by DAT_00089324 bits;
  kind 2 = SHIPS: &DAT_0003a095 region stride 0x162, k < 0x6b, gated by
  DAT_00043489 count + byte==5. 21-byte cursor array allocated at 0x26a4f
  size = count*21 ((edi*4+edi)<<2+edi), freed/realloc'd on init (0x26a13..).
- RECONCILIATION (the cycle-1 +0x172/+0x572 vs +0xb3/+0xb5 confusion):
  [win+0xb3] = 21-byte CLIP RECORD cursor array the producer fills and
  builder 0x284bc walks; [win+0x172] = u32 POINTER array the builder appends
  visible clips into via FUN_0002974c (0x29740 zeroes count at +0x172+0x400
  = +0x572). Painter reads the pointer array + count word. ONE table, two
  stages, both cited.
- STAR COORDINATES: star rec pointer stored at rec+0x28 of the star record
  (LAB_00013bc5 == STATE+0xdb5 == star-base STATE+0xd8d + 0x28); builder
  kind-0 leg (asm 0x2853f..0x28552): mov eax,[clip]; add eax,8 ->
  FUN_00053324 transforms THE FLOAT TRIPLE AT STAR RECORD +0x30/+0x34/+0x38
  — the EXACT campaign star table (t441 law, STATE+0xd8d+0x60j).
- MEASURED 3D DISTRIBUTION (41.sav, T=50 decoded 50/50): x [-412.9,376.9]
  y [-421.9,436.3] z [-421.3,402.4]; radius sqrt(x2+y2+z2) in [50,440];
  z independent of x,y (0/50 zero, stdev 222) — the galaxy is a VOLUME, not
  a plane. Mapgen (OQ-012c/OQ-025 CLOSED shells) supplies x,y; z is the
  third axis of the same generation. => D21 'rotating sphere containing a
  volume of stars' = THE GALAXY ITSELF projected; newgame screen shows the
  demo galaxy (~100 clips per tNGF census).
- CONSEQUENCE FOR PORT: star source = existing closed mapgen law extended
  to 3D (z same magnitude as x/y, sphere containment intrinsic — max radius
  440 at T=50); NO separate star RNG; NO reswin.txt (that fn 0x4709c is the
  TECH-TREE layout, S9). Rotation law = t416 (world Y/X basis orbit +-2deg
  per pump tick, pump ~1/s t302-measured) — P2 dbg witness now CONFIRMATORY
  only, not a port prerequisite.
## S7. CYCLE 2 PROBES, ORDERED
 P1 decode FUN_0004709c's file format string ds:0x24bb + find the shipped
    star file; if absent -> generator law only (say so honestly).
 P2 dbg scratch session: BP FUN_000284bc entry; bank ret0 + orientation
    matrix [cam+0x14e] x2 ~2s apart -> axis + rate MEASURED.
 P3 pump census: fires/s of msgs 0x1f6/0x1f7/0x1f9 (t302 protocol) + read
    FUN_00028fc0 delay arg.
 P4 port + pins: count=100, radial profile + colour census vs refcap (t441
    regions), ROTATION pin (two shots ~2s apart, field rotated by cited rate).
 P5 re-package scratchpad/NG-usergrade.png (--checklist) -> NEXT =
    WAIT-USER-GRADE-NG3.


## S8. CORRECTIONS + CLOSER DETAIL (same iteration, late probes — VERIFIED)
- FUN_0004709c's file path: opens 'reswin.txt' (imm ds:0x24b0 VERIFIED).
  FILE ABSENT from the shipped tree (work/r1/game/: no reswin.txt; cob
  extraction has none) => FUN_000206c0 returns 0 => the GENERATOR branch is
  the live vendor law. Honest negative banked.
- Generator verbatim (asm 0x470aa..0x470ed + Ghidra): N=100 records stride 0xc
  at obj+0x143; init x=0.0, y=k (0..99), z=0.0. Then view/viewproj init
  FUN_000203b8(fov=30.0 [0x41f00000], near=1.0, far=50000.0 [0x47c35000],
  320 [0x140], ...) and position block obj+0xdf = (0,0,-150.0 [0xc3160000]).
  NOTE this camera (fov30/-150/5e4, 320-wide) DIFFERS from the COSMOSWnd
  camera in FUN_00026a9c (fov35/-1500/1e5) — two cameras; the COSMOSWnd one
  is the one the star painter's clips use (built at newgame msg arm 0x52aad).
- Rotation primitive FUN_0005324c: rotates (v[0], v[2]) by param_1 DEGREES
  (x' = x*cos - z*sin; z' = z*cos + x*sin), no-op when param_1==0.
- qword ds:0x2c50 = 0.5 (VERIFIED double) — the round bias in FUN_00053374.
- L3 rate structure: three counters wrap at 5 / 8 / 3 => combined period
  120 pump ticks; each tick repaints the field; the pump is fn 0x28fc0
  one-shot re-post. WHO ROTATES the COSMOSWnd orientation matrix
  ([cam+0x14e]) is STILL UNNAMED statically (honest negative; instrument =
  dbg BP at clip builder FUN_000284bc entry, dump matrix twice ~2s apart).

## S14. CYCLE 3 — W1 STATIC HALF: AUTO-LATCH SITE FOUND (VERIFIED asm,
## work/tNGS3 state-map census + t442_disasm 0x26b34..0x26e90)
- COSMOSWnd msg handler ENTRY = 0x26b34 (esi=win; msg cascade dx: 0x3b pump ->
  0x27a18 VERIFIED at entry 0x26b5b/0x26b65; dials 0x32..0x37 -> latch chain
  0x27824..0x27d2a region per t416).
- WINDOW-STATE DISPATCH: state = DAT_0007e582 >> 16 (same read at 0x26cf6 for
  the race-count mirror 0x13b96 — HIWORD law). Branches inside the init leg:
  * state==3 (0x26d43): rect (17,12,324,320), FOV 35.0, camera re-init
    0x203b8, and 0x26dd1: `mov dword [esi+0xc0], 1` — BIT0 LATCH SET =
    AUTO-ROTATE ON at window init. (t416 msg-3 leg = this branch.)
  * state==0xd (0x26e36): rect (0,0,323,315) — the 320-wide DEMO field; latch
    store for this branch NOT yet read (disasm owed 0x26e90..0x26f65).
  * state==7 (0x26e1f setne->dec): [esi+0xd4] = (state!=7 ? 1 : 0).
- Generic init tail 0x26c89: `mov dword [esi+0xc0], 0` (latch CLEAR) preceded by
  call 0x56374(0x7a35c, ecx=0, edx=[esi+0x41], 0, 0) with ebx=0x3b pending —
  pump-post context.
- CONSEQUENCE: whether the NEWGAME field auto-spins = WHICH state value the
  newgame screen opens COSMOSWnd in (state 3 => latched spin at init; a branch
  that stores 0 => static). W1 witness decides: BP 0x283e4 (writer entry:
  eax=win, edx selector, f32 angle at [esp+0xc] per VERIFIED asm 0x283e4..
  0x28422) + BP 0x26b34 (read DAT_0007e582 at entry = the screen state code).

## S15. CYCLE 3 — Z1 STAR-Z LAW CLOSED [verified asm, work/tNGS3_22878a/b.asm]
THE STAR-POSITION GENERATOR IS FUN_00022878 (0x22878..0x22ce1; sole caller
0x226fe = the msg-0x1f6 arm family). Per star k (loop 0x22a0c..0x22cc4,
ebp = [esp+0x7fc] + k*0x60, [esp+0x7fc] = lea [game+0xdb5] at 0x229ab — the
campaign star table, t441 base law):
 1. field clears +6=0xffff, +0x14..17=0, +0x44=0, +0x5a=0 (0x22a20..0x22a49).
 2. TYPE draw: rng (FUN_0007824f) % [esp+0x810] + 1, weighted scan of the
    13-entry starstat population table u16[0x63ac..] (0x22b2c..0x22b61),
    STORED [ebp+0] = record type.
 3. POSITION TRIPLE: THREE consecutive draws (0x22b61/0x22b8d/0x22bb4):
    v = (rng%1000-500, rng%1000-500, rng%1000-500) (idiv ecx=0x3e8, sub
    edx,0x1f4 — VERIFIED bytes 0x22b66 'b9 e8 03 00 00 ... 81 ea f4 01 00 00'),
    fild each -> f32 at esp+0x7e8/7ec/7f0; FUN_00052fa0 = NORMALIZE
    (sqrt(x2+y2+z2) via 0x76da0, divide by length when length>0 — VERIFIED
    asm 0x52fa0..0x52ff0); then multiply all three by the SHELL ACCUMULATOR
    [esp+0x820]; store esp+0x7dc/7ec/7f0 -> [ebp+8], [ebp+c], [ebp+0x10]
    == rec+0x30/+0x34/+0x38 (base game+0xdb5 = STATE+0xd8d+0x28 law).
 4. SHELL SCHEDULE constants CODE-VERIFIED (the r1-savestate.md 'INFERRED'
    formula r=max(50,440-75j) is now law): start edi=440.0 (0x2288c
    'bf 00 00 dc 43'), per-shell add -75.0 (f32 [0x836fc]=0xc2960000 VERIFIED),
    reset imm 50.0 (0x22aee 'c7 84 24 20 08 00 00 00 00 48 42' = 0x42480000
    VERIFIED) gated on fcomp [0xb50] (bss, runtime — cycle-2 pitfall stands).
=> Z LAW: z is NOT an independent axis — (x,y,z) = normalize(uniform
   [-500,499]^3) x shell_radius. Direction = uniform-in-box NORMALIZED to the
   unit sphere (refines OQ-012c 'uniform on sphere [inferred]': the actual
   mechanism is box-normalize, which is ALMOST sphere-uniform but slightly
   favours axis directions; density weight = 1/|v(direction)|^2 of the box
   ray). Envelope: r = shell(k) in {440,365,290,215,140,65,50} — matches the
   measured 41.sav radius band [50,440] exactly; z-independent-of-x/y observed
   IS the isotropy of the normalize.
=> PORT (P4): draw 3 ints rng%1000-500, normalize, scale by the OQ-025 shell
   radii list — no separate z sampler, no statistical seam. The tNGS cycle-2
   'port draws z uniform-in-envelope as a NAMED SEAM' clause is RETIRED.

## S16. CYCLE 3 W1 WITNESS — NOT YET DECIDED (honest negative); instrument
## fixed to the point of one more session. State of play:
- Legs armed successfully 4x (w1_writer 0x283e4, w1_pump 0x27a18, w1_hdlr
  0x26b34 at P0+off; BPLIST confirmed each time; BREAK lottery ~50% per
  launch -> scripts/r_tNGS3_w1_relaunch.sh wraps 5 launches).
- Navigation failure chain (each fix banked as a PITFALL):
  1. t287 title slot table (193..473) does NOT apply to a fresh-boot scratch
     title: rows sit 200..230 PlayIntro / 240..270 Tutorial / 280..310
     NewGame (navy-row detector measured on run 141025). Arrow keys do NOT
     move the menu highlight (it is HOVER state).
  2. RFB CHANNEL DEAD on this machine build: bundled
     work/r1/localdeb/root/usr/bin/x11vnc fails at exec —
     libvncserver.so.1 missing (x11vnc.out verbatim). Every RFB move/click
     was silently lost (frames byte-identical). scripts/r287_vncinput.py now
     honours RFB_PORT env (default 5910 unchanged).
  3. xsend warp-click DOES work on the private Xvfb (t292 law) but the
     FIRST click only establishes hover (t385b law re-witnessed: New Game
     row highlighted teal, no transition). Session now sends neutral click
     (320,60) then the New Game click (250,295).
  4. BREAK lottery: settle 45 s then BREAK; hdr=None/no-PONG kills the whole
     launch (in-process retry useless) -> relaunch loop.
- LAST RUN (145012) reached exactly the fixed nav sequence; the two-click
  fix had not yet been observed end-to-end when budget closed. NEXT session:
  run scripts/r_tNGS3_w1_relaunch.sh; verdict lands in dbg-tngs3w1-*/w1.json
  ("AUTO-SPIN ON..." vs "STATIC..." per the S14 leg table).

## S17. CYCLE 3b W1 RUN — NAV ROOT CAUSE MEASURED (run dbg-tngs3w1-20261122-151714)
Frame diff _raw_03 (title settled, orange 0.679) vs _raw_04 (after the
two-click nav): changed row bands = 339..370 and 380..410, ZERO px in
275..315. Vision on _raw_03: rows are PlayIntro ~295-338, Tutorial
~339-371 (TEAL highlighted), New Game ~378-412, Return/Load/Save/Exit
below; game 640x480 content sits at root (80,100)..(720,580) on the
800x600 private Xvfb.
=> TWO LAWS: (1) xsend click coords are WINDOW coords (root = +80,+100);
   the script's (250,295) landed EXACTLY on the New Game row (root y 395).
   The fresh-boot row table 280..310 NewGame in GAME/window coords is
   CORRECT. (2) The neutral-first-click variant was WRONG: the target-row
   click DID move hover onto New Game (band diff proves it) but the press
   was still consumed as hover-establishment. t385b REFINED: the first
   click ON A ROW only hovers; click the SAME row twice (first=hover,
   second=fire). Script patched: NewGame click x2 with 2 s settle, plus a
   conditional third; Begin click likewise x2.
## S17b. Same-row DOUBLE-click also FAILED (runs 153216/153535: identical
frame diff — hover moved to New Game, orange unchanged 0.679). Combined
with the t439 law ("xsend key Return failed; RFB/PointerEvents worked"):
xsend's XSendEvent ButtonPress is SYNTHETIC and the dbg dosbox ignores it;
the hover moves because XWarpPointer is a real warp. FIX = XTEST channel
(xdotool mousemove+click = real fake-input events).
## S18. ROOT CAUSE OF ALL NAV FAILURES + FIX (verified on disk)
The RFB channel (the ONLY proven firing input: t292/t439 entered campaigns
through it) was DEAD in every tNGS3 session: x11vnc.out verbatim
"error while loading shared libraries: libvncserver.so.1". Production
(r1_playcap_vnc.sh:158) exports LD_LIBRARY_PATH=$DEB/root/usr/lib/... when
launching x11vnc; r_tNGS3_w1_session.py launched it WITHOUT that env, and
set rfb_* helpers to the WRONG offsets (192/184) — the fresh-Xvfb window
origin is (80,100) (vision-measured game content 80..720 x 100..580),
matching r287_vncinput defaults RFB_XOFF/YOFF=80/100. xsend's XSendEvent
presses are SYNTHETIC: they warp the real cursor (hover moves) but the
vendor never fires them — that is the complete t385b "first click only
hovers" explanation. FIX: LD_LIBRARY_PATH in the Popen env + nav via
rfb_move/rfb_click (offsets 80/100) with double-click insurance.

## S19. CYCLE 3b VERDICT: W1 STILL UNDECIDED — nav fixed to the LAST
## open question (one control experiment away). Honest negative, banked in
## full. Runs: 151714/153216/153339/153535/155426/155552/155718 (+3 BREAK
## lottery losses).
WHAT THIS ITERATION PROVED (all measured, runs above):
 1. xsend (XSendEvent) presses are SYNTHETIC: XWarpPointer moves the real
    cursor (hover repaints) but the vendor NEVER fires the press. Neutral-
    first-click and same-row-double-click variants BOTH failed with the
    IDENTICAL frame diff (bands 339-370 + 380-410 only).
 2. The bundled x11vnc died at exec EVERY prior tNGS3 session
    (libvncserver.so.1) — FIXED this iteration by exporting
    LD_LIBRARY_PATH=work/r1/localdeb/root/usr/lib/x86_64-linux-gnu in the
    Popen env (r1_playcap_vnc.sh:158 precedent). Verified: x11vnc 0.9.17
    starts, accepts connections (x11vnc.out of 155718 logs them).
 3. rfb_* helpers carried the WRONG offsets (192/184 production-drift);
    fresh-Xvfb window origin is (80,100) (vision: content 80..720 x
    100..580) = r287 defaults. FIXED.
 4. With RFB move+click at correct coords: hover lands ON New Game and
    STAYS (vision on _raw_04 of 155718), guest is RUNNING (frames
    repaint), yet orange stays 0.679 — the press does not activate.
STILL OPEN (the ONE question): do synthetic button events fire the dbg
dosbox-x-dbg title menu AT ALL? t287 (production) shows an RFB click DID
activate a row (the stale-hover Tutorial — DOSBox processed press with
pre-move coords). If clicks fire on dbg, the New Game row should have
transitioned (stale-hover would fire TUTORIAL, changing the screen — it
did not). Therefore suspicion: the dbg build or the unfocused fresh-Xvfb
window gates BUTTON delivery while motion still repaints hover.
CONTROL EXPERIMENT FOR NEXT (one session, decide in minutes):
 C1 after arming at the settled title, RFB click the "Exit to DOS" row
    (window (250,448) -> r287 +80/+100 = root (330,548)). Guest QUITTING =
    clicks fire -> then the New Game problem is coordinate/timing-local
    (try click at the vision cursor pos exactly, and a 1 s hold:
    move, press, sleep 1.0, release).
 C2 if no quit: RFB key Return (fires the HOVERED row per t287 — default
    hover is Tutorial; if the tutorial launches, KEYS fire -> nav law =
    move-to-row, wait 1 s, Return; NOTE S16: arrows do NOT move hover).
    Also try xsend key Return once more (xsend calls XSetInputFocus on the
    DOSBox window — t439 said it failed on production, re-verify on dbg).
 C3 if NEITHER fires: the dbg window is input-deaf on fresh Xvfb; then
    run the SAME control against the PRODUCTION binary on a scratch copy
    (no breakpoints needed for C1/C2) to isolate build vs environment.
    If production-scratch fires and dbg does not, W1's dynamic half is
    dbg-instrument-limited: fall back to the STATIC verdict (S14: latch
    auto-fires iff state==3) and CLOSE W1 as "static law cited, dynamic
    witness blocked — named instrument ceiling", then P4 PORT proceeds on
    the static law (auto-spin ON with the t416 +-2deg law) with the
    ceiling stated in the package open-list.

## S20. C2 EXECUTED (run 165042): RFB key Return ALSO did not fire
(after_ng_orange_key=0.679, hover verified on New Game). Both input
channels move hover, neither activates, on dosbox-x-dbg at a fresh :97.
The C3 production-binary control (S19) is the decisive next probe; if it
fires, W1's dynamic half is dbg-instrument-limited and W1 CLOSES on the
S14 static law with the ceiling named (auto-spin ON per state==3 latch,
t416 +-2deg rotation in the port).

## S21. CYCLE 3c C3 CONTROL — LAUNCHED (scripts/r_tNGS3c_c3_session.py)
Design (decided BEFORE the run so the verdict can't drift): production
/usr/bin/dosbox-x on a fresh private Xvfb :97, scratch game-wp only, own
x11vnc 5911 with LD_LIBRARY_PATH (S18), RFB offsets 80/100, RESUME.GAM = the
md5-asserted Oct-29 copy (same menu geometry as the dbg sessions). A rung
ladder is recorded SEPARATELY so the first FIRING channel is identified:
  A RFB move(250,295) hover witness (teal rows + band diff)
  B RFB click x2      C RFB press-hold 1.0 s
  D xsend key Return (TITLE arg law xsend.c:54; XSetInputFocus first)
  E RFB key Return (hovered-row law t287)
Fired = title orange < 0.20 (wait_title law r293_move_session.py:374).
VERDICT TABLE: production fires => dbg BUILD is input-deaf => W1 dynamic
half dbg-instrument-limited => W1 closes on the S14 static law, P4 ports NO
auto-spin for the newgame/Begin field. Production deaf too => the fresh
unfocused-Xvfb window class is the blocker (build-independent) => same
static-law close, ceiling named as the environment class. Either branch
closes W1 on the static law; only the ceiling wording differs.
Bonus (fires-branch only): two production newgame grabs 12 s apart inside
the state==3 cosmos rect (17,12,324,320) vs a control box (400,40,630,120) =
a VISUAL spin witness for W1 (field px ~ ctrl noise => static; >> => spinning).

## S22. C3 VERDICT + W1 CLOSED BY MEASUREMENT (runs c3-20261122-214652,
## c3-20261122-215511 — production /usr/bin/dosbox-x, scratch game-wp,
## fresh Xvfb :97, own x11vnc 5911, RFB offsets 80/100)
1. PRODUCTION FIRES via rung B (RFB move+click x2 at game (250,295)):
   title orange 0.679 -> 0.006. Rung A hover witness clean: default teal
   band rows 240..270 (Tutorial) -> 280..310 (New Game) after move. =>
   the dbg build dosbox-x-dbg IS input-deaf at a fresh Xvfb (S19/S20 four
   witnesses); the RFB+XTEST channel itself is fine (build-independent,
   t439 production law re-confirmed on a SECOND production session).
2. BONUS: production reaches the NEWGAME screen, so W1's dynamic half was
   NEVER instrument-limited — the debugger legs were the wrong instrument;
   a plain visual witness works. RUN 215511 sampled the state-law cosmos
   panel 6x over 60 s (cursor parked inside the panel at (250,295)):
     frame t+0/12/24/36/48/60 s: field-rect changed px =
       0 / 1082 / 1095 / 1080 / 1085 / 1087  (FLAT, not accumulating)
     control box (400,40,630,120) changed px = 0 at every frame
     star centroid match f1<->f6 (brightest-cluster census, tol 6):
       n1=131 n6=150 matched=34, displacement MEDIAN 0.0 px, p90=4,
       only 8/34 >= 3 px (twinkle jitter, not translation)
   The t416 law is +-2 deg/tick at the ~1/s pump (t302): 60 s of spin
   would be ~120 deg — at r=100 px a star would sweep ~200 px. Observed:
   zero systematic displacement, flat twinkle floor, dead-quiet control.
   RUN 214652 corroborates at 12 s (median 0, rotation-correlation peak
   at theta=0: overlap 0.281 vs <=0.048 at every tested rotation).
3. W1 VERDICT: THE NEWGAME STARFIELD DOES NOT AUTO-SPIN. [verified: two
   production runs, 60 s + 12 s witnesses, pixel-measured] Consistent with
   the S14 static law: the latch store 0x26dd1 sits ONLY in the state==3
   branch (campaign cosmos map); the newgame screen opens COSMOSWnd in a
   different state whose init tail (0x26c89) CLEARS [win+0xc0]. D21's
   "rotating" recollection = the cosmos map, not the newgame field.
   Scope stated honestly: witness covers the at-rest field for the first
   60 s after the New Game click with cursor inside the panel; the
   hover-driven spin-zone law (t423 F7, Begin panel) is separate and
   unaffected. => P4 ports NO auto-spin for the newgame field; the t416
   +-2deg law stays for the COSMOS map only.
4. HARNESS NOTE: crop-pixel counting on RGB must use the per-channel
   zero-bins (min(h[0],h[256],h[512])); the histogram-sum form is
   identically -2*npix on RGB (measured: field=-189112 for a 307x308
   crop). Fixed in scripts/r_tNGS3c_c3_session.py.

## S23. CYCLE 3c P4 PORT + P5 RE-PACKAGE LANDED
P4 (the S15+S22 law, rewrite):
- ascend::game::shellRadiiFor(n) made PUBLIC (mapgen.h/.cpp — declaration
  added, body unchanged); title.cpp preview painter now:
  previewDraws (three rng%1000-500 draws from the cosmosHash word, splitmix
  finalizer) -> previewStar (normalize x shellRadiiFor[i], camera
  (0,0,-1500), focal 769.1, +0.5 bias, well clip) -> SEL = 4*type + cls
  (S5 class ladder). The t423 cylinder (circle r300 + depth+-300) and the
  old focal-500 sphere maths are GONE from this site.
- ROTATION: idle advance REMOVED (S22); only the t423 F7 zone
  (kPreviewSpinZone 379..493 x 420..472, kPreviewSpinArmedPerFrame) turns
  the field. The Begin-panel mini-cluster (beginYaw, title.cpp:1097) is a
  separate site — untouched this cycle.
- New pure law home = ui/menulaw.h (kCosmosCamZ/kCosmosFovDeg/
  kCosmosFocalPx/previewDraws/previewStar).
- PINS (test_newgame_behavior_tNGB.cpp, 5 new): draws range [-500,499] +
  BOUNDARY REACHABILITY (both extremes must occur in 20k draws — the
  bounds-only pin survived a %999 mutant, the reachability term kills it),
  |p| == shell(k) exactly (kills cylinder + sphere-surface samplers),
  class-band edges {221/220/1/0/-219/-220}, projection envelope (shell-440
  equator 440*769.1/1500=225.6 inside well; near-camera tail <=20% honest),
  no-idle-spin (zone geometry + purity of previewStar). SUITE 494/494.
- MUTATION-VERIFIED: cls boundary 220->221 FAILS class test; %1000->%999
  FAILS draws test (after strengthening). Both reverted; suite green.
- RADIAL CENSUS vs refcap: attempted, RETIRED AS UNUSABLE — the vendor
  refcap's cosmos well contains the summary text block (1124 "bright
  clusters" at median r 175 = text-dominated, not a star census). Honest
  negative; the shell pin is code-law-exact instead.
- Witness render: scripts/t412_newgame_shot.sh -> /tmp/t412_shots/
  t412-newgame.png (n 50 law line printed); vision confirms well-wide
  depth-scaled multi-colour field, no circle clip. t441_screen_diff
  newgame PASS on the P4 build.
P5: scratchpad/NG-checklist.txt rewritten (cycle 3: placement law,
NO-auto-spin measurement story, open list = spin RATE seam + right-edge
chrome + Begin-cluster sprite seam — honest: starfield law cited, at-rest
law MEASURED on the original, hover-spin rate is a named seam);
scripts/tNGU_composite.py -> scratchpad/NG-usergrade.png 1290x1704
18/18 PASS t441 rc=0.

## S24. ADOPTION VERIFICATION (fresh session, 2026-11-22 ~23:05)
The cycle-3c session died before its FINISH SEQUENCE; this session adopted
its uncommitted tree. Verification of the adopted state (all re-run, not
trusted):
- rebuild BUILD_EXIT=0; run_tests 494/494 ok (5 tngs_p4_* pins green).
- composite RE-VERIFIED: the shipped scratchpad/NG-usergrade.png is
  reproducible — tNGU_composite.py /tmp/t412_shots/t412-newgame.png
  scratchpad/newgame-original.png OUT --checklist scratchpad/NG-checklist.txt
  -> 1290x1704 18/18 PASS t441 rc=0 (COMPOSITE_EXIT=0).
  HARNESS TRAP: system python3 has NO PIL; the documented interpreter is
  ~/tools/revenv/bin/python (usage string line 22) — has PIL 12.3.0.
- gate GATE_EXIT=0; ledger_audit LEDGER AUDIT OK open=[016,019].
- GAME ring HEALTHY: pid 1470999 up 08:10, Xvfb :9 + x11vnc 5910 alive.
  Timeline tail 2000 lines: turn_max 1086 => NO new sitting (no steering).
No content changes were needed; adoption = verify + commit + NEXT rewrite.

## S25. STRAY scratcphad/ DIR (typo) — UNEXPLAINED, LEFT UNTRACKED
15 desktop screenshots (512x398) landed in ./scratcphad/ at 23:03-23:04
while this session ran. Content = the VENDOR newgame screen (DOSBox menu
bar visible). No script in scripts/ or work/r1 writes that path (grep).
Not mine; left untracked, NOT committed, NOT deleted. BONUS corroboration
(free): frame 1 vs 15 (~12 s apart) whole-frame changed px = 1263/203776
(0.6% twinkle floor) — independent support for the S22 no-auto-spin verdict.

## S26. CYCLE 4 START — D22 CONTRADICTS S22 (the W1 verdict is at risk)
D22 (USER, verbatim): "both starfields do spin all the time, no matter
where the mouse is, and it takes a given star about five seconds to
complete a circuit." S22 measured ZERO displacement over 60 s on
production run 215511 with the cursor PARKED AT (250,295) — inside the
Begin panel. The two are reconcilable ONLY if spin is cursor-state
dependent (S22's cursor sat inside the t423 F7 spin-zone; the D22
witness was captured with the mouse parked elsewhere), or S22's run
never had the pump alive. P4 ("no auto-spin for the newgame field") is
built on S22 and must be treated as SUSPECT until this is resolved.
PLAN (cycle 4, in order): (X1) static: read the state==0xd init branch
0x26e36..0x26f65 for the [esi+0xc0] latch store (S14 debt) + pump body
0x28fc0 delay arg (L3 debt) + per-tick angle delta at the 0x3b pump leg
0x27a18 region; (X2) production frames witness, 60 s, cursor parked
OUTSIDE both fields, single-star arc tracking (per D22-assistant note);
verdict rewrites W1 + the P4 spin clause.

### S26-X1 STATIC (byte-exhaustive, capstone-confirmed)
- Full-obj0 byte scan for ALL base+0xc0 dword stores (c7/89 modrm x6 regs,
  mod=10 disp32 — 0xc0>127 so disp8 form impossible, scan is exhaustive):
  ONLY 0x26c89 ([esi+0xc0]=0, generic init tail) and 0x26dd1 (=1, state==3).
  => state==0xd branch (0x26e36..0x26f65) has NO latch store (S14 debt CLOSED;
  0xd inherits whatever the tail order gives). Capstone linear sweep of
  0x14bb0..0x82bb0 finds only esp+0xc0 stores — consistent.
- NOTE THE RATE MISMATCH: t416 +-2deg/tick at ~1/s pump = 180 s/circuit, NOT
  D22's ~5 s. If D22 is right, the newgame spin is NOT the t416 latch leg —
  it must be the L3 pump family (msg 0x1f6/0x1f7/0x1f9 counters
  +0xb7/+0xb9/+0xbb, fn 0x226e4/0x22ce4), whose RATE (fn 0x28fc0 delay arg)
  is still unread.

### S26-X2a S22 WITNESS RE-READ — THE "AT-REST" VERDICT IS UNSUPPORTED
Re-measured run 215511 frames directly (raw numpy, threshold >30/channel):
 - consecutive 12 s steps: field changed px = 1147/1152/1145/1146/1153,
   control box = 0 EVERY STEP. Vision confirms the frames ARE the New Game
   screen (big field + Begin cluster present).
 - A field with a ~5 s rotation period sampled every 12 s (~2.4 circuits
   between samples) shows EXACTLY this signature: a flat, dt-independent
   changed-pixel floor with nothing repeating. "Flat ~1085 px" is evidence
   of CONTINUOUS MOTION, not of twinkle — a truly static field's diff vs
   f1 would dip whenever a sample landed near a full turn.
 - The centroid-match (tol 6 px) "median 0.0" only proves no star moved
   LESS than ~6 px between 12 s samples; with 5 s circuits stars are at
   unrelated positions every sample (only 34/150 matched at all — the
   expected ~random overlap, not a static field).
 - The t416-vs-D22 rate mismatch (180 s/circuit law vs ~5 s eyeball) was
   the hidden premise that let S22 read the floor as twinkle. The t416
   law governs the state==3 latch leg; the L3 pump family (0x1f6/0x1f7/
   0x1f9, painters 0x52114/0x526b4) is the newgame-field candidate and
   its RATE was NEVER READ (fn 0x28fc0 delay arg outstanding since L3).
VERDICT SO FAR: S22's W1 close is WITHDRAWN (over-claim from an aliasing
measurement); S22's C3 verdicts (production fires, dbg input-deaf) STAND.
D22 (user, vendor game, mouse parked) + this re-read both say the big
newgame field SPINS CONTINUOUSLY. Begin-panel field: D22-assistant
measured it changing with mouse parked (band-gate REFUTED); needs the
same fine-rate treatment.

### S26-X2b D22 REFCAP STAR-ARC MEASUREMENT (vendor game, 1 s cadence)
Bright-peak matching (3x3-max, lum>350, tol 5 content-px) on the 15
vendor refcaps, big field: 23 matched pairs across 14 consecutive 1 s
steps, displacement median 3.16 content-px (p25 1.5, p75 ~3.5; 82% of
matched stars moved >=1.5 px). Twinkle does not translate peaks: the big
field MOVES ~3 content-px/s (= ~3.8 px in 640-space) with the mouse
parked. Consistent with D22 (continuous, mouse-independent). RATE NOTE:
3.8 px/s at r~100 px = ~2.2 deg/s = ~165 s/circuit — matches the t416
+-2deg/tick @ ~1/s pump rate almost EXACTLY, and contradicts the "~5 s
circuit" eyeball. The 5 s figure is NOT supported by the pixel data;
treat the t416 RATE as the leading candidate, D22's 5 s as an eyeball
estimate of "visible motion". (S22's aliasing trap: sampling a 2 deg/s
field every 12 s still shows a flat changed-px floor because the star
set is sparse and repaints reshuffle dim/bright.)

### S26-X2c LAG-CURVE + ROTATION-CORRELATION (vendor refcaps, 15 shots)
- changed-px vs LAG (big field, >30/chan, content px): lag1..9 all
  ~856-889 FLAT, min never below 742; control strip ~15-20. A 5 s
  circuit would dip at lag 5 (874, no dip) => D22's "~5 s circuit" is
  NOT supported by the pixel data [measurement]. Flat-from-lag-1 = the
  field decorrelates within ~1 s (star set sparse: ~880 changed px/s
  over ~150 stars).
- rotation-correlation over the peak clouds (theta -12..+12 deg, tol 4):
  aggregate best -9 deg (score 22) vs theta=0 (17) — WEAK, per-pair
  thetas scatter sign. NOT a rate witness; honest negative on rate.
- matched-star displacement median 3.16 px/s (content) [measurement].
CONCLUSION (S26 verdict): the vendor big newgame field ANIMATES
CONTINUOUSLY with the mouse parked (refcap changed-px 880/s vs control
17/s; S22 production run 1146/step 640-space vs ctrl 0). W1's S22
"does NOT auto-spin" is WITHDRAWN as an over-claim: (a) it was decided
with the cursor parked INSIDE the Begin panel (D22 refutes band-gating
anyway), (b) the centroid tol-6 method cannot see >=6 px steps and the
"flat changed-px floor" is equally the signature of continuous motion —
the discriminator is a lag curve on the VENDOR (done here: no dip), not
a flatness read. RATE remains OPEN (eyeball 5 s vs displacement ~3 px/s
vs t416 2deg/tick@1/s ~ 180 s/circuit — all unreconciled). D22 is the
binding ruling: BOTH fields spin, mouse-independent; the PORT must
re-implement spin and MEASURE the rate on production frames (1 s
cadence x 60 s, star-arc + lag curve), never 12 s sampling.

## S27. CYCLE 4 — L3 RATE DEBT CLOSED (static) + R1 WITNESS RUNNING
### S27-X1 THE "0x28fc0 delay arg" DEBT WAS A MISIDENTIFICATION [verified asm]
S26 carried "read fn 0x28fc0's delay arg" as the outstanding rate leg. The
body (t442_disasm 0x28fc0..0x29090, work/ascend_restored.bin) has NO timer
call and no delay argument — it is the COSMOS DRAW-LIST BUILDER, exactly as
docs/re/ships.md:1181 and docs/re/ui-runtime.md:774 already named it. The
early cycle-1 note ("0x28fc0 = one-shot re-poster") was wrong; the pump is
MSG 0x3b handled at 0x27a18. Cited verbatim:
  28fcd: mov word ptr [eax+0xb7], 0        (clear carousel index)
  2901c: movsx esi, di / imul esi,0x60 / add esi,0x13bc5
  2903a: mov [edx+eax], esi                (store record ptr at cursor)
The leg S26 flagged (0x2900b ebx=0x659 edx=0xff0 call 0x2a428) is an
ASSERT, not a period: 0x2a428 = `test eax,eax; jne ret; push ebx; push edx;
push 0x106a; jmp 0x2a4cc` -> 0x2a4cc pushes 0x6500 (assert-context string
head, 2-byte entries) and calls sprintf 0x76c79 with coswnd.cpp (cstr at
0x83bae) + line 0x106a; failure path ends at int3 0x2a424. ebx=0x659/0x66b
are ASSERT-CONTEXT IDs, edx=0xff0/0x83bae the message. => no cadence info
there; the L3 rate question is answered by the PUMP, below.

### S27-X2 THE RATE CITATION (code law) — 2 DEG PER PUMP TICK AT ~1/s
  dispatcher 0x27a18 (esi=win), gates on byte [win+0xc0]:
    27a1e: test dh,1  -> 27a28: mov dword [esp+0x14],0xfffffffe  (bit1 set)
                        27a32: mov dword [esp+0x14],2            (bit1 clear)
    27a3a: fild [esp+0x14] ; 27a4b: call 0x283e4 (win, edx=-1, f32 angle)
    27a50: test bh,4  -> 27a60/27a6a: +-2 -> call 0x283e4 (edx=0)
  => per-tick delta is the IMMEDIATE 2.0 deg (radians via DAT_00088b88
  pi/180, t416 S / tNGS S11 independent re-derivation). Cadence = msg 0x3b,
  t302 LIVE-measured ~1/s (docs/re/_wip_t416.md:36, t302 stop-names).
  CODE RATE = 2 deg/s = ~180 s/circuit.
  NOTE 0x27a28 sign quirk: bit1 SET gives -2, bit1 CLEAR (bit0 only) gives
  +2 — the latched-pair semantics t416 F2 documented.

### S27-X3 NEWGAME IS THE state==3 BRANCH => LATCH IS SET AT INIT
S14: state==3 (0x26d43) sets rect (17,12,324,320) and 0x26dd1
`mov dword [esi+0xc0], 1` = bit0 latch SET. The C3 vision-confirmed newgame
field box IS (17,12,324,320) (scripts/r_tNGS3c_c3_session.py FIELD_BOX,
run c3-20261122-215511). Combined with S26-X1 (no OTHER latch store
anywhere in obj0), the newgame field opens LATCHED bit0 => the 0x3b pump
applies +2 deg/tick continuously with no input. That is the static half of
the spin law and it agrees with D22 and with the vendor pixel data
(3.16 content-px/s at r~100 => ~1.8 deg/s [S26-X2b]).
=> RATE VERDICT (D22's tie-break rule "code wins"): 2 deg/s about WORLD Y
   (bit0/bit1 = spin pair, FUN_00053584 mixes x,z per t416 F2). The blob
   fit and the code AGREE (~1.8-2.2 deg/s); D22's ~5 s/circuit (= 72 deg/s)
   is NOT supported by code OR pixels and is recorded as an eyeball figure.

### S27-X4 R1 PRODUCTION WITNESS RUN 20261123-010310 (61 grabs @1 s)
Harness: /usr/bin/dosbox-x, scratch game-wp, Xvfb :97, RFB 5911, offsets
80/100. B_click2 FIRED on attempt 1 (orange 0.679 -> 0.006). Cursor parked
(600,250) — OUTSIDE FIELD_BOX(17,12,324,320), BEGIN_BOX(515,380,565,465)
and the menu band. 61 frames saved work/r1/tngs4-20261123-010310/caps/frames/.
MEASURED (median over 60 steps): big field ~950 changed px/step (range
884-995), Begin cluster ~700 (449-755), control strip (500,30,630,80) = 0
EVERY STEP. => BOTH fields ANIMATE CONTINUOUSLY on production with the
mouse parked [measurement]. Matches the vendor refcap signature (856-889
content px/s, ctrl 15-20) and D22's ruling.
HARNESS ROOT CAUSE (3 failed fires before this): my first versions omitted
makedirs(out/save). dosbox autosave=10 then fails writing <savedir>/CMOS
and the GAME shows a MODAL "Failed to save the current state." dialog that
swallows every click (vision on _raw_004: dialog over the menu, New Game
row at y313 image-space). NOT a channel failure. The C3 script pre-created
save/ — that, not the hover rung, is what made C3 fire. Banked as a trap.
OPEN SUB-QUESTION: bright-peak nearest-neighbour match returned n=0 on
every step (threshold lum>350 on 0..765 scale, tol 6 px) — either the
field has no peaks above 350, or the ~950 px/s churn is twinkle-dominated
rather than coherent translation. Offline analysis on the saved frames
(peak census, lag curve, rotation correlation) decides the RATE.

### S27-X5 OFFLINE RATE ANALYSIS (scripts/tNGS4_rate_analyze.py, run 010308)
BIG FIELD (box 17,12,324,320), 61 frames @1 s:
 - bright peaks (3x3-max, lum>120): ~27/frame. Consecutive match at tol 6:
   median n=3 (twinkle turns peaks on/off, so few survive), and the
   SURVIVORS move median 3.58 px/s. At r~100 px that is 2.05 DEG/S —
   INDEPENDENT blob confirmation of the code rate 2 deg/tick @ ~1/s
   (S27-X2) within 3%. Vendor refcap agreed: 3.16 content-px/s = 1.8 deg/s.
   (The in-session run reported n=0 because its threshold was lum>350 on a
   0..765 scale where only 102 px/frame qualify; offline census used 120.)
 - lag curve changed-px: lag1 972, lag2 985, lag3 984, lag4 988, lag5 993,
   lag8 986 — FLAT, no dip at lag 5. Second confirmation (vendor +
   production) that D22's "~5 s circuit" is NOT the period; 5 s would put a
   minimum there. Consistent with a ~180 s circuit sampled at 1 s.
 - rotation-correlation on the 27-peak clouds (theta -14..+14, tol 4, pair
   5 s apart): scores 0-1 at EVERY theta incl. +10 (the 2deg/s prediction).
   HONEST NEGATIVE: the peak set is too sparse + twinkle-scrambled for this
   estimator; the displacement-median is the working statistic. The blob fit
   and the code AGREE on 2 deg/s, so no disagreement to report per D22.
BEGIN CLUSTER (box 515,380,565,465), same run:
 - ~147 peaks/frame (lum>120); consecutive match at tol 3: median 130/145
   matched with displacement median 0.0 px — POSITIONS ARE STATIC.
 - mass (sum lum-60) churns median 944 units/s and ~700 px/step change
   >30/chan, while centroid wanders only 0.7/1.4 px/s. => the Begin field's
   animation is BRIGHTNESS/CLASS CYCLING AT FIXED POSITIONS, exactly the
   tNG-C3 port law ("Positions are STATIC (the rotation drives only the
   class)", title.cpp:1062). D22's "both fields spin" holds for the Begin
   panel as the colour/dark cycle sweeping the cluster, not translation.
RATE VERDICT (all three channels): code 2 deg/s (S27-X2) == production blob
fit 2.05 deg/s == vendor refcap 1.8 deg/s. D22's 5 s/circuit = eyeball,
refuted by TWO independent flat lag curves. PORT RATE = 2 deg/s.

### S27-X6 R3 PORT LANDED (spin restored, pump law, both fields)
rewrite/src/ui/menulaw.h: kPreviewSpinDegPerTick=2.0 (imm at 0x27a32),
kPreviewSpinTickMs=1000 (t302), previewSpinWorldY(x,z,yaw) pure helper;
previewStar takes yawDeg=0.0 default (WORLD-Y, applied to the model point
BEFORE depth band + divide). rewrite/src/ui/title.cpp: ONE accumulator
newgameSpinDeg pumped SDL_GetTicks-driven at the top of the newgame screen
block; big field passes it to previewStar; Begin cluster uses the same
accumulator (radians) for its class term — replacing the per-frame
kPreviewSpinPerFrame fudge AND the S22 hover-only advance. SIGN: the
bit0-only latch (the newgame init value) selects the +2 immediates at
0x27a32 [verified asm]; the screen-side direction of OUR +yaw vs the
vendor's FUN_00053584 mixer (v0'=v0c+v8s, v8'=v8c-v0s at 0x5329a/0x532ab,
on basis slots +0xc/+0x18 = the vectors rotated by the writer) is NOT
pixel-verified — NAMED SEAM: rotation direction unmeasured (a
left-vs-right on-screen check needs a marked-star witness; mutation M4
(sign flip) surviving the suite is the honest state of that seam).
PINS (test_newgame_behavior_tNGB.cpp): tngs_s27_spin_rate_is_two_deg_per_
tick, tngs_s27_spin_is_world_y_and_isometric (y and |p| preserved, 90deg
maps (100,0,0)->(0,0,-100)), tngs_s27_pump_wiring_pin (source-text: pump
advances by the constant, call site passes previewYaw, Begin reads the
same accumulator), tngs_s27_motion_determinism_and_census_pins (same yaw
identical; 2deg tick moves stars; depth changes; never-empty at any yaw).
tngs_p4_no_idle_spin_term rewritten to SUPERSEDED (keeps the zone rects +
purity claim, drops the withdrawn armed-rate CHECK).
MUTATION-VERIFY (measured): M1 rate 2.0->1.0 FAILS rate pin; M2 axis z->y
(roll shape) FAILS 51 pins; M3 call-site detached to 0.0 FAILS wiring pin;
M4 sign flip SURVIVES (direction seam, above). Suite 498/498 green
(494 + 4 new).

### S27-X7 SINGLE-BLOB ARC TRACK (D22's requested fit) — HONEST NEGATIVE
Continuity tracker (seed lum>180 peaks, +-4 px/step, require lum>140 next
frame) on run 010308: 20 seeds, ZERO survived 10 steps — the twinkle
reclass cycles every star's brightness below the floor within a few
seconds (this IS the class-cycling the pump drives). The matched-pair
displacement median (S27-X5, 3.58 px/s) is therefore the working rate
statistic; per-star signed arcs (=> rotation DIRECTION) are not recoverable
from 1 s pixel data on this field. Direction stays a named seam (checklist
item 5).

### S27-X8 W1 STATUS: CLOSED-BY-USER-REFCAP (per D22 steering rule 3)
W1 (does the newgame field auto-spin?) = YES, CONTINUOUSLY, mouse-
independent. Evidence: (a) user refcaps scratchpad/Screenshot_2026-11-
22_23-03-55..23-04-10.png (15 shots ~1 s apart, mouse parked) — matched
bright stars median 3.16 content-px/s [S26-X2b]; (b) production witness
work/r1/tngs4-20261123-010308 (61 frames @1 s, cursor (600,250)) — big
field ~950 changed px/step ctrl 0, matched stars 3.58 px/s [S27-X4/X5];
(c) static law: state==3 latch store 0x26dd1 + pump imm 2 @0x27a28..32
[S27-X2/X3]. Rate = 2 deg/s (code wins per D22; blob fit agrees). PORTED
(S27-X6) with pins; direction = named seam (S27-X7).

## S28. CYCLE 5 — tNG-R PUMP CADENCE (assigned; user stopwatch 5.3 s vs shipped 180 s)
### S28-X0 STATIC CADENCE CHAIN (pre-session, base-0 work/ascend_restored.bin, revenv capstone)
- NO immediate msg-0x3b poster: d32 `mov edx,0x3b` = 0 hits; push 0x3b = 0 hits.
  The pump msg id is NOT hardcoded at the dispatch call — it flows through the
  window SCHEDULER queue. Chain (verified asm this session):
  POSTER 0x26c66 (loop tail of the 0x26b34-region fn; 0x26bcf `cmp ebx,7;
  jge 0x26c66`): `push 0; mov ebx,0x3b; mov eax,0x7a35c; mov ebp,0x168;
  mov edx,[esi+0x41]; push 0; xor ecx,ecx; xor edi,edi; call 0x56374`.
  SCHEDULER 0x56374: scans 17 slots stride 0x16 at [win+0x44ae]; free slot gets
  msg word at +0x44b2 (=bx low word), param1 +0x44ae, +0x44b4, +0x44b8, and
  FIRE-TIME dword +0x44c0 = [DAT_000a2044] + ebp (0x563f4..0x56401). => msg 0x3b
  is a SELF-REPOSTING DELAYED message: delay = 0x168 = 360 units of whatever
  clock DAT_000a2044 counts (unit UNKNOWN statically — ms? ticks? that IS the
  open leg). This is the cadence chain S26 said was broken: it exists, but its
  period is a data value whose clock unit is not statically decidable here.
- Corollary (t302 ~1/s figure): consistent with delay 360 @ ~1 kHz clock, but
  a frame-loop clock (60 Hz) would give 6 s, and 36 Hz ~10 s. NOT decidable.
- Latch/pump/applier re-verified verbatim (S27-X2 stands): 0x27a18 gates on
  [esi+0xc0] bit0, delta imm ±2, call 0x283e4; 0x283e4 fmuls [0x9f108]
  (pi/180) and rotates the basis at win+0x14e via 0x53584 (edx=-1) — 0x53584
  rotates [eax+0xc] and [eax+0x18] = win+0x15a/+0x166 (up,fwd per 0x26a9c init:
  eye@+0x10e=(0,0,-1500), A@+0x14e=(1,0,0), up@+0x15a=(0,1,0), fwd@+0x166=(0,0,1)).
  => LIVE INTEGRATION WITNESS AVAILABLE: dump win+0x14e..0x180 per pump fire;
  accumulated rotation / accumulated guest-run time = the rate law, aliasing-
  free (this closes S27-X7's twinkle-negative by a different channel).
- S28-X0b CLOCK TICKER: DAT_000a2044 has exactly ONE increment site, fn 0x53d84
  (`inc dword [0xa2044]; ret`). The dword at file 0x8b35c == 0x53d84 sits in an
  EDGE-STEPPING table (0x735f3 raster loop indexes [ebp*4+0x8b350] as a y-step
  LUT) — a numeric coincidence, NOT a callback registration. No static
  reference to 0x53d84 as a handler exists => the tick source is installed at
  runtime (DPMI/IRQ/timer hook). Cadence unit is NOT statically decidable;
  Phase D measures units/s live.
### S28-X1 PASS 1 RESULT (run dbg-tngr-20261123-102741, rc=0) — PUMP LEG COLD AT NEWGAME
- BREAK lottery won (relaunch attempt 1); leg w1_pump 0x27A18 armed BPLIST
  '00. BP 0160:1E6E68' (= P0+0x27a18 exact); New Game click fired
  (after_ng_orange 0.006, vision-confirmed NEWGAME screen 04_after_ng_click.png);
  cursor parked (600,250). 30 s armed window, 12-stop budget: ZERO FIRES.
- READ: the msg-0x3b pump leg (the 2-deg applier) DOES NOT RUN at the newgame
  screen. The frame-loop hypothesis for a 5.3 s spin (2 deg/tick @ ~36 Hz) is
  REFUTED at this leg. Two survivors: (a) msg 0x3b never posts to the newgame
  window (spin law = campaign-map only; the field's visible churn is the
  CLASS-CYCLING law — D23's own alternative); (b) a gate between handler entry
  and the leg. DISCRIMINATOR (pass 2): arm cos_hdlr ENTRY 0x26b34 too; bank
  msg=[esp+0x38] (t425 law) + esi per stop. If 0x3b reaches the entry but not
  the leg -> gate; if no 0x3b ever -> no pump scheduled here, period.
- Cross-check banked: t302/t305/t318 census measured msg-0x3b ~1/s ON THE
  CAMPAIGN MAP (cos_hdlr/s2_56cda legs). The S27-X2 chain silently TRANSFERRED
  that cadence to newgame — the transfer is now measured FALSE at the leg.
- Note: S27-X4's ~950 changed-px/step at newgame STANDS (field animates) but
  its spin INTERPRETATION is now contested by X1. S22's tol-6 centroid said
  positions STATIC; both pixel channels + this leg agree on NO POSITION SPIN.
### S28-X2 PASS 2 RESULT (run dbg-tngr-20261123-103130, rc=0, attempt 4) — USER VINDICATED
- Pump leg 0x27a18 FIRES at newgame: 12 stops, win=0xfd2310, latch=1 (bit0)
  every fire. (Pass-1 zero-fires = artifact: leg armed but BREAK cadence lost
  it; the cos_hdlr entry leg never armed that run — lesson: verify BPLIST
  shows BOTH legs before trusting a zero.)
- BASIS INTEGRATION (aliasing-free): camera fwd azimuth at win+0x166 sampled
  stopped->RUN->stopped, 5 windows T=2.25/2.25/2.25/5.25/10.25 s wall:
  az (-147.3->-43.3->88.7->-143.3->154.7->76.7). fwd.y CONSTANT 0.3796 across
  all samples => pure world-Y rotation, no tilt. Wrap-consistent deltas
  (+104,+132,+128,+298,+282) => 46-66 deg/s (dump-overhead 0-0.5 s family);
  ALL rotation happens while RUNNING (gap deltas exactly 0.0 — the dump
  quiescence law self-proved).
- FIT: 59-65 deg/s == user stopwatch 360/5.3 = 67.9 deg/s. The shipped
  2 deg/s (180 s/circuit) is REFUTED by ~30x. Frame-loop-shaped: 2 deg/tick
  at ~30 Hz (cadence = msg-0x3b repost delay 360 units on a ~10.8 kHz clock).
- SIGN: azimuth increases while latch=1 (init-only, mouse parked) => +2 deg
  world-Y is the NEWGAME direction => DIRECTION SEAM (checklist #5) CLOSED for
  newgame at the basis level (azimuth = atan2(fwd.x, fwd.z), stored law).
- HIT-COUNT CAVEAT banked: banked inter-fire gaps 2.45 s = debugger poll
  overhead lower-bound, NOT cadence (30 s window / 12-stop budget). Do not
  cite hit-count at a hot leg as cadence on this instrument.
- CLOCK SAMPLE DEFECT: dump_mem tag 'clk' reused -> same file overwritten;
  only last sample survived (=0x0) => units/s unmeasured in this run. Pass 3
  = dedicated ticker census: leg 0x53D84 (`inc dword [0xa2044]; ret`, the ONLY
  incrementer), count stops over wall T + unique-tag clock samples + 17-slot
  scheduler scan (stride 0x16, msg word +4, fire_at +0x12) for the pending
  0x3b slot. cadence = units/s / 360 decides 30 vs 36 Hz exactly.
### S28-X3 CADENCE VERDICT (from S28-X2 data; basis = exact fire counter)
Each pump fire rotates EXACTLY +2 deg (imm 2 @0x27a32, applier verified), so
the azimuth integral IS a hit-count log: fires = dtheta/2.
  T=2.25 s windows: +104,+132,+128 (k=0) -> 23-33 fires/s
  T=5.25 s window: -62+360=+298 (k=1) -> 28.4 fires/s
  T=10.25 s window: -78+720=+642 (k=2) -> 31.3 fires/s
Constant-rate fit UNIQUELY selects k=0/1/2 (k=1 at 2.25 s => 207 deg/s would
require wrapped +7 at 5.25 s, observed -62 — excluded). CADENCE ~30 +/-4
fires/s => RATE 60-66 deg/s => CIRCUIT 5.5-6.0 s.
USER STOPWITNESS CONFIRMED (5.3 s = 67.9 deg/s). SHIPPED 2 deg/s (180 s)
REFUTED by ~30x. tNGS4 blob fit (S27-X5 "3.58 px/s = 2.05 deg/s") ALSO
REFUTED: tol-6 centroid matcher at 1 s cadence against ~100 px steps can only
match twinkle coincidences — the exact trap REFUTED-ROUTES ln1607 names.
t302 "~1/s" RE-READ: the census banked at most 6 stops/window and the pty
count tracked our ~1 s poll loop => it measured POLL RATE, never cadence; the
transfer of that figure to the spin law was the root error.
CLOCK LEG FAILED (honest): units/s unmeasured — dump_mem tag collision
overwrote every sample (filename = tag+addr; constant tag 'clk'), and the
final surviving sample read 0x0 (mapping of DAT_000a2044 unverified). Cadence
cited from the basis counter instead. Scheduler slot layout guess was garbage
(msg 0x600) — layout stays unverified; do not cite slot offsets.
DIRECTION: azimuth atan2(fwd.x, fwd.z) INCREASES with latch=1 bit0, mouse
parked => +2 deg world-Y is the newgame direction. Checklist #5 CLOSED at the
basis level (newgame only; map dial directions unchanged, t416 F2).
### S28-X4 FIX LANDED (rate + sign; suite 498/498)
- menulaw.h kPreviewSpinTickMs 1000 -> 32 (band 28-33 fires/s cited; circuit
  law pin 5.4-6.3 s added; kPreviewSpinDegPerTick 2.0 unchanged); comments
  rewritten to cite dbg-tngr-20261123-103130 and to name the two refuted
  channels (poll-limited map census; 1 s blob matcher).
- title.cpp previewYaw = -newgameSpinDeg AND beginYaw negated (camera-basis
  +2/fire => apparent star/class drift -2/fire; checklist #5 CLOSED newgame).
- Suite 498/498. MUTATION CHECK PARTIAL (budget): circuit-band pin kills any
  slow-cadence mutation by construction; the SIGN negation is NOT
  mutation-verified this iteration (pixel channel needed) — named residue.

## S29. CYCLE 5 RE-PACKAGE — SIGN AUDIT FINDING FIRST (2026-11-23, steering D24)
### S29-X1 THE SHIPPED WIRING VIOLATES THE D24 USER LAW (double negation)
D24's assistant check computed the menulaw FORMULA at raw +2 deg (near z=-400
sx 200->190.24 LEFT) and declared the seam closed. But title.cpp:558 passes
previewYaw = -newgameSpinDeg (the S28-X3 negation), so the COMPOSED shipped
behaviour was never checked. Composition audit this session (/tmp/
s29_sign_check.cpp, g++ -I rewrite/src, run rc=0):
  formula +2deg:   near sx 200->190 LEFT ; far 200->206 RIGHT   (== D24 law)
  shipped (yaw=-spin): near sx 200->210->219->229->239->248 RIGHT every tick;
                       far LEFT every tick.  == LAW INVERTED in both fields
  (beginYaw at title.cpp:1115 carries the same negation).
READ-BACK: the S28-X3 sign argument (camera basis +2/fire => apparent stars
-2/fire => negate the star-model term) double-counted the inversion: the
vendor's apparent-star result IS what raw +2 deg on the star model produces
(measured azimuth increase + user near-left law are the SAME fact about one
rotation; converting camera->star terms is the one inversion, not two).
The pre-S28 code (no negation) was direction-CORRECT; S28 broke it while
fixing cadence. Cadence (tick 32 ms) is untouched by this.
FIX: remove BOTH negations (previewYaw = newgameSpinDeg; beginYaw =
+spin*rad), then add the steering-requested unit pin (near-side star sx
strictly decreases per +kPreviewSpinDegPerTick shipped tick) + a source-text
pin that title.cpp passes the accumulator UNNEGATED. Mutation-verify by
re-negating and confirming the pins FAIL.
### S29-X2 FIX + PINS + MUTATION-VERIFY (suite 500/500)
- title.cpp:558 previewYaw = newgameSpinDeg (negation REMOVED); title.cpp
  beginYaw likewise un-negated (same double-inversion). Cadence constants
  untouched (tick 32 ms, 2 deg/tick).
- NEW PINS (test_newgame_behavior_tNGB.cpp):
  tngs_s29_near_star_moves_left_per_tick — composes the shipped accumulator
  exactly; near on-axis star (z=-400) sx STRICTLY decreases and far star
  strictly increases per +2 deg tick, 35 ticks (0..70 deg window; the
  monotone window is measured, /tmp/s29 sweep: strict through 72 deg, flat
  px quantisation past ~73 deg near the camera plane — window pinned, not
  hand-waved).
  tngs_s29_title_wiring_is_unnegated — source-text pin:
  "const double previewYaw = newgameSpinDeg;" present AND "-newgameSpinDeg"
  absent anywhere in title.cpp (S28-X3 defect shape killed at the text level;
  closes the S28-X4 sign-mutation residue).
- MUTATION-VERIFY (S28-X4 residue CLOSED):
  M1 previewSpinWorldY R(-t) (true inverse rotation): FAILS 71 tests incl.
  both direction claims (tngs_s29 ln399, tngs_s27 isometry ln427) — DEAD.
  M2 previewYaw re-negated in title.cpp: FAILS the wiring pin (ln416) — DEAD.
  Both reverted; suite re-run 500/500 (498 + 2 new).
- PIXEL WITNESS post-fix (scripts/tNGS4_ours_shot.sh run 12:16): 1095
  changed px total / 774 in-well over 4 s ctrl 0 = animates at tick 32.
- PACKAGE NG5: scratchpad/NG-checklist.txt rewritten (cycle 5: owns the
  30x mis-ship as poll-rate transfer, CONFIRMS the 5.3 s stopwatch with the
  dbg-tngr-20261123-103130 + basis-integration witnesses, states the CLOSED
  direction item honestly incl. the caught-in-time inversion, renumbers open
  items 5-7 = hover-adder / right-edge chrome / Begin-cluster sprites);
  tNGU_composite.py ng_t0.png + newgame-original.png ->
  scratchpad/NG-usergrade.png 1290x1782, 18/18 PASS, t441 rc=0.
  (scratchpad/ is gitignored — package artifacts live on disk, not in git.)
### S29 VERDICT
Cadence law SHIPPED and pinned; direction law SHIPPED UN-NEGATED, pinned
behaviourally + at source text, and mutation-proof; S28-X4 residue closed;
NG5 packaged. No OQ row touched (tNG-S tracks none — honest negative).
NEXT = WAIT-USER-GRADE-NG5.
