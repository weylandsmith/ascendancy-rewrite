# _wip_t335 — STATE-RECORD FILE-VS-RAM DIFF + id-BRANCH RE-DERIVATION (VERBATIM)

Zero-capture iteration (static disasm + offline .sav census). Predecessor:
docs/re/_wip_t334.md (S0-S13). Assignment: docs/STATE.md NEXT ACTION t335.

## S0. Setup
- Sitting check FIRST: `python3 scripts/r1_t283_tailturn.py work/r1/playcap/live-timeline.jsonl 4000000`
  -> rows 168, first/last turn 1086, max turn 1086 == corpus. NEGATIVE (no new
  sitting; r1_t85g_sitting.py not required).
- Static source: work/r331_disasm.txt (whole-image objdump, 7.1 MB) — region
  0x57ee6..0x58072 re-read VERBATIM this iteration (see S1).
- Stream-law self-note: an `awk '/57f27/,/82070/'` range overran to EOF and cost
  a 3 MB dump. Use explicit line windows from `grep -n` instead.

## S2. FORMAT STRINGS VERBATIM FROM 41.sav (needle-verified B=0x1bf4d8, turn 1086,
## law member = B + 0x82bb0 + X) — THE BRANCH VALUE IS THE PARSED STATE id
```
ds:0x3101 = "%s %d\0"          (STATE line COUNT scan)
ds:0x3107 = "%s %d\0"          (per-entry scan; %d -> [esp+0x378] = tested edx)
ds:0x310d = "%s %d %d %d\0"    (id==0 branch: NAME + 3 ints)
ds:0x3119 = "%s %d %d %d\0"    (id==1 branch)
ds:0x3125 = "..\\winmgr.cpp\0"  (the assert-file argument at 0x58051)
```
So t334's reading of the branch variable (the parsed STATE id) STANDS, and the
windows.txt grammar (re-counted this iteration over extracted/ascend00/
windows.txt, 138 STATE-ish line hits): `STATE 1 0` n=7, `STATE 0` n=9 (count 0 ->
loop skipped at 0x57f21, no records), `STATE 3 1 7 13` n=12, `STATE 1 16` n=19,
`STATE 1 17` n=14, and — decisive — `STATE 4 1 3 7 13` n=1 and `STATE 3 2 4 15`
n=1 carry ids > 1. Under the verbatim code those entries take the ELSE branch
(0x5804c -> assert 0x2a438 -> int3 0x2a424) and then FALL THROUGH to the normal
advance (0x57fa4), leaving byte0 of that slot UNWRITTEN and skipping the
compactor call. The game boots and plays 1086 turns, so the int3 path is
survivable in the shipped build. PREDICTION for the census (falsifiable):
windows whose STATE ids are all in {0,1} have well-formed tags (0/1) at win+0x6d;
windows with any id > 1 show a non-{0,1} tag at the offending slot (stale RAM)
and a counter [win+0xa1] inconsistent with the text count.

