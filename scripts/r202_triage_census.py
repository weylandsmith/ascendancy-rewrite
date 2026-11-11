#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t202 — corpus census of the AI demolish-triage PRECONDITION fields.

Fields (system-object base = planet-NAME - 0x24; window j = P0+k*123+H so
sys+X lands at j + (X-0x24), r201_threat_census convention, self-checked):
  sys+0x1c empty-non-rock  -> j-8      sys+0x20 cls0-empty -> j-4
  sys+0x42 pop             -> j+0x1e   sys+0x4a cap -> j+0x26
  sys+0x4c used            -> j+0x28   sys+0x52 sel-cell -> j+0x2e
  sys+0x54 pending-item    -> j+0x30   sys+0x57 owner -> j+0x33
Slot array: u32[rec+0x10] member = ptr + 0x88 (t31 pointer-law correction);
slot = 4B {cls, item@+1 (0xff empty), flags u16@+2 bit0 ACTIVE}; count
u16[rec+0x1a] = cap. Item table member B+0x82bb0+0x73e40 stride 0x28:
byte0 IND +1 RES +2 PROS +3 MPOP +4 UPOP; byte+5 REQUIRES.

Self-check legs (print, must match banked numbers or the layout is wrong):
  IND max 77 / RES max 52 / PROS max 16 (t198); cell set {7,11,23,45,73} +
  cap==cells+10 for 2650/2650-era locators; used<=pop<=cap 2900/2900 (t198).

Outputs:
  A) joint (used==cap?, used==pop?, pop==cap?) class histogram
  B) OVER-CAP branch (0x3f178 fires iff used>=cap): count + among fires,
     does a CANDIDATE exist (occupied cell<cells, item!=5, MPOP==0,
     UPOP>0, max-UPOP pick) + would the recheck used>=pop hold (return)?
  C) SWEEP branch (0x3f354 reached): fires iff free=pop-used>0 AND triage
     gate open [gate open iff c1c<2 OR (c1c==c20 && ability!=2)];
     predicted victim = min-REQUIRES cell (ties first) with MPOP < cap-pop
  D) ability numbers: diplo table at member B+0x82bb0+0x12e16, rows stride
     0x1ee, row+0 = owner idx, name @row+0x1d, ability byte row+0x19d.
  E) cross-save WITNESS: adjacent saves (sorted by mtime, same planet-name
     + owner) item-multiset loss -> candidate in-play demolish events.
