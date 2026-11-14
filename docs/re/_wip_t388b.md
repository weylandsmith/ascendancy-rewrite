# t388b WIP — SOUND FIDELITY (D9) — session log 2026-11-14

STATUS: LANDED. The durable law lives in docs/re/audio.md §6 (engine +
addresses §6.1, volume §6.2, cue table + TUNEID base §6.3, silent-degrade
§6.4, button-SFX seam §6.5). This file keeps the working detail the law doc
deliberately omits.

## Session ledger
- No new sitting (live-timeline.jsonl mtime 2026-11-12 < HEAD commit
  2026-11-14 16:10) — assignment t388b stood.
- Windows.txt SOUNDCHANNEL census: 119 records, values {0 x118, -0 x1}.
- DIGITALMUSIC/FADEMUSIC/TUNEID strings: ONLY in game/ascend00.cob:0x2811f
  (a data blob), zero in the exe image — the parser matches on the verb
  NUMBER, words are labels.
- Payload pool anchors: 'SUBTITLE.TXT' 0x83fb0 (imm 0x1400), 'SUBTITLE'
  0x8411e, bad-data format 0x8419f (imm 0x15ef).
- Disasm via ~/tools/revenv/bin/python + capstone 5.0.7 (Ghidra HTTP 8089
  was down this session; not needed).
- CORRECTION during session: first WIP reading transposed the cue frames
  (said TUNEID 6@1, 7@20). cat -A of subtitle.txt: 6@20, 7@988, VOLUME 127
  @988 in its OWN FADEMUSIC block BEFORE the TUNEID-7 block. Fixed in code,
  tests, and audio.md §6.3 before any commit.

## Code sites changed (all cited in audio.md §6)
- rewrite/src/ui/audio.h/.cpp: trackNames() {theme00, intro00, intro01};
  playTune (switch/same-no-restart/-1-stop, STATIC range law so the state
  machine is device-independent); setMusicVolume (drop-not-clamp 0..127);
  --audio-trace prints with fflush; multi-tune musicWavs_ (each buffer must
  outlive its Mix_Music — 4d use-after-free lesson).
- rewrite/src/ui/ui.h/ui.cpp: playIntro(flic, maxFrames, audio) cue table
  {20 tune1, 966/971/976/981 vol 100/80/60/30, 988 vol 127, 988 tune2};
  fires at replay index i where i+1 == FRAMENUMBER (base ±1 named).
- rewrite/src/ui/title.cpp: runTitleScreen takes AudioEngine*; after Intro,
  playTune(0) restores theme00 (captured-selector law).
- rewrite/src/main.cpp: --audio-trace flag; silent-degrade on init failure
  (was exit 1); dead P3-era Mix_OpenAudio/Mix_CloseAudio pair removed;
  help text updated.
- rewrite/tests/test_audio.cpp: +4 tests (subtitle cue bytes, tune table +
  file sizes, volume scale, tune switch machine). run_tests now links
  ascend_ui (CMakeLists change).

## Witnesses (real runs)
- run_tests: 293 tests, 0 failed (was 289 + 4 new; prior suite green).
- Gate smoke shape: SDL_AUDIODRIVER=dummy --ui --resume --audio
  --audio-trace --campaign 1 --autoplay --seed 4 ->
  `audio ok: 85 sfx chunks, music 8191719 B` + `music 0 theme00` +
  `ui ok: turn 1`, exit 0.
- Intro cue live witness (scripts/_wip_t388b_intro_witness.sh): xsend click
  318,215 (Play Introduction) -> `music 1 intro00` fired at frame 20 mid-
  movie, dummy audio driver, Xvfb :81.
- Silent-degrade witness: --data /tmp/fakeroot2 (ascend01/data emptied of
  .voc) -> `audio: cannot open .../button.voc (degraded: silent)` then
  `ui ok: turn 1`, exit 0.

## Residue (open, named)
- TUNEID 1-based: [inferred] only; closing witness = user hearing or a
  capture diff of the heap tune table (B-relative reads failed before;
  §3.4 class).
- Per-button vendor SFX id: runtime-table-fed (+0x1bcc/+0x1bce), no static
  cite (§6.5). Port names stay documented choices until a witness exists.
- Race00..20 themes: unloaded; selector never captured (§3.3).
- FRAMENUMBER base ±1: one 71 ms frame slack, named in ui.h.
