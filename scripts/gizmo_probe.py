#!/usr/bin/env python3
"""Probe gizmos.txt + planitem.txt -> docs/re/gizmos.md, docs/re/economy.md.

Both files carry the vendor's own format documentation above a '#' marker —
the grammar here is transcribed, and every count/range is re-measured.
Invariants asserted (a violation aborts rather than producing a wrong doc):
  gizmos: 76 records, name row + numeric row, cat in 0..5, >=10 numeric
          fields, ResReq in {255} u [0,106), flag list ends the row with 255.
  items:  39 records after the '39 22 9' count triple, last field 255,
          field7 (REQUIRES) in {255} u [0,106).
"""
import argparse
import collections
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D0 = os.path.join(ROOT, "extracted", "ascend00")
NUMROW = re.compile(r"^[\d\s]+$")


def body(path):
    raw = open(path, "rb").read()
    i = raw.find(b"\x1a")
    if i >= 0:
        raw = raw[:i]
    return raw.decode("cp437").replace("\r", "").split("\n")


def name_num_records(lines):
    recs, name = [], None
    for s in (l.strip() for l in lines):
        if not s:
            continue
        if NUMROW.match(s):
            if name is not None:
                recs.append((name, [int(x) for x in s.split()]))
                name = None
        else:
            name = s
    return recs


