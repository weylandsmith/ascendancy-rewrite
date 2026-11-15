#!/usr/bin/env python3
# t390: dump PIL plane slices for diffing against the C++ decoder's output.
# Usage: t390_slices.py <cpp_dump.bin>  (or no arg -> write ref slices file)
import sys
from PIL import Image

im = Image.open('/home/hrethric/projects/ascendancy/extracted/ascend01/data/0opening.gif')
im.load()
ref = im.tobytes()
if len(sys.argv) > 1:
    got = open(sys.argv[1], 'rb').read()
    print('len', len(got), 'ref', len(ref))
    diffs = [k for k in range(min(len(got), len(ref))) if got[k] != ref[k]]
    print('ndiff', len(diffs), 'first', diffs[:10], 'last', diffs[-5:] if diffs else None)
else:
    open('/tmp/t390_ref.bin', 'wb').write(ref)
    print('wrote /tmp/t390_ref.bin')
