# _wip_t433 — CHROME EXACT MEMORY-SURFACE ROUTE (WIP, this iteration)

Task (STATE.md NEXT ACTION): determine whether the vendor chrome/speckle
generator has an EXACT memory surface reachable via the pointer law, so the
port's fitted Markov approximations (chrome.md SS1.5, speciesWellAt chain
45/35) could be replaced by the vendor's exact bytes. Route as assigned: R1
scratch-copy session + guest-RAM capture. Probes below ran the ZERO-CAPTURE
preflight first, which is where the answer landed.

## F0 — Alignment law re-verified (BINDING for every census here)
- docs/assets/refcap/*.png : 640x480, png_row = SCREEN_ROW + 40 (rows 0..39
  pure black [verified this iteration: (ref[:40]==0).all() True]).
- work/screens/*/  *_game.png (VNC grabs): png_row = SCREEN_ROW (identity;
  screen row 0 already carries chrome-family rgb (90,134,140) at x0..2).
  [verified] R-t425c said this for original-strategic-map.png; it generalises.
- PITFALL (self-inflicted, t433): slicing BOTH families at the same file rows
  compares screen y vs screen y+40 and silently produces junk identities
  (got 22.8% / 16.2% that way). Always convert refcap file rows -40 first.

## F1 — Palette quantisation law (BINDING)
- refcap is palette-PURE under game.pal with the DOSBox DAC scale
  rgb = raw6*4 + raw6//16 : 100.0% exact over all 307200 px of
  original-strategic-map.png [verified]. chrome.md SS1.1's stated scale
  (v*255//63) only reaches 91.2% exact — the *4+v//16 scale is the right one.
- work/screens/*_game.png (DOSBox-X scaler output) is NOT palette-pure:
  69.3% exact under either scale, 82.5-83.1% within nearest-palette
  distance <=4, max distance 8, 181 unique rgb vs refcap's 190 [verified].
  => VNC grabs can only support TOLERANT colour statements, never byte-exact
     ones. Indexing them by argmin is unsafe (palette near-ties flip index
     for identical rgb); compare raw rgb with a +-2 gate instead.

## F2 — PROBE 0: no verbatim vendor chrome run in guest RAM (clean negative)
scripts/t433_surface_probe.py + a pitch-independent per-row variant.
- 63 signatures of 4 stacked left-band rows (28 px each): 0/63 hits in the
  Memory (17,055,880 B) AND Vga (2,647,348 B) members of 41/42.sav.
- Weakened to single 7-px band rows (pitch-independent: a run of <=7 px at
  any stride >=7 is found by a contiguous search of the flattened image) over
  screen rows 40..479 x 20 saves x {Memory, Vga}: ZERO hits, 0 blobs with any
  hit. [verified]
- Save-side sanity: game.pal's raw 768 B IS present verbatim in Memory member
  0x28a6b3 (phys 0x28a62b per the pointer-value law) => the search machinery
  works on these members. [verified]
- Vga member is NOT a raw framebuffer: 0 of 646 4-KB blocks exceed 5.0 bits of
  entropy (median 0.0, max 4.24); Memory at phys 0xA0000 is 0xFF-filled.
  [verified] => these saves hold no 640x480 paletted surface at all, so F2 is
  evidence about the save corpus, not a refutation of a RAM surface existing
  in a live session. A live capture would still be a NEW probe, not a re-run.

## F3 — Within-session identity is TOTAL; cross-pipeline identity is partial
Left band screen x0..6, y40..439, aligned:
- t252 session, 4 shots (baseline/back1/back2/final_escape2): 100.0% pairwise
  identical [verified] => the field is painted once per process and never
  repainted (corroborates chrome.md F1 "screen-fixed, painted once").
- refcap(map) vs t252(map): PARTIAL — see F4 for the corrected number.

## F4 — THE CHROME PATTERN IS CANONICAL ACROSS PROCESSES (decisive)
Aligned screen-coordinate comparison, palette-INDEX plane (the scaler-safe
representation; VNC grabs blend rgb but decode to the vendor's index):
- ref-map vs t252-map (VENDOR pristine vs our scratch-copy session, two
  independent processes): left band x0..6 y40..439 = **100.0%** index-identical
  (2800/2800); top band y0..6 x0..465 = **100.0%** (3262 px); right strip
  x466..472 y60..439 = **100.0%** (2660 px). t252-species shot identical too
  (100.0% left band) => same field on every screen, per process-independent.
- Tie control: game.pal has only 253 unique rgb (idx 127/241/243 duplicate
  others), 758/281600 refcap px are nearest-palette ambiguous; restricting to
  tie-free px leaves the 100.0% unchanged. A 3x5-window "scaler-tolerant
  consensus" test also gives 100.0%. [verified]
- CONTRAST pairs (same statistic, same regions): ref-map vs ref-planet left
  band 78-90% per 40-row block (never 100), full-screen 59.3%; ref-map vs
  ref-species full-screen 68.7%. So 100% is not the trivial/ceiling value —
  the ref-vs-ref family genuinely disagrees while VENDOR-vs-OURS agrees
  exactly. [verified]
VERDICT: the chrome field is a CANONICAL deterministic pattern, not a
per-process random instance. The vendor generator is seeded deterministically
(the same bytes appear in a vendor capture and in a scratch-copy run on a
different machine/process), so chrome.md SS1.5's "statistical law is the
ceiling" was a ceiling on the ROUTE, not on the pattern: an exact pattern
exists and is reproducible. Consequence for the port: the current splitmix64
per-pixel Markov draw can never be byte-exact; exactness needs either the
canonical byte run or the generator + its seed.

## F5 — THE PATTERN IS NOT A CONTIGUOUS BYTE RUN ON DISK (clean negative)
Whole-corpus scan of extracted/ (471 files) for verbatim vendor chrome bytes:
- 396 signatures of 4 stacked left-band rows (screen y40..435, 28 B each):
  **0 files with >=1 hit**. A 448-byte top-band block (y0..6 x0..63): 0 hits.
- 400 single-row 7-B signatures: 16 files with hits, 147 max
  (7racesel.tmp, 1starmap.tmp, 3cfgnew.tmp, 13negot.tmp, 20res.tmp ...), but
  the SAME regions give 0 hits at 28 B => the 7-B matches are low-entropy
  coincidences (chrome rows are short runs of grey/teal ramp indices). NOT
  evidence of a stored surface. [verified]
- PITFALL (self-inflicted x2, t433): (a) numpy int64 `.tobytes()` makes a
  "7-byte row" signature 56 B of garbage — cast the index plane to uint8
  first; (b) the cropped refcap has only 440 screen rows, so y>=436 slices are
  EMPTY and `b.find(b'')` hits every file at offset 0 — assert non-empty
  signatures before scanning.

## F4b — THE FIELD HAS MANY INSTANCES, AND INSTANCE == UI-REPAINT STATE
scripts/t433_instance_relation.py + a 49-shot sweep over
work/screens/{t252,t253,t268}/*_game.png (chrome-family-dominated left band
filter), band = screen x0..6 y40..439, identity vs the three refcaps:
- EXACTLY THREE exact instances appear among the 49 shots, and each shot hits
  one of them at 100.0% or is a documented mixture (75.1/78.7/80.7 — see the
  transition shots below):
    I_MAP    (100.0 vs ref-map, 84.6 vs ref-planet, 85.5 vs ref-species):
             t252 baseline/back1/back2/final_escape*/goodbye/preflight/
             species2/species_menu, t253 baseline/esc_to_galaxy, t268
             baseline/esc1/esc2/esc_res/goodbye/neg_ungooma/raceclick/races
    I_WIN    (84.6/100.0/99.1): t252 intel_open, t268 intel/intel_row, t253
             esc1/esc_design/esc_fleet/esc_to_fleet/fleet_open/tab_defenses/
             tab_weapons  (== the ref-planet instance family)
    I_RES    (85.5/99.1/100.0): t252 research_open/res_pan_v/res_pan_v2, t268
             node_discovered/node_empty/node_red/reswin (== ref-species)
  ref-planet vs ref-species agree 99.1% (near-same instance); ref-map vs both
  84.6/85.5. MIXTURES: t253 tab*/design*/reopen/row1_rightclick all land at
  exactly (75.1, 85.5, 85.5) = a FOURTH instance; t253
  fleet_row1_leftclick (80.7/92.7/92.7); t252 sel_orfa + t268 neg_orfa both
  (78.7/65.7/66.2) = a FIFTH instance, identical across two sessions again.
  [verified]
- READ: the instance is a deterministic function of UI/repaint state, NOT of
  the process or the machine — the same UI state reproduces the same instance
  byte-exactly across independent sessions on independent runs, and DIFFERENT
  UI states give different instances. So "painted once per process" (F3 and
  chrome.md F1) is REFINED: repaints happen on window open/close and each
  repaint draws a deterministic instance of the same law.
- LAW EQUALS ACROSS INSTANCES (scripts/t433_instance_relation.py): lag-1 h/v
  0.237..0.259 / 0.398..0.428, vertical run k1 0.588..0.609, k2 0.227..0.239
  for all five instances — one law, different draws. Family-level agreement
  (grey ramp 2..6 / teal ramp 48..58 / dark 0,1,196,200 / accents) map-vs-other
  is 87.2..91.9% while pixel-level is 75.1..85.5%: the disagreements are
  mostly WITHIN-family (teal->teal 180 px, teal->accent 141 px, accent->teal
  72 px out of 431 for map-vs-planet), and 0% of disagreeing px are black —
  real dither-phase differences, not overlay bleed. [verified]
- NOT A SHIFT: vertical shift sweep over dy=-300..300 for all 20 ordered pairs
  raises identity by at most 2.0 points (84.6->86.5 at dy=272), and the
  index-offset test gives no k with B==A+k (top delta is always 0 at the
  identity value, next 4.9%). So the instances are NOT phases of one long
  buffer — a single extracted surface cannot be re-phased to cover them.

## F7 — PROBE 4: THE DISPLAYED PIXELS ARE NOT RESIDENT (scripts/t433_fb_resident_probe.py)
Vacuity gate on F2, plus a pitch sweep. Save 41/42/43.sav (bank-play-20261111):
- game.pal (raw 768 B) IS in both members: Vga 0x845c5, Memory 0x28a6b3
  (phys 0x28a62b) => the members are searchable. [verified]
- 45 signatures of 64 B taken from DISTINCTIVE screen content (2 rows x 32 px
  at six x-anchors across the frame): **0/45 in Vga AND 0/45 in Memory**. So
  the save does not store the displayed frame as packed palette bytes in
  either member; F2's Vga half is therefore NOT vacuous about chrome — the
  framebuffer simply isn't there to hold it. [verified]
- Planar caveat handled: vertical runs >=8 px of one chrome colour (17 such
  runs in the vendor left band) tested at pitch 80 / 160 / 320 / 640 in both
  members. Result 80/Mem 12, 160/Mem 8, 320 0, **640/Mem 183, 640/Vga 158**.
  Pitch controls: 639 -> 0, 641 -> 0, 632 -> 0, 648 -> 0, 1280 -> 17. A
  shuffled-band null control (same value census, pattern destroyed) gives 4.
  So a REAL 640-pitch paletted surface exists in Memory, clustered in a 258 KB
  window around member 0x2f69f9..0x335979 (phys -0x88). [verified]
- BUT IT IS NOT THE CHROME BACKDROP: 60 consecutive 40-byte rows from that
  surface (pitch 640) are found **0/60** in any of the three refcaps, and its
  colour census is 82% black (idx 0) with only 6.2% chrome-family, versus a
  chrome band that is ~100% chrome-family. The 2-row/4-px 640-pitch anchor test
  also gives 0 matches, and sliding a candidate base over all 183 hit offsets x
  7 column hypotheses matches **0** band rows. [verified]
  READ: the 640-pitch surface is some other 640-wide paletted buffer (a window
  or sprite canvas), not the full-screen backdrop. The vertical-run support is
  explained by both fields being dithers of the same palette family; it is NOT
  evidence of a chrome surface.

## F6 — CONSEQUENCE (this iteration's verdict on the t433 route)
0. THE ASSIGNED ROUTE IS ANSWERED WITHOUT A CAPTURE, NEGATIVELY. There is no
   chrome memory surface to extract in the zero-capture corpus (F2 packed-run
   negative, F7 residency + pitch analysis), and the field is not one canonical
   pattern (F4b). A live R1 capture would be a NEW experiment whose object is
   the generator's seed/state, not "the surface" — that is the t433c shape, and
   it is NOT free: R-t422c already killed the static generator hunt, and F4b
   says any capture pins at best the instance for the UI state it happened to
   visit.
1. The chrome field is NOT a single canonical byte pattern (F4b refutes F4's
   strong reading: ref-map == t252 is ONE instance that both processes happen
   to share, not the only instance).
2. It is also not a per-process random field: instance identity is
   reproducible across machines and tied to UI state.
3. It is not stored on disk as contiguous bytes (F5) and no verbatim copy of
   the map instance appears in the save corpus (F2, F7).
=> The generator law (chrome.md SS1.5 Markov fit) remains the port's honest
   ceiling. NOTE the port's law is also now measurably WRONG in kind for the
   repaint case: it draws a fresh splitmix64 field per call, whereas the vendor
   repaints deterministic named instances (F4b). Fixing that needs the vendor
   seed law, which no on-disk artefact supplies.
