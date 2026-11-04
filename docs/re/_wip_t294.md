# t294 — word[+0x16] TEMPLATE SOURCE (OQ-016 residue 3) — RESOLVED: FILE TABLE

Session state: tree CLEAN at start (no orphan to adopt). Pure-STATIC iteration:
zero launches, production :9 ring read tail-only (58/59/60.sav, t1086).

## Scope correction (recorded before any probe)
STATE.md t294 text calls word[+0x16] "the ship-design word". WRONG DOMAIN:
word[+0x16] is the PLANET terrain weight-row index (planet record stride 0x7b,
stored @0x37e33 by world-gen FUN_00037d80; income-law.md S10). The ship-side
+0x16 in ships.md:1192 is the lane-visibility mask — different field. Worked
the ledger's own wording (OQ-016 residue 3): "word[+0x16] template source (the
11 weight rows: file table vs hardcoded)". Two sub-questions were conflated:
  (A) SOURCE OF THE 11 ROW VALUES at runtime 0x744f4 — file vs compiled-in.
  (B) SOURCE OF THE PER-PLANET INDEX word[+0x16] — file vs rng draw.

## ANSWER (A): FILE TABLE. Airtight, three legs + one elimination.
A1 [verified raw-asm this session, objdump -D -b binary -m i386 -M intel over
work/ascend_payload.bin] The fill loop inside scenario loader FUN_00037fc0,
payload 0x38011..0x38069, aligned decode:
    0x38003 LEA EAX,[ESP+0xC8] / PUSH EAX / PUSH 0x1CDD("%d") / PUSH ESI(handle)
    0x38011 MOV EBP,4
    0x38016 CALL 0x40021            ; fscanf(handle,"%d",&buf)  <- first int
    0x38023 MOV EAX,[ESP+0xC8] / 0x3802c MOV DS:0x66e4,EAX   ; POP-GROWTH SCALAR
    0x3801e MOV ECX,0x1CE0          ; record/format id for the weight rows
    0x3802a XOR EDI,EDI             ; edi = row counter
    outer (0x3803c): EDX = edi*4 ; EBX = ebp
      inner (0x38045): PUSH buf/ECX/ESI; CALL 0x3ffc3 ("%d" read); ADD ESP,0xC
                       INC EDX ; AL=[ESP+0xC8]
                       0x3805f MOV BYTE [EDX+0x744f3],AL   ; = 0x744f4 + edi*4+n
                       CMP EDX,EBX / JNE inner              ; 4 slots per row
    0x38033 tail: INC EDI / ADD EBP,4 / CMP EDI,0xB / JGE 0x3806b
  => 11 rows x 4 slots, ROW-MAJOR, 44 bytes into 0x744f4..0x744fb. (My first
  pass read this as "w0 slot only" — WRONG, corrected here: the inner loop
  writes all four w-slots; ebp is the running row-end bound 4*(row+1).)
A2 [verified BSS elimination] work/ascend_payload.bin is 0x8cc83 bytes and the
  obj1 DATA segment maps at payload 0x82bb0 <-> data-address 0, so the file
  initialises data addresses only up to 0xa0d3. 0x744f4 > 0xa0d3, therefore the
  weight table is UNINITIALISED DATA (BSS): the EXE carries no values for it.
  Reading payload 0x82bb0+0x744f4 = 0xf70a4 is past EOF (empty read, verified).
A3 [verified write census, SIB-aware] Image-wide scan for every store form
  (88/C6/89/C7, 66-prefix included, mod=10 disp32, SIB handled) with disp32 in
  [0x744f0,0x74520): EXACTLY ONE hit — 0x3805f, the loader store above. No
  second writer, no memcpy-from-immediate. Combined with A2 this makes the file
  the ONLY possible source of the live values.
