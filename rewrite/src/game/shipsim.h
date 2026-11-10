#pragma once
#include <cstdint>
#include <vector>
#include "formats/shipsave.h"

namespace ascend::game {
// PER-SHIP SIM (queue rows t361+t363, user ruling D2=(b)). Build contract:
// docs/re/pership-spec.md (2); durable laws: docs/re/ships.md S17/S21/S22/S22
// S24/S59, docs/re/combat.md §1, docs/re/ai-dossier.md §5. Every constant
// below cites docs/ (rewrite evidence rule, docs/PLAN.md rule 1); INFERRED
// modelling choices are flagged as such. Scope t361: ship list, per-ship
// dwell countdown, order apply at the turn boundary. Scope t363
// (docs/re/_wip_t363.md S1..S6): gizmo inventory + upkeep (spec 3 G1..G9)
// and carrier/cargo FIELDS (spec 4 C1..C4 — the C5 chooser stays a named
// non-goal). The combat round (spec 5) is t364 — the sim applies ORDERS and
// cited upkeep laws, never invented gizmo effects.

// Order kind verbatim, +0x58 (pership-spec §2 kind enum, end-to-end values
// {0..5} with the imm store census 0x24a00/0x3fb3e/0x3ca60/0x39859/0x2202f/
// 0x22243 in ai-dossier §5). Functional descriptions only — SO_ labels are a
// NON-GOAL (spec N5).
enum class OrderKind : uint8_t {
    NoOrder = 0,     // command clear (live kind 0 only on dead slots, spec A4)
    Move = 1,        // coord payload; completion FUN_00049880 (T-6)
    StarTarget = 2,  // colonize/land path; completion FUN_00049a34
    Engage = 3,      // act state (targetability gate FUN_00039894)
    InSystem = 4,    // arrived/positioned; DWELL state (T-8)
    Placement = 5,   // transit-to-star (lane march T-7 / placement T-3)
};

// Single-image LCG FUN_0007824f verbatim (income-law.md S10 t29b):
// state = state*0x41C64E6D + 0x3039; value = (state >> 16) & 0x7fff.
// Same form as campaign.cpp worldNext()/homeNext()/visNext() — the campaign
// RNG discipline (REFUTED-ROUTES) means ShipSim keeps its OWN isolated stream
// (t195 visLcg_ precedent) that provably cannot perturb campaign streams.
struct Lcg {
    uint32_t state = 0;
    int next() {
        state = state * 0x41C64E6Du + 0x3039u;
        return static_cast<int>((state >> 16) & 0x7fffu);
    }
};

// One star for the placement law (T-3): position := star coords + (0,-200,0)
// + rng%200 on the other two axes (ships.md §19 T3, jitter const LIVE -200.0
// at B+0x82bb0+0xaee).
struct SimStar {
    int id = 0;
    float pos[3] = {0, 0, 0};
};

// One lane for the march law (T-7). gate1 = byte[lane+0x23] bit0 (third-speed
// lane, pool word 0.333333 MEASURED, ships.md S22 L1/L3); the species gate2
// (double) is NEVER-SEEN zero-witness (S22 L5) — kept as a flag, never fired
// by any shipped scenario (spec N4: model the cited FORMS only).
// `closed` = byte[lane+0x23] bit 0x2 (t363R polarity adjudication, _wip_t363
// S4 item 3 + S6 raw re-read 0x49a21 `test BYTE[lane+0x23],0x2; jne -> 0`):
// SET means DENIED to a star-target transit, CLEAR means admitted. Named
// `closed` because that is what the branch enforces (FUN_000499f8).
struct SimLane {
    int id = 0;
    int a = -1, b = -1;        // SimStar ids (lane endpoints)
    float len = 0;             // lane_len = |A-B| (S22 L1)
    bool thirdSpeed = false;   // gate 1
    bool closed = false;       // transit DENIED (byte[lane+0x23] & 0x2)
};

// ---- GIZMO INVENTORY (t363, spec §3 G1..G9; laws _wip_t363 S1a/S3a/S3d/S6) --
//
// Key cidx verbatim from extracted/ascend00/gizmos.txt (work/r363_gizmo_rows
// .json, cross-validated against the RAM census in ships.md §12 — _wip_t363
// S3b reproduces the measured gate/cost/level multisets EXACTLY).
enum : uint8_t {
    kCidxCloaker = 0x2a,        // recalc +0x24++ per copy      (0x49bc9)
    kCidxLaneDrive = 0x2b,      // recalc lane-step-X pool copy (0x49bb6)
    kCidxHyperdrive = 0x2c,     // recalc lane-step-Z pool copy (0x49bc0)
    kCidxMagnetron = 0x3c,      // residue HOME only (zero-carried, S4/S5)
    kCidxPhaseBomb = 0x46,      // residue HOME only (zero-carried, S4/S5)
    kCidxColonizer = 0x47,      // recalc +0x28 := -1           (0x49b9b)
    kCidxInvasionModule = 0x49, // carrier/cargo C1/C2
};

// Lane-step pools (recalc 0x49bce..0x49c04: fistp(cntA * ds:0x2583) -> [+8],
// fistp(cntB * ds:0x258b) -> [+c]). The pool words themselves are DATA-Pool
// values not present in the image dump (t43 stale-DAT law), so they are
// DERIVED from the MEASURED live pairs (+8,+c) in {(14,0),(0,28)} — one
// Star Lane Drive contributes 14 lane-step X, one Hyperdrive 28 lane-step Z
// (_wip_t363 S3a NEW SYNTHESIS; closes the ships.md S22 "step CONSTANT 14"
// residue as a derived-from-measurement value, flagged as such).
constexpr float kLaneStepXPool = 14.0f;
constexpr float kLaneStepZPool = 28.0f;
constexpr int kRingSlots = 25;   // formats::ShipSave::kRingSlots (parser law)

// One inventory slot: stride 7 (cidx u8 / use u16 / payload u32), verbatim
// from the ring walk (0x4a6b0 `add ebx,0x7`, spec G2/G7). cidx 0xFF = EMPTY.
struct InvSlot {
    uint8_t cidx = 0xff;
    uint16_t use = 0;       // per-slot use counter (spec G7; semantics OPEN)
    uint32_t payload = 0;   // MEASURED 0 on 5860/5940 slots, 0xFFFFFFFF on 80
                            // slots that ALL sit on upkeep-gate rows; the
                            // -1 test is the only cited consumer (_wip S4/S5)
};

// A design (gizmo) row, restricted to the columns the cited laws read
// (spec G1: stride 0x6a, 76 rows, base PTR_DAT_0007650c; the rewrite's
// Gizmo parse of gizmos.txt IS this table — _wip_t363 S3b). Derived-slot
// law: cat0 weapon +0x52=Level, cat1 shield +0x56=Level, cat2 drive +0x5e,
// cat3 scanner +0x62, cat4 generator +0x66=POWER(+0x36); the init-zero law
// (recalc 0x49ad5..0x49b19 zeroes every accumulator first) means a row of a
// category contributes ONLY to its own slot, hence the row* fields below.
struct SimDesign {
    int cat = 5;                 // +0x32 (0 weapon,1 shield,2 drive,3 scanner,
                                 // 4 generator, 5 special — economy.h GizmoCat)
    int32_t power = 0;           // +0x36 (op cost; generators: power supplied)
    int32_t range = 0;           // +0x3a
    int32_t level = 0;           // +0x3e
    int32_t numUses = 0;         // +0x42 (refresh operand, spec G7; 0 = the
                                 // dispatcher's "no decrement" guard)
    int32_t industry = 0;        // +0x46 (spec G1 col order); never read by a
                                 // cited law (G8: no design-cost total is ever
                                 // materialised) — carried for the model only
    bool upkeepGate = false;     // w16 +0x33 bit 0x20 (TOGGLEABLE per the
                                 // vendor flag table, gizmos.md §1) — MEASURED
                                 // true on EXACTLY rows 10..15, all cat 1
    // Derived-slot contributions (recalc 0x49b52..0x49b8e), pre-switched so
    // the recalc body stays verbatim without a category branch per slot:
    int32_t rowWeapon = 0;       // cat==0 ? level : 0   (+0x00)
    int32_t rowShield = 0;       // cat==1 ? level : 0   (+0x04, also +0x90)
    int32_t rowDrive = 0;        // cat==2 ? level : 0   (+0x10)
    int32_t rowScanner = 0;      // cat==3 ? level : 0   (+0x20)
    int32_t rowGenPower = 0;     // cat==4 ? power  : 0  (+0x18)
};


// Ship record fields the skeleton consumes. Offsets are into the 0x162 record
// (pership-spec §1 field table); fields the t360 parser does not read
// (+0x52 ETA) are flagged at the seam. Guest-physical pointer fields
// (+0x59/0x63/0x68) are represented by SIM-LEVEL ids (star/lane ids) — the
// sim is driven headlessly from record state, never from live pointers
// (spec N8).
struct Ship {
    int id = -1;             // array slot (record index; identity law A2 uses
                             // the record address — slot is the save-side
                             // surrogate, parse-verified t360)
    int owner = -1;          // +0x56 race index == (+0x54 handle)>>16 (t273)
    OrderKind kind = OrderKind::NoOrder;         // +0x58
    uint32_t orderTarget = 0;                    // +0x59 (raw value kept)
    int targetStar = -1;     // sim-level target for StarTarget/Engage
    int laneId = -1;         // sim-level target while Placement (kind 5)
    uint8_t act = 0;                             // +0x5d (0 none, 1 congregate, 2 engage)
    uint32_t actTarget = 0;                      // +0x5e
    uint8_t orderType = 0;                       // +0x67 (issuer sets 5 for delayed moves)
    float targetPos[3] = {0, 0, 0};              // walk target triple (+0x6c
                             // abs-triple semantics for orderType 3, S17 T1;
                             // ptr-deref triple for type 1 — the sim holds
                             // the triple explicitly, INFERRED surrogate)
    float pos[3] = {0, 0, 0};                    // +0x9e triple
    int32_t power = 0;                           // +0x88 multi-turn fuel budget
    int32_t powerMax = 0;                        // +0x18 recharge cap
    int32_t moves = 0;                           // +0x94 per-call budget (sugar units)
    int32_t driveStat = 0;                       // +0x10 drive total (refill source)
    int32_t integrity = 0;                       // +0x8c
    int32_t maxIntegrity = 0;                    // +0x98
    uint16_t status = 0;                         // +0x9c
    int32_t laneStepX = 0;                       // +0x8  (step0 = X+Z, S22 L2)
    int32_t laneStepZ = 0;                       // +0xc
    int32_t etaDay = 0;                          // +0x52 dual-use field; NOT read
                             // by the t360 parser — fromRecord() defaults it
                             // to the current turn (INFERRED: full refill),
                             // explicit values via direct assignment.
    // ---- t363 recalc-owned fields (FUN_00049acc, spec G2 "stats
    // re-materialized on every mutation"; _wip_t363 S3a byte-level). The
    // recalc ZEROES these and re-derives them from the ring, so they are
    // engine state, never inputs, once the sim owns a design table. NB the
    // recalc also zeroes [+0x18] powerMax (generator sum) — fromRecord()
    // therefore imports powerMax VERBATIM and recalcShip() is never fired on
    // import (named asymmetry, _wip_t363 contract item 5).
    uint32_t weaponLevel = 0;    // +0x00 sum of row[+0x52] over non-empty slots
    uint32_t shieldLevel = 0;    // +0x04 sum of row[+0x56]
    uint32_t cat2PowerCarry = 0; // +0x1c sum of row[+0x36] where cat==2 (0x49b85)
    uint32_t scannerTotal = 0;   // +0x20 sum of row[+0x62]
    uint32_t specialCount = 0;   // +0x24 count of cidx==0x2a Cloaker (0x49bc9)
    int32_t targetSlot = 0;      // +0x28 := -1 IFF carrying a Colonizer (0x49b9b)
    int32_t hullBaseDrive = 0;   // +0x14: driveTotal := this BEFORE slot adds
                             // (read at 0x49ae4, stored at 0x49b29)
    uint32_t shields = 0;        // +0x90 SHIELD CHARGES (t86 CLOSED): zeroed
                             // ALWAYS at 0x4a6a6, += row[+0x56] per affordable
                             // cat-1 slot, zeroed again if status bit3 set
    // Inventory ring (spec G2/G3): 25 stride-7 slots, window = invCap for the
    // mutators/recalc (fillFirstEmpty scans i<cap, 0x4964a — NOT all 25; the
    // slots beyond cap are the PHANTOM zone, set-slot admits idx==cap).
    // invFilled == +0x15e (inc/dec at the mutators; fromRecord imports the
    // stored verbatim value, phantom +1 preserved — parser law shipsave.h:34).
    InvSlot inv[kRingSlots];
    uint32_t invCap = 0;         // +0x15a
    uint32_t invFilled = 0;      // +0x15e
    // Direction flag +0xa2 (kind-2 completion 0x49a85..0x49a97: := 1.0f iff
    // the order target == lane[0], the A-end system object — S22 L1 "A :=
    // ptr[H]"). true == the ship entered the lane at the A end, so laneMarch
    // marches toward B: endpoint = laneToB ? star(l->b) : star(l->a) (contract
    // item 3; the raw flag drives the NOT-CITED galactic-frame transform,
    // spec G-d — this is the sim-level surrogate). Default true keeps the
    // t361 golden-jitter test green (its mkLane has A==B anyway).
    bool laneToB = true;
    // The SimLane id the order payload +0x68 refers to (vendor: FUN_00049a34
    // takes edx = [ship+0x68] = the lane RECORD pointer; guest-physical, so
    // the sim holds the id — spec N8). fromRecord() leaves -1 (the parser
    // keeps orderPayload raw; the caller maps it). Set alongside targetStar.
    int orderPayloadLane = -1;
    // Species col-0x12 lane-travel gate (0x49a17, race table stride 0x1ee):
    // NEVER-SEEN zero-witness (S22 L5; spec N4 keeps the FORM, never fired
    // by shipped scenarios). Per-ship surrogate for BYTE[0x12fb3+race*0x1ee]
    // == 0x12; default false == gate never admits on species alone.
    bool speciesLaneTravel = false;

