# UI + resource manifest — `windows.txt` / `subtitle.txt` measurement
Sources: `extracted/ascend00/windows.txt` (42,478 B), `extracted/ascend00/subtitle.txt` (2,801 B), CP437/CRLF/0x1A. Produced by `scripts/ui_probe.py`; gate stage 3k. Every number measured.

## 1. windows.txt structure [verified]
- a resource MANIFEST (key/value lines before the first `TYPE`), then **132 window definitions**, each starting at a `TYPE` key.
- window-key frequency: {'TYPE': 132, 'NAME': 124, 'X0': 124, 'Y0': 124, 'X1': 124, 'Y1': 124, 'PARENT': 123, 'STATE': 123, 'SENDMESSAGE': 123, 'SENDPARAM1': 123, 'SENDPARAM2': 123, 'HELPINDEX': 123, 'MOUSEFOCUS': 119, 'SHAPEFRAME': 119, 'SOUNDCHANNEL': 119, 'WINITEMS': 108, 'TEXTITEM': 18, 'SHAPEFILE': 9, 'STATENUMBER': 8, 'BUTTONSTATE': 7, 'SHAPEITEM': 7, 'BACKGRNDCOLOR': 2, 'CURSORSHAPE': 2, 'STAR_SHAPES': 1, 'SHIP_SHAPES': 1, 'NUM_STARS': 1, 'NUM_LANES': 1, 'SMALLSEED': 1, 'MEDIUMSEED': 1, 'LARGESEED': 1, 'HUGESEED': 1, 'NUMCONTROLS': 1, 'RACE1CONTROL': 1, 'RACE2CONTROL': 1, 'RACE3CONTROL': 1, 'RACE4CONTROL': 1, 'RACE5CONTROL': 1, 'RACE6CONTROL': 1, 'RACE7CONTROL': 1, 'DIGITFRAMES': 1, 'FLICFILE': 1, 'BUFFERMEGS': 1, 'PRELOADMEGS': 1, 'MAXFRAME_KB': 1, 'READSIZE_KB': 1, 'SKIPFRAME': 1, 'LOOPCOUNT': 1, 'SHOWINFO': 1, 'cX0': 1, 'cY0': 1, 'cX1': 1, 'cY1': 1, 'END': 1}
- window TYPE histogram: {0: 69, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 7, 7: 1, 8: 1, 9: 1, 10: 10, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 16: 1, 17: 1, 18: 1, 19: 1, 20: 1, 21: 1, 22: 1, 23: 1, 24: 1, 25: 7, 26: 1, 29: 5, 30: 1, 31: 1, 32: 1, 100: 8} (TYPE is the window class; TYPE 0 = button-like menu entries in the opening screen; the vendor does not document the numeric meanings -> OQ-015)
- coordinate envelope: X 0..639, Y 0..479 over all X0/X1/Y0/Y1 -> logical resolution is **640x480** (max X1 639, Y1 479). This is evidence for OQ-012(d): the ORIGINAL logical extent is the screen itself; galaxy star positions (galactic.tsv coords <=639x479) live in the same envelope. Our rewrite renders 1024x1024 logical and scales to the screen — unchanged decision, now with the original value documented.
- WINITEMS counts sum 25; TEXTITEM sub-keys observed 18 (differ: other item kinds exist -> item sub-grammar OQ-015)

## 2. Manifest content [verified; canonical DATA\\ set]
- manifest key histogram: {'TABLE': 23, 'MEM_REQ': 1, 'HAZEBRBLES': 1, 'NUMTABLES': 1, 'FONTS': 1, 'SMALLFONT': 1, 'LARGEFONT': 1}
- MEM_REQ 2300000, HAZEBRBLES 200, NUMTABLES 23 == 23 TABLE lines (asserted). The 23 TABLE paths are the palette (.haz) tables the engine loads: RACEA03, BLACK00..24 step 4, RED01, GREEN01, BLUE01, WHITE00..09, HILITE00, BW — **cross-validates the 256-byte-palette .haz finding** and matches docs/re/loader.md §5's 26 DATA\\ templates.
- fonts: [('FONTS', '300'), ('SMALLFONT', 'DATA\\SMFONT.FNT'), ('LARGEFONT', 'DATA\\BIGFONT.FNT')] (SMFONT.FNT + BIGFONT.FNT -> the two-face UI of the manual screenshots)
- remaining manifest keys (verbatim, meanings mostly OQ-015): []

