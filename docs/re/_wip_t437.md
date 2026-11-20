# _wip_t437.md — OQ-027(b) STRATEGIC SFX ID: windows.txt SOUNDCHANNEL -> record+0x57 ROUTE

Assignment: STATE.md t437 (OQ-027b). NOTE: the STATE text quoted the +0x1bcc
control-record route — that exact wording is SUPERSEDED by R-t429 (batfx
keyboard table, click-driven census dead). The LIVE residue t429 left is the
row's real question: "which id-0/+0x57 site covers the strategic rail/NEXTTURN
press, and does windows.txt SOUNDCHANNEL write +0x57 (if it does, the t395
census {0 x118} means the vendor plays 'button' on those controls)". That is
what this iteration works. Zero-capture static + save-corpus census.

## Inputs / carried laws
- fn 0x575e4 = windows.txt parser (t336; grammar = sequential sub-parsers
  selected by TYPE value; keyword strings scanned but mostly NOT compared).
- t336 S1 store census: parser stores to window record at
  {+0x18,+0x1a,+0x1e,+0x3d,+0x59,+0x63,+0xa7,+0xab} + item path. NO store at
  +0x57 itself was reported — but see F1: the SFX field is a DWORD at +0x57
  whose HIWORD (= word at +0x59) is what the play sites read.
- Play sites (t429 census): 7 sites `mov edx,[obj+0x57]; sar edx,0x10;
  cmp edx,-1; je skip` -> wrapper 0x4fb30 -> FUN_000500e0 (manifest index into
  86-name soundfx.txt; -1 silent).
- windows.txt SOUNDCHANNEL census (t395): {0 x118, -0 x1}.
- Addressing: pool-relative immediates; pool base 0x82bb0 (fmt '%s %d' abs
  0x85fdb = rel 0x342b); "windows.txt" abs 0x85bac = pool-rel 0x2ffc.
  payload addr == restored addr (verified this iteration: string at 0x85bac in
  work/ascend_payload.bin, and no absolute-imm xrefs — all refs are 0x2ffc-style).
- Save corpus: 196 needle-verified saves (t335/t336 law), winmgr state table
  fingerprint W=0x2bc3e4 in 196/196; window HANDLE byte at record+0x41.

## F1 [MEASURED byte-scan work/ascend_payload.bin code 0x200..0x82bb0]
Byte-level scan for [reg+0x57] accesses (mod=01 disp8 0x57, opcodes 88/89/8a/8b
+ 66-prefixed + C7/0):
- WRITES to [r+0x57]: exactly 6, ALL BYTE writes (opcode 0x88):
  0x21e42, 0x23ca7, 0x3a66c, 0x3ae28, 0x3b09c, 0x41d64. Zero dword (0x89)
  writes, zero C7/0. => the byte at +0x57 is a DIFFERENT field from the sfx
  dword the play sites read: writing the low byte cannot set the HIWORD.
- READS: 75 total; the 7 sfx sites are the 0x8b (dword) ones:
  0x30e65, 0x321ff, 0x3335f, 0x3af88, 0x3af93, 0x4e443, 0x4e502 (t429's cited
  call addrs 0x30e75/0x3220f/0x3336f/0x3af9e/0x4e453/0x4e512 = the calls
  ~0x10 later; consistent). All other reads are 0x8a byte reads = the
  low-byte field (unit/gizmo state family, 0x38xxx-0x4xxxx cluster).
- COROLLARY: the sfx id lives in the HIGH WORD of dword[+0x57] = bytes
  +0x59/+0x5a. A writer must therefore write disp +0x59 (word), +0x5a (byte),
  +0x55/+0x56/+0x58 (overlapping dwords), or copy a quad.
  t336 found EXACTLY ONE parser store in that family: edx+0x59 @ 0x57e7a.

## F2 [MEASURED objdump 0x57c00..0x57ea0, windows.txt parser fn 0x575e4]
The window-keyword sub-block is a FIXED SEQUENCE of scanner calls (fmt 0x30e3
'%s %d' abs 0x85c93) each storing into a record base edx = [esp+0x37c], in
windows.txt file order:
  0x57c47 scan -> count loop 0x57c70 (STATE ids -> call 0x57194, t336 law)
  0x57cd5 mov DWORD [edx+0x1a],0 ; 0x57cdc mov WORD [edx+0x18],ax  (state tbl)
  0x57cf8 scan -> 0x57d00 cmp parsed,0 ; if != 0: 0x57d11 mov DWORD [eax+0x3d],-1
  0x57d3d scan -> 0x57d45 cmp parsed,0 ; if != 0: 0x57d56 mov DWORD [eax+0xab],-1
  0x57d79 scan -> dest [edx+0x8]   (X0)
  0x57d9a scan -> dest [edx+0xc]   (Y0)
  0x57dbb scan -> dest [edx+0x10]  (X1)
  0x57ddc scan -> dest [edx+0x14]  (Y1)
  0x57dfa scan -> (MOUSEFOCUS)
  0x57e39 scan (fmt 0x30dd) -> 0x57e48 mov DWORD [edx+0xab],eax  (control tbl)
  0x57e64 scan -> 0x57e7a mov WORD [edx+0x59],ax   <-- THE SOUNDCHANNEL STORE
  0x57e90 scan -> dest [edx+0x45] ; 0x57ec4 -> [edx+0x4b] ; 0x57ede -> [edx+0x4f]
  0x57efc scan -> item count -> item array at [edx+0x6d] (t335 law)
