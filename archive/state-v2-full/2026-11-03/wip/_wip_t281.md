# _wip_t281 — SA_Cornucopia (0x43de4) REPAINT WIRING (pure code)

## S0 PRE-FLIGHT (2026-11-02)
- r214_triage RC=0: tail 400 rows ALL turn 645 (tutorial lineage), 400 distinct,
  one canonical key shape — identical state to t280's close => NO new sitting,
  assignment stands (STATE t281 card).
- Production :9 pid 576895 alive (triage GAME PROCESS section).
- Drive-class re-queue check: needs NO :5910 client AND production-lineage ring.
  Ring is tutorial-645 lineage (not production) -> t279 stays HELD regardless of
  the client; verify client too (record below).
- Cited law (aicode.md §6.3 line ~950): body 0x43de4 — own planets, SKIP
  [p+0x16]==10; track MIN word [p+0x42]; on the min planet every slot-class
  byte in {0,1} := uniform pick {2,3,4} (pool 0x6838 u32x3, rng 0x7824f %3).
- Current rewrite (campaign.cpp:1676): picks min-pop owned star (pop>0 gate),
  richPros += 2. Task: wire the repaint verbatim over cellClasses, retire
  richPros, re-target test_species.cpp:211 leg.

## S1 RAW BODY 0x43de4..0x43e96 (re-read from work/t280_bodies.txt:152)
SELECT leg (0x43de4..0x43e31): eax = 0x2b057 (static planet pool), edx = index,
bound = dword[0x3a091] >> 0x10 (u16 high half — the pool count), stride 0x7b.
  - owner gate: bl = byte[eax+0x57]; cmp bl, byte[ebp] (self); != -> next.
  - SKIP gate: bx = WORD[eax+0x16]; cmp 0xa; == 10 -> next. (word read, not byte)
  - MIN leg: si = WORD[eax+0x42]; cmp cx, si; `jbe -> next` with cx init 0xffff
    and ecx NOT reset on accept => STRICTLY-LESS wins, FIRST wins on ties
    (cx = current best pop). Accept: [esp+0x6d0] = rec ptr, ecx = its pop.
  - 0x43e31: if best ptr == 0 -> EXIT 0x4400a (no owned eligible planet = no-op).
REPAINT leg (0x43e40..0x43e96):
  - ecx = dword[best+0x10]  (slot-array pointer, same field the orbit/planetary
    system object law uses), ebx = slot index, stride 4 per slot (the 4-byte
    slot record {class, item, flags, shield} of the OQ-014/planet-object law).
  - BOUND = WORD[best + 0x18] == surface cell count (the +0x18 analog) =>
    SURFACE SLOTS ONLY; the orbital ring [+0x18, +0x18+10) is NEVER repainted.
    (Sharpens §6.3, which did not state the bound.)
  - class byte al = byte[ecx]; if al != 0 && al != 1 -> skip slot (no write).
    NO occupied/pending gate — a slot holding an item is repainted too.
  - draw: scratch esp+0x6b0 loaded from pool 0x6838 via 3x movsd EVERY painted
    slot; call 0x7824f -> eax; edx:eax idiv 3 (signed, sar 0x1f first);
    al = byte[esp + edx*4 + 0x6b0]; byte[ecx] = al. Pool values measured t280
    = {2,3,4} => uniform pick of class 2/3/4 per eligible slot.
  - loop continues over ALL surface slots (one rng draw per painted slot).
## S1b CONSEQUENCES FOR THE REWRITE
  - Operands the rewrite carries: owner_ (star owner), planets_.pop (+0x42),
    planets_.surfaceCells (+0x18), planets_.cellClasses (class byte analog).
    MISSING operand: the +0x16 weight-row index (see S2).
  - rng: the vendor draws per painted slot. Rewrite RNG discipline: abilities
    must not disturb the dip-pair/turn stream (t256 note). Decide: deterministic
    pick vs rng_ draw — must be justified, not defaulted.


