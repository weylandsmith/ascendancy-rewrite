# WIP t395 — SOUND AUDIBILITY (D10 "not hearing any sound on Athens")

Working notes; distils into docs/re/audio.md §6.6 at landing.

## Census (MEASURED 2026-11-15, scripts/t395_soundchannel_census.py)
windows.txt (extracted/ascend00/windows.txt): 119 SOUNDCHANNEL records over
124 distinct NAME records. Value histogram {0 x118, -0 x1} — the lone `-0`
sits in the ALIENDIP record (file offset 0x51aa). Title-side buttons that
carry the field: INTRO 0, RESUME 0, EXITTODOS 0 (t394 measured NEXTTURN /
NEXTTURNCONT / cluster also 0). => CONFIRMS audio.md §6.5: the shipped table
carries NO per-button sound id; "channel 0 = click08" is NOT citable.
Channel->soundfx stays the named seam (OQ-027 leg b): FUN_000500e0 UI callers
0x17488/0x1749b read runtime control-record +0x1bcc/+0x1bce, no static feed.
OQ-027 STAYS OPEN (strict-close; the census re-pins the negative, closes nothing).

## Root-cause candidates for D10 silence (ranked)
0. CLICK08 OFF-MANIFEST (FOUND, MEASURED): click08.voc exists in
   ascend01/data but soundfx.txt does NOT name it -> AudioEngine never
   loaded it -> play("click08") silent no-op since t388 (campaign rail
   included). init() now loads it explicitly; chunks 85->86; gate 4d +
   pin audio_click08_offmanifest_t395.
1. THE FLAG GAP: AudioEngine only exists when `--audio` is passed
   (main.cpp o.audio). The exported README tells users `--audio` is an extra
   flag; a plain `./ascendancy --ui --data ...` boot NEVER opens a device and
   NEVER prints any audio line — not even the degrade warning. On Athens this
   is indistinguishable from device failure. FIX: audio ON by default on the
   --ui path (opt out --no-audio; --mute keeps load-at-zero), so the
   diagnostic line prints in EVERY user run.
2. init() failure with opaque err (e.g. "music track missing: theme00.raw"
   when --data points at a dir without extracted/ beside the cobs). FIX:
   every failure path names the exact paths tried (item 4 of the row).
3. playTune-on-entry: main.cpp:547 DOES call playTune(0) after init (t388b),
   so fresh launch is NOT silent-by-code any more — the row's LOCAL FACTS
   predate t388b. Verified: title.cpp:613 restores tune 0 after intro.
   Still wiring the law properly: pure bootTuneFor(state) + play on state
   entry in the title loop (covers Load-screen-return paths).
4. Title button clicks played nothing; campaign map plays click08 (port
   choice, §5). Symmetric port choice: click08 on title button clicks,
   labelled as port choice, trace-visible. Never claimed as vendor law.

## Diagnostic line law (item 3)
SUCCESS: `audio: driver=<Mix_GetCurrentAudioDriver> sfx=<loaded> tunes=<loaded>
vol=<0|127>` (one line, unmissable, printed in default-on mode always).
FAILURE: `audio: <err> (degraded: silent; paths tried: <p1>, <p2>, ...)` —
silent-degrade law unchanged: never aborts (main.cpp keeps exit 0).
