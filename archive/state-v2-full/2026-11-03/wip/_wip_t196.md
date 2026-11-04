# _wip_t196 — residue triage via vision oracle (OQ-005 forward motion)

## Trigger triage
- live-timeline.jsonl size 5,721,578,066 == t194 re-frozen BASE_SIZE; HEAD=t195
  commit, tree clean. NO new sitting -> assigned task t196 stands.

## S0. R13 STATUS CHANGE [verified this session]
vision_analyze WORKS on this deployment now (measured: CONTROL--17np--rec0
render identified as "blank UI panel, beveled frame, top row of 5 cells +
large body, not garbage"). The R13 entry (t55, "image input is not supported",
measured 2026-10-11) is STALE. Per the t193 vision-oracle law this licenses
identification-by-context on our own renders; grading codec CORRECTNESS stays
R13-reserved (only the player's eyeball closes OQ-005).

## S1. Structural reclassification of the 71 residues [verified, corpus census]
Probe: capacity walk (S9 grammar, declared W, stop at span end) over every FAIL
record; JSON snapshot work/r1/shp_png/_t196_probe.json.
  - EMPTY (stream_start >= span end, zero pixel bytes): 26 records —
    1starmap k1, destroy k14, expl00 k9, expl01 k8/k9, expl03 k0/k9,
    expl04 k0/k9, expl05 k9, expl07 k0, expl08 k0/k9, orbex00 k8/k9,
    sg37/45/47/49expl k0+k9, sg66expl k0/k9, sg70expl k9.
    All carry the S3 variant header dims 0x7FFFFFFB/BB (u16-pair reading
    (-69,-1)/( -69,-69)); the 8-byte k0 variants span=8 = header only.
    These are DIRECTIONAL/EMPTY animation slots (9-frame expl/sg*expl ladders
    truncated at the last frame; k0 variant = whole lib first-frame empty).
    Nothing to render. Candidate close-as-empty-slot class (player ruling).
  - TINY (1..8 stream bytes): 13 records — cos_star k40..k51 (span 0x1b each,
    dims word 0), sg50expl k9 (span 0x18). Same story one notch larger:
    near-empty slots. cos_star rec0 dims=2x2 [verified] -> the 2x2-class star
    pips plausibly degenerate here; cos_star k1..k39 pass with A law.
  - ART (real streams, walk completes PART of the frame): 32 records —
    planind k0..k12 (13), 3cfgnew k0..k12 (13), 1starmap k3/k4/k6,
    14intel k8, mouse k6/k7.
    [verified] rows_done at declared W within span: planind 77..95 of 99
    (78-96%, monotonically non-decreasing over the ladder!);
    3cfgnew EXACTLY 55 rows of 79/80 for all 13 records (69%);
    1starmap k6 27/28 (96%), k3 18/22, k4 18/23; 14intel k8 13/18;
    mouse k6 47 rows at W=77 (declared H=0 -> dims word broken, stream real),
    mouse k7 avail 0x7f6 too (dims 0x0,0x0).
  => The dims-location question now has a MEASURED shape: for every ART
     residue the span holds a prefix of the declared frame (60-96%), consistent
     with delta-frame/partial-paint storage, INCONSISTENT with "dims live at
     another offset" (no alternative dims reading is needed to walk the prefix).
     Cross-class witness [verified]: planres.shp and planpro.shp have the SAME
     structure (count=21, dims 107x99, same header law) and pass 21/21; only
     planind (the manufacturing gauge per player ID) is partial. So partiality
     is per-LIBRARY vendor data, not a header-form difference.

## S2. Library facts (census, this session) [verified]
planind 21 recs FAIL13+A8 | planres 21 V1+A20 | planpro 21 V1+A20 |
planitem 40 recs all pass, 9 unique dims, dims0=33x33 | 3cfgnew.shp 13 FAIL
(the .tmp head passes V 639x479) | cos_star 55 = V1+A42+FAIL12, 5 uniq dims,
rec0 2x2 | mouse 12 = V1+A9+FAIL2 | 14intel 10 = V1+A8+FAIL1 | 1starmap.shp
68 = V1+A63+FAIL4 | planets.shp 55 all pass (dims0 11x11, 13 uniq) |
planal00.shp 5 all pass (47x47).

## S3. Render plan
- Permissive dumper tools/shp_partialdump.cpp: same ShapeLibrary load + S9
  row-walk semantics, but row loop STOPS at span exhaustion instead of failing;
  reports rows_done; plane is width x rows_done (rest of declared H left as
  index-0 underlay by the compositor). NO candidate search (R2 respected).
- Sheets (labeled tiles, class-grouped) + a gauge-LADDER sheet from the
  all-pass libs planres/planpro/planind-visible-8 (ladder order = record index)
  for the level->record question. planitem sampled every 4th (33x33 item art).
- vision_analyze per sheet: "what game-screen does each tile belong to" +
  verbatim text + style-cluster flag vs 10status/2savegam/4loadgam.

## Log
- vision oracle probe: 17np rec0 = blank panel frame + 5-cell header strip.

## S4. Post-sheet measurements (all banked to shp.md S20)
- Vision identifications: sheet1 planind=factory ladder growth CONFIRMED,
  3cfgnew=new-game/race-config art (dot-wheels, shields, orbs); sheet3
  planres/planpro ladders k0->k20 MONOTONIC, index=plausible level, no
  repeats; sheet4 planitem=distinct item icons (not anim), planets=biome
  spheres, planal00=cratered SURFACE crops -> pose-set hypothesis KILLED;
  sheet2 (retry after a 500 blip) 14intel mood faces, 1starmap star-map
  sprites w/ verbatim "NEXT TURN <ENTER>", mouse cursors + "Exit <ESC>".
- VISION PITFALL: misread label digits (claimed rows=7-9 vs real 77-95).
  Numbers come from triage_report.txt, never the vision transcript.
- UNBOUNDED WALK (no span bound, canonical dims): EXACT-H for planind
  k0-12 (13), 3cfgnew k0-11 (12), 14intel k8, 1starmap k3/k4/k6 = 29/71
  records are FULL FRAMES under the closed dims law. 3cfgnew k12 dies at
  FILE EOF mid-row-55 (genuinely truncated vendor data). mouse k6/k7 have
  no valid dims word (H=0 / W=0).
- Paint-profile discriminator (painted px per row, head vs tail):
  14intel k8 + 1starmap k3/4/6 tail mean = 0.0 (trailing rows pure
  transparent skips -> in-game draw visually complete); planind tail rows
  desync into next-record header bytes painting ground-colour fill stripes
  (row 95 = bytes of the NEXT header 6b 00.. -> single full-width run);
  3cfgnew tails paint at ~head rate (next record is same-style art, so the
  desync is invisible-ish at tile scale).
- BLIT CODE WITNESS (static, S12): FUN_0005caac has NO stream-length arg and
  NO overrun error code (-1 dims/-2 empty clip/-3 outside only); cache =
  verbatim whole-library copy (S10/S12) => the [rec,nxt) walk bound in
  r1_shp_unifiedlaw.py + rewrite decode() is OUR artifact. Precedent: t182
  off-by-8 false-FAIL set.
- HONEST REMAINDER for dims-location: 16 records with non-drawable dims words
  (cos_star k40..k51 dims 0, mouse k6/k7, 1starmap k1, sg50expl k9) + the
  26 EMPTY zero-stream slots + 3cfgnew k12 EOF-truncation. Whether these are
  "never-selected slots" (blit -1 path) or broken data = paint-routine
  census / player ruling, NOT more file probing.
- Decision left for NEXT: validator X-tag promotion + rewrite decode() bound
  decision (29 records) queued as its own iteration; the paint-routine item
  keeps its queue slot because it also decides the cos_star/mouse residue,
  the level->record compression law, and the population-slot library ID.
