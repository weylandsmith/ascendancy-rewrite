# r271c_pendctx.py — t271: pending/accumulator context for the item-36/38 tracks.
# For each (run, planet) that held item 35/36/38 in a slot, dump per save:
# turn, owner, +0x54 (pending byte), +0x50 (build acc u32), +0x44 (stored IND),
# the track slot's raw word. Distinguishes: queued-forever build (pend==item,
# acc < COST) vs stale slot residue (pend==0xFF, byte1 set, word2&1 clear).
import sys, os, glob, struct as st, zipfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
import r1_income_law as IL

TURN_PHYS, IMG = 0x254E10, 0x1BF450
TARGETS = {35, 36, 38}

def main():
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = build_anchors(pay)
    tracks = set()
    # first pass: find (run,name,slot)
    found = collections.defaultdict(set)
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
            for rec in IL.find_records(m):
                rb = rec[0]
                if m[rb + 0x57] == 0xFF:
                    continue
                ptr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
                capw = st.unpack_from("<H", m, rb + 0x1a)[0]
                name = m[rb + 0x24:m.index(b"\x00", rb + 0x24)].decode("cp437", "replace")
                for k in range(min(capw, 200)):
                    if m[ptr + 4 * k + 1] in TARGETS:
                        found[(runname, name)].add(k)
    print("worlds with 35/36/38 slot obs:", sorted(found.keys()))
    # second pass: dump context
    for run in sorted(glob.glob("work/r1/*")):
        if not os.path.isdir(run):
            continue
        runname = os.path.basename(run)
        keep = {w: s for (r, w), s in found.items() if r == runname}
        if not keep:
            continue
        print(f"\n=== {runname} ===")
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
                name = m[rb + 0x24:m.index(b"\x00", rb + 0x24)].decode("cp437", "replace")
                if name not in keep:
                    continue
                ptr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
                capw = st.unpack_from("<H", m, rb + 0x1a)[0]
                pend = m[rb + 0x54]
                acc = st.unpack_from("<I", m, rb + 0x50)[0]
                ind = st.unpack_from("<H", m, rb + 0x44)[0]
                for k in sorted(keep[name]):
                    if k >= capw:
                        continue
                    cls = m[ptr + 4 * k]
                    it = m[ptr + 4 * k + 1]
                    fl = st.unpack_from("<H", m, ptr + 4 * k + 2)[0]
                    if it in TARGETS or pend in TARGETS:
                        print(f"  {os.path.basename(f)} t{turn} {name} owner={owner} "
                              f"pend54={pend} acc=0x{acc:x} ind={ind} "
                              f"slot{k}: cls={cls} item={it} flags=0x{fl:04x}")

if __name__ == "__main__":
    main()
