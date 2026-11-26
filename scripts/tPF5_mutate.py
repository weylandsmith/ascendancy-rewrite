#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""tPF-5 mutation campaign: prove the strip-anchor pins encode the law.

Per mutation-campaign skill: WORKING paths only, snapshot + md5-verified
restore, os.utime after every copy (stale-mtime trap 8b(i)), one mutant at a
time, verdict = run_tests EXIT CODE (never substring-match output), and each
mutant's first FAIL lines kept for the ledger.
"""
import hashlib
import os
import shutil
import subprocess
import sys

REPO = "/home/hrethric/projects/ascendancy"
PS = f"{REPO}/rewrite/src/ui/planetstrip.cpp"
UI = f"{REPO}/rewrite/src/ui/ui.cpp"
BUILD = f"{REPO}/rewrite/build"
SNAP = "/tmp/tpf5_mut_snaps"

MUTANTS = [
    ("M1 drop-L (x = rect.x0)", PS,
     "return Pt{rect.x0 + recLeft, rect.y0 + recTop};",
     "return Pt{rect.x0, rect.y0 + recTop};"),
    ("M2 drop-T (y = rect.y0)", PS,
     "return Pt{rect.x0 + recLeft, rect.y0 + recTop};",
     "return Pt{rect.x0 + recLeft, rect.y0};"),
    ("M3 sign-flip T", PS,
     "return Pt{rect.x0 + recLeft, rect.y0 + recTop};",
     "return Pt{rect.x0 + recLeft, rect.y0 - recTop};"),
    ("M4 swap L/T", PS,
     "return Pt{rect.x0 + recLeft, rect.y0 + recTop};",
     "return Pt{rect.x0 + recTop, rect.y0 + recLeft};"),
    # The ui.cpp seam: neutralise the anchor term at the call site. Short
    # anchor on purpose — the 3-line block gets reflowed by clang-format and
    # a long anchor would report a bogus ANCHOR-GUARD miss.
    ("M5 ui.cpp neutralises the anchor term", UI,
     "stripGaugeBlitPos(gr.rect, grr.left,",
     "stripGaugeBlitPos(gr.rect, 0,"),
]


sys.stdout.reconfigure(line_buffering=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def main():
    os.makedirs(SNAP, exist_ok=True)
    pristine = {}
    for path in {m[1] for m in MUTANTS}:
        pristine[path] = md5(path)
        shutil.copy2(path, f"{SNAP}/{os.path.basename(path)}.pristine")
        os.utime(path, None)

    results = []
    try:
        for name, path, old, new in MUTANTS:
            src = open(path).read()
            n = src.count(old)
            if n != 1:
                results.append((name, f"ANCHOR-GUARD count={n} (NOT applied)"))
                print(f"{name}: ANCHOR-GUARD count={n}", flush=True)
                continue
            open(path, "w").write(src.replace(old, new))
            os.utime(path, None)
            b = subprocess.run(["cmake", "--build", BUILD, "-j8"],
                               capture_output=True, text=True)
            if b.returncode != 0:
                results.append((name, "BUILD-FAIL (not a verdict)"))
                print(f"{name}: BUILD-FAIL\n{b.stderr[:800]}", flush=True)
            else:
                r = subprocess.run([f"{BUILD}/run_tests"],
                                   capture_output=True, text=True)
                fails = [ln for ln in r.stdout.splitlines()
                         if "FAIL" in ln][:6]
                verdict = "CAUGHT" if r.returncode != 0 else "MISSED"
                results.append((name, verdict))
                print(f"{name}: {verdict} (rc={r.returncode})", flush=True)
                for ln in fails:
                    print("    " + ln.strip(), flush=True)
            # restore + verify
            shutil.copy2(f"{SNAP}/{os.path.basename(path)}.pristine", path)
            os.utime(path, None)
            if md5(path) != pristine[path]:
                print(f"!! RESTORE MISMATCH {path} — ABORTING", flush=True)
                return 2
    finally:
        for path, h in pristine.items():
            shutil.copy2(f"{SNAP}/{os.path.basename(path)}.pristine", path)
            os.utime(path, None)
            assert md5(path) == h, path
    missed = [r for r in results if r[1] == "MISSED"]
    print(f"\nVERDICT: {len(results)-len(missed)}/{len(results)} CAUGHT")
    for name, v in results:
        print(f"  {name}: {v}")
    return 0 if not missed else 1


if __name__ == "__main__":
    sys.exit(main())
