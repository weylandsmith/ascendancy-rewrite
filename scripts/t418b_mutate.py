#!/usr/bin/env python3
# t418b mutation campaign: one cited branch at a time in
# rewrite/src/ui/planetview.cpp; the suite MUST fail (CAUGHT).
# Usage: python3 t418b_mutate.py M1 M2 ...   (run ONLY as tracked background
# or inside execute_code; never foreground-with-timeout — skill rule 8.)
# Restore = file copy + os.utime (rule 8b: stale-mtime binaries).
import os, shutil, subprocess, sys, time

REPO = "/home/hrethric/projects/ascendancy"
SRC = f"{REPO}/rewrite/src/ui/planetview.cpp"
SNAP = "/tmp/t418b_planetview.orig.cpp"

MUT = {
 "M1": ("if (col < B || col >= B + C) return -1;",
        "if (col < B || col >= B + C + 1) return -1;"),  # 0x3963b bound
 "M2": ("return cum + col - B;  // 0x3963f..0x39647",
        "return cum + col;      // 0x3963f..0x39647"),   # B subtraction
 "M3": ("if (cum + C > cell) break;",
        "if (cum + tt.rowOffset[size][r] + C > cell) break;"),  # THE t418 misparse
 "M4": ("if (size < 0 || size >= 5 || cell < 0 || cell >= surfaceCells)\n        return false;\n    int cum = 0, r = 0;",
        "if (size < 0 || size >= 5 || cell < 0 || cell > surfaceCells)\n        return false;\n    int cum = 0, r = 0;"),  # 0x39671 jae
 "M5": ("return Pt{110 + col * 34 + row * 17, 410 + col * 17 - row * 34};",
        "return Pt{110 + col * 17 + row * 17, 410 + col * 17 - row * 34};"),  # imul 0x22
 "M6": ("return Pt{110 + col * 34 + row * 17, 410 + col * 17 - row * 34};",
        "return Pt{110 + col * 34 + row * 34, 410 + col * 17 - row * 34};"),  # row x-step
 "M7": ("if (17 * std::abs(dx) + 34 * std::abs(dy) > 578) continue;",
        "if (17 * std::abs(dx) + 34 * std::abs(dy) > 1156) continue;"),       # diamond size
 "M8": ("        if (rock != (item == 38)) return PlacementBlock::RockMismatch;",
        "        // rock veto deleted (0x38519 mutant)"),
 "M9": ("if (item == 5 || item == 35) return PlacementBlock::None;  // 0x385f6/ff",
        "if (item == 6 || item == 39) return PlacementBlock::None;"),
 "M10": ("const int dr[4] = {1, -1, 0, 0}, dc[4] = {0, 0, -1, 1};",
         "const int dr[4] = {1, 1, 0, 0}, dc[4] = {0, 0, -1, 1};"),  # row-1 probe lost
 # tPL-B1b: the polarity flip is THE bug this iteration fixed — each mutant
 # re-introduces one inverted/wrong-polarity reading.
 "M11": ("            return PlacementBlock::None;  // active neighbour: jne-exit, legal",
         "            return PlacementBlock::NoActiveNeighbour;  // INVERTED (t418b bug)"),
 "M12": ("    return PlacementBlock::NoActiveNeighbour;  // 0x386fc xor edi,edi",
         "    return PlacementBlock::None;  // all-inactive mutant"),
 "M13": ("        if (cellSurface != itemSurface) return PlacementBlock::SurfaceVsRing;",
         "        if (cellSurface == itemSurface) return PlacementBlock::SurfaceVsRing;"),
 "M14": ("    if (item < 31) {",
         "    if (item < 22) {"),  # 0x384e0 cmp dl,0x1e
 "M15": ("    if (cell < 0 || cell >= surf + kRingSlots)",
         "    if (cell < 0 || cell >= surf)"),  # ring domain lost
 "M16": ("        if (!barren || own) return PlacementBlock::TerraformSite;",
         "        if (own) return PlacementBlock::TerraformSite;"),  # barren arm lost
 "M17": ("    if (own) return PlacementBlock::None;  // 0x385ee own-ACTIVE jne-exit",
         "    // own-skip deleted (0x385ee mutant)"),
}

def restore():
    shutil.copy2(SNAP, SRC)
    os.utime(SRC, None)  # rule 8b: make sees a fresh mtime

if not os.path.exists(SNAP):
    shutil.copy2(SRC, SNAP)

names = sys.argv[1:]
results = []
for name in names:
    old, new = MUT[name]
    txt = open(SNAP).read()
    n = txt.count(old)
    if n != 1:
        results.append((name, f"PATCH-MISS (count={n})")); continue
    open(SRC, "w").write(txt.replace(old, new))
    b = subprocess.run(["cmake", "--build", ".", "-j8"], cwd=f"{REPO}/rewrite/build",
                       capture_output=True, text=True)
    if b.returncode != 0:
        results.append((name, "BUILD-FAIL")); restore(); continue
    t = subprocess.run(["./run_tests"], cwd=f"{REPO}/rewrite/build",
                       capture_output=True, text=True)
    fails = [l.strip() for l in t.stdout.splitlines() if "FAIL" in l][:2]
    verdict = "CAUGHT" if t.returncode != 0 or "failed" in t.stdout.splitlines()[-1].replace(", 0 failed","") else "MISSED"
    last = t.stdout.splitlines()[-1] if t.stdout else "?"
    verdict = "CAUGHT" if not last.endswith("0 failed") else "MISSED"
    results.append((name, verdict + " | " + last + (" | " + "; ".join(fails) if fails else "")))
    restore()
    time.sleep(0.3)

# AFTER-RESTORE sanity: rebuild clean and run
subprocess.run(["cmake", "--build", ".", "-j8"], cwd=f"{REPO}/rewrite/build",
               capture_output=True, text=True)
t = subprocess.run(["./run_tests"], cwd=f"{REPO}/rewrite/build",
                   capture_output=True, text=True)
print("AFTER-RESTORE:", t.stdout.splitlines()[-1])
for name, v in results:
    print(name, v)
