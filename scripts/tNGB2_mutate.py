#!/usr/bin/env python3
"""tNG-B cycle-2 mutation campaign (B2 species wheel -> player-count seam).
Laws docs/re/_wip_tNGB.md 'B2 SPECIES ARM FULL DECODE'; pins
rewrite/tests/test_newgame_behavior_tNGB.cpp (tngb_species_rank_cycle).
Catcher classes:
  "tests"   — caught by run_tests (exit code ONLY);
  "witness" — caught by tNGB_species_shot.sh + tNGB_species_witness.py;
  "anchor"  — caught by tNGB_species_shot.sh + tNGB_b3_anchor.py (spec0).
One mutant at a time: apply (anchor EXACTLY once) -> rebuild -> catch ->
restore from the pristine snapshot taken AT LAUNCH (COPY revert) ->
md5-verify, ABORT on mismatch. LAUNCH GUARD: green suite only.
Usage: tNGB2_mutate.py [names...]
"""
import hashlib
import os
import os.path as osp
import shutil
import subprocess as sp
import sys

ROOT = "/home/hrethric/projects/ascendancy"
ML = osp.join(ROOT, "rewrite/src/ui/menulaw.h")
TC = osp.join(ROOT, "rewrite/src/ui/title.cpp")
SNAP = "/tmp/tNGB2_mutate_snap"

MUTANTS = [
    # S1: wrap TERM [0x52e6b] — off-by-one: 7->8 becomes observable.
    ("S1-species-wrap-term", ML,
     "    return v >= 8 ? 3 : v;",
     "    return v > 8 ? 3 : v;",
     "tests"),
    # S2: wrap VALUE [0x52e6d mov word[+0xb9],3] — resets to 4 not 3.
    ("S2-species-wrap-value", ML,
     "    return v >= 8 ? 3 : v;",
     "    return v >= 8 ? 4 : v;",
     "tests"),
    # S3: the species arm wrongly runs the density REGEN (wheelGen bumps,
    # galaxy rebuilt) — positions-preserved law must catch it on the log
    # (wheelgen != 0 + h15 moves) and the density-panel pixel leg.
    ("S3-species-click-regen", TC,
     "                            speciesSetting = speciesRankNext(speciesSetting);\n                            colourLcg = 0x12e10u;  // seam: per-click reseed",
     "                            speciesSetting = speciesRankNext(speciesSetting);\n                            rebuildWheelGalaxy(densityIdx, ++wheelGen);\n                            colourLcg = 0x12e10u;  // seam: per-click reseed",
     "witness"),
    # S4: the screen default wrongly Seven (the pre-B2 value) — the word
    # sequence shifts (Five,Three,Four,Six) AND the wheel art is k9 where
    # the refcap shows k7 [window-init 0x52c55].
    ("S4-default-seven", TC,
     "    int speciesSetting = 5;",
     "    int speciesSetting = 7;",
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
    for f in (ML, TC):
        shutil.copy2(f, osp.join(SNAP, osp.basename(f)))
        os.utime(f, None)
    return {f: md5(f) for f in (ML, TC)}


def restore(pristine):
    for f in (ML, TC):
        shutil.copy2(osp.join(SNAP, osp.basename(f)), f)
        os.utime(f, None)
        if md5(f) != pristine[f]:
            sys.exit(f"RESTORE MD5 MISMATCH {f} — ABORTING campaign")


def species_catch(anchor_only):
    """CAUGHT == catcher exit != 0 (rc!=0 law for EVERY class)."""
    r = sh("bash scripts/tNGB_species_shot.sh")
    if "SHOTS" not in r.stdout:
        return True, "capture failed: " + r.stdout[-200:] + r.stderr[-200:]
    if anchor_only:
        w = sh("~/tools/revenv/bin/python scripts/tNGB_b3_anchor.py "
               "/tmp/tNGB_species/spec0.png")
    else:
        w = sh("~/tools/revenv/bin/python scripts/tNGB_species_witness.py "
               "/tmp/tNGB_species")
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
            print(f"{name}: tests rc={r.returncode} -> "
                  f"{'CAUGHT' if caught else 'MISSED'} {first}")
        else:
            caught, first = species_catch(catcher == "anchor")
            print(f"{name}: {catcher} -> "
                  f"{'CAUGHT' if caught else 'MISSED'} {first}")
        verdicts.append((name, "CAUGHT" if caught else "MISSED"))
        restore(pristine)
    b = sh("cmake --build rewrite/build -j8")
    r = sh("rewrite/build/run_tests")
    print(f"AFTER-RESTORE rc={r.returncode} build={b.returncode}")
    for f in (ML, TC):
        print("md5-ok" if md5(f) == pristine[f] else f"MD5-DRIFT {f}", f)
    n_caught = sum(1 for _, v in verdicts if v.startswith("CAUGHT"))
    print("VERDICTS:", verdicts)
    print(f"MUTATION {n_caught}/{len(verdicts)} CAUGHT")


if __name__ == "__main__":
    main()
