#!/usr/bin/env python3
"""t298 — LIVE MOVE-ORDER WITNESS #2 (fixed picker, correct gates, OQ-019 r1/r3).

r297 base class + four fixes (docs/re/_wip_t298.md T298-A..D):
 1. End Turn ONCE after campaign entry (t297 gating fact: owner-0 fleet has
    no kind-4 ship at t=1086; slot 8 lands kind-4 MOVES=12 at t=1087).
 2. Candidate picker: owner==0 && kind==4 && MOVES>0 from the NEWEST ring
    rows (post-End-Turn), and FLEET ROW PICKER = click row candidates
    (93,200,305,410) until ds:0x43504's star name == target ship's nearest
    star (system-view identity oracle T298-D: value is a PHYSICAL star-record
    pointer; name at value+0x88+0x1c).
 3. SHIP SPRITE finder by COLOUR CLASS (tan hull R>100, R-B>45, R>=G>=B,
    G-B>12; y>=112; bbox<=64; >=60px; >80px from the planet blob) —
    validated OFFLINE on t297 11_orbital.png (finds (48,151); vision said
    (48,148)). Luminance floods MERGED planet+chrome (t297 trap).
 4. DELTA witnesses vs the fresh post-End-Turn baseline: kind-2 census,
    target ship record bytes +0x30..+0x60 (order-list region per t296 msg-
    0x50 law [sel+0x42+ebx*4]), ds:0x43504/0x43508, command ring
    (game obj B+OFF+0x7a35c, widx u16 @+0x44ac, entry stride 10 =
    {code u16, param u32, extra u32} — T298-C; ring churns at turn
    boundary, so mid-battery ring deltas are the signal).

BATTERY (batcon re-read T298-B: dl = kind of the CLICKED clip):
  S1 click ship sprite          (dl==2 @0x1b9f6: mode 0 -> SELECT -> 2)
  S2 right-click empty          (STATE t298 item 5: 0x1ba45/0x1ba8c probe)
  S3 click ship sprite again    (mode 2 no-op / re-select after S2 deselect)
  S4 left-click PLANET blob     (dl==3 @0x1bad3: mode==2 -> relay 0x326 =
                                 ORDER; if selection was lost this NAVIGATES
                                 — detected by star-name change -> Escape +
                                 retry with next sprite, max 2 sprites)
  S5 right-click PLANET blob    (dl==3 leg ignores the button byte)
Then escape ladder -> map, End Turn x2 + drain, verdict: kind 4->2 on the
watched slot AND movement with order evidence (t293 verdict law).

SAFETY (binding, docs/BLOCKED.md runbook): scratch game-wp only (asserted);
private Xvfb; production :9 ring-tail read-only; output=x11; -time-limit;
kill-by-recorded-PID in finally; assert_on_map BEFORE every click; NEVER
Escape at the bare map; EVENTWIN closed by Escape only (t293 L3).

usage: r298_order_session.py [--disp 97] [--tl 1500] [--settle 45] [--boot 170]
Exit 0 = order ISSUED + kind-2/flight WITNESSED. 1 = honest negative. 2 = harness.
"""
import argparse
import glob
import json
import os
import os.path as op
import struct
import sys
import time
import zipfile

ROOT = op.abspath(op.join(op.dirname(__file__), ".."))
sys.path.insert(0, op.dirname(op.abspath(__file__)))
import r1_slot as SL                                    # noqa: E402
import r293_move_session as R293                        # noqa: E402

FLEET_ROWS = (93, 200, 305, 410)     # row hit-points measured off t297
                                    # 10_fleet.png (name bands 52-64,
                                    # 160-170, 264-276, 372-382; pitch ~104)


