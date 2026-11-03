# _wip_t292 — LIVE end-ctrl presenter witness (OQ-021 last residue), freeze-free poke-upward

Task (docs/STATE.md NEXT ACTION t292): in a SCRATCH session with its OWN ring
dir, poke V upward so V>=34 STICKS, run the end-turn pass, and WITNESS in order
(1) selector byte guest 0x43510 0 -> 5 written by evaluator FUN_00024a34 store
0x24d9f, (2) rank dword 0x4350c written, (3) the end-ctrl victory text on screen
(presenter table entry sel 5 @0x1eb468+0x14 -> end-ctrl.txt). HARD BUDGET 5
attempts; each dead RUN (EPIPE / ring freeze) counts as a negative.

## S0 — session-start state (t287 screen-check law, done BEFORE any probe)
- Production :9 pid 660167 ALIVE (timeout wrapper 660165, watch 660182 alive).
- Screenshot work/r1/t292_prod_screen.png (16:48) + vision: CAMPAIGN GALAXY MAP
  (turn 01150, "STARS CONTROLLED 23", neutral Biorythm panel) — HEALTHY, not a
  title menu, not a victory screen. Ring fresh (newest .sav 16:47:46).
- live-timeline.jsonl tail-scan 30 MB / 1264 rows: turn 1150 ONLY (walls
  13:20:08..16:45:50). NO new sitting -> r1_t85g_sitting NOT run; the t292
  assignment stands.
- No dosbox-x-dbg / Xvfb :96 leftovers from t290; port 55999 free.
- Oct-29 backup md5 verified 5b382afbb789186c3654f3cec085b2e2 (== OCT29_MD5 in
  scripts/r290_poke_session.py).

## S1 — t290 post-mortem read before relaunch (why poke, not freeze)
t290 attempt-2 (work/r1/t290-loop/attempt-2-freeze-34-console.log) reached the
fire window cleanly: sentinel BPLM 0028A2FB armed at title, ENTRY OK, MID-PASS
STOP eip=0x1e36c4 file=0x24274 [FLOOD], ds=0x168, SMV 34 OK, FM 0168:28A2FB
value 34 OK — then the DECISIVE 'EXEC RUN' EPIPE'd 40 s later and the ring froze
at t1086/V0 (no further autosaves). The ONLY new debugger state that run had
never carried before was the FM freeze itself (BPLM+SMV+RUN had all been
exercised in earlier sessions). Hence STATE's freeze-free directive: poke mode
keeps the sentinel and writes SMV d:40 — writes stick UPWARD because the flood
re-reads V and increments per admit (0x2439d..0x243a8), so N=40 >= 34 arms the
comparator regardless of how many admits remain.

## S2 — attempt log
(append one block per attempt: rc, run dir, fire lines, ring rows, verdict)

## S2 — attempt log
- 16:50:35 direct poke-40 launch (background): BREAK lottery loss, rc=1.
- 16:51:58 direct poke-40 launch: BREAK lottery loss, rc=1.
- 16:53:18 r290_relaunch.sh poke 40 3, inner attempt 1: lottery loss.
- 16:54:05 inner attempt 2 — POSITIVE rc=0 (full sequence in S0 note +
  work/r1/bank-t292-witness/session.log): armed title BREAK, BPLM armed,
  entry OK, MID-PASS STOP 0x24274 FLOOD, SMV 40, DECISIVE RUN survived
  (NO FM — freeze-free law confirmed), 9 drain fires V 40->56, ring t1087
  20/20 sel=5 rank=42, screen = end-ctrl.txt verbatim (vision-verified,
  banked end-ctrl-screen-t1087.png).
- VERDICT: all three witness legs observed -> OQ-021 CLOSED strict-close.
- Ledger mechanics touched: OPEN-QUESTIONS status cell + STATUS t292;
  ledger_audit.py --expect default drops OQ-021 (t195 precedent);
  STATE.md index block moved open->closed. audits OK (16 closed / 3 open).
- Production :9 untouched throughout (own ring dir law; pid 660167 healthy).
