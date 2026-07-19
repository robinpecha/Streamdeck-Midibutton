# Runbook: adding Stream Deck controllers for Mixing Station / Behringer WING

Audience: AI agents (and humans) working on THIS machine. This documents the
complete, verified pipeline and the exact steps to add more controllers.
Generic plugin/OpenDeck reference: `~/src/Streamdeck-Midibutton/docs/OPENDECK.md`
(fork `robinpecha/Streamdeck-Midibutton`, branch `v2-bidirectional`).

## Architecture (all verified working 2026-07)

```
Stream Deck XL
  └─ OpenDeck (runs as rr)  ~/.config/opendeck/profiles/sd-A00NA53831YSOD/Default.json
      └─ midibutton plugin  (ALSA seq client "RtMidi client"/"RtMidi Input Client")
          │  ▲
          ▼  │            midi-bridge.service (auto-wires BOTH directions by name)
        snd-virmidi card 2  (seq 'Virtual Raw MIDI 2-0' ⇄ rawmidi VirMIDI [hw:2,0,0])
          │  ▲
          ▼  │
  Mixing Station desktop (runs as rr, Java → sees only rawmidi)
      midiMap: CC ⇄ console parameter (+ feedback CC on every value change)
          └─ Behringer WING (network, autoconnect on; REST API on :8080 while connected)
```

- Deck→mixer: key press → CC on the virmidi port → MS maps it to a console
  parameter (`consoleParam` action).
- Mixer→deck: any parameter change (deck, tablet, console surface) → MS sends
  a feedback CC (`outputMode 0`) → plugin `HandleMidiInput` → key state/colour.

## Current allocation

| deck key | CC (ch 5, statusByte 180) | target | display |
|---|---|---|---|
| 0–5 | CC 12–17 | DCA 1–6 mute (`ch.76`–`ch.81.mix.on`) | red = muted, white = unmuted |
| 24,26,28,30,31 | — | user's app launchers (oadesktopentry) — do not touch | |

Free CC space on ch 5 (WING DCA/MG native convention): CC 18–27 (DCA 7–16),
CC 28–31 (Mute Group 1–4), CC 44–47 (MG 5–8). Other channels are entirely
free for MS-mapped controls (MS doesn't care which channel/CC you pick — the
WING-native map only matters if the deck ever talks to a WING directly).

## Recipe: add a new button end-to-end

Adapt the two generators in `/apps/sys/opendock/tools/` (they are the
DCA-mute versions that built the working setup):

1. **Pick** CC number + channel, console parameter path, and semantics
   (toggle-with-status vs momentary vs scene recall...).
2. **Deck side** — edit `tools/v2_dca_keys.py` (or write a sibling):
   - stop OpenDeck first: `pkill -x opendeck` (it saves profile from memory
     on exit — never edit the profile while it runs); **back up the profile**;
   - key JSON rules: context = `Keypad.<key position 0-31>.0` (wrong order
     half-works and breaks feedback — see gotchas), top-level `states` field
     is REQUIRED (parse failure ⇒ OpenDeck saves back an EMPTY profile);
   - for a status button: `cctoggle` + settings `statusDisplay: true` +
     action `disable_automatic_states: true`; `dataByte2` = state-0 value,
     `dataByte2Alt` = state-1 value (same bytes drive send AND feedback);
   - for fire-and-forget (scene recall etc.): plain `cc` with `ccMode: 1`
     (127 on press, 0 on release — what MS's `click`/`momentary` slots want);
   - seed `current_state` from live REST so colours start truthful;
   - restart as rr (see Environment).
3. **MS side** — edit `tools/write_midimap_v2.py`:
   - MS must be CLOSED (or at least disconnected) — it reads midiMap.json
     ONLY at console connect and rewrites it from memory on disconnect/exit;
   - controller: `type` 2 Button / 0 Fader / 1 Rotary; `eventType` 2 = CC;
     `channel` 0-based (deck statusByte 180 = 0xB4 ⇒ channel **4**);
     `paramA` = CC#; actionSlots key: `momentary` (follow 127/0 — use for
     status buttons), `touch` (rising edge, toggles), `click` (needs 127→0
     pair within **660 ms**), `longClick`;
   - action: `consoleParam` + `path`; `boolMode` 0=Any 1=only-on 2=only-off
     3=never 4=always-off; `invertOutput: true` for mute paths (`mix.on`
     true = UNmuted); `outputMode: 0` + `outputValue: 127` = feedback;
   - other action keys that exist (from the 3.1.1 jar): `mutegroup`,
     `msScene`, `setValue`, `toggleValue`, `sendsOnFader`, `selectCh`,
     `clrSolo`, `usbply`, `sigGen`, `macros`, `fx`, `softKeys`, `spill`,
     `flash`, `chMeters`, ...
   - relaunch MS as rr; it autoconnects to the WING in ~3 s.
