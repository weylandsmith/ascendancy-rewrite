import sys
data = open('work/ascend_restored.bin','rb').read()
lo=int(sys.argv[1],16) if len(sys.argv)>1 else 0x32f0
hi=int(sys.argv[2],16) if len(sys.argv)>2 else 0x3478
# find first '07 10' anchor then walk 10-byte entries while pattern holds
i=lo
while i<hi-10:
    if data[i]==0x07 and data[i+1]==0x10:
        dst=int.from_bytes(data[i+2:i+6],'little')
        val=int.from_bytes(data[i+6:i+10],'little')
        print(f"{i:x}: opcode16 dst={dst:#010x} val={val:#010x} ({val})")
        i+=10
    else:
        i+=1
