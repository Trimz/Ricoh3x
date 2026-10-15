# Image Control and white balance

Read [settings.md](settings.md) first. Full value tables are in
[`data/userdata_set_values.tsv`](../data/userdata_set_values.tsv).

**Verified on camera:** `UserData Set StillImageControlNo2 Standard` and
`UserData Set StillImageControlNo2ParamStandardSaturation P2` made Custom 2 show
Standard / Saturation +2 in the menu, and the change persisted with the script
removed.

## Slots

| Item | Values |
|---|---|
| `StillActiveImageControlSet` | `No0` (normal) `No1` (Custom 1) `No2` (Custom 2) |
| `StillImageControlNo{0,1,2}` (base effect of the slot) | `Standard` `Vivid` `MonotoneGR` `SoftMonotone` `HardMonotone` `HighContrastBW` `PositiveFilm` `BleechBypass_GR` `Retro` `HdrCuisine` `CrossProcess` `NegativeFilm` (internal 11–22) |

Parameters are stored **per base effect**:
`StillImageControlNo{n}Param<Base><Param>`, e.g.
`StillImageControlNo1ParamPositiveFilmContrastShadow`. NegativeFilm parameters
were added later and use `AfterReleaseStillImageControlNo{n}ParamNegativeFilm<Param>`.
Not every base has every parameter; the TSV lists which exist.

## Parameters

| `<Param>` | Values |
|---|---|
| `Saturation`, `ColorHue`, `ImageKey`, `Contrast`, `ContrastHighLight`, `ContrastShadow`, `Sharpness`, `Shading`, `ClarityControl` | `M4 M3 M2 M1 OFF P1 P2 P3 P4` (−4…+4, internal 0…8) |
| `ColorToneRetro` | `M4…P4` |
| `ColorToneMonotone` | `OFF` `Sepia` `Red` `Green` `Blue` `Purple` … (see TSV) |
| `ColorToneBleechBypass` | `Normal` `Cool` `Warm` |
| `ColorToneHdrIntense` | `OFF` `BW` `Sepia` |
| `HdrIntense` | `Low` `Mid` `High` |
| `Particle` (grain, monochrome bases) | `Off` `Low` `Mid` `High` (internal 0, 3, 2, 1) |
| `FilterEffectCustom` | `OFF` `Custom1`…`Custom4` |
| `FilterEffect{R,G,B}Custom{1..4}` | int (custom filter colour components; range unknown) |

## White balance

| Item | Values |
|---|---|
| `StillWhiteBalance` | `Auto` `Multi` `Daylight` `Shade` `Cloudiness` `Flu_D` `Flu_N` `Flu_W` `Flu_L` `Tungsten` `Cte` `Manual1` `ColorTemp1` `Custom1` `Custom2` `Custom3` |
| `StillWhiteBalance<Preset>AdjustBA` | `B14…B1 NORMAL A1…A14` |
| `StillWhiteBalance<Preset>AdjustGM` | `G14…G1 NORMAL M1…M14` |
| `StillWhiteBalanceColorTemp` | int (Kelvin; range unknown) |
| `AfterReleaseStillWhiteBalanceCustom{1,2,3}` | base preset for WB Custom 1–3 |
| `AfterReleaseStillWhiteBalanceCustom{n}{BA,GM,ColorTemp}` | fine-tune / Kelvin for the custom WB |
| `StillFixWbAutoAdjust`, `StillTungstenAwb` | `On`/`Off`, `Strong`/`Weak` |

Nothing in WB has been tested on the camera.

## Implementation notes

- Example setter: Custom 1 Standard saturation → `FUN_5325de5c(model, 0..8)`,
  reached via `0x532f2ccc` from the Set handler `FUN_5334688c`.
- Get (`FUN_53386230`) prints the same tokens, so the Get and Set vocabularies match.
- Wi-Fi HTTP API can only *select* an effect (including Custom 1/2); USB/MTP
  saturation setters in `mtpd` are dead code. The UserData shell is the only
  write path found that covers individual parameters.
