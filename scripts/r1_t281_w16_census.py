#!/usr/bin/env python3
"""t281 — MEASURE word[planet_rec + 0x16] (+0x16 = the [p+0x16]==10 skip key of
SA_Cornucopia 0x43de4) over the static planet pool in TWO campaign lineages.

Pool law [verified t105/t248]: base 0x2b057 (Ghidra data addr), stride 123,
count = hi16 of ds-dword 0x3a091 (==145). Member index = B + 0x82bb0 + X
(pointer-index corollary; STATE.md). Fields: owner byte +0x57 (0xFF unowned),
pop word +0x42, skip-word word +0x16, surface word +0x18.

Prints: value histogram of +0x16 over ALL records and over OWNED records
(owner != 0xFF, the init-signature set == the 7 home planets per t248), plus
per-value owned breakdown. RC=0 always unless the anchor/base fails.
"""
import os, re, struct, sys, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = 136  # dosbox-x 2025.02.01 header; re-derive per build (STATE law)

def census(path):
    z = zipfile.ZipFile(path)
    m = z.read("Memory")
    # base via the item-table name anchor (r1_t105_verify pattern): the
    # spaced row-0 name sits at corollary addr 0x82bb0+0x73e40+8.
    hits = [mo.start() - (0x82bb0 + 0x73e40 + 8)
            for mo in re.finditer(rb"\x1e\x00Factory", m)]
    if len(set(hits)) != 1:
        print(f"  {path}: anchor not unique/unfound ({len(set(hits))} votes) -- SKIP")
        return
    B = hits[0]
    def idx(X, n):
        return m[B + 0x82BB0 + X: B + 0x82BB0 + X + n]
    cnt = struct.unpack("<H", idx(0x3a091 + 2, 2))[0]  # hi16 of dword
    hist_all, hist_own = {}, {}
    rows = []
    for i in range(cnt):
        rec = idx(0x2b057 + 123 * i, 0x7b)
        if len(rec) < 0x7b:
            print(f"  REC {i}: SHORT"); continue
        v16 = struct.unpack("<H", rec[0x16:0x18])[0]
        own = rec[0x57]
        pop = struct.unpack("<H", rec[0x42:0x44])[0]
        name = rec[0:12].split(b"\x00")[0].decode("cp437", "replace")
        hist_all[v16] = hist_all.get(v16, 0) + 1
        if own != 0xFF:
            hist_own[v16] = hist_own.get(v16, 0) + 1
            rows.append((i, v16, own, pop, name))
    print(f"\n== {os.path.basename(os.path.dirname(path))}/{os.path.basename(path)} base=0x{B:x} count={cnt}")
    print("  +0x16 hist ALL  :", dict(sorted(hist_all.items())))
    print("  +0x16 hist OWNED:", dict(sorted(hist_own.items())), f"(n={sum(hist_own.values())})")
    for r in rows:
        print(f"    rec{r[0]:3d} v16={r[1]:2d} owner={r[2]} pop={r[3]:3d} {r[4]}")

for p in (sys.argv[1:] or [
        os.path.join(ROOT, "work/r1/bank-t1254/41.sav"),
        os.path.join(ROOT, "work/r1/bank-t273-tutorial645/41.sav")]):
    census(p)
