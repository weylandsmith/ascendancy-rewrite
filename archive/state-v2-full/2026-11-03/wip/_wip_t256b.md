# t256b WIP — AI GAP ROW 12 DISPOSITION (relation-STATE ladder, inter-race)

Assigned verbatim from STATE.md t256 queue (row order: 11 landed t256, 12 now,
16 next, t257 last). No steering note prepended; no BLOCKED.md ruling applies.

## S0. Task shape as I read it (before probing)
Gap map row 12 (docs/re/ai-dossier.md:324): attitude word + relation-STATE
ladder 0..3 + proposal emitter + attacked-bitmap — PARTIAL.
Already shrunk: attacked-bitmap consumer law (t206, display-only, diplomacy.md
§18); two-party chooser threshold-exact (decideDipAction, §7/§8); state-enum
SEMANTICS closed t189b/OQ-023 (1=PEACE, 2=WAR, 3=ALLIANCE, cited by OBSERVED
transitions, diplomacy.md §13 + §16).
Remaining substance: the rewrite carries ONE attitude scalar (AI->player), so
AI-vs-AI relations have NO state at all. Two admissible outcomes:
  (A) MEASUREMENT closes the ladder -> wire the minimal N x N state model.
  (B) honest negative + BANK the disposition (accept the two-party projection
      permanently, with a written rationale and a corrected row-12 label).
Strict-close: nothing here can close an OQ row on a default.

## S1. Measurement plan (the ring/banks, NOT a new capture)
Instrument already exists: scripts/r1_playcap_watch.py relation() reads the
FULL matrix per slot — states[i][j] at 0x12e16+0x1ee*i+0x1c0+j, atts[i][j] at
+0x1b2+2j, per-race DIPVALUES th[i], third-party matrix at 0x12fd6 — and every
timeline row carries it under key "relation". So the AI-AI question is a
STREAM query, not a memory hunt:
  1. Stream work/r1/playcap/live-timeline.jsonl via r1_stream (NEVER
     json.loads the whole file — OOM law), per-session trust (t255 law).
  2. For every ordered pair (i,j), i!=j, both non-player rows AND all pairs,
     census state values seen + every transition with turn/wall.
  3. Cross-check the static banks: bank-t251-live1255 (4-race mid-game, t1255)
     and bank-t1254 — full matrix decoded per slot via r1_sav_scan base vote.
  4. Key question for the disposition: do AI-vs-AI cells ever leave 1 in a
     campaign where the player is not a party? §11 says the 0->1 contact fires
     for AI pairs but NEVER advanced to 2 without a player declaration — that
     is n=1 campaign evidence from the user sitting; the self-play ring is an
     INDEPENDENT campaign lineage.
## S2. Findings (MEASURED — full detail banked to diplomacy.md §20)
Tool: scripts/r256b_relmatrix.py (keeper). 65,751 unique relation rows /
24 sessions (mtime-gap >600 s split) / per-session stale-echo watermark.
1. State census off-diagonal: {0:118268, 1:539740, 2:90992, 3:136}; 52
   transitions total (many are cross-session re-load echoes).
2. PLAYER-PARTY pairs ever {0,1,2} + {0,1,3} (§16 alliance). AI-AI pairs ever
   {0,1} ONLY — all six directed cells, every session entry, every row.
3. All 34 zero-transitions are 0->1 RECIPROCAL contact with att:=issuer
   START_ATTITUDE (Orfa 420->obs 423 within the +3/turn drift; Chamachies 320
   exact; Minions 340; Ungooma 410) — matches §13.4b bl=0 seeding writer.
4. Post-contact AI-AI bands 256..470 (348,936 obs) vs issuer thresholds
   DW {200,210,290} / AA {570,600,600} (static min==max in RAM): ZERO below
   DW, ZERO above AA. Ladder real in state space, DORMANT in every captured
   lineage. 2nd independent lineage corroborating §11.
5. Rewrite facts verified in code: dipState_ is per-AI (AI->PLAYER) —
   campaign.h:615; war_[][] full matrix exists (freeForAll seed 245, setWar
   symmetric 1899); combat t204 charge fires only a==kPlayer (1998);
   contacted_ only kPlayer row (1545-47). So the missing substance is exactly
   AI-AI attitude CELLS, and the measurement shows they never crossed a rung.

## S3. Disposition (BANKED, decision not default)
Keep the two-party projection PERMANENTLY. Wiring guessed AI-AI attitude
dynamics would add behaviour no captured lineage ever witnessed; the firing
LAW is already cited statically (§13 + third-party rungs) for any future
OQ-019-boundary build. Row-12 label rewritten in ai-dossier.md; rationale in
diplomacy.md §20 (a)-(d). NO rewrite code change, NO OQ row closed
(strict-close honored — "dormant in captured lineages" closes nothing).

## S4. Harness pitfalls banked (in r256b_relmatrix.py comments too)
- relation object sits at line offset ~28800 (after 28 KB ship_raw) —
  head[:600]/tail[-260] slices MISS it; probe '"states": [[' from 600.
- nested values indented ('"n": 4,\n') -> int(slice.strip()).
- "n" precedes "states" in the object -> derive n=len(states) from the slice.

