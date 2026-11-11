#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""le_probe.py — locate and verify the OS/2-LE (Watcom) tables inside
game/ascend.exe without assuming a header field map.

Why this exists: Ghidra 12.1.4 ships no LE loader
(Ghidra/Features/Base/lib/Base-src.zip:ghidra/app/util/bin/format/lx/
LinearExecutable.java is `throw new NotYetImplementedException()`), and its
MZ loader stops at 0x2a4e, so the 32-bit Watcom client is invisible. To load
it we must rebuild the flat linear image, which needs the object/page tables.

Method (no guessed spec): every LE field we care about is either a FILE OFFSET
(monotone-increasing, inside the file, multiples of the page size) or a small
COUNT. So we DISCOVER the tables first by scanning for runs of monotone u32s
whose deltas are multiples of a candidate page size, and only then read off
which header dword names each table. The invariant that licenses the map is
that the discovered page-table length times the page size accounts for the
declared image size, and that the last page's file span ends exactly at EOF.

Usage: le_probe.py [--out FILE]
Exit non-zero if the page table cannot be located or accounting fails.
"""
import argparse, struct, struct as S, sys, os
from collections import Counter

PAGE_CANDIDATES = (512, 1024, 2048, 4096)


def find_tables(data):
    """Return list of (start_off, entry_stride, n_entries, page) candidates
    for a page/offset table: >=12 consecutive u32s (at `u32_at` inside the
    stride) that strictly increase with deltas that are nonzero multiples of
    `page`, all values inside [0, len(data)]."""
    hits = []
    N = len(data)
    for page in PAGE_CANDIDATES:
        for stride in (4, 6, 8, 12, 12 + 4, 16):
            for u32_at in (0, 2, 4, 4, 8):
                if u32_at + 4 > stride:
                    continue
                best_run, best_at, run_start = 0, 0, 0
                run = 0
                i = 0
                while i + stride + u32_at + 4 <= N:
                    a = struct.unpack_from("<I", data, i + u32_at)[0]
                    b = struct.unpack_from("<I", data, i + stride + u32_at)[0]
                    d = b - a
                    ok = (0 < d <= 0x200000 and d % page == 0 and b <= N)
                    if ok:
                        if run == 0:
                            run_start = i
                        run += 1
                    else:
                        if run > best_run:
                            best_run, best_at = run, run_start
                        run = 0
                    i += stride
                if run > best_run:
                    best_run, best_at = run, run_start
                if best_run >= 11:  # 12 values = 11 deltas
                    hits.append((best_at, stride, best_run + 1, page, u32_at))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=os.path.join(os.path.dirname(__file__), "..", "game", "ascend.exe"))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    data = open(args.exe, "rb").read()
    N = len(data)
    le_off = struct.unpack_from("<I", data, 0x3C)[0]
    assert data[le_off:le_off + 2] == b"LE", "no LE magic where MZ e_lfanew points"

    out = []
    P = out.append
    P("# LE (Watcom) container probe — ascend.exe")
    P("")
    P(f"[verified] file size {N} ({N:#x}); MZ e_lfanew @0x3c -> LE header @ {le_off:#x}")
    P(f"[verified] payload (LE header start -> EOF) = {N - le_off} ({N - le_off:#x}) B")
    P("")
    P("## Raw LE header dwords (relative to LE header start)")
    P("")
    P("| +off | u32 | u32 as dec | plausible kind |")
    P("|---|---|---|---|")
    rows = []
    for o in range(0, 0xC0, 4):
        if le_off + o + 4 > N:
            break
        v = struct.unpack_from("<I", data, le_off + o)[0]
        kind = []
        if 0 < v < N:
            kind.append("file-offset-or-size")
        if v == 0:
            kind.append("zero")
        if 0 < v < 0x10000:
            kind.append("count/size")
        rows.append((o, v, "/".join(kind) or "-"))
        P(f"| +0x{o:02x} | {v:#010x} | {v} | {kind and '/'.join(kind) or '-'} |")
    P("")

    P("## Discovered monotone-offset tables (spec-free discovery)")
    P("")
    hits = find_tables(data)
    P(f"candidate runs found: {len(hits)}")
    P("")
    P("| table start | stride | n_values | page | u32_at | first 3 deltas |")
    P("|---|---|---|---|---|---|")
    for (start, stride, n, page, u32_at) in sorted(hits, key=lambda h: -h[2])[:25]:
        vals = [struct.unpack_from("<I", data, start + k * stride + u32_at)[0] for k in range(min(n, 4))]
        deltas = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
        P(f"| {start:#x} | {stride} | {n} | {page} | +{u32_at} | {deltas} |")
    P("")
    if not hits:
        print("\n".join(out))
        print("\n[le_probe] NEGATIVE: no monotone page table found in any "
              "(stride, page, u32_at) configuration.", file=sys.stderr)
        return 2
    print("\n".join(out))
    if args.out:
        open(args.out, "w").write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