    // Dwell countdown (QUEUE-TURN LAW, ships.md §10 item 1 + §11): a queued
    // order with turn word != 0 SUPPRESSES the move and decrements per turn.
    // FIELD HOME DISPUTED (spec G-a): the 0x3ac1c write site is on the
    // pending-slot/command object (word +0xac), NOT a cited ship-record
    // offset — behaviour modelled, home unresolved, do not invent an offset.
    int32_t dwellTurns = 0;
    // Lane-local progress while kind==5 (lane-local frame, S21 item 4; the
    // galactic-frame transform at lane end is NOT cited — spec G-d — so the
    // sim re-places via the cited T-3 placement law on arrival).
    float laneX = 0;
    bool arrivedFlag = false;  // walk flag 8 (S17 T1: arrived := walk == d)

    // Map a parsed save record (formats::ShipSave::Record, t360) onto a sim
    // ship. Census laws (S59 L2 full-window scan, L4 probe-home rule) are the
    // PARSER's job and already applied: dead rows must be filtered by the
    // caller BEFORE this call. targetStar/laneId stay -1 — pointer fields are
    // not dereferenced here (guest-physical values kept raw in orderTarget).
    static Ship fromRecord(const formats::ShipSave::Record& r,
                           int currentTurn);
};

// Turn-boundary report (what one advanceBoundary() did).
struct BoundaryReport {
    int asserts = 0;            // assert-law violations counted (never crashes)
    int rngDraws = 0;           // LCG draws consumed this boundary
    int sweeps = 0;             // executor sweep passes run this boundary
                                // (driver FUN_0002547c 0x2550c..0x25527 repeat
                                // law, t362; >=2 means piecemeal departure fired)
    std::vector<int> placed;    // ship ids: kind 5 -> 4 arrival placement (T-3)
    std::vector<int> landed;    // ship ids: kind 1 arrival landing (T-6)
    std::vector<int> laned;     // ship ids: kind 2 arrival -> kind 5 transit
                                // (FUN_00049a34 admitted leg, t363; the assert
                                // leg COUNTS these per _wip_t363 S4 item 4)
    std::vector<int> acted;     // ship ids: the executor pick(s) this boundary,
                                // in pick order (a ship may repeat: interleaving
                                // is by REMAINING POWER, S17 T4)
    bool executorStalled = false;  // safety cap hit (must never fire)
};

// The per-ship engine skeleton. Turn frame per pership-spec §2 (ai-dossier §1
// turn frame + ships.md S22 IDENTITY TIE):
//   (1) per-ship turn tail: status +0x9c := 0, POWER refill [+0x88] :=
//       trunc([+0x18]*(1+clamp((T-[+0x52])//100,0,10)/10)) [t101 leg3,
//       combat.md §1; the clamp caps the multiplier at 2.0];
//   (2) ship list order: stable-stable ascending on the verbatim comparator
//       0x40eb4 — [ship+0x52] - [ship+0x52] (raw read, _wip_t361 S1; the
//       ai-dossier "descending design power" label vs the +0x52 operand is
//       DISPUTED — the VERBATIM comparator wins);
//   (3) queue suppressor: dwellTurns > 0 suppresses the executor and
//       decrements ONCE per boundary AFTER all sweeps read the words (T-10
//       behaviour, home DISPUTED G-a);
//   (4) executor DRIVER (FUN_0002547c, t362): REPEATS the whole per-race pass
//       while any race reports work (0x25525 test edi,edi jne). Each pass, per
//       race: refill MOVES from drive (+0x94 := +0x10, FUN_0004a658 re-grant
//       at 0x412cf — INSIDE the re-invoked prologue, so PER SWEEP), then pick
//       the ONE eligible ship with MINIMUM POWER (strict <, first-in-list
//       ties — ships.md S17 T4 t183 decompile; ai-dossier "MAX" wording is a
//       misread, _wip_t361 S1), commit its move, assert kind in {3,4} else
//       count violation 0x93e (0x419cf..0x419f1 verbatim). Work is reported by
//       the COMMIT EXIT (0x41b8f: remaining walk > 0 -> -1, else 0): a ship
//       with walk left re-arms the repeat => PIECEMEAL DEPARTURE — ships
//       depart one-per-sweep in ascending-POWER order until each arrives or
//       drains (witness: 3 same-owner kind flips in one boundary,
//       work/r362_witness.out B2). The t361 one-pick-per-boundary reading is
//       superseded (_wip_t362 S4/S6/S7).
// Decider policy (FUN_00040178 target scoring FUN_00039b28) is NOT banked —
// hooks below, default no-op; the sim never invents AI target choice (C5/N2).
class ShipSim {
  public:
    explicit ShipSim(unsigned seed, int turn = 0);

