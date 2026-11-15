#!/usr/bin/env python3
# t395 probe: SOUNDCHANNEL census over windows.txt (cited vendor table).
import re, collections, sys

path = sys.argv[1] if len(sys.argv) > 1 else \
    '/home/hrethric/projects/ascendancy/extracted/ascend00/windows.txt'
txt = open(path, newline='').read()

vals = collections.Counter()
occ = []
for m in re.finditer(r'SOUNDCHANNEL\s+(-?\d+)', txt):
    vals[m.group(1)] += 1
    pre = txt[:m.start()]
    nm = re.findall(r'(?m)^\s*NAME\s+"?([A-Za-z0-9_]+)"?', pre)
    occ.append((nm[-1] if nm else '?', m.group(1), m.start()))

print('total SOUNDCHANNEL records:', sum(vals.values()))
print('value histogram:', dict(vals))

TITLE = {'RESUME','INTRO','NEWGAME','LOADGAME','SAVEGAME','TUTORIAL',
         'EXITTODOS','BEGINNEWGAME','CANCEL','OK','NEXTTURN','NEXTTURNCONT',
         'RACECONTROLS'}
for n, v, off in occ:
    if n in TITLE:
        print('title button:', n, '-> SOUNDCHANNEL', v)
for n, v, off in occ:
    if v.strip('-0') != '':
        print('ODD value:', n, '->', repr(v), 'offset', hex(off))

# distinct (name) coverage sanity: how many distinct window records total
names = re.findall(r'(?m)^\s*NAME\s+"?([A-Za-z0-9_]+)"?', txt)
print('distinct NAME lines:', len(names))
