# _wip_t428f.md — K5 ORIGIN VIA RUNTIME FRAME READ

Assignment: docs/STATE.md NEXT ACTION t428f. Inputs: E6 law (docs/re/_wip_t428e.md)
— fn 0x5caac composes x = p4 + struct[+4] + dir[+0x10], y twin (work/combat_decomp/
5caac.c:58-64, arg map shp.md S12.1); the k5 site 0x3c82d pushes 3 of 5 args
($0,$0,$5) then handle+&struct — pending-push accounting at the call is the open
question; measured peak (224,107) is NOT a law.

## F0 — DESIGN (pre-session)
Legs (file offsets; linear = P0+off, P0=0x1BF450 deterministic base):
  k5_gate 0x3C7CD  `cmpl $0xffffffff,0x35(%eax)` (bytes MEASURED in
                   work/ascend_payload.bin: 83 78 35 ff — matches E1 asm).
                   Stops with eax = 0x56d1c(0x7a35c,"PLANLIST") result.
                   Bank: widget ptr, u32@+0x35 (the gate datum), head head
                   magic+name@+0x20.
  k5_blit 0x3C82D  `call 0x5caac` (bytes e8 7a 02 02 00; rel: 3c832+0x2027a
                   = 5caac EXACT). Fires ONLY if gate passed. Bank: 0x20
                   bytes at esp (ret0 + p1..p5 AS THE CALLEE WILL SEE THEM),
                   struct[0..0x18] at p1, payload head 0x40 + dir entry for
                   sel=p3 at p2+8+8*p3, entry rect fields +8/+0xc/+0x10/+0x14.
                   Compute x = p4 + s[+4] + dir[+0x10], y = p5 + s[+8] +
                   dir[+0x14] (E6 law) and compare to (224,107) [screen law:
                   png = screen + (80,100), t428c].
Phases: boot -> campaign (Oct-29 RESUME.GAM) -> drain -> "planets" (click
553,145, census 15 s) -> "row" (click 200,105 per t254 Vega-IV recipe, census
15 s). Safety: scratch game-wp, private Xvfb :97, port 55998, core=normal,
-time-limit, SIGKILL recorded PIDs, base assert B==0x1BF4D8.
Offline companion: witness-B gate value — read widget+0x35 from
work/r1/bank-t251-live1255 (the t254 sitting ON the planet screen, witness-B
lineage) via the 0x56d1c walk (needs the walk law; Ghidra if up, else asm).

## F1 — OFFLINE WITNESS-B GATE READ (pre-session) [MEASURED,
## work/r1/bank-t251-live1255 41..60.sav, magic-record census]

Every sav holds a window record magic 0x12345678 + NAME@+0x20 census:
PLANLIST @ sav-linear 0xfe689c, PLSQUARE 0xfe71f8, PLANETALLOC 0xfe670c,
PLRES/PLIND/PLPRO/PLPOP/PLBUILD siblings. **PLANLIST dword@+0x35 == 0 in ALL
20 slots** (bytes +0x30..+0x3f verbatim all-zero) — gate `cmpl $-1,0x35(%eax)`
would FAIL *if* 0x56d1c returns this magic record AND the bank state is
representative of the witness-B moment. CAVEATS: (i) the bank (Nov 1 08:21)
predates t254's 11:17 STATUS/row clicks — the widget may be initialised at
detail-open; (ii) the return-value identity of 0x56d1c (magic record vs member
table 0x7a35c entry) is NOT yet cited. 0/126 magic records anywhere in RAM hold
dword+0x34-window == -1 (16 hold 0xFFFFF000). The live gate stop (eax = the
actual 0x56d1c result) settles both.

## F1b — ARG ACCOUNTING CORRECTION TO E6 (from E1's own banked asm)
[E6 VERIFIED against work/t198_planwin.asm:2011-2040 + add $0x14 cleanup]
The k5 site pushes FIVE args in total, not two: push $0 (y), push $0 (x),
push $5 (sel) BEFORE the 0x1fc34 fetch (Watcom memory-clobber discipline),
then push %eax (payload ptr) + lea/push &struct. `add $0x14,%esp` (20 B = 5
args) at 0x3c832 proves the count. t428e E6's "p3/p4/p5 are frame leftovers"
is WRONG for this site — x=0, y=0, sel=5 are EXPLICIT. E6's composition law
then gives origin = (dir[+0x10], dir[+0x14]) with s[+4],s[+8] clamps — i.e.
the runtime payload-dir entry ALONE decides placement. The live [esp..esp+0x14]
dump at 0x3c82d is the direct witness of all five args as the callee sees them.

## F2 — SESSION dbg-t428f-20261119-201742: PAINT BODY RAN; k5 GATE SITE
## NEVER EXECUTED (attempt 1, rc=1) [MEASURED]

