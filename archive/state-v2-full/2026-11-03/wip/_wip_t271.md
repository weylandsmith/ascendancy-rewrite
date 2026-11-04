# _wip_t271 — per-cell terrain/nuke WIRING SCOPING (OQ-016 residue)

TASK: "DECIDE the cell model shape first (slot-array law + locator law are in
hand, STATE 'PLANET SYSTEM OBJECT'), then wire or file a REFUTED row with the
decision rationale. Cite economy.md §4 + STATE."

## S0. CITATION AUDIT (task premise vs disk)
- economy.md has THREE sections (1 grammar, 2 planet-type order/grids, 3 item
  table) — there is NO §4, and economy.md is REGENERATED every gate by
  scripts/gizmo_probe.py stage 3j (BLOCKED.md trap class): hand-authoring
  there is forbidden. The per-cell laws the task means are income-law.md
  §12 (CB picker, t42), §13 (built-item cell + rule G + hex geometry, t43),
  §13.5 (cargo chain, t44), T38 (rock event/semantics), T39 (completion
  branches incl. rock-consume + nuke-blocked), S10/T36 (world-gen class draw,
  capBase seed). STATE.md:195 'PLANET SYSTEM OBJECT' holds the slot-array law
  (base = planet-name-0x24; +0x10 slot-array ptr, member = ptr-0x88; slot 4B
  {class, itemIdx, flags u8, shield u8}) + locator law (cells {7,11,23,45,73}
  AND cap==cells+10; 2650/2650 x 17 captures).
- "rewrite wiring is PARKED (no cell model)" is STALE — it echoes the OQ-014
  row's t-era note. The rewrite HAS a cell model today (S1).

## S1. CELL MODEL AS IMPLEMENTED (audit campaign.h/.cpp, 2026-11-02)
PlanetState: cellClasses (world-gen chain draw replay + orbital ring 1 +
rock |8 event, campaign.cpp:161-190), itemCells (explicit cell parallel to
items), pendingItem/buildAcc. Pickers: drawCbCell (:574, t42 uniform non-rock
barren-included), drawItemCell (:666, rule-G uniform; dig = rock-only set),
cellActiveNeighbour/sizeClassFor (:635/:626, hex geometry pinned t43).
Completion path buildPhase :1026-1090 (dig consume + free-tech grant t203;
surface drawItemCell w/ documented fallback; orbital lowest-free ring).
channelAccFor reads class AT itemCells (:509-532). demolishAt keeps itemCells
parallel.
SHAPE DECISION (see S4): keep slot-indexed model; do NOT build a 2-D grid.

## S2. REACHABILITY CENSUS — MEASURED (scripts/r271_cellreach.py RC=0,
work/r1/t271_cellreach.out; 1074 saves, 66 run dirs, slot array via STATE
locator law):
- ACTIVE item census: {0:9726, 1:3235, 2:4091, 3:3250, 5:11631, 6:19946,
  7:6369, 8:15002, 12:793, 14:348, 15:21, 18:1519, 20:6067, 21:891,
  22:1621, 23:326, 24:142, 26:2743, 27:231, 28:2281, 29:400, 30:105}
- item 35 (Automation): any=0 ACTIVE=0 — NEVER queued/placed anywhere.
- item 36 (Terraforming): any=78, ACTIVE=0 — pending-only, zero completions.
- item 38 (dig): any=9, ACTIVE=0 (pending; AI chain A buys it — wired t203).
- word[0x73e3c] census {0: 1074}: static item-table region reads ZERO at
  VA+H in saves — the KNOWN t43 dump artifact (runtime copy lives elsewhere;
  the live value 22 was measured 4/4 in full captures, OQ-014 CLOSED row).
- Drill r271b_tfdrill.py + r271c_pendctx.py (RC=0,
  work/r1/t271_tfdrill.out / _pendctx.out): all 78 item-36 obs are on
  PLAYER (owner 0) worlds of the production-campaign lineage
  (selftest-t111-playcap t1131: Smorgasbord II/Hope I/Unterwelt I/Crell I;
  t260/t261 t1255: Sirverei III/Unterwelt I), pend54==36, slot word2&1 CLEAR,
  +0x50 low word 32..48 of COST 50, turn FROZEN (idle game) — mid-progress
  human queues the 10 s ring never saw complete. 0 T39b witnesses.
  Crell II slot62 cls=9 item=38 = pending dig on rock (1|8) — rule-D
  consistent.
- NEW OBSERVATION: a pending build RESERVES its slot: byte1 := item id with
  word2 bit0 CLEAR (human explicit-cell queue; t44 cargo-chain shape).
  Refines t202b's "autosave ring never catches pending != 0xFFFF" — pending
  IS observable in idle-turn production captures (turn held -> ring rotates
  within one turn). +0x4c M4 law unaffected (it counts SLOTTED items;
  pending term measured 0 there is about word2&1, consistent).

