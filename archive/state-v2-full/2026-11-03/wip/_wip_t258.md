# _wip_t258 — OQ-021 END-TURN-RECOMPUTE DISCRIMINATOR (working log)

Task (STATE.md NEXT ACTION, verbatim intent): stream the full corpus ONCE with
per-session trust (t255 law), compute a candidate feature vector per row
(score_stars=V, turn, systems_any/full, planets_mine, owner-0 alive ship count,
total alive ship count, per-ship order-kind multiset from ship_raw), diff the
vector across the 39 V-change boundaries and against V-stable boundaries as
control. STRICT BAR: explains ALL changes AND zero non-changes, all sessions,
load-turn V==0 excluded from the fit but consistent with the first post-load
value. Pass -> upgrade rewrite victory check (campaign.cpp:738) + pin + CLOSE
OQ-021. Fail -> bank the candidicide table + record the capture-ask, row open.

Inputs already banked (no new capture run in this iteration):
- corpus work/r1/playcap/live-timeline.jsonl (7.42 GB, 303,487 lines at start)
- score.md S2 (display law: percent = TRUNC(100*V/T), T = total stars =
  (int16)(DAT_00016143>>16)), S10 (t255 behavioural law: V moves only at turn
  boundaries; V not save-persisted; lineage-dependent; t1254 read V=14 in one
  lineage and V=23 in another at the same systems_any=36)
- order-kind field law: ship record +0x58 order kind (bytes rebuilt from the
  verbatim 177-u16 window; r256c_shipstate.py decode() is the reference impl)

## S1. Format probe (scripts/r258_probe.py, work/r1/t258_probe.out)

MEASURED over the corpus as of this iteration: 303,625 lines / 7,428,797,748 B,
line len 280..32,129 (avg 24,467). `"score_stars"` sits in the FIRST 100 BYTES
of EVERY line (bucket 0: 303625/303625) — so a 200-byte head slice is SAFE for
V, turn, T, selector_byte; `systems_any/systems_full/planets_mine/wall/
file_mtime_ns` are at line END (tail 260 B), per the t255 pitfall note. V==0
rows = 42,971 raw (also offset-bucket 0). ZERO rows with V>=25 anywhere in the
corpus (re-confirms the t255 "no V>=25 row, Control boundary unobserved" leg at
the new corpus size) and max turn seen 1335 (live :9 still parked at t1255).

## S2. Pass 1 of r258_vdisc.py — TWO INSTRUMENT BUGS FOUND AND FIXED (honest)

Pass 1 (work/r1/t258_vdisc.out) reported trusted_V_rows=53,345, v0_rows=9,997,
dedup=237,290, stale=3,437, sessions=25 — but two defects invalidated its
boundary math, caught by reading the boundary dump itself:

  BUG A (tuple-index): `prev` is (sessions, fn, mt, turn, vec, wall) and the
  boundary code read prev[2] as the turn. prev[2] is the mtime. Consequence:
  `prev[2] == turn` was never true, so ALL 38 V-change pairs landed in `vchg`
  and `midturn` was 0 — i.e. pass 1's "MID-TURN=0 corroborates t255" was NOT a
  valid measurement. It ALSO inflated the control population: `elif prev[2] !=
  turn` was always true, so stable_turnb=53,284 counted every V-stable PAIR
  (mid-turn resamples included) instead of V-stable TURN boundaries. Fixed by
  unpacking `p_ses, p_fn, p_mt, p_turn, pvec, p_wall = prev`.
  NOTE the 39-vs-38 discrepancy vs t255: t255 counted 39 turn-boundary changes
  on a 65,380-row corpus; pass 1's 38 is the count of ALL V-change pairs under a
  broken predicate, so it is not a counter-claim. Pass 2 re-measures.

  BUG B (JSON slice): ship_raw_fast() sliced line[i:j] with j = index of the
  closing brace, dropping it -> json.loads always failed -> ship_raw=None on
  every row, so all 12 order-kind features and the three alive counts were
  constant 0/None (the candidicide table's 0/0 rows are an artifact, not a
  measurement). Fixed to line[i:j+1]. Verified against r256c_shipstate.py's
  reference get_obj() on a live row before adopting.

