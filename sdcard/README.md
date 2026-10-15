# SD card layouts

Copy a folder's *contents* to the card root (`cp -X`, then `dot_clean` the card
so macOS `._` files don't end up on it). Format the card in the camera
between experiments. Read ../docs/SAFETY.md first.

| Folder | Boot | Effect | Status |
|---|---|---|---|
| `diag_modeset_info/` | MENU+power | shows DSP/CPU version screen | verified, read-only |
| `step1_enable_scripts/` | MENU+power | enables startup/shutdown scripts | verified |
| `undo_disable_scripts/` | MENU+power | disables scripts | not yet run |
| `enable_debuglog/` | MENU+power | stores debug log (black screen is normal) | verified |
| `undo_debuglog/` | MENU+power | disables debug-log storage | not yet run |
| `step2a_fileonly/` | normal | writes `C:\ttl_a.txt` | verified |
| `step2b_one_sendln/` | normal | runs `CPU_buildinfo`, writes markers | verified |
| `step4_userdata_set/` | normal | **writes** Custom 2 = Standard, Saturation +2 | verified |
| `step5_export_settings/` | normal | exports all settings to `C:\KB609.DOM` (`dd_out`) | verified, read-only; too early in boot (defaults) |
| `step6_export_diff/` | normal | export / set Custom 2 sat P3 / export / set P2 / export | verified |
| `step7_verify_batch/` | normal on/off | sets in shutdown.ttl (not saved; kept as evidence) | verified, no effect |
| `step8_verify_two_round/round1`, `round2` | normal on/off | **set 8 settings** / restore them, export at power-off | verified |
| `_DO_NOT_USE_crashes/` | — | scripts that crashed the camera; kept as evidence only | **do not use** |

Remember: delete `script/startup.ttl` after it has run once.
