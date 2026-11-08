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
UPDATE t328 (2026-11-07): the ask shrank. Our decoder reproduces 1513 of 1557
vendor sprite records byte-lawfully (t197 corpus). We then asked the vendor
itself which of the 44 failures it can even DRAW (shp.md S25, cited):
  - 39 records are CITED-NO-WITNESS: the vendor draws NOTHING for them.
    12 cos_star k40..k51 have zero dims in every slot -> the blit's own
    -1 gate (@0x5cb2b) refuses them outright; 25 ladder slots
    (destroy/expl*/orbex/sg*expl — all named in batfx.txt battle-effects)
    carry ZERO stream bytes; 1starmap k1 likewise (and no selector selects
    it). Nothing to keep, nothing to see — batch-ruling them junk is now a
    formality backed by measurement, not a guess.
  - 3cfgnew k12 is truncated at the file's EOF by the vendor itself:
    junk-certain. sg64expl k0 is combat art = unreachable by capture.
  - ONLY mouse k5/k6/k7 (sheet rows C27-C29) remained adjudicable, and
    T330 RAN (2026-11-08, docs/re/shp.md S26): the vendor's draw-time dims
    slot is MEASURED = the u16 pair at record offset 0 (stored H-1,W-1) —
    k5/k6/k7 are therefore VALID-dims records (78x47), not invalid. But NO
    selector anywhere names k5/k6/k7 (windows.txt requests only cursor
    shape 2), while the library itself draws on every right-bar panel open
    (records k0/k2 witnessed live). So the question shrank from 'keep or
    junk' to 'valid-but-unselected art: keep as-is?' — a formality.
So the live ask is now just:
  B1..B29   identified frames with thumbnails — confirm or correct the ID
            (work/r1/shp_png/decision-sheet.md + sheets/)
  C27-C29   mouse k5/k6/k7: keep / junk / wait-for-t330 — or say
            "draw-capture" and we run t330 instead of asking.
  A rows     restatement only; confirm if you like.
Effort: ~2 minutes. If undecided: row stays open, rewrite unaffected (it
renders its own vector art; the codec is a validation asset).

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
(player-testimony class). UPDATE t329 (2026-11-06) — routes re-scored against
cited evidence; the original list below over-promised two entries:
  OQ-005  -> D1 ruling remains the closure. T328 LANDED (2026-11-07): 39 of
             the 44 C-rows are now CITED-NO-WITNESS (vendor draws nothing —
             shp.md S25), 1 junk-certain, 1 unreachable; the live ask is
             B-rows + mouse C27-C29 only. T330 LANDED (2026-11-08): draw-time
             dims slot MEASURED (rec+0 u16 pair, shp.md S26); C27-C29 are
             valid-dims, unselected records — ruling is now a formality.
  OQ-019  -> CLOSED-ROUTE SUPERSEDED: the t293 scripted move-order capture
             and every follow-on capture route are now CITED-DEAD (t319/t320
             pump, t322 mouse, t323 activation, t324 RAM class table).
             Disposition packet drafted (docs/re/_wip_t329.md S4): closing
             this row needs YOUR ruling — D2 (a/b/c) plus accepting the
             cited-dead notes for select/destination + magnetron.
  OQ-016  -> UPDATE t339 (2026-11-07): the last zero-capture decode LANDED and
             came up EMPTY — no poster of msg 0x1c01 to BatControlWnd's slot 61
             exists anywhere in the image, the child SENDMESSAGE road (804/805)
             is structurally blocked, and the arming gate is reachable only via
             a self-bootstrap with no external entry (ships.md S58). The
             residue is now fully in the cited-dead class (EIGHT named legs):
             closing it is YOUR call (accept as unreachable, like the
             magnetron). Residue (5) build-order minutiae still needs a
             disposition (diminishing tail).
  magnetron -> CLOSED-ROUTE SUPERSEDED: scripted route retired (arming runs
             through the batmode-family pinned state WORD — docs/re/
             _wip_t329.md S2); carriage census shows zero carriers in your
             campaign and zero uses in the epochs that did carry
             (scripts/r329_magnetron_census.py). Static use-site law stands.
Beyond those, mining the corpus yields diminishing witnesses (three separate
full-corpus censuses came back empty — that's the shape of the tail).
RECOMMENDED (D3 = yes): run the remaining queue (t325-t328), then park the
loop on a sentinel and ship the project as "N/19 closed + honest
capture-limited notes" where anything resists. What the loop can close
without you: NONE end-to-end (OQ-016's tail residue still needs a word from
you too, though t325/t326 could move it a long way). Alternatives: keep
looping literally until zero open (risk: churn against refuted-class routes),
or stop now.

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
