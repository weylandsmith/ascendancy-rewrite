import sys
data = open('work/ascend_restored.bin','rb').read()
lo=int(sys.argv[1],16); hi=int(sys.argv[2],16)
# Watcom large-frame prologue: push imm32 ; mov edi,esp (89 e7) ; mov ebp,esp (89 e5)
for s in range(lo, hi):
    if data[s]==0x68:
        imm=int.from_bytes(data[s+1:s+5],'little',signed=True)
        if imm>0x100:
            seg=data[s+5:s+120]
            if b'\x89\xe7' in seg and b'\x89\xe5' in seg:
                print(hex(s), 'push', hex(imm), data[s:s+16].hex())
