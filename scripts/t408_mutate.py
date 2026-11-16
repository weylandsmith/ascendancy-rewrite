#!/usr/bin/env python3
"""t408 mutation campaign (researchview law pins).
Skill rules: anchor guard (count==1 or refuse), revert by FILE COPY from a
snapshot (never git-checkout mid-flight), one mutant serial, verdict = the
FILTERED run_tests exit code + named FAIL lines. Run from repo root."""
import os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "rewrite/src/ui/researchview.cpp")
HDR = os.path.join(ROOT, "rewrite/src/ui/researchview.h")
BUILD = os.path.join(ROOT, "rewrite/build")
SNAP = "/tmp/t408-snap"
os.makedirs(SNAP, exist_ok=True)
shutil.copy(SRC, os.path.join(SNAP, "researchview.cpp"))
shutil.copy(HDR, os.path.join(SNAP, "researchview.h"))

MUTANTS = [
    # (name, file, old, new)
    ("M1 setStudy accepts OWNED rows", SRC,
     "    if (camp.techRowOwnedFor(owner, row)) return false;",
     "    if (false) return false;"),
    ("M2 setStudy accepts BLOCKED rows", SRC,
     "    for (int p : tree.all()[row].prereqs)\n        if (!camp.techRowOwnedFor(owner, p)) return false;",
     "    // prereq gate dropped"),
    ("M3 header join drops ' Knowledge'", SRC,
     'return ownerName + " Knowledge";',
     'return ownerName + " Tech";'),
    ("M4 days plural pair inverted", SRC,
     'return "(" + std::to_string(n) + (n == 1 ? " day)" : " days)");',
     'return "(" + std::to_string(n) + (n == 1 ? " days)" : " day)");'),
    ("M5 days floor instead of ceil", SRC,
     "        days = std::ceil(remaining / rateLastTurn);",
     "        days = std::floor(remaining / rateLastTurn);"),
    ("M6 allows gizmo order reversed", SRC,
     "    for (int i = 0; i < ng; ++i) {\n        const ag::Gizmo* g = camp.gizmoAt(i);",
     "    for (int i = ng - 1; i >= 0; --i) {\n        const ag::Gizmo* g = camp.gizmoAt(i);"),
    ("M7 pan rect MoveUp extent widened", HDR,
     "inline constexpr Rect kResMoveUp{563, 442, 593, 457};",
     "inline constexpr Rect kResMoveUp{563, 442, 593, 472};"),
    ("M8 hit precedence nodes before pan", SRC,
     "    if (in(kResRotLeft, px, py))   { h.kind = ResHit::RotLeft;   return h; }",
     "    if (false)   { h.kind = ResHit::RotLeft;   return h; }"),
    ("M9 partition merges Study into Available", SRC,
     "                nd.state = camp.isTechQueuedFor(owner, r) ? TechNodeState::Study\n                                                          : TechNodeState::Available;",
     "                nd.state = TechNodeState::Available;"),
]

def restore():
    shutil.copy(os.path.join(SNAP, "researchview.cpp"), SRC)
    shutil.copy(os.path.join(SNAP, "researchview.h"), HDR)

def build():
    subprocess.run(["cmake", "--build", BUILD, "--target", "run_tests", "-j4"],
                   capture_output=True)

def run():
    r = subprocess.run([os.path.join(BUILD, "run_tests"), "researchview"],
                       capture_output=True, text=True)
    return r.returncode, r.stdout

fails = 0
for name, path, old, new in MUTANTS:
    restore()
    s = open(path).read()
    c = s.count(old)
    if c != 1:
        print(f"{name} ANCHOR GUARD count={c} — REFUSING (source moved?)")
        fails = 1
        continue
    open(path, "w").write(s.replace(old, new))
    build()
    rc, out = run()
    named = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")]
    if rc != 0 and named:
        print(f"{name} CAUGHT: {named[0]}")
    elif rc != 0:
        print(f"{name} CAUGHT-UNCLEAN rc={rc} (no FAIL line — crash?)")
        fails = 1
    else:
        print(f"{name} *** SURVIVED ***")
        fails = 1

restore()
build()
rc, out = run()
print(out.splitlines()[-1] if out else "no output")
print(f"MUTATION CAMPAIGN DONE fails={fails}")
sys.exit(fails)
