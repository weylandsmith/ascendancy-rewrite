# _wip t360 — PER-SHIP SAVE PARSER (read-side)

## S0 Pre-flight
- Sitting check: 400 KB tail-seek of work/r1/playcap/live-timeline.jsonl
  (8,890,184,654 B), 16 records parsed, max turn == 1086 == pinned value since
  t310s. NO new sitting -> r1_t85g_sitting.py NOT run; t360 proceeds VERBATIM.
- Assignment: rewrite/src/formats/ ShipRecord structs + parser for RESUME.GAM
  ship regions per pership-spec.md §6; round-trip tests vs banked frames +
  ring .sav; census invariants (62,762-row base, owner/race law t273, kind
  {1..5} live). Read-side only, no behavior change.
- Corpus: work/r1/playcap/save/41..50.sav present; bank-t1086* to be located.

## S1 Proven reader facts (r1_slot.py / r256c_shipstate.py, cited)
- ZIP 'Memory' member == full guest RAM (17,055,880 B for memsize=16); base B
  via unanimous high-entropy anchor vote (r1_sav_scan.build_anchors/
  find_base, min_votes=5; anchors = zero-free >40-distinct 128-B windows at
  16 KiB stride of work/ascend_payload.bin; cached work/r1/.anch-cache.json).
- Member address law: data offset X lives at member offset B + 0x82bb0 + X.
- Ship array: member offset B+0x82bb0+0x3a095, stride 0x162, count word
  u32[B+0x82bb0+0x43489]>>16, cap 0x6b (pership-spec A1).
- Dead-row marker (r256c oc_of): owner-handle (u32@+0x54)>>16 == 0xffff.
- Turn gate before trusting a slot: u32[B+0x82bb0+0x12e10] in 1..4000.

## S2 SAVE-SIDE CENSUS MEASURED (scripts/r360_save_shipcensus.py + follow-ups,
   production ring work/r1/playcap/save/41..60.sav, turn 1086, 20/20 slots
   base-verified, ZERO rejects) [MEASURED 2026-11-09]
- B == 0x1bf4d8 on 20/20 saves (independent re-derivation via the anchor vote;
  agrees with the t333 banked needle value).
- Whole 0x6b-slot record window byte-identical across the ring:
  md5 54bea6e3e9cd66236dd3ff0d6ba34738 (the ring holds one static turn state —
  autosaves inside turn 1086 do not mutate the ship array).
- Count word == 30 on 20/20, but LIVE records number 30 per save across
  indices 1..33: 26 live within 0..29 plus 4 live at indices >= 30
  (beyond_count_word=80/20). CONFIRMS ships.md item 3 (count word is NOT the
  fleet census; pickers must scan past 30). Parser therefore scans the full
  0..0x6b window and treats the marker as dead, count word kept as data.
- Full-window live rows 600 / dead-marker rows 1540.
  attr law (u32@+0x54)>>16 == byte@+0x56: 600/600 on live rows (t273 law
  re-confirmed save-side). Dead marker: u32@+0x54 == 0xffff0000 (low u16 0,
  race byte 0xff), uniform (kind,cap,filled) == (0,5,0) on 1540/1540.
- Live kind census {3:80, 4:60, 5:460} (subset of {1..5} ✓ A4; kind 0 only on
  dead rows ✓). Owners {0:280, 1:140, 2:180}. Caps {10:500, 15:20, 25:80}
  (subset of ships.md §18 caps {10,15,25} ✓).
- FILLED LAW — CORRECTION TO THE INCLUSIVE READING (measured):
  filled(+0x15e) == count(cidx!=0xFF over slots 0..cap-1 EXCLUSIVE) on
  600/600 live rows here. The ships.md §18 INCLUSIVE law and this are the same
  fact seen through the phantom byte: the 25-slot ring (0xab..0x15a, stride 7)
  ENDS exactly where the cap u32 @+0x15a begins, so a stride-7 probe at slot
  index == cap on a cap==25 row reads the cap dword's LOW BYTE (== 25, never
  0xFF) — a self-read artifact, always +1. On cap<25 rows index==cap is a real
  ring slot (occupied on the 100 ships.md phantom rows; unoccupied on all 500
  cap-10 rows here). Law as the parser models it: store cap+filled verbatim,
  compute occ_excl (0..min(cap,25)-1) and occ_incl; corpus pin asserts
  filled==occ_excl 600/600 and occ_incl==occ_excl+1 exactly on the 80 cap==25
  rows (the artifact), never calling the probe at idx==cap inventory.
