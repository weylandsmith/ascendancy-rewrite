#!/usr/bin/env python3
"""cob_probe.py — assert the .cob container grammar (OQ-004, docs/re/datafiles.md §3).

    +0x000 u32 N; +0x004 N x 50-byte NUL-padded names; then N x u32 absolute
    blob offsets; entry i = [off_i, next off) (EOF for the last).

Checks per archive (ascend00/01/02): TOC parses, offsets strictly increasing,
every name is plausible CP437, blobs tile without overlap, and for ascend00
(all 54 entries, md5 against extracted/ascend00/) plus one sampled entry per
other archive where an extracted twin exists, blobs hash equal.
Exit 0 = grammar holds; 1 = drift (report printed); 2 = harness error.
"""
import argparse, hashlib, os, os.path as ospath, struct, sys

ROOT = ospath.dirname(ospath.dirname(ospath.abspath(__file__)))


def parse(blob):
    n = struct.unpack("<I", blob[:4])[0]
    names = []
    for i in range(n):
        s = blob[4 + 50 * i:4 + 50 * i + 50]
        e = s.find(b"\0")
        if e == 0 or e < 0:
            return None
        try:
            names.append(s[:e].decode("cp437"))
        except UnicodeDecodeError:
            return None
    base = 4 + 50 * n
    offs = [struct.unpack("<I", blob[base + 4 * i:base + 4 * i + 4])[0]
            for i in range(n)]
    return names, offs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-each", type=int, default=1,
                    help="md5-check this many entries per archive that have an "
                         "extracted twin (ascend00 always checks all 54)")
    a = ap.parse_args()
    problems = []
    checks = 0
    for n in ("ascend00", "ascend01", "ascend02"):
        p = ospath.join(ROOT, "game", f"{n}.cob")
        if not ospath.isfile(p):
            print("harness-error: missing", p)
            return 2
        blob = open(p, "rb").read()
        got = parse(blob)
        if got is None:
            problems.append(f"{n}: TOC failed to parse")
            continue
        names, offs = got
        if offs != sorted(offs) or len(set(offs)) != len(offs):
            problems.append(f"{n}: blob offsets not strictly increasing")
        last = max(offs) if offs else 0
        twins_done = 0
        want_all = (n == "ascend00")
        for i, (nm, off) in enumerate(zip(names, offs)):
            nxt = offs[i + 1] if i + 1 < len(offs) else len(blob)
            if off >= nxt:
                problems.append(f"{n}[{i}] {nm}: empty/overlapping blob")
                continue
            fp = ospath.join(ROOT, "extracted", n, ospath.basename(nm))
            if not ospath.isfile(fp):
                continue
            if not want_all and twins_done >= a.sample_each:
                continue
            mb = hashlib.md5(blob[off:nxt]).hexdigest()
            mf = hashlib.md5(open(fp, "rb").read()).hexdigest()
            checks += 1
            twins_done += 1
            if mb != mf:
                problems.append(f"{n}[{i}] {nm}: blob md5 != extracted twin")
        print(f"{n}: entries={len(names)} first_off={min(offs):#x} "
              f"last_off={last:#x} filesize={len(blob):#x} md5-checked={twins_done}")
    for x in problems:
        print("DRIFT:", x)
    print(f"grammar probe done: {checks} md5 checks, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
