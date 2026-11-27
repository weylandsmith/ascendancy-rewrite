# tESC-1 WIP — RE-DERIVE THE VENDOR ESCAPE CHAIN AT BYTES (D31)

Task (docs/STATE.md NEXT ACTION 2026-11-27): Escape from the galaxy map
should return to the MAIN/TITLE screen per user law D31; the t410
"quit at bottom" citation is CONTESTED. Re-derive from handler asm what
Escape pops at the bottom level: process exit or boot-to-title. Cite FUNs.
If vendor unwinds to title -> ship exactly that + pin. If vendor asm
genuinely quits the process -> DO NOT silently keep it; write the cited asm
excerpt here and leave OPEN for the user's ruling.

## P1 — WHAT THE CONTESTED CITATION ACTUALLY IS [verified by re-read]
- docs/re/_wip_t410.md L106-110: "ESCAPE CHAIN: ONE level per press
  [verified t252 pixel-diff ...]; 1 -> 16 -> 17: Esc 17->16, Esc 16->1,
  Esc 1 = standing quit." The bottom-level leg is labelled "STANDING" —
  i.e. it inherits the port's pre-existing ui.cpp behaviour, NOT a vendor
  asm citation. docs/re/ui-runtime.md L439: "ESCAPE: inside a screen ->
  map (t252 live); on the map -> quit (standing)." Same: only the
  inside-screen->map leg was ever live-verified; the map->quit leg was a
  PORT DEFAULT carried forward.
- So D31 vs t410 is user-law vs PORT-default, not user-law vs vendor-law.
  The "citation CONTESTED" framing in the assignment overstates what t410
  claimed.

## P2 — THE t285 LIVE WITNESS ALREADY ANSWERS THE QUESTION [verified]
- docs/REFUTED-ROUTES.md §t285 (witnessed 2026-11-03 04:38, screenshots +
  saves banked work/r1/bank-t285-flip1255/): "one Escape at the bare
  campaign map ejects to the TITLE MENU while autosave keeps writing the
  RAM campaign — in_game stays True".
- Meaning: IN THE VENDOR, Escape at the galaxy map level does NOT exit the
  process — it boots the title menu overlay while the campaign stays live
  in RAM (corroborated by R-t439: title "Return to Current Game" returned
  turn 1086 after exactly such an ejection). The user's D31 memory is
  CORROBORATED by an existing pixel-measured capture; the port's
  process-exit leg is the deviation.

## P3 — BYTE-LEVEL RE-DERIVATION OF THE ESC HOTKEY [measured this iteration]
Harness: objdump -b binary -m i386 -M intel over work/ascend_payload.bin
(pre-fixup image, imagebase 0, OQ-008 law). Byte census first: the ONLY
`cmp ebx,0x1b` in the whole 576643-byte image is 0x576d8 (inside fn
0x575e4, a windows.txt PARSER — 0x1b there is a record-count bound, not a
key). ESC is keyed by SCAN CODE 1, not char 0x1b, in the hotkey dispatcher.

- fn 0x54d18 = THE HOTKEY DISPATCHER (known since t337 S104 / t429), keyed
  on WORD ds:0x484c4 (the MSG/scan-code word; writers 0x2a72a INT16h
  AH=0 -> scan, 0x2a91d DOSBox record+0xc; t346 S1). Tree at
  0x54faf: `cmp ax,1 / jb 0x54ead / jbe 0x54e96` — SCAN CODE 1 (ESC) is a
  HANDLED key with its own arm at 0x54e96.
- ESC ARM 0x54e96 (verbatim):
    54e96  cmp  DWORD [ecx+0x489e],0x0
    54e9d  jne  0x54ecb            ; modal open -> just clear it
    54e9f  mov  eax,[ecx+0x4226]   sar eax,0x10
    54ea8  cmp  eax,0x11           ; state 0x11 -> ESC inert
    54eab  jne  0x54eb7
    54ead  mov  eax,0xffffffff     ret          ; (inert path)
    54eb7  mov  edx,0xffffffff ; mov eax,ecx
    54ebe  call 0x57020                          ; POP THE SCREEN STACK
    54ec3  mov  eax,0 ; ret
    54ecb  mov  DWORD [ecx+0x489e],0 ; mov DWORD [ecx+0x48a2],0 ; ret
  => PRECEDENCE: modal flag [obj+0x489e] first (t409 modal-precedence law,
  now cited at bytes), else POP ONE via FUN_00057020(obj, -1).
