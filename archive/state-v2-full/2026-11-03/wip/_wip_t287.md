# _wip_t287 — diplomacy second-campaign corroboration (session scratch)

Session start 2026-11-03 ~08:25 EST. Assignment: STATE.md NEXT = t287.
Pre-check: watcher rows show t=1086 steady (no new turns since t286 — no
sitting steering needed). Production :9 live pid 660167 (timeout-wrapped
660165), ring cycling 10 s, DAT_482fb=0/50 rel_nonzero_cells=12 ships=30.

## Plan (from STATE.md t287 row)
1. Open ALIENDIP per known race from the species menu (READ-ONLY; close via
   Goodbye only on the measured row-1 band, else Escape-to-species-menu;
   NEVER click rows 2+ — trade rows can PROPOSE, t252 rendered 5 rows).
2. Bank disposition + dialogue lines vs watcher RAM relation-matrix rows at
   the same wall-second (tail-scan <=400 KB, OOM law).
3. Cross-check c-overlay STARS CONTROLLED line vs DAT_482fb on this seed.

## Safety laws in force (recap so a handoff can't miss them)
- NEVER PROPOSE/DECLARE/ABANDON/END-TURN (t244, t254).
- NEVER Escape at the BARE GALAXY MAP (t285: exits campaign to title menu).
  Escape is only attempted from INSIDE the NEGSCREEN panel, and every step is
  screenshot-verified before the next click.
- 2 consecutive no-effect clicks = STOP-AND-LOOK (bank + screenshot + flag).
- Kill by recorded PID only; SIGKILL on softlock.

## Findings
(wip — append as measured)

## F1. PRODUCTION WAS OFF-CAMPAIGN; RECOVERED (t287, 08:25-09:12 EST)
Session start: screen = Play Tutorial SELECT (7-item list), not galaxy map —
a VNC user (user's main PC per grants) navigated off-campaign; RAM campaign
intact (n=4 t=1086 relation rows streaming, RESUME.GAM md5 verified
5b382afbb78918, no tutorial ever STARTED so no clobber). Escape -> title
menu. Recovery = RFB click on "Return to Current Game" (row 4, slot
313-353, center 318,333) -> GALAXY MAP t=1086 confirmed by vision, zero turn
drift, zero proposals. Evidence chain: work/r1/t287-dip/{evidence_tutorial_
menu,esc1,nav_pre_enter,r4click5}.png.

## F2. NEW INPUT LAW: MENUS ARE HOVER-ARMED; xsend CLICKS FIRE THE STALE ROW
MEASURED 08:40:48: xsend warps then clicks, but SDL rejects synthetic
MotionNotify, so the game's hover state NEVER moved — the click activated
whatever row a REAL (XTEST) pointer last hovered. xsend click (318,333)
'Return to Current Game' from title menu -> TUTORIAL SELECT opened (the row
the VNC user last hovered). diff esc1 vs backgame = 248874 px. Consequence:
for every hover-driven menu, motion MUST arrive via XTEST (RFB) and the
highlight MUST be screen-verified before activation. xsend keys still work
(Escape 248874 px at title menu pops nothing, just re-renders; earlier
'c'-liveness probes remain valid).

## F3. RFB INPUT CHANNEL INSTRUMENT: scripts/r287_vncinput.py (KEEPER)
Speaks RFB 3.3 to the local x11vnc (:5910, -localhost -nopw) -> XTEST events
SDL accepts. Laws banked IN the file:
- 3.8 handshake + 4-byte security selection RESETS the socket on this build;
  3.3 flow (zero-terminated type list — this server answers EMPTY, then
  behaves as SecurityNone; 1-byte selection; NO SecurityResult) works.
- PointerEvent = u8 type, u8 down-mask, u16 x, u16 y. A trailing-mask pack
  (">BBHHB") sends down=0 always and desyncs 1 byte/event: hover moves,
  clicks do nothing (this bug ate three click attempts).
- COORDS: RFB coord == X ROOT coord (x11vnc framebuffer = whole Xvfb :9);
  game coords need +80/+100 (t250 origin law). Three-way evidence in file.
- scripts/r287_title_nav.py: title-menu highlight detector (cyan bg
  (16,69,74) vs dark (8,32,48), slots = separator-anchored 40 px pitch at
  y=233/273/313/353/393/433/473) + guarded 'enter' (refuses unless R4).
- xsend keyboard at title menu: Down x3 did NOT move the highlight (hover-
  driven menu ignores keys); mouse/XTEST motion is the ONLY selector there.

## F5. NEGSCREEN CORROBORATION RESULTS (full write-up docs/re/diplomacy.md §21)
Five-row option set + pixel-identical PLAYERDIP bands on both campaign seeds;
race02.dip:172 / race11.dip:173 verbatim; Goodbye(480,334) closes to species
menu on both. 'c' overlay R0-R3 lines EXACT vs watcher atts/states row0;
"STARS CONTROLLED 0" == DAT_482fb=0/50. Species rows here at y 61/100/139
(t252's 73/140/207 does NOT port).

## F6. "EXTINCT" ROW = ELIMINATED RACE, CONTACT REFUSED (adjudicated)
Row 3 prints "Extinct" (coswnd string static.txt:53); help.txt:775 "You
cannot contact species which are Unknown or Extinct."; MEASURED: two clicks
changed only the row highlight (4562 px, bbox in the row-list), right half
never became negscreen; RAM still carries states[0][3]=2 WAR att 318.
VISION HALLUCINATION WARNING: a full-screen read invented a dialogue line
("We are the last of our kind.") for this no-negscreen screen; 3x zoom shows
NO text. Always zoom before transcribing.

## F7. SESSION DISCIPLINE REMINDER (self-inflicted, caught cheap)
xsend click on the title menu fired the VNC user's stale hover -> tutorial
SELECT opened (never entered a tutorial; RESUME.GAM md5 held). Root cause =
SDL rejecting synthetic MotionNotify (F2). Recovery consumed ~25 probes
because my first RFB client had TWO stacked bugs (3.3-vs-3.8 handshake;
PointerEvent mask byte position) — both fixed and documented IN
scripts/r287_vncinput.py. New SOP: any menu interaction starts with
r287_vncinput.py move + screen-verified highlight, then click.

## F8. END STATE (parked)
Galaxy map t=1086, overlay toggled back OFF, cursor parked neutral, ring
untouched, zero proposals/declares. Production pid 660167 alive.

## F4. RAM RELATION SNAPSHOT at recovery (watcher tail, wall 08:28-09:12)
n=4 names [Chamachies, Orfa, Ungooma, Minions]; states row0 = [0,1,1,2]:
player PEACE Orfa, PEACE Ungooma, WAR Minions (t=1086, stable all session).
atts row0 = [_,600,318,318]. th per race banked in dipstep output (Orfa
ACCEPT_ALLIANCE 570, DW 210; Ungooma AA 600 DW 200; Minions AA 600 DW 290;
Chamachies AA 590 DW 210 START 320). 2nd-campaign lineage: t256b's OLD
campaign had player at WAR with Minions AND Ungooma — this fresh campaign
differs (peace with Ungooma), so NEGSCREEN option sets are a genuine
cross-campaign comparison, not a rerun of t252/t253.
