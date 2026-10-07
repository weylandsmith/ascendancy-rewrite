# Audio — vendor formats and the P5b scope [codec settled; rates partly open]

Implementation: `rewrite/src/formats/voc.{h,cpp}` (pure parsing, in
ascend_core, unit-tested) + `rewrite/src/ui/audio.{h,cpp}` (SDL2_mixer,
2.8.1 on this host). Manifests: extracted/ascend00/{soundfx,music}.txt.

## 1. soundfx.txt [verified line-by-line]

`extracted/ascend00/soundfx.txt` (CRLF): 3 header lines `2 10000`,
`3 45000`, `1 65000`; then the literal count `86`; then 86 sample names
(bare, no extension, mixed case, `shield` listed twice). All 86 names match
a file `<name>.voc` in extracted/ascend01/data/ case-insensitively.
The header-pair semantics are UNKNOWN (OQ-018) — nothing consumes them.

## 2. The vendor "VOC" container (15 files) [verified on all 15]

Magic `Creative Voice File\0` (bytes 0..19), then NON-STANDARD layout —
standard VOC block chains parse to zero blocks, so treat as vendor-specific:

```
off  size  meaning                    (bang01.voc, filesize 41420)
0    19    "Creative Voice File" (NO NUL; byte 19 is 0x1A, byte 20 0x1A)
20   u16   version, always 26         26
22   u16   always 0x0114              276
24   u8    block type, always 0x1F    0x1F
25   u16   always 0x0911              2321   (meaning unknown, OQ-018)
27   u24   PAYLOAD-REGION length      41389 == filesize - 31 (all 15)
30   u32   SAMPLE RATE Hz             22050 (14 files) / 11025 (bullet.voc)
34   u8    bits per sample            8 (all 15)
35   u8    channels                   1 (14 files) / 2 (bullet.voc)
36   6     always zero                (unknown field, OQ-018)
42   ...   PCM 8-bit unsigned (0x80 = silence; first sample after the
           zeros is 0x80 on 14/15, 0xA4 on bullet)
last      always byte 0x00            (all .voc files)
```

Playback interpretation used by the rewrite: PCM = bytes 42..EOF−1,
format u8 unsigned at the header rate, 1 channel (bullet.voc's 2 is played
as-is via the header value). The u24 at 27 counts filesize−31, i.e. 11
bytes MORE than PCM(42..EOF) — recorded as an invariant, NOT reinterpreted;
if the vendor meaning turns out to shift PCM to 31 or 36, audio is a few
bytes of silence different and the probe pins whichever it is.

## 3. Headerless samples (77 .voc + all .raw) [verified: no header at all]

First bytes are PCM silence (0x80 region; 63/77 .voc start within ±4 of
0x80). Codec is uncompressed 8-bit unsigned PCM [inferred from the 15
headered files + identical byte character]. SAMPLE RATE AND CHANNEL COUNT
ARE NOT IN THE FILES [verified by exhaustive header search] — OQ-006
stays open pending exe-side audio init (R1-blocked). P5b DEFAULT:
22050 Hz mono, matching the 14-of-15 majority rate of headered SFX. An
FFT anti-alias check was run and is NOT decisive (music spectra are
bottom-heavy at either rate) — recorded so nobody re-tries it expecting
an answer.

### 3.1 Rate law MEASURED — OQ-006 CLOSED 2026-10-07 [verified, restored image]
The exe plays ALL audio (headered, headerless, music) at **22050 Hz mono**.
Chain in ascend_payload.bin (byte-identical to work/ascend_restored.bin):

- **0x4f690** `PUSH 0x5622` (=22050) / `PUSH ESI` / **0x4f696**
  `CALL 0x68816` — first audio-open site (inside the audio-config block
  that reads the setup word at [EBP+0x223], -1 = audio-off bail @0x4f669).
- **0x4f90b** `PUSH 0x5622` / `PUSH EBP` / **0x4f911** `CALL 0x68816` —
  second open site (same block, post-`FUN_0004f9bc` branch).
- **0x68816** wrapper (logging-guarded: call-count global 0xa2190, debug
  format strings at pool 0x40fb/0x407c — same wrapper shape at 0x685e0,
  0x68f6c) forwards arg2 verbatim at **0x68882** `CALL 0x6e000` — its
  ONLY call edge in the whole image (E8-scan).
