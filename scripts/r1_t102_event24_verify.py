#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t102: EVENT-24 (SA_) CONSUMER DECODE verify. RC=0 iff all legs pass.

LEG 1 (pump type-switch law, restored image 0x55cbc..0x55db1): the record
TYPE tree routes 24 (0x18) to the ring-maintenance null arm — cited bytes:
  0x55d02: 83 f9 17        cmp $0x17,%ecx
  0x55d0d: 83 f9 19        cmp $0x19,%ecx
  0x55d10: e9 ..           jmp 0x55d69   (type==24 falls here after jb miss)
  0x55d12: 83 f9 16        cmp $0x16,%ecx
  0x55d15: e9 ..           jmp 0x55d69   (type==22)
  0x55d69: 85 c9           test %ecx,%ecx
  0x55d6f: ring maintenance (read cursor ++, wrap-zero both cursors)
  0x55da1: 74 ..           je 0x55db1    (edi==0 -> NO 0x56ad4 re-arm)
and 0x55b99 xor edi,edi precedes the switch (edi=0 for the 24 path).
LEG 2 (dispatch-site census law): FUN_00043b50 has EXACTLY the three rel32
callers {0x37baf, 0x37cb1, 0x3eb3c}, and the 0x3eb3c gate bytes are
  0x3eb22: 8a 35 8e 45 07 00   mov ds:0x7458e,%dh
  0x3eb28: 3a 31               cmp (%ecx),%dh
  0x3eb2a: 75 09               jne 0x3eb35
  0x3eb2c: 83 3d a4 0b 01 00 ff  cmpl $-1,ds:0x10ba4
  0x3eb33: 75 0c               jne 0x3eb41  (local race skips unless -1)
  0x3eb35: ba 01 00 00 00      mov $1,%edx
  0x3eb3c: call 0x43b50
=> SA_ bodies run SYNCHRONOUSLY for every race != ds:0x7458e always; the
   0x7458e race calls only when ds:0x10ba4 == -1 (netplay all-local).
LEG 3 (event-24 producer gate, FUN_0003e6e0 tail): cited bytes
  0x3e7d5: 8a 15 8e 45 07 00   mov ds:0x7458e,%dl
  0x3e7dc: 8a 45 00            mov 0x0(%ebp),%al
  0x3e7e5: 38 d0               cmp %dl,%al
  0x3e7e7: 75 31               jne 0x3e81a   (event 24 ONLY for race==0x7458e)
  0x3e803: 39 d8               cmp %ebx,%eax  (counter == cad EXACT)
  0x3e807: ba 18 00 00 00      mov $0x18,%edx
  0x3e80c: b8 5c a3 07 00      mov $0x7a35c,%eax
  0x3e815: call 0x55a60
Producer and sync-dispatch gates are the SAME equality: the local race's
row queues event 24 (no effect arm) INSTEAD of calling the bodies at
0x3eb3c; the human UI path is FUN_00037b6c (edx=ebx=1 at 0x37cb1).
LEG 4 (order-executor drain law, F8b sites): jump table FILE 0x41244
(7 u32 == [0x419cf,0x41cc6,0x41bb3,0x41ded,0x41ded,0x41ded,0x41c56]) and
drain leg bytes
  0x41df4: 66 8b 86 88 00 00 00   mov WORD [ship+0x88],%ax
  0x41dfb: c7 86 94 00 00 00 00   movl $0,[ship+0x94]
  0x41e05: 29 c3                  sub %eax,%ebx
  0x41e07: c7 86 88 00 00 00 00   movl $0,[ship+0+0x88]
  0x41e19: jmp 0x41b8f
