#!/usr/bin/env python3
"""r1_x86walk.py — minimal recursive x86 decoder for the restored image
(stdlib-only: capstone unavailable t42). Walks functions from an entry:
falls through, follows rel32/jcc targets, records call targets, stops at
ret/hlt/int3/jmp-uncond-abs. Prints 'addr: bytes  mnem ops' lines.
Decode rules restricted to the instruction classes actually seen in the
Watcom-32 image; unknown opcodes print as 'db XX' and abort that path.
usage: python3 scripts/r1_x86walk.py <entry_hex> [more entries...]
"""
import sys

d = open("work/ascend_restored.bin", "rb").read()
CODE_HI = 0x82bb0

TWO = {
    0xb6: ("movzx", "r,rm8", None), 0xb7: ("movzx", "r,rm16", None),
    0xbe: ("movsx", "r,rm8", None), 0xbf: ("movsx", "r,rm16", None),
    0xaf: ("imul", "r,rm", None), 0xa3: ("bt", "rm,r", None),
    0xa4: ("shld", "rm,r8", "b"), 0xac: ("shrd", "rm,r8", "b"),
    0xb3: ("btr", "rm,r", None), 0xab: ("bts", "rm,r", None),
    0x93: ("setae", "rm8", None), 0x92: ("setb", "rm8", None),
    0x94: ("sete", "rm8", None), 0x95: ("setne", "rm8", None),
    0x9c: ("pushfd", None, None), 0xa1: ("bt", "rm,r", None),
    0x38: ("", None, None),  # sse3 group — bail
}
REGS = ["eax", "ecx", "edx", "ebx", "esp", "ebp", "esi", "edi"]
REG8 = ["al", "cl", "dl", "bl", "bl", "ch", "dh", "bh"] if False else \
       ["al", "cl", "dl", "bl", "ah", "ch", "dh", "bh"]
JCC = ["jo", "jno", "jb", "jae", "je", "jne", "jbe", "ja",
       "js", "jns", "jp", "jnp", "jl", "jge", "jle", "jg"]

def modrm(d, i, namesz):
    """returns (text, nbytes) for modrm+sib+disp at i; rm text."""
    m = d[i]
    mod, reg, rm = m >> 6, (m >> 3) & 7, m & 7
    j = i + 1
    if mod == 3:
        return REGS[rm], j
    base = None
    parts = []
    if rm == 4:  # SIB
        sib = d[j]; j += 1
        sb, idx, sc = sib & 7, (sib >> 3) & 7, 1 << (sib >> 6)
        if idx != 4:
            parts.append(f"{REGS[idx]}*{sc}")
        if mod == 0 and sb == 5:
            disp = int.from_bytes(d[j:j+4], "little"); j += 4
            parts.append(f"[{disp:#x}]")
        else:
            parts.append(REGS[sb])
    elif rm == 5 and mod == 0:
        disp = int.from_bytes(d[j:j+4], "little"); j += 4
        return f"dword [{disp:#x}]" if namesz == 32 else f"[{disp:#x}]", j
    else:
        parts.append(REGS[rm])
    if mod == 1:
        disp = d[j] - 256 if d[j] > 127 else d[j]; j += 1
        parts.append(f"{disp:+d}")
    elif mod == 2:
        disp = int.from_bytes(d[j:j+4], "little"); j += 4
        parts.append(f"{disp:+d}" if disp < 0x80000000 else f"{disp:#x}")
    seg = ""
    return seg + "[" + " ".join(p if p.startswith("[") or "*" in p or p.endswith("]") and len(parts) == 1 else p for p in parts) + "]" if len(parts) > 1 else parts[0], j

