# t338 — STATE-16 LIVE DRIVE: WITNESS THE MODE-1 ARMING CHAIN WHILE THE GAME IS IN BATTLE STATE (working notes, streamed)

Assignment: docs/STATE.md NEXT t338 (2026-11-08). Question: with current-state
(core+0x4228) == 16, do ANY of the eight t332 chain legs {fn156d4_entry 0x156D4,
tbl15ef1, gate15fed, post1615d, relay1616f 0x1616F, post161d1, mode1_1b7dd
0x1B7DD, backch_1b180} fire? Plus new routing legs: hit-test fn 0x56890 entry,
focus-set arm 0x56aa4, SET-STATE fn 0x56e10 entry, RING-A state-switch arm
0x55ea3. Witness = CLOSES OQ-016 residue-(1) arming edge. Zero-with-control-fires
= second independent zero -> arming question moves to fn 0x156d4 internal gates
(msg 0x51 path); row stays open.

## S0 — SITTING CHECK (first action)
tail -c 400000 work/r1/playcap/live-timeline.jsonl -> newest turn 1086 == corpus.
NEGATIVE. r1_t85g_sitting.py NOT run.

## S1 — STATE-16 TRIGGER FOUND IN EXISTING RUN DATA (zero-capture, decisive)
The five state-16 saves (t299-leg-20261105-112859/save/43..47.sav) sit EXACTLY
inside the star1 ENTER census window of that run: save mtimes 43=11:32:59 ..
47=11:33:39, click (238,282) at 11:32:30 (log line 98), banked btn_hdlr stop
11:32:32, escape_to_map presses 11:33:44-46, save 48 (state 1) at 11:33:49.
MEASURED per-save state word (base 0x2bc3e4 fingerprint, groups=18 all): state
16 for 43..47, state 1 for 48..60+41..42. => ENTERING THE ICARUS SYSTEM VIEW
via the galaxy-map pip click (238,282) puts the game in state 16 for ~45 s of
wall (guest time less: bank cascades freeze it), and Escape exits it. The
t307/t308 runs reproduced the (238,282) enter (diff 94504/94712) — the trigger
is DETERMINISTIC from the md5-pinned RESUME.GAM (t1086 corpus). t332's
rowjump-enters-orbital law stands: the rowjump is a DIFFERENT view (state 17);
the pip-enter is the battle/system state 16.
Screen check: 14_star1_screen.png = system view (Icarus/Red Dwarf sidebar,
planet list, view buttons) — the 16BATTLE.SHP family; orange-frac 0.005 (safe
under the 0.20 title gate). windows.txt state-16 family = 20 windows;
clickable children (text space, t332 law 5): Pass (500,70) sm=807, Auto (604,70)
sm=808, Repeat (552,70) sm=809, W (494,118) sm=810, S (533,118) sm=811,
Z (572,118) sm=813, I (611,118) sm=812, My^Items (513,118) sm=804, Other^Items
(591,118) sm=805, BatListWnd interior (553,200), TOGGRID (572,418) sm=74,
BATROTLEFT (486,418) sm=50, BATROTRIGHT (501,418) sm=51, BATZOOMIN (533,410)
sm=54, TOGELEV (611,418) sm=76, RECENTER (611,457) sm=71. (ABANDON skipped —
destructive-class, not needed by the chain.)
Leg bytes verified verbatim in work/r331_disasm.txt: 0x55ea3 `e8 68 0f 00 00`
call 0x56e10 (RING-A resolver arm), 0x56890 `53 51 52` (hit-test entry),
0x56aa4 `83 7c 24 04 ff` (focus-set arm), 0x56e10 `51 56 57` (SET-STATE entry).
Last-4 FirePat tokens: no collision vs the eight t332 legs (preflight re-audits).

## S1b — session design decisions
Reuse scripts/r332_batctrl_session.BatSess (operand capture + BatControlWnd/
BatModeWnd magic-record b7/b9 oracle + set_legs + click_phase). NEW legs
setstate_56e10, ringa_55ea3, hit_test_56890, focus_56aa4. Sub-batteries per the
t330 entry-consumption law: S={setstate,ringa} armed across the enter click
(witness edx=0x10); A=downstream chain+btn_hdlr (no entry); B=entry+btn_hdlr
alone; H=hit_test+focus alone (hit-test fires on EVERY mouse event = hot).
State oracle = r337_state_word.find_base fingerprint per newest .sav.

