#!/usr/bin/env python3
"""v2 MS midiMap: 6 Button controllers CC12-17 ch5 -> DCA1-6 mute, slot
"momentary" (CC 127 -> action true, CC 0 -> action false; no click pairing),
invertOutput (127 = mute = mix.on false), outputMode 0 = send feedback CC on
every value change (127 muted / 0 unmuted) -> deck key state.
EDIT ONLY WHILE MS IS CLOSED (it autosaves the in-memory map on exit, and
only reads the file at console connect).
Usage: write_midimap_v2.py [slot] [invert0|1]   (defaults: momentary 1)
"""
import json, sys

F = "/home/rr/.config/MixingStation/wing/settings-default/midiMap.json"
slot = sys.argv[1] if len(sys.argv) > 1 else "momentary"
invert = bool(int(sys.argv[2])) if len(sys.argv) > 2 else True

CCS  = [12, 13, 14, 15, 16, 17]
DCAS = [76, 77, 78, 79, 80, 81]   # ch index = DCA1..6 master strip

m = json.load(open(F))
dev = m["devices"]
if isinstance(dev, list):
    dev = dev[0]

def controller(i, cc, ch_idx):
    return {
        "type": 2, "eventType": 2, "channel": 4, "paramA": cc,
        "outputMode": 0, "outputValue": 127,
        "name": f"DCA {i+1} Mute",
        "uuid": f"00000000-0000-4000-8000-0000000000{i+1:02d}",
        "actionSlots": {
            "key": slot,
            "actions": {"actions": [{
                "key": "consoleParam",
                "path": f"ch.{ch_idx}.mix.on",
                "boolMode": 0,
                "invertOutput": invert,
                "enable": True, "col": -1, "lo": None,
                "uuid": f"00000000-0000-4000-8000-0000000000a{i+1}",
            }]},
        },
    }

dev["cm"]["controllers"] = [controller(i, CCS[i], DCAS[i]) for i in range(6)]
m["devices"] = dev
json.dump(m, open(F, "w"), indent=2)
print(f"wrote {F}: 6 controllers, slot={slot} invert={invert} outputMode=0")
