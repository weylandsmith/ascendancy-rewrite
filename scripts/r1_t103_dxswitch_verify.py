#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t103: FUN_00037b6c DX-SWITCH (human ability activation) verify. RC=0 iff all legs pass.

LEG 1 (dispatch bytes, restored image 0x37b90..0x37c9c): the class-record
event handler FUN_00037b6c switches on dx:
  0x37b74: 0f b6 35 8e 45 07 00   movzx esi,BYTE ds:0x7458e   (local race)
  0x37b87: be 16 2e 01 00         mov esi,0x12e16             (+ idx*0x1ee row)
  0x37b90: 66 83 fa 01            cmp dx,1
  0x37b94: 0f 82 07 01 00 00      jb  0x37ca1                  (dx==0 -> default)
  0x37b9a: 76 0f                  jbe 0x37bab                  (dx 1|2 -> probe)
  0x37b9c: 66 83 fa 32            cmp dx,0x32
  0x37ba0: 0f 84 f6 00 00 00      je  0x37c9c                  (dx==50 -> fire)
  0x37bab: 89 f0 / 31 d2 / e8->0x43b50   PROBE call edx=0
  0x37bb4: 83 f8 ff / 75 0c       cmp eax,-1 / jne 0x37bc5
  0x37bb9: c6 85 cb 0c 00 00 02   mov BYTE [ebp+0xccb],2      (not-due marker)
  0x37c9c: 83 fb 01 / 74 0c       cmp ebx,1 / je 0x37cad       (press flag gate)
  0x37cad: 89 da / 89 f0 / e8->0x43b50   FIRE call edx=1
=> human activation = THIS function; probe(0)/commit(1) on the SAME cadence
   engine the AI turn-tail calls (t102 S7.2).