4. **Bridge**: nothing to do — `midi-bridge.service` wires new clients by
   name automatically in both directions.

## Console parameter paths (WING via MS, consoleId 6)

92 strips: `ch.0-39` inputs, `ch.40-47` aux, `ch.48-63` bus, `ch.64-71`
matrix, `ch.72-75` main, **`ch.76-91` = DCA 1–16**. Useful leaves:
`ch.<i>.mix.on` (mute, inverted), `ch.<i>.mix.fader` (level),
`ch.<i>.cfg.name` / `ch.<i>.cfg.color` (REST only — not reachable via MIDI).
Discover live: `GET http://127.0.0.1:8080/console/data/get/<path>/val`
(full tree dump exists at the fork/scratchpad `ms_paths.json`).

## Verification loop (no hands needed)

```bash
# read a param (REST is up only while MS is connected to the console)
curl -s http://127.0.0.1:8080/console/data/get/ch.81.mix.on/val
# write a param (GET set-paths do NOT work — POST only)
curl -X POST -H 'Content-Type: application/json' -d '{"value":false}' \
  http://127.0.0.1:8080/console/data/set/ch.81.mix.on/val
# inject MIDI as if the deck sent it (tools/*.mid are single-CC files)
aplaymidi -d 1 -p 24:0 tools/cc17_127.mid
# simulate a REAL key press (full key_down/up pipeline): double-click the key
# in the OpenDeck window
xdotool getwindowgeometry $(wmctrl -l | grep -i opendeck | awk '{print $1}')
xdotool mousemove <abs_x> <abs_y> click --repeat 2 --delay 80 1
# watch plugin activity
grep -E 'HandleMidiInput|ChangeButtonState|SendMidiMessage' \
  ~/.local/share/opendeck/logs/opendeck.log | tail
# check the seq wiring (expect RtMidi client -> 24:0 -> RtMidi Input Client)
aconnect -l | grep -A3 'Virtual Raw'
# screenshot the OpenDeck window to SEE key states
import -window <wid> /tmp/od.png   # (DISPLAY=:1 XAUTHORITY=/run/user/1000/gdm/Xauthority)
```

MIDI test-file hex (single CC, value V at CC N on 0xB4):
`4d546864000000060000000100604d54726b0000000800 b4 NN VV 00ff2f00` → `xxd -r -p`.

## Gotchas (each one cost real debugging time)

1. **Claude sessions run as ROOT with HOME=/home/rr.** Launch every GUI app
   as rr or it uses root's empty configs (MS: no licence, no autoconnect) and
   litters root-owned files that later segfault rr's apps:
   `sudo -u rr env DISPLAY=:1 XAUTHORITY=/run/user/1000/gdm/Xauthority XDG_RUNTIME_DIR=/run/user/1000 HOME=/home/rr DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus setsid nohup <app> &`
2. Deck profile: edit only while OpenDeck is stopped; keep a backup; every
   key needs the top-level `states`; context is `Keypad.<position>.<index>`
   — position = slot in the keys array, index = 0 (unless multi-action child).
3. MS midiMap: edit only while MS is closed/disconnected; if a
   `settings-reconnect` bundle dir exists under `~/.config/MixingStation/wing/`,
   it loads INSTEAD of settings-default once, then is deleted.
4. Use `pkill -x` / `pgrep -x` (exact names: `opendeck`, `mixing-station`).
5. Never install/copy into `~/.config/opendeck/plugins/` with sudo.
6. Plugin binary lives at
   `~/.config/opendeck/plugins/co.uk.clarionmusic.midibutton.sdPlugin/midibutton-linux`;
   rebuild: `cd ~/src/Streamdeck-Midibutton && cmake --build build -j`, copy,
   chown rr, restart OpenDeck.
7. Feedback only exists while MS is running AND connected; REST likewise.

## Idea backlog (agreed direction: finish universal MIDI work first)

- More status buttons (pure config): DCA 7–16, Mute Groups 1–8 (`mutegroup`
  action), input/bus/main mutes, sends-on-fader, solo clear.
- Fire buttons (pure config): scene/snippet recall (`msScene`), USB
  player transport (`usbply`), signal generator, MS macros.
- Fader nudges: MS Rotary controller (`type` 1, `incrementValue`) — a pair of
  deck keys as −/+ dB for any fader.
- WING-native MIDI profile for the plugin (TBD, for people without MS).
- Post-v2 pivot (TBD): dedicated "mixingstation" OpenDeck plugin using the
  REST/WebSocket API — channel NAMES + COLOURS + meters on keys, no MIDI
  limits (names/colours are provably not transportable over plain CC).