    void addStar(const SimStar& s);
    void addLane(const SimLane& l);
    void addShip(const Ship& s);

    // List order is engine state (the sorted array drives tie-breaks).
    const std::vector<Ship>& ships() const { return ships_; }
    Ship* findShip(int id);
    int turn() const { return turn_; }
    uint32_t lcgState() const { return lcg_.state; }
    int totalRngDraws() const { return rngDraws_; }

    // Order issue API (the "order apply" surface at the turn boundary).
    // setAct mirrors the decider's store (0x40224 act-legality decider,
    // t96 correction in ai-dossier §5): act + actTarget in one step.
    void setAct(int shipId, uint8_t act, uint32_t actTarget);
    // issueTravel mirrors travel issuer FUN_000220a8 (T-4): validates order
    // kind in {Move, StarTarget}, sets kind Placement + orderType 5, resets
    // lane-local progress. False (state unchanged) if the kind is not issuable.
    bool issueTravel(int shipId, int laneId);
    // retreatToSystem mirrors 0x220f2 (T-5): kind in {Engage, Move,
    // StarTarget} -> InSystem when the target stops being targetable. The
    // targetability test itself (FUN_00039894) is engagement scope (t364);
    // the caller invokes this when IT knows the target is gone.
    bool retreatToSystem(int shipId);
    // Per-race focus object (0x41a1c compares [+0x5e] against the current
    // object): when set for a race, ships whose actTarget differs get their
    // act CLEARED at the boundary (0x41a30) — re-decide is the caller's hook.
    void setFocus(int race, uint32_t focus);

