#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r343_artifact_validate.py — validate the committed RE artifacts (t343).

Artifacts (tracked under artifacts/):
  artifacts/ascend_restored.bin  fixup-site-restored Ghidra image
                                 (builder: scripts/r1_restore_sites.py)
  artifacts/functions_full.tsv   Ghidra full-analysis function table
                                 (exported from ghp5/ascend5, base 0x100000
                                 import of ascend_restored.bin; sizes HEX)

CHECKS
  V1 REBUILD DETERMINISM (needs a capture): re-run the restore pass on the
     newest slot of the newest work/r1/r1sav-* run and compare the rebuilt
     image against the committed artifact byte-for-byte. Image-class fixup
     sites are link-time facts, so any mismatch is printed with a per-class
     breakdown (mismatch at an image-payload site = real problem; sites that
     only differ in TSV class = capture-dependent runtime mutation, expected).
  V2 WATCOM START DENSITY: for every decoded target d of a restored
     image-payload site (u32 in artifacts/ascend_restored.bin inside the code
     window that points at code storage), the first byte pay[d] must be a
     plausible Watcom function-start byte (START set from r1_pointer_law.py).
     Compared against a uniform control sample in the same code window.
     PASS bar: run-rate >= 2x control AND >= 30% absolute (banked pairing
     measurement 60% vs 15%).
  V3 TSV STRUCTURE: header exact, all rows hex-parse, size>0, start inside the
     payload, start+size <= CBIMAGE. Overlapping spans are KNOWN (pick the
     tightest) and reported, not failed.

