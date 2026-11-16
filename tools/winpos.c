/* winpos: print geometry of the first top-level window whose WM_NAME
 * matches a substring.  Output: "X Y W H TITLE" (root coords).
 * D13 walkthrough tool: xsend needs root coords; UI crops crop to logical
 * 640x480.  Build: gcc -O1 -o winpos winpos.c -lX11 */
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/Xatom.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char** argv) {
    if (argc < 2) { fprintf(stderr, "usage: winpos TITLE-SUBSTR\n"); return 2; }
    Display* d = XOpenDisplay(NULL);
    if (!d) { fprintf(stderr, "no display\n"); return 1; }
    Window r, parent, *kids = NULL; unsigned n = 0;
    XQueryTree(d, DefaultRootWindow(d), &r, &parent, &kids, &n);
    for (unsigned i = 0; i < n; i++) {
        XTextProperty wn;
        char* name = NULL;
        if (XGetTextProperty(d, kids[i], &wn, XA_WM_NAME) && wn.value)
            name = (char*)wn.value;
        XWindowAttributes g;
        if (name && strstr(name, argv[1]) && XGetWindowAttributes(d, kids[i], &g)
            && g.map_state == IsViewable && g.width > 100) {
            int rx = 0, ry = 0; Window child;
            XTranslateCoordinates(d, kids[i], DefaultRootWindow(d), 0, 0, &rx, &ry, &child);
            printf("%d %d %d %d %s\n", rx, ry, g.width, g.height, name);
            return 0;
        }
    }
    fprintf(stderr, "no viewable window matching '%s'\n", argv[1]);
    return 1;
}
