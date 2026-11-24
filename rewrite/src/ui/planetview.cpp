// SPDX-License-Identifier: GPL-3.0-or-later

// t406 PLANET VIEW + PROJECT-SET law — see planetview.h for the citations.
// Pure data + gate math (no SDL), compiled into run_tests (statuslist.cpp
// precedent). Working notes: docs/re/_wip_t406.md.
#include "ui/planetview.h"

#include <cstdlib>  // std::abs (t418b tile hit-test)

#include "game/economy.h"  // requiresAvailable (OQ-014 CLOSED)
#include "ui/planetwin.h"  // planetGaugesFor (t276 gauge wiring)
#include "ui/statuslist.h"  // statusLine1 / statusDays (shared assembly)

namespace ascend::ui {

namespace {
// The 0x388ec domain gate: cmd0 rejects item >= 39 (cmp 0x27; jae reject).
inline bool inOrderDomain(int item) { return item >= 0 && item < 39; }
}  // namespace

PlanetView planetViewFor(const ascend::game::Campaign& camp, int star,
                         const std::string& name) {
    PlanetView v;
    const auto& g = camp.galaxy();
    if (star < 0 || star >= int(g.stars.size())) return v;
    const auto& ps = camp.planetAt(star);
    const int sizeIdx = ascend::game::Campaign::sizeClassFor(ps.surfaceCells);
    v.title = statusLine1(name, sizeIdx, ps.terrainRow);
    v.pop = int(ps.pop);                       // +0x42 analog
    v.used = camp.usedPopFor(star);            // +0x4c analog
    v.cap = camp.popCapAt(star);               // +0x4a analog
    const PlanetGauges gsg = planetGaugesFor(camp, star);
    v.res = gsg.res; v.ind = gsg.ind; v.pros = gsg.pros;
    v.pendingItem = camp.pendingItemFor(star);
    v.noProject = v.pendingItem < 0;
    v.noFreePopulation = (v.pop == v.used);    // the 0x508da predicate
    if (v.pendingItem >= 0) {
        if (const auto* pi = camp.planetItem(v.pendingItem))
            v.days = statusDays(pi->cost, camp.buildAccFor(star),
                                camp.channelWordsFor(star).ind);
    }
    return v;
}

std::vector<ProjectOption> projectOptionsFor(
    const ascend::game::Campaign& camp, int star) {
    // LIST MEMBERSHIP (planetview.h header): table order, REQUIRES-gated
    // (income-law S4), domain < 39 (0x388ec). Free-pop is an ORDER gate,
    // not a list filter — the vendor shows the row and the order rejects.
    std::vector<ProjectOption> out;
    if (star < 0 || star >= int(camp.galaxy().stars.size())) return out;
    const int n = camp.planItemCount();
    for (int id = 0; id < n && id < 39; ++id) {
        const auto* pi = camp.planetItem(id);
        if (!pi) continue;
        if (!ascend::game::requiresAvailable(pi->reqByte, camp.techCountTotal(),
                                             camp.playerTechs()))
            continue;
        out.push_back(ProjectOption{id, pi->name, pi->cost});
    }
    return out;
}

bool projectOrderable(const ascend::game::Campaign& camp, int star, int item) {
    // cmd0 gates (1)(2)(3) — verbatim order of the fn 0x38840 legs.
    if (!inOrderDomain(item)) return false;                       // 0x388ec
    if (camp.pendingItemFor(star) >= 0) return false;             // 0x388e2
    const auto* pi = camp.planetItem(item);
    if (!pi) return false;
    // 0x388f7: WORD[+0x42] - WORD[+0x4c] >= UPOP  (free population)
    const int freePop = int(camp.planetAt(star).pop) - camp.usedPopFor(star);
    if (freePop < pi->upop) return false;
    return true;
}

std::optional<int> projectRowFor(Pt p, int first) {
    if (!inRect(kProjectListRect, p)) return std::nullopt;
    const int rel = p.y - (kProjectListRect.y0 + 2);  // 2 px inner padding
    if (rel < 0) return std::nullopt;
    const int i = rel / kProjectRowPitch;
    if (i < 0 || i >= kProjectVisibleRows) return std::nullopt;
    return first + i;
}

// ---- t418b SURFACE TILE GRID ----------------------------------------------
// Citations: header block + docs/re/_wip_t418.md F1/F2/F3.

int gridCellFor(const ascend::game::TerrainTables& tt, int size, int row,
                int col) {
    // 0x395dc..0x39647: row in [0,15), col >= 0, B <= col < B+C, else 0xffff
    // (here -1). cumWidth = SUM GridC[size][0..row-1] (0x395f5..0x39612).
    if (size < 0 || size >= 5 || row < 0 || row >= 15 || col < 0) return -1;
    const int B = tt.rowOffset[size][row];
    const int C = tt.rowWidth[size][row];
    if (col < B || col >= B + C) return -1;  // 0x3962b jl / 0x3963b jge
    int cum = 0;
    for (int r = 0; r < row; ++r) cum += tt.rowWidth[size][r];
    return cum + col - B;  // 0x3963f..0x39647
}

bool gridRowCol(const ascend::game::TerrainTables& tt, int size,
                int surfaceCells, int cell, int* row, int* col) {
    // FUN_0003965c VERBATIM (work/r331_disasm.txt 0x39691..0x396bd): entry
    // gate cell < WORD[rec+0x18] else 0xffffffff; per row: col candidate
    // edi = cell + B[row] - cum (0x3969a..0x396a6), then cum += C[row] and
    // BREAK at the first row where cum + C > cell (0x396b0 add eax,esi /
    // 0x396b2 cmp ax,bx / 0x396b5 ja). THE LOOP TEST IS cum+C, NOT cum+B+C
    // (B enters only the col formula) — the t418 WIP F1 shorthand "cum+B+C"
    // was a misparse; with B>0 it can land invalid cols (size-2 cell 14:
    // the buggy walk breaks at row5 and lands col 8, OUTSIDE row 5's valid
    // cols 3..7; the vendor lands row6 col4). Minimality gives
    // cum <= cell < cum+C at the break, so col = cell-cum+B is always in
    // [B, B+C).
    if (size < 0 || size >= 5 || cell < 0 || cell >= surfaceCells)
        return false;
    int cum = 0, r = 0;
    for (; r < 15; ++r) {
        const int C = tt.rowWidth[size][r];
        if (cum + C > cell) break;
        cum += C;
    }
    if (r >= 15) return false;  // unreachable for cell < surfaceCells on a
                                // well-formed grid; refuse-not-crash
    *row = r;
    *col = cell - cum + tt.rowOffset[size][r];
    return true;
}

Pt tileCenter(int size, int row, int col) {
    // tPL-V1 F1/F3 (supersedes the t418 F2 shorthand, which TRANSPOSED the
    // two cursors). Vendor record 0x3c211..0x3c274: the field carrying the
    // SYMMETRIC +-0x22 offsets is X (68-wide diamond), the field carrying
    // 0/+0x11/+0x22 is Y (34 tall):
    //   X = 410 + 34*col - 34*row ; Y(anchor top vertex) = 110 + 17*col +
    //   17*row ; centre = anchor + (0,17). col step (34,17), row step
    //   (-34,17): |det| = 1156 == diamond area (68*34/2) => EXACT edge-to-
    //   edge tiling, NO gaps (the old law's |det| = 1445 gave 80% coverage
    //   = the D26 "rows have gaps" complaint). Witness on the VENDOR
    //   capture t254/02_planet_detail.png: 100.0% edge support for THIS law
    //   vs 26.0% for the old one (scripts/tplv1_lattice_witness.py).
    (void)size;  // the lattice is size-independent; size kept for call-site
                 // symmetry (the painter clamps validity via gridCellFor)
    return Pt{410 + col * 34 - row * 34, 127 + col * 17 + row * 17};
}

int tileEdgePaletteIndex(int cellClass) {
    // tPL-V1 F2 EDGE-COLOUR selector, paint body 0x3bbd6..0x3bc52: EXACT
    // compares on the slot class byte (BYTE[rec+0x10]+0): 0 -> 0 (black,
    // 0x3bc00), 2 -> 117 red (0x3bc16), 3 -> 146 green (0x3bc2e), 4 -> 255
    // blue (0x3bc46), default 12 white (0x3bbdc). game.pal converted
    // (t398 law): 12 -> (203,203,203), 117 -> (190,44,16), 146 -> (44,195,
    // 12), 255 -> (0,0,255) — the D26 list white/red/green/blue + black.
    // Exact-equality is the law: a rock-flagged byte (1|8 = 9) takes the
    // WHITE default, and so does 0xff (empty item) — the compares run on
    // the raw byte. The companion grey-ramp FILL selector (7/8/8/9/10/13)
    // is gated by widget byte 0x18b bit0 (0x3bbcb) and drew ZERO pixels in
    // the witness — seam TPLV1-A; the fill stays the cited uniform 0x96.
    switch (cellClass) {
        case 0: return 0;
        case 2: return 117;
        case 3: return 146;
        case 4: return 255;
        default: return 12;
    }
}

int tileHitFor(const ascend::game::TerrainTables& tt, int size,
               int surfaceCells, Pt p) {
    // F2 hit-test |dx|/34 + |dy|/17 <= 1 (integer form 17|dx|+34|dy| <= 578)
    // over the VALID cells only. Diamonds touch edge-to-edge, so a strict
    // hit is unique; boundary ties resolve to the nearest centre [port law].
    int best = -1, bestD2 = 1 << 30;
    for (int row = 0; row < 15; ++row) {
        const int B = tt.rowOffset[size][row];
        const int C = tt.rowWidth[size][row];
        for (int col = B; col < B + C; ++col) {
            const Pt c = tileCenter(size, row, col);
            const int dx = p.x - c.x, dy = p.y - c.y;
            if (17 * std::abs(dx) + 34 * std::abs(dy) > 578) continue;
            const int d2 = dx * dx + dy * dy;
            if (d2 < bestD2) { bestD2 = d2; best = gridCellFor(tt, size, row, col); }
        }
    }
    (void)surfaceCells;  // valid cells ARE [0,surfaceCells) for well-formed
                         // grids (grid C row sums == +0x18, OQ-014 census);
                         // kept in the signature for the caller's guard
    return best;
}

// ---- tPL-B1b PLACEMENT BLOCK (was t418b orderCellBlock, INVERTED) ---------
// Chain order verbatim from checker FUN_0003830c (citations in the header
// F3 block + docs/re/_wip_tPLB1.md F7/F9). EDI semantics: 0x38444 resets
// EDI=0 for the placement region; return 0x38706 yields -1 (legal) iff
// EDI != 0 — the zeroing arms are the vetoes.

namespace {
// ds:0x73e3c == 22 surface-item rows [verified RAM census 4/4, OQ-014
// ledger + income-law.md S4 XOR law verbatim].
constexpr int kSurfaceItemCount = 22;
constexpr int kRingSlots = 10;  // slot-array cap +0x1a == cells+10 (OQ-014)
}  // namespace

PlacementBlock placementBlock(const ascend::game::Campaign& camp, int star,
                              int item, int cell) {
    if (star < 0 || star >= int(camp.galaxy().stars.size()))
        return PlacementBlock::None;
    const auto& ps = camp.planetAt(star);
    const int surf = ps.surfaceCells;
    if (item == 0xff) return PlacementBlock::None;  // demolish exempt (S4)
    if (cell < 0 || cell >= surf + kRingSlots)
        return PlacementBlock::None;  // 0x3843a slot-cap early exit
    const auto* pi = camp.planetItem(item);
    const bool bit2 = pi && (pi->flags & 0x4);  // build-on-top class (S4)
    // Occupancy + active census (slot byte0 / word+2 bit0 analogs; the port
    // stores ACTIVE items only, parallel itemCells).
    bool own = false;
    std::vector<char> active(size_t(surf > 0 ? surf : 0), 0);
    for (size_t i = 0; i < ps.items.size() && i < ps.itemCells.size(); ++i) {
        const int c = ps.itemCells[i];
        if (c == cell) own = true;
        if (c >= 0 && c < surf) active[size_t(c)] = 1;
    }
    // F10 GRANT ACCUMULATOR: 0x38444 `xor edi,edi` resets EDI=0 at the
    // placement-region entry; the region's `mov edi,-1` legs (A 0x38446
    // bit0/race-state, B 0x38493 byte0!=0/demolish/bit2) GRANT and the
    // `xor edi,edi` legs VETO. Rule B is ALWAYS granted for observed play
    // (t43 barren-build census 263/892 == terrain rate; the picker filters
    // by this checker) — so the port implements only the vetoes. THERE IS
    // NO OCCUPIED VETO: occupancy lives in word+2 bit0, read by own-active
    // 0x385ee (a skip) and rules E/F — never as a refuse (F10 consequence
    // 1; t43's empty-cell law is a PICKER law, the port's completion
    // re-picks the cell).
    (void)own; (void)bit2;
    // XOR 0x384db, ONLY item < 31 (0x384e0 cmp dl,0x1e ja): booleans EQUAL
    // pass (0x38515 je skips the veto), DIFFER zero EDI -> refuse.
    if (item < 31) {
        const bool cellSurface = cell < surf;         // 0x384e5 setb
        const bool itemSurface = item < kSurfaceItemCount;  // 0x384f5 setl
        if (cellSurface != itemSurface) return PlacementBlock::SurfaceVsRing;
    }
    // ROCK 0x38519: veto iff (byte0 bit3) != (item == 38) — Xeno Dig is
    // legal ONLY ON ROCK (dig arm 0x38546 sete), normal items refuse on
    // rock. Ring slots skip (T36 forces class 1 == dig-equal reading).
    if (cell < surf && cell < int(ps.cellClasses.size())) {
        const bool rock = ps.cellClasses[size_t(cell)] & 8;
        if (rock != (item == 38)) return PlacementBlock::RockMismatch;
    }
    // 0x38554 item 36 Terraforming: requires byte0==0 (barren) AND
    // byte1==0xff (empty) AND a surface cell (ring class 1 vetoes).
    if (item == 36) {
        const bool barren = cell < surf && cell < int(ps.cellClasses.size()) &&
                            ps.cellClasses[size_t(cell)] == 0;
        if (!barren || own) return PlacementBlock::TerraformSite;
    }
    // ADJACENCY 0x385b7..0x386fc. Ring cells skip (0x385b7 jae).
    if (cell >= surf) return PlacementBlock::None;
    if (own) return PlacementBlock::None;  // 0x385ee own-ACTIVE jne-exit
    if (item == 5 || item == 35) return PlacementBlock::None;  // 0x385f6/ff
    const int size = ascend::game::Campaign::sizeClassFor(surf);
    if (size < 0) return PlacementBlock::None;  // unknown geometry
    int row = 0, col = 0;
    if (!gridRowCol(camp.terrainTables(), size, surf, cell, &row, &col))
        return PlacementBlock::None;
    const auto& tt = camp.terrainTables();
    // FOUR probes (0x38624..0x38661 call order: row+1, row-1, col-1, col+1).
    // An existing ACTIVE neighbour exits via `jne 0x386fe` WITHOUT running
    // 0x386fc `xor edi,edi` => ACTIVE neighbour is LEGAL. All four
    // inactive/absent => 0x386fc zeroes EDI => REFUSE. (The t418b port had
    // this inverted — tPL-B1 F5; flipped here per the raw bytes.)
    const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, -1, 1};
    for (int d = 0; d < 4; ++d) {
        const int n = gridCellFor(tt, size, row + dr[d], col + dc[d]);
        if (n >= 0 && n < surf && active[size_t(n)])
            return PlacementBlock::None;  // active neighbour: jne-exit, legal
    }
    return PlacementBlock::NoActiveNeighbour;  // 0x386fc xor edi,edi
}

bool ordersWithoutCell(const ascend::game::Campaign& camp, int item) {
    // FLAG bit1 (0x3b3f5 `and al,0x2` + 0x38a5a cmd2 skip): the cell-less
    // items {31,32,33,34,37} order with edx=0xffff (tPL-B1 F2 census).
    const auto* pi = camp.planetItem(item);
    return pi && (pi->flags & 0x2);
}

}  // namespace ascend::ui
