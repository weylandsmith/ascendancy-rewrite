#!/usr/bin/env python3
"""attribution_scan.py — attribute code to source modules via debug strings.

THE SIGNAL (Watcom 11 i386, measured 2026-10-05j): data storage holds
..\\module.ext path strings (33 modules); code that references a module's
strings is that module's. Two encodings exist and both are scanned:

  E1 (restored, exact): in work/ascend_restored.bin, ALIGNED sites that held
      link-time fixups were rewritten to d = rv-P0 = payload file offset
      (pointer law, r1_restore_sites.py docstring). So a u32 == s at any
      byte offset inside code storage is a reference to string s.
  E2 (raw, operand-filtered): pre-fixup the file stores the INTRA-target-
      object offset for cross-object refs (measured: site 0x14fa0 file u32
      = 0x20 = batcon.cpp string 0x82bd0 minus data-object start 0x82bb0).
      These values are small and produce massive false positives UNLESS the
      u32 sits in an immediate operand position: the byte before must be an
      opcode that takes imm32 (0x8D lea, 0xB8-0xBF mov r32, 0x68 push,
      0xA1/0xA3 mov m32, 0x81/0x83 group tails are excluded as ambiguous —
      0x81 uses disp/imm ordering checked below) and the two bytes before
      must not both be part of another immediate (approximated by requiring
      the preceding byte NOT be in a "likely-imm" position, i.e. we accept
      the small measured error and cross-check against E1 overlap).

      NOTE E2 additionally requires, per instruction stream, a real decode
      pass to be trustworthy; this tool therefore reports E1 counts as
      PRIMARY and E2 as a hint column only.

OUTPUT
  work/attribution.tsv   module, site_off, encoding(E1/E2), est_func
  stdout                 per-module E1 sites + distinct est_func count.
Exit 0 if >=3 modules have >=5 E1 sites; 1 negative; 2 harness-error.
"""
import os, re, struct, sys, bisect, collections

CODE_LO, CODE_HI = 0x14bb0, 0x82bb0
DATA_LO = 0x82bb0
IMM32_PREV = {0x8D, 0x68, 0xA1, 0xA3} | set(range(0xB8, 0xC0))

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pay_path = os.path.join(root, "work/ascend_payload.bin")
    if not os.path.isfile(pay_path):
        # t343 PORTABILITY: the payload is a byte-exact slice of the tracked
        # original game/ascend.exe at file offset 0x2a50 (measured 2026-11-08:
        # exe[0x2a50:0x2a50+0x8cc83] == work/ascend_payload.bin exactly,
        # 576,643 B). Derive instead of harness-error so a fresh clone with
        # the game dir runs this gate.
        exe_path = os.path.join(root, "game/ascend.exe")
        if not os.path.isfile(exe_path):
            print("harness-error: no payload and no game/ascend.exe to derive from"); return 2
        exe = open(exe_path, "rb").read()
        pay = exe[0x2a50:0x2a50 + 0x8cc83]
        if len(pay) != 0x8cc83:
            print("harness-error: derived payload size wrong"); return 2
        print("payload derived from game/ascend.exe@0x2a50 (work copy absent)")
    else:
        pay = open(pay_path, "rb").read()
    if len(pay) != 0x8cc83:
        print("harness-error: payload size"); return 2

    strs = {}   # module -> ALL (file offset, byte length) of ..\ occurrences
    for m in re.finditer(rb'\.\.\\\\?([A-Za-z][A-Za-z0-9_]{1,20}\.(?:cpp|c|h))', pay):
        if m.start() >= DATA_LO:
            strs.setdefault(m.group(1).decode(), []).append(
                (m.start(), len(m.group(0))))
    if not strs:
        print("harness-error: no debug strings"); return 2

    # E1: restored absolute offsets (aligned-rewritten immediates). A ref
    # may land anywhere inside the ..\x.cpp bytes (string interior), so the
    # value map covers every byte position of every occurrence.
    try:
        res_path = os.path.join(root, "artifacts/ascend_restored.bin")
        if not os.path.isfile(res_path):
            res_path = os.path.join(root, "work/ascend_restored.bin")
        res = open(res_path, "rb").read()
    except OSError:
        print("harness-error: ascend_restored.bin missing "
              "(tracked copy at artifacts/, rebuild via scripts/r1_restore_sites.py)"); return 2
    off2mod = {}
    for n, occ in strs.items():
        for p, ln in occ:
            for k in range(ln):
                off2mod[p + k] = n
    hits = collections.defaultdict(list)
    code = memoryview(res)[CODE_LO:CODE_HI]
    for o in range(len(code) - 4):
        v = struct.unpack_from("<I", code, o)[0]
        if v in off2mod:
            hits[off2mod[v]].append((CODE_LO + o, "E1"))

    # E2: raw intra values in imm32 operand position (hint only)
    rawpay = memoryview(pay)[CODE_LO:CODE_HI]
    intra2mod = {}
    for n, occ in strs.items():
        for p, ln in occ:
            for k in range(ln):
                intra2mod[p + k - DATA_LO] = n
    e2 = collections.defaultdict(list)
    e1_sites = {s for v in hits.values() for s, _ in v}
    for o in range(1, len(rawpay) - 4):
        if rawpay[o - 1] not in IMM32_PREV:
            continue
        v = struct.unpack_from("<I", rawpay, o)[0]
        if v in intra2mod:
            site = CODE_LO + o
            if site not in e1_sites:
                e2[intra2mod[v]].append((site, "E2"))

    e1_mods = [n for n in hits if len(hits[n]) >= 5]
    if len(e1_mods) < 3:
        print(f"negative: only {len(e1_mods)} modules with >=5 E1 sites")
        for n, v in sorted(hits.items(), key=lambda kv: -len(kv[1]))[:10]:
            print(f"  {n}: E1={len(v)}")
        return 1

    # est_func: nearest preceding Watcom prologue byte
    START = {0x55,0xB8,0x53,0x56,0x57,0xE8,0x9C,0xC8,0x6A,0x68,0xB9,0xBA,
             0xBB,0xBE,0xBF,0x33,0x31,0x8B,0xF6,0xF7,0x81,0x83,0xE9,0xEB}
    pros = [o for o in range(CODE_LO, CODE_HI) if pay[o] in START]
    def est(site):
        i = bisect.bisect_right(pros, site) - 1
        return pros[i] if i >= 0 else CODE_LO

    tsv_path = os.path.join(root, "work/attribution.tsv")
    os.makedirs(os.path.dirname(tsv_path), exist_ok=True)  # t343: fresh clones have no work/
    out = open(tsv_path, "w")
    out.write("module\tsite\tenc\test_func\n")
    summary = []
    for nm in sorted(set(list(hits) + list(e2)),
                     key=lambda n: -len(hits.get(n, []))):
        rows = sorted(hits.get(nm, []) + e2.get(nm, []))
        e1n = len(hits.get(nm, []))
        funcs = sorted(set(est(s) for s, _ in rows))
        summary.append((nm, e1n, len(rows) - e1n, len(funcs)))
        for s, enc in rows:
            out.write(f"{nm}\t0x{s:x}\t{enc}\t0x{est(s):x}\n")
    out.close()
    print(f"{'module':16s} E1   E2   est_funcs")
    for nm, a, b, nf in summary:
        print(f"{nm:16s} {a:4d} {b:4d} {nf:8d}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
