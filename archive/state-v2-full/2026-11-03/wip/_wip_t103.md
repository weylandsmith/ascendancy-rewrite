# t103 WIP — FUN_00037b6c DX-SWITCH ADJUDICATION (human ability-activation spec)

Assignment (docs/STATE.md NEXT t103): decode the whole dx-switch of
FUN_00037b6c (extent 0x37b6c..0x37f02 per functions_full.tsv hex length 0x396).
Why chain-critical: t102 S7.2 proved the local/human race's SA_ abilities fire
ONLY through FUN_00037b6c (dx==1 gate 0x37c9c -> call 0x43b50(edx=1) at
0x37cb1), so this function IS the human ability-activation spec.
Legs: (1) dx cases, (2) 0xccb 'not-due' marker at 0x37bb9 + consumer of
0xccb+2, (3) string-table leg 0x37cc0 (push cad, push 0x1ca1), (4) caller
census + ebx register flow, (5) live 60.sav consistency (row+0x19e vs cad).
Verify tool target: scripts/r1_t103_dxswitch_verify.py.

Context carried in (from STATE/aicode S6/S7): FUN_00043b50 = per-race SA_
cadence engine; jump table FILE 0x43b10 16 entries; row+0x19d ability number,
row+0x19e charge counter; cadence word WORD[0x6780+2*ability] (FILE 0x89330);
live 60.sav B=0x1bf4d8, deterministic anchor b"\x1e\x00Factory" at
B+0x82bb0+0x73e40+8; race rows stride/locator per t99.

## probes
(P1) session start: live-timeline.jsonl 5691796463 B mtime Oct 26 15:44 ==
    STATE's 5.69 GB figure -> NO new sitting; assignment stands.
(P2) objdump -D -b binary (NOTE: `-D` required; `-d` alone prints nothing on a
    raw binary) 0x37b6c..0x37f02: function ENDS at 0x37cf7 (ret); next func
    starts 0x37cf8 (a gizmo/shape draw fn using 0x9f10c + FUN_0001fc34 +
    FUN_0005caac). functions_full.tsv hex length 0x396 over-runs by 10 bytes.
(P3) HEAD LAW: EAX arg = UI object ptr (ebp); DX arg = message code; EBX arg =
    flag (register args, no prologue frame args). esi = LOCAL race row:
      movzx esi, BYTE ds:0x7458e           (local race idx, t102 identity)
      eax = ((idx*32-idx)*8-idx) = idx*247; eax+=eax = idx*494 = idx*0x1ee
      esi = 0x12e16 + idx*0x1ee            (race diplomacy-row base, §matrix)
    -> esi+0x19a..0x19d = ability byte (= [esi+0x19a]>>24, consistent with t99
       row+0x19d), esi+0x19e = charge counter dword.
(P4) DISPATCH (0x37b90..0x37ba6, cited bytes):
      cmp dx,1 / jb 0x37ca1        dx==0 -> DEFAULT
      jbe 0x37bab                  dx==1 or 2 -> LEG A (PROBE + COUNTDOWN TEXT)
      cmp dx,0x32 / je 0x37c9c     dx==50 -> LEG B (ACTIVATE)
      jmp 0x37ca1                  else -> DEFAULT
    DEFAULT 0x37ca1: movsx edx,dx; eax=ebp; call 0x33ff8; jmp exit.
    LEG A 0x37bab: edx=0; call FUN_00043b50(eax=row, edx=0) = DRY-RUN PROBE.
      eax==-1 -> BYTE [ebp+0xccb] := 2 ('not available' state) -> tail.
      else -> countdown text leg (P5).
    LEG B 0x37c9c: cmp ebx,1 / je 0x37cad; NOT-1 -> DEFAULT (0x33ff8).
      0x37cad: edx=ebx(=1); eax=esi(row); call FUN_00043b50(row, 1) = ACTIVATE
      -> then the help-window leg (P6) -> tail.
    TAIL 0x37c78: [ebp+0x35] := -1; [ebp+0x39] := -1; ebx := [ebp+0xa7];
      edx := 0; call [ebx+0xc]  (vtable refresh/paint); eax := 0; ret.
    DEAD CODE noted: `mov ebx,2` at 0x37bca inside leg A is overwritten at
    0x37beb (`mov ebx,[esi+0x19e]`) and never read (ebx is read only at
    0x37c9c, which leg A cannot reach, and 0x37c81 reloads it).
