#!/usr/bin/env python3
"""t293 SCRIPTED MOVE-ORDER CAPTURE — witness the sugar-cube scale live (OQ-019).

QUESTION (docs/re/ships.md §17 T1/T2 + §t48 route, docs/BLOCKED.md
"Scripted-move capture — LIVE"): does one End-Turn of flight move a ship by the
RAW walked distance of FUN_00049f54 (walk = min(d/160, MOVES[+0x94]); commit
[+0x9e] += normalize*(walk/steps)*32*5; fuel [+0x88] -= steps; 32-grid
quantizer) — or by a hop/handpoint abstraction? One witnessed flight with
per-autosave coordinates discriminates at ring granularity: t265's st4 DWELL law
says an in-system march resolves inside ONE turn boundary, so the endpoint after
one End-Turn is the committed walk endpoint. endpoint == start + d*min(1,MOVES/
(d/160)) AND on the 32-grid => walk law CONFIRMED live.

CHOREOGRAPHY (vendor help.txt, verbatim lines banked in docs/re/_wip_t293.md):
  - coswnd (Galactic Display): clicking a discovered star ENTERS THE SYSTEM.
  - batmode (System Display): "You can move a selected ship by clicking on a
    desired destination."
  - t244 MEASURED law (selfplay.md §4): RIGHT-CLICK (Button3) on the orbital
    grid = ORDER MODE, a green target marker appears on the grid.
So: title -> Return to Current Game (318,333) -> click the home star pip ->
System View -> right-click a destination point in the orbital grid -> verify the
GREEN MARKER pixel signature (the order-mode witness t244 describes) -> verify
via the RING that a player ship's kind [+0x58] / coords [+0x9e] moved -> End
Turn x2 sampling the ring per slot.

MEASUREMENT SURFACE: this scratch session's OWN ring (r1_playcap_watch schema:
ships[] + ship_raw u16 windows; kind=byte+0x58, MOVES=u16+0x94, FUEL=u16+0x88,
xyz=f32+0x9e, stride 0x162) + screenshots banked per step. No debugger.

SAFETY (docs/BLOCKED.md runbook, binding): scratch copy work/r1/game-wp ONLY
(asserted, never game/); OWN ring dir + private Xvfb (never :9, production pid
660167 untouched); output=x11 (vblank autosave law); nosound; -time-limit;
kill-by-recorded-PID in finally (NEVER pkill); screen gate assert_on_map BEFORE
every click (t285 orange-frac law); NEVER Escape at the bare map; popup drain
runs ONLY when a press did not advance AND the screen is not the title (t273/
t289 guards); no-advance presses counted, 2 in a row = STOP-AND-LOOK.

usage: r293_move_session.py [--disp 96] [--tl 1500] [--settle 45] [--boot 120]
Exit 0 = a flight was WITNESSED (ship coords changed across a turn boundary
    after an issued order) — evidence dir printed.
     1 = ran to a real negative (order never landed / no flight) — evidence
       dir printed with every screenshot + ring sample.
     2 = harness error.
"""
import argparse
import glob
import hashlib
import json
import os
import shutil
import signal
import struct
import subprocess
import sys
import time
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as SL                                              # noqa: E402

from PIL import Image                                             # noqa: E402

SCRATCH = os.path.join(ROOT, "work/r1/game-wp")
PAYLOAD = os.path.join(ROOT, "work/ascend_payload.bin")
OCT29 = os.path.join(ROOT, "work/r1/game/RESUME.GAM.user-oct29")
OCT29_MD5 = "5b382afbb789186c3654f3cec085b2e2"
DOSBOX = "/usr/bin/dosbox-x"
XSEND = os.path.join(ROOT, "tools/xsend")
RETURN_TO_GAME = (318, 333)
NEXTTURN = (511, 67)
MAP_CENTER = (236, 240)          # inside COSMOSWnd rect 7,7-465,472 (windows.txt)
XOFF, YOFF = 80, 100            # root origin law (t250)
WALL_FIELDS = {"wall", "file", "file_mtime_ns"}


def dspec(disp):
    return f":{str(disp).lstrip(':')}"


def kill_rec(pid):
    try:
        os.kill(pid, signal.SIGKILL)
    except Exception:
        pass


