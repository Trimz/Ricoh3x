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

## Image looks (e.g. from Lightroom presets)

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

- Back up / restore all settings (needs a read-back path, see open-questions.md).
- Load user modes U1–U3 from a card.
- Set LCD calibration, button layouts and display overlays in bulk.