RC=0 always.
"""
import os, sys, re, struct, zipfile, collections
sys.path.insert(0, "/home/hrethric/projects/ascendancy")
from r1_sav_scan import build_anchors, find_base

ROOT = "/home/hrethric/projects/ascendancy"
RUN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "work/r1/playcap")
PAY = os.path.join(ROOT, "work/ascend_payload.bin")
PLANET_P0 = 0x26D07B
STRIDE = 123
NAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"


def main():
    pay = open(PAY, "rb").read()
    anch = build_anchors(pay)
    # item self-check: file-order names from planitem loader layout
    item_base_img = 0x82BB0 + 0x73e40
    files = []
    savedir = os.path.join(RUN, "save")
    for f in sorted(os.listdir(savedir)):
        if f.endswith(".sav"):
            files.append((os.path.getmtime(os.path.join(savedir, f)), f))
    files.sort()
    joint = collections.Counter()
    firesB = firesB_cand = firesB_recheck = 0
    firesC = firesC_gateopen = sweep_pred = 0
    c1c_hist = collections.Counter()
    gates_hist = collections.Counter()
    ind_max = res_max = pros_max = 0
    ab_map = {}
    per_save_loss = []
    prev_snap = None
    tot = 0
    for mt, f in files:
        try:
            mem = zipfile.ZipFile(os.path.join(savedir, f)).read("Memory")
        except Exception as e:
            print(f"{f}: {e!r}")
            continue
        votes, _ = find_base(mem, anch)
        if not votes:
            print(f"{f}: base unresolved")
            continue
        H = votes.most_common(1)[0][0] - 0x1BF450
        n = 0
        while True:
            j = PLANET_P0 + n * STRIDE + H
            if j >= len(mem) or mem[j] == 0 or not re.match(NAME_RE, mem[j:j+40]):
                break
            n += 1
        # ability rows
        try:
            for r in range(24):
                base = item_base_img + H - 0x82BB0 + (0x12e16 - 0x73e40) + 0x1ee * r
                # member index of image addr X (data pool): B + 0x82bb0 + X ;
                # H here == B + 0x1BF450 -> B = H - 0x1BF450; data member =
                # B + 0x82bb0 + X = H - 0x1BF450 + 0x82bb0 + X
                B = H + 0x1BF450
                addr = B + 0x82bb0 + 0x12e16 + 0x1ee * r
                if addr + 0x1ee >= len(mem):
                    break
                own = mem[addr]
                nm = mem[addr + 0x1d: addr + 0x1d + 20].split(b"\x00")[0]
                ab = mem[addr + 0x19d]
                if own < 24 and nm.isalpha():
                    ab_map[own] = (nm.decode("ascii", "replace"), ab)
        except Exception as e:
            print(f"{f}: diplo {e!r}")
        snap = {}
        for k in range(n):
            j = PLANET_P0 + k * STRIDE + H
            rec = j - 0x24
            name = mem[j:j+30].split(b"\x00")[0]
            ind = struct.unpack_from("<H", mem, j + 0x20)[0]
            res = struct.unpack_from("<H", mem, j + 0x22)[0]
            pros = struct.unpack_from("<H", mem, j + 0x24)[0]
            ind_max = max(ind_max, ind); res_max = max(res_max, res)
            pros_max = max(pros_max, pros)
            c1c = struct.unpack_from("<H", mem, rec + 0x1c)[0]
            c20 = struct.unpack_from("<H", mem, rec + 0x20)[0]
            cells = struct.unpack_from("<H", mem, rec + 0x18)[0]
            capw = struct.unpack_from("<H", mem, rec + 0x1a)[0]
            pop = struct.unpack_from("<H", mem, rec + 0x42)[0]
            cap = struct.unpack_from("<H", mem, rec + 0x4a)[0]
            used = struct.unpack_from("<H", mem, rec + 0x4c)[0]
            sel = struct.unpack_from("<H", mem, rec + 0x52)[0]
            pend = struct.unpack_from("<H", mem, rec + 0x54)[0]
            own = mem[rec + 0x57]
            if cells not in (7, 11, 23, 45, 73):
                continue
            if capw != cells + 10:
                continue
            tot += 1
            joint[(used >= cap, used >= pop, pop >= cap)] += 1
            c1c_hist[min(c1c, 12)] += 1
            # slot walk (needs sane ptr)
            ptr = struct.unpack_from("<I", mem, rec + 0x10)[0]
            slots_ok = 0x100000 < ptr < 0x800000 and ptr + 0x88 + 4 * 32 < len(mem)
            items = []
            if slots_ok:
                for si in range(capw if capw <= 93 else 0):
                    s = ptr + 0x88 + 4 * si
                    it = mem[s + 1]
                    fl = struct.unpack_from("<H", mem, s + 2)[0]
                    items.append((it, fl))
            itemmultiset = tuple(sorted(i for i, f_ in items if i != 0xFF))
            snap[name] = (own, itemmultiset)
            ab = ab_map.get(own, ("?", None))[1]
            gate_open = c1c < 2 or (c1c == c20 and ab != 2)
            gates_hist[(c1c >= 2, c1c == c20, ab)] += 1
            if used >= cap:
                firesB += 1
                cand = None
                for si, (it, fl) in enumerate(items[:cells]):
                    if it == 0xFF or it == 5:
                        continue
                    ib = item_base_img + H - 0x82BB0 + 0x28 * it - 0x82BB0 * 0
                    ia = (H + 0x1BF450) + 0x82bb0 + 0x73e40 + 0x28 * it
                    mpop = mem[ia + 3] if ia + 3 < len(mem) else -1
                    upop = mem[ia + 4] if ia + 4 < len(mem) else -1
                    if mpop == 0 and upop > 0 and (cand is None or upop > cand[2]):
                        cand = (si, it, upop)
                if cand:
                    firesB_cand += 1
                    if used >= pop:
                        firesB_recheck += 1
            if pop - used > 0:
                firesC += 1
                if gate_open:
                    firesC_gateopen += 1
                    # predicted sweep victim among cells<cells
                    best = None
                    for si, (it, fl) in enumerate(items[:cells]):
                        if it == 0xFF:
                            continue
                        ia = (H + 0x1BF450) + 0x82bb0 + 0x73e40 + 0x28 * it
                        if ia + 5 >= len(mem):
                            break
                        mpop = mem[ia + 3]
                        req = mem[ia + 5]
                        margin = cap - pop
                        if mpop < margin and (best is None or req < best[2]):
                            best = (si, it, req)
                    if best:
                        sweep_pred += 1
        per_save_loss.append((f, snap))
        print(f"{f}: recs={n}")
    print("TOTAL located recs:", tot)
    print(f"SELF-CHECK IND max {ind_max} (t198:77) RES {res_max} (52) PROS {pros_max} (16)")
    print("A) (used>=cap, used>=pop, pop>=cap) hist:", dict(joint))
    print("B) over-cap fires:", firesB, "with candidate:", firesB_cand,
          "recheck-used>=pop:", firesB_recheck)
    print("C) free-pop records:", firesC, "gate-open:", firesC_gateopen,
          "sweep victim predicted:", sweep_pred)
    print("C1c hist (capped 12):", dict(sorted(c1c_hist.items())))
    print("gates (c1c>=2, c1c==c20, ability) hist:", dict(sorted(gates_hist.items(), key=str)))
    print("D) ability rows:", ab_map)
    print("E) cross-save item-loss witnesses:")
    w = 0
    for (fa, sa), (fb, sb) in zip(per_save_loss, per_save_loss[1:]):
        for nm in set(sa) & set(sb):
            oa, ma = sa[nm]; ob, mb = sb[nm]
            if oa == ob and ma != mb:
                lost = collections.Counter(ma) - collections.Counter(mb)
                if lost:
                    w += 1
                    if w <= 25:
                        print(f"  {fa}->{fb} {nm} owner {oa} lost {dict(lost)} gained {dict(collections.Counter(mb)-collections.Counter(ma))}")
    print("  total loss witnesses:", w)


main()
