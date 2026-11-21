#!/usr/bin/env python3
"""tA3 TEXT LAW mutation campaign. Two catcher classes:
  (a) constant mutants -> pinned by rewrite/tests/test_textlaw_tA3.cpp
      (run_tests catches);
  (b) draw-site mutants (face flag / ink colour) -> caught by the live
      witness scripts/r1_tA3_capture.sh + scripts/r1_tA3_witness.py
      (big-face iou + exact-(255,255,255)-core census).
One mutant at a time: apply (anchor EXACTLY once) -> rebuild -> catch-test
-> restore from the pristine snapshot taken AT LAUNCH -> md5-verify the
restore, ABORT on mismatch (skill rule 8c/8b). Revert = copy + os.utime.
Usage: r1_ta3_mutate.py [mutant-name ...]   (default: all, serial)
"""
import hashlib
import os
import os.path as osp
import shutil
import subprocess as sp
import sys

ROOT = "/home/hrethric/projects/ascendancy"
ML = osp.join(ROOT, "rewrite/src/ui/menulaw.h")
HL = osp.join(ROOT, "rewrite/src/ui/hudlayout.h")
UI = osp.join(ROOT, "rewrite/src/ui/ui.cpp")
TC = osp.join(ROOT, "rewrite/src/ui/title.cpp")

# (name, file, old, new, catcher)  catcher: "tests" | "witness"
MUTANTS = [
    ("M1-raildx", HL, "inline constexpr int kRailLabelDx = 2, kRailLabelDy = 2;",
     "inline constexpr int kRailLabelDx = 6, kRailLabelDy = 2;", "tests"),
    ("M2-raildy", HL, "inline constexpr int kRailLabelDx = 2, kRailLabelDy = 2;",
     "inline constexpr int kRailLabelDx = 2, kRailLabelDy = 8;", "tests"),
    ("M3-controldy", ML, "inline constexpr int kControlLabelDy = 10, kPlayerColorLabelDy = 12;",
     "inline constexpr int kControlLabelDy = 12, kPlayerColorLabelDy = 12;", "tests"),
    ("M4-pcdy", ML, "inline constexpr int kControlLabelDy = 10, kPlayerColorLabelDy = 12;",
     "inline constexpr int kControlLabelDy = 10, kPlayerColorLabelDy = 2;", "tests"),
    ("M5-nametop", ML, "inline constexpr int kNameTop = 17, kHeaderTop = 15;",
     "inline constexpr int kNameTop = 18, kHeaderTop = 15;", "tests"),
    ("M6-headertop", ML, "inline constexpr int kNameTop = 17, kHeaderTop = 15;",
     "inline constexpr int kNameTop = 17, kHeaderTop = 16;", "tests"),
    ("M7-summarytop", ML, "inline constexpr int kSummaryTop = 326, kSummaryPitch = 13;",
     "inline constexpr int kSummaryTop = 327, kSummaryPitch = 13;", "tests"),
    ("M8-loretop", ML, "inline constexpr int kLoreTextTop = 265;",
     "inline constexpr int kLoreTextTop = 258;", "tests"),
    ("M9-rail-face-revert", UI,
     "txt.draw(ren, tx, rr.y + kRailLabelDy, railLabel(b), true,\n                     kRailInk);",
     "txt.draw(ren, tx, rr.y + kRailLabelDy, railLabel(b), false,\n                     kRailInk);",
     "witness"),
    ("M10-rail-ink-235", UI,
     "txt.draw(ren, tx, rr.y + kRailLabelDy, railLabel(b), true,\n                     kRailInk);",
     "txt.draw(ren, tx, rr.y + kRailLabelDy, railLabel(b), true,\n                     kText);",
     "witness"),
    ("M11-control-face-revert", TC,
     "txt.draw(ren, cxp - wl / 2, c.rect.y0 + kControlLabelDy,\n                         c.label, true, kNewgameInk);",
     "txt.draw(ren, cxp - wl / 2, c.rect.y0 + kControlLabelDy,\n                         c.label, false, kNewgameInk);",
     "witness"),
    ("M12-begin-ink-title", TC,
     "txt.draw(ren,\n                         (r.x + (r.w - w) / 2), kBeginLabelTop, lbl, true,\n                         kNewgameInk);",
     "txt.draw(ren,\n                         (r.x + (r.w - w) / 2), kBeginLabelTop, lbl, true,\n                         kInk);",
     "witness"),
]

