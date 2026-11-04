# t185 WIP — OQ-019 magnetron identity (loaded gizmo table census)

Assignment (STATE.md NEXT t185, STATIC, last fully-offline candidate):
 (a) enumerate category-5 rows in the scenario-LOADED gizmo design table
     (live copy, member B+0x82bb0+0x7650c raw-record start, stride 0x6a,
     76 rows, name ASCIIZ at rec+0 — t87 loader law; t101 CORRECTION:
     ships.md S12's 0x7653c "row" base = raw+0x30), re-run the slot census
     against LOADED rows rather than file order;
 (b) if a loaded row is named Lane Magnetron, cite the row-index law linking
     it to immediate 0x24 at 0x4159a (FUN_00049768 slot-finder call).
Refutation context (t183): file order puts idx36 = Disarmer, Lane Magnetron
= file row 59; ship slot census 15/35 carry idx36, 0 carry idx59.

Plan (<=35 calls):
 1. WIP (this file).
 2. Live-table tool scripts/r1_t185_magnetron_census.py over 20 playcap
    saves: names+cat of all 76 loaded rows; cat5 name list; slot-occupancy
    census by cidx over all ship rows (t101 locator: base B+0x82bb0+0x3a095
    stride 0x162, owner hi16 of dword+0x54 < 20, ring +0xab stride 7 x25);
    file-vs-live row identity check.
 3. Ghidra headless: disasm around 0x41590..0x415c0 — prove/disprove that
    edx==0x24 is the literal call-site value vs a loaded variable (cites the
    index law for (b)).
 4. Bank to ships.md S18-adjacent (new S19 or S17 T6 amendment), OQ-019 row,
    STATE.md, gate, audit, commit.

## Findings
F1 [verified, extracted/ascend00/gizmos.txt row order + t87 t87 76/76
live-name match RC=0 on 60.sav]: the loaded design table row 36 is
**Recaller** (gizmos.txt:196, cat 5), row 37 = Disarmer, row 60 =
Lane^Magnetron. t183's §17-T6 parenthetical "index-36 == Disarmer ...
Magnetron = file row 59" is OFF BY ONE ROW (t183's ad-hoc row map); the
correct file-order indices are Disarmer=37, Lane Magnetron=60.
SECOND independent numbering proof: gizhelp.txt:695-699 prints
"#Recaller / #5 7 0 0 0 40... / help gizmo36" — the vendor's own help tag
binds Recaller to 36. gizhelp.txt:1173-1176 binds Lane^Magnetron to
gizmo60 (and its inline stats line differs from gizmos.txt: Range 25 vs
50, ResReq 255 vs 50 — the two files are NOT byte-identical for row 60).
F1b [verified gizhelp.txt:695-702]: Recaller help text = "creates an
unstable shunt through star lane space to a ship's home system. The ship
using the Recaller moves instantly into the shunt and arrives immediately
at its home system." — instant-transit semantics matching the kind-5
placement branch far better than the Magnetron ever did. NumUses field = 0
in gizmos.txt col5 for Recaller (help header line same), while Magnetron = 1.
F2 (census tool scripts/r1_t185_magnetron_census.py — first run had a
slice bug m[a:m[a+0x40]] -> byte-value end; fixed, rerun pending).
First-run partial [measured before fix, table-name leg broken but SLOT leg
valid]: occupied cidx census across all work/r1 saves incl playcap:
idx36 (Recaller) 129 slot-occurrences; idx60 (Lane Magnetron) 360; idx37
(Disarmer) ABSENT from census output. So ships DO carry both 36 and 60;
the 0x4159a branch keys on 36.
NOTE: work/r1 has MANY run dirs; the campaign autosave ring that holds the
1234-row fleet is work/r1/playcap/ (n=38 ship-table rows); several other
r1thr-* dirs are thread-probe runs with EMPTY scenario state (dword
0x43489>>16 = 0) — not save failures, just headless probe boots.


## CLOSE (t185 DONE)
Final artifacts: ships.md §19 (+ §16 item-3 UPDATE + §17-T6 SUPERSEDED
bracket), OPEN-QUESTIONS OQ-019 STATUS t185 block, STATE.md LANDED t185 +
NEXT t186 idle re-arm. Census tool RC=0 verified (1368 members, 0 name
mismatches; output snapshot work/r1/loop/t185_census_out.txt). Headline:
0x4159a branch = RECALLER (t183 off-by-one corrected); MAGNETRON use-site
FOUND = FUN_0004ca50 case cl==0x3c @0x4cd5c -> 0x220a8 + kind5 -> 0x21f58
placement (star + (0,-200,0) + rng%200 x2, jitter const live -200.0 at
B+0x82bb0+0xaee) -> 0x496e4 slot rebuild; 0x4a360 use-word guard
0x4a373..0x4a390 (design[+0x42]!=0). Gate 0, LEDGER AUDIT OK.
