# Roadmap — TBDs and visions

Agreed priority (user, 2026-07-18): **finish the universal/global MIDI work
for all people first**, then machine-specific niceties, then the big pivot.

## 1. Finish the universal MIDI task ("for all people")

- [ ] **Property-inspector UI for `statusDisplay`** — the new CC-Toggle
      status mode currently has NO checkbox in the PI; it can only be set by
      editing profile JSON. Add it to the cctoggle PI (propertyinspector/)
      so non-technical users can enable it.
- [ ] Decide merge strategy: fold `v2-bidirectional` into `linux-support`
      (basis of upstream PR tsbkelly/Streamdeck-Midibutton#19) or keep the
      fork as the living home and document that. Upstream is abandoned since
      2020 — the fork is realistically the product.
- [ ] Release packaging: prebuilt `midibutton-linux` binary + install script
      (including `contrib/midi-bridge/`) so users don't need cmake.
- [ ] README refresh: point users to docs/OPENDECK.md + bridge; screenshots.
- [ ] Windows port (manifest already anticipates it) — far future, low value.

## 2. Behringer WING MIDI profile (TBD, user-requested)

A ready-made deck profile / documentation for people driving a WING
DIRECTLY over its USB/DIN MIDI remote protocol (no Mixing Station). The
official WING map (from Behringer docs, noted 2026-07): remote control on
USB MIDI "port 4"; CH1 = faders (CC12-31 → ch1-20, CC44-63 → ch21-40,
CC70-77 aux, CC78-93 bus, CC94/95/102/103 main, CC104-111 matrix);
CH2 = mutes (same CC layout); CH3 = pan; CH4 = DCA faders CC12-27;
CH5 = DCA mutes CC12-27 + Mute Groups CC28-31 (MG1-4) / CC44-47 (MG5-8);
CH6 = Custom Controls; CH9-16 = FX. Physical link question was parked.

## 3. More controllers on the current setup (pure config, use ai/tools/)

- [ ] Mute Groups 1–8 as status keys (MS `mutegroup` action / ch5 CC28-31+44-47)
- [ ] DCA 7–16 mutes if ever needed (CC18-27)
- [ ] Scene/snippet recall keys (MS `msScene` action) — "show mode" row
- [ ] USB player transport (`usbply`), signal generator (`sigGen`), macros
- [ ] Fader nudge pairs (MS Rotary controller type, incrementValue) — −/+ dB keys
- [ ] Talkback momentary key (momentary slot, hold-to-talk)
- [ ] Panic multi-action (mute all DCAs + safe scene)

## 4. The big vision: "mixingstation" OpenDeck plugin (post-v2 pivot)

A NEW OpenDeck plugin talking Mixing Station's REST/WebSocket API directly
(port 8080 while connected) instead of MIDI. Unlocks what MIDI provably
cannot carry: **channel NAMES and COLOURS rendered on keys**, level meters,
unlimited parameters, no CC bookkeeping. Facts already established:
- REST read: `GET /console/data/get/<path>/val`; write: `POST .../set/<path>/val`
  with `{"value":...}` body. Names/colours: `ch.<i>.cfg.name` / `ch.<i>.cfg.color`.
- REST only listens while MS is connected to a console.
- Full live data tree was dumped once (`ms_paths.json`, 764 KB — regenerate
  by walking the REST tree while connected).
- MS 3.1.1 jar internals are mapped (obfuscated `blob/*`; see the machine
  memory + docs/OPENDECK.md notes): midiMap schema, action registry, 660 ms
  click window, feedback outputModes — useful for parity decisions.
Decision pending: new plugin from scratch (Rust/C++/node) vs extending this
one. OpenDeck manifest rules are in docs/OPENDECK.md.

## 5. Housekeeping / known rough edges

- [ ] `write_midimap.py` v1 script is superseded by `tools/write_midimap_v2.py`.
- [ ] Deck profile keys 6–7 are empty (trimmed); decide DCA 7–8 or other use.
- [ ] MS REST `set` for `mix.on` was verified; some paths may need different
      value formats — probe before batch use.
- [ ] The user's PC accumulates root-owned files if agents launch GUI apps
      as root — see RUNBOOK gotcha #1; sweep with
      `find /home/rr/.cache /home/rr/.config /home/rr/.local/share ! -user rr`.
