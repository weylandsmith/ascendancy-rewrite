#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t105 STATIC PAIR probe (OQ-016-adjacent residuals named by t99 S6.4).

(b) STRIDE-45 TABLE 0x74782: hypothesis = parallel per-research-row array
    alongside the stride-75 restree RUNTIME (base 0x7478b == row base+2).
    Legs:
      B1 live words WORD[0x74782 + 45*i] for i in 0..65 (60.sav, pointer-law
         corollary member index B+0x82bb0+X); check row-i cost == restree.txt
         FILE cost (the t99 claim "live 50/90/100 for rows 0..4").
      B2 FILE-offset read of 0x74782 (expected GARBAGE per the t81 mid-turn
         trap — data-intra file bytes are pre-relocation; recorded so the
         next session doesn't re-trust it).
(a) GOVOROM race-row WORD[0x12e16 + 0x1ee*r + 0x42] for r=0..n: dump value
    + neighbours (+0x3a..+0x50) to characterise the field. Cross-check the
    restree ownership-mask dword at runtime row+0x7478b (row0 == 0x0f000000).
Self-validation: restree.txt row-0 name via stride-75 loader law on live RAM
(the restree runtime rows must carry the file's 66 names in order OR the
stride-75 runtime hypothesis is reported as failing).
Exit 0 = probes ran and printed findings (analysis decisions live in the doc).
"""
import os, re, struct, zipfile, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAV = os.path.join(ROOT, "work/r1/playcap/save/60.sav")

def load_member():
    with zipfile.ZipFile(SAV) as z:
        m = z.read("Memory")
    hits = [mo.start() - (0x82bb0 + 0x73e40 + 8)
            for mo in re.finditer(rb"\x1e\x00Factory", m)]
    if len(set(hits)) != 1:
        raise SystemExit(f"harness-error: item-table anchor not unique: {len(set(hits))}")
    return m, hits[0]

def restree_file_rows():
    """Parse game/restree.txt: 66 rows, row = name + cost-ish columns.
    We only need (name, first numeric tokens) for a cost cross-check."""
    p = os.path.join(ROOT, "extracted", "ascend00", "restree.txt")
    with open(p, "r", errors="replace") as f:
        lines = f.read().splitlines()
    rows = []
    for ln in lines:
        t = ln.replace("^", " ").split()
        if len(t) >= 2 and not t[0].isdigit():
            rows.append(t)
    return lines[0], rows

def main():
    m, B = load_member()
    print(f"B = 0x{B:x}  (item-table anchor, 60.sav)")
    idx = lambda X, n: m[B + 0x82BB0 + X: B + 0x82BB0 + X + n]

    hdr, frows = restree_file_rows()
    print(f"restree.txt header: {hdr!r}  rows={len(frows)}")

    # ---- (b) stride-45 live words
    w45 = [struct.unpack("<H", idx(0x74782 + 45 * i, 2))[0] for i in range(66)]
    print("stride45 words[0..19]:", w45[:20])
    print("stride45 words[20..65]:", w45[20:66])

    # file cost column: find which column matches w45[:5] = [50,90,100,...]
    # print first 6 file rows raw for eyeballing
    for i in range(6):
        print(f"file row {i}: {frows[i][:8]}")

    # try every column position for numeric match against w45 across all rows
    ncols = max(len(r) - 1 for r in frows)
    for c in range(1, ncols):
        hits = 0
        tot = 0
        for i in range(min(66, len(frows))):
            toks = frows[i]
            if c < len(toks):
                try:
                    v = int(toks[c]); tot += 1
                    hits += (v == w45[i])
                except ValueError:
                    pass
        if hits:
            print(f"  file column {c}: {hits}/{tot} == stride45 word")

    # ---- stride-75 runtime names check (validation of the row-base model)
    names = []
    for i in range(66):
        blob = idx(0x74789 + 75 * i, 64)  # guess: name near row start; scan
        mname = re.search(rb"[A-Za-z][A-Za-z ()'/\-]{4,29}", blob)
        names.append(mname.group(0).decode(errors="replace") if mname else None)
    match = sum(1 for i in range(min(66, len(frows)))
                if names[i] and names[i].strip().lower() in frows[i][0].lower())
    print(f"stride75@0x74789 name-in-order matches: {match}/66 (model probe)")
    # alternative: runtime rows might start at 0x7478b-2=0x74789 or elsewhere;
    # try phase scan for the row-0 name to locate the runtime row stride/base
    name0 = frows[0][0].encode()
    phases = []
    for ph in range(0, 200):
        if idx(ph, len(name0)) == name0:
            phases.append(ph)
    print("phases where row0 restree name sits:", phases[:10])

    # ---- (a) race-row +0x42
    print("\nrace rows (base 0x12e16 stride 0x1ee):")
    for r in range(6):
        rb = 0x12E16 + 0x1EE * r
        row = idx(rb, 0x1ee)
        if len(row) < 0x1ee:
            print(f"row {r}: truncated"); break
        v42 = struct.unpack("<H", row[0x42:0x44])[0]
        ability = struct.unpack("<H", row[0x19d:0x19f])[0]
        counter = struct.unpack("<H", row[0x19e:0x1a0])[0]
        nb = " ".join(f"+0x{o:02x}={struct.unpack('<H', row[o:o+2])[0]}"
                      for o in range(0x3a, 0x52, 2))
        print(f"row {r}: +0x42={v42} ability={ability} counter={counter} | {nb}")

    # ---- FILE-offset leg for 0x74782 (expected garbage; record verbatim)
    with open(os.path.join(ROOT, "work/ascend_restored.bin"), "rb") as f:
        f.seek(0x74782)
        raw = f.read(16)
    print("\nFILE bytes @0x74782 (pre-relocation, expected garbage):", raw.hex())
    return 0

if __name__ == "__main__":
    sys.exit(main())
