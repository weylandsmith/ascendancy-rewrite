#!/usr/bin/env python3
"""tNG-B mutation campaign (B1 density-wheel rebuild + B3 anchors).
Laws docs/re/_wip_tNGB.md; pins rewrite/tests/test_newgame_behavior_tNGB.cpp.
Catcher classes:
  "tests"   — caught by run_tests (exit code ONLY, skill rule 1a);
  "witness" — caught by scripts/tNGB_density_shot.sh + tNGB_density_witness.py.
One mutant at a time: apply (anchor EXACTLY once) -> rebuild -> catch ->
restore from the pristine snapshot taken AT LAUNCH (COPY revert, NOT git —
uncommitted B1 work in these files) -> md5-verify, ABORT on mismatch.
LAUNCH GUARD: snapshot only on a green suite. Usage: tNGB_mutate.py [names...]
"""
import hashlib
import os
import os.path as osp
import shutil
import subprocess as sp
import sys

ROOT = "/home/hrethric/projects/ascendancy"
ML = osp.join(ROOT, "rewrite/src/ui/menulaw.h")
MC = osp.join(ROOT, "rewrite/src/ui/menulaw.cpp")
TC = osp.join(ROOT, "rewrite/src/ui/title.cpp")
SNAP = "/tmp/tNGB_mutate_snap"

MUTANTS = [
    # Wrap term (0x52dc9 cmp==5 -> 0): off-by-one wrap.
    ("M1-wrap-term", ML,
     "    return r >= kDensityCycleCount ? 0 : r;",
     "    return r > kDensityCycleCount ? 0 : r;",
     "tests"),
    # Straddle rung law: cycle-order table must equal sorted set via fn.
    ("M2-count-table", MC,
     "int densityStarCount(int rank) {\n    return kDensityStarCounts[rank >= 0 && rank < kDensityCycleCount\n                                  ? rank\n                                  : 0];",
     "int densityStarCount(int rank) {\n    return kDensityStarCounts[rank >= 0 && rank < kDensityCycleCount\n                                  ? (rank + 1) % kDensityCycleCount\n                                  : 0];",
     "tests"),
    # Off-domain guard: bad rank must fall back to rung 0, not 1.
    ("M3-guard-fallback", MC,
     "                                  : 0];",
     "                                  : 1];",
     "tests"),
    # rand-law model: seed must ride the gen counter (new set per click).
    ("M4-seed-no-gen", TC,
     "        mc.seed = wheelBaseSeed + gen;  // new set per regen (rand law)",
     "        mc.seed = wheelBaseSeed;  // new set per regen (rand law)",
     "witness"),
    # B3 anchor: density dy correction +{-1}.
    ("M5-anchor-dy", ML,
     "inline constexpr int kWheelBlitDy[3] = {-1, 0, -1};",
     "inline constexpr int kWheelBlitDy[3] = {0, 0, -1};",
     "anchor"),
    # B3 anchor: atmos dx correction {-2}.
    ("M6-anchor-dx", ML,
     "inline constexpr int kWheelBlitDx[3] = {1, 1, -2};",
     "inline constexpr int kWheelBlitDx[3] = {1, 1, 0};",
     "anchor"),
    # Preview cosmos hash: gen key term removed -> stable set across clicks
    # (pure pure fn in menulaw.h now; unit pin tngb_cosmos_hash_gen_key).
    ("M7-hash-no-gen", ML,
     "           uint64_t(gen) * 0x100000001ull;",
     "           0ull;",
     "tests"),
    # Display galaxy decoupled from the rebuild -> rendered cosmos n frozen
    # at the Average default (cosmos-n law-line witness catches it).
    ("M8-n-frozen", TC,
     "                const int n = wheelGal ? int(wheelGal->stars.size())\n                                       : kDensityStarCounts[densityIdx];",
     "                const int n = kDensityStarCounts[2];",
     "witness"),
]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def sh(cmd):
    return sp.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)


def launch_guard():
    r = sh("rewrite/build/run_tests")
    if r.returncode != 0:
        sys.exit("LAUNCH GUARD RED — suite not green, refusing to snapshot")
    os.makedirs(SNAP, exist_ok=True)
    for f in (ML, MC, TC):
        shutil.copy2(f, osp.join(SNAP, osp.basename(f)))
        os.utime(f, None)
    return {f: md5(f) for f in (ML, MC, TC)}


def restore(pristine):
    for f in (ML, MC, TC):
        shutil.copy2(osp.join(SNAP, osp.basename(f)), f)
        os.utime(f, None)  # skill rule 8b: make must see the newer content
        if md5(f) != pristine[f]:
            sys.exit(f"RESTORE MD5 MISMATCH {f} — ABORTING campaign")


def witness_catch(shots_full):
    """Capture raceconfig and run the pixel/log witness(es).
    Returns (caught, first_line). CAUGHT == witness exit != 0 (bug-1 fix:
    round 1 returned rc==0 as caught — inverted)."""
    r = sh("bash scripts/tNGB_density_shot.sh")
    if "SHOTS" not in r.stdout:
        return True, "capture failed: " + r.stdout[-200:] + r.stderr[-200:]
    if shots_full:
        w = sh("~/tools/revenv/bin/python scripts/tNGB_density_witness.py "
               "/tmp/tNGB_density")
    else:
        w = sh("~/tools/revenv/bin/python scripts/tNGB_b3_anchor.py "
               "/tmp/tNGB_density/rung0.png")
    first = next((l for l in w.stdout.splitlines()
                  if l.strip().startswith("- ")), "")
    return w.returncode != 0, first


def main():
    names = sys.argv[1:]
    todo = [m for m in MUTANTS if not names or m[0] in names]
    pristine = launch_guard()
    verdicts = []
    for name, path, old, new, catcher in todo:
        src = open(path).read()
        count = src.count(old)
        if count != 1:
            print(f"{name}: PATCH-GUARD anchor count {count} — SKIPPING")
            verdicts.append((name, "PATCH-MISS"))
            continue
        open(path, "w").write(src.replace(old, new))
        b = sh("cmake --build rewrite/build -j8")
        if b.returncode != 0:
            print(f"{name}: BUILD-FAIL (compile catches it) -> CAUGHT")
            verdicts.append((name, "CAUGHT(build)"))
            restore(pristine)
            continue
        if catcher == "tests":
            r = sh("rewrite/build/run_tests")
            caught = r.returncode != 0
            first = next((l for l in r.stdout.splitlines() if "FAIL" in l), "")
            print(f"{name}: tests rc={r.returncode} -> {'CAUGHT' if caught else 'MISSED'} {first}")
        else:
            full = catcher == "witness"  # witness=full density witness,
            caught, first = witness_catch(full)  # anchor=b3 rung0 check
            print(f"{name}: {catcher} -> {'CAUGHT' if caught else 'MISSED'} {first}")
        verdicts.append((name, "CAUGHT" if caught else "MISSED"))
        restore(pristine)
    b = sh("cmake --build rewrite/build -j8")
    r = sh("rewrite/build/run_tests")
    print(f"AFTER-RESTORE rc={r.returncode} build={b.returncode}")
    for f in (ML, MC, TC):
        print("md5-ok" if md5(f) == pristine[f] else f"MD5-DRIFT {f}", f)
    n_caught = sum(1 for _, v in verdicts if v.startswith("CAUGHT"))
    print("VERDICTS:", verdicts)
    print(f"MUTATION {n_caught}/{len(verdicts)} CAUGHT (tests class)")


if __name__ == "__main__":
    main()