A4 [verified value match, three corpora] planitem.txt (scratch copy
  work/r1/game/planitem.txt, md5 7e77b10c84c563fa91d56a0f9353a03f) block after
  the lone '#' delimiter: pop-growth scalar "50" at file offset 0x1c7, then the
  11x4 weight block at 0x1d1..0x269. Parsed rows:
    [100,0,0,0] [50,2,2,2] [20,3,5,3] [0,3,20,3] [40,10,2,2] [20,20,2,2]
    [40,2,2,10] [20,3,3,20] [40,10,10,10] [20,15,15,15] [0,33,34,33]
  == banked runtime table (income-law S10, 13 captures) EXACTLY (programmatic
  compare True) == LIVE PRODUCTION RAM read this session from playcap
  58.sav/59.sav/60.sav at B=0x1bf4d8, member index B+0x82bb0+0x744f4, 44/44
  bytes equal on all three saves (pointer law).
  Note why earlier hunts missed it: the values are ASCII DECIMAL TEXT in the
  file, so packed-byte signature search (t54b's method, and my first sweep
  this session) returns zero hits BY CONSTRUCTION. t54b's "EXE constants, file
  route REFUTED" verdict was about the OTHER pair of tables (0x88f90/0x88fe4,
  21 dwords each) and does not cover 0x744f4 — no contradiction, but the
  doc boundary must be stated so nobody re-refutes this row from t54b.

## ANSWER (B): THE INDEX IS AN rng DRAW, NOT FILE DATA (banked law stands)
  0x37e2e CMP EAX,0xB / 0x37e31 JGE -> 0x37e39 MOV WORD [ESI+0x16],2 (clamp);
  0x37e33 MOV WORD [ESI+0x16],AX (else store arg). Arg arrives from the
  scenario-init call site: second draw `CALL 0x7824f; IDIV 11` @0x23a97..0x23aa8
  (T54b verbatim asm), passed through @0x23b14..0x23b49 into FUN_00037d80.
  So: per-planet row = fresh uniform rng%11 at new-game; the FILE supplies the
  row CONTENTS. Consistent with retracted-R11 (save-time +0x16 IS the
  generation row; barren% tracks w0 monotonically, row0 -> 99.3%).

## BONUS 1 [verified]: pop-growth scalar has a cited home
  First post-'#' integer of planitem.txt (value 50) -> DS:0x66e4 @0x3802c.
  Matches the file's own vendor comment line 23 ("first, note we have pop
  growth amount number"). The income-law "counter-50" constant now has a
  source-of-values citation, not just a consumer citation.

## BONUS 2 [verified]: the surface-cell table's PER-BYTE split (OQ-014 "grid C")
  campaign.cpp:147-151 carried {7,11,23,45,73} as SUMS ONLY ("per-byte split
  not observed"). It IS in the file: planitem.txt grid C (docs' name, OQ-014) =
  5 rows x 15 ints, the THIRD numeric block after '#' (order: weights, grid B,
  grid C), loaded to 0x744a8 by the sibling loop 0x380ad..0x380ed (record
  0x1ce6). Aligned decode of that loop: EDX=15i, INC-then-store at
  [EDX+0x744a7], stop when EDX==EBP=15(i+1) INCLUSIVE -> 15 stores landing
  0x744a8+15i..+15i+14, i.e. the full 15-value row verbatim (same INC-first
  law as the weight loop: stores 4i+1..4(i+1) -> 0x744f4+4i..+4i+3, all four
  weights).
  File grid C rows sum to 7/11/23/45/73 EXACTLY (programmatic check), and live
  RAM 0x744a8 read this session (58/59/60.sav) gives the same sums.
  Sibling grid B -> base 0x7445b, rows land at 0x7445c+15i (record 0x1ce3,
  0x38070..0x380a9). DS:0x74458 dword is the -1 "tables loaded" sentinel
  banked in T30b (live bytes 0x74458..5b = 255,255,255,255 re-confirmed in the
  same read; note T30b said sentinel==-1 triggers the load — live mid-campaign
  shows -1 too, so the sentinel semantics are NOT re-derived here, only its
  adjacency). Grid B content is NOT consumed by the rewrite; left unmapped.

## REWRITE UPGRADE (LANDED)
  campaign.cpp:142-146 hardcodes kRows[11]. Values are stock-identical, so this
  is NOT a value change — it is lifting the table to its true source so a
  modded planitem.txt drives generation the way the original does. Plan:
  economy.{h,cpp} loadTerrainTables() (weights 11x4 + grid B 5x15 + popGrowth),
  Campaign consumes it at scenario init, vendor array stays as the
  documented no-data fallback; pin campaign_terrain_weight_table_oq016_t294
  with a DIFFERENTIAL leg (patched file -> generation follows the patch) so the
  test proves consumption, not just parsing.
