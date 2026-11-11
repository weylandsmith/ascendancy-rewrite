#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t85e: per-gate forward decode. Gate addrs come from byte-pattern scans so
they are instruction-aligned; decoding FORWARD from a gate self-syncs even
where linear sweeps misalign (dark zone). Compact report mode."""
import subprocess, re, sys

ROOT = "/home/hrethric/projects/ascendancy"
data = open(ROOT + "/work/ascend_restored.bin", "rb").read()
POOL = 0x82bb0


def pstr(v):
    if not v:
        return None
    va = POOL + v if v < 0x4000 else v
    if not (0 <= va < len(data)):
        return None
    s = data[va:va + 60].split(b"\x00")[0]
    return s.decode("latin-1") if re.fullmatch(rb"[ -~]{2,58}", s) else None


def objdump(a, b):
    out = subprocess.run(
        ["objdump", "-D", "-b", "binary", "-m", "i386", "-M", "intel",
         "--start-address", hex(a), "--stop-address", hex(b),
         "work/ascend_restored.bin"],
        capture_output=True, text=True, cwd=ROOT).stdout
    ins = []
    for ln in out.splitlines():
        m = re.match(r" *([0-9a-f]+):\t((?:[0-9a-f]{2} )+)\s+(.*)", ln)
        if m:
            ins.append((int(m.group(1), 16), m.group(3).strip()))
    return ins


def gate_report(gate, n=16, label=""):
    ins = objdump(gate, gate + 120)
    ins = [(a, t) for a, t in ins if a >= gate][:n]
    strs, calls, branch = [], [], None
    out = []
    for a, t in ins:
        ann = ""
        mm = re.search(r",\s*0x([0-9a-f]{3,6})$", t)
        if mm:
            s = pstr(int(mm.group(1), 16))
            if s:
                ann = "  ; " + repr(s)
                strs.append(s)
        cm = re.match(r"call\s+0x([0-9a-f]+)", t)
        if cm:
            calls.append(hex(int(cm.group(1), 16)))
        bm = re.match(r"(j\w+)\s+0x([0-9a-f]+)", t)
        if bm and branch is None and "ds:" in (ins[0][1] if ins else ""):
            branch = (bm.group(1), int(bm.group(2), 16))
        out.append(f"  {a:x}: {t}{ann}")
    print(f"### {gate:#x} {label} | taken-if {'flag=-1' if 'ffffffff' in ins[0][1] else 'flag==0'}")
    print("\n".join(out))
    return out, branch


if __name__ == "__main__":
    addrs = [int(x, 16) for x in sys.argv[1:]]
    for a in addrs:
        gate_report(a)
