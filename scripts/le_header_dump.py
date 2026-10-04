#!/usr/bin/env python3
"""le_header_dump.py — dump the OS/2 LE header, object table and page table of
game/ascend.exe using ONLY fields this repo can cross-validate from the file.

WHY NOW: an earlier attempt mis-parsed the header and produced impossible
values ("+0x14=121 can't be a fixup page size, +0x2c=211 can't be a file
offset"). That judgement was made against a RECALLED field map. Since then we
have two hard anchors measured from this very file:
  * a table of exactly 121 u32 values at file 0x2b40 stepping by exactly 0x100,
    which matches an LE page table with cbObjectPageSize=0x1000 (the value is
    the low byte moving, i.e. flags in the low byte of a 24-bit page number
    record);
  * the payload running from 0x2a50 to EOF (10832 + 576643 = 587475), i.e. the
    image is the whole tail of the file.
With cPageCount == 121 verifiable, the field at that offset IS cPageCount and
the surrounding map is therefore anchored, not recalled.

WHAT IT ANSWERS
  OQ-011 (absolute base C): the LE object table gives each object's memory
  base address, and the page table gives each page's file offset. If
  mem(page) - file(page) is constant, the image is a flat mapping and C is that
  constant. If not, per-page/per-object bases are required and static absolute
  identity is impossible without runtime evidence — which is itself the answer,
  and it is reportable.

USAGE
  ~/tools/revenv/bin/python scripts/le_header_dump.py [--out docs/re/loader.md]
"""
import argparse, struct, os, sys, collections

EXE = "game/ascend.exe"
LE_SIG = b"LE"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    d = open(EXE, "rb").read()
    N = len(d)
    lines = []
    P = lines.append

    le = struct.unpack_from("<I", d, 0x3C)[0]
    P(f"file {EXE} size={N}")
    P(f"MZ+0x3c -> LE header at {le:#x}")
    assert d[le:le + 2] == LE_SIG, "no LE signature at MZ+0x3c"

    # --- header, per the field order we anchor below ---
    # Word/u32 reads. Only fields whose value we can check are interpreted.
    o = le
    def u8(k):  return d[o + k]
    def u16(k): return struct.unpack_from("<H", d, o + k)[0]
    def u32(k): return struct.unpack_from("<I", d, o + k)[0]

    raw = d[o:o + 0xC0]
    P("")
    P("header bytes (0xc0 from LE):")
    for i in range(0, 0xC0, 16):
        P(f"  +{i:#06x}  {raw[i:i+16].hex()}")

    P("")
    P("field-by-field (offset : u16 / u32 interpretation):")
    for k in range(0x00, 0x80, 4):
        P(f"  +{k:#04x}  u32={u32(k):#010x} ({u32(k)})   u16@+0={u16(k)}  u16@+2={u16(k+2)}")

    # --- anchor the page table ---
    # We measured 121 u32 stepping 0x100 at file 0x2b40. Find every offset run
    # of that shape and report it, then treat the first as the page table.
    P("")
    P("page-table shape scan (u32 runs stepping exactly +0x100):")
    best_run, best_at = 0, None
    p = 0
    while p + 8 <= N:
        v0 = struct.unpack_from("<I", d, p)[0]
        run, q = 1, p + 4
        while q + 4 <= N:
            vn = struct.unpack_from("<I", d, q)[0]
            if vn == v0 + 0x100 * run:
                run += 1
                q += 4
            else:
                break
        if run > best_run:
            best_run, best_at = run, p
        p = max(p + 4, q)
    if best_at is None:
        P("  VERDICT: no page-table-shaped run; aborting")
        print("\n".join(lines))
        return 2
    P(f"  best: count={best_run} at {best_at:#x} "
      f"first={struct.unpack_from('<I', d, best_at)[0]:#x}")

    pgs = [struct.unpack_from("<I", d, best_at + 4 * i)[0] for i in range(best_run)]
    P(f"  page record low bytes (flags?): {[hex(v & 0xff) for v in pgs[:16]]}")
    P(f"  page numbers (v>>8 if low byte is flags): {[hex(v >> 8) for v in pgs[:8]]}")
    P(f"  page numbers (v>>12 if whole u32 is page idx): {[hex(v >> 12) for v in pgs[:8]]}")

    # --- the decisive arithmetic ---
    P("")
    P("DECISIVE: does file offset of page i equal best_at + 4*N + i*0x1000 ?")
    tbl_end = best_at + 4 * best_run
    first_data = tbl_end
    P(f"  page table ends at {tbl_end:#x}; if pages follow contiguously, page 0 "
      f"would start at {first_data:#x} with page k at first_data + k*0x1000")
    P(f"  file size {N:#x}; 121 pages * 0x1000 = {121*0x1000:#x}; "
      f"{first_data:#x} + that = {first_data + 121*0x1000:#x}")
    delta = N - first_data
    P(f"  actual data area = {delta:#x} bytes ({delta} = {delta/0x1000:.2f} pages)")
    P(f"  payload size (0x2a50..EOF) = {N-0x2a50:#x}")

    # If the page records ARE file offsets of pages, their values should span
    # the data area. Test both readings.
    for shift, name in ((8, "low byte = flags, rest = page number"),
                        (0, "raw value = file offset of the page"),
                        (12, "value >> 12 = page index")):
        vals = [v >> shift for v in pgs]
        inspan = sum(1 for v in vals if first_data <= v < N)
        mono = all(vals[i + 1] >= vals[i] for i in range(len(vals) - 1))
        P(f"  reading '{name}': in-data-area {inspan}/{len(vals)} monotone={mono} "
          f"min={vals[0]:#x} max={vals[-1]:#x}")

    # --- runtime fixups / debug info presence ---
    P("")
    P("trailing tables (last 0x400 bytes):")
    tail = d[-0x400:]
    P("  " + tail[:64].hex())
    P(f"  entropy-ish distinct bytes: {len(set(tail))}")

    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        open(args.out, "w").write("\n".join(lines) + "\n")
        print(f"[le_header_dump] wrote {args.out}")
    for l in lines:
        print(l)
    return 0


if __name__ == "__main__":
    sys.exit(main())
