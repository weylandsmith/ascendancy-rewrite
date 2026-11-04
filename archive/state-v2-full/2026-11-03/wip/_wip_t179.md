# t179 WIP — consolidated stock-AI dossier

Goal: answer the deferred player question "does the AI defend systems and
choose offensive thrusts, or is it haphazard?" from t90..t105 decodes, with
a verdict section + rewrite gap map. Target file docs/re/ai-dossier.md.

## Evidence inventory (verified locations this session)
- aicode.md §1 master turn FUN_00024f24 phase order; §2 per-race chain
  FUN_0003e6e0 / decision block FUN_0003ea54 (dip -> build -> expansion ->
  maintenance 0x43b50 -> fleet orders).
- aicode.md §2b ship list sorts DESCENDING design power ([[a]+0x52] - [[b]+0x52],
  comparator 0x40eb4) — strongest ships first.
- aicode.md §2f + §2f-supplement (t94/t107): order kind byte +0x58 values
  {0..5}; stores imm 0 @0x24a00, 1 @0x3fb3e, 2 @0x3ca60, 3 @0x39859/0x49cd6,
  4 @0x2202f/0x22127/0x49db9, 5 @0x22243/0x2228f; travel issuer 0x220a8 +
  consumer 0x21f58 (kind5 -> kind4 on arrival); retreat-downgrade 0x220f2
  (un-targetable -> kind4 at owning star); decider 0x40178 (kind in {1,2,5}
  early-return = orders are STICKY).
- aicode.md §2f CONGREGATION LAW: race with research target + empty ship ->
  nearest friendly ship via path-cost table 0x45beb, +0x5d:=1/+0x5e:=pick.
- aicode.md §3b/§3c/§3d research picker = FUN_00040018 (same slot as
  expansion target DAT_00076492); tiers sentinel(45%, flag 0x0f all shipped
  AI) / first-preferred {1,47} / uniform; t93 landed in rewrite.
- aicode.md §6 (t99/t100/t101/t102/t103/t105): 0x43b50 = special-ability
  cadence engine, 16 case bodies, cad table 0x6780 (zero stores), event 24 =
  UI signal only, SA effects synchronous.
- income-law.md §9 (0x3f130 build selector): need-class FUN_0003fec4, 65/35
  roll, threat byte planet+0x59 gates item 18/19 shields w/ period
  200/225/300/400 by threat class @0x45beb; over-cap emergency demolish,
  min-REQUIRES demolish, 70-cost abort law.
- combat.md S2g firing order 0x4a55c/0x4a5c1 (every cat-0 weapon, stored
  order; stance setter +0x67/+0x68); 0x4b8e4 same-system gate +0x58==4 &&
  +0x59 equal; deterministic damage (measured negative on hit roll);
  0x43a4c diplomacy-on-attack (attitude -= 10*(word[0x13bc4]+1), doubled if
  state==3, attacked bitmap +0x48304).
- combat.md S2i callers-of-0x49f28 census (OPEN-QUESTIONS t88a ~L115-125):
  exactly TWO mode-1 commit callers (0x25560/0x25570, inside player-command-
  exec 0x2547c); EVERY AI-attack path is a mode-0 dry run.
- diplomacy.md §8 DIPVALUES map, §10-§12 relation-state ladder + playcap
  transitions; ai-data.md §2 21-race parameter table (data-driven personality).

## Pending verifications before verdict
V1: AI target-selection sites — does any attack-issuing path pick a target by
    military value (vs random)? Probe callers/inside 0x41260 attack module
    region + 0x3ca60 + 0x4105c.
V2: scope-of-search statement for "no system-level threat plan": enumerate
    what WAS searched (writer censuses, decision-block call graph) so the
    negative is bounded, not universal.
V3: rewrite gap map line numbers (campaign.cpp phases read this session:
    buildPhase :726, researchPhase :885, expansionPhase :948, driveHopsFor
    :1020, diplomacyPhase :1046, abilityPhase :1077, attackScore :1249,
    defenseScore :1282, shieldChargesFor :1295, combatPhase :1325).

## FINAL (session complete)
Dossier shipped at docs/re/ai-dossier.md (9 sections incl. PLAIN). P1/P2/P3
probes all banked into it (§5 P1/P2, §6 P3, §3a threat law). P2 census numbers
reproduced inline (hermes_tools terminal, method = r1_t90_callgraph.py rel32
scan over [0x14bb0,0x82bb0)). V2 done as dossier §7 scope-of-search paragraph.
V3 = gap map table dossier §8. OQ-016 row annotated (no closure). STATE.md
rewritten: NEXT=t180 with ordering rationale. Gate/audit run per finish seq.
