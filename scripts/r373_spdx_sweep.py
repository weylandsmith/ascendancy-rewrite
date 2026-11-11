#!/usr/bin/env python3
"""r373_spdx_sweep.py — insert SPDX-License-Identifier headers (t373).

Per docs/re/_license_draft_t372.md S4: sweep set = git-tracked files with
extension {.c .cpp .h .hpp .py .sh}, MINUS archive/ (historical state;
provenance beats uniformity), MINUS files already carrying the identifier.
No copyright line is inserted (asserting a holder is the user's call, S7).

Placement law (measured t373 — 4 files carry a PEP-263 coding cookie on line 2
behind a shebang; pushing the cookie to line 3 would silently void it):
  - line 1 is a shebang  -> insert AFTER the shebang; if line 2 is a coding
    cookie, insert AFTER the cookie instead (line 3).
  - otherwise            -> insert as the new first line.
Comment syntax: '//' for c/cpp/h/hpp, '#' for py/sh.

Idempotent: rerunning prints inserted=0. Verify law (S4): after the sweep
  git ls-files ... | xargs grep -L SPDX-License-Identifier  -> prints nothing
and gate + run_tests stay green (comment-only change; pins compile the
sources so a broken comment is a build break).
"""
import os
import subprocess
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTS = {".c": "//", ".cpp": "//", ".h": "//", ".hpp": "//",
        ".py": "#", ".sh": "#"}
SPDX = "SPDX-License-Identifier: GPL-3.0-or-later"


def sweep_set():
    out = subprocess.run(
        ["git", "ls-files", "*.c", "*.cpp", "*.h", "*.hpp", "*.py", "*.sh"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [f for f in out.splitlines()
            if f and not f.startswith("archive/")]


def insert(path):
    p = os.path.join(ROOT, path)
    raw = open(p, "rb").read()
    if b"SPDX-License-Identifier" in raw[:600]:
        return "already"
    tok = EXTS[os.path.splitext(path)[1]]
    line = (tok + " " + SPDX).encode() + b"\n"
    lines = raw.split(b"\n")
    if lines and lines[0].startswith(b"#!"):
        if len(lines) > 1 and b"coding" in lines[1].lower():
            out = lines[:2] + [line] + lines[2:]     # after shebang+cookie
        else:
            out = lines[:1] + [line] + lines[1:]     # after shebang
    else:
        out = [line] + lines
    open(p, "wb").write(b"\n".join(out))
    return "inserted"


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "apply"
    ins = skip = err = 0
    for f in sweep_set():
        try:
            r = insert(f)
        except Exception as e:
            print(f"ERR {f}: {e}")
            err += 1
            continue
        if r == "inserted":
            ins += 1
            if mode == "check":
                print(f"MISSING {f}")
        else:
            skip += 1
    print(f"inserted={ins if mode=='apply' else 0} missing={ins if mode=='check' else 0} already={skip} err={err}")
    return 1 if (err or (mode == "check" and ins)) else 0


if __name__ == "__main__":
    sys.exit(main())
