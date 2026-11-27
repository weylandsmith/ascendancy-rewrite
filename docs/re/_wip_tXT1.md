# tXT-1 WIP — player extinct-by-day-20 on dense games (D32)

## REPRO (headless, cheap path — no CONT cycle needed)
`./rewrite/build/ascendancy --data . --campaign 60 --stars 100 --seed 1`
EXITS t20: `[t20] owner 1 captured Phoebe` + `VICTORY: Extinct (end-xtnc.txt)`
(log /tmp/tXT1_headless_s1.log). Same exit the instrument caught in the
user's CONT run (ui.cpp:1625 advance-stop printed the identical event line,
then ui quit cause=victory:Extinct turn=20). Binary md5 74e2a42458b608eb4f6c18b36db9b17d.

Per-turn census (headless, player idle): player stars 1 t1..t19, 0 at t20.
AI stars `1 1 1 1 1 1` t1..t19 -> `2 1 1 1 1 1` t20. Player techs 0 all game.
- NOT (a) bookkeeping corruption: census drops 1->0 in lockstep with the
  event; the event names the player's own home star, owner 1 = real captor.
- NOT (c) fleetPending: headless player has no fleet; wait law irrelevant.
- (b) CONFIRMED as the proximate cause: owner 1 invades the player home at
  t20 and wins against a zero-navy idle player. The DEEP cause is why it is
  at war at all:

## ROOT CAUSE — freeForAll=true arcade default (campaign.h:144)
`war_[x][y]=1 ALL PAIRS at scenario init` (campaign.cpp:321-324) when
cfg_.freeForAll (default true; buildCampaign never sets it -> every --ui and
--campaign game starts EVERYONE at war, from turn 1, with no declare).
VENDOR LAW (cited, docs/re/diplomacy.md):
- §19: "measured: 200/200 fresh-campaign non-war pairs sit at
  START_ATTITUDE 600 > DECL 210" — fresh campaigns are NOT at war.
- §13.3 enum law: "scenario seeding never writes 0" and the AT-WAR writer
  is case bl=2 (0x455cb) — a dialogue action, not init.
- §11 live witness: player declaration 1->2 reciprocal; pre-war every pair
  sat at state 1 (PEACETIME).
So the vendor's early-game peace is exactly the ground truth the user
reported ("vendor dense games do NOT end by t20"), and our t20 exit is a
port artifact of the arcade default. Consequences of FFA in the port:
- combatPhase invasion gate (campaign.cpp:2155) passes for every border
  pair from t1 -> the player (idle, no navy) is capturable turn ~20 as
  soon as one AI's pop score beats home defense;
- guaranteeWarOnInvasion (the cited vendor channel that STARTS wars) can
  never fire under FFA (handler returns early when victimAtWar) — the port
  has the escalation law wired but a default that pre-empts it.

## FIX
freeForAll default -> false (campaign.h:144). Tests that want war set the
flag explicitly (grep: 8 test files set freeForAll=true by name, so they are
insulated; test_campaign.cpp:63 parameterised). Remeasure: dense+7 soak 60t
pin + PLAYTHROUGH seeds re-record.

## MEASURED MATRIX PRE-FIX (idle headless player, --campaign 60)
| seed | stars50 | stars75 | stars100 |
| 1 | no victory | no victory | EXTINCT t20 (captured Phoebe) |
| 2 | no victory | no victory (capt Tonsberg AI-AI) | no victory |
| 3 | no victory (capt Fomalhaut) | no victory | no victory |
Dense-specific + seed-dependent, matching the user's "very dense + seven
species -> exits t20" shape (headless default owners = 6 AI + player = 7).

## turnloop.md staleness
docs/re/turnloop.md §5 line ~114 said "campaign default freeForAll=true
starts everyone at war (arcade setting)" — updated with this landing.

## POST-FIX REMEASURE (binary md5 822b822cf2bf365bbebd490969611542)
- matrix 3x3 (--campaign 60, idle player): 9/9 "no victory after 60 turns";
  t60 census player stars 1 on every cell (logs /tmp/tXT1_fix_s*_st*.log).
- seed 2024 --campaign 1600: Extinct t1067 (long-game dynamics unchanged —
  D32's claim is about t20, not t1067); seed 23 Control t1582; seed 13
  Extinct t538 (was t536 pre-fix — dynamics verifiably DID change).
  Declares now fire mid-game via the chooser channel (seed 2024:
  FLUDENTRI t143, KAMBUCHA t185 — zero pre-war-turn captures).
- PLAYTHROUGH.md re-recorded from the post-fix binary; gate greps
  ('VICTORY Control' AND 'VICTORY Extinct') both satisfied.
- Begin-path WITNESS scripts/tXT1_dense7_witness.sh: density rung 2 (100
  stars) + species word 5->7 via the wheel, BEGIN, 60 NEXT TURN presses —
  "newgame live stars 100 owners 7 gov 1", SURVIVED 60, rc=0
  (/tmp/txt1_dense7/app.log). This is the user's exact repro shape.
- Pins test_peace_start_txt1 x3 (peace-init census 7x7, dense+7 60t soak
  x3 seeds, clamp-is-the-only-war-entry pure battery). MUTATION M1
  (default back to true) CAUGHT: peace_start_default FAILs 42x,
  dense_seven_survives FAILs (Extinct + starsOwned 0); suite restored
  md5-verified (c2b4b76a0f1b4835b6249f9996d077c5) and REBUILT before the
  witness (tXT trap: last-mutant binary persists).

## OPEN RESIDUES (bank, keep honest)
- AI-AI war: rewrite models NO AI-AI diplomacy (turnloop.md; campaign.cpp:
  2296-2300 comment). Post-fix, AI-AI pairs are permanently at peace — the
  vendor's inter-race ladder (DA_DeclareWarOnOtherRace rung 0x44ce0 needs
  self==2 AND third==1) is UNWIRED (documented scope, OQ-020 territory).
  Vendor dense games do expand/capture AI-AI eventually; our port won't.
  That is a pre-existing documented gap, NOT introduced by this fix.
- gate greps PLAYTHROUGH.md for 'VICTORY Control' AND 'VICTORY Extinct'
  (gate.sh:522-525). If peace-start dynamics change which seeds hit which
  victory inside 1600, re-record runs honestly; if NO seed yields Extinct,
  that is a finding to report, not a reason to keep the arcade default.
