# t304 — CALLER WITNESS + CENSUS AT THE TRUE DISPATCH SITE (WIP)

## S0. Task (STATE.md t304 assignment)
t303 REFUTED the slot-1 router law (cos_hdlr fired 15x with all five
`call [ecx+4]` sites armed+silent). Missing datum: WHICH instruction calls the
class msg handlers. Assigned PROBE: (1) cos_hdlr-only stop -> [esp] ret0 names
the caller EIP verbatim; (2) static read below ret0 for the call boundary;
(3) census at THAT site with close_eventwin between clicks + btn_hdlr armed.

## S1. STATIC PRE-READ (this session, work/ascend_payload.bin 0x8cc83, BEFORE
##     any guest run) — PRIME SUSPECT FOUND, and it is not in t303's armed set
Modrm law correction (t303's site list used the right encoding; my first scan
this session did not): CALL is group-1 /2, so `call [ecx+disp8]` = `ff 51 dd`
— verified against the 5 known ff5104 sites. Slot offsets are BYTES: slot0=+0,
slot1=+4, slot2=+8, slot3=0xc. cos_hdlr/btn_hdlr are SLOT 2 == +0x8.

Census of `call [reg+disp8]` for slot 2 (ff /2 mod=01, disp8=08):
```
call[eax+8] 0 | call[ecx+8] 0 | call[edx+8] 0
call[ebx+8] 1   -> 0x809fe
call[esi+8] 13  -> 0x15b0f 0x356a5 0x3afc3 0x3b38b 0x3b3a9 0x3b4e9 0x3b584
                   0x3b5be 0x3b607 0x553cb 0x553e5 0x55406 0x56cda
call[edi+8] 2   -> 0x4e2cb 0x54a83   (NOTE: pay.count() said 2, byte-context
                   print found 0 for edi — RE-VERIFY before interpreting)
```
=> ZERO `call [ecx+8]` exists. The slot-2 handler call NEVER goes through ecx,
which is why t303 armed a set that could not see it. The dominant form is
**esi = class table, `call [esi+8]`**.

13/13 esi-sites are preceded by a `mov esi,[reg+0xa7]` (8b b0/b6/ba a7 00 00
00) = the window-record class-table load, and most load edx with a small const
(0x32, 0x34, 0x33, 0x8, 0x1, 0x2) = MSG ID. Shape at the top candidate:
```
0x15b0f:  8d c4 00 00 00            lea    esp,[eax]
          8b 9d c0 00 00 00         mov    ebx,[ebp+0xc0]
          8b b0 a7 00 00 00         mov    esi,[eax+0xa7]   ; CLASS TABLE
          c1 fb 18                  sar    ebx,0x18         ; MSG ID
          ff 56 08                  call   [esi+8]          ; SLOT 2
          31 c0 81 c4 8c 00 00 00   xor eax,eax; add esp,0x8c
          5d                        pop ebp
```
[inferred, strongly] one of these 15 sites is the pump caller; 0x15b0f is the
lead because it loads the msg id from a stack/record field by `sar 0x18`
(high byte) rather than a compile-time const, i.e. it is generic.
[verified] none of the 15 is in t303's armed set — the t303 negative is
consistent with the handler being reached and is NOT evidence of a bypass.

## S2. INSTRUMENT PATCH (scripts/r299_leg_session.py)
(a) LEGS += the 15 slot-2 call sites (d2_* names) so the census can attribute.
(b) census default legs = the slot-2 sites + cos_hdlr + btn_hdlr (btn_hdlr was
    MISSING in t303, which made the NEXTTURN control unwitnessable by
    construction — t303 defect (4b)).
(c) census_click: close_eventwin BEFORE assert_on_map (t298 modal law, t303
    defect (4a) — the Sparrowhawk dialog swallowed planet/empty/nextturn).
(d) bank_stop already dumps [esp]+8 and records ret_stack.ret0/ret0_file_off
    (patched t303, unmodified). ret0-3 == site for a 3-byte ff /2 call.

## S3. RUN LOG

## S1b. STATIC RE-VERIFICATION BY THIS SESSION (independent whole-image ff/2
##     decode, NOT a mod=01 grep) — the WIP's site list was INCOMPLETE: 22
Decode every 0xFF with modrm reg==2 (CALL [m]) over all 0x8cc83 payload bytes:
681 CALL-[m] total; **22 have disp==+8** (slot 2):
  esi form (ff 56 08, 13): 15b0f 356a5 3afc3 3b38b 3b3a9 3b4e9 3b584 3b5be
    3b607 553cb 553e5 55406 56cda
  edi form (ff 57 08, 2):  4e2cb 54a83   <- WIP's "count said 2, context print
    found 0" gap RESOLVED: both are real; each preceded by `8b b8 a7 00 00 00`
    mov edi,[eax+0xa7] (the WIP's context window/grep missed the REX-free edi
    encoding)
  ebx form (ff 53 08, 1):  809fe   (global object-table index, no +0xa7 load)
  ebp form (ff 55 08, 6):  26c43 27082 31550 333ef 3340c 56c74  <- MISSED by
    the WIP scan entirely: the class-table load there is DISP32
    (`8b 88/ba/a8 a7 00 00 00` = mov r32,[r32+0xa7] mod=10), and the WIP only
    matched mod=01 `8b b? a7 00 00 00`.
