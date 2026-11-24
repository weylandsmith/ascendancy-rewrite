// SPDX-License-Identifier: GPL-3.0-or-later

// tPL-B2 indicator-popup law — citations in indpopups.h.

#include "ui/indpopups.h"

#include <cstdio>

#include "ui/statuslist.h"  // statusSizeWord / statusTypeWord

namespace ascend::ui {

int countdownDays(int target, int acc, int rate) {
    // FUN_0x47010 verbatim (0x47010..0x47034): rate<=0 -> 0xffff; else
    // eax = (target-acc-1)/rate + 1 (signed idiv, sar-sext), clamped >= 1.
    if (rate <= 0) return -1;
    const int d = (target - acc - 1) / rate + 1;
    return d < 1 ? 1 : d;
}

Rect indicatorPopupRect(Rect pr) {
    // 0x3dbe5..0x3dc34: wrec[8]+10 / wrec[0xc]+10 .. wrec[8]+0x145 /
    // wrec[0xc]+0xcf (the widget record's X0/Y0 are its rect origins).
    return Rect{pr.x0 + 10, pr.y0 + 10, pr.x0 + 0x145, pr.y0 + 0xcf};
}

std::vector<PopupLine> indicatorLines(const std::string& planetName,
                                      const IndicatorContent& c) {
    std::vector<PopupLine> out;
    char buf[256];
    // L-D 0x3e4db: gated on +0x72 (nameWord) != 0.
    if (c.nameWord) {
        // getter(99) "%s %s: %d per day" (planet+0x24, +0x72, u16 +0x7e).
        std::snprintf(buf, sizeof(buf), "%s %s: %d per day",
                      planetName.c_str(), c.nameWord, c.perDay);
        out.push_back({buf, 0xf});
    }
    // L-E 0x3e530: gated on +0x6e != 0 (the indicator sets +0x6e=-1 iff it
    // has a countdown subject).
    if (c.nameWord && c.subject && c.verb) {
        if (c.days < 0) {
            // 0x3e545 sentinel: sprintf(+0x62 fmt, +0x5a subject).
            if (c.noProgress) {
                std::snprintf(buf, sizeof(buf), c.noProgress, c.subject);
                out.push_back({buf, 0x50});
            }
        } else {
            // getter(100) + plural pair getter(28)""/getter(29)"s" iff
            // days==1 (0x3e560..0x3e576 cmp $0x1).
            std::snprintf(buf, sizeof(buf), "%s will %s in %d day%s.",
                          c.subject, c.verb, c.days, c.days == 1 ? "" : "s");
            out.push_back({buf, 0x50});
        }
    }
    return out;
}

std::vector<PopupLine> fullInfoLines(const PlanetIdentity& id) {
    std::vector<PopupLine> out;
    char buf[256];
    // L0 0x3e2d3: the raw NAME push (hold 0xf).
    out.push_back({id.name, 0xf});
    // L1 0x3e2ea: getter(94) "%s %s Planet". cdecl pushes are right-to-
    // left: ebx=0x74540[type] pushed first (last arg), ecx=0x7452c[size]
    // second (first arg) -> fmt takes (sizeWord, typeWord) — the same
    // (size, type) order and the same r402-censused word tables as
    // statusLine1 (sizeIdx=sizeClassFor, typeIdx=terrainRow).
    const char* sw = statusSizeWord(id.sizeIdx);
    const char* tw = statusTypeWord(id.typeIdx);
    if (sw && tw) {
        std::snprintf(buf, sizeof(buf), "%s %s Planet", sw, tw);
        out.push_back({buf, 0x3c});
    }
    // L2 0x3e3cc: getter(96) "Owned by |%d|%s" (owner name buffer, chip
    // code, hold 0x5a). SEAM TPLB2-B: the port renderer has no inline chip
    // directive, so the text keeps "Owned by " + the name; the chip code
    // (raceChipCode(raceIdx)) is computed here so the pin can bind it.
    {
        const int chip = raceChipCode(id.chipRaceIdx);
        (void)chip;  // render seam; pinned via raceChipCode in tests
        const std::string shown =
            id.owner < 0 ? std::string("No One") : id.ownerName;
        std::snprintf(buf, sizeof(buf), "Owned by %s", shown.c_str());
        out.push_back({buf, 0x5a});
    }
    // L3 0x3e432: getter(97) "Maximum Population  %d" (TWO spaces) u16+0x4a.
    std::snprintf(buf, sizeof(buf), "Maximum Population  %d", id.maxPop);
    out.push_back({buf, 0x78});
    // L4 0x3e47a region: getter(98) "Self Managed" iff owner==player and
    // the governor word is 0xffff (port analog governor == -1).
    if (id.owner == ascend::game::kPlayer && id.selfManaged)
        out.push_back({"Self Managed", 0x96});
    return out;
}

std::vector<PopupLine> popupLinesFor(const ascend::game::Campaign& camp,
                                     int star, PlanetPanel panel,
                                     const std::string& planetName) {
    if (star < 0) return {};
    const auto& ps = camp.planetAt(star);
    const auto cw = camp.channelWordsFor(star);
    IndicatorContent c;
    switch (panel) {
        case PlanetPanel::PlRes: {
            // KEY 0 body 0x3dc61: name "Research", rate = +0x46 analog.
            c.nameWord = "Research";
            c.perDay = cw.res;
            const int row = camp.queuedTechFor(ascend::game::kPlayer);
            if (row >= 0) {
                // Word[0x76492+2r] != 0xffff analog: a queued topic exists.
                const auto* tree = camp.researchTree();
                if (tree && row < int(tree->all().size())) {
                    const auto& tech = tree->all()[size_t(row)];
                    c.subject = tech.name.c_str();
                    c.verb = "be discovered";
                    c.noProgress = "No progress is being made on %s.";
                    // 0x47010(eax=WORD[tech+0x3c] cost, edx=acc, ebx=bank).
                    // Port analogs: cost = runtimeCost() (the OQ-013
                    // runtime-cost law), acc = techProgressFor, rate =
                    // techRateFor (the t408 read pair).
                    c.days = countdownDays(tech.runtimeCost(),
                                           int(camp.techProgressFor(
                                               ascend::game::kPlayer)),
                                           int(camp.techRateFor(
                                               ascend::game::kPlayer)));
                }
            }
            // No topic: +0x6e stays 0 (L-E never renders); L-D only.
            break;
        }
        case PlanetPanel::PlInd: {
            // KEY 1 body 0x3dd17: name "Industry", rate = +0x44 analog.
            c.nameWord = "Industry";
            c.perDay = cw.ind;
            if (ps.pendingItem >= 0) {
                const auto* it = camp.planetItem(ps.pendingItem);
                if (it) {
                    c.subject = it->name.c_str();
                    c.verb = "be completed";
                    c.noProgress = "No progress is being made on %s.";
                    // SEAM TPLB2-A (Ship/Automation cost legs, statuslist
                    // precedent): plain-file cost leg 0x39531..0x39544
                    // == planitem COST word.
                    c.days = countdownDays(it->cost, ps.buildAcc, cw.ind);
                }
            }
            break;
        }
        case PlanetPanel::PlPro: {
            // KEY 2 body 0x3ddc0 EXACT.
            c.nameWord = "Prosperity";
            c.perDay = cw.pros;
            c.subject = "Population";
            c.verb = "grow";
            const int pop = int(ps.pop);
            const int maxp = camp.popCapAt(star);
            if (pop >= maxp) {
                // 0x3de08 `cmp %bx,%dx; jae` (dx=pop, bx=maxpop) ->
                // getter(74); +0x7a keeps the 0xffff init.
                c.noProgress = "%s has no more room to grow.";
            } else {
                // 0x3de0d..0x3de23: 0x47010(eax=dword[0x66e4]=wrap 50,
                // edx=+0x4e growthCounter, ebx=+0x48 pros/day).
                c.days = countdownDays(camp.terrainTables().popGrowth,
                                       ps.growthCounter, cw.pros);
                if (c.days < 0) c.noProgress = "%s is not growing.";
            }
            break;
        }
        case PlanetPanel::PlPop: {
            // KEY 4: the full-info chain (no IndicatorContent).
            PlanetIdentity id;
            id.name = planetName;
            id.sizeIdx = ascend::game::Campaign::sizeClassFor(
                ps.surfaceCells);
            id.typeIdx = ps.terrainRow;
            id.owner = camp.starOwner(star);
            id.ownerName = camp.ownerName(id.owner);
            if (id.owner == ascend::game::kPlayer) id.ownerName = "Player";
            id.maxPop = camp.popCapAt(star);
            id.selfManaged = id.owner == ascend::game::kPlayer &&
                             ps.governor == -1;  // 0xffff analog (t45 law)
            id.chipRaceIdx = id.owner;  // SEAM TPLB2-C analog
            return fullInfoLines(id);
        }
        case PlanetPanel::PlBuild:
            // 0x3dc53 ja-leg equivalent: PLBUILD is msg 51, never 50; the
            // builder with an empty struct pushes nothing.
            return {};
    }
    return indicatorLines(planetName, c);
}

}  // namespace ascend::ui
