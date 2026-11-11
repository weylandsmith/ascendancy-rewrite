# SPDX-License-Identifier: GPL-3.0-or-later

# r1_built_cell_law.py — t43: non-CB built-item cell law.
#
# STATIC (Ghidra, this session):
#  - Picker FUN_0003875c IGNORES the caller's slot register: it only consumes
#    EAX=planet and DL=item (stashed @0x38769 BEFORE EDX is clobbered
#    0x38770; the pushed ECX/EBX are never re-read — no [ESP+0xe4]/[ESP+0xe8]
#    reads in the 59-instruction listing). So EVERY placement through the
#    wrapper FUN_00038818 — all 19 call sites incl. the 16 build sites that
#    pass EBX=0 — is the uniform random draw over checker-legal empty cells.
#    T40(6) "prefix-from-0 refuted 0/2720" is now fully explained.
#  - Checker FUN_0003830c full 325-instruction listing re-read with exact
#    SET semantics (EDI:=-1 at entry; only XOR EDI,EDI MAKES ILLEGAL):
#      EBP branch (skipped for item >= 0x27): tech requirement
#        item.tech = byte[(item*5) + 0x73e45] (stride 40 = 0x28),
#        illegal if item.tech >= DAT_00074744 (empire research count);
#      EBP pop term: (pop[+0x42] - queue[+0x4c] (+ item-queue[+0x54] adj
#        byte[(q*5)+0x73e44])) >= byte[((item*5)<<3)+0x73e41]
#        (item byte3 — pop requirement);
#      EBP: item 0x17 also ORs FUN_00039a9c(planet); item 5 sets EBP := -1.
#      rule A/B = redundant EDI := -1 sets (no-op: EDI already -1, A/B run
#        before the zeroing rules).
#      rule C: surface/orbital match  ((slot<+0x18) == (item < WORD 0x73e3c)).
#      rule D: rock illegal except item 0x26.
#      rule F (item 0x24 Terraforming): legal only if terrain byte == 0
#        (or class-0 cell with empty slot byte).
#      rule G @0x385b7..0x386fe: surface slots; EXEMPT item 5 (0x385f9) and
#        item 0x23 (0x38602); target's own word2 bit0 -> early exit (not the
#        zeroing); else NEIGHBORHOOD: r = FUN_0003965c(planet,slot) returns
#        (row<<16)|(col + rowOffset[row]) with row tables at 0x7445c (per-
#        planet-type row offsets/starts) and 0x744a8 (row widths); the four
#        FUN_000395c4 calls probe (row-1,x),(row+1,x),(row,x-1),(row,x+1);
#        if ANY of the four has word2 bit0 (active) -> JNZ 0x386fe exit
#        WITHOUT zeroing = LEGAL; all inactive/absent -> XOR EDI,EDI =
#        ILLEGAL. i.e. BUILT ITEMS MUST ADJOIN AN ACTIVE ITEM (hex-grid
#        neighbourhood; CB and 0x23 exempt).
#
# EMPIRICAL: every active non-CB item cell must have (at placement) an
# active neighbour; necessary in FINAL state for items placed when it was
# the 2nd active (only CB precedes): test = non-CB items with ZERO active
# neighbours in some save AND non-zero active neighbours in a later save of
# the same run (transitional) vs items with zero neighbours in the run's
# LAST save (final violation — would refute rule G).
import sys, os, glob, struct as st, zipfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
import r1_income_law as IL

TURN_PHYS, IMG = 0x254E10, 0x1BF450
SURF_MAX_ROWS = 15
KROWS = bytes([100, 0, 0, 0, 50, 2, 2, 2, 20, 3, 5, 3, 0, 3, 20, 3,
               40, 10, 2, 2, 20, 20, 2, 2, 40, 2, 2, 10, 20, 3, 3, 20,
               40, 10, 10, 10, 20, 15, 15, 15, 0, 33, 34, 33])
# The static DAT tables 0x744a8 (row widths) / 0x7445c (row starts) are
# ZERO in saved RAM at their image VA (verified: static data RAM region
# isn't dumped); the runtime copy sits 152 bytes before the terrain weight
# rows (verified ptype 3/4 sums == live +0x18 for 45/73-cell planets).
HH = 0            # set per-save: member index = VA + HH  (geometry tables)
ROWW = 0          # set per-save: member index of row-widths table base
ROWSTART = 0


def slot_geom(m, rb, k):
    """(row, x-continuous-col) of surface slot k, or None."""
    ptype = m[rb + 0x14]
    base = ptype * SURF_MAX_ROWS
    cum = 0
    for r in range(SURF_MAX_ROWS):
        w = m[ROWW + base + r]
        if k < cum + w:
            return r, (k - cum) + m[ROWSTART + base + r]
        cum += w
    return None


