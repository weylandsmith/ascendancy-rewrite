import sys
from capstone import *
data = open('work/ascend_restored.bin','rb').read()
md = Cs(CS_ARCH_X86, CS_MODE_32)
start=int(sys.argv[1],16); end=int(sys.argv[2],16)
a=start
while a<end:
    got=False
    for ins in md.disasm(data[a:min(end,a+16)], a):
        print(f"{ins.address:x}: {ins.mnemonic} {ins.op_str}")
        a=ins.address+ins.size; got=True
        if a>=end: break
    if not got:
        print(f"{a:x}: .byte {data[a]:02x}")
        a+=1