(P5) COUNTDOWN TEXT (0x37be0..0x37c77): cad = WORD[eax*2+0x6780] with
    eax = row[+0x19a]>>24 (the cadence word, t99/t100 law, FILE 0x89330);
    ebx = row[+0x19e] counter; edx = cad - counter;
    edx==1 -> string idx 0x1c else 0x1d; call FUN_00021a20 (static.txt getter,
    t96 CLOSED law) -> formatted via call 0x76c79 (4 stack args) into the
    object's field-0xcd0 buffer path, then a byte-copy loop 0x37c2f..0x37c46
    (Watcom inline strcpy, 2 bytes/iter) into [ebp+0xcd0]; then string 0x1e
    copied (loop 0x37c5f..0x37c75) to [[ebp+0x67]+0x4]+0x20 (a widget text
    slot). => leg A is DISPLAY: "days remaining until the ability is ready".
    NOTE the days value passed is cad-counter (unsigned 16-bit).
(P6) LEG B HELP WINDOW (0x37cb6..0x37cef): eax = row[+0x19a]>>24 (ability id),
    push 0x1ca1, lea out-buffer, call 0x76c79 = snprintf(out, fmt, ability).
    POOL-REL IMMEDIATES BYTE-PINNED in work/ascend_restored.bin:
      0x1ca1 -> file 0x84851 = "abres%02d"   (ability-result help resource name)
      0x1cab -> file 0x8485b = "help.txt"
    then call 0x33f40(eax=object, edx=0x1cab "help.txt") -> then tail vtable.
    => dx==50/ebx==1 = HUMAN FIRING + opening the abres<NN> help text.
(P7) CALLER CENSUS: ZERO rel32 calls to 0x37b6c image-wide (173k-insn objdump).
    Exactly ONE u32 == 0x37b6c in the whole file: file 0x8893c, inside a run of
    u32 code pointers (0x88934 0x37ad0 / 0x88938 0x30d08 / 0x8893c 0x37b6c /
    0x88940 0x37cf8 / 0x88944 0x311b8 / 0x88948 0x316f0 ...), above a region of
    packed-pair geometry-looking u32s. => window-manager HANDLER TABLE, invoked
    indirectly (dispatcher passes eax=object, edx=dx, ebx=flag). Identity TBD.

## WORKING LAW (to be cited-verified)
FUN_00037b6c = the special-ability WINDOW handler for the LOCAL race:
  dx 1..2 -> probe FUN_00043b50(row,0); -1 -> state byte +0xccb=2; else draw
             countdown "cad - counter" days (static.txt strings 28/29/30).
  dx 50   -> iff caller flag ebx==1: FIRE FUN_00043b50(row,1), then open the
             abres<ability> help text from help.txt.
  else    -> pass through to FUN_00033ff8 (default handler).
OPEN: (i) how FUN_00043b50 uses edx (0 probe / 1 commit — needs the internal
sites); (ii) consumers of [obj+0xccb] and +0xccd; (iii) handler-table identity
+ who arms ebx==1; (iv) live 60.sav cad/counter consistency leg.

(P8) CLASS-RECORD IDENTITY CLOSED: the u32 run at restored FILE 0x88934 ==
    pool VA 0x5d84 (0x88934-0x82bb0) is the WIDGET CLASS RECORD; constructor
    FUN_00037ac0 (0x37ac0..0x37acf): call 0x33ee0 (base ctor); mov DWORD
    [eax+0xa7],0x5d84. FUN_00037ad0 = create/dtor leg (test cl,4 -> load
    template edx=0x888f8 via 0x76cac+0x76ccc; else edx=1 + vtable store +
    call 0x33ef8). The class slots: +0 FUN_00037ad0 (create), +4 0x30d08
    (shared), +8 FUN_00037b6c (EVENT HANDLER — the dx-switch), +0xc
    FUN_00037cf8 (PAINT: shp lib 0x9f10c sel 250 + race glyph
    [race*2+0x12e18] via FUN_0001fc34/FUN_0005caac). Sibling ability window
    classes at the same run: {...,0x37844,0x30d08,0x37894,0x37904,...} and
    {...,0x362c8,0x30d08,0x36348,0x366a4,...} share +4/+paint-pair slots =>
    generic 6-slot class layout. ZERO rel32 callers = DISPATCHED via
    [class+0x8] (pump hunt P9). Tail of 0x37b6c 0x37c90 calls [ebx+0xc] =
    the PAINT slot — refresh-after-event law.
