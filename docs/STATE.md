# STATE — machine-readable working memory for the closeout loop (v2)
# Update EVERY turn. A fresh session must be able to resume from THIS file alone.
# v1 history (full turn log 2026-10-03..2026-10-05l): archive/ralph-v1/STATE.md
# Patch discipline inherited: ONE patch per region, read_file verify after
# (multi-patch batches mangled v1 twice).

phase: P7-closeout
milestone: 6  # keep 6: gate.sh keys build/test/boot stages off milestone >= 3; lowering it silently guts the gate
updated: 2026-10-28T05:35
policy: strict-close  # FINAL-DEFAULT never closes an OQ; only cited measurement does (docs/GOAL.txt)

## LEDGER (statuses mirror docs/OPEN-QUESTIONS.md; that file is the record of
## resolution evidence — this block is the fast index. Update BOTH or neither.
## t157 LESSON: hand-mirroring drifted 6 rows (5 closed rows still listed open,
## OQ-023 missing) and nothing caught it — at t157 gate.sh ran NEITHER ledger
## check, and ledger_audit only checked the record against its own --expect
## list (both statements pre-t158; see the t158 note below for current state).
## RE-DERIVE, don't hand-maintain: python3 scripts/ledger_index_check.py prints
## the true open set from the record and diffs this block against it. AS OF
## t158 gate.sh stage 3t RUNS that check plus ledger_audit on every gate, so
## this block cannot drift out green anymore.)
ledger:
  closed:
    - "OQ-001 .cob offsets = N not N+1"
    - "OQ-002 FLIC codec (both vendor videos, golden-pinned)"
    - "OQ-022 music span-vs-check contradiction CLOSED 2026-10-07 t8 — player
      FUN_00059c70's 0x1d4d0 span check never sees theme00 (guard @0x59984
      precedes the checked call; DS:0xa200c all-zeros 10/10 saves,
      DAT_00010ba0==0); engine INACTIVE in captured states, audio.md §3.4,
      no rewrite dependency; menu-music server explicitly unmapped (non-claim
      banked)"
    - "OQ-024 planet GOVERNOR assignment law CLOSED t45 — @0x38df0 branch of
      FUN_00038ba4 pinned verbatim (item 33 -> PROS+=IND>>2, item 34 ->
      RES+=IND>>2); [0x743b9]>>0x18 == item-table UPOP(35), 32/32 saves;
      writer census r1_0x54_writer_sweep.py, activator @0x38b26 sole trigger,
      0/2810 corpus records hold 33/34/35; rewrite PlanetState::governor +
      storedProsFor/storedResFor (campaign.cpp/.h), pin
      campaign_governor_law_t45"
    - "OQ-007 text encodings CP437"
    - "OQ-008 loader model usable for control flow (imagebase 0)"
    - "OQ-009 AI data side (21 raceNN.dip parameter sets)"
    - "OQ-011 POINTER LAW: runtime_u32 = P0 + payload_file_offset(target); P0 = B - H per-run; guest linear == physical; obj0 code [0x14bb0,0x82bb0)@0x1d4000, obj1 data [0x82bb0,0x8cc83)@0x242000 (battery scripts/r1_pointer_law.py 12/12 slots, gate 3q)"
    - "OQ-017 vendor .fnt codec + wired into UI"
    - "OQ-013 RESTREE LIVE TABLE LAW: in play = 66 main rows only (loader
      FUN_00046870 row loop bounded by count line 66; variants 0/40 in 27 slots
      x 13 captures); record = stride 75 (count u16@+0, name 60B@+2 ^->space,
      runtime cost u16@+62, prereq bytes@+64 (0FF term, <=5), child slots@+69..72
      (second pass, 66/66 exact), field0 u8@+76); MEASURED COST LAW runtime =
      file_cost x (2row-20) for row>10 clamp 65000 (instructions 0x4691d..0x46a15,
      reproduced 66/66; row65 300->33000); resume.gam block byte-identical to
      fresh RAM (static data); rewrite upgraded (Tech::runtimeCost,
      includeVariants default false) + 2 pinned tests; docs/re/research.md 6"
    - "OQ-014 PLANITEM LAWS: loader FUN_00037fc0 + checker FUN_0003830c +
      init FUN_00037d80 (restored image; strings verified payload
      0x8488d..0x848d6); record stride 0x28 IND@0 RES@+1 PROS@+2 MPOP@+3
      UPOP@+4 REQUIRES@+5 FLAGS u16@+6 COST u16@+8 name30@+10, 39/39
      byte-exact vs file (2 captures, table phys 0x2b5f50). REQUIRES law:
      avail iff req==0xFF || (req<66 && owned) -> 254 DEAD (rewrite
      requiresAvailable, gatedBy deleted). Count triple: 22=SURFACE
      (RAM 0x73e3c==22 4/4) XOR placement law idx<=30 specials-exempt;
      9=ORBITAL rows 22..30. Grid C row sums = size-class surface cells
      {7,11,23,45,73}: live +0x18 2650/2650 x 17 captures, cap==cells+10
      zero violations. MPOP=upkeep-demolition, UPOP=start-gate. FLAG bits
      consumer-mapped (bit4 set by no shipped row, bit7 no consumer); RAM
      census == file 39/39. Spec docs/re/economy.md §4; 3 pin tests (89
      tests 0 fail); gate green incl seed-2024 Control t145. Per-cell
      terrain/nuke laws documented, rewrite wiring PARKED (no cell model)"
    - "OQ-004 TABLE LOADING + .COB GRAMMAR: pool-relative immediate law (imm =
      str_off-0x82BB0 -> relocated P0+str_off; 337 RAM-verified sites; census
      docs/re/datafiles.md — every pool name has a referrer, refuting 06r .shp
      false-zero); ascend02 .bin/.tsv opened via RAM name table @0x250c1c
      (3/3 captures) from .cob TOC, zero exe literals; .cob = u32 N + N x 50B
      names + N x u32 blob offsets, ascend00 54/54 md5 round-trip; gate
      scripts/cob_probe.py (3i2); NO rewrite delta — rewrite reads the
      extracted dir directly, nothing TOC-side to upgrade (datafiles.md S5)"
    - "OQ-018 soundfx.txt header pairs, VOC u16@25, theme selection mapping
      — CLOSED 2026-10-07 (STATE index was stale, moved 2026-10-08 t28):
      header pairs = voices/size-band law (voiceBand() +
      test_audio_voice_band_law_oq018, 327/328 spans == disk sizes); VOC
      field map 15/15 (u16@25==0x0911 constant, audio.md §2.1, voc.cpp
      pins); race->theme map REFUTED (DAT_00010ba0 single writer 0x21309)"
    - "OQ-010 combat application law CLOSED t89 (static law S2d..S2h
      instruction-verified t85g..t88a + rewrite UPGRADE S2j): firing order =
      stored gizmo-slot order every cat-0 engages (0x4a5c1); damage =
      design[+0x52] guns / [+0x4a] specials, NO hit roll (measured-negative);
      two-layer clamped absorb shield-then-hull + death 0x49d2c; commit law
      mode==1 only 0x25560/0x25570. Code sites: rewrite/src/game/
      campaign.cpp attackScore (volley = SUM researched cat-0 Levels,
      replaces MAX), defenseScore (hull layer only), combatPhase (noise draws
      REMOVED per cited determinism; capture iff volley - MIN(volley,
      shieldChargesFor) > hull), shieldChargesFor/setAllTechs + campaign.h
      absorbSplit; pin TEST(campaign_combat_law_oq010) (file sums 49/16,
      volley delta 49 full-vs-none tech, split edges, determinism). 109 tests
      0 failed; timelines regenerated: 2024 Control t777 / 42 Extinct t581 /
      13 Extinct t503 / 1 Control t842 / 2 Control t677, all FINITE <1200;
      PLAYTHROUGH.md regenerated. AGGREGATE model caveats S2i (no per-ship
      slots/same-system/range gates; per-ship = OQ-019)"
    - "OQ-006 headerless sample rate CLOSED 2026-10-07: DEVICE rate = 22050
      MEASURED — open chain PUSH 0x5622 @0x4f690/@0x4f90b -> CALL 0x68816 ->
      unique edge 0x68882 -> rate setter 0x6e000 stores [obj+0x3c]; constructor
      default 11025 @0x6df3e always overwritten; audio.md 3.1; pin
      audio_open_rate_measured_oq006 (channels: no vendor field, mono by
      convention)"
    - "OQ-012 mapgen CLOSED t78: (a) size options measured 2026-10-12 (density
      cycle 50/75/100/15/25, wraps; rewrite --stars knob), (b) closed 06o (pps
      U{1..5}), (c) closed 06p/06q (shell position law; rewrite upgraded +
      tested), (d) closed 06k (sphere extent, refined by (c))"
    - "OQ-015 DA_ template selection order + full %token table CLOSED
      2026-10-08 (t12-t14): chooser FUN_00044a44 return == ACTIONS pool idx;
      DIPVALUES field map via FUN_00044290; trade gates/cadence rekeyed into
      OQ-023 as BUILD work (law in hand, engine unwired); %token census 22/22
      files == {%m,%y,%s,%t}; pins dip_action_chooser_law_oq015_t12 +
      dip_strict_threshold_oq015_t13 + dip_trade_predicate_bytes_oq015_t14"
    - "OQ-020 ability charge days CLOSED t100: cadence word
      WORD[0x6780+2*ability] (live 60.sav == FILE 0x89330, zero writers;
      5:60 6:100 7:62 8:77 9:90 10:150 11:70 12:63 13:66 14:72 16:92 17:100
      19:89 20:68, zeros == passive set) wired as kCad[21] in species.cpp
      abilityChargeTurns + abilityPhase COUNT-UP law; pins + verify tool
      r1_t100_cad_verify.py both legs"
    - "OQ-025 mapgen non-default-density POSITION law CLOSED t79: shell radii
      fixed at every size, populations = halving law (T//2+1 then halve);
      reproduces the T=50 battery table exactly; rewrite shellRadiiFor()
      replaces the wrong i%50 wrap; ladder test extended"
  open:
    - "OQ-003 .gam full record map — joint with OQ-010 (planet records joined
      151/151 @ stride 123; STAR TABLE + ORBIT laws closed 2026-10-06 give the
      neighbourhood map: star stride 96, planet ptrs name+0x2A, orbit pair
      planet-name+0x57/+0x5f; field semantics open)"
    - "OQ-005 .shp pixel codec — static route exhausted (6 angles,
      docs/REFUTED-ROUTES.md); needs exe shape loader via live image"
    - "OQ-016 campaign per-turn constants — scope NARROWED t29: income,
      growth, cadence, build order, AI SELECTOR LAW (S9) and POP-CAP SEED LAW
      (S10) closed (income-law.md S6..S10). STILL OPEN: per-cell
      terrain/nuke wiring, home-placement verification, +2 residual minutiae
      (0.4% samples), scenario-template preset source"
    - "OQ-019 ship design model (hull+gizmo inventory, cost hack, Orbital
      Docks); per-ship combat application = OQ-010 aggregate caveats S2i"
    - "OQ-021 end-ctrl threshold: comment 'over half' vs prose 'two-thirds' —
      t73 dark-zone hit: score strings at 0x2807b/0x280e7 (pool-rel), score law
      TRUNC(100*DAT_482fb/T), presenter eventwnd.cpp 0x2c03a cluster;
      comparator writes = ZERO direct encodings -> evaluator hunt via
      dark-zone enumeration (t73b); capture fallback. Default >1/2 stands"
    - "OQ-023 dip third-party/trade branch — RE residual OPEN: nonzero
      relation-state ENUM semantics (which of 1/2/3 = war vs allied; idle
      corpus holds ONLY 1, no injected transition), same closure class as
      OQ-021 (interactive original session). Two-party main-branch law itself
      MEASURED diplomacy.md 7/8/9 and implemented; the ENGINE build for
      TRADE/third-party offers is separate build work, not measurement"

## WHAT IS IN HAND (tools + laws — a fresh session starts here, not from scratch)
- R1 save-state capture LIVE: scripts/r1_savestate.sh (boot -> autosave ZIP,
  full guest RAM) + scripts/r1_sav_scan.py (per-run base B, NEVER hard-code;
  member = physical + H, H=136 for dosbox-x 2025.02.01, re-derive per build).
- Deep capture LIVE: scripts/r1_deepcapture.sh (title -> New Game clicks
  318,293 then (511,67) cadence, needle-gated); campaign start proven
  byte-wise (scripts/r1_campaign_probe.py); planet records resume.gam<->RAM
  join 151/151, stride 123 (scripts/r1_planet_layout.py).
- POINTER-INDEX COROLLARY (OQ-014 turn, self-proved): for a Ghidra image
  address X of runtime-loaded data (BSS/data globals like DAT_00073e40), the
  SAVE-ZIP member index is B + 0x82BB0 + X (B = r1_sav_scan.find_base vote),
  and guest PHYSICAL of a member byte is member - 0x88. Reading B + X instead
  yields data 0x88 too low and fails SILENTLY (wrong grid, wrong values, no
  error). Self-proof: item table name-anchored in member 0x2b5ec8 ==
  B+0x82bb0+0x73e40 exactly, and the same index form returned file-identical
  grids + sentinel -1 + growth 50 + research count 66. Heap pointers stored
  in RAM remain physical addresses: member = ptr - 0x88. Helper pattern:
  idx = lambda X,n: m[B+0x82BB0+X : B+0x82BB0+X+n].
- PLANET SYSTEM OBJECT (runtime, OQ-014): base = planet-name - 0x24; +0x10 u32
  slot-array ptr (physical; member = ptr-0x88), +0x12 growth-inc, +0x14 size
  class 0..4, +0x18 surface cells {7,11,23,45,73}, +0x1a cap = cells+10, slot
  = 4B {class, itemIdx (0xff empty), flags u8, shield u8}. Locator law:
  cells in {7,11,23,45,73} AND cap==cells+10 AND ptr sane — 2650/2650 records
  matched across 17 captures, zero false layout reads.
- Turn counter: u16 guest-phys 0x254e10 (idle-pinned 0, NEXTTURN-advanced,
  byte-verified). TURN-BOUNDARY law: planet records mutate only across
  counter-changing slot pairs; hot head-block = older-convention
  +0x35..0x3F (name-based +0x57..0x61), high-entropy u16s every turn.
- STAR TABLE LAW CLOSED 2026-10-06 (battery scripts/r1_star_table.py, gate 3s,
  green 259/259 slots x 13 captures): stride-96 name-anchored star records;
  idx u32 @name-0x18; pos f32[3] @name-0x14; planet ptrs u32[5] @name+0x2A
  targeting planet-NAME-0x24, LIVE iff name prefix matches, single-owner law;
  sub-pool 0x258xxx stride 39 permutation. ORBIT LAW: centered radius constant
  (0 violations 277 planets); per-planet constant dtheta/turn applied by turn
  loop (sample r=544 -> -13.52 deg); unassigned planets subset of static.
  Full field table docs/re/r1-savestate.md "STAR TABLE + ORBIT LAWS". Census
  tool scripts/r1_record_census.py (per-record per-offset planet churn).
- Restored image for Ghidra: work/ascend_restored.bin (built by
  scripts/r1_restore_sites.py; base-0 address space; validation: pointer
  runs >=8 hit Watcom starts 60% vs 15% control). Full analysis ghp5:
  1,144 functions (work/functions_full.tsv).
- Module attribution LIVE: scripts/attribution_scan.py + gate 3r,
  work/attribution.tsv (225 E1 refs, 62% on true fixup sites; flic 43,
  winmgr 24, gsystem 23, race 20, cosmos/batmode 10, planet 8).
- Restree law tool LIVE: scripts/r1_restree_law.py (anchor on row-0 name, walk
  stride 75, no hard-coded address; exit 0 only if the cost law cross-checks
  >=90% of located rows). Green on every banked capture (66/66 rows, 27 slots).
- DATA-FILE STRING -> LOADER ROUTE (proven on OQ-013, 2026-10-06r; the general
  key to the "needs code path" items): the payload holds literal data-file
  names next to their module's debug path (e.g. 'restree.txt' at payload
  offset 0x85014 beside '..\research.cpp'). Tool scripts/r1_datafile_strings.py
  scans guest RAM for u32 == P0 + payload_offset and prints the Ghidra address
  d = (member_off - H) - P0 of every referrer (never hard-code bases). Census
  06r (r1deep-20261006-123049, 20 slots): ALL 23 .txt names referenced --
  batfx 0x1ad97, help 11 refs (0x1bee3...), music 0x212d5, cosmos 0x2140e,
  static 0x218c1, names 0x22894, history 0x2b4d5, end-{xtnc,dest,capt,unit,
  ctrl} 0x2c04e/0x2c065/0x2c07c/0x2c093/0x2c0aa, gwshare 0x31563, tutindex
  0x35a7b, planitem 0x37fcd, restree 0x468d3 (== the independently-found
  loader site -- self-validating), reswin 0x4712b+0x47579, gizmos 0x49081,
  soundfx 0x4ff42, newgame 0x5212c, gizhelp 0x56105, planhelp 0x561f0,
  windows 0x575c3. 06s REFUTES the 06r claim that .shp names had "zero direct
  u32 referrers": the census regex dropped backslash paths and upper-case
  extensions; re-censed correctly, ALL names have referrers (shp 6/6 e.g.
  data\\planets.shp 0x2b224, DATA\\planets.shp 0x51921, MOUSE.SHP 0x309f9;
  HAZ 3/3 in FUN_0001cf20; DIP 2/2; .tmp 10/10 at 0x5a2b3..0x5a39b). Root
  mechanism now CLOSED (pool-relative immediate law, 337 verified sites):
  the obj stores imm = str_off - 0x82BB0 and relocation rewrites it to
  P0 + str_off -- full spec + census in docs/re/datafiles.md. Caveats kept:
  (1) the RESTORED image keeps the unrelocated immediate (Ghidra prints
  'MOV EAX,0x2464' at 0x468d3; live RAM imm 0x244464) -- referrer addresses
  come from the RAM scan, never from image immediates; (2) not every referrer
  lands inside a Ghidra function (end-ctrl.txt 0x2c0aa) -- use disassembly
  context. OQ-004 CLOSED 06s (which tables load + .cob container grammar:
  u32 N + N x 50B names + N x u32 blob offsets; ascend00 54/54 md5; gate
  scripts/cob_probe.py): ascend02 .bin/.tsv have ZERO exe literals -- the
  engine opens them from a RAM name table at guest-phys 0x250c1c (3/3
  captures) sourced from the .cob TOC (anchor ascend01.cob:0x3f98).
- Static trust boundary (from v1 attempt 3): trust rel32 edges + rewritten-
  site immediates ONLY; batch-4-style blind decompile sweeps of E1 batches
  skew UI/allocators (4ae24 = operator-new).
- Gate: bash scripts/gate.sh is the single verification command; ~2-3 min;
  R1 attempts are NEVER gate stages (gate stays fast, side-effect-free).

## NEXT ACTION (exactly one)

