# Continuum scattering source

SMElib normally treats the continuum source as the local Planck function.

Call `SetContinuumScatteringSourceMode(1)` to solve an approximate continuum mean intensity and enable the scattering source.

The source is defined by:

\[
S_\lambda = \frac{\kappa_\lambda B_\lambda + \sigma_\lambda J_\lambda}{\kappa_\lambda + \sigma_\lambda}.
\]

The implementation supports plane-parallel and spherical transfer.

Call `SetContinuumScatteringSourceMode(0)` to restore the default Planck-source treatment.

`GetContinuumOpacityComponents` returns true absorption, coherent scattering, and their sum.

`GetContinuumScatteringSource` returns the computed mean intensity and continuum source for the current atmosphere and geometry.

The option changes the source treatment only; it does not change the continuum opacity contributors.
