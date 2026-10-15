# On-camera test log

One GR IIIx, updated from 1.42 to **1.60** before testing (the official update:
`fwdc243b.bin` in the card root, **hold MENU + power**, Execute).
Card layouts are in [`sdcard/`](../sdcard).

| # | Date | Card layout | Boot | Result |
|---|---|---|---|---|
| 0 | 2026-10-15 | `diag_modeset_info` | normal | nothing happens: ModeSet is not read on normal boot |
| 0 | 2026-10-15 | `diag_modeset_info` | MENU+power | info screen (DSP/CPU version, "Camera Mode: Normal") |
| 1 | 2026-10-15 | `step1_enable_scripts` | MENU+power | "script enable complete" |
| 2 | 2026-10-15 | `_DO_NOT_USE_crashes/step2_readonly_probe` | normal | `camprop_*_wo_linux` in startup.ttl → **black screen, boot hang**. Recovered by pulling the battery and booting without card. Exception log: NULL deref in Script task. |
| 2a | 2026-10-15 | `step2a_fileonly` | normal | boots; `C:\ttl_a.txt` = "script ran" |
| 2b | 2026-10-15 | `step2b_one_sendln` | normal | boots; `sendln 'CPU_buildinfo'` returns, `result=0`, `inputstr` empty |
| 2c | 2026-10-15 | `_DO_NOT_USE_crashes/step2c` | normal on/off | shutdown `camprop_get_current_wo_linux 128` crashes the Script task (survived); `SYS_copylog` without a dir arg does nothing |
| 2d | 2026-10-15 | `_DO_NOT_USE_crashes/step2d` | normal on/off | all 26 `_wo_linux` reads crash (survived); `SYS_copylog <dir> <dir>` writes `except*.txt` |
| 3 | 2026-10-15 | `enable_debuglog` | MENU+power | black screen, no message (expected) |
| 3 | 2026-10-15 | `_DO_NOT_USE_crashes/step3_debuglog` | normal on/off | `camprop_get_current 128` → "unknown property accessed", crash; exception logs now include Flush Log |
| 4 | 2026-10-15 | `step4_userdata_set` | normal | `UserData Set StillImageControlNo2 Standard` + `…No2ParamStandardSaturation P2` → menu shows Custom 2 = Standard, Saturation +2 |
| 4b | 2026-10-15 | (script removed) | normal | Custom 2 still Saturation +2: **persistent** |
| 5 | 2026-10-15 | `step5_export_settings` | normal | `sendln 'dd_out'` wrote `C:\KB609.DOM` (150,512 bytes); boot normal. Chunks APP/HT/FE/INF/PF/DC. |
| 6 | 2026-10-15 | `step6_export_diff` | normal | export A, set Custom 2 Std saturation P3, export B, set P2, export C. `filerename` works. A and B = factory defaults (too early in boot); C = real values and differs from A exactly at table offsets 0x1c0/0x1c2/0x38c → **APData01 offset = store offset**. Parsed C confirmed by the user in the menus. Script ran on two boots. |
| 7 | 2026-10-15 | `step7_verify_batch` | normal on/off | in `shutdown.ttl`: export, set 8 values, export, restore, export. All three exports identical → exports show the **saved** state and sets made in `shutdown.ttl` are never saved. Camera unchanged. |
| 8a | 2026-10-15 | `step8_verify_two_round/round1` | normal on/off | `startup.ttl` sets 8 values, `shutdown.ttl` exports. All 8 changed exactly as intended, nothing else (except lens focus position). User saw Custom 1 contrast +1 in the menu. |
| 8b | 2026-10-15 | `step8_verify_two_round/round2` | normal on/off | same with the original values. Export identical to the pre-test export (0 differences). User saw Custom 1 contrast back at 0. |
| 9 | 2026-10-15 | round-trip "restore" of 956 settings (generated, personal, not committed) | normal on/off | **Camera damaged:** slow menus, live-view noise, freeze after every shot. Export differed from the backup. See incident-2026-10-15.md. |
| 9r | 2026-10-15 | recovery | — | Reset Settings, card format, firmware 1.60 reinstall, `[DBG_LOG_STORE_EN_MODE DIS]` and `[SCRIPT_EN_MODE DIS]` (confirmed). Freeze after shots remains → Ricoh service. |

Exception logs: `camlogs/2d` (from tests 2–2d), `camlogs/3b` (test 3).
