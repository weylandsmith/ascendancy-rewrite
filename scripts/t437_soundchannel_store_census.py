#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t437 census: does the windows.txt SOUNDCHANNEL value land at window-record
+0x59 in LIVE saved memory, and what do the strategic play sites read?

Static law this verifies (docs/re/_wip_t437.md F2/F3):
  - parser fn 0x575e4 stores the SOUNDCHANNEL line as  mov WORD [rec+0x59],ax
    (0x57e7a), i.e. the u16 at +0x59 == the HIWORD of dword[rec+0x57].
  - the seven strategic play sites read  mov edx,[rec+0x57]; sar edx,0x10;
    cmp edx,-1; je skip  -> wrapper 0x4fb30 -> FUN_000500e0 (soundfx manifest).
  - windows.txt: SOUNDCHANNEL is 0 for 118 windows and "-0" (== 0) for ALIENDIP.

Method (t335/t336 corpus law): magic 0x12345678 + printable NAME at +0x20 are
the window records; handle = byte @ +0x41; truth = ON-DISK windows.txt joined by
NAME. Records are stored at arbitrary offsets, so +0x59 is read record-relative.

Exit 0 = measured. Prints per-save counts and the value distribution.
"""
import os, re, struct, sys, zipfile, collections, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAGIC = b"\x78\x56\x34\x12"


def file_truth():
    wt = open(os.path.join(ROOT, "extracted", "ascend00",
                           "windows.txt"), "rb").read().decode("latin-1").replace("\r", "")
    out = {}
    cur = None
    for line in wt.split("\n"):
        m = re.match(r"^NAME\s+(\S+)", line)
        if m:
            cur = m.group(1)
            out.setdefault(cur, None)
            continue
        m = re.match(r"^SOUNDCHANNEL\s+(\S+)", line)
        if m and cur:
            tok = m.group(1)
            # "-0" scanned by %d == 0
            out[cur] = int(tok)
    return out


def census(path, truth, per_rec_out=None):
    mem = zipfile.ZipFile(path).read("Memory")
    L = len(mem)
    vals = collections.Counter()
    named = 0
    hits = []
    for mo in re.finditer(MAGIC, mem):
        b = mo.start()
        if b + 0x120 > L:
            continue
        nm = mem[b + 0x20:b + 0x40].split(b"\x00")[0]
        if not (1 <= len(nm) <= 24 and all(32 <= c < 127 for c in nm)):
            continue
        named += 1
        name = nm.decode("ascii", "replace")
        w59 = struct.unpack_from("<H", mem, b + 0x59)[0]
        d57 = struct.unpack_from("<i", mem, b + 0x57)[0]
        sfx = d57 >> 16
        vals[w59] += 1
        if name in ("NEXTTURN", "NEXTTURNCONT", "TOGLANES", "TOGEMPIRE",
                    "TOGSHIPS", "TOGCOLONIES", "RESEARCH", "FLEET", "STATUS",
                    "GALAXY_MORE", "ALIENDIP", "PLANLIST", "PLSQBUT0", "RESWIN",
                    "HELPBUTTON0", "EVENTBUTTON0", "BatControlWnd", "INTRO"):
            hits.append((name, hex(b), w59, sfx))
        if per_rec_out is not None:
            per_rec_out.append((name, b, w59, sfx))
    return {"save": os.path.basename(path), "named": named,
            "w59_dist": dict(vals), "spot": hits}


def main():
    truth = file_truth()
    nonzero_truth = {k: v for k, v in truth.items() if v not in (0, None)}
    print("file truth: %d windows, non-zero SOUNDCHANNEL: %s" %
          (len(truth), nonzero_truth))
    dirs = [os.path.join(ROOT, "work", "r1", "playcap", "save")]
    dirs += sorted(glob.glob(os.path.join(ROOT, "work", "r1", "dbg-t*")))
    saves = []
    for d in dirs:
        if os.path.isdir(d):
            saves += sorted(glob.glob(os.path.join(d, "*.sav")))
    if not saves:
        print("NO SAVES"); return 1
    print("corpus: %d saves" % len(saves))
    all_recs = []
    dist = collections.Counter()
    named_total = 0
    mismatch = []
    for s in saves:
        try:
            r = census(s, truth, all_recs)
        except Exception as e:
            print("  SKIP", os.path.basename(s), repr(e)); continue
        named_total += r["named"]
        for k, v in r["w59_dist"].items():
            dist[k] += v
        for name, off, w59, sfx in r["spot"]:
            t = truth.get(name)
            if t is not None and w59 != (t & 0xffff):
                mismatch.append((r["save"], name, off, w59, t))
    print("records: %d named window records across %d saves" % (named_total, len(saves)))
    print("+0x59 value distribution (all named records):",
          dist.most_common(12))
    print("file-vs-RAM mismatches on spot-checked strategic windows:",
          len(mismatch))
    for m in mismatch[:10]:
        print("   ", m)
    # per-name aggregate for strategic controls
    agg = collections.defaultdict(collections.Counter)
    for name, b, w59, sfx in all_recs:
        agg[name][sfx] += 1
    keys = [k for k in agg if k in ("NEXTTURN", "NEXTTURNCONT", "TOGLANES",
            "TOGEMPIRE", "TOGSHIPS", "TOGCOLONIES", "RESEARCH", "FLEET",
            "STATUS", "GALAXY_MORE", "ALIENDIP", "PLANLIST", "PLSQBUT0",
            "RESWIN", "HELPBUTTON0", "EVENTBUTTON0", "BatControlWnd")]
    print("per-window HIWORD(dword[+0x57]) == play-site sfx id:")
    for k in sorted(keys):
        print("   %-16s %s" % (k, dict(agg[k])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