- **0x6e000** rate setter: `MOV [EAX+0x3c], EDX` (arg2).
- Constructor default at **0x6df3e** `MOV dword [EAX+0x3c], 0x2b11`
  (=11025) — overwritten by both open sites at every startup; there is no
  path where a file header rewrites +0x3c (no imm32 write sites at
  disp8/disp32 0x3c outside these, C7-scan over the full code range).

So the 11025 header of bullet.voc is honoured by the FILE loader (formats
side, §2), while the DEVICE rate for everything else is the open-chain
constant 22050. Rewrite: `Mix_OpenAudio(22050, …)` (ui/audio.cpp:55) and
`Sample::rate = 22050` (formats/voc.cpp:30) now cite this chain; pin test
`audio_open_rate_measured_oq006` checks the exact bytes at 0x4f690,
0x4f90b, 0x6df3e. Channel count: the object exposes no channels field in
this chain (+0x40/+0x44 are buffer-size/volume plumbing set from globals at
0xa2570); vendor DOS audio is mono-by-convention, and the rewrite's stereo
mixer is a documented presentation choice — mono samples upmix
identically. OQ-018's soundfx.txt header pairs remain open.

## 4. music.txt [verified]

29 entries `data\<name>.raw`: theme00-04, victory, intro00-01, race00-20.
All 29 files exist: theme*/victory in ascend02/data, intro* in
ascend01/data, race* in ascend02/data. Sizes 0.44-8.2 MB headerless PCM
(= 20-371 s @22050 mono, 10-186 s if stereo; loop behaviour unknown).

## 5. P5b runtime scope (documented defaults; no fakery)

- `ui/audio.cpp`: opens SDL2_mixer (22050, stereo, 512), builds in-memory
  RIFF WAV wrappers around vendor PCM (Mix_LoadWAV_RW cannot read raw),
  loads ALL 86 manifest SFX + theme00 music; prints
  `audio ok: <n> sfx chunks, music <bytes> B` and exits non-zero on any
  load failure. `--audio` opts in; UI plays click08 on NEXT TURN, laser01
  on map click, bang01 when a new event line contains "captured" (names
  verbatim from soundfx.txt §1). `--mute` zeroes mixer volume.
- Gate 4d: SDL_AUDIODRIVER=dummy + `--ui --audio --campaign 1` must print
  the audio-ok line and `ui ok: turn 1`, exit 0.
- NOT in P5b: music track SELECTION logic (which race gets which theme —
  race00..20 mapping unknown, OQ-018), stereo music semantics, per-sample
  volume from the soundfx.txt header pairs, voice/panning, and any rate
  correction when OQ-006 closes. No synthesized sounds; if a sample is
  missing, nothing plays and the gate shows it.

### 3.2 OQ-018 PARTIAL (2026-10-07) — soundfx.txt header-pair law, loader side
Loader FUN_0004ff34 (unique referrer of `soundfx.txt` string, imm 0x2a08 @0x4ff42):
- parses EXACTLY 3 header lines with sscanf format pool 0x2a14 (`%d %d`),
  loop `CMP EDI,0x3` at 0x4ff66; per-group dword arrays via `ADD ECX,0x4`
  (0x4ff60), i = 0..2. Per line (ESI = running cumulative, decompile
  FUN_0004ff34 confirms):
  group START `[obj+0xc50+4i] = ESI` (0x4ff83);
  group END `[obj+0xc5c+4i] = ESI + n - 1` (0x4ff8f);
  group THRESHOLD `[obj+0xc44+4i] = col2` (0x4ff99) — per-group stride 4
  (NOT last-wins; corrected same-turn from the decompile);
  acc += n*col2 (IMUL 0x4ffa2) — Σ = 2*10000+3*45000+1*65000 = 215000 sizes
  the sample buffer allocation, and per-slot cursor bases are
  base + Σ-of-preceding-group sizes (0x4ff34 tail loop `iVar2 += [obj+0xc44]`
  per group crossing, written at `[obj+0xbb8+0x16i]`);
  monotonicity gate: error line 839 (str 0x2a1a) when col2 decreases across
  lines (file is ascending 10000/45000/65000);
  Σ(col1) must equal 6 else error (decompile `if (iVar5 != 6)`), verified on
  file 2+3+1=6;
  then count line `%d` -> `[obj+0x700]` u16 (<100 enforced, line 873) and
  entry names `%9s`-style at `[obj+0x702 + 10i]`; 6 voice slots stride 0x16
  init: +0x00 ptr, +0x10 u16 0, +0x12 u16 0x5622 (=22050 — OQ-006 cross-ref:
  the rate constant is stamped into every slot), +0x14 u16 0xffff.
