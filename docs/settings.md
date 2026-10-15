# Camera settings over the SD card: the `UserData` interface

Read [SAFETY.md](SAFETY.md) first. Requires script support ([modeset.md](modeset.md))
and a script ([scripting.md](scripting.md)).

## The command

The internal shell has a debug command `UserData` (handler `0x53008038`,
`UserDataDebug::shell_UserData`):

```
UserData Get <Item>            # prints the value to the debug log (FUN_53386230)
UserData Set <Item> <Value>    # writes the value (FUN_5334688c)
```

From a script: `sendln 'UserData Set StillJpegSize M'`.

`Set` finds the item by an exact string compare, parses `<Value>`, then calls
the same UserData model setter that the camera's menus call
(`FUN_5320ad88()` → `FUN_5320b31c()` → per-item setter). The value is
therefore stored and persisted like a menu change. An unknown value prints
`argv[3] invalid` to the debug log and changes nothing.

## Catalogue

[`data/userdata_set_values.tsv`](../data/userdata_set_values.tsv) lists **all 1,036
items** accepted by `Set`. It is generated statically by
[`tools/userdata_values.py`](../tools/userdata_values.py) from the firmware
(columns: item, kind, values, setter, handler, store). `store` is where the setter writes
in the in-RAM UserData struct, e.g. `u8@0x2aa`; `*8` means the value is written to all 8
struct copies (the model holds 8 struct pointers at +4..+0x20). 1,034 of 1,036 resolved.

| Kind | Count | Value syntax |
|---|---|---|
| `enum` | 909 | one of the listed tokens, e.g. `On`, `Off`, `P2`, `Standard` (`token=internal value`) |
| `int` | 108 | integer, parsed with `strtoul(…, 0)` (decimal or `0x…`) |
| `float` | 19 | decimal number, parsed with `strtod` |

Caveats:
- The token list is what the **debug shell** accepts. It can be narrower than the
  menu (e.g. `StillAspectRatio` accepts only `3_2` and `1_1`).
- For `int`/`float` items the parser does **no range check**. Whether the setter
  clamps is unknown, so never write a number you haven't seen the camera use
  itself.
- `Netherlandish ` (SetupLanguage) contains a trailing space in the firmware.
- Verified on camera so far: `StillImageControlNo2` and
  `StillImageControlNo2ParamStandardSaturation`. Everything else is static analysis.

### Groups

| Prefix | Items | What |
|---|---|---|
| `Still…` | 437 | still shooting: exposure, focus, drive, quality, NR, Image Control, WB |
| `Movie…` | 319 | the same for movie mode |
| `Custom…` | 70 | button/dial assignments, display options, **user modes** (`CustomSettingBox*`) |
| `Setup…` | 43 | system setup (LCD, sounds, power, Wi-Fi/BT, language, file naming) |
| `Common…` | 39 | shared state (Tv/Av/Sv/Xv, menu cursor positions, live-view geometry) |
| `Play…` | 17 | playback |
| `AfterRelease…` | ~110 | settings added in later firmware: NegativeFilm params, WB custom 1–3, user-mode memory flags, snap-focus priority |

### Still shooting (non Image Control)

