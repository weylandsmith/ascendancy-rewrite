# STATE — machine-readable working memory for the loop
# Update EVERY turn. A fresh session must be able to resume from THIS file alone.

phase: P1
milestone: 1  # 0..6 ; gate.sh keys build/test stages off milestone >= 3
updated: 2026-10-03T06:30
turn_log_recent:
  - "seed: environment installed, cob.py extracts 468 files, Ghidra+MCP wired, plan written"

## CURRENT FOCUS
P1 data formats, starting with the ascend02 .tsv/.bin table pair.

## NEXT ACTION (exactly one)
Write scripts/tsv_probe.py: parse all .tsv tables in extracted/ascend02
(delimiter, header rows, column count per line, types); dump column
inventory to docs/re/tables.md. Cross-check one row of galactic.tsv
against galactic.bin bytes.

## KNOWN-ISSUES / PARKING LOT
- Ghidra headless server: scripts/ghidra_headless_up.sh must be started
  before any mcp ghidra calls; health = GET 127.0.0.1:8089/health.
- dosbox audio: no sound device in this box; run dosbox with
  nosound=true for captures (visual only).
- resume.gam may be from a different version than the shipped exe —
  verify version bytes before trusting it as golden data.
- radare2 unavailable on Debian 13; do not waste turns looking for it.

## DEFINITION-OF-DONE (from goal contract)
See docs/PLAN.md P6 + goal contract. All P0-P6 items checked below.

## CHECKLIST
[P0] env verified
[x] P1a .cob format spec (docs/FINDINGS.md)
[ ] P1b .tsv/.bin tables
[ ] P1c .shp sprites
[ ] P1d .gam saves
[ ] P1e FLIC/audio inventory
[ ] P1f text encodings
[ ] P2 Ghidra subsystem specs (9 subsystems, docs/re/*.md)
[ ] P3 engine skeleton builds, importer verified, headless smoke test
[ ] P4 all systems ported with tests
[ ] P5 UI+media parity pass
[ ] P6 full campaign playable to victory; README
