# DECISIONS — what still needs you (2026-11-03)

Three decisions + one optional resource question. A reply can be one line
("D1 batch: sheet looks right except C7; D2 a; D3 yes; RAM yes") — annotate
rows by id, or just say "as recommended" per item.

Status snapshot: ledger 16 closed / 3 open (OQ-005, OQ-016, OQ-019). OQ-021 —
the one that needed a debugger — CLOSED 2026-11-03 by live watchpoint witness;
the two pages you sent made it possible. Production game (:9) is your Oct-29
campaign driven to t1150 as the RE corpus; the original save is intact at
work/r1/game/RESUME.GAM.user-oct29.

## D1 — .shp sprite library ruling (closes OQ-005, the oldest open row)
Our decoder reproduces 1477 of 1557 vendor sprite records byte-lawfully. The
80 that don't fit cannot be closed by measurement: every reader in the game
takes dimensions from the record header, so the odd ones can only be adjudicated
by a human looking at frames, or by capturing the vendor game drawing them.
Deliverable waiting on you: work/r1/shp_png/decision-sheet.md (88 rows, 5
contact sheets under work/r1/shp_png/sheets/):
  A1..A15   your own Oct-29 verdicts transcribed — just confirm still accurate
  B1..B29   identified frames with thumbnails — confirm or correct the ID
  C1..C44   decode failures — rule each keep / junk / re-render
Batch rulings are explicitly fine: e.g. "all B correct; the 25 zero-byte ladder
slots = junk; mouse k5/k6/k7 + 3cfgnew = junk; cos_star k40..k51 = leave".
Effort: ~5 minutes.
Alternative if you'd rather not eyeball: say "draw-capture" and we run one
scratch session that makes the VENDOR draw those records and pixel-compares our
decode against its output — a measurement, no ruling needed.
If undecided: row stays open, rewrite unaffected (it renders its own vector
art; the codec is a validation asset).

## D2 — Per-ship fleet simulation: build scope decision (not an RE unknown)
The vendor tracks per-ship order states, gizmo inventories, and carrier/
invasion mechanics (all laws are now CITED and observable — 62,762-row census).
The rewrite models fleets as aggregate vectors instead, which reproduces vendor
outcomes on every pinned seed. We declared the gap a permanent BOUNDARY
(t209/t210/t256c) rather than silently leaving it — but "permanent boundary"
is really your call wearing our clothes:
  (a) aggregate stays — status quo, recommended unless gameplay fidelity of
      fleets is something you want for its own sake;
  (b) commission the per-ship sim — large but well-specified work (the AI
      dossier docs/re/ai-dossier.md is effectively a spec for it);
  (c) middle slice — per-ship transport/invasion layer only (carriers +
      landings), the smallest piece that would change observed behaviour.

## D3 — Definition of done: how long the loop keeps running
GOAL.txt says: stop when every open row is CLOSED. Strict-close forbids closing
on a plausible default, so some residues may be legally unclosable on this box
(player-testimony class). What remains with a documented closing route:
  OQ-005  -> D1 above
  OQ-019  -> sugar-cube scale: t293 scripted move-order capture (queued NOW)
  OQ-016  -> three one-shots: Phase Bomb forced-capture run; setup-time home
             draw law; word[+0x16] template source (static hunt)
  magnetron -> needs one witnessed use; scriptable via the t289 drive class
Beyond those, mining the corpus yields diminishing witnesses (three separate
full-corpus censuses came back empty — that's the shape of the tail).
RECOMMENDED (D3 = yes): run the remaining queue, then park the loop on a
sentinel and ship the project as "N/19 closed + honest capture-limited notes"
where anything resists. Alternatives: keep looping literally until zero open
(risk: churn against refuted-class routes), or stop now.

## D4 — Optional: VM resources (you offered; one thing is worth taking)
+8 GiB RAM (15 -> 23) is the only high-value add: OOM killed two batches (both
self-inflicted giant json reads, now law-forbidden), and heavy-debugger scratch
sessions are RAM-hungry. A 4th core only speeds compiles — model inference does
not run on this box, so neither change changes loop pace. Take it if free,
otherwise fine as-is.

## Resolved without you since the last check-in (no action needed)
- OQ-021 CLOSED by the debugger you green-lit: master-built dosbox-x, BPLM
  watchpoint, live presenter witness ("Your score is 42%", threshold V >=
  floor(2T/3)+1 measured — the vendor's own comment "over half" is decoration).
- OQ-023 closed earlier by an OBSERVED alliance event in your campaign's RAM.
- Vendor tutorial discarded per your grant; your Oct-29 save restored and
  backed up; VNC attaches are now assumed harmless on this box.
- Watchers retired; single capture writer running (two-writer law).

## Archive map (what got cut and where it went, 2026-11-03 slim)
archive/state-v2-full/2026-11-03/
  STATE.md            full 4077-line working memory incl. every LANDED block
                      (md5 a2faccfb648418045b2647be66364f10)
  OPEN-QUESTIONS.md   full 1846-line ledger with complete per-row evidence
                      (md5 e897be73e0fd4b06cb51aa0881c0ff5d)
  BLOCKED.md          full 615-line block register incl. closed history
                      (md5 2e7c0940e11e839390abb7c9ebf4c1a6)
  stop-report.md      the 2806-line v2 stop report (md5 5a061b7ce7b572bbaec67f494718b6cb)
  wip/                all 153 per-iteration working notes (_wip_t*.md, 1.3 MB)
Older history: archive/ralph-v1/ (v1), archive/state-v2-full/STATE-full-2026-10-28.md.
Anything a slimmed doc used to say is findable there; the slimmed docs carry
archive paths where the detail lives.