## S2 +0x16 SEMANTICS — MEASURED (scripts/r1_t281_w16_census.py, RC=0)
Census of WORD[rec+0x16] over the static pool (base 0x2b057 stride 0x7b, count
hi16 ds 0x3a091) in TWO lineages, item-table-anchored base 0x1bf4d8:
  bank-t1254 (production lineage, count 145): hist ALL
    {0:10 1:16 2:13 3:14 4:14 5:8 6:11 7:13 8:14 9:17 10:15} — uniform-ish
    over 0..10; OWNED n=124 every value present; v16==10 records: 15, spread
    across owners 0/1/2 (rec3 pop61, rec21, rec22, rec37, rec46(o1), rec63,
    rec66, rec73, rec107(o2), rec122, rec125(o1), rec130, rec140, ...).
  bank-t273-tutorial645 (count 135): same uniform shape {0:12..10:12}.
VERDICT: +0x16 is a STORED per-planet weight-row index (world-gen rng%11
@0x23a97/aa8 — this is the FIRST direct persistence measurement of that draw),
NOT a homeworld marker. t105 §3's "[rec+0x16]==10 leg = homeworld exclusion
[inferred from this match]" is REFUTED by this census (15 tens across 3 owners;
every value appears among owned records). Row 10 = preset [0,33,34,33] (income-
law.md S10 table) = the ZERO-BARREN template => the skip means "Cornucopia never
re-repaints a planet whose template can't produce barren ground" [inferred
reading of intent; the mechanical law is just word==10].
t29b residue (save-time +0x16 does not predict save-time barren%%) STANDS —
the census says the field persists, not that it drove the observed histogram.
REWRITE REPRESENTABILITY: the ctor ALREADY draws `const int row = next() % 11`
(campaign.cpp:156) but discards it. Storing it (PlanetState.terrainRow) makes
the skip operand EXACTLY representable. No refutation needed.


