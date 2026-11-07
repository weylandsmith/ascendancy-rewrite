#!/usr/bin/env python3
"""t332 — BatControlWnd CHAIN LIVE WITNESS (OQ-016 residue-1 last uncited edge).

Question (docs/re/_wip_t331.md S7 verdict + STATE.md t332): does msg 0x1c01 ever
reach fn 0x156d4 (BatControlWnd, registry slot 61) in a live session, and if so
does the cited chain flow to the mode-1 arming store 0x1B7DD?

TWO INSTRUMENT FINDS THIS SESSION (docs/re/_wip_t332.md S1, fresh objdump of
work/ascend_restored.bin 0x16060..0x16200):
  * THE DELIVERY EDGE HAS A CANDIDATE INSIDE THE HANDLER ITSELF: the shared tail
    0x16162..0x1616f loads ebx=[ebp+0xa7] (BatControlWnd's OWN class table),
    edx=0x1c01, eax=ebp and does `call [ebx+0xc]` — a class-table slot-3
    SELF-RELAY (reached from the 0x16071 shield jmp, the 0x16145 jmp and the
    fallthrough of the 0x51 post at 0x1615d). An immediate census cannot see it,
    which is why t331 concluded "no static poster". Leg `relay1616f` measures it.
  * THE COORDINATE IN THE ASSIGNMENT IS IN GRAB SPACE, NOT CLICK SPACE: (80,100)
    is the ROOT-ORIGIN LAW FOR GRABS (r293_move_session.py:73 XOFF,YOFF used at
    :121 img.crop). Clicks go 1:1 with windows.txt (NEXTTURN (511,67) == rect
    474,52-548,82 centre, 64 clean turns; FLEET (553,184) == rect 474,169-632,199
    centre). So the My^Items rect 479,103-548,133 centre is CLICK (513,118);
    (593,218) as a click lands inside BatListWnd (474,142-632,394), not My^Items.
    Both are probed; the rect centres lead.

HEAVY-CHECK LAWS APPLIED (t330: an armed ENTRY leg consumes the census window —
the fired bp is BPDEL'd and the heavy check does not re-enter the same block
post-RUN). Therefore the session runs TWO sub-batteries in one launch:
  A) DOWNSTREAM legs armed (tbl15ef1, gate15fed, post1615d, relay1616f,
     post161d1, mode1_1b7dd, backch_1b180) + btn_hdlr as the instrument-alive
     control — banked stops carry full operand state.
  B) ENTRY leg armed ALONE (+control) in dedicated windows — separates "the
     window was never messaged" from "a downstream leg ate it", which A alone
     cannot do.
Ring oracle (the .sav axis, independent of the debugger): BatControlWnd and
BatModeWnd records located by magic 0x12345678 + RAW ASCII name at +0x20 (t331
law), read relative to the magic — [+0xb0] mode byte, [+0xb1], [+0xb7] MODE
(mode-1 store target), [+0xb9] the 0x1c01 state machine, [+0xb5]/[+0xbb] the
BatListWnd/BatModeWnd pointers. A live mode-1 store MUST show up as
BatModeWnd[+0xb7]==1 in a post-click save: that is the save-axis corroboration
of leg mode1_1b7dd.

SAFETY: scratch game-wp only (preflight asserts, never game/); OWN ring dir
(two-writer law); private Xvfb (never :9); core=normal; -time-limit; teardown
SIGKILL by RECORDED PID only (t325 SIGNAL LAW); Oct-29 md5-verified RESUME.GAM;
production :9 untouched. VENV INTERPRETER LAW (PIL).
Exit 0 = session ran and the instrument-alive control fired (census banked);
     1 = honest negative / control silent; 2 = harness error.
"""
import argparse
import json
import os
import os.path as op
import struct
import sys
import time

ROOT = op.abspath(op.join(op.dirname(__file__), ".."))
sys.path.insert(0, op.join(ROOT, "scripts"))
import r299_leg_session as L                       # noqa: E402
import r1_dbg_session as D                          # noqa: E402

P0 = D.P0
NEW_LEGS = {"fn156d4_entry": 0x156D4,   # BatControlWnd msg-handler ENTRY (eax=rec, edx=msg id)
            "tbl15ef1":      0x15EF1,   # jmp DWORD cs:[eax*4+0xb04] (RAM-rebased table)
            "gate15fed":     0x15FED,   # gizmo-flag gate block (0x1c01 table entry[1])
            "post1615d":     0x1615D,   # call 0x56ca4  POST msg 0x51 -> slot 63 (bit40 CLEAR)
            "relay1616f":    0x1616F,   # call [ebx+0xc] SELF-RELAY msg 0x1c01 (shared tail)
            "post161d1":     0x161D1,   # call 0x56ca4  POST msg 0x51 (bit40 SET block)
            "mode1_1b7dd":   0x1B7DD,   # mov BYTE[ebp+0xb7],1  MODE-1 ARMED (BatModeWnd)
            "backch_1b180":  0x1B180}   # BatModeWnd -> BatControlWnd back-channel post
