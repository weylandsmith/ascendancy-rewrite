# t306 WIP — SELECTION-WRITER WITNESS: arm the t296 static gate sites on a live sprite select

## S0. PRE-FLIGHT (this session)
- No new sitting: live-timeline.jsonl continuous, production game still t=1086
  sel=0 since the 08:51:35 watcher restart (9230 sav-lines, zero turn/sel
  change) — r1_t85g_sitting.py NOT run (assignment stands, no re-check loop).
- FirePat regression EXACT before any census (dosbox-debugger.md t305 law):
  033648 cos_hdlr 41 / 052925 s2_56cda 3 / 061825 cos_hdlr 60, s2_56cda 20,
  s2_56c74 1 — PASS (fresh run of fire_pats against the three mcp-pty.log).
- Leg bytes payload-verified (work/ascend_payload.bin):
  0x1aef8 = 56 57 55 83 ec 14 (push esi/edi/ebp; sub esp,0x14) = handler entry;
  0x1b71f = c6 85 b7 00 00 00 02 = mov BYTE [ebp+0xb7],2 (msg-0x53 EFFECT,
    verbatim vs t91_code_disasm.txt:7922 — gates at 1b6f6 kind==2 / 1b709 owner
    / 1b716 moves>0 all precede it);
  0x1ba39 = c6 86 b7 00 00 00 02 = mov BYTE [esi+0xb7],2 (mouse msg-4 EFFECT,
    disasm:8143; esi=BatModeWnd record, ebp=0xffffffff at that leg);
  0x1b070 = cmp BYTE [ebp+0xb7],4 (disasm:7392) = batmode msg-4 router.
- FirePat last-4 uniqueness re-audited over the full 37-leg LEGS table: NONE
  duplicate (batmode_dead/bat_s53/bat_mouse/bat_router included).

## S1. INSTRUMENT CHANGES (this iteration, committed with the landing)
- scripts/r299_leg_session.py: LEGS += bat_s53 0x1B71F, bat_mouse 0x1BA39,
  bat_router 0x1B070 (batmode_dead 0x1AEF8 comment corrected — t299 zero-fires
  were DYN-core artifact territory per t304/t305 re-attribution).
- --target-kinds filter (default sprite,planet,empty = back-compat; t306 runs
  sprite only). control_nextturn always runs = positive control.
- SELECTION ORACLE inside the census block: before/after every click reads the
  newest scratch .sav -> B -> DAT_43504, DAT_43508 (u32 @B+OFF+X) and byte
  0x43510 (the watch.log sel= field); pairs land in census.json["oracles"].
  Delta-pair law per t297-A: these scalars churn WITHOUT input, so only
  before-vs-after around a specific click is evidence.
- scripts/r306_relaunch.sh (copy of r305 loop): --census --legs
  batmode_dead,bat_router,bat_s53,bat_mouse,btn_hdlr --target-kinds sprite
  --window 60 --disp 97 --port 55999 --tl 7200. cos_hdlr/56cda deliberately
  NOT armed: the 0x3b pump storm (15-60 fires/run) floods bank_stop (storm cap
  6/window) and would crowd out the cold bat legs; the pty whole-log census
  only counts ARMED legs anyway. btn_hdlr stays armed = the t302/t305-proven
  positive control for msg dispatch liveness (NEXTTURN msg 0x7/0x8).
- Reading law at a bat stop (ships.md S24): ebp (0x53 leg) or esi (mouse leg)
  = BatModeWnd window record -> bank_stop's magic loop (esi,eax,ebp order)
  names it; eax at 0x1b71f = ship record physical (clip+1 deref); the clip
  blob at edx is NOT meaningful at these legs (edx holds gate temporaries) —
  interpret via wrec_* + win grid +0xb7 (mode) instead.

## S2. RUN t299-leg-20261105-101054 (attempt 1, rc=0, SESSION END
### census-measured=['sprite','control_nextturn'])
Instrument healthy: census-ctl MEMDUMPBIN MATCH x3, census-arm ok att=0 x3,
resume-liveness alive x2, teardown SIGKILL own pid 62387, no stray
dosbox-x-dbg/Xvfb :97, production :9 untouched (watch.log still t=1086).
FirePat regression re-passed same session before arming (5/5 exact).

WHOLE-LOG PTY CENSUS (37-leg table, only the 5 armed legs counted):
  {batmode_dead(entry 0x1aef8): 0, bat_router(0x1b070): 0,
   bat_s53(effect 0x1b71f): 0, bat_mouse(effect 0x1ba39): 0, btn_hdlr: 2}