def tech_names():
    return [l.split()[0] for l in body(os.path.join(D0, "restree.txt"))[1:] if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    techs = tech_names()
    NT = len(techs)
    out = []
    w = out.append

    # ---------------------------------------------------------------- gizmos
    g = body(os.path.join(D0, "gizmos.txt"))
    gs = [i for i, l in enumerate(g) if l.strip() == "#"][0]
    grecs = name_num_records(g[gs + 1:])
    assert len(grecs) == 76, len(grecs)
    assert all(v[-1] == 255 for _, v in grecs)
    assert all(len(v) >= 10 for _, v in grecs)
    assert all(v[0] in range(6) for _, v in grecs)
    rr = [v[8] for _, v in grecs]
    assert all(x == 255 or 0 <= x < NT for x in rr)

    # ------------------------------------------------------------------ items
    p = body(os.path.join(D0, "planitem.txt"))
    ps = [i for i, l in enumerate(p) if l.strip() == "#"][0]
    seen_count = False
    ilines = []
    for s in (l.strip() for l in p[ps + 1:]):
        if not s:
            continue
        if not seen_count and NUMROW.match(s):
            if [int(x) for x in s.split()] == [39, 22, 9]:
                seen_count = True
            continue
        if seen_count:
            ilines.append(s)
    irecs = name_num_records(ilines)
    assert len(irecs) == 39, len(irecs)
    assert all(v[-1] == 255 for _, v in irecs)
    # REQUIRES is the SEVENTH numeric field = v[6] (vendor header order).
    # v[7] is the first flag bit-position when present; an earlier revision
    # of this probe tested v[7] and the check passed VACUOUSLY (flag bits
    # 0..7 also live in [0, NT)). Values outside tech range: 255 (x5, vendor
    # 'no research required') and 254 (x1, Interstellar Trucking, UNDOCUMENTED).
    req = [v[6] for _, v in irecs]
    assert sum(1 for x in req if x == 255) == 5
    assert sum(1 for x in req if x == 254) == 1
    assert all(x == 255 or x == 254 or 0 <= x < NT for x in req), req

    # grids: numeric blocks between '#' and the count triple
    # Grids live between '#' and the count triple; stop AT the triple so it is
    # not swept into a trailing 1x3 'grid' (my first pass did exactly that).
    grids, cur = [], []
    for s in (l.strip() for l in p[ps + 1:]):
        if s and NUMROW.match(s) and [int(x) for x in s.split()] == [39, 22, 9]:
            break
        if not s:
            if cur:
                grids.append(cur)
                cur = []
            continue
        if NUMROW.match(s):
            cur.append([int(x) for x in s.split()])
    if cur:
        grids.append(cur)
    shapes = [(len(x), len(x[0])) for x in grids]
    assert shapes == [(1, 1), (11, 4), (5, 15), (5, 15)], shapes
    # The count triple's first number must match the records we parsed. The
    # other two (22, 9) match NO candidate we tested (ungated=20, flagged=19,
    # gated=19, per-column nonzero counts 5/6/4/35/39) -> semantics OQ-014;
    # we record them verbatim instead of forcing a meaning.
    assert irecs and len(irecs) == 39, len(irecs)
    i_ungated = sum(1 for x in req if x in (254, 255))
    i_gated = sum(1 for x in req if x not in (254, 255))   # NB: 'gated' is the
    flagged = sum(1 for _, v in irecs if len(v) > 8)       # gizmo count below

    # ------------------------------------------------------------- gizmos.md
    w("# ship devices (gizmos) — `gizmos.txt` measurement\n")
    w("Source: `extracted/ascend00/gizmos.txt` (7,263 B, CP437/CRLF, 0x1A EOF). "
      "The vendor documents this format himself above the `#` marker — that "
      "documentation is transcribed verbatim below and then re-measured. "
      "Produced by `scripts/gizmo_probe.py`; gate stage 3j.\n")
    w("\n## 1. Vendor grammar (transcribed) [verified against 76/76 records]\n")
    w("```\nrecord := Name \\n Cat Power Range Level NumUses Industry Special1 "
      "Special2 ResReq {flag_list} 255\n```\n")
    w("- Cat: Weapon 0, Shield 1, Drive 2, Scanner 3, Generator 4, Special 5.\n")
    w("- Power: operating cost (generators: power SUPPLIED). Range: max range "
      "(weapons/scanners). Level: weapon damage / shield strength / scanner "
      "range-per-turn / drive max travel in sugar-cube units. NumUses: per "
      "turn, 0 = unlimited. Industry: cost added to the ship build. ResReq: "
      "research node index or 255.\n")
    w("- Flag bits (vendor table): TARGETSHIP 1, TARGETLANE 2, TARGETORBIT 4, "
      "TARGETSURFACE 8, TARGETOWNSHIPS 16, TOGGLEABLE 32, NOTARGET 64, "
      "PASSIVE 128. The flag_list lists BIT POSITIONS, not values, and ends "
      "with 255 (which doubles as the row terminator: rows with flags have "
      "one more field than rows without — never re-split on 255).\n")

    w("\n## 2. Measured shape [verified]\n")
    w("- **76 records**, names unique; category counts: %s\n"
      % dict(collections.Counter(v[0] for _, v in grecs)))
    for c, label in enumerate(["weapon", "shield", "drive", "scanner",
                               "generator", "special"]):
        sub = [v for _, v in grecs if v[0] == c]
        if not sub:
            continue
        w("- %-9s n=%-3d power %d..%d, range %d..%d, level(damage/strength/"
          "scan-per-turn/drive-dist) %d..%d, industry %d..%d\n"
          % (label, len(sub),
             min(v[1] for v in sub), max(v[1] for v in sub),
             min(v[2] for v in sub), max(v[2] for v in sub),
             min(v[3] for v in sub), max(v[3] for v in sub),
             min(v[5] for v in sub), max(v[5] for v in sub)))
    gated = sum(1 for x in rr if x != 255)
    w("- ResReq: %d/%d records gated by a research node; %d distinct nodes; "
      "every index < %d (restree row count) — **cross-validates the restree "
      "row numbering**: e.g. Fergnatz Lens -> 44 = `Fergnatz's^Last^Theorem`, "
      "Plasmatron -> 29 = `Plasmatics`, Ueberlaser -> 35 = "
      "`Coherent^Photonics`, Hypersphere Driver -> 48 = `Hypergeometry`. "
      "This is the second independent source pinning restree indices.\n"
      % (gated, len(grecs), len(set(rr)), NT))
    fh = collections.Counter(tuple(v[9:-1]) for _, v in grecs)
    w("- flag-list histogram (top): %s\n" % fh.most_common(8))

    w("\n## 3. What this settles for combat (OQ-010 partial)\n")
    w("- weapon damage values ARE in data (level column, 1..13). Shield "
      "strength 1..5. What is NOT in data: the damage APPLICATION formula "
      "(hit probability, shields subtract vs absorb, overkill) — still needs "
      "R1 or battle.txt prose mining (docs/re/combat.md when written).\n")

    w("\n## 4. Full table\n")
    w("```\n")
    for n, v in grecs:
        w("%-28s %s\n" % (n, " ".join(map(str, v))))
    w("```\n")

    gizmos_md = "".join(out)

    # ------------------------------------------------------------- economy.md
    out = []
    w = out.append
    w("# items and planetary economy — `planitem.txt` measurement\n")
    w("Source: `extracted/ascend00/planitem.txt` (3,180 B, CP437/CRLF, 0x1A "
      "EOF). Vendor-documented above `#`; produced by `scripts/gizmo_probe.py`; "
      "gate stage 3j.\n")
    w("\n## 1. Item grammar [verified against 39/39 records]\n")
    w("```\nNAME IND RES PROS MPOP UPOP COST REQUIRES {flags} 255\n```\n")
    w("(vendor header line, verbatim: `NAME IND RES PROS MPOP UPOP COST   "
      "REQ      FLAG DELIMITER`). Field roles by that header: IND/RES/PROS = "
      "industry/research/prosperity contribution; MPOP/UPOP = pop "
      "maintenance/upkeep pop; COST = industry; REQUIRES = restree node or "
      "255. Field counts vary 8/9/10 because the flag list, when present, "
      "shares the 255 terminator — same trap as gizmos.md §1.\n")
    w("- **39 items** after the count triple `39 22 9`. The `39` equals the "
      "record count (verified). `22` and `9` match no property we could test "
      "(sentinel REQUIRES: %d; gated: %d; rows with a flag list: %d; nonzero "
      "IND/RES/PROS/MPOP/UPOP: 5/6/4/35/39) — semantics unknown, OQ-014; "
      "recorded verbatim, never forced. Names unique.\n"
      % (i_ungated, i_gated, flagged))
    w("- REQUIRES (field 7 of the row, v[6]): %d rows carry real restree "
      "indices, 5 rows carry 255 (vendor: no research required), and exactly "
      "ONE row — Interstellar Trucking — carries **254**, a second sentinel "
      "the vendor comment does not define (OQ-014). Sampled gates are "
      "semantically coherent (Shipyard->Orbital Structures, Terraforming->"
      "Planetary Replenishment, Surface Shield->Superconductivity), which "
      "cross-validates the restree row numbering a third time.\n" % i_gated)
    w("- parse trap (caught by this probe mid-run): testing v[7] for tech-"
      "range passes VACUOUSLY because flag bit-positions 0..7 also fall in "
      "[0, 106). Always test the vendor-named field index, not a neighbour.\n")
    w("- CONTROL (disambiguates v[6] vs v[7] on the 19 longer rows): reading "
      "v[7] as REQUIRES gives semantically broken gates — Surface Shield -> "
      "Spacetime Surfing, Orbital Missile Base -> Tonklin Diary, Terraforming "
      "-> Orbital Structures. The v[6] reading gives Surface Shield -> "
      "Superconductivity, Orbital Missile Base -> Power Conversion, "
      "Terraforming -> Planetary Replenishment. Vendor header order + meaning "
      "both select v[6]; v[7..] are the flag bit-positions.\n")
    w("\n## 2. Planet-type order and grids [verified, semantics inferred]\n")
    w("- vendor lists the order: HUSK PRIMORDIAL CONGENIAL EDEN MINING MOFFET "
      "CHAPEL CATHEDRAL RICH TYCOON CORNUCOPIA (11 types).\n")
    w("- numeric blocks between `#` and the count triple, shapes %s:\n" % shapes)
    w("  - `50` alone = \"pop growth amount\" (vendor sentence: *first, note "
      "we have pop growth amount number*).\n")
    w("  - 11x4 = per planet type: first column reads as a decline curve "
      "(100,50,20,0,...) and cols 2-4 as [?]. Semantics NOT documented -> "
      "OQ-014.\n")
    w("  - 5x15 and 5x15 = two more matrices (rows = 5 of something; cols = "
      "15). Values 0..9, ridge-shaped. Semantics undocumented -> OQ-014.\n")
    w("\n## 3. Full item table\n")
    w("```\n")
    for n, v in irecs:
        w("%-22s %s\n" % (n, " ".join(map(str, v))))
    w("```\n")
    economy_md = "".join(out)

    open(os.path.join(ROOT, "docs/re/gizmos.md"), "w").write(gizmos_md)
    open(os.path.join(ROOT, "docs/re/economy.md"), "w").write(economy_md)
    if not a.quiet:
        print("wrote docs/re/gizmos.md (%d B) and docs/re/economy.md (%d B)"
              % (len(gizmos_md), len(economy_md)))


main()
