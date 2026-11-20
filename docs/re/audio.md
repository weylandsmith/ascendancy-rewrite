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
### 2.1 Headered-VOC byte map MEASURED 2026-10-07 (closes OQ-018 VOC residue)
All 15 headered files (magic "Creative Voice File\0x1A" @0..19): ver@20 ==
0x1A; type@24 == 0x1F; **u16@25 == 0x0911 on 15/15** — the long-standing
"0x0911 mystery" resolves as a CONSTANT across every shipped headered file
(no per-file payload; no code read-site located; loader-side validation
pins it, rewrite/src/formats/voc.cpp). u16@27 == filesize − 31 on 15/15
(PCM byte count); LE u32@30 = play rate, 22050 on 14 files, and
**bullet.voc is the only exception: 11025 Hz + byte@35 == 2 (stereo)** —
the vendor honours the header per file, which is why the OQ-006 device-rate
law and the OQ-012a rate-setter chain remain about the DEVICE, not per-
sample rates; byte@34 == 8 (bits); byte@35 == channels ({1,2}); bytes
36..41 all zero on 15/15 (the "six zero bytes @36" residue: reserved,
invariant — closed as a measured constant, nothing synthesises from them);
PCM 42..EOF−1 with trailing 0x00. Census: stereo files == {bullet.voc};
rates == {22050 x14, 11025 x1}. Test pins: audio_headered_voc (existing)
now runs under the stricter field checks.

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
  with override scan 0x10a74/0x10b82 while [0x10b96]>0. Whether the span is
  ticks or loaded-sample bytes was OPEN at this point (see SCALAR IDENTITY).
- BYTE-CAP STATUS CORRECTED (turn 3): the turn-2 "refuted" note was WRONG —
  it grouped sound effects by MANIFEST INDEX, but FUN_000500e0 selects the
  group by the SCALAR THRESHOLD rule (first c44[i] >= scalar). Under that
  rule the measured census is CONSISTENT with col2 = per-group sample-size
  cap: 77/86 .voc resolve in extracted/ascend01/data; ZERO files >65000;
  the single file >45000 (laser01 = 45277) falls into band 2 (cap 65000),
  and the 73 files in (10000,45000] max at 44633/45277 under caps 45000/
  65000. Buffer regions n_i*col2_i (2*10000, 3*45000, 1*65000; Σ=215000)
  are exactly sized for the band's cap x voice count. col1 = voices per
  band [verified]; col2 = band size cap + group threshold [verified].
- SCALAR IDENTITY (open, the real residue): FUN_000209d8 = [0x102a4+4i] -
  [0x102a0+4i] with i = obj+0x108. NO disp32 WRITER exists for either table
  (Ghidra get_xrefs_to: 5 refs, all READS @0x20955/0x20a0a/0x20a6e/0x20a99/
  0x20b5b) — the tables are built through pointer indirection at init. Two
  live hypotheses: (a) loaded-sample span (end-start) -> col2 cap reading
  complete; (b) named-timer span (sibling FUN_0002086c registers timers by
  NAME from a 50-byte-stride table at 0xa0f8; FUN_0007b1ad tickget reads
  [DAT_0x9868+id*4], 0 if id>=[DAT_0x9814] @0x7b1b4, PIT-shadow for id<=5;
  helper 0x78db0 = INT 21h AH=44h IOCTL input-status TEST, NOT a tick pump —
  turn-2 note "PIT-port latch pump" over-stated, corrected). Decisive next
  probe: callers of FUN_0002086c and what sets the AUDIO object's +0x108.
- PAYLOAD vs RESTORED DISCREPANCY (turn 3, [verified]): the two files differ
  at 6244 bytes / 993 clusters; 850 clusters match imm+=0x82BB0 exactly (the
  documented fixup), 143 clusters are NOT imm-fixups (jump/data tables,
  e.g. 0x84e4, 0x156b4). Ghidra program = payload (pre-fixup disps); use the
  RESTORED file only for byte-pinning, and re-verify any disp-semantics
  claim against BOTH. Test audio_open_rate_measured_oq006 pins restored-
  image bytes — keep payload-semantics wording aligned (0x4f690 both).
