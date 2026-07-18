# midi-bridge — connect this plugin to rawmidi-only apps (both directions)

Some applications on Linux (notably Java/`javax.sound.midi` apps such as
Mixing Station) can only see ALSA **rawmidi** devices, while this plugin's
virtual "Streamdeck MIDI" port exists only in the ALSA **sequencer** layer.
This bridge closes the gap with the `snd-virmidi` kernel loopback and keeps
the connections alive across restarts of OpenDeck, the plugin, or the app.

It wires **both directions**:

- deck → app: plugin output (`RtMidi client`) → virmidi seq port
- app → deck: virmidi seq port → plugin input (`RtMidi Input Client`), so the
  app's MIDI feedback (e.g. Mixing Station's *output mode* state messages)
  reaches the plugin, which updates toggle-button states on the deck
  (`HandleMidiInput`).

## Install

```bash
# load snd-virmidi at boot, one device with a stable card index
echo snd-virmidi | sudo tee /etc/modules-load.d/virmidi.conf
echo 'options snd-virmidi index=2 midi_devs=1' | sudo tee /etc/modprobe.d/virmidi.conf
sudo modprobe snd-virmidi index=2 midi_devs=1

sudo cp midi-bridge-connect.sh /usr/local/bin/
sudo chmod 755 /usr/local/bin/midi-bridge-connect.sh
sudo cp midi-bridge.service /etc/systemd/system/
sudo systemctl enable --now midi-bridge.service
```

The receiving app then opens the rawmidi device `VirMIDI [hw:2,0,0]` for
input *and* output. Java apps cache the MIDI device list at startup — start
them after virmidi is loaded.

## Notes

- Connections are made by client *name* and re-fired on every ALSA
  `System:announce` event, so dynamic client numbers never matter.
- RtMidi creates two clients named "RtMidi Input Client" (one has no ports);
  the script resolves numeric ids to dodge that.
- See `docs/OPENDECK.md` for the full picture, including a worked
  bidirectional Mixing Station setup.
