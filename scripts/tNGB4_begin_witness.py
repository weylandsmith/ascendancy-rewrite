#!/usr/bin/env python3
"""tNG-B B4 WITNESS: Begin press -> SETTINGS-APPLY seam.
Laws docs/re/_wip_tNGB.md 'B4 VERDICT ROUND 2' + 'B4 VERDICT'. Checks the
app.log law lines captured by scripts/tNGB4_begin_shot.sh:
  1. ATMOSPHERE CLICK LAW [0x52eec..0x52f01]: default 1 -> 2 (wrap 3), and
     the summary word moves to Hostile.
  2. STATE-IDENTITY APPLY [begin block 0x52a44..0x52b75]: the apply triple
     maps wheels IDENTITY-wise — stars == the density rung the wheel last
     drew (kDensityStarCounts cycle), owners == the species word VERBATIM,
     gov == the atmosphere word VERBATIM.
  3. LIVE TERMS: 'newgame live stars S owners O' == the apply triple — the
     rebuild actually took (pre-B4 code enters play on the BUILT campaign:
     50 stars, 7 owners — S==75 and O==6 refute that).
  4. INTRO FOLLOW: 'ui raceintro ... atmosphere G' == the apply gov (the
     gated history.txt section rides the same wheel).
Exit 0 GREEN / 1 RED with named failures.
"""
import re
import sys

LOG = sys.argv[1] if len(sys.argv) > 1 else "/tmp/tNGB4_begin/app.log"
# Port cycle ladder (menulaw.cpp kDensityStarCounts) — same VISITED sequence
# as the vendor sorted table 0x895c8 from the Average default (B1 law).
LADDER = [50, 75, 100, 15, 25]

fails = []


def fail(msg):
    fails.append(msg)
    print(f"FAIL {msg}")


lines = open(LOG, errors="replace").read().splitlines()

# 1. atmosphere click law
atmos = [int(m.group(1)) for l in lines
         if (m := re.search(r"ui raceconfig atmos wheel (\d+)", l))]
if atmos != [2]:
    fail(f"atmos wheel sequence {atmos} != [2] (default 1 -> Hostile, "
         f"wrap-3 law 0x52efc)")
if not any("DIFFICULTYMORE" in l and "-> Hostile" in l for l in lines):
    fail("DIFFICULTYMORE summary word did not move to Hostile")

# 2. apply triple identity law
m = None
for l in lines:
    if (mm := re.search(r"ui newgame apply stars (\d+) owners (\d+) gov (\d+)", l)):
        m = mm
if not m:
    fail("no 'ui newgame apply' line (Begin out-param never filled)")
    sys.exit(1)
a_stars, a_owners, a_gov = map(int, m.groups())
if a_stars not in LADDER:
    fail(f"apply stars {a_stars} off the density ladder {LADDER}")
# one density click from the Average default -> visited rung index 1 == 75
if a_stars != LADDER[1]:
    fail(f"apply stars {a_stars} != 75 (one GALAXY_MORE click from Average)")
if a_owners != 6:
    fail(f"apply owners {a_owners} != 6 — species word VERBATIM identity "
         f"(one PLAYERS_MORE click from Five); owners != species-1 exposes "
         f"an off-by-one transform")
if a_gov != 2:
    fail(f"apply gov {a_gov} != 2 — atmosphere word VERBATIM identity "
         f"(vendor 0x52b44 stores the wheel byte verbatim)")

# 3. live terms == apply terms (gov term reads Campaign::govByte() — the
#    LIVE global value the dip charge consumes, not the handoff intent)
m = None
for l in lines:
    if (mm := re.search(r"newgame live stars (\d+) owners (\d+) gov (\d+)", l)):
        m = mm
if not m:
    fail("no 'newgame live' line (campaign rebuild not verified)")
else:
    l_stars, l_owners, l_gov = map(int, m.groups())
    if (l_stars, l_owners, l_gov) != (a_stars, a_owners, a_gov):
        fail(f"live ({l_stars},{l_owners},{l_gov}) != apply "
             f"({a_stars},{a_owners},{a_gov}) — play did NOT enter on the "
             f"wheel scenario (the t393 seam shape: built 50/7/gov1)")
    if l_stars == 50 and l_owners == 7:
        fail("live == the BUILT campaign (50,7) — apply never ran")
    if l_gov == 1 and a_gov == 2:
        fail("live gov frozen at 1 — atmosphere->byte[0x13bc4] plumb dead")

# 4. intro follows the atmosphere wheel
m = None
for l in lines:
    if (mm := re.search(r"ui raceintro specnum \d+ atmosphere (\d+)", l)):
        m = mm
if not m:
    fail("no 'ui raceintro' line after Begin")
elif int(m.group(1)) != a_gov:
    fail(f"intro atmosphere {m.group(1)} != apply gov {a_gov}")

if fails:
    print(f"RED ({len(fails)} failures)")
    sys.exit(1)
print(f"GREEN: atmos 1->2 wrap3; apply ({a_stars},{a_owners},{a_gov}) "
      f"identity-mapped; live == apply; intro rides gov")
