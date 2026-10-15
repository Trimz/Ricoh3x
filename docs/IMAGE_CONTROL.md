# Writing Image Control (Custom 1 / Custom 2) from the SD card

Status (2026-10-15, GR IIIx fw 1.60): **works and persists across reboots.**
Verified on camera: Custom 2 set to Standard + Saturation +2 via a startup script,
shown in the camera menu, still there after a reboot with the script removed.

Read SAFETY.md first.

## Chain

1. One-time: enable scripts with a ModeSet file (MODESET_AND_SCRIPTS.md).
2. Put `script/startup.ttl` on the SD card (CRLF line endings, TTL dialect).
3. In the script, call the hidden `UserData` debug shell:

```
sendln 'UserData Set StillImageControlNo2 Standard'
sendln 'UserData Set StillImageControlNo2ParamStandardSaturation P2'
```

4. Power on normally, then remove the script from the card.

`UserData Set` dispatches by item name to the same UserData-model setters the
camera menu uses (e.g. `FUN_5325de5c(model, value)` for Custom1 Standard
saturation), so it goes through normal validation and is saved like a menu change.

## The `UserData` shell command (`0x53008038`)

- `UserData Get <Item>` (argc 3) → `FUN_53386230`; prints the value to the debug
  log only (the output is **not** returned to the script — `inputstr` stays empty).
- `UserData Set <Item> <Value>` (argc 4) → `FUN_5334688c` (too large for the
  Ghidra decompiler; follow per-item branches in the disassembly).
- Every one of the 377 Image-Control / White-Balance item names in
  `userdata_items_image_control_wb.txt` is matched by both Get and Set.

## Item naming

Slots: `No0` = the normal (non-custom) setting, `No1` = Custom 1, `No2` = Custom 2.
`StillActiveImageControlSet` selects which set is active.

Base effect of a slot: `StillImageControlNo{0,1,2}` with one of

```
Standard Vivid MonotoneGR SoftMonotone HardMonotone HighContrastBW
PositiveFilm BleechBypass_GR Retro HdrCuisine CrossProcess NegativeFilm
```

(internal enum 0x0b … 0x16 in that order; the spelling `BleechBypass_GR` is Ricoh's).

Parameters are stored **per base effect**:
`StillImageControlNo{n}Param<Base><Param>`, e.g.
`StillImageControlNo1ParamPositiveFilmContrastShadow`. NegativeFilm parameters use
the prefix `AfterReleaseStillImageControlNo{n}Param...`.

`<Param>` (not every base has every parameter — see the item list):

| Param | Meaning |
|---|---|
| `Saturation` | saturation |
| `ColorHue` | hue |
| `ImageKey` | high/low key |
| `Contrast`, `ContrastHighLight`, `ContrastShadow` | contrast, highlight / shadow contrast |
| `Sharpness` | sharpness |
| `Shading` | vignetting |
| `ClarityControl` | clarity |
| `Particle` | grain (monochrome bases) |
| `ColorToneMonotone`, `ColorToneBleechBypass`, `ColorToneRetro`, `ColorToneHdrIntense`, `HdrIntense` | toning / intensity |
| `FilterEffectCustom`, `FilterEffect{R,G,B}Custom{1..4}` | B&W filter effect and custom filter colours |

## Values

For the ±4 sliders (verified for Saturation; same parser shape seen elsewhere):

```
M4 M3 M2 M1 OFF P1 P2 P3 P4      →  enum 0..8  (= -4 … +4)
```

Toning, filter, HDR intensity, white-balance colour temperature, etc. use other
token sets. Before writing one of those, read its branch in `FUN_5334688c` (the
`strcmp` chain against `argv[3]`) and the matching Get branch in `FUN_53386230`
(which prints the same tokens).

White balance items exist too (`StillWhiteBalance*`,
`AfterReleaseStillWhiteBalanceCustom{1,2,3}{,BA,GM,ColorTemp}`), but nothing in
WB has been tested.

## Reading values back

`UserData Get` output only reaches the debug log. The only proven way to read it
from outside so far is the "Flush Log" section of an exception log, which needs a
crash. That is **not** acceptable as a read method. Open problem: find a log sink
that writes to the card without a crash (ideas: `DEBUG_LOG_READ` ModeSet item 19,
`llog_export`, `inf_camlog`, or `med_fputs` from inside the shell).

Practical read method today: have the user look at the camera menu.

## Lightroom mapping (planned, approximate)

| Lightroom | Image Control |
|---|---|
| Saturation / Vibrance | Saturation |
| Contrast | Contrast |
| Highlights / Shadows | ContrastHighLight / ContrastShadow |
| Clarity / Texture | ClarityControl |
| Vignette | Shading |
| Grain | Particle (monochrome bases only) |
| B&W / film looks | base effect |
| Sharpening | Sharpness |
| Temp / Tint | white balance items (untested) |
