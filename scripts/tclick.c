// SPDX-License-Identifier: GPL-3.0-or-later

/* tclick.c — t267: synthetic click at an EXPLICIT window id (xsend targets by
 * title and must keep refusing "warning" titles; a quit-confirm xmessage is
 * the one case where the blocker IS the target, and it must be hit by id,
 * never by pattern). Usage: tclick 0xWINID x y   (coords inside that window)
 */
#include <X11/Xlib.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char** argv) {
    if (argc < 4) { fprintf(stderr, "usage: tclick 0xWINID x y\n"); return 2; }
    Window w = (Window)strtoull(argv[1], NULL, 0);
    int x = atoi(argv[2]), y = atoi(argv[3]);
    Display* d = XOpenDisplay(NULL);
    if (!d) { fprintf(stderr, "no display\n"); return 1; }
    XSync(d, False);
    XEvent ev;
    memset(&ev, 0, sizeof(ev));
    ev.xbutton.type = ButtonPress;
    ev.xbutton.display = d;
    ev.xbutton.window = w;
    ev.xbutton.root = DefaultRootWindow(d);
    ev.xbutton.same_screen = True;
    ev.xbutton.x = x; ev.xbutton.y = y;
    ev.xbutton.button = Button1;
    ev.xbutton.state = 0;
    if (!XSendEvent(d, w, False, ButtonPressMask, &ev)) {
        fprintf(stderr, "XSendEvent press failed\n"); return 1;
    }
    XFlush(d); usleep(80000);
    ev.type = ButtonRelease;
    ev.xbutton.state = Button1Mask;
    if (!XSendEvent(d, w, False, ButtonReleaseMask, &ev)) {
        fprintf(stderr, "XSendEvent release failed\n"); return 1;
    }
    XFlush(d); XSync(d, False);
    printf("clicked window 0x%lx at %d,%d\n", (unsigned long)w, x, y);
    XCloseDisplay(d);
    return 0;
}
