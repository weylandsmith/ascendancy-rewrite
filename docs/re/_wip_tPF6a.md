# _wip_tPF6a — "Does the vendor ever show a Build whose PLANLIST has no buildable row?" (iteration log)

Task: STATE NEXT ACTION TPF6-A. tPF-6b proved the hard half (PLBUILD always
opens cell -1; popup Build leg == fill checker 0x3830c). Remaining per STATE:
(1) write the implication out as S15.1 (two-callsites argument 0x3d579 vs
0x3b786); (2) port-side pin: for every id where popupButtonIds yields Build,
projectOptionsFor(-1) non-empty; (3) honest-negative check on the escape
hatches: item 5 and item 23 (seam TPF6-SHIP: does the popup's item-23 leg
agree with the fill's — verify 0x3d564..0x3d58e runs the same 0x39a9c path).

## HYPOTHESISED HATCHES (to kill or keep)
- H1 item 5: fill skips 5 UNCONDITIONALLY (0x3b76a). If the checker could PASS
  item 5 at the popup's cell, popup Build could show over an all-but-5-empty
  set. tPF-6b notes "item==5 -> pop-leg exempt 0x38435" — exempt != pass;
  need the item-5 path's final verdict.
- H2 item 23: checker item 23 (0x17) replaces the pop verdict via 0x39a9c when
  the pop leg FAILS (0x38422). If 0x39a9c reads ebx (the caller's cell), the
  popup (armed cell) could PASS item 23 while the fill (cell -1) FAILS it ->
  popup Build over an empty fill. If 0x39a9c is cell-independent (0x3958c
  scans internally), both callsites agree and emptiness stays impossible.
- H3: popup loop range vs fill loop range (popup 54 items? fill 0..0x26) and
  what CELL the popup passes (word[widget+0xab] per tPF-6b P4).

## PROBES
P1 disasm 0x3d4f0..0x3d5e0 (popup buildable loop: range, cell reg, call args)
P2 disasm 0x39a9c..0x39b25 (cell-independence of the ship pop-exemption)
P3 disasm item-5 verdict path inside 0x3830c (0x38425..0x38445 + final 0x386fe)
P4 port: popupButtonIds + projectOptionsFor current source, pin location

## FINDINGS

### F1 — H2 (item 23 / TPF6-SHIP) IS CLOSED AT CALL-SITE LEVEL [verified bytes]
0x39a9c (137B, full body read): prologue pushes ebx/ecx/edx FIRST (0x39a9c-d),
verdict computed ONLY from (a) race byte [obj+0x57] vs [0x13b96]>>16, (b)
0x3958c(obj, 0x16) first-empty-cell scan (0xffff -> fail; cell word+2 bit0
== 0 -> fail), (c) 0x402d8(race*78 + 0x12e16) > 0. The caller's ebx (cell) is
NEVER READ before the push and is restored by the epilogue (0x39b21-23).
=> checker(item 23) pop-leg outcome is CELL-INDEPENDENT: the popup's 0x3d579
call and the fill's 0x3b786 call get the SAME verdict for item 23. The
0x402d8 seam stays unrecovered but is IRRELEVANT to the emptiness question
(it can only grant/deny item 23 identically at both callsites). STATE's
escape hatch (3) is CLOSED: emptiness stays impossible via item 23.

### F2 — H1 (item 5) IS DEAD: THE POPUP LOOP SKIPS 5 TOO [verified bytes]
Popup item loop 0x3d550..0x3d58e (fn 0x3d2fe): ecx 0..0x26, 0x3d55f
`cmp cl,5 / je 0x3d559` — UNCONDITIONAL skip-5, identical to fill 0x3b76a.
The earlier worry was the checker's internal 0x38430..0x38435 (item==5 ->
ebp := -1, pop-leg EXEMPT -> checker CAN pass item 5), but since BOTH
callsite loops skip 5, no Build button is ever attributed to item 5. Hatch
killed at the callsites, no checker semantics needed.

### F3 — POPUP COMPOSITION STRUCTURE (fn 0x3d2fe, msg dispatch 0x3d343)
[ebp-0x10] = widget; 0x3d319 cl-family: cell item = byte[cell word+0xab]
indexed via obj+0x10 table (+1 byte). Dispatch on msgid dx: <0x33 -> 0x3db06;
0x33..0x34 -> 0x3daae; 0x35..0x37 -> 0x3d8b0; 0x38..0x39 -> 0x3d8f9/0x3d93d;
0x3a -> 0x3da8e. THE ITEM LOOP AT 0x3d550 IS REACHED ONLY VIA 0x3d3bc
`cmp cl,0xff / je 0x3d550` = EMPTY CELL PATH. Non-empty cell: item 23
(ship) path 0x3d3c5..0x3d505 emits ship-family buttons (0x34/0x36/0x39/0x37/
0x38/0x32 by ownership legs via 0x396cc/0x49768/0x3958c) and NEVER runs the
item loop; other-item path 0x3d506..0x3d54e emits 0x38 (demolish?) and 0x35
by `cmp cl,5` legs. => THE BUILD BUTTON (id 0x36, emitted at 0x3d586) EXISTS
ONLY FOR EMPTY CELLS AND ONLY FOR ITEMS PASSING 0x3830c(item, word[w+0xab]=
EMPTY CELL INDEX).

### F4 — THE MONOTONICITY ARGUMENT (the S15.1 core) [verified + inferred]
checker(item, cell) = LEG-A AND LEG-B AND LEG-C (final AND 0x386fe).
- LEG-A (0x3835d): reads req byte, race mask word[0x74744], tech bits — no
  cell operand. CELL-INDEPENDENT. [verified tPF-6b body audit]
- LEG-B (0x383b3): acc = word[+0x42] - word[+0x4c] + SBYTE UPOP(pending),
  pure world-state arithmetic; item 23 failure replaced by 0x39a9c verdict
  (F1: cell-independent). CELL-INDEPENDENT. [verified]
- LEG-C (0x3843a): `cmp bx, word[esi+0x1a]; jae 0x386fe` — cell -1 (0xffff)
  bypasses every cell leg with edi pre-granted -1 => CHECKER SET AT cell=-1
  IS A SUPERSET of the checker set at any real cell: pass(c,-1) => pass(c,c')
  contrapositive of the tPF-6b jae-bypass law.
=> pass(item, popup_cell) => pass(item, -1). Popup Build (id 0x36) requires
pass(item, popup_cell) for some item != 5 in [0,0x27); by monotonicity that
item passes at -1, and the fill loop (cell forced -1 by PLBUILD SENDPARAM1 1)
appends it => THE VENDOR LIST BEHIND A VISIBLE BUILD BUTTON IS NEVER EMPTY.
### F5 — 0x3958c IS A PURE FIRST-EMPTY-CELL SCAN [verified bytes]
0x3958c(obj eax, dl=item): pushes ebx/ecx/esi, loops cells 0..word[+0x1a]-1
for byte[cell]+1 == cl, returns first hit or 0xffff. No caller-state reads
beyond obj. Confirms F1(b): the ship-exemption's cell comes from the scan,
never from the caller's ebx.

### F6 — *** THE 0x38422 ITEM-23 REPLACEMENT IS A REVOCATION, NOT A RESCUE ***
[verified bytes 0x3840a..0x38430; ebp init law: 0x38317 mov ebp,-1 at entry,
0x3834b `xor ebp,ebp` (right after the item-index math, BEFORE LEG-A) clears
it on every in-domain item — so ebp at 0x3841d is -1 iff the POP test passed]
  0x3840f mov ax,[esp+0x1c] / 0x38414 cmp eax,ecx / 0x38416 jl 0x3841d
  0x38418 mov ebp,-1              <- pop PASS sets -1; pop FAIL leaves 0
  0x3841d cmp ebp,-1 / 0x38420 jne 0x38430   <- POP-FAIL SKIPS the 0x38422
                                                  replacement entirely
  0x38422 cmp dl,0x17 / jne 0x38430
  0x38427 call 0x39a9c / 0x3842e mov ebp,eax  <- runs ONLY when pop PASSED:
                                                 0x39a9c may REVOKE (eax=0)
                                                 a passing ship row.
=> tPF-6b's wording "item 23 -> 0x39a9c REPLACES the verdict (pop-short
   exempt)" MISSTATED the direction: item 23 is never EXEMPTED by pop-fail;
   a pop-PASS can be REVOKED by 0x39a9c. Consequence: the checker set for
   item 23 is a SUBSET of {pop-pass AND req-pass} at every cell, and the
   revocation verdict is cell-independent (F1) — the fill (cell -1) can only
   have MORE item-23 rows than the popup, never fewer. Monotonicity holds
   for item 23 a fortiori. Port note: projectOptionsFor's `id != 23 &&
   freePop < upop -> skip` models the pop leg as exempt for 23, which is
   STRICTLY WEAKER than the vendor (vendor additionally revokes via 0x39a9c
   and requires leg A for 23 too). The revocation stays seam TPF6-SHIP; it
   cannot create vendor emptiness, and port-side the 23-row is always
   present when the popup offers Build — the invariant direction we pin.

### F7 — LEG-A FAIL PATH (0x38372/0x383ad -> 0x38430) ALSO EXEMPTS ITEM 5
0x38430 cmp dl,5 / jne 0x3843a / 0x38435 mov ebp,-1: item 5 reaching 0x38430
(leg-A fail OR pop fail) gets ebp := -1 => checker(item 5, -1) = PASS always.
The fill loop's unconditional skip-5 (0x3b76a) is therefore load-bearing for
vendor behaviour, and the popup loop's skip-5 (0x3d55f) mirrors it exactly
(F2) — so the item-5 asymmetry hatch is closed at BOTH callsites.
PORT DEFECT CANDIDATE (small, honest): port requiresAvailable-gates item 5
in projectOptionsFor AND in the ui.cpp lambda, while the vendor exempts 5
from legs A+B. Only observable when REQUIRES would refuse 5 — the port then
drops the Colony Base row where the vendor keeps it. NOT emptiness-relevant
(drops rows from BOTH sets); noted, not shipped this iteration (item 5 is
never a row at the fill anyway — wait, the fill skips 5 unconditionally, so
the port's skip-5 ALREADY matches the vendor; the vendor's checker-internal
exemption never reaches the list. => NO PORT DEFECT: exemption is dead code
as far as the list is concerned. Pinned as reasoning, no change.)

### F8 — PORT-SIDE INVARIANT + PIN (this iteration's ship)
Port structure (ui.cpp:1303 lambda, planetwin.cpp popupButtonIds,
planetview.cpp projectOptionsFor):
  lambda(item) = freePop>=upop AND requiresAvailable AND placementBlock==None
                 (items 0xff and 23 skip the first two legs);
  popupButtonIds(empty cell) = {kPbBuild iff lambda passes some item in
                 [0,0x27) skip 5, first-match-break} + {kPbCancel};
  projectOptionsFor(star, -1) = {id in [0,n) skip 5: requiresAvailable AND
                 (id==23 OR freePop>=upop)}.
=> DERIVED THEOREM (port mirror of F4): lambda(item) => (item==23 OR
   item in projectOptionsFor(-1)); and item 23 in the port is ALWAYS in
   projectOptionsFor(-1) when requiresAvailable(23) (upop=1, exempt leg).
   So popup Build => fill non-empty, port-side, PROVIDED the lambda keeps
   its free-pop/requires legs. The MUTATION-WORTHY pin is the implication
   itself: widening the lambda's 23-exemption to skip freePop while
   projectOptionsFor gated 23 on freePop would break it.
PIN: test build_build_button_implies_nonempty_fill_tpf6a in
test_optionsfilter_tpf6.cpp — enumerate cells; for each empty cell run
popupButtonIds with a lambda echoing the ui.cpp wiring; if Build present,
assert projectOptionsFor(c, star, cell) non-empty AND the witness item is
in the -1 list (monotonicity of the port predicates).