IDLE (re-check #48 done at t161; stop-report.md §54): loop awaits a user
event; re-arm ONLY on one of these two triggers (t113 issued the
LOOP-END PROPOSAL — docs/re/stop-report.md §6 — after three consecutive
empty watches t111/t112/t113; do NOT run another watch or census while
idle — an idle turn is the two-trigger probe and nothing else).
RUN THE TOOL, DO NOT RE-DERIVE THE PROBES (t117, amended t145/t146/t147):
    `python3 scripts/r1_idle_probe.py` — RC=0 both negative (stay IDLE),
    RC=1 a trigger armed (it prints which and why), RC=2 probe failure —
    as of t147 this INCLUDES the watcher being down: trigger (A)'s signals
    are produced BY scripts/r1_playcap_watch.py, so with it dead, (A) is
    NOT ADJUDICATED (see the A4 line in its output; repair via
    `bash scripts/r1_playcap_vnc.sh`, re-run the probe, and do NOT record
    the turn as a clean steady-state negative).
    SEPARATELY RUN `python3 scripts/ledger_index_check.py` (t157): diff of
    THIS file's ledger block vs docs/OPEN-QUESTIONS.md using the audit's own
    classifier; LEDGER INDEX OK means the open menu a re-armed session picks
    from is truthful. t157 measured it had drifted 6 rows un-noticed by every
    existing check (see §50). If it FAILS, re-derive the block from the
    record (the record wins) before anything else this turn.
    AS OF t158 BOTH ledger checks are WIRED INTO gate.sh (stage 3t: audit +
    index), so drift cannot exit green via the harness post-flight or the
    finish sequence anymore — the run above is belt-and-braces confirmation,
    not the enforcement. t158 also tightened ledger_audit's EVIDENCE leg to
    demand a SPECIFIC handle (0x address / FUN_ / DAT_ / md5 / capture run dir
    / N-of-M / scripts/*.py / docs/re/*.md); the words "measured"/"verified"/
    "law" alone no longer close a row. LAW: shipping a checker is not
    enforcement — `grep -l <name> scripts/gate.sh scripts/loop_one_task.sh`
    with zero hits means you shipped a suggestion (stop-report §51).
    VERDICT WORDING (t155/B5): at SESSION START a clean tree prints
    "IDLE — neither trigger". If it prints "IDLE with CANDIDATE" you are
    almost certainly running it MID-ITERATION after editing a loop-owned
    file (STATE.md itself counts) — finish normally. But if you edited
    NOTHING this session and it prints CANDIDATE, the uncommitted diff in
    docs/OPEN-QUESTIONS.md / docs/BLOCKED.md / docs/re/ IS either the §3
    answer or crash residue: read `git diff HEAD` before keeping the IDLE
    block. RC stays 0 by design either way (crash residue and a typed
    answer are byte-identical states; mtime cannot separate them).
    It encodes the probe laws that cost iterations to earn:
    session-start cutoff on the find sweep; CONTENT-diff (never mtime)
    for (B); `ps -eo comm` matching (never `pgrep -af`, t114 self-match
    trap); untracked files split by LOOP_OWNED ownership (t153/B4;
    loop-owned _wip_*.md informational, foreign untracked ARMS). Timeline
    path is work/r1/playcap/live-timeline.jsonl. Run it at SESSION START,
    before editing docs — a loop-owned-only delta (STATE.md/stop-report.md)
    prints a CAUTION and stays NEGATIVE, while a delta outside loop-owned
    paths (rewrite/, PLAN.md, game docs) IS the user answer.
    MEASURED SCOPE NOTE (t155): LOOP_OWNED's "work/" entry is inert for the
    git legs (nothing under work/ is tracked; .gitignore ignores work/
    wholesale) — work/r1 is covered by the (A) find sweep instead, and both
    capture launch paths pin their out-dir under work/r1 (r1_playcap.sh:22,
    r1_playcap_vnc.sh:30), so every real capture sits inside a leg. The
    residual blind surface (a user editing scratch under work/ OUTSIDE
    work/r1) is an accepted boundary, not a hole to chase.
    AS OF t149 trigger (A) also has an (A5) ingestion leg: it walks the capture
    dir (skipping caps/, loop/) and reports save-looking files the watcher's
    `save/*.sav` glob (r1_playcap_watch.py:161, lowercase) CANNOT read — a
    healthy watcher can still be blind to a slot it cannot name, and no other
    (A) leg reports that shape. CAUTION only, never a trigger (t117). Two
    false-positive guards are load-bearing and measured, not stylistic: only
    files that are valid save-state ZIPs containing a "Memory" member count
    (work/r1/playcap/evidence_slot04_t1254.SAV is a raw 88 KB memory excerpt,
    is_zipfile False — naming it every turn is permanent noise), and the
    find-sweep now excludes work/r1/.anch-cache.json via TOOL_ARTIFACTS because
    t149 PROVED any analyzer run refreshes it (r1_slot.py:49) and it armed all
    of (A) by itself. Do not "simplify" either guard away.
    AS OF t145 the tool covers BOTH (B) routes including the prompt note;
    AS OF t146 it also covers the COMMITTED-decision route (B3): HEAD vs
    the last journal.tsv sha (last tab field, first token), arming on a
    commit outside loop-owned paths since the last iteration. The hand
    checks are no longer required; run any by hand only if its tool leg
    errors, and then re-check the probe's OWN paths/baseline first.
    t151 ADDS A CONTENT BASELINE for the timeline leg; t156 ENACTS it in
    code (hole A6: grep -c 'md5|hashlib' in the probe was 0 — the rule lived
    only in this file's prose, so a session that armed on (A) without re-reading
    it replayed the stale shared sitting, the exact t152 hazard). The leg now
    hashes head/tail 64 KiB ITSELF when mtime/size differ: same size + both
    md5s == the frozen values => prints "TOUCHED not grown", does NOT arm
    (sound: the watcher appends, r1_playcap_watch.py:146, so an ingest cannot
    be md5-neutral); anything else => arms naming the measured values;
    unreadable => arms without the content check. Frozen values: head
    42a0bed0507f9052e2009ec94e9c27f1 / tail 1529ab1ad70ac360f441d819703f943f
    (stop-report §44; last row {"file":"60.sav","turn":1254,...}), pinned as
    BASE_HEAD_MD5/BASE_TAIL_MD5 — re-freeze ONLY when a sitting legitimately
    lands, never to silence a trigger. R1_TIMELINE overrides the path for
    fixtures. Never md5 the whole 5.7 GB file (edge-hashes are 0.02 s).
    T146 LESSON (generalising t145): every (B) leg WAS a working-tree
    comparison, so a user answer delivered as a clean commit moved HEAD and
    read as idle for an unlimited number of turns. The invariant that
    catches it: the harness writes journal.tsv AFTER each iteration's commit
    with that iteration's sha first in the last tab field, so
    HEAD != journal-sha at session start == commits outside the loop.
    t145 LESSON (how to trust a probe): "the tool touches X" != "the tool
    adjudicates X". t144 cited `r1_idle_probe.py:82-84` (getmtime on the
    prompt glob) as proof the tool was immune to the lexical-sort trap;
    those lines are the FALLBACK session-start cutoff and the tool then
    had NO prompt-content check at all — the only steering leg was an
    existence glob `ls docs/STEERING* STEERING*`, so a PREPENDED prompt
    note could never arm (B). If a probe's verdict contradicts a hand
    reading, re-check the probe's OWN paths/baseline AND ask what it does
    with each documented input, not merely whether it reads the file.
(A) NEW CAPTURE: a new work/r1/playcap-<ts>/ dir (selftest-t111-playcap
    is a self-test artifact, NOT a capture, mtime 21:10 — ditto
    work/r1/.anch-cache.json, written by scripts/r1_slot.py:49 during
    that self-test), OR live-timeline.jsonl mtime past 2026-10-26
    15:44:01.304 / size past 5691796463 B, OR a capture-side file newer
    than session start (only work/r1/loop/* = negative). If armed: run
    scripts/r1_t85g_sitting.py-style adjudication on the new
    turn-boundary sitting — PASS THE CAPTURE DIR AS ARGV[1] (t152 law;
    since t152 it prints which dir it read). TWO HARNESS ROUTES, TWO
    TIMELINES [verified]: r1_playcap_vnc.sh accumulates into
    work/r1/playcap (the 5.7 GB shared file the probe baselines), while
    r1_playcap.sh:78 starts a PER-RUN watcher writing
    work/r1/playcap-<ts>/live-timeline.jsonl. Bare
    `r1_t85g_sitting.py` defaults to the SHARED dir, so on a playcap.sh
    capture it silently replayed the stale t1253/1254 sitting (measured: 45050
    trusted rows vs 0 for the per-run dir) and printed its alliance/ship/
    damage evidence as if it were the user's new game. Check the dir echo.
    (T>0-only slot law PLUS the t111 hygiene law —
    idle boots also yield in_game=true and flat t=/score; require turn or
    score MOVEMENT across slots), then bank OQ-021/023/019 per
    docs/re/stop-report.md §4 (VNC route localhost:5910, launch via
    `bash scripts/r1_playcap.sh` — autodetects :9).
(B) USER DECISION (stop-report §3): accept/reject documented defaults
    (OQ-003 entropy, OQ-005 dims, OQ-019 sugar-cube [1,3]+immediate,
    OQ-023 threshold-only branch); authorize/refuse capture sittings;
    resume t89a follow-on code work or not. MEASURE WITH CONTENT, NOT
    MTIME (t116 law): `git diff HEAD` plus TRACKED `git status
    --porcelain` lines are decisive; `find docs -newermt <last commit>`
    is NOT — the preflight gate runs after each commit and mtime-touches
    docs/re/{text,modules,economy,gizmos,fnt}.md with zero content delta;
    and `--untracked-files=all` is NOT decisive (t117: it lists this
    iteration's own files). AS OF t153 the untracked line is split by
    OWNERSHIP instead of being blanket-informational: `??` paths under
    LOOP_OWNED are informational, a FOREIGN untracked path ARMS (B4) — a §3
    answer left as a NEW file (docs/ANSWER.md, notes.md, a RESTORE-ME note, a
    re-added deleted doc) previously moved no leg at all, because B1 diffs
    tracked files, B3 compares commits, B2 reads prompt text and the STEERING
    leg globs literal names only. Gitignored scratch never appears in porcelain
    and .gitignore covers the loop's scratch surface, so no loop tool can arm
    it; do not re-blanket the leg. Steering note route: the harness prepends a
    note to work/r1/loop/prompt-<n>.txt — the TOOL now adjudicates this by
    digit-stripped content diff (t145); if you must do it by hand,
    enumerate with NUMERIC sort, never `ls -1` (t144 law: `ls -1 | tail
    -1` returns prompt-9.txt, a single-digit prompt ~57 turns old, so the
    diff silently compares the wrong pair). A real answer becomes the
    next STATE.md assignment verbatim and REOPENS the loop.
If neither trigger is present when a session starts, write the honest
negative, keep this IDLE block, run gates, commit, stop.
CLOSURE NOTE (t159): if a future turn closes the LAST open row, the terminal
green needs BOTH index legs done right — empty STATE's `open:` list AND edit
ledger_audit.py's --expect default to "" (an empty open set now passes an empty
expect; before t159 it could not). Do NOT delete either check to go green.
INDEX-FAILURE REPAIR (t161): if ledger_index_check prints "record-CLOSED OQ-NNN
missing from STATE index entirely", the record gained/kept a closed row the block
omits — paste the stub the tool prints (id + one-line summary copied FROM the
record; keep the two-quote-per-entry YAML shape, no raw inner quotes). It is a
hard DIVERGENCE by design; do not delete the leg to go green.

T161 LANDED (IDLE re-check #48 — no trigger fired; deliverables:
scripts/ledger_index_check.py (legs E+F, tightened leg B, nost-path printing),
docs/STATE.md ledger block repaired (+OQ-022, +OQ-024), docs/re/stop-report.md
§54, docs/re/_wip_t161.md; no OPEN-QUESTIONS row touched, game/ untouched, no
watch or census run against the live capture). (1) Trigger (A) NEGATIVE — probe
RC=0 at 05:15:28: newest playcap dir playcap-20261014-224611; live-timeline.jsonl
mtime_ns 1793043841304000000 / 5691796463 B (50th consecutive byte-identical
reading t111..t161); (A6) content baseline reproduced a TENTH time head
42a0bed0507f9052e2009ec94e9c27f1 / tail 1529ab1ad70ac360f441d819703f943f, last
row still t1254; zero dosbox procs; find sweep non-loop none; A4 watcher ALIVE
pid 27774; A5 none (save/*.sav = 20). NOTE for hand re-stats: `stat -c %Y` is
SECONDS — comparing it to the probe's nanosecond baseline naively "diverges"
(1793043841 vs 1793043841304000000); use %y+size or python st_mtime_ns (t147
near-miss family). (2) Trigger (B) NEGATIVE — clean tracked tree at b9cf937 at
session start (verdict wording valid per t155/B5), no STEERING, B3 HEAD ==
journal sha b9cf937 (journal row 82 ct 05:12:48, OK, fail_streak 0), prompt pair
prompt-83 vs prompt-82 (58/58) digit-stripped delta 0. (3) THE FINDING — t160's
audit-the-grader law one level deeper: ask which ids NO leg compares, not whether
each leg fires. ledger_index_check had FOUR legs, all indexed on the open side or
on entries the index already has — a record-CLOSED row absent from STATE's block
moved nothing and printed LEDGER INDEX OK. Live drift: OQ-022 (closed t8) and
OQ-024 (closed t45) absent from the block; record has 19 closed ids (12 main + 7
v1), index listed 17. git log -S proves neither id was touched in the block since
t157 re-derived it — the drift is residue of t157's own repair (open side
re-derived, closed list hand-copied). Fourth recursion t157/t158/t159/t160/t161:
every grader fix audits clean except its own blind direction. LAW: a
bidirectional consistency checker must enumerate directions as SET PAIRS
(record→index on open AND closed; index→record on open AND closed); legs built
from "what drifted last time" inherit last time's blind side. (4) FIX by real
execution, fixtures deleted: leg E (record-CLOSED missing -> names id + pasteable
stub), leg F (duplicate id in record — dict kept LAST copy silently; measured 18
rows/18 distinct today so early trip only; nost early-return no longer swallows
the finding), leg B tightened (the v1 exemption now excuses ONLY "absent from
record" — STATE listing a v1 id OPEN now fails, pre-patch it printed OK).
Six-branch validation: un-repaired real pair RC=1 naming both rows (negative
control run BEFORE repairing); v1 closed id removed RC=1; v1 id injected open
RC=1; duplicate status-bearing row RC=1; duplicate no-status (nost path) RC=1
with dupe line still printed; repaired real pair OK RC=0. STATE repaired with
record-sourced summaries; YAML convention kept (exactly 2 quotes/entry — first
draft's raw inner quote caught by awk vs HEAD). One test-harness trap banked
§54: a fixture-building heredoc silently produced NO file and the checker's
correct RC=1 (FileNotFoundError) briefly read as a passing divergence test —
grep the fixture into existence before trusting any RC. Enforcement holds per
t158: gate.sh:421 stage 3t invokes the fixed tool. (5) Bank hygiene fresh
(grep -rln stop-report scripts/ -> r1_idle_probe.py + ledger_audit.py docstrings
only; 2030 lines zero diff vs HEAD before appending §54). Infra unchanged since
t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log 2026-10-27
17:30:18/30114 — zero connects). NO row closed (strict-close honest negative —
harness hardening, not measurement), no law falsified. NEXT stays IDLE; the t113
LOOP-END PROPOSAL stands (48 idle turns). Gate 0.

T160 LANDED (IDLE re-check #47 — no trigger fired; deliverables:
scripts/ledger_index_check.py (V1_IDS derived+reconciled), docs/re/stop-report.md
§53, docs/re/_wip_t160.md; no ledger row touched, game/ untouched, no watch or
census run against the live capture). (1) Trigger (A) NEGATIVE — probe RC=0 at
05:01:53: newest playcap dir playcap-20261014-224611; live-timeline.jsonl
mtime_ns 1793043841304000000 / 5691796463 B (50th consecutive byte-identical
reading t111..t160; independently re-statted, equal to BASE_MTIME_NS/BASE_SIZE);
(A6) content baseline reproduced a NINTH time head
42a0bed0507f9052e2009ec94e9c27f1 / tail 1529ab1ad70ac360f441d819703f943f, last
row still t1254; zero dosbox procs; find sweep non-loop none; A4 watcher ALIVE
pid 27774; A5 none (save/*.sav = 20). (2) Trigger (B) NEGATIVE — clean tracked
tree at 87b41a4 at session start (verdict wording valid per t155/B5), no
STEERING, B3 HEAD == journal sha 87b41a4, prompt pair prompt-82 vs prompt-81
(58/58) digit-stripped delta 0. (3) THE FINDING — the t158 audit-the-grader law
applied to the last hand-maintained literal left in the ledger checks after
t159: ledger_index_check.py's V1_IDS exemption set (ids skipping both
"absent from record" legs because the record closes them in the "- > OQ-" v1
block ledger_audit skips by design). Measured first: derived-from-record == the
literal exactly 7/7, zero live drift — but nothing compared them, so a record
v1-block edit armed FALSE divergence while an id ADDED to the block silently
exempted a row from every cross-check. FIX: V1_IDS derived each run from the
record (v1_block_ids(), ^- > OQ-(\d+)) and RECONCILED against kept code pin
V1_IDS_EXPECTED; disagreement fails RC=1 naming the delta in both directions.
LAW (fourth family instance t157/t158/t159/t160): a constant in a checker that
names objects in another artifact must DERIVE from the contract artifact and
KEEP the literal as a reconciliation pin — derive-and-reconcile, not
copy-and-hope, not delete-and-trust. Four-branch validation by REAL execution
(fixtures deleted): real OK RC=0; block deleted RC=1 (drift line + 7 absent-id
lines, double signal); spurious OQ-099 in block RC=1 naming it; pre-t157 drifted
STATE RC=1 naming all six original drifts. One self-inflicted TEST-harness bug
(a "; true" truncating the invocation so t4 ran nothing and printed RC=0) —
caught by verifying the fixture existed; the checker itself was never wrong.
Enforcement holds per t158: gate.sh:421 stage 3t invokes the fixed tool.
(4) Bank hygiene fresh (grep -rln stop-report scripts/ -> r1_idle_probe.py +
ledger_audit.py docstrings only; 1967 lines zero diff vs HEAD before appending
§53). Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log 2026-10-27 17:30:18/30114 — zero connects). NO row closed
(strict-close honest negative — harness hardening, not measurement), no law
falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands (47 idle turns).
Gate 0.

T159 LANDED (IDLE re-check #46 — no trigger fired; deliverables:
scripts/ledger_audit.py (completion-state fix), docs/re/stop-report.md §52,
docs/re/_wip_t159.md; no ledger row touched, game/ untouched, no watch or census
run against the live capture). (1) Trigger (A) NEGATIVE — probe RC=0 at 04:40:29:
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (49th consecutive byte-identical reading
t111..t159; independently re-statted, equal to BASE_MTIME_NS/BASE_SIZE); (A6)
content baseline reproduced an EIGHTH time head 42a0bed0507f9052e2009ec94e9c27f1
/ tail 1529ab1ad70ac360f441d819703f943f, last row still t1254; zero dosbox procs;
find sweep non-loop none; A4 watcher ALIVE pid 27774; A5 none (save/*.sav = 20).
(2) Trigger (B) NEGATIVE — clean tracked tree at 0e8c8e9 at session start
(verdict wording valid per t155/B5), no STEERING, B3 HEAD == journal sha 0e8c8e9,
prompt pair prompt-81 vs prompt-80 (58/58) digit-stripped delta 0. (3) THE
FINDING — t158's corollary (audit the grader) run against the one input
ledger_audit had never seen in 158 iterations: ZERO open rows, which IS
GOAL.txt:2's completion condition. Measured on an all-18-rows-CLOSED fixture
(verified via the tool's own rows()/status_of): `--expect ''` => "OPEN-SET
MISMATCH vs expected ['']" RC=1, because "".split(",")==[""] makes want={""} —
an empty open set can never equal it. The strict-close grader therefore made the
project's terminal green unreachable by construction (a completing session would
gate RED forever). ledger_index_check was already correct on the same fixture
(RC=0 with an emptied STATE block). FIX one line: `want = {x.strip() for x in
a.expect.split(",") if x.strip()}`. Four branches validated by REAL execution,
fixtures deleted after: real ledger + real default OK (byte-identical
regression); fixture + --expect '' OK; clone with the default string itself
emptied + fixture OK (the completing session's actual edit shape; t89/t100
history shows the default is hand-edited per closure); that clone vs the REAL
open ledger FAILED RC=1 (an empty default cannot silently bless open rows).
py_compile clean. LAW (extends t158): when a grader encodes a set as a literal,
ask what its EMPTY case does — a checker that cannot represent success converts
"done" into "broken" (mirror image of t157's cannot-represent-drift bug).
(4) MEASURED BOUNDARIES kept, not fixed: status_of is position-dependent (first
pipe-wrapped status-shaped cell wins, ledger_audit.py:52-61, t85 design) —
fixture F5 pasted "| CLOSED t40 note |" into OQ-021's question field and the row
flipped CLOSED, but BOTH gate-3t legs caught it (audit RC=1 mismatch, index RC=1
naming the row): lousy message, no silent green; a strict column-2 rule was
rejected because OQ-016-style rows legitimately hold status words in prose.
--expect stays a hand-maintained duplicate (deriving it from the record is
circular). (5) RE-ARM MEASURED ALIVE, first explicit record: tmux `ascendloop`
78558 (PPid 1) -> 78559 -> loop_one_task.sh 78561; this session = iteration 81
(timeout -s KILL 12600 hermes chat --query-file work/r1/loop/prompt-81.txt);
journal iter 80 OK 0e8c8e9; fail_streak 0; no crontab. Supervisor death is
un-adjudicated by design (A4 covers the watcher only); repair = check for
work/r1/loop/STOP, then relaunch the exact 78558 command line. (6) Gate
traversal: stage 3t unavoidable — set -u not set -e, err() only sets fail=1,
sole exit `exit $fail` at gate.sh:464, post-flight runs the whole script
(loop_one_task.sh:119) — t158's open question answered in the negative. Bank
hygiene fresh (grep -rln stop-report scripts/ -> only the two docstrings; 1901
lines zero diff vs HEAD before appending §52). NO row closed (strict-close honest
negative — harness hardening, not measurement), no law falsified. NEXT stays
IDLE; the t113 LOOP-END PROPOSAL stands (46 idle turns). Gate 0.

T158 LANDED (IDLE re-check #45 — no trigger fired; deliverables:
scripts/gate.sh (stage 3t), scripts/ledger_audit.py (tightened EVIDENCE),
docs/re/stop-report.md §51, docs/re/_wip_t158.md; no ledger row touched, game/
untouched, no watch or census run against the live capture). (1) Trigger (A)
NEGATIVE — probe RC=0 at 04:17:08: newest playcap dir playcap-20261014-224611;
live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B (48th
consecutive byte-identical reading t111..t158; independently re-statted, equal
to BASE_MTIME_NS/BASE_SIZE); (A6) content baseline reproduced a SEVENTH time
head 42a0bed0507f9052e2009ec94e9c27f1 / tail 1529ab1ad70ac360f441d819703f943f,
last row still t1254; zero dosbox procs; find sweep non-loop none; A4 watcher
ALIVE pid 27774; A5 none (save/*.sav = 20). (2) Trigger (B) NEGATIVE — clean
tracked tree at ec8a5ee at session start (verdict wording valid per t155/B5),
no STEERING, B3 HEAD == journal sha ec8a5ee, prompt pair prompt-80 vs
prompt-79 (58/58) digit-stripped delta 0. (3) THE FINDING — t157's law
recursed onto t157's own fix: ledger_index_check.py was pointed at by prose but
referenced by ZERO automatic paths (grep -c ledger_index_check: gate.sh 0,
loop_one_task.sh 0; the only post-flight checks are gate.sh + ledger_audit.py at
loop_one_task.sh:119-124), so one careless future turn that edits STATE.md's
block without running the tool re-introduces the 6-row drift invisibly. FIX:
gate.sh stage 3t runs ledger_audit.py AND ledger_index_check.py (/usr/bin/
python3 like every other python stage); validated BOTH directions by real
execution — clean tree GATE_EXIT=0; pre-t157 drifted STATE.md (from 1f62e45,
via R1_STATE) GATE_EXIT=1 naming all six drifts + the repair instruction;
fixture deleted. (4) SECOND HOLE — the strict-close grader itself: ledger_audit's
EVIDENCE regex accepted the generic words measured/verified/law/slots/.sav/...
as citation (a prose default grading itself CLOSED — exactly what GOAL.txt
forbids) while having no FUN_/DAT_ alternative at all, blind to the project's
dominant citation form. FIX: >=1 specific handle required (0x/FUN_/DAT_/md5/
run-dir r1xxx-NNNNNN/N-of-M/scripts/*.py/docs/re/*.md). Measured first over all
12 real closed rows — every row has >=1 handle (per-row counts in §51), so zero
retroactive false positives — then verified: real record LEDGER AUDIT OK
unchanged; synthetic prose-only row -> "MISSING evidence: OQ-100" RC=1;
handle-bearing row passes. LAW (third t145-family instance, first inside the
previous iteration's own fix): shipping a checker is not enforcement; the
checker must sit in a path the loop cannot exit through — grep -l it against
gate.sh/loop_one_task.sh before calling the fix done. Corollary: when a policy
is restated, audit the GRADER (the regex IS the policy, not the docstring).
(5) Bank hygiene fresh (stop-report.md zero diff vs HEAD at 1832 lines before
appending §51). Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher
27774; x11vnc.log 2026-10-27 17:30:18/30114 — zero connects). NO row closed
(strict-close honest negative — harness hardening, not measurement), no law
falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands (45 idle turns).
Gate 0.

T157 LANDED (IDLE re-check #44 — no trigger fired; deliverables:
scripts/ledger_index_check.py (NEW), docs/STATE.md ledger block re-derived,
docs/re/stop-report.md §50, docs/re/_wip_t157.md; no ledger row touched, game/
untouched, no watch or census run against the live capture). (1) Trigger (A)
NEGATIVE — probe RC=0 at 03:55:39 (cutoff 03:53:57): newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B (47th consecutive byte-identical reading t111..t157;
independently re-statted, equal to BASE_MTIME_NS/BASE_SIZE); (A6) content
baseline reproduced a SIXTH time head 42a0bed0507f9052e2009ec94e9c27f1 / tail
1529ab1ad70ac360f441d819703f943f, last row still t1254; zero dosbox procs; find
sweep non-loop none; A4 watcher ALIVE pid 27774; A5 none (save/*.sav = 20).
(2) THE FINDING — a control-plane hole OUTSIDE the trigger surface: STATE.md's
ledger fast index had drifted SIX rows from the authoritative record
docs/OPEN-QUESTIONS.md, measured by importing ledger_audit's own classifier:
OQ-006/012/015/020/025 listed open while the record CLOSED them, OQ-023 open
but MISSING from the index. STATE's header said "Update BOTH or neither" — a
prose invariant with zero enforcement: gate.sh never runs ledger_audit.py
(verified by grep), and ledger_audit checks the record only against its
hard-coded --expect list, never against STATE.md (its docstring even describes
an index format STATE never used). Hazard: a re-armed session obeys "resume
from STATE.md ALONE" and would pick tasks from a 10-row menu with 5 stale rows
and 1 missing row. Mechanism: scope-narrowing narrative — closed sub-legs
stayed INLINE in open-entry text while the row never moved lists. FIX shipped:
ledger_index_check.py diffs STATE's block vs the record (same parser, so the
two checks cannot disagree by classifier; v1 ids exempt because they close in
the record's "- > OQ-" block ledger_audit skips). Validated by REAL execution:
HEAD's pre-repair STATE.md => RC=1 naming all six drifts; repaired block =>
RC=0 LEDGER INDEX OK; fixture deleted. Index re-derived from the record (open
= OQ-003/005/016/019/021/023). NEXT ACTION block now instructs running the
index check every session start. LAW GENERALISED (extends t145/t146/t155/
t156): a documented invariant between TWO files is enforced by nobody who only
reads one of them — each artifact satisfied its own check while they disagreed;
if a fact must hold across artifacts, ship a checker that reads BOTH and point
the prose at the checker, not at manual discipline. (3) Trigger (B) NEGATIVE —
clean tracked tree at 1f62e45 at session start (verdict wording valid per
t155/B5), no STEERING, B3 HEAD == journal sha 1f62e45 (re-extracted by hand
from journal.tsv last tab field), prompt pair prompt-79 vs prompt-78 (58/58)
digit-stripped delta 0. §3 answers outstanding after forty-four idle turns.
(4) Bank hygiene fresh (grep -rln stop-report scripts/ -> only
r1_idle_probe.py + .pyc; stop-report.md zero diff vs HEAD at 1779 lines before
appending §50). Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher
27774; x11vnc.log 2026-10-27 17:30:18/30114 — zero connects). NO row closed
(strict-close honest negative — the repair is bookkeeping, not measurement),
no law falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands. Gate 0.

T156 LANDED (IDLE re-check #43 — no trigger fired; deliverables:
scripts/r1_idle_probe.py ((A6) leg + edge_md5() + R1_TIMELINE + docstring law),
docs/re/stop-report.md §49, docs/re/_wip_t156.md; no ledger row touched, game/
untouched, no watch or census run against the live capture). (1) Trigger (A)
NEGATIVE — probe RC=0 at 03:39:49 (cutoff 03:38:08): newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B (46th consecutive byte-identical reading t111..t156;
independently re-statted, equal to BASE_MTIME_NS/BASE_SIZE); t151 content
baseline reproduced a FIFTH time head 42a0bed0507f9052e2009ec94e9c27f1 / tail
1529ab1ad70ac360f441d819703f943f, last row still t1254; zero dosbox procs; find
sweep non-loop none; A4 watcher ALIVE pid 27774; A5 none (save/*.sav = 20).
(2) THE FINDING — hole (A6), t145 method aimed at the timeline growth leg: it
compared ONLY mtime/size — `grep -c 'md5|hashlib' scripts/r1_idle_probe.py` ==
0 — while the t151 touch-vs-ingest rule lived ONLY in STATE.md prose. A session
arming on (A) without re-reading that prose would adjudicate the SHARED
stale t1253/1254 sitting as the user's new game (the exact t152 hazard, no
error, default path prints no warning). FIX: edge_md5() (first/last 64 KiB,
seek-based, 0.019 s measured on the real 5.7 GB file; a file <= one window is
its own head and tail) + the (A6) leg inside trigger_a: same size AND both md5s
== frozen values => "TOUCHED not grown", NOT armed (sound because the watcher
appends r1_playcap_watch.py:146, so an ingest strictly grows the file and can
never be md5-neutral); anything else => armed naming measured values; OSError =>
armed without content check. TIMELINE env-overridable (R1_TIMELINE) per loop
convention so the leg is testable. Five validations by REAL execution, fixtures
deleted: t1 growth arms CONTENT CHANGED; t2 touch does NOT arm; t3 same-size
content-diff arms; t4 unreadable arms without content check; helper MATCHes the
hand-measured dd/tail md5s on the real file. One self-inflicted patch bug caught
by the tests: v1 edge_md5 left the position at EOF after the head read, so sub-
window files hashed an empty tail (d41d8cd9) contrary to its docstring — inert
for the real file, latent lie for any small fixture; rewritten with an explicit
size<=window branch. LAW GENERALISED (extends t145/t155): a rule recorded in
STATE.md prose is NOT a leg — adjudication that depends on a human re-reading
the doc at trigger time will not happen; encode it in the tool or declare the
surface un-adjudicated. (3) Trigger (B) NEGATIVE — clean tracked tree at
1767c28, no STEERING, B3 HEAD == journal sha 1767c28 (row 77 ct 03:37:15,
re-extracted by hand outside the probe), prompt pair prompt-78 vs prompt-77
(58/58) digit-stripped delta 0; verdict printed "IDLE — neither trigger", valid
per t155/B5 because the tree was clean AT SESSION START. §3 answers outstanding
after forty-three idle turns. (4) Bank hygiene fresh (grep -rln stop-report
scripts/ -> only r1_idle_probe.py + .pyc; gate.sh only -s/grep -q docs/re,
never writes stop-report.md; 1727 lines zero diff vs HEAD before appending
§49). Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log 2026-10-27 17:30:18/30114 — zero connects). NO row closed
(strict-close honest negative), no law falsified. NEXT stays IDLE; the t113
LOOP-END PROPOSAL stands. Gate 0.

T155 LANDED (IDLE re-check #42 — no trigger fired; deliverables:
scripts/r1_idle_probe.py (B5) leg + docstring B4/B5 laws,
docs/re/stop-report.md §48, docs/re/_wip_t155.md; no ledger row touched,
game/ untouched, no watch or census run against the live capture). (1)
Trigger (A) NEGATIVE — probe RC=0 at 03:16:34 (cutoff 03:14:49): newest
playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (45th consecutive byte-identical reading
t111..t155; independently re-statted, equal to BASE_MTIME_NS/BASE_SIZE at
r1_idle_probe.py:55-56); t151 content baseline reproduced a FOURTH time
(head 42a0bed0507f9052e2009ec94e9c27f1 / tail 1529ab1ad70ac360f441d819703f943f,
last row still t1254); zero dosbox procs; find sweep non-loop none; A4
watcher ALIVE pid 27774; A5 none (save/*.sav = 20). (2) THE FINDING — hole
(B5), the t145 method aimed at the last leg whose OUTPUT SHAPE had never been
questioned: trigger_b demoted every tracked delta under LOOP_OWNED to a buried
CAUTION reason line while the printed VERDICT asserted "neither trigger" and
RC=0 — and LOOP_OWNED contains docs/OPEN-QUESTIONS.md and docs/BLOCKED.md,
the two files stop-report §3 invites the user to answer INTO. STATE.md quotes
the RC line, so the caution never reached any decision. Fix: trigger_b returns
decision_candidate; the (B) header prints "CANDIDATE — read the CAUTION" and
the VERDICT "IDLE with CANDIDATE ... read `git diff HEAD` before keeping the
IDLE block". DELIBERATELY NOT ARMED (RC stays 0): t117 law — a crashed
pre-commit iteration leaves byte-identical state and mtime cannot separate the
origins, so escalation-not-arming is the only sound resolution; the
mtime-discriminator was considered and rejected. Five branches validated by
REAL execution, fixtures deleted: real CANDIDATE RC=0 (self-demonstrating —
the patched probe is itself loop-owned); clean tree + old code NEGATIVE RC=0
(regression control); clean tree + new code CANDIDATE RC=0; foreign untracked
docs/ANSWER-t155test.md ARMED RC=1 (B4 precedence holds); fixture removed ->
CANDIDATE RC=0. LAW GENERALISED (extends t145): "the leg prints a CAUTION" !=
"the VERDICT carries it" — adjudication that never reaches the line the caller
reads is an unenacted leg. (3) TWO MEASURED SCOPE FACTS, banked as accepted
boundaries, not chased: prompt corpus = 77 files / only 3 distinct
digit-stripped bodies (41x15, 63x3, 58x59), so B2's newest-pair rule has no
multi-shape drift exposure; LOOP_OWNED's "work/" entry is INERT for B1/B3/B4
(git ls-files work/ empty + .gitignore ignores work/ wholesale) — the only
leg that sees work/ is the (A) find sweep, scoped to work/r1, and BOTH capture
launch paths pin OUT under work/r1 (r1_playcap.sh:22 per-run dir,
r1_playcap_vnc.sh:30 shared), so every real capture sits inside a leg; the
residual (user edits scratch under work/ outside work/r1) has no documented
route and broadening the sweep re-creates the t149 self-arm shape. (4)
Trigger (B) NEGATIVE at session start — clean tracked tree at f0e9527, no
STEERING, B3 HEAD == journal sha f0e9527 (re-extracted via rev/cut outside
the probe), prompt pair prompt-77 vs prompt-76 (58/58) digit-stripped delta 0
by tool AND by hand ls -1v. §3 answers outstanding after forty-two idle
turns. (5) NEXT ACTION block: stale t117-era untracked wording replaced with
the t153/B4 ownership law + the new B5 verdict-wording guidance. Bank hygiene
fresh (grep -rln stop-report scripts/ -> only r1_idle_probe.py + .pyc;
stop-report.md 1683 lines zero diff vs HEAD before appending §48). Infra
unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log
2026-10-27 17:30:18/30114 — zero connects). NO row closed (strict-close honest
negative), no law falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL
stands. Gate 0.

T154 LANDED (IDLE re-check #41 — no trigger fired; deliverables:
docs/re/stop-report.md §47, docs/re/_wip_t154.md; no scripts changed, no ledger
row touched, game/ untouched, no watch or census run against the live capture).
(1) Trigger (A) NEGATIVE — probe RC=0 at 03:06:14 (cutoff 03:05:19): newest
playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (44th consecutive byte-identical reading
t111..t154; independently re-statted, equal to BASE_MTIME_NS/BASE_SIZE at
r1_idle_probe.py:55-56 re-read from source); t151 content baseline reproduced
a THIRD time (head 42a0bed0507f9052e2009ec94e9c27f1 / tail
1529ab1ad70ac360f441d819703f943f; last line still the t1254 row); zero dosbox
procs; find sweep non-loop none; A4 watcher ALIVE pid 27774; A5 none
(save/*.sav = 20). (2) THE FINDING — none this turn, honestly: the t145 method
applied to the t153 surfaces found no hole, but yielded a structural
confirmation worth keeping — the (A) find-sweep filter (r1_idle_probe.py:118-
124) excludes only the `work/r1/loop/` PREFIX + TOOL_ARTIFACTS, NOT LOOP_OWNED
wholesale, so foreign files under work/r1 arm (A) while (B4)'s ownership split
(:259/:277) owns the rest of the tree: the t153 division of labour is
complementary BY CONSTRUCTION, verified in source not just at run time. B2
numeric sort (:361-364 int() key) re-verified vs the t144 trap. (3) Trigger (B)
NEGATIVE — clean tracked tree at d62b1f3, no STEERING, B3 HEAD == journal sha
d62b1f3 (independently re-extracted from journal.tsv last tab field), prompt
pair prompt-76 vs prompt-75 (58/58) digit-stripped delta 0; (B4) clean on real
state on its first production turn. §3 answers outstanding after forty-one
idle turns. (4) Bank hygiene fresh (grep -rln stop-report scripts/ -> only
r1_idle_probe.py + .pyc; gate.sh has no docs/re write; stop-report.md 1636
lines zero diff vs HEAD before appending §47). Infra unchanged since t112
(Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log 2026-10-27
17:30:18/30114 — zero connects). NO row closed (strict-close honest negative),
no law falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands. Gate 0.

T153 LANDED (IDLE re-check #40 — no trigger fired; deliverables:
scripts/r1_idle_probe.py (B4) leg, docs/re/stop-report.md §46,
docs/re/_wip_t153.md; no ledger row touched, game/ untouched, no watch or
census run against the live capture). (1) Trigger (A) NEGATIVE — probe RC=0 at
02:50:35 (cutoff 02:48:55): newest playcap dir playcap-20261014-224611;
live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B (43rd
consecutive byte-identical reading t111..t153; independently re-statted, equal
to BASE_MTIME_NS/BASE_SIZE at r1_idle_probe.py:55-56 re-read from source); zero
dosbox procs; find sweep non-loop none; A4 watcher ALIVE pid 27774; A5 none
(save/*.sav = 20). t151 CONTENT BASELINE reproduced a third time byte-identical
(head 42a0bed0507f9052e2009ec94e9c27f1 / tail 1529ab1ad70ac360f441d819703f943f
— the touch-vs-ingest rule now measured-reproducible twice over). (2) THE
FINDING — hole (B4), t145 method (what the leg DOES with its input) applied to
the last un-adjudicated (B) surface: the untracked line printed `??` entries as
blanket "informational, NOT a trigger". t117's law was earned against the
LOOP'S OWN _wip_*.md but applied to every path, so a §3 answer delivered as a
NEW FILE (docs/ANSWER.md, notes.md, RESTORE-ME, a re-added deleted doc) moved
nothing — B1 diffs tracked files only, B3 compares commits, B2 reads prompt
text, the STEERING leg globs literal names. FIX: split untracked by LOOP_OWNED
ownership; loop-owned informational (t117 kept), foreign ARMS. Safety measured
BEFORE patching: porcelain never lists gitignored paths and .gitignore covers
the loop's scratch surface (build/, .logs/, __pycache__/, *.pyc, work/, *.log,
.cache/...), verified by fixtures in each. Four-branch validation by REAL
execution, fixtures deleted: real state none/RC=0; foreign root ANSWER file
ARMED RC=1 naming the path; gitignored scratch correctly prints none (the (A)
find-sweep armed on a work/r1 fixture instead — correct division of labour,
and a useful discovery: the sweep already owns work/r1, so (B4) only needs to
own the rest of the tree); post-cleanup control RC=0. (3) Trigger (B) NEGATIVE
— clean tracked tree at 1abf176, no STEERING, B3 HEAD == journal sha 1abf176,
prompt pair prompt-75 vs prompt-74 (58/58) digit-stripped delta 0. §3 answer
outstanding after forty idle turns. (4) Bank hygiene fresh: grep -rln
stop-report scripts/ -> only r1_idle_probe.py docstring + .pyc; stop-report.md
1581 lines zero diff vs HEAD before appending §46. Infra unchanged since t112
(Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log 2026-10-27
17:30:18/30114 — zero connects); probe children per the t118 noise law. NO row
closed (strict-close honest negative), no law falsified. NEXT stays IDLE; the
t113 LOOP-END PROPOSAL stands. Gate 0.

T152 LANDED (IDLE re-check #39 — no trigger fired; deliverables:
scripts/r1_t85g_sitting.py (argv[1] RUN + dir echo), docs/re/stop-report.md
§45, docs/re/_wip_t152.md; no ledger row touched, game/ untouched, no watch or
census run against the live capture). (1) Trigger (A) NEGATIVE — probe RC=0 at
02:28:41 (cutoff 02:26:59): newest playcap dir playcap-20261014-224611;
live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B (42nd
consecutive byte-identical reading t111..t152; re-statted independently, exact
match, equal to BASE_MTIME_NS/BASE_SIZE at r1_idle_probe.py:55-56); zero
dosbox procs; find sweep non-loop none; A4 watcher ALIVE pid 27774; A5 none
(save/*.sav = 20, all match the glob). (2) T151'S NEW CONTENT BASELINE
REPRODUCED byte-for-byte — head 64 KiB md5 42a0bed0507f9052e2009ec94e9c27f1,
tail 1529ab1ad70ac360f441d819703f943f: the touch-vs-ingest rule is now
measured-reproducible, not merely recorded. (3) THE FINDING — a defect in the
(A) re-arm PATH, downstream of the trigger. The instruction every idle turn
hands forward ("run r1_t85g_sitting.py-style adjudication on the new sitting")
named a tool that pinned its evidence dir (r1_t85g_sitting.py:18 == the shared
work/r1/playcap). Two harnesses, two dirs [verified from source]:
r1_playcap_vnc.sh ACCUMULATES into work/r1/playcap, while r1_playcap.sh — the
user-facing one-shot STATE/(A) and stop-report §4 name as the launch path —
creates work/r1/playcap-<ts>/ and at :78 starts a PER-RUN watcher writing a
PER-RUN live-timeline.jsonl (4 of 5 playcap-* dirs hold one, 4.8 KB..284 KB).
HAZARD PROVEN BY EXECUTION: per-run dir -> "0 trusted rows" (correct: 65 rows,
ALL turn=0, a t82-law idle boot); legacy default -> "45050 trusted rows", the
OLD shared t1253/1254 sitting printed WITH relation snapshots, ship events and
damage deltas. A re-arm on a playcap.sh capture would have banked stale
evidence as the user's new game — no error, no dir named. Same family as the
0x88 pointer-law trap. FIX: RUN = sys.argv[1] else DEFAULT_RUN (back-compat
for t85g's own historical re-runs) + the header echoes the source dir;
py_compile clean, BOTH branches executed. LAW banked (generalising t145): when
a procedure names a tool AND an object, verify the tool can address THAT
object — a pinned default that was right for 30 turns proves nothing about the
next. The trigger itself was never blind (r1_idle_probe.py:74 arms on any new
playcap-<ts> name). (4) Trigger (B) NEGATIVE — clean tracked tree at 6ff9ded,
no STEERING, B3 HEAD == journal row 73 sha 6ff9ded (re-read independently, ct
02:26:06), prompt pair prompt-74 vs prompt-73 (58/58) digit-stripped delta 0.
§3 answer outstanding after thirty-nine idle turns. (5) t147 law run again —
r1_idle_probe.py:335-341 numeric sort, r1_playcap_watch.py:161 lowercase glob,
r1_slot.py:49 .anch-cache.json all re-read from source; bank hygiene -> only
r1_idle_probe.py docstring + .pyc, stop-report.md 1514 lines zero diff vs HEAD
before appending. Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 /
watcher 27774; x11vnc.log 2026-10-27 17:30:18/30114 — zero connects); probe
children 171676/171728 per the t118 noise law. NO row closed (strict-close
honest negative), no law falsified. NEXT stays IDLE; the t113 LOOP-END
PROPOSAL stands. Gate 0.

T151 LANDED (IDLE re-check #38 — no trigger fired; deliverables:
docs/re/stop-report.md §44 appended, docs/re/_wip_t151.md; no ledger row
touched, no scripts/ change, no watch/census run against the live capture).
(1) Trigger (A) NEGATIVE — probe RC=0 at 02:19:44 (session-start cutoff
02:17:58): newest playcap dir playcap-20261014-224611; live-timeline.jsonl
mtime_ns 1793043841304000000 / 5691796463 B (41st consecutive byte-identical
reading t111..t151; re-statted independently, exact match, equal to
BASE_MTIME_NS/BASE_SIZE at r1_idle_probe.py:55-56); zero dosbox procs; find
sweep non-loop none; A4 watcher ALIVE pid 27774 (PPid 27772 wrapper pair,
t115), wchan=hrtimer_nanosleep State S, fds 1/2->watch.out,
3->live-timeline.jsonl, 4->watch.log; A5 none (save/*.sav = 20, all match the
watcher glob). (2) THE ITERATION'S VALUE — the (A) timeline baseline was
mtime+size only, so it could not distinguish a touch from an ingest and could
not be re-proved content-stable cheaply. Banked a CONTENT signature of the
frozen timeline (t116 law aimed at the baseline itself): head/tail 64 KiB md5s
42a0bed0507f9052e2009ec94e9c27f1 / 1529ab1ad70ac360f441d819703f943f, last
line {"file":"60.sav","turn":1254,...} — now recorded in the (A) block above
with the adjudication rule; no probe change (the growth leg is proven, t117
positive control). (3) Trigger (B) NEGATIVE — clean tracked tree at 39dcdc2,
no STEERING file, B3 HEAD == journal row 72 sha 39dcdc2 (re-read
independently); prompt pair prompt-73 vs prompt-72 (58/58) digit-stripped
delta 0, hand cross-check agrees with the tool leg. §3 answer outstanding
after thirty-eight idle turns. (4) t147 law run again — every cited site
re-read from source before banking: r1_idle_probe.py:335-341 numeric prompt
sort, r1_playcap_watch.py:161 lowercase glob, r1_slot.py:49 .anch-cache.json;
bank hygiene grep -> only r1_idle_probe.py docstring + .pyc, stop-report.md
1468 lines zero diff vs HEAD pre-append. Infra unchanged since t112 (Xvfb
1196 / x11vnc 1207 / watcher 27774; x11vnc.log 2026-10-27 17:30:18/30114 —
zero connects); probe children 170331/170382 per the t118 noise law; removed
the stale /tmp/t149-watch fixture t149 left behind. NO row closed (strict-close
honest negative), no law falsified. NEXT stays IDLE; the t113 LOOP-END
PROPOSAL stands. Gate 0.

T150 LANDED (IDLE re-check #37 — no trigger fired; deliverables:
docs/re/stop-report.md §43 appended, docs/re/_wip_t150.md; no ledger row
touched, no scripts/ change, no watch/census run against the live capture).
(1) Trigger (A) NEGATIVE — probe RC=0 at 02:10:24 (session-start cutoff
02:09:27): newest playcap dir playcap-20261014-224611; live-timeline.jsonl
mtime_ns 1793043841304000000 / 5691796463 B (40th consecutive byte-identical
reading t111..t150; re-statted independently via `stat -c '%Y %y %s'`, exact
match, and equal to the probe's own BASE_MTIME_NS/BASE_SIZE at
r1_idle_probe.py:55-56); zero dosbox procs (`ps -eo pid,comm`); find sweep
non-loop none; A4 watcher ALIVE pid 27774, wchan=hrtimer_nanosleep State S
(5 s poll tick, not wedged), fds 1/2->watch.out, 3->live-timeline.jsonl,
4->watch.log; A5 none (save/*.sav = 20, all match the watcher glob).
(2) Trigger (B) NEGATIVE — clean tracked tree at 61d32e2, no STEERING file,
B3 HEAD == journal row 71 sha 61d32e2 (journal re-read independently). The
prompt route was additionally cross-checked BY HAND this turn (numeric
enumeration -> pair prompt-72.txt vs prompt-71.txt, 58/58 lines,
digit-stripped diff 0 lines exit 0): identical verdict to the tool leg. §3
answer outstanding after thirty-seven idle turns. (3) THE ITERATION'S VALUE —
t149's two load-bearing guards and both cited code sites re-verified from
source rather than trusted (t148 law): bank-hygiene `grep -rln stop-report
scripts/` -> only r1_idle_probe.py docstring (line 3) + its .pyc, so nothing
regenerates stop-report.md; r1_playcap_watch.py:161 IS the lowercase
`glob.glob(os.path.join(out,"save","*.sav"))` poll line; r1_slot.py:49 IS the
`.anch-cache.json` path inside anchors_cached(), so the TOOL_ARTIFACTS
exclusion (r1_idle_probe.py:118) still names the right file. Honest scope
note recorded (not fixed): A5 walks only the capture dir
(r1_idle_probe.py os.walk over os.path.dirname(TIMELINE)), so a slot written
OUTSIDE work/r1/playcap would still be invisible to it; no such file exists
and the game writes its ring slots into the watched save dir (20/20 t149), so
it is an accepted boundary. Infra unchanged since t112 (Xvfb 1196 / x11vnc
1207 / watcher 27774; x11vnc.log 2026-10-27 17:30:18/30114 — zero connects);
probe children 169020/169107 per the t118 noise law; /tmp/{a,b}.txt scratch
deleted. NO row closed (strict-close honest negative), no law falsified. NEXT
stays IDLE; the t113 LOOP-END PROPOSAL stands. Gate 0.

T149 LANDED (IDLE re-check #36 — no trigger fired; deliverables:
docs/re/stop-report.md §42 appended, docs/re/_wip_t149.md, scripts/r1_idle_probe.py
(+A5 leg, +TOOL_ARTIFACTS); no ledger row touched, game/ untouched, no watch or
census run against the live capture). (1) Trigger (A) NEGATIVE — probe RC=0 at
01:47:58 (cutoff 01:47:06): newest playcap dir playcap-20261014-224611; timeline
mtime_ns 1793043841304000000 / 5691796463 B (39th consecutive byte-identical
reading t111..t149; independently re-statted outside the probe — exact match);
zero dosbox procs; find sweep non-loop none; A4 watcher ALIVE pid 27774, and a
deeper read outside the probe shows it parked in hrtimer_nanosleep (State S, i.e.
the 5 s poll tick, not wedged in I/O) with fds 1/2->watch.out,
3->live-timeline.jsonl, 4->watch.log open for append. (2) Trigger (B) NEGATIVE —
clean tracked tree at 082866b, no STEERING, prompt-71 vs prompt-70 (58/58)
digit-stripped delta 0, B3 HEAD == journal sha 082866b. §3 outstanding after
thirty-six idle turns. (3) NEW EVIDENCE CLASS FOR THE (A) NEGATIVE — the
collector was shown FUNCTIONAL, not merely alive (t145 law one level deeper):
`python3 scripts/r1_playcap_watch.py /tmp/t149-watch --once` over two copied ring
slots emitted 2 valid JSONL rows (t=1254, mine_any=36 full=32 planets=36,
DAT_482fb=14/50, 38 ships) and a second pass re-deduped to 0 new rows (t85b `seen`
law holds); the live timeline was never written and the pristine dir never
mounted. (4) THE FINDING THAT MATTERS — that same test exposed an ingestion
asymmetry: the watcher reads only lowercase `save/*.sav`, so a save file it cannot
name is invisible to every (A) leg at once (no new playcap dir, no timeline
growth, no dosbox proc). All 20 real ring slots are lowercase and valid ZIPs, so
there is no live blind spot today [verified]; A5 now makes the shape visible
instead of changing the watcher (restarting pid 27774 to make the glob
case-insensitive trades a provably-inert asymmetry for the t147 failure shape —
declined). (5) SELF-INFLICTED FALSE POSITIVE FOUND AND FIXED — my scratch run
refreshed work/r1/.anch-cache.json (r1_slot.py:49) and the find sweep armed all of
(A) on that single file; encoded as TOOL_ARTIFACTS. LESSON GENERALISED: the probe
must not treat its OWN toolchain's writes as user evidence — before trusting a
find-sweep arm, ask which loop tools can write that path. One patch bug
self-inflicted, caught by running the tool: a dropped closing quote in the
find-sweep line (SyntaxError line 112) — py_compile before the fixture matrix
caught the repair. A5 fixture matrix validated by real execution (all-lowercase ->
none; uppercase VALID-zip -> flagged; non-zip .SAV -> correctly not listed;
uppercase removed -> none) and post-patch real state RC=0 "A5 ... none
(save/*.sav = 20, all match the watcher glob)". FUTURE TURNS: if the user ever
places a played slot with a non-matching name, A5 CAUTION means adjudicate that
file directly — do not read the (A) NEGATIVE as "no sitting happened".
T148 LANDED (IDLE re-check #35 — no trigger fired; deliverables:
docs/re/stop-report.md §41 appended, docs/re/_wip_t148.md; no ledger row
touched, no code changed, no watch/census run per §6 discipline). (1) Trigger
(A) NEGATIVE — probe RC=0 at 01:41:11 (cutoff 01:39:21 from the iter-*.log
name): newest playcap dir playcap-20261014-224611; live-timeline.jsonl
mtime_ns 1793043841304000000 / 5691796463 B (38th consecutive byte-identical
reading t111..t148); zero dosbox procs; find sweep 4 files, non-loop: none;
A4 watcher ALIVE pid 27774 => (A) fully adjudicated; r1_t85g_sitting.py
correctly not run. (2) Trigger (B) NEGATIVE — clean tracked tree at 153a6f4,
no STEERING, prompt-70 vs prompt-69 (58/58 lines) digit-stripped delta 0, B3
HEAD == journal sha 153a6f4. §3 answer outstanding after thirty-five idle
turns. (3) THE ITERATION'S VALUE — t147's NEAR-MISS law run PREEMPTIVELY:
every load-bearing constant in the verdict resolved from source
(r1_idle_probe.py:51-56) and independently re-statted before banking (size
5691796463 / mtime_ns 1793043841304000000 — exact match); fresh-reader
reproducibility confirmed, zero divergence. No new coverage hole: reviewed
the full (A)/(B) trigger surface against stop-report §3/§6 — every documented
user-answer route has an adjudicating leg. One asymmetry documented and
deliberately declined: the find-sweep cutoff is session-start, but a real
capture always also makes a playcap-<ts> dir and grows the timeline, so the
leg is redundant-not-blind there; tightening it would add false-positive
surface for no proven gain. Infra unchanged since t112 (Xvfb 1196 / x11vnc
1207 / watcher 27774; x11vnc.log 2026-10-27 17:30:18/30114 — zero connects);
transients 165351 (harness) / 165418 (probe child) per the t118 noise law.
Bank hygiene checked fresh: grep -rln stop-report scripts/ -> only
r1_idle_probe.py + pycache; zero diff vs HEAD at 1292 lines before appending
§41. NO row closed (strict-close honest negative), no law falsified. NEXT
stays IDLE; the t113 LOOP-END PROPOSAL stands. Gate 0.

T147 LANDED (IDLE re-check #34 — no trigger fired; deliverables:
scripts/r1_idle_probe.py (A4) leg, docs/re/stop-report.md §40,
docs/re/_wip_t147.md; no ledger row touched, no rewrite/ change, no
watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE — probe RC=0 at
01:22:47 (cutoff 01:21:48 from the iter-*.log name): newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B (37th consecutive byte-identical reading t111..t147); zero dosbox
procs; find sweep 4 files, non-loop: none; r1_t85g_sitting.py correctly not
run. (2) Trigger (B) NEGATIVE — clean tracked tree at 4ad8a23, no STEERING,
prompt-69 vs prompt-68 (58/58 lines) digit-stripped delta 0, B3 HEAD == journal
sha 4ad8a23 (row 68 hand-re-verified with cat -A). §3 answer outstanding after
thirty-four idle turns. (3) THE ITERATION'S VALUE — hole (A4): every (A) leg
observes what scripts/r1_playcap_watch.py WRITES, so a dead watcher on an
otherwise-healthy box (daemons persist, dosbox exits after a completed sitting)
reads NEGATIVE over a real sitting forever; infra() only pattern-matched
Xvfb|x11vnc|python3 and asserted liveness in prose. Fixed by matching the
interpreted script at argv[1] over ps -eo pid=,args= in Python; dead => CAUTION
+ NOT ADJUDICATED + RC=2, never armed (absence of signal != absence of event).
First draft's substring fallback self-matched through the test shell's own env
assignment — t114 trap caught by REAL EXECUTION, not review. Three-branch
validation: real ALIVE RC=0; forced-dead RC=2; bash -c launch no self-match.
NEAR-MISS LAW banked: before accusing the probe of fabricating output, resolve
its constants from source (PLAYCAP=work/r1 => work/r1/vnc/x11vnc.log exists
exactly as printed 17:30:18.172/30114) — my composed playcap/vnc path was the
bug. Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774 with
fds on live-timeline.jsonl + watch.out + watch.log verified this run);
transients 163246 (harness mcp_death_supervisor) / 163362 (probe child) per the
t118 noise law. Bank hygiene checked fresh: zero diff vs HEAD before appending
§40; grep -rln stop-report scripts/ -> only r1_idle_probe.py + pycache. NO row
closed (strict-close honest negative). NEXT stays IDLE. Gate 0.

T146 LANDED (IDLE re-check #33 — no trigger fired; deliverables:
scripts/r1_idle_probe.py (B3) leg, docs/re/stop-report.md §39,
docs/re/_wip_t146.md; no ledger row touched, no rewrite/ change, no
watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE — probe RC=0 at
01:01:44 (cutoff 01:00:00 from the iter-*.log name): newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B (36th consecutive byte-identical reading t111..t146); zero dosbox
procs; find sweep 4 files, non-loop: none; r1_t85g_sitting.py correctly not
run. (2) Trigger (B) NEGATIVE — clean tracked tree at 7d2ccd7, no STEERING,
prompt-68 vs prompt-67 (58/58 lines) digit-stripped delta 0. §3 answer
outstanding after thirty-three idle turns. (3) THE ITERATION'S VALUE — hole
(B3) found by generalising the t145 method: ALL four (B) legs compared the
WORKING TREE, so a user decision delivered as a clean COMMIT (the normal way
work lands here — edit rewrite/, commit) moved HEAD and every leg printed
NEGATIVE; 32 turns adjudicated (B) on uncommitted state only, and subject
convention is no backstop (123 repo commits don't match ^t<digits>:). Fixed
via the measured journal law (journal.tsv is written AFTER each commit, last
tab field starts with that iteration's sha — verified row 67 7d2ccd7 == HEAD,
ct 00:58:12): B3 compares HEAD vs journal sha, enumerates the range with
--name-only ('C ' commit-line prefix), arms ONLY on a foreign path, CAUTION
(not trigger) for loop-confined divergence, explicit NOT-adjudicated note if
the journal is unreadable; R1_JOURNAL env override for testing. Validated by
real execution on five branches then fixtures deleted: real NEGATIVE RC=0;
journal-at-row-66 CAUTION RC=0 (t145 was loop-owned-only — correct);
journal-at-row-1 (2e50020) ARMED RC=1 naming rewrite/+gate.sh+t86..t145
scripts; deadbeef ancestor diverged ARM RC=1; missing file NOT-adjudicated
RC=0. Two self-inflicted patch bugs caught pre-run by post-patch reading:
git format '%h' inside a Python %-format, then a 1-specifier format with a
2-tuple — double-%% + two %s is what shipped. Infra unchanged since t112
(Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log 2026-10-27 17:30:18/
30114 — zero connects); transients 161126 (harness runner) / 161175 (probe
child) per the t118 noise law. Bank hygiene checked fresh: grep -rln
stop-report scripts/ -> only r1_idle_probe.py + pycache; zero diff vs HEAD
before appending §39. NO row closed (strict-close honest negative):
ledger_audit rows=18 open=[OQ-003,OQ-005,OQ-016,OQ-019,OQ-021,OQ-023]
closed=12, LEDGER AUDIT OK. NEXT stays IDLE. Gate 0. Commit subject kept
short per the t145 law.

T145 LANDED (IDLE re-check #32 — no trigger fired; deliverables:
scripts/r1_idle_probe.py (B2) leg + HEAD-echo trim, docs/re/stop-report.md §38,
docs/re/_wip_t145.md; no ledger row touched, no rewrite/ change, no watch/census
run per §6 discipline). (1) Trigger (A) NEGATIVE — probe RC=0 at 00:44:23
(cutoff 00:43:18 from the iter-*.log name): newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B (35th consecutive byte-identical reading t111..t145); zero dosbox
procs; find sweep 4 files, non-loop: none; r1_t85g_sitting.py correctly not run.
(2) Trigger (B) NEGATIVE — clean tracked tree at de16f04 pre-edit, no STEERING
file, prompt-67 vs prompt-66 (58/58 lines) digit-stripped delta 0, no delta
outside loop-owned paths. §3 answer outstanding after thirty-two idle turns.
(3) THE ITERATION'S VALUE — a coverage hole in the idle probe, found by asking
what the tool DOES with prompts rather than whether it reads them: t144 banked
"the TOOL is immune (r1_idle_probe.py:82-84 picks the prompt by mtime)" while
those lines are the fallback session-start cutoff and the tool's only steering
leg was an existence glob over docs/STEERING* — so the documented prepended-
prompt-note route could NEVER arm (B), for every idle turn since the tool
shipped, and the hand check that did cover it was discouraged by the NEXT ACTION
text. Fixed in code (numeric prompt sort + digit-stripped unified diff, arms on
content delta, annotates numbering drift) and verified on all four branches by
real execution: real state NEGATIVE RC=0; prepended note RE-ARM; word-level edit
ARMED RC=1; digit-only diff line NEGATIVE RC=0 with the drift annotation. Also
trimmed the HEAD echo to 130 chars — trigger_b() printed `git log --oneline -1`
whole and idle subjects grow monotonically (800->1310 chars over the last 25
commits), so each re-check re-read the previous LANDED summary; FUTURE TURNS:
keep commit subjects under ~200 chars, STATE.md's LANDED block is the record.
Tester lesson banked §38: delete the positive fixture BEFORE running the negative
control (my first control compared prompt-99-vs-98 because prompt-98 had been
removed but 99 was still there), and `RC=$?` after a pipe reads grep, not the
probe. Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log 2026-10-27 17:30:18/30114 — zero connects); transient 158952 (harness
mcp_death_supervisor --parent-pgid 158932) per the t118 noise law. Bank hygiene
checked fresh: grep -rln stop-report scripts/ -> only r1_idle_probe.py + pycache;
1117 lines zero diff vs HEAD before appending §38. NO row closed (strict-close
honest negative): ledger_audit rows=18 open=[OQ-003,OQ-005,OQ-016,OQ-019,OQ-021,
OQ-023] closed=12, LEDGER AUDIT OK. NEXT stays IDLE. Gate 0.


T144 LANDED (IDLE re-check #31 — no trigger fired; deliverables:
docs/re/stop-report.md §37 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 00:37:04 (session start 00:35:19):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (34th consecutive byte-identical reading
t111..t144); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at ffd9e55 (diff HEAD --name-only empty, status --porcelain empty,
no untracked), no STEERING file, prompt-66.txt identical to prompt-65.txt after
digit-stripping (diff -u 0 lines, both 58 lines), no delta outside loop-owned
paths. §3 answer outstanding after thirty-one idle turns. THE ITERATION'S
VALUE — NEW PROBE PITFALL banked in §37 and in the NEXT ACTION block: the hand
steering check enumerated prompts with `ls -1 | tail -1`, which on
`prompt-*.txt` returns prompt-9.txt (lexical order) and diffs the iteration's
real prompt against a prompt ~57 turns old. SILENT defect: the loop prompt text
is stable, so the verdict came out NEGATIVE for the wrong reason and would
mask any steering note added after single-digit numbering. Re-ran with `ls -1v`
(prompt-66 vs prompt-65, 58 lines, diff 0) before accepting. Checked the tool:
`r1_idle_probe.py:82-84` picks the session-start prompt by mtime
(`sorted(glob, key=getmtime)[-1]`), so the tool was never exposed — same lesson
as t117: trust the tool's enumeration over a hand-globbed glob. No tool change
made (the defect is in the hand procedure, now documented). Infra unchanged
since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log
2026-10-27 17:30:18/30114 — zero connects against the t111-FIXED launch path);
transients 157622 (harness mcp_death_supervisor.py, identified via ps -o args=)
/ 157674 (own probe child) per the t118 noise law, correctly ignored. Bank
hygiene re-checked fresh: grep -rln stop-report scripts/ hits only
r1_idle_probe.py + its pycache, zero diff vs HEAD at 1072 lines pre-append, no
regeneration trap. NO row closed (strict-close honest negative), no law
falsified. NEXT stays IDLE. Gate 0, LEDGER AUDIT OK

T143 LANDED (IDLE re-check #30 — no trigger fired; deliverables:
docs/re/stop-report.md §36 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 00:30:54 (session start 00:29:08):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (33rd consecutive byte-identical reading
t111..t143); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 2c6c274 (diff HEAD --name-only empty, status --porcelain empty,
no untracked), no STEERING file, prompt-65.txt identical to prompt-64.txt after
digit-stripping (diff -u 0 lines, both 58 lines), no delta outside loop-owned
paths. §3 answer outstanding after thirty idle turns. Infra unchanged since t112
(Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log 2026-10-27 17:30:18/30114 —
zero connects against the t111-FIXED launch path); transients 156466 (harness
mcp_death_supervisor.py --parent-pgid 156446, identified via ps -o args=) /
156528 (own kernel/probe child, verified gone on ps -p) per the t118 noise law,
correctly ignored. Bank hygiene re-checked fresh: grep -rln stop-report scripts/
hits only r1_idle_probe.py + its pycache, zero diff vs HEAD at 1039 lines
pre-append, no regeneration trap. stop-report §36. NO row closed (strict-close
honest negative), no law falsified. NEXT stays IDLE. Gate 0, LEDGER AUDIT OK

T142 LANDED (IDLE re-check #29 — no trigger fired; deliverables:
docs/re/stop-report.md §35 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 00:24:54 (session start 00:23:52):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (32nd consecutive byte-identical reading
t111..t142); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 6b68faa (diff HEAD --name-only empty, status --porcelain empty,
no untracked), no STEERING file, prompt-64.txt identical to prompt-63.txt after
digit-stripping (diff -q clean). §3 answer outstanding after twenty-nine idle
turns. Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log 2026-10-27 17:30:18/30114 — zero connects against the t111-FIXED
launch path); transients 155315 (harness mcp_death_supervisor.py --parent-pgid
155295, identified via ps -o args=) / 155367 (this session's own
hermes_kernel_runner.py) / 155401 (probe child, gone on ps -p) per the t118
noise law, correctly ignored. Bank hygiene re-checked fresh: grep -rln
stop-report scripts/ hits only r1_idle_probe.py + its pycache, zero diff vs
HEAD at 1005 lines pre-append, no regeneration trap. stop-report §35. NO row
closed (strict-close honest negative), no law falsified. NEXT stays IDLE.
Gate 0, LEDGER AUDIT OK

T141 LANDED (IDLE re-check #28 — no trigger fired; deliverables:
docs/re/stop-report.md §34 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 00:19:44 (session start 00:18:53):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (31st consecutive byte-identical reading
t111..t141); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 17dfdd5 (diff HEAD --stat empty, status --porcelain empty,
--untracked-files=all empty), no STEERING file, prompt-63.txt identical to
prompt-62.txt after digit-stripping (diff -q clean). §3 answer outstanding
after twenty-eight idle turns. Infra unchanged since t112 (Xvfb 1196 / x11vnc
1207 / watcher 27774; x11vnc.log 2026-10-27 17:30:18/30114 — zero connects
against the t111-FIXED launch path); transients 154161 (identified by
ps -o args= as the harness's own mcp_death_supervisor.py --parent-pgid 154141)
/ 154226 (verified gone on ps -p) per the t118 noise law, correctly ignored.
Bank hygiene re-checked fresh: grep -rln stop-report scripts/ hits only
r1_idle_probe.py + its pycache, zero diff vs HEAD at 972 lines pre-append,
no regeneration trap. stop-report §34. NO row closed (strict-close honest
negative), no law falsified. NEXT stays IDLE. Gate 0, LEDGER AUDIT OK

T140 LANDED (IDLE re-check #27 — no trigger fired; deliverables:
docs/re/stop-report.md §33 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 00:14:34 (session start 00:12:50):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (30th consecutive byte-identical reading
t111..t140); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 52d8b81 (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-62.txt identical to prompt-61.txt after
digit-stripping (unified diff 0 lines, both 58 lines). §3 answer outstanding
after twenty-seven idle turns. Infra unchanged since t112 (Xvfb 1196 / x11vnc
1207 / watcher 27774; x11vnc.log 2026-10-27 17:30:18/30114 — zero connects
against the t111-FIXED launch path); transients 153003 (harness runner,
elapsed matches session start) / 153055 (probe child, verified gone on ps -p)
per the t118 noise law, correctly ignored. Bank hygiene re-checked fresh
before appending: grep -rln stop-report scripts/ hits only r1_idle_probe.py +
its pycache, and the file had zero diff against HEAD at 940 lines —
hand-authoring safe. NO row closed (strict-close honest negative), no law
falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands. Gate 0,
LEDGER AUDIT OK

T139 LANDED (IDLE re-check #26 — no trigger fired; deliverables:
docs/re/stop-report.md §32 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 00:08:29 (session start 00:06:44):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (29th consecutive byte-identical reading
t111..t139); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 7f3a589 (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-61.txt identical to prompt-60.txt after
digit-stripping (unified diff 0 lines). §3 answer outstanding after twenty-six
idle turns. Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher
27774; x11vnc.log 2026-10-27 17:30:18/30114 — zero connects against the
t111-FIXED launch path); transients 151887 (harness runner) / 151940 (probe
child, gone on ps -p re-check) per the t118 noise law, correctly ignored. Bank
hygiene re-checked fresh before appending: grep -rln stop-report scripts/ hits
only r1_idle_probe.py + its pycache, and the file had zero diff against HEAD at
903 lines — hand-authoring safe. NO row closed (strict-close honest negative),
no law falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands. Gate 0,
LEDGER AUDIT OK

T138 LANDED (IDLE re-check #25 — no trigger fired; deliverables:
docs/re/stop-report.md §31 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 00:01:59 (session start 00:00:16 —
first idle turn after the calendar rollover to 2026-10-28; the probe derives
its find cutoff from process start, so midnight needed no adjustment): newest
playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (28th consecutive byte-identical reading
t111..t138); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 9b75419 (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-60.txt identical to prompt-59.txt after
digit-stripping (unified diff 0 lines, both 58 lines). §3 answer outstanding
after twenty-five idle turns. Infra unchanged since t112 (Xvfb 1196 / x11vnc
1207 / watcher 27774; x11vnc.log 2026-10-27 17:30:18/30114 — zero connects
against the t111-FIXED launch path); transients 150738/150789 per the t118
noise law, both verified gone on `ps -p` re-check, correctly ignored. Bank
hygiene re-checked fresh before appending: grep -rln stop-report scripts/ hits
only r1_idle_probe.py + its pycache, and the file had zero diff against HEAD at
870 lines — hand-authoring safe. NO row closed (strict-close honest negative),
no law falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands. Gate 0,
LEDGER AUDIT OK

T137 LANDED (IDLE re-check #24 — no trigger fired; deliverables:
docs/re/stop-report.md §30 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 23:56:01 (session start 23:55:04):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (27th consecutive byte-identical reading
t111..t137); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 295c0e3 (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-59.txt identical to prompt-58.txt after
digit-stripping (unified diff 0 lines). §3 answer outstanding after
twenty-four idle turns. Infra unchanged since t112 (Xvfb 1196 / x11vnc
1207 / watcher 27774; x11vnc.log 2026-10-27 17:30:18/30114 — zero connects
against the t111-FIXED launch path); transients 149557/149638 per the
t118 noise law, correctly ignored. Bank hygiene re-checked fresh before
appending: grep -rln stop-report scripts/ hits only r1_idle_probe.py + its
pycache, and the file had zero diff against HEAD at 841 lines — hand-authoring
safe. NO row closed (strict-close honest negative), no law falsified. NEXT
stays IDLE; the t113 LOOP-END PROPOSAL stands. Gate 0, LEDGER AUDIT OK

T136 LANDED (IDLE re-check #23 — no trigger fired; deliverables:
docs/re/stop-report.md §29 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 23:51:14 (session start 23:50:16):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (26th consecutive byte-identical reading
t111..t136); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 2c62078 (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-58.txt identical to prompt-57.txt after
digit-stripping (unified diff 0 lines, both 58 lines). §3 answer outstanding
after twenty-three idle turns. Infra unchanged since t112 (Xvfb 1196 / x11vnc
1207 / watcher 27774; x11vnc.log 2026-10-27 17:30:18/30114 — zero connects
against the t111-FIXED launch path); transients 148438/148483/148498 per the
t118 noise law, correctly ignored. Bank hygiene re-checked fresh before
appending: grep -rln stop-report scripts/ hits only r1_idle_probe.py + its
pycache, and the file had zero diff against HEAD at 812 lines — hand-authoring
safe. NO row closed (strict-close honest negative), no law falsified. NEXT
stays IDLE; the t113 LOOP-END PROPOSAL stands. Gate 0, LEDGER AUDIT OK

T135 LANDED (IDLE re-check #22 — no trigger fired; deliverables:
docs/re/stop-report.md §28 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 23:45:53 (session start 23:44:08):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (25th consecutive byte-identical reading
t111..t135); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 815a9fe (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-57.txt identical to prompt-56.txt after
digit-stripping (unified diff 0 lines, both 58 lines). §3 answer outstanding
after twenty-two idle turns. Infra unchanged since t112 (Xvfb 1196 / x11vnc
1207 / watcher 27774; x11vnc.log 2026-10-27 17:30:18/30114 — zero connects
against the t111-FIXED launch path); transients 147254/147306 per the t118
noise law, correctly ignored. Bank hygiene re-checked fresh before appending:
grep -rln stop-report scripts/ hits only r1_idle_probe.py + its pycache, and
the file had zero diff against HEAD at 779 lines — hand-authoring safe. NO row
closed (strict-close honest negative), no law falsified. NEXT stays IDLE; the
t113 LOOP-END PROPOSAL stands. Gate 0, LEDGER AUDIT OK

T134 LANDED (IDLE re-check #21 — no trigger fired; deliverables:
docs/re/stop-report.md §27 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 23:39:50 (session start 23:39:00):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (24th consecutive byte-identical reading
t111..t134); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at a40a7d8 (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-56.txt identical to prompt-55.txt after
digit-stripping (unified diff 0 lines, both 58 lines). §3 answer outstanding
after twenty-one idle turns. Infra unchanged since t112 (Xvfb 1196 / x11vnc
1207 / watcher 27774; x11vnc.log 2026-10-27 17:30:18/30114 — zero connects
against the t111-FIXED launch path); transients 146140/146217 per the t118
noise law, correctly ignored. Bank hygiene: §27 verified hand-authoring safe
(grep -rln stop-report scripts/ = r1_idle_probe.py + pycache only, per t133;
file byte-stable at 746 lines pre-append). NO row closed (strict-close honest
negative), no law falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL
stands. Gate 0, LEDGER AUDIT OK

T133 LANDED (IDLE re-check #20 — no trigger fired; deliverables:
docs/re/stop-report.md §26 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 23:35:10 (session start 23:34:19):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (23rd consecutive byte-identical reading
t111..t133); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 1a1c448 (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-55.txt identical to prompt-54.txt after
digit-stripping (unified diff 0 lines, both 58 lines). §3 answer outstanding
after twenty idle turns. Infra unchanged since t112 (Xvfb 1196 / x11vnc
1207 / watcher 27774; x11vnc.log 17:30:18/30114 — zero connects against the
t111-FIXED launch path); transients 145064/145154 per the t118 noise law,
correctly ignored. Bank-hygiene re-checked fresh: grep -rln stop-report
scripts/ hits only r1_idle_probe.py + its pycache — no regeneration trap.
NO row closed (strict-close honest negative), no law falsified. NEXT stays
IDLE; the t113 LOOP-END PROPOSAL stands. Gate 0, LEDGER AUDIT OK

T132 LANDED (IDLE re-check #19 — no trigger fired; deliverables:
docs/re/stop-report.md §25 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 23:30:25 (session start 23:29:29):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (22nd consecutive byte-identical reading
t111..t132); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 11c105d (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-54.txt identical to prompt-53.txt after
digit-stripping (unified diff 0 lines, both 58 lines). §3 answer outstanding
after nineteen idle turns. Infra unchanged since t112 (Xvfb 1196 / x11vnc
1207 / watcher 27774; x11vnc.log 17:30:18/30114 — zero connects against the
t111-FIXED launch path); transients 143957/144039 per the t118 noise law,
correctly ignored. Bank-hygiene re-checked fresh: grep -rln stop-report
scripts/ hits only r1_idle_probe.py + its pycache — no regeneration trap.
NO row closed (strict-close honest negative), no law falsified. NEXT stays
IDLE; the t113 LOOP-END PROPOSAL stands. Gate 0, LEDGER AUDIT OK

T131 LANDED (IDLE re-check #18 — no trigger fired; deliverables:
docs/re/stop-report.md §24 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 23:25:49 (session start 23:24:51):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (21st consecutive byte-identical reading
t111..t131); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 555817b (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-53.txt identical to prompt-52.txt after
digit-stripping (unified diff 0 lines, both 58 lines). §3 answer outstanding
after eighteen idle turns. Infra unchanged since t112 (Xvfb 1196 / x11vnc
1207 / watcher 27774; x11vnc.log 17:30:18/30114 — zero connects against the
t111-FIXED launch path); transients 142872/142952 per the t118 noise law,
correctly ignored. Bank-hygiene re-checked fresh via probe output:
grep -rln stop-report scripts/ hits only r1_idle_probe.py + its pycache — no
regeneration trap. NO row closed (strict-close honest negative), no law
falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands. Gate 0,
LEDGER AUDIT OK

T130 LANDED (IDLE re-check #17 — no trigger fired; deliverables:
docs/re/stop-report.md §23 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 23:21:02 (session start 23:20:07):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (20th consecutive byte-identical reading
t111..t130); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 69ed9b9 (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-52.txt identical to prompt-51.txt after
digit-stripping (unified diff 0 lines, both 58 lines). §3 answer outstanding
after seventeen idle turns. Infra unchanged since t112 (Xvfb 1196 / x11vnc
1207 / watcher 27774; x11vnc.log 17:30:18/30114 — zero connects against the
t111-FIXED launch path); transients 141762/141834/141847 per the t118 noise
law, correctly ignored. Bank-hygiene re-checked fresh via probe output:
grep -rln stop-report scripts/ hits only r1_idle_probe.py + its pycache — no
regeneration trap. NO row closed (strict-close honest negative), no law
falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands. Gate 0,
LEDGER AUDIT OK

T129 LANDED (IDLE re-check #16 — no trigger fired; deliverables:
docs/re/stop-report.md §22 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 23:16:09 (session start 23:15:04):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (19th consecutive byte-identical reading
t111..t129); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at c933845 (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-51.txt identical to prompt-50.txt after
digit-stripping (unified diff 0 lines, both 58 lines), no delta outside
loop-owned paths. §3 answer outstanding after sixteen idle turns. Infra
unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log
17:30:18/30114 — zero connects against the t111-FIXED launch path); transients
140640 / 140735 (this iteration's own probe + shell) per the t118 noise law,
correctly ignored. Bank-hygiene re-checked fresh: grep -rln stop-report scripts/
hits only r1_idle_probe.py + its pycache — no regeneration trap. NO row closed
(strict-close honest negative), no law falsified. NEXT stays IDLE; the t113
LOOP-END PROPOSAL stands. Gate 0, LEDGER AUDIT OK

T128 LANDED (IDLE re-check #15 — no trigger fired; deliverables:
docs/re/stop-report.md §21 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 23:10:23 (session start 23:08:40):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (18th consecutive byte-identical reading
t111..t128); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at fa773c4 (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-50.txt identical to prompt-49.txt after
digit-stripping (unified diff 0 lines, both 58 lines), no delta outside
loop-owned paths. §3 answer outstanding after fifteen idle turns. Infra
unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log
17:30:18/30114 — zero connects against the t111-FIXED launch path); transients
139526 / 139578 per the t118 noise law, correctly ignored. Bank-hygiene
re-checked fresh: grep -rln stop-report scripts/ hits only r1_idle_probe.py +
its pycache — no regeneration trap. NO row closed (strict-close honest
negative), no law falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL
stands. Gate 0, LEDGER AUDIT OK

T127 LANDED (IDLE re-check #14 — no trigger fired; deliverables:
docs/re/stop-report.md §20 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 23:01:55 (session start 23:00:51):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (17th consecutive byte-identical reading
t111..t127); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 690a85d (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-49.txt identical to prompt-48.txt after
digit-stripping (diff 0 lines, both 58 lines), no delta outside loop-owned
paths. §3 answer outstanding after fourteen idle turns. Infra unchanged since
t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log 17:30:18/30114 — zero
connects against the t111-FIXED launch path); transients 137997 / 138092 per
the t118 noise law, correctly ignored. Bank-hygiene re-checked fresh (t126 had
skipped it): grep -rln stop-report scripts/ hits only r1_idle_probe.py + its
pycache — no regeneration trap. NO row closed (strict-close honest negative),
no law falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands. Gate 0,
LEDGER AUDIT OK

T126 LANDED (IDLE re-check #13 — no trigger fired; deliverables:
docs/re/stop-report.md §19 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 22:56:55 (session start 22:55:47):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (16th consecutive byte-identical reading
t111..t126); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 9f1e2ab (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-48.txt identical to prompt-47.txt after
digit-stripping (diff 0 lines), no delta outside loop-owned paths. §3 answer
outstanding after thirteen idle turns. Infra unchanged since t112 (Xvfb 1196 /
x11vnc 1207 / watcher 27774; x11vnc.log 17:30:18 / 30114 B — zero connects
against the t111-FIXED launch path); transients 136797 / 136851 / 136888 per
the t118 noise law, correctly ignored. No row closed (strict-close honest
negative), no law falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL
stands. Gate 0, LEDGER AUDIT OK

T125 LANDED (IDLE re-check #12 — no trigger fired; deliverables:
docs/re/stop-report.md §18 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 22:51:57 (session start 22:50:52):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (15th consecutive byte-identical reading
t111..t125); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 86900c5 (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-47.txt identical to prompt-46.txt after
digit-stripping (diff 0 lines), no delta outside loop-owned paths. §3 answer
outstanding after twelve idle turns. Infra unchanged since t112 (Xvfb 1196 /
x11vnc 1207 / watcher 27774; x11vnc.log 17:30:18 / 30114 B — zero connects
against the t111-FIXED launch path); transients 135661 / 135777 per the t118
noise law, correctly ignored. Bank-hygiene re-checked fresh: grep -rln
stop-report scripts/ hits only r1_idle_probe.py + its pycache, no
regeneration trap. NO row closed (strict-close honest negative), no law
falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands.
Gate 0, LEDGER AUDIT OK

T124 LANDED (IDLE re-check #11 — no trigger fired; deliverables:
docs/re/stop-report.md §17 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 22:47:01 (session start 22:45:19):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (14th consecutive byte-identical reading
t111..t124); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 17846a7 (diff HEAD empty, status --porcelain empty), no
STEERING file, prompt-46.txt identical to prompt-45.txt after digit-stripping
(diff empty), no delta outside loop-owned paths. §3 answer outstanding after
eleven idle turns. Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 /
watcher 27774; x11vnc.log 17:30:18 / 30114 B); transients 134591 (this
session's runner) + probe child 134644 (gone on ps re-check) ignored per the
t118 noise law. (3) Bank-hygiene re-checked fresh: grep -rln stop-report
scripts/ hits only r1_idle_probe.py + its __pycache__ bytecode — no
regeneration trap, hand-authoring safe. NO row closed (strict-close honest
negative), no law falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL
stands. Gate 0, LEDGER AUDIT OK

T123 LANDED (IDLE re-check #10 — no trigger fired; deliverables:
docs/re/stop-report.md §16 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` RC=0 at 22:40:57 (session start 22:39:11):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (13th consecutive byte-identical reading
t111..t123); zero dosbox procs; session-start find sweep 4 files, non-loop:
none. r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 00728b4 (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-45.txt identical to prompt-44.txt after
digit-stripping (diff empty), no delta outside loop-owned paths. §3 answer
outstanding after ten idle turns. Infra unchanged since t112 (Xvfb 1196 /
x11vnc 1207 / watcher 27774; x11vnc.log 17:30:18 / 30114 B); transients
133462/133529 (this session's runner + probe child) ignored per the t118
noise law. (3) Bank-hygiene re-checked fresh: `grep -rln stop-report scripts/`
hits only r1_idle_probe.py plus its __pycache__ bytecode — no regeneration
trap, hand-authoring safe. NO row closed (strict-close honest negative), no
law falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL is re-endorsed in
§16 (ten idle turns have produced zero measurement — an idle session cannot
close a capture-gated or decision-gated row). Gate 0, LEDGER AUDIT OK

T122 LANDED (IDLE re-check #9 — no trigger fired; deliverables:
docs/re/stop-report.md §15 appended; no ledger row touched, no code
changed, no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` at 22:35:06.625 RC=0: newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B (12th consecutive byte-identical reading t111..t122); zero
dosbox procs; session-start (22:33:22) find sweep 4 files, all
work/r1/loop/. r1_t85g_sitting.py correctly not run. (2) Trigger (B)
NEGATIVE — clean tracked tree at 7c9a18f, no STEERING file, prompt-44.txt
identical to prompt-43.txt after digit-stripping (diff empty), no delta
outside loop-owned paths. §3 answer outstanding after nine idle turns.
Infra unchanged since t112 (Xvfb 1196/x11vnc 1207/watcher 27774;
x11vnc.log 17:30:18/30114); transients 132359/132412 (this session's runner
+ probe child) ignored per the t118 noise law. (3) Bank-hygiene re-checked
fresh: grep -rln stop-report scripts/ hits only r1_idle_probe.py plus its
__pycache__ bytecode — no regeneration trap, hand-authoring safe. NO row
closed (strict-close honest negative), no law falsified. NEXT stays IDLE.
Gate 0, LEDGER AUDIT OK

T121 LANDED (IDLE re-check #8 — no trigger fired; deliverables:
docs/re/stop-report.md §14 appended; no ledger row touched, no code
changed, no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` at 22:29:23 RC=0: newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B (11th consecutive byte-identical reading t111..t121); zero
dosbox procs; session-start (22:28:18) find sweep 4 files, all
work/r1/loop/. r1_t85g_sitting.py correctly not run. (2) Trigger (B)
NEGATIVE — clean tracked tree at e7d736c, no STEERING file, prompt-43.txt
identical to prompt-42.txt after digit-stripping (diff empty), no delta
outside loop-owned paths. §3 answer outstanding after eight idle turns.
Infra unchanged since t112 (Xvfb 1196/x11vnc 1207/watcher 27774;
x11vnc.log 17:30:18/30114); transients 131136/131252 (this session's runner
+ probe child) ignored per the t118 noise law. (3) Bank-hygiene re-checked
fresh: grep -rln stop-report scripts/ hits only r1_idle_probe.py's docstring
— no script regenerates the bank, hand-authoring is safe. NO row closed
(strict-close honest negative), no law falsified. NEXT stays IDLE.

T120 LANDED (IDLE re-check #7 — no trigger fired; deliverables:
docs/re/stop-report.md §13 appended; no ledger row touched, no code
changed, no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` at 22:24:09 RC=0: newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B (10th consecutive byte-identical reading t111..t120); zero
dosbox procs; session-start (22:22:27) find sweep 4 files, all
work/r1/loop/. r1_t85g_sitting.py correctly not run. (2) Trigger (B)
NEGATIVE — clean tracked tree at 9b9c291, no STEERING file, prompt-42.txt
identical to prompt-41.txt after digit-stripping (diff empty), no delta
outside loop-owned paths. §3 answer outstanding after seven idle turns.
Infra unchanged since t112 (Xvfb 1196/x11vnc 1207/watcher 27774;
x11vnc.log 17:30:18/30114); INFRA-leg transients 130014 (harness loop
runner, started at session start) and 130066 (probe child, gone on re-check)
correctly ignored per the t118 noise law. NO row closed (strict-close honest
negative), no law falsified. NEXT stays IDLE.

T119 LANDED (IDLE re-check #6 — no trigger fired; deliverables:
docs/re/stop-report.md §12 appended; no ledger row touched, no code changed,
no watch/census run per §6 discipline). (1) Trigger (A) NEGATIVE —
`python3 scripts/r1_idle_probe.py` at 22:18:56 RC=0: newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B (9th consecutive byte-identical reading t111..t119); zero
dosbox procs; session-start (22:18:03) find sweep 4 files, all
work/r1/loop/. r1_t85g_sitting.py correctly not run. (2) Trigger (B)
NEGATIVE — clean tracked tree at 110ea35, no STEERING file, prompt-41.txt
identical to prompt-40.txt after digit-stripping (diff empty), no delta
outside loop-owned paths. Infra unchanged since t112 (Xvfb 1196/x11vnc 1207/
watcher 27774; x11vnc.log 17:30:18/30114); probe-own shell children seen per
the t118 noise law, correctly ignored. §3 answer outstanding after six idle
turns. NO row closed (strict-close honest negative), no law falsified. NEXT
stays IDLE.

T118 LANDED (IDLE re-check #5 — no trigger fired; deliverables:
docs/re/_wip_t118.md, stop-report.md §11 appended; no ledger row touched, no
code changed, no watch/census run per §6 discipline). (1) Trigger (A)
NEGATIVE — `python3 scripts/r1_idle_probe.py` at 22:12:21.769 EDT RC=0:
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B, 8th consecutive byte-identical reading
(t111..t118); zero dosbox procs; session-start (22:10:42) find sweep 4 files,
all work/r1/loop/. r1_t85g_sitting.py correctly not run. (2) Trigger (B)
NEGATIVE — clean tracked tree at 35a9027, no STEERING file, prompt-40.txt
byte-identical to prompt-39.txt modulo digits (diff after digit-stripping:
empty — cheaper steering check than grepping instruction prose, since the
standing instruction line itself contains the word "steering"), no delta
outside loop-owned paths; §3 answer outstanding after five idle turns.
(3) TOOL VALIDATED BY A FRESH READER (the iteration's value): t118 is the
first session that ran r1_idle_probe.py without having authored it, and the
verdict was reproducible from the tool's printed evidence alone — every leg
prints its own number, no hand re-derivation needed. No defect found.
(4) NEW NOISE LAW banked (stop-report §11): the probe's INFRA leg also lists
Hermes-own processes (pid 127729 tools/mcp_death_supervisor.py, started at the
harness's own 22:10:42) and the probe's transient children (pid 127778, gone
on `ps -p` re-check — the probe shells out with shell=True, so its git/find/
stat children appear in a mid-run `ps -eo` snapshot). Trigger evidence is
dosbox processes and capture-side files ONLY; never arm on Hermes/probe-own
python rows. (5) Infra alive so the negatives are trustworthy: Xvfb :9 1196,
x11vnc :5910 1207, watcher 27774; x11vnc.log 2026-10-27 17:30:18 / 30114 B
unchanged since t112. (6) Bank-law pre-check: only scripts/r1_idle_probe.py
mentions stop-report (docstring cross-ref), nothing regenerates it.
NEXT = `python3 scripts/r1_idle_probe.py` on the next idle session; loop
stays IDLE at 12 closed / 6 open. NO row closed (strict-close honest
negative); no banked law falsified. Gate 0, LEDGER AUDIT OK

T117 LANDED (IDLE re-check #4 — no trigger fired; deliverables: NEW
scripts/r1_idle_probe.py RC=0, docs/re/_wip_t117.md, stop-report.md §10
appended; no ledger row touched, no code changed, no watch/census run per
§6 discipline). The iteration's value is cost reduction: four consecutive
idle turns had re-implemented the same probe by hand, so it is now a script
that carries the probe laws with it. (1) Trigger (A) NEGATIVE at 21:56:50
manual / re-confirmed by the tool at 22:01:45 — newest playcap dir
20261014-224611; live-timeline.jsonl mtime 2026-10-26 15:44:01.304 /
5691796463 B, 7th consecutive byte-identical reading (t111..t117); zero
dosbox processes; session-start find sweep 4 files, all work/r1/loop/.
r1_t85g_sitting.py correctly not run. (2) Trigger (B) NEGATIVE — clean
tracked tree at 50f098e, no STEERING file, this iteration's harness prompt
(prompt-39.txt) is the generic loop prompt (grep -i steering hits only the
standing instruction line); §3 answer still outstanding. (3) TOOL DEFECTS
found and fixed by execution while authoring (both are traps the next
session hits blind — see stop-report §10): wrong timeline path printed
"timeline missing" while a manual stat succeeded; and `--untracked-files=
all` ARMED trigger (B) on the loop's own mid-iteration files. Hand-typed
baseline ns was also wrong (stat %Y = 1793043841304000000), which produced
an accidental POSITIVE CONTROL: the tool correctly reported ARMED + "timeline
grew past frozen baseline", proving the growth leg is live. (4) Infra alive
so the negatives are trustworthy: Xvfb 1196, x11vnc 1207, watcher
27772+27774 (wrapper+child, normal); x11vnc.log 17:30:18.172 / 30114 B
unchanged since t112, all 138 Client lines predate the t111 DISPLAY fix.
(5) Bank-law pre-check: no script generates stop-report.md or _wip_*.md.
NEXT = `python3 scripts/r1_idle_probe.py` on the next idle session; loop
stays IDLE at 12 closed / 6 open. NO row closed (strict-close honest
negative); no banked law falsified. Gate 0, LEDGER AUDIT OK

T116 LANDED (IDLE re-check #3 — no trigger fired; deliverables:
docs/re/_wip_t116.md, stop-report.md §9 appended; no ledger row touched,
no code changed, no watch/census run per §6 discipline): (1) trigger (A)
measured NEGATIVE fresh at 21:48:52.130 EDT — newest playcap dir
20261014-224611; live-timeline.jsonl mtime 2026-10-26 15:44:01.304 /
5691796463 B, 6th consecutive byte-identical reading (t111..t116); no
dosbox process (`ps -eo comm`, pgrep self-match trap avoided);
find-newermt sweep returned only work/r1/loop/ harness files.
r1_t85g_sitting.py correctly not run. (2) trigger (B) NEGATIVE with a
NEW PROBE PITFALL banked: five docs (re/text, re/modules, re/economy,
re/gizmos, re/fnt) showed post-commit mtimes 21:46:27-41 — cause is THIS
ITERATION'S preflight gate (ran ~21:46, after the t115 commit 21:45:13,
before session start 21:47:01; gate.sh:144-150/281 verify gizmos/economy/
fnt directly) touching them with ZERO content delta (`git diff HEAD`
empty, tree clean incl. untracked). LAW: trigger (B) is adjudicated by
CONTENT diff, never mtime. No STEERING file; §3 answer still outstanding.
(3) Infra alive so the negatives are trustworthy: Xvfb 1196, x11vnc 1207,
watcher 27772+27774 (bash wrapper + python child, normal pair);
x11vnc.log mtime 2026-10-27 17:30:18.172 / 30114 B unchanged since t112 —
zero connects against the t111-FIXED launch path. (4) Bank-law pre-check:
no script generates stop-report.md or _wip_*.md; PLAYTHROUGH.md untouched.
NEXT = same two-trigger probe on the next idle session (stop-report §9
wording + the content-diff rule); loop stays IDLE at 12 closed / 6 open.
NO row closed (strict-close honest negative); no banked law falsified; no
new tool. Gate 0, LEDGER AUDIT OK

T115 LANDED (IDLE re-check #2 — no trigger fired; deliverables:
docs/re/_wip_t115.md, stop-report.md §8 appended; no ledger row touched,
no code changed, no watch/census run per §6 discipline): (1) trigger (A)
measured NEGATIVE fresh at 21:42:23.745 EDT — newest playcap dir
20261014-224611; live-timeline.jsonl mtime 2026-10-26 15:44:01.304 /
5691796463 B, 5th consecutive byte-identical reading (t111..t115); no
dosbox process (`ps -eo comm`, t114's pgrep self-match trap avoided).
PROBE UPGRADE worth keeping: `find work/r1 -type f -newermt <session start>`
returns ONLY harness bookkeeping under work/r1/loop/ (loop.log, iter-*.log,
prompt-37.txt, preflight_gate.log, iter.count, journal.tsv, fail_streak,
post_audit.log) — proves no capture-side file exists anywhere, stronger than
the mtime check alone. r1_t85g_sitting.py correctly not run. (2) trigger (B)
NEGATIVE — clean tree at f1b1fde, no STEERING file, no harness note, no doc
edited post-commit; stop-report §3 answer still outstanding. (3) Infra alive
so the negatives are trustworthy: Xvfb 1196, x11vnc 1207, watcher 27772 +
27774 (bash wrapper + python child; the PAIR is normal, not a duplicate
watcher — do not "fix" it); x11vnc.log mtime 2026-10-27 17:30:18.172 / 30114 B
unchanged since t112 — zero connects against the t111-FIXED launch path.
(4) Bank-law pre-check: grep shows no script generates stop-report.md or
_wip_*.md (hits are comment cross-refs only); PLAYTHROUGH.md untouched.
NEXT = same two-trigger probe on the next idle session (stop-report §8
wording); loop stays IDLE at 12 closed / 6 open. NO row closed
(strict-close honest negative); no banked law falsified; no new tool.
Gate 0, LEDGER AUDIT OK

T114 LANDED (IDLE re-check #1 — no trigger fired; deliverables:
docs/re/_wip_t114.md, stop-report.md §7 appended; no ledger row touched,
no code changed, no watch run per §6 discipline): (1) trigger (A)
measured NEGATIVE fresh — newest playcap dir 20261014-224611;
live-timeline.jsonl mtime 2026-10-26 15:44:01.304 / 5691796463 B,
4th consecutive byte-identical reading (t111/t112/t113/t114); no dosbox
process (ps -eo comm empty for dosbox; NOTE: `pgrep -af dosbox` can
self-match the probing shell's own command line — false positive,
confirm with `pgrep -x dosbox-x` / ps). r1_t85g_sitting.py correctly not
run. (2) trigger (B) measured NEGATIVE — git tree clean at fd49364, no
harness steering note, no STEERING file, no post-commit doc edits.
(3) Watch infra verified alive (Xvfb :9 pid 1196, x11vnc :5910 pid 1207,
watcher pid 27772) so the negative is trustworthy; x11vnc.log mtime
2026-10-27 17:30:18.172 unchanged — still zero VNC connects against the
t111-FIXED launch path. NEXT = same two-trigger probe on the next idle
session (stop-report §7 wording); loop stays IDLE at 12 closed / 6 open.
NO row closed (strict-close honest negative); no banked law falsified;
no new tool. Gate 0, LEDGER AUDIT OK

T113 LANDED (FINAL WATCH + LOOP-END PROPOSAL — idle turn #3; deliverables:
docs/re/stop-report.md §6 NEW dated block, docs/re/_wip_t113.md; no ledger
row touched, no code changed): (1) all watch signals re-measured fresh
21:30 EDT, THIRD consecutive negative — live-timeline.jsonl mtime
2026-10-26 15:44:01.304 / 5691796463 B byte-identical to t111/t112;
newest playcap dir still 20261014-224611; no dosbox process; watch infra
alive (Xvfb :9 pid 1196, x11vnc :5910 pid 1207, watcher pid 27772) so the
negative is trustworthy; r1_t85g_sitting.py correctly NOT run. (2) VNC
signal via /proc/1207/fd — log is work/r1/vnc/x11vnc.log, mtime
2026-10-27 17:30:18.172 UNCHANGED since t112: still zero connect attempts
against the t111-FIXED launch path. (3) NO user decision arrived: git
clean, no docs/ file modified after the t112 commit — assignment branch
(3) applies. (4) LOOP-END PROPOSAL appended (stop-report §6): end at 12
closed / 6 open — capture-gated OQ-016/019/021/023, user-decision-gated
OQ-003/005; re-arm triggers (A) capture dir/timeline growth, (B) §3
answer. NEXT ACTION rewritten to IDLE (no further watches while idle).
NO row closed (strict-close honest negative); no banked law falsified; no
new tool. Gate 0, LEDGER AUDIT OK

T112 LANDED (WATCH task — SITTING WATCH NEGATIVE #2; deliverables:
docs/re/_wip_t112.md; no ledger row touched, no code changed): (1) all watch
signals re-measured fresh 21:20 EDT — newest playcap dir still
2026-10-14 22:46; live-timeline.jsonl mtime 2026-10-26 15:44:01.304 /
5691796463 B UNCHANGED; no dosbox-x process; watch infra alive (Xvfb :9,
x11vnc :5910, r1_playcap_watch.py) so the negative is trustworthy;
r1_t85g_sitting.py correctly not run. (2) TIMING INSIGHT: x11vnc.log ends
17:30:18 today and ALL of today's connect bursts (08:02..17:30) predate the
t111 DISPLAY-autodetect fix (self-test 21:09) — zero VNC attempts have yet
been made against the FIXED launch path, so the t111 root-cause story is
intact and the event is still plausibly imminent, just not observed.
(3) NEW CHECK: disk 30% used / 64 G avail — rules out a full-disk residual
behind capture failure. (4) t111 self-test artifact re-read confirms the
hygiene law signature (9 slots t=1131 flat, DAT_482fb=0/50); the same flat-t
signature retro-reads the Oct-26 shared-timeline tail (slots 49-60 all
t=1254) as idle autosave churn. NO row closed (strict-close honest
negative); no banked law falsified. NEXT t113 = final watch + loop-end
proposal (see above). Gate 0, LEDGER AUDIT OK

T111 LANDED (WATCH task — sitting watch NEGATIVE + CAPTURE-HARNESS DEFECT
FOUND AND FIXED; deliverables: scripts/r1_playcap.sh DISPLAY autodetect,
docs/re/_wip_t111.md, amendments to docs/re/stop-report.md §4 and
docs/BLOCKED.md t82; no ledger row touched): (1) sitting watch verified
fresh — live-timeline.jsonl mtime 2026-10-26 15:44:01.304/5691796463 B
unchanged, newest playcap dir still 2026-10-14, no dosbox-x process;
r1_t85g_sitting.py not run. Watcher infra alive (Xvfb :9 11d, x11vnc :5910
11d, r1_playcap_watch.py --no-exit 1d13h) so the negative is trustworthy.
(2) NEW SIGNAL: x11vnc.log logs EIGHT client connect bursts TODAY
(08:02..17:30, viewer requesting 2560x1325/3000x1573 vs 800x600) while zero
playcap dirs and zero new slots exist — someone reached the capture display,
nothing launched. (3) ROOT CAUSE [measured + inferred]: r1_playcap.sh:24
defaulted DISPLAY=:0; /tmp/.X11-unix has ONLY socket X9, DISPLAY=:0
xdpyinfo fails, :9 answers; bare run would die inside dosbox silently
(script's own preflights pass). FIX: autodetect first answering /tmp/
.X11-unix/X* socket (explicit DISPLAY still wins; hard exit-2 with socket
list if none answers). (4) SELF-TEST (real run, 21:09): TL=90 bash
scripts/r1_playcap.sh -> banner display=:9, 9 ring slots, 213 KB
live-timeline.jsonl, analyzer parsed 41.sav t=1131 T=50 score=0 in_game=true,
dosbox exited on time-limit, watcher reaped, scratch ring + shared timeline
mtimes UNCHANGED; artifact renamed selftest-t111-playcap so future watches
can't confuse it with a user capture. HYGIENE LAW banked: idle boots write
in_game=true/T=50 slots — mtimes+score movement, not in_game, prove a
sitting. NO ledger row closed (strict-close honest negative: no measurement
of game behaviour moved any row); no banked law falsified. NEXT t112 =
sitting watch only (see above). Gate 0, LEDGER AUDIT OK

T110 LANDED (STOP-REPORT task — FINAL STOP-REPORT + SITTING WATCH;
deliverable docs/re/stop-report.md NEW + working notes
docs/re/_wip_t110.md; no ledger row touched, no new tool): (1) sitting
watch re-verified — work/r1/playcap/live-timeline.jsonl mtime
2026-10-26 15:44:01 unchanged, no new work/r1/playcap-<ts>/ dir since
2026-10-14 -> stale assignment worked, r1_t85g_sitting.py not run.
(2) Ledger re-derived fresh this session (ledger_audit: rows=18,
closed=12, open=OQ-003/005/016/019/021/023 — OQ-006 CLOSED, the t109
NEXT-ACTION text's inclusion of it was a transcription error, corrected
here). (3) stop-report.md banks: outcome status; per-row capture lift
(OQ-021 via >50% colonization or debug-'C' percent readout; OQ-023 via
attitude>570-then-accept for a state-3 cell [UNOBSERVED in 42k rows];
OQ-016 0x4402a caller + 4 minutiae; OQ-019 step-CLAMP + inventory path,
sugar-cube BLOCKED-USER-LEVEL on two zero-corpora t49/t58; OQ-003
play-mutation variants); user-decision lift list (defaults
accept/reject, capture authorization, t89a code-work resumption); full
r1_playcap.sh protocol + one-sitting play checklist + cadence/slot laws
restated from docs/BLOCKED.md. NO row closed (strict-close honest
negative: bookkeeping, not measurement); no banked law falsified. Loop
is now event-driven: NEXT t111 = sitting watch only (see above). Gate 0,
LEDGER AUDIT OK

T109 LANDED (STATIC task — COUNT-COLUMN PURGE; deliverable
docs/re/census-audit.md S2 replaced in place + S9/S10 stop-report; OQ-016
t106 tool-leg counts struck + t109 block appended; working notes
docs/re/_wip_t109.md): (1) all 13 S2 offsets re-censused with BOTH
t108-patched tools (limited-op + full-op) under the authoritative fn-start
rule + code-span filter [0x14bb0,0x82bb0); corrected truth column = full-op
in-code (44:22 46:7 48:10 4e:8 50:13 52:23 54:22 58:32 5d:25 66:15 67:30
88:23 90:14); WORD counts identical to pre-purge on all 13 offsets —
structural confirmation the phantom class was byte-op-only. Cross-check:
tool-derived +0x66 in-code set == S7 hand-adjudicated 15 exactly. (2) t106
+0x55 FOUR-word list (0x37f9a/0x39224/0x44054/0x3a664) re-verified verbatim
(6 verified / 5 in-code / 4 WORD; stale "12 verified" struck in OQ-016);
+0x42 corrected 23/19/13 with colonise 0x23cac surviving; all four t107
amendments (0x49307 +0x90-of-14, 0x24a00+0x3ca60 +0x58-of-32-in-code,
0x41d80 DEC +0x88-of-23) survive with counts re-cited. Op-family note banked:
r1_t106_writers alone cannot see group-80 /1 — even the banked +0x66 |=1/|=2
pair requires the full-op tool. (3) closing control r1_t108_disp32_audit.py
RC=0 reproduces S6 numbers exactly (277/58/0 FPU; 0xccb 1/0/0; +0x67 8/0/0).
NO row closed (strict-close honest negative: bookkeeping, not measurement);
NO banked law falsified; no new tool. Sitting watch unchanged. NEXT t110 =
final stop-report + sitting watch (see above). Gate 0, LEDGER AUDIT OK

T108 LANDED (STATIC task — FULL-OP RE-AUDIT OF REMAINING CENSUS-CITED
CLAIMS + +0x66 ATTRIBUTION; deliverable docs/re/census-audit.md S6-S8 +
new tool scripts/r1_t108_disp32_audit.py + tool fixes in r1_t106_writers.py
and r1_t107_writers_full.py; working notes docs/re/_wip_t108.md P1-P4):
(1) ALL FIVE outstanding census-cited claims HOLD under the whole-code-span
function-start decode method (140,902 insns, generator-free): ds:0x7458e
EXACTLY-two-stores law re-proved two independent ways (owning-insn map over
all 277 raw u32 runs + span decode; 0x52cc6 = dark-zone site beyond tsv
extent, adjudicable only by the sequential chain); [ui+0xccb] one-store
zero-readers confirmed and address corrected 0x37bbb->0x37bb9; FPU-no-+0x67
negative holds + scope-annotated in income-law 6d (non-FPU +0x67 stores
exist, none is pop storage); r1_t88_caller_census re-run GREEN RC=0 with
identical caller set; diplomacy stride-0x1ee census = RAM-value census
already retracted in S10, no code-census tool liability. (2) THIRD TOOL
DEFECT FOUND + FIXED (the iteration's load-bearing find): boundary_ok
accepted decode base == candidate for 16-aligned addrs (objdump starts AT
the candidate -> every byte pattern self-verifies; proof 0x41835 mid-insn in
fn 0x41260's real chain) AND objdump wraps long-insn tails as bytes-only
lines (0x544ff = tail of the mov at 0x544f8; skipping them hid coverage).
Rule banked: fn-start chain is AUTHORITATIVE — mid-insn coverage = reject,
no fallback vote; merge wrapped tails. Effect: +0x66 "27 in-code / 43
verified" -> 15 true code sites. BLAST-RADIUS SPOT AUDIT 36/37 banked sites
OK; 1 phantom citation (0x390a0 range fragment) corrected in S3 — NO banked
law falsified (WORD/DWORD sites always fn-start-solid; phantoms were
byte-op families). (3) +0x66 FLAG LAW PROVEN COMPLETE among all
boundary-verified writes: |=2 0x37f7b + |=1 0x39229 are the ONLY
planet-record flag ORs image-wide; others attribute clean: planet template
copy 0x3a696 (fn 0x3a558 ctor law), SHIP DESIGN table 0x490e3/0x4923a (edx
walks 0x7650c stride 0x6a, in-window cited), 9 stack-local slots in shp-cache
callers (fn 0x3db80/0x4e6fc `sub ebp,0x82` frame rebase + fn 0x34148 loop
counter vs [obj+0x69]>>16). Item (2) closed by the assignment's own clean-
no-carriers clause. (4) Ledger: OQ-016 annotated, STAYS OPEN (open set
unchanged; strict-close — tool-validity + law-completeness, no new constant).
REWRITE: no delta. Gate GATE_EXIT=0, LEDGER AUDIT OK.

T107 LANDED (STATIC task — WORD-WRITER CENSUS AUDIT; deliverable
docs/re/census-audit.md hand-authored + new tool scripts/r1_t107_writers_full.py;
working notes docs/re/_wip_t107.md P1-P3): (1) t106 claim REPRODUCED: the
pre-fix tool (git d8dda8f — the working-tree copy was already t106-patched,
baseline taken from git, disclosed) yields ZERO 16-bit word sites on all 13
audited offsets (+0x44/46/48/4e/50/52/54/58/5d/66/67/88/90); fixed tool: 40
word sites, EVERY one in a family already banked via INDEPENDENT evidence
(planet-field laws trace to the t23 w16-mask census, colonisation RMW named,
SA_IndustryBoost/event+200 named) or proven other-struct (fn 792/147 +0x5d
words, fn 111 data region). NO CLOSED ROW FALSIFIED. (2) SECOND BLIND SPOT
found and fixed: the t86 op set also lacked AND/OR/XOR/ADC/SBB/XCHG/INC/DEC/
NEG/NOT/shift stores -> full-op tool; it re-found every banked non-census
site (0x21b85 INC word +0x44, 0x39084 INC +0x50, +0x66 |=2/|=1) and surfaced
three doc gaps amended in-place: aicode S7.4 THIRD power-burn path 0x41d80
`dec DWORD [ship+0x88]` (per-order spend, fn 2010), combat S2d 14th +0x90
writer 0x49307 (template-time zeroer inside banked init_global_gizmos),
aicode S6 order-kind imm-0 0x24a00 + imm-2 0x3ca60 (banked text claimed
"no imm-0 or imm-2 stores"). Laws themselves unchanged everywhere; REWRITE
no delta (no per-ship POWER/slot model in aggregate). (3) METHOD LAWS banked
(census-audit S1/§5): "WORD PTR" substring matches DWORD (use (?<!D));
byte-family byte censuses over a flat image REQUIRE the obj0 code-span filter
+ per-record-class attribution before any "only writers" claim. (4) Ledger:
OQ-016 annotated, STAYS OPEN (same residual set — strict-close, the audit
moved tool-validity not behaviour). Gate GATE_EXIT=0, LEDGER AUDIT OK.

T106 LANDED (STATIC task — the scenario-template PRESET SOURCE for the +0x55
seed deviation: ASSIGNMENT PREMISE REFUTED; a banked census-tool bug found and
fixed; working notes docs/re/_wip_t106.md P1-P12, tools scripts/r1_t106_*):
(1) RESIDUAL CHARACTERISED, PRESET ATTRIBUTION DEAD — deviations are RUN-LOCAL
not NAME-LOCAL (r1_t106_deviation: 15 r1deep runs x first save, 2320 samples,
43 dev; 7/15 runs ZERO dev; 41/424 names ever deviate, none consistently; flat
across +0x16 rows and sizes; all on owner 0xFF), FROZEN for the run
(r1_t106_drift: one fingerprint + constant d across all 20 saves of the
15-dev run => mid-capture terrain writers and aliasing both out), NOT array
aliasing (r1_t106_alias: 6/322), NOT in any data file (r1_t106_srcscan v2
contiguous-block join, DEV 3/29 vs CTRL 12/72 — v1 was invalid, stride-4
compressed pattern searched contiguously, disclosed before use), and header-
INDISTINGUISHABLE (r1_t106_hdrdiff +0x6b==105 "discriminator" was 1-record
noise via two-proportion recount over 8282 records). Framing correction: banked
"first saves" are MID-campaign (41..56.sav) — a generation law audited after
40+ turns of event drift; +2 scan @0x4402a..0x44054 explains small positives
[inferred]. (2) TOOL BUG FIXED (the iteration's load-bearing find):
r1_t86_write_census.py encodings() never prepended the 0x66 operand-size prefix
AND dis_at() decoded one objdump window at addr&~0xF (desync = R7 self-inflicted)
=> NO 16-bit word write had ever entered a banked byte-pattern census. Fixed
tool: +0x55 = 12 verified sites (4 WORD: 0x37f9a seed nb/3+5, 0x39224 item-37
+10, 0x44054 owner-scan +2, 0x3a664 planet-record CONSTRUCTOR copy — FUN
0x3a558 field-at-identical-offset copy, callers 0x258dd/0x26044), +0x42 = 28
sites incl. colonise 0x23cac. New boundary-checked variant
r1_t106_writers.py. (3) Ledger: income-law.md T106 + S-T106-TOOL appended;
OQ-016 annotated, STAYS OPEN (open set rewritten: preset-source item REMOVED
as refuted; remaining = terrain/nuke wiring, home placement, +2 minutiae,
event-dispatch caller of 0x4402a [capture-class], live-UI-trace armer);
REFUTED-ROUTES R12 added. REWRITE: no delta (seed/cap laws unchanged; the
residual class does not alter the aggregate model). No new capture run.
Gate GATE_EXIT=0, LEDGER AUDIT OK.

T105 LANDED (STATIC task — the last two aicode.md S6.4 residuals CLOSED;
verify tool scripts/r1_t105_verify.py RC=0 FIVE legs; working notes
docs/re/_wip_t105.md P1-P3): (1) "stride-45 table 0x74782" REFUTED — no
such table: SA_FreeResearch body index math lea[edx*4]/add/shl4/sub ==
75*t byte-pinned 0x4416b..0x44189, and WORD[0x74782 + 75*i] IS the restree
runtime COST word (record base 0x74744 stride 75, cost @+62; row-0 spaced
name at corollary X 0x74746; 65 consecutive stride-75 deltas; live fit
66/66 vs the OQ-013 cost law). aicode S6.3 corrected; _wip_t99 F17 marked
REFUTED. (2) GOVOROM +0x42 CLOSED: assignment premise FALSE (race-row
+0x42 = pointer garbage rows 0..20; no GOVOROM race row in campaign —
GOVOROM = ability NUMBER 10). Real residual (t99 F12/F18 min key)
resolved: SA_Cornucopia body 0x43de4..0x43e96 (pinned incl pool base
0x2b057 stride 123, owner [rec+0x57], skip [rec+0x16]==10, idiv 3 pick
pool 0x6838) min-walks WORD[planet_rec+0x42] == the population counter
per the t24 CLOSED pop law (38f68.c:154-177 same layout); STORED COUNTER,
not a cache. Writer census r1_t86 0x42: 10 verified sites, zero race-row
carriers; 0x3b0a7 low-word==2 corroborates colonize pop:=2. Live 60.sav:
pool 145 rows (count law hi16 ds 0x3a091), max counter +0x4e 48 < 50, all
64 pop>=cap rows carry counter 0 (LAB_000393f9). (3) Ledger: aicode.md
S6.4 residuals ALL CLOSED + S6.3 correction + F17 refutation; OQ-016 row
annotated, STAYS OPEN (same open set; strict-close). REWRITE: no delta
(FreeResearch already completes the queued tech; Cornucopia already keys
on pop — laws confirm existing behaviour, aggregate model unaffected).
Gate GATE_EXIT=0, LEDGER AUDIT OK.

T104 LANDED (CAPTURE task — F8b ORDER-COMPLETION POWER DRAIN OBSERVED +
the five-rows mystery CLOSED BY SUBSTITUTION; verify tool
scripts/r1_t104_drain_verify.py RC=0 four legs; working notes
docs/re/_wip_t104.md P1-P5): (1) NO new harness needed — the banked
playcap stream (44,928 rows, 17,170 boundary pairs) already contained
the closure vehicle (tool scripts/r1_t104_drain_watch.py + gate-gated
scripts/r1_t104c_fulllaw.py). (2) OBSERVED: completion drain executing on
CONTINUOUS tracked records (same owner+design+state both sides) — 4
events (day369 slot3, 678 slot14, 945 slot10, 1017 slot28, owner0):
POWER +0x88 >0 -> 0 WITH order-state +0x5d CLEARED 0x3->0 in the same
sample pair; MOVES net-unchanged (zero leg 0x41ded + FUN_0004a658
re-grant); POWER restored at the NEXT boundary (679 P4 / 946 P5 / 1018
P8) == recharge FUN_0004a74c one End-Turn later. CONTROL burn class
(b5d unchanged same-day P->0) = 126 members = travel/upkeep
0x4a2d4..0x4a314 — gate separates completion from burns. (3) REFUTED:
the t102 "five zero-POWER rows = post-recharge completion drains"
mechanism — rows on 59+60.sav (both T=1254) sit EXACTLY on slots
2/4/11/12/15, ALL FIVE observed state->0 mid-t1253 (t85g war turn;
r1_t85g2_slots.py independently named them), reappearing t1254 as
post-death FREE-RECORD REUSE (slot4 design 2->4, xyz frozen, ETA
1257..1264 > T = the 0x40e96 order stamp); P=0 = fresh record awaiting
next recharge. No recharge-law exception (t101 bound stands). (4)
METHOD LAW banked: any P>0->0 transition census MUST gate on record
continuity or it counts death/recycle as drains (t104b proved via
battle-frame trace). (5) Docs: aicode.md S7.4 adjudicated (observation-
cited), S7.5 amended; OQ-016 annotated, STAYS OPEN (terrain/nuke,
home-placement, minutiae, preset source, live-UI-trace armer). REWRITE:
no delta (aggregate model never models per-ship POWER). Gate
GATE_EXIT=0, LEDGER AUDIT OK.

T103 LANDED (STATIC task — 0x37b6c DX-SWITCH / HUMAN ABILITY ACTIVATION
CLOSED, verify tool scripts/r1_t103_dxswitch_verify.py RC=0 five legs):
(1) IDENTITY: FUN_00037b6c (real extent 0x37b6c..0x37cf7) has ZERO rel32
callers; sole u32 ref = FILE 0x8893c = pool 0x5d84 +0x8 = ABILITY-WINDOW
CLASS RECORD (ctor 0x37ac5 stores 0x5d84; +0 create 0x37ad0 loads abil%02d
description file 0x8483f; +c paint 0x37cf8 draws race ability glyph — shp
lib 0x9f10c sel 250 + BYTE [race*2+0x12e18]); dispatched via pump
FUN_00056b5c (call [class+0x8] @0x56c74) and relay FUN_00056ca4 (msg code
= caller ebx arrives as dx; handler ebx = caller ecx; @0x56cd1..0x56cda).
(2) LAW: head esi = 0x12e16 + ds:0x7458e*0x1ee (local race row);
dx 1|2 -> PROBE 0x43b50(row,0): -1 READY -> dead marker [ui+0xccb]:=2
(disp32 census: store 0x37bbb ONLY hit, zero readers); not-due -> countdown
'N day(s)' cad-counter (0x37bf1 cad read, 0x37bfb singular iff ==1,
static.txt 191-string blob idx 28=''/29='s'/30='OK' via ascend00.cob,
0x76c79 snprintf-family). dx 50 -> gate cmp ebx,1 @0x37c9c -> FIRE
0x43b50(row,1) + 'abres%02d' (pool 0x1ca1 = file 0x84851, byte-pinned;
0x1cab='help.txt') result window via FUN_00033f40; else base filter
0x33ff8. Tail 0x37c78 resets [ui+0x35]/[ui+0x39]:=-1 + repaint [class+0xc].
(3) FUN_00043b50 edx PARAMETER LAW cited: gate cad>counter -> 0; ready:
edx==0 returns -1 (probe); edx==1 dispatches bodies (al=[row+0x19d]-5,
cs:[eax*4+0x2ef60]); RESET row+0x19e := counter - cad (0x44001 sub edx,eax
— DIRECTION correction vs t99 prose; zero exactly at fire, t100 model
stands). (4) CORRECTION banked in aicode S6.4: 'abres%02d at dx==2'
REFUTED (abres = dx-50 result resource). (5) ARRIVAL honest negative: all
9 pump + 56 relay sites register-traced; msg-50 relays exist (0x3b6ac,
0x3d8xx family) none arms ecx==1; input relay 0x54976 pumps ds:0x484c4/c6
verbatim from the DOSBox event record (+0xc/+0x10) — positive armer needs
live UI trace (carried residual). Live 60.sav leg: rows 0..3 ability
19/2/11/0, counters 8/1/64/0 all < cad (89/0/70/0) — consistent, no
pending fire. Docs: aicode.md S8 NEW (S6 OPEN-RESIDUALS dx-switch item
CLOSED). Ledger: OQ-016 annotated, STAYS OPEN (strict-close: F8b capture
+ live-UI-trace residual). REWRITE: no delta (human path is UI input; AI
sync law already wired t99/t100). Gate 0, LEDGER AUDIT OK.

T102 LANDED (STATIC task — EVENT-24 CONSUMER DECODE CLOSED, verify tool
scripts/r1_t102_event24_verify.py RC=0 five legs): (1) PUMP LAW:
FUN_00055ae8 (sole caller 0x54b74 in FUN_00054650; gates ds:0x7a358!=-1,
write cursor !=0, [[obj+0x4226]>>16]==1, EVENTWIN lookup 0x85943) pops
the stride-10 ring on 0x7a35c; TYPE SWITCH 0x55cbc..0x55d69 decoded
EXHAUSTIVELY — type 24 arms to 0x55d69 ring-maintenance NULL (bytes
83 f9 17 / 72 0b / 83 f9 19 / eb->0x55d69 pinned); edi=0 -> tail 0x55da1
je skips the 0x56ad4 re-arm. The queued event does NOTHING but advance
the ring: the queue is a UI signal. (2) SPLIT LAW (cited both gates):
FUN_00043b50 rel32 callers EXACTLY {0x37baf edx=0 probe, 0x37cb1 UI
edx=1, 0x3eb3c turn-tail}; the 0x3eb3c gate skips the local race
(race==ds:0x7458e) unless ds:0x10ba4==-1 — the SAME equality as the
event-24 producer: AI races fire SYNCHRONOUSLY in FUN_0003e6e0 (via
FUN_0003ea54 call 0x3e7bb), local race event-24 = EVENTWIN refresh,
human ability activation = UI path FUN_00037b6c dx==1. REWRITE: no
deferred queue needed; abilityPhase == cad fires immediately (AI),
player fires on UI activate (same bodies, same T1 reset). (3) ds:0x7458e
identity: two store sites only (0x21aa0 idx+bitmask 0x89324; 0x52cc6
zero); live 0 == race0 byte. ds:0x10ba4 live 0 (netplay flag [inferred]).
(4) F8b drain sites ATTRIBUTED not observed: FUN_00041260 order-state
dispatch on BYTE [ship+0x5d] jump table FILE 0x41244 7/7; completion leg
0x41ded..0x41e19 ZEROS [ship+0x94]+[ship+0x88] (delta into stack budget),
arrival 0x41d80 decl; five zero-POWER rows = post-recharge drains, [rec
+0x52] > T ETA re-stamp 5/5 on 59.sav AND 60.sav (b5d==0 signature).
(5) FUN_0003e6e0 adjudicated = per-race turn tail: leg (a) EVENT 11 per
item (local race, FUN_000402d8<0), leg (b) EVENT 10 race-death row+3:=-1,
leg (c) recharge pass per ship FUN_0004a74c, leg (d) event-24 producer —
ALL queue traffic (types 10/11 too) hits null arms = UI refresh. Docs:
aicode.md S7 NEW (S6 OPEN-RESIDUALS first item CLOSED). Ledger: OQ-016
annotated, STAYS OPEN (strict-close: human dx-switch law + F8b capture
remain). Gate 0, LEDGER AUDIT OK.

T101 LANDED (STATIC task — +0x88-vs-+0x94 RE-ATTRIBUTION CLOSED, verify
tool scripts/r1_t101_field_verify.py RC=0 three legs): (1) PANEL LAW byte-
pinned 0x1da8a..0x1daaf: cdecl pushes [ship+0x8c],[+0x94],[+0x88] R-to-L
into 'POWER %d MOVES %d INTEGRITY %d' F 0x831c9 (only 'MOVES' string
image-wide) => +0x88=POWER, +0x94=MOVES, +0x8c=INTEGRITY (+0x98 max,
+0x18 POWER cap, +0x52 birth day); t85g '+0x88=MOVES' label REFUTED (raw
observations stand verbatim in combat.md S1), t99 aicode S6.4 NOTE
CONFIRMED + annotated. (2) t90 S2e REFUTED: the 'race-maintenance legs'
0x43bd0 (integrity:=max), 0x43c0a (attitude floor), 0x43c5b (+0x88<<=1)
are the SA_HealShips/ForcePeace/DoublePower BODIES (jump table FILE
0x43b10 re-resolved 16/16 == t99; 0x43c3d = jmp, no fallthrough into
0x43c3f); 'boundary recharge is THESE TWO sites' VOID. (3) RECHARGE LAW
CLOSED: FUN_0004a74c [ship+0x88] := trunc([+0x18]*(1+clamp((T-[+0x52])//
100,0,10)/10)) (0x4a96c idiv+clamp, 0x4a99c float mul; live constants
0x851f3=0.1 and 0x2647=2.0 verified on 60.sav), called per-turn per-ship
at 0x3e7b0 + build completion 0x49d0d; live fit 25/35 exact + 35/35
bounded (10 deviations = same-day upkeep/travel burns; 5 zero-POWER
Ungooma rows = F8b residue [unverified mechanism], NOT SapAlienPower —
no shipped race has ability 9). (4) FUN_0004a658 raw: MOVES re-grant
[+0x94]:=[+0x10] (+ds:0x77f6c by status bit1, zero bit0); t47 S12/S13
corrected to the +0x30 record-start artifact — rows 10..15 are the SHIELD
family (LIVE-NAMED Ion Wrap..Nanoshell, drives = cat2 16..20), values
stood on the right bytes; travel consumes BOTH budgets at 0x4a2d4..0x4a314
(mode==1 gate): fsub/fistp +0x94 AND int-dec +0x88 — the t47 CONSUMER-OPEN
item CLOSED. Docs: combat.md S1/S2d/S2f/S2g amended, aicode.md S2e
REFUTATION + S6.4 ADJUDICATED, ships.md S12 t101 block, full trail
docs/re/_wip_t101.md; OQ-016/OQ-019 annotated, BOTH STAY OPEN (strict-
close — no ledger closure, no rewrite delta: per-ship fields are OQ-019
territory, aggregate model unaffected). Gate
GATE_EXIT=0, LEDGER AUDIT OK.

T100 LANDED (CODE task — OQ-020 CLOSED, the measured per-ability cadence
table wired): abilityChargeTurns (rewrite/src/game/species.cpp) now returns
the CITED vendor table kCad[21] = WORD[0x6780+2*ability] (5:60 6:100 7:62
8:77 9:90 10:150 11:70 12:63 13:66 14:72 16:92 17:100 19:89 20:68; zeros
exactly at the passive set) replacing the falsified 30-turn placeholder;
abilityPhase (campaign.cpp:1076) rewired from count-DOWN to the cited
COUNT-UP law: charge_ == original row+0x19e, +1/turn, fires iff counter ==
cad EXACTLY (gate 0x43b58), resets 0 on fire (exit T1 0x4400a; T2 0x43fe5
stores 0 at the equality point too — one reset models both); init all-zeros
(first fire exactly at turn cad). Verify tool scripts/r1_t100_cad_verify.py
RC=0 — THREE legs byte-exact: C++ kCad == restored FILE 0x89330 == LIVE
playcap/save/60.sav (item-table-anchored B=0x1bf4d8). TRAP BANKED: the
high-entropy anchor vote against the CURRENT game/ascend.exe is WEAK on
playcap saves (capture-time needle differs; t98 exe-identity context) —
use the deterministic b"\x1e\x00Factory" anchor at B+0x82bb0+0x73e40+8.
Tests: species_charge_split_verified pins the full 21-word table +
nonzero==charged set; species_charged_ability_fires_on_schedule pins t60
fire / reset 0 / t120 second fire (period == cad); six per-ability tests
moved to their cadence words (100/66/92/72/150/63). GATE: stage 3m smoke
40->65 turns (HealShips cad 60). 110 tests 0 failed; timeline seeds
UNCHANGED (2024 Control t737 / 42 Extinct t688 / 13 Extinct t503 / 1 t836 /
2 t657, all finite <1200) — PLAYTHROUGH.md already matches, no regen;
record_playthrough.sh comment updated (closes t93's self-noted stale-echo).
Docs: abilities.md §2/§3/§5 rewritten to the measured law; ledger row
CLOSED with evidence + code sites + the T57b separate-object caveat (the
gizmo-slot amass path is NOT the SA_ species pool); ledger_audit default
open set now {003,005,016,019,021,023} (rows=18 open=6 closed=12 OK).
Working notes docs/re/_wip_t100.md. Gate GATE_EXIT=0, LEDGER AUDIT OK.

T99 LANDED (STATIC task — W6-A6 CLOSED THE A6/A7 RESIDUAL, cited, NO ledger
closure, tool scripts/r1_t99_maint_census.py RC=0): FUN_00043b50 = the
PER-RACE SPECIAL-ABILITY CADENCE ENGINE, decoded end-to-end (extent
0x43b50..0x44029 + dispatch): the cs:[eax*4+0x2ef60] jump table resolves via
the t96 code-object law to restored FILE 0x43b10 (raw 0x2ef60 pinned as pool
garbage — 16/16 entries outside the function); key row+0x19d = the race's
SPECIAL ABILITY NUMBER (sole writer 0x4460f inside the RACE%02d.DIP loader
FUN_00044290; scenario row byte+1 source; live 60.sav rows 0..3 active ==
19/2/11/0, row4 stale); row+0x19e = charge counter (+1/turn iff
[[row+7]+0x14]&0x80, stores at exit 0x4400a, reset on fire); counter ==
cadence word fires EVENT 24 via 0x55a60 on game object 0x7a35c (299 sites;
consumer = named P0 random-event territory). ALL 16 case bodies disassembled
AND matched 1:1 to help.txt abil%02d/abres%02d vendor text (5 HealShips,
6 KnowGalaxy, 8 FastedResearch, 9 DisruptBuild, 10 Plague, 11 BumpShipsIn-
Lanes, 12 StealTech [popcount(owners mask)>>=2, own bit ORed into row byte
+3, re-pick target 0xffff], 13 Shield [planet +0x62 := 0xffffffff], 15/18
NOP/passive, 17 Hatred [dyadic, skips self, [r+0x1c0]==2 gate, [r+0x1b2]
attitude], 20 IndustryBoost; full bodies aicode.md §6). THE HEADLINE: data
table 0x6780 (FILE 0x89330, data-intra law) is the CHARGE-DAYS-PER-ABILITY
table — the measurement t57's seven negative probes failed to find; its
nonzero set == the rewrite's kCharged set {5..14,16,17,19,20} exactly, which
falsifies the rewrite's 30-day OQ-020 placeholder -> t100 assigned. Cadence
table/pick-pool reads fixed to data-intra law (CADENCE_FILE 0x89330, pick
pool {2,3,4} u32 validated). Ledger: OQ-016 t99 annotation appended (row
STAYS OPEN), OQ-020 corrected to open-with-measurement (the t57 BLOCKED
"static route exhausted" claim refuted by t99 itself). Banked: aicode.md §6
(permanent), docs/re/_wip_t99.md (full probe trail F1..F18). Gate 0,
LEDGER AUDIT OK.

T98 LANDED (STATIC task — W6-A5 WLINK VERDICT, cited negative, NO closure,
NO code change): spec-first per the t97 rule (IBM OS/2 LX spec rev 11
fetched, cached ~/.hermes/cache/web/archive.org-c9e087b277.md); tool
scripts/r1_t98_wlink.py RC=0 with structural seals (objtab 2x24B -> obj
page table 121x4B -> resident name 'corn' -> entry table tile BYTE-EXACT;
loader-section end == DATA PAGES OFFSET 0x17600). MEASURED: DEBUG INFO
OFF/LEN (le+0x98/0x9c) = 0/0 -> no debug section exists at all (spec §2.2
zero = absent); file-wide signatures NB03/NB00/NB02/ODIAG/DWARF/OS21001
ALL ZERO; each of the 8 SO names occurs EXACTLY ONCE in the whole exe
(the block itself at 0x8b8b0); non-res name table absent (DW(le+0x88)=0);
module-name vocabulary absent ('.obj' 0, 'shiporders' 0). SO block lies
inside the demand-page span = plain image data. t97c ROOT CAUSE found:
DW(le+0x30) is FIXUP SECTION SIZE, not the object table (correct: DW(le+
0x40)/DW(le+0x48) header-relative); LE object table has no name strings at
all (spec §2.4) — t97's twice-guessed "name-count semantics" was a
phantom premise. VERDICT per t97 closing rule: A5 component CLOSED as
debug-only identifiers — the kind->SO-name tie is UNMEASURABLE by ANY
remaining route (no symbol table, no consumer, no live pointer); user-
visible mapping lives in game/static.txt only (t96 string-getter law);
index==act reading stays [inferred] (act domain 0..7 vs 8 names — closer
fit than the old kind-domain note, still unmeasured). REFUTED-ROUTES R14
kills the LE-debug route. OQ-016 row annotated, STAYS OPEN (A6/A7
minutiae remain). Banked aicode.md §2i. No rewrite delta (ANALYSIS-ONLY).
Gate GATE_EXIT=0, ledger_audit LEDGER AUDIT OK.
T97 LANDED (STATIC task — W6-A5 CONSUMER PASS, all three t96 hammers
executed to conclusion, honest negative, NO closure, NO code change):
helper 0x2fb38 identity MEASURED (disasm + 106 rel32 caller census):
Watcom staging scaffolding (byte-writes [[esi+4]+0xf3], conditional
0x5e940(eax, esi+8)), NOT the R12/relocation helper and NOT a block
consumer (t96 note corrected: relocation remains loader-side; live imm at
0x1dae6 reads P0+0x88e60 exactly, re-verified playcap/save/60.sav B=
0x1bf4d8). Display fn FULL extent 0x1d989..0x1df18 (ret walk) has NO
reader of the [esp+0x10] SO slot; act-arms 0x1de9c append [+0x5e]+0x1c/
+0x24 target names (static.txt law unchanged). 20-stride indexed census
(152,831 obj0 insns, tool r1_t97_so_consumer.py): 6 sites, all esp-frame
printf arg tables — no pool-backed stride-20 reader. CENSUS-BLIND-SPOT FIX
(t94 used static-file form only): pool-rel-form imm scan found 14 block
candidates, disassembly adjudicated 13 decode artifacts (mov [reg+0x63],0
class) + 1 real (0x1dae6). LIVE proof of disuse: ZERO u32 in the full
16 MiB save RAM (every byte phase, tool r1_t97b_liveptr.py) holds any
address into the relocated block. Jump-table census (tool
r1_t97d_jmptables.py, decode-boundary-verified): 9 computed-jump sites in
obj0, only batmode-zone one is t96's F 0x1d840 status table — no second
kind-keyed dispatcher; t96's suspected 'twin 0x1dd290' is inside the
kind3 arm (fully disassembled). CONTRAST: dip-state name cluster = 62 imm
referrers (shape of a CONSUMED table). Verdict: SO block = debug symbol
table signature is strong, but strict-close demands a cited debug-format
tie -> row STAYS OPEN; next hammer named = WLINK ID-Info parse (fetch the
spec first; two failed format guesses banked so t98 doesn't repeat them).
OQ-016 row annotated with the full t97 negative. No rewrite delta
(ANALYSIS-ONLY). Gate GATE_EXIT=0, ledger_audit LEDGER AUDIT OK.

T96 LANDED (CORRECTION task — adopted + committed the killed t94/t95 tree
first as f66cb55, then refuted its load-bearing premises and banked two
CLOSED sub-laws): ADDRESS LAW RE-CHECK killed the t95 story — cs-relative
0x8c90 == restored FILE 0x1d840 (code-object intra +0x14bb0 + 0x8c90), where
a CLEAN 6-pointer jump table sits (bodies F 0x1d989/0x1db4f/0x1dc1b/0x1dcfd/
0x1d9ab/0x1d9ab; live = FILE+P0 exactly per the CLOSED pointer law; the
"LE-fixup garbage" at restored[0x8c90] was obj1 pool data read at a member
index; no fixup decoding was EVER needed). STATIC disasm of all six bodies:
the dispatcher is the batmode.cpp SHIP-PANEL STATUS builder mapping kind ->
static.txt TEMPLATE (kind0 'Sun %s' star-name; kind1 'Planet %s' + [+0x57]
planet idx, 0xff sentinel; kind2 star-name + '\nMoving to Star Lane/Planet'
chosen by +0x5d (1/else) when in own system & act!=0, else '\nOwned by %s';
kind3 'Star Lane', [+0x23]&1 -> 'Red Link', owner-bitmap fail -> tail; kind4
== kind5 -> shared tail POWER/MOVES/INTEGRITY fmt F 0x831c9; 'INVALID ORDER'
staged with guard cmp [+0x5d],7) — NOT the SO-name map: REFUTED-ROUTES R13
added, t95 tool header warning added. STRING-GETTER LAW CLOSED (FUN_00021a20
+ init FUN_000218b4): getter(n) = nth quoted string of game/static.txt
(191 strings; runtime table data-intra 0x10ba8 -> P0+0x93758, count ds
P0+0x959bc live 0xbf; live dump matches FILE ORDER exactly). +0x5d ACT ENUM
census CLOSED-with-sites (imm stores 0:{0x41a30,0x41bff,0x41c26,0x41c98,
0x41ced,0x41dab,0x460d9,0x499e5} 1:{0x45e31,0x4aa50} 2:{0x40224}; +0x5e =
act-target object ptr paired; t93's "FUN_0004105c (+0x5d:=2)" corrected —
0x4105c decides legality, caller stores). SO-name->kind numeric tie STILL
NOT MEASURED (strict-close honest negative; block = 8 names + 2 'BAD' vs
kind domain 0..5 -> indices != kinds [inferred]; sole ref 0x1dae5 whole-block
copy, no stack reader found in 0x1c000..0x1e500). OQ-016 annotated, STAYS
OPEN. Banked aicode.md §2g-correction/-2, §2h. No rewrite, no game/ change.
Gate GATE_EXIT=0, ledger_audit LEDGER AUDIT OK (rows=18 open=7 closed=11).
T94 LANDED (STATIC task — W6-A5 order-ENUM MEASUREMENT PASS, honest
negative, NO closure, NO code change): the SO name block dumped byte-exact
(8 names stride 20 @0x88e60 SONothing..SOGoSpace, pool-rel 0x62b0+20k);
reference census over the restored image (NEW scripts/r1_t94_so_xref.py +
r1_t94_so_imm.py): exactly ONE code u32-imm to any name (0x1dae5 -> SONothing
base, ship-info display copying the whole 200-B block — engine indexes the
table at runtime, no per-name immediates; zero u32 anywhere points into the
block). +0x58 store/READ census (NEW scripts/r1_t94_order_census.py —
complements r1_t86 which lacks C6/0 mov-imm8; 56 verified obj0 sites, zero
outside): imm stores 1:{0x3fb3e} 3:{0x39859,0x49cd6} 4:{0x2202f,0x22127,
0x49db9} 5:{0x22243,0x2228f}, no imm-0/2 stores. EXEC SEMANTICS measured:
0x21f58 consumes kind==5 (target [+0x59] = star record; copies 3 f32 star
offsets, rng%200 jitter each, places via 0x49aa8, stores kind:=4); 0x220a8
issues kind:=5; 0x220f2 downgrades kinds {3,1,2} with lost targets to 4 with
[+0x59]:=owning star (0x13bc5 stride-0x60 law); the 0x40178 decider returns
early on {1,2,5} and asserts kind==4 at 0x553 fallthrough. THE BLOCKER: the
UI 6-way dispatcher 0x1de40 indexes a jump table at image 0x8c90 — region
below obj0 code start 0x14bb0, fixup-encoded in the restored file (raw u32s
garbage), so no static case-body read exists YET; named closer = t95 above.
Banked in aicode.md §2f-supplement; OQ-016 row annotated, STAYS OPEN
(strict-close — no numeric->name mapping cited). Game checksums untouched;
no rewrite change (enum is per-ship, rewrite aggregate-only). Gate
GATE_EXIT=0, ledger_audit LEDGER AUDIT OK.
T93 LANDED (CODE task — OQ-016 RESEARCH PICKER sub-law CLOSED-with-code-
site + §3c CORRECTED): before implementing, the banked §3c disassembly was
re-verified against raw objdump and FOUND WRONG in its load-bearing claim:
the uniform-leg entry test 0x40134..0x4013d (`test eax,eax; jge 0x4015b`
on sign-extended chosen) means the uniform fallback 0x4013f runs for
chosen<0 INCLUDING the sentinel -2 and OVERWRITES it — a -2 NEVER reaches
the DAT_00076492 store from the picker path. TRUE LAW [verified]:
sentinel(flag DAT_00074902, live 0x0f=all shipped AI) skips ONLY the
preferred-bias scan (guard 0x400fb); flagged races pick uniform at 100% of
pick opportunities; the §3c "no pick this turn" model is VOID and the
-2-consumer residual is UNREACHABLE (aicode.md §3d). Delta implemented on
the true law: campaign.h Campaign::aiResearchPreferred (pure tier decision;
preferred membership {1,47} per §3c math) + campaign.cpp researchPhase AI
branch = FUN_00040018 tier chain (row-order legal candidates cap 32
@0x40044, one rng_ draw rng%100<45 @0x400c4, preferred-first else uniform
@0x4013f); player path UNCHANGED. TEST(campaign_research_picker_law_oq016)
pins membership/first-wins/sentinel-skip edges on rows 1/47 + 60-turn
campaign leg; 110 tests 0 failed. UNCITED uniform-random pick replaced by
cited law — the GOAL's core verb executed. Timelines re-measured after
delta, ALL FINITE <1200: 2024 Control t737 (was t777) / 42 Extinct t688
(was t581) / 13 Extinct t503 (unchanged) / 1 Control t836 / 2 Control t657;
PLAYTHROUGH.md regenerated by record_playthrough.sh PT_RC=0 (script's
t89 echo-comment updated? NO — header comment still cites t89 numbers;
display-only, fixed next docs touch). OQ-016 row annotated, STAYS OPEN
(A5/A6/A7 minutiae, strict-close). Lesson banked in §3d: re-verify banked
prose against the raw disassembly BEFORE implementing — the disassembly
was right twice now (t87 table, t93 guard) and the prose wrong once.
T92 LANDED (measurement pass for the CODE task — budget-interrupted,
honest negative, NO code change, NO closure): the picker disassembly was
completed and CORRECTED the tier order: §3b's "sentinel skips preferred
scan" was wrong in one direction — guards 0x400fb (outer head, chosen!=-1
-> exit) + 0x4010d + 0x4013b prove precedence sentinel(-2) > FIRST-
preferred-member > uniform rng, all [verified] (aicode.md §3c). NEW
MEASUREMENTS: (1) preferred list 0x67be re-dumped byte-exact; membership
math over rows 0..65 => ONLY values 1,47 can match (pin-test spec flows
from this); (2) sentinel flag DAT_00074902 LIVE: 0x0f in the user's
playcap 60.sav (every AI race flagged — sentinel is ACTIVE in the shipped
scenario) vs 0x00 in r1deep scripted slots; probe self-validated (rowcount
66, row-0 mask +0x47) on all three slots via the corollary member index
B+0x82bb0+X; (3) sole-code-referrer census for 0x74902 (only data false
hits); (4) named residual: -2 pseudo-target consumer semantics (completion
guard 0x46bbb is zero-extended cmp >= 0xffff, so -2 indexes row 0xfffe —
NOT safe to copy blindly; rewrite models sentinel as "no pick, no progress
this turn", §3c). OQ-016 row annotated with t92 status; rewrite delta
remains = t93 by the one-task rule. Gate GATE_EXIT=0, ledger_audit LEDGER
AUDIT OK.

T91 LANDED (STATIC task — W6-A4 AI RESEARCH PICKER CLOSED to docs/re/
aicode.md §3b): the field "race+0x1d4e" identity was the lock: turn call
site 0x2502f passes EAX=0x74744 to FUN_00046aec, and 0x74744+0x1d4e ==
DAT_00076492 — the SAME table t90 censused as the expansion target (0x1d5c
== DAT_000764a0 accumulator). Exhaustive write census over obj0: raw u16
0x1d4e scan = exactly 6 hits (all in FUN_00046aec completion/clear +
FUN_00046e84 indexed read); disp32 0x76492 = 19 insn sites, VALUE writers
only 0x40164 (FUN_00040018) and 0x47e34 (research-window UI = human path);
0xffff writers 0x22db7 init / 0x43f5b completion-clear / 0x47880 / 0x47985
(UI); disp window 0x1d00..0x1dff confirms no second base. PICK LAW: gate
0x3eb1d calls FUN_00040018 iff target==0xffff -> legal candidates (skip
owned, FUN_00046d3c prereq chain, cap 0x20) -> preferred-list scan (static
0x67be 23 u16, zero writers) -> DAT_00074902-bit race rng%100<45 sentinel
-2 -> uniform rng — research and expansion are ONE per-race slot picked by
ONE law. Build-completion grant FUN_00046e84 (sole caller 0x39173, item-
completion branch) rng-picks a legal tech and sets owned mask +0x4a/0x4b
directly, never touching the target word — the t90 "picker may be in
0x41260" hypothesis is RESOLVED: it was the grant path, not a pick. NEW
tool scripts/r1_t91_picker_census.py (boundary-verified disp censuses +
pinned sites, RC=0; objdump --start-address needs 0x prefix — trap fixed
mid-run). rewrite delta deferred to t92 by one-task rule. Gate
GATE_EXIT=0, ledger_audit LEDGER AUDIT OK.

find the writer of race research-target word row+0x1d4e (and its partner
+0x1d5c accumulator reset sites) in the restored image. t90 narrowed the
field: the completion consumer FUN_00046aec READS +0x1d4e and clears it
to 0xffff on completion (aicode.md §3); the 0x257cf call site of
FUN_00046fa0 is only a 0x1d72-byte restree buffer COPY (0x46870 loader
fallback + 0x20c48 copy primitive) — so the PICK happens in the AI
command executor FUN_00041260 (callees 0x38818 build-cmd/0x39894 —
aicode.md §1 P8) or in the research module around 0x46fa0 (grep the
image for moffs/disp disp reads+stores of 0x1d4e relative to row base
0x2b057+race-row and of the restree runtime 0x7478b preferred mask).
Method: objdump full-code scan for imm 0x1d4e / 0x1d5c operands
(store-form census pattern = scripts/r1_t86_write_census.py), then
decompile the enclosing function(s). Bank the PICK law in aicode.md §3
(rewrite researchPhase uniform-random pick is UNCITED — if the original
law is e.g. preferred-list-first like expansion 0x40018, bank the exact
tier order + rng thresholds; rewrite delta = t92, one task per session).
Rationale: t90 mapped the AI turn loop end-to-end; the two W6 items the
map feeds directly are A4 (research picker — the ONLY AI decision still
with zero cited law: build=done t28, expansion=selection half closed
t90, diplomacy=structure cited) and A5 (order enum). A4 is cheaper
(single field-writer census) and closes a rewrite placeholder the user
explicitly named. A5 next after. Sitting watch: live-timeline 5.69 GB,
user idle at t=1254 all week (sitting check 2026-10-26 16:40 ran clean:
no new turn-boundary rows past t=1254, t85g sitting stands as newest); a
NEW turn-boundary sitting outranks this -> scripts/r1_t85g_sitting.py
first, and any new sitting's combat frames are a free cross-check of
combat.md S2j (volley steps == design Levels).
OQ-021 passive watch continues (boundary sample 23/50, selector never
armed).
T90 LANDED (STATIC task — W6-A3 AI TURN LOOP MAP CLOSED to docs/re/
aicode.md, first content of that file): full phase-ordered map of the
original turn: master FUN_00024f24 (single caller 0x55f06 in the
END-TURN dispatcher FUN_00055df4) = random-event window -> income
0x2501c -> ship orders 0x25023 -> research 0x2502f (FUN_00046aec) ->
growth 0x2503c (t81 law) -> pop-cap 0x25056 -> per-race AI 0x25083/
0x250a5 (FUN_0003e6e0, SKIP iff row idx == DAT_0007458e player idx) ->
scored-star ownership scan (the INC-word producer at 0x251a2 for
DAT_00048300 — first cited producer path near the OQ-021 field) ->
command-exec tail incl. 0x2554f FUN_00041260 (the AI acts through the
SAME gun/ability primitives 0x49f28/0x39c10 as the player — callee-set
verified). Per-race decision block FUN_0003e6e0: eliminated-race fleet
DEATH law (0x40ec0 collect -> 0x49d2c per ship), extinction writer
(row+3 := 0xffffffff + event 0xa), decision block 0x3ea54 order =
diplomacy chain (0x3ecb8->0x3ef2c->0x44690->0x3eb88) -> build-selector
loop (0x3f130 called ONLY at 0x3eade on queue-empty own planets, gate
[+0x5a]==0 && [+0x54]==0xff — t28 law re-verified from the caller side)
-> expansion 0x40018 -> race maintenance 0x43b50 (integrity restore
ship+0x8c := +0x98; global attitude FLOOR enemy-strength+20 write at
0x43c36; moves x2 recharge loop 0x43c5b — the t85g boundary recharge is
THESE TWO sites) -> per-ship orders 0x40178 (kind/target +0x58/+0x59;
congregation-to-nearest-friend via 0x4aa10 starlane-cost table 0x45beb).
Expansion SELECTION law cited: tech-legal candidates (0x46d3c prereq
chain, restree rows) -> preferred-list scan (runtime 0x67be 11 u32) ->
rng%100<45 sentinel -2 -> uniform rng fallback; store DAT_00076492[race]
(19-site census). Research COMPLETION law cited (progress = +1/planet
gated govtype==2&&word<15, + planet RES word; x1.2 f64 pair
0x3feb3333; >= cost -> owned-mask +0x4a/+0x4b). NEW tool
scripts/r1_t90_callgraph.py (rel32 edge census over obj0 + pinned caller
sets, RC=0; pkl at work/t90_callgraph.pkl). NO ledger closure (strict-
close — structure map, not a constant/formula closure): OQ-016 row
annotated with the t90 status + explicit STILL-OPEN set (research PICKER
= A4, order ENUM = A5, 0x43b50 tail/0x2ef60 cases = A6/A7, random-event
module). No rewrite code change (map task by design; delta candidates
listed aicode.md §5). Gate GATE_EXIT=0, ledger_audit LEDGER AUDIT OK.

T89 LANDED (CODE task — OQ-010 CLOSED, the loop's first static-law closure
with changed code sites): the assignment executed in full: (1) rewrite/src/
game/campaign.cpp attackScore volley = SUM of researched cat-0 weapon Levels
(NumUses!=0 gate) replacing v1 MAX — cites volley loop 0x4a5c1 every-weapon
law + design[+0x52]==file Level (t87 t87_gizmo_table map); (2) defenseScore
= HULL layer only (pop/10 + fortify 2) — the v1 shield-addend was REFUTED by
the cited hit path 0x4b740, which never adds shields to a defense total but
clamped-absorbs MIN(damage,[t+0x90]) and spills (0x4b7c4..0x4b7d1); the split
is now Campaign::absorbSplit (campaign.h) used by combatPhase: capture iff
volley - absorb > defenseScore; (3) the uniform(0,10) noise draws REMOVED per
the S2g measured-negative hit roll — decision (b) of S2i taken explicitly,
rng_ re-diversion regenerated ALL timelines and every checked seed stays
FINITE inside the 1200 gate budget: 2024 Control t777, 42 Extinct t581,
13 Extinct t503, 1 Control t842, 2 Control t677; PLAYTHROUGH.md regenerated
(record_playthrough.sh echo-lines carried a stale 600 literal since T41 —
fixed, display-only); (4) new shieldChargesFor() = SUM researched cat-1
Levels (charge law 0x49f15); (5) TEST(campaign_combat_law_oq010) pins
re-extracted file sums (10 weapons SUM=49, 6 shields SUM=16), the full-vs-
no-tech volley delta == 49 (a MAX model cannot produce 49), absorb/clamp/
spill edges, seed determinism over 40 FFA turns: 109 tests 0 failed.
Ledger: OQ-010 row CLOSED (status cell + STATUS t89 with sites + caveats);
ledger_audit default open set updated to
{003,005,016,019,020,021,023}; STATE ledger block mirrors. combat.md gains
S2j (landing + honest aggregate-model caveats: per-ship slots, same-system
gate 0x4b982, range gate 0x4ba57, per-shot power accounting are NOT modelled
— OQ-019 territory); turnloop.md §5 rewritten from [INFERRED] to the cited
law. BLOCKED t89a budget-block marked RESOLVED. Mid-task self-corrections
recorded: first defenseScore draft folded shields into the total (contradicts
0x4b740, fixed before build), vector<bool> proxy trap in setAllTechs (fixed),
const-qualified atk blocked SA_DoublePower doubling (compiler caught, fixed).
Sitting watch: no new turn (all readouts t=1254). Gate GATE_EXIT=0, ledger_audit
LEDGER AUDIT OK (open set now {003,005,016,019,020,021,023}).
T89A LANDED (scoping pass for the t89 CODE task — budget-interrupted, honest
negative, NO code change): the assignment's own "check first" gate EXECUTED
and PASSED — rewrite/src/game/campaign.cpp:1247-1322 IS a combat phase
(attackScore :1204 / defenseScore :1226 / capture walk :1289-1321, advance()
:1376), so the "rewrite never modelled combat" BLOCKED branch is DEAD.
Scoping measured the structural constraint (S2i): no per-ship gizmo
inventory exists in the rewrite (ShipInTransit {owner,from,target} only,
fleet_ cleared every turn campaign.cpp:929), so the upgrade is an
AGGREGATE-law change: (a) volley = SUM of researched cat-0 Levels replaces
MAX (:1217, cites 0x4a5c1 every-weapon law; file cat-0 rows re-verified
this pass: Levels 1,2,4,4,1,4,6,4,10,13 / NumUses 1,1,1,1,5,1,2,2,2,3);
(b) the :1275/:1305-1306 noise draws are an UNCITED v1 abstraction the S2g
measured-negative determinism forbids — removal decision + PLAYTHROUGH
regeneration procedure banked; (c) shield-then-hull maps to fleetDamage_
ordering, no new pool invented. docs/re/combat.md S2i + OPEN-QUESTIONS
t89a status + BLOCKED t89a (budget interrupt, supersession note for the
t70 research-block entry) written. OQ-010 STAYS OPEN (strict-close: closing
measurement = the code change + its pin test). Sitting watch: live-timeline
5.68 GB, all readouts t=1254 DAT_482fb=14 — no new turn, assignment stands.
Gate GATE_EXIT=0, ledger_audit LEDGER AUDIT OK (open set unchanged
{003,005,010,016,019,020,021,023}).
T88A LANDED (S2g audit + COMMIT LAW): re-verified instruction-by-instruction
every load-bearing t88 draft claim (dispatcher 0x4a360 category legs, gate
0x49f28 [ship+0x62], volley loop 0x4a5c1 stored-order law, gun handler
0x4b8e4 same-system/range/damage gates, hit call 0x4bb56 arg law, hit path
0x4b740 full body incl. two-layer clamp + death 0x49d2c + event 0x55a60) —
census tool scripts/r1_t88_caller_census.py RC=0 (6 callers of 0x4b740,
LCG unique 0x7825b, zero rng edges [0x4a360,0x4f097)). NEW MEASUREMENT: mode
census of all 13 callers of 0x49f28 — mode==1 COMMIT edges are EXACTLY
0x25560 (gun) and 0x25570 (ability 0x39c10) inside player-command-exec
0x2547c (per-system loop stride 0x60 @campaign+0x3335, ah==3 gun / ah==2
ability / ah>=4 assert 0x2a438); AI-attack module + volley loop all pass
mode==0 dry-run. Self-destruct 0x4d191/0x4d2dd pass the dispatcher mode var
(0x4d2dd at-war-gated [edx+0x12fd6]==2). Banked docs/re/combat.md S2h +
OPEN-QUESTIONS t88a status. OQ-010 STAYS OPEN (strict-close: needs the code
site change = t89). No code change this iteration. Gate + audit green.
T87 LANDED (W6-A2 gizmo dispatcher case table + column map CLOSED):
(c) CLOSED-BY-MEASUREMENT: gizmos.txt -> design record map 76/76 rows,
76/76 names, 10/10 fields (tool scripts/r1_t87_gizmo_table.py exit 0;
loader FUN_00049074 store sites 0x49183..0x491d3 + runtime join save/50.sav,
B=0x1bf4d8 6/6 anchors, member=B+0x82bb0+X). CORRECTS t86: +0x4a = FILE
Special1 column, NOT Industry (the t86 75/76 "Industry" match was value
coincidence); +0x46 is Industry. Post-pass 0x4923a + Cat jump table 0x344b0
derive +0x52/+0x56/+0x5e/+0x62/+0x66 from Level (cats 0-3) or Power (cat 4).
(a) case table decoded (combat.md S2f, all 13 case bodies disassembled):
0x4cd90 is the SPECIAL-GIZMO ACTIVATION handler (tree trap: every jbe after
cmp+jb captures a SINGLE cl value, not a range) — 0x24 Recaller target-list
reset, 0x26 Smart Bomb area fire GATED on relation byte==2 (0x12fd6 matrix),
0x2e Gravimetric Catapult negates ship xyz, 0x35 Cannibalizer self-damage +
moves gain, 0x38 Condensor range scan, 0x3a Remote Repair heals clamped at
NEW FIELD +0x98 = max integrity, 0x3f/0x39/0x41/0x45 flag/charge ops
(+0x9c bits 2/4/0x10 — Invulnerablizer sets the absorb-null bit t85g saw at
0x4b7bc), 0x48 Self Destructotron = 0x4d075 (t85g's "combat loop" SCOPED to
this case), 0x4b Hyperfuel +40 moves; mode==1 charges power before the
effect (0x4d594). (b) 0x43a4c identity CLOSED: NOT star-defense — the
DIPLOMACY-ON-ATTACK handler (attitude -= 10*(word[0x13bc4]+1), doubled at
state==3, at-war short-circuits, attacked-bitmap [[edi+2]>>16 + 0x48304]
bit-set). OQ-010 stays OPEN (strict-close): hit-probability roll still
unseen anywhere, firing order lives in the generic-gun caller chain (t88);
the four 0x4b740 callers banked. No rewrite code change. Gate + audit green.
T86 LANDED (W6-A1 shield-layer census + attacker-object correction):
tool scripts/r1_t86_write_census.py (store-form byte census, objdump
boundary-verified, R12-safe; control passed: finds 0x4d1ea). Results
(docs/re/combat.md S2d): ship +0x90 = SHIELD CHARGES with full writer set —
charged by CAT==1 gizmo Level design[+0x56] (0x49f15 per-gizmo loop over
ship+0xab count [ship+0x15a], gate gizmo[+0x33]&0x20; fire loop 0x4a71f;
zeroed at fire-loop entry 0x4a6a6, by flag [ship+0x9c]&8 at 0x4a73a, and in
0x4a756 init which also sets +0x88 = gizmo-power sum 0x4a99c). CORRECTED
t85g: EDI at 0x4cddc = 0x7650c + 0x6a*gizmo (static design table; 76 rows
names byte-verified from held-turn slot 48 via string-anchor base vote —
note r1_sav_scan anchors need payload strings, 'Factory' needle alone gets
zero votes on this slot) — NOT a battle-built combat object; dispatcher
0x4cd90 case cl==0x3x/0x4x family routes the fire modes, 0x4b740 hit path
re-read whole (flag +0x9c bit0x10 zeroes the +0x90 absorb; +0x9c bit2/bit3
set on shield/hull overflow). Design table values measured live (weapons
+0x3a=range 25..1000, +0x56=level only for shields 1..5). OQ-010: shield
identity CLOSED-with-evidence-in-doc, row STAYS OPEN (hit prob / order /
0x43a4c / +0x4a column identity remain — strict-close). OQ-021: no new
boundary frames, passive watch continues. Gate + ledger_audit green.
T85g LANDED (t1253 sitting adjudication — FIRST mid-turn combat frames):
user played turn 1253 (alliance proposal #2 to Orfa DECLINED, war on
Ungooma, one Ungooma fleet destroyed, return fire) and saved slot 4 at
t1254. Captured: ring + banked copy work/r1/playcap/evidence_slot04_t1254.
SAV (nine stale watchers killed first; one live kept). Findings (docs/re/
combat.md S1-S3, scripts/r1_t85g_sitting.py + r1_t85g2_slots.py): ship
+0x8c = INTEGRITY with volley-step decrements to 0 then owner->free
(death law, MEASURED mid-turn for the first time); +0x88 = MOVES with
boundary recharge; +0x90 = SHIELD LAYER live in-battle (0->10->5->0
cycles, design-dependent, always 0 at boundary); return fire VERIFIED
(player slot14 40->38->36->34, matches testimony "fired back once or
twice"); static: the ONLY +0x8c subtract in the image at 0x4d1ea inside
combat loop 0x4d075 (distance-squared range gate, xyz law cross-confirm)
-> hit path 0x4b740 two-layer clamped absorb -> death handler 0x49d2c.
Diplomacy: PROPOSAL moves the AI-side cell (+39, corrects t85c); war
reciprocity law reproduced a second time. OQ-021: DAT_482fb OSCILLATES
(8..15) independent of territory — systems_full hypothesis FALSIFIED
(0/786 rows match). PLAN.md gains W6 (AI behavior decode A1..A7, user-
requested loop for closing rewrite placeholders). OQ-010/021/023 rows
updated with t85g statuses; all remain open (strict-close).
T84 LANDED (contract-compliance sweep): every CLOSED ledger row audited
for BOTH legs (cited evidence + changed-code-site-or-explicit-disposition)
-> 12 full rows PASS; two real gaps fixed: OQ-004 row now names its code
site (formats/bin_table.h, consumer main.cpp:151 counts-only) and the
7-item closed-index block now cites code sites per item or marks
ANALYSIS-ONLY (OQ-008 fresh-start-only, OQ-009 W-B input) — all cited
paths verified to exist before commit (ai-data.md, loader.md present;
ui.cpp has 9 fnt refs). Tooling traps banked mid-audit: (1) '| open |'
wraps across lines -> whitespace-join rows before status match; (2) the
index block must not start lines with bare ^OQ- or row tools misparse it
-> entries now prefixed '- >'. NEW scripts/ledger_audit.py reruns the
whole check (open-set equality + leg audit): AUDIT_RC=0, open set
exactly {003,005,010,019,021,023}. OQ-020 confirmed status BLOCKED (not
open) + legs present. Docs-only turn, no code change.
NEXT t85: open items are ALL capture/user-blocked; remaining productive
offline work is thin by design. Do one honest loop-state consolidation
pass (STATE/BLOCKED single-source the user-ask; verify scripts/
ledger_audit + r1_playcap are referenced from STATE), then STOP-REPORT
to the user: the loop cannot close the last six items without the
r1_playcap session (repeat exact command + what to do in-game).
T85b LANDED (playcap harness repair + first-capture analysis; user report:
combat analyzer OOM-killed mid-run on the multi-sitting capture):
(1) ROOT CAUSE measured: r1_t85_combat loaded ALL of live-timeline.jsonl
(4.3 GB, 191k rows x up to 107 ship windows) = 65 MB/1k points, projected
12.1 GB on the 16 GB VM -> thrash then SIGKILL. New scripts/r1_stream.py
streams: offset index only, ONE point in RAM; whole 4.3 GB pass = 290 MB
measured. All three t85 analyzers rewritten onto it (victory now prints
per-turn, not per-slot; combat caps stdout 400 lines and keeps counting).
(2) DATA-HYGIENE LAWS (each measured first, r1_stream docstring): trusted
ORDER = (file_mtime_ns, file); DEDUP first-per-(file,mtime) — watcher
`seen=set()` re-init AFTER the jsonl re-ingest banked 73,052 dup rows
(FIXED at source r1_playcap_watch.py); STALE-INSTANCE = a second dosbox
picked up an older save and autosaved one End-Turn BEHIND live for days
(12,516 rows; file-order diffing FABRICATED bounce transitions — the first
relation-analyzer run showed 260 transitions, the true set is 24).
(3) HARNESS LEAK: 12 stale watchers (up to 6 days old) were alive at once
— each sitting's setsid watcher never died (--no-exit kept it looping;
single watch.pid tracked only the newest). Killed all 12 by recorded-PID
+ /proc/cmdline verify; vnc harness now REAPS watch*.pid before relaunch;
live watcher replaced with fixed code (session untouched, dosbox alive).
(4) FIRST-EVIDENCE BANKED from the user's campaign (turns 37..1131):
diplomacy.md §11 (war = cell 1->2 reciprocal at t887->888 per user's
stated war-on-Minions; Orfa alliance = attitude +280 sustained, NO cell
change; values {1,2} only) + score.md S6 (DAT_482fb census: never crossed
half, max 23/50, selector never armed at 26 systems_full; t912 spike
11->22 unexplained; >1/2-on-DAT_482fb stands CONSISTENT, not closed) +
ledger rows OQ-010/021/023 status notes. OQ-010: ZERO destruction in 1100
turns incl 244 war turns — turn-boundary sampling cannot see combat; the
capture class that could is in-battle recording, banked in the row.
NEXT: user asks remain open (victory screen seen by t1131? alliance
ACCEPTED or just proposed?); analyzers run clean on all future sittings.
gate GATE_EXIT=0, ledger_audit AUDIT_RC=0 (open set unchanged).
T83 LANDED (OQ-005 W3 sanctioned route executed to its boundary):
decoder FUN_0005caac caller census = 75 direct sites / 32 functions;
header law re-read verbatim @0x5cabe/0x5cac7 (dims ALWAYS record-start
[ptr][W-1][H-1], clip rect comes from caller widgets); both raw-[reg]
arg-prep sites (0x50535,0x50e60) adjudicated as screen-coord/dst pushes,
not dims; cache load FUN_0001fc34->FUN_00020acc = verbatim file->slot
copy, no dims parse/transform anywhere. Net: NO non-standard dims reader
exists in the image — residue closure class unchanged (drawn-frame, R13),
sanctioned negative now cited in shp.md W3 + ledger. Mid-turn trap:
functions_full.tsv offsets are HEX (decimal bisect gave garbage func
0x142ca, discarded). No code change (ShapeLibrary garbage-dims behaviour
already matches original: report, never allocate).
NEXT t84 (contract-compliance sweep, offline): verification criterion
demands EVERY closed item names evidence AND the changed code site —
scripted audit over docs/OPEN-QUESTIONS.md closed rows (heuristic:
contains a hex address|offset AND a rewrite/ path|'no code change'|
'documented default'); fix any row missing a leg by tracing its doc;
this directly de-risks the final gate-of-gates and has zero capture need.
T82 LANDED (ledger triage + capture readiness): open set confirmed
exactly {OQ-003 packed-entropy residue (OQ-005 closure class), OQ-005,
OQ-010, OQ-019, OQ-021, OQ-023}; every one states its closure class in
the ledger. Harness fact surfaced: OQ-021's scratch build is
work/r1/game/ascend.exe (lowercase; mounted as C:\ASCEND.EXE). NEW
scripts/r1_playcap.sh BANKED READY: one user-run session of the original
closes OQ-021+OQ-023+OQ-010 together (colonize >50%; war+alliance
accepted; one fire exchange), autosave ring + instant per-slot readout
of T/scored-stars/selector/rank; title-menu T=0 slots carry uninitialized
selector heap (0xC500 observed) -> analyzer law: trust T>0 slots only.
Safety invariants kept (scratch-only mount, -time-limit, pkill -x only);
interactive BY DESIGN for the user, agent never plays.
NEXT t83 (offline, sanctioned route ONLY): my first t83 idea (grammar-
differential of well-formed vs undersized heads) was checked against R2
and RETIRED pre-attempt — R2's six angles include span/dims/metadata-slot
variants, and R2 names the sole sanctioned route: the exe shape loader
via call graph + live image (W3). t83 = caller analysis of the banked
decoder FUN_0005caac (control-byte grammar source): find its callers in
the restored image, decompile the loader caller, and look for where an
in-record DIMS field would be READ (the grammar asm never mentions dims;
a consumer read site would name the offset). If no caller reads dims,
bank that as the hard static boundary for the residue.
T81 LANDED (OQ-003 field-meanings leg): growth pass decompiled
(FUN_00038f68 -> work/coswnd_decomp/38f68.c) and revalidated against the
FULL 20-slot r1deep timeline: 90/90 owned-planet transitions agree
(rate = stored PROS + 1 iff owner != DAT_0007458e and PROS<4; threshold
DAT_000066e4; cap clamp to +0x4a; upkeep>=cap resets accumulator; slot0
excluded as banked seed residue, slot n in {0,1} fitted because
DAT_00012e10 reads 0 across all r1deep slots). Live global votes 20/20:
DAT_000066e4=50, DAT_0007458e=0 — rewrite campaign.cpp growth block
matches EXACTLY, evidence upgraded, no code change. +0x4a=POP CAP and
+0x55=population SEED named (equation re-measured; uniform +2 = banked
event-50 bonus, not a gap); +0x0a explicit UNMAPPED. Mid-turn trap:
payload-FILE reads at 0x82bb0+X are pre-relocation garbage (returned
threshold 100); only live member P0+0x82bb0+X is valid — banked so no
future turn re-trusts the file read. scripts: r1_t81_census.py,
r1_t81_mpop.py. OQ-003 residue now = packed-entropy regions only (shares
OQ-005 blocked closure class).
NEXT t82 (ledger triage + capture-class prep): the open ledger is now
OQ-003 (packed-entropy residue), OQ-005 (blocked), OQ-010 (one-battle
recipe banked), OQ-019 (blocked), OQ-021 (BLOCKED-USER-LEVEL), OQ-023
(state-enum capture). Verify each still states its closure class and
exit-code route; prepare (do not run blind) the cheapest R1 capture that
would close a real item: the one-battle OQ-010 recipe — confirm its
harness still exists and gate-cleans, record readiness, no spiral.
T80 LANDED (OQ-003 join leg, offline): star->planet JOIN CLOSED by
measurement — pointer law star-rec +0x2A/2E/32 u32 P -> planet NAME at
file offset P-2507337 (116/116 RESUME.GAM; banked-base form P-K-0x24),
plus pool-membership law u8 name-0x18 == owning star idx 138/138 over the
whole contiguous stride-123 planet pool 0x8e0e..0xd05c (22 IV/V rows are
beyond the 3-pointer capacity and unlinked — membership field is the
authoritative join). Star chain: 96-B records mirror BYTE-VERBATIM into
live RAM (50/50 rows; single 12-byte repair window on Barataria's 0xFF
tail) — copied-not-parsed re-confirmed star-side. Mid-turn "two planet
regions" reading caught and corrected before commit (bad walk-back base;
t75 0xaae2 chain = mid-pool entry, its owner-join law stands). Star-idx
field t50 [inferred] -> [verified]. OQ-003 stays OPEN: +0x0a/+0x20/+0x4a/
+0x55 meanings, counter identity, packed-entropy regions remain; no
rewrite behaviour change (rewrite is fresh-start-only; mapgen already
generates 3+ planets/star).
NEXT t81 (OQ-003 field-meanings leg): the t50 banked unknowns +0x0a/
+0x20/+0x4a/+0x55 (name-0x24-base) — census each across the r1deep 20-slot
timeline for monotone/turn-coupled behaviour (population/shield/production
candidates), and cross-check candidate meanings against the banked income-
law channel words; every field either gets a cited meaning or an explicit
UNMAPPED verdict.
T77b LANDED (diplomacy state-enum: honest block, one retraction banked):
static re-read of the chooser entry @0x447ba (`cmp byte [ebp+0x1c0],0 / JE
skip`) proves the relation-state byte gates ALL diplomacy emission, but
the banked corpus cannot settle WHICH nonzero value is war vs allied: an
idle-slots census (945 slots) shows ONLY value 1 off-diagonal and the §7
rung structure admits no injective enum from idle data alone. A first
window-census draft claiming '1 = AT WAR' was CAUGHT BY CROSS-AUDIT
against the chooser gate and RETRACTED in diplomacy.md §10 before any code
site consumed it (also recorded: the base-0x12e16 window needs per-run
re-validation before any future census trusts it; the drift-filter rerun
was itself mis-implemented — noted so its all-drifted output is not
re-read as confirmation). Kept facts: matrix structure law (attitude i16
+0x1b2+2t, state +0x1c0+t, row stride 0x1ee @0x12e16 static) + live
START_ATTITUDE values 310..620 match race files verbatim. LEDGER: OQ-023
stays open with the state-enum RESIDUAL RE UNKNOWN named explicitly
(same closure class as OQ-021: interactive session); diplomacy.h header
comments updated MEASURED->[inferred]-retired ( DECLARE_WAR range
re-measured 130..450 across 21 race files mid-turn, my draft's 150 fixed
before commit). No rewrite behaviour change this turn; 108 tests stand.
NEXT t80 (OQ-003 field-semantics leg, offline): star-record fields
(name-0x1C small per-system value; name+0x10 stride-0x39 sub-pool; star
+0x17 owner byte per §9; starlanes table 0x16147 stride 0x27 owner bits
+0x20) cross-joined against .gam star chain (0x1e46 stride 96) and
planet chain (0xaae2 stride 123) over the banked r1deep slots — every
field gets a join or an explicit UNMAPPED note; save-writer code dive
(FUN_0004* save family) only if joins suffice to name the packed regions.
T79 LANDED (OQ-025 CLOSED same-turn it was opened): the t78 "non-shell-slot
at T=100" lead was a MEASUREMENT BUG — hypot(x,y) is the xy-PROJECTION of
the sphere point f32[x,y,z]@name-0x14; projection scatters discs by
geometry. Correct measurement (scripts/r1_t79_pos.py; records gated idx==k
+ planet-pointer-on-grid; in-play = chain head cut at slot DAT T) across
T=15/25/50/75/100 arms + r1deep control: shell radii FIXED (440,365,290,
215,140,65,50) at every size; shell POPULATIONS = halving law (shell0 =
T//2+1, shells 1..5 halve the remainder (rem 1 keeps), shell6 keeps tail):
15->8/3/2/1/1, 25->13/6/3/1/1/1, 50->26/12/6/3/1/1/1 (== the 2026-10-06p
battery table EXACTLY — the battery was an instance of the general law),
75->38/18/9/5/2/1/2, 100->51/24/12/6/3/2/2; zero monotonicity violations
everywhere (viol=0 all arms). Self-caught on the positive control (deep
run disagreed with the banked 0/1225 law -> checked my own reading before
doubting the banked law). Rewrite UPGRADED: shellRadiiFor(n) (mapgen.cpp
anon namespace) replaces the i%50 wrap (measured WRONG for T>50: slot 50
lives on shell 440 pop 51); at n=50 output identical to old table so
default timelines untouched; ladder test extended with per-size shell-run
expectations (108 tests 0 failed); mapgen.md §OQ-025 + ledger + mapgen.h
comment re-cited.
T78 LANDED (OQ-012(a) CLOSED BY MEASUREMENT + OQ-025 opened): GALAXY_MORE
button (windows.txt NEWGAMEWND rect 7,381..122,472 -> (64,426)) cycles FIVE
densities, each arm a fresh New Game, T read from slots via pointer law
(scripts/r1_t78_read.py over save/*.sav Memory): Average 50 -> Dense 75 ->
Very Dense 100 -> Vacuous 15 -> Sparse 25 -> wraps Average (runs
r1size-{033341,040859,041459,042719,043229,044658,045501}; labels from
screenshot crops, click law per run click.log). Harness bug found+fixed
mid-turn: env var is NCLICKS (CLICKS silently no-op'd two arms, re-ran
them). GATE FIX: the t78 capture harnesses leaked their Xvfb servers on
exit (t75 has a cleanup trap; the t78 scripts didn't) -> 9 orphan Xvbfs
held displays :90-:98, and the intro pixelcheck on :91 captured a stale
root window (1024x768) instead of the game; pkill -x Xvfb + EXIT traps
added to all three t78 harnesses, gate re-green (GATE_EXIT=0). Non-default-T POSITION law measured NON-shell-slot (T=100 chain
idx==k verified: 3537/4950 slot-radius inversions vs 0/1225 at T=50;
envelope max r=440.0 holds) -> new OQ-025 open, banked offline-solvable
from r1size-* slots. Rewrite UPGRADED: --stars CLI knob (main.cpp
Options::stars -> MapConfig::starCount, usage text), default 50 re-cited
mapgen.h, mapgen.cpp:92 comment re-marked DOCUMENTED DEFAULT (OQ-025);
test galaxy_density_ladder_matches_measured_sizes pins the five sizes +
connectedness + r<=441 envelope; 108 tests 0 failed; CLI spot-verified
T=100 and T=15 campaigns run. mapgen.md new §OQ-012(a) CLOSED section.
T76 LANDED (OQ-021 CLOSED-EXHAUSTIVE FINAL + OQ-023 lead): all 10 code
readers of the star-owner block DAT_00013bc5 decompiled (work/coswnd_decomp/
3ecb8.c 220a8.c 3a4e0.c 3eb88.c 439f4.c 44634.c 49c14.c 49d2c.c 500e0.c):
NONE is the end-ctrl comparator — 0x3ecb8 = per-race AI ATTITUDE scorer
(state table [obj+r+0x1c0]: 1=ally-ish path sums star-bitmap +0x14/+0x15
product with 0x67aa 31-byte record entries and 0x13b9c stride-6 weights,
applies -1/+3 on the two-others-ally comparison and -2/+4 on relative-
strength deltas; state 2 = rank-distance path clamp(0,3); accumulator
u16@(obj+r*2+0x1b2) clamped [50(0x32), 950(0x3b6)] with hi-word gate
(obj+r*2+0x1b0)>>16); 0x439f4 = ally-bitmask builder (state==2 races);
0x44634 = pair-adjacency test on star bitmap +0x17. => comparator ABSENT
from image at full scope (confirms 06s; t74 S5 + t75 capture death, see
BLOCKED T75 POST-MORTEM). Corpus adjudication: 745 banked slots across
every r1* run, 0 with DAT_43510/DAT_4350c armed — idle scripts never
colonize, so no banked evidence can ever close OQ-021. LEDGER UPDATED:
OQ-021 BLOCKED-USER-LEVEL, default >1/2 unchanged.
(t80 NEXT superseded — see T80 block above.)

T56 LANDED + CORRECTED (PER-TURN BRACKET PARSE, income-law.md T56/T56b;
BLOCKED t55 CLOSED): End-Turn (511,67) works-but-flaky (advance try 3, then
6/6 at 25 s); channel words +0x44/+0x46/+0x48 = RATES not stockpiles
(verified across all 19 ck); growth tick player +PROS / AI +PROS+1 fresh
40/40 (t24 law re-measured); word +0x52 = CELL INDEX NOT item id (corpus
0..59 > 39 items; S10 map confirmed) — mid-turn correction of an earlier
wrong reading; FRESH-RUN AI opening build = AGRIPLOT (+0x54 := 0x01) 4/4
thin; c1c -1 co-occurrence with queue flip 4/4 (cell reservation at queue
time [inferred]); T56b per-pair offset census + heap BASE-DRIFT hazard law
(never one absolute base across a session's checkpoints). Player home sits
at RECORD 89 — parsers must scan 151.
T57 LANDED (OQ-012(a) density probe AMBIGUOUS -> best default fixed-50,
BLOCKED t57: one-click (65,427) during setup, fresh-map star count 50 ==
cosmos.txt default; click-inert vs cycle-wrap inseparable (glyph readout,
R13); scripts/r1_t57_density.sh banked.
T57b LANDED (income-law.md): OQ-020 item SUPPLY side closed verbatim
(FUN_00039b6c + raw-asm slot-writer attribution 0x38fc8..0x39003: top-up
OR word+2 hi |= p3; p3=7 MissileBase/ShortWhopper, 8 LongWhopper, 0
TractorBeam skips write; flag&4 items exactly 17/28/29/30 [battery];
EBX 45/45/90/200 + p4 slots UNATTRIBUTED; same-turn draft mislabels
retracted in-place). Decrement period capture-gated (zero flag&4 slots in
corpus, T49); r1_ability_charge.py banked; OQ-020 stays OPEN (period half).
T57c LANDED (income-law.md): OQ-020 use path FUN_00039c10 fully mapped
(counter = slot word+2 hi, use-gated write |= (c-1)<<8, OR-semantic hazard
flagged unresolved, EBX=range x32 gate consumer located, +0x70 parallel
countdown). Amass formula UNMEASURED, OQ-020 stays OPEN, capture-gated
(zero flag&4 slots, T49). OQ-006 stale-NEXT corrected: CLOSED 2026-10-07.
T58 LANDED (income-law.md T58; ledger OQ-019 escalated BLOCKED-USER-LEVEL,
OQ-016 queue-chain note): deep run turns 0..52, 113 ck. Scale leg NULL at
depth (565 slot obs, 0 state-4/0 owned/0 moved, 0 landings) — no save-
observable route contains flight; only original-hardware capture remains.
First live t28 queue completion (Tubes->Agriplot re-queue, cheap-first,
player never queues). Threshold-50 wrap exactly once at pop 2->3, 8 AI
drops on pop steps; rewrite growthPhase unchanged. HARNESS LESSONS:
r1_trajectory_regression.py IGNORES argv (scans ALL runs) — read its header
before quoting numbers; the constant-7 byte at 0x1BF450+H is NOT the turn
counter (T42 law needs a KNOWN phys).
NEXT (t59): full-ledger classification DONE t58b — remaining open: OQ-005
(W3 in progress: recon banked docs/re/shp.md S7 — registration pass
FUN_00023388 sole-caller of FUN_0001fa60; t59 u32-scan NEGATIVE VOID by t60
file-provenance law (wrong file); INT21 wrapper cluster 0x777xx-0x77dxx
found, 74 CD21 sites),
OQ-010 combat application (static route bounded; scripted campaigns have NO
combat -> capture class same as scale), OQ-012(a) blocked glyph-readout,
OQ-016 attribution + OQ-003 meanings replay-only, OQ-019 scale
BLOCKED-USER (t58), OQ-020 amass capture-gated-unreachable, OQ-021
end-screen rides multi-hour gameplay BLOCKED-USER, OQ-023 build-work parked
by standing option-C decision (not RE). CONCRETE NEXT ACTION (t61b): DECODER FOUND t61 (docs/re/shp.md S9):
FUN_0005caac shape blit w/ control-byte grammar (C==0 end-row, C==1 skip,
odd literal C>>1, even run of next byte C>>1); cache module mapped
(FUN_0001fc34 accessor + 20 callers, FUN_00020acc raw-load, cache.cpp
strings). Corpus exact-span 27/208 libs clean, rec0 grammar well-formed
198/208; rec1+ prefix law NOT universal -> live-RAM anchor queued: grep
banked ck heap spans for loaded-shape run patterns (e.g. listbox stream
bytes) to pin per-record stream start; then full-corpus revalidation; then
REWRITE upgrade (PNG/sample renderer decision per shp.md S6 — rendering
before codec closure fabricates pixels; after closure it is legitimate).
t62 live-RAM anchor (shp.md S10): cache payload = VERBATIM whole-library
file copy (constant-delta image match ck113); runtime shape structs DO NOT
exist in RAM (negative) — [ptr][W-1][H-1] assembled per draw (widget
descriptor law: array +0x6d, u16 count +0xa1, stride 0x0d, type byte0,
+5 u32 -> FUN_0001fc34 -> FUN_0005caac). Payload-array base offsets from
regparm decompiles NOT trustworthy (ASCII-hit artifact banked; t61 slot-
flag readings VOID). CONCRETE: raw asm 0x3144a..0x31470 arg order +
FUN_00031660 to pin dims/pixel-ptr provenance, then corpus revalidation.
T63 LANDED (shp.md S11): both raw-asm reads done — widget pass passes the
UNADJUSTED lib base (record selection excluded there and in the cache);
FUN_00031660 = trivial row helper (closed). CONCRETE t63b: FUN_0005caac
prologue stack-arg mapping (stream cursor vs shape struct; clip pushes
0x14 survive per ADD ESP,0x14 @0x31467) + PLANETS.SHP inter-ck
in-place-rewrite test.
OQ-005 stays OPEN until revalidated across corpus.T64 LANDED (shp.md S12): blit input law code-pinned (5 cdecl args; stream
cursor = payload + u32[payload+8+8*sel] + 0x18); cache anatomy measured
([0x88][verbatim 1.10], base 0x242088); .tmp ARE libraries; DECISIVE
NEGATIVE: 0/12 loaded payloads satisfy the blit law autoplay — raw !=
draw-time payload. t65 RUNNING (r1ad-20261011-180908, proc_965332c0bf73 +
r1_intel_drive.sh proc_c5780e49dc24): intel panel opened via verified
(553,318) + 12 turns; post-run = strict blit-input scan on loaded/
rewritten payloads; RESULT t65 NULL (S13): 71 ck x 200 slots x sel 0..7
= 0 survivors despite verified click delivery + mid-run cache misses ->
blit-5arg path does not consume raw payloads. REFUTED t66 as a
SCAN-BASE BUG (shp.md S14): correct arg2 = slot+0x88 verbatim base (file
u64 dir at file+0x10 == u32 stride-8 series at PAY+8; tsz doubles as
rec0 virtual slot) -> 3504 strict survivors over 72 ck, raceflag sel1
pixels RAM==FILE. Caller idiom: slot=[widget+24], sel=[widget+28]>>16,
payload UNMODIFIED to blit — no transform pass. Rows x-unbounded
(writes clamp @0x5cd31/0x5cd62); exact-span 2xH = animation frames.
DONE t67 (b1b20b8): widget arglaw pinned (@0x31001..32: arg1=widget+4
DEST struct => W/H clamp is DESTINATION; slot [widget+24], selector
[widget+28]>>16, -1 skips); header-pair stream-start discriminator ran
with fixed bounds: 57/208 libs all-records-pass, 151 hold failing
records (UI-lib cluster) — NOT closure (shp.md S15).
DONE t67b/t67c: autopsy + unified law (shp.md S16,
scripts/r1_shp_unifiedlaw.py): V(k0 rec+8)/A(k>=1 rec+0x18 dims@+0x10)/
B(k>=1 rec+0x20 dims u16@+0x18) -> 1477/1557 records pass, 176/208 libs
clean; residual 80 records/31 files in 3 classes (span-undersized
planind+3cfgnew 26, simple-format cos_star 12, stragglers 42).
DONE t68: runtime table UNIFORM [measured ck072,
scripts/r1_shp_ramtable.py]: 4 verbatim-cached libs x all selectors,
hist {sel0 delta 8, k>=1 delta 24} zero exceptions (shp.md S17) —
S16 V/A law holds code-side; fixup-vary theory dead for table region.
OQ-005: codec grammar CLOSED (S9+S12+S14+S16+S17); dims-location
residue (80 recs/31 files + non-verbatim .tmp heads) recorded
BLOCKED-USER-LEVEL (needs human-verifiable drawn frame).
DONE t69: rewrite/src/formats/shp.{h,cpp} ShapeLibrary (container laws
S1, V/A stream-start S16/S17, S9 control-byte grammar with blit-faithful
write-clamp + untouched-destination semantics) + tests/test_shp.cpp
(raceflag law pins, in-memory container rejection, corpus parity floors
from the measured Python run). MEASURED: 107 tests 0 failed; corpus
208 libs / 1557 recs / 1484 decode-pass / 185 clean libs — EXCEEDS the
1477/176 floors (4096 dims cap added after a FAIL-class record's
garbage dim words triggered bad_alloc: decode REPORTS, never allocates).
DONE t70: ledger OQ-005 rewritten (closed portion cites S9/S12/S14/S17 +
code site rewrite/src/formats/shp.cpp + measured corpus; residue
BLOCKED-USER-LEVEL). OQ-010 triaged: batmode join=6 small funcs under full
analysis; static route at banked hard boundary; headless corpora zero ships
-> in-battle capture = OQ-019 class (BLOCKED entry filed w/ one-battle
closing recipe). Ledger open set now: OQ-010/OQ-019/OQ-021 (capture-class),
OQ-003/OQ-016 (replay-only/documented), OQ-012(a) (R13), OQ-023 (parked).
DONE t71: RECALC RESIDUAL CLOSED (income-law.md T71; ledger).
byte-exact FUN_00038ba4 recompute == stored +0x44/46/48 at ck001/020/060/
100 of the 52-turn run AND .gam-restored slots (5/5 everywhere). t55b
"missing term" + S6 52/139 were harness-era artifacts (pre-t33 raw slot
reads). Harness: r1_income_law.py --slot now finds ck/ AND save/ (was
silently failing late-timeline verification). Rewrite code UNCHANGED —
existing channel chain verified exact, pin campaign_channel_law_oq016.
DONE t72: OQ-021 restored-image scan — strings FOUND (0x83b16/0x83b2a in
a GAMEWND/..\coswnd.cpp pool => consumer module identified); VA==file
offset encoding re-inverted from known-good 0x2b224; zero u32 code-region
refs (R12: lead-out not proof). NEW bounded angle banked: 36 coswnd.cpp
functions never decompiled (batches 1/3 skipped coswnd).
NEXT t73: DONE (see T73 block) — t73b = eventwnd.cpp module decompile batch
(OQ-021 comparator hunt).

T74 LANDED (OQ-021 static CLOSED-EXHAUSTIVE + capture de-risked; score.md S5):
selector-writer hunt negative under ALL direct encodings (moffs, mod00/disp32
incl SIB-25, mod10 base, cmp grp, f6/f7) AND under runtime-relocated
full-RAM scans: relocated 0x43510 addr occurs EXACTLY 3x in 16MiB (= the 3
known readers), struct base 0x4348d EXACTLY 1x (0x1d740 end-EVENT-QUEUE
builder: c6 35 byte-stores, sub-record stride 13, type bytes 0..8 measured,
count u16@0x43502==9 both runs). f32 2/3: ZERO image-wide; f32 0.5: only a
data bitmask ramp. STRUCT MAP: 0x4348d queue (count/counters 0x43502/04/08),
0x4350c rank, 0x43510 fired-selector. LIVE OWNER LAW MEASURED: static table
0x3a095 (stride 0x162, owner byte +0x56) stays ALL-0xFF for the ENTIRE
campaign (19 slots, 2 runs incl deep ck067) — the BLOCKED recipe's inject
site is WRONG TABLE. Live copy = heap: found at corollary X=0x38ad8 in ck067
(16 owner-0 + 85 x0xFF of 101 cap; candidates cluster stride-0x162 phase-4,
(43 hits — pin with two checkpoints before injecting). Owner dword +0x54 in the
STATIC table reads 0xFFFF always (do not confuse with live +0x56).
T74b SCENARIO CORRECTIONS (offline, RESUME.GAM + ck067): total stars T=50
(hi-u16 DAT_16143 measured — NOT 101; my 101-record table scans over-ran the
table). .gam STAR CHAIN FOUND: 0x1e46 stride 96 x 50 records (names verified:
Masticon..Barataria); .gam contains NO 0x162-stride owner table (exhaustive
offset scan) -> owner encoding rides the planet/system records (t50 join
class), NOT a star-table copy. Discriminating injection band at T=50:
owned 26..33 (fires >1/2, not >=2/3) — use 30. RAM star chain is NOT
contiguous at name+stride 96 in ck067 (allocator scatters; chain-walk law
holds per-record via idx/pos anchors only).
CONCRETE NEXT t75 (capture, exit-code driven per R1 law): via r1_planet_layout
join, find the RAM byte within the 123B planet record that is player-owned in
a colonized AI/player planet (ground truth: banked ck corpus mid-campaign)
vs unowned; verify same offset in .gam planet chain (0xaae2 stride 123, t53
convention); inject owned=player at 30 systems' home-planet records in scratch
RESUME.GAM, boot r1_mutation_run pattern, end-turn x2, read DAT_43510 byte
(corollary idx) + end-screen screenshot. Fire @30 => >1/2; no fire => 2/3. If
owner ground truth unresolvable from banked corpora -> record one line
(capture class, needs interactive colonization), move to OQ-003 replay
semantics.

T75 LAUNCH (in flight): join SOLVED offline — .gam planet chain 0xaae2/123
+0x33 == RAM planet +0x57 (83/83 join rows on r1mut world incl owned Verithil
I==0; star-chain +0x33 writes VOID — unowned stars legitimately hold 18/250).
Chain spans 29 distinct stars; the 4 AI home stars are NOT in the chain
(zero-collision verified) -> injecting owner=0 on ALL chain planets = 29/50 =
58% band: fire => (50,58]% (>over half), no fire => >=58% (two-thirds class).
Harness banked: scripts/r1_t75_inject.py + r1_t75_run.sh (511,67 end-turn x4
at 30 s, t56 law) + r1_t75_read.py (per-slot owned/selector/rank + VERDICT).
rev1/rev2 FAILURE DIAGNOSED (shot-02 = still title menu): clicks went to
(318,333) = NEW GAME row; pixel-measured rows put Return-to-Current-Game at
(318,372). HERMESSEN needle useless at verify (text RAM-resident at boot from
the .gam). rev1 endturns=0 (absolute-vs-relative NOW bug, t75b); rev2 clicks
landed but game stayed at menu -> DAT_482fb stayed 0 = INVALID not no-fire;
read.py now tri-state (FIRING / NO-FIRE-with-counting / INVALID rc=1).
rev3 IN FLIGHT proc_f5c3fcaf82cd (r1thr-*, BOOT=200, resume (318,372) x6
from t=75, end-turns optimistic from t=150, adjudication POST-HOC: counting
>=1 star only happens in-campaign). On completion: read analysis.log ->
update OQ-021 (CLOSE only if FIRING or NO-FIRE-with-counting), possibly
campaign.cpp:738, gate, commit. If rev3 INVALID: one line per exit-code law,
OQ-021 capture needs interactive session -> BLOCKED, move to OQ-003.

T73 LANDED + CORRECTED (OQ-021 static, dark-zone HIT; docs/re/score.md NEW):
(1) ATTRIBUTION CORRECTION: work/attribution.tsv est_func is a BACKWARD-SCAN
estimate, NOT a function start — all 36 coswnd est_func values landed mid-
function (0/36 in functions_full.tsv); re-resolved to 12 CONTAINING functions,
decompiled all 12 (scripts/coswnd_run.sh, fresh ghp6 project, DecompileCombat
.java now env-driven DECOMP_TARGETS/DECOMP_OUT; ghp4/ghp5 untouched).
(2) t72's "zero u32 refs to the score strings" is REFUTED by corrected scan
base (t66 lesson): OQ-004 pool-relative immediates = str_off - 0x82BB0 (NOT
VA). push 0xf66/push 0xf7a sites = 0x2807b/0x280e7, inside the DARK ZONE
0x26b32..0x284bb which holds ZERO Ghidra functions (auto-analysis never
reached it) — that is why every static-xref route was blind there. Runtime
law re-verified live (r1deep-20261007-224831/41.sav): code relocates
0xf66->P0+0x83b16, 0xf7a->P0+0x83b2a exactly at the anchored site (window
0x280de.., block base == B vote); obj1 data at B+0x82bb0+X law re-confirmed
(item table 'Factory' name anchor).
(3) SCORE-DISPRODUCER LAW (dark zone 0x280be..0x280e7, raw objdump
-b binary -M intel on work/ascend_restored.bin — banked harness tool):
percent = TRUNC( DAT_000482fb * 100 / (DAT_00016143 >> 16) ) — mul-100 idiom:
lea eax,[edx*4]; sub eax,edx (=3N); shl 3 (=24N); add edx,eax (=25N);
shl edx,2 (=100N); mov eax,edx; sar edx,1f; idiv ebx (ebx = signed hi-word
of DAT_00016143 = total stars). "STARS CONTROLLED %d" prints DAT_000482fb
itself (push eax @0x28079 after mov eax,ds:0x482fb @0x28074); shown only
when DAT_0010ba0 == -1 == [ebp+0x58e] (0x28059..0x2806e gates). [inferred:
DAT_482fb = player-owned star count; producer not yet traced.]
(4) end-ctrl PRESENTER is eventwnd.cpp (NOT coswnd): jump-table handler
cluster 0x2c03a..0x2c0b6 pushes pool-rel end-*.txt names (0x130c/0x1319/
0x1333/0x1340/0x134d -> end-xtnc/-dest/-unit/-ctrl.txt + "Couldn't open %s",
payload 0x83ebc.. verified); file-name dispatch by ReadFile (0x7739d) +
strcmp (0x775aa) against 0x1371/0x1375 strings. DAT_43510/4350c: ZERO write
encodings in image (A0/A2/88/8A/89-05/c7-05/A3/80-grp scans over 0x200..
0x82bb0) — comparator consumer is a BYTE reader (a0 at 0x2c01d) fed by the
END-CONDITION EVALUATOR, which must live in the same dark zone (0x26b32..) as
its 0x280be sibling. CONCRETE t73b: enumerate dark-zone functions by
prologue/epilogue walk (objdump whole 0x26b32..0x2c600 span; find the block
containing 0x2c01d), grep for cmp idioms x*2 vs N / x*3 vs N*2 feeding the
DAT_43510 byte; default >1/2 stands until cited comparator.
HARNESS LESSONS: objdump -b binary -m i386 -M intel works directly on the
restored image (no Ghidra round-trip for dark zones); Ghidra function names
FUN_ + 8 hex digits (6-digit regex = silent zero); r1_sav_scan.find_base
returns (votes,positions) tuple — vote most_common(1) with >=5 threshold.
T85c LANDED (user testimony adjudicated against the banked stream):
(a) CONTROL: player saw NO victory screen through t1131 -> consistent with
>1/2 on DAT_482fb (max 23/50=46%); cheapest closer is the score screen's
own percent (law percent=TRUNC(100*DAT_482fb/50)).
(b) ORFA: never accepted because att[Orfa->Chamachies] peaked 485, never
crossing their ACCEPT_ALLIANCE=570; player PROPOSE moves only the
player-side cell (600). docs/re/diplomacy.md §12.
(c) COMBAT OQ-010 CORRECTED: t85b's "zero AI-ship events" was a
free-record (65535) filter artifact; presence-law census banks 9
owner->free deletions, 4 of them Minion ships (slots 0/5/8/12 — the
Minions fielded exactly 4 ships in 1100 turns, all died in-war; matches
"only one ship, it didn't shoot back"). scripts/r1_t85c_focus.py.
(d) NIMBULOIDS: NOT in the campaign window — every trusted row n=4
[Chamachies,Orfa,Ungooma,Minions], ship owners ever {0,1,2,3}; the
repulsion cannot be their SA_IndustryBoost (or Frutmaka's, also absent).
Only Ungooma holds a lane effect (SA_BumpShipsInLanes); reversal census
is proportional-to-movement (cannot isolate firing race by kinematics).
OPEN USER CHECK (10 s): read the race NAMES off the in-game diplomacy
screen — if it shows "Nimbuloids" where memory decodes "Ungooma", the
+0x1c0 name-byte decode is wrong, not the player.
NEXT: war on the real 5th power is NOT possible in this campaign (n=4);
combat-law closure needs either in-battle frame recording or the static
application-code site (Ghidra, no capture). Gate GATE_EXIT=0, audit
AUDIT_RC=0, open {003,005,010,016,019,020,021,023}.
T85c-followup (player answers): race-name check RESOLVED — decode says
Ungooma, screen says Ungooma; "Nimbuloids" was a player typo. Name-byte
law validated; repulsion attribution (Ungooma SA_BumpShipsInLanes) stands
unopposed. Score-screen closer DEAD — no score screen exists in the SP UI
(disproducer is debug-pool/gated, score.md S7). OQ-021 closer is now
passive: keep playing; when a turn-boundary DAT_482fb sample reaches 25+
(26 systems_any currently, but boundary sample 23; the current held-turn
autosave reads DAT_482fb=0 — turn-boundary reads only), watch whether the
0x2c01d end-ctrl arm fires. Combat (OQ-010) needs in-battle recording or
the static app-code site; Nimbuloid war is impossible (campaign is n=4).