| Item | Values |
|---|---|
| `StillExposureMode` | `P` `Av` `Tv` `M` |
| `StillProgramLine` | `Normal` `Depth` `DepthDeep` |
| `StillAeMode` | `Multi` `Center` `Spot` `Highlight` |
| `StillSvAuto`, `StillSvAutoManual` | `On` `Off` |
| `StillSvAutoUpper`, `StillSvAutoLower`, `StillSvAutoLowerTv` | float |
| `StillNdFilter` | `Auto` `On` `Off` |
| `StillFocus` | `AutoArea` `AutoAreaM` `ZoneSelect` `Select` `Pinpoint` `Follow` `Continuous` `Mf` `Snap` `Infinity` |
| `StillSnapDistanceCm` | `30` `100` `150` `200` `250` `350` `500` `Infinity` |
| `StillFullPressSnap` | `On` `Off` |
| `StillAfRange` | `10cmToInfinity` `10cmTo50cm` `50cmToInfinity` |
| `StillFaceDetection` | `On` `OnlyAutoArea` `Off` |
| `StillFocusAssist` | `EdgeEnhance` `EdgeExtract` `Off` |
| `StillAfAssistBeam`, `StillMfAutoZoom`, `StillAeLinkAfArea` | `On` `Off` |
| `StillAfCActionPriority` | `Focus` `Release` |
| `StillDriveMode` | `Single` `Continuous` `Bracket` `MultiExposure` `Interval` `IntervalMultiExposure` |
| `StillSelfTimer` | `Off` `2Sec` `10Sec` |
| `StillBracketPriority` | `ZeroMinus` `Minus` `Plus` `ZeroPlus`; `StillExposureBracketStep` float |
| `StillMultiExposureCompositeType` | `Additive` `Average` `Bright` |
| `StillInterval*` | trigger `Off`/`Clock`, times/counts as int |
| `StillStillRecordForm` | `Jpeg` `Raw` `RawPlus` |
| `StillJpegSize` | `L` `M` `S` `XS` |
| `StillAspectRatio` | `3_2` `1_1` |
| `StillCropMag` | float |
| `StillColorSpace` | `sRGB` `AdobeRGB` |
| `StillHighlightCorrect` | `Auto` `On` `Off` |
| `StillShadowCorrect` | `Auto` `Low` `Mid` `High` `Off` |
| `StillHighIsoNR` | `Auto` `Low` `Mid` `High` `Custom` `Off` |
| `StillHighIsoNRCustomIso{50…819200}` | `Low` `Mid` `High` `Off` |
| `StillLongTvNR` | `Auto` `On` `Off` |
| `StillLensShadingCorrection`, `StillShakeReduction`, `StillAutoHorizon` | `On` `Off` |
| `StillLowPassSelector` | `Strong` `Weak` `Off` |
| `StillFlashMode` | `Force` `ForceRedEye` `SlowSync` `SlowSyncRedEye`; `StillFlashCorrectValue` float |
| `StillWhiteBalance…` | see [image-control.md](image-control.md#white-balance) |

### Setup highlights

| Item | Values |
|---|---|
| `SetupLcdBrightness`, `SetupLcdColorSaturation` | `M7…M1` `Normal` `P1…P7` |
| `SetupLcdAdjustBA` / `SetupLcdAdjustGM` | `B7…B1 Normal A1…A7` / `G7…G1 Normal M1…M7` |
| `SetupOutdoorMonitor` | `P2` `P1` `Off` `M1` `M2` |
| `SetupAutoPowerOff`, `SetupSleep` | `1min` `3min` `5min` `10min` `30min` `Off` |
| `SetupBeepVolume` | `Lv0`…`Lv3` |
| `SetupFileNumbering` | `FolderFile` `File` `Off` |
| `SetupWlan`, `SetupGeotagging`, `SetupAutoTransmit` | `On` `Off` |
| `SetupBleMode` | `AlwaysOn` `LinkPowerState` `AlwaysOff` |
| `SetupStartUpDustRemoval`, `SetupShutDownDustRemoval` | `On` `Off` |

`SetupMenuReset*` and `SetupLanguage` are on the do-not-touch list in SAFETY.md.

### Customisation and user modes

- `CustomSwitch*`: button assignments (Fn, ADJ, Wi-Fi short/long, AE-L, …).
- `CustomAdjMode1…5`: ADJ lever menu slots.
- `CustomCapture*` / `CustomPlayback*`: which overlays appear in each display mode.
- `CustomSettingBox{1,2,3}`, `…Name{n}`, `…Regist{n}`: **user modes U1–U3** (contents, names,
  registration). `AfterReleaseModeMemory*`: which settings are remembered.
  These are the route to loading complete user modes from the card, but they are
  untested and should be explored read-first.

## Exporting all settings (read-back)

`sendln 'dd_out'` in a script (or ModeSet `[USR_DAT_READ]`) writes every settings
domain to `C:\KB609.DOM` (609 = model code). Verified on camera (test 5): 150 KB file,
boot unaffected. The camera is not changed.

Format: chunks `[char tag[4]][u32 len][data]`, tags `APP`, `HT`, `FE`, `INF`, `PF`, `DC`
(`BE` also exists in code). Each chunk holds sub-records: a 0x3c-byte header (name such as
`APData01.bin`, NUL-padded; 0x14 bytes if header words +0x14/+0x18 are non-zero), a u32
size, then the data. `APP` contains `APData00`–`APData11`; `APData01`–`08` (0xb26 bytes
each) are the 8 UserData struct copies, fields stored little-endian.

Mapping file offsets to the RAM `store` offsets above is **not finished** (they don't line
up 1:1 for every field). The safe way to pin it down is a diff test: export, change one
known setting, export again. See open-questions.md.

The import direction (`dd_in`, `[USR_DAT_WRITE]`) restores a whole package and is on the
do-not-run list until the format is fully understood.

## Regenerating

```
python3 -I tools/userdata_values.py out/rtos.bin > data/userdata_set_values.tsv
```

`out/rtos.bin` is the decompressed RTOS image (see firmware.md). On another firmware
version, the Set handler's address range (`SET_LO`/`SET_HI`) and parser addresses
must be re-located first.
