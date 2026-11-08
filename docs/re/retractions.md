# retractions.md — dead readings index (built t343, 2026-11-08)

Purpose: 340+ iterations retracted some of their OWN earlier readings. A
newcomer must not pick up a dead reading as fact. One entry per retracted
claim: WHAT WAS SAID / WHO SAID IT / SUPERSEDED BY / CURRENT LAW. Every pair
was verified against the citing document this iteration (citations are
file:line as of t343; line numbers drift, section anchors do not).
Add an entry HERE the moment you retract something, citing both sides.

## Table/number laws
1. pop-cap "+2 residual" + skip-Colony-Base model preference.
   SAID: t31/t32 (recalc vs observed left a +2 residue; flags&4 rows skipped).
   BY: t33 — the harness read the slot array at the WRONG address; correct
   base is stored-ptr+0x88, and the residual + skip preference were harness
   artefacts (archive/state-v2-full/2026-11-03/OPEN-QUESTIONS.md ~L1106-1111
   "old t31 numbers RETRACTED"; docs/re/income-law.md "T33").
   CURRENT: +0x4a = clamp(0..100, +0x55 + MPOP sum over ALL active slots,
   Colony Base INCLUDED) — 72066/72066 holds (income-law.md T33).

2. ship design-record field labels "design-list pointer / fuel / propulsion".
   SAID: t47 §12/§13.
   BY: t101 — the labels were a +0x30 base-offset artefact; values were on
   the right bytes, semantics wrong; rows 10..15 are live-NAMED shields
   (docs/re/ships.md §12 "t101 CORRECTIONS + CLOSURE" ~L346;
   archive OPEN-QUESTIONS ~L1588 "t47's §12/§13 ... RETRACTED").
   CURRENT: row base sits 0x30 ABOVE raw design-record start; every [row+K]
   == raw design[+0x30+K] (ships.md t101 block).

3. "owner-1 speed 4.67/day = 14/3 = THREE movement sub-steps".
   SAID: t187 (open question form).
   BY: t265 flight-mining — same-turn consecutive-row x-deltas EXACTLY 0.0 in
   17,595 pairs; the reading "is DEAD" (docs/re/ships.md S24 ~L1280).
   CURRENT: ONE step per turn boundary; 4.6667 is a single step VALUE
   (x = k*step law, S21).

4. research stride-45 table.
   SAID: t105 draft (0x74782 in a stride-45 table).
   BY: t105 itself, verified leg 2+3 (docs/re/aicode.md "t105 CORRECTION"
   ~L975). CURRENT: index math is 75*t; 0x74782 is the row-0 runtime COST
   word of the restree table (stride 75, cost@+62 — the OQ-013 law). NO
   independent stride-45 table exists.

5. RNG range "0..99" for the barren-cell draw.
   SAID: pre-t29b draft of the world-gen law.
   BY: t29b (docs/re/income-law.md ~L668: "CORRECTED t29b: an earlier draft
   said 0..99"). CURRENT: rng 0x7824f returns 0..32767 (LCG, SHR 0x10; AND
   0x7FFF @0x78269).

6. item COST word at +2 (planitem record).
   SAID: t342 STATE assignment (cost word +2).
   BY: t342 landing — docs/STATE.md CORRECTION LANDED block: COST word is
   DS+0x73E40+8+0x28*idx (FLAGS +6, COST +8); t340's own income-law S8 text
   had it right all along.
   CURRENT: stride 0x28, COST u16@+8 (matches the OQ-014 record map).

## Field-attribution readings (one-sample traps)
7. word[star/planet rec +0x16] = "homeworld marker".
   SAID: t105 §3 ([inferred], one sample).
   BY: t281 census — UNIFORM over 0..10 among owned AND unowned (15 tens
   across 3 owners); REFUTED (docs/re/aicode.md ~L1054-1057).
   CURRENT: +0x16 = stored world-gen weight-row index (ctor rng%11
   @0x23a97/aa8); row 10 == zero-barren preset [0,33,34,33].

