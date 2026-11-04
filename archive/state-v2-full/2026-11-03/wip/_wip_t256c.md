# _wip_t256c.md — AI GAP ROW 16 DISPOSITION (per-ship order state) — working log

## S0. Task + plan (written before probing)
Task (STATE.md NEXT ACTION verbatim intent): ai-dossier.md gap-map row 16
(per-ship order kinds {0..5}, stickiness, congregation, retreat-downgrade,
invasion-module carrier — §5, t179 P1/P3) is labelled "GAP (largest)". The
"NOT REPRESENTABLE" note applies (rewrite has no ship positions/system
objects). DECIDE AND BANK the disposition: accept the aggregate model
permanently with cited reasons (correcting the label to a documented
boundary), or scope the minimal per-ship state the cited laws need. No
silent stub either way. Gate + rewrite tests must pass.

Plan (measurement-first per strict-close habit):
1. The corpus banks a per-ship raw window EVERY timeline row: watcher
   ship_raw = per slot 177 u16s at stride 0x162 from runtime ship array
   (scripts/r1_playcap_watch.py:93, law r1_slot.ship_array_law:
   base = B+0x82bb0+0x3a095, count = u32[0x43489]>>16, cap 0x6b slots).
   u16 index = byte offset / 2. Cited fields: +0x54 owner (idx 42),
   +0x58 ORDER KIND (idx 44), +0x59 ORDER TARGET ptr (idx 44.5/45 —
   straddles u16s, read pair), +0x5d ACT enum (idx 46), +0x88 POWER
   (idx 68), +0x94 MOVES (idx 74), gizmo slots stride 7 BYTES = 3.5 u16s
   (stride-7 byte law: volley loop 0x4a5c1, t179 P3; the invasion test
   is slot VALUE == 0x49 == 73 == gizmos.txt row 73 Invasion Module).
2. Tool scripts/r256c_shipstate.py (keeper pattern = r256b: streaming,
   per-session trust, dedup (file, mtime_ns), per-session turn watermark).
   Measure across the FULL corpus:
   (a) KIND VALUE CENSUS: which of {0..5} actually occur in captured play,
       per owner class (player row0 vs AI rows 1..n-1).
   (b) STICKINESS: on consecutive trusted rows, how often a ship whose
       kind ∈ {1,2,5} changes kind next row (law predicts the AI does not
       re-think; player edits possible).
   (c) RETREAT-DOWNGRADE: kind {1,2,3} -> 4 transitions observed count
       (law 0x220f2).
   (d) INVASION-MODULE CARRIER: slots holding gizmo value 0x49 anywhere in
       the stride-7 window (t179 P3A eligibility).
   (e) ACT census + POWER/MOVES nonzero fraction (t179 P1 power tie-break
       input availability).
3. DECIDE: the cited §5/t179 laws are all functions of (kind, target,
   gizmo inventory, position) — position is NOT banked (xyz IS banked in
   "ships", but system-object membership is not directly; kind==4 means
   in-system per §5). The decision options:
   A. ACCEPT aggregate permanently + relabel row 16 a documented boundary,
      reasons cited (OQ-019 BLOCKED-USER is the same boundary: no save-
      observable route contains flight; rewrite fleet_ is transit-only).
   B. SCOPE minimal per-ship state (kind byte + owner + design) — only if
      measurement shows the aggregate fleet_ model misses an OBSERVED law
      that is representable without positions.
   Decision after data.

## S1. MEASURED — first full per-ship ORDER-STATE census (scripts/r256c_shipstate.py, RC=0)
Corpus: 62,762 unique trusted rows with ship_raw / 25 sessions / turns
240..1335 (256 rows lacked ship_raw = early title-class). Single-pass stream
(file is append-ordered; buffering decoded rows would cost >1.5 GB RSS).

KIND CENSUS (slot observations; owner class from +0x54>>16, DEAD = 0xffff):
  AI:      kind1 98,001 | kind3 2 | kind4 284,917 | kind5 588,532 | kind2 ZERO
  PLAYER:  kind1 33,265 | kind2 15,239 | kind3 246,835 | kind4 115,277 | kind5 426,902
  DEAD:    kind0 94,573 only.
