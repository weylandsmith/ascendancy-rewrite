# t260 — GUI-loadstate restore experiment (WIP, 2026-11-01 ~19:30)

Goal: determine whether a banked dosbox-x savestate ZIP (t1255, clean copy
work/r1/bank-t251-live1255/60.sav md5 0024340df46c0375ce6472e085345e71 —
VERIFIED this session) can be RESTORED into a running Ascendancy process on
this build (dosbox-x 2025.02.01 commit 32b2c24). Prior pairing-session
negatives [from STATE.md]: no CLI flag, no autoexec command, saveslot+
forceloadstate only set the ACTIVE SLOT, F12 via XSendEvent produced no load.

## MEASURED this session (before the experiment)
1. Live production session IS up and healthy: dosbox-x PID 524517
   (`-conf work/r1/vnc/session.conf -nogui -time-limit 28800`, under
   `timeout -s KILL 28830`), autosave ring 41-60 writing every 10 s
   (log: "Saving state to slot: 55 ... Saved. (Slot 55)"), timeline rows at
   turn 1086 wall 19:14:49. X window `0xc00009 "DOSBox-X 2025.02.01: ASCEND -
   100%" 640x480+80+100` on :9.
2. Savestate ZIP structure (python zipfile, both bank and ring copies):
   26 members incl. CMOS/CPU/DMA/Dos/EMS/... (full guest RAM per
   r1_playcap_watch.py, BLOCKED t259 note (4)). `dosboxversion` member = 2
   bytes; version string member "DOSBox-X_Version" 82 bytes.
3. Binary symbol/action names (strings on /usr/bin/dosbox-x): `mapper_loadstate`,
   `mapper_savestate`, `force_loadstate`, `forceloadstate`, and human-readable
   menu/mapper labels "Save state" / "Load state" present VERBATIM. No CLI
   loadstate option string found.
4. Reference conf (/usr/share/dosbox-x/dosbox-x.reference.conf L180-241):
   savefile / saveremark / forceloadstate documented; `forceloadstate` =
   "load a saved state even if it finds there is a mismatch in the DOSBox-X
   version, machine type, program name and/or the memory size". No
   load-on-boot key other than forceloadstate.
