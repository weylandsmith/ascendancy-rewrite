#!/usr/bin/env python3
"""t326 PRE-RUN OFFLINE CENSUS (zero capture).

Two questions that decide the t326 shape BEFORE spending any launch:
  (1) does the production campaign's race-0 ALREADY own restree row 13
      (Molecular^Explosives, the Phase Bomb ResReq)?
  (2) does any production ship carry gizmo cidx 70 (Phase^Bomb)?

Laws used (all previously cited, NOT re-derived):
  - known-tech mask law: cheat body 0x47828 verbatim (docs/re/debugflags.md
    + work/t91_code_disasm.txt): mask byte for tech row i at
    ds:0x7478e + 0x4b*i, bit (1<<race); count word ds:0x74744 (=66 in play,
    OQ-013). Save member = B + 0x82bb0 + X (t297-A).
  - prereq lists: extracted/ascend00/restree.txt rows after the count line,
    255-terminated (OQ-013 row law).
  - ship rows base B+0x82bb0+0x3a095 stride 0x162, count u32@0x43489>>16
    clamped 0x6b, owner hi16 dword[+0x54] < 20 (t101/t185); gizmo ring
    ship+0xab + 7*i, cidx u8 @+0 (0xff empty), 25 slots (t184).
  - cidx 70 == 'Phase^Bomb' by gizmos.txt file order (counted after the '#'
    marker: 76 names, index 70 lands on Phase^Bomb; same law family as
    r1_t185_magnetron_census.py's cidx-60 verdict).
Exit 0 = census complete; 2 = harness broken.
"""
import glob, struct, zipfile, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import r1_sav_scan as SS

def restree_rows():
    rows = []
    started = False
    for ln in open(os.path.join(ROOT, "extracted/ascend00/restree.txt"),
                   errors="replace"):
        parts = ln.split()
        if not parts:
            continue
        if parts[0] == "66":
            started = True
            continue
        if not started:
            continue
        nums = []
        ok = True
        for x in parts[1:]:
            if not x.isdigit():
                ok = False
                break
            nums.append(int(x))
        if not ok or len(nums) < 2:
            continue
        pre = []
        for n in nums[2:]:
            if n == 255:
                break
            pre.append(n)
        rows.append((parts[0], pre))
    return rows[:66]


def main():
    pay = open(os.path.join(ROOT, "work/ascend_payload.bin"), "rb").read()
    anch = SS.build_anchors(pay)
    saves = sorted(glob.glob(os.path.join(ROOT, "work/r1/playcap/save/*.sav")),
                   key=os.path.getmtime)
    if not saves:
        print("harness: production ring empty")
        return 2
    p = saves[-1]
    mem = zipfile.ZipFile(p).read("Memory")
    votes, _ = SS.find_base(mem, anch)
    if not votes:
        print("harness: base fail")
        return 2
    B = votes.most_common(1)[0][0]
    DB = B + 0x82BB0
    print(f"save={os.path.basename(p)} B=0x{B:x}")

    rows = restree_rows()
    print(f"restree rows parsed: {len(rows)}")
    names = {i: rows[i][0] for i in range(len(rows))}
    print(f"row13 = {names.get(13)!r}")

    cnt = struct.unpack_from("<H", mem, DB + 0x74744)[0]
    masks = [mem[DB + 0x7478E + 0x4B * i] for i in range(66)]
    print(f"research count word = {cnt}")
    print("masks rows 0..20:", [hex(m) for m in masks[:21]])

    # semantic validation of mask==known-tech: prereq closure per race,
    # IN-PLAY rows only (prereq index >= 66 references a variant row that is
    # never loaded per OQ-013 6c — those edges are excluded, honest note).
    tot = viol = 0
    open_edges = collections.Counter()
    for i in range(len(rows)):
        for r in range(8):
            if (masks[i] >> r) & 1:
                for q in rows[i][1]:
                    if q >= 66:
                        open_edges[q] += 1
                        continue
                    tot += 1
                    if not (masks[q] >> r) & 1:
                        viol += 1
                        print(f"  VIOLATION tech {i} {names[i]!r} race {r} "
                              f"prereq {q} {names.get(q)!r} not owned")
    print(f"prereq-closure (in-play edges): {tot} checks, {viol} violations")
    if open_edges:
        print(f"edges to never-loaded variant rows (excluded): {dict(open_edges)}")

    print(f"row13 mask = 0x{masks[13]:02x} -> races "
          f"{[r for r in range(8) if (masks[13] >> r) & 1]}")

    # cidx-70 carriage census
    n = min(struct.unpack_from("<I", mem, DB + 0x43489)[0] >> 16, 0x6B)
    kinds = collections.Counter()
    carriers = []
    for k in range(n):
        rb = DB + 0x3A095 + k * 0x162
        own = struct.unpack_from("<I", mem, rb + 0x54)[0] >> 16
        if own >= 20:
            continue
        kinds[(own, mem[rb + 0x58])] += 1
        for i in range(25):
            if mem[rb + 0xAB + 7 * i] == 70:
                nm = mem[rb + 0x0C:rb + 0x20].split(b"\x00")[0] \
                    .decode("cp437", "replace")
                carriers.append((k, own, nm, i))
    print(f"ship rows: {n}")
    print("owner0 kind histogram:",
          {k[1]: v for k, v in sorted(kinds.items()) if k[0] == 0})
    print("cidx-70 carriers:", carriers if carriers else "ZERO")
    return 0


if __name__ == "__main__":
    sys.exit(main())
