# _wip_t429.md — OQ-027(b) CONTROL-RECORD SFX-ID CAPTURE

Assignment: docs/STATE.md NEXT ACTION t429. Closure bar (OQ-027 row): "capture
diff of control-record +0x1bcc across control classes, or user hearing."
Inputs cited: FUN_000500e0 = the SFX play routine (work/coswnd_decomp/500e0.c,
banked t83); callers 0x17488/0x1749b/0x4fb59 (audio.md §2 line 149);
windows.txt SOUNDCHANNEL census {0 x118, -0 x1} (t395, audio.md §6.6).

## T429-A — CALLER-SITE DISASSEMBLY REFUTES THE "CONTROL-RECORD" READING
[MEASURED: objdump -b binary -M intel over work/ascend_payload.bin, file offsets
0x17433..0x174c8; payload = pre-fixup image, imagebase 0 (OQ-008 law)]

The sites 0x17488/0x1749b are NOT per-control-record reads. Exact bytes:

    17433  movsx eax,al            ; al = KEY CHARACTER (arg to enclosing fn)
    17436  shl   eax,2
    17439  lea   ebx,[ecx+eax]     ; ebx = obj + 4*key  <-- KEY-indexed entry
    1743c  mov   eax,[ebx+0x1a90]  ; dword at obj+0x1a90+4*key
    17442  sar   eax,0x10          ; HIWORD
    17447  mov   dx,[ecx+eax*2+0x19c6]  ; u16 table @obj+0x19c6
    1744f  mov   eax,0x9f10c       ; handle (fetch fn 0x1fc34, k5-law fetch)
    17454  call  0x1fc34
    17459  mov   eax,[ebx+0x1a92]  ; second dword, same entry
    17462  mov   dx,[ecx+eax*2+0x19c6] (after sar 0x10)
    1746a  mov   eax,0x9f10c ; call 0x1fc34
    1747a  mov   edx,[ebx+0x1bcc]  ; dword at obj+0x1bcc+4*key
    17480  mov   eax,0x78638       ; AUDIO-OBJECT handle (param_1 of 0x500e0)
    17485  sar   edx,0x10          ; SFX ID = HIWORD  <-- the cited site
    17488  call  0x500e0           ; play sfx #HIWORD([obj+0x1bcc+4*key])
    1748d  mov   edx,[ebx+0x1bce]  ; second id, same key entry
    17493  mov   eax,0x78638
    17498  sar   edx,0x10
    1749b  call  0x500e0

LAW (three corrections to audio.md §6.5 / the OQ-027 row premise):
1. +0x1bcc/+0x1bce are NOT fields of a control record — they are the 3rd/4th
   u16s of a per-KEY-CHARACTER dword entry (obj + 0x1a90 base region, stride 4;
   entry = {dword@+0, dword@+2} overlapping reads at +0/+2/+0x13c/+0x13e...
   exact struct shape TBC). The index is the ASCII key code, NOT a control id.
2. The value passed to FUN_000500e0 is the HIWORD (sar $0x10) of the dword —
   the low u16 is ignored at these sites.
3. The enclosing function is a KEYBOARD handler: it classifies al against
   literals '4','7',' ','8','J',':','.','<',';','D','-','(',')','$','H','&'
   (0x17317..0x173f0, writing codes 3..0xf to [obj+0x4f37]) — mouse clicks on
   rail/NEXTTURN buttons do NOT route through 0x17488. The t429 assignment's
   "drive clicks across control CLASSES" premise is refuted at the static level:
   a click-driven capture at these two BPs would bank NOTHING.

FUN_000500e0 semantics (already banked, work/coswnd_decomp/500e0.c, re-read
t429): param_1 = audio object (guards [obj+0x213]==-1 / [obj+0x20b]==0 ->
silent no-op), param_2 = MANIFEST INDEX into the soundfx.txt count/name table
([obj+0x700] count, names [obj+0x702+10*i], played as "data\%s.voc" via
s_data__s_voc_00085616 @0x85616 — line 48 of the decompile). Id >= count or < 0
-> FUN_0002a428 vendor error. So the vendor can ONLY play manifest names;
click08 (off-manifest, t395) is unplayable by the vendor through this path.

## T429-B — THIRD CALLER 0x4fb59 = GENERAL PLAY WRAPPER 0x4fb30 [MEASURED]
objdump 0x4fb30..0x4fb5e: prologue, cmp [eax+0x213],-1 / [eax+0x20b],0 guards
(same silent-audio guards), movsx edx,dx, call 0x500e0. So 0x4fb30(obj, id) is
the general "play manifest sfx id" wrapper — ITS callers carry the per-event
ids. Census of 0x4fb30 call sites + how edx is loaded is the decisive offline
probe for "which sample does the vendor play per event" (see T429-C).

## T429-C — THE +0x1bcc TABLE IS batfx.txt, LOADED BY THE BATTLE-CONTROL
## WINDOW CTOR; ITS SITES ARE KEYBOARD HANDLERS, NOT CONTROL CLASSES
[MEASURED: full call-site census of 0x4fb30/0x500e0 over
work/ascend_payload.bin code 0x200..0x82bb0; loader 0x1acd0..0x1aef6;
strings pool-rel: 0x3bd="batfx.txt" @0x82f6d, fmt "%d" @0x82f86,
fmt "%s" @0x82f98, fmt "%d %d %d %d" @0x82f9b — all four referenced ONLY
inside 0x1acd0 (imm scan: 0x1ae25/0x1ae93 for the fmts)]

