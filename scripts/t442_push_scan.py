import sys
data = open('work/ascend_restored.bin','rb').read()
lo=int(sys.argv[1],16); hi=int(sys.argv[2],16)
targets={234:'slot_top_x?',68:'slot_top_y?',64:'slot_left_x?',404:'slot_right_x?',407:'slot_bottom_y?',170:'r170',236:'centre_x',239:'centre_y',235:'x235',238:'y238'}
for a in range(lo,hi-5):
    if data[a]==0x68:  # push imm32
        v=int.from_bytes(data[a+1:a+5],'little')
        if v in targets:
            print(f"{a:x}: push {v}  <- {targets[v]}   ctx={data[a:a+6].hex()}")
    elif data[a]==0x6a:  # push imm8 (signed)
        v=data[a+1]
        if v<128 and v in targets and targets[v]=='r170' or (v in targets and v<128):
            print(f"{a:x}: push {v}  <- {targets[v]} (imm8) ctx={data[a:a+6].hex()}")
