#!/usr/bin/env python3
"""t342: corpus census of the HUMAN (owner-0) build queue — residue-(5).

ZERO CAPTURE: offline over existing .sav files (Memory member of the
dosbox-zip), anchor-verified per r1_sav_scan law.

Laws in use (all banked; docs/re/_wip_t342.md S0):
  heap-record (t33/OQ-014): IL.find_records; owner byte rb+0x57 (t248),
  queue cell WORD rb+0x52, queue item BYTE rb+0x54 (0xff=empty), acc WORD
  rb+0x50, local-flag DWORD rb+0x5a, IND rb+0x44, cells WORD rb+0x18.
  DS-seg linear = B + 0x82bb0 (t340). Item gate record stride 0x28 at
  DS+0x73e40: flags u16 @ +6, cost u16 @ +2 (t340 runtime-verified).
  netplay u32 DS+0x10ba4; local-player byte DS+0x7458e.
  turn clock u16 phys 0x254E10 at off 0x254E10+(B-0x1BF450).

The VENDOR-selector signature (t341 Gridsor I witness): at a turn boundary,
a pending row whose acc reaches COST is reset (acc=0, +0x52=0xffff/+0x54=0xff
or immediately re-written) and a NEW item appears in the SAME boundary
(complete-then-requeue). The UI leg (fn 0x3aa0a -> 0x38818 chain) writes a
queue row WITHOUT a same-boundary completion of that planet's row.

Prints:
  1. per-save globals (netplay, local) histograms over the whole corpus
  2. every owner-0 PENDING row histogram (item, cell sanity, acc, +0x5a)
  3. anomaly flags: items the UI cannot order (special 0x21-0x23 per t45,
     item>=39), cell>=cells, cell==0xffff, acc>COST
  4. per run dir, adjacent-save transitions per owner-0 planet classified:
     PROGRESS / SAME_ITEM_REQUEUE / NEW_ITEM (fresh or after-completion) /
     DRAIN, with the completion-boundary flag from prev acc vs COST.

Exit codes: 0 = census ran; 2 = harness broken.
"""
import os
import struct as st
import sys
import glob
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_income_law as IL
from r1_sav_scan import build_anchors, find_base

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TURN_PHYS, IMAGE_MAP_BASE = 0x254E10, 0x1BF450
GOVERNOR_ITEMS = (0x21, 0x22, 0x23)  # +0x54 governor values, t45 mode-3 law


def turn_of(m, base):
    off = TURN_PHYS + (base - IMAGE_MAP_BASE)
    if not (0 <= off and off + 2 <= len(m)):
        return None
    t = st.unpack_from("<H", m, off)[0]
    return t if t < 20000 else None


def all_view(m):
    """(owner, name) -> row dict for EVERY planet record (pending or not)."""
    out = {}
    for rec in IL.find_records(m):
        rb = rec if isinstance(rec, int) else rec[0]
        owner = m[rb + 0x57]
        if owner == 0xFF:
            continue
        name = m[rb + 0x24:m.index(b"\x00", rb + 0x24)].decode("cp437", "replace")
        item = m[rb + 0x54]
        out.setdefault((owner, name), dict(
            rb=rb, item=item,
            cell=st.unpack_from("<H", m, rb + 0x52)[0],
            acc=st.unpack_from("<H", m, rb + 0x50)[0],
            ind=st.unpack_from("<b", m, rb + 0x44)[0],
            flag5a=st.unpack_from("<I", m, rb + 0x5a)[0],
            cells=st.unpack_from("<H", m, rb + 0x18)[0],
        ))
    return out


def cost_of(m, ds, idx):
    """COST word: DS:0x73e40 + 8 + 0x28*idx (income-law.md:448 verbatim
    `word [EAX*0x8 + 0x73e48]`, EAX=idx*5). Gate FLAGS word is at +6."""
    if idx >= IL.N_ITEMS:
        return None
    b = ds + 0x73E40 + idx * 0x28
    if b + 0x28 > len(m):
        return None
    return st.unpack_from("<H", m, b + 8)[0]


