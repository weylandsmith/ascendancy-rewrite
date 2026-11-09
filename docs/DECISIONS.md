# DECISIONS — what still needs you (2026-11-03)

Three decisions + one optional resource question. A reply can be one line
("D1 batch: sheet looks right except C7; D2 a; D3 yes; RAM yes") — annotate
rows by id, or just say "as recommended" per item.

Status snapshot (t367 update 2026-11-09): ledger 17 closed / 2 open (OQ-016,
OQ-019). D1 ANSWERED + APPLIED t367 (see the APPLIED note under D1 and the
USER RULING blocks at the tail). D2 answered (b), build queued t360+. D3
DEFERRED by you. OQ-021 —
the one that needed a debugger — CLOSED 2026-11-03 by live watchpoint witness;
the two pages you sent made it possible. Production game (:9) is your Oct-29
campaign driven to t1150 as the RE corpus; the original save is intact at
work/r1/game/RESUME.GAM.user-oct29.

## D1 — .shp sprite library ruling (closes OQ-005, the oldest open row)
>>> APPLIED t367 2026-11-09: OQ-005 CLOSED strict-close on your ruling page
>>> submit (12:45); mouse k4..k7 decode in the rewrite at 78x47 (shp.md S28);
>>> sheet dispositions final (3 rows KEEP-RULED). Your B5-B29 "drawn wrong /
>>> top-part chain" testimony is banked in shp.md S28 as user testimony — the
>>> prime suspect is our own dumper's X-class span-crossing paint, NOT the
>>> game's bytes; no ledger row opens on it. Nothing further needed from you.
REBUILD t347 (2026-11-09): the decision sheet was regenerated from banked
inputs only (zero capture) and now prints a CITED DISPOSITION on every one of
its 44 C-rows, so the ask you have to read is 3 rows plus a batch word. Sources
per row: shp.md S25 (t328 feasibility census), S26 (t330 live blit witness, run
dbg-t330b-20261107-080216), S27 (t344 selector law + corner witness, run
dbg-t344d-20261108-161132), and the t323 combat-unreachable amendment.

  41 of 44 rows LEAVE the ask (asserted by the generator, so the number can't
  drift silently):
    - 12 cos_star k40..k51 — all-zero headers, dims zero in EVERY slot, so the
      blit's own -1 gate (@0x5cb2b) draws nothing (S25.2/S12).
    - 25 ladder slots (destroy k14, expl00/01/03/03/04/04/05/07/08/08,
      orbex00 k8/k9, sg37/45/47/49expl k0+k9, sg66expl k0/k9, sg70expl k9) —
      measured span==header, i.e. ZERO stream bytes, in libraries named in
      extracted/ascend00/batfx.txt battle-effects (S25.2, t323).
    - 1starmap k1 — zero stream bytes and no selector names it (SHAPEITEM is
      k3/k4/k5/k7; windows.txt 456/477/498/517).
    - sg50expl k9 + sg64expl k0 — combat art, UNREACHABLE-BY-CAPTURE (t323).
    - 3cfgnew k12 — JUNK-CERTAIN: the vendor truncated it at file EOF.
  Nothing here is a guess about your files; it is what the vendor's own code
  does with those records. Batch-accepting them is one word.

  THE 3 ADJUDICABLE ROWS — C27-C29, mouse.shp k5/k6/k7. T330 MEASURED the
  draw-time dims slot (u16 pair at record offset 0, stored H-1,W-1), and T344
  found the selector: fn 0x54650's mode chain requests id mode+4 from the
  cursor position, so k4/k5/k6/k7 are the four screen-CORNER cursors
  (TL/TR/BL/BR) — TL and TR witnessed live byte-exact. The earlier
  "invalid dims / no selector anywhere" reading was wrong on both counts: the
  zero component was one half of a SIGNED bbox pair, and all four records are
  ONE 78x47 glyph at four anchors (12/12 file-measured, S27). What is still
  capture-limited is the PIXELS — no blit deref at k5/k6/k7 offsets occurred in
  the witness window. So the question is not keep-or-junk on broken data, it is:
  keep valid-but-seldom-drawn corner-cursor art as-is?

So the live ask:
  C27-C29   mouse k5/k6/k7 — keep as-is / junk. (Recommended: keep — the bytes
            are valid and the selector is known; junking them buys nothing.)
  BATCH     the 41 dispositions above — accept / contest specific row ids.
  B1..B29   identified frames with thumbnails — confirm or correct the IDs
            (work/r1/shp_png/decision-sheet.md + sheets/). Optional but it is
            the only part that could still surprise us.
  A6-A8     the 10status/2savegam/4loadgam triad you called "possibly junk
            data" — now a live keep/junk call from the thumbnails (they decode
            cleanly as 639x479 menu panels; we have never seen them drawn).
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
             T344/T347 (2026-11-08/09): C27-C29's selector FOUND (screen-corner
             cursor modes, TL/TR live-witnessed, shp.md S27) and the sheet was
             regenerated with per-row cited dispositions — the ask is now 3 rows
             + a batch word (see D1 above).
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

## USER RULING 2026-11-09 (chat, assistant as scribe) — D2
USER: D2 = (b) commission the per-ship fleet simulation — fidelity to the
USER:   original is the goal. Per the assistant's note accepted: NO permanent
USER:   config toggle; per-ship becomes THE engine once it passes the
USER:   pinned-seed suite; aggregate demotes to a test oracle during the
USER:   transition, removed after seeds agree.
USER: D1 = ruling page live (work/r1/d1page); D1 answer to follow via page submit.
USER: D3 = DEFERRED by user until D1/D2 work has landed.

## USER RULING 2026-11-09 12:45:01 (from ruling page)
USER: D1 mouse k5/k6/k7 = keep as-is
USER: D1 batch 41 dispositions = accept all 41
USER: D1 A6 keep=True, A7 keep=True, A8 keep=True
USER: D1 B-rows misidentified = none
USER: D1 notes: I don't think the A series are used anywhere, but it doesn't hurt to keep them. If nothing else, they're a historical curiosity, and maybe someday someone will pipe up with a story behind them. The B series is generally correct. B3 is the star-map research menu button icon, and B4 is an icon I don't immediately recognize or remember seeing anywhere in the game. B5-B16 are from the new game menu, B17-B29 are a subset of the planet screen manufactoring indicators, and B5-B29 are drawn wrong here. B5 contains the top part of the image for B6, B6 contains the top part of the image for B7, ... B17 contains the top part of the image for B18, B18 contains the top part of the image for B19, and so on.

## USER RULING 2026-11-09 12:45:31 (from ruling page)
USER: D1 mouse k5/k6/k7 = keep as-is
USER: D1 batch 41 dispositions = accept all 41
USER: D1 A6 keep=True, A7 keep=True, A8 keep=True
USER: D1 B-rows misidentified = none
USER: D1 notes: I don't think the A series are used anywhere, but it doesn't hurt to keep them. If nothing else, they're a historical curiosity, and maybe someday someone will pipe up with a story behind them. The B series is generally correct. B3 is the star-map research menu button icon, and B4 is an icon I don't immediately recognize or remember seeing anywhere in the game. B5-B16 are from the new game menu, B17-B29 are a subset of the planet screen manufacturing indicators, and B5-B29 are drawn wrong here. B5 contains the top part of the image for B6, B6 contains the top part of the image for B7, ... B17 contains the top part of the image for B18, B18 contains the top part of the image for B19, and so on.