8. u16@0x131b4 = "the header planets counter".
   SAID: t246 (attribution also rode into commit 867d3e2's message).
   BY: t249 — reads 60 at t1092 AND t1254 while the header went 60->102;
   ZERO absolute references in code (docs/re/selfplay.md ~L95 "t246
   attribution WRONG, corrected here").
   CURRENT: race-block-relative field, not a counter; the real
   header-planets counter was found in the same t249 session.

9. star byte +0x5a = "colonised-planet count".
   SAID: t247 (lead).
   BY: t248 — sum(+0x5a) over all 50 stars == 145 == named record count;
   per-system len(planets)==+0x5a (docs/re/selfplay.md "t247's +0x5a LEAD
   REFUTED" ~L115/L149).
   CURRENT: +0x5a = TOTAL planet SLOTS in the system. (Note: a DIFFERENT
   +0x5a — the PLANET-record local-race byte — is live law from t341/t342;
   do not conflate record types.)

10. "occupied == populated" (Planets header).
    SAID: implied by t248's 60-vs-80 anomaly reading.
    BY: t249 live re-open — header counts 80/80 owner-flag planets, NO pop
    filter; the 60 was a stale snapshot (archive STATE ~L1749-1751).
    CURRENT: header "N Planets Occupied" == owner-flag count.

11. DAT_000482fb / DAT_00048300 alias + that block as score producer.
    SAID: t212-era aicode.md block (alias claimed, producer walk).
    BY: t212 CORRECTION itself (docs/re/aicode.md ~L60-66): the block writes
    ONLY word[0x48300], OUTSIDE the displayed dword [0x482fb..0x482fe]; it is
    a debug dump with a line counter; the displayed count's writer has ZERO
    statically-encodable forms image-wide.
    CURRENT: runtime-watchpoint class (t283 later WITNESSED the producer with
    a BPLM write-watchpoint, docs/re/dosbox-wp-t283.md).

## Witness / event claims
12. "the corpus holds none" (mid-campaign slot with V and +0x15 both
    non-degenerate).
    SAID: score.md S9-era text.
    BY: t251 CORRECTION (docs/re/score.md ~L289): scan roots missed
    work/r1/bank-*; bank-t1254 V=23 with NINE +0x15 rows, bank-t251-live1255
    V=14 with TEN. CURRENT: witness class OBSERVED; non-join holds (V !=
    ownP, != occ); row 2 +0x15==0x3 kills the single-owner-bit reading.

13. "production :9 SOFTLOCK at 21:38".
    SAID: t261-era ops reading.
    BY: t266 forensics — content-refuted as a production event: TWO-WRITER
    RING COLLISION; production dosbox.log has ZERO "Loading state from slot"
    (n=0 over 5.8M lines; the 3.89M "Extracting:" lines are SAVE-path churn —
    misreading them was a live trap) (archive STATE ~L1159, REFUTED-ROUTES
    t266 block).
    CURRENT: ring dirs can be written by a scratch session; attribute ring
    events by campaign-fingerprint + writer lineage, not mtime alone.

14. "kill ONLY pkill -x dosbox-x".
    SAID: pre-t267 advice.
    BY: RETRACTED in docs/BLOCKED.md ~L107 (the detector earned its keep on
    its author; see the t267 incident block in docs/re/selfplay.md).
    CURRENT: follow BLOCKED.md's kill SOP (structured, never pkill -f).

15. "ah>=4 hits the runtime-error trap" (combat command byte).
    SAID: t88a.
    BY: t210-era correction (archive STATE ~L2939: "'ah>=4' -> 'ah==1 or
    ah>=4'"). CURRENT LAW: ah==1 ALSO hits assert trap 0x2a438(0x8f5,0xd92).
    NOTE: live docs/re/combat.md mode==1 section (~L467) still prints the
    narrow form — read this entry alongside it.

16. "mouse k6/k7 not walkable" (shp).
    SAID: t196 S20.1 (canonical-slot dims only).
    BY: t328 MEASURED (docs/re/shp.md "MOUSE CORRECTION" ~L1177): with the
    u16 dims PAIR AT rec+0 (46x77) the S9 walk completes EXACT-H 77/77 for
    k5/k6/k7. CURRENT: real art bytes exist; the dispute is DIMS-SLOT-LOCATION
    (canonical A dims u32@+0x10 have a zero component) — OQ-005's live
    residue, do NOT re-claim "no art".

17. "zero-ladder slots are dims-zero".
    SAID: t328 task framing (S1 GROUP).
    BY: t328's own S-numbered correction (docs/re/shp.md ~L1159): u16@+0 reads
    139x139/199x199 — the structural fact is ZERO STREAM BYTES at the
    law-cited stream slot, not zero dims.
    CURRENT: 25 zero-stream ladder slots named; combat class =>
    UNREACHABLE-BY-CAPTURE (t323 amendment).

18. "mouse k7 span 2062 (GROUP E: 2062 each)".
    SAID: t328 S1.
    BY: t330 re-measure (docs/re/_wip_t330.md ~L18: k7 span MEASURED 189;
    "correction banked").
    CURRENT: k5/k6 span 2062, k7 span 189.

19. "the arming msgs 0x4d..0x51 are the launcher family" + consumer leg.
    SAID: t326b S8 (outcome-B index reading).
    BY: t331 (docs/re/ships.md S49 title ~L2298 "THE 'ARMING MSGS' WERE
    TABLE INDICES" + "ALIVE-IN-IMAGE (t326b consumer-leg REFUTED ...)"
    ~L2332).
    CURRENT: the real poster posts msg 81 elsewhere; window-identity law =
    class tables live at FILE 0x88xxx, installer imm is pool-relative
    (imm+0x82bb0=file).

20. "win+0xa1 is the STATE-line count / state-line consumer".
    SAID: t334 (S53 interim S12 reading, already retracted in _wip_t334 S13).
    BY: t335 (docs/re/ships.md "t334'S 'STATE-LINE CONSUMER' IS RETRACTED"
    ~L2566, decisive 22,398-window census).
    CURRENT: [win+0xa1] == count of TEXTITEM+SHAPEITEM lines in the window's
    file block (22398/22398 EXACT; vs STATE-line count it FAILS); the id-16
    assert paradox dissolves — the STATE array never touches this block.

## Coverage corrections (law held, corpus did not)
21. governor trigger values "33/34/35 NEVER occur (0/2810)".
    SAID: t45 closure text.
    BY: t342 full-corpus census (scripts/r342_queue_census.py exit 0):
    production t1086 holds 320 owner-0 values {34:180, 35:140} — the t45
    figure was corpus-limited to the Oct-5/6 early-turn captures
    (docs/re/income-law.md S14 correction block + S-T342).
    CURRENT: closure route unchanged (t45's law itself re-verified); the
    NEVER claim is retired.

22. "watchpoint route measured-dead on this box" (OQ-021/OQ-019 class).
    SAID: t272 (Debian +dfsg dosbox-x links the debugger out; route re-opens
    only with a debugger-enabled build).
    BY: the user supplied one — t283 witnessed the DAT_482fb producer live
    with BPLM (docs/re/dosbox-wp-t283.md), and t292 closed OQ-021 on the same
    instrument class.
    CURRENT: dead ONLY for the +dfsg build; debugger-build sessions are a
    live instrument class (scratch copy, own ring dir, campaign-resident
    before arming).

23. pointer-law "rv-B re-derivation" (2026-10-05j).
    SAID: a same-day re-derivation claiming the law was rv-B.
    BY: its own printed evidence — the statistic was mislabeled
    (matches-as-diffs); the verbatim-copy test mem[B+f]==payload[f] holds
    ~95% and misses are exactly the fixup sites
    (scripts/r1_restore_sites.py docstring ~L21-23).
    CURRENT: d = rv - P0, P0 = B - H, H = 0x88 member header — CLOSED, do not
    re-litigate (r1_pointer_law.py battery, gate 3q).

24. BASELINE manifest leg "verified" (pre-t162).
    SAID: gate 1 checked originals integrity.
    BY: t162 audit — the old leg enumerated manifest->disk only: an ADDED
    file produced zero signal and an ABSENT manifest silently REBUILT itself
    from whatever was on disk (bless-the-tamper hole)
    (scripts/gate.sh stage-1 comment, docs/re/stop-report.md §55).
    CURRENT: bidirectional check + never-regenerate rule.
