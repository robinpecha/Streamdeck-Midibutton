#!/usr/bin/env bash
# Auto-connect the OpenDeck MIDI plugin's output to the snd-virmidi loopback,
# so Mixing Station (a Java/javax.sound.midi app that only sees ALSA *rawmidi*)
# can receive MIDI from the Stream Deck (whose plugin only exposes an ALSA *seq*
# virtual port).
#
# Matches ports by NAME, so the dynamic ALSA client IDs (which change every time
# OpenDeck or the plugin restarts) never matter. Re-fires on every sequencer
# client/port change via System:announce, so it survives OpenDeck restarts and
# deck re-plugs.
set -uo pipefail

SRC='RtMidi client'        # the plugin's MIDI-OUT client (its port is "Streamdeck MIDI")
DST='Virtual Raw MIDI'     # the snd-virmidi loopback seq client ("Virtual Raw MIDI 2-0")
FB='RtMidi Input Client'   # the plugin's MIDI-IN client (v2: mixer state feedback)

wire() {
    aconnect "$SRC" "$DST" 2>/dev/null || true  # deck -> mixer (idempotent; "already subscribed" is harmless)
    # mixer -> deck (v2 feedback): Mixing Station's rawmidi writes reappear on
    # the seq side of the virmidi port. RtMidi creates TWO clients named
    # "RtMidi Input Client" (one portless), so name-based aconnect fails with
    # "Invalid argument" — resolve the numeric ids and try each.
    for c in $(aconnect -l | sed -n "s/^client \([0-9]\+\): '$FB'.*/\1/p"); do
        aconnect "$DST" "$c:0" 2>/dev/null || true
    done
}

wire  # connect immediately in case both ports already exist

# Prefer event-driven: System:announce emits on every client/port create/destroy
# (OpenDeck restart, deck re-plug). Fall back to polling if aseqdump is absent.
if command -v aseqdump >/dev/null 2>&1; then
    stdbuf -oL aseqdump -p 'System:announce' 2>/dev/null | while read -r _event; do
        wire
    done
else
    while true; do wire; sleep 3; done
fi
