#!/usr/bin/env python3
"""tNG-C mutation campaign (cycle 2). Laws docs/re/t423-newgame-law.md
SS14-SS16; pins rewrite/tests/test_newgame_content_tNGC.cpp (+ the t401
chip-constant checks). Catcher classes:
  "tests"   — constant mutants caught by run_tests;
  "witness" — draw-site mutants caught by scripts/r1_tA3_capture.sh +
              scripts/r1_tNGC_chip_witness.py (ramp ink / frame count).
One mutant at a time: apply (anchor EXACTLY once) -> rebuild -> catch ->
restore from the pristine snapshot taken AT LAUNCH -> md5-verify, ABORT on
mismatch. LAUNCH GUARD: snapshot only on a green suite (poisoned-snapshot
lesson, r1_ta3_mutate.py). Usage: r1_tNGC_mutate.py [mutant-name ...]
"""
import hashlib
import os
import os.path as osp
import shutil
import subprocess as sp
import sys

ROOT = "/home/hrethric/projects/ascendancy"
ML = osp.join(ROOT, "rewrite/src/ui/menulaw.h")
VT = osp.join(ROOT, "rewrite/src/ui/vendortext.cpp")
TC = osp.join(ROOT, "rewrite/src/ui/title.cpp")

# (name, file, old, new, catcher)
MUTANTS = [
    ("M1-chipx0", ML,
     "inline constexpr int kPlayerChipX0 = 381, kPlayerChipPitch = 16,",
     "inline constexpr int kPlayerChipX0 = 384, kPlayerChipPitch = 16,",
     "tests"),
    ("M2-chipy", ML,
     "                     kPlayerChipY = 433, kPlayerChipW = 15,",
     "                     kPlayerChipY = 434, kPlayerChipW = 15,",
     "tests"),
    ("M3-ramp-shift", VT,
     "    return slot + 4 * family;",
     "    return slot + 4;",
     "tests"),
    ("M4-ramp-domain", VT,
     "    if (slot < 16 || slot > 19) return slot;  // navy 242 + strays: identity",
     "    if (slot < 16 || slot > 20) return slot;  // navy 242 + strays: identity",
     "tests"),
    ("M5-frame-top", ML,
     "inline constexpr int kChipFrameTop = 434, kChipFrameBottom = 458;",
     "inline constexpr int kChipFrameTop = 435, kChipFrameBottom = 458;",
     "tests"),
    ("M6-frame-bottom", ML,
     "inline constexpr int kChipFrameTop = 434, kChipFrameBottom = 458;",
     "inline constexpr int kChipFrameTop = 434, kChipFrameBottom = 459;",
     "tests"),
    ("M7-planet-anchor", ML,
     "inline constexpr Pt kDescPlanetCentre{406, 217};",
     "inline constexpr Pt kDescPlanetCentre{401, 218};",
     "tests"),
    ("M8-species-domain", ML,  # menulaw.cpp actually; fixed below
     "", "", "tests"),
    ("M10-family-zero", TC,
     "                        blitShapePalRamp(ren, raceflagLib, selIndex,\n"
     "                                         cx + cr.left, kPlayerChipY + cr.top,\n"
     "                                         k);",
     "                        blitShapePalRamp(ren, raceflagLib, selIndex,\n"
     "                                         cx + cr.left, kPlayerChipY + cr.top,\n"
     "                                         0);",
     "witness"),
    ("M11-frame-off", TC,
     "                    if (k == playerColourIdx) {",
     "                    if (k == -1) {",
     "witness"),
]
# M8 lives in menulaw.cpp (function body, not the header).
MUTANTS[7] = ("M8-species-domain", osp.join(ROOT, "rewrite/src/ui/menulaw.cpp"),
              "            if (value < 3 || value > 7) return -1;\n            return 2 + value;",
              "            if (value < 2 || value > 8) return -1;\n            return 2 + value;",
              "tests")


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def run_tests_caught():
    r = sp.run(["ctest"], cwd=osp.join(ROOT, "rewrite/build"),
               capture_output=True, text=True, timeout=900)
    out = r.stdout + r.stderr
    # ctest exit code is the authority. NEVER substring "tests failed":
    # the passing line "0 tests failed out of 1" contains it (tNGC bug).
    failed = r.returncode != 0
    return failed, out.strip().splitlines()[-3:] if out else [], r.returncode


def build():
    r = sp.run(["cmake", "--build", ".", "-j8"],
               cwd=osp.join(ROOT, "rewrite/build"),
               capture_output=True, text=True, timeout=900)
    return r.returncode == 0


def capture_witness_caught():
    env = dict(os.environ, OUT="/tmp/tNGC_mut_shots", DISP=":99")
    sp.run(["bash", osp.join(ROOT, "scripts/r1_tA3_capture.sh")],
           capture_output=True, text=True, timeout=300, env=env)
    r = sp.run(["/home/hrethric/tools/revenv/bin/python",
                osp.join(ROOT, "scripts/r1_tNGC_chip_witness.py"),
                "/tmp/tNGC_mut_shots/newgame.png"],
               capture_output=True, text=True, timeout=120)
    return r.returncode != 0, (r.stdout or "").strip().splitlines()[-4:]


PRISTINE = {}


def snapshot():
    caught, last, rc = run_tests_caught()
    if caught:
        print("LAUNCH-GUARD: suite NOT green at launch:", last, rc,
              "— ABORT (tree may hold an applied mutant)")
        sys.exit(4)
    for f in {m[1] for m in MUTANTS}:
        PRISTINE[f] = md5(f)
    print("snapshot:", {osp.basename(k): v[:8] for k, v in PRISTINE.items()},
          flush=True)


def apply_mutant(m):
    _, f, old, new, _ = m
    s = open(f).read()
    if s.count(old) != 1:
        print(f"ANCHOR ERROR {m[0]}: {s.count(old)} matches"); return False
    open(f, "w").write(s.replace(old, new))
    os.utime(f)  # force rebuild
    return True


def restore():
    for f, h in PRISTINE.items():
        shutil.copyfile(f + ".pristine", f)
        os.utime(f)
        if md5(f) != h:
            print("RESTORE MD5 MISMATCH", f); sys.exit(3)


def main():
    names = sys.argv[1:]
    ms = [m for m in MUTANTS if not names or m[0] in names]
    snapshot()
    for f in PRISTINE:
        shutil.copyfile(f, f + ".pristine")
    results = []
    for m in ms:
        name, f, old, new, catcher = m
        print(f"== {name} ({catcher})", flush=True)
        if not apply_mutant(m):
            results.append((name, "ANCHOR-ERROR")); continue
        if not build():
            print("BUILD FAILED for", name)
            restore()
            results.append((name, "BUILD-FAIL")); continue
        if catcher == "tests":
            caught, last, rc = run_tests_caught()
        else:
            caught, last = capture_witness_caught()
        print("  ", "CAUGHT" if caught else "SURVIVED", last, flush=True)
        restore()
        results.append((name, "CAUGHT" if caught else "SURVIVED"))
    build()  # green binary back on disk
    # game/ integrity is the gate's job (checksum stage); our own restores
    # are md5-verified inside restore().
    print("RESULTS:")
    surv = 0
    for n, s in results:
        print(f"  {n:<22} {s}")
        if s != "CAUGHT":
            surv += 1
    for f in PRISTINE:
        try:
            os.remove(f + ".pristine")
        except OSError:
            pass
    sys.exit(1 if surv else 0)


if __name__ == "__main__":
    main()
