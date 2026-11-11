#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t87 (W6-A2c): gizmos.txt column -> design-record map, settled RIGHT.

Legs:
  1. FILE  parse extracted/ascend00/gizmos.txt the way the EXE loader
     FUN_00049074 does: skip '#' lines, per row "%s" then
     "%d %d %d %d %d %d %d %d %d" then flag-list "%d" loop (255-terminated).
  2. CODE  loader store sites (verified disasm this session):
        name  -> rec+0
        col1 Cat      -> BYTE  +0x32   (S+0xc8)
        col2 Power    -> DWORD +0x36
        col3 Range    -> DWORD +0x3a
        col4 Level    -> DWORD +0x3e
        col5 NumUses  -> DWORD +0x42
        col6 Industry -> DWORD +0x46
        col7 Special1 -> DWORD +0x4a
        col8 Special2 -> DWORD +0x4e
        col9 ResReq   -> BYTE  +0x35   (S+0xe8)
        flag bits     -> WORD  +0x33
     Post-pass 0x4923a zeroes +0x52,+0x56,+0x5a,+0x5e,+0x62,+0x66 then the
     Cat jump table 0x344b0 copies Level(+0x3e) or Power(+0x36) into ONE of
     them per category.
  3. LIVE  read the static design table 0x7650c + 0x6a*g (g=0..75) out of a
     held-turn autosave via the pointer law (member = B + 0x82bb0 + X),
     names anchored at rec+0, and compare EVERY field against the file.

Exit 0 only if names 76/76 AND the full 9-column map matches 76/76 (or
reports the exact mismatch set). Usage: r1_t87_gizmo_table.py [SAV]
"""
import sys, os, zipfile, struct
from collections import Counter

ROOT = "/home/hrethric/projects/ascendancy"
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import r1_sav_scan  # find_base(mem, anchors) -> (votes, positions)

H = 136          # dosbox-x 2025.02.01 SAV member header (re-derive per build)
TABLE = 0x7650c  # design table Ghidra addr (stride 0x6a, 76 rows)
NROWS = 76
FIELDS = [("+0x32 cat", 0x32, 1), ("+0x35 resreq", 0x35, 1),
          ("+0x36 power", 0x36, 4), ("+0x3a range", 0x3a, 4),
          ("+0x3e level", 0x3e, 4), ("+0x42 numuses", 0x42, 4),
          ("+0x46 industry", 0x46, 4), ("+0x4a sp1", 0x4a, 4),
          ("+0x4e sp2", 0x4e, 4), ("+0x33 flags", 0x33, 2)]


def parse_file(path):
    """Replicate FUN_00049074 row semantics: '#' skip, tokenless-line skip,
    NAME line then its 9-int line (+ flag list, 255-terminated)."""
    lines = []
    for ln in open(path, "rb"):
        s = ln.decode("cp437", "replace").strip()
        if not s or s.startswith("#"):
            continue
        lines.append(s)

    def ints(s):
        try:
            return [int(x) for x in s.split()]
        except ValueError:
            return None

    out = []
    i = 0
    while i < len(lines) - 1:
        nums = ints(lines[i + 1])
        if nums and len(nums) >= 9:
            name = lines[i].replace("^", " ")
            vals = nums
            flags = []
            j = 9
            while j < len(vals) and vals[j] != 255:
                flags.append(vals[j])
                j += 1
            out.append(dict(name=name, cat=vals[0], power=vals[1],
                            range=vals[2], level=vals[3], numuses=vals[4],
                            industry=vals[5], sp1=vals[6], sp2=vals[7],
                            resreq=vals[8], flags=flags, raw=nums))
            i += 2
        else:
            i += 1
    return out


def load_sav(path):
    if open(path, "rb").read(2) != b"PK":
        raise SystemExit(f"{path}: not a dosbox SAV zip (raw dump?) — use save/NN.sav")
    z = zipfile.ZipFile(path)
    return z.read("Memory")


def main():
    sav = sys.argv[1] if len(sys.argv) > 1 else \
        os.path.join(ROOT, "work/r1/playcap/evidence_slot04_t1254.SAV")
    frows = parse_file(os.path.join(ROOT, "extracted/ascend00/gizmos.txt"))
    print(f"file rows parsed: {len(frows)}")
    mem = load_sav(sav)
    print(f"member size {len(mem)} (0x{len(mem):x})")
    # base vote — t86 note: 'Factory' needle alone gets 0 votes on this slot;
    # use the payload-file anchors the scan script builds.
    needle = open(os.path.join(ROOT, "work/ascend_payload.bin"), "rb").read()
    anch = r1_sav_scan.build_anchors(needle)
    votes, positions = r1_sav_scan.find_base(mem, anch)
    if not votes:
        print("FATAL: base vote empty"); return 2
    B, nvotes = votes.most_common(1)[0]
    print(f"B vote = {hex(B)} ({nvotes} anchors)")

    idx = lambda X, n: mem[B + 0x82BB0 + X: B + 0x82BB0 + X + n]

    nm_ok = 0
    mismatches = []
    per_field_ok = Counter()
    for g in range(NROWS):
        rec = idx(TABLE + 0x6a * g, 0x6a)
        if len(rec) < 0x6a:
            print(f"row {g}: SHORT READ"); continue
        nm = rec.split(b"\0")[0].decode("cp437", "replace").replace("^", " ")
        f = frows[g] if g < len(frows) else None
        name_ok = f is not None and nm.strip() == f["name"].strip()
        nm_ok += name_ok
        vals = {}
        for label, off, w in FIELDS:
            raw = rec[off: off + w]
            v = raw[0] if w == 1 else (struct.unpack("<H", raw)[0] if w == 2
                                       else struct.unpack("<I", raw)[0])
            vals[label] = v
        if f:
            want = {"+0x32 cat": f["cat"], "+0x35 resreq": f["resreq"],
                    "+0x36 power": f["power"], "+0x3a range": f["range"],
                    "+0x3e level": f["level"], "+0x42 numuses": f["numuses"],
                    "+0x46 industry": f["industry"], "+0x4a sp1": f["sp1"],
                    "+0x4e sp2": f["sp2"],
                    "+0x33 flags": sum(1 << b for x in f["flags"]
                                       for b in (x,) if x != 255)}
            # flags: bits set for each listed bitpos
            fb = 0
            for b in f["flags"]:
                fb |= (1 << b)
            want["+0x33 flags"] = fb
            for label, _, _ in FIELDS:
                if vals[label] == want[label]:
                    per_field_ok[label] += 1
                else:
                    mismatches.append((g, f["name"], label, vals[label],
                                       want[label]))
        show = g in (0, 10, 36, 38, 53, 56, 57, 58, 63, 65, 69, 72, 75)
        if show or not name_ok:
            print(f"g={g:2d} {hex(0x6a*g+TABLE)} [{nm[:28]:28s}] "
                  + " ".join(f"{k.split()[0]}={v}" for k, v in vals.items()))
    print(f"\nnames: {nm_ok}/{NROWS}")
    for label, _, _ in FIELDS:
        print(f"{label:16s} match {per_field_ok[label]}/{NROWS}")
    if mismatches:
        print("\nMISMATCHES (first 40):")
        for m in mismatches[:40]:
            print(f"  g={m[0]:2d} {m[1][:24]:24s} {m[2]:14s} live={m[3]} file={m[4]}")
    ok = nm_ok == NROWS and all(per_field_ok[l] == NROWS for l, _, _ in FIELDS)
    print("\nVERDICT:", "FULL COLUMN MAP CLOSED" if ok else "PARTIAL/OPEN")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