    // One day at the turn boundary: steps (1)-(4) of the frame above, races
    // in ascending owner order. Assert violations are COUNTED, never fatal
    // (headless harness; the vendor calls assert fn 0x2a428).
    BoundaryReport advanceBoundary();

    // ---- t363 GIZMO/INVENTORY API (laws: _wip_t363 S1a upkeep, S3a recalc,
    // S1c refresh, S6 mutators FUN_00049698/0x496e4/0x49624) ----------------
    // Install the design table (index == cidx; SimDesign cat 5 rows are the
    // specials). The sim keeps its OWN copy — the vendor indexes a raw table
    // at 0x7650c + cidx*0x6a directly; unset rows behave like all-zero cat-5
    // rows (no gate, no contributions), which is the honest default for
    // designs the pin tests do not model.
    void setDesigns(const std::vector<SimDesign>& designs);
    const std::vector<SimDesign>& designs() const { return designs_; }
    // FUN_00049acc verbatim: zero accumulators, driveTotal := hullBaseDrive,
    // sum the window i<invCap over non-empty slots, special cidx legs, then
    // laneStepX/Z from the DERIVED pools (kLaneStepXPool/kLaneStepZPool).
    // NEVER fired by fromRecord (would destroy the stored powerMax — see the
    // Ship field note).
    void recalcShip(Ship& s) const;
    // FUN_0004a658 verbatim (upkeep): MOVES re-grant branch on status bit0/
    // bit1 (bit1 SET adds driveAddend_ — the sim-level stand-in for the
    // UNMEASURED ds:0x77f6c, _wip_t363 S3c), shields := 0 ALWAYS, ring scan
    // (ALWAYS RUNS, even on the bit0 branch — S4 item 1), per-slot upkeep
    // gate/payload/payable chain, bit3 zeroes shields. Returns the burn
    // actually applied to power (0 when nothing was payable).
    int32_t upkeep(Ship& s);
    // Turn-tail slot refresh 0x4a772..0x4a7a4: every non-empty slot's use
    // word := design[+0x42] (numUses; MEASURED 5940/5940 save-side, _wip S4
    // item 5). Runs for EVERY ship, no kind gate (S1c NB).
    void refreshUseCounts(Ship& s);
    // FUN_00049698 set-slot: REJECT iff idx > invCap (idx==cap ADMITTED ->
    // phantom slot, stats inert because the recalc window is i<cap); REJECT
    // same-cidx-in-target-slot only (duplicates across slots LEGAL); filled
    // +1 iff the old byte was 0xFF; recalc. True == accepted (-1 leg).
    bool setSlot(Ship& s, uint32_t idx, uint8_t cidx);
    // FUN_000496e4 clear-slot: NO index bound (phantom clearable); byte
    // 0xFF -> no-op false; filled -1; recalc.
    bool clearSlot(Ship& s, uint32_t idx);
    // FUN_00049624 fill-first-empty: first EMPTY (0xFF) slot in i<invCap;
    // none (or cap<=0) -> false, state untouched; else filled+1 + recalc.
    bool fillFirstEmpty(Ship& s, uint8_t cidx);
    // CARRIER / CARGO accessors (spec C1..C4; C5 chooser is a NON-GOAL —
    // these answer "which ship carries what", never "who should carry it").
    // carriesCode: any slot in i<invCap with cidx == code.
    bool carriesCode(const Ship& s, uint8_t code) const;
    // firstCarrier: C2 shape (engagement loop 0x42d09..0x42d5b verbatim) —
    // FIRST ship in list order with kind==InSystem AND a slot == code. No
    // strength comparison: eligibility is order-state + equipment.
    const Ship* firstCarrier(uint8_t code) const;
    // ds:0x77f6c stand-in (UNMEASURED, ships.md:365 — sim-level constant,
    // never a record offset; default 0 == the bit1-clear branch always).
    void setDriveAddend(int32_t addend) { driveAddend_ = addend; }