- STATUS (turn 3 restatement): col1 = voices-per-band [verified]; col2 =
  ascending band size cap, n*col2 region sizing [verified]; band selection
  scalar = FUN_000209d8(obj-handle) span of tables 0x102a0/0x102a4 —
  LOADED-SAMPLE SPAN vs TIMER SPAN undetermined (see SCALAR IDENTITY);
  physical unit question defers to that identity. VOC u16@25=0x0911 and
  race->theme mapping open.
- SCALAR IDENTITY CLOSED — MEASURED (turn 4, R1 capture ck005 + ck014 +
  ck018 of r1ad-20261006-144225, base B=0x1bf4d8, index law member=B+
  0x82BB0+X): the pair of tables DAT_000102a0/0x102a4 IS THE RESOURCE-FILE
  SPAN TABLE, parallel to the name table at image 0xa0f8 (stride 50,
  entries "data\NAME" + start u32 + end u32, count [DAT_0x10a70]=471 at
  runtime). Proof: 327/328 disk-comparable entries have span (end-start)
  EXACTLY equal to the on-disk file size (the single mismatch is
  data\intro01.raw, whose negative span marks the ascend02 archive mount —
  entries 0..52 ascend00 text set, 53+ ascend02 data set with its own
  base). ALL 86 soundfx manifest names are present; laser01.voc span =
  45277 = disk size exactly. Tables byte-identical across turns 0/1/2 —
  file offsets, not timers (the timer-adjacent sibling FUN_00020a50 uses
  the same start array for a different purpose; earlier "tick delta"
  framing is dead).
- HEADER-PAIR LAW, FINAL (closes the OQ-018 audio sub-question): at play
  (FUN_000500e0) the sample's FILE SIZE (span, via FUN_000209d8 with the
  file-table index at obj+0x108) selects the voice band = number of leading
  col2 thresholds <= size (do-loop in FUN_000500e0: break when size <
  c44[i]; all-three-below -> FUN_0002a428 vendor error); size >=
  65000 (all three <= size) = vendor error. Measured census over the 86
  manifest entries: band0 (<10000, 2 voices) = 4 files, band1 (10000..45000,
  3 voices) = 81, band2 (45000..65000, 1 voice) = 1 (laser01),
  WOULD-ERROR = 0 — shipped data is exactly consistent with the cap law.
  Band = voices-per-size-class with in-band eviction (FUN_000689ee()==4
  scan); region sizes n_i*col2_i. col1 = voices/band, col2 = size-class
  threshold, BOTH [verified] static: file 2 10000 / 3 45000 / 1 65000.
  CORRECTION (turn 4): earlier "77/86 resolve" was a case artifact — with
  names lowercased ALL 86 manifest lines (85 unique, 'shield' twice)
  resolve to lowercase .voc files in ascend01/data; census over the 86
  lines: {band0:4, band1:81, band2:1, error:0}. Rewrite pins this as
  formats/voc.h voiceBand() + test audio_voice_band_law_oq018.

### 3.3 Race->theme tune selection (2026-10-07, static chain + capture census)
MEASURED facts:
* music.txt loader = FUN_00020fd4 (unique caller FUN_0007b7d7); loads all 29
  tracks (theme00..04, victory, intro00/01, race00..20) via name/span tables;
  span-table check vs ascend02 files: 27/27 span == on-disk size.
* Global tune state DAT_00010ba0 (image): get_xrefs_to -> 14 refs, exactly ONE
  writer: 0x21309 inside FUN_00020fd4. Sequence @0x212f6: CALL 0x77ece
  (key imm 0x943, second imm 0x945 — compressed string pool, name NOT
  statically recoverable, same limitation class as OQ-020 runtime strings);
  if returned nonzero -> MOV [DAT_00010ba0], -1. No other store exists in the
  whole image (SIB-aware 89/C7 scan of disp32 a6480000/aa480000 confirms the
  audio-object fields +0x48a6/+0x48aa are only written 0 / -1 state values,
  never track numbers).
* Capture census: DAT_00010ba0 == 0 in ALL banked saves (ck005 and ck010 x5
  runs, r1ad-20261006-131350..153435) at member B+0x82BB0+0x10ba0.
