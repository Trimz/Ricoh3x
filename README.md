# Ricoh GR IIIx firmware knowledge base (fw 1.60)

What is known about the Ricoh GR IIIx firmware from static reverse engineering
of v1.60 and controlled tests on one camera, with the goal of **reading,
changing and customising camera settings from the SD card**.

**Main result:** with a one-time unlock, a script on the SD card can change
**any of 1,036 camera settings** (shooting, Image Control, white balance, focus,
drive, noise reduction, playback, setup, button customisation, user modes)
through the camera's own settings code. Changes show in the menus and survive
reboots. No firmware modification is involved.

> ⚠️ This is undocumented developer functionality on real hardware. Read
> [docs/SAFETY.md](docs/SAFETY.md) first. Never flash modified firmware.
> Everything is specific to **firmware 1.60**. AI agents: read [AGENTS.md](AGENTS.md).

## Capability map

| Capability | Status | Doc |
|---|---|---|
| Unencrypted firmware, decompressor, RTOS image analysis | done | [firmware.md](docs/firmware.md) |
| Developer "ModeSet" commands from the card (MENU + power) | 3 of 58 commands tested | [modeset.md](docs/modeset.md) |
| Startup/shutdown scripts from the card (Tera Term macro dialect) | working | [scripting.md](docs/scripting.md) |
| Run internal shell commands from a script (584 commands) | working; some crash | [scripting.md](docs/scripting.md) |
| **Write any UserData setting by name** (1,036 items, value tables) | working; 10 items covering every value kind verified on camera | [settings.md](docs/settings.md) |
| Image Control Custom 1/2 (all parameters per base effect) | working | [image-control.md](docs/image-control.md) |
| **Read all settings**: export (`dd_out` → `KB609.DOM`) + decoder `tools/dom_parse.py` | working, verified against the menus | [settings.md](docs/settings.md#exporting-all-settings-read-back) |
| camctl remote-control commands (93) | documented, untested | [interfaces.md](docs/interfaces.md) |
| Crash / debug logs to the card | working | [scripting.md](docs/scripting.md#logs) |
| Wi-Fi HTTP API, Linux side, USB/MTP | endpoints listed; effect selection only / MTP setters dead | [interfaces.md](docs/interfaces.md) |

## 30-second version

1. One time, unlock scripts: copy `sdcard/step1_enable_scripts/*` to the card root,
   **hold MENU and power on**. The camera says "script enable complete".
2. Put a `script/startup.ttl` on the card (CRLF line endings):
   ```
   sendln 'UserData Set StillSnapDistanceCm 250'
   sendln 'UserData Set StillImageControlNo2 Standard'
   sendln 'UserData Set StillImageControlNo2ParamStandardSaturation P2'
   ```
3. Power on normally. Then **delete the script** from the card.
4. To read everything back: put `sendln 'dd_out'` in `script/shutdown.ttl` (exports show the
   last saved settings), then
   `python3 -I tools/dom_parse.py KB609.DOM data/userdata_set_values.tsv`.

Valid item names and values: [data/userdata_set_values.tsv](data/userdata_set_values.tsv).

## Repository layout

```
AGENTS.md    rules for AI agents working with the camera
docs/        knowledge base (start with SAFETY.md)
data/        machine-readable tables extracted from the firmware
  userdata_set_values.tsv   every settable item, value kind, accepted tokens, setter address
  shell_commands.tsv        584 internal shell commands (name, handler)
  shell_usage.tsv           their help text and argument placeholders
  symbols.tsv               named firmware addresses
  modeset_commands.tsv      58 ModeSet commands (dev item, tested?)
sdcard/      ready-to-copy card layouts used in the tests
tools/       decompressor, value-table extractor, ARM xref helpers, Ghidra scripts
camlogs/     exception logs pulled from the camera during testing
```

Ricoh's firmware and anything extracted or decompiled from it are not in this
repo (copyright, size). [firmware.md](docs/firmware.md) explains how to rebuild them.

## Docs index

- [SAFETY.md](docs/SAFETY.md): rules, dangerous commands and settings, recovery
- [firmware.md](docs/firmware.md): format, tooling, key addresses, other interfaces
- [modeset.md](docs/modeset.md): unlock files, full ModeSet command table
- [scripting.md](docs/scripting.md): script engine, shell, logs
- [interfaces.md](docs/interfaces.md): camctl, Wi-Fi HTTP API, Linux side, USB/MTP
- [settings.md](docs/settings.md): the `UserData` interface and the settings catalogue
- [image-control.md](docs/image-control.md): Custom 1/2 Image Control in detail
- [test-log.md](docs/test-log.md): every on-camera experiment and its outcome
- [open-questions.md](docs/open-questions.md): what is unknown and next leads
- [applications.md](docs/applications.md): things to build on top (presets, shooting profiles)
