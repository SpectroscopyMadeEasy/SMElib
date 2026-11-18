# Continuum-scattering source modes

`SetContinuumScatteringSourceMode(0)` retains the historical Planck source.
Mode `1` is the existing opt-in continuum-only solve. Mode `2` is a separate
opt-in path: it solves the continuum source with continuum extinction, then
solves the line-plus-continuum field with LTE line opacity added to true
absorption. Plane-parallel mode 2 uses the six-angle Feautrier solver; spherical
models use the conservative spherical moment solver with `RADIUS + RAD_ATMO`.
The default remains mode 0, and NLTE synthesis continues to use the existing
source handling.

For a quantitative comparison, synthesize identical embedded MARCS atmospheres
with modes 0, 1, and 2 in fresh processes. Keep the wavelength raster and line
list fixed, clear inherited `PYSME_H_*` and scattering-control environment
variables, and set `VECLIB_MAXIMUM_THREADS=1`, `OMP_NUM_THREADS=1`, and
`OPENBLAS_NUM_THREADS=1`. Compare continuum flux ratios and normalized-flux
max/rms differences in the H-line core/wings and metal-line cores over
3650--3820, 3900--4100, 4300--4400, and 5000--5200 A. A mode-2 run should also
record the 3700-A gain and, for the two giant controls, the frozen BN `a(n)`
metric for H10/H11/H15--H18. The PySME exposure and submodule bump are deferred
until the upstream decision between modes 1 and 2.
