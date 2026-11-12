# t382 WIP — PLAYTEST BOOT (read-only observer)

## Input-format adjudication (probes 1-9, 2026-11-12) — DECIDED: BOTH paths
1. dosbox-x savestate ZIP (ring shape): existing ShipSave reader (t360/t366)
   full path (anchor vote, member offsets).
2. native raw .SAV (work/r1/game/01..04.SAV): **POSITIVE — the ship array IS
   in the raw .SAV, marker-prefixed.** (An earlier 64-B needle at record
   +0x52 MISSED because that window holds guest-POINTER fields which the save
   writer rewrites/zeroes — pointer-window needles are BLIND; name-window
   needles at record +0x34 hit. Correction banked.)
   MEASURED LAWS (04.SAV day 1254 vs ring 60.sav t1254 RAM, same world; and
   02.SAV day 1253):
   - day = u32@0 (4/4: 1086/1253/887/1254).
   - SHIP BLOCK: record N at file home H0 + N*0x166 (STRIDE 0x166 = 0x162
     record + 4-byte u32 marker PREPENDED per record; marker before record N
     at home-4 reads N exactly — markers 0..40 clean walk, terminator = first
     home where marker != index (observed 4 at the post-block position)).
     H0(04.SAV)=H0(02.SAV)=0xd6e1 (same world; cross-world NOT verified —
     discovery must be content-based: find p with u32@p==1 && u32@(p+0x166)
     ==2 && u32@(p+2*0x166)==3, then H0 = p-0x162).
     VERBATIM PROOF: slot-0 WHOLE record (0x162 B) byte-identical save-side
     vs RAM (ring 60); slot-2 differs ONLY at fields that legitimately drift
     between the save instant and the later ring capture (+0x50, +0x58..0x64
     order-target pointer region, +0x78..0x84, +0x88 power, +0x90, +0x9e pos)
     — layout law proven, drift is state, not format.
   - STAR BLOCK: stride 0x60 (the K8 star-slot table 0x13bc5 shape),
     home(04)=home(02)=0x1e2a; 47/50 records byte-verbatim vs ring 60 RAM,
     the 3 diffs are single BYTES at +0x14/+0x15 (owner byte — drift between
     save instant and capture, same class as above). Names CP437 at +0x1c
     ('Vega'…'Trovaricon', 50/50 key to the RAM table); coords f32 triple
     +0x08 (star0 359.5/246.45/-60.19 exact).
   - OWNER byte (+0x14 star / +0x56 ship) verbatim in both blocks.
3. FRAME BRIDGE = NAMED RESIDUE (honest negative): ship pos triples live in a
   32-aligned world frame (extents ~±2300; t380 quantizer law); star-record
   triples are NOT 32-aligned and span ~±430. NO scale factor unifies them:
   scan of scales 3.5..8.0 (mean nearest-star distance of 19 kind-4 ships)
   bottoms out ~630 world-units at 5.0-6.0 with no snap (intra-system scatter
   is ~100-500); the f32 -1560.0 (placement-anchor candidate for the
   GUANDAGNINI (1280,-1760,1344) magnetron landing per ships.md S19 T3
   star+(0,-200,0)+rng%200) appears ZERO times in the whole 60.sav member.
   Observer therefore renders the two frames as SEPARATE labelled maps and
   claims no projection between them.
4. kind-4 +0x59 deref (ZIP path): member = phys+0x88 lands EXACTLY on the
   star-slot record (Atropos: 0x255c85+0x88 = 0x255d0d = slot member) — name
   read +0x1c..; 19/19 kind-4 ships attribute to a named star slot
   (Atropos 10, Vernunft 4, Feculon 2, Unterwelt/Pulveran/Sirverei 1 each).
   Raw path cannot deref (pointer space absent) — roster line omits target.

## STAR-BLOCK + BLOCK LAW FINAL (probes 10-14)
- Star block: stride 0x60, home 0x1e2a in ALL FOUR raw saves (Vega name hit
  0x1e46 = home+0x1c in 01.SAV too). Count by structural walk (name printable
  at +0x1c, K u32@+0x00 <= 12, coords sane) = 50 on the corpus world.
- Ship block: marker chain walk = PACKED LIST OF LIVE RECORDS, marker u32 at
  record-4 = RAM slot id, strictly ascending, terminator = first violation
  (marker > 0x6a or <= previous). VALIDATED: 01.SAV block markers == the live
  set of bank-t1086-preplay RAM (30 == 30 EXACT SET EQUALITY). Block start
  SHIFTS between saves (01 rec0=0xd6e1 chain-from-marker-1; corpus saves
  0xd6e1) — discovery MUST be content-based (scan for marker chain), never a
  hard-coded offset.
- VERBATIM GRADE: lane-run map of 04.SAV slot2 vs same-world ring-60 RAM =
  big MATCH runs (0x008..0x050, 0x0ac..0x0e0, 0x0f4..0x160) with diffs confined
  to the pointer field region +0x58..0x68 (save-writer pointer rewrite class,
  t298) and legitimate state drift (+0x88 power, +0x9e pos). Name (+0x34),
  coords-in-record, owner (+0x56) all inside MATCH runs. Whole-record equality
  against a DIFFERENT-day RAM is NOT expected and was NOT claimed.

## Star-record law for the map (cited, planets-ui.md §1 + r1_t246)
- runtime entry = B + 0x82bb0 + 0x13bc5 + i*0x60, count u16 at img 0x16145
  (r1_t246_header_law.py; planets-ui.md §1 "static base 0x13bc5, stride 0x60").
- coords at record +0x08/+0x0c/+0x10 (planets-ui.md §1: "The star record
  matches ships.md S11 (coords +0x08/+0x0c/+0x10, stride 0x60, +0x59 owner
  ptr)"). [live shape check pending this session]
- ship dots: Record::pos (+0x9e, 3 f32) via the t360 parser (already lands).

## Design (lands this session)
- src/game/observer.{h,cpp} (ascend_core, no SDL): pure functions over the
  parsed member image -> SaveBoot { day, stars[(x,z)], ships[(x,z,owner,slot)] }
  + text-map projection (grid, stars letters/digits by type, ships '+',
  luminance-safe: distinct glyphs not colours).
- main.cpp: --save FILE branch BEFORE archive load (media-smoke position,
  like --flic); ZIP magic PK\x03\x04 -> full path; else raw .SAV -> day+refusal.
  Zero write-back (read-only OBSERVER; serializeRecord NOT called).
- pins test_saveboot_t382.cpp on ring 60.sav (t1254) + 41.sav witness values,
  REQUIRE_DATA-gated; raw .SAV day law pinned if game-dir present.
- mutation campaign per mutation-campaign skill (checkpoint first).
