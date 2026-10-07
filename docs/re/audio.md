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