=> LIVE kind value set is {1..5} exactly; kind 0 occurs ONLY on dead slots
   (consistent with the command-clear writer imm0 0x24a00 pairing WORD+0x56
   :=0xffff). AI never holds kind 2 in 25 sessions (kind 2 = the second move
   issuer 0x3ca60 — apparently a player-command path).

TRANSITIONS (consecutive trusted rows, owner-equal slot pairs):
  kind_changes_total = 1,938 over ~1.8M slot-pair obs (0.107%).
  AI 4->5: 416 and AI 5->4: 416 — EXACTLY symmetric: the travel/arrival pair
  (kind5 jittered in-transit -> kind4 on arrival, travel issuer 0x220a8,
  consumer 0x21f58) measured live, first time, in self-play.
  retreat-downgrade (1|2|3 -> 4, law 0x220f2): 143 OBSERVED (e.g. t346 slot0
  owner3 3->4; t399 slot4 owner2 1->4) — the retreat-to-system law is ALIVE
  in captured play, both owners.
  sticky_kept = 1,160,582 (kind ∈ {1,2,5} unchanged next row). CAVEAT banked:
  the parked-at-t1255 ring samples the same state every 10 s, so this number
  cannot separate "sticky law" from "no turn advanced"; the 1,938-change rate
  is consistent with §5 stickiness but is NOT an independent proof of it.

ACT CENSUS: AI act=1 873,404 / act=0 98,031 / act=2 17; PLAYER act=1 456,768 /
act=0 376,824 / act=3 3,638 / act=7 288. POWER nonzero 1,755,965/1,808,970,
MOVES nonzero 1,797,070 — the t179 P1 power tie-break inputs are banked and
populated for every live ship.

INVASION-MODULE CARRIER (t179 P3A): gizmo ring rebuilt from the u16 window
(bytes at 0xab + 7i, count dword +0x15a); type 0x49 present in 480 DISTINCT
ships across the corpus (1,707,051 slot-obs). The invasion-carrier eligibility
state is observable in RAM — it is only the rewrite's lack of a ship model
that makes the law unwireable.

## S2. DISPOSITION (decision, rationale in ai-dossier S11 + row 16 rewrite)
ACCEPT THE AGGREGATE MODEL PERMANENTLY as a documented boundary; relabel row
16 from "GAP (largest)" to BOUNDARY (accepted t256c). Rationale (a)-(d) in
the dossier. NO rewrite code change; NO OQ closed (strict-close); OQ-019 row
ANNOTATED with the census, stays OPEN.

## S3. LANDING RECORD + TOOL PITFALLS
- ai-dossier.md: row 16 rewritten (GAP->BOUNDARY, census inline), priority-
  read paragraph updated, S11 NEW (decision + caveats + ledger effect).
- OPEN-QUESTIONS.md: OQ-019 row STATUS t256c appended, stays "| open |".
- rewrite/src/game/campaign.h ShipInTransit: boundary comment only (the
  "no silent stub" requirement — the boundary is named AT the code site a
  future builder hits). No semantic delta; 137 tests 0 fail after change.
- r256c_shipstate.py pitfalls (keeper notes are in its docstring too):
  (1) ship_raw sits at line offset ~3200 (before relation ~28800) — locate
  by find() + bracket-depth match, head/tail slices miss it; (2) the gizmo
  ring is BYTE-odd (0xab + 7i) so bytes must be rebuilt from the u16 window
  via struct.pack("<177H", ...) before indexing; (3) owner class split must
  treat 0xffff/0xffffffff as DEAD first or kind-0 garbage pollutes AI stats;
  (4) SINGLE-PASS mandatory: the two-pass version buffering decoded rows
  would exceed RAM on the 7.35 GB corpus (t251 law) — the timeline is
  append-ordered so session-split + watermark work streaming.
- Verification: gate exit 0 (ran once, covers build+tests+ledger stages);
  gate_tests.log 137 tests 0 failed; ledger_audit LEDGER AUDIT OK rows=19
  open=OQ-005/016/019/021 closed=15; ledger_index_check LEDGER INDEX OK.

