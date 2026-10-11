# tmp dump: worlds whose last save has an active Factory with zero active
# neighbours per r1_built_cell_law geometry; print full row map + actives.
import sys, os, glob, struct as st, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
import r1_income_law as IL
import r1_built_cell_law as B

IMG = 0x1BF450
pay = open("work/ascend_payload.bin", "rb").read()
anch = build_anchors(pay)
for run in sorted(glob.glob("work/r1/*")):
    if not os.path.isdir(run):
        continue
    files = sorted(glob.glob(run + "/save/*.sav"), key=os.path.getmtime)
    if not files:
        continue
    f = files[-1]
    try:
        m = zipfile.ZipFile(f).read("Memory")
    except Exception:
        continue
    votes, _ = find_base(m, anch)
    if not votes:
        continue
    base = votes.most_common(1)[0][0]
    B.HH = base - IMG
    for rec in IL.find_records(m):
        rb = rec[0]
        if m[rb + 0x57] == 0xFF:
            continue
        ptr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
        surf = st.unpack_from("<H", m, rb + 0x18)[0]
        capw = st.unpack_from("<H", m, rb + 0x1a)[0]
        name = m[rb + 0x24:m.index(b"\x00", rb + 0x24)].decode("cp437", "replace")
        act = {k: m[ptr + 4 * k + 1] for k in range(min(capw, 200))
               if st.unpack_from("<H", m, ptr + 4 * k + 2)[0] & 1}
        facs = [k for k, v in act.items() if v == 1 and k < surf]
        hit = any(B.active_neighbours(m, rb, ptr, surf, k) == 0 for k in facs)
        if not (facs and hit):
            continue
        print(f"== {run}/{os.path.basename(f)} {name} ptype={m[rb+0x14]} "
              f"surf={surf} capw={capw} pop={st.unpack_from('<H',m,rb+0x42)[0]}")
        cum = 0
        for r in range(15):
            w = m[B.HH + 0x744A8 + m[rb + 0x14] * 15 + r]
            if w == 0:
                continue
            cells = []
            for c in range(w):
                k = cum + c
                terr = m[ptr + 4 * k]
                it = m[ptr + 4 * k + 1]
                a = st.unpack_from("<H", m, ptr + 4 * k + 2)[0]
                x = c + m[B.HH + 0x7445C + m[rb + 0x14] * 15 + r]
                tag = "?" if it == 0xFF else f"{it}{'*' if a & 1 else ''}"
                cells.append(f"x{x}:{terr}{tag}")
            cum += w
            print(f"  r{r:2d} w{w:2d} " + " ".join(cells))