class Session:
    def __init__(self, args):
        self.a = args
        self.disp = dspec(args.disp)
        self.out = os.path.join(ROOT, "work/r1",
                                f"t293-move-{time.strftime('%Y%m%d-%H%M%S')}")
        os.makedirs(os.path.join(self.out, "save"), exist_ok=True)
        self.savedir = os.path.join(self.out, "save")
        self.logp = os.path.join(self.out, "session.log")
        self.dbl = os.path.join(self.out, "dosbox.out")
        self.pay = SL.load_payload(ROOT)
        self.anch = SL.anchors_cached(ROOT, self.pay)
        self.payload_ship = None
        self.no = 0

    # ---------- logging ----------
    def log(self, msg):
        line = f"{time.strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        with open(self.logp, "a") as f:
            f.write(line + "\n")

    # ---------- screen ----------
    def grab(self, name):
        self.no += 1
        raw = os.path.join(self.out, f"_raw_{self.no:02d}_{name}.png")
        r = subprocess.run(["import", "-window", "root", raw],
                           capture_output=True, timeout=30,
                           env=dict(os.environ, DISPLAY=self.disp))
        if r.returncode != 0:
            self.log(f"grab FAILED {name}")
            return None
        img = Image.open(raw).convert("RGB")
        crop = img.crop((XOFF, YOFF, XOFF + 640, YOFF + 480))
        path = os.path.join(self.out, f"{self.no:02d}_{name}.png")
        crop.save(path)
        return crop

    @staticmethod
    def orange_frac(im):
        if im is None:
            return -1.0
        px = im.load()
        tot = orange = 0
        for y in range(0, 330, 3):
            for x in range(0, 640, 4):
                r, g, b = px[x, y]
                tot += 1
                if r > 140 and g > 50 and b < 110 and r - b > 70:
                    orange += 1
        return orange / max(1, tot)

    @staticmethod
    def green_count(im, x0=40, y0=60, x1=460, y1=460):
        """Bright-GREEN pixels in the map/orbital area — the order-mode marker
        signature t244 describes (green target marker on the grid). UI chrome
        in this area is blue/cyan/cyan-trim; green text exists only in list
        rows (fleet/ship windows), which must be CLOSED during this census."""
        px = im.load()
        n = 0
        for y in range(y0, y1, 2):
            for x in range(x0, x1, 2):
                r, g, b = px[x, y]
                if g > 150 and g - r > 60 and g - b > 60:
                    n += 1
        return n

    @staticmethod
    def diff_px(a, b):
        if a is None or b is None:
            return -1
        pa, pb = a.load(), b.load()
        n = 0
        for y in range(0, 480, 2):
            for x in range(0, 640, 2):
                if pa[x, y] != pb[x, y]:
                    n += 1
        return n * 4

    def assert_on_map(self, why):
        im = self.grab("precheck")
        f = self.orange_frac(im)
        if f > 0.20:
            self.log(f"TITLE MENU ON SCREEN (orange {f:.3f}) at {why} — STOP "
                     f"clicks (t285 law)")
            return False
        return True

    # ---------- input ----------
    def send(self, args):
        env = dict(os.environ, DISPLAY=self.disp)
        for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
            env.pop(k, None)
        try:
            r = subprocess.run([XSEND, "DOSBox-X"] + args,
                               capture_output=True, timeout=30, env=env)
            self.log(f"xsend {args} rc={r.returncode}")
            return r.returncode
        except Exception as e:
            self.log(f"xsend {args} EXC {e}")
            return -1

    def popup_ok_center(self, im):
        """t250/t261 detector: white-text rows in the popup band, OK = last
        group on the bottom row, click at label-row TOP minus 3."""
        px = im.load()
        rows = {}
        for y in range(330, 470):
            xs = [x for x in range(170, 486)
                  if px[x, y][0] > 190 and px[x, y][1] > 190 and px[x, y][2] > 190]
            if len(xs) > 8:
                rows[y] = xs
        if sum(len(v) for v in rows.values()) < 120:
            return None
        ybot = max(rows)
        groups = []
        for x in sorted(set(rows[ybot])):
            if groups and x - groups[-1][-1] <= 8:
                groups[-1].append(x)
            else:
                groups.append([x])
        ok = groups[-1]
        ytop = min(y for y in rows if y >= ybot - 12)
        return (sum(ok) // len(ok), ytop - 3)

    def eventwin_open(self, im):
        """Construction/event popup = LIGHT background box (t293 MEASURED: the
        white-WHITE-TEXT detector is blind to it; white px 804->2689 when one
        opens). Signature: many near-white pixels inside the EVENTWIN rect
        60,100-395,355 (windows.txt)."""
        px = im.load()
        n = 0
        for y in range(105, 350, 2):
            for x in range(65, 392, 2):
                r, g, b = px[x, y]
                if r > 185 and g > 185 and b > 185:
                    n += 1
        return n > 400

    def close_eventwin(self):
        """L3 LAW (selfplay.md, re-confirmed t293 L3: OK clicks at
        windows.txt EVENTBUTTON1 centre (330,332) did NOTHING — synthetic
        Button1 unreliable): close popups with key Escape, ONE press, then
        VERIFY. Title guard first (t285: Escape at the bare map ejects)."""
        for attempt in range(4):
            im = self.grab(f"ewc{attempt}")
            if im is None or not self.eventwin_open(im):
                return True
            if self.orange_frac(im) > 0.20:
                self.log("close_eventwin: TITLE visible — abort (t285)")
                return False
            self.send(["key", "Escape"])
            time.sleep(2.0)
            chk = self.grab(f"ewc{attempt}b")
            if chk is not None and not self.eventwin_open(chk):
                self.log(f"EVENTWIN closed by Escape (attempt {attempt})")
                return True
        return False


    def drain_popups(self, maxn=10):
        im0 = self.grab("drain_gate")
        if self.orange_frac(im0) > 0.20:
            self.log("drain SKIPPED — title menu (t289 screen guard)")
            return 0
        closed = 0
        for _ in range(maxn):
            im = self.grab("popup") if closed == 0 else None
            if im is None and closed:
                # cheap re-check: only re-grab when we might click
                im = self.grab("popup")
            c = self.popup_ok_center(im)
            if c is None:
                return closed
            self.send(["click", str(c[0]), str(c[1])])
            closed += 1
            time.sleep(2.5)
        return closed

    # ---------- ring ----------
    def ring_mem_rows(self):
        rows = []
        for sp in sorted(glob.glob(os.path.join(self.savedir, "*.sav")),
                         key=os.path.getmtime):
            try:
                mem = zipfile.ZipFile(sp).read("Memory")
            except Exception:
                continue
            if len(mem) < 0x90000:
                continue
            B = SL.base_of(mem, self.anch)
            if B is None:
                continue
            d = SL.read_slot(sp, mem, B)
            d["path"] = sp
            d["mt"] = os.path.getmtime(sp)
            try:
                base, n = SL.ship_array_law(mem, B)
                recs = {}
                for k in range(n):
                    r = base + k * SL.SHIP["stride"]
                    if r + SL.SHIP["stride"] > len(mem):
                        break
                    recs[k] = dict(
                        owner=struct.unpack_from("<I", mem, r + 0x54)[0] >> 16,
                        kind=mem[r + 0x58],
                        design=struct.unpack_from("<I", mem, r + 0x10)[0],
                        xyz=struct.unpack_from("<3f", mem, r + 0x9e),
                        fuel=struct.unpack_from("<H", mem, r + 0x88)[0],
                        moves=struct.unpack_from("<H", mem, r + 0x94)[0])
                d["recs"] = recs
            except Exception as e:
                d["recs_error"] = repr(e)[:120]
            rows.append(d)
        return rows

    def sample(self, tag):
        rows = self.ring_mem_rows()
        keep = []
        for d in rows:
            keep.append(dict(file=d["file"], turn=d["turn"],
                             score=d["score_stars"], sel=d["selector_byte"],
                             mt=d["mt"],
                             recs={str(k): v for k, v in (d.get("recs") or {}).items()
                                   if v["owner"] == 0}))
        path = os.path.join(self.out, f"ringsample_{tag}.json")
        with open(path, "w") as f:
            json.dump(keep, f, indent=1)
        self.log(f"sample {tag}: {len(rows)} slots -> {os.path.basename(path)}"
                 + (f" latest t={keep[-1]['turn']}" if keep else " EMPTY"))
        return rows

    # ---------- lifecycle ----------
    def launch(self):
        shutil.copy2(OCT29, os.path.join(SCRATCH, "RESUME.GAM"))
        low = os.path.join(SCRATCH, "resume.gam")
        if os.path.exists(low):
            os.rename(low, low + ".vendor-t293")
        conf = os.path.join(self.out, "session.conf")
        with open(conf, "w") as f:
            f.write(f"""[dosbox]
machine=svga_s3
memsize=16
core=normal
captures={self.out}/caps
autosave=10 41-60
saveremark=false
[sdl]
output=x11
fullscreen=false
autolock=false
[mixer]
nosound=true
[autoexec]
MOUNT C {SCRATCH}
C:
ASCEND.EXE
""")
        self.xv = subprocess.Popen(
            ["Xvfb", self.disp, "-screen", "0", "800x600x24"],
            stdout=open(os.path.join(self.out, "xvfb.out"), "wb"),
            stderr=subprocess.STDOUT)
        time.sleep(2.0)
        env = dict(os.environ, DISPLAY=self.disp, TERM="xterm")
        for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
            env.pop(k, None)
        dlog = open(self.dbl, "wb")
        self.child = subprocess.Popen(
            [DOSBOX, "-conf", conf, "-nogui", "-savedir", self.savedir,
             "-time-limit", str(self.a.tl)],
            stdin=subprocess.DEVNULL, stdout=dlog, stderr=subprocess.STDOUT,
            cwd=self.out, env=env, start_new_session=True)
        self.log(f"spawned dosbox pid={self.child.pid} display={self.disp} "
                 f"out={self.out} tl={self.a.tl}")

    def cleanup(self):
        kill_rec(self.child.pid)
        time.sleep(1.0)
        if getattr(self, "xv", None):
            kill_rec(self.xv.pid)

    # ---------- phases ----------
    def wait_title(self):
        t0 = time.time()
        hits = 0
        while time.time() - t0 < self.a.boot:
            time.sleep(5)
            im = self.grab("titlepoll")
            f = self.orange_frac(im)
            self.log(f"title poll orange={f:.3f} ({time.time()-t0:.0f}s)")
            if f > 0.20:
                hits += 1
                if hits >= 2:
                    return True
            else:
                hits = 0
        return False

    def enter_campaign(self):
        # The title menu MUST be on screen here (t287 law: verify from the
        # screen before clicking). This click is the deliberate exception to
        # "no clicks at the title" — t292 proved the motion-warp click on
        # (318,333) enters the campaign on a fresh private Xvfb (no stale
        # hover state there).
        im = self.grab("title_before_enter")
        f = self.orange_frac(im)
        self.log(f"enter_campaign: title orange={f:.3f} (expect >0.20)")
        if f < 0.20:
            self.log("NOT on the title menu — refusing Return-to-Game blind")
            return False
        self.send(["click", str(RETURN_TO_GAME[0]), str(RETURN_TO_GAME[1])])
        time.sleep(3)
        im = self.grab("entered")
        f = self.orange_frac(im)
        self.log(f"after Return-to-Game orange={f:.3f}")
        if f > 0.20:
            return False
        # ring must show the loaded campaign
        t0 = time.time()
        while time.time() - t0 < 90:
            rows = self.ring_mem_rows()
            if rows and rows[-1]["turn"] > 0 and rows[-1].get("recs"):
                self.log(f"ring loaded: t={rows[-1]['turn']} "
                         f"ships={len(rows[-1]['recs'])}")
                return True
            time.sleep(5)
        return False

    def pick_target(self, rows):
        """Home star = star index most-represented among owner-0 orbit ships
        (kind 5). Returns (star_xyz, [ship slots there]) from the newest slot."""
        newest = rows[-1]
        recs = newest.get("recs") or {}
        from collections import Counter
        cnt = Counter()
        for k, v in recs.items():
            if v["kind"] == 5:
                cnt[tuple(round(c, 2) for c in v["xyz"])] += 1
        if not cnt:
            # fallback: any owner-0 ship
            for k, v in recs.items():
                return tuple(round(c, 2) for c in v["xyz"]), [k]
            return None, []
        xyz, _n = cnt.most_common(1)[0]
        slots = [k for k, v in recs.items()
                 if tuple(round(c, 2) for c in v["xyz"]) == xyz]
        return xyz, slots

    @staticmethod
    def fleet_open(im):
        """t253 law: blue scroll-rail pixels at bands y 59-68 / 450-457,
        x 606-635 of the FLEET window."""
        px = im.load()
        n = 0
        for (y0, y1) in ((59, 68), (450, 457)):
            for y in range(y0, y1):
                for x in range(606, 635):
                    r, g, b = px[x, y]
                    if b > 150 and b - r > 60:
                        n += 1
        return n

    def enter_system_via_fleet(self, map_im):
        """FLEET sidebar (553,184 = windows.txt rect centre) -> left-click row
        1 (200,93) JUMPS to that ship's orbital view (t253 MEASURED, 109479
        px). Far more deterministic than pip-guessing the galaxy map."""
        if not self.assert_on_map("fleet_open"):
            return None
        self.send(["click", "553", "184"])
        time.sleep(2.5)
        im = self.grab("fleet")
        d = self.diff_px(map_im, im)
        rails = self.fleet_open(im)
        self.log(f"FLEET click diff {d} rails {rails}")
        if d < 30000 and rails < 6:
            self.log("fleet window did not open")
            return None
        self.send(["click", "200", "93"])
        time.sleep(2.5)
        im2 = self.grab("orbital")
        d2 = self.diff_px(im, im2)
        self.log(f"row-1 jump diff {d2}")
        if d2 < 30000:
            self.log("row jump did not change the screen")
            return None
        return im2

    def escape_to_map(self, map_im):
        """Verified escape ladder, CHECK BEFORE EVERY PRESS (t285: one Escape
        at the bare map ejects the campaign). States: title -> abort(False);
        close-to-map baseline -> done(True); otherwise press Escape ONCE and
        re-check. Fleet rails / orbital view are just 'not the map'."""
        for step in range(4):
            cur = self.grab(f"esc{step}")
            if cur is None:
                return False
            f = self.orange_frac(cur)
            dm = self.diff_px(map_im, cur)
            rails = self.fleet_open(cur)
            self.log(f"escape check {step}: orange={f:.3f} diff_vs_map={dm} "
                     f"rails={rails}")
            if f > 0.20:
                self.log("TITLE on screen — campaign ejected; abort")
                return False
            if dm < 15000:
                return True
            self.send(["key", "Escape"])
            time.sleep(2.0)
        return False

    def enter_system(self, map_im):
        """Click a player star pip on the galaxy map; verify the screen
        changed big-time (system view replaced the map)."""
        if not self.assert_on_map("enter_system"):
            return None
        # pips: bright dots in the map region, prefer the CENTRAL quadrant
        px = map_im.load()
        cands = []
        for y in range(60, 440, 2):
            for x in range(40, 455, 2):
                r, g, b = px[x, y]
                if r + g + b > 380:
                    cands.append((abs(x - MAP_CENTER[0]) + abs(y - MAP_CENTER[1]),
                                  x, y))
        cands.sort()
        tried = []
        for _d, x, y in cands[:6]:
            tried.append((x, y))
            self.send(["click", str(x), str(y)])
            time.sleep(2.5)
            im = self.grab("system")
            d = self.diff_px(map_im, im)
            self.log(f"pip click ({x},{y}) screen diff {d}")
            if d > 15000:
                return im
        self.log(f"no pip click changed the screen; tried {tried}")
        return None

    def orbital_ship_px(self, im):
        """Bright non-terrain dots in the orbital grid area — ship-clip
        candidates. COS_SHIP pips are bright; terrain bodies sit on yellow
        stalks. Returns up to 6 (x, y) sorted by luminance, map-region only."""
        px = im.load()
        cands = []
        for y in range(60, 430, 2):
            for x in range(50, 450, 2):
                r, g, b = px[x, y]
                if r + g + b > 420:
                    cands.append((r + g + b, x, y))
        cands.sort(reverse=True)
        out = []
        for _s, x, y in cands:
            if all(abs(x - ux) > 8 or abs(y - uy) > 8 for ux, uy in out):
                out.append((x, y))
            if len(out) >= 6:
                break
        return out

    def select_and_order(self, sys_im, watch_slots):
        """batmode help VERBATIM: 'A ship can be used by selecting it and then
        choosing the appropriate device'; 'You can move a selected ship by
        clicking on a desired destination.' => click a ship clip (select),
        then click a destination point. WITNESS = ring order bytes (kind +0x58
        etc.) change on a watch slot. Destination chosen OFFSET from the ship
        (a bare click on the ship again opens/views it: 'view a selected planet
        by clicking it again' — offsets avoid re-clicking the same object)."""
        pre_bytes = self.order_bytes(watch_slots)
        ship_pts = self.orbital_ship_px(sys_im)
        self.log(f"orbital ship candidates: {ship_pts}")
        dests_off = [(60, -40), (-70, 30), (40, 70)]
        for (sx, sy) in ship_pts[:4]:
            if not self.assert_on_map("select"):
                return None
            self.send(["click", str(sx), str(sy)])
            time.sleep(1.5)
            im = self.grab(f"sel_{sx}_{sy}")
            g = self.green_count(im)
            dsel = self.diff_px(sys_im, im)
            self.log(f"select click ({sx},{sy}) green={g} diff_vs_sys={dsel}")
            if dsel > 40000:
                # navigated (planet detail / ship window) instead of selecting
                # — unwind ONE level and try the next candidate
                self.send(["key", "Escape"])
                time.sleep(1.5)
                chk = self.grab(f"selback_{sx}_{sy}")
                if chk is not None and self.orange_frac(chk) > 0.20:
                    self.log("Escape hit TITLE from system view — abort "
                             "(t285)")
                    return None
                sys_im = chk if chk is not None else sys_im
                # L3 FIX: don't skip — selection likely PERSISTS after the
                # Escape-unwind (selfplay.md list-handle law); fall through
                # and try the destination clicks from the restored view.
            for (dx, dy) in dests_off:
                dxp, dyp = sx + dx, sy + dy
                if not (50 < dxp < 450 and 60 < dyp < 430):
                    continue
                # batmode help VERBATIM: 'move a SELECTED ship by clicking on
                # a desired destination' => LEFT click first; click3 (t244
                # order-mode) is the fallback below.
                self.send(["click", str(dxp), str(dyp)])
                time.sleep(1.5)
                im2 = self.grab(f"dest_{dxp}_{dyp}")
                g2 = self.green_count(im2)
                self.log(f"dest click3 ({dxp},{dyp}) green={g2}")
                time.sleep(12)
                pb = self.order_bytes(watch_slots)
                ch = {k: v for k, v in pb.items() if pre_bytes.get(k) != v}
                if ch:
                    self.log(f"ORDER ISSUED (select+click3, ring witness): {ch}")
                    return dict(how="select+click3", click=[dxp, dyp],
                                slots=sorted(int(k) for k in ch))
                # vendor alt choreography: plain left-click destination
                self.send(["click", str(dxp), str(dyp)])
                time.sleep(12)
                pb2 = self.order_bytes(watch_slots)
                ch2 = {k: v for k, v in pb2.items() if pre_bytes.get(k) != v}
                if ch2:
                    self.log(f"ORDER ISSUED (select+click, ring witness): {ch2}")
                    return dict(how="select+click", click=[dxp, dyp],
                                slots=sorted(int(k) for k in ch2))
        return None

    def issue_order(self, sys_im, watch_slots):
        """Try choreographies inside the system view; WITNESS from the ring
        that a watch-slot ship's order bytes moved (kind +0x58 / target
        +0x59..0x68 / order byte) or green marker pixels appeared.
        A: left-click dest (batmode help: selected ship + click dest).
        C: right-click dest (t244 order mode, green marker), witness green."""
        base_green = self.green_count(sys_im)
        self.log(f"system view green baseline {base_green}")
        pre_bytes = self.order_bytes(watch_slots)
        pts = [(236, 200), (280, 240), (200, 260), (250, 160)]
        for (x, y) in pts:
            if not self.assert_on_map("issue_order"):
                return None
            self.send(["click3", str(x), str(y)])
            time.sleep(2.0)
            im = self.grab(f"order_{x}_{y}")
            g = self.green_count(im)
            d = self.diff_px(sys_im, im)
            self.log(f"click3 ({x},{y}) green {g} (base {base_green}) diff {d}")
            marker = g >= base_green + 4 or (g >= 6 and d > 2000)
            # give the ring one cadence to reflect an issued order
            time.sleep(12)
            post_bytes = self.order_bytes(watch_slots)
            changed = {k: v for k, v in post_bytes.items()
                       if pre_bytes.get(k) != v}
            if changed:
                self.log(f"ORDER ISSUED (ring witness): {changed}")
                return dict(how="ring", click=[x, y],
                            slots=sorted(int(k) for k in changed))
            if marker:
                # order mode armed but no ring change yet — left-click the
                # same point as confirm, then re-check
                self.send(["click", str(x), str(y)])
                time.sleep(12)
                post2 = self.order_bytes(watch_slots)
                ch2 = {k: v for k, v in post2.items()
                       if pre_bytes.get(k) != v}
                if ch2:
                    self.log(f"ORDER ISSUED (marker+confirm, ring witness): "
                             f"{ch2}")
                    return dict(how="marker+confirm", click=[x, y],
                                slots=sorted(int(k) for k in ch2))
                self.log("marker appeared but order bytes unmoved after "
                         "confirm click")
        return None

    def order_bytes(self, slots):
        """kind(+0x58) + target/order fields (+0x59..+0x68) + MOVES/FUEL hex
        per watch slot from the newest ring slot."""
        rows = self.ring_mem_rows()
        out = {}
        if not rows:
            return out
        sp = rows[-1]["path"]
        try:
            mem = zipfile.ZipFile(sp).read("Memory")
        except Exception:
            return out
        B = SL.base_of(mem, self.anch)
        if B is None:
            return out
        base, n = SL.ship_array_law(mem, B)
        for k in slots:
            k = int(k)
            if k >= n:
                continue
            r = base + k * SL.SHIP["stride"]
            out[str(k)] = mem[r + 0x58:r + 0x69].hex() + "|" + \
                struct.pack("<HH", *struct.unpack_from("<HH", mem, r + 0x88)).hex()
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--disp", default="96")
    ap.add_argument("--tl", type=int, default=1500)
    ap.add_argument("--settle", type=int, default=45)
    ap.add_argument("--boot", type=int, default=150)
    args = ap.parse_args()

    for p, why in [(SCRATCH, "scratch copy"), (PAYLOAD, "payload"),
                   (OCT29, "Oct-29 campaign backup"), (DOSBOX, "dosbox-x")]:
        if not os.path.exists(p):
            print(f"HARNESS ERROR: missing {why} {p}")
            return 2
    if os.path.abspath(SCRATCH).startswith(os.path.join(ROOT, "game") + os.sep):
        print("HARNESS ERROR: refusing to mount game/")
        return 2
    if hashlib.md5(open(OCT29, "rb").read()).hexdigest() != OCT29_MD5:
        print("HARNESS ERROR: Oct-29 backup md5 mismatch")
        return 2

    s = Session(args)
    s.log(f"t293 move-order capture start out={s.out}")
    s.launch()
    rc = 1
    try:
        if not s.wait_title():
            s.log("NEGATIVE class BREAK-lottery: title never appeared")
            return 1
        if not s.enter_campaign():
            s.log("NEGATIVE: campaign entry failed (title still up / ring "
                  "never loaded)")
            return 1
        time.sleep(s.a.settle)
        rows0 = s.sample("loaded")
        if not rows0 or not rows0[-1].get("recs"):
            s.log("NEGATIVE: ring has no ship records after settle")
            return 1
        # guarded drain ONCE after load (t244 saw popups after resume)
        closed = s.drain_popups()
        s.log(f"post-load popup drain closed {closed}")

        map_im = s.grab("map")
        xyz, slots = s.pick_target(rows0)
        s.log(f"target star xyz={xyz} orbit slots={slots}")
        if xyz is None:
            s.log("NEGATIVE: no owner-0 ship found in the ring")
            return 1

        order = None
        in_system = False
        all_mine = list((rows0[-1].get("recs") or {}).keys())
        # ROUTE 1 (deterministic, t253-measured): FLEET sidebar -> row jump.
        sys_im = s.enter_system_via_fleet(map_im)
        if sys_im is None:
            s.log("fleet route failed — trying galaxy-pip route")
            sys_im = s.enter_system(map_im)
        if sys_im is not None:
            in_system = True
            r = s.select_and_order(sys_im, all_mine)
            if r is None:
                r = s.issue_order(sys_im, all_mine)
            if r:
                order = dict(**r, watch=all_mine)
                s.log(f"ORDER ISSUED via {r['how']} at {r['click']}")
        else:
            s.log("system view never opened — will still test the ring axis "
                  "for any order effect")

        # RETURN TO THE BARE MAP before End Turn (t244/t245: modal views
        # swallow NEXTTURN). Verified escape ladder (t285: NEVER Escape blind
        # — one Escape at the bare map ejects the campaign to title).
        on_map = True
        if in_system:
            on_map = s.escape_to_map(map_im)
            if not on_map:
                s.sample("not_on_map")
                return 1

        pre = s.sample("pre_turn")
        pre_by_file = {d["file"]: d for d in pre}

        # End Turn presses with advance detection + STOP-AND-LOOK law
        noadv = 0
        presses = 0
        rows = pre
        turn_base = turn0 = max((d["turn"] for d in pre), default=0)
        s.log(f"turn baseline {turn0}")
        deadline = time.time() + 420
        while time.time() < deadline and presses < 4:
            if not s.assert_on_map("end_turn"):
                break
            s.send(["click", str(NEXTTURN[0]), str(NEXTTURN[1])])
            presses += 1
            t0 = time.time()
            advanced = False
            while time.time() - t0 < 90:
                time.sleep(5)
                rows = s.ring_mem_rows()
                if rows and max(d["turn"] for d in rows) > turn0:
                    advanced = True
                    break
            s.log(f"press {presses}: advanced={advanced} "
                  f"turn_now={max((d['turn'] for d in rows), default=-1)}")
            if advanced:
                noadv = 0
                turn0 = max(d["turn"] for d in rows)
                s.sample(f"turn{turn0}")
                s.grab(f"map_after_t{turn0}")
                # t245: turn-end popups SERIALIZE after the AI pass and swallow
                # every further input — drain BEFORE the next press.
                closed = s.drain_popups()
                if closed:
                    s.log(f"post-turn drain closed {closed}")
                if turn0 >= turn_base + 2 and presses >= 2:
                    break
            else:
                # t245 serialize law: a popup (dark OR the LIGHT construction
                # EVENTWIN) swallows every input. Identify-and-close before
                # counting the no-advance (t293 measured: presses 2-3 of L2
                # died behind a construction-complete EVENTWIN the old detector
                # could not see).
                im = s.grab("noadv_check")
                if im is not None and s.eventwin_open(im):
                    s.log("EVENTWIN popup detected after no-advance press")
                    if s.close_eventwin():
                        noadv = 0
                        continue
                noadv += 1
                if noadv >= 2:
                    s.log("STOP-AND-LOOK: 2 consecutive no-advance presses "
                          "(t289 law); draining popups once then ending the "
                          "press loop")
                    s.drain_popups()
                    break
        post = s.sample("final")

        # ---- verdict ----
        # A flight counts ONLY if the moved ship ALSO shows order/budget
        # evidence (t293 L2 lesson: constant-kind constant-budget dx equal to
        # the t189 lane steps {28,14,4.6667} is background lane traffic that
        # was ordered long before this session — NEVER a witness).
        moved = []
        if pre and post:
            pmap = pre[-1].get("recs") or {}
            for d in sorted(post, key=lambda x: x["turn"]):
                if d["turn"] <= pre[-1]["turn"]:
                    continue
                for k, v in (d.get("recs") or {}).items():
                    pv = pmap.get(k)
                    if not pv or v["xyz"] == pv["xyz"]:
                        continue
                    evidence = (v["kind"] != pv["kind"]
                                or v["moves"] != pv["moves"]
                                or v["fuel"] != pv["fuel"])
                    moved.append(dict(file=d["file"], turn=d["turn"],
                                      slot=int(k),
                                      pre=[list(pv["xyz"]), pv["kind"],
                                           pv["moves"], pv["fuel"]],
                                      post=[list(v["xyz"]), v["kind"],
                                            v["moves"], v["fuel"]],
                                      evidence=evidence))
        # THE witness law (t293 L2 lesson): background lane traffic (constant
        # kind/budget, dx == t189 step) is NEVER a flight. A POSITIVE requires
        # the ORDER-ISSUED slot (order_bytes delta, logged) to be the slot that
        # moved across a turn boundary.
        wslots = set((order or {}).get("slots") or [])
        witnesses = [m for m in moved if m["slot"] in wslots]
        s.log("VERDICT order=" + json.dumps(order) + " moved=" +
              json.dumps(moved[:8]) + f" witnesses={len(witnesses)}")
        if witnesses:
            s.log("POSITIVE: issued order + witnessed movement — evidence dir "
                  "above")
            rc = 0
        else:
            s.log("NEGATIVE: no issued-order witness with attributable "
                  "movement (lane background traffic excluded)")
            rc = 1
        return rc
    finally:
        s.log(f"final ring snapshot; rc={rc}; killing recorded pid "
              f"{s.child.pid}")
        try:
            s.sample("cleanup")
        except Exception:
            pass
        s.cleanup()


if __name__ == "__main__":
    sys.exit(main())
