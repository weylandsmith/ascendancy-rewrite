# t405 WIP — sub-screen navigation + rail liveness

## F1 (measured, extracted/ascend00/windows.txt, parsed 136 records this session)
The STATE id-list law (t388, 123/123) says the rail buttons are MAP-ONLY:

| NAME | TYPE | PARENT | STATE | RECT | MSG/p1 |
|---|---|---|---|---|---|
| STATUS (Planets) | 0 | NONE | `1 1` | 474,130-632,160 | 1 / 10 |
| FLEET (Ships) | 0 | NONE | `1 1` | 474,169-632,199 | 1 / 18 |
| RESEARCH | 0 | NONE | `1 1` | 474,208-632,238 | 1 / 20 |
| SPECIALAB | 0 | NONE | `1 1` | 474,247-632,277 | 5 / 0 |
| RACES (Species) | 5 | NONE | `1 1` | 474,286-632,316 | 1 / 7 |
| Intelligence | 0 | NONE | `1 7` | 474,303-632,333 | 1 / 14 |
| COSMOSWnd | 2 | NONE | `4 1 3 7 13` | 7,7-465,472 | 0 |
| STATUSWND | 16 | NONE | `1 10` | 7,7-632,472 | 0 |
| STATPLANLST | 10 | STATUSWND | `1 10` | 7,46-632,472 | 0 |
| FLEETWND | 17 | NONE | `1 18` | 7,7-632,472 | 0 |
| STATSHIPLST | 10 | FLEETWND | `1 18` | 7,46-632,472 | 0 |
| RESWIN | 9 | NONE | `1 20` | 7,46-476,472 | 1 / 0 |
| RESROTLEFT/RIGHT, RESMOVEUP/DOWN | 0 | RESWIN | `1 20` | 524..593,442..472 | 50-53 |

Consequences [verified from the table]:
- The five plain rail buttons carry STATE `1 1` → active in state 1 (map) ONLY.
  No sub-screen state (10/14/18/20) appears in any rail-button list.
- STATUSWND/STATPLANLST rects (7,46-632,472) span the FULL width INCLUDING the
  rail column x>=474, while COSMOSWnd stops at x=465.
- The research screen's own children (RESROTLEFT/RIGHT/MOVEUP/MOVEDOWN) sit at
  x 524..593 y 442..472 — i.e. INSIDE the rail column, in state 20. So the
  vendor DOES put interactive controls in the rail column while a sub-screen
  is open; they are just not the rail buttons.

## F2 — the reported defect is a hit-map fall-through, not a STATE question
Owner D13: from the Planets screen, Ships/Research/Species clicks "route into
the status screen's scroll/select". Whatever the rail-liveness law, the port's
bug is that a click at (474..632, 130..316) while screen==kScreenStatus is
swallowed by the status list branches (ui.cpp:285-305 use full-width rects).

## F3 — RESOLVED: the queue's premise "rail stays live, screens SWAP" is REFUTED
Three independent lines of evidence, all measured THIS session:
1. windows.txt (F1): the five plain rail buttons carry STATE "1 1" — no
   sub-screen id (10/14/18/20) appears in ANY rail-button STATE list. There
   is NO list that keeps the rail live during sub-screens.