[verified] ZERO `call [ecx+8]` sites (confirms the WIP's key negative by an
independent method) -> t303 arming slot-1 ff5104 could not witness cos_hdlr.
[inferred] 26c43/27082 lie INSIDE cos_hdlr's span (0x26b34..), 333ef/3340c
inside the btn handler span (0x336b4 is the handler ENTRY per LEGS, so 333ef/
3340c are ~0x2c5 BEFORE it — i.e. a DIFFERENT function in the type-0 class
object file that chains messages to siblings; note `ba 91 01 00 00` / `ba 92
01 00 00` = msg ids 0x191/0x192 at those two sites).

## S2b. WITNESS RESULT (run work/r1/t299-leg-20261105-033648, attempt 1,
##     03:38:55) — DISPATCH INSTRUCTION NAMED, FIRST STOP:
cos_hdlr stop (leg cos_hdlr, eip 0x1e5f84 = file 0x26b34, eax=0xfd2310
win[eax] magic NAME='COSMOSWnd', edx=0x3b = the periodic pump msg) ->
[esp] ret0 = **0x21612d** -> linear-P0 = 0x56cdd -> 3-byte call boundary:
call site = **file 0x56cda** = `ff 56 08` = **call [esi+8]** — VERIFIED against
payload bytes at that offset, and it is one of the 22 static sites.
Containing function shape (bytes 0x56c80..0x56cdd):
  mov eax,[esp+0xc]; mov eax,[eax+0x4226]; sar eax,0x10; test eax,eax;
  jle out; lea eax,[eax*4]; sub(edx); mov eax,[esi+eax*8+4];
  mov esi,[eax+0xa7]      ; CLASS TABLE from a RECORD in an ARRAY
  mov edi,ebx             ; (msg id staged earlier via `mov ebx,[esp+..]`-ish)
  call [esi+8]            ; SLOT 2  <-- THE DISPATCH
