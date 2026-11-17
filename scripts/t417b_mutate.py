#!/usr/bin/env python3
# t417b mutation campaign. Revert by FILE COPY from /tmp/t417b-snap (skill
# rule 1 — land uncommitted). Anchor guard: old snippet must occur EXACTLY
# once (rule 2). Verdict = run_tests exit code + named FAIL lines (t408
# lesson: harness.h prints 'FAIL <file>' first; grep 'FAIL').
import shutil, subprocess, sys, os

ROOT = "/home/hrethric/projects/ascendancy"
SNAP = "/tmp/t417b-snap"
FILES = ["rewrite/src/ui/statusbg.cpp", "rewrite/src/ui/statusbg.h",
         "rewrite/src/ui/statuslist.h", "rewrite/src/ui/statuslist.cpp"]

MUTANTS = [
    ("M1 backdrop-accepts", "rewrite/src/ui/statusbg.cpp",
     "return screen != kScreenStatus;", "return true;"),
    ("M2 pitch-112", "rewrite/src/ui/statuslist.h",
     "inline constexpr int kStatusRowPitch = 141;",
     "inline constexpr int kStatusRowPitch = 112;"),
    ("M3 top-117", "rewrite/src/ui/statuslist.h",
     "inline constexpr int kStatusRowsTop = 57;",
     "inline constexpr int kStatusRowsTop = 117;"),
    ("M4 ramp-y46-colour", "rewrite/src/ui/statusbg.cpp",
     'case 46: *out = RGB{33, 56, 57}; return true;',
     'case 46: *out = RGB{24, 28, 24}; return true;'),
    ("M5 weights-119", "rewrite/src/ui/statusbg.cpp",
     "const int kSpeckleWeights[kSpeckleCount] = {37, 35, 18, 6, 1, 1};",
     "const int kSpeckleWeights[kSpeckleCount] = {45, 42, 22, 8, 1, 1};"),
    ("M6 marker-x62", "rewrite/src/ui/statusbg.h",
     "inline constexpr Rect kStatusMarkerRect{16, 2, 69, 25};",
     "inline constexpr Rect kStatusMarkerRect{62, 2, 71, 16};"),
    ("M7 rowguard-removed", "rewrite/src/ui/statuslist.cpp",
     "    if (p.y < topY) return std::nullopt;\n    const int i = (p.y - topY) / kStatusRowPitch;",
     "    const int i = (p.y - topY) / kStatusRowPitch;"),
    ("M8 ramp-pale-single", "rewrite/src/ui/statusbg.cpp",
     "        case 39:\n        case 40: *out = RGB{123, 182, 181}; return true;",
     "        case 39: *out = RGB{123, 182, 181}; return true;"),
    ("M9 well-navy-k0", "rewrite/src/ui/statusbg.h",
     "inline constexpr RGB kStatusWellNavy{8, 32, 49};",
     "inline constexpr RGB kStatusWellNavy{12, 32, 48};"),
]

def sh(cmd):
    return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)

os.makedirs(SNAP, exist_ok=True)
for f in FILES:
    dst = os.path.join(SNAP, f.replace("/", "__"))
    shutil.copy2(os.path.join(ROOT, f), dst)

def restore():
    for f in FILES:
        shutil.copy2(os.path.join(SNAP, f.replace("/", "__")), os.path.join(ROOT, f))
        # copy2 PRESERVES the snapshot's old mtime -> make can consider a
        # binary built mid-campaign "up to date" (t417b run-2 poisoning).
        import time
        os.utime(os.path.join(ROOT, f), None)

results = []
for name, f, old, new in MUTANTS:
    restore()
    path = os.path.join(ROOT, f)
    src = open(path).read()
    n = src.count(old)
    if n != 1:
        results.append((name, f"PATCH-MISS(count={n})"))
        continue
    open(path, "w").write(src.replace(old, new))
    b = sh("make -C rewrite/build -j$(nproc) 2>&1 | tail -1")
    if not os.path.exists(ROOT + "/rewrite/build/run_tests"):
        results.append((name, "BUILD-FAIL")); restore(); continue
    r = sh("cd rewrite/build && ./run_tests 2>&1 | grep -E '^FAIL|^  FAIL|failed' | head -6")
    fails = [l for l in r.stdout.splitlines() if "FAIL" in l]
    rc = sh("cd rewrite/build && ./run_tests >/dev/null 2>&1; echo $?").stdout.strip()
    verdict = "CAUGHT" if rc != "0" else "MISSED"
    results.append((name, verdict + (f" rc={rc} " + fails[0][:90] if fails else " (no FAIL lines — check crash)")))
    restore()

# after-restore sanity
sh("make -C rewrite/build -j$(nproc) >/dev/null 2>&1")
rc = sh("cd rewrite/build && ./run_tests 2>&1 | tail -1").stdout.strip()
print("AFTER-RESTORE:", rc)
for name, v in results:
    print(f"{name}: {v}")
caught = sum(1 for _, v in results if v.startswith("CAUGHT"))
print(f"VERDICT {caught}/{len(MUTANTS)} CAUGHT")
sys.exit(0 if caught == len(MUTANTS) else 1)