    // Determinism digest: FNV-1a64 over every ship's cited state + the LCG
    // state + the turn counter. Two runs, same seed + same inputs => same
    // digest (pin test t361).
    uint64_t digest() const;

    // Cited helpers, exposed for the pin tests.
    // powerRefill: trunc(powerMax * (1 + clamp((T-eta)//100, 0, 10)/10))
    // (combat.md §1 t101 leg3; integer //100 = truncating division).
    static int32_t powerRefill(int32_t powerMax, int32_t deltaDays);
    // walkLaw (S17 T1/T2, FUN_00049f54): d = |delta| * 0.00625 (1/160 world->
    // sugar); walk = min(d, moves); steps = max(1, x86round(walk)); if
    // power < steps: walk *= power/steps, steps = power; arrived = walk == d;
    // commit: pos += normalize(delta) * walk * 160 (the per-step
    // normalize*(walk/steps)*32.0*5.0 collapsed — quantizer NOT applied mid-
    // walk, INFERRED; snapped to the 32-grid on ARRIVAL only, S17 T3).
    // Returns steps burned; mutates pos/power/moves/arrived per the commit
    // law (param_2==1 equivalent: the sim always commits — mode-0 dry runs
    // are the engagement resolver's concern, t364/K6).
    static int32_t walkLaw(float pos[3], int32_t* power, int32_t* moves,
                           const float delta[3], bool* arrived);
    // x86 default-mode rounding (fistp round-half-to-even); C roundf is
    // half-AWAY and would differ on .5 ties.
    static int32_t x86Round(float v);

