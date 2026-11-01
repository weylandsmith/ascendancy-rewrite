# _wip_t255 — OQ-021 WRITER RE-PROBE with the t251 drive corpus

TASK (STATE.md NEXT ACTION t255): DAT_482fb (displayed "score stars", guest
data-seg 0x482fb) has ZERO statically-encodable writers (t212, three
instruments + controls). Redo the behavioural probe with the NEW drive
corpus (turns 1086->1255, scripted r1_t250_turndrive, plus the t187/t189b
sitting rows and everything banked in playcap). Goals:
  1. Full per-slot V=score_stars series in trusted order (r1_stream laws:
     dedup (file,mtime_ns), stale-echo watermark, turn>0).
  2. Classify every V-change: TURN-TRANSITION (turn advanced between this
     slot's obs and the slot's previous trusted obs) vs MID-TURN (same turn,
     V differs). Mid-turn changes falsify "recompute only at End Turn".
  3. Oscillation range check vs t212's 12..22 bank (did the drive widen it?).
  4. Alert conditions while streaming: selector_byte>0 anywhere; V>=25
     (T=50 -> comparator boundary, would be the OQ-021 closing observation).

MEASURED PRE-FLIGHT (session start):
- timeline work/r1/playcap/live-timeline.jsonl = 7,104,712,820 B @ 11:41,
  growing (self-play watcher alive; 7 watcher PIDs incl orphans — t214 law:
  do NOT kill, trust-law dedups).
- Live ring last row: 42.sav t=1255 V=14 sel=0 systems_any=36
  systems_full=29 planets_mine=36 wall 11:45:22. Game still at t1255
  (PLANET screen parked, Escape does not unwind — t254 law).
- watch.out has 292,953 DAT_482fb lines (all sittings; human format, cheap
  grep-able fallback if the jsonl scan is too heavy).
- Banks intact: bank-t251-predrive (20 slots @1086), bank-t251-live1255,
  bank-t1254 (20 slots @1254, V=23), bank-t249-live-open, bank-t1096.
- Known screen-open events (for trigger attribution):
  * t249: Planets screen opened on :9 at turn 1086 (sig-obj 0xfda074
    appeared between pre/post-click slots — docs/re/selfplay.md t249).
  * t251 drive 1086->1255: End-Turn clicks ONLY (r1_t250_turndrive v4;
    zero screen opens by construction; recovery never fired).
  * t187/t189b sitting: player opened screens incl 'c' overlay at t1255+.
  => If V oscillates DURING the drive window (turns strictly between 1086
     and 1255), the screen-open recompute hypothesis is falsified at turn
     granularity; if V is piecewise-constant per turn across the drive and
     only jumps at turn boundaries, per-turn recompute is corroborated
     (still not a write-site — strict-close stays).

STATUS: per-session analysis DONE (scripts/r255d_persession.py, output
work/r1/t255d_persession.out). Two HEADLINE MEASUREMENTS:

H1. ZERO MID-TURN V CHANGES across 65,380 deduped rows / 25 sessions /
    39 turn-boundary changes. V changes ONLY at turn transitions. Combined
    with the t249 controlled experiment (opening the Planets screen at turn
    1086 changed the header list but NOT V, before and after), the
    "recompute when a screen opens" hypothesis is REFUTED. The t189b
    testimony (player saw 14->21 across different screen-opens) is fully
    explained by per-turn evolution + opening the screen on different turns.

