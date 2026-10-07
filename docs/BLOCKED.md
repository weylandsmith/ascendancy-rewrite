# BLOCKED.md — v2 (decision history in archive/ralph-v1/BLOCKED.md)

## Standing decision (NOT re-openable)
Option C hybrid, B-priority, chosen by the user 2026-10-04: data-first work
plus R1 runtime capture via dosbox-x save states, no cadence limit (abolished
2026-10-05). Full rationale and the refuted A/B fork: archive/ralph-v1/BLOCKED.md.

## Current blocks
### OQ-021 — Control-victory threshold: >1/2 or >=2/3? (user decision; default in force: >1/2)
The vendor's own artifact contradicts itself: extracted end-ctrl.txt line 2
(header comment, the condition's own title) says "over half the galaxy",
while its enddesc/congrat prose says "spans over two-thirds" / "more than
two-thirds of the stars" (verified 2026-10-06g by direct read). The threshold
is code-side (numeric constant in the end-condition evaluator); the .txt has
no numeric grammar, filename refs exist only as runtime stack strings
(eventwnd.cpp region; static xref of the data string = 0 hits), and locating
the comparator statically needs obj1 call-edge recovery — long horizon, not
this loop. DEFAULT IN FORCE: rewrite keeps `mine * 2 > total`
(rewrite/src/game/campaign.cpp:738), citing the header-comment title over
display prose. UPDATE 2026-10-06s (pool-relative law, docs/re/datafiles.md):
all five end-*.txt literals have exactly one referrer each (0x2c04e/0x2c065/
0x2c07c/0x2c093/0x2c0aa), all inside the ending PRESENTER FUN_0002bfa8 (rank
= clamp(DAT_0004350c/10 - 1, 0, 9), switch on DAT_00043510 selects the file).
DAT_0004350c and DAT_00043510 have READERS ONLY — exhaustive writes search
(moffs + disp32 + SIB-base + fixup_sites.tsv + Ghidra xrefs over full code
range 0x200..0x82bb0) found ZERO writers, so the comparator is NOT in the
image: former option (b) "obj1 call-edge recovery" is REFUTED, not merely
long-horizon. What remains: (a) user ruling on comment-vs-prose, or (c) the
controlled-mutation capture — set player-owned systems to just over 1/2 in
RAM at the 0x3a095 owner table (stride 0x162, owner = +0x54 sar 16 per
FUN_00040ec0) before an end-turn, and observe whether end-ctrl fires; a
second run at 60% discriminates >1/2 from >=2/3. Item STAYS OPEN per strict-
close policy; other workstreams unaffected.

### OQ-020 — ability charge days (static route EXHAUSTED 2026-10-07; default in force: 30 turns)
Seven static probes, all negative: (1) `%d day`/`amass`/`SA_*` count ZERO in
the image and in ascend00 .cob/.bin tables — the help text reaches RAM as a
runtime-loaded string table (phys 0x252f50..; entry array at phys 0x252ba8,
u32-per-entry, ~0x330 entries), so no static string xref exists; (2) pointer
scan of the r1deep capture for u32 == phys of a `%d day` string hit only two
HEAP sites (0x252cc8/0x252d8c = the string table itself), no code/global
holder; (3) no 21-entry or 14-entry all-(0,200] static table in image data
except a triangular 1..10 ramp at 0x88f90 (economy-shaped, not charge);
(4) race .dip DIPVALUES carry no charge parameter (15 params verified,
diplomacy/bio only); (5) the stride-494 per-race table at DAT TB=0x12fb3 is
pointer/text data, NOT the dip param block; (6) the one dip-params copy found
(phys 0x255067, race00 6-u16 anchor 290,360,450,510,600,750 — byte-exact) is
a single unpaced heap buffer, race01 absent within +-64 KB, no stride law;
(7) the help blocks around all 14 `%d day` lines contain no other numeric
token (template + `pos 10 160` only). REMAINING ROUTES: obj1 call-edge
recovery of the help-formatter argument (same class as OQ-015/OQ-021) or a
controlled-mutation capture (activate an ability, read the countdown field
over end-turns). DEFAULT IN FORCE: 30 turns (abilities.md §Charge; no
rewrite upgrade). Item STAYS OPEN per strict-close policy.

## R1 runbook (mandatory safety invariants — a run without them is a bug, not research)
Route: scripts/r1_savestate.sh (+ r1_sav_scan.py per-run base; never hard-code
B). Deep capture: scripts/r1_deepcapture.sh. Invariants (enforced statically
by gate 3n):
- dosbox NEVER mounts pristine game/ — scratch copy under work/r1/ only
- headless-safe config: output=x11 under Xvfb for captures needing vblank
  autosave (host-clock autosave is checked at vblank — dummy video = no
  saves); nosound=true; stdin=/dev/null
- -time-limit always; all output bounded (head -c); DOSBOX RULE in STATE.md
- kill ONLY pkill -x dosbox-x
- CADENCE LAW (measured 2026-10-06m, 19 runs): host-clock autosave period is
  a CONSTANT 10 s (median gap 10 s in every run's save dir). Turn advance is
  NEVER automatic: 14 idle runs (zero landed clicks) hold turn constant for
  the whole run. Each NEXTTURN click that lands ON THE STRATEGIC MAP advances
  exactly +1 turn (r1ad-144225: 0->1->2; r1deep-230146: 8 scheduled clicks ->
  7 boundaries, the missing one landed while a modal screen was open — modal
  views SWALLOW clicks, see 06f/06j). Schedule by TIME and verify by TURN
  number in checkpoints, never by counting slots: at 10 s autosaves a turn
  may straddle 1-3 slot copies and slots rotate 41..60 cyclically.
- exit codes: 0 = base derived / upgrade formulas; 1 = normal negative,
  record ONE line in STATE.md, no in-turn retry; 2 = harness bug, fix it

## Closed-as-dead capture routes (do not resurrect; full trail in
## docs/REFUTED-ROUTES.md)
- external ptrace tracer: dosbox-x 2025.02.01 makes itself untraceable
  (ATTACH/SEIZE EPERM, maps EACCES by t+2 s) — dead on this box
- dosbox-x -break-start: superseded by save states AND carries the EOF-spam
  trap; do not pilot
- static absolute-base schemes: four refuted, fifth forbidden — the runtime
  pointer law (OQ-011 CLOSED) is the answer
