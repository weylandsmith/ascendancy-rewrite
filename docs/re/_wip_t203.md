# t203 — FREE-TECH GRANT ON BUILD COMPLETION (gap row 7) — WIP

Image: work/ascend_restored.bin (base-0, OQ-008/OQ-011 law). Capstone via
~/tools/revenv/bin/python (.venv has NO capstone — use revenv).

## S1. FUN_00046e84 verbatim (0x46e84..0x46f9d, disasm this session) [verified]
Signature: EAX = restree runtime base (caller passes 0x74744), DL = race index
(0x39170 `mov dl,[esi+0x57]` planet owner). EBX clobbered/saved at [esp+0xc8],
race kept as WORD at [esp+0xcc]; frame sub esp,0xd0; candidate array at
[esp+0..] (u16 x n, cap 0x20 implicit by caller semantics).

Order of operations:
1. 0x46ea1 ASSERT GUARD: `edx = DAT_00013b96; sar edx,0x10; if (raceword <
   (short)(DAT_00013b96>>16)) { ebx=0x12d(301); edx=0x8504f; call 0x2a428 }`
   — debug/error handler when race < some threshold (identity of
   DAT_00013b96>>16 TBD; string image-offset 0x8504f TBD).
2. CANDIDATE LOOP 0x46ec7..0x46f1a, stride 0x4b (75 = runtime restree stride),
   row index eax 0..N-1 bounded by `eax < word[esi]` (row-count word at restree
   header +0 — same 66-count law as OQ-013). For each row R skip (0x46ecf) iff:
   a. R == DAT_00076492[race]  (0x46ee6 `mov cx,[esi+race*2+0x1d4e]`;
      0x74744+0x1d4e == 0x76492 == the per-race research TARGET word, t91
      field identity) — the target row is NEVER a grant candidate;
   b. owned: `([row+0x47] >> 0x18) & (1<<race)` nonzero (0x46eff..0x46f0e).
   Else store R into cand[n++] (0x46f16).
   NO prereq/legality call (contrast FUN_00040018 which calls 0x46d3c) — the
   free-tech grant ignores the prereq chain entirely. [verified by absence:
   no call in the loop; sole call in function is 0x7824f + conditional 0x2a428]
3. EMPTY GUARD 0x46f1c: `test dx,dx; je exit` (n==0 -> return, no grant).
4. UNIFORM PICK 0x46f23: `call 0x7824f` (RNG; eax = random 32-bit) ->
   `edx = eax; sar edx,0x1f; idiv ecx(ecx=n)` -> signed remainder edx
   (negative rng -> negative remainder -> candidate index [esp+edx*2] reads
   BELOW the array = UB quirk of the original; banked not modelled) ->
   chosen = cand[edx]. NO preferred list, NO sentinel — pure uniform.
5. GRANT 0x46f38..0x46f64: rowbase = base + chosen*(5*16) == base + chosen*75;
   `al = 1 << race; ah = [row+0x4a] | al; dl = [row+0x4b] | al; store both`
   — sets the race bit in BOTH owned-mask bytes +0x4a/+0x4b.
   NEVER touches DAT_00076492[target] (confirmed: sole +0x1d4e ref in the
   function is the candidate-loop READ 0x46ee6). [verified]
6. ANNOUNCE 0x46f67..0x46f92: `if (race == DAT_0007458e)` (the human-player
   race byte) -> `call 0x55a60` with eax=0x7a35c, ebx=EDI (leftover caller
   reg — at 0x39173 caller EDI was set 0xffffffff in the sibling block
   0x39135-preceding path; NOT locally initialised in 0x46e84 = original quirk),
   ecx=0, edx=0 -> event post (t202b: code-0 event; ai-dossier earlier read
   "code 0x16" came from a different reg assumption — flag as CORRECTED
   pending string decode of the event name; cosmetic UI/event only).
7. 0x46f93 epilogue: add esp,0xd0; pop ebp/edi/esi/ecx; ret.

## S2. Caller 0x39173 (build-completion engine, inside 0x390a3.. tail) [verified]
Completion sequence context (ESI = build-record; +0x10 item-table base ptr,
+0x52 item index word, +0x54 item type byte, +0x57 owner race byte, +0x50
progress/cost words @+0x50/+0x44):
- 0x3909f/0x390a3: progress += cost; call 0x394d8; 0x390ac `cmp ax,[esi+0x50];
  ja` -> not complete yet exits (0x392a2).
- 0x390fc block: player-only event (item 0x17 etc.) — separate.
- 0x3913b THE GRANT GATE: `dl = byte[[esi+0x10] + item*4 + 1] & 8` — that is
  planitem FLAGS bit 8 (record stride 0x28? no: runtime stride 4/dword view,
  byte+1 == FLAGS low byte, OQ-014 field map). If bit8 == 0 -> jump 0x3917e
  (NO grant): `or byte[[esi+0x10]+item*4+2], 1`.
  If bit8 != 0: clear it (`and [eax],0xf7`), set slot byte+1 = 0xff (free),
  then 0x39173 `call 0x46e84` with eax=0x74744, dl=owner race.
