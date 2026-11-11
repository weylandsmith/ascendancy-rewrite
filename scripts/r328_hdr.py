# SPDX-License-Identifier: GPL-3.0-or-later

import struct, glob, sys
p=sys.argv[1]; ks=[int(x) for x in sys.argv[2:]]
d=open(p,'rb').read(); count=struct.unpack_from('<I',d,4)[0]; tsz=struct.unpack_from('<I',d,8)[0]
te=0x10+tsz
starts=[te]+[struct.unpack_from('<Q',d,0x10+8*k)[0] for k in range(count-1)]
ends=starts[1:]+[len(d)]
for k in ks:
    s=starts[k]
    print(f'== k{k} off {hex(s)} span {ends[k]-s}')
    print('   bytes[0x00:0x18]', d[s:s+0x18].hex(' '))
    print('   u16@+0 ', struct.unpack_from('<HH',d,s))
    print('   u32@+0 ', struct.unpack_from('<II',d,s))
    print('   u16@+10', struct.unpack_from('<HH',d,s+0x10))
    print('   u32@+10', struct.unpack_from('<II',d,s+0x10))
    print('   u16@+18', struct.unpack_from('<HH',d,s+0x18))
