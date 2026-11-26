

## P2 — VENDOR ANCHOR LAW CLOSED AT RAW BYTES [verified work/ascend_restored.bin]

FUN_0005caac prologue disassembled this iteration (capstone via
~/tools/revenv, region 0x5caac..0x5cb90) — the S12 arg-map note said the entry
rect fields are read "+screen"; the bytes now say exactly how:

  0x5cb41 mov eax,[ebp-0x4c]      ; clipL of the CALLER shape-struct (clamped >=0)
  0x5cb44 add [ebp+0x14], eax     ; screen_x += clipL
  0x5cb47/0x5cb4a                  screen_y += clipT (same shape)
  0x5cb4d..0x5cb59  esi := payload + [payload + 8 + 8*sel]   (record entry)
  0x5cb61  dest_x = [esi+0x8]  + [ebp+0x14]     <-- RECORD L ADDED
  0x5cb6a  dest_y = [esi+0xc]  + [ebp+0x18]     <-- RECORD T ADDED
  0x5cb73  right  = [esi+0x10] + [ebp+0x14]
  0x5cb7c  bottom = [esi+0x14] + [ebp+0x18]
  0x5cb85  add esi,0x18            ; stream = entry+0x18 (S12 confirmed)
  0x5cb8b  cmp right,dest_x -> 0x5cea5 (error -3 fully outside)
Widget pass FUN_00031384 shape-blit arm 0x3143a..0x31467 pushes
[desc+9]>>16 then [desc+7]>>16 as the x/y, so the descriptor supplies an ANCHOR
and the record's bbox corner is added on top. CONCLUSION: dest = anchor + (L,T)
is LAW, not inference.

## P3 — BLAST AREA [measured scripts/tPF5_anchor_census.py]

Every lib the port draws through blitShape, counting records with L!=0 or T!=0:
  planres 21 recs  0 anchored      planpro 21 recs  0 anchored
  planind 21 recs 21 anchored  (0,1)x8 (0,5)x5 (0,11)x2 (0,20)x4 (0,23)x2
  17np k1,k2,k3 anchored (1,1)/(1,1)/(2,1); k4 (field) (0,0)
  planitem all 40 NEGATIVE anchors (L,T ~ -34,-17) — the port centres these
    deliberately (structure art is centre-anchored), NOT touched this task
  smship19 recs negative (-66,-41) etc — ship-row art, tPF-4, NOT touched
  planal* 55/55 records negative ((-47,-48) x11, (-75,-75) x11 ...) — the
    planet disc, port centres by gcx-W/2, NOT touched
Rationale for the narrow fix: positive-T records are the strip's; the negative
anchors are centre-anchored art the port already positions by its own centre
law, and adding (L,T) there would shift 95 already-witnessed pixels for no
cited reason. Fix scope = the three strip panels ONLY.

## P4 — FIX SHIPPED + PINNED [build+suite green]

 - NEW pure law fn ui::stripGaugeBlitPos(rect, recLeft, recTop) in
   rewrite/src/ui/planetstrip.{h,cpp} -> {x0+L, y0+T}. ui.cpp strip call site
   now composes it (blitShape(ren, gl, gr.rec, gp.x, gp.y)); planres/planpro
   unaffected (L=T=0).
 - STALE DOC CLAIMS CORRECTED (they asserted a law that is false under the bbox
   law, and would have been re-tightened into a fabricated gate):
   planetstrip.h header block, planetstrip.h gate comment, planetstrip.cpp gate
   error string ("!= 107x99 (rect-fill)" -> width-108 + varying-height law).
 - PINS rewrite/tests/test_stripanchor_tpf5.cpp x5 (CMakeLists entry ADDED —
   tPF-4's silent-zero-tests trap avoided): (1) planind is the only anchored
   lib + the exact T ladder {23,23,20x4,11x2,5x5,1x8} + H==100-T + anti-vacuity
   assert; (2) bottom-right pinning for all 63 records THROUGH the shipped fn;
   (3) dropped-anchor-is-the-bug: shipped y == y0+T on all 21, old band == T,
   new band-below == 0, differ==21; (4) ui.cpp call-site wiring (source-text
   pin, tngs_s29 precedent — anchorless form must be ABSENT); (5) gate accepts
   varying heights, rejects 17np on count.
 - SUITE 564 -> 569, 0 skipped, 0 failed. Build both ascendancy AND run_tests.
