# Title art identity — t386 CLOSED 2026-11-14 (title screen = 0opening.gif)

Hand-authored (no generator references this file — verified via grep before
writing; STATE.md QUEUE phase-10 banking rule). Instruments written this
iteration, all re-runnable:
- `scripts/t386_title_art.py` — GIF structural walk + frame-identity scan +
  race-art census (sections A..E)
- `scripts/t386_colour_witness.py` — palette-membership law vs every engine
  palette + the two video unions
- `scripts/t386_remap_test.py` — zero-shift single-valued map test (REFUTED arm)
- `scripts/t386_registration.py` — landmark + silhouette + shift-swept
  conflict-count map test (THE decisive instrument)
- `rewrite/tests/data/title_palette_t386.tsv` — the derived title palette
  (52 entries: gif index -> gif GCT rgb -> vendor shot rgb)

VERIFICATION RULE respected: no self-graded vision of our renders. The one
vision read is of the PINNED VENDOR screenshot (external-grader artifact,
docs/re/refcap.md §1); every identity claim below is a pixel/index measurement.

## 1. The identity law [verified]

**The vendor title screen is `DATA\0OPENING.GIF` blitted 1:1 at logical
(0,0), drawn through an index-preserving PALETTE SWAP, with one index kept
as a colour-key hole for the menu.**

Decisive witness (scripts/t386_registration.py, full-grid map test): build
the map f(gif_index) = shot_colour over capture rows aligned by
capture_row = logical_row + 40 (the banked window-chrome offset, refcap.md
§1 "ROOT row = emulator row + 40"):

    shift +40:  0 conflicts over all 52 art indices (238k pixels)
    shift +39:  213,415 conflicts
    shift +41:  117,327 conflicts
    shift  0:   206,356 conflicts        (zero-shift identity REFUTED)

0 vs 10^5 is not a near-miss; the GIF IS the screen. The single non-
singleton index is the key solid (§2). The shot's six white label bands
(centres 254, 294, 334, ~372, ~410, ~450) sit at windows.txt button centres
(215, 255, 295, 335, 375, 415, 455) + 40 capture chrome; the seventh (Exit
to DOS, 495) is below the 480-tall capture — exactly as the D9 seven-button
law predicts.

## 2. The key-solid: the GIF ships the menu hole [verified]

GIF index 255 (GCT rgb [0,0,255]) occupies EXACTLY the bounding box
(159,200)-(477,470) — bit-for-bit the union of the seven windows.txt button
rects (159,200..470)+(319x31 minus edge) — 69,223 px = 22.5% of the frame.
Including index 255 in the map test produces the ONLY conflicts (11,039):
under the key the shot shows the game's own menu chrome (0opening.shp
strips + VendorText labels), not GIF art. So the vendor engine skips/blanks
index 255 and composites the button column there. This is the mechanism the
port must copy: GIF blit -> key-255 hole -> 0opening.shp + text on top.

## 3. What the pieces are [verified]

| asset | measurement | role |
|---|---|---|
| 0opening.gif | 45,092 B md5 e2c5fb66a57595fc550bbb90cc8a0952; GIF87a, ONE frame 640x480, GCT 256 (sha[:16] aa78b73219b6cbe9), index plane sha[:16] 85310df45be96aeb, 53 distinct indices, non-bg density 0.9996 | THE title art |
| 0opening.shp | magic "1.10", N=7: one 318x30 + six 30x318 records, 7,223 B | menu STRIP SET (button chrome), NOT art |
| windows.txt L34-36 | TYPE=100 STATENUMBER 0 SHAPEFILE DATA\0OPENING.SHP | declares the strip lib state for the opening screen |
| exe string | `DATA\0OPENING.GIF` at payload file offset 0x835b6 (restored image), neighbours `..\corn.cpp`; referrers in the 0x2183x startup cluster (docs/re/datafiles.md §2) | the boot-time GIF open |
| intro65a.flc, logic.flc | EXACT index-plane match count vs GIF frame: 0 of 1144, 0 of 226 | the GIF is NOT a movie frame |

## 4. The palette swap (and what it is NOT) [verified]

The GIF's own GCT is NOT the title palette: index-preserving swap test over
the art region scores 1/39 against the GIF's GCT, 1/39 game.pal, 1/39
logo.pal, 0/39 subfont.pal, and best-of-1144 intro65a frame palettes 1/39.
The .haz index-remap hypothesis is dead too (black00..15 + racea03: 0/45).
The transform is a straight COLOUR replacement per index: derived map in
title_palette_t386.tsv; channel deltas cluster at -39..-43 (a darkening of
the GIF's own entries, e.g. idx128 [254,177,96]->[215,138,56]), with no
linear model tighter than max-err 33 — the vendor simply installed a
different 256-entry table. WHERE that table lives (embedded literal vs
built at boot) is NOT resolved this row; the derived TSV is the portable
witness. For the port: render GIF indices through the TSV colours.

Consequence for phase 10 MEASUREMENT LAW (new law, banked here): palette
MEMBERSHIP (refcap d0/d4) is BLIND at the title screen — every candidate
palette scores identically d0=9.2% (only black exact) because the screen is
a re-coloured render. The working instrument is STRUCTURAL REGISTRATION:
single-valued index-map conflict counts at the capture-chrome shift. Do not
re-run membership laws to identify title chrome.

## 5. The Chamachies lead (D9 user testimony) [measured, not supported]

Chamachies = specnum 19 (species.md roster; ai-data.md race19.dip). Their
art cannot compose the figure: lgrace19.shp is a SINGLE record (51,416 B,
header dims 296x?, zero records >=200x200; absent from ascend01),
smrace19.shp is one 49-px sprite (7,653 B). The figure is the GIF's own
prerendered art, not race art. Whether the vendor's GIF figure "looks like
a Chamachies head" is a user-grader aesthetic reading (the pinned screenshot
vision read describes a reptilian head, top-centre, brown/gold/tan, red eye
at capture (312..318, 83..89) = logical ~(315,46)) — mechanically the
SOURCE question is closed: lib 0opening.gif, full frame, no race asset
participates.

