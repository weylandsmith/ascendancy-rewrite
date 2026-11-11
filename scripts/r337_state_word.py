#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t337 census: the CURRENT-STATE word u16 @ core+0x4228 in .sav Memory.

Law (all cited this iteration, docs/re/_wip_t337.md S2-S4):
  core object = 0x7a35c (pointer-law constant; fn 0x54650 called as
  `mov eax,0x7a35c; call` ships.md:1778; 0x56e10 SET-STATE same base 0x21733).
  dword core+0x4226: LOW u16 = distinct-group count (`inc WORD` 0x57207 /
  `dec WORD` 0x5711e); HIGH u16 = core+0x4228 = CURRENT STATE ID
  (sole runtime writer 0x56f66 `mov WORD PTR [esi+0x4228],di` inside fn
  0x56e10; boot call 0x21733 edx=0; hotkey 0x54d92 edx=2 / 0x54dba edx=4).
  STATE table: count u16 @ core+0x3068+0x8e*id, 32 u32 handles @
  core+0x306a+0x8e*id (fn 0x57194; t336 census located W=0x2bc3e4 196/196).

Method: locate core base B by the SAME exact-membership fingerprint as
scripts/r336d_state_census.py (treat base as unknown; group id k's slot array
at B+0x3068+0x8e*k must equal windows.txt group k verbatim). Then MEASURE:
  - u16 @ B+0x4228 per save (current state) -> distribution over the corpus
  - u16 @ B+0x4226 (group count) -> expect 18 where t336 measured it
  - consistency: for state s measured, group-s slot count>0 and all handles
    resolve to names (the state's windows are resident)
Exit 0 = ran; prints per-value histogram.
"""
import os, re, struct, sys, zipfile, glob, collections

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


def find_base(mem, per_id):
    L = len(mem)
    hname = {}
    for mo in re.finditer(MAGIC, mem):
        b = mo.start()
        if b + 0x120 > L:
            continue
        nm = mem[b + 0x20:b + 0x40].split(b"\x00")[0]
        if not (1 <= len(nm) <= 24 and all(32 <= c < 127 for c in nm)):
            continue
        hname.setdefault(mem[b + 0x41], nm.decode("ascii", "replace"))
    pre = re.compile(b"..[\x01-\x20]\x00", re.DOTALL)
    votes = collections.Counter()
    for m in pre.finditer(mem):
        off = m.start() + 2
        cnt = mem[off]
        if off + 2 + 128 > L:
            continue
        vals = struct.unpack_from("<32I", mem, off + 2)
        nz = vals[:cnt]
        if any(v not in hname for v in nz) or any(v != 0 for v in vals[cnt:]):
            continue
        for k, members in per_id.items():
            if len(members) == cnt and [hname[v] for v in nz] == members:
                votes[off - CNT_OFF - STRIDE * k] += 1
    if not votes:
        return None, None, hname
    B = votes.most_common(1)[0][0]
    return B, votes[B], hname


def main():
    per_id = file_truth()
    dirs = [os.path.join(ROOT, "work", "r1", "playcap", "save")]
    for pat in ("dbg-t332-*/save", "t299-leg-*/save", "dbg-t331-*/save"):
        for d in sorted(glob.glob(os.path.join(ROOT, "work", "r1", pat))):
            if d not in dirs:
                dirs.append(d)
    hist = collections.Counter()
    base_hist = collections.Counter()
    tot = located = 0
    resid_ok = 0
    rows = []
    for d in dirs:
        for f in sorted(x for x in os.listdir(d) if x.endswith(".sav"))[:12]:
            path = os.path.join(d, f)
            tot += 1
            try:
                mem = zipfile.ZipFile(path).read("Memory")
            except Exception as e:
                rows.append((os.path.basename(path), "ERR", str(e)))
                continue
            B, votes, hname = find_base(mem, per_id)
            if B is None:
                rows.append((os.path.basename(path), "UNLOCATED", ""))
                continue
            located += 1
            base_hist[hex(B)] += 1
            gc = struct.unpack_from("<H", mem, B + 0x4226)[0]
            st = struct.unpack_from("<H", mem, B + 0x4228)[0]
            hist[st] += 1
            # residency consistency: state's group has count>0 and all handles resolve
            off = B + CNT_OFF + STRIDE * st if st < 0x20 else None
            ok = None
            if off is not None and off + 2 + 128 <= len(mem):
                cnt = struct.unpack_from("<H", mem, off)[0]
                vals = [struct.unpack_from("<I", mem, off + 2 + 4 * t)[0] for t in range(min(cnt, 32))]
                ok = cnt > 0 and all(v in hname for v in vals)
                if ok:
                    resid_ok += 1
            rows.append((path, hex(B), f"groups={gc} state={st} resident={ok}"))
    print(f"savedir-caps 12/dir; total={tot} located={located}")
    print("core base histogram:", dict(base_hist))
    print("CURRENT-STATE u16 histogram:", dict(sorted(hist.items())))
    print(f"state-group residency OK: {resid_ok}/{located}")
    for r in rows[:40]:
        print("  ", r)
    print("STATE-16 saves:")
    for r in rows:
        if "state=16" in r[2]:
            print("  ", r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