## S3. STATIC BOUNDS (read verbatim this session, work/ai_selector_disasm.txt)
- Scorer candidate loop 0x3f528..0x3f592: `cmp bl,5; je skip` (CB excluded) +
  `mov ax,[0x73e3c]; cmp ebx,eax; jge skip` — rows >= surface-count (22) are
  NEVER scored; loop walks 0..0x26 (cmp ebx,0x27). Matches the CLOSED OQ-016
  "candidates surface rows 0..21 minus Colony Base" and the rewrite's
  id<22 cap.
- Emergency chain FUN_0003fc4c purchase sets (ai-dossier.md S10 measured):
  {38 dig, 18, 19, 11, template {12,13,14,15,37}} — NO 35/36.
- Orbital-defence template {28,29,30,0,26} imm 0x89360 inside FUN_0003f758
  (shipyard tail) — the AI's orbital buys ARE live (22..30 active counts
  above); rewrite models the gate as NOT-modelled (_wip_t202 :266, no ship
  model) -> AI-DOCTRINE gap, banked for a future task, NOT per-cell terrain.

## S4. DECISION (the task's deliverable)
1. CELL MODEL SHAPE: KEEP the slot-indexed model (cellClasses + itemCells +
   class-byte rock bit). The slot-array law is a flat member array; rule G
   adjacency (the ONLY spatial law in the checker) is fully served by the
   pinned hex-geometry helpers. A 2-D occupancy grid would add no law the
   cited sources require. The model is already wired for every law with a
   WITNESS: world-gen classes, rock event, CB draw (t42), built-item draw
   (t43), channel gating (T35/T40), dig consume (t203), LGB (S10).
2. DO NOT wire the T39b item-36 Terraforming mutation (word2:=0/byte1:=0xFF/
   byte0:=1) or item-35 Automation word2|=2 into the rewrite NOW:
   - item 35: zero observations in ANY slot in 1074 saves — no witness ever;
   - item 36: zero completions ever witnessed (78 pending-only obs, turn
     frozen); AI-unreachable by two independent cited bounds (S3 scorer cap
     + chain set); player-reachable ONLY through the human UI, which the
     rewrite does not have (kBuildOrder is a documented stand-in policy);
   - strict-close + t256c precedent: wiring adds behaviour the captured
     original never exhibited. Filed as REFUTED-ROUTES t271 (route DEAD until
     re-open conditions: a human build UI ships OR a capture witnesses an
     actual completion).
3. Automation's OBSERVABLE economy effect is already modelled where cited:
   the +0x4c slot-flags-bit1 skip is a no-op by construction (rewrite stores
   active items only; campaign.h usedPopFor comment) and the governor==35
   UPOP bonus is pinned (t45).
4. Per-slot SHIELD byte (byte3 := 0 then |= 0xf (or 0x23 for id 0x1b) at
   shield completion, T39b generic branch): REACHABLE writes (18:1519,
   26:2743, 27:231 active obs; 19 ZERO — chain-C never fired) but its
   CONSUMER is unmapped (t207:
   bombard is fire-and-forget price, no per-ship gunnery channel; emergency
   chain reads the +0x59 COUNT not charges). Storing the write without a
   consumer = dead state; documented gap, OQ-019 family, NOT wired.
5. NUKE (Phase Bomb gizmo 70): unchanged BLOCKED.md :95 — capture-gated,
   static dead-ends T39e, default NOT modelled. Re-affirmed this iteration
   (no new capture class exists; closing route needs a scripted run).
6. Mid-game rock-consume T39a: remains unreachable — t29b CLOSED the only
   mid-game terrain mutation routes (item-36 completion + world-gen rock);
   with 36 unwired-by-decision and no other rock writer, a pending build can
   never land on a newly-rocky cell in the rewrite. Consistent, not a gap.

## S5. LEDGER DISPOSITION
- OQ-016 STAYS OPEN (strict-close): residue after this task = Phase Bomb
  capture law, human build-order minutiae, setup-draw law (t273 seed),
  per-slot shield consumer (OQ-019 family), word[+0x16] template source.
- REFUTED-ROUTES: new entry t271 (wire-T39b-now route DEAD + re-open
  conditions).
- AI orbital shipyard-tail template gap ({28,29,30,0,26} @0x89360): banked in
  S3 as a future-task seed (doctrine, not per-cell).
- KEEPER: scripts/r271_cellreach.py, r271b_tfdrill.py, r271c_pendctx.py all
  RC=0; outputs work/r1/t271_{cellreach,tfdrill,pendctx}.out.

PRE-FLIGHT: r1_game_health 07:39 UNHEALTHY (pid 535172 gone, ring stale
2097 s) — task fully offline, unaffected; no :9 interaction, zero clicks, no
loadstate. No new sitting (last timeline row t1236 07:04 predates t270
commit; no re-sit needed).