2. VENDOR BACKDROP DECODED + NATIVE-VISION-GRADED: 10status.shp k0 (639x479)
   dumped via tools/shp_pngdump (rewrite's own decoder) ->
   /tmp/t405/out/raw/10status--0.idx, PNG via game.pal. The backdrop is FULL
   WIDTH (covers x 474..638) and shows NO button faces at the rail y-ranges
   (130-160 Planets ... 303-333 Intelligence). Instead the rail column in
   state 10 carries a RACE-STANDINGS panel ("TOTEM 20", "MOBY 7" boxes at
   y~286-355, x 474..619) — the rail's real estate is OCCUPIED by screen art.
3. Art geometry (numpy on the index plane): list table verticals end at
   x=619/621; row lines y 48/83/117/151/185/219/253/287 (pitch ~34, 7 rows);
   scrollbar-face strip x~622..638 (idx 0/103 faces) with up-arrow box at
   top (y~48-70) and down-arrow box at bottom (y~433-457) — matching the
   shipped kStatusArrowUp{566,46,632,70}/Down{566,433,632,457} hit rects'
   right edge.
=> VENDOR LAW CONFIRMED AS ALREADY CITED IN statuslaw.h: rail is map-only;
   sub-screens SWAP the full screen incl. the rail column; Esc is the cited
   way back (t252 live witness). The port's RAIL BEHAVIOUR IS VENDOR-CORRECT.

## F4 — the owner's witnessed DEFECT, restated honestly
Owner clicked Ships/Research at the rail's LAST-KNOWN position while the
status screen was open; the click fell into the status list's full-width hit
region and scrolled/selected. In the vendor the same click also lands on the
list (table spans x<=619) — BUT the vendor user can see the rail is gone
(backdrop covers it) and the owner themselves quoted the vendor's
discoverability hint "Esc: return to galaxy ... printed bottom-left".
So the fixable deltas are (a) hint text discoverability, (b) keep clicks
outside the vendor table (x>=620 strip) out of the row-hit fall-through.
VERIFY: is the Esc hint baked into 10status k0 bottom-left (then our blit
already shows it) or printed by the engine?

## F5 — MOUSEFOCUS census + meaning (pending, see below)
STATUSWND + STATPLANLST both MOUSEFOCUS 0 — check whether MF=0 means the
widget still takes mouse internally (TYPE-10 lists draw their own arrows).

## F6 — "Esc: return to galaxy" bottom-left: NOT vendor data [verified negative]
CP437 byte-scan of ALL extracted files: zero occurrences of "Esc" except one
race06.raw binary coincidence; tutintro.txt only says "press ESC" in tutorial
prose. ascend.exe strings (ASCII + -e l UTF-16): no "Esc:"/"return to" hint.
The t3 LIVE CAPTURE of the original status screen (native-vision read of
work/screens/t3/planets_header_t1086_after_open.png bottom strip): NO text
bottom-left — just the bevel frame. NOTE: the phrase IS in OUR port already
(ui.cpp ~713, species screen only). The owner's quote likely recalls OUR hint.
=> Do NOT invent vendor hint text; a PORT AFFORDANCE hint is permissible but
   must be labelled as such.

## F7 — t3 capture native grade (original status screen, 640x480 space)
Right side: NO rail buttons; scrollbar arrow boxes at the FAR-RIGHT strip
(~x619..638: up box y~48..94 top, down box y~425..476 bottom — matches the
art measurements in F3/next). Left edge of each row: small race-flag icon.
Rows: system circle art + system name (cyan) + small planet icon + planet
name line "(Large Cathedral Planet)" + status line + 3 surface thumbnails +
red gauge-dot block. Header centred green. So the vendor list DOES extend
under the whole rail column; the only interactive chrome in that column is
the arrow strip x>=619.

## F8 — arrow art rects MEASURED (numpy on 10status k0 index plane)
Top arrow box: border x619..638, y48..94 (face idx0/103 inside; box top
lines y48-51 span 612..638 = shares header line).
Bottom arrow box: x620..638, y425..478 (border bottom line y478).
=> shipped kStatusArrowUp{566,46,632,70}/Down{566,433,632,457} are 50px too
   WIDE on the left (566 vs 619) — clicks at x566..618 in those bands scroll
   in our port but hit the list in the vendor. THIS is the machine-visible
   half of the D13 fall-through complaint.

## F9 — IMPLEMENTED + PINS + MUTATION + WITNESS (this session)
Code (rewrite, gate 0, suite 352->356/0):
- statuslist.h: kStatusArrowUp{619,48,638,94} kStatusArrowDown{620,425,638,476}
  (MEASURED on the backdrop plane, F8; old PORT rects 566-wide REMOVED),
  kStatusScrollCol{619,48,638,476}, unified statusHitFor(Pt,topY) with
  precedence arrows -> scroll-column(inert) -> rows(table x 7..618).
- statuslist.cpp: statusHitFor implemented.
- ui.cpp: the three-branch status click chain REPLACED by one statusHitFor
  dispatch; rejected points are silent/inert (no sound, no scroll, no
  select); row-frame paint right edge 632->618 so the vendor scrollbar
  column shows through (native-vision confirmed on the after-shot).
PINS tests/test_statusnav_t405.cpp x4 (no vendor data read -> no
REQUIRE_DATA needed, t403 census clean).
MUTATION (scripts/t405_mutate.py, revert by file-copy from /tmp/t405-snap):
M1 arrows->old 566 rects CAUGHT (statusnav_arrows_measured_t405);
M4 precedence flipped CAUGHT (same test); M5 rail active everywhere CAUGHT
(statuslaw_rail_activity_state_lists); M6 unknown-target clamps CAUGHT
(statusnav_swap_and_escape_chain_t405); M7 Esc dead on intel CAUGHT
(statuslaw_escape). M2 (drop column guard ALONE) and M3 (drop row x-boundary
ALONE) are VACUOUS — verified manually: suite passes with either alone; the
two guards are mutually redundant (skill rule 6). M2c = OLD CODE SHAPE (no
guard AND no boundary, the actual D13 regression) CAUGHT with named FAILs at
test lines 42/44/56/60. Honest score: 5 named + M2c CAUGHT; 2 vacuous
single-guard mutants documented, not hidden.
WITNESS scripts/t405_statusnav_witness.sh (Xvfb :97, SDL_AUDIODRIVER=dummy
+ --audio-trace, seed 5): VERDICT PASS — rail opens status; (580,60) = ROW
select (old code scrolled there); (628,70) scroll up; (628,450) scroll down;
(628,250) trough INERT (exactly 4 status lines); rail-position click inside
the screen switches NOTHING; Esc -> map; zero laser01.
VENDOR-ART ARROW RECTS are now cited law, closing the t402 "exact arrow
rects UNCITED" seam.

## F10 — LEDGER (strict-close honest negative)
Closes NO OQ row: the rail-liveness question was a queue premise, not an OQ;
the fix measures the vendor's list geometry (cited above) but no open row
owns it. OQ-016/019/027 untouched. The t405 queue row's premise "rail stays
live" is DISPOSITIONED as refuted (F3); the owner's witnessed fall-through
is fixed by the hit-map (F9). Residual seams, named: (1) trough/thumb drag
inert (no vendor drag law captured); (2) row 0's frame still clips the art's
"nam" header cell (pre-existing t402, t406 row-assembly territory); (3) the
vendor's per-open header freeze (t402 seam unchanged).