5. xdotool NOT installed (XT=1). tools/xsend (XSendEvent+XWarpPointer) IS the
   loop's input injector; usage `xsend title (key|keyup KEYSYM [ch] |
   click|click3 x y | x y)`; window matched by TITLE SUBSTRING — two live
   DOSBox-X windows on one display are therefore ambiguous, hence the
   experiment runs on its OWN display.
6. Watcher "Extracting: Time_Stamp/Save_Remark/Program_Name" log lines are the
   watcher's metadata reads of ring ZIPs, NOT a load in progress (verified
   against the autosave cadence + no "Loading state" line).

## EXPERIMENT DESIGN (isolated, zero blast radius on the live session)
- New display :8 (own Xvfb 800x600), new scratch dir work/r1/t260-loadstate/
  with save/ holding ONLY the clean t1255 copy as 60.sav; conf autosave=0 so
  nothing churns; forceloadstate=true, saveslot=60; launched WITHOUT -nogui.
- Verification is structural, not vibes: after a successful load, save to a
  scratch slot from the loaded process and read turn/V out of the ZIP's Memory
  member with the pointer law (scripts/r1_slot.py path), expecting turn 1255
  (V=14 per the frozen timeline row). A vision read of the screen is a
  secondary witness (title menu vs campaign map is unambiguous).
- BLAST RADIUS: none to the production session (separate display, separate
  save dir, no in-game Save, no shared writes). The game dir work/r1/game is
  mounted by both instances read-mostly; RESUME.GAM is written only by
  in-game Save (t259 measured the game never rewrote it across hundreds of
  turns), and the experiment never issues one.

## GUI MENU CENSUS (measured on the :8 experiment instance, PID 526862)
Menu bar IS present without -nogui (Main CPU Video Sound DOS Drive Capture Help,
window 640x497 — the extra 17 px is the menu bar itself). Full dropdown census:
  Main   : Configuration tool F12+C | Mapper editor F12+M | Quick launch program
           F12+Q | Load language file | Load mapper file | Send special key > |
           Select host key > | Shared clipboard functions > | Capture mouse
           Ctrl+F10 | Autolock mouse | Mouse wheel movements | Always on top |
           Pause emulation F12+Pause | Pause with interrupts | Reset VM F12+R |
           Reboot guest F12+B | APM power button | Restart instance | Restart w/
           config | Quit Ctrl+F9           -> NO save/load-state items
  CPU    : Turbo | Normal F12+Left | Speed up F12+I | Slow down F12+O |
           Increment/Decrement cycles | Emulate CPU speed | Edit cycles |
           CPU core | CPU type            -> NO state items
  Video  : (aspect/fullscreen/scaler/shader list) -> NO state items
  Sound  : (volumes/mixer/SB/MIDI) -> NO state items
  DOS    : (DOS version | LFN | host apps | mouse emu | EMS | A20 | swap |
           rescan | print screen) -> NO state items
  Drive  : A..M mounts -> NO state items
  Capture: Take screenshot | Take raw screenshot | Capture format | Record video
           to AVI | Record audio WAV | multi-track AVI | FM (OPL) | MIDI |
           network traffic | **Save state** | **Load state** | Save/load options |
           Select save slot | Auto-save settings... | Browse save file... |
           Display state information
  => THE HYPOTHESIS IS CONFIRMED STRUCTURALLY: load-state IS GUI-menu-only, and
     it lives under **Capture** (NOT "DOS" as the STATE note guessed). No CLI
     flag, no autoexec command, no default hotkey (Main menu census shows F12
     combos are taken by CPU/Video/pause functions; strings on the binary hold
     mapper_loadstate/mapper_savestate as mapper ACTION names, bindable via the
     Mapper editor — but the editor refuses while a program runs: dialog
     "Another program is already running." observed verbatim at ~20:00).

## INPUT-PATH FIND (why the earlier F12 attempt went dark)
tools/xsend uses XSendEvent (send_event=True synthetic events). Menu-bar clicks
via xsend WORK (dropdowns opened and were screenshotted), so synthetic events DO
reach this SDL2 build's X path for pointer/button events. The earlier "F12 sent,
no load log" is consistent with there being NO loadstate binding on F12 at all
(Main/Capture menus show no such hotkey), not with an event-filter failure.

## SAVE-SLOT PATH MEASURED
Experiment conf set saveslot=60 -> log "Active save slot: 60" (vs production's
"Active save slot: 1 [Empty]" then the autosave cycle). dosbox-x resolves slot
files under <savedir>/NN.sav; savedir defaults to cwd-relative "save" (no
savedir key exists in the conf; production harness cds so it lands in
work/r1/playcap/save). The experiment therefore runs with an explicit
`-savedir work/r1/t260-loadstate/save` holding ONLY the clean t1255 copy —
zero chance of touching the production ring.

## ATTEMPT 1 (20:15) — LOAD ITSELF WORKED; PROCESS THEN EXITED
Sequence on :8 (window 0x600009, conf t260-experiment.conf, explicit
`-savedir work/r1/t260-loadstate/save` holding ONLY the clean t1255 60.sav):
menu-bar click via xsend at (315,8) opened Capture; dropdown located
PROGRAMMATICALLY (scripts/r1_t260_menulocate.py — neutral-dark panel census;
vision gave the item ORDER: Save state F12+S | Load state F12+L | Save/load
options > | Select save slot > | Auto-save settings | Browse save file |
Display state information). Click (350,197) = "Load state" ->
  LOG: Loading state from slot: 60
  LOG: [20:15:55]: Loaded. (Slot 60)
then the dosbox-x process EXITED within seconds (ps gone, window gone, no
error lines, no core dump logged). 60.sav md5 UNCHANGED (0024340d) — the
failure is not state corruption on disk.
Theory [inferred]: the saved process ran with -time-limit 28800 and the TL
deadline/kill is carried by the state itself (the state ZIP stores the timer
config; on load the kill fires against a deadline already long past).
NOTE the menu hotkeys are VISIBLE: Save state F12+S, Load state F12+L — the
earlier pairing-session F12-alone test could not have worked (bare F12 is the
HOSTKEY, and the action is F12+L; tools/xsend sends keys with state=0, no
modifier support, so chords need a code change or menu clicks).
## ATTEMPT 2 (pending): relaunch WITHOUT -time-limit, load again, watch exit.
