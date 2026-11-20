# Continuum scattering source

SMElib normally treats the continuum source as the local Planck function.

Select the source treatment with `SetContinuumScatteringSourceMode(mode)`:

| mode | source treatment | status |
|---:|---|---|
| 0 | Historical local Planck source | Default |
| 1 | Continuum-only mean intensity used inside continuum and spectral lines | Deprecated |
| 2 | Separate continuum and line-plus-continuum radiation fields, with LTE line opacity treated as true absorption | Recommended scattering mode |

Mode 1 can strongly overfill line cores and wings where scattering is
important, for example in metal-poor cool giants in the near-UV. Selecting it
emits a deprecation warning once per process. Use mode 2 for new work; mode 1
will be removed in a future major release.

The source is defined by:

\[
S_\lambda = \frac{\kappa_\lambda B_\lambda + \sigma_\lambda J_\lambda}{\kappa_\lambda + \sigma_\lambda}.
\]

Modes 1 and 2 support plane-parallel and spherical transfer. In mode 2,
plane-parallel models use a six-angle Feautrier solve and spherical models use
the conservative spherical moment solver on the actual atmosphere radius grid.

The coherent-scattering term includes Rayleigh scattering by H I, He I, and H₂, together with electron scattering.

Call `SetContinuumScatteringSourceMode(0)` to restore the default Planck-source treatment.

In fixed four-region comparisons over 3650--3820, 3900--4100, 4300--4400, and
5000--5200 A, mode 2 minus mode 1 reached maximum/RMS normalized-flux
differences of `0.4057/0.3094` for an HD 122563-like spherical atmosphere and
`0.3015/0.2342` for a BD-18 5550-like spherical atmosphere in the
3650--3820 A region. The corresponding differences were `0.00433/0.00248` for
an HD 84937-like plane-parallel atmosphere and `0.00271/0.00118` for a solar
plane-parallel atmosphere.

`GetContinuumOpacityComponents` returns true absorption, coherent scattering, and their sum.

`GetContinuumScatteringSource` returns the computed mean intensity and continuum source for the current atmosphere and geometry.

The option changes the source treatment only; it does not change the continuum opacity contributors.