REFUTED: the "race->theme mapping TABLE" hypothesis — no table, no format
strings (%s.raw/race%02d absent image AND runtime RAM), no per-race writes.
OPEN CONTRADICTION [unverified]: music player FUN_00059c70 validates the
opened-file span CMP EAX,0x1d4d0 @0x59cc5 (error 0x1047 if above), yet
theme00.raw span == 8,191,719 bytes in ck005. So either +0x48a6 indexes a
segmented/chunked view (0x1d4c0-byte reads seen @0x59cef) or FUN_00059c70 is
not the main-menu theme path. Resolving needs the options-menu capture (set
the DAT-gating option, capture, diff) or the compressed-pool decoder.
REWRITE: audio.cpp playMusic uses data/theme00.raw == music.txt track 0 ==
the vendor path observed in every captured configuration; no default change
required for the captured domain. [verified] = image/capture facts above.

### 3.4 OQ-022 CLOSED as "engine unreachable in captured states" (2026-10-07)
Decision-rule result from the FUN_000598fc head disassembly:
* The function copies the caller name (pool imm, e.g. 0x2cce) into static
  buffer DS:0xa200c (WIDE copy loop — bytes kept at even offsets), appends a
  suffix from pool 0x3561 (probably an extension), mirrors [0x484d0]/
  [0x484d4] into DS:0xa2000/0xa2004, then GUARDS: if [obj+0x48a6] == -1 OR
  [obj+0x48aa] == -1 it returns at 0x59984 with EAX=0 — the 0x1d4d0-checked
  open FUN_00059c70 @0x59987 is NEVER reached [verified disasm].
* Image-wide writer census (SIB-aware, t6): +0x48a6 stores = {0 @0x5454b,
  -1 @0x5988f, 0 @0x598c9}; +0x48aa stores include -1 @0x54911, @0x59990,
  @0x59a96. NOTE: these are heap-relative object fields (the audio object is
  heap-allocated; reading DS base+0x48a6 returns unrelated text bytes), so
  their per-capture values were NOT measured — the selector DAT_00010ba0
  (static, DS) == 0 in all captures [verified].
* Capture corroboration: static name buffer DS:0xa200c is ALL ZEROS in all
  10 banked saves (ck005 x5 + ck010 x5, runs r1ad-20261006-131350..153435 —
  the complete banked set) — no name was ever composed there during the
  captured runs [verified via pointer law member B+0x82BB0+0xa200c].
Conclusion [verified facts + inferred]: the DIGITALMUSIC-style engine path
(0x598fc/0x59dfc -> 0x59c70) is INACTIVE in every captured game state — the
menu music heard by the vendor in these states is therefore NOT served by
this engine (no claim about what serves it; candidates: startup load of all
29 tracks + a separate raw-play path, unmapped). The span-vs-check
"contradiction" evaporates: no captured run feeds theme00 to the 0x1d4d0
check. Rewrite loads theme00.raw directly == observed vendor state; code
site rewrite/src/ui/audio.cpp playMusic (comment updated to cite §3.4).

## 6. t388b SOUND FIDELITY law (2026-11-14; payload disasm + subtitle.txt)

### 6.1 The subtitle-script engine (flic.cpp) [verified, payload bytes]
Loader 0x2d144 refs 'SUBTITLE.TXT' (pool imm 0x1400 = file 0x83fb0) then
parser 0x2e46c reads each line VERB-NUMBER-first (sscanf pool '%s %d'-family
at 0x77fe1) and dispatches at 0x2e4fe..0x2e525: case 2 -> 0x2e614, case 11
-> 0x2ea50, case 16 -> 0x2e947, unknown -> "Bad Subtitle Data" (pool 0x15ef,
error reporter 0x2a438). The verb WORDS DIGITALMUSIC/FADEMUSIC exist ONLY
as ascend00.cob data (game/ascend00.cob:0x2811f) — zero copies in the exe
image: the numbers are the real verb ids; the words label them in the file.
- case 16 (DIGITALMUSIC arg): stores type word 0x1e (=30) at rec+0x206
  (0x2e9e8; COMMAND==1 -> 0x1f=31 via setne/add 0x1e @0x2e9c7); TUNEID ->
  rec+0x208 dword (0x2e9a3); COMMAND -> rec+0x204 (0x2ea24). The literal
  `16` is NEVER stored — the handler ignores its own argument number.
- case 11 (FADEMUSIC arg): stores type word 0xb at rec+0x206 (0x2ea81);
  CHANNEL -> rec+0x208 (0x2eac2); VOLUME -> rec+0x204 (0x2eb36, word).