def geom_slot(m, rb, r, x):
    """inverse: surface slot at (row,x), or None."""
    ptype = m[rb + 0x14]
    base = ptype * SURF_MAX_ROWS
    if not (0 <= r < SURF_MAX_ROWS):
        return None
    if not (m[ROWSTART + base + r] <= x <
            m[ROWSTART + base + r] + m[ROWW + base + r]):
        return None
    cum = sum(m[ROWW + base + i] for i in range(r))
    return cum + x - m[ROWSTART + base + r]


def active_neighbours(m, rb, ptr, surf, k):
    g = slot_geom(m, rb, k)
    if g is None:
        return 0
    r, x = g
    n = 0
    for dr, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        s = geom_slot(m, rb, r + dr, x + dx)
        if s is not None and s < surf:
            if st.unpack_from("<H", m, ptr + 4 * s + 2)[0] & 1:
                n += 1
    return n


def main():
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = build_anchors(pay)
    # per (run, world-name): sequence of (turn, turn<=1?, {item: slots},
    # per-slot (item, active, nactive_neighbours))
    perworld = collections.defaultdict(list)
    items_seen = collections.Counter()
    for run in sorted(glob.glob("work/r1/*")):
        if not os.path.isdir(run):
            continue
        runname = os.path.basename(run)
        for f in sorted(glob.glob(run + "/save/*.sav"), key=os.path.getmtime):
            try:
                m = zipfile.ZipFile(f).read("Memory")
            except Exception:
                continue
            votes, _ = find_base(m, anch)
            if not votes:
                continue
            base = votes.most_common(1)[0][0]
            H = base - IMG
            kr = m.find(KROWS)
            if kr < 0:
                continue
            globals()["ROWW"] = kr - 76
            globals()["ROWSTART"] = kr - 152
            try:
                turn = st.unpack_from("<H", m, TURN_PHYS + H)[0]
            except Exception:
                continue
            for rec in IL.find_records(m):
                rb = rec[0]
                owner = m[rb + 0x57]
                if owner == 0xFF:
                    continue
                ptr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
                surf = st.unpack_from("<H", m, rb + 0x18)[0]
                capw = st.unpack_from("<H", m, rb + 0x1a)[0]
                name = m[rb + 0x24:m.index(b"\x00", rb + 0x24)].decode("cp437", "replace")
                snap = {}
                for k in range(min(capw, 200)):
                    it = m[ptr + 4 * k + 1]
                    act = st.unpack_from("<H", m, ptr + 4 * k + 2)[0] & 1
                    if it == 0xFF:
                        continue
                    items_seen[it] += 1
                    nn = active_neighbours(m, rb, ptr, surf, k) if (
                        k < surf and it not in (5, 0x23)) else -1
                    snap[k] = (it, act, nn)
                    # NOTE: EBP-branch sanity (tech byte 0x73e45, pop-req byte
                    # 0x73e44) NOT run — the static item table is zeroed in
                    # saved RAM at its image VA (same dump artifact as the
                    # terrain tables; runtime copy unfound).
                perworld[(runname, name)].append((turn, snap))

    print(f"runs scanned; worlds tracked: {len(perworld)}")
    print("item census (idx: count active+pending records):")
    print(" ", dict(sorted(items_seen.items())))


    zero_final = collections.Counter()
    zero_trans = collections.Counter()
    nonzero_final = collections.Counter()
    for (run, name), seq in perworld.items():
        seq.sort(key=lambda t: t[0])
        for it, cnt in collections.Counter(
                s[0] for turn, snap in seq for k, s in snap.items()
                if s[1] and s[0] not in (5, 0x23) and s[2] == 0).items():
            zero_trans[it] += 1
        turn_last, snap_last = seq[-1]
        for k, s in snap_last.items():
            it, act, nn = s
            if not act or it in (5, 0x23) or nn < 0:
                continue
            (zero_final if nn == 0 else nonzero_final)[it] += 1
    print("\nRULE G TEST (non-CB surface active items, active-neighbour req):")
    print(" final-state ZERO-neighbour items by idx:", dict(sorted(zero_final.items())))
    print(" final-state NONZERO-neighbour items:", dict(sorted(nonzero_final.items())))
    print(" transitional zero-> later-active rows:", sum(zero_trans.values()),
          "by idx", dict(sorted(zero_trans.items())))

    print("\nrule-G verdict:",
          "CONFIRMED (zero final-state violations)" if not zero_final
          else f"REFUTED ({sum(zero_final.values())} violations)")


if __name__ == "__main__":
    main()
