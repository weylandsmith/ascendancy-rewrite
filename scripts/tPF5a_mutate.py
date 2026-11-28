#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tPF5-A mutation campaign. Rules: snapshot-copy revert (never git),
apply->build->run->restore per mutant, exit code is the verdict, md5
copy-back-then-verify, line-buffered stdout, anchors assert count==1."""
import hashlib, os, shutil, subprocess, sys

sys.stdout.reconfigure(line_buffering=True)
ROOT = "/home/hrethric/projects/ascendancy"
SNAP = "/tmp/tPF5A_snap"
IND_C = ROOT + "/rewrite/src/ui/indpopups.cpp"
IND_H = ROOT + "/rewrite/src/ui/indpopups.h"
UI_C = ROOT + "/rewrite/src/ui/ui.cpp"
FILES = [IND_C, IND_H, UI_C]
PRISTINE = {}

MUTANTS = [
    ("M1 frame at content origin (drop the -10)", IND_C,
     "const int x0 = content.x0 - 10, y0 = content.y0 - 10;",
     "const int x0 = content.x0, y0 = content.y0;"),
    ("M2 frame size = content size (316x198 constants)", IND_H,
     "inline constexpr int kIndPopupFrameW = 336;  // help.shp k0 width\ninline constexpr int kIndPopupFrameH = 256;  // help.shp k0 height",
     "inline constexpr int kIndPopupFrameW = 316;\ninline constexpr int kIndPopupFrameH = 198;"),
    ("M3 wiring: drop the frame blit (keep the law fn)", UI_C,
     "blitShape(ren, indPopupFrameLib, 0, fr.x0, fr.y0);",
     "(void)fr;"),
    ("M4 record index 0 -> 1 (k1 is the 171x76 text box)", UI_C,
     "blitShape(ren, indPopupFrameLib, 0, fr.x0, fr.y0);",
     "blitShape(ren, indPopupFrameLib, 1, fr.x0, fr.y0);"),
    ("M5 frame gated on planetSquarePopup (indicator leg loses it)", UI_C,
     "if (haveFrame) {",
     "if (haveFrame && planetSquarePopup) {"),
]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def restore():
    for f in FILES:
        shutil.copy2(SNAP + "/" + os.path.basename(f), f)
        os.utime(f, None)  # rule 8b: make must not see a stale mtime
        assert md5(f) == PRISTINE[f], "RESTORE MD5 MISMATCH " + f


def main():
    os.makedirs(SNAP, exist_ok=True)
    for f in FILES:
        shutil.copy2(f, SNAP + "/" + os.path.basename(f))
        PRISTINE[f] = md5(f)
    restore()  # campaign starts from verified-pristine (rule 8 pre-flight)
    results = []
    for name, path, old, new in MUTANTS:
        restore()
        src = open(path).read()
        n = src.count(old)
        if n != 1:
            print(f"{name}: PATCH-MISS count={n} — ABORT")
            return 2
        open(path, "w").write(src.replace(old, new))
        b = subprocess.run(["cmake", "--build", ".", "--target", "run_tests",
                            "-j4"], cwd=ROOT + "/rewrite/build",
                           capture_output=True, text=True)
        if b.returncode != 0:
            print(f"{name}: BUILD-FAIL (counts as caught if pin-relevant)")
            results.append((name, "CAUGHT(build)"))
            continue
        r = subprocess.run(["./run_tests"], cwd=ROOT + "/rewrite/build",
                           capture_output=True, text=True)
        fails = [l.strip() for l in r.stdout.splitlines() if "FAIL" in l
                 and "tests," not in l][:4]
        # Verdict = exit code first (rule 1a/13); the summary line ALWAYS
        # contains the word "failed" ("0 failed"), so parse the count.
        last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
        nfail = int(last.split(",")[2].split()[0]) if last else -1
        caught = r.returncode != 0 or nfail != 0
        verdict = "CAUGHT" if caught else "MISSED"
        results.append((name, verdict))
        print(f"{name}: {verdict} rc={r.returncode} " + "; ".join(fails))
    restore()
    b = subprocess.run(["cmake", "--build", ".", "--target", "run_tests",
                        "-j4"], cwd=ROOT + "/rewrite/build",
                       capture_output=True, text=True)
    r = subprocess.run(["./run_tests"], cwd=ROOT + "/rewrite/build",
                       capture_output=True, text=True)
    print("AFTER-RESTORE:", r.stdout.strip().splitlines()[-1])
    for name, v in results:
        print(f"  {v:14s} {name}")
    return 0 if all(v.startswith("CAUGHT") for _, v in results) else 1


if __name__ == "__main__":
    sys.exit(main())
