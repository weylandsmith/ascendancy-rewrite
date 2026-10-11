#!/usr/bin/env python3
"""r1_cb_placement_paths.py — t42 decisive census: which path placed each CB,
and does the race table byte (rule-A blanket legality) explain barren CBs.

STATIC LAWS BANKED THIS TURN (raw disasm, docs/re/income-law.md T42):
  checker FUN_0003830c EDI chain (last-writer-wins, legal = EDI!=0 && EBP!=0):
    ruleA @0x38446: item.flags bit0 || raceTable byte[owner]==2 -> EDI:=-1
    ruleB @0x38493: cell class != 0 -> EDI:=-1 (ANY item, unconditional);
                    class==0: illegal unless item 0xff or flags bit1
    ruleC @0x384db: (slot<surf) XOR (item<22) -> EDI:=0  [item 5 NOT exempt]
    ruleD @0x38519: rock XOR (item==38) -> EDI:=0
    ruleG @0x385f6: adjacency, SKIPPED for item 5 and 35 (CMP DL,5; JZ end)
  picker FUN_0003875c: uniform rng % count over legal EMPTY slots [0,cap)
  picker CALLERS (EBX=0xffff => picker path):
    home seed    FUN_000238e8 @0x23ca2..0x23cb2 (EDX:=5)
    standalone   FUN_00041d64..0x41d7b (EDX:=5, owner:=DAT_00012e10)
  ACTIVATOR-ONLY (NO cell legality): FUN_0003aa0a branch @0x3b0a6..0x3b0d1
    claim-star + pop:=2 + CALL FUN_00038840 mode0 (BL=cargo item, DX=slot)
  race table: member idx B + 0x82bb0 + 0x12fb3 + owner*0x1ee (pointer corollary)
"""
import sys, os, glob, struct as st, zipfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
import r1_income_law as IL

TURN_PHYS, IMAGE_MAP_BASE = 0x254E10, 0x1BF450  # banked H-map law (r1_pros_growth)
RACE_TB = 0x12fb3


def main():
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = build_anchors(pay)
    worlds = {}
    for run in sorted(glob.glob("work/r1/*")):
        if not os.path.isdir(run):
            continue
        for f in sorted(glob.glob(run + "/save/*.sav"), key=os.path.getmtime):
            try:
                m = zipfile.ZipFile(f).read("Memory")
            except Exception:
                continue
            votes, _ = find_base(m, anch)
            if not votes:
                continue
            base = votes.most_common(1)[0][0]
            items = IL.item_table(m, base)
            if items is None or not IL.names_ok(items):
                continue
            turn = st.unpack_from("<H", m, TURN_PHYS + (base - IMAGE_MAP_BASE))[0]
            ids, cbs = [], []
            for rec in IL.find_records(m):
                rb = rec[0]
                owner = m[rb + 0x57]
                if owner == 0xFF:
                    continue
                ptr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
                surf = st.unpack_from("<H", m, rb + 0x18)[0]
                capw = st.unpack_from("<H", m, rb + 0x1a)[0]
                name = m[rb + 0x24:m.index(b"\x00", rb + 0x24)].decode("cp437", "replace")
                ids.append((name, capw))
                for k in range(min(capw, 200)):
                    if (m[ptr + 4 * k + 1] == 5
                            and (st.unpack_from("<H", m, ptr + 4 * k + 2)[0] & 1)
                            and k < surf):
                        sur = [m[ptr + 4 * q] for q in range(surf)]
                        cbs.append((name, owner, sur, k))
            if not ids:
                continue
            wid = tuple(ids)
            if wid not in worlds or os.path.getmtime(f) < worlds[wid][1]:
                # race bytes: owner i -> byte0 of block i (empire index order)
                rbytes = tuple(m[base + 0x82bb0 + RACE_TB + i * 0x1ee]
                               for i in range(7))
                worlds[wid] = (f, os.path.getmtime(f), turn, cbs, rbytes)

    homes = [w for w in worlds.values() if w[2] <= 1]
    mgames = [w for w in worlds.values() if w[2] > 1]
    print(f"worlds: {len(worlds)}  homes(turn<=1)={len(homes)} mid={len(mgames)}")
    rb_hist = collections.Counter(w[4] for w in worlds.values())
    print(f"race byte0 tuples (per world): {dict(list(rb_hist.items())[:4])}")

    # cross-tab: (population, racebyte, barren?) and rank shape
    xt = collections.Counter()
    rank_h = {True: collections.Counter(), False: collections.Counter()}
    for (f, mt, turn, cbs, rbytes) in worlds.values():
        pop = "home" if turn <= 1 else "mid"
        for (name, owner, sur, k) in cbs:
            rb = rbytes[owner] if owner < 7 else -1
            bar = sur[k] == 0
            xt[(pop, rb, bar)] += 1
            legal = [q for q, c in enumerate(sur)
                     if c != 0 and not (c & 8)]
            r = legal.index(k) if k in legal else -1
            rank_h[bar][min(r, 6) if r >= 0 else -1] += 1
    print("\ncross-tab (pop, race byte0, CB-on-barren) -> count:")
    for key in sorted(xt, key=str):
        print(f"   {key}: {xt[key]}")
    print(f"\nrank-over-legal-nonbarren hist, barren-CBs:   "
          f"{dict(sorted(rank_h[True].items()))}")
    print(f"rank-over-legal-nonbarren hist, nonbarren-CBs: "
          f"{dict(sorted(rank_h[False].items()))}")

    # RULE-A CHECK with the actual item-5 legality the picker enforced:
    # picker-legal cells at placement = non-rock AND (class!=0 OR racebyte==2)
    viol_home = n_home = 0
    viol_mid = n_mid = 0
    rank2 = {"home": collections.Counter(), "mid": collections.Counter()}
    for (f, mt, turn, cbs, rbytes) in worlds.values():
        pop = "home" if turn <= 1 else "mid"
        for (name, owner, sur, k) in cbs:
            rb = rbytes[owner] if owner < 7 else 0
            legal = [q for q, c in enumerate(sur)
                     if not (c & 8) and (c != 0 or rb == 2)]
            n_home += 1 if pop == "home" else 0
            n_mid += 1 if pop == "mid" else 0
            if k not in legal:
                if pop == "home":
                    viol_home += 1
                else:
                    viol_mid += 1
            else:
                rank2[pop][min(legal.index(k), 8)] += 1
    print(f"\nCB inside race-aware picker-legal set (nonrock & (nonbar|race==2)):")
    print(f"   homes: {n_home - viol_home}/{n_home}   mid: {n_mid - viol_mid}/{n_mid}")
    print(f"   home rank hist (capped8): {dict(sorted(rank2['home'].items()))}")
    print(f"   mid  rank hist (capped8): {dict(sorted(rank2['mid'].items()))}")
    # rank >= 2 check (t40 envelope restated with the corrected legal set)
    lo_h = sum(v for r, v in rank2["home"].items() if r < 2)
    lo_m = sum(v for r, v in rank2["mid"].items() if r < 2)
    print(f"   rank<2 in-set: home {lo_h}, mid {lo_m}")


main()
