# AI continuation point — read this first

You are an AI agent continuing an ongoing project. This folder is the
complete project brain: state, machine runbook, roadmap, tools, and config
snapshots. The human will typically say *"read /ai and continue"*.

## The project in one paragraph

Control a Behringer WING digital mixer (via the Mixing Station desktop app)
from a Stream Deck XL running OpenDeck on Ubuntu. This repo is the user's
fork of the abandoned Streamdeck-Midibutton plugin, ported to Linux
(`linux-support` branch, upstream PR tsbkelly#19) and extended on
`v2-bidirectional` with true two-way state sync: deck keys send MIDI CC to
toggle DCA mutes, and the mixer's real state comes back as MIDI feedback that
colours the keys (red = muted, white = unmuted) no matter where the change
originated (deck, tablet, console surface).

## Status: v1 + v2 DONE and live-verified (2026-07-18)

- 6 deck keys = DCA 1–6 mutes with truthful colours; first press effective;
  survives reboots (systemd bridge + kernel module configs persisted).
- Everything was verified end-to-end on the real WING, including simulated
  full key presses (see RUNBOOK verification loop).

## Files here

| file | what |
|---|---|
| `RUNBOOK-THIS-PC.md` | machine-specific runbook: architecture, add-a-controller recipes, verification loop, gotchas. THE key document when working on the user's PC. |
| `ROADMAP.md` | all agreed TBDs and longer-term visions, prioritised |
| `tools/` | the actual generator scripts + test MIDI files that built the working setup |
| `config-snapshots/` | known-good deck profile + Mixing Station midiMap as deployed |
| `../docs/OPENDECK.md` | generic reference: OpenDeck profile format, plugin action MIDI semantics, seq/rawmidi bridge |
| `../contrib/midi-bridge/` | the bridge script + systemd unit (installable anywhere) |

## Where you might be running

- **On the user's PC** (`/apps/sys/opendock` working dir, user `rr`,
  hostname with the deck + WING): full live pipeline available. Read
  `RUNBOOK-THIS-PC.md` before touching anything — especially the root-vs-rr
  launching gotcha and the edit-timing rules. There is also a Claude-specific
  memory file at `~/.claude/projects/-apps-sys-opendock/memory/` with history.
- **Anywhere else** (cloud, another machine): you can do code, docs, plugin
  features, and planning. You canNOT live-test: the Stream Deck, snd-virmidi,
  Mixing Station licence, and the WING are on the user's PC. Prepare changes
  + exact verification commands; run them next time the PC session exists.

## Conventions

- Keep responses to this user SHORT (explicitly requested).
- Never commit/push without being asked, EXCEPT the user has a standing
  pattern of asking for pushes to their own fork branches.
- Branches: `linux-support` = Linux port (basis of upstream PR #19);
  `v2-bidirectional` = feedback work (current). New features → new branches.
- Test mutes only on channels the user allows (during live shows they will
  designate a safe DCA, historically DCA 6).
