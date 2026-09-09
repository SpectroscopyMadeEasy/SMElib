# Brackett Stark-profile convolution

SMElib `v6.13.18` adds an optional Stark-profile construction for Brackett lines from Br10 upward (`n=4`, `m>=10`).
The default remains the historical profile so existing calculations do not change silently.

## Selecting the profile

Set the following environment variable before synthesis:

```bash
export PYSME_H_STARK_CONVOLUTION=convolution
```

Only the value `convolution` enables the new path.
An unset variable or the value `legacy` selects the historical profile.

The switch does not affect lower Brackett lines, other hydrogen series, EOS, occupation probabilities, or continuum opacity.

## Construction

The legacy path adds the impact and quasistatic Stark components.
The new path convolves the impact-electron component with the total quasistatic component, which contains the ion and electron contributions.

Both components are evaluated on one uniform vacuum-wavelength support with 201 points over ±40 Å.
The component functions receive the corresponding air wavelengths, matching the existing non-Lyman convention.
The convolution is converted from wavelength to frequency units and interpolated to the requested wavelength.
It is zero outside the support.
Results are cached for repeated evaluations of the same line and atmospheric state.

No physical constants, species data, partition functions, or EOS tolerances are changed.

## Regression values

The release regression uses a solar MARCS atmosphere (`Teff=5772 K`, `log(g)=4.44`, `[M/H]=0`, `vmic=1 km/s`), resolving power 300,000, a ±5 Å window, and a 0.02 Å wavelength step.
Equivalent widths are integrated over the synthesis window.

| Line | Legacy EW (Å) | Convolution EW (Å) | Reference EW (Å) |
| --- | ---: | ---: | ---: |
| Br10 | 1.212788 | 0.561734 | 0.5618 |
| Br11 | 0.926236 | 0.355227 | 0.3553 |

The convolution results agree with the accepted reference values to better than 0.03%.
The unset/default mode reproduces the legacy result.

These values are regression anchors, not a complete validation over stellar parameters or all high-order Brackett lines.
Keep `legacy` available when reproducing older work.