Drive: Oct-29 RESUME.GAM (turn 1086), base B=0x1BF4D8 OK; Planets click
(553,145) planets_diff=153800; detail-row click (200,105) row_diff=171424
(both screens captured). Legs armed across both census windows.
PTY WHOLE-LOG CENSUS (the authoritative counter): {k5_gate: 0, k5_blit: 0,
blit1: 1}. The single blit1 stop (tag row#0, 20:19:49): eip=0x1fae2f
(file 0x3b9df), eax=p2=0x4ac540, [esp]=p1=0xfe6688 — the t428d PORTED blit-1
call executing LIVE, i.e. THE PAINT BODY'S HEAD RAN after the row click.
(The census.json 'k5_gate:1' line is a harness artifact: the MEMDUMPBIN
control filename mem_ctl_census_001fbc1d.bin matches the bare FirePat —
fire-candidate eip was 0x23357a, not a leg; the pty has exactly ZERO real
gate fire lines. Fix later: filenames must not contain leg signatures.)

CONSEQUENCE: t428e E2's "no ret exists between head and site => every paint
runs the k5 gate" is REFUTED BY LIVE EXECUTION: the head ran (blit1) and the
gate site did not. A branch between 0x3b9df and 0x3c7cd SKIPS the k5 block on
this planet/screen state. F3 = find it statically; F4 = witness its inputs if
cheaply reachable.

## F3 — LIVE GATE WITNESS (attempt 2, rc=0) dbg-t428f-20261119-210504
## [MEASURED]: k5 IS GATED OFF ON THE PLANET DETAIL SCREEN

PTY WHOLE-LOG CENSUS {k5_gate: 1, k5_blit: 0, blit1: 1}. The gate stop (fired
during the detail-row click — i.e. the paint body REACHED 0x3c7cd on the live
frame): eax = widget ptr 0xfe6814, head magic 0x12345678 OK, NAME@+0x20 =
"PLANLIST", **DWORD[widget+0x35] == 0** -> `cmpl $-1` FAILS -> branch to
0x3c835, the k5 fetch+blit NEVER EXECUTES. k5_blit leg armed, zero fires —
consistent. blit1 control fired (paint head ran, p1=0xfe6688 = widget+4 law,
p2=0x4ac540 shape payload). Screen drive: planets_diff 153800, row_diff 171424
(detail screen captured 10_planets_screen/11_row_screen.png).

CONSEQUENCES:
 (i) t428e E2 ("no ret between head and site => every paint runs the k5
      gate") was WRONG in its CONCLUSION, right in its edge analysis: the
      gate DOES run on every paint; it FAILS on every state witnessed
      (live attempt 2 + offline F1 20/20 bank slots +0x35==0). k5 is a
      GATED-OFF branch, not an unreachable one.
 (ii) The t428c (224,107) registration peak (1566 px, z=18.6, 4.4x permute
      baseline) is a FALSE POSITIVE: since the vendor never paints k5 on
      witness B's screen, those matched pixels are lattice/pop-art art that
      happens to share k5's speckle colours. NO k5 port (a port would draw
      art the vendor does not draw — the strict-close bar catches it).
 (iii) SEAM T428c-A CLOSED: identity CLOSED t428e (E3/E7); the ORIGIN
      question is CLOSED as a NON-QUESTION for the witness class — the blit
      does not execute there, so no origin exists to pin. Residual OPEN
      (banked, not chased): the condition that would set PLANLIST+0x35=-1
      (writers of -1 to widget+0x35: 0x3ab24 bulk-init after the 0x56ce4
      widget loop, 0x3d3a7 button-handler path; 0x3d765 clears to 0 —
      [verified asm work/t198_planwin.asm]).

## F4 — F1b CONFIRMED BY THE LIVE FRAME: the k5 site's five args are
EXPLICIT (x=0,y=0,sel=5 via the Watcom double-duty push trick + handle +
&struct; `add $0x14,%esp` = 5 args). E6's "p3/p4/p5 stale frame leftovers" is
RETIRED for this site (the composition LAW 5caac.c:58-64 stands; only the
leftover-input premise dies).

## F5 — HARNESS LAW (cold-leg census): resume_and_rearm's BPDEL * + re-arm
DESTROYS a pending halt at the next cold leg (attempt 1: CPU parked at
0x1FBC1D with the fire line + I-> register line visible in the pty; BPDEL *
released it unbanked; the stock whole-log census then counted the
mem_ctl_census filename, a false 1). FIX (in r428f_k5_session.py, instance
patch): POLL-BY-BREAK census — BREAK, EV eip, attribute, bank; resume = BPDEL
ONLY the fired index + RUN. Cold paint-site legs make this safe (t302
hot-storm law does not apply). Generalise for future cold-leg sessions.

## LEDGER (t428f)
Closes NOTHING in docs/OPEN-QUESTIONS.md (planet-screen visuals have no OQ
owner; t414..t428e precedent; OQ-016/019/027 untouched). Seam T428c-A CLOSED
(F3). k5 law finalised: FOURTH paint blit, record 5 IMMEDIATE, gate
widget[+0x35]==-1, gate FAILS on all witnessed states -> NOT PORTED.
