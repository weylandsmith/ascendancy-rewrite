# t195 WIP — OQ-026 visibility layer in the rewrite + pin

Assigned: docs/STATE.md NEXT ACTION t195. Closure bar (strict-close): rewrite
SURFACE (filter + share-equivalent reveal + ability effects) implemented with
citations S23 L6/L7/L9, pinned by TEST(campaign_visibility_law_oq026_t195),
full suite + gate green; then abilities.md SA_KnowHomeWorlds / SA_KnowStarLanes
leave FILED NO-OP.

## Trigger triage (session start)
live-timeline.jsonl size 5,721,578,066 / mtime 2026-10-29 13:22:12.100000000
— EXACTLY the t194 re-frozen baseline. NO new sitting; r1_t85g_sitting.py not
run (nothing to adjudicate). Dirty tree at session start: `M
scripts/loop_one_task.sh` reported by the harness prompt, but `git diff`/
`git status --porcelain` both EMPTY and HEAD is t199 (loop-harness fix already
committed 2d3f4a9) — the snapshot was stale, nothing to adopt.

## Cited law inventory (all from docs/re/ships.md S23)
L5 (t191): lane rec+0x20 = per-empire visibility bitmask, bit e = 1<<e.
L6 (t192): FUN_00046354 mutual lane-vision share, __regparm3 (EAX=diplo row
  base 0x12e16+0x1ee*idx, EDX=other row idx, EBX=mode). state
  byte[row1+0x1c0+p2]==3 (ALLIANCE) -> RNG modulus 6 else 3; N=rand%(3|6)+1
  grants per call. DH=1<<row1 own idx, DL=1<<empire p2 idx.
  EBX!=0 receive-only: rec+0x20&DL && !(rec+0x20&DH) && EBX<N -> OR DH
  (party-1 receives a lane party-2 sees).
  EBX==0 bidirectional: mirrored -> OR DL (party-2 receives).
  OR-only, per-call counters, sticky (no lane-pool-scoped clear).
  Callers: 0x45778 EBX=0 bidirectional INSIDE the alliance-formation block
  (same chain writes row+0x1c0 and the +10/+5 attitude bumps);
  0x55f6e EBX=-1 receive-only in the per-race event loop (party-1 = current
  player row [0x7458e]).
  STAR TWIN FUN_00046524: star table 0x13bc5 stride 0x60, count u16 0x16145,
  mask pair +0x16/+0x17, modulus 4 if state==3 else 2.
  New-game witness: race r's lane list == EXACTLY {mask==1<<r} (100/100).
L7 (t193): mid-game the mask IS multi-bit ({1,3,6,7,11,15} of 1160 recs);
  value 6 = AI-only lanes exist; per-empire fog 9/8/25/32 of 58; masks
  md5-static inside a window with no alliance transition.
L9 (t194): CONSUMER = cosmos list builder FUN_00028fc0 — lane i admitted IFF
  rec+0x20 & DAT_00089324 != 0, else NO ENTRY (never drawn by painter
  FUN_000284bc, never clickable). Viewer mask setter FUN_00021a84(idx):
  mask = (idx==0xff ? 0xff : 1<<(idx&0x1f)), also writes X_CUR; one reader
  (0x2914e). Stars are ALWAYS drawn/listed (builder kind-0 unconditional),
  but star-click FUN_00028e70 gates select on star+0x17 & viewer and
  lane-follow on star+0x16 & viewer => invisible star = unselectable.
  LIVE: mid-game saves mask==0x01, 49/58 lanes admitted, 9 withheld.

## Design decisions (rewrite-side)
D1 Storage mirrors the original fields, not a new concept:
   laneMask_  per galaxy lane index   (rec+0x20 analog)
   starLaneMask_/starSelMask_ per star (star +0x16 lane-follow / +0x17 select
   analogs; the original has TWO bytes and the click handler consumes them
   separately, so two vectors — one would silently merge two measured
   distinct masks, cf. L7 where +0x16 and +0x16 census differ).
D2 Viewer concept = the t194 setter law verbatim:
   viewerMask(viewer) = (viewer==0xff ? 0xff : 1<<(viewer&0x1f)).
   255 = spectator/reveal-everything viewer (0x21a94 DL=0xff branch).
D3 Initial reveal at construction = own lanes + own stars. Justification:
   t192 new-game witness "race r sees EXACTLY {mask==1<<r}" + t193 re-read
   "the per-race list is the race's OWN claimed lanes". Rewrite analog of
   claimed lane = lane incident to a star the empire owns at scenario init.
   [documented default for the INIT PATH — the vendor site that writes the
   initial 1<<r bits is not among the cited writers; L6's pool-create zeroes
   +0x20 and the four FUN_00022ce4 callers all read as setup paths.]