    // T-7 march + T-3 arrival. PUBLIC (t362): the march-spends-NEITHER law is
    // invisible at boundary observation — the per-sweep MOVES re-grant (0x412cf)
    // overwrites moves before any observation, exactly as in the vendor — so
    // the law is pinned at the seam itself (mutant: march decrementing
    // moves/power must fail here, not at advanceBoundary).
    void laneMarch(Ship& s, BoundaryReport& rep);

  private:
    struct RaceFocus { int race; uint32_t focus; };
    void sortShipList();                 // step (2), stable on +0x52
    // Per-kind dispatch. RETURNS the executor work status: 0 when no walk
    // committed (kind not walkable / no target triple — the vendor arms that
    // report status 0 and keep the driver's edi clear), nonzero (steps spent)
    // when a walk committed (driver `or edi,eax` -> repeat, t362 S6).
    int commitMove(Ship& s, BoundaryReport& rep);
    void landingAttempt(Ship& s, BoundaryReport& rep);  // T-6 (slot model is
                                                        // planet-side, t363:
                                                        // default = no free
                                                        // slot -> dwell+scatter)
    const SimLane* lane(int id) const;
    const SimStar* star(int id) const;
    // FUN_00049a34 kind-2 completion (t363; _wip_t363 S3d/S6 raw). Called on
    // an orderType-2 ARRIVAL inside commitMove (completion switch 0x4a333..
    // 0x4a33d verbatim). Admission FUN_000499f8: (laneStepX+laneStepZ > 0)
    // OR the species col-0x12 gate (NEVER-SEEN zero-witness, spec N4 — the
    // sim models the FORM via a per-sim flag speciesLaneTravel, default
    // false, never fired by shipped scenarios); AND the lane exists and is
    // NOT closed (byte[lane+0x23]&0x2 clear, S4 item 3 polarity). Admitted:
    // target := existing [+0x59] (the kind==3 leg at 0x49a44 is unreachable
    // from the sole caller — walk guard is kind 4 — so the sim does not
    // model it), kind := 5, lane-local x := 0, laneId := target, laneToB :=
    // (target == lane->a) — verbatim 0x49a85 `cmp esi,[ecx]` (lane[0] == the
    // A-end system object, S22 L1); the DIRECTION meaning of +0xa2 feeds the
    // NOT-CITED galactic-frame transform (spec G-d), so the laneMarch
    // endpoint mapping is the flagged contract choice, not a cited law.
    // False (state untouched) when denied.
    bool starArrivalComplete(Ship& s);

    // Owners present in the list, ascending (per-race loop order, ai-dossier
    // §1 "per-race AI loop" over the control table).
    std::vector<int> ownersOf() const;

    std::vector<Ship> ships_;
    std::vector<SimStar> stars_;
    std::vector<SimLane> lanes_;
    std::vector<RaceFocus> focus_;
    std::vector<SimDesign> designs_;   // index == cidx (setDesigns)
    int32_t driveAddend_ = 0;          // ds:0x77f6c stand-in (UNMEASURED)
    Lcg lcg_;
    int turn_ = 0;
    int rngDraws_ = 0;

    int draw() { ++rngDraws_; return lcg_.next(); }
};

}  // namespace ascend::game
