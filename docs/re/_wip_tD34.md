# tD34 — D33-L1 capture-emitter legality: REPRO + vendor capture-handler FUN-by-FUN (2026-11-27)

STEER (mid-tXT-1, D33): kPlayer=0 => "owner 1" = AI; user law: no capture of
an inhabited home is possible by day 20; "Dense+7 exits t20 for BOTH species
tested"; fix the EMITTER (campaign.cpp:2258) to the vendor fleet-arrival law,
not the Extinct check; cite vendor capture handler FUN-by-FUN before shipping.

## S1 REPRO MEASURED (post-tXT-1 binary f7452a3, build 2026-11-27 09:54)
Headless matrix `--campaign 60 --stars 100 --seed {1,2,3} --species {0,1,2,3,4}`
(15 runs): 15/15 "no victory after 60 turns"; every run `player stars 1` at
t60, all AI `ai stars 1 1 1 1 1 1` — zero captures, zero war, zero t20 exit.
Logs /tmp/d34repro/. Plus tXT-1's Begin-path witness (dense rung 2 + species
word 7, 60 NEXT TURN presses) already green on this fix (STATE tXT-1 LANDED).
=> THE STEERING PREMISE IS STALE: "exits t20 for BOTH species" was the
freeForAll=true arcade default (pre-f7452a3); the tXT-1 root-cause + fix
stands. Post-fix an AI capture requires war_ (combatPhase gate
campaign.cpp:2152), and fresh campaigns start at PEACE (diplomacy.md S19/S13.3),
first AI declare measured mid-game t143 — t20 capture is now structurally
gated by the war channel, not merely absent by luck.
HONEST LIMIT: the gate is the WAR channel, not a fleet-arrival channel. If a
chooser declared war at t5 on some seed, the port emitter could still take an
inhabited home with zero fleet involvement (pop-firepower garrison death,
bridge S1/S5). User law L1 ("no way... even if they were directly adjacent")
is NOT structurally guaranteed by the vendor's actual law — see S2.

## S2 VENDOR CAPTURE HANDLER FUN-BY-FUN (cite-below; disasm work/ascend_restored.bin)
(chain assembled from diplomacy.md S19, ships.md S69, _wip_t209 S4/S5, combat.md)
...
## S2 VENDOR CAPTURE HANDLER FUN-BY-FUN — FUN_0003a174 (disasm of
work/ascend_restored.bin THIS iteration, ranges 0x3a174..0x3a4a0; consistent
with diplomacy.md S19 / ships.md S69 / _wip_t209 S4-S5, all re-verified at
bytes, not just cited):
  ENTRY SHAPE: EAX = target PLANET record, EDX = star index (bound-checked
  0x3a187 vs planet+0x1a), EBX = OUT param. Assert planet-slot type byte
  ==0x17 at 0x3a1a6 (the call admits only a planet target).
  OWNER GUARD 0x3a1cc..0x3a1e1: ship->star owner ([esi+0x57]) must be !=0xff
  and != the ship's own owner — the resolver runs only for an INVASION of
  someone ELSE'S owned star.
  SUPER-MARINES PROBE 0x3a1f4..0x3a215: [esp] := -1; IF ability byte
  [row(attacker)+0x19d] == 0 THEN [esp] := 1. row = 247*owner x2-scale at
  0x12fb3 (t202 ability byte, distribution {0,2,11,19}). This [esp] flag is
  the FORCED-1 out-param source AND the success override (t209 S4).
  DIPLOMACY PRICE 0x3a255 FUN_00043a4c (attacker, victim) — t204 handler;
  return -1 (not-at-war path) -> GUARANTEE-WAR CLAMP 0x3a25a..0x3a291
  (slams attitude cell to DECLARE_WAR-10) — t207 law, verbatim.
  AMMO COUNT 0x3a2a2..0x3a2c5: count := NUMBER of the target planet's slot
  records (cap planet+0x15a, stride 7 from +0xab) whose byte == 0x49 — the
  INVASION MODULE cargo item (cidx 73). THE STAR ITSELF CARRIES THE
  INVASOR'S PAYLOAD COUNT: an invasion only exists as modules landed at the
  objective star.
  SHIELD DEFICIT 0x3a2c7..0x3a325: shields := 2 per ACTIVE item-0x13 (Mega
  Shield) slot + 1 per ACTIVE item-0x12 (Surface Shield) slot (planet item
  array esi+0x10 stride 4, active bit0 of word+2).
  NEED 0x3a327..0x3a345: need := max(count, shields+1); IF [esp] (ability
  byte == 0) THEN need := 1 (the SuperMarines FORCE). OUT param written
  0x3a35e = need.
  PAYLOAD CONSUMPTION 0x3a360..0x3a38b: clearSlot (0x496e4) the FIRST
  `min(need, count)` 0x49 slots at the star. 0x3a38d call 0x49acc.
  ITEM DISPLACEMENT 0x3a39d..0x3a45a: relocates up to `need` item-0x12
  slots then up to (need-edi)/2 item-0x13 slots via 0x38840 (the t381
  walk) — the invasion eats shields too.
  *** SUCCESS GATE 0x3a45c..0x3a46a (THE LAW):
      mov eax,[esp+0x10]        ; count (invasion modules AT the star)
      cmp eax,[esp+0x4]         ; shields
      jg  success               ; count > shields  => capture
      cmp dword [esp], -1       ; attacker ability byte != 0?
      jne fail                  ; YES (normal race)  => NO CAPTURE
      (fall through)             ; ability byte == 0 => capture regardless
  success tail 0x3a46c..: event-0xd announce (0x55a60) when attacker is the
  player global [0x7458e] and [0x7e582>>16]!=0x10, then ownership transfer
  (planet+0x67 := [0x12e10] per _wip_t209). fail tail 0x3a4cc.
