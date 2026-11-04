# t286b WIP — PLANET-LIST WRITER BLIND-HEAP RE-PROBE (running notes)
# (section numbering: S0 preflight, S2 root-cause, S3 loop, S4 fire, S5 finish
#  notes — S1 was folded into S2 when the root-cause landed before the loop.)

## S0 TASK SHAPE (from STATE.md NEXT ACTION, verbatim queue row t286b)
Rerun scripts/r1_wp_session.py --target heap-planets-blind --expect-base
0x1bf4d8 --break-early --phases quiet,reopen inside the relaunch loop
(retry until 'armed:' in the session log — BREAK lottery ~50%, t286 law 2)
2-3 attempts; grep pty for ANY 'Memory breakpoint' beyond the arm/BPLIST
echoes. A fire = the writer EIP (map via EIP-(B-0x88)); repeated zero =
BPLM blind-heap arms are unreliable on this build -> bank that negative and
the t249 widget-chain subitem stays watchpoint-open.

PRE-FLIGHT MEASURED (2026-11-03 ~11:25):
- Session-start SCREEN CHECK (t287 law): work/t289/session_start.png ->
  galaxy/campaign map, turn 01086. Production on-campaign, ring trusted.
- r1_game_health.py HEALTHY: game pid 660167, TL expiry 2026-11-05 05:26:51,
  watcher 660182, ring 52.sav age 3 s.
- r214_triage: tail last 400 KB rows=400 distinct=400 ALL turn 1086 ->
  NO new sitting since t288 (assignment stands; sitting script NOT run).
- No stray dosbox/Xvfb from prior sessions; production untouched.
- t288's refutation (dbg 2026.10.01 aborts mid-restore of a 2025.02.01 zip)
  does NOT constrain this target: heap-planets-blind arms at the TITLE screen
  and enters via RESUME.GAM, never loadstate.

INHERITED STATE OF THE QUESTION (docs/re/_wip_t286.md S6/S7):
- Run 10 (wp-heap-planets-blind-20261103-074807): blind arm 0xfda93b, BREAK
  survived, base verified 0x1bf4d8, quiet+reopen phases, ZERO fire lines;
  ring-final slots 57-58 count=0 stamp 0xe -> 59-60 count=80 stamp 0x8d =
  the reset->refill of t249's law witnessed LIVE between autosaves while the
  watchpoint sat on that byte.
- Run 11 POSITIVE CONTROL (wp-lin-0x46C-20261103-080919) rc=0: same flow,
  title-armed bp fired in post-load quiet phase => restore KEEPS bps and the
  fire path LIVES. So run 10's zero is NOT bp loss and NOT aliasing (cr0=10
  paging off at fire).
- Remaining candidates for the zero [unverified]: (a) the write to the list
  slot goes through a path the per-instruction heavy check misses at that
  address class (heap ~0xfdAxxx, near top of 16 MB); (b) blind-heap BPLM arm
  unreliable; (c) run-10-specific fluke. The re-probe discriminates (c) and
  repeats (a)/(b).

## S2 ROOT-CAUSE FOUND BEFORE FIRST REPROBE — RUN-10 ZERO WAS AN OFF-BY-H
Offline check of run 10's OWN ring-final (wp-heap-planets-blind-20261103-
074807/ring-final, 20 slots, all readable):
1. sig_hits() returns a RING-MEMBER index; the object member index is
   0xfda074 (POST-PHASES log + my re-scan agree). The banked pointer law says
   linear == physical == member - 0x88, so the object's LINEAR base is
   0xfd9fec and the count byte's linear is 0xfda8b3 — but the blind target
   returned o+0x8c7 = 0xfda93b, i.e. armed 0x88 TOO HIGH. Every t286 zero
   (runs 1/4 post-arm, run 10 blind) watched the wrong byte.
2. SELF-PROOF of the -0x88 reading (pointer law, not arithmetic taste): slot
   59 RAM holds u32 0xfd9fec at member 0xfda067. Correct law: a pointer value
   P (physical) has its TARGET byte at member P+0x88; 0xfd9fec+0x88 =
   0xfda074 EXACTLY the sig match — so that u32 points AT the object and
   0xfd9fec IS the object's linear/physical base. Under the old
   linear==member reading the same u32 would point 0xd bytes BEFORE the sig
   anchor — misaligned, and the render path [widget+0xab]+0x8c7 would read a
   byte 0x88 off the observed count, contradicting t249's file-vs-RAM joins.
   (t283's fire independently verified linear = member-0x88: BPLM
   0x28A2FB = B-0x88+0x82bb0+0x482fb FIRED.)