## S1. THE 3-WAY BRANCH DATAFLOW, VERBATIM (0x57f3e..0x58062, work/r331_disasm.txt)
The value tested is NOT an independently-parsed "STATE id register" — it is the
OUTPUT SLOT of the scan call, and the same slot is reused for the count:
```
57ef6: push 0x3101 ; push esi          ; esi = scanner state
57efe: call 0x77fe1                    ; -> writes DWORD [esp+0x378]
57f09: mov  eax,DWORD [esp+0x378]      ; COUNT
57f17: mov  DWORD [esp+0x3ac],eax      ; loop bound
57f1e: test ax,ax / jle 0x58062        ; count<=0 -> no records at all
...
loop 57f3e: push [esp+0x378]-ptr; push 0x3107; push esi; call 0x77fe1
57f5c: mov  edx,DWORD PTR [esp+0x378]  ; <-- THE TESTED VALUE (same slot)
57f63: test edx,edx
57f65: jne  0x57ffa
       ; edx==0 : mov BYTE[ecx],0 ; scan fmt 0x310d (4 args) ; call 0x315c4
       ;          -> mov DWORD[ecx+0x1],eax   (u32 name handle)
57ffa: cmp  edx,0x1 / jne 0x5804c
       ; edx==1 : mov BYTE[ecx],1 ; scan fmt 0x3119 ; eax=0x9f10c; call 0x1fe20
       ;          -> and eax,0xffff ; mov DWORD[ecx+0x1],eax  (u16 index)
5804c: mov ebx,0xcd6 ; mov edx,0x3125 ; xor eax,eax ; call 0x2a438  ; else
5805d: jmp 0x57fa4                     ; ASSERT PATH FALLS BACK INTO THE SAME
                                       ; ADVANCE CODE (no exit, no abort seen)
```
So the branch tests the u32 the scanner wrote for the ENTRY token under format
ds:0x3107. t334's "id==0 / id==1" reading is only correct if ds:0x3107 scans a
plain integer. THE ASSERT IS NOT UNCONDITIONAL: `0x2a438` VERBATIM
(`85 c0 / 75 e9 / push ebx; push edx; push 0x1088; jmp 0x2a4cc`) FIRST tests
eax: with eax==0 (the assert site's `xor eax,eax`) it proceeds to 0x2a4cc ->
`push 0x6500; call 0x76c79; add esp,0x10; call 0x2a424` where 0x2a424 is `int3`
— i.e. a DEBUGGER TRAP, not a message-box/exit sequence; and `0x2a428` (the
sibling) with eax!=0 returns immediately (`jne 0x2a425` = ret). [inferred] The
vendor build's assert handler is therefore trap-based; whether the shipped game
survives it depends on a trap handler being installed, which the CENSUS answers
empirically: if `STATE 1 16` windows have a well-formed record, the else-branch
was NOT taken at load time.

## S4. DECISIVE CENSUS (scripts/r335b_item_array.py, RC=0, 196/196 needle-verified
## saves; truth side = on-disk extracted/ascend00/windows.txt) — THE win+0x6d
## STRIDE-13 ARRAY IS THE WINDOW-ITEM ARRAY (TEXTITEM/SHAPEITEM), NOT THE STATE
## ARRAY. t334 S5/S8 WAS A MIS-ATTRIBUTION.
MEASURED (all 196 saves, 22,398 window instances):
- `[win+0xa1] == number of TEXTITEM+SHAPEITEM lines in the window's file block`:
  **22398/22398 exact** (histogram {0:19600, 1:980, 2:1960} == file WINITEMS
  values {2:10 windows, 1:5 windows, 0:93+16-none}). Against the STATE-line count
  the same test FAILS: eq 3844 / neq 18554.
- record byte0 == item kind: (0,'TEXTITEM') 3528 + (1,'SHAPEITEM') 1372,
  **4900/4900 positional agreement**, zero mismatches, for every slot index.
- tag==0 u32@+1 = interner offset: `pool(ds:0x6fda8) + u32` string == the file
  item's literal NAME verbatim: **3528/3528 hits** (INTRO 0x0 "Play^Introduction",
  LOAD 0x3b "Load^Game" + slot1 0x45 "Alt-L", RACES 0x6d "Species", ...).
- Windows ever having records: exactly the **15** file windows that have item
  lines (INTRO, PLAYTUTORIAL, FRESHGAME, RESUME, LOAD, SAVE, EXITTODOS, RACES,
  RESEARCH, FLEET, STATUS, SPECIALAB, GALAXY_MORE, PLAYERS_MORE, DIFFICULTYMORE)
  — 15/15 both directions. Every STATE-bearing window without item lines
  (COSMOSWnd, BatModeWnd, ROT*, LOADSCREEN, ...) has counter 0 and zeroed slots.
FORMAT-STRING CORROBORATION (41.sav verbatim): ds:0x30fb="%s %s",
ds:0x3101="%s %d" (= `WINITEMS 2` scan -> loop bound [esp+0x3ac]),
ds:0x3107="%s %d" (item kind, always 0/1 in the file: kind histogram {0:18,
1:7}), ds:0x310d/0x3119="%s %d %d %d" (= the item line's trailing int triple;
u16s land in the record tail — e.g. LOAD slot0 `00 3b000000 000000 0200 0000
0400` for `Load^Game 2 0 4`, FLEET slot1 tag1 for `1starmap.shp 3 109 0`). The
branch structure matches the ITEM grammar exactly and NOT the STATE grammar.
THE PARADOX DISSOLVES: the else-branch assert 0x5804c can only be reached with
item kind > 1, which shipped windows.txt never contains — so `STATE 1 16` never
trips it, and the game boots, exactly as observed. t334's "STATE line has a
parse-time consumer at win+0x6d" is RETRACTED; the consumer of the block
0x57ee6..0x58062 is the WINITEMS/TEXTITEM/SHAPEITEM builder (fn 0x31690 = item
appender, its "[eax+0x9f]>>16 >= 4" gate = counter<4 cap; fn 0x31384 = the
paint-time item renderer over the same array).