PRISTINE = {}

def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

def snapshot():
    # GUARD (tA3 lesson): a killed foreground mutate run can leave a
    # mutant APPLIED; snapshotting that tree poisons every later restore
    # and every test run (the poison shows as an unrelated-looking pin
    # failure). Launch only on a green suite.
    caught, last, fails = run_tests_caught()
    if caught:
        print("LAUNCH-GUARD: suite NOT green at launch:", last[-1] if last else "?",
              fails, "— ABORT (tree may hold an applied mutant)")
        sys.exit(4)
    for f in {m[1] for m in MUTANTS}:
        PRISTINE[f] = md5(f)
    print("snapshot:", {osp.basename(k): v[:8] for k, v in PRISTINE.items()},
          flush=True)

def restore(f):
    shutil.copy2(osp.join("/tmp/ta3_snap", osp.basename(f)), f)
    os.utime(f, None)
    got = md5(f)
    if got != PRISTINE[f]:
        print(f"RESTORE-MISMATCH {f} {got} != {PRISTINE[f]} — ABORT")
        sys.exit(3)

def run_tests_caught():
    r = sp.run("./build/run_tests", shell=True, cwd=osp.join(ROOT, "rewrite"),
               capture_output=True, text=True)
    last = [l for l in r.stdout.splitlines() if "tests," in l]
    fails = [l.strip() for l in r.stdout.splitlines() if "FAIL" in l][:2]
    return (r.returncode != 0 or (last and not last[-1].endswith("0 failed"))), last, fails

def run_witness_caught():
    c = sp.run("bash scripts/r1_tA3_capture.sh", shell=True, cwd=ROOT,
               capture_output=True, text=True)
    w = sp.run("~/tools/revenv/bin/python scripts/r1_tA3_witness.py "
               "/tmp/tA3_shots/newgame.png /tmp/tA3_shots/map.png",
               shell=True, cwd=ROOT, capture_output=True, text=True)
    fails = [l.strip() for l in w.stdout.splitlines() if "FAIL" in l][:2]
    return w.returncode != 0, [w.stdout.splitlines()[-1] if w.stdout else "?"], fails

def run_one(name, f, old, new, catcher):
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
        caught, last, fails = (run_tests_caught() if catcher == "tests"
                               else run_witness_caught())
        print(f"{name}: {'CAUGHT' if caught else 'MISSED'} {last[-1] if last else '?'} "
              f"{fails}", flush=True)
        return caught
    finally:
        restore(f)

def main():
    names = sys.argv[1:]
    todo = [m for m in MUTANTS if not names or m[0] in names]
    os.makedirs("/tmp/ta3_snap", exist_ok=True)
    snapshot()
    for m in MUTANTS:
        shutil.copy2(m[1], "/tmp/ta3_snap/" + osp.basename(m[1]))
    ok = 0
    for name, f, old, new, catcher in todo:
        if run_one(name, f, old, new, catcher):
            ok += 1
    print(f"RESULT {ok}/{len(todo)} CAUGHT", flush=True)
    b = sp.run("cmake --build build -j8", shell=True, cwd=osp.join(ROOT, "rewrite"),
               capture_output=True, text=True)
    caught, last, fails = run_tests_caught()
    print("AFTER-RESTORE build", b.returncode, "|", last[-1] if last else "?",
          flush=True)

if __name__ == "__main__":
    main()
