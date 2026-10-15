"""Convert a Lightroom / Camera Raw preset (.xmp) into a GR IIIx Custom 1/2 profile.

    python3 -I tools/xmp_to_profile.py preset.xmp --slot 1 [--base Standard] > look.profile
    python3 -I tools/grsettings.py script look.profile OUTDIR --export

The camera has far fewer, coarser controls (-4..+4), so this is an approximation:

    Lightroom                         -> Image Control parameter
    Saturation (+ half of Vibrance)   -> Saturation
    Contrast                          -> Contrast
    Highlights                        -> ContrastHighLight
    Shadows                           -> ContrastShadow   (sign inverted: LR + lifts shadows)
    Clarity (+ half of Texture)       -> ClarityControl
    Post-crop vignette amount         -> Shading          (sign inverted: LR - darkens corners)
    Grain amount                      -> Particle         (monochrome bases only)
    Sharpening amount                 -> Sharpness        (relative to LR default 40)
    Convert to B&W                    -> base MonotoneGR (HardMonotone if contrast >= +2)
    B&W split-toning hue              -> ColorToneMonotone (Sepia/Red/Green/Blue/Purple)

Parameters that do not exist for the chosen base are skipped (see
data/userdata_set_values.tsv). Temperature/tint are not mapped.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(HERE, '..', 'data', 'userdata_set_values.tsv')
STEP = ['M4', 'M3', 'M2', 'M1', 'OFF', 'P1', 'P2', 'P3', 'P4']


def read_crs(path):
    text = open(path, encoding='utf-8', errors='replace').read()
    vals = {}
    for k, v in re.findall(r'crs:(\w+)="([^"]*)"', text):
        vals[k] = v
    for k, v in re.findall(r'<crs:(\w+)>([^<]*)</crs:\1>', text):
        vals[k] = v
    return vals


def num(vals, *keys, default=0.0):
    for k in keys:
        if k in vals:
            try:
                return float(vals[k].replace('+', ''))
            except ValueError:
                pass
    return default


def step(x, scale=25.0):
    """Lightroom -100..100 -> camera -4..+4 token."""
    i = max(-4, min(4, round(x / scale)))
    return STEP[i + 4]


def tone_from_hue(h):
    if h < 0:
        return None
    if 20 <= h < 60:
        return 'Sepia'
    if h < 20 or h >= 330:
        return 'Red'
    if 60 <= h < 170:
        return 'Green'
    if 170 <= h < 260:
        return 'Blue'
    return 'Purple'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('xmp')
    ap.add_argument('--slot', type=int, choices=(1, 2), required=True, help='Custom 1 or Custom 2')
    ap.add_argument('--base', help='force the base effect (e.g. Standard, PositiveFilm, NegativeFilm)')
    a = ap.parse_args()

    names = {l.split('\t', 1)[0] for l in open(TSV)}
    v = read_crs(a.xmp)
    bw = v.get('ConvertToGrayscale', 'False').lower() == 'true'
    contrast = num(v, 'Contrast2012', 'Contrast')
    base = a.base or (('HardMonotone' if contrast >= 50 else 'MonotoneGR') if bw else 'Standard')

    params = {
        'Saturation': step(num(v, 'Saturation') + 0.5 * num(v, 'Vibrance')),
        'Contrast': step(contrast),
        'ContrastHighLight': step(num(v, 'Highlights2012', 'Highlights')),
        'ContrastShadow': step(-num(v, 'Shadows2012', 'Shadows')),
        'ClarityControl': step(num(v, 'Clarity2012', 'Clarity') + 0.5 * num(v, 'Texture')),
        'Shading': step(-num(v, 'PostCropVignetteAmount')),
        'Sharpness': step(num(v, 'Sharpness', default=40.0) - 40.0, scale=20.0),
    }
    grain = num(v, 'GrainAmount')
    params['Particle'] = 'Off' if grain < 10 else 'Low' if grain < 35 else 'Mid' if grain < 65 else 'High'
    if bw:
        tone = tone_from_hue(num(v, 'SplitToningShadowHue', default=-1.0)
                             if num(v, 'SplitToningShadowSaturation') > 0 else -1.0)
        if tone:
            params['ColorToneMonotone'] = tone

    slot = f'No{a.slot}'
    print(f'# from {os.path.basename(a.xmp)}  (approximate; review before use)')
    print(f'StillImageControl{slot} = {base}')
    prefix = 'AfterReleaseStillImageControl' if base == 'NegativeFilm' else 'StillImageControl'
    skipped = []
    for p, val in params.items():
        item = f'{prefix}{slot}Param{base}{p}'
        if item in names:
            print(f'{item} = {val}')
        elif val not in ('OFF', 'Off'):
            skipped.append(f'{p}={val}')
    print(f'StillActiveImageControlSet = {slot}')
    if skipped:
        print(f'# not available for {base}: {" ".join(skipped)}')


if __name__ == '__main__':
    main()
