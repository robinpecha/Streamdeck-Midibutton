#!/usr/bin/env python3
"""v2: deck keys 0-5 = CC Toggle DCA mutes with mixer-state feedback.
State 0 = RED "muted" (plugin sends/receives CC value 127 = dataByte2),
state 1 = WHITE "unmuted" (CC value 0 = dataByte2Alt) — matches
HandleMidiInput: value==dataByte2 -> state 0, value==dataByte2Alt -> state 1.
Usage: v2_dca_keys.py <s0> <s1> <s2> <s3> <s4> <s5>   (initial current_state
per key, from live mixer: mix.on true(unmuted) -> 1, false(muted) -> 0)
Run ONLY while OpenDeck is stopped."""
import json, sys

F = "/home/rr/.config/opendeck/profiles/sd-A00NA53831YSOD/Default.json"
PLUG = "co.uk.clarionmusic.midibutton.sdPlugin"
ICON = f"plugins/{PLUG}/midibuttoncc.png"
init = [int(a) for a in sys.argv[1:7]] or [1] * 6

def state(text, colour):
    return {
        "alignment": "middle", "background_colour": "#000000",
        "colour": colour, "family": "Liberation Sans", "image": ICON,
        "image_scale": 100, "name": "", "show": True, "size": 17,
        "stroke_colour": "#000000", "stroke_size": 3, "style": "Regular",
        "text": text, "underline": False,
    }

def key(idx):
    two = lambda t: [state(t, "#FF5050"), state(t, "#FFFFFF")]
    return {
        "action": {
            "controllers": ["Keypad"],
            # feedback (via plugin statusDisplay mode) is the only state driver
            "disable_automatic_states": True,
            "encoder": None,
            "icon": ICON,
            "name": "MIDI CC Toggle",
            "plugin": PLUG,
            "property_inspector": f"plugins/{PLUG}/propertyinspector/index.html",
            "states": two(""),
            "supported_in_multi_actions": True,
            "tooltip": "Toggle a MIDI CC message",
            "uuid": "uk.co.clarionmusic.midibutton.cctoggle",
            "visible_in_action_list": True,
        },
        "children": None,
        # context = Keypad.<key position 0-31>.<action index, 0 unless child>
        # (getting this wrong makes OpenDeck silently drop plugin SetState etc.)
        "context": f"Keypad.{idx}.0",
        "current_state": init[idx],
        "states": two(f"DCA {idx + 1}"),
        "settings": {
            "statusDisplay": True,   # press sends OPPOSITE of shown state; feedback sets state
            "ccMode": 0,
            "statusByte": 180,          # 0xB4 = CC ch5 (WING DCA-mute map)
            "dataByte1": 12 + idx,      # CC12..17 = DCA1..6
            "dataByte2": 127,           # sent when toggling INTO state 0 (mute)
            "dataByte2Alt": 0,          # sent when toggling INTO state 1 (unmute)
            "fadeCurve": 0, "fadeTime": 0, "toggleFade": False,
        },
    }

p = json.load(open(F))
for i in range(6):
    p["keys"][i] = key(i)
json.dump(p, open(F, "w"))
print(f"keys 0-5 -> cctoggle v2, initial states {init}")