(P9) FUN_00043b50 INTERNAL edx LAW (cited bytes):
      0x43b63 xor ebx,ebx; 0x43b6f ax=WORD[eax*2+0x6780] (cad);
      0x43b7c cmp eax, DWORD [ebp+0x19e]; 0x43b82 jg 0x44017
        => NOT-READY (cad > counter) -> eax=0 early return.
      ready (counter >= cad): 0x43b88 [esp+0x6c4] := -1;
      0x43b93 cmp edx,1 / 0x43b96 je 0x441c1
        => edx==0 (PROBE, from 0x37baf): return eax=-1 (ready).
        => edx==1 (COMMIT): 0x441c1 body dispatch: al=BYTE[ebp+0x19d]-5;
           cmp al,0xf; ja 0x4400a (out-of-{5..20} -> passive, store
           [esp+0x6c8]=ebx=0); else jmp cs:[eax*4+0x2ef60] (t99 FILE 0x43b10
           16-entry body table).
      RESET exits byte-exact: shared tail 0x43fe5..0x44011 =
           eax=[ebp+0x19a]>>24; ax=cad; edx=[ebp+0x19e]; sub edx,eax;
           [esp+0x6c8]=edx; 0x4400a: [ebp+0x19e] = [esp+0x6c8]
        => row+0x19e := counter - cad  (t99 prose 'cad - cnt' was DIRECTION-
           WRONG; equal at the ==cad fire moment, so t100's reset-0 model
           stands unchanged).
(P10) 0xccb CONSUMER CENSUS (disp32 raw-byte scan over obj0 0x14bb0..0x82bb0):
      disp32==0xccb EXACTLY ONE hit (0x37bbb = the store itself); 0xccd ZERO
      hits; 0xcd0 four hits (0x37c15,0x37c2b in this fn = text-field ptr;
      + 0x3b291,0x3b2b7 = sibling fn reading the same field — identity check).
      => the 'ready' marker byte [ui+0xccb]:=2 has NO READER image-wide
      (honest negative under the disp32-encoding law: code disp32 fields are
      not fixup sites, live==file; computed-offset readers can't be excluded
      statically). UI countdown is driven by the re-probe, not the marker.
(P12) EVENT PUMP (indirect-dispatch identity) CLOSED ENOUGH: FUN_00056b5c
    (0x56b5c..0x56c9e, eax=game obj 0x7a35c, dx=message, ebx/ecx=coords,
    1 arg ret 0x4): reads window idx WORD[obj+0x4226]>>16 (t102 pump's
    sibling), indexes stride-0x8e window table at obj+0x3068
    (imul eax,0x8e 0x56bdb); window-rec word +2 (member obj+eax*1+0x4) gates
    active; 0x56c16 reloads (edx,msg,ebx) from stack args;
    0x56c6b mov ebp,[eax+0xa7]; 0x56c71 sar edx,0x10; 0x56c74 call [ebp+0x8]
    => the CLASS-RECORD +0x8 slot IS the message handler; ebx passes through
    VERBATIM from the pump caller. Sibling FUN_00056ca4 (window-message
    forwarder, 56 rel32 callers incl 0x37bdb inside our leg A) resolves
    target widget from stride-4 table at obj+0x4 (idx in edx>>16, stride*3*4
    form at 0x56cc4) then calls target class +0x8 with movsx(dx).
    Pump rel32 callers (9, all in the UI/event loop 0x53f95/0x54976/0x54ac5/
    0x54b36/0x5531e/0x5548c/0x55f80/...): each arms ebx explicitly
    (0x53f95 xor ebx,ebx msg 0xd; 0x54976 loads bx from ds:0x484c6 + msg
    from cx=ds:0x484c4; 0x54ac5 msg 4 ebx=ds:0x484ec; 0x54b36 msg 5;
    0x5531e/0x5548c xor ebx,ebx). The pending-input globals 0x484c4/c6
    (msg,ebx pair) + 0x484ec/f0 (pair) are written by the INPUT layer —