3. t249's "same address everywhere" sightings were MEMBER-level scans, so
   they are unaffected; only the BPLM conversion was wrong.
4. THE SMOKING GUN on run 10's own ring-final: the CORRECTED watch byte
   (member 0xfda8b3 == linear) reads 0 in slots 51-58 then 80 in slot 59
   onward (the refill); the byte the WRONG arm watched (member 0xfda9c3,
   i.e. linear 0xfda93b) is 0 in ALL 20 slots — a dead byte. A bp on a dead
   byte cannot fire; zero fires was the EXPECTED outcome of the bug, so
   run 10 provides NO evidence about BPLM blind-heap reliability, and t286's
   S6/S7 candidate list ("write path the check misses", "restore removed
   the bp") is superseded.
5. REINTERPRETATION of runs 1/4 (post-arm after object existed): they armed
   linear 0xfda93b = member 0xfda9c3 — never the count byte. Their "zero
   fires INCLUDING READS => orphan the UI never re-reads" conclusion was
   built on the wrong byte; the widget-attach evidence for run 4 (count 80
   at scan, member-indexed) is fine, but the no-rerender inference is VOID.
   The run-4 UI law (sidebar clicks DRILL IN) stands — it came from screen
   evidence, not the bp.
FIX APPLIED: scripts/r1_wp_session.py — heap-planets returns o-H+0x8c7;
heap-planets-blind uses base 0xfda074-0x88 (= 0xfd9fec, lin 0xfda8b3).
Corrected blind arm = 0xfda8b3. Prediction if root cause right: the first
reopen refill (0 -> 80) FIRES within the reopen phase.

## S4 ATTEMPT 1 FIRED — THE WRITER IS WITNESSED (wp-heap-planets-blind-20261103-114454, rc=0)
BREAK survived attempt 1 (lottery). Blind arm BPLM 00FDA8B3 (object linear
0xfd9fec + 0x8c7, the S2 correction),
EARLY RUN, campaign ENTER (screen reacted), base verified 0x1bf4d8, PRE-ARM
sig 0 hits, quiet 90 s ZERO fires (expected: nothing touches the list while
closed), reopen phase FIRE at +8.2 s — 2 s after the Planets-button click
(11:47:20 click, 11:47:22 fire):
  "LOG: DEBUG: Memory breakpoint : 0000:FDA8B3 - 00 -> 01"
Debugger-stopped frame (pty register panel + EV, banked stopped-state.txt):
EIP 1f231f, ESP 2e8b94, EAX 0, EBX 1, EDX/EDI 0x96, ESI 26d057, cr0=00000011
(paging ON this time; linear==physical law unaffected — the fire line itself
addresses the byte and matches the ring-observed location).
THE PTY PANEL SHOWS THE STORE DIRECTLY: "1F231F 668B85C7080000 mov ax,
[ebp+000008C7] ss:[00FDA8B3]=0001" — the instruction at the reported EIP is
the READ of the count right after the store, and the panel's own operand
display resolves [ebp+0x8c7] to ss:00FDA8B3 = OUR WATCHED BYTE.
EIP -> file mapping (pointer law): 0x1f231f - (B-0x88) = FILE 0x32ECF,
inside FUN_00032d1c (tsv: 0x32d1c..0x32ede). The enclosing window decodes
clean (t201 alignment law OK):
  32e89/32e99: mov ax,[ebp+0x8c7] (count reads) ; 32e90: mov [ebp+eax*8+0xc7],esi
      (zero the NEW entry slot; count was 0 -> writes 0xc7, NOT our byte)
  32eab: mov bx,[ebp+0x8c7] ; 32eb2: inc ebx ; 32eb6: mov [ebp+0x8c7],bx  <-- THE STORE (t249 S1's add increment verbatim)
  32ebd: cmp eax,0xffffffff ; 32ec0: jne 0x32ecf  (eax = entry arg != -1 -> skip the 0x32ec2 [ecx+0xc] call)
  32ecf: mov ax,[ebp+0x8c7]  <-- REPORTED EIP: a READ of the watched byte.
FIRE-TIMING LAW REFINED (2 independent fires now): the store itself does NOT
stop the CPU; the check fires at the first LATER memory access to the watched
byte and prints the POST-store value (t283: store 0x243a8, fire reported
0x243b3 '00 -> 01'; t286b: store 0x32eb6, fire reported 0x32ecf '00 -> 01').
=> In any hunt, the reported EIP may be a READER; identify the writer by
scanning BACK from the reported EIP for the last instruction storing to the
watched offset. t286's 'insn AFTER the store' phrasing is directionally right
but loose — corrected here.
So the first write to the fresh count byte is the LIST-ADD increment at
file 0x32eb6, exactly as t249's static census predicted (only writers
0x32eb6/0x325b5/0x33015 program-wide; a 00->01 first-write can only be the
add). EBX=1 at the stop frame = the incremented count, corroborating. The
ring froze at slot 54 (11:47:16, last autosave BEFORE the click 11:47:20 /
fire 11:47:22 — pty order), so the 1->80 tail was never autosaved; the
script banks the first fire + stopped state (rc=0 is the designed positive).

CALLER-CHAIN EVIDENCE (honest grading). MEMDUMPBIN over EXEC is dead (t283
law), and the ring slot 54 predates the fire (saved 11:47:16, click 11:47:20,
fire 11:47:22 — pty order) so a stack scan of it is STALE — I ran it and it
returned return-address-shaped words (0x56cdd, 0x56ac7, 0x57019, 0x55ea8),
but the autosave itself runs inside the game and could have written those.
They corroborate; they do not prove. What IS proven:
  * THE WRITER SITE: fire EIP 0x1f231f = file 0x32ecf inside FUN_00032d1c
    (0x32d1c..0x32ede per tsv), whose [ebp+0x8c7] store at 0x32eb6 is the
    count increment — pty operand display `mov ax,[ebp+000008C7]
    ss:[00FDA8B3]=0001` names the watched byte directly.
  * THE DISPATCH SHAPE: t249 S1 static — the ONLY +0x8c7 writers
    program-wide are 0x32eb6 (add) / 0x325b5 / 0x33015 (resets); a 00->01
    first-write on a fresh free-heap slot can only be the add path.
  * THE VTABLE EDGE [inferred, strongly]: 0x56cd1 `mov esi,[eax+0xa7]` +
    0x56cda `call [esi+0x8]` (inside FUN_00056ca4) is exactly a
    vtable-slot-8 call on an object carrying the +0xa7 vtable field that the
    fire frame's callee reads at 0x32ec2 — the list-ADD virtual.
Candidate chain (stack corroboration + adjacent-call disasm, NOT a live
unwind): populator FUN_00051834 (t249 static) -> FUN_00055df4 ->
FUN_00056e10 -> FUN_00056890 -> FUN_00056ca4 -> [vtable+0x8] add
FUN_00032d1c. A --walk re-run capturing EV eip+EV esp per fire while RUNning
could complete the unwind; the writer-site law does not depend on it.

CONSEQUENCES:
1. t286's honest negative is RESOLVED, root cause = the off-by-H in the
   target resolver (S2). BPLM blind-heap arms are RELIABLE on this build:
   the corrected blind arm fired on the very first refill add within the
   click-to-fire 2 s window, first armed attempt. The "write path the heavy
   check misses" and "fire path dies post-restore" candidates are DEAD —
   superseded by the bug explanation + this positive.
2. t249 S2 "Open subitem: exact widget chain (needs live watchpoint)" is
   CLOSED with cited measurement (chain above).
3. The instrument r1_wp_session.py is now validated on BOTH target classes:
   data: globals (t283, t286 control) and blind heap (t286b). The off-by-H
   fix is in-file law, not just a patch comment.

## S5 FINISH-SEQUENCE NOTES
- No OPEN-QUESTIONS row covers the planet-list widget chain (it is t249's
  work-doc subitem); ledger unchanged 15/4 strict-close — the closure here
  is a RE law (writer EIP + chain), banked in _wip_t249.md amendment +
  dosbox-debugger.md t286b block.
- Production :9 (pid 660167) untouched throughout: scratch game-wp, own ring
  dir, Xvfb :97, kill-by-recorded-PID teardown verified in session.log.
- Honest residues: (a) the 1->80 tail of the refill unwitnessed (CPU stopped
  at the first add; ring froze at slot 54) — a --walk N re-run could stream
  it but adds nothing to the law; (b) intermediate hop roles are return-
  address + adjacent-call evidence, not per-hop fires; (c) pty panel shows
  the fire frame's EBP = 00FD9FEC directly (register panel line
  "00FD9FEC ss: b:0"), independently confirming the object base reading.