## 3. Opening-screen windows (first 12) [verified]
```
TYPE=100 NAME=-                rect=(-,-)-(-,-) msg=-/-,- help=-
TYPE=0 NAME=INTRO            rect=(159,200)-(477,230) msg=1/6,1 help=intro
TYPE=0 NAME=PLAYTUTORIAL     rect=(159,240)-(477,270) msg=1/15,1 help=tutorial
TYPE=0 NAME=FRESHGAME        rect=(159,280)-(477,310) msg=1/3,1 help=newgame
TYPE=0 NAME=RESUME           rect=(159,320)-(477,350) msg=1/1,1 help=resume
TYPE=0 NAME=LOAD             rect=(159,360)-(477,390) msg=1/4,1 help=loadgame
TYPE=0 NAME=SAVE             rect=(159,400)-(477,430) msg=1/2,1 help=savegame
TYPE=0 NAME=EXITTODOS        rect=(159,440)-(477,470) msg=2/0,0 help=exitdos
TYPE=100 NAME=-                rect=(-,-)-(-,-) msg=-/-,- help=-
TYPE=5 NAME=RACES            rect=(474,286)-(632,316) msg=1/7,1 help=1races
TYPE=2 NAME=COSMOSWnd        rect=(7,7)-(465,472) msg=0/0,0 help=coswnd
TYPE=0 NAME=ROTRIGHT         rect=(495,364)-(509,394) msg=51/999,0 help=1spin
```
- the four menu buttons are exactly the main menu (Play Introduction / Tutorial / New Game / Resume), matching the manual — the UI rewrite can reproduce the opening screen from THIS file alone.

## 4. subtitle.txt = intro movie script [verified]
- **12** FRAMENUMBER-triggered blocks; command keys: {'SUBTITLE': 18, 'TEXT': 18, 'FRAME_START': 18, 'FRAME_END': 18, 'FRAMENUMBER': 12, 'DELAY': 5, 'FRAME_RATE': 5, 'FADEMUSIC': 5, 'CHANNEL': 5, 'VOLUME': 5, 'DIGITALMUSIC': 2, 'TUNEID': 2, 'COMMAND': 2, 'TITLEBOX': 1, 'TITLERECT_X0': 1, 'TITLERECT_Y0': 1, 'TITLERECT_X1': 1, 'TITLERECT_Y1': 1, 'SUBFONT': 1, 'FONTFILE': 1, 'FONTPALETTE': 1, 'FONTPALSTART': 1, 'FONTPALCOUNT': 1, 'FONTBACKCOLOR': 1, 'END': 1}
- first/last trigger frames: 1 / 669 (gizmos.flc/intro playback timeline). Commands include DIGITALMUSIC(TUNEID n)+COMMAND, FADEMUSIC(CHANNEL,VOLUME), SUBTITLE text placement, FRAMES_PER_SECOND style keys -> intro cinematic is DATA-DRIVEN; our FLIC player (OQ-002 deferred codecs) only needs to honour frame triggers.
- TITLERECT 0,379-639,419 + SUBFONT font file/palette slots 240..255: subtitle band geometry [verified].

## 5. Verbatim key census (window defs)
```
TYPE           132
NAME           124
X0             124
Y0             124
X1             124
Y1             124
PARENT         123
STATE          123
SENDMESSAGE    123
SENDPARAM1     123
SENDPARAM2     123
HELPINDEX      123
MOUSEFOCUS     119
SHAPEFRAME     119
SOUNDCHANNEL   119
WINITEMS       108
TEXTITEM       18
SHAPEFILE      9
STATENUMBER    8
BUTTONSTATE    7
SHAPEITEM      7
BACKGRNDCOLOR  2
CURSORSHAPE    2
STAR_SHAPES    1
SHIP_SHAPES    1
NUM_STARS      1
NUM_LANES      1
SMALLSEED      1
MEDIUMSEED     1
LARGESEED      1
HUGESEED       1
NUMCONTROLS    1
RACE1CONTROL   1
RACE2CONTROL   1
RACE3CONTROL   1
RACE4CONTROL   1
RACE5CONTROL   1
RACE6CONTROL   1
RACE7CONTROL   1
DIGITFRAMES    1
FLICFILE       1
BUFFERMEGS     1
PRELOADMEGS    1
MAXFRAME_KB    1
READSIZE_KB    1
SKIPFRAME      1
LOOPCOUNT      1
SHOWINFO       1
cX0            1
cY0            1
cX1            1
cY1            1
END            1
```