H2. V IS NOT PERSISTED WITH THE SAVE — same turn, two sessions, different V:
    t=1254: S17 (Oct-26 sitting) V=14 vs S21 (Oct-31 sitting) V=23 (the ONLY
    disagreeing turn; both trusted). Mechanism traced in the wall-clock
    record: the Oct-31 game session played continuously 1131->1254 (V
    co-evolved 22->23); it softlocked ~19:40, a RESTART loaded an OLDER save
    (turn 1086) and V came up 14 — a value that session had held at t~1238,
    NOT the continuous-run 23. Later the same state was re-driven
    (t251, Nov-1 08:11+) to 1255 where V rode 14. So V lives only at
    [0x482fb] in RAM, is NOT restored by load (the loader never writes it —
    consistent with t212's ZERO static writers!), and its value is a
    function of the session's PLAY HISTORY, not of the save-state snapshot.
    This also EXPLAINS the t212 semantic non-join (V in {0,1} on fresh
    saves) and the V=0 rows at turns 692/1131/1253/1086 (title-slot class
    after restarts: in_game true via turn>0, V never written).

H3. Oscillation range did NOT widen with the drive corpus: V in 8..23 over
    the whole corpus (T=50). No V>=25 row, no selector arm, anywhere. The
    Control-victory boundary test remains unobservable passively at the
    current operating point (V rides 14 at live t1255; systems_full=29).

PARSING PITFALLS BANKED (t255): (a) watcher APPENDS systems_*/mtime/wall at
line END (multi-KB rows) — head-600 parse sees None there; (b) '"file": "'
is 9 chars — r1_stream.py:15 `i += 8` lands ON the quote so its fn field is
always '' (dedup survives on mtime; file attribution silently empty — do not
trust r1_stream's file field, r255c/r255d parse it correctly); (c) the
GLOBAL stale-echo watermark drops a deliberately re-loaded lower-turn
campaign (r1_stream doc caveat) — per-session trust is REQUIRED for this
corpus (r255d).

TRAJECTORY RESULTS (scripts/r255f_traj.py, work/r1/t255f_traj.out):

H4. V==0 AT EVERY SESSION'S LOAD TURN, first value appears at the FIRST
    End-Turn after load — 20/25 sessions show the pattern (t692->693,
    t1131->1132, t1086->1087, t1253->..., t1254->...). Load/start does NOT
    restore V (slot zero); V is RECOMPUTED at the turn boundary. Kills the
    "loader writes it" branch of t212's residue and re-confirms H2
    (not-persisted) from a second direction.

CORRECTION (t255 wall-clock drill-down — the H5 claim above was an artifact
and is WITHDRAWN to its supportable core): the ring samples every ~10 s but
during the Nov-1 drive the game ran 1087->1255 in ~6 minutes, so turns
1097..1254 were NEVER OBSERVED in S24. Corrected facts:
  * V=23 was OBSERVED across turns 1087..1096 (9 trusted turn boundaries)
    while any/full/planets/ships moved — still supports "V != territory
    snapshot", NOT "flat for 167 turns".
  * 23->14 happened inside the UNOBSERVED sprint 1096->1255 (08:14:19 t1096
    V=23 -> 08:17:39 t1255 V=14), during heavy self-play combat. The H2
    narrative "the value the pre-drive session banked" is WRONG — no
    cross-session memory is needed; V simply fell during the sprint.
  * H2's core stands: at the SAME turn t1254, two lineages disagreed
    (Oct-26 V=14 vs Oct-31 V=23, both any=36) — V is not a function of the
    save snapshot alone; it depends on lineage history.
  * STRONGER version of H4 from the same drill-down: after the Oct-31
    19:51 restart the game sat at t1086 with V=0 for 5.8 h (41.sav
    19:51:46 V=0), then the FIRST End-Turn produced V=23 — and the Nov-1
    08:11 restart from the same loaded state reproduced V=23 at t1087
    EXACTLY. So (a) the save does not restore V (it read 0 all night), and
    (b) the first-turn recompute is DETERMINISTIC in the loaded world state
    (same state -> same 23), while mid-campaign V is not a territory count.
    The recompute's inputs include something that decays during combat
    sprints (23 -> 14 across the 1096..1255 self-play sprint).

H6. past-match lag search: of ~39 V-changes, only 7 hit any/full/planets at
    ANY past turn in-session (mostly coincidences at V==any in early game);
    the "V = stale territory snapshot" family is not supported beyond what
    growth alone explains.

PROBE NEXT (out of budget this iteration, fold into t256+ or a t255b slot):
owner-wise ship census per turn (ship_raw is in every row) aligned to V
change turns in S18 vs flat turns in S24 — discriminates "enemy ships
defeated this turn" vs "systems contested".
