# _wip_t428e.md — PLANET-SCREEN CYCLE 5 (K5 WIDGET HUNT + BLIT-2 PORT DECISION)

Assignment: docs/STATE.md NEXT ACTION t428e. Ordering rationale: t428d closed
the paint-body head completely (docs/re/_wip_t428d.md F1-F4) — blit-1 = 17np
k4@(7,115) PORTED; blit-2 = lib WORD[widget+0x175+2*WORD[planet+0x16]], record
= SIZE CLASS, at (408,296), gate BYTE[widget+0x18b]&4; blit-3 = 17np k1@(0,0)
unported (no witness). Record 5 is NOT reachable from the head, yet 17np
record 5 (416x316) registers in witness B at screen (224,107) (z=18.6, 14.6%
coverage — t428c). Seam T428c-A = k5 widget identity.

Sub-tasks: (a) find the code site that can blit k5 (variable selector, other
lib, or other paint body); (b) only if (a) resolves, decide the blit-2 port
(census rect (408,296) first); (c) tile-click popup law only if (a)+(b) land.

## E0 — BLIT-SITE INVENTORY (all 0x1fc34 callers in the banked listings)
[run: grep -n 0x1fc34 work/*.asm; listings parsed with python (addr->text map)]
t198_planwin.asm (4128 insns, 0x3aa0a..0x3e33d) — 16 sites:
  0x3b9d5 0x3ba17 0x3ba40 0x3bf21 0x3c1a0 0x3c446 0x3c6fd 0x3c7a9
  0x3c81f 0x3cd20 0x3cdb4 0x3ce1e 0x3cecc 0x3d0d7 0x3d114 0x3dbc5
t200_coswnd2.asm (1061 insns, 0x2976c..0x2a491) — 1 site: 0x2a214
  (selector WORD ds:0x6fd96 — a DIFFERENT global slot, not 44; cos-window).
Every t198 site loads `mov $0x9f10c,%eax` (the shape-lib array base) before
the call; the lib word is read into %dx from either a stack slot or a global.

## E1 — K5 BLIT SITE FOUND: 0x3c81f, 17np RECORD 5 IMMEDIATE, INSIDE THE
## SAME PAINT BODY (t428e) [VERIFIED asm 0x3c7bc..0x3c832]

This answers task (a) directly: the site that CAN blit record 5 is not another
lib and not another paint body — it is a FOURTH blit in work/t198_planwin.asm,
downstream of the paint-body head, with the record as an IMMEDIATE.

  3c7bc  mov    $0x1f06,%edx            ; widget id / name key
  3c7c1  mov    $0x7a35c,%eax           ; game object
  3c7c6  xor    %ebx,%ebx
  3c7c8  call   0x56d1c                 ; widget lookup (same winmgr fn as
                                        ; 0x55ffb MOV EDX,0x85975 "ABILITYWIN")
  3c7cd  cmpl   $0xffffffff,0x35(%eax)  ; GATE: widget field +0x35 == -1 ?
  3c7d1  jne    0x3c835                 ;   no -> skip the k5 blit entirely
  3c7d3  mov    $0x484f8,%ebx           ; gsystem obj (t344 banked)
  3c7d8  mov    $0x70,%ecx              ; 112
  3c7dd  mov    $0x210,%edi             ; 528
  3c7e2  push   $0x0                    ; arg5 = y = 0
  3c7e4  mov    $0x1ac,%eax             ; 428 (stored esp+0x300, then OVERWRITTEN)
  3c7e9  xor    %edx,%edx
  3c7eb  push   $0x0                    ; arg4 = x = 0
  3c7ed  mov    0x378(%esp),%dx         ; 2 pushes pending (8B): esp0-8+0x378
                                        ;   = esp0+0x370 = WORD[0x6fd9c] = 44 = 17np
  3c7f5  mov    %ebx,0x2f0(%esp)        ; 0x484f8
  3c7fc  mov    %ecx,0x2f4(%esp)        ; 112
  3c803  mov    %ecx,0x2f8(%esp)        ; 112   <- struct passed to the blit fn
  3c80a  mov    %eax,0x300(%esp)        ; 428
  3c811  push   $0x5                    ; arg3 = RECORD 5   <-- k5!
  3c813  mov    $0x9f10c,%eax
  3c818  mov    %edi,0x300(%esp)        ; 528 overwrites the 428
  3c81f  call   0x1fc34                 ; shape fetch (lib 44, record 5, x=0,y=0)
  3c824  push   %eax                    ; handle
  3c825  lea    0x2f8(%esp),%eax
  3c82c  push   %eax                    ; &{112, ?, 528}
  3c82d  call   0x5caac                 ; BLIT fn (t344 banked as the blit fn)
  3c832  add    $0x14,%esp

STACK LAW CHECK (same arithmetic that fixed t428d F4): with exactly 2 pushes
pending at 0x3c7ed, `mov 0x378(%esp),%dx` = esp0+0x370 — the EXACT slot banked
at 0x3b996 (WORD[0x6fd9c] = 44 = 17np). Consistency PASSES: the lib word is the
same constant-44 slot blit-1 and blit-3 use.

CONSEQUENCES:
 - k5's selector is NOT the widget+0x175 table (blit-2's law) and NOT the size
   class. It is a constant record 5 behind a RUNTIME WIDGET-STATE GATE:
   paint k5 only when the widget found by 0x56d1c(0x7a35c, 0x1f06) has
   field +0x35 == -1.
 - The blit-1/2/3 head law from t428d is UNCHANGED (this is a fourth blit,
   later in the body). t428d's "k5 unreachable" statement is scoped to the
   HEAD only — corrected here.
 - Destination: the shape fetch uses x=0,y=0 but the actual blit goes through
   0x5caac with a rect struct {0x2f8=112, 0x300=528}. Whether the effective
   screen position is (0,0), (112,?) or derived from that rect is the next
   question (t428c MEASURED k5 registering at screen (224,107) — a third
   candidate, so the rect law must be resolved before porting).

OPEN (narrowed): (i) fn 0x5caac's rect semantics (does (0,0)+rect compose?);
(ii) widget 0x1f06 identity + what field +0x35==-1 means in game terms;
(iii) whether witness B satisfies the gate (if +0x35 != -1 on B, the 14.6%
peak is a false positive and k5 is simply NOT PAINTED on B — the honest
reading would then be "k5 is gated off on witness B", not "k5 is at (224,107)").

## E2 — CONTROL FLOW INTO THE k5 BLIT: LOOP EXIT, NOT A BRANCH AWAY (E1 gate
## is the ONLY real condition) (t428e) [VERIFIED control flow]

The only edge to 0x3c7bc in the whole listing is `jle 0x3c7bc` at 0x3c4ed,
which is the NORMAL EXIT of the lattice row loop: 0x3c4ca `inc %ecx` (row
counter at esp+0x330), 0x3c4e7 `mov 0x1a(%eax),%dx` (bound = WORD[planet+0x1a]
— a NEW planet-record field, distinct from +0x14 size / +0x16 type), 0x3c4eb
cmp, exit when counter > bound. No `ret` exists anywhere between 0x3ba5e and
0x3c83e (measured: grep of the parsed listing), so any paint path that reaches
the head necessarily falls through the loop tail into 0x3c7bc.
=> THE k5 BLIT RUNS ON EVERY PAINT UNLESS THE WIDGET GATE FAILS:
   0x56d1c(game obj 0x7a35c, key 0x1f06, ebx=0) -> result, gate
   DWORD[result+0x35] == -1.  (0x56d1c = the winmgr widget-lookup fn — same fn
   the winmgr wiring uses with EDX="ABILITYWIN" (docs/STATE.md:1230).)
Other notes from the tail walk: 0x3c47e adds 0x46 (=70) to the size-class slot
esp+0x348 AFTER blit-2 has consumed it (no effect on blit-2); 0x3c486 remaps
size-class remainder 4 to 0x77 (=119) in the same slot for downstream text
calls; the blit-2/3 rect/clip args flow through 0x5d5a1 (0x4850c = the
t344-banked draw-context obj).

## E3 — WIDGET 0x1f06 IS "PLANLIST" (t428e) [MEASURED, pool-relative law]

The t344 amendment law (docs/REFUTED-ROUTES.md:1250-1256): widget/window
lookup immediates are POOL-RELATIVE, real string offset = imm + 0x82bb0
(verified there for MOUSE.SHP: 0x84314 - 0x82bb0 = 0x1764). Applying it:
  0x1f06 + 0x82bb0 = 0x84ab6 -> work/ascend_restored.bin 0x84ab6 ==
  b'PLANLIST\x00..\\planwin.cpp\x00' [MEASURED this iteration]
Control: 0x85975 ("ABILITYWIN", the STATE.md:1230 winmgr wiring) reads as
b'ABILITYWIN\x00HELPWINDOW\x00' [MEASURED] — same string pool, so the law
holds for this call family too. The adjacent source-path string
`..\planwin.cpp` is the widget's own debug path: the PLANLIST widget is
declared in the PLANET-window source file, i.e. it is a CHILD of the planet
screen — exactly the state-17 screen we are painting.

=> THE k5 GATE, IN GAME TERMS: the planet window paints 17np record 5 as its
   backdrop only when the PLANLIST widget's field +0x35 == -1.
   [inferred] +0x35 = the widget's selection/scroll state, -1 = "no planet
   selected in the list" (unverified — no RAM measurement of +0x35 yet).

CLIP-STRUCT ARITHMETIC [verified asm 0x3c7d3..0x3c818]: ecx=0x70 (112) stored
at esp+0x2f4 AND esp+0x2f8; edi=0x210 (528) stored at esp+0x300 (overwriting
the 0x1ac=428 written 8 bytes earlier). The pointer handed to the blit fn is
`lea 0x2f8(%esp)` = {112, <esp+0x2fc>, 528}. NOTE: 528 - 112 = 416 = EXACTLY
k5's WIDTH (t428c: k5 = 416x316) — the rect spans precisely one k5 width,
consistent with a clip rect [x0=112, x1=528] rather than an arbitrary box.
The (0,0) pushes belong to the 0x1fc34 SHAPE-FETCH (record selector + lib),
NOT to the blit — the blit at 0x3c82d passes only (handle, &rect) explicitly;
its screen x/y come from the pre-existing stack slots this body uses for the
other blits (0x5caac is a 5-arg fn, ADD ESP,0x14 — shp.md S12.1).

## E4 — CANDIDATE-ORIGIN MEASUREMENT: k5 DOES NOT REGISTER AT ANY
## CLIP-DERIVED ORIGIN IN WITNESS B (t428e) [MEASURED,
## scripts/t428e_k5_origin.py, run on work/r1/screens/t254/02_planet_detail.png]

17np record 5 (416x316, 10748 lit px) placed at named origins (png = screen +
(80,100)), tol-8 colour match:

  clipx0+PLANLIST (112,120)    56  ( 0.52%)   <- the clip-rect prediction
  PLANLIST rect   (120,120)    43  ( 0.40%)
  blit-2          (408,296)    28  ( 0.26%)   onscreen 4059/10748
  origin          (0,0)       436  ( 4.06%)
  field blit-1    (7,115)      46  ( 0.43%)
  t428c peak      (224,107)  1566  (14.57%)   colour-permute control 340-388

READ: the peak is REAL (1566 vs permute baseline ~360 = 4.4x; the pairing is
not colour-noise) but NONE of the origins derivable from the static windows.txt
rects or from the clip struct explains it. So either (i) the PLANLIST widget's
RUNTIME rect differs from its windows.txt X0/Y0 (120,120) — the widget is
created/moved by code, not by the table — or (ii) fn 0x5caac composes the
screen position from stale stack slots (it is a 5-arg fn and this call site
pushes only 2 args: handle + &rect, so args 3..5 are leftovers from earlier
calls in the same body — consistent with shp.md S12.1's desc-derived x/y).
Both readings keep k5's position OPEN; neither supports (408,296), (112,120)
or (0,0). Ghidra headless was DOWN this iteration (server_status:
connected=false on 13100), so 0x5caac's arg law could not be decompiled here —
that is the single missing input.

NOTE 224 = 2 x 112 (the clip x0) — suggestive of a doubled/scaled coordinate
in the leftover-slot path, but UNVERIFIED; do not port on it.

OVERLAP CENSUS at the (224,107) placement (windows.txt PLSQUARE rect
152,120..487,375 — ln1519-1528): INSIDE PLSQUARE 0/2048 matched (0.0%),
OUTSIDE 1566/8700 (18.0%), outside mismatches 2747 bright / 4387 dark. The
interior is fully suppressed (PLSQUARE art covers it [inferred]) — consistent
with k5 being a BACKDROP behind the children, and again inconsistent with any
origin that would put k5's speckle inside the panel.

## E5 — BLIT-2 CENSUS AT (408,296): NOTHING REGISTERS — BLIT-2 STAYS
## UNPORTED (t428e) [MEASURED]

Task (b) census: each 17np size-class record placed at screen (408,296)
(png 488,396), tol-8: rec0 62/49558 (0.1%), rec1 0/41, rec2 0/30, rec3 0/44,
rec4 1/269 (0.4%). The rect on witness B is 71% pure black (45360/63648 px
RGB(0,0,0) in the crop) — the field backdrop zone, no distinct sprite. Per the
assignment rule ("if it is the pop-grid/lattice overpaint zone with no
distinct sprite, blit-2 is inert and stays unported"): VERDICT = unported,
law banked only (t428d F4). Note the gate BYTE[widget+0x18b]&4 is runtime
state anyway (widget = the painted planet window), so even a positive census
could not pin a table entry from windows.txt.

## E6 — THE 0x5caac ARG LAW + STALE-ARG FACT AT THE k5 SITE (t428e)
## [VERIFIED from banked decompile work/combat_decomp/5caac.c + push walk]

0x5caac is cdecl 5-arg (shp.md S12.1 arg map, confirmed against the decompile
on disk work/combat_decomp/5caac.c): p1 = shape struct ptr ({hdr, clip...} =
widget+4 copy), p2 = payload base, p3 = selector u32, p4 = screen x, p5 =
screen y. Position composition [verified decompile :58-64]:
    x := p4 + struct[+4]   (iVar10 = param_1[1])
    y := p5 + struct[+8]   (iVar11 = param_1[2])
    then x := *(p2+0x10) + x,  y := *(p2+0x14) + y   (:63-64)
i.e. THE PAINT ORIGIN IS ALSO OFFSET BY THE PAYLOAD-SLOT RECT FIELDS — which
shp.md S12.2 measured to be RUNTIME bookkeeping (slot+0x88 holds the verbatim
file copy; the slot HEAD holds non-file content), NOT derivable from the
extracted .shp file.

AT THE k5 SITE (0x3c824..0x3c82d) only TWO args are pushed: p1 = &struct
(stores 0x2f0/0x2f4/0x2f8/0x300 written around 0x3c7f5..0x3c818 — NOTE the
pending-esp shifts between those stores and the `lea 0x2f8(%esp)` at 0x3c825
(a push $5 at 0x3c811 and the fc34 call+return sit between them), so the
EXACT frame slot the struct starts at is ambiguous without full
control-flow-accurate accounting: the straight-line pending walk says 64/72
bytes at the two calls but it over-counts un-taken loop branches), p2 = the
0x1fc34 handle. p3/p4/p5 (selector, x, y) are NEVER PUSHED at this site —
they are frame leftovers written earlier in the body (loop-internal calls).
=> k5's effective origin = p4_stale + struct[+4] + slotrect.x, and the y twin.
   Three of those five inputs are runtime/stale state. Measured placements:
   (112,528)=0 hits, (112,112)=56, (0,0)=436, (224,107)=1566 — the peak is
   consistent with SOME stale+cache combination but NO statically-derivable
   one.
 - CONCLUSION: the k5 paint POSITION cannot be pinned statically (two stale
   frame words + the runtime payload-slot rect). Pinning needs a runtime
   witness of the frame/payload slot (capture class, cf. OQ-019) or a second
   witness at a different planet where the peak MOVES predictably. Seam
   T428c-A stays open, narrowed to "k5 blit ORIGIN OPEN" (widget identity
   CLOSED E3+E7; gate + record law CLOSED E1/E2).

## E7 — POOL-BASE CONTROL FOR WIDGET-NAME IMMEDIATES (t428e) [MEASURED]

Banked bank says "RESWIN"@0x2c0c (docs/re/_wip_t323.md). 0x2c0c in the
restored image is NOT the string (it's data/code bytes) [measured]; RESWIN is
at 0x857bc, and 0x2c0c + 0x82bb0 = 0x857bc EXACTLY. So the pool-relative law
(imm + 0x82bb0) holds for fn 0x56d1c widget-name immediates as well as for
shape refs (t344) — E3's PLANLIST reading stands on this control, not just on
the single PLANLIST hit.

## LEDGER (t428e)
Closes NOTHING in docs/OPEN-QUESTIONS.md (strict-close honest negative —
planet-screen visuals have no OQ owner; t414..t428d precedent; OQ-016/019/027
untouched). Seam progress (docs/re seams, not ledger rows): T428c-A k5 widget
IDENTITY CLOSED (E3+E7: PLANLIST, gate +0x35==-1, E1/E2 law); k5 ORIGIN still
OPEN (stale-arg law E6); T428-B unchanged. Blit-2 census NEGATIVE -> unported
(E5). No port change this iteration (the k5 origin is unpinnable; shipping
(224,107) would be exactly the "plausible default" strict-close forbids).
