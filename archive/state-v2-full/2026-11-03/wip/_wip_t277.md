# t277 WIP — TL-expiry forensics (in progress)

## F1 TL=28800 EXPIRY CONFIRMED as the production death mode (MEASURED)
Census of every dosbox session ever logged in work/r1/vnc/dosbox.log (33
"DOSBox-X version" banners; per-session window = first..last guest timestamp
`LOG: [hh:mm:ss]`, plus the autosave count). Data: awk over the whole log,
session boundaries = banner line numbers.

  session  first      last       wall_s   saves   saves*10   delta
  S02      23:24:11   07:24:22   28811    2880    28800      +11
  S03      15:38:48   23:39:07   28819    2881    28810       +9
  S04      23:39:44   07:40:03   28819    2881    28810       +9
  S05      20:08:38   04:08:52   28814    2880    28800      +14
  S06      11:20:04   19:20:24   28820    2881    28810      +10
  S07      22:34:23   06:34:39   28816    2880    28800      +16
  S09      15:17:22   23:17:39   28817    2881    28810       +7
  S10      23:18:31   07:18:46   28815    2880    28800      +15
  S11      10:37:03   18:37:21   28818    2881    28810       +8
  S12      19:34:36   03:34:53   28817    2881    28810       +7
  S13      14:34:41   22:34:59   28818    2881    28810       +8
  S15      09:40:40   17:40:59   28819    2881    28810       +9
  S17      10:21:30   18:21:47   28817    2881    28810       +7
  S19      23:39:05   07:39:15   28810    2881    28810       +0
  S20      16:46:29   00:46:45   28816    2880    28800      +16
  S21      07:43:40   15:43:56   28816    2880    28800      +16
  S28      07:44:57   15:45:08   28811    2880    28800      +11
  S31      23:04:08   07:04:27   28819    2780    27800    +1019 (see F4)

18 of 33 sessions end at 28810..28820 s of wall clock with exactly
TL/CADENCE = 28800/10 = 2880 autosaves (+1 for the slot that lands in the
final second). The autosave count IS the TL counter read out through the ring:
2880 saves is 28800 s, not a coincidence and not a game-side event.
=> CONFIRMED: the "unexplained" deaths are -time-limit expiry, not an engine
   crash. S28 end 15:45:08 == the recorded Nov-1 15:45 death; S31 end
   07:04:27 == the recorded Nov-2 07:04 death; S21 end 15:43:56 == the third
   death the t273 note listed (its "+15:45 pattern" leg, Nov-1 prior day).
   All three are TL expiries.
Non-TL ends (manual stop / other class): S08 19033 s, S14 11541, S16 11489,
S18 13891, S22-S27, S29, S30, S32 (all < TL, or short interactive sessions).

## F2 SILENT EXIT — there is NO farewell line (MEASURED, negative)
The queue asked to find "the exact farewell line in the log or strings".
  - `grep -c 'Shutting down' work/r1/vnc/dosbox.log` == 0 (290 MB log).
  - `grep -c -i 'kill'` over the same log == 0.
  - The only time-limit strings in /usr/bin/dosbox-x are the help text
    "  -time-limit <n>    Kill the emulator after 'n' seconds" and the conf
    variable name "time-limit". No expiry/shutdown message exists.
  - Golden witness ON DISK: work/r1/selftest-t111-playcap/dosbox.out — the
    t111 TL=90 self-test (OUT dir playcap-20261027-210912, launched 21:09:12):
    first guest stamp 21:09:22, last line `LOG: [21:10:42]: Saved. (Slot 49)`
    followed by the slot-list refresh and then EOF = 90 s after launch, 9
    saves (9 x 10 s). It expired and logged nothing.
  - Same silent tail in work/r1/playcap-20261013-001711/dosbox.out and
    work/r1/playcap-20261014-214407/dosbox.out: last line of a dead session is
    always `LOG: Active save slot: 1 [Empty]` (the slot-list refresh), never a
    shutdown notice.
=> Detection-by-log-line is IMPOSSIBLE. Any liveness SOP must poll the process
   (recorded pid + /proc), which is exactly what r1_game_health.py does.

## F3 THE t267 WARNING IS TOO NARROW TO EVER FIRE (MEASURED from loop.log)
r1_game_health.py:136-137 appends T:WARN when TL-remaining <= WARN_AHEAD
(default 600 s). But the loop only samples health ONCE PER ITERATION
(loop_one_task.sh:185, immediately before the pre-flight gate) and iterations
run ~0.5-2.5 h (journal wake stamps 11:22:30, 13:47:12, 14:58:59, 16:16:21,
16:45:02). A 600 s window inside a 1-2.5 h sampling interval is ~7-17% likely
to be sampled at all. The Nov-2 07:04 death was caught at 07:39:24 — 35 min
AFTER the fact (loop.log G:DEATH), i.e. the detector works, the cadence does
not. WARN_AHEAD must exceed the iteration interval.

## F4 honest negatives / residuals
  - S31 (the Nov-2 07:04 death) banked 2780 saves in 28819 s: 1019 s of the
    window produced no ring row. Not re-litigated here (the t266 ~150 s
    oscillation class and modal-freeze windows both suppress rows); the
    lifetime conclusion is unaffected because wall clock, not the save count,
    carries it.
  - S27 (19:51:46 -> 02:52:00) 25214 s wall with 2689 saves: ended BEFORE its
    TL (manual stop / kill class), so it is excluded from the TL set.
  - Whether the internal -time-limit exit or the `timeout -s KILL $((TL+30))`
    wrapper is the proximate killer is NOT separable from wall clock alone
    (measured lifetime ~28821 s sits between TL=28800 and TL+30=28830). The
    help text says the emulator kills ITSELF, and the wrapper is a backstop 30
    s later; either way the session ends at the configured TL, which is the
    only thing the SOP depends on. [inferred] internal exit is proximate.
