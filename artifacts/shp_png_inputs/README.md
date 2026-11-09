# artifacts/shp_png_inputs/ — the OQ-005 decision sheet's banked inputs (t347)

Why these two files are committed while `work/` is gitignored wholesale: the
t347 queue row exists precisely because the 2026-11-03 slim archived
`docs/re/_wip_*.md` and someone had to prove the decision sheet was still
reproducible. `scripts/r1_t278_decision_sheet.py` reads ONLY these two files
(all user quotes and citations live in the script), so these are the complete
durable input set for a sheet the user rules on. Same rationale as
artifacts/ascend_restored.bin (t343): small, capture-independent, expensive to
re-derive. Copied out of gitignored work/ per the t343 copy-into-tracked-dir
route (no `git add -f`).

## index_t278pristine.txt (13,510 B, md5 ed0e3acfd2956870ec11c22f6242b5c4)
The t197-era evidence-dump census, banked VERBATIM at t278 (md5 re-verified
2026-11-09). 88 record rows: 5 CONTROL + 10 RESTORED-V + 29 SPAN-FREE + 44
RESIDUE (rows C1..C44 of the sheet, in this file's order — the row ids the user
annotates, e.g. DECISIONS.md C27-C29, are pinned to it, so NEVER re-sort it).
Header lines carry the t182 law snapshot and the t197 walk-bound correction.

## ids.tsv (11,324 B, md5 42787120fa657fd8b75f4f19650e18e6)
t196 per-record vision identifications: header
`lib\trec\tclass\tunbounded\tidentification\tsource` + 82 data rows, tab-
separated. The generator keys on fields 0,1 (library, record) and takes field 4
as the identification. Comment lines start with `#` (class taxonomy EMPTY /
TINY / ART and the t197 unbounded tag are defined there).

## Regenerating the sheet from here
`scripts/r1_t278_decision_sheet.py` resolves each input from work/r1/shp_png/
first and falls back to this directory, so the sheet survives a wiped work/:

    python3 scripts/r1_t278_decision_sheet.py   # writes decision-sheet.md + index.txt

Zero capture, stdlib only. The script ASSERTS the 40/1/3 disposition split and
raises on any census row it cannot classify.
