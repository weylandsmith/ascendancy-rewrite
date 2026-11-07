#!/usr/bin/env python3
"""r334_parse_map.py — t334 windows.txt PARSE-FIELD MAP (zero capture).

Builds the file->field map of the winmgr windows.txt parser fn 0x575e4
(work/r331_disasm.txt, body 0x575e4..0x597ff) by enumerating EVERY
`call 0x77fe1` site and resolving, per site:
  - the pushed keyword constant (small constants <0x10000 are OFFSETS INTO THE
    RESIDENT windows.txt TEXT — windows.txt is 42,478 B and ascend_restored.bin
    at those addresses is CODE, so they cannot be image pointers; measured
    t334, and it also explains t333's keyword-literal ZERO result);
  - whether a STATUS read `mov eax,DWORD PTR [esp+0x3a6] ; sar $0x10 ;
    cmp eax,IMM` guards the site within 40 insns above (note: NO instruction
    in the fn body WRITES [esp+0x3a6] — measured t334; it is caller-inherited
    stack, so its value at 0x57d18/0x57e14 is a PARSE-RESULT left by 0x77fba);
  - the first store to a NON-ESP-based field after the call (window-record
    field write of the parsed value).
KEY MEASURED SITES (verbatim):
  0x57d18/0x57d22 STATUS==0x19 -> call 0x57d3d -> 0x57d56
      `mov DWORD PTR [eax+0xab],0xffffffff`   POISON (only if parsed != 0)
  0x57e14/0x57e1e STATUS==0xf  -> call 0x57e39 -> 0x57e48
      `mov DWORD PTR [edx+0xab],eax`          COPY parsed u32 verbatim
  0x58ae8/0x58b26 WORD ds:0x13b98 bounds the 0x31d58 enablement loop 0x58aff.
Law reused: NEVER json-load the timeline; static-only, exit 0 = map printed.
"""
import re, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIS = os.path.join(ROOT, "work", "r331_disasm.txt")
WTXT = os.path.join(ROOT, "extracted", "ascend00", "windows.txt")
FN_LO, FN_HI = 0x575e4, 0x597ff


def load():
    out = []
    for l in open(DIS, errors="replace"):
        m = re.match(r"\s+([0-9a-f]+):\t?\s*(.*)", l)
        if m:
            a = int(m.group(1), 16)
            if FN_LO <= a <= FN_HI:
                out.append((a, m.group(2).strip()))
    return out


def kw_context(raw, off, w=26):
    if off is None or off >= len(raw):
        return ""
    seg = raw[max(0, off - 14):off + w]
    return seg.decode("latin-1").replace("\r", "\\r").replace("\n", "\\n")


PUSH = re.compile(r"push +(0x[0-9a-f]+)$")
FIELD_STORE = re.compile(r"mov +(DWORD|WORD) PTR \[(e[a-z]+)\+?(0x[0-9a-f]+)\],")


def main():
    raw = open(WTXT, "rb").read()
    body = load()
    sites = [i for i, (a, t) in enumerate(body) if "call   0x77fe1" in t]
    print(f"parse fn body insns={len(body)}  call-0x77fe1 sites={len(sites)}")

    rows = []
    for i in sites:
        a, _ = body[i]
        consts = []
        j = i - 1
        while j >= 0 and i - j < 14:
            t = body[j][1]
            m = PUSH.search(t)
            if m:
                consts.append(int(m.group(1), 16))
            if t.startswith("call"):
                break
            j -= 1
        smalls = [c for c in consts if c < 0x10000]
        kw = smalls[0] if smalls else None
        # status guard: look above for the trio load/sar/cmp on esp+0x3a6
        guard = None
        k = i - 1
        while k >= 0 and i - k < 40:
            t = body[k][1]
            if "esp+0x3a6]" in t:
                # find the cmp imm within the next 3 insns below k
                for m3 in range(k, min(k + 4, i)):
                    mm = re.search(r"cmp +eax,(0x[0-9a-f]+)", body[m3][1])
                    if mm:
                        guard = int(mm.group(1), 16)
                        break
                break
            k -= 1
        # first non-esp field store after the call (within 12 insns)
        store = None
        saddr = None
        for m3 in range(i + 1, min(i + 13, len(body))):
            t = body[m3][1]
            ms = FIELD_STORE.search(t)
            if ms and ms.group(2) != "esp":
                store = t
                saddr = body[m3][0]
                break
        rows.append((a, kw, guard, saddr, store))

    n_kw = sum(1 for r in rows if r[1] is not None)
    n_st = sum(1 for r in rows if r[4] is not None)
    n_gd = sum(1 for r in rows if r[2] is not None)
    print(f"sites: keyword-const={n_kw}/{len(rows)}  field-store-after={n_st}  status-guarded={n_gd}")

    print("\n== [1] ALL sites whose post-call store touches window offset 0xab ==")
    hit = 0
    for a, kw, guard, saddr, store in rows:
        if store and "+0xab]" in store:
            hit += 1
            print(f"  call 0x{a:05x} kw_off={hex(kw) if kw else '-'} guard={guard} "
                  f"store@0x{saddr:05x}: {store}")
            print(f"      windows.txt@kw: {kw_context(raw, kw)!r}")
    if not hit:
        print("  (none — 0xab stores are NOT in the post-call window of any 0x77fe1 site)")

    print("\n== [2] ALL status-guarded sites (STATUS high-half == imm) ==")
    for a, kw, guard, saddr, store in rows:
        if guard is not None:
            print(f"  call 0x{a:05x} STATUS=={guard} kw={hex(kw) if kw else '-'} "
                  f"store={'0x%05x ' % saddr if saddr else ''}{store or ''}")

    print("\n== [3] FULL MAP keyword->field (sites with both, all) ==")
    for a, kw, guard, saddr, store in rows:
        if kw is not None and store:
            print(f"  0x{a:05x} kw@0x{kw:x} {kw_context(raw, kw, 20)!r} => {store}")

    print("\n== [4] sites with keyword but NO non-esp store within 12 insns ==")
    c = 0
    for a, kw, guard, saddr, store in rows:
        if kw is not None and store is None:
            c += 1
            if c <= 25:
                print(f"  0x{a:05x} kw@0x{kw:x} {kw_context(raw, kw, 20)!r}")
    print(f"  total: {c}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
