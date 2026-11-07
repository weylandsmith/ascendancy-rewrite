#!/usr/bin/env python3
"""t329: Lane Magnetron (design idx 60) carriage census for the OQ-019
disposition packet.

Question the packet must answer honestly: is the magnetron's "one witnessed
use" residue merely an ABSENCE problem (ships never carried it) or a
WITNESS-CLASS problem (ships carried it, sessions ran, use never happened /
never reached a commit edge)?

Laws used (all previously cited, NOT re-derived):
  - loaded design table member B + 0x82bb0 + 0x7650c stride 0x6a (t87/t101);
    base B via unique '\\x1e\\x00Factory' needle at +0x82bb0+0x73e40+8 (t101/t184).
  - ship rows base B+0x82bb0+0x3a095 stride 0x162, count u32@0x43489>>16
    clamped 0x6b, owner = hi16 dword[+0x54] < 20 (t101/t185).
  - gizmo ring ship+0xab + 7*i, cidx u8 @+0 (0xff empty), 25 slots (t184).
  - cidx 60 == 'Lane Magnetron' in the LOADED table == file order
    (scripts/r1_t185_magnetron_census.py VERDICT, re-run green t329).

Exit 0 = census complete (whatever the counts are); 2 = harness broken.
"""
import struct, os, sys, zipfile, re, glob, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "work", "r1")
NEEDLE = rb"\x1e\x00Factory"
OFF = 0x82bb0 + 0x73e40 + 8

# Named dirs only (no full work/r1 walk — t265 OOM-era law: bounded inputs).
PROD = [os.path.join(BASE, "playcap", "save")]
SCRATCH = sorted(glob.glob(os.path.join(BASE, "t261-drive", "save")) +
                 glob.glob(os.path.join(BASE, "t288-probe-*", "save")))


def census_dir(d):
    saves_ok = 0
    slots60 = 0
    owners = collections.Counter()
    shiprows = 0
    for f in sorted(os.listdir(d)):
        if not f.endswith(".sav"):
            continue
        try:
            m = zipfile.ZipFile(os.path.join(d, f)).read("Memory")
        except Exception:
            continue
        hits = {mo.start() - OFF for mo in re.finditer(NEEDLE, m)}
        if len(hits) != 1:
            continue
        B = hits.pop()
        g = lambda X: B + 0x82bb0 + X
        n = min(struct.unpack_from("<I", m, g(0x43489))[0] >> 16, 0x6b)
        saves_ok += 1
        shiprows += n
        for k in range(n):
            r = g(0x3a095) + k * 0x162
            own = struct.unpack_from("<I", m, r + 0x54)[0] >> 16
            if own >= 20:
                continue
            for i in range(25):
                if m[r + 0xab + 7 * i] == 60:
                    slots60 += 1
                    owners[own] += 1
    return saves_ok, shiprows, slots60, dict(owners)


def main():
    print("PRODUCTION corpus (playcap/save, the t=1086 sitting):")
    s, rows, c60, own = census_dir(PROD[0])
    print(f"  saves={s} ship_rows={rows} cidx60_slots={c60} owners={own}")
    prod_zero = (c60 == 0)
    print("\nSCRATCH self-drive epochs that DID carry magnetrons:")
    scratch_had = 0
    for d in SCRATCH:
        s, rows, c60, own = census_dir(d)
        print(f"  {os.path.relpath(d, BASE):55s} saves={s:2d} cidx60_slots={c60:4d} owners={own}")
        scratch_had += c60
    print("\nVERDICT:", end=" ")
    if prod_zero and scratch_had > 0:
        print("ABSENCE in the production sitting, but PRESENCE (owner 0) in the "
              "t261/t288 drive epochs where use-frame mining (t265/t273) still "
              "returned ZERO uses -> witness-class problem, not absence-only.")
    elif prod_zero:
        print("absent everywhere censusable.")
    else:
        print("production carries magnetrons -> packet premise WRONG, re-open.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
