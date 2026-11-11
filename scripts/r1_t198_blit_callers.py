#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t198 — BLIT-CALLER CENSUS with per-function module attribution.

Purpose (OQ-005 / planet-screen paint routine hunt): enumerate EVERY E8
call site of the shape blit FUN_0005caac over the whole restored image
(t83 counted 75 sites in 32 functions via a different tool; Ghidra's
get_function_callers only reports 15 because of unanalysed regions), and
attribute each enclosing function to the vendor module whose debug path
string that function references.

Image facts this relies on (docs/STATE.md, docs/re/shp.md S11/S12):
  * work/ascend_restored.bin is a base-0 image: IMAGE ADDRESS == FILE OFFSET.
  * obj0 code span [0x14bb0, 0x82bb0); obj1 data pool [0x82bb0, 0x8cc83).
  * In the RESTORED image a string reference immediate is the UNRELOCATED
    pool-relative value: imm = str_off - 0x82BB0  (STATE "DATA-FILE STRING ->
    LOADER ROUTE", caveat 1).  So attribution maps a code immediate back to
    a string by S = imm + 0x82BB0.
  * Vendor debug paths are literal "..\\module.cpp" strings in the data pool.

No candidate search, no guessing: pure enumeration + attribution, printed as
a tsv.  Usage: r1_t198_blit_callers.py [--target 5caac]
"""
import sys, re, collections

IMG = "work/ascend_restored.bin"
POOL = 0x82BB0
CODE_LO, CODE_HI = 0x14BB0, 0x82BB0


def load(path=IMG):
    with open(path, "rb") as f:
        return f.read()


def debug_strings(img):
    """{image_addr: module} for every literal '..\\xxx.cpp' / 'xxx.txt'."""
    out = {}
    for m in re.finditer(rb"\.\.\\\\([A-Za-z0-9_]{2,24})\.cpp\x00", img):
        out[m.start()] = m.group(1).decode()
    # the restored image may store single backslash; try that too
    for m in re.finditer(rb"\.\.\\([A-Za-z0-9_]{2,24})\.cpp\x00", img):
        out.setdefault(m.start(), m.group(1).decode())
    return out


def function_table():
    """work/functions_full.tsv -> sorted [(start, end)] (file_off == image addr)."""
    fns = []
    with open("work/functions_full.tsv") as f:
        hdr = f.readline()
        for line in f:
            p = line.split("\t")
            try:
                s = int(p[0], 16)
                n = int(p[1], 16) if len(p) > 1 and p[1].strip() else 0
            except ValueError:
                continue
            fns.append((s, s + max(n, 1)))
    fns.sort()
    return fns


def bisect_fn(fns, addr):
    lo, hi = 0, len(fns) - 1
    best = None
    while lo <= hi:
        mid = (lo + hi) // 2
        s, e = fns[mid]
        if s <= addr < e:
            return s, e
        if addr < s:
            hi = mid - 1
        else:
            lo = mid + 1
    return None


def main():
    target = 0x5CAAC
    for i, a in enumerate(sys.argv):
        if a == "--target":
            target = int(sys.argv[i + 1], 16)
    img = load()
    strs = debug_strings(img)
    # imm -> module  (pool-relative immediates as they appear in the restored image)
    imm2mod = {}
    for addr, mod in strs.items():
        imm2mod[addr - POOL] = mod
    fns = function_table()

    code = img[CODE_LO:CODE_HI]
    sites = []
    # fast byte pass first: E8 xx xx xx xx little-endian rel32 == target - (addr+5)
    want = target
    i = 0
    n = len(code)
    cand = []
    while i < n - 5:
        if code[i] == 0xE8:
            rel = int.from_bytes(code[i + 1:i + 5], "little", signed=True)
            a = CODE_LO + i
            if a + 5 + rel == want:
                cand.append(a)
            i += 5
        else:
            i += 1

    # attribute enclosing functions
    byfn = collections.defaultdict(list)
    for a in cand:
        r = bisect_fn(fns, a)
        key = r[0] if r else a
        byfn[key].append((a, r))

    print(f"target={target:#x} sites={len(cand)} functions={len(byfn)}")
    rows = []
    for key in sorted(byfn):
        r = bisect_fn(fns, key)
        s, e = r if r else (key, key + 1)
        # module vote: every instruction's 4-byte LE window that maps to a debug string
        vote = collections.Counter()
        j = s
        while j < e - 4:
            v = int.from_bytes(img[j:j + 4], "little")
            if v in imm2mod and 0x1000 < v < 0x40000:
                vote[imm2mod[v]] += 1
            j += 1
        if not vote:  # fall back: absolute image-address references to strings
            j = s
            while j < e - 4:
                v = int.from_bytes(img[j:j + 4], "little")
                if v in strs:
                    vote[strs[v]] += 1
                j += 1
        mod = vote.most_common(3)
        rows.append((s, e, len(byfn[key]), mod[0][0] if mod else "?",
                     ",".join(f"{m}:{c}" for m, c in mod[:3])))
    print("fn_start\tfn_end\tblit_sites\tmodule\tvotes")
    for s, e, k, m, v in rows:
        print(f"{s:#x}\t{e:#x}\t{k}\t{m}\t{v}")


if __name__ == "__main__":
    main()
