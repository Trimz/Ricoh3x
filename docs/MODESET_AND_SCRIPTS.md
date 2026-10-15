# Hidden ModeSet + script engine (GR IIIx fw 1.60)

Read SAFETY.md first.

## 1. ModeSet — developer commands from the SD card

**Trigger: hold MENU while pressing power** (the same boot used for firmware
updates). On a normal power-on, ModeSet files are ignored.

Files in the card root:

| File | Content |
|---|---|
| `DEVELOP.MOD` | 10 bytes `07 01 2c 1f 10 03 1e 16 05 2d` (unlock level 1, verified on camera). An alternative key `07 1a 02 0a 19 18 1b 1c 05 11` (level 2) was found statically; **untested**. |
| `00078490.609` | text, one `[COMMAND]` per line, `;` comments. Name comes from the format `C:\%08ld.%03ld` (`ModeSetOperation.cpp`, `FUN_536be850`). Verified on one camera; not proven to be the same on every unit. |

Verified on camera:

| Command | Result |
|---|---|
| `[INFORMATION]` | screen with DSP/CPU version and "Camera Mode: Normal" (Debug if `DEBUG_MODE` on) |
| `[SCRIPT_EN_MODE EN]` | message "script enable complete"; stores `0x5aa5a55a` in a persistent flag (`FUN_53290798`) |
| `[DBG_LOG_STORE_EN_MODE EN]` | **black screen, no message** (normal for this item), then power off; exception logs now carry a "Flush Log" section (`FUN_53290aa8`, flag at +0x20 of the same block) |

Command string table: `0x538f2d94`, 0x20 bytes/entry. Mapping table
`0x53b5b6a0`: 58 entries `{int16 cmdIndex, u8 devItem, u8 sub}`; dispatched via
`FUN_532912a8` (OnModeSetMessage) → `FUN_53290c58`.

| ModeSet line | dev item | sub |
|---|---|---|
| `[DEBUG_MODE EN]` / `DIS` | 1 | 6 / 5 |
| `[WRITE_CF_VNDR EN]` / `DIS` | 3 | 1 / 2 |
| `[SCRIPT_EN_MODE EN]` / `DIS` | 4 | 1 / 2 |
| `[SW_DEBUG_MENU EN]` / `DIS` | 5 | 1 / 2 |
| `[USR_DAT_CLEAR]` | 6 | 0 |
| `[DSP_ROM_STORE]` | 7 | 0 |
| `[ADJ_DAT_READ]` / `[ADJ_DAT_WRITE]` | 8 / 9 | 0 |
| `[USR_DAT_READ]` / `[USR_DAT_WRITE]` | 10 / 11 | 0 |
| `[CAM_LOG_DAT_READ]` | 12 | 0 |
| `[USR_CLEAR_CAM_DISP]` | 13 | 0 |
| `[RELEASE_COUNT 0/10/25/50/100]` | 14–18 | 0 |
| `[DEBUG_LOG_READ]` | 19 | 0 |
| `[EXCEPTION_LOG_READ]` | 20 | 0 |
| `[SERIAL_INPUT_EN_MODE EN]` / `DIS` | 21 | 1 / 2 |
| `[THERMAL_SHUTDOWN EN]` / `DIS` | 22 | 1 / 2 |
| `[WIFI_ADJ ON]` / `OFF` | 23 | 3 / 4 |
| `[WAIT_S1]` | 24 | 0 |
| `[SAVE_FLASH_FS]` | 25 | 0 |
| `[SR_PWM_OFF]` | 26 | 0 |
| `[SR_TRIPODCHECK_OFF]` | 27 | 0 |
| `[RELEASE_AGING]` | 28 | 0 |
| `[OPEN_DEBUG_MENU]` | 29 | 0 |
| `[OPEN_FACTORY_DEBUG_MENU]` | 30 | 0 |
| `[SCREEN_SHOT_MENU]` | 31 | 0 |
| `[SWITCH_TEST]` | 32 | 0 |
| `[CAM_LOG_DISP]` | 33 | 0 |
| `[INFORMATION]` | 35 | 0 |
| `[ELECTRICLEVEL_CHECK]` | 36 | 0 |
| `[SR_HALL_TEST]` | 41 | 0 |
| `[DEBUG_LOG_ERASE]` / `[EXCEPTION_LOG_ERASE]` | 42 / 43 | 0 |
| `[DBG_LOG_STORE_EN_MODE EN]` / `DIS` | 49 | 1 / 2 |
| `[WLAN_RF_TEST]` / `[BLE_RF_TEST]` | 50 / 51 | 0 |
| `[COLLAB_MODE STREET/ING/URBAN/DIARY_EDITION]` / `DIS` | 52 | 8/9/10/11 / 7 |
| `[DBG_LOG_PURGE_EN_MODE EN]` / `DIS` | 53 | 1 / 2 |
| `[LENS_FILTER_TYPE ND]` / `HDF` | 54 | 12 / 13 |
| `[WIFI_INFO_PASSKEY_INIT]` | 55 | 0 |

