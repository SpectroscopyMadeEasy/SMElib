# Native line-depression contribution function

This optional diagnostic decomposes absolute continuum-minus-full intensity
into atmospheric interval contributions. It supplements the emission
contribution function, which describes escaping radiation. The numerical
implementation is experimental; integral closure alone does not establish
convergence of the depth distribution.

## Transfer equation and source functions

With distance s increasing towards the observer, write

\[
\frac{dI_c}{ds}=-\chi_c I_c+\chi_c S_c,\qquad
\frac{dI_f}{ds}=-\chi_f I_f+\chi_f S_f.
\]

For D = Ic − If and chi_l = chi_f − chi_c,

\[
\frac{dD}{ds}=-\chi_fD+\chi_\ell(I_c-B)+q,\qquad
q=\chi_cS_c-\chi_fS_f+\chi_\ell B.
\]

The diagnostic attenuates this local driving by full-opacity optical depth
towards the observer and retains the finite boundary separately. Native path
column mass increases inward; the positive integration measure is k dm,
equivalent in magnitude to chi ds. Spherical path lengths, not a fixed
plane-parallel 1/mu factor, determine the mass increments.

The LTE branch of `OPMTRX` uses the Planck function for the full-opacity source,
while the continuum source can include its continuum-scattering solution.
Therefore q must use the actual returned sources. It cannot generally be
replaced by sigma(Jc−Jf): that identity requires compatible continuum and full
scattering solutions. For Sf=B at the nodes, q=chi_c(Sc−B). The LTE line-driving
interpretation is the tested scope; general NLTE line attribution is not
validated by this implementation.

## Native solution and the L/Q/N decomposition

See `TBINTG_sph`, `SMEPhysicalCFLDPath` and `SMEPhysicalCFLD` in
[the native source](../src/sme/sme_synth_faster.cpp).
The diagnostic reuses prepared atmospheric state, evaluates `OPMTRX`, and
repeats native formal transfer with tracing enabled. It does not read traces
cached by an earlier synthesis. The trace captures optical increments,
Bézier controls, incoming/outgoing intensities and the boundary intensity.
`cfld_inside` evaluates the within-cell continuum intensity from the captured
incoming intensity and retained quadratic source, including its small-optical-
depth series. It does not substitute B or emergent continuum flux for Ic.

At an integration point, let ec, ef be the native Bézier extinction profiles,
cs, fs the source interpolants evaluated in their respective optical-depth
coordinates, and kl and B the linearly interpolated nodal line extinction and
Planck source. The native effective depression driving is

\[
A_{\rm eff}=(e_f-e_c)I_c+e_c c_s-e_f f_s.
\]

The decomposition used by the diagnostic is

\[
L_{\rm local}=k_l(I_c-B),\qquad
Q_{\rm local}=\operatorname{linear}(q_i,q_{i+1}),\qquad
N_{\rm local}=A_{\rm eff}-L_{\rm local}-Q_{\rm local}.
\]

Each term is integrated with the same full-opacity attenuation and path
measure. Thus N accounts locally for extinction and source-interpolation
terms relative to the chosen nodal representation. It is not distributed
from a measured global closure residual, an additional physical process or
an uncertainty estimate. Its magnitude and localisation depend on the
representation and resolution. Signed contributions are retained without
renormalisation. Optically thick intervals are subdivided for quadrature;
the implementation caps subdivisions at 4096 and neglects further attenuated
driving once accumulated full optical depth reaches 700.

## Spherical mapping and boundaries

`cfld_geometry` currently duplicates native spherical path construction in a
diagnostic helper. Core rays reach the deepest radial node. Tangent rays
contain near-side nodes, a turning-shell chord and mirrored far-side nodes.
For n=8 tangent path entries, node indices map to radial nodes as
`[0,1,2,3,3,2,1,0]`. Integrated intervals i=1..6 map to radial intervals
`[1,2,3,2,1,0]`. Both ends of the turning chord use node-3 fields: this is the
inherited endpoint approximation, not a newly sampled turning-point model.
Near/far contributions add to their radial shell. Path buffers are sized
before folding into radial-interval buffers, rather than using a radial
stride for a longer path.

The native recurrence excludes the outgoing interval 0–1 and the diagnostic
preserves that domain. It does not imply the omitted segment is physically
negligible. Tangent rays retain the far-side outer interval. Two-entry grazing
paths return zero contributions/intensities; their projected-area weights
must not be redistributed to other rays. Core rays retain the native bottom
source/gradient boundary prescription; tangent rays have zero incident
boundary intensity.

The physical depression boundary is

\[
D_b=e^{-\tau_{f,b}}(I_{c,b}-I_{f,b}).
\]

It differs from the difference of emission boundaries,
exp(−tau_c,b) Ic,b − exp(−tau_f,b) If,b. Compatible emission decompositions can
close the same total depression with their own boundaries but do not thereby
provide the same local physical driving distribution. Emission controls here
come directly from the traced recurrence; the legacy emission-CF interface
and its spherical indexing concern are not repaired by this patch.

## Arrays, flux and interpretation

`SMEPhysicalCFLD` returns `(wavelength, ray, 6, radial_interval)` channels:
L, Q+N, continuum emission, full emission, Q, N. Complete shell contributions
are L+Q+N. Metadata contains Ic, If, attenuated continuum/full boundaries,
physical depression boundary, sampled minimum internal Ic/If, path count and
tangent flag. Sampled minima are diagnostics, not proofs of positivity
throughout each interval. `SMEPhysicalCFLDPath` provides the prescribed-field
interface; `SMECFLDRayGeometry` exposes path geometry.

Absolute intensities retain native `FLUX_SCALE` units. Disc flux uses pi times
**global projected-area weights**, with flux normalised at the inherited outer
radius. The caller supplies compatible native ray nodes/weights; chunk weights
must not each be renormalised. Shell integrals are divided by each coordinate's
own positive bin widths to produce densities in log tauRoss, log tau5000 or
height. Boundaries remain separate. No broadening is applied.

“Physical” identifies the continuum-minus-full driving definition; the complete
returned quantity also includes native numerical accounting N. Neither a CFLD
peak nor its width identifies a species-population shell or a gas velocity.
Tests should distinguish analytical agreement, ordinary/diagnostic intensity
agreement, closure, source consistency, and angular/depth distribution
convergence. The companion PySME tests cover prescribed fields; broader stellar
validation and current limitations belong in the accompanying PR evidence.

Global atmospheric state requires serialised access across preparation and
diagnostics. Thread-local trace restoration does not make SMElib thread-safe.
API/export conventions, C-ABI allocation-exception handling and cross-platform
symbol lookup still require integration review; Linux is the tested platform.