class Sess(R293.Session):
    """r293 drive class + t298 instruments."""

    def __init__(self, args):
        super().__init__(args)
        self.out = op.join(ROOT, "work/r1",
                           f"t298-order-{time.strftime('%Y%m%d-%H%M%S')}")
        os.makedirs(op.join(self.out, "save"), exist_ok=True)
        self.savedir = op.join(self.out, "save")
        self.logp = op.join(self.out, "session.log")
        self.dbl = op.join(self.out, "dosbox.out")
        self.evidence = []

    # ---------- RAM ----------
    def newest_sav(self):
        rows = self.ring_mem_rows()
        return rows[-1]["path"] if rows else None

    def read_mem(self, path):
        try:
            return zipfile.ZipFile(path).read("Memory")
        except Exception:
            return None

    def ship_state(self, mem, B):
        base, n = SL.ship_array_law(mem, B)
        out = {}
        for k in range(n):
            r = base + k * SL.SHIP["stride"]
            if r + SL.SHIP["stride"] > len(mem):
                break
            out[k] = dict(
                owner=struct.unpack_from("<I", mem, r + 0x54)[0] >> 16,
                kind=mem[r + 0x58],
                xyz=struct.unpack_from("<3f", mem, r + 0x9e),
                moves88=struct.unpack_from("<H", mem, r + 0x88)[0],
                raw3060=mem[r + 0x30:r + 0x60].hex(),
                addr=r)
        return out

    def star_name_at(self, mem, ptr_phys):
        """ds:0x43504 holds a PHYSICAL star-record pointer; name at
        member(ptr)+0x1c (T298-A pointer law, 'Icarus' verified)."""
        m = ptr_phys + 0x88 + 0x1c
        if not (0 < m < len(mem) - 20):
            return ""
        z = mem.find(b"\x00", m, m + 20)
        s = mem[m:z if z > 0 else m + 20]
        try:
            s.decode("ascii")
        except Exception:
            return ""
        return s.decode("ascii", "replace").strip() if s.isalnum() or not s else ""

    def nearest_star_name(self, mem, B, xyz):
        """Star grid: name at member 0x255be1 + (B-0x1BF450) + 96k, position
        f32 triple at name-0x14 (r1_star_table law)."""
        H = B - 0x1BF450
        best = (1e18, "")
        for k in range(52):
            p = 0x255be1 + H + 96 * k
            if p + 0x40 > len(mem):
                break
            sx, sy, sz = struct.unpack_from("<3f", mem, p - 0x14)
            if not all(-20000 < v < 20000 for v in (sx, sy, sz)):
                continue
            d = ((sx - xyz[0]) ** 2 + (sy - xyz[1]) ** 2 +
                 (sz - xyz[2]) ** 2) ** 0.5
            if d < best[0]:
                z = mem.find(b"\x00", p, p + 20)
                nm = mem[p:z if z > 0 else p + 20].decode("ascii", "replace")
                best = (d, nm)
        return best

    def ring_state(self, mem, B):
        g = B + SL.OFF + 0x7a35c
        widx = struct.unpack_from("<H", mem, g + 0x44ac)[0]
        ents = []
        for s in range(8):
            c = struct.unpack_from("<H", mem, g + 0x422c + s * 10)[0]
            p = struct.unpack_from("<I", mem, g + 0x422e + s * 10)[0]
            e = struct.unpack_from("<I", mem, g + 0x4232 + s * 10)[0]
            if c or p or e:
                ents.append([c, p, e])
        return widx, ents

    def snapshot(self, mem, B, tgt):
        st = self.ship_state(mem, B)
        kind2 = sorted(k for k, v in st.items()
                       if v["owner"] == 0 and v["kind"] == 2)
        sel = struct.unpack_from("<I", mem, B + SL.OFF + 0x43504)[0]
        dst = struct.unpack_from("<I", mem, B + SL.OFF + 0x43508)[0]
        widx, ents = self.ring_state(mem, B)
        t = st.get(tgt, {})
        return dict(
            turn=struct.unpack_from("<I", mem, B + SL.OFF + 0x12e10)[0],
            kind2_owner0=kind2,
            sel43504=sel, star=self.star_name_at(mem, sel),
            dst43508=dst, ring_widx=widx, ring_ents=ents,
            tgt_kind=t.get("kind"), tgt_moves88=t.get("moves88"),
            tgt_xyz=list(t.get("xyz", [])), tgt_raw3060=t.get("raw3060", ""))

    def witness(self, tag, tgt, base_snap):
        rec = {"tag": tag}
        p = self.newest_sav()
        mem = self.read_mem(p) if p else None
        if mem is None:
            rec["error"] = "no mem"
            self.evidence.append(rec)
            self.log(f"WITNESS {tag}: no memory yet")
            return rec
        B = SL.base_of(mem, self.anch)
        snap = self.snapshot(mem, B, tgt)
        rec.update(snap)
        deltas = {}
        for k in ("kind2_owner0", "sel43504", "star", "dst43508",
                  "ring_widx", "ring_ents", "tgt_raw3060", "tgt_kind"):
            if snap.get(k) != (base_snap or {}).get(k):
                deltas[k] = [(base_snap or {}).get(k), snap.get(k)]
        rec["deltas"] = deltas
        self.evidence.append(rec)
        self.log(f"WITNESS {tag}: file={op.basename(str(p))} t={snap['turn']} "
                 f"kind2={snap['kind2_owner0']} star={snap['star']!r} "
                 f"dst={snap['dst43508']:#x} ring_w={snap['ring_widx']} "
                 f"tgt(kind,m88)={snap['tgt_kind']},{snap['tgt_moves88']} "
                 f"DELTAS={list(deltas)}")
        return rec

    # ---------- screen ----------
    def ship_sprites(self, im):
        """Tan-hull colour class; exclude icon strip y<112 and planet
        neighbourhood. Returns [(x,y,px)] sorted by px desc."""
        px = im.load()
        W, H = im.size

        def tan(x, y):
            # BatModeWnd CLIENT RECT x 7..465 (windows.txt) — sidebar chrome
            # at x>466 is tan-coloured and MUST be excluded (t298 run 3 bug).
            if y < 112 or x < 8 or x > 465:
                return False
            r, g, b = px[x, y]
            return r > 100 and r - b > 45 and r >= g >= b and g - b > 12
        seen = set()
        comps = []
        for y in range(112, H):
            for x in range(8, W - 8):
                if not tan(x, y) or (x, y) in seen:
                    continue
                stack = [(x, y)]
                comp = []
                seen.add((x, y))
                while stack and len(comp) < 800:
                    cx, cy = stack.pop()
                    comp.append((cx, cy))
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            nx, ny = cx + dx, cy + dy
                            if tan(nx, ny) and (nx, ny) not in seen:
                                seen.add((nx, ny))
                                stack.append((nx, ny))
                if len(comp) < 60:
                    continue
                xs = [c[0] for c in comp]
                ys = [c[1] for c in comp]
                if max(xs) - min(xs) > 64 or max(ys) - min(ys) > 64:
                    continue
                comps.append((len(comp),
                              int(sum(xs) / len(comp)),
                              int(sum(ys) / len(comp))))
        comps.sort(reverse=True)
        # planet exclusion: largest bright luminance blob
        planet = None
        best = 0
        for y in range(112, H, 4):
            for x in range(8, W - 8, 4):
                r, g, b = px[x, y]
                if r + g + b > 380:
                    n = 0
                    for yy in range(max(112, y - 30), min(H, y + 30), 4):
                        for xx in range(max(8, x - 30), min(W, x + 30), 4):
                            if sum(px[xx, yy]) > 380:
                                n += 1
                    if n > best:
                        best, planet = n, (x, y)
        out = []
        for n, cx, cy in comps:
            if planet and abs(cx - planet[0]) < 80 and abs(cy - planet[1]) < 80:
                continue
            out.append((cx, cy, n))
        return out

    def planet_point(self, im):
        """Largest bright luminance blob centroid in the map field (kind-3
        clip target — planet clips exist for every planet in-system).
        CLIENT RECT BOUND x<=465: sidebar chrome is bright (t298 run 3)."""
        px = im.load()
        W, H = im.size
        best = (0, 0, 0)
        for y in range(112, H, 2):
            for x in range(8, min(W - 8, 466), 2):
                if sum(px[x, y]) <= 380:
                    continue
                n = 0
                sx = sy = 0
                for yy in range(max(112, y - 20), min(H, y + 20), 2):
                    for xx in range(max(8, x - 20),
                                    min(min(W - 8, 466), x + 20), 2):
                        if sum(px[xx, yy]) > 380:
                            n += 1
                            sx += xx
                            sy += yy
                if n > best[0]:
                    best = (n, sx // n, sy // n)
        return (best[1], best[2]) if best[0] else None

    def empty_point(self, im, avoid):
        for cand in ((236, 200), (140, 200), (300, 150), (400, 430),
                     (120, 300), (350, 250), (250, 390), (180, 130)):
            if all(abs(cand[0] - cx) > 45 or abs(cand[1] - cy) > 45
                   for cx, cy in avoid) and self.is_black_at(im, *cand):
                return cand
        return None

    def is_black_at(self, im, x, y, rad=6, frac=0.85):
        px = im.load()
        tot = dark = 0
        for yy in range(max(0, y - rad), min(im.height, y + rad)):
            for xx in range(max(0, x - rad), min(im.width, x + rad)):
                tot += 1
                if sum(px[xx, yy]) < 200:
                    dark += 1
        return tot and dark / tot >= frac


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--disp", default="97")
    ap.add_argument("--tl", type=int, default=1500)
    ap.add_argument("--settle", type=int, default=45)
    ap.add_argument("--boot", type=int, default=170)
    args = ap.parse_args()

    for p, why in [(R293.SCRATCH, "scratch copy"), (R293.PAYLOAD, "payload"),
                   (R293.OCT29, "Oct-29 campaign backup"),
                   (R293.DOSBOX, "dosbox-x")]:
        if not os.path.exists(p):
            print(f"HARNESS ERROR: missing {why} {p}")
            return 2
    if os.path.abspath(R293.SCRATCH).startswith(
            op.join(ROOT, "game") + op.sep):
        print("HARNESS ERROR: refusing to mount game/")
        return 2
    import hashlib
    if hashlib.md5(open(R293.OCT29, "rb").read()).hexdigest() != R293.OCT29_MD5:
        print("HARNESS ERROR: Oct-29 backup md5 mismatch")
        return 2

    s = Sess(args)
    s.log(f"t298 order-witness session start out={s.out}")
    s.launch()
    rc = 1
    try:
        if not s.wait_title():
            s.log("NEGATIVE: title never appeared")
            return 1
        if not s.enter_campaign():
            s.log("NEGATIVE: campaign entry failed")
            return 1
        time.sleep(s.a.settle)
        closed = s.drain_popups()
        s.log(f"post-load popup drain closed {closed}")

        # ---- END TURN ONCE (t298 item 1: slot 8 lands kind-4 at t+1) ----
        if not s.assert_on_map("pre_endturn"):
            return 1
        rows = s.ring_mem_rows()
        turn0 = max((d["turn"] for d in rows), default=0)
        presses = 0
        advanced = False
        while presses < 3 and not advanced:
            if not s.assert_on_map(f"endturn{presses}"):
                return 1
            s.send(["click", str(R293.NEXTTURN[0]), str(R293.NEXTTURN[1])])
            presses += 1
            t0 = time.time()
            while time.time() - t0 < 90:
                time.sleep(5)
                rows = s.ring_mem_rows()
                if rows and max(d["turn"] for d in rows) > turn0:
                    advanced = True
                    break
            s.log(f"pre-battery press {presses}: advanced={advanced}")
            if not advanced:
                im = s.grab("ewc_pre")
                if im is not None and s.eventwin_open(im):
                    if not s.close_eventwin():
                        s.log("NEGATIVE: EVENTWIN would not close")
                        return 1
        if not advanced:
            s.log("NEGATIVE: could not advance one turn pre-battery")
            return 1
        closed = s.drain_popups()
        # t298 LAW RE-APPLICATION (t293 L3): drain_popups is BLIND to the
        # light-background EVENTWIN (white-text detector); the post-turn
        # construction popup swallows every subsequent click (run 2: FLEET
        # diff 216 with eventwin count 503 on screen). Escape is the law.
        if not s.close_eventwin():
            s.log("NEGATIVE: post-turn EVENTWIN would not close")
            return 1
        s.log(f"post-turn drain closed {closed}")

        # ---- TARGET from newest ring rows (post-End-Turn) ----
        rows = s.ring_mem_rows()
        if not rows or not rows[-1].get("recs"):
            s.log("NEGATIVE: ring has no ship records")
            return 1
        recs0 = rows[-1]["recs"]
        cand = [k for k, v in recs0.items()
                if v["owner"] == 0 and v["kind"] == 4 and v["moves"] > 0]
        s.log(f"post-turn t={rows[-1]['turn']} owner-0 n={len(recs0)} "
              f"kinds={sorted(set(v['kind'] for v in recs0.values()))} "
              f"cand(kind4,moves>0)={cand}")
        if not cand:
            s.log("NEGATIVE: no owner-0 kind-4 MOVES>0 after End Turn "
                  "(G1/G4 gates unsatisfiable — honest negative)")
            return 1
        target = int(sorted(cand)[0])
        mem_r = s.read_mem(rows[-1]["path"])
        B_r = SL.base_of(mem_r, s.anch)
        d_star, tgt_star_name = s.nearest_star_name(
            mem_r, B_r, recs0[target]["xyz"])
        s.log(f"target slot {target} nearest star {tgt_star_name!r} d={d_star:.0f}")

        # ---- FLEET ROW PICKER (t298 rework) ----
        if not s.close_eventwin():
            s.log("NEGATIVE: EVENTWIN open before fleet route")
            return 1
        # Listing order law [inferred, 1 datapoint t293 row-1->slot-1 + t253
        # "25 Ships" header + 4-row paging]: fleet list == ship-array order.
        # Slot 8 => 1-based position 8 => PAGE 2 (positions 5-8), ROW 4.
        # Paging: right-rail down arrow (620,453) (t253 measured blue-pixel
        # scroll pair (620,63)/(620,453)). Star identity via ds:0x43504 is
        # LOGGED but not gating: kind-4 xyz is system-local, so nearest-star
        # matching cannot identify the ship's system (measured t298: slot 8
        # kind-4 xyz (-352,-2080,-992) is 1911 units from any star).
        map_im = s.grab("map")
        if not s.assert_on_map("fleet_open"):
            return 1
        s.send(["click", "553", "184"])
        time.sleep(2.5)
        im = s.grab("fleet")
        d = s.diff_px(map_im, im)
        if d < 30000:
            # swallowed by a popup? close and click once more (t298)
            s.close_eventwin()
            s.send(["click", "553", "184"])
            time.sleep(2.5)
            im = s.grab("fleet2")
            d = s.diff_px(map_im, im) if im is not None else 0
        rails = s.fleet_open(im) if im is not None else 0
        s.log(f"FLEET click diff {d} rails {rails}")
        if d < 30000:
            s.log("NEGATIVE: fleet window did not open (post-retry)")
            return 1
        # Slot 8 = RANK 4 (1-based) among owner-0 ships in array order
        # (FLEETWND lists the player's fleet only — "25 Ships" header law).
        o0 = sorted(int(k) for k, v in recs0.items() if v["owner"] == 0)
        rank = o0.index(target)                  # 0-based
        page = 1 + rank // 4
        row_idx = rank % 4                       # 0-based row on that page
        s.log(f"fleet route: target {target} rank {rank} -> page {page} "
              f"row {row_idx}")
        for _pg in range(page - 1):
            if not s.assert_on_map(f"page{_pg}"):
                return 1
            s.send(["click", "620", "453"])      # down arrow
            time.sleep(2.0)
            im2 = s.grab(f"page_{_pg}")
            dd = s.diff_px(im, im2)
            s.log(f"page-turn {_pg+1}: diff {dd}")
            if dd < 3000:
                s.log("NEGATIVE: page turn did not redraw")
                return 1
            im = im2
        sys_im = None
        ry = FLEET_ROWS[row_idx]
        if not s.assert_on_map("rowjump"):
            return 1
        s.send(["click", "200", str(ry)])
        time.sleep(2.5)
        im2 = s.grab(f"rowjump_p{page}_r{ry}")
        d2 = s.diff_px(im, im2)
        star = ""
        for _try in range(3):                    # autosave cadence 10 s
            p = s.newest_sav()
            mem2 = s.read_mem(p)
            B2 = SL.base_of(mem2, s.anch) if mem2 else None
            if B2:
                star = s.star_name_at(
                    mem2, struct.unpack_from("<I", mem2,
                                             B2 + SL.OFF + 0x43504)[0])
                if star:
                    break
            time.sleep(5)
        s.log(f"page {page} row y={ry} (target slot {target}): "
              f"diff {d2} system star {star!r}")
        if d2 >= 30000:
            sys_im = im2
        else:
            s.log("NEGATIVE: row click did not open a system view")
            return 1

        # ---- BASELINE (fresh, post-End-Turn, in-system) ----
        p0 = s.newest_sav()
        mem0 = s.read_mem(p0)
        B = SL.base_of(mem0, s.anch)
        base_snap = s.snapshot(mem0, B, target)
        s.log(f"baseline {op.basename(p0)} B={B:#x} snap={json.dumps(base_snap)[:400]}")

        sprites = s.ship_sprites(sys_im)
        planet = s.planet_point(sys_im)
        emp = s.empty_point(sys_im, [(x, y) for x, y, _ in sprites] +
                            ([planet] if planet else []))
        s.log(f"sprites={sprites} planet={planet} empty={emp}")
        if not sprites:
            s.log("NEGATIVE: no tan-hull sprite found in target system view")
            return 1

        base_mtime = os.path.getmtime(p0) if p0 else time.time() - 60

        def fresh_sav():
            t0 = time.time()
            nonlocal base_mtime
            while time.time() - t0 < 18:
                p = s.newest_sav()
                if p and os.path.getmtime(p) > base_mtime + 0.5:
                    base_mtime = os.path.getmtime(p)
                    return p
                time.sleep(2)
            return s.newest_sav()

        def click_step(name, kind, pt):
            if pt is None:
                s.log(f"SKIP {name}: no target point")
                return {"tag": name, "skipped": True}, False
            if not s.assert_on_map(name):
                return None, True
            s.send([kind, str(pt[0]), str(pt[1])])
            time.sleep(1.5)
            imn = s.grab(name)
            navigated = imn is not None and s.diff_px(sys_im, imn) > 40000
            fresh_sav()
            p = s.newest_sav()
            memn = s.read_mem(p)
            Bn = SL.base_of(memn, s.anch) if memn else None
            rec = s.witness(name, target, base_snap) if (memn and Bn) \
                else {"tag": name, "error": "no mem"}
            rec["navigated"] = navigated
            return rec, navigated

        def back_to_target_system():
            """after a nav: Escape to map, reopen fleet, page+row re-jump"""
            if not s.escape_to_map(map_im):
                return None
            s.send(["click", "553", "184"])
            time.sleep(2.5)
            imf = s.grab("fleet2")
            if imf is None or s.diff_px(map_im, imf) < 30000:
                s.log("re-open fleet failed")
                return None
            for _pg in range(page - 1):
                s.send(["click", "620", "453"])
                time.sleep(2.0)
            s.send(["click", "200", str(ry)])
            time.sleep(2.5)
            im2 = s.grab("rj2")
            if im2 is None or s.diff_px(imf, im2) < 30000:
                s.log("re-jump row did not change screen")
                return None
            return im2

        issued = None
        order_how = None
        # S1 select
        rec, nav = click_step("S1_select_ship", "click",
                              (sprites[0][0], sprites[0][1]))
        if rec is None:
            return 1
        if nav:
            sys_im = back_to_target_system()
            if sys_im is None:
                return 1
        # S2 right-click empty (STATE t298 item 5 probe)
        if emp:
            rec2, nav2 = click_step("S2_empty_right", "click3", emp)
            if rec2 is None:
                return 1
        # S3 re-click ship (no-op at mode 2; re-select if S2 deselected)
        rec3, nav3 = click_step("S3_ship_again", "click",
                                (sprites[0][0], sprites[0][1]))
        if rec3 is None:
            return 1
        # S4 left-click planet (ORDER leg if still selected; NAV if not)
        if planet:
            rec4, nav4 = click_step("S4_planet_left", "click", planet)
            if rec4 is None:
                return 1
            if nav4:
                s.log("S4 NAVIGATED -> selection was lost; re-enter, retry "
                      "with sprite #2 if any")
                sys_im = back_to_target_system()
                if sys_im is None:
                    return 1
                sprites = s.ship_sprites(sys_im)
                planet = s.planet_point(sys_im) or planet
                if len(sprites) >= 2:
                    click_step("S5_select_ship2", "click",
                               (sprites[1][0], sprites[1][1]))
                    rec4, nav4 = click_step("S6_planet_left2", "click",
                                            planet)
                    if rec4 and not rec4.get("navigated") and \
                            (rec4.get("deltas") or {}):
                        issued = dict(how="S6 click planet sprite2 "
                                          "(dl==3 relay 0x326)",
                                      click=list(planet))
            if rec4 and not rec4.get("navigated") and (
                    rec4.get("deltas") or {}):
                issued = dict(how="S4/S6 click planet (dl==3 relay 0x326)",
                              click=list(planet))
        # S5 right-click planet (button-agnostic leg)
        if planet and not issued:
            rec5, nav5 = click_step("S7_planet_right", "click3", planet)
            if rec5 is None:
                return 1
            if rec5 and not rec5.get("navigated") and (
                    rec5.get("deltas") or {}):
                issued = dict(how="S7 right-click planet", click=list(planet))
        s.log("BATTERY DONE issued=" + json.dumps(issued))

        # ---- verdict path: End Turn x2 on the bare map ----
        if not s.escape_to_map(map_im):
            s.sample("not_on_map")
            s.log("NEGATIVE: could not get back to the bare map")
            return 1
        pre = s.sample("pre_turn")
        turn0 = max((d["turn"] for d in pre), default=0)
        turn_base = turn0
        presses = 0
        noadv = 0
        deadline = time.time() + 330
        rows = pre
        while time.time() < deadline and presses < 3:
            if not s.assert_on_map("end_turn"):
                break
            s.send(["click", str(R293.NEXTTURN[0]), str(R293.NEXTTURN[1])])
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
                closed = s.drain_popups()
                s.close_eventwin()      # EVENTWIN-blind drain fix (t298)
                if turn0 >= turn_base + 2:
                    break
            else:
                im = s.grab("noadv_check")
                if im is not None and s.eventwin_open(im):
                    if s.close_eventwin():
                        noadv = 0
                        continue
                noadv += 1
                if noadv >= 2:
                    s.log("STOP-AND-LOOK: 2 no-advance presses")
                    s.drain_popups()
                    break

        post = s.sample("final")
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
                    ev = (v["kind"] != pv["kind"] or v["moves"] != pv["moves"]
                          or v["fuel"] != pv["fuel"])
                    moved.append(dict(file=d["file"], turn=d["turn"],
                                      slot=int(k),
                                      pre=[list(pv["xyz"]), pv["kind"],
                                           pv["moves"], pv["fuel"]],
                                      post=[list(v["xyz"]), v["kind"],
                                            v["moves"], v["fuel"]],
                                      evidence=ev))
        kind2_post = sorted({int(k) for k in (post[-1].get("recs") or {})
                             if (post[-1]["recs"][k]["kind"] == 2
                                 and post[-1]["recs"][k]["owner"] == 0)})
        ordered_slots = set(kind2_post) | {target}
        for e in s.evidence:
            ordered_slots |= {int(k) for k in (e.get("kind2_owner0") or [])}
        tgt_moved = [m for m in moved if m["slot"] in ordered_slots]
        s.log("VERDICT issued=" + json.dumps(issued) +
              f" target={target} tgt_moved={len(tgt_moved)} "
              f"kind2_post={kind2_post} moved_n={len(moved)}")
        with open(op.join(s.out, "verdict.json"), "w") as f:
            json.dump(dict(issued=issued, target=target,
                           tgt_star_name=tgt_star_name,
                           evidence=s.evidence, moved=moved[:20],
                           tgt_moved=tgt_moved, kind2_post=kind2_post), f,
                      indent=1)
        kind2_seen = bool(kind2_post) or any(e.get("kind2_owner0")
                                             for e in s.evidence)
        raw_delta = any("tgt_raw3060" in (e.get("deltas") or {})
                        for e in s.evidence)
        if issued and kind2_seen and tgt_moved and \
                any(m["evidence"] for m in tgt_moved):
            s.log("POSITIVE: order issued + kind-2 witness + target slot "
                  "moved with order evidence across the turn boundary")
            rc = 0
        elif kind2_seen or raw_delta:
            s.log("PARTIAL: order-state witness present "
                  f"(kind2={kind2_seen}, raw3060_delta={raw_delta}); flight "
                  "NOT attributable this session — evidence banked")
            rc = 1
        else:
            s.log("NEGATIVE: no order-state witness anywhere (honest)")
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
