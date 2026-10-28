# t109 WIP — count-column purge (scratch, streams as probes land)

Assignment: STATE.md t109. Re-run the census-offset set with the t108-FIXED
tools, replace the S2 table numbers IN PLACE (old numbers kept as struck
"old verifier" column), re-adjudicate the t106 +0x55 four-WORD list + t107
amendments against the authoritative rule with fresh counts re-cited, append
S8 statement that no banked LAW changed, run r1_t108_disp32_audit.py as the
closing control, STOP-REPORT.

## P1 runs launched
- bg proc_b412a6555c08: r1_t107_writers_full.py 0x44 0x46 0x48 0x4e 0x50 0x52
  0x54 0x58 0x5d 0x66 0x67 0x88 0x90 -> /tmp/t109_full.txt
  then r1_t106_writers.py 0x55 0x42 -> /tmp/t109_t106.txt; status /tmp/t109_status
- Baseline being purged (S2, old verifier): 44:30 46:12 48:19 4e:26 50:22
  52:33 54:26 58:39 5d:29 66:43 67:31 88:23(full-op) 90:14; WORD 44:9 46:3
  48:3 4e:5 50:8 52:9 54:0 58:0 5d:3 rest 0.

## P2 results (BANKED -> census-audit.md S2 replaced in place)
Corrected table (full-op in-code | WORD): 44:22|11  46:7|3  48:10|3  4e:8|5
50:13|8  52:23|9  54:22|0  58:32|0  5d:25|3  66:15|0  67:30|0  88:23|0  90:14|0.
Cross-check green: full-op in-code +0x66 = 15 == S7 hand count exactly.
Word counts UNCHANGED vs old S2 WORD column -> confirms S8 (phantoms were
byte-op-only; WORD/DWORD always passed fn-start decode).
+0x55 (limited tool): 6 verified / 5 in-code / WORD in-code 4 — exactly the
t106 four: 0x37f9a seed, 0x39224 item-37 +10, 0x44054 +2 scan, 0x3a664 ctor
copy. All survive. (Extra byte in-code site 0x757cf add8, fn 30; data-region
0x82d6a.) +0x42: 23 verified / 19 in-code / WORD 13; colonise 0x23cac survives.
Old OQ-016 numbers "+0x55 now 12 verified (4 word), +0x42 28" were inflated
by 6 and 5 byte-op phantoms respectively.

## P3 adjudication (BANKED)
t107 amendments all survive authoritative decode, counts re-cited:
0x49307 mov DWORD [eax+0x90],0 in +0x90 set of **14** (combat S2d stands);
0x24a00 BYTE +0x58:=0 and 0x3ca60 BYTE +0x58:=2 in +0x58 set of **32** in-code
(aicode S6 stands); 0x41d80 DEC DWORD +0x88 in +0x88 set of **23** (aicode
S7.4 stands). Op-family gap sites 0x21b77/0x21b85 (INC WORD +0x44), 0x467b6,
0x39084 (INC +0x50) re-found by full tool only — limited op set lacks group
80/FF + shifts entirely, and lacks group-80 /1 (so even the banked +0x66
|=1/|=2 pair is invisible to r1_t106_writers alone; S2's old "+0x66 43" came
from full-op runs).

## P4 closing control (BANKED -> census-audit.md S9 item 4)
r1_t108_disp32_audit.py RC=0 (/tmp/t109_control.txt): 0x7458e 277 raw u32 runs,
58 moffs verified, 0 FPU; 0xccb 1 raw, 0 moffs, 0 FPU; +0x67 8 raw, 0/0.
Identical to the t108 S6 run. Control GREEN.
