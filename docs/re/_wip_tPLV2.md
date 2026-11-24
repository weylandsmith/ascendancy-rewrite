# tPL-V2 — ORBITAL SLOTS LEFT (D26) — WIP

Task: D26 demands 10 orbital squares LEFT of the planet, five rows of 2,
NOT isometric, hover shows a thin greyish box OUTLINE. t428 identified
"orbital column LEFT" with the PLRES strip window twice; STATE.md tPL-V2
says resolve that identity properly first.

## Probes (session 2026-11-24 ~00:45)

P1 windows.txt (extracted/ascend00/windows.txt, CRLF):
 - PLANETALLOC @1486; children: PLANLIST @1503, PLSQUARE @1519
   (X0 152 Y0 120 X1 487 Y1 375, STATE 1 17, SENDMESSAGE 1),
   PLRES @1536 TYPE 29 rect 7,7..114,106 SENDMESSAGE 50 PARAM1 0
   HELPINDEX plres SHAPEFRAME -1; PLIND 123..230 (P1=1), PLPRO 239..346
   (P1=2), PLPOP 355..454 (P1=4), PLBUILD 463,8..632,106 SENDMESSAGE 51.
   PLSQBUT0..5 children of PLSQUARE TYPE 0.
 - NO window named anything orbital-ish anywhere in the 100-name census
   (grep ^NAME full dump). So the 10 orbital squares are NOT a
   windows.txt window -> they are code-painted (paint body 0x3b96c or a
   sub-painter) and hit-tested by hand, like the surface lattice.
 - NOTE the PLRES rect is 107x99 — a 2-col x 5-row grid of ~19px squares
   does NOT fit 10 squares of visible "thin greyish box" size at the
   strip scale the user described ("to the LEFT of the planet", i.e. in
   the FIELD, west of the sphere). t428's PLRES identity was about the
   strip star-disc art gap — a DIFFERENT defect (tPL-B1c strip painter,
   already shipped). The D26 orbital-squares defect is the FIELD one.

P2 port state: rewrite/src/ui/planetview.h:142/159 (orbital ring NOT
   adjacency-linked; items 22..30 need the ring), ui.cpp:2139 skips
   orbital ring tiles in the surface painter. sysview.h:43-50 orbital
   grid CODE-DRAWN, "PORT LAW — no vendor per-planet position datum".

NEXT: find the vendor field painter's orbital-slot loop in
work/t198_planwin.asm / Ghidra 0x3b96c body: candidate signature = a
5-iteration (or 10) loop left of the sphere drawing slot frames; hover
outline handler = mousemove path painting a 1-px rect frame grey.

## F1 — ORBITAL SLOT LAW DERIVED (tPL-V2, Ghidra FUN_0003b96c second loop)

FUN_0003b96c (planet-screen paint body, imagebase-0 payload addr) has TWO
loops. Loop 1 (0x3bb2c..0x3c26d) = the SURFACE lattice (tPL-V1 law,
centre = 410+34*(col-row), 110+17*(col+row) paint origin). Loop 2
(0x3c33a..0x3c4d9) = THE ORBITAL SLOT LOOP. Raw disasm
(work/ascend_restored.bin, objdump -b binary -mi386 -Maddr32,reg32):

  3c33a: mov $0xd,%edx        ; X0 = 13
  3c33f: mov $0x77,%ebx       ; Y0 = 119
  3c34b: mov %edx,0x324(%esp) ; slot-X accumulator
  3c355: mov %ebx,0x348(%esp) ; slot-Y accumulator
  3c38e: mov 0x18(%eax),%ax   ; ax = planet[+0x18]  (surface cell count)
  3c39c: mov %eax,0x330(%esp) ; idx = surface count  <- START INDEX
  3c3a3: shl $0x2,%eax        ; cell stride 4
  3c3b4: add $0x23,%eax -> 0x35c  (Y-accumulator + 35, see below)
  3c4e7: mov 0x1a(%eax),%dx ; cmp %edi,%edx ; jle 0x3c7bc   ; LOOP BOUND = planet[+0x1a]
  3c47e: addl $0x46,0x348(%esp)      ; Y += 70 EVERY slot
  3c470: eax = idx - planet[+0x18] ; idiv 5 ; cmp $0x4,%edx
  3c489: jne ...  else: 0x348 = 0x77 (Y reset 119); 0x35c += 70; 0x324 (X) += 70

=> LAW (exact): slot k (0-based, k = idx - surface_count) paints at
   X = 13 + 70*(k/5),  Y = 119 + 70*(k%5),  iterating k while
   (surface_count + k) < planet[+0x1a].  With the standard 10 orbital
   cells that is TWO columns x FIVE rows:
     col0 x=13 : y = 119,189,259,329,399
     col1 x=83 : y = 119,189,259,329,399
   — NOT isometric, exactly D26's "10 squares, five rows of 2".
   The orbital cells live in the SAME cell array as the surface cells
   (0x31c = 4*surface_count pointer offset into DAT_00043508+0x10, +4 per
   slot), item byte at cell[+1].  So +0x1a = +0x18 + 10 is the count law.

## F2 — HOVER OUTLINE LAW (same loop, 0x3c546..0x3c5d7)

  3c546: if (widget+0xac == idx && item_byte == 0xff && flag334 == 0
            && widget+0xab == 0xff)
  3c5d7: call 0x2fe04  with rect (X, Y) .. (X+0x46, Y+0x46) [70x70],
         colour immediate 0x96 (=150) and 0x45 (=69) frame size.

