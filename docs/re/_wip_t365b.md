# _wip_t365b — FAILURE DIAGNOSIS (measured run, 2026-11-10)

run_tests: 223 tests, 3 test-level FAILs (the "154 failed" headline counts
CHECK invocations, not tests — main.cpp:14-21 counts failures(), loop-
multiplied). Failing tests:

1. campaign_advance_after_victory_is_noop — seed 1 gets NO victory in 1200
   turns (pre-flip: Control t842). Trajectory change, root = 2/3 below.
2. campaign_fleet_oracle_equivalence_t365_p2 — out.shieldCharges==0,
   captured false, hullHit 0.
3. campaign_fleet_chase_targetpos_t365_p3 — targetPos/fireTarget/
   dispatcherGate unset on the sim's shooter record.

ROOT CAUSES (both code-verified, shipsim.cpp/shipsim.h cited):

A) DANGLING SHIP POINTER. shipsim.h:555 `std::vector<Ship> ships_`;
   addShip (shipsim.cpp:105) push_back → reallocation invalidates every
   Ship*. resolveEngagement takes `Ship* shooter` BEFORE
   `addShip(garrison)`; all later writes (power, targetPos, activeSlot)
   land in freed memory. Fix: re-lookup shooter after every addShip.
   Explains P3 (targetPos unset) and P2's ran=false (power stayed 0 →
   S3 suppression → no shots → no captures → no victory → test 1).

B) SLOT PAYLOAD DEFAULT. InvSlot::payload defaults to 0 (shipsim.h:98-103);
   the cited upkeep shield law skips any slot whose payload != 0xffffffff
   (shipsim.cpp:282, 0x4a6f9). Measured save-side: -1 sits on upkeep-gate
   rows (shipsim.h:100-102). syncRows never sets payload → upkeep burns
   nothing and materialises ZERO shield charges. Fix: syncRows sets
   payload := 0xffffffff on every synced slot (uniform; the only cited
   consumer is the upkeep -1 test, so non-gate rows are observably
   unaffected).

P5 "80 agreed" is NOT trustworthy evidence while A/B stand (facts recorded
from a suppressed engagement agree with a no-capture oracle trivially).

NOT A BUG: loadGizmos never sets Gizmo::shield (economy.cpp:138-170) — the
bridge already maps d.rowShield = g.level per the shieldChargesFor law
(campaign.cpp:1957-1970, SUM of cat-1 levels gated by requiresAvailable).

## ROOT CAUSE OF SEED-1 DIVERGENCE (measured t365trace, 2026-11-10)
Pre-flip seed 1: owner 6 captured Parsimony t265, Extinct t266. Post-flip:
NO captures t259-266. Census facts at the fork (t265 att6 def0 star30):
popA10=2 wsum=2 shld=0 hullDef=3 fd=0 dbl=0 base=4 shots=0 simCap=0.
The engagement RUNS (power gate passed, base 4 > hull 3) but commits ZERO
shots — while the standalone P2 debug harness (fresh bridge, same tables,
fd=0) gets shots=1+. So the commit loop loses shots in the CAMPAIGN
sequence (persistent shooter records across turns), not in first principles.
Also measured standalone debug: dmg=10 shields=1 hull=33 -> out.hullHit=0
(the FIRST committed shot reports hullAbsorb 0) — the apply/report tail of
commitShot needs reading (0x4b7e0 clamp region, shipsim.cpp:547+).

## THE cap=0 MECHANISM (measured, t265 shooter dump)
[dbg] t265 att6 star30 shooter: gate=1 otype=0 fire=100030 aslot=0 cap=0
filled=1 power=4. Sequence: engagement kills garrison (C4 zeroes kind/act/
gate/slots but NOT inventory rows or invCap); NEXT turn the same star's
garrison is "recreated" via `if (!findShip(gid))` — but gid is STILL in the
vector (corpse, owner=-1), so addShip never runs and the record keeps its
dead state; the bridge's slotMap_[gid]/slotMap_[sid] likewise survives, so
slotFor() returns OLD slot ids and NEVER touches invCap (growth only happens
on map-miss). Fresh Ship structs (shooter death -> recreated by engagement
code) start invCap=0 with a stale-populated map -> window 0 -> every scan
skips, upkeep materialises 0 shields (P2 shields=15->0 class), commitShot
reads stale non-gun rows (C1 handler != gun -> shots 0). Fix: ShipSim::
resetInventory(shipId) (sim-level plumbing: zero slots/cap/filled) + bridge
clears slotMap_[id] whenever it (re)initialises a record — dead corpse or
fresh add. A ship that DIED must be reborn with a clean inventory, not a
corpse's stale rows.

## FIX 5 — STALE slotMap_ ACROSS RECORD REBIRTH (measured, root of seed-1)
[sync] ship 6030 cat 0 ENTER cap=0 filled=1 / EXIT nextSlot=0: the map was
FULLY populated from prior engagements, so slotFor() hit the cache every
row, never grew invCap (growth happens only on map-miss) -> window 0 ->
companionScan 0 -> engageRound picks nobody -> shots 0 every turn -> no
captures -> seed-1 Extinct t266 vanished. Records die (C4) and are rebuilt
(fresh Ship struct, empty slots) but slotMap_ kept the corpse's rows.
Fix: bridge resetShipRecord(id) — slotMap_.erase(id) + zero the sim
record's inv/cap/filled — run on EVERY addShip AND on every garrison
resurrection (corpse owner==-1 path) AND shooter-recreation; syncRows then
rebuilds the window from scratch each engagement (idempotent per design:
setSlot same-cidx refusal + fresh map = same slots, same order).

## FIX 5 DECISION (shape): reset-per-engagement, not corpse-rebirth
Bridge resets BOTH records to a clean slate at the top of every
resolveEngagement (zero inv rows/cap/filled/stance fields; slotMap_.erase).
Rationale: the pre-flip aggregate was STATELESS per engagement (recomputed
from pop/tech each turn); persisting engagement state across turns was the
bridge's own flourish and produced the corpse/stale-map class. Ammo
(numUses) is a per-boundary concept and refreshUseCounts already re-arms
before every commit pass. Verdict-relevant state at fire time is fully
re-materialised by the cited laws after reset (syncRows -> recalc, upkeep
-> shields, setStance -> gate/stance).