Grammar count check (extracted/ascend00/windows.txt, MEASURED): X0/Y0/Y1/X1 x124,
PARENT x123, STATE x123, MOUSEFOCUS x119, SHAPEFRAME x119, SOUNDCHANNEL x119 —
the three-way 124/123/119 tiering matches the block structure (the two
pre-window blocks + TYPE-100 opening page account for the deltas).

## F3 [MEASURED — the decisive join]
The SOUNDCHANNEL value is stored as the u16 at record+0x59. The seven strategic
play sites read `mov edx,DWORD [rec+0x57]; sar edx,0x10` — the HIGH WORD of the
dword at +0x57 IS the word at +0x59. Therefore:
    SOUNDCHANNEL value == the manifest id the vendor plays at those sites,
    and -1 (0xffff/0xffffffff) == silent (cmp edx,-1; je skip).
VERBATIM site 0x30e20..0x30e75 (record base esi):
    30e20 cmp ecx,[eax+0xc] / 30e29 cmp ecx,[esi+0x14]   ; rect hit-test
    30e32 mov eax,[esi+0x47] ; 30e35 mov cx,[esi+0x45] ; 30e3f mov ebx,[esi+0x4b]
    30e65 mov edx,[esi+0x57] ; 30e68 sar edx,0x10 ; 30e6b cmp edx,-1 ; 30e6e je
    30e70 mov eax,0x78638    ; 30e75 call 0x4fb30         ; play manifest id
    30e7a cmp dword [esi+0x63],0 -> 30e80 mov eax,0x7a35c ; control pool call
RECORD IDENTITY (same struct as the parser writes): the parser block reads
[ebp+0x41] as the window HANDLE (t336 S4, fn 0x57194 arg); this handler reads
[esi+0x41] as the handle at 0x30d79/0x30d98/0x30daa (compare vs ds:0x7d35e, then
two calls into 0x7a35c-pool helpers). Same displacement, same role.

## F4 [MEASURED — windows.txt SOUNDCHANNEL value census, all 119 lines]
Per-window values (name -> SOUNDCHANNEL): EVERY window is 0 EXCEPT
ALIENDIP (TYPE 26) which is "-0". "-0" scanned with %d == 0, so the RUNTIME
value is 0 for all 119 windows. Named strategic controls verified individually:
NEXTTURN 0, NEXTTURNCONT 0, TOGLANES/TOGEMPIRE/TOGSHIPS/TOGCOLONIES 0,
RESEARCH 0, FLEET 0, STATUS 0, SPECIALAB 0, GALAXY_MORE 0, Player^Color 0,
SHIPDESSCREEN 0, WEAPONS/HULL/... 0, PLANLIST 0, PLSQBUT0..5 0, RESWIN 0,
HELPBUTTON0..4 0, ABILBUTTON0..1 0, EVENTBUTTON0..1 0, BatControlWnd 0.
=> soundfx.txt manifest[0] == "button" (t429 banked name list). So for every
window in the file, the record field the play sites read is 0 == "button".
This is the t429-narrowed question answered: SOUNDCHANNEL DOES write the field
the +0x57 sites read, and its value is 0 everywhere, i.e. the vendor's
strategic-window press sound is manifest[0] "button" — NOT a per-button id.

## F5 [MEASURED scripts/t437_soundchannel_store_census.py, 20-save corpus]
Window records located by magic 0x12345678 + printable NAME at +0x20 (t335 law),
record-relative +0x59 read per record. 2,480 named window records over 20 saves:
  +0x59 distribution: {0: 2400, 0xffff: 80}.
  The 80 are 4 names x 20 saves: COSMOSWnd, BatModeWnd, INTROFLIC, WMGRDEBUG —
  all FOUR are absent from windows.txt (runtime-created windows; the file has
  COSMOSWnd only as a PARENT reference, never as its own TYPE block). Their
  HIWORD is -1 == the sites' silent branch.
  Every file-declared window in live RAM carries +0x59 == 0, including the
  spot-checked strategic set NEXTTURN, NEXTTURNCONT, TOGLANES, TOGEMPIRE,
  TOGSHIPS, TOGCOLONIES, RESEARCH, FLEET, STATUS, GALAXY_MORE, PLANLIST,
  PLSQBUT0, RESWIN, ALIENDIP, BatControlWnd (20/20 each, zero file-vs-RAM
  mismatch).