- => THE GRANT IS NOT "every completion": it fires ONLY when the completed
  item's FLAGS bit 8 is set (one-shot flag consumed on grant). ai-dossier §3c
  "build completion can grant a free tech" understates the gate. [verified]

## S3. GATE SEMANTICS RESOLVED — the grant is the XENO DIG completion law [verified]
Gate is ITEM-BLIND and RACE-BLIND: every build completion runs 0x3913b; the
branch key is the COMPLETING CELL's rock bit, and item 38 is simply the only
item placement law ever allows on a rock cell. Dig completing on a NON-rock
cell takes 0x3917a (`or word+2, 1` = normal ACTIVE activation): dig persists
as a built item, NO grant, no rock clear.
- Slot byte0 bit3 (0x8) == the rock/unbuildable cell marker: mapgen drawer
  0x37f77 `or byte [eax + edx*4], 8` (rock draw in planet gen, inside the
  gen function that also writes terrain classes 0x37eec and the +0x55 =
  ecx/3+5 pop law 0x37f97); raw hist byte0 classes 8..12 (23 slots fresh
  48.sav, income-law line 881); placement law (income-law §S-planner gate 4)
  "cell FLAG bit3 allowed ONLY for itemIdx 38 (Xeno Archeological Dig)".
- Caller tail re-read 0x3913b..0x3917a (this session, verbatim):
  eax = [rec+0x10] + [rec+0x52]*4 (the COMPLETING item's slot);
  if byte0 & 8: byte0 &= 0xF7 (rock cleared), byte1 := 0xFF (slot emptied —
  the dig CONSUMES ITSELF), then call 0x46e84(restree base 0x74744,
  dl = owner race [rec+0x57]); ELSE (no bit8): word+2 |= 1 (normal ACTIVE
  activation). Race-blind gate: fires for player AND AI; 0x46e84's event
  post is the only player-conditional part (0x46f77 cmp DAT_0007458e).
- Completion tail siblings confirm the item-special layout: 0x391bf item 36
  Terraforming, 0x391fe item 35 Automation (0x23), 0x39212 item 37 Lush
  Growth Bomb (0x25), 0x392a2 item 31 (0x1f) per-race dip delta — and NO
  `cmp 0x26` anywhere: item 38's ENTIRE completion effect IS the bit8 gate.
- THEREFORE THE LAW: when item 38 (Xeno Archeological Dig) completes in its
  rock cell: clear cell rock bit; empty the slot; grant ONE uniform-random
  tech to the owner: candidates = rows 0..65, EXCLUDING (a) the race's
  research target word DAT_00076492[race] (0x46ee6) and (b) rows already
  OWNED by the race ([row+0x47]>>24 & (1<<race)); NO prereq check (no
  legality call in 0x46e84 — dossier §3c "legal rows" over-stated,
  CORRECTED); pick rng%count (rng 0x7824f = 15-bit LCG, always >=0, no UB);
  set owned-mask bytes +0x4a/+0x4b |= 1<<race; NEVER writes the target word
  (sole +0x1d4e ref in 0x46e84 is the candidate-loop read). count==0 -> no
  grant, slot still emptied + rock still cleared (0x46f1c jumps to exit AFTER
  the 0x39156/0x39164 stores already ran — order: stores PRECEDE the call).
- AI free tech thus bypasses the prereq chain — it can unlock an arbitrary
  row including deep rows (cost irrelevant, owned bit only).

## S4. Census probes (this session) [verified]
- String image-offset 0x8504f == "..\\research.cpp" (raw bytes this session);
  0x2a428 = debug-assert handler (ebx=301 line, edx=file-str). The guard at
  0x46ea1 fires iff race < (short)(DAT_00013b96>>16) — same guard shape appears
  in sibling FUN_00046de0 (0x46e0a, ebx=0x116) and 20+ other sites: it is the
  decompiler's bounds-assert idiom, NOT a game law. Model: skip.
- RNG 0x7824f: LCG state via FUN_00078249; `state = state*0x41c64e6d + 0x3039;
  return (state>>16) & 0x7fff` — 15-bit positive draw. So the idiv at 0x46f2b
  (`sar edx,0x1f; idiv ecx`) is ALWAYS non-negative: no UB. rng%count, plain.
- PLAYER GRANT IS DEAD CODE [verified]: gate 0x39141 `dl =
  byte[[rec+0x10] + cell*4 + 1]` is the SLOT's itemIdx byte (income-law §6g
  slot layout byte0 terrain/byte1 itemIdx/word+2 flags), NOT the item-table
  FLAGS. FLAG bit8 of the ITEM-TABLE is a different field (stride 0x28 +6).
  The caller reads the SLOT ARRAY byte1. Completion of item 0x24 (=36
  Terraforming, compared at 0x3917e) is exactly the item whose effect zeroes
  the slot — so the call fires when a terrain-changed cell COMPLETES with a
  non-0xFF itemIdx byte AND bit 8 of the cell terrain class set (byte0 & 8:
  class values 8..12 = special classes, t-something census line 881).
  RE-DERIVE needed: what cell classes have byte0 & 8 and hold built items.
  (Original semantics of byte0&8 NOT asserted; banked as probe target.)

