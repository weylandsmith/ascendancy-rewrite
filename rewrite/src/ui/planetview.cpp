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
    // F2: center = origin + col*(34,17) + row*(17,-34); the x/y cursors at
    // (row,col)=(0,0) read 0x6e=110 / 0x19a=410 (0x3bb5d / loop head).
    (void)size;  // the lattice is size-independent; size kept for call-site
                 // symmetry (the painter clamps validity via gridCellFor)
    return Pt{110 + col * 34 + row * 17, 410 + col * 17 - row * 34};
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

OrderCellBlock orderCellBlock(const ascend::game::Campaign& camp, int star,
                              int item, int cell) {
    // F3 build-checker legs in verbatim order (0x385b7..0x3870d).
    if (star < 0 || star >= int(camp.galaxy().stars.size()))
        return OrderCellBlock::None;
    const auto& ps = camp.planetAt(star);
    const int surf = ps.surfaceCells;
    if (cell < 0 || cell >= surf) return OrderCellBlock::None;  // 0x385b7 jae
    std::vector<char> active(size_t(surf), 0);
    bool own = false;
    for (size_t i = 0; i < ps.items.size(); ++i) {
        const int c = ps.itemCells[i];
        if (c == cell) own = true;
        if (c >= 0 && c < surf) active[size_t(c)] = 1;  // word+2 bit0 analog
    }
    if (own) return OrderCellBlock::None;               // 0x385ee jne
    if (item == 5 || item == 38) return OrderCellBlock::None;  // 0x385f6/ff
    const int size = ascend::game::Campaign::sizeClassFor(surf);
    if (size < 0) return OrderCellBlock::None;          // unknown geometry
    int row = 0, col = 0;
    if (!gridRowCol(camp.terrainTables(), size, surf, cell, &row, &col))
        return OrderCellBlock::None;
    const auto& tt = camp.terrainTables();
    // Four probes (row-1,col),(row+1,col),(row,col-1),(row,col+1); each:
    // slot exists AND ACTIVE -> REFUSE (0x386fe edi=1).
    const int dr[4] = {-1, 1, 0, 0}, dc[4] = {0, 0, -1, 1};
    for (int d = 0; d < 4; ++d) {
        const int n = gridCellFor(tt, size, row + dr[d], col + dc[d]);
        if (n >= 0 && n < surf && active[size_t(n)])
            return OrderCellBlock::ActiveNeighbour;
    }
    return OrderCellBlock::None;
}

}  // namespace ascend::ui