## 6. Honest negatives + open residues

1. BLIT CHAIN EDGE: the GIF name's referrer is recorded only as "the 0x2183x
   startup cluster" (datafiles.md §2). Neither the pool-relative immediate
   0xa06 (= 0x835b6 - 0x82BB0, OQ-004 law) nor the raw VA 0x835b6 occurs as
   a u32 anywhere in work/ascend_restored.bin (576,643 B scan). The
   reference is not a plain u32 immediate. Instrument that would resolve it:
   Ghidra xref walk of the 0x2183x cluster on the restored image (NOT tried
   this iteration — budget; the identity does not depend on it).
2. Where the vendor's title PALETTE TABLE comes from: unresolved (§4); the
   derived TSV substitutes.
3. Our own stdlib GIF-LZW desyncs on this file at output index 6096 (early-
   change codes); PIL is the reference rasterizer (same one refcap uses);
   ffmpeg's pal8 plane carries 1,024 B extra per frame — not comparable.
   Decode pins above are PIL-plane values.
4. The GIF bottom rows 440..479 are clipped by the 480-tall capture at
   +40; they are measured only from the GIF itself (bottom ~40 logical rows
   never witnessed on the vendor screen). The port renders them; the grader
   can only see 0..439.
5. No OQ ledger row moved: t386 is phase-10 QUEUE work (STATE.md), the
   strict-close ledger (OQ-016, OQ-019 open) is untouched.
6. t390 residue (§8.3): HOW the engine uses 0opening.shp at the title
   screen is unresolved (windows.txt TYPE 100 declares the lib; the strips
   are measurably NOT the label glyphs). Candidates: hover/selected button
   state art, or a fill layer under the TEXTITEM render. Instrument that
   would resolve it: live-RAM diff of the draw-time verbatim library copy
   (shp.md §10/S12) while hovering a button — NOT tried; the screen closes
   the band law without it.

## 7. Port implementation checklist (feeds t387+)

- Title render: decode 0opening.gif index plane (PIL law mirrored in C++ or
  ship the extracted plane), colour via title_palette_t386.tsv, blit at
  (0,0); SKIP index 255; then 0opening.shp state-0 strips + VendorText
  labels at windows.txt rects (159,200..440 step 40, h 30).
- The wordmark ("ASCENDANCY") and the creature are INSIDE the GIF — the
  port gets them for free from the blit; do not add shp/text art for them.
- Verification for t387's own pixel work: registration conflict-count at
  shift 0 against OUR captures (self-graded VISION still banned; conflict
  counting on our own index plane vs our own screenshot is mechanical).

## 8. t390 LANDED 2026-11-14 — the blit exists, art-zone mass 0 -> 124,800

Instruments (all re-runnable): `scripts/t390_strip_witness.py`,
`t390_textmatch.py` (venv python), `t390_gifref.py`, `t390_lzwmirror.py`,
`t390_slices.py`, `t390_artmass.py`; screenshot harness
`scripts/r1_t390_titleshot.sh`; witness
`work/r1/loop/t390-artzone-witness.png`.

Code: `rewrite/src/formats/gif.{h,cpp}` (GIF87a single-frame index-plane
decoder, refuse-not-clamp), `rewrite/src/ui/titlepalette.{h,cpp}` (TSV
load + GCT fallback flagged per-index), `title.cpp` blit + band fill;
pins `rewrite/tests/test_gif_t390.cpp` (297 tests, 0 failed).

New measurements that REFINE §7:
1. INTERLACE TRAP [verified]: the file's LOGICAL SCREEN packed byte is
   0xd7 (interlace bit SET) while the IMAGE DESCRIPTOR packed byte (offset
   790) is 0x00 (not interlaced). The decoder reads interlace from the
   descriptor (spec law) and refuses if set.
2. CODE-WIDTH LAW [verified vs PIL]: grow when next >= 2^width. The
   "early change" variant desyncs at output 11208 of THIS file
   (t390_lzwmirror.py two-variant test). The C++ decoder now matches the
   PIL plane BIT-EXACTLY (ndiff 0 over 307,200 B; FNV pins in the test).
3. THE SHP STRIPS ARE NOT THE LABELS [verified]: state-k strip ink
   (values 15/145; fills 242) vs the pinned shot's white(44) mask — best
   shift overlap 74/234 at (dx,dy)=(-23,-2), ink bbox cols 89..227 vs text
   cols 275..361. §7's "shp strips + text" composition is WRONG for the
   labels; the white labels come from the TEXTITEM render. The strips'
   role at the title screen stays an honest residue (§6.6).
4. BAND-CLOSURE LAW [verified per band]: every pixel inside a button rect
   of the pinned shot is EXACTLY flat fill (0,0,8) + label white
   (215,215,215) (k1 carries 40 black AA pixels; k6 is below the capture).
   The port therefore paints fill + VendorText into the key hole — and our
   own render now closes the same law (t390_artmass.py: every band
   other=0, fill 9.3-9.5k, white 106-311).
5. ART-ZONE VERDICT on our render [verified, mechanical]: rows 0..194
   non-bg mass 124,800 (was 0 at assignment), top-5 colours all in the
   TSV vendor set ((215,138,56) first — the t386 §4 example pair).
   `ui title art ok 640x480 key255-hole` in the run log.
6. §7 wordmark law respected: no text/band frame drawn when the art is
   present (fallback keeps the old honest-vector render).
