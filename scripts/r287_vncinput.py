#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t287 RFB input channel — REAL pointer motion into display :9 via x11vnc.

WHY: the title-menu/game menus are hover-driven, and the game updates hover
ONLY from motion events. SDL2 rejects synthetic MotionNotify (xsend.c header),
so xsend warped clicks fire the STALE hovered row — MEASURED 08:40:48 EST:
click (318,333) 'Return to Current Game' activated 'Tutorial' (the row a VNC
user had last hovered; esc1 vs backgame diff 248874 px). Keys are fine via
xsend; MOTION is the broken channel.

x11vnc (pid banked work/r1/vnc/x11vnc.pid, -localhost -nopw -rfbport 5910)
translates RFB PointerEvent/KeyEvent into XTEST events — indistinguishable
from real input, which is exactly what SDL will accept. This tool speaks just
enough RFB 3.8 (SecurityNone, ClientInit, Pointer/Key events, NO framebuffer
requests so nothing streams back).

Coordinates are GAME-relative (640x480); the tool adds the window origin
(+80,+100 root offset — t250 law) for PointerEvents. NOTE: root coords assume
the game window stays at +80+100 (xwininfo-verified this session).

usage:
  r287_vncinput.py move X Y
  r287_vncinput.py click X Y      # move, settle, press, release (all XTEST)
  r287_vncinput.py key KEYSYM     # e.g. Escape, Return, Down
"""
import os, socket, socketserver, struct, subprocess, sys, time

HOST, PORT = "127.0.0.1", 5910
XOFF, YOFF = (int(os.environ.get("RFB_XOFF", 80)),
              int(os.environ.get("RFB_YOFF", 100)))
# CALIBRATION (t287, three-way evidence): RFB PointerEvent coords == X ROOT
# coords (x11vnc framebuffer = whole Xvfb :9), so GAME coords need +80/+100
# (t250 window-origin law). (1) offsets 80/100 move(318,333) highlighted
# menu row R4 (game y 313-353); (2) offsets 0 move(5,5) = root(5,5), OUTSIDE
# the window: highlight CLEARED + 9676 px re-render; (3) offsets 0
# move(318,333) = game(238,233) separator: no highlight. Earlier "clicks did
# nothing" was the PointerEvent mask-packing bug below, not coordinates.
# ALWAYS verify expected highlight via r287_title_nav.py status first.

KSYM = {"Escape": 0xff1b, "Return": 0xff0d, "Down": 0xff54, "Up": 0xff52,
        "Left": 0xff51, "Right": 0xff53, "space": 0x20, "Tab": 0xff09}


def recvn(s, n, tmo=2.0):
    s.settimeout(tmo)
    buf = b""
    while len(buf) < n:
        c = s.recv(n - len(buf))
        if not c:
            break
        buf += c
    return buf


def session():
    s = socket.create_connection((HOST, PORT), timeout=10)
    ver = s.recv(12)
    if not ver.startswith(b"RFB"):
        sys.exit(f"not RFB: {ver!r}")
    # MEASURED x11vnc flow: answering with 3.8 + 4-byte security selection
    # RESETS the socket; the 3.3 flow (zero-terminated type list, 1-byte
    # selection, no SecurityResult) completes and accepts events.
    s.sendall(b"RFB 003.003\n")
    types = b""
    while True:
        b1 = recvn(s, 1)
        if not b1 or b1 == b"\x00":
            break
        types += b1
    if 1 not in types and types:
        sys.exit(f"server offers {list(types)}, no SecurityNone")
    # MEASURED: this x11vnc answers the 3.3-style query with an EMPTY
    # zero-terminated list (0x00) then behaves as SecurityNone; sending
    # 0x01 proceeds to ServerInit. Trust the measured flow.
    s.sendall(b"\x01")                      # select None, shared=1 (3.3 fuses)
    hdr = recvn(s, 24)
    if len(hdr) != 24:
        sys.exit(f"no ServerInit ({hdr!r})")
    # geometry/name parsing is irrelevant for INPUT (x11vnc PointerEvent
    # coords == X root coords), but drain the name so the stream is clean.
    nlen = struct.unpack(">I", hdr[20:24])[0]
    if 0 < nlen < 4096:
        recvn(s, nlen - 16, 1.0)
    return s


def ptr(s, x, y, mask=0):
    # RFB PointerEvent = u8 type(5), u8 down-mask, u16 x, u16 y. The earlier
    # ">BBHHB" with a TRAILING mask sent down=0 always and desynced one byte
    # per event — 'clicks' reached the game as motion (hover moved, nothing
    # ever activated; MEASURED: R4 highlighted, 0 px on press).
    s.sendall(struct.pack(">BBHH", 5, mask, x + XOFF, y + YOFF))


def keyev(s, keysym, down):
    s.sendall(struct.pack(">BBB3sI", 4, down, 0, b"\x00\x00\x00", keysym))


def main():
    args = sys.argv[1:]
    mode = args[0]
    s = session()
    if mode == "move":
        ptr(s, int(args[1]), int(args[2]))
    elif mode == "click":
        x, y = int(args[1]), int(args[2])
        ptr(s, x, y)
        time.sleep(0.25)
        ptr(s, x, y, 1)
        time.sleep(0.08)
        ptr(s, x, y, 0)
    elif mode == "key":
        ks = KSYM.get(args[1])
        if ks is None:
            sys.exit(f"unknown keysym {args[1]}")
        keyev(s, ks, 1)
        time.sleep(0.05)
        keyev(s, ks, 0)
    else:
        sys.exit(__doc__)
    # let queued events flush server-side before closing
    time.sleep(0.15)
    s.close()
    print(f"sent {mode} {args[1:]} via RFB", file=sys.stderr)


if __name__ == "__main__":
    main()
