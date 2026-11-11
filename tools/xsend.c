// SPDX-License-Identifier: GPL-3.0-or-later

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

/* t245: dosbox-x's X window name is CONSTANT ("DOSBox-X ...: ASCEND - 100%")
 * across boots, and an occluding "Quit DOSBox-X warning" xmessage window
 * matches the same substring. The wrong hit silently swallowed 20 minutes of
 * input (screenshot = root window only, so the blocker is INVISIBLE; events
 * went to the blocker). Refuse titles whose name contains "warning". */
static Window find_game(Display* d, Window w, const char* title, int depth) {
    char* nm = NULL;
    if (XFetchName(d, w, &nm) && nm) {
        int hit = strstr(nm, title) != NULL;
        int blocker = strstr(nm, "warning") != NULL;
        if (hit && blocker)
            fprintf(stderr, "xsend: REFUSING blocker window '%s'\n", nm);
        XFree(nm);
        if (hit && !blocker) return w;
    }
    Window root, parent, *kids = NULL;
    unsigned n = 0;
    if (depth > 6 || !XQueryTree(d, w, &root, &parent, &kids, &n)) return 0;
    for (unsigned i = 0; i < n; i++) {
        Window r = find_game(d, kids[i], title, depth + 1);
        if (r) { XFree(kids); return r; }
    }
    if (kids) XFree(kids);
    return 0;
}

int main(int argc, char** argv) {
    const char* title = argv[1];
    const char* mode = argv[2];
    /* t244 modes: key KEYSYM [ch] (press+release), keyup KEYSYM [ch] (press
     * ONLY, for hold semantics), click x y / click3 x y (Button1/Button3 —
     * Ascendancy ship move/attack orders are RIGHT-click), legacy x y. */
    int is_key = strcmp(mode, "key") == 0 || strcmp(mode, "keyup") == 0;
    int press_only = strcmp(mode, "keyup") == 0;
    int button = strcmp(mode, "click3") == 0 ? Button3 : Button1;
    if (argc < (is_key || strcmp(mode,"click")==0 || strcmp(mode,"click3")==0 ? 4 : 3)) {
        fprintf(stderr, "usage: xsend title (key|keyup KEYSYM [ch] | click|click3 x y | x y)\n");
        return 2;
    }
    int x = 0, y = 0; KeySym ks = 0; KeyCode kc = 0;
    Display* d = XOpenDisplay(NULL);
    if (!d) { fprintf(stderr, "no display\n"); return 1; }
    if (is_key) {
        ks = XStringToKeysym(argv[3]);
        if (ks == 0L) { fprintf(stderr, "bad keysym '%s'\n", argv[3]); return 2; }
        kc = XKeysymToKeycode(d, ks);
    } else if (strcmp(mode, "click") == 0 || strcmp(mode, "click3") == 0) {
        x = atoi(argv[3]); y = atoi(argv[4]);
    } else {   /* legacy positional: xsend title x y */
        x = atoi(argv[2]); y = atoi(argv[3]);
    }
    XSetErrorHandler(ignore_badwindow);
    Window root = DefaultRootWindow(d);
    Window w = find_game(d, root, title, 0);
    if (!w) { fprintf(stderr, "window '%s' not found\n", title); return 1; }
    XEvent e;
    memset(&e, 0, sizeof e);
    int press;
    if (!is_key) {
        XWarpPointer(d, None, w, 0, 0, 0, 0, x, y);
        XSync(d, False);
        usleep(20000);
        e.xbutton.window = w;
        e.xbutton.x = x; e.xbutton.y = y;
        e.xbutton.button = button;
        e.xbutton.same_screen = True;
        e.xbutton.subwindow = None;  /* target IS the event window */
    }
    for (press = 1; press >= (press_only ? 1 : 0); press--) {
        if (is_key) {
            e.type = press ? KeyPress : KeyRelease;
            e.xkey.window = w;
            e.xkey.root = root;
            e.xkey.subwindow = None;
            e.xkey.same_screen = True;
            /* XLookupString on a synthetic event reads keycode->keysym via
             * the server keymap; a caller may override keycode with the
             * KEYSYM OF THE LITERAL CHAR (argv[4]) so DOS text apps see it. */
            const char* ch = (argc > 4) ? argv[4] : "";
            e.xkey.keycode = (press && ch[0])
                ? XKeysymToKeycode(d, XStringToKeysym(ch)) : kc;
            /* state=0 intentionally: synthetic modifiers unverified */
        } else {
            e.type = press ? ButtonPress : ButtonRelease;
            e.xbutton.send_event = True;
        }
        e.xkey.send_event = True;
        XSendEvent(d, w, True, is_key ? (KeyPressMask|KeyReleaseMask)
                                      : (ButtonPressMask | ButtonReleaseMask), &e);
        XFlush(d);
        usleep(50000);
    }
    fprintf(stderr, "sent %s%s to 0x%lx at %d,%d (%s)\n",
            is_key ? argv[3] : (button == Button3 ? "button3" : "button1"),
            is_key && press_only ? " (press only)" : "", w, x, y,
            press == -1 ? "window died before release" : "press+release");
    XCloseDisplay(d);
    return 0;
}
