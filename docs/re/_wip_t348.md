# _wip_t348 — PLANET-RECORD +0x0a: WRITER WITNESS THEN SEMANTICS (HARD BUDGET)

## S0 — ASSIGNMENT (from STATE.md t348, verbatim duties)
- Field: planet-record +0x0a (stride-123 records, phys 0x26d07b, NAME +0x00,
  chain start 0xAAE2 — r1-savestate.md:990 area).
- Known: "23 distinct, 0..50328 packed look" (r1-savestate.md ~:934);
  file-side TWO VALUE BANDS ~17.5k / ~50.2k; live value churns on UNOWNED
  records too; "pointer-like seed field repaired at load; not read by income
  recalc" (income-law.md:2050).
- METHOD ORDER (binding): (1) OFFLINE pointer-law test of the bands across the
  48-save corpus; (2) ONE bounded static store census pass over
  work/r331_disasm.txt ([reg+0xa] HIGH NOISE — one pass max); (3) live launch
  ONLY IF (1)/(2) names something. <=2 launches, <=35 tool calls.
- EXIT RAMP: writer EIP without semantics => bank partial + honest negative,
  t349 = WAIT-TRIGGER sentinel. No second hunt.

## S1 — SITTING CHECK (first action, tail-seek)
- live-timeline.jsonl tail: newest turn 1086 (56.sav/58.sav wall 03:46:48/59).
  NOT >1086 => negative, t348 stands. (Same finding as t346/t347 landing.)

## S2 — PRIMERS READ
- r1-savestate.md ~:934: +0x0a alongside +0x20/+0x4a/+0x55 unnamed; +0x10 is
  the dword slot-array pointer, runtime-filled (FILE values are counter-region
  artifacts, NOT valid pointers — t50 lesson).
- income-law.md:2050: +0x0a unmapped; two file bands ~17.5k/~50.2k; churns on
  unowned; pointer-like repaired at load; NOT read by income recalc.
- t53 controlled mutation (r1-savestate.md ~:990+): record blob copied
  VERBATIM file->RAM (rec1 differs ONLY at injected sentinels); needle rec0
  name HERMESSEN at member 0x26edd7; rec i = needle + 123*i.
  => the +0x0a BYTES are copied verbatim; whatever "repair" exists happens
  AFTER the blob copy (or the value is never repaired and merely reused).
- Cross-read from the t1086 timeline ship_raw (context, not measurement):
  pointer-shaped u32s in the 17k/50k bands appear as PLAIN decimal values
  (e.g. 17560, 50372, 17572) in ship records — same numeric bands as planet
  +0x0a file-side. Suggests one arena allocator's address space.

## S3 — OFFLINE CENSUS (probe 1, scripts/r348_planet0a_census.py, 48 saves,
##     7401 rec-samples, full output /tmp/t348_census.txt)
- distinct +0x0a values across corpus: 207; V=0 n=2385; LOW band ~17073..17700;
  HIGH band ~49900..50442. 50328-17560 == 0x8000 (bit-15 hypothesis tested).
- HYPOTHESIS BATTERY ALL FAILED (hits/samples): low16(+0x10 phys), low16(arr
  member), (arr-base)&0xffff, data-seg offset of p10 or of rec, star*40
  (36/7401 = coincidence), bit15 — NOTHING matches. V is NOT a self-offset of
  the record, NOT the slot-array pointer's low half.
- TARGET-SHAPE PROBE (DS = B+0x82bb0; B == 0x1bf4d8 in ALL 16 runs — fixed):
  DS+V for HIGH-band values lands in a BSS pool of race sprite filenames:
  strings 'data\smraceNN.shp' at DS+50117/50158/50208/50258 (stride 50);
  owner0's V=50213 == DS+50213 == exactly 'smrace06.shp' (the name part AFTER
  'data\'). LOW-band values land MID-string in the AIL_* debug-string pool
  (DS+17000..18200 = 'AIL_start_sequence(0x%X)\n' etc.) — NOT string starts.
  => DS+V coincidence is clean only for owner0; the alignment is INCONSISTENT
  across owners (owner1 V=50151 = smrace05-string MINUS 7). Pointer-to-shp-name
  as stated is NOT established; the numeric range overlap may be arena aliasing.
- OWNER LAW [verified, single save 60.sav + cross-checked]: +0x0a is CONSTANT
  PER OWNING RACE within one save: {0:[50213], 1:[50151], 2:[17640], 3:[17595],
  4:[17610], 255: 41 distinct}. 44/146 UNOWNED records carry a value that is
  also an owned-race value; the rest scatter in both bands.
- CHURN LAW [verified within-run]: 50/50 star-slots churn across the 20 saves
  of run r1deep-20261005-230146, and each slot's series is MONOTONE INCREASING
  (star0: 17103,17179,17230,17281,17306,17331...) — allocator-address look, not
  state. No owner-change events in that run to test V-vs-colonization directly.
