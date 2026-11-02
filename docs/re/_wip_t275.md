# _wip_t275 — REWRITE COMBAT INTEGRATION (queue row 14)

## S0 — pre-flight (measured this session)
- r1_game_health.py: HEALTHY, game pid 576895, TL expiry 2026-11-04 10:07:01
  (155146 s left), watcher 576910, ring 44.sav age 1s. RC=0.
- New-sitting check (400 KB tail-scan of live-timeline.jsonl per OOM law):
  122 rows, turn first/last/min/max ALL 645, zero turn resets, wall
  14:41:26..15:01:25 — the production :9 tutorial session is still idling at
  t645; NO new sitting. Assignment t275 stands.

## S1 — task triage against the record (BEFORE any code)
The queue row names four sub-laws + a citation set. Status of each against
the tree (ai-dossier gap table row 14, combat.md S2i/S2j, code read):

1. deterministic damage — LANDED t89: combatPhase draws nothing from rng_
   (campaign.cpp:1956..1966 comment; uniform(0,10) draws removed), pin
   campaign_combat_law_oq010 leg (4) seed-determinism 40 turns.
2. ordered cat-0 volley — LANDED t89 at AGGREGATE level: attackScore =
   SUM of researched cat-0 Levels (campaign.cpp:1842..1853), pin leg (1)
   delta == 49 == file sum. The ORDER itself (0x4a5c1 stored slot order) is
   invisible without per-ship slots (row 16 boundary, S11 accepted
   permanently t256c) — ORDER is not queueable short of an OQ-019 build.
3. shield-then-hull two-layer absorb — LANDED t89: absorbSplit mirrors
   0x4b7c4..0x4b8a6 (campaign.h:383), pin leg (3) edge classes.
4. death at <1 — LANDED t89 as the capture/Extinct verdict mapping (S2i(c)
   "cite the mapping, do not invent a hull pool").

=> the three aggregate sub-laws are NOT re-implementable; re-doing them
would churn, not advance. THE REAL DELTA in the row's citation set is the
engagement-resolution region 0x42c60..0x42e6e (t179 P3, ai-dossier §6):
  Leg A (invasion): first-eligible ship, kind==4 + gizmo slot == 0x49.
  Leg B (firepower): first-eligible ship, kind==4 && 0x4a604 != 0 &&
    0x4a55c(ship,1,target) != 0; first match wins; NO strength comparison.
That region has NEVER been read verbatim in this repo (t179 banked a summary;
no objdump listing banked; _wip_t179.md doesn't mention 0x42c60). The row's
"pins from the t85b 244-turn battle law set" is stale in detail: the 244-turn
war (OPEN-QUESTIONS OQ-010 row) is banked in combat.md §1 (t85g mid-turn
frames: integrity volley-steps, return fire REAL player 40>38>36>34, death
law +0x8c->0->owner-free) — pins must key on THAT, not on per-ship state the
aggregate model lacks.

## S2 — probe plan (bounded)
- objdump work/ascend_restored.bin region 0x42c60..0x42e6e verbatim; answer:
  (a) what is the ship array [esp+0x380] (count [esp+0x354]) — attacker-only
      or all ships in the engagement? (b) who calls the resolver; (c) is
      there a DEFENDER volley arm (return fire) inside the region?
- If (c) is YES: the rewrite's combatPhase currently applies NO defender
  fire — return fire (measured REAL, combat.md §1) is the honest missing
  body. Mapping candidate per cited law: return fire charges the attacker's
  POWER analogue fleetDamage_ (the channel SA_SapAlienPower already uses,
  campaign.cpp:1927 — NOT an invented pool).
- BLAST RADIUS before wiring: return fire flips capture outcomes -> all
  timelines move; closing measurement = seed re-verification (2024/42/13 +
  1/2) FINITE in the 1200 budget, like t89 did.

## S3 — OUTCOME (session close)
The S2 probe ran; every finding is banked in docs/re/combat.md S2k (the
authoritative version — this scratch file's S2 wiring sketch is SUPERSEDED:
the return-fire mapping was NOT taken, see S2k honest-negative (2)/(3); the
resolver never sees the defender, so "return fire charges fleetDamage_" had
no cited aggregate call site and would have re-trajectories every timeline
on uncited ground). Ledger: OQ-019 annotated STAYS OPEN; rewrite code
unchanged; gate green; committed as t275.
