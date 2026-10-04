/* gate helper: synthetic X11 input for the P5a UI window.
 * Rationale: no xdotool/libXtst-dev/python-xlib on this host; XSendEvent
 * needs only libX11, and SDL2 accepts synthetic Button/Key events (only
 * synthetic MotionNotify/ClientMessage are rejected, SDL_x11_window.c).
 * SDL re-reads the POINTER for synthetic Button events, so XWarpPointer
 * first (measured 2026-10-04). The app may destroy its window between the
 * press and release (a click that ends the campaign) — tolerate BadWindow.
 * Build: gcc -O1 -o xsend xsend.c -lX11
 * Usage: xsend <window-title-substring> <x> <y>   (button1 press+release) */
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int ignore_badwindow(Display* d, XErrorEvent* e) {
    (void)d;
    if (e->error_code == BadWindow) return 0;  /* app closed mid-burst */
    fprintf(stderr, "xsend: X error %d (request %d)\n", e->error_code,
            e->request_code);
    exit(3);
}

static Window find_named(Display* d, Window w, const char* title, int depth) {
    char* nm = NULL;
    if (XFetchName(d, w, &nm) && nm) {
        int hit = strstr(nm, title) != NULL;
        XFree(nm);
        if (hit) return w;
    }
    Window root, parent, *kids = NULL;
    unsigned n = 0;
    if (depth > 6 || !XQueryTree(d, w, &root, &parent, &kids, &n)) return 0;
    for (unsigned i = 0; i < n; i++) {
        Window r = find_named(d, kids[i], title, depth + 1);
        if (r) { XFree(kids); return r; }
    }
    if (kids) XFree(kids);
    return 0;
}

int main(int argc, char** argv) {
    if (argc < 4) { fprintf(stderr, "usage: xsend title x y\n"); return 2; }
    const char* title = argv[1];
    int x = atoi(argv[2]), y = atoi(argv[3]);
    Display* d = XOpenDisplay(NULL);
    if (!d) { fprintf(stderr, "no display\n"); return 1; }
    XSetErrorHandler(ignore_badwindow);
    Window root = DefaultRootWindow(d);
    Window w = find_named(d, root, title, 0);
    if (!w) { fprintf(stderr, "window '%s' not found\n", title); return 1; }
    XWarpPointer(d, None, w, 0, 0, 0, 0, x, y);
    XSync(d, False);
    usleep(20000);
    XEvent e;
    memset(&e, 0, sizeof e);
    e.xbutton.window = w;
    e.xbutton.x = x; e.xbutton.y = y;
    e.xbutton.button = Button1;
    e.xbutton.same_screen = True;
    e.xbutton.subwindow = None;  /* target IS the event window */
    int press;
    for (press = 1; press >= 0; press--) {
        e.type = press ? ButtonPress : ButtonRelease;
        e.xbutton.send_event = True;
        XSendEvent(d, w, True, ButtonPressMask | ButtonReleaseMask, &e);
        XFlush(d);
        usleep(50000);
    }
    fprintf(stderr, "sent button1 to 0x%lx at %d,%d (press%s)\n", w, x, y,
            press == -1 ? "+release" : " only (window died)");
    XCloseDisplay(d);
    return 0;
}