- rec0 (member 0x26d0df, linear 0x26d057 — SAME address in all 16 runs) V
  differs across runs (0 / 49996 / 17169 / 50213...) => value is written at
  load/runtime, file blob carries whatever the last session left (t53 verbatim
  copy law).
- STATIC bounded pass (one pass as budgeted): [reg+0xa] lines inside
  +0x55/+0x57 anchor windows at 0x32099/0x320af read WORD [eax+0xa] where
  eax = [esi+0xab] + idx*27 — stride 27, a DIFFERENT record array (t249
  planet-object pointer field hosts it), testing bits 0 and 2 of that byte and
  OR/AND-ing bit 2 back. NOT our stride-123 field; no stride-123 writer named
  statically (as predicted: base is heap-relative, immediate grep is noise).

## S4 — LIVE LAUNCH 1 (of 2 budgeted; run work/r1/wp-lin-0x26D061-20261109-042523,
##     rc=1, base vote B=0x1bf4d8 EXACT, core=normal UNDER [dosbox] = INERT per
##     t304 CORE-CONF LAW — wp.conf L4; pty printed the Dynamic-core warning)
- ONE fire, boot/load class: 'Memory breakpoint : 0000:26D061 - 00 -> 06'
  eip=22d85c, banked work/r1/.../boot-fires.txt. Byte was 00 at arm (MEMDUMPBIN
  failed => no artifact rejection, but 00-baseline means NOT a nonzero-artifact
  fire: this is the first WRITE to rec0's +0x0a low byte in the session).
- EIP DECODED [verified]: pty code panel shows '0160:0022D82E 8B502C mov
  edx,[eax+002C]' — translation linear = file + P0 (0x22d82e-0x1bf450=0x6e3de).
  Fire EIP 0x22d85c = 0x22d82e+0x2e = FILE 0x6e40c = 'mov edx,[eax+0x2c]', the
  SECOND read inside the generic iterator-reset fn at file 0x6e3d0 (reads
  +0x2c/+0x28, writes +0x24/+0x2c — NOT the +0x0a writer). LAW 7: reader.
- Phase phases INCONCLUSIVE: every xsend logged 'window died before release';
  turn stayed 1086 across all 20 saves (NEXTTURN never advanced) — zero phase
  fires cannot be attributed to absence of writes.
- POST-RUN SAVE CENSUS (the real haul, scripts inline; run's own 20 saves +
  ring-final): rec0 member 0x26d0df V=17414 CONSTANT in all 20 saves (idle
  session), owner=0, and 17414 low byte == the fired 0x06. Cross-run table
  (17 runs): rec0 V in {0, 49917, 49996, 50213, 17169, 17414} — run-RANDOM;
  per-owner constants likewise run-random (owner0 low8: 0x25,0x4d,0x6,0xc...).
- RECONCILIATION with S3 churn law: within-run churn (monotone, 50/50 slots)
  was measured in the SELF-PLAY run (turns advancing); the wp run was IDLE
  (turn fixed) and rec0 did NOT churn. => churn is TURN-PROCESSING work, not
  idle repaint. 'repaired at load' + 'churns on turns' both stand.

## S5 — VERDICT (t348 exit ramp taken; launch 2 NOT spent)
SEMANTICS INCREMENT [verified measurement]:
1. +0x0a is written at LOAD TIME exactly once per record per session (fired
   00->06 mid-boot; word view: full 0x4406=17414 stamped), value == the
   record-owner's PER-RACE RUNTIME CONSTANT (owner0's constant == 17414 ==
   rec0's value in the same session).
2. The constant is run-random (allocator-address shape), stable for the whole
   session while idle, rewritten during turn processing, and its value's
   DS+V interpretation is owner-INCONSISTENT (S3) => pointer-to-shp-name REFUTED.
3. No income/pop consumer (income-law standing); file-side blob carries the
   previous session's leftovers verbatim (t53 law) — which is why the save
   census sees 207 distinct values across 48 saves while each save is tidy.
HONEST NEGATIVE: writer EIP UNNAMED (the fire is a reader at file 0x6e40c; the
store precedes it inside the load path, uncaught); the MEANING of the per-race
pointer-shaped constant UNNAMED. Field stays open; NOT OQ-016 (no income link
found — checked) and NOT a live OQ row at all (OQ-003 CLOSED t181; open rows
OQ-005/OQ-016/OQ-019 untouched). t349 = WAIT-TRIGGER sentinel per ramp.
REFUTED this iteration (to REFUTED-ROUTES): (1) DS+V==shp-name-pointer semantics;
(2) self-offset/low16/dataseg-offset battery for +0x0a; (3) idle-churn reading
of the corpus churn (churn is turn-driven).