plus arrival dec 0x41d80 ff 8e 88 00 00 00 (decl [ship+0x88]).
LEG 5 (live 60.sav, item-table-anchored): mid-turn state consistent with
the laws — queue EMPTY (hi word of dword[obj+0x4758] == 0 at object
0x7a35c), ds:0x10ba4 == 0 (singleplayer: sync dispatch active for AI
races only), ds:0x7458e == race0 byte, and ALL zero-POWER ship rows carry
[rec+0x52] > T (mid-transit ETA stamps) with order-state [rec+0x5d] == 0
(the drain/arrival signature). Correlation check, NOT closure of F8b.
"""
import struct, os, sys, zipfile, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "work/ascend_restored.bin")
SAV = os.path.join(ROOT, "work/r1/playcap/save/60.sav")


def rel32_callers(d, target):
    return [a for a in range(0, len(d) - 5)
            if d[a] == 0xE8 and struct.unpack_from("<i", d, a + 1)[0] == target - (a + 5)]


def leg1():
    d = open(IMG, "rb").read()
    ok = True
    chk = [(0x55d02, b"\x83\xf9\x17"), (0x55d05, b"\x72\x0b"),
           (0x55d0d, b"\x83\xf9\x19"), (0x55d12, b"\x83\xf9\x16"),
           (0x55d67, b"\x85\xc9"),          # test %ecx,%ecx (type==0 -> 0x55bae)
           (0x55d69, b"\x0f\x84\x3f\xfe\xff\xff"),  # je 0x55bae
           (0x55b99, b"\x31\xff")]          # xor edi,edi precedes the switch
    for a, pat in chk:
        ok &= d[a:a + len(pat)] == pat
    for a in (0x55d10, 0x55d15):            # jmp SHORT 0x55d69 (24 / 21-22 arms)
        ok &= d[a] == 0xEB and a + 2 + struct.unpack_from("<b", d, a + 1)[0] == 0x55D69
    a = 0x55da1                               # je 0x55db1 (edi==0 -> no re-arm)
    ok &= d[a] == 0x74 and a + 2 + struct.unpack_from("<b", d, a + 1)[0] == 0x55DB1
    return bool(ok), "type-24 null arm + edi==0 no-re-arm bytes @0x55cbc..0x55db1"


def leg2():
    d = open(IMG, "rb").read()
    cs = set(rel32_callers(d, 0x43B50))
    ok = cs == {0x37baf, 0x37cb1, 0x3eb3c}
    chk = [(0x3eb22, b"\x8a\x35\x8e\x45\x07\x00"), (0x3eb28, b"\x3a\x31"),
           (0x3eb2a, b"\x75\x09"), (0x3eb2c, b"\x83\x3d\xa4\x0b\x01\x00\xff"),
           (0x3eb33, b"\x75\x0c"), (0x3eb35, b"\xba\x01\x00\x00\x00")]
    for a, pat in chk:
        ok &= d[a:a + len(pat)] == pat
    ok &= d[0x3eb3c] == 0xE8 and 0x3eb3c + 5 + struct.unpack_from("<i", d, 0x3eb3d)[0] == 0x43B50
    return bool(ok), f"callers=={{0x37baf,0x37cb1,0x3eb3c}} (got {sorted(hex(x) for x in cs)}) + gate bytes"


def leg3():
    d = open(IMG, "rb").read()
    chk = [(0x3e7d5, b"\x8a\x15\x8e\x45\x07\x00"), (0x3e7dc, b"\x8a\x45\x00"),
           (0x3e7e5, b"\x38\xd0"), (0x3e7e7, b"\x75\x31"),
           (0x3e803, b"\x39\xd8"), (0x3e807, b"\xba\x18\x00\x00\x00"),
           (0x3e80c, b"\xb8\x5c\xa3\x07\x00")]
    ok = all(d[a:a + len(p)] == p for a, p in chk)
    ok &= d[0x3e815] == 0xE8 and 0x3e815 + 5 + struct.unpack_from("<i", d, 0x3e816)[0] == 0x55A60
    return bool(ok), "event-24 producer gate bytes @0x3e7c0..0x3e815"


def leg4():
    d = open(IMG, "rb").read()
    want = [0x419cf, 0x41cc6, 0x41bb3, 0x41ded, 0x41ded, 0x41ded, 0x41c56]
    ent = [struct.unpack_from("<I", d, 0x41244 + 4 * k)[0] for k in range(7)]
    ok = ent == want
    chk = [(0x41df4, b"\x66\x8b\x86\x88\x00\x00\x00"),
           (0x41dfb, b"\xc7\x86\x94\x00\x00\x00\x00"),
           (0x41e05, b"\x29\xc3"),
           (0x41e07, b"\xc7\x86\x88\x00\x00\x00\x00"),
           (0x41d80, b"\xff\x8e\x88\x00\x00\x00")]
    ok &= all(d[a:a + len(p)] == p for a, p in chk)
    ok &= d[0x41e19] == 0xE9 and 0x41e19 + 5 + struct.unpack_from("<i", d, 0x41e1a)[0] == 0x41B8F
    return bool(ok), f"drain leg + jump table FILE 0x41244 (7/7, got {[hex(x) for x in ent]})"


def leg5():
    m = zipfile.ZipFile(SAV).read("Memory")
    hits = {mo.start() - (0x82bb0 + 0x73e40 + 8)
            for mo in re.finditer(rb"\x1e\x00Factory", m)}
    if len(hits) != 1:
        raise SystemExit("harness-error: item-table anchor not unique")
    B = hits.pop()
    g4 = lambda X: struct.unpack_from("<I", m, B + 0x82bb0 + X)[0]
    g1 = lambda X: m[B + 0x82bb0 + X]
    T = g4(0x12E10)
    obj = 0x7A35C
    q = g4(obj + 0x4758) >> 16
    mode = g4(0x10BA4)
    local = g1(0x7458E)
    race0 = g1(0x12E16)
    base = B + 0x82bb0 + 0x3a095
    n = min(g4(0x43489) >> 16, 0x6B)
    tot = sig = 0
    for k in range(n):
        r = base + k * 0x162
        if struct.unpack_from("<I", m, r + 0x54)[0] >> 16 >= 20:
            continue
        if struct.unpack_from("<I", m, r + 0x88)[0] != 0:
            continue
        tot += 1
        d52 = struct.unpack_from("<I", m, r + 0x52)[0]
        st = struct.unpack_from("<I", m, r + 0x5d)[0]
        sig += d52 > T and st == 0
    ok = q == 0 and mode == 0 and local == race0 and tot == 5 and sig == 5
    return bool(ok), (f"queue_hi={q} 0x10ba4={mode} local_race={local}==race0 "
                      f"zero-power rows={tot} with ETA(b52>T)+state5d==0: {sig}/5")


def main():
    rc = 0
    for name, fn in (("pump-null-arm", leg1), ("dispatch-census", leg2),
                     ("producer-gate", leg3), ("drain-leg", leg4),
                     ("live-consistency", leg5)):
        try:
            ok, msg = fn()
        except SystemExit:
            raise
        except Exception as e:
            ok, msg = False, f"EXC {e!r}"
        print(f"{name}: {'OK' if ok else 'FAIL'}  {msg}")
        rc |= 0 if ok else 1
    print("RC=", rc)
    return rc


if __name__ == "__main__":
    sys.exit(main())