CENSUS (byte-exact re-scan, FINAL): 0x500e0 called from 3 sites (0x17488,
0x1749b cited + 0x4fb59 inside wrapper 0x4fb30); wrapper called from 32 sites,
ALL eax=0x78638 (single global AUDIO object). Wrapper-site id sources:
13 batfx-table [reg+0x1bcc(+idx*4)] (0x17b02,0x17d37,0x184e4,0x189dd,0x18e50,
0x18f91,0x1913d,0x1928b,0x195a3,0x198d3,0x19ca3,0x19dab,0x19f6a);
1 +0x1bce-twin-via-wrapper (0x1853d); 1 frame-copy of the entry after 0x1ce1c
bounds check (0x1a1bd `mov edx,[esp+0x1ba]`); 8 id0 (below); 6 +0x57 record
(below); 1 imm7 trust01 (0x17917); 2 computed (0x17eca movsx edx,di after
0x1ce1c; 0x180c3 edx preloaded). Original rough pass said "18 table sites" —
superseded by this accounting. Id source per site:
- 18 sites at 0x17af3..0x1a1c2 + 0x17d28/0x184d5/0x189ce/0x18e41/0x18f82/
  0x1912e/0x1927c/0x1958e/0x198c2/0x19c94/0x19d9c/0x19f5b: `mov edx,[reg+
  0x1bcc(+idx*4)]` then `sar edx,0x10` — THE CITED TABLE (batfx entries).
  Enclosing fns 0x17a38/0x17b2c/0x183bc/0x187c0/... are the 1734-byte
  batmode.cpp battle-control window member handlers; the index is the KEY
  entry (0x1a8e count, table base 0x19c6 stride 2, entries stride 4 at
  0x1a90: dword@+0 = {sfx1 u16, sfx2 u16} — overlaps +0x13c/+0x1bcc/+0x1bce
  reads: entry_base = obj+0x1a90+4*key, sfx1 = u16@(base+0x13c-?) — exact
  overlap law: u16[0x19c6+2i] key char i; dword[0x1a90+4i] == u16@0x1bce+4i
  reads: fields land at +0x1bcc = entry+0x13c = {sfx1,sfx2} pair).
- 8 sites `xor edx,edx` (id 0 = "button"): 0x1b0b5/0x1b1ca (batmode window
  click branches — INSIDE rect cmp x0/x1 tests), 0x27e4b, 0x36637 (message
  ids 0x145..0x1d8), 0x47e0e, 0x529fe/0x52a60, 0x549fe. (RE-COUNT via
  byte-exact `31 d2` scan: 8 call addrs 0x1b0b0/0x1b1c5/0x27e46/0x36632/
  0x47e09/0x529f9/0x52a5b/0x549f9, all eax=0x78638.)
- 7 sites `mov edx,[obj+0x57]; sar edx,0x10; cmp edx,-1; je skip`
  (0x30e7a, 0x32214, 0x33374, 0x3afa3, 0x4e458, 0x4e517): per-OBJECT SFX-id
  field +0x57 (unit/gizmo records), -1 = silent.
- 0x1791c: `mov edx,7` = "bang01"? NO — manifest[7] = trust01 (names list
  banked below); 0x17ecf movsx edx,di (computed); 0x180c8 add esi,0x9e path.

LOADER LAW (0x1acd0, batmode.cpp strings, ctor of the battle-control window):
open "batfx.txt" (0x206c0); sscanf "%d" -> [obj+0x1a8e] count (bounds-checked
<=0x64 -> error batmode.cpp:0x1e4/0x1ea); loop count x {sscanf "%s" ->
0x1fe20 (char->u16 key conversion) -> u16 [obj+0x19c6+2i]}; then loop count x
{sscanf "%d %d %d %d" -> four dwords, LOW u16s written to
[obj+0x1a92], [obj+0x1a94], [obj+0x1bce], [obj+0x1bcc+4] per ebx stepping —
i.e. the per-key entry quad (col1,col2,col3,col4)}. THE SFX IDS ARE FILE
COLUMNS 3 AND 4 OF batfx.txt, u16-truncated, read as the HIWORD of the packed
dword. windows.txt SOUNDCHANNEL NEVER TOUCHES THIS TABLE.

batfx.txt CONTENT [MEASURED extracted/ascend00/batfx.txt]: 79 numeric
4-int lines; header line "81" names count... (count line value re-read: "81"
vs 79 numeric lines — TBC, the file may carry 81 numeric lines incl.
single-int lines); key charcode -> line hypothesis (entry i = line i, key =
ASCII code) matches the handler's key-branch literals ('4','7',' ','8',':',
'.','<',';','D','H','J','$','&','(',')','-') EXACTLY for the codes present.
soundfx.txt manifest (86 names, index 0 = "button") banked:
[button shield laser01 ship01 bang01 bang02 bang03 trust01 trust02 destroy
destroy2 shield blueexit redexit gb00..gb09 gh00..gh09 sg33bull..sg70bull
sg33expl..sg70expl ss53/57/63/65/69/75expl orbb00..02 orbex00..02 SG32BULL
SG59BULL SG68BULL SM38EXPL SM72EXPL ST40BULL ST74BULL SM38BULL]
=> the vendor's play path can ONLY emit these 86 names; click08 is
unreachable through 0x4fb30/0x500e0 BY CONSTRUCTION (id-space = manifest).
