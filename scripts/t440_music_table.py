#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""t440_music_table.py — read the vendor's LOADED music tune table out of
banked save states and prove the TUNEID index base. No debugger session.

LAW (measured t440, docs/re/_wip_t440.md F1/F4):
  * The subtitle type-word dispatch 0x2ee9e sends DIGITALMUSIC (type 0x1e) to
    0x2ee3b: `mov eax, AUDIO_OBJ_FIXUP; mov edx,[rec+0x208]; movsx; call
    0x4f86c`. FUN_0004f86c indexes names at obj+0x37a + tuneid*28 (0x4f929..
    0x4f945: *8, -tuneid, <<2) with NO bias, bounds-checked against
    WORD[obj+0x6fa] (0x4f89a).
  * SAVE COORDINATES: a guest LINEAR address L lives at Memory-member offset
    L + H (H from the BDA signature). The audio object is .bss (data-segment
    base 0x242000 + 0x78638) — it exists ONLY in a save, never in the payload.
  * The object's runtime linear is run-independent, but we do not assume it:
    we locate the dispatch site in the member by its stable tail
    `8b 92 08 02 00 00` (mov edx,[edx+0x208]) and read the `b8 imm32`
    (opcode 0xb8) immediately before it -> the fixup VALUE = object linear.

EXIT: 0 = every save decoded and agrees with the cited law (intro00@6,
intro01@7, WORD[+0x6fa]==29); 1 = negative/mismatch; 2 = harness error.
"""
import argparse, os, re, struct, sys, zipfile

TAIL = bytes.fromhex("8b9208020000")   # mov edx,[edx+0x208]  (TUNEID load)
MOV_EAX = 0xB8                          # mov eax, imm32
F_COUNT, F_CUR, F_TBL, PITCH = 0x6fa, 0x6fc, 0x37a, 28


def bda_h(mem):
    return [h for h in range(0, 0x2000)
            if struct.unpack_from("<H", mem, h + 0x413)[0] == 0x280
            and struct.unpack_from("<H", mem, h + 0x44A)[0] == 80]


def cstring_at(mem, off, limit=64):
    if off < 0 or off >= len(mem):
        return None
    end = mem.find(b"\0", off, off + limit)
    if end < 0:
        return None
    raw = mem[off:end]
    if not raw or any(c < 0x20 or c > 0x7e for c in raw):
        return None
    return raw.decode("ascii")


def audio_object(mem, H):
    """Locate the audio object's guest LINEAR via the dispatch-site fixup."""
    for m in re.finditer(re.escape(TAIL), mem):
        p = m.start()
        if p >= 5 and mem[p - 5] == MOV_EAX:      # b8 imm32 then the tail
            imm = struct.unpack_from("<I", mem, p - 4)[0]
            if 0x100000 < imm < 0x400000:
                return imm, p - H
    return None, None


def read_table(mem, H, esi):
    """Apply the 0x4f86c index law to the save's RAM."""
    def u16(lin):
        return struct.unpack_from("<H", mem, lin + H)[0]
    def name(i):
        return cstring_at(mem, esi + H + F_TBL + i * PITCH)
    count = u16(esi + F_COUNT)
    names = [name(i) for i in range(min(count, 64))]
    return count, u16(esi + F_CUR), names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saves", default="work/r1/bank-t438-ring-2200",
                    help="directory of banked .sav files")
    ap.add_argument("--one", help="single .sav path (overrides --saves)")
    args = ap.parse_args()

    if args.one:
        files = [args.one]
    else:
        files = sorted((os.path.join(args.saves, f) for f in os.listdir(args.saves)
                        if f.endswith(".sav")),
                       key=lambda p: int(re.search(r"(\d+)\.sav$", p).group(1)))
    if not files:
        print(f"harness-error: no .sav in {args.saves}")
        return 2

    ok_all, n_ok = True, 0
    for f in files:
        try:
            mem = zipfile.ZipFile(f).read("Memory")
        except Exception as e:
            print(f"{os.path.basename(f)}: harness-error {e}")
            ok_all = False
            continue
        hs = bda_h(mem)
        if len(hs) != 1:
            print(f"{os.path.basename(f)}: H ambiguous {hs}")
            ok_all = False
            continue
        H = hs[0]
        esi, site = audio_object(mem, H)
        if esi is None:
            print(f"{os.path.basename(f)}: dispatch site not found (negative)")
            ok_all = False
            continue
        count, cur, names = read_table(mem, H, esi)
        e6, e7 = (names + [None] * 8)[6], (names + [None] * 8)[7]
        verdict = (count == 29 and e6 == "data\\intro00.raw"
                   and e7 == "data\\intro01.raw")
        n_ok += verdict
        ok_all &= verdict
        print(f"{os.path.basename(f):8s} H={H:#x} esi={esi:#x} site={site:#x} "
              f"count={count} cur={cur} [6]={e6} [7]={e7} "
              f"{'OK' if verdict else 'MISMATCH'}")

    print(f"\n{len(files)-n_ok} mismatched / {n_ok}/{len(files)} agree with the "
          f"cited 0-based law (intro00@6, intro01@7, count 29)")
    if ok_all:
        print("VERDICT PASS: TUNEID is a ZERO-BASED index into the music.txt-"
              "order table (obj+0x37a + tuneid*28, 0x4f929..0x4f945)")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