=> [inferred, strongly] 0x56cda is the GENERIC pump: msg id comes from a
   dword array indexed by index (NOT a compile-time const like the 0x3b*
   sites' `ba 32/34/08 00 00 00`), and the target window record comes from an
   array at [rec+0x4226]>>0x10. t303's negative is fully re-attributed: it
   armed slot-1 ff5104 sites; the pump walks slot-2 ff56 08 @0x56cda.
INSTRUMENT GUARD BUG (cosmetic, datum still banked): bank_stop's
ret0_file_off gate compares (r0&P0-mask) against image SIZE 0x8CC83 instead of
the image END (P0+0x8CC83) -> logged file=None while ret0 hex was fine. FIXED
this session (CODE_END bound).

## S2c. WITNESS STRENGTH: 12/12 cos_hdlr stops (3 windows x 4 banked stops,
##     run 033648) give the IDENTICAL ret0=0x21612d -> call site 0x56cda.
##     THE dispatch for the periodic 0x3b pump is ONE site, deterministic.
NOTE: guard bug made witness.json's ret0_file_off null (see S2b FIX), so the
relaunch loop's ret0 tell cannot fire for attempt 1; witness hex is in the
session.log + fixed code re-derives file_off for any later attempt. The
combined --witness+--census fall-through works: 24/24 legs armed at 03:46:06
(22 s2_* + cos_hdlr + btn_hdlr), census phase started, FLEET click 03:46:44.

## S3. CENSUS RESULT (attempt 1 continued, run 033648, rc=0, 45 banked stops,
##     24/24 legs armed incl. btn_hdlr, close_eventwin BEFORE every click —
##     ALL FOUR targets measured, guest alive, 20 autosaves, turn 1086->1086)
PTY whole-log census: {'s2_*': ALL 0, 'cos_hdlr': 41, 'btn_hdlr': 4}.
PER-STOP ret_stack (hits.json — the authoritative caller datum):
  sprite_48x151#0  btn_hdlr  eax=0xfe7594 NAME='Leave Orbit' edx=0x1  <- the
                     sprite click opened the ship dialog; the FIRST handler msg
                     measured for it is 'Leave Orbit' msg 1 via ret0=0x21612d
                     (= site 0x56cda, the same generic pump)
  planet_439x331#0 btn_hdlr  eax=0xfe7748 NAME='Cancel' edx=0x4 ret0->0x56c74
  empty_236x200#0  btn_hdlr  eax=0xfe7748 NAME='Cancel' edx=0x4 ret0->0x56c74
  control_nextturn btn_hdlr  eax=0xfe7170 NAME='PLSQUARE' edx=0x8
                     ret0=0x1fc7e1 -> file 0x3d391; bytes below: `e8` at
                     0x3d38e?? NO — 0x3d38e decodes `63` (ARPL) = NOT a call
                     boundary; the real call is E8-form: bytes 0x3d38c-e =
                     `c1 fa 10 e8` -> E8 at 0x3d38f, rel32 -> target = the
                     DIRECT btn_hdlr call (51 E8-callsites of btn_hdlr exist;
                     t303's "ZERO" claim was about the OTHER legs). NEXTTURN
                     msg edx=0x8 (t302 saw 0x7 at the same handler — 0x7/0x8 =
                     release/press pair, windows.txt SENDMESSAGE family).
  41x cos_hdlr (pump 0x3b) ALL ret0=0x21612d -> site 0x56cda.
=> THE DISPATCH LAW (measured, this run): class msg handlers are reached from
   a small family of GENERIC pump sites: 0x56cda (call [esi+8], record array
   [rec+0x4226]>>16, msg id from stack dword sar 0x10) and 0x56c74 (same
   function, second call site: `mov esi,[eax+0xa7]; sar eax,0x10; ...
   call [ebp+8]` where ebp = class table copy — the esi-form/ebp-form PAIR is
   one function 0x56c4x..0x56cdd). 0x3d38f = direct E8 call inside a button
   press handler. The t301/t303 "slot-1 router 0x30d08" is NOT in the live
   fire path at all.
MAP-CLICK ENTRY ANSWERED (OQ-019 selection-writer target family): the working
sprite click DOES walk the class msg layer — btn_hdlr msg 0x1 on window
'Leave Orbit' — but via pumps 0x56cda/0x56c74, NOT slot-1. t302's cited
negative re-scoped: "not cos_hdlr/slot-1" was right; "not the class msg layer"
was an artifact of arming only slot-1.
OPEN CONTRADICTION (instrument, not game): site BPs for 0x56cda etc. were in
BPLIST every window yet NEVER fired while the handler BPs fired 41x from the
same calls. Probe running (--witness --legs s2_56cda): if a lone site BP also
never fires, C_HEAVY_DEBUG CheckBreakpoint compares GetAddress(seg,eip) —
see S4 for the source-law hypothesis.

## S4. HARNESS LAW (measured + source-cited): `core` is a [cpu] setting, NOT
##     [dosbox] — EVERY t299..t304 debugger run ran the DYNAMIC core.
Canonical conf law (dosbox-x-2026.10.01, ~/.config/dosbox-x/dosbox-x-2026.10.01.conf):
`core` lives under [cpu] (L494-497); `mcp_server`/`autosave`/`captures` live
under [dosbox]. launch() wrote `core=normal` under [dosbox] -> INERT ->
core=auto -> dynamic. GROUND TRUTH: pty verbatim 'Warning: Single-stepping may
not work correctly with "Dynamic core"' printed at debugger-enable when
CPU_IsDynamicCore() != 0 (debug.cpp:5446-5450, cpu.cpp:249-261). Count of that
warning: run 033648 = 1, 043543 = 1 (both old conf); 051904/052925 = 0 (fixed
conf, [cpu]core=normal[dosbox]-reopen layout) => fix works.
DYNREC BP LAW: DEBUG_HeavyIsBreakpoint() is checked ONLY at the top of the
dynrec run loop (core_dynrec.cpp:268), i.e. at INDIRECT-BRANCH targets. A
handler ENTRY (call target, e.g. cos_hdlr 0x1e5f84) stops; a MID-BLOCK site
(call [esi+8] at linear 0x21612A inside a straight block) can NEVER stop.
=> t303's site-zero-fires and sitecheck1 043543 (lone site BP, guest alive,
0 stops, census control MATCH=True) are CORE ARTIFACTS, not game evidence.
NEW ANOMALY (unresolved, -> t305): under the FIXED conf (normal core, warning
absent), runs 051904 (lone s2_56cda BP) and 052925 (s2_56cda + cos_hdlr, 60 s
windows x3) banked ZERO stops — NOT EVEN cos_hdlr, which fired 41x under the
dynamic core — while the guest was ALIVE (autosave files grew to 16, break-EIP
moved 0x20ef05 -> 0x2284f5, turn 1086 held). core_normal.cpp:181 checks every
instruction under C_HEAVY_DEBUG, so zero-fire is unexplained. Candidates:
(a) pump msg 0x3b is generated by a path the slower normal core does not
    reach in-window (wall-clock vs cycle coupling); (b) the two-[dosbox]-
    sections conf breaks something downstream (autosave still worked);
    (c) stop rendering differs under normal core and the fire-pattern law
    (t302 DrawCode form) misses it while the guest... but autosave growth
    argues the guest was NOT stopped. Untested either way.
NOTE: the S2b/S3 ret0 witnesses are guest DATA — core-independent. The
dispatch law (cos_hdlr called from 0x56cda) stands regardless.