## S3 REWRITE STATE CENSUS + DESIGN (richPros retirement)
- richPros (campaign.h:92): writer = ONLY campaign.cpp:1683 (Cornucopia case);
  readers = storedProsFor (campaign.cpp:786 joins it into the PROS acc) +
  richProsFor accessor (campaign.h:208) + test_species.cpp:236. NO ui/*.cpp|h
  reader (source census; the build/*.o hits are inlined campaign.h copies).
  Field was the [documented default] stand-in; the cited law is the repaint.
- The repaint's REAL income channel already exists: channelAccFor T35 gives a
  +1 class bonus per active item whose cell class is 2/3/4 (field non-zero).
  Repainting barren/normal cells under items raises income through the SAME
  accumulator the vendor uses — no synthetic field needed.
- cellClasses = raw class byte analog INCLUDING rock bit 3 (|8): vendor's raw
  byte test {0,1} naturally SKIPS rock bytes 8/9 — replicate by testing the raw
  stored int, NOT (cls & ~8). Orbital ring cells (index >= surfaceCells) are
  outside the vendor bound WORD[+0x18] — replicate bound exactly.
- RNG DECISION (justified, not defaulted): the vendor's single 0x7824f stream
  was split in the rewrite into worldLcg_ (world-gen + item-cell picker laws,
  the t40/t43 mid-turn draws) and rng_ (freeTech grant etc.). The repaint is a
  TERRAIN mutation, same law family as the world-gen draw loop and the rock
  event (both worldLcg_ territory); drawing it from worldNext() keeps the free-
  tech rng_ trajectory untouched. Pick = 2 + worldNext() % 3 per painted slot.
  [inferred stream choice; pick MEMBERSHIP {2,3,4} is the cited part.]
- min-key: drop the current pop>0 gate (vendor has none; cx=0xffff prune is
  strictly-less, first pool index wins ties -> iterate stars in order with
  strict '<').
- terrainRow: ctor campaign.cpp:156 already computes `const int row = next() %
  11` then discards it; store into PlanetState.terrainRow (+0x16 analog).
- test plan: split the Cornucopia legs out of
  species_more_max_pop_raises_caps_and_cornucopia_adds_pros into
  species_cornucopia_repaints_min_pop_colony_t281: control differential
  (Cornucopia vs Unknown, seed 16, fire t150 = cad[10]); painted-set (cell diff
  vs control over owned planets) == {argmin eligible}; every raw surface byte
  of target NOT in {0,1} after fire; rock bytes + orbital ring invariant;
  event text. Mutation catchers: bound widened to cellClasses.size() (paints
  ring) and skip-leg deleted (if seed 16 exercises the skip — measure).


## S4 WIRING LANDED (campaign.h + campaign.cpp + test_species.cpp)
- campaign.h: PlanetState gains `int terrainRow` (+0x16 analog, ctor-stored);
  `double richPros` DELETED (comment keeps the why); `richProsFor` accessor
  DELETED (source census: zero UI readers; build/*.o hits were inlined copies).
- campaign.cpp ctor:154: `planets_[s].terrainRow = row;` (the previously
  discarded rng%11 world-gen draw).
- storedProsFor: richPros join removed; govBonus (t45 governor law) KEPT
  (mid-edit slip: first patch dropped `+ govBonus`; caught and reverted the
  same minute — suite green after).
- Cornucopia case: verbatim select (owner, skip terrainRow==10, strict-< min
  pop, first-wins ties, null-exit) + repaint over [0, surfaceCells) of raw
  {0,1} -> 2 + worldNext()%3; event "made <star> a rich world (N cells
  repainted)".
- TEST species_cornucopia_repaints_min_pop_colony_t281 (split out of the
  more_max_pop test, which keeps only its own legs): seed-16 control
  differential (target computed independently from owner/pop/terrainRow; all
  other stars' cellClasses byte-identical vs control; target surface has zero
  surviving 0/1; painted cells only 0/1 -> {2,3,4}; orbital ring frozen) PLUS
  the seed-8 SKIP/NULL-EXIT leg: MEASURED (temp seed-scan diagnostic, seeds
  1..40, deleted after use) that owner 1's ONLY colony at t150 sits on row 10
  for seeds 8/9/14/14/18/26/31 -> on seed 8 the cited skip must produce NO
  event and NO cell change.
- MUTATION PROBES: M1 bound widened (paints orbital ring) -> CAUGHT (10
  fails, ring-equality line). M2 skip leg neutered -> CAUGHT (seed-8 line
  304 !hasEvent fails). M3 tie-break >= -> NOT caught (seed 16's owned set has
  no pop tie at the argmin; honest negative — the first-wins reading stands on
  the raw `jbe` at 0x43e24, not on test coverage). All reverted; suite 159/0.
- Suite: 159 tests 0 failed (was 158; +1 net after the test split).


## S5 FINISH (docs + gate + commit)
- Docs banked: aicode.md §6.3 t281 amendment block; abilities.md SA_Cornucopia
  row rewritten; ai-dossier.md row 11 (abstraction clause corrected in place +
  T281 PASS appended); income-law.md +0x16 note under world-gen seed section;
  OPEN-QUESTIONS.md OQ-016 STATUS t281 (STAYS OPEN — persistence measured,
  provenance still open); this file S0..S5.
- Keeper tool: scripts/r1_t281_w16_census.py (anchor-derived base, two-lineage
  +0x16 histogram). Temp diagnostic rewrite/tests/t281_diag_seedscan.cpp used
  for the seed-8 fixture premise, DELETED after use (not committed).
- Machine UNTOUCHED throughout: production :9 pid 576895 (ESTAB VNC client
  re-confirmed at start -> drive HOLD; ring still tutorial-645 lineage -> t279
  release condition unmet regardless). No clicks, no saves.
- QUEUE DISPOSITION: t281 was the last §6.3 body whose operands the rewrite
  state carries (task-card premise, re-checked: remaining labels are per-ship
  = OQ-019 boundary or AI->AI = row-12 boundary, both refused with reasons on
  file). Offline RE work is drained -> NEXT parked on the WAIT-TRIGGER
  sentinel per the after-drains law; triggers named in the NEXT block.

