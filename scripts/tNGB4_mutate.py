#!/usr/bin/env python3
"""tNG-B cycle-3 mutation campaign (B4 begin-press -> settings-apply seam).
Laws docs/re/_wip_tNGB.md 'B4 VERDICT ROUND 2'; pins
rewrite/tests/test_newgame_behavior_tNGB.cpp (tngb_atmosphere_rank_cycle,
tngb_newgame_settings_identity); witness scripts/tNGB4_begin_shot.sh +
tNGB4_begin_witness.py.
One mutant at a time: apply (anchor EXACTLY once) -> rebuild -> catch ->
restore from the pristine snapshot taken AT LAUNCH (COPY revert) ->
md5-verify, ABORT on mismatch. LAUNCH GUARD: green suite only.
Usage: tNGB4_mutate.py [names...]
"""
import hashlib
import os
import os.path as osp
import shutil
import subprocess as sp
import sys

ROOT = "/home/hrethric/projects/ascendancy"
ML = osp.join(ROOT, "rewrite/src/ui/menulaw.h")
MC = osp.join(ROOT, "rewrite/src/main.cpp")
SNAP = "/tmp/tNGB4_mutate_snap"

MUTANTS = [
    # T1: atmosphere wrap TERM [0x52eff jne] — off-by-one: 3 becomes
    # observable (domain 0..3), the pin's domain + visited legs fire.
    ("T1-atmos-wrap-term", ML,
     "    return r >= 3 ? 0 : r;",
     "    return r > 3 ? 0 : r;",
     "tests"),
    # T2: owners identity -> transform: species word MINUS ONE (the
    # player-count misreading the identity law refutes: word[state+0xd88]
    # is TOTAL races incl. the player).
    ("T2-owners-minus-one", ML,
     "    s.owners = species;  // identity law: wheel value == TOTAL races",
     "    s.owners = species - 1;  // MUTANT: player-excluded misreading",
     "tests"),
    # T3: the rebuild never runs (the t393 seam shape restored — Begin
    # enters play on the BUILT campaign). Witness: 'newgame live' line
    # disappears -> RED.
    ("T3-apply-never-runs", MC,
     "        if (newGame.set) {\n            std::string aerr;",
     "        if (false && newGame.set) {  // MUTANT: seam re-opened\n            std::string aerr;",
     "witness"),
    # T4: gov not plumbed (cfg.govByte keeps default 1 while the wheel said
    # Hostile) — the atmosphere->byte[0x13bc4] law leg dies. Witness live
    # gov term reads Campaign::govByte(), catches the frozen value.
    ("T4-gov-not-plumbed", MC,
     "        cfg.govByte = apply->gov;",
     "        cfg.govByte = 1;  // MUTANT: atmosphere wheel never reaches the global",
     "witness"),
]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def sh(cmd):
    return sp.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)


def launch_guard():
    r = sh("rewrite/build/run_tests")
    if r.returncode != 0:
        sys.exit("LAUNCH GUARD RED — suite not green, refusing to snapshot")
    os.makedirs(SNAP, exist_ok=True)
    for f in (ML, MC):
        shutil.copy2(f, osp.join(SNAP, osp.basename(f)))
        os.utime(f, None)
    return {f: md5(f) for f in (ML, MC)}


def restore(pristine):
    for f in (ML, MC):
        shutil.copy2(osp.join(SNAP, osp.basename(f)), f)
        os.utime(f, None)
        if md5(f) != pristine[f]:
            sys.exit(f"RESTORE MD5 MISMATCH {f} — ABORTING campaign")


def witness_catch():
    """CAUGHT == catcher exit != 0 (rc!=0 law for EVERY class)."""
    r = sh("bash scripts/tNGB4_begin_shot.sh")
    if "SHOTS" not in r.stdout:
        return True, "capture failed: " + r.stdout[-200:] + r.stderr[-200:]
    w = sh("~/tools/revenv/bin/python scripts/tNGB4_begin_witness.py "
           "/tmp/tNGB4_begin/app.log")
    first = next((l for l in w.stdout.splitlines()
                  if l.strip().startswith("FAIL")), "")
    return w.returncode != 0, first


def main():
    names = sys.argv[1:]
    todo = [m for m in MUTANTS if not names or m[0] in names]
    pristine = launch_guard()
    verdicts = []
    for name, path, old, new, catcher in todo:
        src = open(path).read()
        count = src.count(old)
        if count != 1:
            print(f"{name}: PATCH-GUARD anchor count {count} — SKIPPING")
            verdicts.append((name, "PATCH-MISS"))
            continue
        open(path, "w").write(src.replace(old, new))
        b = sh("cmake --build rewrite/build -j8")
        if b.returncode != 0:
            print(f"{name}: BUILD-FAIL (compile catches it) -> CAUGHT")
            verdicts.append((name, "CAUGHT(build)"))
            restore(pristine)
            continue
        if catcher == "tests":
            r = sh("rewrite/build/run_tests")
            caught = r.returncode != 0
            first = next((l for l in r.stdout.splitlines() if "FAIL" in l), "")
            print(f"{name}: tests rc={r.returncode} -> "
                  f"{'CAUGHT' if caught else 'MISSED'} {first}")
        else:
            caught, first = witness_catch()
            print(f"{name}: {catcher} -> "
                  f"{'CAUGHT' if caught else 'MISSED'} {first}")
        verdicts.append((name, "CAUGHT" if caught else "MISSED"))
        restore(pristine)
    b = sh("cmake --build rewrite/build -j8")
    r = sh("rewrite/build/run_tests")
    print(f"AFTER-RESTORE rc={r.returncode} build={b.returncode}")
    for f in (ML, MC):
        print("md5-ok" if md5(f) == pristine[f] else f"MD5-DRIFT {f}", f)
    n_caught = sum(1 for _, v in verdicts if v.startswith("CAUGHT"))
    print("VERDICTS:", verdicts)
    print(f"MUTATION {n_caught}/{len(verdicts)} CAUGHT")


if __name__ == "__main__":
    main()