(P13) DISPATCH ARRIVAL ANALYSIS (who can hand dx=50/ebx=1 to the handler):
    FUN_00056ca4 register law RE-READ (0x56ca4..0x56cdf): edi=caller ebx =
    the MESSAGE CODE (handler receives it as dx via movsx at 0x56cd7);
    caller ecx -> handler ebx (0x56caa mov ebx,ecx); caller edx = target
    window index (>>16); target = [[game+0x4][...]] (0x56ccd). So relays of
    the shape {ebx=0x32} send msg code 50. CENSUS of all 56 relay sites:
    msg-50 senders exist (0x3b6ac, 0x3d83f/8a3/8ec/910, 0x3da6e/ac5/af9) but
    NONE arms ecx==1 (their ecx: 12/10/10, 10/10/11, 10, 11 — slot/context
    indices; msg-52/50 families sit in ship-context code 0x3d8xx-0x3dbxx
    whose gates read ship record fields [x+0xab]/[x+0xae] and ds:0x43508).
    Top-window pump sites (0x56b5c, 9 callers): 0x54976 is the INPUT relay —
    msg := WORD ds:0x484c4, ebx := WORD ds:0x484c6 verbatim from the DOSBox
    event record read at 0x2a875/0x2a8fe (record+0xc -> 0x484c4 = VK code,
    record+0x10 -> 0x484c6 = ASCII char, INT 16 families at 0x2a5f0/0x2a6d0
    corroborate scan/char pairing). STATIC VERDICT: no code path in the
    image provably delivers (msg 50, ebx 1) by either route [honest
    negative — dispatch paths are exhausted (pump 9 + relay 56 sites, all
    register-traceable), but a live UI trace is the only POSITIVE
    confirmation of which user action arms it]. Handler-internal law stands
    either way: gate dx==50 -> requires ebx==1 -> FIRE.
(P14) 0x33f40 (help-opener called by leg B): copies edx string to
    [obj+0xab] (the help-file name, 'help.txt'), ebx string to [obj+0xc9]
    (the resource name, 'abres%02d'-formatted); sets [obj+0xdab]/[obj+0xda7]
    bookkeeping. Sibling leg at 0x37b63 (create path, 0x37ad0 test cl,2 ->
    0x76cd4) loads the DESCRIPTION resource 'abil%02d' (file 0x8483f) +
    'help.txt' (0x84848) — window shows abil<NN> description at open,
    abres<NN> result text after a FIRE. (t99's abil/abres text pair, now
    wired to the two UI events.)

## VERDICT (t103)
The human ability-activation spec IS FUN_00037b6c, fully decoded
(scripts/r1_t103_dxswitch_verify.py RC=0 five legs):
  OPEN (create leg 0x37ad0): shows static.txt/abil<NN> description.
  dx 1|2 (window events incl. the child-2 relay at 0x37bdb): PROBE
    FUN_00043b50(row,0); -1 (ready) -> [ui+0xccb]:=2 dead marker (NO reader
    image-wide) -> tail; else -> countdown string 'N day(s)' (static.txt
    idx 28 ''/29 's' singular test cad-counter==1) + 'OK' label.
  dx 50 (press-class message): iff ebx==1 -> COMMIT FUN_00043b50(row,1) =
    body dispatch (ability-5, 16 cases, t99 table) + row+0x19e :=
    counter - cad, then open abres<ability> from help.txt; else default
    FUN_00033ff8 (base-class message filter).
  Dispatch identity: ability-window CLASS RECORD pool 0x5d84 (file 0x88934),
    +0 create +8 handler +c paint (race ability icon shp 0x9f10c sel 250 +
    glyph byte row 0x12e18); zero direct callers; pump FUN_00056b5c
    [class+0x8], relay FUN_00056ca4 (msg=caller ebx, handler ebx=caller ecx).
CORRECTIONS banked: (a) aicode S6 expectation 'abres%02d at dx==2' REFUTED —
abres is the dx-50 RESULT resource, dx 1|2 is the countdown; (b) FUN_00043b50
reset direction is counter - cad (0x44001 sub edx,eax), equal to 0 only at the
exact fire moment (t100 reset-0 model unaffected); (c) t99 prose '0x4400a
stores 0' only true for the fire leg via counter==cad.
REWRITE: no delta — the rewrite's abilityPhase (AI auto-fire at ==cad) already
matches S7.2 sync law; the human path is UI input, out of model scope.
OPEN RESIDUAL (carried): positive runtime confirmation of which user action
arms (msg 50, ebx 1) — live UI trace territory (F8b queue second).
(P11) COUNTDOWN TEXT semis CLOSED: FUN_00021a20(0x1c)='' / (0x1d)='s'
       (ascend00.cob static.txt blob, 191 strings, indices 28/29 = SINGULAR/
      PLURAL suffix — edx==1 iff cad-counter==1 picks ''), 0x1e='OK' copied to
      [[ebp+0x67]+4]+0x20 (OK-button label widget). Formatter 0x76c79 =
      snprintf-family (prologue maps stack args, calls 0x79345 with state
      ecx=0x620b6, NUL-terminates dst at retlen 0x76c9e). Template arg comes
      from object field [ebp+0xcd0] (text-field ptr set at window build).
      Assignment's EXPECTATION 'abres%02d at dx==2' REFUTED by measurement:
      abres%02d (pool 0x1ca1) is used in the dx==50 FIRE leg (result text),
      dx 1/2 leg is the probe+countdown.