- tick/consumer loop 0x2ed37 (stride-0xc records): 0xb -> 0x2ee72 calls
  FUN_0004feec(obj, movsx VOLUME); 0x1e -> 0x2edf5: TUNEID==-1 ->
  FUN_00067b85(handle) (stop), else FUN_000678ec(handle, TUNEID) (play);
  0x1f -> 0x4f9bc (stop/finish); type 1 -> frame bookkeeping.
- FUN_000678ec -> FUN_00074a88(handle, tuneid): opens slot table entry,
  stores tuneid at [handle+0x8868]; the tune table is heap-relative, so the
  BASE (0- vs 1-indexed) is NOT statically decidable — same limitation
  class as §3.4's +0x48a6 fields.

### 6.2 VOLUME law [verified]
FUN_0004feec @0x4feec: stores the volume byte at [audioObj+0x6fe] ONLY when
-1 < v <= 0x7f; out-of-range values are SILENTLY DROPPED (no clamp, no
error), then the device is poked via CALL 0x6888c(device,[obj+0x358]).
Sibling 0x4ff1c stores a second 0..127 byte at +0x6ff (same guard). Vendor
music-volume scale = 0..127. Rewrite mirror: vendorVolumeOk() +
AudioEngine::setMusicVolume drop-not-clamp (ui/audio.{h,cpp}); pin
audio_vendor_volume_scale_law.

### 6.3 Intro cue table (subtitle.txt verbatim law) [verified file bytes]
  DIGITALMUSIC 16 / TUNEID 6 / COMMAND 1 / FRAMENUMBER 20
  DIGITALMUSIC 16 / TUNEID 7 / COMMAND 1 / FRAMENUMBER 988
  FADEMUSIC 11 / CHANNEL 0 / VOLUME 100|80|60|30 / FRAMENUMBER 966|971|976|981
  FADEMUSIC 11 / CHANNEL 0 / VOLUME 127 / FRAMENUMBER 988
(file order: the VOLUME-127 line precedes the TUNEID-7 block, so the dip
100->30 recovers to full volume ON the switch frame.) Pin
audio_subtitle_script_cues_oq018 pins these lines byte-exactly.
TUNEID->track mapping [inferred, NOT statically decidable — §6.1]: 1-based
music.txt reading 6=intro00.raw, 7=intro01.raw. Consistency witness:
intro00 2,000,000 B = 90.7 s @22050 mono covers frames 20..988 (80.6 s)
without looping; intro01 479,670 B = 21.75 s covers the movie tail (988 ->
1144 frames = 11.1 s) plus title handoff. The 0-based reading (6=intro01
looping ~4x over 80.6 s, 7=race00 as intro music) is structurally possible
but content-incoherent. HONEST STATUS: 1-based banked as the port's law,
labelled inferred; a USER listening check (intro tune count/character) is
the closing witness if ever needed.
Rewrite: AudioEngine::trackNames() = {theme00, intro00, intro01} (cited
members only; race00..20 stay UNLOADED — the race->theme selector never
materialised in any capture, §3.3); playIntro(flic, maxFrames, audio) fires
the cue table at frame index == FRAMENUMBER-1 (the FRAMENUMBER base is
±1-uncited; one 71 ms frame of named slack); title.cpp restores tune 0
(theme00, the captured-selector law §3.3) after the movie. playTune switch
law: different tune replaces, same tune never restarts, -1 stops (vendor
TUNEID -1 path). Pins audio_tune_switch_law + audio_music_tune_table_law.
Instrument: --audio-trace prints `sfx <name>` / `music <n> <name>` (fflush)
per played sound — wiring is machine-verified, hearing stays the USER's
grade (R13). Live witness 2026-11-14 (scripts/_wip_t388b_intro_witness.sh,
Xvfb :81 + xsend click 318,215): `music 0 theme00` at boot, `ui title click
INTRO -> intro`, `music 1 intro00` at frame 20.

### 6.4 Silent-degrade law + dead-code removal [verified behaviour]
main.cpp: --audio init failure now prints `audio: <err> (degraded: silent)`
and CONTINUES without the engine (was: exit 1). Witness: --data
/tmp/fakeroot2 (archives + ascend00/ascend02, ascend01/data emptied) ->
`audio: cannot open .../button.voc (degraded: silent)` then `ui ok: turn 1`,
exit 0. The dead P3-era Mix_OpenAudio(22050, S16SYS mono, 1024) block on the
non-campaign path (and its matching Mix_CloseAudio) is removed — it opened a
second device, played nothing, and its "rate provisional, OQ-006" comment
predated the closed law.