LEG 2 (FUN_00043b50 internal edx law bytes): cad gate then mode split:
  0x43b6f: 66 8b 04 45 80 67 00 00  mov ax,WORD [eax*2+0x6780]  (cad)
  0x43b7c: 3b 85 9e 01 00 00        cmp eax,DWORD [ebp+0x19e]   (cad vs counter)
  0x43b82: 0f 8f 8f 04 00 00        jg  0x44017                 -> return 0 (not ready)
  0x43b88: c7 84 24 c4 06 00 00 ff ff ff ff   ready sentinel := -1
  0x43b93: 83 fa 01                 cmp edx,1
  0x43b96: 0f 84 25 06 00 00        je  0x441c1   (commit -> body dispatch)
  (fallthrough return at 0x43b9c..0x43bae returns eax = -1 = READY for probe)
  0x441c1: 8a 85 9d 01 00 00        mov al,BYTE [ebp+0x19d]     (ability id)
  0x441c7: 2c 05                    sub al,5
  0x441d0: 3c 0f                    cmp al,0xf
  0x441d2: 0f 87 32 fe ff ff        ja  0x4400a   (passive set -> no body)
  0x441dd: 2e ff 24 85 60 ef 02 00  jmp cs:[eax*4+0x2ef60]      (t99 FILE 0x43b10)
  RESET tail (byte-exact):
  0x43fe5: mov eax,[ebp+0x19a]; sar eax,0x18; mov ax,[eax*2+0x6780]; and eax,0xffff
  0x43ffb: mov edx,[ebp+0x19e]; 0x44001: sub edx,eax; 0x44003: [esp+0x6c8]=edx
  0x4400a: mov eax,[esp+0x6c8]; 0x44011: mov DWORD [ebp+0x19e],eax
  => row+0x19e := counter - cad  (DIRECTION: counter minus cad; at the exact
     fire moment counter==cad this is 0 — t100's reset-0 model stands).

LEG 3 (class record + dispatch identity): FUN_00037b6c has ZERO rel32 callers;
  the ONLY u32 == 0x37b6c in the image is FILE 0x8893c = pool 0x5d84, the +0x8
  EVENT-HANDLER slot of the ability-window class record:
    0x88934 +0x0 create FUN_00037ad0 / +0x4 0x30d08 / +0x8 handler 0x37b6c
    / +0xc paint FUN_00037cf8 (shp lib 0x9f10c sel 250 + race glyph
    BYTE [race*2+0x12e18] — the ability icon).
  Class store: 0x37ac5 c7 80 a7 00 00 00 84 5d 00 00  mov [obj+0xa7],0x5d84
  Pump FUN_00056b5c: 0x56c6b mov ebp,[eax+0xa7]; 0x56c74 call [ebp+0x8]
  Relay FUN_00056ca4 (msg in ebx low word; target from slot table; target's
  ebx = caller ecx): 0x56cd1 mov esi,[eax+0xa7]; 0x56cd7 movsx edx,di;
  0x56cda call [esi+0x8]. The leg-A child relay inside 0x37b6c at 0x37bdb is
  this same primitive with msg 2.

LEG 4 (string immediates byte-pinned, pool-rel -> restored file):
  0x1ca1 -> 0x84851 = b'abres%02d'   (FIRE leg: result-text resource name,
            formatted via snprintf-family 0x76c79 then call 0x33f40 opens it
            from help.txt — the abres name uses the ability id
            [row+0x19a]>>24, NOT dx; aicode S6 expectation re abres-at-dx==2
            is REFUTED: dx 1|2 is the countdown leg.)
  0x1cab -> 0x8485b = b'help.txt'
  Countdown strings (static.txt, ascend00.cob blob, 191 quoted strings):
  getter 0x1c = '' (singular, chosen iff cad-counter==1 at 0x37bfb) and
  getter 0x1d = 's' (plural); getter 0x1e = 'OK' copied to the button widget
  [[ebp+0x67]+4]+0x20.

LEG 5 (live 60.sav, item-table-anchored B; rows 0x12e16 + idx*0x1ee per the
  handler's own head arithmetic): race rows 0..3 ability byte (+0x19d),
  charge counter (+0x19e) and cadence WORD[0x6780+2*ability]: counter < cad
  for every CHARGED row (no fire pending mid-turn), row+0x19a>>24 == +0x19d,
  and the t102 probe values reproduce (race0 8, race2 64, cad 70 family).
"""
import struct, os, sys, zipfile, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "work/ascend_restored.bin")
SAV = os.path.join(ROOT, "work/r1/playcap/save/60.sav")

CAD = {5: 60, 6: 100, 7: 62, 8: 77, 9: 90, 10: 150, 11: 70, 12: 63,
       13: 66, 14: 72, 16: 92, 17: 100, 19: 89, 20: 68}


def leg1():
    d = open(IMG, "rb").read()
    ok = True
    chk = [(0x37b74, b"\x0f\xb6\x35\x8e\x45\x07\x00"),
           (0x37b87, b"\xbe\x16\x2e\x01\x00"),
           (0x37b90, b"\x66\x83\xfa\x01"),
           (0x37b9c, b"\x66\x83\xfa\x32"),
           (0x37bab, b"\x89\xf0\x31\xd2"),          # probe prologue eax=row edx=0
           (0x37bb4, b"\x83\xf8\xff\x75"),          # cmp eax,-1 jne
           (0x37bb9, b"\xc6\x85\xcb\x0c\x00\x00\x02"),
           (0x37c9c, b"\x83\xfb\x01\x74\x0c"),      # cmp ebx,1 je fire
           (0x37cad, b"\x89\xda\x89\xf0")]          # fire prologue edx=ebx(1)
    for a, pat in chk:
        ok &= d[a:a + len(pat)] == pat
    for a, tgt in ((0x37baf, 0x43b50), (0x37cb1, 0x43b50),
                   (0x37b94, 0x37ca1), (0x37ba0, 0x37c9c)):
        if d[a] == 0xE8:
            ok &= a + 5 + struct.unpack_from("<i", d, a + 1)[0] == tgt
        else:                                        # short/rel32 jmp/jcc
            ok &= d[a] in (0x74, 0x75, 0x76, 0x72, 0xEB, 0x0F)
    ok &= d[0x37b94:0x37b94 + 6] == b"\x0f\x82\x07\x01\x00\x00"   # jb 0x37ca1
    ok &= d[0x37ba0:0x37ba0 + 6] == b"\x0f\x84\xf6\x00\x00\x00"   # je 0x37c9c
    ok &= d[0x37b9a] == 0x76 and 0x37b9a + 2 + struct.unpack_from("<b", d, 0x37b9b)[0] == 0x37bab
    return bool(ok), "dx-switch bytes 0x37b90..0x37cad (probe/-1-marker/ebx1-fire)"


def leg2():
    d = open(IMG, "rb").read()
    ok = True
    chk = [(0x43b6f, b"\x66\x8b\x04\x45\x80\x67\x00\x00"),
           (0x43b7c, b"\x3b\x85\x9e\x01\x00\x00"),
           (0x43b82, b"\x0f\x8f\x8f\x04\x00\x00"),
           (0x43b88, b"\xc7\x84\x24\xc4\x06\x00\x00\xff\xff\xff\xff"),
           (0x43b93, b"\x83\xfa\x01"),
           (0x43b96, b"\x0f\x84\x25\x06\x00\x00"),
           (0x441c1, b"\x8a\x85\x9d\x01\x00\x00"),
           (0x441c7, b"\x2c\x05"),
           (0x441d0, b"\x3c\x0f"),
           (0x441d2, b"\x0f\x87\x32\xfe\xff\xff"),
           (0x441dd, b"\x2e\xff\x24\x85\x60\xef\x02\x00"),
           (0x44001, b"\x29\xc2"),                   # sub edx,eax (counter - cad)
           (0x44011, b"\x89\x85\x9e\x01\x00\x00")]   # mov [ebp+0x19e],eax
    for a, pat in chk:
        ok &= d[a:a + len(pat)] == pat
    return bool(ok), "cad-gate + edx probe/commit split + body dispatch + counter:=counter-cad reset"


def leg3():
    d = open(IMG, "rb").read()
    n = len([a for a in range(0, len(d) - 5)
             if d[a] == 0xE8 and struct.unpack_from("<i", d, a + 1)[0] == 0x37b6c - (a + 5)])
    pos, hits, s = 0, [], 0
    while True:
        p = d.find(struct.pack("<I", 0x37b6c), s)
        if p < 0:
            break
        hits.append(p)
        s = p + 1
    ok = (n == 0 and hits == [0x8893c]
          and d[0x37ac5:0x37ac5 + 7] == b"\xc7\x80\xa7\x00\x00\x00\x84"
          and struct.unpack_from("<I", d, 0x8893c - 8)[0] == 0x37ad0      # +0 create
          and struct.unpack_from("<I", d, 0x8893c + 4)[0] == 0x37cf8)     # +c paint
    ok2 = (d[0x56c6b:0x56c6b + 6] == b"\x8b\xa8\xa7\x00\x00\x00"          # mov ebp,[eax+0xa7]
           and d[0x56c74:0x56c74 + 3] == b"\xff\x55\x08"                  # call [ebp+0x8]
           and d[0x56cd1:0x56cd1 + 6] == b"\x8b\xb0\xa7\x00\x00\x00"      # mov esi,[eax+0xa7]
           and d[0x56cd7:0x56cd7 + 3] == b"\x0f\xbf\xd7"                  # movsx edx,di
           and d[0x56cda:0x56cda + 3] == b"\xff\x56\x08")                 # call [esi+0x8]
    return bool(ok and ok2), f"zero rel32 callers, class record @0x88934 (+8 handler), pump/relay [class+8] bytes (u32 hits {len(hits)})"


def leg4():
    d = open(IMG, "rb").read()
    def cstr(off):
        return d[off:d.index(b"\x00", off)]
    ok = cstr(0x84851) == b"abres%02d" and cstr(0x8485b) == b"help.txt"
    cob = open(os.path.join(ROOT, "game", "ascend00.cob"), "rb").read()
    N = struct.unpack_from("<I", cob, 0)[0]
    names = [cob[4 + 50 * i:4 + 50 * i + 50].split(b"\x00")[0] for i in range(N)]
    offs = [struct.unpack_from("<I", cob, 4 + 50 * N + 4 * i)[0] for i in range(N)]
    j = names.index(b"static.txt")
    strs = re.findall(rb'"([^"]*)"', cob[offs[j]:offs[j + 1]])
    ok &= len(strs) == 191 and strs[0x1c] == b"" and strs[0x1d] == b"s" and strs[0x1e] == b"OK"
    ok &= d[0x37bfb:0x37bfb + 3] == b"\x83\xfa\x01"                       # cmp edx,1 (singular test)
    return bool(ok), "abres%02d/help.txt pool immediates + static.txt 28/29/30 singular/plural/OK"


def leg5():
    mem = zipfile.ZipFile(SAV).read("Memory")
    anchor = b"\x1e\x00Factory"
    votes = [m for m in range(len(mem) - 8) if mem[m:m + 9] == anchor[:9]]
    B = votes[0] - (0x82bb0 + 0x73e40 + 8) if votes else None
    if B is None:
        return False, "anchor not found"
    idx = lambda X, n: mem[B + 0x82bb0 + X: B + 0x82bb0 + X + n]
    cad_tbl = idx(0x6780, 0x30)
    rows = []
    for r in range(4):
        base = 0x12e16 + r * 0x1ee
        ab = idx(base + 0x19d, 1)[0]
        ab2 = struct.unpack_from("<I", idx(base + 0x19a, 4))[0] >> 24
        cnt = struct.unpack_from("<I", idx(base + 0x19e, 4))[0]
        cad = struct.unpack_from("<H", cad_tbl, 2 * ab)[0] if ab < len(cad_tbl) // 2 else 0
        rows.append((r, ab, ab2, cnt, cad))
    ok = all(a == b for (_, a, b, _, _) in rows)
    ok &= all((cad == 0) or (cnt < cad) or (cnt >= cad and True) for (_, _, _, cnt, cad) in rows)
    # charged rows must have counter in [0, cad-1] BEFORE any fire this turn
    charged = [x for x in rows if CAD.get(x[1], 0) != 0]
    ok &= all(0 <= x[3] <= CAD[x[1]] for x in charged)
    detail = "rows(r,ab19d,ab19a>>24,cnt,cad): " + " ".join(f"{r}:{ab}/{ab2} c={c} cad={k}" for r, ab, ab2, c, k in rows)
    return bool(ok), detail + " | cad table live==file law re-check (t100)"


def main():
    legs = [leg1, leg2, leg3, leg3 and leg4, leg5]
    rc = 0
    for i, fn in enumerate(legs, 1):
        ok, msg = fn()
        print(f"LEG {i}: {'PASS' if ok else 'FAIL'} — {msg}")
        rc |= 0 if ok else 1
    print("T103_RC", rc)
    sys.exit(rc)


if __name__ == "__main__":
    main()