=> SOUNDCHANNEL -> record+0x59 -> HIWORD-read by the strategic play sites is
MEASURED end-to-end (static store site 0x57e7a + live RAM value + the sites'
own read pattern), and the value is 0 = soundfx manifest[0] "button" for every
file-declared window, -1 (silent) for the four runtime-created windows.

## F6 [MEASURED — positional grammar proof + click-dispatch identity]
(a) GRAMMAR POSITION. windows.txt TYPE-0 block order (69/132 blocks, and the
same sub-sequence in TYPE 5/6/8/8/10/11/15/15/18/25/29 blocks):
  PARENT, STATE, MOUSEFOCUS, X0, Y0, X1, Y1, SHAPEFRAME, SOUNDCHANNEL,
  SENDMESSAGE, SENDPARAM1, SENDPARAM2, HELPINDEX, WINITEMS.
Parser scan sequence in 0x57c00..0x57f00 (all fmt '%s %d'), with stores:
  STATE loop (0x57194) -> MOUSEFOCUS (cond +0x3d=-1; cond TYPE==25 +0xab=-1)
  -> X0 +8 -> Y0 +0xc -> X1 +0x10 -> Y1 +0x14 -> SHAPEFRAME +0x1e word
  -> (cond TYPE==16: control-table scan -> +0xab, t333 law)
  -> SOUNDCHANNEL: 0x57e7a mov WORD [edx+0x59],ax
  -> SENDMESSAGE +0x45 -> SENDPARAM1 +0x4b -> SENDPARAM2 +0x4f -> WINITEMS +0x6d.
The four rect stores pin the sequence: X0/Y0/X1/Y1 land +8/+c/+10/+14 in file
order, so the scan two positions after Y1 (after SHAPEFRAME +0x1e) is the
SOUNDCHANNEL line, and its store is +0x59. Byte-scan corroboration: inside the
parser (0x575e4..0x59900) there is EXACTLY ONE write to any displacement in
0x55..0x5c (corrected scan: modrm rm=5 mod=01 is EBP+disp32 STACK, not record
+0x5d — first-pass scan was wrong; corrected scan says the same thing anyway):
0x57e7b mov DWORD [edx+0x59],eax. Outside the parser, dword writes at +0x59 are
gizmo/unit-record code (0x40ea2/0x49dc4/0x4d05a, adjacent +0x52/+0x54/+0x63
gizmo fields) — different struct class, not windows.
(b) CLICK DISPATCH. The play site 0x30e75 sits in a rect hit-test over
[rec+8/+0xc/+0x10/+0x14] (X0/Y0/X1/Y1 as the parser stores them); on hit it
plays HIWORD(dword[rec+0x57]) then dispatches [rec+0x45]/[rec+0x4b]
(SENDMESSAGE/SENDPARAM1 as the parser stores them) into the STRATEGIC control
pool 0x7a35c (call 0x56ad4). Same record shape as the sibling fragment 0x30edc
(SENDPARAM2 byte test at +0x4f) and the handle/pool code at 0x30d79..0x30dad
([rec+0x41] vs ds:0x7d35e, pool calls). This is the strategic-window
mouse-press dispatch, not batfx.
(c) DUAL-PATH ROBUSTNESS. t429 counted 8 xor edx,edx (id 0) sites and 7 +0x57
sites. For every file-declared window both paths resolve to manifest id 0:
the id-0 sites literally play 0, and the +0x57 sites read SOUNDCHANNEL == 0.
Only the runtime windows COSMOSWnd/BatModeWnd/INTROFLIC/WMGRDEBUG (absent from
windows.txt, +0x59 = -1 in 20/20 saves) are silent on that path.
(d) manifest[0] re-verified verbatim: extracted/ascend00/soundfx.txt line 4
"86", line 5 "button".

## T437 VERDICT (OQ-027b)
The t429-narrowed question is ANSWERED WITH MEASUREMENT: windows.txt
SOUNDCHANNEL DOES write the field the strategic +0x57 play sites read (store
0x57e7a -> rec+0x59 == HIWORD(dword rec+0x57)), and its value is 0 for every
one of the 119 file lines (file census + 2,400 live records in 20 saves). The
vendor therefore plays soundfx manifest[0] "button" on strategic-window presses
(rail buttons, NEXTTURN, title buttons — all TYPE-0/25 windows with SC=0) and
NOTHING on COSMOSWnd/map. There is NO per-button vendor id for the strategic UI;
per-key ids exist only in batfx.txt (keyboard gizmo fire, t429). Port upgrade:
sfxForPress RailButton/NextTurn/TitleButton click08 (off-manifest no-op since
t395!) -> "button"; MapClick stays nullptr (COSMOSWnd SC-absent => -1 => silent
— MEASURED, and now corroborating rather than assumed).
