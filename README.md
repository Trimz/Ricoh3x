# Ricoh GR IIIx — Image Control from the SD card (fw 1.60)

Goal: load Lightroom-style looks into the camera's **Custom 1 / Custom 2** Image
Control slots without Ricoh software.

**Status:** working end-to-end on one GR IIIx running firmware 1.60. A script on
the SD card can set any Image Control parameter of Custom 1/2 through the
camera's own settings code; the change shows in the menu and survives reboots.

> ⚠️ Undocumented developer features on real hardware. Read
> [docs/SAFETY.md](docs/SAFETY.md) before running anything. Never flash
> modified firmware. Everything here is version-specific to **v1.60**.

## How it works (short)

1. **Unlock:** `DEVELOP.MOD` + `00078490.609` containing `[SCRIPT_EN_MODE EN]` in
   the card root, then **hold MENU and power on**. Camera says
   "script enable complete". One time only.
2. **Script:** put `script/startup.ttl` (Tera Term macro dialect, CRLF) on the
   card. It runs on every normal power-on.
3. **Set values** through the hidden `UserData` shell:
   ```
   sendln 'UserData Set StillImageControlNo2 Standard'
   sendln 'UserData Set StillImageControlNo2ParamStandardSaturation P2'
   ```
   `No1` = Custom 1, `No2` = Custom 2; values `M4…M1 OFF P1…P4` = −4…+4.
4. **Remove the script** from the card after one boot.

## Docs

- [docs/SAFETY.md](docs/SAFETY.md): guardrails, dangerous commands, recovery
- [docs/IMAGE_CONTROL.md](docs/IMAGE_CONTROL.md): the `UserData` interface, item names, values, Lightroom mapping
- [docs/MODESET_AND_SCRIPTS.md](docs/MODESET_AND_SCRIPTS.md): ModeSet commands, script engine, test history
- [docs/FIRMWARE_NOTES.md](docs/FIRMWARE_NOTES.md): firmware format, tooling, addresses
- [docs/userdata_items_image_control_wb.txt](docs/userdata_items_image_control_wb.txt): all 377 settable Image Control / WB item names

## Layout

```
docs/        findings (start here)
sdcard/      ready-to-copy card layouts (see sdcard/README.md)
tools/       firmware decompressor, ARM xref helpers, headless Ghidra scripts
camlogs/     exception logs retrieved from the camera during testing
```

Not committed (copyrighted / large): the firmware zip, `fw/`, `out/` (extracted
RTOS image, strings, decompiler output), `rootfs/`, `lx/`, Ghidra projects. Rebuild
them with the steps in FIRMWARE_NOTES.md.

## Next steps

- Lightroom `.xmp` → `startup.ttl` converter (mapping table in IMAGE_CONTROL.md).
- A crash-free way to read `UserData Get` output back to the card.
- Value tokens for toning / filter / WB items.
