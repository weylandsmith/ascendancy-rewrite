#!/usr/bin/env python3
"""tA2-CONT mutation campaign: prove the chrome-law pins (test_mapchrome_t394
mapchrome_tA2_well_edge_law + menulaw constants). One mutant at a time:
apply (anchor must occur EXACTLY ONCE) -> rebuild -> run_tests -> restore
from the pristine snapshot taken AT LAUNCH (tree verified clean+md5 before
launch) -> md5-verify the restore, ABORT campaign on mismatch (skill rule
8c/8b). Revert is copy + os.utime (make must see the restored mtime).
Usage: r1_ta2c_mutate.py [mutant-name ...]   (default: all, serial)
"""
import hashlib
import os
import os.path as osp
import shutil
import subprocess
import subprocess as sp
import sys

ROOT = "/home/hrethric/projects/ascendancy"
MC = osp.join(ROOT, "rewrite/src/ui/mapchrome.cpp")
ML = osp.join(ROOT, "rewrite/src/ui/menulaw.h")

# (name, file, old, new, expected-catcher)
MUTANTS = [
    ("M1-cosmos-y0",   ML, "Rect kNewgameCosmosRect{8, 8, 492, 372};",
     "Rect kNewgameCosmosRect{8, 9, 492, 372};", "kNewgameCosmosRect.y0==8"),
    ("M2-cosmos-x1",   ML, "Rect kNewgameCosmosRect{8, 8, 492, 372};",
     "Rect kNewgameCosmosRect{8, 8, 493, 372};", "kNewgameCosmosRect.x1==492"),
    ("M3-cosmos-y1",   ML, "Rect kNewgameCosmosRect{8, 8, 492, 372};",
     "Rect kNewgameCosmosRect{8, 8, 492, 373};", "kNewgameCosmosRect.y1==372"),
    ("M4-ridge0-w",    MC, "{{61, 61, 61}, 169}", "{{61, 61, 61}, 60}",
     "n61 share window"),
    ("M5-ridge1-w",    MC, "{{97, 97, 97}, 169}", "{{97, 97, 97}, 60}",
     "n97 share window"),
    ("M6-recessTop-w", MC, "{{24, 24, 24}, 93}", "{{24, 24, 24}, 20}",
     "n24 share window"),
    ("M7-recessL-w",   MC, "{{5, 7, 8}, 90}", "{{5, 7, 8}, 20}",
     "n578 share window"),
    ("M8-recessR-w",   MC, "{{0, 0, 0}, 102}", "{{0, 0, 0}, 20}",
     "n000 share window"),
    ("M9-beginVis-x0", ML, "Rect kBeginPanelVisual{502, 381, 632, 472};",
     "Rect kBeginPanelVisual{494, 381, 632, 472};", "kBeginPanelVisual.x0==502"),
    ("M10-ridge-swap", MC,
     "if (y == 373) { tab = kRidge0; n = 14; }\n    if (y == 374) { tab = kRidge1; n = 14; }",
     "if (y == 373) { tab = kRidge1; n = 14; }\n    if (y == 374) { tab = kRidge0; n = 14; }",
     "m373/m374 windows + dark-above/light-below pair"),
    ("M11-chain-revert", MC, "y > 7 && y != 373 && y != 374", "y > 7",
     "m373 window (the fixed defect re-appears ~50.6)"),
    ("M12-edges-swap", MC, "tab = (x <= 250) ? kLeft : kRight; n = 4;",
     "tab = (x <= 250) ? kRight : kLeft; n = 4;", "ml window"),
]

PRISTINE = {}

def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

def snapshot():
    for f in {m[1] for m in MUTANTS}:
        PRISTINE[f] = md5(f)
    print("snapshot:", {osp.basename(k): v[:8] for k, v in PRISTINE.items()},
          flush=True)

def restore(f):
    shutil.copy2(osp.join("/tmp/ta2c_snap", osp.basename(f)), f)
    os.utime(f, None)  # skill 8b: make must rebuild
    got = md5(f)
    if got != PRISTINE[f]:
        print(f"RESTORE-MISMATCH {f} {got} != {PRISTINE[f]} — ABORT")
        sys.exit(3)

def run_one(name, f, old, new, why):
    s = open(f).read()
    n = s.count(old)
    if n != 1:
        print(f"{name}: ANCHOR-ERROR count={n}", flush=True)
        return False
    open(f, "w").write(s.replace(old, new))
    try:
        b = sp.run("cmake --build build -j8", shell=True, cwd=osp.join(ROOT, "rewrite"),
                   capture_output=True, text=True)
        if b.returncode != 0:
            print(f"{name}: CAUGHT (compile error)", flush=True)
            return True
        r = sp.run("./build/run_tests", shell=True, cwd=osp.join(ROOT, "rewrite"),
                   capture_output=True, text=True)
        out = r.stdout
        last = [l for l in out.splitlines() if "tests," in l]
        fails = [l.strip() for l in out.splitlines() if "FAIL" in l][:2]
        caught = r.returncode != 0 or (last and not last[-1].endswith("0 failed"))
        print(f"{name}: {'CAUGHT' if caught else 'MISSED'} {last[-1] if last else '?'} "
              f"{fails}", flush=True)
        return caught
    finally:
        restore(f)

def main():
    names = sys.argv[1:]
    todo = [m for m in MUTANTS if not names or m[0] in names]
    os.makedirs("/tmp/ta2c_snap", exist_ok=True)
    snapshot()
    for m in MUTANTS:
        shutil.copy2(m[1], "/tmp/ta2c_snap/" + osp.basename(m[1]))
    ok = 0
    for name, f, old, new, why in todo:
        if run_one(name, f, old, new, why):
            ok += 1
    print(f"RESULT {ok}/{len(todo)} CAUGHT", flush=True)
    # AFTER-RESTORE: rebuild clean and run the suite (skill: never trust).
    b = sp.run("cmake --build build -j8", shell=True, cwd=osp.join(ROOT, "rewrite"),
               capture_output=True, text=True)
    r = sp.run("./build/run_tests", shell=True, cwd=osp.join(ROOT, "rewrite"),
               capture_output=True, text=True)
    last = [l for l in r.stdout.splitlines() if "tests," in l]
    print("AFTER-RESTORE build", b.returncode, "|", last[-1] if last else "?",
          flush=True)

if __name__ == "__main__":
    main()