## S3 — RUN 1 (work/r1/dbg-t338-20261107-224027, in flight; findings banked live)
TRIGGER REPRODUCED EXACTLY: click (238,282) diff=94504 (t307 verbatim),
STATE-ORACLE S_state16 sav=56.sav state=16 groups=18 (pre_battery state=1).
WITNESS 1 (state-switch edge, t337's SET-STATE law): `STOP post-rearm
leg=setstate_56e10 eip=0x216260 file=0x56e10 eax=0x2bc35c ecx=0x10 edx=0x10
ebp=0x2bc35c` — fn 0x56e10 entered with edx=0x10 (new state 16) on the core
object, seconds after the enter click. The state-16 ENTRY path is LIVE.
WITNESS 2 (state-16 hit routing): click (591,118) in state 16 -> btn_hdlr stop
`win[esi] name='My^Items' eax=0xfe6054 edx=0x8` — the pixel owner in state 16
IS the state-16 family window My^Items (t332 measured the SAME pixel as
NEXTTURNCONT in state 1). t337's routing law corroborated live.
Chain legs A battery: in progress.

## S2 — session design (scratch, own ring, private Xvfb, core=normal, one capture)

## S3 — run + census

## S4 — verdict

## S3 (complete) — RUN 1 census + banked detail
PTY WHOLE-LOG CENSUS: {setstate_56e10:1, ringa_55ea3:1, btn_hdlr:17,
tbl15ef1:0, gate15fed:0, post1615d:0, relay1616f:0, post161d1:0, mode1_1b7dd:0,
backch_1b180:0, fn156d4_entry:0, hit_test_56890:2, focus_56aa4:0}.
STATE-ORACLE timeline: pre_battery 1 -> S_state16 16 -> 13 consecutive reads 16
(A battery + B_pre) -> final_map 16 (escape ladder ran AFTER the last oracle;
honest note: the exit to state 1 was NOT re-measured this run — it stands from
S1's save-mtime analysis of run 112859).
BANKED STOPS 20: setstate_56e10 (eax=ebp=0x2bc35c edx=0x10), hit_test_56890 x2
(eax=0x2bc35c, edx=0x76/0xc8 = click Y), btn_hdlr x17 — per-click window names
+ msg ids (press edx=7 / release edx=8 pattern):
  A_myitems My^Items 7; A_otheritems My^Items 8; A_w_btn Other^Items 8;
  A_i_btn Auto 4; A_batlist Other^Items 8; A_toggrid TOGGRID 7; A_rotleft
  TOGGRID 8; A_zoomin BATZOOMIN(rec 0xfe5b80) 8; B_myitems BATZOOMIN 8;
  B_s_btn Auto 4; B_i_btn My^Items 8; B_batlist Other^Items 8; T_pass Pass 7;
  T_auto Pass 8; T_repeat Auto 8. ret0 sites 0x21612d/0x2160c7/0x1f0bcd = the
  hit-test fn's own dispatch call sites INSIDE fn 0x56890 (file offsets
  0x56890+span) — the routing machinery executing, corroborating witness 2.
batrec oracle: BatModeWnd b7==1 ZERO across all before/after reads; BatControlWnd
magic-rec +0xb7 0 pre-battery, 253 constant during state 16 (t337 note verbatim).
Teardown: SIGKILL dosbox 200239 / xvfb 200235 (recorded); production :9
(136357/136359, Xvfb 1461) ps-verified untouched post-run.

## S4 — VERDICT (OUTCOME C, the honest negative the assignment named)
With the game MEASURED in state 16 and state-16 hit-routing PROVEN executing
(hit_test x2, btn_hdlr x17 on the family rows), all eight chain legs are ZERO.
t337's candidate explanation for t332's zero (capture sat in the wrong state)
is REFUTED as the cause. The arming question moves to fn 0x156d4's intake:
BatControlWnd is a TYPE-19 PARENT with rect 0,0-0,0 — it can never itself be
the mouse hit target; every family-row click lands on a CHILD button record.
Entry at fn 0x156d4 therefore needs SOMETHING to post 0x1c01 (or any msg) to
registry slot 61 — the named open edge is: do child-button SENDMESSAGE values
(804/805/807-813 family) propagate to the parent record, or are they handled
only by the pump/consumers? That is a zero-capture decode (t339): walk the
windows.txt SENDMESSAGE consumer (t302 law: btn msg 0xc -> 0x30edc rect
hit-test -> ring post fn 0x56ad4 / registry dispatch fn 0x56ca4 edx=[win+0x63])
for the state-16 family specifically, and census what [win+0x63] is for the
child records in the state-16 saves. LEDGER: nothing closed strict-close
(16/3); residue-(1) REWRITTEN (SEVEN named unreachable legs; mouse road dead
twice over). Files: docs/re/_wip_t338.md, ships.md S57, OPEN-QUESTIONS row,
scripts/r338_state16_session.py (rc=0).