- play path FUN_000500e0 (callers 0x17488, 0x1749b, 0x4fb59): scalar
  `FUN_000209d8()` (value = table[DAT_000102a4+i] - table[DAT_000102a0+i],
  override scan over DAT_00010a74/DAT_00010b82 while DAT_00010b96>0) compared
  against THREE dwords obj+0xc44/+0xc48/+0xc4c; group index = count of
  thresholds <= scalar; a free voice slot is then searched inside that
  group's [start,end] over the 6-slot table obj+0xbb8 stride 0x16 (slot
  fields: +0x04/+0x08 buffer cursors, +0x0c end, +0x12 priority-ref u16
  (the value scanned at 0x6df3e-area presets), +0x14 sound idx);
  eviction: oldest active slot in-group via
  FUN_000689ee()==4 (playing?).
- REMAINING (do not guess): writer of obj+0xc40 (no disp32=0xc40 write found
  in 0x200..0x82bb0; likely SIB/pointer form or constructor at 0x6ed50-area)
  and the provenance of the FUN_000209d8 scalar (perf/clock table
  DAT_000102a0/0x102a4) — together they decide whether the second header
  column is a per-sample byte cap (allocation evidence says yes) or also a
  playback threshold. VOC u16@25=0x0911 and race->theme mapping also open:
  music.txt lists 29 entries (theme00..04, victory, intro00/01, race00..19
  .raw; pool imm refs 0x2a66 `data\%s.voc`, theme00.raw ref @0x210f3).
- SCALAR PROVENANCE (2026-10-07 turn 2, xrefs via Ghidra get_xrefs_to):
  DAT_000102a0/0x102a4 are indexed by obj+0x108 — a TICK-TIMER SLOT field:
  sibling FUN_00020a50 computes tickget(FUN_000779e6->0x7b1ad) -
  [idx*4+0x102a0] (0x20a6e `SUB EBX,[ECX*4+0x102a0]`), FUN_00020a7c starts
  timers, FUN_00020ad0 is a wait-until-expired loop (PUSH 5 tick sleep
  @0x20af0). FUN_000209d8 = table 0x102a4[idx] - 0x102a0[idx] (slot span),
  with override scan 0x10a74/0x10b82 while [0x10b96]>0. So the play path
  buckets by a TICK DELTA, not a byte length.
- BYTE-CAP HYPOTHESIS REFUTED (measured census, extracted/ascend01/data):
  77/86 soundfx entries resolve to .voc files; ZERO exceed 65000; max is
  laser01 = 45277 bytes — but laser01 is entry index 2, i.e. GROUP 1
  (indices 2..4, col2 45000), so a per-sound col2 byte-cap is violated by
  277 bytes. Group membership is by INDEX (col1 cumulative), col2's role in
  the play path is the eviction-band tick threshold (first c44[i] >= scalar;
  all-below -> vendor error). Buffer geometry per loader tail: per-group
  region n_i*col2_i, slot cursor bases cumulative.
- STATUS: col1 = voices-per-index-band [verified]; col2 = ascending tick
  threshold + alloc contribution [verified]; scalar physical unit [open —
  next step: disassemble FUN_0007b1ad (tick source; DOS 18.2Hz vs ms) —
  10000 ticks @18.2Hz = 549 s is implausible for per-sound play, ms would
  give 10 s plausible bands 10/45/65 s]. VOC u16@25 and race->theme open.
- TICK SOURCE PARTIAL (same turn): FUN_0007b1ad reads software timer slot
  `[DAT_0x9868 + id*4]` (0x7b1fb), returns 0 when id >= [DAT_0x9814]
  (slot-count global, unsigned JC), and for ids <= 5 pokes hardware PIT
  port bytes ([0x9868]+id*4+1 bit 0x40 latch check, helper 0x78db0) — so
  slots 0..5 shadow the DOS tick counter, higher slots are software-
  incremented. Unit of the incrementer = the LAST unknown for the
  10000/45000/65000 bands (find writers of [0x9868] slots / the ISR chain).