### 6.5 Button SFX id: NOT statically cited — named seam
FUN_000500e0's UI callers 0x17488/0x1749b read the sound index from
control-record fields +0x1bcc/+0x1bce (runtime window-item table area,
stride 0x1e); no static literal feeds them, and windows.txt SOUNDCHANNEL is
0 on 118 + -0 on 1 of 119 records — the shipped table carries NO per-button
sound id. Which of button/button01/button02/click08 the vendor plays per
button class is therefore uncited; the port keeps click08 on NEXTTURN /
laser01 on map click / bang01 on "captured" as DOCUMENTED port choices
(§5). STATE.md's phase-10 note '"2 10000 button" is the cited SFX id' is
FALSE — soundfx.txt has no such line (header pairs are 2 10000 / 3 45000 /
1 65000; name list starts `button` at index 0). Closing witness candidates:
a capture diff of the +0x1bcc field across control types, or user hearing.

### 6.6 t395 SOUND AUDIBILITY law (2026-11-15; D10 "not hearing any sound on Athens")

MEASURED this iteration (scripts/t395_soundchannel_census.py): windows.txt
carries 119 SOUNDCHANNEL records over 124 NAME records, histogram {0 x118,
-0 x1} (the lone -0 sits in ALIENDIP at file offset 0x51aa). Title-side
buttons INTRO/RESUME/EXITTODOS all 0. Re-pins §6.5: NO per-button sound id
exists in the shipped table; channel->sample stays the named seam (OQ-027b,
still OPEN — a census re-pins a negative, it closes nothing).

Three real defects found and fixed (all pinned, rewrite/tests/test_sound_t395.cpp):

1. AUDIO WAS OPT-IN ON THE UI PATH. main.cpp built the AudioEngine only when
   `--audio` was passed, so a plain `./ascendancy --ui` boot never opened a
   device AND never printed even the degrade line — on Athens indistinguishable
   from a dead sound card. LAW: on the --ui path audio is ON unless
   --no-audio; --headless/non-UI paths keep opt-in. Witness:
   scripts/t395_sound_witness.sh (no --audio flag) prints
   `audio: driver=dummy sfx=86 tunes=3 vol=127`.

2. play("click08") WAS A SILENT NO-OP SINCE t388. MEASURED: click08.voc
   EXISTS in ascend01/data but soundfx.txt (86 names) does NOT list it —
   the data dir holds samples the manifest does not name. init() now loads
   the referenced-but-unlisted click08 explicitly (chunks 85->86; gate 4d
   expects 86). The title-menu buttons play click08 symmetric with the
   campaign rail — DOCUMENTED PORT CHOICE per §6.5, never vendor law.

3. FAILURE LINES NAMED NOTHING. AudioEngine::triedPaths() records every
   path init() opened or probed; the degrade line appends
   `; last path tried: <p>`, and the missing-music error names BOTH archive
   layouts (ascend02/data/<t>.raw AND ascend01/data/<t>.raw) so "--data
   without extracted/" reads differently from a dead device. Silent-degrade
   unchanged: audio failure NEVER aborts boot.

Also: MENU-MUSIC ENTRY LAW made explicit — bootTune(Title)==0, every other
state kTuneNoChange(-2) (boot.h, pinned); the title loop requests it every
frame (idempotent via the playTune same-tune no-op). playTune hardened: any
t < -1 is a no-op (pre-fix, t=-2 indexed music_ out of bounds — UB).


### 6.7 t404 CLICK-SFX LAW (2026-11-15; D13 "clicking anywhere in the galaxy
map makes a laser-fire sound")

The t400-era map branch played laser01 on EVERY left click inside COSMOSWnd
(an early placeholder, ui.cpp:348 pre-fix). §6.5/§6.6 already established the
shipped windows.txt SOUNDCHANNEL column {0 x118, -0 x1} carries NO per-button
sound id, so laser01-on-click was never vendor-flavoured — and laser01 is a
combat sample (soundfx.txt name index 2; span 45277 = band2/1-voice per the
§2 header-pair census) while the port has no fire-order interaction at all.