## S4. Passes 2/3 — BUGS C+D: the ship-feature zero was ALWAYS an extractor
artifact; instrument hygiene law banked

Pass 2 (work/r1/t258_vdisc2.out, after bug A+B) STILL showed all 12 order-kind
features and the alive counts at 0/None. Pass 3 crashed early (missing
`defaultdict` import — fixed). Root cause, PROVEN by direct probe rather than
theory (the t258 instrument-hygiene lesson):

  BUG C (offset): KEY '"ship_raw": {' is 13 chars, code advanced 13 — that part
  was actually fine; my first "fix" note was wrong and re-verifying corrected it.
  BUG D (THE REAL ONE): the fast slice starts AFTER the opening brace and ends
  AT the closing one, so the segment is `"0": [60, ...], ... }` — json.loads
  fails "Extra data: line 1 column 4 (char 3)" (it parses the key `"0"` then
  hits the colon). The except-swallow returned None on EVERY row.
  META-BUG E: the 40/40 "agreement with the r256c reference get_obj" that I
  recorded as verification in S2 was VACUOUS on those rows — get_obj ALSO
  returned None there (its depth-walk starts at the same '{' but it re-searches
  from the key; on the sampled rows both were None, and None==None scored as
  agreement). LAW BANKED: a verifier agreement is worth nothing unless the
  verified value is non-degenerate — assert the value TYPE/CONTENT ("got a dict
  with >=1 int-list slot"), never just fast==reference.

  Fix: `json.loads("{" + line[i:j+1])`. VALIDATED the honest way before the
  final pass: on 200 tail-corpus in-game rows the extractor returned non-empty
  dicts 200/200, and a t1255-class vector is sane: alive_total=35
  (player 22 / AI 13), player kinds {3:10, 4:3, 5:9}, AI kinds {1:5, 4:4, 5:4}
  — exactly the r256c kind-set law {1..5}, kind0 zero, AI kind2 zero.

## S5. Measurements from pass 3 that stand regardless of the ship bug

  * MID-TURN V changes = 0 with the FIXED boundary predicate (pass 1's 0 was
    an artifact; pass 3/4's 0 is a real measurement over 53,412 trusted V-rows,
    25 sessions) — t255's "V moves only at turn boundaries" re-corroborated.
  * Control population with the fixed predicate: 795 V-stable TURN-boundary
    pairs (pass 1's 53,284 was inflated by counting mid-turn resamples).
    same-file pairs = 0 among them — every trusted turn-advance pair crosses a
    save-file name (the ring rotates 41..60.sav), an expected structural fact.
  * none_census over trusted V rows = {} after the fix (before the fix, the
    ship_raw(missing) bucket would have lit up ~53k times — the census added
    precisely to make the table's zeros non-degenerate, closing META-BUG E).
  * PER-SESSION V TRAJECTORIES (the shape clue, full text in
    work/r1/t258_vdisc4.out): S02 1,2,3,5,6,7,9,11 (early growth, +1/+2 steps);
    S07 11->13->12->13->11->22->23 (t911->t912 DOUBLING); S13 22->11 (t1141
    HALVING), 10->8->14; S14/S15 the SAME turn pair t1169->1170->1171 replayed
    in two sessions reproduces 14->12->14 EXACTLY (deterministic recompute,
    2nd lineage after t255's V=23@t1087 pair); S17 14->12->14, 15->13->15->14;
    S19 14,15,12,15,16,21,19,22,21 up to t1335; S25 23@t1096 -> 14@t1255 (the
    unobserved self-play sprint). The replayed 14->12->14 across S14/S15 is a
    THIRD independent determinism witness and a NEW one (t255 had only t1087).
  * rank=65535 and selector_byte=0 on every sampled trusted row; zero V>=25
    rows in the whole 303k-line corpus — the Control-victory boundary remains
    UNOBSERVED (the row's closure bar cannot be met by this corpus alone).

## S3. Pass-1 byproducts that ARE valid (independent of the extractor bugs)

  * The FIRST-post-load V table (bug B only zeroes the ship features, not V/T/
    systems_*): every session's first non-zero-V row after a V==0 stretch, with
    its world. It shows V is NOT a function of the loaded snapshot: t693 reads
    V=11 with systems_any=9/systems_full=7 (S03,S04) and V=11 with full=6 (S05);
    t1087 reads V=23 with full=25 (S22,S23) and V=23 with full=24 (S25);
    t1167 reads V=14 with full=27 (S14) and V=14 with full=29 (S15); t1254 V=14
    full=32, t1255 V=14 full=34. So V co-varies weakly with systems_full but is
    neither equal to it nor determined by it — the t255 lineage-dependence leg
    re-corroborates at 22 load points.
  * V==0 rows are NOT all turn==0: 33 distinct (session, turn) pairs carry V==0
    at turns 692..1254 (e.g. S19 t1254, S22/23/25 t1086). That is the LOAD-TURN
    class (you load INTO turn 1086 and the save restores no V), consistent with
    t255 §2 — and it means the fit must exclude these rows by CLASS, not by
    turn==0.
  * Multi-step and non-monotone V moves are real in the boundary dump: S02
    3->5, 7->9, 9->11; S07 13->12, 13->11, 11->22; S13 22->11 (halving), 8->14;
    S19 16->21, 19->22. A 22->11 halving and an 11->22 doubling in the same
    variable on adjacent turns is hard to reconcile with a monotone territory
    count and is the strongest single clue for the shape of the recompute.


## S6. Pass 4 (FINAL, work/r1/t258_vdisc4.out) — candidicide with LIVE ship features

Same populations (38 change / 795 stable), extractor fixed and validated
non-degenerate (200/200 tail rows decode to dicts; t1255-class vector sane vs
the r256c kind-set law). CANDIDICIDE TABLE (changes at N/38 boundaries | N/795
stable | verdict): turn 38|795|no (tautology); T, rank, sel 0|0|no (constants);
systems_any 1|1|no; systems_full 1|2|no; planets_mine 1|1|no; alive_total
5|24|no; alive_player 2|3|no; alive_ai 5|23|no; P_k0 0|0; P_k1 3|28; P_k2 1|6;
P_k3 6|46; P_k4 22|289; P_k5 24|283; A_k0 0|0; A_k1 7|30; A_k2 0|0; A_k3 0|4;
A_k4 33|278; A_k5 33|277. SURVIVORS: NONE.

Supplementary aggregate-fit probe (separate stream pass, all 53,412 rows with
ship_raw, candidate closed forms vs observed V): Pk4+Pk5+Ak4+Ak5 5,688/53,412
(10.6%); alive_player 4,013; Pk3+Pk4+Pk5+Ak1 3,996; sum_Pk3_5 985;
2*(Pk4+Pk5) 154; alive_ai 3; sum_Ak4_5 2; sum_all_k 1. Every first-miss at t37
(V=1, zero ships — the fleet had not launched; the queue's load-turn rule
handled by excluding V==0 rows only, t37 stays in and kills the fleet formulas).
Conclusion: the banked world-feature space is MEASURED-CLOSED as an
explanation of V. OQ-021 kept open; USER ASK (A) passive drive past V>=25,
(B) watchpoint build approval — in docs/BLOCKED.md. Per the queue's own
honest-expectation note, the lineage-dependence leg predicted exactly this:
the deliverable is the candidicide table + the ask, not a forced close.
