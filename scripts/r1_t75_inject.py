#!/usr/bin/env python3
"""r1_t75_inject.py — OQ-021 discriminating injection (t75).

Laws in force (all measured): .gam planet chain at 0xaae2, stride 123, name at
+0x00 (t53); OWNER byte .gam +0x33 == RAM planet-record +0x57 (t75 join:
83/83 rows incl the one owned Verithil I == 0; unowned == 0xFF). Star-level
0x33 writes are VOID (unowned stars legitimately hold 18/250 there).

Plan: total stars T=50 (hi-u16 DAT_00016143). The planet chain holds 29
distinct stars; AI home stars (Stavern/Chloros/Syzygifer/Oslo) are NOT in the
chain (verified zero collisions t75), so injecting owner=0 on ALL chain stars
touches no AI: player = 29/50 = 58% — ABOVE half, BELOW two-thirds.
Fire => threshold in (50%, 58%] (the ">over half" comment class).
No fire across all post-end-turn slots => threshold >= 58% (two-thirds class).

Writes ONLY the work/r1/game scratch copy (never game/). Backup .pret75.
--restore restores. Usage: r1_t75_inject.py <resume-file> [--restore]
"""
import re, sys, shutil, os, struct
from collections import Counter

NBASE = 0xAAE2
STRIDE = 123
OWNER_OFF = 0x33
KEEP_STARS = {b"Chloros", b"Oslo", b"Syzygifer"}   # AI homes, left untouched
ROMAN = rb"\s+(I{1,3}|IV|V|VI{1,3}|VIII|IX|IX|X)$"

def chain_records(data):
    recs, k = [], 0
    while True:
        base = NBASE + k * STRIDE
        nm = data[base:base + 30].split(b"\0")[0]
        if not nm or not all(32 <= c < 127 for c in nm):
            return recs
        recs.append((base, nm))
        k += 1

def star_of(pname):
    return re.sub(ROMAN, b"", pname)

def main():
    path = sys.argv[1]
    bak = path + ".pret75"
    if "--restore" in sys.argv:
        if os.path.exists(bak):
            shutil.copy2(bak, path)
            print("restored", path)
        else:
            print("no backup at", bak)
        return
    data = bytearray(open(path, "rb").read())
    recs = chain_records(data)
    if len(recs) < 70:
        print("ABORT: chain short", len(recs)); sys.exit(2)
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    stars = {}
    for base, nm in recs:
        stars.setdefault(star_of(nm), []).append(base)
    injected, kept = [], []
    for star, bases in sorted(stars.items()):
        if star in KEEP_STARS:
            kept.append(star); continue
        for b in bases:
            if data[b + OWNER_OFF] != 0x00:
                data[b + OWNER_OFF] = 0x00
        injected.append(star)
    # load-path needle (t53 law): rec0 planet renamed HERMESSEN
    nm0 = bytes(data[NBASE:recs[0][0] + 30]).split(b"\0")[0]
    data[NBASE:NBASE + 30] = b"HERMESSEN" + b"\0" * 21
    open(path, "wb").write(bytes(data))
    print("chain recs:", len(recs), "stars:", len(stars))
    print("injected stars (owner=0):", len(injected), [s.decode() for s in injected])
    print("kept (AI home):", [s.decode() for s in kept])
    print("rec0", nm0.decode("cp437", "replace"), "-> HERMESSEN")
    print(f"expected player stars post-load: {len(injected)} of 50 = "
          f"{100*len(injected)//50}% (fires >1/2; 2/3=34 unreachable here)")

if __name__ == "__main__":
    main()
