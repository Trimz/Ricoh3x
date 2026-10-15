# ModeSet: developer commands from the SD card

Read [SAFETY.md](SAFETY.md) first.

**Trigger: hold MENU while pressing power** (the same boot used for firmware
updates). On a normal power-on, ModeSet files are ignored.

## Files (card root)

| File | Content |
|---|---|
| `DEVELOP.MOD` | 10 bytes `07 01 2c 1f 10 03 1e 16 05 2d` (unlock level 1, verified on camera). An alternative key `07 1a 02 0a 19 18 1b 1c 05 11` (level 2) was found statically; **untested**. |
| `00078490.609` | text, one `[COMMAND]` per line, `;` comments. The name comes from the format `C:\%08ld.%03ld` in `AnalyzeModeSetFile` (`FUN_536be850`). Verified on one camera; not proven to be identical on every unit. |

## Verified commands

| Command | What the camera does |
|---|---|
| `[INFORMATION]` | screen with DSP/CPU version and "Camera Mode: Normal" ("Debug" if `DEBUG_MODE` is on) |
| `[SCRIPT_EN_MODE EN]` | message "script enable complete"; stores `0x5aa5a55a` in a persistent flag (`FUN_53290798`). Enables [scripting](scripting.md). |
| `[DBG_LOG_STORE_EN_MODE EN]` | **black screen, no message** (normal for this item), then power off. Exception logs afterwards carry a "Flush Log" section (`FUN_53290aa8`, flag at +0x20 of the same block). |

## All commands

Machine-readable: [`data/modeset_commands.tsv`](../data/modeset_commands.tsv).

Command string table `0x538f2d94` (0x20 bytes/entry). Mapping table `0x53b5b6a0`:
58 entries `{int16 cmdIndex, u8 devItem, u8 sub}`, dispatched by
`FUN_532912a8` (OnModeSetMessage) → `FUN_53290c58`. Items 1–5, 21–23, 48–49,
52–54 are handled inline (flags); the others open a controller/screen.

| ModeSet line | dev item | sub | Likely meaning |
|---|---|---|---|
| `[DEBUG_MODE EN]` / `DIS` | 1 | 6 / 5 | debug camera mode |
| `[WRITE_CF_VNDR EN]` / `DIS` | 3 | 1 / 2 | vendor write enable (unknown) |
| `[SCRIPT_EN_MODE EN]` / `DIS` | 4 | 1 / 2 | **script support** |
| `[SW_DEBUG_MENU EN]` / `DIS` | 5 | 1 / 2 | software debug menu |
| `[USR_DAT_CLEAR]` | 6 | 0 | clear user settings |
| `[DSP_ROM_STORE]` | 7 | 0 | write DSP ROM (!) |
| `[ADJ_DAT_READ]` / `[ADJ_DAT_WRITE]` | 8 / 9 | 0 | factory calibration data to/from card (!) |
| `[USR_DAT_READ]` / `[USR_DAT_WRITE]` | 10 / 11 | 0 | user settings to/from card |
| `[CAM_LOG_DAT_READ]` | 12 | 0 | camera log to card |
| `[USR_CLEAR_CAM_DISP]` | 13 | 0 | |
| `[RELEASE_COUNT 0/10/25/50/100]` | 14–18 | 0 | shutter count manipulation (!) |
| `[DEBUG_LOG_READ]` | 19 | 0 | debug log to card |
| `[EXCEPTION_LOG_READ]` | 20 | 0 | exception log to card |
| `[SERIAL_INPUT_EN_MODE EN]` / `DIS` | 21 | 1 / 2 | serial console input |
| `[THERMAL_SHUTDOWN EN]` / `DIS` | 22 | 1 / 2 | thermal protection (!) |
| `[WIFI_ADJ ON]` / `OFF` | 23 | 3 / 4 | |
| `[WAIT_S1]` | 24 | 0 | |
| `[SAVE_FLASH_FS]` | 25 | 0 | |
| `[SR_PWM_OFF]` | 26 | 0 | shake-reduction actuator test |
| `[SR_TRIPODCHECK_OFF]` | 27 | 0 | |
| `[RELEASE_AGING]` | 28 | 0 | shutter aging test |
| `[OPEN_DEBUG_MENU]` | 29 | 0 | debug menu |
| `[OPEN_FACTORY_DEBUG_MENU]` | 30 | 0 | factory debug menu |
| `[SCREEN_SHOT_MENU]` | 31 | 0 | |
| `[SWITCH_TEST]` | 32 | 0 | button test |
| `[CAM_LOG_DISP]` | 33 | 0 | |
| `[INFORMATION]` | 35 | 0 | version screen |
| `[ELECTRICLEVEL_CHECK]` | 36 | 0 | level sensor check |
| `[SR_HALL_TEST]` | 41 | 0 | |
| `[DEBUG_LOG_ERASE]` / `[EXCEPTION_LOG_ERASE]` | 42 / 43 | 0 | |
| `[DBG_LOG_STORE_EN_MODE EN]` / `DIS` | 49 | 1 / 2 | **store debug log** |
| `[WLAN_RF_TEST]` / `[BLE_RF_TEST]` | 50 / 51 | 0 | radio tests |
| `[COLLAB_MODE STREET/ING/URBAN/DIARY_EDITION]` / `DIS` | 52 | 8/9/10/11 / 7 | special-edition branding |
| `[DBG_LOG_PURGE_EN_MODE EN]` / `DIS` | 53 | 1 / 2 | |
| `[LENS_FILTER_TYPE ND]` / `HDF` | 54 | 12 / 13 | GR IIIx HDF variant switch (!) |
| `[WIFI_INFO_PASSKEY_INIT]` | 55 | 0 | reset Wi-Fi passkey |

"Likely meaning" is inferred from names only. (!) marks commands that could
change factory data, counters or hardware identity. See SAFETY.md.
