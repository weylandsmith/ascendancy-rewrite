#!/usr/bin/env python3
# t411 mutation campaign. Each mutant: patch -> incremental build ->
# run_tests -> expect FAIL -> restore. PITFALL t410 F6: run this under
# execute_code/background with the restore-guard (finally: restore + rebuild),
# never a foreground call that can time out mid-mutant.
import subprocess, sys, os, shutil

ROOT = '/home/hrethric/projects/ascendancy'
os.chdir(ROOT)
files = ['rewrite/src/ui/mapchrome.cpp', 'rewrite/src/ui/cam3d.cpp',
         'rewrite/src/ui/mapchrome.h', 'rewrite/src/ui/vendortext.cpp']
snap = {f: open(f).read() for f in files}

def restore():
    for f, s in snap.items():
        open(f, 'w').write(s)

def build():
    r = subprocess.run(['cmake', '--build', '.', '-j6'],
                       cwd=f'{ROOT}/rewrite/build', capture_output=True, text=True)
    return r.returncode

def run_tests():
    r = subprocess.run(['./run_tests'], cwd=f'{ROOT}/rewrite/build',
                       capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout

MUTANTS = [
    ('M1 mottle cell 6->4 (>>2)', 'rewrite/src/ui/mapchrome.cpp',
     'const int cx = x / 6, cy = y / 6;', 'const int cx = x >> 2, cy = y >> 2;'),
    ('M2 mottle cell 6->8', 'rewrite/src/ui/mapchrome.cpp',
     'const int cx = x / 6, cy = y / 6;', 'const int cx = x >> 3, cy = y >> 3;'),
    ('M3 mottle per-pixel (pre-t411)', 'rewrite/src/ui/mapchrome.cpp',
     'const int cx = x / 6, cy = y / 6;', 'const int cx = x, cy = y;'),
    ('M4 depth-dim ramp reversed', 'rewrite/src/ui/cam3d.cpp',
     'static const int kDim[4] = {96, 160, 224, 256};',
     'static const int kDim[4] = {256, 224, 160, 96};'),
    ('M5 depth-dim far band unscaled', 'rewrite/src/ui/cam3d.cpp',
     'static const int kDim[4] = {96, 160, 224, 256};',
     'static const int kDim[4] = {200, 224, 240, 256};'),
    ('M6 depth-dim near band scaled', 'rewrite/src/ui/cam3d.cpp',
     'static const int kDim[4] = {96, 160, 224, 256};',
     'static const int kDim[4] = {96, 160, 224, 200};'),
    ('M7 depth-dim out-of-domain 0', 'rewrite/src/ui/cam3d.cpp',
     'return cls < 0 || cls > 3 ? 256 : kDim[cls];',
     'return cls < 0 || cls > 3 ? 0 : kDim[cls];'),
    ('M8 bevel mid brightened', 'rewrite/src/ui/mapchrome.h',
     'inline constexpr RGB kBevelMid{49, 54, 53};',
     'inline constexpr RGB kBevelMid{119, 119, 119};'),
    ('M9 bevel mid==in (no ramp)', 'rewrite/src/ui/mapchrome.h',
     'inline constexpr RGB kBevelIn{5, 6, 6};',
     'inline constexpr RGB kBevelIn{49, 54, 53};'),
    ('M10 blend-mode line removed (WIRING — witness-caught, pin-expected-MISS)',
     'rewrite/src/ui/vendortext.cpp',
     '    SDL_SetTextureBlendMode(tex, SDL_BLENDMODE_BLEND);\n', ''),
]

results = []
try:
    for name, path, old, new in MUTANTS:
        src = snap[path]
        if old not in src:
            results.append((name, 'PATCH-MISS')); continue
        open(path, 'w').write(src.replace(old, new, 1))
        if build() != 0:
            results.append((name, 'BUILD-FAIL')); restore(); build(); continue
        rc, out = run_tests()
        nfail = out.count('FAIL')
        results.append((name, ('CAUGHT' if rc != 0 else 'MISSED'), nfail))
        restore()
        build()
finally:
    restore()
    build()
    rc, out = run_tests()
    print('AFTER-RESTORE:', out.strip().splitlines()[-1])
for r in results:
    print(*r)
