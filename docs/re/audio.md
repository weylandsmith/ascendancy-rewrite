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
