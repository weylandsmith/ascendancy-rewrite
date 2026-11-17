# t421 — 0x892ac TILE-COLOUR SEAM CLOSED STATICALLY (per-class law REFUTED)

TRIGGER AUDIT (done first, per STATE): no USER: lines after the D16 block in
docs/DECISIONS.md (file ends line 418 with the sheet text itself). playcap
live-timeline.jsonl mtime 2026-11-12 06:45 — pre-dates t419/t420;
scripts/r1_t85g_sitting.py re-run confirms same baseline-vs-t>=1240 shape,
NO new sitting. STATE's NEXT was WAIT; harness launched anyway, so this
iteration audited t420's claim that "every remaining seam needs a live-vendor
witness" — and REFUTED it for the 0x892ac seam, closing it with measurement
instead of a witness.

F0 THE SEAM AS ASSIGNED (t418 note, planets-ui.md §11; t420 re-check list
"witness 0x3c2a3 esp+0x310"): the claim was that the 8-byte table at 0x892ac
{00 00 01 03 01 03 02 02} "selects a 24-byte-stride vertex-parameter set per
something-per-class" — i.e. a per-terrain-class tile COLOUR law the port
(uniform pal[150]) is missing.

F1 COPY-SITE MEASUREMENT [verified verbatim, ascend_restored.bin capstone
sweep 0x3c1f8..0x3c2da; banked objdump t198_planwin.asm lines 1679-1701]:
  3c274 mov $0x960000,%eax            ; pal150
  3c279 lea 0x310(%esp),%edi
  3c280/87/8e/95 four stores of 0x960000 at esp+0x268/0x280/0x298/0x2b0
        (the FOUR VERTEX colour slots of the 24B-stride diamond record
        esp+0x260..0x2c0 — x@+0 y@+4 c@+8, 4 records, stride 0x18)
  3c2a3 mov $0x892ac,%esi             ; UNINDEXED immediate
  3c2d8/9 movsd x2                    ; copy EXACTLY 8 bytes -> esp+0x310
esi lifecycle (capstone, 13 insns 0x3c2a3..0x3c2d9): the ONLY esi write is
the load itself. No scaling, no class term, no reload. Every tile of every
size class copies the SAME 8 bytes and fills ALL FOUR vertex colours with
the SAME immediate 0x960000.

F2 WHOLE-IMAGE REFERRER CENSUS [verified, scripts/r1_t421_referrer_census.py
raw-u32 dual-form scan + capstone detail-mode precise pass over code span
[0x14bb0,0x82bb0)]: EXACTLY ONE code referrer to 0x892a0..0x89340 touches
0x892ac — 0x3c2a3. (Adjacent hits 0x89324/0x89325 are byte-disp references
from unrelated flag code; the raw scan's 76 "hits" are false positives from
misaligned windows — the precise X86_OP_IMM/X86_OP_MEM pass is the law.)
No second site indexes the table; no per-class addressing exists anywhere in
the image. Zero data-region u32 pointers point into the range.

F3 RUNTIME-VERBATIM [verified, scripts/r1_t421_c3_runtime.py RC=0]: guest
bytes at mem[B+0x892ac] == 00 00 01 03 01 03 02 02 in 178/178 independent
saved runs (every run under work/r1 with a decodable anchor, different
galaxies/species/turn depths) + slot 60 (deepest game, t327v t~1300+).
No writer ever touched the block in any captured state. A live esp+0x310
census could therefore only ever re-confirm constants.

F4 CONSUMER ANALYSIS (why the block is not a colour law): callee 0x61770
(polygon fill; args push $0x4850c, $4, lea esp+0x260) never reads the
caller's stack — full body 0x61770..0x61a92 has ZERO esp refs beyond its own
saved-reg frame (scan: none >=0x18(%esp)); it consumes the 96-byte vertex
block via arg1 (stride math shl3+shl1+add = *24 x count 4). Inside the
painter, esp+0x310 is referenced exactly TWICE in the whole function (banked
objdump grep): the copy target 0x3c279 and an overwrite 0x3c5b4 (second
paint branch reuses the slot as scratch). The 8 bytes are a fixed draw-mode
parameter block with NO identified consumer on this path — a compiler/
struct artifact. They modulate nothing per-class.

F5 VERDICT: THE PER-TILE-CLASS COLOUR LAW AT 0x892AC IS REFUTED. The t418
"selects ... per something-per-class" was a misparse of an unindexed
constant copy. The port's t418b uniform pal[150] fill IS the cited vendor
law (single immediate, all four vertices, all classes). No rewrite delta.
The seam DROPS from the live re-check list; t420's blanket "every remaining
seam needs a live witness" is FALSE for this seam — static + existing-save
measurement closed it. Remaining live-witness seams unchanged: H3 race
colours 0x12e18+specnum*494 (NOTE: save-census candidate, the t421 method
probably applies), t418b disc provenance F4 (0x9f10c), t419 reswin draw
chain, t416 pump cadence.

## PITFALLS BANKED (t421)
1. WRONG NEEDLE, DATA REGION: work/ascend_payload.bin vs
   work/ascend_restored.bin differ at FIXUP sites only — imm 0x3c2a3 reads
   0x66fc (intra-obj1) in payload vs 0x892ac in restored (delta 0x82bb0,
   OQ-011). Reading DATA bytes out of the payload file at an absolute image
   address is valid ONLY where no fixup lands (t421 verified 0x892ac file
   bytes agree in both images and match all saves — but don't rely on that;
   use restored for CODE truth, saves for DATA truth).
2. B vs P0: image BYTES live at mem[B + file_offset]; P0 = B-H is the
   POINTER-decode constant. First C3 cut read mem[P0+0x892ac] and produced
   178 false DIFFERs (H=88 shifts the window ~55 bytes onto psqwin.cpp
   debug-string sludge: "PLP...BUILD......../psqwin.cpp...HELP...").
   Control that catches it: the C1 law-window check mem[B+0x3c200] must be
   16/16 — print it alongside any data probe.
3. CAPSTONE: plain linear sweeps desync on mixed code/data (a 0x4000 sweep
   from 0x3b96c silently lost both known esp+0x310 refs — trust the banked
   objdump text grep, or use md.skipdata=True). For immediate/disp censuses
   use md.detail=True + X86_OP_IMM / X86_OP_MEM operand walk; regexing
   op_str re-derives false positives from misaligned windows (raw scan said
   76 referrers, truth is 1).
4. capstone lives in ~/tools/revenv/bin/python3 (NOT the execute_code
   sandbox interpreter, NOT system python3).

LEDGER: closes NOTHING (strict-close honest negative — the seam has no OQ
owner; t414..t419b precedent). The measurement is real: it retires a
live-witness ask the user could never have answered better than 178 saves
already did, and REFUTED-ROUTES gains the per-class-colour entry so no
future iteration re-opens it.