def walk(entry, out, seen):
    addr = entry
    while True:
        if addr in seen or addr >= CODE_HI or addr < 0:
            return
        seen.add(addr)
        i = addr
        prefix = ""
        while d[i] in (0x66, 0x67, 0x2e, 0x36, 0x3e, 0xf0):
            prefix += f"{d[i]:02x} "
            i += 1
        op = d[i]
        namesz = 16 if d[addr] == 0x66 else 32
        nxt, text, targets = None, None, []
        try:
            if op in (0xc3,):
                text, nxt = "ret", None
            elif op == 0xcc:
                text, nxt = "int3", None
            elif op == 0x90:
                text, nxt = "nop", i + 1
            elif op == 0xe8:
                rel = int.from_bytes(d[i+1:i+5], "little", signed=True)
                text, nxt, targets = f"call {addr+5+rel:#x}", i + 5, [addr+5+rel]
            elif op == 0xe9:
                rel = int.from_bytes(d[i+1:i+5], "little", signed=True)
                text, nxt, targets = f"jmp {addr+5+rel:#x}", None, [addr+5+rel]
            elif op == 0xeb:
                rel = d[i+1] - 256 if d[i+1] > 127 else d[i+1]
                text, nxt, targets = f"jmp {addr+2+rel:#x}", None, [addr+2+rel]
            elif 0x70 <= op <= 0x7f:
                rel = d[i+1] - 256 if d[i+1] > 127 else d[i+1]
                text, nxt, targets = f"{JCC[op-0x70]} {addr+2+rel:#x}", i + 2, [addr+2+rel]
            elif op == 0x68:
                text, nxt = f"push {int.from_bytes(d[i+1:i+5],'little'):#x}", i + 5
            elif op == 0x6a:
                v = d[i+1] - 256 if d[i+1] > 127 else d[i+1]
                text, nxt = f"push {v}", i + 2
            elif op == 0x50 + 0 or 0x50 <= op <= 0x57:
                text, nxt = f"push {REGS[op-0x50]}", i + 1
            elif 0x58 <= op <= 0x5f:
                text, nxt = f"pop {REGS[op-0x58]}", i + 1
            elif op == 0xc7:  # mov rm, imm
                rm, j = modrm(d, i + 1, namesz)
                if namesz == 16:
                    v = int.from_bytes(d[j:j+2], "little"); j += 2
                else:
                    v = int.from_bytes(d[j:j+4], "little"); j += 4
                text, nxt = f"mov {rm}, {v:#x}" if v > 0xffff else f"mov {rm}, {v}", j
            elif op == 0xc6:
                rm, j = modrm(d, i + 1, 8)
                text, nxt = f"mov byte {rm}, {d[j]}", j + 1
            elif op == 0xff:  # inc/dec/jmp/jmpf group
                rm, j = modrm(d, i + 1, namesz)
                g = (d[i+1] >> 3) & 7
                mn = ["inc", "dec", "call", "callf", "jmp", "jmpf", "push", ""][g]
                text, nxt = f"{mn} {rm}", j
                if g in (2, 4): targets = []
            elif op == 0xfe:
                rm, j = modrm(d, i + 1, 8)
                g = (d[i+1] >> 3) & 7
                text, nxt = f"{'inc' if g==0 else 'dec'} byte {rm}", j
            elif op == 0x8d:
                rm, j = modrm(d, i + 1, namesz)
                text, nxt = f"lea {REGS[(d[i+1]>>3)&7]}, {rm}", j
            elif op == 0x85:
                rm, j = modrm(d, i + 1, namesz)
                text, nxt = f"test {rm}, {REGS[(d[i+1]>>3)&7]}", j
            elif op == 0x84:
                rm, j = modrm(d, i + 1, 8)
                text, nxt = f"test byte {rm}, {REG8[(d[i+1]>>3)&7]}", j
            elif op == 0x8f:
                rm, j = modrm(d, i + 1, namesz)
                text, nxt = f"pop {rm}", j
            elif op == 0x50:  # handled above but keep
                text, nxt = "push eax", i + 1
            elif op in (0xb0, 0xb1, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7):
                r = op - 0xb0
                if op <= 0xb3:
                    text, nxt = f"mov {REG8[r]}, {d[i+1]}", i + 2
                else:
                    v = int.from_bytes(d[i+1:i+3], "little")
                    text, nxt = f"mov {REGS[r]}, {v:#x}", i + 3
            elif 0xb8 <= op <= 0xbf:
                v = int.from_bytes(d[i+1:i+5], "little")
                text, nxt = f"mov {REGS[op-0xb8]}, {v:#x}", i + 5
            elif op in (0x40, 0x41, 0x42, 0x43):  # inc eax..ebx
                text, nxt = f"inc {REGS[op-0x40]}", i + 1
            elif op in (0x48, 0x49, 0x4a, 0x4b):
                text, nxt = f"dec {REGS[op-0x48]}", i + 1
            elif op in (0x44, 0x45, 0x46, 0x47, 0x4c, 0x4d, 0x4e, 0x4f):
                r = (op - 0x40) & 7
                text, nxt = f"{'inc' if op < 0x48 else 'dec'} {REGS[r]}", i + 1
            elif op in (0x99,):  # cdq
                text, nxt = "cdq", i + 1
            elif op in (0xf7,):  # test/test/div/mul imm
                rm, j = modrm(d, i + 1, namesz)
                g = (d[i+1] >> 3) & 7
                if g in (0, 1):
                    v = int.from_bytes(d[j:j+(2 if namesz==16 else 4)], "little")
                    j += 2 if namesz == 16 else 4
                    text, nxt = f"test {rm}, {v:#x}", j
                else:
                    text, nxt = f"{['','','mul','imul','div','idiv'][g]} {rm}", j
            elif op in (0xf6,):
                rm, j = modrm(d, i + 1, 8)
                g = (d[i+1] >> 3) & 7
                if g in (0, 1):
                    text, nxt = f"test byte {rm}, {d[j]}", j + 1
                else:
                    text, nxt = f"{['','','mul','imul','div','idiv','neg','not'][g]} byte {rm}", j
            elif op in (0xd1, 0xd3, 0xc1):  # shifts rm
                rm, j = modrm(d, i + 1, namesz)
                g = (d[i+1] >> 3) & 7
                mn = ["rol","ror","rcl","rcr","shl","shr","sal","sar"][g]
                if op == 0xc1:
                    text, nxt = f"{mn} {rm}, {d[j]}", j + 1
                elif op == 0xd1:
                    text, nxt = f"{mn} {rm}, 1", j
                else:
                    text, nxt = f"{mn} {rm}, cl", j
            elif op == 0xd2:
                rm, j = modrm(d, i + 1, 8)
                g = (d[i+1] >> 3) & 7
                mn = ["rol","ror","rcl","rcr","shl","shr","sal","sar"][g]
                text, nxt = f"{mn} byte {rm}, cl", j
            elif op in (0x80, 0x81, 0x82, 0x83):  # group rm, imm
                namesz8 = op in (0x80,)
                imm8 = op == 0x83
                rm, j = modrm(d, i + 1, 8 if namesz8 else namesz)
                g = (d[i+1] >> 3) & 7
                mn = ["add","or","adc","sbb","and","sub","xor","cmp"][g]
                if namesz8:
                    v = d[j]; j += 1
                    text, nxt = f"{mn} byte {rm}, {v}", j
                elif imm8:
                    v = d[j] - 256 if d[j] > 127 else d[j]; j += 1
                    text, nxt = f"{mn} {rm}, {v}", j
                else:
                    v = int.from_bytes(d[j:j+4], "little"); j += 4
                    text, nxt = f"{mn} {rm}, {v:#x}", j
            elif op in (0x03, 0x0b, 0x23, 0x2b, 0x33, 0x3b):
                rm, j = modrm(d, i + 1, namesz)
                mn = {0x03:"add",0x0b:"or",0x23:"and",0x2b:"sub",0x33:"xor",0x3b:"cmp"}[op]
                text, nxt = f"{mn} {REGS[(d[i+1]>>3)&7]}, {rm}", j
            elif op in (0x01, 0x09, 0x21, 0x29, 0x31, 0x39):
                rm, j = modrm(d, i + 1, namesz)
                mn = {0x01:"add",0x09:"or",0x21:"and",0x29:"sub",0x31:"xor",0x39:"cmp"}[op]
                text, nxt = f"{mn} {rm}, {REGS[(d[i+1]>>3)&7]}", j
            elif op in (0x0f0b,):
                text, nxt = "ud2", i+2
            elif op == 0x0f:
                op2 = d[i+1]
                if op2 in (0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87,
                           0x88, 0x89, 0x8a, 0x8b, 0x8c, 0x8d, 0x8e, 0x8f):
                    rel = int.from_bytes(d[i+2:i+6], "little", signed=True)
                    text, nxt, targets = f"{JCC[op2-0x80]} {addr+6+rel:#x}", i + 6, [addr+6+rel]
                elif op2 in TWO and TWO[op2][1] is None:
                    text, nxt = TWO[op2][0], i + 2
                elif op2 in TWO:
                    rm, j = modrm(d, i + 2, 32 if TWO[op2][0] in ("movzx","movsx","imul","bt","btr","bts") else 32)
                    text, nxt = f"{TWO[op2][0]} {REGS[(d[i+2]>>3)&7]}, {rm}", j
                    if TWO[op2][2] == "b":
                        text, nxt = f"{TWO[op2][0]} {rm}, {REG8[(d[i+2]>>3)&7]}, {d[j]}", j+1
                else:
                    text, nxt = f"db 0f {op2:02x} ;unknown", None
            else:
                text, nxt = f"db {op:02x} ;unknown", None
        except Exception as e:
            text, nxt = f"; decode-fail {e}", None
        out.append((addr, prefix, text))
        for t in targets:
            if t not in seen and 0 <= t < CODE_HI:
                walk(t, out, seen)
        if nxt is None:
            return
        i = nxt
        addr = i

def main():
    entries = [int(a, 16) for a in sys.argv[1:]]
    seen = set()
    out = []
    for e in entries:
        walk(e, out, seen)
    out.sort(key=lambda x: x[0])
    for a, p, t in out:
        print(f"{a:#07x}: {p}{t}")

main()
