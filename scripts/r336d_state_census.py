#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t336 census: winmgr STATE-ID table in .sav Memory (fn 0x57194 law).

Layout (fn 0x57194 verbatim; stride geometry self-consistent 0x3066..0x30f4):
  count u16 @ winmgr + 0x3068 + 0x8e*id   (high half of dword read +0x3066)
  32 x u32 handle slots @ winmgr + 0x306a + 0x8e*id (fill order = registration
  order = windows.txt file order; removal = remover fn 0x57284)
Window HANDLE (probe-measured 41.sav): u16 @ record+0x40 >> 8 == byte@+0x41,
unique 1..115 across the 115 magic+NAME records (the code's [ebp+0x41]).
Truth = ON-DISK extracted/ascend00/windows.txt.
Exit 0 = measured.
"""
import os, re, struct, sys, zipfile, collections, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAGIC = b"\x78\x56\x34\x12"
STRIDE = 0x8e
CNT_OFF = 0x3068


def file_truth():
    wt = open(os.path.join(ROOT, "extracted", "ascend00",
                           "windows.txt"), "rb").read().decode("latin-1").replace("\r", "")
    names = list(re.finditer(r"(?m)^NAME\s+(\S+)", wt))
    per_id = collections.defaultdict(list)
    for i, m in enumerate(names):
        seg = wt[m.end(): names[i + 1].start() if i + 1 < len(names) else len(wt)]
        s = re.search(r"(?m)^STATE\s+(\d+)((?:\s+\d+)*)", seg)
        if s:
            for v in [int(x) for x in s.group(2).split()]:
                per_id[v].append(m.group(1))
    return per_id


def census(path, per_id, verbose=False):
    mem = zipfile.ZipFile(path).read("Memory")
    L = len(mem)
    recs = []
    for mo in re.finditer(MAGIC, mem):
        b = mo.start()
        if b + 0x120 > L:
            continue
        nm = mem[b + 0x20:b + 0x40].split(b"\x00")[0]
        if not (1 <= len(nm) <= 24 and all(32 <= c < 127 for c in nm)):
            continue
        h = mem[b + 0x41]          # handle = BYTE at record+0x41 ([ebp+0x41] low byte)
        recs.append((b, nm.decode("ascii", "replace"), h))
    hname = {}
    for b, nm, h in recs:
        hname.setdefault(h, nm)
    runs = []
    pre = re.compile(b"..[\x01-\x20]\x00", re.DOTALL)
    for m in pre.finditer(mem):
        off = m.start() + 2
        cnt = mem[off]
        if off + 2 + 128 > L:
            continue
        vals = struct.unpack_from("<32I", mem, off + 2)
        nz = vals[:cnt]
        if any(v not in hname for v in nz):
            continue
        if any(v != 0 for v in vals[cnt:]):
            continue
        runs.append((off, cnt, [hname[v] for v in nz]))
    # exact-membership match to file ids -> consistent winmgr base
    ws = collections.Counter()
    for off, cnt, names in runs:
        for k, members in per_id.items():
            if len(members) == cnt and names == members:
                ws[off - CNT_OFF - STRIDE * k] += 1
    best = ws.most_common(1)
    res = {"save": os.path.basename(path), "nrec": len(recs),
           "runs": len(runs), "W": hex(best[0][0]) if best else None,
           "ids_ok": best[0][1] if best else 0, "ids_total": len(per_id)}
    if verbose and best:
        W = best[0][0]
        for k in sorted(per_id):
            off = W + CNT_OFF + STRIDE * k
            cnt = struct.unpack_from("<H", mem, off)[0]
            vals = [struct.unpack_from("<I", mem, off + 2 + 4 * t)[0]
                    for t in range(min(cnt, 32))]
            got = [hname.get(v, f"?{v:x}") for v in vals]
            exp = per_id[k]
            mark = "OK " if got == exp else "XX "
            print(f"  {mark}id {k:2d} cnt={cnt} got={got[:5]} exp={exp[:5]}")
    return res


def main():
    per_id = file_truth()
    dirs = [os.path.join(ROOT, "work", "r1", "playcap", "save")]
    for pat in ("dbg-t332-*/save", "t299-leg-*/save", "dbg-t331-*/save"):
        for d in sorted(glob.glob(os.path.join(ROOT, "work", "r1", pat))):
            if d not in dirs:
                dirs.append(d)
    dirs = dirs[:20]
    ok = 0
    tot = 0
    w_hist = collections.Counter()
    id_ok_hist = collections.Counter()
    # per-id agreement, measured at the located W (per-save W from census() is
    # authoritative). Classes: exact | appended (file list is a prefix; runtime
    # CreateWindow calls joined the group) | substituted (slots rewritten in
    # place -- the window at that registration slot is a different window).
    per_id_seen = collections.Counter()
    per_id_exact = collections.Counter()
    per_id_prefix = collections.Counter()
    per_id_subst = collections.Counter()
    cls_hist = collections.Counter()
    for d in dirs:
        for f in sorted(x for x in os.listdir(d) if x.endswith(".sav"))[:12]:
            path = os.path.join(d, f)
            r = census(path, per_id, verbose=False)
            tot += 1
            if r["ids_ok"]:
                ok += 1
                w_hist[r["W"]] += 1
                id_ok_hist[r["ids_ok"]] += 1
                mem = zipfile.ZipFile(path).read("Memory")
                Wloc = int(r["W"], 16)
                hname = {}
                for mo in re.finditer(MAGIC, mem):
                    b = mo.start()
                    if b + 0x120 > len(mem):
                        continue
                    nm = mem[b + 0x20:b + 0x40].split(b"\x00")[0]
                    if not (1 <= len(nm) <= 24 and all(32 <= c < 127 for c in nm)):
                        continue
                    hname.setdefault(mem[b + 0x41], nm.decode("ascii", "replace"))
                save_cls = []
                for k in sorted(per_id):
                    off = Wloc + CNT_OFF + STRIDE * k
                    cnt = struct.unpack_from("<H", mem, off)[0]
                    got = [hname.get(v, "?") for v in
                           (struct.unpack_from("<I", mem, off + 2 + 4 * t)[0]
                            for t in range(min(cnt, 32)))]
                    exp = per_id[k]
                    per_id_seen[k] += 1
                    if got == exp:
                        per_id_exact[k] += 1
                        save_cls.append("exact")
                    elif got[:len(exp)] == exp:
                        per_id_prefix[k] += 1
                        save_cls.append("appended")
                    else:
                        per_id_subst[k] += 1
                        save_cls.append("substituted")
                cls_hist[tuple(sorted(set(save_cls)))] += 1
    print("per-id at located W  (exact / file-list-is-prefix / substituted):")
    for k in sorted(per_id):
        print(f"  id {k:2d}: {per_id_exact[k]:3d}/{per_id_seen[k]}  "
              f"prefix={per_id_prefix[k]:3d}  subst={per_id_subst[k]:3d}  "
              f"file_n={len(per_id[k])}")
    print("\nsave-level class mix:")
    for cls, n in cls_hist.most_common():
        print(f"  {n:4d} saves: {list(cls)}")
    print(f"\nVERDICT saves_with_state_table={ok}/{tot} W_hist={dict(w_hist)} "
          f"ids_ok_hist={dict(id_ok_hist)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
