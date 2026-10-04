#!/usr/bin/env python3
"""Species special-ability probe (docs/re/abilities.md, gate 3m).

Asserts the three-source roster invariant and the charge/passive split:
  1. help.txt carries exactly 21 `// SA_<T>` + `help abilNN` blocks, indices
     contiguous 0..20, tokens unique, titles unique.
  2. Every raceNN.dip header token (20 of 21) equals the help block token at
     the same index; race02.dip is tokenless and its display name equals the
     abil02 title ('Orfa').
  3. Charged (carries 'amass the energy') blocks == 14; passive blocks are
     exactly indices {0,1,2,3,4,15,18}.
  4. rewrite/src/game/species.cpp kNotes has one entry per token, every entry
     cites '[help.txt L'.
Exits nonzero with a message on any violation."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
A00 = ROOT / "extracted" / "ascend00"
PASSIVE = {0, 1, 2, 3, 4, 15, 18}


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


help_txt = (A00 / "help.txt").read_bytes().decode("cp437")
segs = re.split(r"//------------", help_txt)
blocks = {}
for s in segs:
    m = re.search(r"// SA_(\w+)\s*\n\s*\nhelp abil(\d{2})\s*\n\s*\ntext\s*\n(.+?) Special Ability\s*\nendtext", s)
    if not m:
        continue
    idx = int(m.group(2))
    blocks[idx] = ("SA_" + m.group(1), m.group(3).strip(), "amass the energy" in s)

if len(blocks) != 21:
    fail(f"help.txt abil blocks = {len(blocks)}, want 21")
if set(blocks) != set(range(21)):
    fail(f"abil indices not contiguous 0..20: {sorted(blocks)}")
tokens = [blocks[i][0] for i in range(21)]
if len(set(tokens)) != 21:
    fail("duplicate tokens in help.txt abil blocks")
titles = [blocks[i][1] for i in range(21)]
if len(set(titles)) != 21:
    fail("duplicate titles in help.txt abil blocks")

charged = {i for i in range(21) if blocks[i][2]}
if charged != set(range(21)) - PASSIVE:
    fail(f"charged set changed: {sorted(charged)}")

for i in range(21):
    hdr = (A00 / f"race{i:02d}.dip").read_bytes().decode("cp437").splitlines()[0]
    m = re.search(r"SA_(\w+)", hdr)
    if m:
        if m.group(0) != tokens[i]:
            fail(f"race{i:02d}.dip token {m.group(0)} != help token {tokens[i]}")
    else:
        if i != 2:
            fail(f"race{i:02d}.dip header unexpectedly tokenless")
        name_m = re.search(r"for (.+?)\.\s*$", hdr)
        if not name_m or name_m.group(1).strip() != titles[2]:
            fail(f"race02 display name does not match abil02 title {titles[2]!r}")

cpp = (ROOT / "rewrite" / "src" / "game" / "species.cpp").read_text()
notes = re.findall(r'^\s+"(.*?)",\s*$', cpp.split("kNotes")[1].split("};")[0], re.M)
if len(notes) != 21:
    fail(f"species.cpp kNotes has {len(notes)} entries, want 21")
for n in notes:
    if "[help.txt L" not in n:
        fail(f"kNotes entry missing help.txt line citation: {n!r}")
noops = [n for n in notes if n.startswith("FILED NO-OP")]
if len(noops) != 4:
    fail(f"FILED NO-OP count = {len(noops)}, want 4 (the knowledge/build-on-black family)")

print(f"OK: 21 abilities, 14 charged / 7 passive, race02 tokenless->'{titles[2]}', kNotes 21/21 cited ({len(noops)} filed no-ops)")