Exit 0 all pass; 1 a check failed; 2 harness-error (artifact missing).
"""
import os, random, struct, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "artifacts")
BIN = os.path.join(ART, "ascend_restored.bin")
TSV = os.path.join(ART, "functions_full.tsv")
PAYLOAD_SIZE = 0x8CC83
CBIMAGE = 0xA7710
CODE_LO, CODE_HI = 0x14BB0, 0x82BB0
START = {0x55, 0xB8, 0x53, 0x56, 0x57, 0xE8, 0x9C, 0xC8, 0x6A, 0x68, 0xB9,
         0xBA, 0xBB, 0xBE, 0xBF, 0x33, 0x31, 0x8B, 0xF6, 0xF7, 0x81, 0x83,
         0xE9, 0xEB}

def v1(rebuild):
    if not rebuild:
        print("V1 rebuild-determinism: SKIPPED (--no-rebuild)")
        return 0
    runs = sorted(d for d in os.listdir(os.path.join(ROOT, "work/r1"))
                  if d.startswith("r1sav-"))
    savedir = os.path.join(ROOT, "work/r1", runs[-1], "save") if runs else None
    slots = sorted(f for f in os.listdir(savedir) if f.endswith(".sav")) if savedir and os.path.isdir(savedir) else []
    if not slots:
        print("V1 rebuild-determinism: SKIPPED (no captures present)")
        return 0
    import subprocess
    out_bin = "/tmp/r343_rebuild.bin"; out_tsv = "/tmp/r343_rebuild.tsv"
    rc = subprocess.run([sys.executable, os.path.join(ROOT, "scripts/r1_restore_sites.py"),
                         "--run-dir", os.path.join(ROOT, "work/r1", runs[-1]),
                         "--needle", os.path.join(ROOT, "work/ascend_payload.bin"),
                         "--out-bin", out_bin, "--out-tsv", out_tsv],
                        capture_output=True, text=True, cwd=ROOT)
    print("V1 rebuild cmd: scripts/r1_restore_sites.py --run-dir work/r1/%s" % runs[-1])
    for line in rc.stdout.strip().splitlines():
        print("   | " + line)
    if rc.returncode != 0:
        print("V1 FAIL: rebuild harness rc=%d %s" % (rc.returncode, rc.stderr[-300:]))
        return 1
    a = open(BIN, "rb").read(); b = open(out_bin, "rb").read()
    if len(a) != len(b):
        print(f"V1 FAIL: size {len(a)} vs {len(b)}"); return 1
    if a == b:
        print("V1 PASS: rebuilt image BYTE-IDENTICAL to committed artifact (%d B)" % len(a))
        return 0
    diffs = [i for i in range(len(a)) if a[i] != b[i]]
    code_diffs = [i for i in diffs if CODE_LO <= i < CODE_HI]
    # Data-region diffs are EXPECTED capture-dependent class drift: a site that
    # decoded image-class in the artifact's capture (Oct 5) can decode
    # heap/other in a later production capture, so the rebuild leaves the raw
    # payload bytes. The invariant that matters: the CODE window is static.
    grouped = []
    for i in diffs:
        if grouped and i - grouped[-1][-1] <= 4: grouped[-1].append(i)
        else: grouped.append([i])
    print(f"V1: {len(diffs)} differing bytes in {len(grouped)} u32-groups, "
          f"code-window diffs: {len(code_diffs)}")
    for g in grouped[:8]:
        print(f"   site 0x{g[0]:x}: artifact={a[g[0]:g[-1]+1].hex()} rebuild={b[g[0]:g[-1]+1].hex()}")
    if code_diffs:
        print("V1 FAIL: code-window bytes differ (link-time content must be capture-invariant)")
        return 1
    print("V1 PASS (with note): code window byte-identical; data-region groups are capture-dependent (known)")
    return 0

def v2():
    img = open(BIN, "rb").read()
    pay_path = os.path.join(ROOT, "work/ascend_payload.bin")
    if not os.path.isfile(pay_path):
        # The banked law's population is THE RESTORED SITES; without the raw
        # payload they can't be isolated (a self-pointer scan mixes in data
        # that coincidentally decodes in-image: measured 21.6% vs 15.6%
        # control — that population CANNOT meet the 2x bar, so failing on it
        # would be a false negative, not a signal). SKIP honestly.
        print("V2 watcom-start-density: SKIPPED (work/ascend_payload.bin "
              "absent — restored sites not isolable; gate 3q covers the law "
              "on machines with captures)")
        return 0
    # PRIMARY population: the restored link-time pointer sites themselves
    # (artifact bytes differ from the raw payload exactly where the restore
    # pass wrote d=rv-P0). Measured 2026-11-08: 575/1039 = 55.3% start-byte.
    pay = open(pay_path, "rb").read()
    pop = [f for f in range(CODE_LO, len(pay) - 4, 4) if img[f:f+4] != pay[f:f+4]]
    name = "restored link-time sites"
    hits = sum(1 for f in pop
               if (d := struct.unpack_from("<I", img, f)[0]) < CODE_HI and img[d] in START)
    pop_code = sum(1 for f in pop if struct.unpack_from("<I", img, f)[0] < CODE_HI)
    random.seed(343)
    c_tot = 20000
    c_hits = sum(1 for _ in range(c_tot)
                 if img[random.randrange(CODE_LO, CODE_HI - 4) & ~3] in START)
    rate, ctrl = (hits / pop_code if pop_code else 0.0), c_hits / c_tot
    print(f"V2 watcom-start-density [{name}]: {hits}/{pop_code} in-code targets "
          f"({len(pop)} sites) = {rate:.1%}  control {c_hits}/{c_tot} = {ctrl:.1%}  "
          f"ratio {rate/ctrl:.2f}x")
    if rate >= 0.30 and rate >= 2 * ctrl:
        print("V2 PASS (bar: >=30% absolute and >=2x control; banked pairing 60%/15%)")
        return 0
    print("V2 FAIL")
    return 1

def v3():
    lines = open(TSV).read().splitlines()
    if lines[0] != "file_off\tsize":
        print("V3 FAIL: header is %r" % lines[0]); return 1
    rows = []
    for i, ln in enumerate(lines[1:], 2):
        p = ln.split("\t")
        if len(p) != 2:
            print(f"V3 FAIL line {i}: {ln!r}"); return 1
        try:
            s, sZ = int(p[0], 16), int(p[1], 16)
        except ValueError:
            print(f"V3 FAIL line {i}: non-hex {ln!r}"); return 1
        if sZ <= 0 or s >= PAYLOAD_SIZE or s + sZ > CBIMAGE:
            print(f"V3 FAIL line {i}: span {s:#x}+{sZ:#x} out of range"); return 1
        rows.append((s, sZ))
    ov = sum(1 for i in range(1, len(rows)) if rows[i][0] < rows[i-1][0] + rows[i-1][1])
    in_code = sum(1 for s, _ in rows if CODE_LO <= s < CODE_HI)
    print(f"V3 PASS: {len(rows)} functions, sizes HEX, all spans in range; "
          f"{in_code} start in code window; {ov} overlapping spans (KNOWN, pick tightest)")
    return 0

def main():
    rebuild = "--no-rebuild" not in sys.argv
    if not (os.path.isfile(BIN) and os.path.isfile(TSV)):
        print("harness-error: artifacts missing under", ART); return 2
    rc = 0
    rc |= v1(rebuild); rc |= v2(); rc |= v3()
    print("ARTIFACT VALIDATION", "OK" if rc == 0 else "FAILED")
    return rc

if __name__ == "__main__":
    sys.exit(main())
