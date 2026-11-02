# r271b_tfdrill.py — t271: drill the 78 item-36 (Terraforming) slot observations.
#
# r271_cellreach.py found: item 36 in slots 78x, ACTIVE 0x; item 35 (Automation)
# 0x anywhere. Hypothesis: queued-but-never-completed UI builds (activator
# writes byte1:=item + word2:=1 only on completion; a queued build shows the
# item id with word2 bit0 CLEAR). Test per (run, planet, slot) across saves in
# mtime order: queued -> completed transition would be byte0 class->1,
# byte1->0xFF (T39b law), i.e. the FIRST LIVE WITNESS of the terrain-mutation
# law. Also dump record pending byte +0x54 and owner for context.
import sys, os, glob, struct as st, zipfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
import r1_income_law as IL

TURN_PHYS, IMG = 0x254E10, 0x1BF450

def main():
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = build_anchors(pay)
    # (run, planet, slot) -> list of (mtime, sav, turn, owner, class, item, flags, pend54)
    seq = collections.defaultdict(list)
    runcount = collections.Counter()
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
            try:
                turn = st.unpack_from("<H", m, TURN_PHYS + H)[0]
            except Exception:
                turn = -1
            for rec in IL.find_records(m):
                rb = rec[0]
                owner = m[rb + 0x57]
                if owner == 0xFF:
                    continue
                ptr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
                capw = st.unpack_from("<H", m, rb + 0x1a)[0]
                name = m[rb + 0x24:m.index(b"\x00", rb + 0x24)].decode("cp437", "replace")
                pend = m[rb + 0x54]
                for k in range(min(capw, 200)):
                    it = m[ptr + 4 * k + 1]
                    if it not in (35, 36, 38):
                        continue
                    cls = m[ptr + 4 * k]
                    fl = st.unpack_from("<H", m, ptr + 4 * k + 2)[0]
                    seq[(runname, name, k)].append(
                        (os.path.getmtime(f), os.path.basename(f), turn, owner, cls, it, fl, pend))
                    runcount[(runname, it)] += 1

    print("obs by (run, item):")
    for (r, it), c in sorted(runcount.items()):
        print(f"   {r} item {it}: {c}")
    print(f"\n(run,planet,slot) tracks holding 35/36/38: {len(seq)}")
    completions = 0
    for key, rows in sorted(seq.items()):
        rows.sort()
        # collapse consecutive identical (cls,item,fl)
        comp = []
        for r in rows:
            sig = (r[4], r[5], r[6])
            if not comp or comp[-1][0] != sig:
                comp.append((sig, r))
        if len(comp) > 1:
            print(f"\n  {key}:")
            for sig, r in comp:
                print(f"     {r[1]} t{r[2]} owner={r[3]} cls={sig[0]} item={sig[1]} flags=0x{sig[2]:04x} pend54={r[7]}")
            # T39b completion signature: last state item==0xFF and cls==1
            # preceded by a state with item==36
            if comp[-1][0][1] == 0xFF and comp[-1][0][0] == 1 and \
               any(c[0][1] == 36 for c in comp[:-1]):
                completions += 1
                print("     ^^^ T39b TERRAIN-MUTATION WITNESS (queued 36 -> cls 1, slot freed)")
    print(f"\nT39b terraform-completion witnesses (queued->class1+freed): {completions}")
    # static per-track verdict
    stat = collections.Counter()
    for key, rows in seq.items():
        items = {r[5] for r in rows}
        acts = {r[6] & 1 for r in rows}
        stat[(tuple(sorted(items)), tuple(sorted(acts)))] += 1
    print("track signatures (items-seen, active-flags-seen) -> n tracks:")
    for k, v in sorted(stat.items()):
        print("  ", k, v)

if __name__ == "__main__":
    main()
