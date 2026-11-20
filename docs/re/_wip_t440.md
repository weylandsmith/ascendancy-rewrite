# t440 — OQ-027(a) TUNEID index base: tune-table read from a banked save

ADOPTION NOTE: a prior session was killed mid-task with docs/OPEN-QUESTIONS.md
edited, this file, and scripts/t440_music_table.py untracked. Its central claim
(TUNEID is 0-based, object statically addressable) is TRUE — re-verified
end-to-end below — but its draft contained THREE errors this rewrite fixes:
(1) it labelled the save-MEMBER offset 0x2baa3a a "payload file offset" (wrong
    coordinate system, see F4); (2) the script used stride 0xc and indexed
    mem[B+0x78638] — both wrong, the script returned a negative (RC=1) as left;
(3) it claimed the table is at "obj+0x37a (file 0x2baa3a)" implying file
    content — the region is RUNTIME-populated .bss, the payload bytes there are
    unrelated garbage (checked).

## F0 SITTING CHECK (mandatory pre-flight)
`python3 scripts/t368_ring_turn.py` 2026-11-20: parsed=20/20, max_turn=1086
min_turn=1086 == the t368 baseline. NO new sitting -> STATE.md assignment
stands (per the t439 law, live-timeline.jsonl byte growth is NOT the test).

## F1 STATIC LAW (objdump -b binary -D -m i386 -Mintel, work/ascend_payload.bin)
Verified instruction-for-instruction this session:

* Subtitle tick-loop type-word dispatch 0x2ee9e (`mov ax,[edx+0x206]`):
      ax==3 -> 0x2edf5 ; ax==0x1e (DIGITALMUSIC) -> 0x2ee3b ; ax==0x1f -> 0x2ee5c
      (stop) ; ax==0xb (FADEMUSIC) -> 0x2ee72 ; else "Bad Track Event" 0x2eec7.
  0x2ee3b = `b8 38 86 07 00` (mov eax,0x78638 — a FIXUP SLOT) `8b 92 08 02 00 00`
  (mov edx,[edx+0x208] = TUNEID) `0f bf d2` (movsx) `e8 1c 0a 02 00` (call 0x4f86c).
  => audio.md §6.1's "0x1e -> 0x2edf5 -> FUN_000678ec(handle,TUNEID)" is WRONG:
  0x2edf5 is the ax==3 branch. FUN_00074a88 (the [handle+0x8868] setter, verified
  at 0x74a99) is a PIT/timer-slot path (0x74307 scans static 0x87e8/0x8868 slots,
  0x742d4 -> 0x742a4 out 0x43/0x40 = 8253 PIT) that the DIGITALMUSIC cue NEVER
  calls. The §6.1 closure-bar premise ("tune table heap-relative via
  [handle+0x8868]") describes the wrong subsystem entirely.

* FUN_0004f86c (the REAL consumer, esi=audio object, edi=TUNEID), verified:
      0x4f87a cmp [esi+0x22b],-1 / 0x4f883 cmp [esi+0x20b],0 -> no-device guard
      0x4f896 test eax,eax / 0x4f89a cmp di,WORD [esi+0x6fa] -> range check,
              error 0x2963 if tuneid<0 or tuneid>=WORD[+0x6fa]
      0x4f929 movsx edx,di ; 0x4f92c lea eax,[edx*8] ; 0x4f933 sub eax,edx ;
      0x4f93a shl eax,2        => eax = tuneid*28   (NO -1, NO bias)
      0x4f93d lea edx,[esi+0x37a] ; 0x4f945 add edx,eax
              => NAME = obj + 0x37a + tuneid*28, ZERO-BASED
      0x4f947 lea eax,[esi+0x240] ; 0x4f94d call 0x207ac (name lookup in the
              loaded container — NOT a DOS open)
      0x4f9aa mov WORD [esi+0x6fc],di  (current tune id, same index space)

## F4 THE SAVE WITNESS — TUNEID IS ZERO-BASED (CLOSED)
Banked save work/r1/bank-t438-ring-2200/60.sav (zip member "Memory", H=0x88,
B=0x1bf4d8, P0=0x1bf450). COORDINATE LAW USED (banked F5): a guest LINEAR
address L lives at Memory-member offset L + H. (NOT B+file-offset — that form
is for payload CONTENT; the audio object is .bss beyond the payload.)

1. The dispatch site IN THE SAVE reads `b8 38 a6 2b 00` (found by scanning the
   member for `8b 92 08 02 00 00` and taking the preceding mov-eax imm):
   runtime fixup value 0x2ba638 = the audio object's guest linear.
2. Member[0x2ba638+0x88+0x37a ..] decodes as a 29-entry pitch-28 ASCII table,
   IN music.txt ORDER (29/29 verbatim): [0] data\theme00.raw ... [5] victory,
   [6] data\intro00.raw, [7] data\intro01.raw, [8..28] race00..race20.
3. WORD[obj+0x6fa] = 29 = 0x1d == the 0x4f89a bound == the entry count.
4. CENSUS 20/20 saves 41..60: identical object linear 0x2ba638, count 29,
   entry[6]=intro00, entry[7]=intro01 (scripts/t440_music_table.py, RC=0).
   WORD[obj+0x6fc] (current tune) reads 2..4 across the slots — plausible
   mid-cycle values of theme00..04 in the SAME 0-based space (1-based would
   make 2=theme01; the in-game set is the first-five menu band either way, so
   this is corroboration, not proof — proof is 2+3).

CONCLUSION (measured, cited): DIGITALMUSIC TUNEID 6 names data\intro00.raw,
TUNEID 7 names data\intro01.raw; TUNEID is a ZERO-BASED index into the 29-entry
music.txt-order table. REFUTED: any 1-based reading (theme00=1 -> 6=victory) and
the older docs' warning that "0-based would loop intro01, 7=race00" (muddled
arithmetic — 0-based IS the measured scheme and gives 6=intro00). The port's
OUTCOME (6->intro00, 7->intro01) was already correct.
The row's closure bar ("a capture read of the ... tune table") is MET by a
banked-save read; the bar's word "heap" carried the refuted §6.1 premise.