- Per-save PIN census (identical 20/20, scripts follow-up probe):
  (count 30, live_in_window 30, dead_in_window 77, live_beyond_count 4,
   kinds {3:4,4:3,5:23}, owners {0:14,1:7,2:9}, caps {10:25,15:1,25:4}).
  NB kinds/owners/caps are the FULL-WINDOW (0..0x6a) live split per save
  (sums to 30); totals across 20 saves {3:80,4:60,5:460}/{0:280,1:140,2:180}.

## S4 PORT TRAP + BUILD RESULT (MEASURED 2026-11-09)
- r1_sav_scan.build_anchors zero law is `w.strip(b"\x00") == w` — Python
  strip() trims END bytes ONLY, so windows with MIDDLE zeros pass (12 anchors
  on ascend_payload.bin). A literal "zero-free anywhere + early break" port
  yields 0 anchors and every findImageBase call fails 0<5. Fixed port checks
  w[0]/w[127] only. (Cost 3 debug rounds; porting Python byte-predicates to
  C++ needs the Python semantics, not the prose gloss.)
- Code landed: rewrite/src/formats/shipsave.{h,cpp} (ShipSave: ZIP EOCD ->
  central dir -> Memory member raw-inflate via zlib; anchor-vote findImageBase;
  countWord/turnCounter; parseShipRecords full-window 0x6b stride 0x162 with
  cited +0x00..+0x15e fields, dead rows flagged not skipped, ring cidx x25).
  ascend_core now links ZLIB::ZLIB (find_package(ZLIB REQUIRED)).
- tests/test_shipsave_t360.cpp x3 cases:
  (1) reader+base vote: inflate determinism, 17,055,880 B member, base found
      20/20, NEGATIVE controls (zero-filled member -> no vote; 4 KiB stub ->
      window-past-end refused not clamped).
  (2) corpus law pins (durable, any in-game corpus): dead marker == 0xffff0000
      with (kind,cap,filled)==(0,5,0); live kind in 1..5; cap<=25 ring-span
      law; attr law (handle>>16==race byte) corpus-wide.
  (3) frozen-ring EXACT pin (self-skips once turn != 1086): B==0x1bf4d8,
      count 30, live 30 (4 beyond count word), dead 77, kinds {3:4,4:3,5:23},
      owners {0:14,1:7,2:9}, caps {10:25,15:1,25:4}, filled==occupiedExclusive
      all live rows, cap==25 probe-at-index-cap reads cap low byte (artifact),
      window FNV-1a64 == 0x3acb4b625a289f54 (Python cross-checked).
- run_tests: 179 tests, 0 failed (176 -> +3). No behavior change to the engine.

## S5 Ledger disposition
- NO OQ row closes this iteration (strict-close; parser artifacts + save-side
  law re-confirmations are not a row's named closer). OQ-019 annotation stays
  as-is (per-ship model exists in rewrite now on the READ side; row still
  user-gated per t329). The filled-law inclusive-vs-exclusive DISPUTED row in
  pership-spec.md §1/+0x15e gets the artifact resolution noted (S2 above):
  ships.md §18 stays the durable law; the exclusive reading here is explained
  by the cap-dword self-read, no contradiction remains.
## S3 Build plan (superseded by S4; kept for the record)
- rewrite/src/formats/shipsave.{h,cpp}: ShipRecord (cited §1 fields only,
  UNKNOWN gaps NOT modelled), shipArrayLaw(), parseShipRecords() full-window,
  readMemoryMember() minimal ZIP central-dir + zlib raw inflate (zlib1g-dev
  installed; ascend_core links ZLIB), findImageBase() anchor-vote port.
- tests/test_shipsave_t360.cpp: skip-clean when work/ absent (test_audio.cpp
  pattern); asserts per-save pin census + attr law + filled law + determinism
  + window FNV-1a pin (pinned constant cross-checked Python<->C++).
