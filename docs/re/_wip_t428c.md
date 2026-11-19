# _wip_t428c.md — PLANET-SCREEN CYCLE 3 (FIELD PROVENANCE)

Task: docs/STATE.md NEXT ACTION t428c. Three parts: (a) identify the row tables
BYTE[0x7445c]/BYTE[0x744a8] the lattice loop reads; (b) decode 17np k4 (625x357)
and compare CONTENT against witness B's field region to settle/kill the
k4-as-field-backdrop candidate at 0x3b98b; (c) budget-permitting the tile-click
popup law. Frame is ALREADY EXACT (t406) — untouched. Grid GATE hunt stays
closed (t428b F1 refuted it).

Sitting check [verified]: work/r1/playcap/live-timeline.jsonl mtime
2026-11-12 06:45 (unchanged since the t428b check) — NO new sitting, so the
t428c assignment stands.

## F1 — THE ROW TABLES ARE PINNED: grid B / grid C OF planitem.txt, AND THE
## PAINT-BODY INDEX LAW IS `15*size + row` (t428c)

TABLE IDENTITY [verified — previously banked, re-cited here so the field thread
stops calling it unpinned]: the two DATs are the ASCII tables in
extracted/ascend00/planitem.txt loaded by the t294 sibling loaders —
grid B tokens 45..119 -> 0x7445c+15i (loop 0x38070..0x380a9, record 0x1ce3) and
grid C tokens 120..194 -> 0x744a8+15i (loop 0x380ad..0x380ed, record 0x1ce6).
Citations: docs/re/_wip_t294.md BONUS 2, docs/re/planets-ui.md §11,
rewrite/src/game/economy.h:99-100 + economy.cpp:241-242,289. OQ-014 CLOSED
2026-10-06 (OPEN-QUESTIONS.md:939 — "grid C row sums = size-class cells
2650/2650"). Nothing new to close; the t428b note "table identity UNPINNED" was
a MISREAD of the ledger, not an open fact.

INDEX LAW [verified from work/t198_planwin.asm, NEW this cycle]:
- 0x3b977 `mov %eax,%ebp` (ebp := u32[0x43508] = the planet record the window
  is showing); 0x3b979-0x3b984: eax := [0x43508], dx := u16[eax+0x14] -> banked
  esp+0x340. So the size class is u16 [planet+0x14].
- 0x3bb19..0x3bb3f (row-loop head): ecx := 0x6e (110) -> esp+0x354 (x cursor),
  esi := 0x19a (410) -> esp+0x320 (y cursor), and
  `eax := edx<<4; eax -= edx` = 15*size -> esp+0x358.
- 0x3bb63 `inc %edx` on esp+0x358 once per ROW (step leg 0x3bb48..0x3bb79).
- Therefore BOTH table reads are indexed by `idx = 15*size + row`:
  0x3bb8e `mov 0x7445c(%edx),%al` -> esp+0x318, and inside the row loop
  0x3c1f2 `mov 0x7445c(%eax),%dl` / 0x3c1fa `mov 0x744a8(%ebx),%al` with eax
  and ebx BOTH loaded from esp+0x328, which 0x3bbb0 sets from the same edx.

INNER-LOOP COUNT LAW [verified — this is what the two reads actually do]:
- Row head sets esp+0x318 := B[idx] (0x3bb94). The inner loop increments
  esp+0x318 at 0x3c1c8 (`inc %esi; mov %esi,0x318(%esp)`) and separately
  increments esp+0x330 (the column cursor, 0x3c1c9/0x3c1d4) and adds 4 to
  esp+0x34c (the record stride cursor, 0x3c1ca).
- The test at 0x3c1e2..0x3c20b computes eax := B[idx] + C[idx] and compares
  against ecx := esp+0x318 = B[idx] + n (n = cells already visited this row);
  `jle 0x3bb48` exits the ROW when B+C <= B+n, i.e. when n >= C[idx].
- => the inner body runs EXACTLY C[size][row] times per row, at columns
  B[size][row] .. B+C-1. B = per-row START COLUMN, C = per-row CELL COUNT —
  both indexed by (size,row), NOT per-cell.
CORRECTION to t428b F1: its reduction "0x744a8 is a PER-CELL count of lattice
positions that get art" is wrong in granularity. It is per-(size,row). The
conclusion it drew still holds (a fixed table read, no function of planet
improvement/pop state), so the H-FIELD-STATE refutation STANDS — but the row
shape now has a cited source: rows with C==0 paint nothing, which is exactly
why the painted region is a diamond rather than a 15x15 square.
Measured grid values (extracted/ascend00/planitem.txt, parsed this cycle):
  B row0 [0,0,0,0,4,4,5,0,0,0,0,0,0,0,0]   C row0 [0,0,0,0,2,3,2,0,...]  sum 7
  B row1 [0,0,0,4,3,4,5,6,0,...]            C row1 [0,0,0,1,3,3,3,1,0,...] sum 11
  B row2 [0,0,3,2,3,3,4,5,7,0,...]          C row2 [0,0,1,4,4,5,4,4,1,0,..] sum 23
  B row3 [0,2,1,1,2,2,3,4,5,7,7... ]        C row3 [0,2,5,6,6,7,6,6,5,2,0,..] sum 45
  B row4 [1,0,0,0,1,1,2,3,4,5,7,...]        C row4 [3,6,7,8,8,9,8,8,7,6,3,..] sum 73
  (sums 7/11/23/45/73 = 159 total per size class; matches the t294 file-vs-RAM
  44/44 byte check.)

PORT STATUS: rewrite/src/ui/ui.cpp:1767-1768 loops
`col = ptt.rowOffset[psize][row] .. rowOffset+rowWidth` — i.e. the port ALREADY
implements the B/C law with the same (size,row) index. No edit justified by F1;
this cycle's value is the citation + the [planet+0x14] size-class provenance +
the granularity correction.

## F2 — 17np k4/k5 DECODED AND REGISTERED IN WITNESS B (t428c) [MEASURED]

Decode [verified]: tools/shp_pngdump on _spec_t254_17np.tsv -> 9/9 recs ok
(work/r1/shp_png/t428c/raw/). k4 = 625x357 index plane, 46 distinct values,
99.88% idx 0 (black); 269 LIT px scattered over x26..620 y2..353, colours
navy/purple-family (idx 197..208 = raw (47,16,63)-ish) + low greys — i.e. a
STARFIELD speckle, not photo art, not lattice art. k5 = 416x316, 31 values,
10748 lit px (8.2%), spread full-frame.

REGISTRATION [scripts/t428c_field_register.py, tol=8 per-channel, game.pal
6-bit scaled]:
- k4: exhaustive offset scan -> best 158/269 (58.7%) at png offset (87,215)
  = SCREEN (7,115). Colour-shuffle control (geometry kept, pairing killed)
  collapses to 6..12 => pairing is REAL, not dark-pixel coincidence. Fresh-
  array random-offset search best 13/269 = background: the peak is UNIQUE
  (script check "background < best/2" PASS).
  SCREEN (7,115) IS EXACTLY the blit-1 coordinates of t428 F4 (pushes
  $0x73,$0x7 at 0x3b9c0-0x3b9c6 => x=7,y=115). So the 0x3b98b-site blit
  (lib slot u16[0x6fd9c] = 44 = 17np.shp, selector = [EBP+0x1c]>>16 =
  SENDMESSAGE = 1 for PLSQUARE) blits 17np k? at (7,115), and the only
  17np record whose speckle pattern registers there is k4.
  [inferred] selector 1 -> record k1 law (t254 SEL law) applies to the POP
  panel's selector table, NOT the widget selector; here selector==SENDMESSAGE
  and the record that lands is k4 — the record-index law for THIS call is
  still open, but the CONTENT candidate k4-as-field-backdrop is SETTLED, not
  killed: k4 IS painted, at (7,115), over the frame.
- k5: best 1566/10748 (14.6%) at png (304,207) = screen (224,107); shuffle
  control 347..374; random-offset distribution mean 56 sd 81 max 1037 =>
  z=18.6, a real peak. k5 registers SOMEWHERE in B (screen (224,107) is
  inside the PLIND rect region) but at only 14.6% — occluded/overpainted or
  partial. NOT settled this cycle (which widget, what selector).
- Mismatch anatomy for k4 at its anchor: 111 mismatches, 101 of them BRIGHT
  witness px (lum>60) — the pop-grid/terrain art paints OVER the starfield;
  10 dark mismatches mean witness (7,11,8) vs k4 star (53,58,51) — capture
  gamma/quantisation of near-black star tones [inferred].

CONSEQUENCES:
1. The t418 "DISC: 0x3b98b = 17np k4/k5 backdrops" candidate is RESOLVED at
   the content level for k4: k4 is the field/backdrop STARFIELD speckle
   blitted at screen (7,115). Witness A's BLACK field is now explained even
   further: k4's contribution IS speckle (269 px of ~223k) — on A's lineage
   screen it is invisible at a glance, consistent with the t428b F1 finding
   that no vendor gate exists.
2. Port gap [verified against rewrite]: ui.cpp has the B/C lattice
   (ui.cpp:1767-1792) but NOTHING paints a k4 starfield speckle at (7,115).
   Whether to port it = the speckle is a fixed 269-px pattern from a vendor
   asset: porting is a pure-asset blit (17np rec k4, 0x9f10c slot law), size
   ~1 pin + 1 painter call. Candidate for t428d.
