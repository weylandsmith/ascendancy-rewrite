#!/usr/bin/env python3
# t428b mutation campaign: the PLANET-SCREEN STRIP law (one cited branch at a
# time), judged by run_tests. Vacuity-checked first (skill rule 5): the seed-2024
# fixture has res=0 ind=1 pros=1 pending=-1 for EVERY star, so
#   - const-0 on the RES gauge is VACUOUS (gaugeSelector(0)==0) -> M3 targets IND
#   - res/ind binding swap IS visible (gaugeSelector(0)=0 != gaugeSelector(1)=1)
#   - project +1 IS visible (-1 != 0)
# Usage: python3 t428b_mutate.py M1 M2 ...  (background/execute_code ONLY)
#
# PITFALL THIS SCRIPT EMBODIES (t428b, skill rule 8 recovery): the first version
# keyed each mutant at the SNAPSHOT path instead of the WORKING path, so it built
# the pristine file (M1 false-MISSED) and then restored the MUTATED snapshot,
# poisoning every later verdict (AFTER-RESTORE 4 failed). Guards now:
#   (1) mutants are applied to WORKING files only;
#   (2) pristine md5s are captured at snapshot time and every restore is
#       md5-verified; a mismatch aborts the campaign instead of continuing red.
import hashlib, hashlib, os, shutil, subprocess, sys, time

REPO = "/home/hrethric/projects/ascendancy"
BUILD = f"{REPO}/rewrite/build"
CPP = f"{REPO}/rewrite/src/ui/planetstrip.cpp"
H = f"{REPO}/rewrite/src/ui/planetstrip.h"
SNAPDIR = "/tmp/t428b_snap"

# name -> (WORKING file, old, new, why)
MUT = {
 "M1": (CPP,
        "{gaugeSelector(cw.res), gaugeSelector(cw.ind),\n                        prosSelector(cw.pros)}",
        "{gaugeSelector(cw.ind), gaugeSelector(cw.res),\n                        prosSelector(cw.pros)}",
        "RES/IND channel->panel binding (S2 dispatch order)"),
 "M2": (H,
        "inline constexpr Pt kPopGridOrigin{355, 7};",
        "inline constexpr Pt kPopGridOrigin{350, 7};",
        "PLPOP rect-origin anchor (windows.txt ln1587)"),
 "M3": (CPP,
        "{gaugeSelector(cw.res), gaugeSelector(cw.ind),",
        "{gaugeSelector(cw.res), 0,",
        "PLIND selector = gaugeSelector(IND) (S3, non-vacuous arm)"),
 "M4": (CPP,
        "s.projectItem = camp.pendingItemFor(star);",
        "s.projectItem = camp.pendingItemFor(star) + 1;",
        "planitem record index == item 1:1 law (shp.md S23.4)"),
}

def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

PRISTINE = {}
def snapshot():
    os.makedirs(SNAPDIR, exist_ok=True)
    for f in (CPP, H):
        shutil.copy2(f, f"{SNAPDIR}/{os.path.basename(f)}")
        PRISTINE[f] = md5(f)

def restore_all():
    for f in (CPP, H):
        shutil.copy2(f"{SNAPDIR}/{os.path.basename(f)}", f)
        os.utime(f, None)               # rule 8b: make must see a fresh mtime
        if md5(f) != PRISTINE[f]:
            raise SystemExit(f"FATAL: restore left {f} != pristine md5 "
                             f"{PRISTINE[f]} — campaign aborted, tree mutated")

if not os.path.exists(f"{SNAPDIR}/planetstrip.cpp"):
    snapshot()
else:
    for f in (CPP, H):
        PRISTINE[f] = md5(f)
print("pristine md5:", {os.path.basename(k): v for k, v in PRISTINE.items()})

results = []
for name in sys.argv[1:]:
    path, old, new, why = MUT[name]
    txt = open(path).read()
    n = txt.count(old)
    if n != 1:
        results.append((name, f"PATCH-MISS (count={n})", why)); continue
    open(path, "w").write(txt.replace(old, new))
    b = subprocess.run(["cmake", "--build", ".", "-j8"], cwd=BUILD,
                       capture_output=True, text=True)
    if b.returncode != 0:
        results.append((name, "BUILD-FAIL", why)); restore_all(); time.sleep(0.3); continue
    t = subprocess.run(["./run_tests"], cwd=BUILD, capture_output=True, text=True)
    last = t.stdout.splitlines()[-1] if t.stdout else "?"
    fails = [l.strip() for l in t.stdout.splitlines() if "FAIL" in l][:3]
    verdict = "CAUGHT" if not last.endswith("0 failed") else "MISSED"
    results.append((name, verdict + " | " + last +
                    (" | " + "; ".join(fails) if fails else ""), why))
    restore_all(); time.sleep(0.3)

subprocess.run(["cmake", "--build", ".", "-j8"], cwd=BUILD, capture_output=True, text=True)
t = subprocess.run(["./run_tests"], cwd=BUILD, capture_output=True, text=True)
print("AFTER-RESTORE:", t.stdout.splitlines()[-1] if t.stdout else "?")
for name, v, why in results:
    print(f"{name} [{why}] :: {v}")
