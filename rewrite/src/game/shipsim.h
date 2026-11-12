// SPDX-License-Identifier: GPL-3.0-or-later

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
// non-goal). t364 (docs/re/_wip_t364.md C1..C9): the per-ship combat round
// (spec 5, setStance/volleyTail/commitShot/engageRound) — cited gates and
// absorb law only; handler-1/2/special effects remain K9 reference scope.

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
    int32_t special1 = 0;        // +0x4a (file Special1; combat.md S2f(c)) —
                                 // the ONLY t364 consumer is the gizmo-0x2f
                                 // damage override 0x4bb40 (Myrmidonic
                                 // Carbonizer damage 20, gizmos.txt row 47)
    bool upkeepGate = false;     // w16 +0x33 bit 0x20 (TOGGLEABLE per the
                                 // vendor flag table, gizmos.md §1) — MEASURED
                                 // true on EXACTLY rows 10..15, all cat 1
    bool targetShip = false;     // w16 +0x33 bit 0x0 (GZ_TARGETSHIP, gizmos.md
                                 // §1 flag table) — the gun handler's engage-
                                 // flag leg ANDs it in at 0x4bae6..0x4baf3;
                                 // ALL 10 cat-0 file rows carry bitpos 0
                                 // (gizmos.txt re-measured t364), so the
                                 // default for a gun row is true
    bool targetLane = false;     // w16 +0x33 bit 0x2 (GZ_TARGETLANE, gizmos.md
                                 // §1 flag table; MEASURED set on RAM row 60
                                 // flags=0x0002 = Lane Magnetron, t377
                                 // design-row readout scripts/r377_design_rows
                                 // .py). C2 CORRECTION (t377): the magnetron
                                 // commit test 0x4cbd4 tests bit0 ONLY — this
                                 // flag is OR-ed into the return word as a
                                 // FLAG, not a gate; its consumers are
                                 // elsewhere (unbanked, do not invent).
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

    // ---- t364 COMBAT-ROUND fields (docs/re/_wip_t364.md S1/C1, S3) --------
    // +0x62 dispatcher gate: 0 -> 0x49f28 routes to movement bookkeeping,
    // 1 -> routes to the gizmo-use dispatcher 0x4a360 (stance setter store
    // 0x4a591; resolver Leg A CLEAR store 0x42d9c). Distinct from act (+0x5d,
    // the decider's act) — the vendor keeps two bytes, so does the sim.
    uint8_t dispatcherGate = 0;
    // +0x63 ACTIVE slot (vendor stores the slot POINTER; the sim keeps the
    // index, -1 == none, the Leg A clear value). The volley writes it for
    // EVERY cat-0 slot it scans (0x4a5ee stores before the slot call, result
    // ignored) — after a volley it holds the LAST cat-0 slot scanned, and
    // the mode-1 commit edges fire THAT gun (_wip_t364 C5 quirk, verbatim).
    int activeSlot = -1;
    // +0x68 engagement target (vendor: guest-physical objective/ship pointer
    // written by the stance setter 0x4a574/0x4a57d/0x4a586 and Leg A
    // 0x42dbd). Sim-level ship id; -1 none. NOT the walk target — the chase
    // seam (type-1 ptr-deref walk toward +0x68) is not modelled (t365).
    int fireTarget = -1;
    // Sim-level stand-in for the [+0x59] system-object identity the K1 gate
    // compares (0x4b997). 0 == no system; two ships engage iff nonzero-equal.
    uint32_t systemId = 0;

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
    // ---- t379 COUNT WINDOW (memory-array law; witness + measurement
    // docs/re/_wip_t379.md S1/S4/S6: banks bank-play-20261111(-late) 40 saves
    // + production ring 20 saves, law holds 60/60). The vendor's ship array
    // is NOT compacted on death: the C4 finalizer marks the corpse IN PLACE
    // (owner 0xffff, kind 0, name NUL-stamped, act 0) and the count word
    // DECREMENTS by one. MEASURED LAW: count == full-array live census (both
    // banks: 41/41 then 40/40), so the count-based walk range(0,count) —
    // r1_slot.ship_array_law / FUN_00022304 — must skip the corpse and still
    // reach every live record; the observable consequence is the ORPHAN:
    // after an in-window death the highest-index live record falls OUTSIDE
    // the window byte-identical (s40 'Intil-Za', sha256-verified untouched).
    // The sim mirrors the law with TWO orderings, never conflated:
    //   ships()      = the SORTED list (+0x52 comparator 0x40eb4) — the
    //                  executor/carrier walks; a corpse is skipped there by
    //                  the owner>=0 filters, not by the window;
    //   countWindow()= the ARRAY-order window (id == record index law A2,
    //                  fromRecord: s.id = r.slot) — memory enumeration;
    //                  contains corpses by construction, may MISS live
    //                  ships whose id >= liveCount (the orphan).
    // liveCount() is the CENSUS MIRROR (count word == live census, measured
    // 60/60 — a derived count, never the vector size: corpses stay in the
    // vector exactly as they stay in RAM).
    int liveCount() const;
    std::vector<const Ship*> countWindow() const;
    // Live records outside the count window (measured: s40 at t1254; exactly
    // one per in-window death since count stays the live census).
    std::vector<const Ship*> orphanedShips() const;
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
    // ---- t378 DESTINATION-TRIPLE ATOMICITY (witness M3, ships.md S64 +
    // work/r1/t370_slot_events_all.txt). The sim-level stand-in for the
    // player issuer of an EMPTY-SPACE destination order: every witnessed
    // issue (4 in-window ships + s14's pre-window order) writes order TYPE
    // (+0x67) := 3 AND the destination triple (+0x6c) IN ONE FRAME — kind
    // (+0x58) is NOT part of this pair (stays 4 at every issue). The vendor
    // issuer's store leg was never disassembled (S64 honest negative
    // neg-(a)); the ATOMIC PAIR is the measured field-level fact, so the
    // seam admits no torn state: accept writes both fields, refuse writes
    // NOTHING (returns false — the sim-level no-target sentinel; the cited
    // 0xffff sentinel lives on the owner half at the 0x24a00 clear, not on
    // the order fields). Two-click x/y-then-z stays CADENCE-BLIND
    // (adjacent XY->Z census = 0): NO two-step internal model (N8).
    bool issueDestination(int shipId, float x, float y, float z);
    // The witnessed ORDER-END leg (s14 Stainer 00:24:02: type 3->0 with
    // trip := (0,0,0) same frame): iff orderType == 3, clear BOTH the type
    // and the triple atomically. Object orders (type 1/2) never own +0x6c —
    // refuse (state untouched).
    bool clearDestination(int shipId);
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

    // ---- t364 PER-SHIP COMBAT ROUND (spec §5 K1..K10; verbatim windows +
    // this session's CORRECTIONS C1..C5: docs/re/_wip_t364.md; resolver
    // region combat.md S2k; laws K1..K8 cited there). Naming law: the vendor
    // resolves an engagement in TWO modes — mode-0 PROBES (volley loop, AI
    // paths: compute flags, charge and apply NOTHING — C3) and mode-1
    // COMMITS (the only two edges 0x25560/0x25570, player-command-exec). The
    // sim exposes the same split; engageRound composes the resolver legs.
    struct EngagementReport {
        int shooter = -1;          // Leg B winner (first-eligible, list order)
        int carrier = -1;          // Leg A winner (first kind-4 + gizmo 0x49)
        int handler = -1;          // +0x67 value the commit ran (0 gun /
                                   // 1 shield-family / 2 drive / 5 special;
                                   // -1 no commit ran). C1: the HANDLER is
                                   // selected by +0x67, not the gizmo cat.
        int shots = 0;             // mode-1 hit calls that reached 0x4b740
                                   // (gates passed; damage may still be 0)
        int shieldAbsorb = 0;      // sum applied to [+0x90] this round
        int hullAbsorb = 0;        // sum applied to [+0x8c] this round
        int destroyed = -1;        // victim slot on death (C4 finalizer ran)
        int flags = 0;             // last hit-path return (bit2 shield
                                   // overflow, bit4 lethal-clamp, bit0x10
                                   // zero-damage skip) — C3: probes set these
                                   // WITHOUT touching record state
        bool legACommitted = false;   // carrier engagement state written
    };
    // Stance setter FUN_0004a55c VERBATIM (0x4a55c..0x4a601 — the volley loop
    // lives INSIDE it): refuses POWER==0 (no state change at all — the ret at
    // 0x4a56f precedes every store); else [+0x62]:=1 (0x4a591) and the
    // arg->+0x67 HANDLER map 0->2, 1->1, 2->1, 3->0 (banked "arg2->0"
    // SUPERSEDED, _wip_t364 C2), [+0x68]:=target, then runs the volley tail.
    // Returns the vendor's truthiness: true iff the tail's dispatch loop
    // remembered a slot (edi != 0 — Leg B's test eax,eax).
    bool setStance(int shipId, int arg, int targetShipId);
    // Companion slot scan FUN_0004a604 VERBATIM: -1 (the vendor's ELIGIBLE
    // sentinel) iff some slot i < invCap has design cat==0 AND (design
    // numUses==0 OR slot use != 0); 0 when none (Leg B's test eax,eax reads
    // -1 as pass, 0 as fail — it is a boolean, NOT a slot index).
    int companionScan(const Ship& s) const;
    // Volley loop 0x4a5c1..0x4a5fc VERBATIM (always mode 0 — 0x4a5ec
    // xor edx,edx): walk slots i < invCap in STORED ORDER, skip 0xff, gate
    // design cat==0, write [+0x63] := slot (per slot, BEFORE the call,
    // whatever it returns), run the dispatcher on it (ammo law
    // 0x4a373..0x4a397; the gun handler's engage flag is the only banked
    // bit0 reporter). Returns the last slot whose dispatch returned bit0
    // (vendor edi), -1 none. PUBLIC (t364): the "volley leaves activeSlot on
    // the LAST cat-0 scanned, not the last HIT one" quirk (C5) is invisible
    // through setStance — the pins need the seam.
    int volleyTail(Ship& s);
    // Dispatcher FUN_0004a360 + gun handler 0x4b8e4 + hit path 0x4b740 on
    // the ship's ACTIVE slot (+0x63). mode must be 0 or 1 (K6: the vendor's
    // only mode-1 edges are the player-command-exec calls; AI passes 0).
    // mode-0: gates + flags + hypothetical absorb ONLY — APPLY (0x4b87a) and
    // the death call are BOTH behind the mode==1 cmp (C3), so nothing lands.
    // mode==1: DEC slot use (NumUses != 0), run the +0x67 handler, charge
    // power -= MIN(design[+0x36], power) (0x4c614), apply shield-then-hull
    // clamped absorb, hull < 1 -> destroy (C4: owner := -1, kind := 0, act
    // := 0 — the 0x249b4 finalizer; the corpse's travel re-issue legs are
    // moot after the finalizer, planet-slot release is planet-side).
    // Returns the hit-path flags (or the handler result for non-gun +0x67).
    EngagementReport commitShot(int shipId, int mode);
    // One engagement resolution (S2k shape, this side's view — K10: the
    // caller-side array is OWNER-RACE FILTERED, return fire is a SEPARATE
    // run; call it once per side). Leg A (carrier) runs unless
    // objectivePlanetShielded (the ACTIVE Ship/Orbital-Shield skip gate,
    // operands are planet state — caller supplies); Leg B picks the shooter
    // FIRST-ELIGIBLE in list order (kind 4, companionScan != -1... the
    // vendor's != 0 test on eax: -1 fails, index >= 0 passes — see impl note)
    // and setStance(ship,1,target) on the WINNER ONLY (the halt test
    // [esp+0x2d0] != 0 at 0x42ded stops scanning once a winner is stored),
    // then commitShot(shooter, mode). K1 same-system gate is enforced inside
    // the gun handler, verbatim (kind 4 both sides + same systemId).
    EngagementReport engageRound(int race, int targetShipId,
                                 bool objectivePlanetShielded, int mode);
    // ---- t377R MAGNETRON USE-SITE (t377 evidence S2 C1..C8 + S3 landing
    // contract docs/re/_wip_t377.md; witnesses ships.md S64 M1) -------------
    // Dispatcher-entry composition for the orderType-2 (handler 0x4ca50)
    // path on the ship's ACTIVE slot (+0x63), magnetron leg (cidx 0x3c) of
    // the kind-2 tail case tree. The entry 0x4a360 does NOT test [+0x62]
    // (that gate lives in the caller FUN_00049f28) and derefs [+0x63]
    // directly: the sim's activeSlot < 0 stands in for the null deref —
    // named divergence, refuse with zero state change.
    // Gate ORDER is the law (verbatim, _wip_t377 S3):
    //   C7 prologue 0x4a373..0x4a397: design numUses==0 -> unlimited, no
    //     DEC; slot use==0 -> BLOCK, handler never runs; else DEC mode-1-
    //     ONLY, BEFORE the handler, UNGATED by any handler-side gate — a
    //     gate-failed use STILL consumes a charge (zero-witness, flagged).
    //   C1 range gate 0x4cb76..0x4cb95: FAIL iff dist < Range*32 (TOO-CLOSE
    //     rejected — t185's inverted reading refused witness M1; the
    //     correction is witness-verified); Range==0 skips the check (je).
    //   C2 0x4cbd4: bit0 = affordable(design cost <= power, 0x4ca90) AND
    //     rangeOK — the ONLY commit gate; bit1 = design TARGETLANE is a
    //     RETURN FLAG, not a gate (consumers elsewhere, unbanked).
    //   C3 charge 0x4cbe3: power -= min(design power, power) (entry-
    //     computed 0x4ca89; M1 90->80 = gizmos.txt row 60 'Power 10' EXACT).
    //   tail case tree cidx==0x3c leg 0x4cd0d..0x4cd43: FUN_000220a8 target
    //     gate (sim surrogate: kind==InSystem AND targetStar resolves —
    //     M1's kind byte stayed 4; other kinds = named non-goal), then
    //     placement FUN_00021f58: star triple + (0,-200,0) + TWO LCG draws
    //     %200 on x/z, stored via FUN_00049aa8 = quantizer snapGrid on all
    //     THREE axes (M1 landing ON-grid), kind transient 5 then 4 (0x2202f;
    //     the 5 is invisible from outside — no boundary between the stores).
    //     Slot rebuild 0x4cd24..0x4cd39 maps the vendor slot POINTER to the
    //     stored index — identity in the sim's index space — then clearSlot
    //     (M1: ring slot REMOVED same event = SINGLE-USE consumption).
    // mode-0 (AI/probe): exits at 0x4cbcd BEFORE any store — no DEC, no
    // charge, no placement; flags + cost are reported WITHOUT landing.
    // HONEST NEGATIVES carried: which star M1 used is UNRECONCILED (S64
    // neg-(a)) — the sim takes the caller's targetStar; pins assert the
    // placement FORM (star+jitter snapped) and the delta class (instant, no
    // walk), NEVER vendor coordinates. A committed use whose target does not
    // resolve has ALREADY paid DEC+charge (byte order: both precede the
    // case tree) — unwitnessed composition consequence, flagged.
    struct MagnetronReport {
        bool ranHandler = false;   // ammo law passed (prologue did not block)
        int32_t cost = 0;          // min(design power, power) at entry (C3)
        int flags = 0;             // return word: bit0 affordable&&rangeOK,
                                   // bit1 TARGETLANE (C2 — flag, not gate)
        bool committed = false;    // mode-1 AND bit0 (0x4cbd4)
        bool placed = false;       // magnetron leg ran placement + clearSlot
    };
    MagnetronReport useMagnetron(int shipId, int mode);
    // System-object id for the K1 gate (vendor [+0x59] star-block index law,
    // 0x49dbd `edx*39*32 + 0x13bc5` re-confirmed in the death path this
    // session). Ships in the sim share a system iff systemId matches; the
    // caller maps star ids onto it. 0 == no system (gates deny).
    void setSystemId(int shipId, uint32_t id) {
        if (Ship* s = findShip(shipId)) s->systemId = id;
    }
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
    // normalize*(walk/steps)*32.0*5.0 collapsed), THEN the quantizer g=32 on
    // all three axes UNCONDITIONALLY — t380 STATIC CORRECTION (_wip_t380
    // S1c/S1d): the quantizer call 0x4a2cf is on the straight line and the
    // quantized copy-back 0x4a2d9 is gated only by mode==1, never by
    // arrival. Returns steps burned; mutates pos/power/moves/arrived per the
    // commit law (param_2==1 equivalent: the sim always commits — mode-0 dry
    // runs are the engagement resolver's concern, t364/K6; the vendor's own
    // dry-run callers 0x15cc5/0x15df0 pass edx=0 and store nothing).
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

    // Gun handler engage-flag block 0x4bad4..0x4bafc (in-range incl. the
    // range==0 unlimited-leg, self-exclusion, GZ_TARGETSHIP) — shared by the
    // volley tail (bit0 of the dispatch result) and commitShot (the gate
    // before charge/damage). Cites its own addresses; see _wip_t364 C9.
    bool gunEngageFlag(const Ship& s, const SimDesign& d) const;

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