def main():
    try:
        pay = open(IL.PAY, "rb").read()
        anch = build_anchors(pay)
    except Exception as e:
        print("ANCHORS FAIL:", e)
        return 2

    if "--all" in sys.argv:
        dirs = sorted(set(glob.glob(os.path.join(ROOT, "work/r1/*/"))))
    else:
        # t342 assignment sources (STATE.md): production playcap (t1086
        # corpus), playcap/caps, bank t1254, t340 ring-final.
        dirs = [os.path.join(ROOT, p) for p in (
            "work/r1/playcap", "work/r1/playcap/caps",
            "work/r1/bank-t1254", "work/r1/t340-shieldc-20261108-014705")]
    total_saves = 0
    saves_unverified = 0
    np_hist = collections.Counter()
    loc_hist = collections.Counter()
    pending_total = 0
    ai_pending_total = 0
    item_hist = collections.Counter()
    flag5a_hist = collections.Counter()
    cell5a_nonzero_pending = []
    anomalies = []
    trans_hist = collections.Counter()
    orbit_hist = collections.Counter()
    gov_acc_hist = collections.Counter()
    boundary_requeue = []      # THE decisive signature on owner-0
    ctrl_hist = collections.Counter()      # POSITIVE CONTROL: owner!=0
    ctrl_boundary = []
    dirs_with_pending = []

    for d in dirs:
        try:
            slots = IL.load_slots(d)
        except Exception:
            continue
        if not slots:
            continue
        dir_pending = 0
        views = []  # (f, turn, owner0 view) in FILE ORDER — NO memory held
        itemtab = None  # per-dir item table (static data; extracted once)
        for f, m, B in slots:
            total_saves += 1
            ds = B + 0x82BB0
            if itemtab is None:
                rows = IL.item_table(m, B)
                if rows is not None and not IL.names_ok(rows):
                    print("ITEM-TABLE NAMES MISMATCH in", d, "-", f)
                    rows = None
                if rows is not None:
                    dsb = B + 0x82BB0
                    for k, r in enumerate(rows):
                        r["cost"] = st.unpack_from("<H", m,
                                                   dsb + 0x73E40 + k * 0x28 + 8)[0]
                itemtab = rows
            turn = turn_of(m, B)
            netplay = st.unpack_from("<I", m, ds + 0x10ba4)[0] \
                if ds + 0x10ba8 <= len(m) else None
            local = m[ds + 0x7458e] if ds + 0x7458f <= len(m) else None
            np_hist[netplay] += 1
            loc_hist[local] += 1
            v = all_view(m)
            pend = {n: r for n, r in v.items()
                    if r["item"] != 0xFF and n[0] == 0}
            ai_pend = {n: r for n, r in v.items()
                       if r["item"] != 0xFF and n[0] != 0}
            dir_pending += len(pend) + len(ai_pend)
            pending_total += len(pend)
            ai_pending_total += len(ai_pend)
            for n, r in pend.items():
                item_hist[r["item"]] += 1
                flag5a_hist[r["flag5a"]] += 1
                if r["flag5a"] != 0:
                    cell5a_nonzero_pending.append((os.path.basename(d), f, n,
                                                   r["flag5a"]))
                cost = cost_of(m, ds, r["item"])
                bit1 = bool(itemtab and r["item"] < IL.N_ITEMS
                            and itemtab[r["item"]]["flags"] & 2)
                if r["item"] >= IL.N_ITEMS:
                    anomalies.append(("junk-item-id", os.path.basename(d),
                                      f, n, r["item"]))
                elif r["item"] not in GOVERNOR_ITEMS and not bit1 \
                        and r["cell"] == 0xFFFF:
                    # t341 S1 writer law: +0x52 stays 0xffff ONLY for
                    # flag-bit1 items; any other pending 0xffff cell is a
                    # row the UI-command chain could not have written.
                    anomalies.append(("cell-ffff-nonbit1",
                                      os.path.basename(d), f, n, r["item"]))
                # cell >= cells is an ORBIT slot (cap = cells+10 law; t340:
                # slot>=cells skips the surface marker) — informational.
                if r["cell"] >= r["cells"] and r["cell"] != 0xFFFF:
                    orbit_hist[r["item"]] += 1
                if cost is not None and r["acc"] > cost:
                    if r["item"] in GOVERNOR_ITEMS:
                        # t45 governor-state accumulation (acc keeps +IND
                        # while +0x54 holds a governor value) — normal.
                        gov_acc_hist[r["item"]] += 1
                    else:
                        anomalies.append(("acc-over-cost-construction",
                                          os.path.basename(d), f, n,
                                          r["item"], r["acc"], cost))
            views.append((f, turn, v))
        views.sort(key=lambda x: (x[1] is None, x[1]))  # RING order -> TURN order
        for (fa, ta, va), (fb, tb, vb) in zip(views, views[1:]):
            if ta is None or tb is None or tb - ta != 1:
                continue
            for n in set(va) | set(vb):
                # owner-0 rows -> trans_hist/boundary_requeue; AI rows ->
                # ctrl_hist/ctrl_boundary (POSITIVE CONTROL: the selector
                # law must produce boundary re-queues on AI planets)
                th, br = (trans_hist, boundary_requeue) if n[0] == 0 \
                    else (ctrl_hist, ctrl_boundary)
                pa = va.get(n)
                pb = vb.get(n)
                a_pend = pa and pa["item"] != 0xFF
                b_pend = pb and pb["item"] != 0xFF
                if a_pend and not b_pend:
                    th["DRAIN"] += 1
                elif not a_pend and b_pend:
                    th["FRESH-QUEUE"] += 1
                elif a_pend and b_pend:
                    if pb["item"] == pa["item"] and pb["acc"] >= pa["acc"]:
                        th["PROGRESS"] += 1
                    else:
                        cost = (itemtab[pa["item"]]["cost"]
                                if itemtab and pa["item"] < IL.N_ITEMS
                                else None)
                        # completion-boundary: prev acc + IND >= COST(prev)
                        at_cost = (cost is not None and
                                   pa["acc"] + pa["ind"] >= cost)
                        if pb["item"] == pa["item"]:
                            k = "SAME-ITEM-REQUEUE"
                        else:
                            k = "NEW-ITEM"
                        th[k] += 1
                        if at_cost:
                            br.append(
                                (os.path.basename(d), fa, ta, fb, n[1],
                                 pa["item"], pa["acc"], pa["ind"], cost,
                                 pb["item"], pb["acc"]))
        if dir_pending:
            turnset = sorted({t for _, t, _ in views if t is not None})
            dirs_with_pending.append((os.path.basename(d), len(slots),
                                      dir_pending,
                                      "%d turns %s..%s" % (
                                          len(turnset),
                                          turnset[0] if turnset else "?",
                                          turnset[-1] if turnset else "?")))

    print("== 1. corpus globals ==")
    print("saves census:", total_saves)
    print("netplay ds:0x10ba4 histogram:", dict(np_hist))
    print("local-player ds:0x7458e histogram:", dict(loc_hist))
    print()
    print("== 2. owner-0 pending rows ==")
    print("total pending rows:", pending_total, "(AI pending rows:",
          ai_pending_total, ")")
    print("item histogram:", dict(sorted(item_hist.items())))
    print("[p+0x5a] histogram (pending rows):", dict(sorted(flag5a_hist.items())))
    if cell5a_nonzero_pending:
        print("PENDING ROWS WITH [p+0x5a]!=0 (selector NOT statically excluded):")
        for x in cell5a_nonzero_pending[:40]:
            print("  ", x)
    print()
    print("== 3. anomalies (selector-unwritable / junk / acc) ==")
    if not anomalies:
        print("NONE")
    else:
        ah = collections.Counter(a[0] for a in anomalies)
        print("counts:", dict(ah))
        for x in anomalies[:40]:
            print("  ", x)
    print("orbit-slot rows (cell>=cells, informational):",
          dict(sorted(orbit_hist.items())))
    print("governor-item acc-over-cost rows (t45 law, normal):",
          dict(sorted(gov_acc_hist.items())))
    print()
    print("== 4. adjacent-save owner-0 transitions ==")
    for k, c in sorted(trans_hist.items()):
        print("  %-16s %d" % (k, c))
    print("complete-then-requeue signature events on owner-0:",
          len(boundary_requeue))
    for x in boundary_requeue[:40]:
        print("  dir=%s prev=%s(t%d) -> %s planet=%s prev_item=%d acc=%d "
              "ind=%d cost=%d | cur_item=%d cur_acc=%d" % x)
    print()
    print("== 4b. POSITIVE CONTROL: adjacent-save AI (owner!=0) transitions ==")
    for k, c in sorted(ctrl_hist.items()):
        print("  %-16s %d" % (k, c))
    print("complete-then-requeue signature events on AI planets:",
          len(ctrl_boundary))
    for x in ctrl_boundary[:20]:
        print("  dir=%s prev=%s(t%d) -> %s planet=%s prev_item=%d acc=%d "
              "ind=%d cost=%d | cur_item=%d cur_acc=%d" % x)
    print()
    print("dirs with pending owner-0 rows: (dir, saves, pending-row-saves)")
    for x in dirs_with_pending:
        print("  ", x)
    return 0


if __name__ == "__main__":
    sys.exit(main())