LAW (rewrite/src/ui/audio.h/.cpp, pinned test_sfxpress_t404.cpp x5): every
sound the UI plays resolves through ONE pure lookup, so silence is pinnable
and no call site may hand-play a literal:
  sfxForPress: MapClick -> nullptr (SILENT — no cited sample, no combat UI);
    RailButton/NextTurn/TitleButton -> "click08" (documented port choice,
    §6.5; owner D11 heard and accepted the click sound). Rail presses gained
    click08 this iteration — symmetric with title/next-turn.
  sfxForEvent: event text containing "captured" -> "bang01" (§5 pairing),
    everything else silent.
  Out-of-range enum -> nullptr (same defensive shape as t395 playTune).
Witness scripts/t404_sfx_witness.sh (Xvfb + --audio-trace, SDL dummy driver):
map click logs zero sfx, rail press logs click08 before its switch line,
next-turn logs click08 after its marker, laser01 zero times — VERDICT PASS.
MUTATION 6/6 CAUGHT (scripts/t404_mutate.py, revert by FILE COPY from
/tmp/t404-snap — land was uncommitted, skill rule 1): M1 map=laser01,
M2 rail silent, M3 out-of-range->bang01, M4 "captured" typo, M5 inverted
event gate, M6 call-site placeholder re-added. Pin lesson banked in the test
file: CHECK(std_string(f())=="x") CRASHES the suite (std::string(nullptr) UB)
when a mutant makes a site silent — use the null-safe streq() helper so
silent mutants fail with named lines (M2/M4/M5 first ran rc-crash "?").
STATUS: laser01 now plays NOWHERE in the rewrite; it returns with a cited
fire-order interaction (combat UI), not before. OQ-027b (channel->sample
mapping) stays OPEN — this row removed a placeholder, it measured nothing
new about the vendor's per-button choice.


### 6.8 t429 — WHAT +0x1bcc ACTUALLY IS: batfx.txt GIZMO-FX TABLE, NOT A
CONTROL-RECORD SFX FIELD (premise correction; OQ-027b narrowed, stays OPEN)

