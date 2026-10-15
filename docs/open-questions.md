# Open questions and leads

## Reading values back (highest priority)

`UserData Get` and most shell commands print only to the debug log. Today the
only way to see that output is the Flush Log section of an exception log, which
needs a crash, so it isn't usable. Leads:

- `SYS_copylog` reports that the debug-log slots aren't valid (`FUN_536b7370`).
  Find when slots get written (maybe only on specific events, or with
  `DBG_LOG_PURGE_EN_MODE`).
- ModeSet `[DEBUG_LOG_READ]` (item 19) and `[CAM_LOG_DAT_READ]` (item 12).
- `llog_export` (writes `C:\linux%02d.log`, Linux side only?), `inf_camlog`.
- `med_fopen`/`med_fputs`/`med_fclose` shell commands, if a value could be
  routed into them.
- Find the `printf` sink (`FUN_536b8150` → `FUN_536b00c8`, `FUN_5381e01c`) and
  whether it can be redirected to a file.

## Settings

- Verify more items on camera, especially `int`/`float` ones and whether
  setters clamp out-of-range values.
- User modes U1–U3: semantics of `CustomSettingBox{n}`, `…Regist{n}`, `…Name{n}`.
- `USR_DAT_READ` / `USR_DAT_WRITE` (ModeSet items 10/11): file format of the
  user-settings dump. A backup/restore of all settings might be possible.
- Token sets for filter-effect custom RGB, toning and WB colour temperature are
  in the TSV but unverified.

## Firmware

- `camprop` property manager (`FUN_533c43e8`/`FUN_533c8498`): its ID space.
  `_wo_linux` uses an object (`FUN_533bcd04()+0xc`) that is NULL in normal mode;
  who initialises it?
- `dbgparam.ttl`: when does it run?
- DEVELOP.MOD level 2 key and what it unlocks.
- Whether the ModeSet file name `00078490.609` is constant across units.
- Portability to GR III (non-x) and other firmware versions.
