# t247 findings (pre-compaction handoff) — 2026-10-31 ~15:30 EDT

## Session state (TAKE THIS AS TRUTH; verify only cheap items)
- Game: dosbox pids 457617/457619, display :9, screen = PLANET LIST,
  header VERBATIM "Chamachies (102 Planets Occupied, 36 Systems Controlled)"
  at in-game turn ~1254 (user said "day 1254"; ring row t=1254 matches:
  systems_any=36 systems_full=34 score_stars=23 planets_mine=36).
- USER INTERACTED with the window ("take control back"). c-key toggle test
  showed 0 changed cells ONCE — ambiguous (overlay may have been ON already;
  state_now.png shows no overlay, so if it was on, the key DID work).
  NOT yet re-tested with a discriminating action.
- RESUME.GAM md5 5b382afb == user-oct29 backup == Oct 29 mtime: the user's
  t1254 session was NEVER saved; it lives in the ring ONLY. Do not in-game
  Save without explicit user OK. Backup file exists.
- Watcher banking normally (freshest slot 48.sav t=1254).

## NEW MEASUREMENT (scripts/r1_t246_header_law.py at t=1254)
owner-byte hist {1:35, 2:5, 4:5, 6:2, 132:1, 129:1, 130:1};
sole-owner(==1<<race)=35; player-bit-set=36 == header "36 Systems" ==
banked systems_any EXACT. SYSTEMS side of the header law now holds at a
SECOND timestamp (t1092 was 26==26).

## t246 PLANETS-side LAW NOW CONTRADICTED — reopen
At t1254: header says 102 planets, but u16@data 0x131b4 STILL reads 60.
So 0x131b4 is NOT the colonized-planet counter (t246 commit message's
attribution was wrong; selfplay.md §t246 says "maintained u16@0x131b4 = 60
== header Planets" — that equality was a coincidence at t1092).
Also: NO single byte offset in the 0x60-stride star table sums to 102 over
bit-set stars (tested all 0x60 offsets, both bit-set and all-stars).
Open questions:
  (1) WHERE does 102 live? Candidates: ui_obj+0x8c7 (the loop's *actual*
      second-count source per disasm 0x5172e), a second loop in
      0x51685..0x517c0 region feeding the FIRST %d (linear-disasm argument
      pairing is desync-limited per t91 — the loop I decoded may feed the
      SYSTEMS %d, not the planets %d), or a planet-table record elsewhere.
  (2) what IS u16@0x131b4 (static 60 at t1092 AND t1254; race-0 block)?
  (3) 102 planets / 36 systems = 2.83 avg — sanity vs the scrollable list.
Method hints: the header region 0x51685..0x51833 has TWO getters (151 at
0x51798 with push-order 0x517cd ff,0x517f2 eax(+0x13 name off), 0x517fa 2;
then 0x51806 call 0x2fb38; 0x5181d call 0x53dd8 with ebx=3) — the 0x53dd8
callee is unexplored; also scan the slot for u16==102 across data segments
(race block had only 60; widen to 0x12e00..0x16200 and 0x48000..0x49000).

## t247 SOFTLOCK #2 + RECOVERY (15:2x-15:4x EDT)
Signature recurred EXACTLY (input-dead incl. both Escapes+c, RAM frozen
22s, screen static) — this time on the USER's t1254 planet-list session,
NOT on a popup. Cause (a) engine bug now far more likely than (b) mouse
hover: user wasn't touching it during the dead window I measured.
Recovery done: all 20 ring slots copied to work/r1/bank-t1254/ BEFORE
restart; old dosbox (pids 457617/457619, 6h33m old) SIGTERM'd -> it popped
its OWN "Quit DOSBox-X warning" xmessage + in-game "Are you sure to quit"
white dialog (rows 254-345, (Yes) default = STRAY ENTER IS FATAL); SIGKILL
ended it; fresh session booting via r1_playcap_vnc.sh start.
NOTE: ring rotated — the t1092 RAM frames are GONE (all banked slots are
t1254). Cross-turn RAM diff for the planets-field hunt is IMPOSSIBLE now;
journal keeps extracted fields only.

## IMMEDIATE NEXT STEPS (sized for post-compaction session)
1. Input check: press '1' (debug flag) or c twice with screenshot between;
   then reclaim via Escape x2 to galaxy if modal screens stacked.
2. Hunt 102: python3 slot scan u16==102 (widen ranges above); then Ghidra-free
   windowed objdump of 0x53dd8 callee; update selfplay.md t246 section with
   the CORRECTION (0x131b4 is NOT planets) — commit even if hunt is negative.
3. Do NOT start long turn drives this session (compaction risk per user).

## Standing safety
- RESUME.GAM untouched all day (md5 5b382afb). Backup: RESUME.GAM.user-oct29.
- work/ gitignored; findings live in commit messages or docs/re/*.md only.
- Gate: bash scripts/gate.sh; ledger: scripts/ledger_audit.py.
- No curl/wget without explicit user yes (standing policy).