## S3. SELF-CORRECTION + CENSUS RUN 1 (scripts/r335_state_records.py, RC=0,
## 196/196 needle-verified saves) — t333's "windows.txt resident in saves" does NOT
## hold in the playcap corpus, and fn 0x31690's gate IS the counter (no new datum)
- MEASURED: `NUMCONTROLS` occurs in ZERO Memory members across 284 save dirs (3
  saves each); `STATE <n>` regex hits = 4 in 41.sav (all in C-string-literal
  regions like `..\\batcon.cpp\0%s\0BatModeWnd\0` at 0x2420e6 — data-segment
  literals, NOT the file). The full windows.txt text (42,478 B,
  sha256 cf54c632..., extracted/ascend00/windows.txt) is NOT resident in the
  playcap saves; the t333 note "text IS resident (member 0x39db51)" does not
  reproduce here. CONSEQUENCE: the file-vs-RAM diff takes its truth side from the
  ON-DISK windows.txt joined by window NAME — legitimate (it is what the parser
  read) and stronger than a fragment join.
- STRUCTURAL FACT: fn 0x31690's "type gate" `mov eax,[eax+0x9f]; sar eax,0x10;
  cmp eax,4` reads the u32 at win+0x9f whose HIGH HALF is exactly the u16 at
  win+0xa1 — the counter. So "gate>=4" IS "counter>=4" (max 4 STATE records per
  window), not a window-type check. t334 S8's "asserts window-type >= 4" wording
  is corrected: it asserts counter < 4. (Census: observed [win+0xa1] in all 196
  saves = {0: 100/save, 1: 5/save, 2: 10/save}, never >=4, never negative.)
- RUN 1 join failure: resident-text truth returned no_text for 21832/22540 window
  instances (root cause = bullet 1). Re-running with on-disk-file truth (S4).
- Loop model for the diff (VERBATIM, all three branches converge at 0x57fa4 ->
  call fn 0x31690): compactor copies 13 B from the cursor to win+0x6d+13*[win+0xa1]
  and increments the counter; cursor also advances +13 per entry, so dst==src
  (self-copy) and the counter ends == number of entries processed. PREDICTION
  per window: [win+0xa1] == text count (capped by the 4-assert); slot byte0 == 0
  for id 0, == 1 for id 1, STALE (untouched) for id > 1; u32@+1 == resolved
  handle (id 0) / u16 index (id 1) / stale (id > 1).

## S5. DISPOSITION (t335) — (sections above landed out of order; read S1->S4)
1. CLOSED BY MEASUREMENT: "what is the win+0x6d stride-13 array" -> the
   window-item array (WINITEMS/TEXTITEM/SHAPEITEM builder), 22398/22398 +
   4900/4900 + 3528/3528 across 196 saves. t334 S5/S8 RETRACTED as
   mis-attribution; the id-16 assert paradox is resolved (kind>1 never ships).
2. STATE-LINE CONSUMER: none in fn 0x575e4 (measured by elimination over the
   full block: count scan 0x3101 = WINITEMS, entry scan 0x3107 = item kind).
   Combined with t333 (no global datum, [win+0xab] = control table), residue-(1)
   has zero remaining STATE-line edges inside the image. Row stays OPEN
   strict-close (mode-1 store never witnessed firing; nuke effect never seen).
3. HARNESS LAWS BANKED: (a) windows.txt is NOT resident in playcap saves
   (NUMCONTROLS 0/284 dirs) — file-vs-RAM diffs use the on-disk extracted file
   joined by window NAME (magic+NAME law); (b) fn 0x31690's [eax+0x9f]>>16 gate
   IS the u16 counter at +0xa1 (max-4-items cap); (c) interner pool ds:0x6fda8
   holds label strings ("^" = accelerator marker), u32 handles are pool offsets.
4. NEXT-SESSION LEAD (not this task): the item renderer fn 0x31384 + paint fn
   0x30fb8 remain outside-image-reachable only; the interesting surviving
   question for OQ-016 residue-(1) is now the CONTROL-enablement loader
   (0x58aff..0x58b3e, t333) vs the ds:0x13b98=4 bound and who ever raises
   ids 16/32/64 flags from 0 — NOT the STATE line again.
