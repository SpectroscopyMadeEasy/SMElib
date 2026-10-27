# Spherical transfer on a reference optical-depth coordinate

The explicit `InputModelEx` interface separates geometry from depth scale.
The original `InputModel` ABI is retained: `TAU` means PP/TAU, `RHOX` means
PP/RHOX, and `SPH` means SPH/RHOX. Passing TAU numbers to legacy `SPH` does
not select optical-depth transfer.

`GetModelInputCapabilities(int, void**)` takes no arguments and returns the
capability string `PP:RHOX,PP:TAU,SPH:RHOX,SPH:TAU`. Unlike the normal
status-returning SME APIs, its nonempty return is data, not an error.

## Explicit input ABI

`InputModelEx(int n, void *args[])` requires exactly 15 arguments:

| Index | C pointee type | Meaning |
| --- | --- | --- |
| 0 | short | Number of layers, 2 through MOSIZE (288) |
| 1 | double | Effective temperature, K |
| 2 | double | log surface gravity, cgs |
| 3 | double | Reference wavelength, Angstrom |
| 4 | short | Geometry: 0 PP, 1 SPH |
| 5 | short | Depth scale: 0 RHOX, 1 TAU |
| 6 | short[20] | Opacity package flags |
| 7 | double[ndepth] | Increasing inward column mass or reference optical depth |
| 8 | double[ndepth] | Temperature, K |
| 9 | double[ndepth] | Electron number density, cm^-3 |
| 10 | double[ndepth] | Atomic number density, cm^-3 |
| 11 | double[ndepth] | Mass density, g cm^-3 |
| 12 | double[ndepth] | Microturbulent velocity, cm s^-1 |
| 13 | double | Reference radius, cm; ignored for PP |
| 14 | double[ndepth] | Height relative to radius, cm; null allowed for PP |

SPH requires positive radius, strictly decreasing heights, and positive
`radius + height` at every layer. The depth coordinate and model arrays
must be finite. Optical depths are linear, not logarithmic. The reference
must be monochromatic continuum extinction at the supplied wavelength,
not Rosseland optical depth.

## Coordinate transformation

For radial column mass m, reference optical depth t, and monochromatic
extinction chi:

```
dt = chi_ref dm
chi_new = chi / chi_ref
kappa_new = kappa / chi_ref
sigma_new = sigma / chi_ref
```

Spherical ray construction retains the geometric path/radial-path factor,
using increments in t instead of m. The existing DELO solver and grazing
ray construction are reused. Geometry/depth state is independent of the
legacy temporary `MOTYPE=-1` used to retrieve raw line opacities.
`GetLineOpacity` continues to return per-gram opacities.

The reference continuum is evaluated exactly, cached, and invalidated with
model, abundance, EOS, or continuum state changes. Approximate wavelength
opacity grids do not replace this reference. Public transfer/source entry
points reject a nonpositive or nonfinite reference before internal solvers
run. Existing continuum-scattering source solvers receive all three opacity
components divided by the same reference.

Spherical contribution functions accumulate into a temporary ray-depth
array, then fold the far-side contribution into physical radial layers.
This avoids writing mirrored depths beyond the caller's physical-depth
array. Unused contribution layers are initialized to zero.

Finite-grid interpolation and integration need not be invariant under a
nonlinear coordinate change. Validate convergence using a controlled
transformation before interpreting differences between separately tabulated
MARCS mass and optical-depth scales. The companion PySME diagnostic is
`examples/validate_sph_tau.py`.