D4 Share law = rewrite of FUN_00046354 shape: grantLanes(a,b,birectional,
   allied) with N = rng%((allied?6:3))+1 lanes per direction, eligibility
   "seer sees it && receiver doesn't", OR-only. Lane iteration order = pool
   (index) order [documented default; the original iterates word[0x177d3]
   lanes at 0x16147+0x27*i = index order — so this is the cited order].
   The grant CAP counter reading (EBX<N counts grants) [inferred from the
   loop; flagged]. Star twin: modulus 4|2 per L6.
D5 Fire sites wired in the rewrite:
   (a) alliance formation -> BIDIRECTIONAL share (cited 0x45778).
   (b) first contact player<->AI -> RECEIVE-ONLY share player<-AI (cited
       shape 0x55f6e per-race event loop; the rewrite has no per-race event
       loop, so the trigger = first turn a colony star of the player is
       lane-adjacent to a colony star of that AI [documented default site]).
   (c) NO AI-AI share path: the rewrite's dip model has no AI-vs-AI
       relationships (abilities.md/turnloop.md documented), so the t193
       AI-only mask-6 witness class has NO rewrite producer. Banked as an
       honest residue of this row, not faked.
D6 Abilities (leaving FILED NO-OP):
   SA_KnowStarLanes (passive, L2295 "see all star lanes"): OR the owner's
     viewer bit into EVERY lane mask at construction. Sticky = consistent
     with the no-clear law.
   SA_KnowHomeWorlds (passive, L1783 "see all alien home stars"): OR the
     owner's bit into both star masks of every OTHER empire's home star.
   [documented model: help.txt effect text is the law; the vendor's internal
   consumer of these two ability flags is not mapped — the rewrite applies
   the effect through the same mask layer the UI filter reads, which is the
   only surface t194 proved exists.]
D7 NO gameplay change: expansion/combat never consult visibility (no cited
   law that fog gates the AI's moves). The layer is a UI/interaction surface
   exactly as L9 measures it, plus the pinned reveal laws. Consumers added:
   laneVisibleTo/starSelectableBy/starLaneFollowable public predicates +
   visibleLaneCountFor(viewer) for the score/UI-style count.

## Implementation outcomes (t195, post-green)
R1 Landed: campaign.h decls + campaign.cpp (ctor seed block after
   pickHomeStars; visNext/contactSeen/seedVisibility/shareLaneVision/
   shareStarVision/filter predicates after pickHomeStars(); visibilityPhase
   before diplomacyPhase; ProposeAlliance branch calls BIDIR share;
   advance() runs visibilityPhase between expansionPhase and diplomacyPhase).
   Pin TEST(campaign_visibility_law_oq026_t195) in tests/test_campaign.cpp.
   111 tests, 0 failed; ability_probe 3m updated 4->2 no-ops; species.cpp
   kNotes rows 3/15 rewritten; abilities.md rows WIRED; ships.md S23 L10.
R2 FIXTURE CORRECTION (self-caught, first test run): home seeding is ONE
   star per empire (pickHomeStars) — the first fixture wrongly assumed
   P owns s0+s1; init law is then EXACTLY {lane0} for P, {lane3} for A on
   the 5-star chain, unowned s1/s2 fogged for both (t193 census supports:
   value-0 lanes exist new-game {0:940}/1160).
R3 SPECTATOR AND-BEHAVIOR pinned (new measured-shape consequence): viewer
   0xff does NOT reveal mask-0 lanes (0 & 0xff == 0 at 0x2914e, no bypass
   branch); consistent with t193 mid-game zero-mask absence (a live
   spectator saw all 58 because mid-game EVERY lane had >=1 bit).
R4 abilities[] constructor vector belongs to owners i+1 (the AI); PLAYER
   species route = cfg.playerSpecies. Pin covers BOTH routes for both
   abilities.
R5 Alliance fixture: race00 dip + proposeAlliance=100 override (start
   attitude 340 > 100 strict) -> chooser fires ProposeAlliance turn 1;
   BIDIR share verified both directions + star twin (P selects AI home,
   A selects player home).
R6 Ledger: row CLOSED (its own bar met), audit default --expect drops
   OQ-026 (t189b precedent), STATE index closed list gains the t195 entry,
   open list loses it. Gate + ledger_audit + ledger_index_check green.