Only the three listed as verified have been run. See SAFETY.md for the ones to avoid.

## 2. Script engine (Tera Term macro dialect)

Once `SCRIPT_EN_MODE` is on, the camera runs, if present:

| File | When |
|---|---|
| `C:\script\startup.ttl` | every **normal** power-on (verified) |
| `C:\script\shutdown.ttl` | every power-off (verified) |
| `C:\script\dbgparam.ttl` | unknown, untested |

`C:\` is the SD card root. Use CRLF line endings.

Interpreter: keyword table `FUN_538c343c`, statement dispatch in
`FUN_538c1258`, error reporter `FUN_538c3148` (errors are logged and stop the
script; they do **not** hang the camera). The run loop `FUN_538bc080` is called
from the Script task at `0x536bc5e4`.

Verified commands: `filecreate`, `fileopen h 'path' 1` (append), `filewriteln`,
`fileclose`, `foldercreate`, `int2str`, `sendln`.

- `sendln '<shell command line>'` (token 0x4e, `FUN_538c06ac`) runs a camera shell
  command through a callback and sets `result` (0 seen). Shell output is **not**
  captured into `inputstr`; it goes to the debug log.
- `execcmnd` is *not* a shell exec: it runs a string as a TTL line (Tera Term
  semantics).
- `filecreate` on an existing file does not truncate it; it writes from offset 0.

Shell command table: 585 name→handler pairs inside the RTOS image (dumped to
`out/shellcmds.txt` locally; not committed). Useful ones:

| Shell command | Notes |
|---|---|
| `UserData Get/Set <Item> [Value]` | the settings interface, see IMAGE_CONTROL.md |
| `SYS_copylog <dir> <dir>` | needs a directory argument (handler reads argv[2]; passing the dir twice works). Copies stored debug-log slots to `<dir>\log%d.txt` and exception logs to `<dir>\except%d.txt`. Without an arg it only prints usage. |
| `CPU_buildinfo` | harmless, used as a sendln smoke test |

## 3. Proven test sequence (what actually happened)

| Step | Folder | Outcome |
|---|---|---|
| diag | `sdcard/diag_modeset_info` | MENU+power → info screen. Normal power → nothing. |
| 1 | `sdcard/step1_enable_scripts` | MENU+power → "script enable complete". |
| 2 | `_DO_NOT_USE_crashes/step2_readonly_probe` | startup camprop_*_wo_linux → **boot hang**, exception log. |
| 2a | `sdcard/step2a_fileonly` | file write OK; startup.ttl runs on normal boot. |
| 2b | `sdcard/step2b_one_sendln` | sendln returns, boot OK, inputstr empty. |
| 2c/2d | `_DO_NOT_USE_crashes/step2c`, `step2d` | shutdown camprop_*_wo_linux → crashes (survived), SYS_copylog gave only except logs. |
| 3 | `sdcard/enable_debuglog` (+ crashing script in `_DO_NOT_USE_crashes/step3_debuglog`) | debug-log store on; `camprop_get_current 128` → unknown property → crash. |
| 4 | `sdcard/step4_userdata_set` | **Custom 2 = Standard, Saturation +2, persists.** |

Exception logs from these runs are in `camlogs/`.
