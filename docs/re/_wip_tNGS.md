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
