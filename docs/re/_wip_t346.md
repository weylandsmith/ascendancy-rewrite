# _wip_t346 — UNMAPPED-WRITER HUNT with tool v2 (STATE.md NEXT ACTION, verbatim row)

## S0 — PREFLIGHT (2026-11-09)
- SITTING CHECK NEGATIVE: newest turn in work/r1/playcap/live-timeline.jsonl
  tail-seek = 1086 (file mtime Nov 9 01:53 predates t345 landing 02:30; only
  58.sav rows at t1086 in the last 200 KB). No r1_t85g_sitting.py run needed.
- CANDIDATE (a) VERIFIED-REFUTED, do not re-verify: docs/re/retractions.md #9
  + docs/re/selfplay.md "t248 ... t247's +0x5a LEAD REFUTED" — star-record
  byte +0x5a = TOTAL planet SLOTS in the system (sum==145==named record
  count; per-system len(planets)==+0x5a), NOT the colonized-planet count.
  (A DIFFERENT +0x5a — the PLANET-record local-race DWORD — is live law from
  t341/t342; not a candidate, its writer is named fn 0x38840 0x38af5..0x38b26.)
- CANDIDATE (b) LIST (grep docs/re/*.md + OPEN-QUESTIONS.md for
  writer/consumer unmapped/unwitnessed/unnamed, live docs only):
  1. selfplay.md:985 (t288) — INPUT-PUMP WRITER of WORD ds:0x484c4 (msg) /
     ds:0x484c6 (char) "writer EIP still unwitnessed". Pointer-law-convertible
     (data seg; static immediate 0x242000+0x484c6=0x28a4c6, live B-0x88+
     0x82bb0+0x484c6). Trigger = ANY key/click: maximally reachable.
     REFUTED SCOPE CHECK: REFUTED-ROUTES t288 bars dbg-restoring SAVESTATE
     ZIPs (glibc abort mid-restore) — it does NOT bar the dbg build loading a
     CAMPAIGN via 'Return to Current Game', the proven r1_wp_session.py route
     (t283/t286/t286b rc=0 positive controls; t286 law 1 BPLM survives load).
     VALUE: names the softlock-class mechanism (the layer that STOPS writing
     in t288's SOFT probe) with a code site.
  2. selfplay.md:426 (t205 family) — per-star victim mark "mark law has an
     unmapped clear OR fire path not 0x43a4c". Trigger = attacking in play:
     NOT scriptably reachable at t1086 (t293: orbital-grid dot-clicks
     navigate, never select; t312 sprite-pixel select DEAD). REJECT.
  3. income-law.md:2050 — planet-record +0x0a "still UNMAPPED ... pointer-like
     seed field repaired at load". Load-time writer; candidate if (1) lands
     early, NOT this iteration (one task per loop rule).
  4. ships.md:881 — lane-step constant/1-3 divisor word UNMAPPED: static
     order-executor hunt, not a DAT writer; ships.md S22 already found the
     march body FUN_0004a74c. REJECT for this row's shape.
  5. abilities.md:40 / ships.md:1223 — SA_KnowHomeWorlds vendor flag consumer
     unmapped: OQ-026 CLOSED territory, documented-model disposition; no
     pointer-convertible datum named. REJECT.
- CHOSEN: candidate 1, the input-pump writer (ds:0x484c4/c6).
- METHOD: static-first (zero capture) SIB-aware store census over
  work/r331_disasm.txt for immediates 0x28a4c4/0x28a4c6 (rebased data-seg
  form; t307 law: code RAM immediates are REBASED, raw 0x484c6 scan is the
  R12 dead method); then ONE live confirmation launch if a store site names
  itself (budget 3 launches, 1 spent so far: zero).
- INSTRUMENT NOTE: assignment names scripts/r1_dbg_session.py (EIP legs);
  for a DATA write-watch the accepted instrument is scripts/r1_wp_session.py
  --target data:0x484c6 (t286 GENERAL write-watchpoint session, positive
  control rc=0; t286 LAW 7: fire EIP may be a READER — writer = last storing
  insn before reported EIP touching the watched offset).

## S1 — STATIC WRITER CENSUS COMPLETE (zero capture, work/r331_disasm.txt
literal-immediate scan for 484c4/484c6; R12 bars reference scans, literal
stores ARE scannable — the relocation adds +0x242000 at load, t307 law):
  WRITERS ds:0x484c6 (char WORD):
    0x2a70e  fn 0x2a5f0  `mov WORD PTR ds:0x484c6,dx` — INT 16h AH=0
           get-char drain (dx = eax with dh zeroed = CHAR CODE).
    0x2a911  fn 0x2a838  `mov ds:0x484c6,ax` — type-3 arm, ax =
           WORD [record+0x10] (DOSBox event record char).
  WRITERS ds:0x484c4 (msg WORD):
    0x2a72a  fn 0x2a5f0  `mov ds:0x484c4,ax` — ax = (int16 result)>>8 =
           SCAN CODE (sar 0x8 @0x2a721; scan 1 = ESC — t288's stuck
           (msg=1,char=0x1b) is EXACTLY this path's ESC shape).
    0x2a91d  fn 0x2a838  `mov WORD PTR ds:0x484c4,dx` — dx = WORD
           [record+0xc] (matches aicode.md §8.4 "record+0xc/+0x10" lead).
    0x54928  fn 0x54650  `mov WORD PTR ds:0x484c4,cx` with cx=0 — pump
           CLEAR after consumption (inside the [esi+0x48aa]==-1 mouse
           branch, adjacent stores ds:0xa2000/04/08; t344's fn 0x54650).
  ORDERING LAW (static, decisive for the needle SOP): in fn 0x2a838 the
  CHAR store (0x2a911) PRECEDES the MSG store (0x2a91d) — msg is published
  LAST, so a consumer that observes msg!=0 always sees the paired char;
  a stuck msg with stale char therefore means the WRITER half-published
  (interrupted between 0x2a911 and 0x2a91d) or the OTHER path wrote.
  fn 0x2a5f0 same shape: char 0x2a70e before msg 0x2a72a.
  fn 0x2a838 = THE DOSBox EVENT-RECORD DEMUX (t288's named "pump"):
  type=[eax+0x8]; <2 -> 0x2aa14 (je 0x2a875 arm: mouse X/Y -> ds:0x484ec/
  0x484f0 — t310's measured mouse-X global); ==2 -> 0x2a8a2 (button word
  ds:0x484ac/0x484d0, t320 law); ==3 -> 0x2a8fe keyboard arm (above).
  Callers: 0x2a838 <- 0x59b3b (fn 0x575e4 span); fn 0x2a5f0 <- fn 0x2a7fc
  (sole caller 0x2a81a; 0x2a7fc <- {0x217a9, 0x555ef INSIDE fn 0x54650,
  0x59a0c}); fn 0x2a7fc clears ds:0x484dc/e0/e8/a0 then calls 0x2a5f0,
  then ds:0x484cc!=0 -> fn 0x2a744 (mouse delta).
  fn 0x2a5f0 also sets ds:0x484a0 = -1 sentinel at 0x2a724 (paired with
  fn 0x2a7fc's clear-to-0 and t320's 484a0=-1@0x2a92d observation).
  CONSUMERS (fn 0x54650 pump): reads 0x54845/0x5485e/0x5486c/0x54872/
  0x548a1/0x54943/0x54968/0x5496f; msg==1 or msg==0x13/0x19 gates;
  dispatch 0x54976 call 0x56b5c (pump_entry leg) with ecx=msg bx=char.
- GAP REMAINING after S1: the t288 honest negative is a WITNESS gap ("which
  EIP actually writes in a live session" — two candidate paths now named
  statically). LIVE LEGS to arm: w484c4_2a91d (record-demux arm) +
  w484c4_2a72a (INT16h arm) + btn_hdlr control; inject 'c'; attribution =
  which leg fires (both firing = both paths live, attribution by stop order
  + EAX/EDX values). Campaign entry route = Return-to-Current-Game on the
  md5-verified Oct-29 RESUME.GAM (r1_wp_session proven; NOT savestate ZIP —
  REFUTED t288 scope is the ZIP restore only).

## S2 — LIVE LAUNCH CONFIG (launch 1 of budget 3)
- Tool delta landed (both lint-clean, preflight rc=0):
  scripts/r299_leg_session.py LEGS += {w484c4_2a91d 0x2A91D, w484c4_2a72a
  0x2A72A, c484c4_54928 0x54928} with payload-verified store bytes;
  scripts/r1_dbg_session.py LEGSPEC += metadata, NEW phase "keys" (t311
  digit-phase shape verbatim: close_eventwin -> assert_on_map -> arm_census
  -> RUN -> popup re-guard -> xsend keys -> census_window -> disarm_run),
  --keys CLI (default "c,1"; NO Escape — t285 self-harm law).
- Command: r1_dbg_session.py --tag t346 --legs w484c4_2a91d,w484c4_2a72a,
  c484c4_54928,btn_hdlr --phases baseline,keys --window 60 --attempts 2
  --expect 'w484c4_2a91d>=1'  (log work/t346_session.out; run dir
  work/r1/dbg-t346-<ts>/; interpreter ~/.hermes/hermes-agent/venv/bin/python
  — the ONLY python with PIL, banked so the next session doesn't re-derive).
- Decision tree on the whole-log census:
  (i)  w484c4_2a91d>=1 -> WRITER WITNESSED, fn 0x2a838 = the pump writer EIP
       family; bank regs (bank_stop dx/rec contents) -> closes the t288
       honest negative with cited live witness; law goes to selfplay.md.
  (ii) w484c4_2a72a>=1 only -> the INT16h drain path is the live writer
       (DOS key-buffer model); fn 0x2a838 arm is dead-code-for-keys.
  (iii) both zero but btn_hdlr alive -> third writer path exists OR keys
       never reached the guest (xsend key law t287); honest negative banked,
       row stays open, budget-2 relaunch NOT worth it without a new lead.
  (iv) c484c4_54928>=1 anywhere -> CONSUMPTION witnessed (pump clear) —
       independent of (i)-(iii), strengthens the pump model.
- LEDGER MAPPING: the t288 negative lives in selfplay.md (softlock drive
  class), NOT an OQ row; no OQ closes from this task under strict-close.
  OQ-016/019/005 rows: untouched this iteration (status lines unchanged).

## S3 — RESULT (launch 1 rc=0 attempt 1; DECISIVE)
- PTY whole-log census {w484c4_2a91d:0, w484c4_2a72a:2, c484c4_54928:0,
  btn_hdlr:2}; baseline 15 s leg window 0 stops. Banked stop keys#0: EIP
  file 0x2a72a EAX=0x2e (scan 'c') EDX=0x63 (char 'c') -> DECISION TREE
  BRANCH (ii) WITH REGISTER PROOF: the INT16h drain fn 0x2a5f0 IS the live
  writer of the (msg,char) pair; the fn 0x2a838 type-3 arm is DEAD for
  injected keys (REFUTED-ROUTES t346(1)). post-rearm btn_hdlr pair carries
  ebx=0x63 ecx=0x2e win NEXTTURN (ret0 0x56c77 + 0x3177d) — t311 focus law
  reproduced for free.
- c484c4_54928 zero = the clear-leg gate (msg==0x19 + [esi+0x48aa]==-1)
  never matched 'c'/'1' — consistent, not a contradiction; consumption road
  for msg==1 is fn 0x54d18 hotkey dispatcher (static, 0x5494a/0x54951).
- ctl_census MATCH=False explained: rebased-immediate instruction (see
  REFUTED-ROUTES t346(2)); arms demonstrably fired (census + banked stop).
- Launches spent 2/3 (attempt-2 dosbox killed at campaign entry by the
  driver — attempt 1's verdict was already decisive; pkill -f self-matched
  the driver shell once, harmless caveat). No relaunch warranted.
- BANKED (final homes): docs/re/selfplay.md t346 block (law + regs +
  instrument laws; t288 honest-negative (1) marked SUPERSEDED in place);
  docs/REFUTED-ROUTES.md t346(1)(2); tool delta scripts/r299_leg_session.py
  LEGS +3, scripts/r1_dbg_session.py LEGSPEC + "keys" phase + --keys.
- REMAINING HONEST NEGATIVE (row stays open class): the softlock HALT CAUSE
  is still unnamed — writer EIP gap closed, "why does the pump stop
  draining" not answerable from this witness (would need a softlock-state
  session, which REFUTED t288 bars for savestate restores; the needle SOP
  r288 §SOP UPGRADE remains the field instrument).