CTRL = "btn_hdlr"                                # type-0 button handler: instrument-alive proof
LEGS_A = ["tbl15ef1", "gate15fed", "post1615d", "relay1616f", "post161d1",
          "mode1_1b7dd", "backch_1b180", CTRL]
LEGS_B = ["fn156d4_entry", CTRL]
ALL_LEGS = ["fn156d4_entry"] + LEGS_A
D.LEGS.update(NEW_LEGS)
L.LEGS.update(NEW_LEGS)

MY_ITEMS = (513, 118)          # windows.txt rect 479,103-548,133 centre
OTHER_ITEMS = (591, 118)       # windows.txt rect 557,103-626,133 centre
BATLIST_MID = (553, 200)       # windows.txt BatListWnd 474,142-632,394, item band
LITERAL = (593, 218)           # the assignment's literal number (inside BatListWnd)
MAGIC = b"\x78\x56\x34\x12"    # u32 0x12345678 LE, at rec+0x00, name at rec+0x20


class BatSess(D.DbgSession):
    """DbgSession + pre-resume operand capture (ebp grid, [ebp+0xbb]/[+0xb5]
    targets) + a .sav-axis window-record oracle + per-phase leg subsets."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.oper = []
        self.batrec = []
        s = self.s
        orig = s.bank_stop

        def bank332(tag):
            extra = self._operand_capture(tag)   # guest is STOPPED here
            rec = orig(tag)                      # proven r299 bank + resume/rearm
            if extra and isinstance(rec, dict):
                rec.update(extra)
                try:
                    with open(op.join(s.out, "hits.json"), "w") as fh:
                        json.dump(s.hits, fh, indent=1)
                except Exception:
                    pass
            return rec

        s.bank_stop = bank332                    # INSTANCE patch (t330 law)

    # ---------- operand capture at a stop ----------
    def _hx(self, v):
        return f"{v:#x}" if isinstance(v, int) else None

    def _u32(self, blob, off):
        try:
            return struct.unpack_from("<I", blob, off)[0]
        except Exception:
            return None

    def _name_at(self, blob, off):
        try:
            return blob[off:off + 24].split(b"\x00")[0].decode("latin1", "replace")
        except Exception:
            return None

    def _operand_capture(self, tag):
        s = self.s
        out = {}
        ebp = s.read_reg("ebp")
        edx = s.read_reg("edx")
        ecx = s.read_reg("ecx")
        if edx is not None:
            out["msg_id_lo"] = edx & 0xFFFF
        if ecx is not None:
            out["ecx"] = self._hx(ecx)
        if not (ebp and P0 < ebp < 0x10000000):
            return out
        blob = s.dump_mem(ebp, 0x28, f"o332hd{len(self.oper)}")
        if blob and len(blob) >= 4:
            out["ebp_head"] = {"magic_ok": blob[:4] == MAGIC,
                               "name": self._name_at(blob, 0x20)}
        # NOTE ON ALIGNMENT: the fields here are BYTE-granular (0xb0, 0xb7, 0xb9)
        # interleaved with DWORD pointers (0xb5 BatListWnd, 0xbb BatModeWnd), so a
        # 4-strided grid CANNOT address them. Every field is read with an explicit
        # unaligned u32/u8 at its own offset.
        g = s.dump_mem(ebp + 0x90, 0x40, f"o332g{len(self.oper)}")
        if g and len(g) >= 0x40:
            u = lambda o: struct.unpack_from("<I", g, o - 0x90)[0]
            out["ebp_fields"] = {
                "+0xb0_byte": g[0xb0 - 0x90],
                "+0xb1_dword": self._hx(u(0xb1)),
                "+0xb5_BatListWnd": self._hx(u(0xb5)),
                "+0xb7_byte_mode": g[0xb7 - 0x90],
                "+0xb9_byte_b9": g[0xb9 - 0x90],
                "+0xbb_BatModeWnd": self._hx(u(0xbb))}
        # [ebp+0xbb] = BatModeWnd record pointer (t331 S6): read ITS mode byte
        bp = s.dump_mem(ebp + 0xbb, 4, f"o332bb{len(self.oper)}")
        tgt = self._u32(bp, 0) if bp else None
        if tgt and P0 < tgt < 0x10000000:
            tb = s.dump_mem(tgt, 0x28, f"o332tm{len(self.oper)}")
            t7 = s.dump_mem(tgt + 0xa0, 0x20, f"o332t9{len(self.oper)}")
            ent = {"ptr": self._hx(tgt),
                   "magic_ok": bool(tb and tb[:4] == MAGIC),
                   "name": self._name_at(tb, 0x20) if tb else None}
            if t7 and len(t7) >= 0x20:
                tu = lambda o: struct.unpack_from("<I", t7, o - 0xa0)[0]
                ent["+0xb0_byte"] = t7[0xb0 - 0xa0]
                ent["+0xb1_dword"] = self._hx(tu(0xb1))
                ent["+0xb7_byte_mode"] = t7[0xb7 - 0xa0]   # mode-1 store target
                ent["+0xb9_byte"] = t7[0xb9 - 0xa0]
            out["mode_wnd"] = ent
        # [ebp+0xb5] = BatListWnd record pointer
        lp = s.dump_mem(ebp + 0xb5, 4, f"o332b5{len(self.oper)}")
        lt = self._u32(lp, 0) if lp else None
        if lt and P0 < lt < 0x10000000:
            lb = s.dump_mem(lt, 0x48, f"o332lm{len(self.oper)}")
            out["list_wnd"] = {"ptr": self._hx(lt),
                               "magic_ok": bool(lb and lb[:4] == MAGIC),
                               "name": self._name_at(lb, 0x20) if lb else None,
                               "slot41": lb[0x41] if lb and len(lb) > 0x41 else None}
        self.oper.append({"tag": tag, "wall": time.strftime("%H:%M:%S"), **out})
        with open(op.join(s.out, "operand.json"), "w") as fh:
            json.dump(self.oper, fh, indent=1)
        s.log(f"OPERAND {tag} ebp={self._hx(ebp)} msg={out.get('msg_id_lo')} "
              f"name={(out.get('ebp_head') or {}).get('name')!r} "
              f"b9={(out.get('ebp_fields') or {}).get('+0xb9_byte_b9')} "
              f"mode_wnd={(out.get('mode_wnd') or {}).get('name')!r}")
        return out

    # ---------- .sav-axis window-record oracle ----------
    def batrec_oracle(self, tag):
        s = self.s
        try:
            p = s.newest_sav()
            mm = s.read_mem(p) if p else None
            if not mm:
                return None
            B = L.SL.base_of(mm, s.anch)
            row = {"tag": tag, "sav": op.basename(p), "B": self._hx(B)}
            for want in ("BatControlWnd", "BatModeWnd", "BatListWnd"):
                pat = want.encode() + b"\x00"
                hits, off = [], 0
                while len(hits) < 6:
                    i = mm.find(pat, off)
                    if i < 0:
                        break
                    off = i + 1
                    rec = i - 0x20                  # magic at rec+0, name at rec+0x20
                    if rec < 0 or mm[rec:rec + 4] != MAGIC:
                        continue                    # pool string, not a record
                    u = lambda o: struct.unpack_from("<I", mm, rec + o)[0]
                    hits.append({
                        "member": self._hx(i), "rec_runtime": self._hx(rec - 0x88),
                        "slot41": struct.unpack_from("<H", mm, rec + 0x41)[0],
                        "b0_byte": mm[rec + 0xb0],
                        "b1_dword": self._hx(u(0xb1)),
                        "b7_mode": mm[rec + 0xb7],
                        "b9": mm[rec + 0xb9],
                        "bb": self._hx(u(0xbb)),
                        "table_a7": self._hx(u(0xa7))})
                row[want] = hits
            self.batrec.append(row)
            with open(op.join(s.out, "batrec.json"), "w") as fh:
                json.dump(self.batrec, fh, indent=1)
            s.log(f"BATREC {tag} " + " ".join(
                f"{k}={[ (h['rec_runtime'], h['b7_mode'], h['b9']) for h in v ]}"
                for k, v in row.items() if isinstance(v, list)))
            return row
        except Exception as e:
            s.log(f"BATREC {tag} error {e!r}")
            return None

    # ---------- phases ----------
    def set_legs(self, legs):
        """Swap the SUB-BATTERY armed for the next census_click. Only the Sess
        attribute is touched: DbgSession.whole_log_census counts over
        self.legs (ALL_LEGS), which must stay intact for the whole run."""
        self.s.legs = list(legs)

    def click_phase(self, xy, tag, seconds):
        self.batrec_oracle(f"{tag}_before")
        recs = self.s.census_click(xy[0], xy[1], tag, seconds)
        self.batrec_oracle(f"{tag}_after")
        return recs

    def run_phases(self):
        s = self.s
        res = {}
        map_im = s.grab("map0")
        # ---- sub-battery A: downstream legs ----
        self.set_legs(LEGS_A)
        res["A_baseline"] = s.census_click(None, None, "A_baseline", 15)
        res["A_myitems_map"] = self.click_phase(MY_ITEMS, "A_myitems_map", self.window)
        res["A_otheritems_map"] = self.click_phase(OTHER_ITEMS, "A_otheritems_map", self.window)
        # leg-free transit into the orbital/battle view (t253 rowjump)
        im = s.enter_system_via_fleet(map_im)
        res["A_rowjump"] = im is not None
        if im is not None:
            res["A_myitems_sys"] = self.click_phase(MY_ITEMS, "A_myitems_sys", self.window)
            res["A_batlist_sys"] = self.click_phase(BATLIST_MID, "A_batlist_sys", self.window)
            res["A_literal"] = self.click_phase(LITERAL, "A_literal", self.window)
            if not s.escape_to_map(map_im):
                s.log("T332: escape_to_map failed after A — stopping battery")
                return res
        # ---- sub-battery B: entry leg alone (dedicated windows, t330 law) ----
        self.set_legs(LEGS_B)
        res["B_baseline"] = s.census_click(None, None, "B_baseline", 15)
        res["B_myitems_map"] = self.click_phase(MY_ITEMS, "B_myitems_map", self.window)
        res["B_otheritems_map"] = self.click_phase(OTHER_ITEMS, "B_otheritems_map", self.window)
        im2 = s.enter_system_via_fleet(map_im)
        res["B_rowjump"] = im2 is not None
        if im2 is not None:
            res["B_myitems_sys"] = self.click_phase(MY_ITEMS, "B_myitems_sys", self.window)
            res["B_hold_sys"] = s.census_click(None, None, "B_hold_sys", self.window)
            s.escape_to_map(map_im)
        res["B_hold_map"] = s.census_click(None, None, "B_hold_map", self.window)
        return res


def analyze(run):
    """Offline verdict over banked artifacts: classify the outcome A/B/C."""
    cpath = op.join(run, "census.json")
    if not op.exists(cpath):
        print("ANALYZE: no census.json")
        return 2
    census = json.load(open(cpath))["pty_census"]
    hits = json.load(open(op.join(run, "hits.json"))) if op.exists(op.join(run, "hits.json")) else []
    batrec = json.load(open(op.join(run, "batrec.json"))) if op.exists(op.join(run, "batrec.json")) else []
    control = census.get(CTRL, 0)
    entry = census.get("fn156d4_entry", 0)
    downstream = {k: census.get(k, 0) for k in LEGS_A if k != CTRL}
    mode1 = census.get("mode1_1b7dd", 0)
    # save-axis: any BatModeWnd record observed with b7_mode == 1 ?
    mode1_sav = sorted({(r["tag"], h["rec_runtime"]) for r in batrec
                        for h in r.get("BatModeWnd", []) if h.get("b7_mode") == 1})
    if mode1 or mode1_sav:
        v = ("OUTCOME A: mode-1 arming WITNESSED"
             + (f" (leg mode1_1b7dd x{mode1})" if mode1 else "")
             + (f" save-axis b7==1 at {mode1_sav[:3]}" if mode1_sav else "")
             + " — residue-1 CLOSED-CLASS candidate; a nuke-effect witness is "
               "still required before any closure claim (strict-close).")
    elif entry:
        eaten = [k for k, n in downstream.items() if n]
        v = ("OUTCOME B: fn 0x156d4 WAS messaged (entry x%d) but the mode-1 "
             "store never fired. Legs that DID fire: %s. CAVEAT (t330 heavy-check "
             "law): sub-battery A arms the downstream legs WITHOUT the entry and B "
             "arms the entry alone, so a leg that fired only in the same invocation "
             "as the entry stop can be under-counted; the reject legs 0x1589b "
             "(BatModeWnd[+0xb7]==4) and 0x15b39 (b9-1>3) are the named suspects."
             % (entry, eaten or "NONE"))
    elif control:
        v = ("OUTCOME C: instrument alive (btn_hdlr x%d) and the ENTIRE chain is "
             "ZERO whole-log — fn 0x156d4 received no msg at all in a battery that "
             "clicked My^Items/Other^Items item rects (513,118)/(591,118) on the map "
             "and in the rowjump view. This is the FIRST instrumented measurement of "
             "the fifth leg (t331 correction C4: earlier armed-zeros never armed the "
             "entry and never clicked these rects). Row stays OPEN strict-close; "
             "D2-c disposition strengthens." % control)
    else:
        v = ("VOID: control leg btn_hdlr silent too — the battery did not exercise "
             "the UI (or arming failed). NOT evidence about the chain.")
    out = {"census": census, "control": control, "entry": entry,
           "downstream": downstream, "mode1_sav": mode1_sav,
           "banked_stops": len(hits), "verdict": v}
    with open(op.join(run, "t332_verdict.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("CENSUS", json.dumps(census))
    print("BANKED STOPS", len(hits))
    print("VERDICT:", v)
    return 0 if control else 1


def live_attempt(tag, window, disp, port, tl, settle):
    ds = BatSess(tag, ALL_LEGS, [], window, disp, port, tl, settle, 0)
    s = ds.s
    try:
        s.log(f"t332 start out={s.out} legsA={LEGS_A} legsB={LEGS_B} "
              f"window={window}")
        s.launch()
        conn = s.connect()
        if conn is None:
            s.log("NEGATIVE: no MCP connection")
            return 1
        lines, ok, hdr = s.req("PING", 10.0)
        if "PONG" not in " ".join(lines):
            s.log("NEGATIVE: no PONG")
            return 1
        s.log(f"settling {settle}s before BREAK")
        time.sleep(settle)
        if not s.do_break():
            s.log("NEGATIVE: BREAK lottery lost — relaunch")
            return 1
        lines, ok, hdr = s.req("EXEC RUN", 20.0)
        s.log(f"post-lottery RUN hdr={hdr}")
        s.pty_new()
        if not s.wait_title():
            s.log("NEGATIVE: title never appeared")
            return 1
        if not s.enter_campaign():
            s.log("NEGATIVE: campaign entry failed")
            return 1
        time.sleep(settle)
        closed = s.drain_popups()
        s.log(f"post-load drain closed {closed}")
        rows = s.ring_mem_rows()
        mem = s.read_mem(rows[-1]["path"]) if rows else None
        B = L.SL.base_of(mem, s.anch) if mem else None
        s.log(f"ring base B={hex(B) if B else None} (expect {hex(L.EXPECT_BASE)})")
        if B != L.EXPECT_BASE:
            s.log("NEGATIVE: base mismatch — armed addresses invalid")
            return 1
        ds.batrec_oracle("pre_battery")
        s.census = True
        s.pay = open(L.R293.PAYLOAD, "rb").read()
        ph_res = ds.run_phases()
        if ph_res is None:
            return 2
        ds.whole_log_census()
        ds.bank_on_exit()          # t330 ORDERING LAW: bank before analyze
        with open(op.join(s.out, "phases.json"), "w") as fh:
            json.dump({k: (v if isinstance(v, (dict, int, float, bool))
                           else (0 if v is None else len(v)))
                       for k, v in ph_res.items()}, fh, indent=1)
        return 0
    finally:
        ds.teardown()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="t332")
    ap.add_argument("--window", type=int, default=25)
    ap.add_argument("--disp", default="97")
    ap.add_argument("--port", type=int, default=55999)
    ap.add_argument("--tl", type=int, default=7200)
    ap.add_argument("--settle", type=int, default=45)
    ap.add_argument("--attempts", type=int, default=2)
    ap.add_argument("--offline", default=None, metavar="RUN_DIR")
    args = ap.parse_args()

    if args.offline:
        run = op.abspath(args.offline)
        rc = D.offline_run(run, [], ALL_LEGS)
        return analyze(run) or (0 if rc == 0 else 1)

    rc = D.preflight(ALL_LEGS)
    if rc:
        return rc
    if not D.port_free(args.port):
        print(f"HARNESS ERROR: MCP port {args.port} busy")
        return 2
    last = 1
    for i in range(1, args.attempts + 1):
        print(f"=== ATTEMPT {i} {time.strftime('%H:%M:%S')} ===", flush=True)
        rc = live_attempt(args.tag, args.window, args.disp, args.port,
                          args.tl, args.settle)
        cands = sorted((d for d in os.listdir(op.join(ROOT, "work/r1"))
                        if d.startswith(f"dbg-{args.tag}-")), reverse=True)
        run = op.join(ROOT, "work/r1", cands[0]) if cands else None
        print(f"attempt {i} rc={rc} run={run}", flush=True)
        if rc == 2:
            print("ATTEMPT harness error — NOT retrying")
            return 2
        if rc == 0 and run:
            ar = analyze(run)
            print(f"analyze rc={ar}")
            return 0 if ar == 0 else 1
        last = 1
    return last


if __name__ == "__main__":
    sys.exit(main())