BANKED STOPS (hits.json, regs verbatim):
1. sprite_48x151#0 leg=btn_hdlr eip=0x1f2b04 (=P0+0x336b4) eax=0xfe72d4
   edx=0x8 ret0=0x1fbfdd -> file 0x3cb8d; win[esi] magic 0x12345678
   NAME='PLIND'. ret0 decodes: file 0x3cb88 = e8 27 6b ff ff call 0x336b4
   (DIRECT call, one of the 51 btn_hdlr E8 sites; enclosing fn prologue
   0x3cb00 push esi/edi/ebp, has a `call [ecx+0xc]` sibling leg at 0x3cb6e —
   a window-family dispatcher, NOT the batmode family). u32 refs to 0x3cb00
   in payload: ZERO (class-table member reached via table base arithmetic).
2. control_nextturn#0 leg=btn_hdlr edx=0x4 win[eax] NAME='Cancel'
   ret0 file 0x56c77 (pump 0x56c74 +3) — the t304 modal-'Cancel' pattern on
   the control: a 'Cancel' record was live in the window stack THIS run. The
   NEXTTURN turn-advance is NOT witnessed this run (t305 witnessed msg 0x8
   PLSQUARE for the same control; this run's single banked stop was the
   Cancel record). CONTROL VALIDITY: btn_hdlr firing proves msg dispatch was
   ALIVE during the sprite window too, so the four ZERO bat counts are
   attributable, not arming failure.

SELECTION ORACLE (census.json["oracles"], delta-pair law):
  sprite_before 53.sav t=1086 sel43510=0 DAT_43504=0x256825 DAT_43508=0x26fe77
  sprite_after  41.sav t=1086 sel43510=0 DAT_43504=0x256825 DAT_43508=0x26f00d
  DAT_43504 UNCHANGED (0x256825 = Icarus star ptr, the system-identity
  reading); DAT_43508 changed but that scalar churns WITHOUT input (t297-A)
  and no bat leg fired — NOT attributable to the click. sel43510 stayed 0.
  Post-run save census (20 saves): all t=1086 sel=0. NO selection store moved.

## S3. READS (t306)
1. THE TASK'S DISJUNCTION RESOLVES TO BRANCH (b): a working sprite click at
   the validated class-coordinate (48,151) dispatches msg 0x8 to the PLIND
   window record (btn_hdlr witnessed) and executes NONE of the t296 batmode
   selection sites — not the handler entry (0x1aef8), not the msg-4 router
   (0x1b070), not either EFFECT writer (0x1b71f/0x1ba39). This is a CITED
   NEGATIVE for the batmode static-gate route under the corrected core +
   corrected fire detector + live positive control; it re-scopes the
   selection-WRITER hunt to the DAT_43504/43508 writer set (0x52003 /
   0x51a8e / 0x51fc2 family — disasm-verified stores this session; 0x51a8e
   gated by ds:0x484ec > 0x96 turn-check, 0x51fc2 stores [edx+0x59], 0x52003
   stores [esi+0x59] code 0x10) exactly as the STATE assignment pre-specified.
2. STANDING GATING FACT CONFIRMS WHY ZERO-EFFECT IS EXPECTED-CONSISTENT:
   t=1086 owner-0 has NO kind-4 (in-system) ship (OPEN-QUESTIONS OQ-019
   gating-fact note: 11 ships kinds {3,5}) — G1/G2 cannot pass, so even a
   msg-0x53 dispatch could not reach 0x1b71f. The entry+router zeros are the
   STRONG part of the negative (they sit BEFORE any gate): a map click's msg
   0x8 does not walk the BatModeWnd handler at all.
3. INSTRUMENT: the bat legs are cold (zero fires is the cheap answer);
   bank_stop crowding was avoided by NOT arming the 0x3b pump (cos_hdlr /
   56cda) — one attempt, one sitting, rc=0. The oracle-pair pattern is now
   built into --census mode for future writer hunts (t307 arms the 0x52003 /
   0x51a8e / 0x51fc2 family the same way).
4. NO LEDGER ROW CLOSED (strict-close): the selection WRITER is still
   unnamed — branch (b) closes the ROUTE QUESTION as a negative note on
   OQ-019 (t306 note appended), the row itself stays open pending a witness
   at the surviving writer set.
