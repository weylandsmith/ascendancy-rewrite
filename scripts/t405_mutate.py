#!/usr/bin/env python3
# t405 mutation battery: prove the statusnav pins encode the measured law.
# Revert by FILE COPY from /tmp/t405-snap (skill rule 1: uncommitted work —
# never git-checkout these files). One mutant per build, serial. Anchor guard:
# each old snippet must occur EXACTLY ONCE.
import shutil, subprocess, sys, os
os.chdir('/home/hrethric/projects/ascendancy')
SNAP = '/tmp/t405-snap'
FILES = ['rewrite/src/ui/statuslist.h', 'rewrite/src/ui/statuslist.cpp',
         'rewrite/src/ui/ui.cpp']

MUTANTS = [
    # name, file, old, new
    ("M1 arrows back to old 566-wide PORT rects (re-introduce D13)",
     'rewrite/src/ui/statuslist.h',
     'inline constexpr Rect kStatusArrowUp{619, 48, 638, 94};',
     'inline constexpr Rect kStatusArrowUp{566, 46, 632, 70};'),
    # VACUITY FINDING (skill rule 6, verified manually t405): M2 alone and
    # M3 alone BOTH pass the suite — the column guard and the row x-boundary
    # are mutually redundant (either one alone makes the trough inert). The
    # regression that matters is the OLD CODE SHAPE (neither guard), pinned
    # as M2c below; it fails with named FAILs (test lines 42/44/56/60).
    ("M2c old-code shape: no column guard AND no x-boundary",
     'rewrite/src/ui/statuslist.cpp',
     '''    if (inR(kStatusScrollCol, p)) return h;  // None: trough/thumb seam
    if (const auto i = statusRowAt(p, topY)) {
        // Rows live inside the table: left frame x 7, right of the scrollbar
        // column boundary x 619 (vendor table verticals end at 619/621).
        if (p.x >= kStatusInterior.x0 && p.x < kStatusScrollCol.x0) {''',
     '''    if (const auto i = statusRowAt(p, topY)) {
        if (true) {'''),
    ("M3 row x-boundary widened past the scroll column",
     'rewrite/src/ui/statuslist.cpp',
     'if (p.x >= kStatusInterior.x0 && p.x < kStatusScrollCol.x0) {',
     'if (p.x >= kStatusInterior.x0 && p.x <= kStatusScrollCol.x1) {'),
    ("M4 precedence flipped: scroll column checked before arrows",
     'rewrite/src/ui/statuslist.cpp',
     '''    if (inR(kStatusArrowUp, p)) { h.kind = StatusHit::ArrowUp; return h; }
    if (inR(kStatusArrowDown, p)) { h.kind = StatusHit::ArrowDown; return h; }
    if (inR(kStatusScrollCol, p)) return h;  // None: trough/thumb seam''',
     '''    if (inR(kStatusScrollCol, p)) return h;
    if (inR(kStatusArrowUp, p)) { h.kind = StatusHit::ArrowUp; return h; }
    if (inR(kStatusArrowDown, p)) { h.kind = StatusHit::ArrowDown; return h; }'''),
    ("M5 rail active on every screen (refutes measured STATE law)",
     'rewrite/src/ui/statuslaw.cpp',
     '    return screen == kScreenMap;\n}',
     '    return true;\n}'),
    ("M6 unknown screen target clamps to map (violates never-clamp)",
     'rewrite/src/ui/statuslaw.cpp',
     '    if (msg == 1 && screenKnown(param1)) return param1;\n    return cur;',
     '    if (msg == 1) return screenKnown(param1) ? param1 : kScreenMap;\n    return cur;'),
    ("M7 Esc dead on the intel screen",
     'rewrite/src/ui/statuslaw.cpp',
     'bool escapeToMap(int screen) { return screen != kScreenMap; }',
     'bool escapeToMap(int screen) { return screen != kScreenMap && screen != kScreenIntel; }'),
]

def restore():
    for f in FILES + ['rewrite/src/ui/statuslaw.cpp']:
        shutil.copy(f'{SNAP}/{os.path.basename(f)}', f)

def build_and_run():
    b = subprocess.run(['cmake', '--build', 'rewrite/build', '-j4'],
                       capture_output=True, text=True)
    if b.returncode != 0:
        return 'BUILD-FAIL'
    r = subprocess.run(['./rewrite/build/run_tests'], capture_output=True,
                       text=True)
    return r.stdout + r.stderr

results = []
for name, f, old, new in MUTANTS:
    restore()
    src = open(f).read()
    if src.count(old) != 1:
        print(f"ANCHOR-GUARD FAIL ({src.count(old)} hits): {name}")
        sys.exit(2)
    open(f, 'w').write(src.replace(old, new))
    out = build_and_run()
    import re as _re
    m = _re.search(r'(\d+) tests, (\d+) skipped, (\d+) failed', out)
    if 'error:' in out and not m:
        verdict, first = 'BUILD-FAIL', next((l for l in out.splitlines() if 'error:' in l), '')[:120]
    elif m and int(m.group(3)) == 0:
        verdict, first = 'MISSED', m.group(0)
    else:
        fails = [l for l in out.splitlines() if 'FAIL ' in l or l.rstrip().endswith('FAILED')]
        verdict = 'CAUGHT'
        first = (fails[0] if fails else (m.group(0) if m else 'no summary line'))[:120]
    print(f"{verdict:8s} {name}\n         -> {first}")
    results.append(verdict)
restore()
print("restored; final:", build_and_run().strip().splitlines()[-1])
print("SUMMARY:", results.count('CAUGHT'), "/", len(MUTANTS), "CAUGHT")
