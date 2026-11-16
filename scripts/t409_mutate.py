#!/usr/bin/env python3
# t409 mutation campaign: prove the ability-dialog + species-menu pins.
# Revert by FILE COPY from /tmp/t409-snap (never git checkout — skill rule 1).
# Verdict = run_tests exit code (t407-F13 lesson: harness prints 'FAIL <file>'
# FIRST; grep patterns like 'name.*FAIL' never match).
import shutil, subprocess, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
SNAP = "/tmp/t409-snap"
FILES = ["rewrite/src/ui/abilitylaw.cpp", "rewrite/src/ui/speciesmenu.cpp"]
os.makedirs(SNAP, exist_ok=True)
for f in FILES:
    shutil.copy(f, SNAP + "/" + f.replace("/", "_"))

MUTANTS = [
    # name, file, old, new
    ("M1 passive-block-gains-use-button",
     "rewrite/src/ui/abilitylaw.cpp",
     'if (texts.size() > 2) p.chargeLine = texts[2];',
     'if (texts.size() > 2) p.chargeLine = texts[2]; else p.buttons.push_back({"Use Ability", 1});'),
    ("M2 index-census-dropped",
     "rewrite/src/ui/abilitylaw.cpp",
     "if (out->size() != 21) {",
     "if (out->size() != 20) {"),
    ("M3 rect-x1-widened",
     "rewrite/src/ui/abilitylaw.cpp",
     "const Rect kAbilityWin{60, 100, 395, 355};",
     "const Rect kAbilityWin{60, 100, 420, 355};"),
    ("M4 hit-exclusive-interior",
     "rewrite/src/ui/abilitylaw.cpp",
     "return x >= kAbilityWin.x0 && x <= kAbilityWin.x1 &&\n           y >= kAbilityWin.y0 && y <= kAbilityWin.y1;",
     "return x > kAbilityWin.x0 && x < kAbilityWin.x1 &&\n           y > kAbilityWin.y0 && y < kAbilityWin.y1;"),
    ("M5 plural-law-inverted",
     "rewrite/src/ui/abilitylaw.cpp",
     'const std::string plural = remaining == 1 ? "" : "s";',
     'const std::string plural = remaining == 1 ? "s" : "";'),
    ("M6 negative-clamp-dropped",
     "rewrite/src/ui/abilitylaw.cpp",
     "if (remaining < 0) remaining = 0;",
     ""),
    ("M7 unknown-owner-rows-emitted",
     "rewrite/src/ui/speciesmenu.cpp",
     "if (!camp.playerKnows(o)) continue;  // static #11 \"known\" gate",
     ""),
    ("M8 extinct-law-dropped",
     "rewrite/src/ui/speciesmenu.cpp",
     "r.extinct = camp.starsOwned(o) == 0;  // static #12 \"Extinct\"",
     'r.extinct = false;'),
    ("M9 specnum-skip-law-broken",
     "rewrite/src/ui/speciesmenu.cpp",
     "if (si.specnum == camp.playerSpecies()) continue;",
     "if (false) continue;"),
]

def restore():
    for f in FILES:
        shutil.copy(SNAP + "/" + f.replace("/", "_"), f)

def build_and_run():
    b = subprocess.run(["make", "-j4", "-C", "rewrite/build"],
                       capture_output=True, text=True)
    if b.returncode != 0:
        return "BUILDFAIL", b.stdout[-400:] + b.stderr[-400:]
    r = subprocess.run(["./rewrite/build/run_tests"], capture_output=True,
                       text=True)
    fails = [l for l in r.stdout.splitlines() if "FAIL" in l][:3]
    return ("CAUGHT" if r.returncode != 0 else "MISSED"), "\n      ".join(fails)

only = sys.argv[1:] or None
results = []
for m in MUTANTS:
    name, path, old, new = m
    if only and name not in only:
        continue
    src = open(path).read()
    n = src.count(old)
    if n != 1:
        print(f"{name}: ANCHOR count={n} — SKIPPED (source moved)"); results.append((name,"ANCHOR")); continue
    open(path, "w").write(src.replace(old, new, 1))
    verdict, detail = build_and_run()
    print(f"{name}: {verdict}\n      {detail}")
    results.append((name, verdict))
    restore()
restore()
subprocess.run(["make", "-j4", "-C", "rewrite/build"], capture_output=True)
r = subprocess.run(["./rewrite/build/run_tests"], capture_output=True, text=True)
print("restored suite:", r.stdout.strip().splitlines()[-1])
caught = sum(1 for _, v in results if v == "CAUGHT")
print(f"MUTATION {caught}/{len(results)} CAUGHT")
sys.exit(0 if caught == len(results) else 1)
