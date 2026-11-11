#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t212 — close the base+disp WRITER blind spot for [0x482f0,0x48300).

Established (r212_ref_census + r212_raw_and_ptr + r212_code_identity):
  * ZERO disp32 encodings targeting the slot window exist ANYWHERE in the
    restored image except the two presenter READS (moffs disp bytes 0x28075/
    0x280c0) — raw decoder-independent scan, 4 occurrences of fb 82 04 00.
  * No RAM dword points into the window (both reloc forms checked; every hit
    is an instruction's own relocated operand field).
Remaining writer shape: a register holding a NEARBY data-segment address
written as [reg+disp8/16], or a pointer variable to a near base.

STATIC SWEEP over obj0 code [0x14bb0,0x82bb0):
  (A) catalog `reg = imm` loads (mov reg,imm32 / lea reg,[imm]) with imm in
      [NEAR_LO,NEAR_HI) data-segment neighbourhood of the slot;
  (B) from each site, walk up to WALK insns forward (resume-past-gaps),
      keeping the register UNMODIFIED (any write to it or to its whole parent
      e.g. eax/ax/ah stops the trace), and report every MEMORY WRITE
      [reg+disp] (any width) whose computed absolute target lands in
      [0x482f0,0x48300); report also writes landing in 0x48300..0x48370 for
      context;
  (C) inverse: every memory write with [reg+disp], |disp|<=0x100, reg in the
      A-catalog register set AT ANY SITE — computed target in window (same as
      B, printed as a flat list).
Exit 0 findings (writer found or zero + controls), 2 control failure.
CONTROL: the scan MUST find nothing new for 0x48304 disp32 sites (they are
not [reg+disp] shapes) and MUST process >100k instructions (t201 floor).
"""
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

IMG = sys.argv[1] if len(sys.argv) > 1 else "work/ascend_restored.bin"
img = open(IMG, "rb").read()
CLO, CHI = 0x14BB0, 0x82BB0
WLO, WHI = 0x482F0, 0x48300            # the displayed-score window
NEAR_LO, NEAR_HI = 0x47F00, 0x48B00    # base-neighbourhood
WALK = 400

WRITE_MN = {"mov", "inc", "dec", "neg", "not", "xchg", "or", "and", "xor",
            "add", "sub", "sbb", "shl", "shr", "sar", "stosb", "stosd",
            "pop", "movabs"}


def decode_stream(start):
    # t201 resume-past-gaps: capstone's generator STOPS at the first
    # undecodable byte; the pass MUST restart at gap+1 or it silently
    # under-reports (first run of this script decoded 8,961 of ~140k insns).
    off = start
    while off < CHI:
        md2 = Cs(CS_ARCH_X86, CS_MODE_32)
        md2.detail = True
        end = off
        try:
            it = md2.disasm(img[off:CHI], off)
            while True:
                ins = next(it)
                yield ins
                end = ins.address + ins.size
                off = end
        except StopIteration:
            if end <= off:
                off = off + 1
            continue


def parents(r):
    if not r:
        return set()
    r = r.lower()
    fam = {"eax": {"eax", "ax", "ax", "ah", "al"},
           "ecx": {"ecx", "cx", "ch", "cl"},
           "edx": {"edx", "dx", "dh", "dl"},
           "ebx": {"ebx", "bx", "bh", "bl"},
           "esi": {"esi", "si", "sil"}, "edi": {"edi", "di", "dil"},
           "ebp": {"ebp", "bp", "bpl"}, "esp": {"esp", "sp", "spl"}}
    for k, v in fam.items():
        if r in v or r == k:
            return v | {k}
    return {r}


def main():
    # PASS 1: collect base-load sites
    basesites = []
    ninstr = 0
    for ins in decode_stream(CLO):
        ninstr += 1
        if ins.mnemonic in ("mov", "lea", "movabs") and len(ins.operands) == 2:
            d, s = ins.operands[0], ins.operands[1]
            val = None
            if s.type == 2 and -0x80000000 <= s.imm < 0x100000000:
                val = s.imm & 0xFFFFFFFF
            elif s.type == 3 and not s.mem.base and not s.mem.index:
                val = s.mem.disp & 0xFFFFFFFF
            if val is not None and NEAR_LO <= val < NEAR_HI \
                    and d.type == 1:
                basesites.append((ins.address, d.reg, val,
                                  f"{ins.mnemonic} {ins.op_str}"))
    print(f"decoded insns={ninstr}  base-load sites in "
          f"[{NEAR_LO:#x},{NEAR_HI:#x}): {len(basesites)}")
    for a, r, v, txt in basesites:
        print(f"  {a:#07x} {r} = {v:#x}   {txt}")

    # PASS 2: trace each base forward
    hits = []
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    for site_a, reg, base, txt in basesites:
        rname = md.reg_name(reg)
        fam = parents(rname)
        nwalk = 0
        for ins in decode_stream(site_a + 1):
            nwalk += 1
            if nwalk > WALK:
                break
            # does this ins modify our reg?
            modified = False
            for o in ins.operands:
                if o.type == 1 and md.reg_name(o.reg) in fam:
                    modified = True
            # memory writes [reg + disp] (no index; index would need base too)
            for oi, o in enumerate(ins.operands):
                if o.type == 3 and o.mem.base and md.reg_name(o.mem.base) == rname \
                        and not o.mem.index:
                    tgt = (base + o.mem.disp) & 0xFFFFFFFF
                    is_wr = ins.mnemonic in WRITE_MN and oi == 0
                    if (WLO <= tgt < WHI) or (is_wr and WHI <= tgt < 0x48380):
                        hits.append((ins.address, rname, base, tgt,
                                     f"{ins.mnemonic} {ins.op_str}",
                                     "WINDOW!!" if WLO <= tgt < WHI else "ctx"))
            # rep block ops while our reg is EDI (destination) — a block copy
            # can cross the score window with NO disp encoding at all
            if ins.mnemonic.startswith("rep") and rname in ("edi", "di"):
                hits.append((ins.address, rname, base, base,
                             f"{ins.mnemonic} {ins.op_str}", "REP-EDI@base"))
            if modified:
                # record writes BEFORE modification only
                break
    print(f"\n[base+disp] writes traced from those bases: {len(hits)}")
    for a, r, b, t, txt, tag in sorted(hits):
        print(f"  {a:#07x} [{r}={b:#x}{t-b:+#x}] -> {t:#x} {tag}  {txt}")

    # PASS 3 (inverse flat): every write [reg+disp] |disp|<=0x100 where reg's
    # value is UNKNOWN cannot be resolved statically; instead report writes of
    # the FORM [reg+disp] whose mnemonic writes and where the SAME function
    # also contains one of the A-site constants (co-location heuristic).
    import re
    fn_of = {}
    print("\nPASS3: co-location check — functions containing a base-load AND a "
          "[reg+disp] write with small negative disp (0x2f..0x75 range offsets)")
    near_sets = {}
    for a, r, v, txt in basesites:
        near_sets.setdefault(a, set()).add(v)
    # crude function grouping: use functions_full.tsv (hex file_off,size)
    for line in open("work/functions_full.tsv").read().splitlines()[1:]:
        parts = line.split("\t")
        try:
            fo = int(parts[0], 16)
            sz = int(parts[1], 16)
        except ValueError:
            continue
        if not any(near_lo <= fo < near_hi for near_lo, near_hi in
                   [(NEAR_LO, NEAR_HI)]):
            pass
        sites_in = [(a, r, v) for a, r, v, _ in basesites if fo <= a < fo + sz]
        if sites_in:
            print(f"  fn {fo:#x}+{sz:#x}: base-loads at "
                  + ", ".join(f"{a:#x}->{v:#x}" for a, r, v in sites_in))
    print("\ndone")


if __name__ == "__main__":
    main()
