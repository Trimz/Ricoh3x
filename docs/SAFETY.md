# Safety and guardrails — read this before touching the camera

This project pokes at undocumented developer features of a real camera that
belongs to a real person. Everything here was found by reverse engineering
firmware v1.60 and has only been tested on one Ricoh GR IIIx. Nothing is
supported by Ricoh, and misuse can lose settings, void warranty, or in the worst
case brick the camera.

## Hard rules

1. **Never flash modified firmware.** Everything in this repo works without
   modifying the firmware image. Only ever install official Ricoh firmware
   (`fwdc243b.bin` from Ricoh, via MENU+power with a full battery).
2. **Firmware version must match.** All addresses, command tables, item names and
   the DEVELOP.MOD key were derived from **v1.60**. Check *MENU → Setup →
   Firmware Info/Options* first. On any other version, re-verify before running
   anything. Ricoh firmware cannot be rolled back after an update.
3. **The agent cannot see the camera.** The human is the only sensor. Ask them
   what is on the screen, never assume success; only claim a result when the
   user confirmed it or a file on the card proves it.
4. **One change per power cycle.** Each test should change one thing and write
   marker lines to a file on the card before/after each command
   (`filecreate`/`fileopen ... 1`/`filewriteln`/`fileclose`), so a hang or crash
   shows exactly which line was responsible.
5. **Read-only before write.** Prove a command path is harmless before using it
   to write. Prefer setters that the camera's own menu uses (the `UserData`
   shell, see settings.md) over low-level property/DSP commands.
6. **Remove `script/startup.ttl` (and `shutdown.ttl`) after use.** Scripts run on
   *every* boot / power-off while they are on the card. A forgotten script will
   silently re-apply settings or keep crashing a task.
7. **Full battery, card easy to remove.** Recovery for every failure seen so far
   was: pull the battery, remove the card, boot without the card.
8. **Do not commit Ricoh's binaries** (firmware, extracted RTOS/rootfs, Ghidra
   projects, decompiled code). They are copyrighted and huge. See `.gitignore`.

## Known-dangerous commands — do not run

Confirmed to crash (Data Abort in the Script task, NULL dereference):

| Command | What happened |
|---|---|
| `camprop_get_support_wo_linux`, `camprop_get_current_wo_linux`, `camprop_set_wo_linux` | Object at `FUN_533bcd04()+0xc` is NULL in normal operation. **At startup the crash blocks boot (black screen)**; at shutdown it is survived. |
| `camprop_get_current <id>` / `camprop_get_setting <id>` with an ID that is not in the property manager (e.g. 128) | "unknown property accessed" → default object with NULL value → crash while printing. IDs are **not** the `_wo_linux` IDs. |
| `camprop_get_support` | just forwards to `camprop_get_support_wo_linux` → same crash. |

Not tested, and destructive or irreversible by name. Do not run without a very
good reason and explicit user consent:

- ModeSet: `USR_DAT_CLEAR`, `USR_DAT_WRITE`, `ADJ_DAT_WRITE`, `DSP_ROM_STORE`,
  `SAVE_FLASH_FS`, `WRITE_CF_VNDR EN/DIS`, `RELEASE_COUNT *`, `DEBUG_MODE EN`,
  `OPEN_FACTORY_DEBUG_MENU`, `DEBUG_LOG_ERASE`, `EXCEPTION_LOG_ERASE`,
  `COLLAB_MODE *`, `LENS_FILTER_TYPE *`, `WIFI_INFO_PASSKEY_INIT`,
  `THERMAL_SHUTDOWN DIS`, `SR_PWM_OFF`, `RELEASE_AGING`, `*_RF_TEST`.
  (ADJ_DAT = factory calibration data. Losing it is not recoverable by the user.)
- Shell: `dd_in`, `dd_load`, `dd_recover_*`, `dd_refresh_*` (settings import/restore), `sys_factory*`, `med_format`, `ftest_format_sd`, `med_rm`, `med_restore`,
  `med_break`, `sys_fwdump`, anything `CAP_*`, `Mxic_*`, `Sdram_*`, `Arbiter_*`,
  `SR_*`, `wlanrf_*`, `blerf_*`, `FE_*`/`BE_*` debug, `USB_*`, `cpu_*`.

## UserData settings: extra care

`UserData Set` (see settings.md) writes real settings that persist. Before writing:

- Tell the user which setting changes and let them note the old value (there is
  no read-back yet).
- Use only tokens from `data/userdata_set_values.tsv`. For `int`/`float` items
  the parser does no range check. Only write numbers the camera itself uses.
- Do not touch without explicit user consent:
  - `SetupMenuReset*`: these probably trigger a reset of whole settings groups.
  - `SetupLanguage`: a wrong value can make the UI unreadable for the user.
  - `SetupWlan`, `SetupBleMode`, `*Transmit*`: wireless, pairing.
  - `CustomSettingBox*`: user modes U1–U3 (overwrites the user's saved modes).
  - `Common*` (Tv/Av/Sv, menu cursor positions): internal state, not user settings.

## What currently is left enabled on the test camera

- Script support (`SCRIPT_EN_MODE EN`) — inert without `script/*.ttl` on the card.
  Undo: `sdcard/undo_disable_scripts/` via MENU+power.
- Debug-log storage (`DBG_LOG_STORE_EN_MODE EN`) — makes exception logs contain a
  "Flush Log" section. Undo: `sdcard/undo_debuglog/` via MENU+power.

## Timing rules learned the hard way

- Change settings in `startup.ttl`. Changes made in `shutdown.ttl` are not saved.
- Export (`dd_out`) in `shutdown.ttl`, never as the first line of `startup.ttl` (defaults).

## Personal data

Settings exports (`KB609.DOM`) contain the owner's configuration and probably Wi-Fi
credentials and device identifiers. Never commit or publish them (`.gitignore` excludes
`camdata/` and `*.DOM`).

## Recovery playbook

| Symptom | Do this |
|---|---|
| Black screen after normal power-on with a script on the card | Pull battery, remove card, boot without card. Delete/fix `script/startup.ttl`. |
| Power-off seems stuck | Wait ~30 s, then pull battery. Delete `script/shutdown.ttl`. |
| Want to know what crashed | Script `sendln 'SYS_copylog C:\grlog C:\grlog'` at shutdown, read `grlog/except*.txt` (backtrace + Flush Log). |
| Want everything back to stock behaviour | Run both undo ModeSet folders, format the card in camera. |
