import sys, bisect
from capstone import *
data = open('work/ascend_restored.bin','rb').read()
md = Cs(CS_ARCH_X86, CS_MODE_32)

def enclosing_start(a, maxback=0x900):
    # walk back to the nearest plausible prologue that linearly reaches 'a'
    for s in range(a-1, a-maxback, -1):
        # common Watcom prologues: push sequence / sub esp,imm / mov edi,esp + rep stosd
        c = data[s]
        if c in (0x55,0x53,0x56,0x57) or c==0x68 or (c in (0x81,0x83) and data[s+1] in (0xec,0xf4,0xfa)):
            # verify linear decode s..a
            try:
                pos=s; ok=True
                for ins in md.disasm(data[s:a+16], s):
                    if ins.address>=a: ok=True; break
                    pos=ins.address+ins.size
                if ok: return s
            except Exception:
                continue
    return None

for a in [int(x,16) for x in sys.argv[1:]]:
    s = enclosing_start(a)
    print(f"=== call@{a:x} enclosing-start={s:x} ===")
    if s is None: continue
    n=0
    for ins in md.disasm(data[s:a+30], s):
        print(f"{ins.address:x}: {ins.mnemonic} {ins.op_str}")
        n+=1
        if n>400: print('...trunc'); break
