# tOQ19-AUDIT — ASSIGNED ROUTE IS CITED-DEAD (premise audit, zero capture)

Session start 2026-11-27 ~18:15 EST. Fresh session; resumed from STATE.md alone.
Assignment (STATE.md:236-251): "tOQ19-1: run the ONE scripted-move capture
session ... driver scripts/r297_order_session.py". NOT RUN. Reason below, every
claim a citation, no inference.

## A1. Four independent binding sources forbid the assigned session
1. REFUTED-ROUTES.md:465-467 (verbatim): "The scripted MOUSE session class is
   also budget-spent by standing law (t293 three + t297 one + t298 three): the
   next witness on the selection/order legs is the debugger class (t299), not
   launch #4." -> a r297/r298 mouse launch is launch #7+ of a budget-spent class.
2. REFUTED-ROUTES.md t322 AMENDMENT (line 888): "THE BATCON MOUSE ROAD IS DEAD
   IN-CAPTURE". t322 armed the four batcon click-road legs
   {0x1AEF8, 0x1B91C, w43508_1b5e6, w43508_1baa7} LIVE FOR THE FIRST TIME over
   the exact t298-shape battery: all ZERO while btn_hdlr lived and the
   instrument verified (census-ctl MATCH=True). The session the assignment
   asks for is that battery again, with the same legs already measured dead.
3. REFUTED-ROUTES.md t323 AMENDMENT (line 907): "BATMODEWnd ACTIVATION HAS NO
   IN-SESSION TRIGGER" — census-complete: the runtime state field is WORD
   [win+0xb1]; the ONLY runtime switcher fn 0x31f30 is reached exclusively from
   fn 0x32100, which is NOT in the cited BATMODE class table. So even a perfect
   click choreography has no activator to drive.
4. REFUTED-ROUTES.md t324 (re-open condition discharged, NEGATIVE ABSOLUTE):
   live-RAM census of the BatModeWnd class table (the sole [rec+0xa7] install
   target, data payload offset 0x58e8, installer fn 0x1ac21) reproduces the
   cited table byte-for-byte; fn 0x32100 ABSENT (as are 0x31f30/0x339a4),
   10/10 saves identical. OPEN-QUESTIONS.md t324 note states it plainly:
   "Every OQ-019 capture route is now cited-dead: t319/t320 pump, t322 mouse,
   t323 activation, t324 class-table."

## A2. The loop's own handoff already forbade this exact launch
t439 LANDED block (git 1627049), item (vii): "CORRECTION TO t438 HANDOFF:
r297_order_session.py is NOT available — REFUTED-ROUTES.md:465-467
budget-spends the scripted-mouse class (t293x3+t297x1+t298x3, next witness =
debugger); t440 must not run it." The tRS- iteration that queued tOQ19-1
re-introduced a route the loop had already retired two handoffs earlier —
STATE.md:236-251 is the stale text, not the refutations.

## A3. The row itself is USER-GATED, independent of the route
DECISIONS.md D7 (USER, 2026-11-11, verbatim ask quoted there) applied as:
"OQ-016/OQ-019 DEFERRED (rows stay open, t329 S4 draft stays DO-NOT-APPLY)."
DECISIONS.md OQ-019 entry: "closing this row needs YOUR ruling — D2 (a/b/c)
plus accepting the cited-dead notes for select/destination + magnetron."
So no capture of any kind closes OQ-019; only a user ruling does. Spending a
capture budget on it would be wrong even if the route were alive.

## A4. Environment fact (secondary, not the reason)
work/r1/loop/GAME_HEALTH_LIVE.txt: "UNHEALTHY | G:DEATH(pid 1623906 gone, zero
harness dosbox-x in /proc); F:FEED-STALE(newest slot 51.sav 150161s old > 60s)".
The production game is down again (t277 TL-expiry class). Irrelevant to the
decision — the route is refuted on law, not on availability — but it rules out
"just run it anyway" as a cheap tiebreaker.

## A5. SITTING CHECK (performed first, NEGATIVE — no new play)
work/r1/playcap/live-timeline.jsonl size 10,512,108,087 B (unchanged from the
last iteration's mtime Nov 26 00:30); 400 KB tail-seek, 17 records parsed,
"turn" field == 1086 on every record == the corpus floor (t368 law: judge by
turn number, never file size). r1_t85g_sitting.py correctly NOT run.
Tree was clean at session start (git status --porcelain empty); the only files
newer than HEAD are gate-regenerated docs/re/*.md. No ruling, no hand edit,
nothing to adopt (t178).

## A6. DISPOSITION
tOQ19-1 is NOT executed. Honest negative banked here; OQ-019 STAYS OPEN
(strict-close — a refuted route is not a closure, and the row needs the USER's
D2 ruling regardless). STATE.md NEXT ACTION rewritten to the one live,
non-user-gated, derivable task (TPF5-A), with this audit cited so the next
session does not re-queue the dead session.

## A7. GROUNDWORK BANKED FOR THE REPLACEMENT TASK (offline, zero capture)
While verifying the replacement assignment was derivable, ran the whole-file
SHAPEFRAME census of extracted/ascend00/windows.txt (51 windows carry
SHAPEFRAME > 0; names verbatim from the census output):
- The four planet INDICATOR tiles PLRES / PLIND / PLPRO / PLPOP (TYPE 29,
  PARENT PLANETALLOC, lines 1536/1553/1570/1587) each carry
  `SHAPEFRAME -1` — i.e. NO per-widget frame record. Each has
  `SENDMESSAGE 50` with SENDPARAM1 0/1/2/4 and HELPINDEX plres/plind/plpro/
  plpop.
- Consequence for seam TPF5-A (D28 item 9, "clicking the frames along the top
  should pop up a window ... with the same mineral framing"): the popup's
  framing CANNOT come from a per-widget SHAPEFRAME word for these four names.
  The answer must be the popup lib resolved through the ds:0x9f10c cache path
  (tPF-4 join pattern: ctx ds:0x9f10c + 0x7d0 + id*32 — statically readable
  from saves, unlike the window registry which t316 proved runtime-rebuilt),
  cross-checked against the tPF-11 result that the RESEARCH screen's framing
  is the CODE-DRAWN chrome family, not a shape lib.
- Frame-word precedent set (census): list/popup-type windows use frame 7
  (RACELIST, LOADLIST, GIZLIST, PLANLIST, STATSHIPLST, PLAYERDIP, BatListWnd,
  HELPWINDOW, STATPLANLST all = 7). help.shp-k0 (336x256, measured tPF-5 P7)
  remains the tile-popup answer; item 9's indicator-popup leg is the open one.
This is constraint data only — TPF5-A itself is NOT attempted this iteration.

