# tRS-V1d — SEAM TRSV1c-E: VENDOR BLITTER ANCHOR LAW (working log)

## P0 ANCHOR LAW [MEASURED, raw asm work/ascend_restored.bin + decompile work/combat_decomp/5caac.c]
Chain: shape draw = FUN_0005d5a1 (hinted blitter) -> fast path 0x5e10b when
(scaleX==0x10000 && scaleY==0x10000 && arg7==0) -> FUN_0005caac (unscaled
row-RLE) or FUN_0005cf96 (mask/alpha variant, selected by [ebp+0x2c] bit0).
0x5caac body (Ghidra decompile lines 58-64, VERBATIM read of the asm):
   piVar1 = *param_1                  // draw-desc -> record struct
   W = piVar1[1]+1 ; H = piVar1[2]    // dims = bbox-diff law (0x61058 twin)
   param_4 += param_1[1]              // x' = passed_x + desc[+4]
   param_5 += param_1[2]              // y' = passed_y + desc[+8]
   rec = *(param_2 + 8 + rec_idx*8) + param_2   // dir entry RELATIVE to base
   dest_left   = rec[+0x08] + x'      // rec.bboxL + x'
   dest_top    = rec[+0x0c] + y'      // rec.bboxT + y'
   dest_right  = rec[+0x10] + x' ; dest_bottom = rec[+0x14] + y'
=> THE PASSED (x,y) IS AN ANCHOR POINT, NOT A TOP-LEFT. Content lands at
   anchor + (bboxL, bboxT). (0x61058: W=R-L+1, H=B-T+1; 0x6108c returns
   (int32[+8]<<16)|u16[+0xc] = the same (L,T) pair = the "hotspot".)

## P1 resring.shp MEASURED bbox quads (extracted/ascend01/data/resring.shp)
Header '1.10' count=4; record dir starts 0x38; the four bbox quads read at
the record starts (S8.2 offsets 56/1200/2363/3532) => (-30,-30,29,29)
W=H=60. bboxL,bboxT = (-30,-30) => content spans anchor-30 .. anchor+29,
i.e. THE RING IS CENTRED ON THE ANCHOR WORD BY CONSTRUCTION.

## P2 CONSEQUENCE (resolves TRSV1c-E)
The vendor passes the projected word word[win+0x5f1]/[+0x6b9] sar 16 DIRECTLY
as the anchor (no centring arithmetic anywhere in the caller), and the record
bbox (-30,-30) does the centring. So vendor drawn-centre == hit-centre.
Our port blits at (x-14, y-14) and draws the decoded W x H rect with its
TOP-LEFT at the blit point => a 60x60 record centres at (x+15,y+15) — exactly
the measured +15,+15 seam. FIX = vendor law verbatim: blit at
(x + record().left, y + record().top). shp.h:80 ALREADY documents left/top as
"bbox L (content offset from the caller anchor)" — the field was there, the
research screen just never used it.

## P3 PORT FIX + PINS + MUTATION (shipped)
- ui.cpp NODES block: blit at (c.x + rr.left, c.y + rr.top) via
  kLibs[8].record(frame); the (x-14,y-14) constant deleted. The silent-degrade
  vector-ring fallback is UNTOUCHED (only fires when the lib refuses).
- rewrite/tests/test_researchanchor_tRSV1d.cpp x3 (CMakeLists registered):
  (1) resring k0..k3 L==T==-dim/2, span contains the anchor, |lo+hi|<=1;
  (2) SOURCE-TEXT wiring pin (tngs_s29 precedent): block contains
  "c.x + rr.left"/"c.y + rr.top", NOT "c.x - 14"/"c.y - 14";
  (3) researchHit at row 2's projected centre resolves row 2 (drawn centre
  == hit centre observable through the pure law). SUITE 523 -> 526, 0 failed.
- MUTANT M-V1d (offset -> -15,-15, rebuild): pin (2) FAILS x4 checks.
  RESTORED, md5 089d35bf2644513f90aae1f62132027a re-verified, suite green.

## P4 PIXEL WITNESS (scripts/tRSV1d_witness.sh + tRSV1d_ringcentre_census.py)
- Flow = the tRS-V1c nav (RESUME -> RESEARCH rail -> dolly out twice), shot
  BEFORE the click, census every logged "available" centre. Seed 5: logged
  centre (397,240); CONTENT bbox about it = (0,0,59,59) n=828, centre offset
  (-0.5,-0.5) — the content fills the anchor crop exactly as the bbox law
  predicts; control crop +30,+30 n=207 (not full) = the ring is localised.
  VERDICT PASS.
- MUTANT leg at the PIXEL level: with the -15,-15 offset the census reports
  content bbox (15,15,59,59) offset (+7,+7) and FAILs; restored -> PASS.
- tRSB1_witness.sh RE-RUN post-fix: VERDICT PASS (study Xenobiology,
  panel-green 0->690, changed-px within 40 of centre 563 -> 827 — the ring
  content moved ONTO the click point, so the local leg grew; the +-24 square
  witness never depended on the offset).
- CENSUS v1 LESSON (banked): thresholding on brightness measures the bright
  RIM subset, which the ring art biases upward — v1 reported a spurious
  -1.5 px y offset on the CORRECT render. The right measure is the CONTENT
  bbox (pixels differing from the flat field bg (16,16,24)).

## P5 SEAM LEDGER
- TRSV1c-E CLOSED by this iteration (drawn-centre == hit-centre, measured
  port-side + law cited vendor-side).
- TRSV1-C (restree.shp picture consumer), TRSV1c-D (frontier off-frame at
  rest), TRSV1b-A (dolly step value) UNCHANGED.
- No OQ row touched: the research screen tracks none (open=[016,019]);
  honest negative under strict-close.

## P6 GRADE-PACKAGE NOTE
- scratchpad/PR-usergrade.png + PR-checklist.txt stay VALID: the +15 px seam
  was never a graded item (it was an internal seam), and checklist item 4
  (picture-in-disk MISSING) is unchanged. If the user ruling asks for a fresh
  ours-shot, scripts/tRSV1d_witness.sh produces it (before.png = tree.png).
