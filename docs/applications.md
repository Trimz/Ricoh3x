# Applications

Things that can be built on the settings interface ([settings.md](settings.md)).

## Shooting profiles on a card

A `startup.ttl` that applies a whole configuration at once, e.g. a "street"
profile:

```
sendln 'UserData Set StillFocus Snap'
sendln 'UserData Set StillSnapDistanceCm 250'
sendln 'UserData Set StillFullPressSnap On'
sendln 'UserData Set StillStillRecordForm RawPlus'
sendln 'UserData Set StillShadowCorrect Low'
```

Keep one card per profile, boot once, remove the script. (Unverified items. Test
them one by one first.)

## Backup (read-only) — restore is NOT safe

Exporting (`dd_out` in `shutdown.ttl`) and decoding (`grsettings.py decode`/`diff`) are fine.
**Restoring a whole export by script damaged the test camera**: see
[incident-2026-10-15.md](incident-2026-10-15.md). Use the export as a written record and
re-enter settings in the menu, or write only a few individual items.

## Image looks (e.g. from Lightroom presets)

`tools/xmp_to_profile.py preset.xmp --slot 1` writes a profile for Custom 1 or 2; then
`grsettings.py script`. Samples: `examples/sample_film.xmp`, `examples/sample_bw.xmp`.

Write Custom 1/2 Image Control from a description of a look. An approximate
Lightroom `.xmp` → Image Control mapping:

| Lightroom | Image Control |
|---|---|
| Saturation / Vibrance | `Saturation` |
| Contrast | `Contrast` |
| Highlights / Shadows | `ContrastHighLight` / `ContrastShadow` |
| Clarity / Texture | `ClarityControl` |
| Vignette | `Shading` |
| Grain | `Particle` (monochrome bases) |
| B&W / film looks | base effect (`MonotoneGR`, `PositiveFilm`, `NegativeFilm`, …) |
| Sharpening | `Sharpness` |
| Temp / Tint | white-balance items (untested) |

The camera works in coarse −4…+4 steps, so the mapping is lossy.

## Ideas

- Back up all settings (`dd_out` + `tools/dom_parse.py`); restore by replaying `UserData Set`
  lines generated from a decoded export (safer than `dd_in`).
- Load user modes U1–U3 from a card.
- Set LCD calibration, button layouts and display overlays in bulk.