LAW (verbatim shape): a star is captured IFF (invasion-module count at the
star > active shield units) OR (attacker race ability byte == 0 ==
SA_SuperMarines). POP/POWER/FIREPLAY NEVER ENTERS THE CAPTURE VERDICT.
=> THE PORT EMITTER IS THE BUG CLASS THE USER NAMED: campaign.cpp combatPhase
transfers owner_ on the BRIDGE GARRISON-DEATH verdict (hull < 1, C4) with
zero invasion-module operand — an empire with enough pop can take any
adjacent at-war star with no fleet, no modules, no shields. t20-class AI
captures were only ever blocked by the war gate (tXT-1); the CAPTURE LAW
itself is un-implemented.
## S3 PORT-FIX DESIGN (what the law means for campaign.cpp combatPhase)
Operand audit: the vendor success gate reads ONLY (count, shields, ability).
Garrison death / pop / firepower NEVER enters the verdict. The port's decider
(out.captured -> owner_ flip -> events push at :2258) is therefore replaced:
  attempt  = engagement ran (S3 power gate) AND modules_[a] > 0 (carrier
             analogue: ships.md S69 M2 witness — the resolver is entered only
             via a carrier carrying cidx-0x49; the t208 ship-cost gate stays
             as the port's carrier stand-in)
  success  = modules_[a] > shields || ability_[a] == SuperMarines
             (0x3a45c verbatim: count > shields; forced-1 leg iff ability 0)
  consume  = min(max(count, shields+1), count) from modules_[a]
             (0x3a2a2..0x3a38b aggregate form; the shield-DISPLACEMENT legs
             0x3a39d..0x3a45a stay UNMODELLED — semantics unread, named)
  clamp    = guaranteeWarOnInvasion fires on every ATTEMPT (resolver runs
             before the success test; t209 position law), not only captures.
modules_ producer: NO cited AI gizmo-production law exists in the corpus
(OQ-AI-production residue) => documented default: +1 per turn per owner that
has a Shipyard star, cap 6 (witness-observed max: Ignatz SIX cidx-73 slots,
ships.md S69(a)). Flagged INFERRED; the LAW being pinned is the gate, not the
producer rate. ind_ ship-cost charge (t208) kept unchanged (abilities.md
consequence doc); module consumption is the vendor operand on top.
Consequences to measure: (i) non-SuperMarines AI-AI captures now need module
accumulation > defender shields — t20 home capture structurally IMPOSSIBLE
(modules start 0, producer needs a Shipyard, first Shipyard itself needs
build time: user law L1 holds by construction); (ii) Minions keep their
always-capture identity (ability 0) but only WITH a carrier + modules;
(iii) PLAYTHROUGH runs may shift -> re-record; (iv) t208 e2e pin needs
setInvasionModulesForTest.

## S3b CORRECTION TO S3 (bytes re-read 0x3a327..0x3a33e, same session):
NEED = min(count, shields+1), NOT max: 0x3a333 cmp count,shields; jle keeps
need=count (0x3a33a need=shields+1 only when count>shields). ships.md S69(b)
"need := min(count, activeShieldUnits + 1)" is the correct prior reading;
Ignatz witness count=2 shields=1 -> need=2 consistent. Consumption = min(
need, count) = need (Minions forced need=1 consume exactly 1). Operand
IDENTITY: the slot walk is on the CARRIER record (ebp = 0x396cc(planet,
starIdx): +0x54 star pointer, +0xab ring stride 7, +0x15a cap == shipsave.h
ring law) — modules ride the SHIP, not the star. Port analogue therefore:
per-owner modules ledger (port has no per-ship inventory, gap row 16),
consumed at attempt time. Producer gate CITED: Invasion Module gizmo row
resReq byte 8 (gizmos.txt) + requiresAvailable law (OQ-014 CLOSED); rate
+1/turn per owner with a Shipyard star cap 6 = DOCUMENTED DEFAULT (Ignatz
six-slot witness bounds the cap; the vendor's AI build law is uncited
residue). Day-20 law L1 holds by construction: modules start 0 AND row-8
research AND Shipyard — "still building their first structure" at t20.
## S4 SHIPPED + MEASURED (this iteration)
CODE: campaign.h invModules_ ledger + invasionModules()/
setInvasionModulesForTest/addItemForTest hooks; campaign.cpp constructor
zero-init + expansionPhase producer (research-gate ONLY; the Shipyard-star
gate variant was tried FIRST and MEASURED-STALLS: seed 2024 zero captures in
6000 turns / no victory, vs 48 captures + Extinct t1436 without it — kept
comment names the evidence) + combatPhase emitter rewrite: attempt =
modules>0; captured = attempt && (count>shields || forced); consume min
(count, shields+1)/forced-1 on every attempt; clamp now ATTEMPT-TIME (t209
position law honored exactly); repel -> 0x3a46a continue before owner flip.
TESTS: suite 611 -> 617 / 0 / 0. Pins test_capture_law_tD34 x6 (early-
impossibility soak x3 seeds 0 capture events; count>shields positive +
consume-1; repelled burns + attempt-time clamp exact 280-neg/4 discriminator;
SuperMarines-without-modules cannot capture (T4, the decider-refutation pin);
producer zero at init; forced-through-shield positive T6). MUTATIONS
scripts/tD34_mutate.sh M1..M6 ALL CAUGHT; restore md5 448642ba verified;
REBUILD after mutation cycle before witnesses (tPF-7a law).
RE-PINS (law-slowed conquest, all MEASURED): test_campaign victory caps
1200->2400 (seed 1 Control t1875, seed 2 Extinct t540, seed 2024 Extinct
t1436, CLI --campaign 4000); test_species + test_ships stall guards
1600->2400 (finite, green). PLAYTHROUGH re-recorded: 2024 Extinct t1436 /
23 Control t1582 / 13 Extinct t538 (both gate greps satisfied). Begin dense+7
witness re-run on clean rebuild: SURVIVED 60t rc=0.
HONEST NEGATIVES: (1) the steering premise "dense+7 exits t20 for BOTH
species" did NOT reproduce post-tXT-1 (15/15 headless matrix runs + witness
survive; S1) — the tXT-1 peace-start fix stands; what was NEVER modelled is
the capture law itself, and that is what tD34 shipped (pop-firepower could
still flip owners pre-fix whenever war existed). (2) Module producer RATE and
the AI carrier behaviour are documented defaults (no cited build law); the
cidx-0x49 operand rides a per-owner ledger, not per-ship rings (gap row 16).
(3) Shield-item DISPLACEMENT legs 0x3a39d..0x3a45a unmodelled. (4) Leg A
"objective has no active Ship/Shield item" skip-flag (0x42cea) is NOT the
0x3a45c gate and stays as bridge S7 as-is. (5) D33-L2 (tSPEC-1) and L3
(tNAME-1) untouched — queued.