- FUN_00057020 = THE POP (verbatim, 0x57020..0x57092):
    57024  edx=[eax+0x4754] sar16; if ==0 -> return 0      ; gate
    57036  edx=[eax+0x4756] sar16; edx = (edx==0 ? 0xf : edx-1)
    5704e  cx = WORD [eax + edx*2 + 0x4736]                ; entry id
    57056  ebx==-1 branch:
      5705b  WORD [eax+0x4758] = dx                        ; last popped
      5706b  WORD [eax+edx*2+0x4736] = 0xffff              ; tombstone
      5707c  bx = WORD [eax+0x4756] - 1 ; [eax+0x4756]=bx   ; depth--
      57089  ebx=0; call 0x56e10                           ; repaint/enter
    5708e  return ecx (the id now on top)
  => SCREEN STACK = WORD array @obj+0x4736 (stride 2), DEPTH = HIWORD
  obj+0x4756, TOP-AFTER-POP = obj+0x4758. t410's ScreenStack model is
  CONFIRMED at bytes (pop = tombstone 0xffff + depth--).
- CALLERS of the pop 0x57020: 0x54ebe (this ESC arm), 0x54a1c (fn 0x54650,
  the input pump), 0x55eb4 (fn 0x55df4). CALLERS of the enter/repaint
  0x56e10: 0x21733, 0x54d92/0x54dba (fn 0x54d18 hotkeys, ebx=-1 with
  edx=2/4), 0x55ea3, 0x57089.
- CRITICAL NEGATIVE: NEITHER the ESC arm NOR the pop contains any exit
  syscall, TerminateProcess, or "return from main" path. The deepest thing
  ESC does is decrement the stack depth and re-enter 0x56e10. There is NO
  "quit the process" leg in the vendor escape chain at all.

## P4 — THE POP GATE AT DEPTH 1 (what "bottom" means) [verified this iteration]
- FUN_00057020 gate 0x57024: `edx=[eax+0x4754] sar 16; if edx==0 return 0`.
  Depth HIWORD obj+0x4756 is decremented at 0x5707c; when the pop empties the
  stack the CALLER (ESC arm 0x54ebe) has already returned — the NEXT ESC at
  depth 0 hits the gate, the pop is a NO-OP, and ESC does literally nothing
  visible. There is no "bottom level exits" arm: the vendor's deepest
  observable behaviour at the map is the ejection that t285 measured, then
  inert keys on the title overlay.
- So "quit at bottom" was never a vendor leg; it is the port's pre-tESC-1
  process-exit default (see P1). D31 vs t410 resolved: USER LAW == VENDOR LAW,
  PORT was wrong.

## P5 — PORT SHIP [shipped + witnessed this iteration]
- ui.cpp: doEscape else-branch sets toTitle + quits the loop (cause named via
  the tPF-1d escCause param, so escape-key-at-bottom vs corner-exit-click stay
  distinguishable); 'ui to title' printed before 'ui ok'; exit path hands the
  window back via *windowOut ONLY on the eject leg (every other leg keeps the
  standing destroy discipline).
- ui.h: runCampaignUi gains bool* outToTitle + void** windowOut;
  runTitleScreen gains void* windowIn (reuse, t385 single-window law).
- title.cpp: windowIn reuse (SetWindowTitle, no create); the existing
  windowOut handoff already fires on BootState::Campaign exit.
- main.cpp: title<->campaign LOOP. newGame reset PER ENTRY (a stale Begin
  triple would rebuild — i.e. destroy — the live mid-game campaign on
  re-entry); re-entry ALWAYS lands on Title (vendor draws the title overlay;
  --resume players pick RESUME msg 1/1); witness line
  'main: campaign -> title (campaign alive turn N)'.
- RUNTIME WITNESS scripts/tESC1_eject_witness.sh (Xvfb :97, Begin-built
  50/5/1, per-leg greps per tPF-9 law) — ALL LEGS PASS:
  LEG1 one Escape at the bare map: cause line + 'ui to title' + main line,
       process STILL ALIVE (kill -0).
  LEG2 RESUME click (318,335) re-entered: 'ui title click RESUME -> campaign'
       — the click LANDED, confirming the reused window (t385: a swap eats
       the first synthetic click).
  LEG3 next-turn on the resumed campaign: 'ui click next-turn' (live object,
       not a rebuild).
  LEG4 second eject (count==2) then EXITTODOS click: process gone.
  (LEG2's first draft grepped 'ui title exit: campaign' — that line only
  prints when the title loop EXITS to campaign from main; the in-loop click
  line is 'ui title click RESUME -> campaign'. Fixed in the script.)
- SUITE: 605/0/0 after the change (no regression); pin
  test_toTitle_tESC1.cpp x3 added.

## P6 — OQ DISPOSITION
- No OPEN-QUESTIONS row covers the escape chain (open rows stay 016/019);
  t410's screen-stack model is CONFIRMED at bytes (P3), its bottom-level
  label corrected here. D31 needs NO user ruling: the citation question is
  answered in the user's favour by existing measurement + asm.