=> hover on an EMPTY orbital slot draws a 69/70-px box outline in palette
   index 150 (the same grey used for the surface adjacency hover,
   tPL-V1). Occupied slots (item != 0xff) draw their art instead; nothing
   is drawn for empty slots at rest. That is D26's "thin greyish box
   outline should appear" — a HOVER-only affordance, no resting frame.

## F3 — ART SELECTOR (0x3c84c / 0x3c8b0 helpers)

Empty-slot branch calls 0x3c84c(widget, idx) -> struct at esp+0x368:
   u16[0] = DAT_0006fd80 ; if item != 0xff: u16[+0x10] = item ;
   if item == 0x17 (23): u16[0] = table DAT_0006fd60[race], +0x10 = 0.
Occupied branch calls 0x3c8b0: same struct, and when item == 0xff uses
   (cell[0] & 8) ? 39 (0x27) : 0 for +0x10.
Blit: 0x1fc34(0x9f10c, ...) fetches the shape, 0x5d5a1(dest=&DAT_0004850c)
blits at the slot coords. 0x9f10c = shape-library handle.

## F4 — HIT LAW + VENDOR QUIRK (FUN_0003a880, verbatim decompile)

  uint FUN_0003a880(int x, int y) {
    if (x < 0xe || x > 0x98 || y < 0x78 || y > 0x1d4) {
      FUN_0003a820();  // lattice row/col decode
      return FUN_000395c4();          // surface cell
    }
    return surface + ((x - 0xd) / 0x46) * 5 + (y - 0x77) / 0x46;
  }
QUIRK [verified]: the hit rect [14,152]x[120,468] starts ONE PX INSIDE the
paint origin (13,119) — pixel (13,119) itself falls through to the lattice
leg (harmless: it decodes to no valid cell). The caller 0x3ac14 stores the
result in widget+0xac (the hover word the paint loop compares), and
0x3ac6b clears it when the hovered cell is an enemy-owned Ship (item 0x17
+ FUN_000396cc race check) — not modelled (no enemy-planet view port-side).

## F5 — ART SELECTOR RESIDUE (SEAM TPLV2-A)

0x3c8b0 fills the shape selector struct: sel0 = WORD[0x6fd80] (the shape
LIBRARY slot — a runtime global; only READERS exist in obj0 code at
0x1543d/0x47693/0x48aa7/0x50972, no static writer -> library identity
RUNTIME-DERIVED, unrecovered statically), sel16 = item byte; the Ship
(item 23) row takes race art from the RUNTIME table DAT_0x6fd60 (code at
0x6fd60 is NOT table data — the address is inside a function epilogue, so
the real table is relocated/heap: honest negative). PORT: blit planitem
record[item] centred in the 70x70 box (the witness blob 69x57 in box
(83,119) is consistent with centred placement), Ship included.

## F6 — PORT SHIPPED (tPL-V2)

 - planetview.{h,cpp}: orbitalSlotOrigin / orbitalSlotHitFor /
   orbitalSlotItem / orbitalHoverOutline + kOrbitalSlots/kOrbitalPitch.
 - ui.cpp kScreenPlanet: orbital loop AFTER the lattice block — occupied
   slot blits planitem[item] centred; empty slot under the polled mouse
   draws the 69x69 pal-150 box (chromePaletteArgb(150), same grey as the
   surface hover); click paths (order leg + select leg) hit the orbital
   rect FIRST (x<=152 never overlaps the lattice).
 - DELETED the t406 debug readout (title/Population/RES-IND-PROS text at
   x12 y118-170) — it sat exactly ON orbital column 0; the strip art
   carries the data now (t428d). planetViewFor call removed with it.
 - Pin tests/test_planetview_tplv2.cpp (grid 10/10 + bounds + column
   step + quirk; hover gate occupied/empty/pick/off-field/bad-star).
   Suite 505/0/0.

## F7 — PORT WITNESS PASS (tPL-V2 census)

scripts/tplv2_port_witness.sh (Xvfb :99, PID-only kill, winpos root-crop,
xsend NEW `warp` mode = XWarpPointer with NO button events — the legacy
`x y` mode clicks and the 400,470 corner click KILLED the app on run 1) +
scripts/tplv2_census.py against seed-5 seed-5 RESUME->STATUS->row0 shots:

  rest / rest-again: 0 target-coloured perimeter px at ALL ten boxes.
  hover-slot0: box(13,119) perimeter 276/272 pts == conv6->8(pal150) =
    (16,69,77); all nine other boxes 0 px.
  hover-slot6: box(83,189) 276/272; others 0.  VERDICT PASS.

BUG THE CENSUS CAUGHT (run 1 FAIL): orbitalHoverOutline had no `slot`
param — the == +0xac leg tested the hovered cell against itself, so EVERY
empty slot outlined at once (leak 2447 px). Vendor law is a PER-SLOT
compare (paint loop tests each k). Fixed: signature now
(camp, star, slot, p, pickPending); pins added (hover slot0 draws k=1/6
must be false). Suite 505/0/0.

HISTORY NOTE: the 276-vs-272 count = 4 corner pixels double-counted by the
perimeter walk; census counts >= 200 as hit.

## SEAMS (unchanged, carried forward)
- TPLV2-A: item-23 (Ship) race-table DAT_0x6fd60 runtime-unrecovered ->
  Ship draws its planitem icon like every item.
- flag334 tutorial ghost-mode leg not modelled (orbitalHoverOutline false).