## F5 METHOD LAWS
* BEFORE arming a debugger on a live game, ask whether the target is (i) named
  by a fixup-addressed instruction operand and (ii) resident in a banked save.
  Both true here -> zero live risk, zero BREAK lottery, zero nosound-vacuity
  exposure. The INT 21h AH=3D route stays valid but is second choice.
* SAVE COORDINATES: Memory-member offset = guest linear + H. B+P0+file-offset
  is only for payload content. A .bss global (e.g. audio obj 0x2ba638 =
  data-seg-base 0x242000 + 0x78638, payload is only 0x8cc83 B) exists ONLY in
  a save, never in the payload file — do not grep the payload for it.
* Self-locating save probe pattern: scan the member for a stable instruction
  tail (`8b 92 08 02 00 00` here) and read the fixup immediate preceding it —
  run-independent, no base math.

## F6 PORT SIDE — no base change needed; three comments corrected
trackNames() = {theme00, intro00, intro01} is the port's OWN loaded subset; the
cue table ui.cpp:2633/:2639 translates vendor TUNEID 6->idx1 (intro00), 7->idx2
(intro01) — the translation OUTCOME was already correct, only its stated
justification ("1-based music.txt reading") was wrong. Corrected to the measured
0-based law in audio.cpp, ui.h, ui.cpp. Pin audio_tuneid_zero_based_t440:
music.txt 0-based indices (intro00==6, intro01==7, count 29) x trackNames
order — a silent re-base or swap of either side fails it.

## F7 LEDGER
OQ-027 CLOSED (item (b) t437 measurement + code-site; item (a) t440 capture
read above). ledger_audit --expect updated to OQ-019,OQ-016; STATE index
re-derived. R-t440 written to REFUTED-ROUTES.md ("heap-relative/not statically
decidable" class for this object + the §6.1 dispatch claim).
