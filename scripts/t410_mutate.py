#!/usr/bin/env python3
# t410 mutation campaign: prove the system-view + screen-stack pins.
# Revert by FILE COPY from /tmp/t410-snap (never git checkout — skill rule 1).
# Verdict = run_tests exit code (t407-F13 lesson: harness prints 'FAIL <file>'
# FIRST; grep patterns like 'name.*FAIL' never match).
import shutil, subprocess, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
SNAP = "/tmp/t410-snap"
FILES = ["rewrite/src/ui/sysview.cpp", "rewrite/src/ui/statuslaw.cpp"]
os.makedirs(SNAP, exist_ok=True)
for f in FILES:
    shutil.copy(f, SNAP + "/" + f.replace("/", "_"))

MUTANTS = [
    # name, file, old, new
    ("M1 stack-duplicate-levels-stacked",
     "rewrite/src/ui/sysview.cpp",
     """    for (size_t i = 0; i < s_.size(); ++i) {
        if (s_[i] == screen) {
            s_.resize(i + 1);
            return;
        }
    }
    s_.push_back(screen);""",
     "    s_.push_back(screen);"),
    ("M2 escape-pops-past-bottom",
     "rewrite/src/ui/sysview.cpp",
     "    if (s_.size() <= 1) return false;  // bottom: the caller's standing quit\n    s_.pop_back();",
     "    if (!s_.empty()) s_.pop_back();"),
    ("M3 toggrid-rect-drift",
     "rewrite/src/ui/sysview.cpp",
     '{"TOGGRID",      {557, 403, 587, 433}, 74,  0},',
     '{"TOGGRID",      {560, 403, 587, 433}, 74,  0},'),
    ("M4 first-match-wins",
     "rewrite/src/ui/sysview.cpp",
     "    for (int i = 0; i < kSysCtlCount; ++i)\n        if (inRect(kSysCtl[i].rect, p))\n            hit = static_cast<SysCtl>(i);",
     "    for (int i = 0; i < kSysCtlCount; ++i)\n        if (inRect(kSysCtl[i].rect, p)) { hit = static_cast<SysCtl>(i); break; }"),
    ("M5 shape-identity-offset",
     "rewrite/src/ui/sysview.cpp",
     "    return fr;\n}",
     "    return fr + 1;\n}"),
    ("M6 seam-faces-accepted",
     "rewrite/src/ui/sysview.cpp",
     "    if (c == SysCtl::MyItems || c == SysCtl::Abandon) return -1;",
     ""),
    ("M7 colonised-index-shifted",
     "rewrite/src/ui/sysview.cpp",
     "    d.colonised = owner >= 0 && pl.index == 0;",
     "    d.colonised = owner >= 0 && pl.index == 1;"),
    ("M8 orbit-pitch-drift",
     "rewrite/src/ui/sysview.cpp",
     "    return kOrbitBase + kOrbitPitch * i;",
     "    return kOrbitBase + (kOrbitPitch - 4.0) * i;"),
    ("M9 hit-radius-law-dead",
     "rewrite/src/ui/sysview.cpp",
     "    long bestD2 = long(radius) * radius;",
     "    long bestD2 = 0;"),
]

def restore():
    for f in FILES:
        shutil.copy(SNAP + "/" + f.replace("/", "_"), f)

def build_and_run():
    b = subprocess.run(["make", "-j4", "-C", "rewrite/build"],
                       capture_output=True, text=True)
    if b.returncode != 0:
        return "BUILDFAIL", b.stderr[-500:]
    r = subprocess.run(["./rewrite/build/run_tests"], capture_output=True,
                       text=True)
    named = [l for l in r.stdout.splitlines() if "FAIL" in l]
    return ("CAUGHT" if r.returncode != 0 or named else "MISSED"), named[:4]

results = []
for name, f, old, new in MUTANTS:
    restore()
    src = open(f).read()
    if old not in src:
        results.append((name, "PATCH-MISS"))
        continue
    open(f, "w").write(src.replace(old, new, 1))
    verdict, detail = build_and_run()
    results.append((name, verdict))
    print(name, verdict, flush=True)
    for d in detail if isinstance(detail, list) else []:
        print("   ", d.strip()[:160])

restore()
# final clean rebuild + run
rc = build_and_run()
print("AFTER-RESTORE:", rc[0], rc[1] if rc[0] != "CAUGHT" else "")
bad = [r for r in results if r[1] != "CAUGHT"]
print("SUMMARY:", len(results) - len(bad), "/", len(results), "CAUGHT",
      ("| PROBLEM: " + ", ".join(b[0] + "=" + b[1] for b in bad)) if bad else "")
sys.exit(1 if bad else 0)