The OQ-027b closure bar ("capture diff of control-record +0x1bcc across control
classes") rests on a FALSE PREMISE, measured this iteration over
work/ascend_payload.bin (imagebase 0, OQ-008 law) with the full call-site census
of the play path plus its loader. Working log docs/re/_wip_t429.md.

1. FUN_000500e0(param_1=audio object handle 0x78638, param_2=MANIFEST INDEX) —
   the index selects names at [obj+0x702 + 10i] (count [obj+0x700]) played as
   "data\%s.voc" (work/coswnd_decomp/500e0.c:26-48). Index <0 or >= count ->
   FUN_0002a428 vendor error; guards [obj+0x213]==-1 / [obj+0x20b]==0 return
   silently. THEREFORE the vendor's entire SFX id-space is the 86-name
   soundfx.txt manifest. button01/button02/click08 exist in ascend01/data but are
   OFF-manifest (t395 measured click08; the manifest list is banked in
   _wip_t429.md) — the vendor cannot play them through this path BY CONSTRUCTION.

2. The two cited sites read the HIWORD of a dword in a 4-byte-stride table:
   0x17439 `lea ebx,[ecx+eax]` with eax = 4*(key charcode), then
   `mov edx,[ebx+0x1bcc]; sar edx,0x10; mov eax,0x78638; call 0x500e0`
   (0x1747a..0x17488) and the +0x1bce twin (0x1748d..0x1749b). The index is the
   KEY CHARACTER, and the enclosing function (starts 0x17224 region, handler
   0x1af00 dispatches on `cmp dx,0x3a/0x4c/0x52/0x53/0x54...`) is a KEYBOARD
   handler in batmode.cpp — mouse clicks on rail/NEXTTURN buttons never reach it.

3. LOADER LAW (0x1acd0..0x1aef6, strings "batfx.txt" @0x82f6d + fmts "%d"
   @0x82f86 / "%s" @0x82f98 / "%d %d %d %d" @0x82f9b, all four referenced ONLY
   inside this function): open batfx.txt; sscanf "%d" -> count [obj+0x1a8e]
   (bounds >0x64 -> error ..\batmode.cpp); loop: sscanf "%s" -> 0x1fe20 -> u16
   [obj+0x19c6+2i] (the key char); loop: sscanf "%d %d %d %d" -> the LOW u16 of
   each of the four columns written to [obj+0x1a92], [obj+0x1a94], [obj+0x1bce],
   [obj+0x1bcc] per entry (ebx steps +4; 0x1aeb2/0x1aec7/0x1aed8 field order
   MEASURED). So +0x1bcc/+0x1bce = batfx.txt COLUMNS 3/4 = sfx1/sfx2 for the
   GIZMO fired by that key. batfx.txt is self-documenting ("shape1 shape2 sfx1
   sfx2", "sfx #s refer to list in soundfx.txt"); 79 four-int lines, entry i
   keyed by charcode i (i=32 ' ' Laneblocker sfx1=46 sg62bull; i=72 'H'
   SelfDestruct sfx1=82 SM72EXPL; i=74 'J' MassCondensor 84 ST74BULL / 34
   sg33bull). windows.txt SOUNDCHANNEL NEVER FEEDS THIS TABLE — the t395 census
   {0 x118, -0 x1} is about a different field entirely.

4. FULL PLAY-PATH CENSUS (32 call sites of wrapper 0x4fb30(obj,id) + the 2 cited
   direct calls to 0x500e0 = 34 sites; every site loads eax=0x78638;
   breakdown 13+1+1+8+6+1+2 = 32 (verified byte-exact per-site scan; the 2
   remaining 'computed' sites 0x17eca movsx edx,di / 0x180c3 are counted in
   the imm/computed bucket — see _wip_t429 T429-C):
   - 13 sites read the batfx table `mov edx,[reg+0x1bcc(+idx*4)]`
     (0x17b02, 0x17d37, 0x184e4, 0x189dd, 0x18e50, 0x18f91, 0x1913d, 0x1928b,
     0x195a3, 0x198d3, 0x19ca3, 0x19dab, 0x19f6a) — battle-mode gizmo fire
     keys; plus 2 batfx-adjacent variants: 0x1a1bd reads a FRAME COPY of the
     entry (`mov edx,[esp+0x1ba]` after a 0x1ce1c bounds check) and 0x1853d
     reads the +0x1bce twin via wrapper; plus the 2 direct-call table reads
     above = 17 table-driven sites total.
   - 8 sites pass IMMEDIATE 0 = manifest[0] "button" (re-count MEASURED,
     byte-exact `31 d2` before the call, eax=0x78638 at all 8):
     0x1b0b0/0x1b1c5 (both
     inside rectangle hit-tests `cmp ecx,[ebp+0xc]/[ebp+0x14]`, 0x1b097..0x1b0a3
     MEASURED), 0x27e46 (same rect pattern at 0x27e2d..0x27e39), 0x47e09 (after
     a 0x46d3c test on handle 0x74744), 0x529f9/0x52a5b (message-id ranges
     0x145..0x1d8 / 0x1a4..0x1d8), 0x549f9. THE VENDOR DOES PLAY A CLICK SOUND,
     and where it is cited it is manifest index 0 = "button.voc" (3,340 B,
     md5 cef40f13a210357d8d9379d52a5ab484).
   - 6 sites read a per-OBJECT sfx field: `mov edx,[obj+0x57]; sar edx,0x10;
     cmp edx,-1; je skip` (0x30e75, 0x3220f, 0x3336f, 0x3af9e, 0x4e453, 0x4e512)
     — record field +0x57 HIWORD, -1 = silent, i.e. per-unit/per-gizmo sound
     identity lives on the RECORD, not on a control table.
   - 0x1791c `mov edx,7` = manifest[7] "trust01"; 0x17ecf/0x180c8 computed.

VERDICT FOR OQ-027b: the row's question ("which sample per button press") is
now NARROWED, not closed. Cited: click branches play "button" (manifest 0), and
the strategic-UI rail cannot use the batfx table. UNMEASURED: which of the
id-0 sites (or a +0x57 record field) covers the strategic map's rail/NEXTTURN
presses — the enclosing modules of 0x27e4b/0x47e0e/0x549fe are unidentified
(no .cpp literal inside those bodies; functions_full.tsv rows there are 1734-byte
blobs, so tsv attribution is unusable). NO rewrite change this iteration:
sfxForPress stays click08 as a DOCUMENTED PORT CHOICE (§6.5/§6.7), because
promoting it to "button" for rail/next-turn without a cited strategic-UI site
would be exactly the plausible-default move strict-close forbids. The port's
click08 divergence is now quantified: the vendor's only reachable click sample
is "button", so a fidelity swap is a one-line change once the strategic site is
identified (probe named in docs/OPEN-QUESTIONS.md OQ-027).

## 6.9 t437 SOUNDCHANNEL -> record+0x59 LAW: the strategic press sound is
## manifest[0] "button" (CLOSES the (b) half's question; trail _wip_t437.md)

The t429 residue ("which id-0/+0x57 site covers the strategic rail/NEXTTURN
press, and does windows.txt SOUNDCHANNEL write +0x57") is ANSWERED by static
disasm + save-corpus census, zero capture:

1. STORE. Parser fn 0x575e4 scan sequence (fmt '%s %d' each), pinned by the
   rect stores X0/Y0/X1/Y1 -> +8/+0xc/+0x10/+0x14 in windows.txt file order:
   ... Y1 -> SHAPEFRAME (+0x1e word) -> SOUNDCHANNEL -> SENDMESSAGE (+0x45)
   -> SENDPARAM1 (+0x4b) -> SENDPARAM2 (+0x4f) -> WINITEMS (+0x6d).
   The SOUNDCHANNEL scan's store is 0x57e7a `mov WORD [edx+0x59],ax` — the
   u16 at record+0x59, i.e. the HIWORD of dword[record+0x57]. Byte-scan:
   inside the parser there is exactly ONE write to any disp in 0x55..0x5c
   (0x57e7b; caveat banked: modrm rm=5 mod=01 is EBP+disp32 STACK, not a
   record +0x5d — naive disp8 scans over-count).
2. READ. Strategic press handler 0x30c9c..0x30edb (record base esi): rect
   hit-test over [esi+8/+0xc/+0x10/+0x14], then 0x30e65 `mov edx,[esi+0x57];
   sar edx,0x10; cmp edx,-1; je skip` -> 0x4fb30(eax=0x78638) -> FUN_000500e0
   manifest play; then dispatches [esi+0x45]/[esi+0x4b] into strategic control
   pool 0x7a35c (call 0x56ad4). Same record shape the parser writes (handle
   [esi+0x41] used at 0x30d79..0x30dad exactly as the parser uses [ebp+0x41]).
3. VALUE. File census: SOUNDCHANNEL is 0 on all 119 lines (the lone "-0" in
   ALIENDIP scans to 0). Live census scripts/t437_soundchannel_store_census.py
   over 20 saves: 2,480 named window records; +0x59 distribution {0: 2400,
   0xffff: 80}; the 80 are COSMOSWnd/BatModeWnd/INTROFLIC/WMGRDEBUG x 20 —
   the four runtime-created windows with NO windows.txt TYPE block. Every
   file-declared window (NEXTTURN, NEXTTURNCONT, TOG*, RESEARCH, FLEET,
   STATUS, GALAXY_MORE, PLANLIST, RESWIN, ALIENDIP, title buttons, ...) is 0
   in 20/20 saves, zero mismatch.
4. IDENTITY. soundfx.txt manifest[0] == "button" (line 5 after count 86).

LAW (measured): the vendor plays soundfx manifest[0] "button.voc" on a press
of ANY file-declared strategic window, and NOTHING (-1) on COSMOSWnd,
BatModeWnd, INTROFLIC, WMGRDEBUG. There is no per-button vendor id for the
strategic UI (per-key ids exist only in batfx.txt, t429). The t429 id-0
immediate sites and these +0x57 sites agree: both resolve to "button".

PORT UPGRADE (this commit): sfxForPress RailButton/NextTurn/TitleButton
"click08" -> "button" (click08 is off-manifest, t395 — the vendor cannot play
it; the trace line made silence audible-proof only in the wiring sense).
MapClick stays nullptr, now CITED (COSMOSWnd +0x59 == -1, 20/20 saves).
Pins: sfx_press_buttons_button_t437 (rewritten from the t404 click08 pin);
witnesses t404_sfx_witness.sh + t395_sound_witness.sh expectations updated
to "sfx button", both VERDICT PASS live (SDL_AUDIODRIVER=dummy --audio-trace).
The audio_click08_offmanifest_t395 pin stays (click08.voc existence +
off-manifest status are still true facts; the explicit chunk load is kept so
any future deliberate use still resolves).
