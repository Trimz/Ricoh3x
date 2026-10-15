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
`FUN_532912a8` (OnModeSetMessage) → `FUN_53290c58`. Dev items 1–6, 21–23, 48, 49 and 52–54 are
handled inline in `FUN_53290c58`; the others go through a controller/screen and
`FUN_536bf368`.

| ModeSet line | dev item | Action (ModeSet_Execute `FUN_536bf368` / DevItem `FUN_53290c58`) |
|---|---|---|
| `[DEBUG_MODE EN]` / `DIS` | 1 | flag +0x04 (Camera Mode Debug/Normal) |
| `[WRITE_CF_VNDR EN]` / `DIS` | 3 | dev-item handler `FUN_53290714`; purpose unknown |
| `[SCRIPT_EN_MODE EN]` / `DIS` | 4 | flag +0x10, **script support** (verified) |
| `[SW_DEBUG_MENU EN]` / `DIS` | 5 | dev-item handler `FUN_5329081c` |
| `[USR_DAT_CLEAR]` | 6 | **reset user settings** (`FUN_53828940` + `FUN_538280b0`) (!) |
| `[DSP_ROM_STORE]` | 7 | write DSP ROM (!) |
| `[ADJ_DAT_READ]` | 8 | factory calibration data → card (`FUN_5352809c`) |
| `[ADJ_DAT_WRITE]` | 9 | card → **factory calibration data** (`FUN_53527c8c`) (!!) |
| `[USR_DAT_READ]` | 10 | **export all settings** to `C:\KB<model>.DOM` (`FUN_53828ea8`), same as shell `dd_out` |
| `[USR_DAT_WRITE]` | 11 | **import all settings** from `C:\KB<model>.DOM` (`FUN_53828410`), same as shell `dd_in` (!) |
| `[CAM_LOG_DAT_READ]` | 12 | camera log → card (`FUN_5353cd84`) |
| `[USR_CLEAR_CAM_DISP]` | 13 | |
| `[RELEASE_COUNT 0/10/25/50/100]` | 14–18 | shutter count manipulation (!) |
| `[DEBUG_LOG_READ]` | 19 | debug log → `C:\log%d.txt` (`FUN_536b98d0(0)`) |
| `[EXCEPTION_LOG_READ]` | 20 | exception logs → `C:\except%d.txt` (`FUN_536c1958(0)`) |
| `[SERIAL_INPUT_EN_MODE EN]` / `DIS` | 21 | flag +0x30 (serial console input) |
| `[THERMAL_SHUTDOWN EN]` / `DIS` | 22 | flag +0x38, inverted (DIS disables thermal protection) (!) |
| `[WIFI_ADJ ON]` / `OFF` | 23 | |
| `[WAIT_S1]` | 24 | |
| `[SAVE_FLASH_FS]` | 25 | |
| `[SR_PWM_OFF]` | 26 | shake-reduction actuator test |
| `[SR_TRIPODCHECK_OFF]` | 27 | |
| `[RELEASE_AGING]` | 28 | shutter aging test |
| `[OPEN_DEBUG_MENU]` | 29 | opens debug menu screen |
| `[OPEN_FACTORY_DEBUG_MENU]` | 30 | opens factory debug menu |
| `[SCREEN_SHOT_MENU]` | 31 | |
| `[SWITCH_TEST]` | 32 | button test screen |
| `[CAM_LOG_DISP]` | 33 | |
| `[INFORMATION]` | 35 | version screen (verified) |
| `[ELECTRICLEVEL_CHECK]` | 36 | level sensor check (`FUN_536b0a74(0x40)`) |
| `[SR_HALL_TEST]` | 41 | |
| `[DEBUG_LOG_ERASE]` / `[EXCEPTION_LOG_ERASE]` | 42 / 43 | erase logs (`FUN_536b9d9c` / `FUN_536c1c34`) |
| `[DBG_LOG_STORE_EN_MODE EN]` / `DIS` | 49 | flag +0x20, **store debug log** (verified) |
| `[WLAN_RF_TEST]` / `[BLE_RF_TEST]` | 50 / 51 | radio tests (!) |
| `[COLLAB_MODE STREET/ING/URBAN/DIARY_EDITION]` / `DIS` | 52 | +0x48 = 1/2/3/4, 0: special-edition branding (!) |
| `[DBG_LOG_PURGE_EN_MODE EN]` / `DIS` | 53 | flag +0x4c |
| `[LENS_FILTER_TYPE ND]` / `HDF` | 54 | `FUN_536b468c(0/1)`: selects ND vs HDF filter type, i.e. the GR IIIx / GR IIIx HDF hardware variant (!) |
| `[WIFI_INFO_PASSKEY_INIT]` | 55 | reset Wi-Fi passkey |

"Flag +0xNN" = a word in the persistent developer flag block (`0x5aa5a55a` = on),
saved by `FUN_53527514`. Blank = not analysed. (!) = changes factory data,
counters, protection or hardware identity; see SAFETY.md.
