# Physical CFLD: reviewer guide

Prepared for review of the optional PySME/SMElib physical line-depression diagnostic, 18 November 2026. This is a description of the **implemented prototype**, including its limitations, rather than a claim of integration readiness.

The principal review questions are the native source treatment, the meaning of the DELO–Bézier correction, and spherical/grazing-ray mapping. Short excerpts below are copied verbatim from the local source. **Code illustrates the implementation; tests and saved numerical audits provide evidence of its behaviour.** Neither is alone proof of physical validity.

## 1. Source identity and scope

SMElib develop base: `a76e1ed5cfdb438aeee841fd3f8ae90ee7264c52`. Numerical tests used predecessor `717c7050563b8b8bc06b802320f526b777a7774a`; the intervening commit changes only the CI workflow.
Companion PySME develop base: `e9b21894626fe2fc887fa590ba5caf3481d5a6b0`.
These identify the bases, not commits containing the modifications. Exact native-file SHA-256 and excerpt hashes are in `PHYSICAL_CFLD_REVIEWER_GUIDE.sources.json`. Line links refer to this worktree and may move during review.

Native implementation: `src/sme/sme_synth_faster.cpp`, principally `TBINTG_sph`, `SMEPhysicalCFLDPath`, `cfld_geometry`, `SMEPhysicalCFLD`. Companion Python implementation: `src/pysme/line_depression.py` and `SME_DLL.GetLineDepressionContributionfunction` in `src/pysme/sme_synth.py`. API names are provisional.

This contribution excludes molecular-line imports, abundance/RV fitting, observational workflows, and the separate outer-boundary restoration experiment. It supports the prepared spherical diagnostic; the analytical plane-parallel limit is tested with prescribed fields, not a general plane-parallel stellar API.

## 2. Continuum-minus-full transfer equation

Let distance s increase towards the observer, with extinction per unit length chi and source function S:

\[
\frac{dI_c}{ds}=-\chi_c I_c+\chi_cS_c,\qquad
\frac{dI_f}{ds}=-\chi_f I_f+\chi_fS_f.
\]

For D = Ic − If and chi_l = chi_f − chi_c, subtraction gives

\[
\frac{dD}{ds}=-\chi_fD+\chi_\ell I_c+\chi_cS_c-\chi_fS_f
=-\chi_fD+\chi_\ell(I_c-B)+q,
\]
\[
q=\chi_cS_c-\chi_fS_f+\chi_\ell B.
\]

For the physical domain actually integrated by the native solver,

\[
D_{\rm out}=e^{-\tau_{f,b}}(I_{c,b}-I_{f,b})+
\int_b^{\rm out}e^{-\tau_{f,\rm out}(s)}[\chi_\ell(I_c-B)+q]ds.
\]

The prototype's RHOX-path variable m increases inward along the stored ray, opposite to propagation. Extinction arrays are used with path-column-mass increments: k dm = chi ds in magnitude. The integration code uses positive dm and outward attenuation; it does not insert a plane-parallel 1/mu factor into spherical-shell integration. Wavelength, source scaling and opacity conventions are those of the native prepared state. `FLUX_SCALE` converts to the native absolute-intensity output; inputs and outputs are not continuum-normalised.

B is the local LTE Planck source used to define line driving. The algebra can retain a general Sf, but the current physical interpretation and stellar tests concern LTE lines. NLTE line attribution has not been validated.

## 3. Actual source arrays and why Q is retained

`SMEPhysicalCFLD` calls `OPMTRX` at each wavelength, obtaining full/continuum opacities and sources. Despite its variable name, `source_line` in OPMTRX is the source used for full-opacity transfer. In the tested LTE branch it is the thermal Planck source; `source_cont` can instead use the continuum-scattering solution:

[Native source, lines 10900–10910](src/sme/sme_synth_faster.cpp#L10900)

```cpp
    SRC_cont=PlanckLambdaSource(CONWL5, HNUK, TEMPER);
    if(initNLTE)
    {
      source_cont[ITAU]=use_continuum_scattering_source?scattering_source[ITAU]:SRC_cont;
      source_line[ITAU]=0.;
    }
    else
    {
      source_cont[ITAU]=use_continuum_scattering_source?scattering_source[ITAU]:SRC_cont;
      source_line[ITAU]=SRC_cont;
    }
```

`CONTINUUM_SCATTERING_SOURCE` obtains absorption/scattering/extinction from `CONTOP_COMPONENTS` and dispatches to `SolveContinuumScatteringMomentSphRhox` for spherical models. It is a continuum solution; this is not evidence of a corresponding full-line scattering field Jf. OPMTRX's NLTE branch is different and is outside this validation scope.

Consequently, when Sf=B at the nodes, q simplifies to kc(Sc−B). It cannot generally be substituted by sigma(Jc−Jf). That latter identity requires consistent continuum/full emissivities with the same scattering coefficient and thermal line source. Even a numerically nonzero Q is therefore not automatically a physical *difference of two self-consistent scattering solutions*. It accounts for the actual source functions used by this native calculation.

Reviewer question: is this source convention intentional for these native modes, and how should its scope be exposed to users? The diagnostic does not silently replace it with another scattering solver.

## 4. Retaining internal directional intensity

The diagnostic reuses the prepared atmospheric/EOS/opacity state and native transfer algorithm. **It repeats native formal transfer with tracing enabled**, once for the continuum and once for the full opacity along each ray. It does not reuse traces cached by an earlier ordinary synthesis. OPMTRX is also evaluated by the diagnostic; this is not a zero-work accessor.

The trace records extinction/source Bézier controls, optical thickness, incoming/outgoing intensity and the initial boundary. The original native update is retained:

[Native source, lines 9367–9370](src/sme/sme_synth_faster.cpp#L9367)

```cpp
    B=ALPHA*SRC_B+BETA*SRC_A+GAMMA*CNTR_AB;
    if(cfld_trace) { CFLDCell &c=cfld_trace->cells[IM]; c.dt=DELTA; c.scontrol=CNTR_AB; c.incoming=INTENSITY; }
    INTENSITY=EPS*INTENSITY+B;
    if(cfld_trace) cfld_trace->cells[IM].outgoing=INTENSITY;
```

`CFLDTraceScope` restores the previous thread-local pointer on leaving each traced call. This protects trace lifetime, not the global atmosphere: the Python caller must hold `smelib_session` over the whole preparation/diagnostic workflow.

At each quadrature position, `cfld_inside` evaluates the local formal solution of the retained quadratic continuum source from the captured incoming intensity. It is an analytical within-cell reconstruction, not a separate atmospheric transfer solver and not Ic=B or the emergent continuum flux. Small optical thickness uses a series approximation. Internal full intensity is similarly sampled for validity diagnostics.

## 5. DELO–Bézier effective terms and N

At local inward mass coordinate t in [0,1], ec and ef are quadratic Bézier extinction profiles. pc and pf are their partial optical depths; cs and fs are quadratic sources evaluated in their respective optical-depth coordinates. B(t) is linearly interpolated, as are the nodal line extinction kl(t) and general source qphysical(t).

Define effective full-minus-continuum extinction k_eff = ef−ec. The implemented local total driving is

\[
A_{\rm eff}=(e_f-e_c)I_c+e_c c_s-e_f f_s.
\]

The chosen nodal line-driving representation is L_local = kl(Ic−B). The remainder is

\[
R=e_cc_s-e_ff_s+(e_f-e_c)B+(e_f-e_c-k_l)(I_c-B).
\]

Q_local is the linear interpolation of nodal q; N_local = R−Q_local. Thus L_local+Q_local+N_local=A_eff **pointwise**, before integration. This accounts for both effective extinction differences and source-product/interpolation differences; it is not merely a source-curvature correction.

[Native source, lines 10277–10287](src/sme/sme_synth_faster.cpp#L10277)

```cpp
      double factor=exp(-tf-pf)*dm*w[j]/panels*FLUX_SCALE;
      double kl=(1-t)*(kf[i]-kc[i])+t*(kf[i+1]-kc[i+1]);
      double q0=kc[i]*sc[i]-kf[i]*sf[i]+(kf[i]-kc[i])*planck[i];
      double q1=kc[i+1]*sc[i+1]-kf[i+1]*sf[i+1]+(kf[i+1]-kc[i+1])*planck[i+1];
      double qphysical=(1-t)*q0+t*q1;
      double correction=ec*cs-ef*fs+(ef-ec)*bb+(ef-ec-kl)*(inside-bb);
      out[i]+=factor*kl*(inside-bb);
      out[(n-1)+i]+=factor*correction;
      out[4*(n-1)+i]+=factor*qphysical;
      out[5*(n-1)+i]+=factor*(correction-qphysical);
    }
```

The shared factor includes exp(−tf−pf), positive path measure, Gauss weights and FLUX_SCALE. Optically thick intervals are subdivided for quadrature; 24 versus 48 local Gauss points is a separate integration check. The code caps panel count at 4096 and stops attenuated contributions once accumulated tf reaches 700; these are numerical limits, not physical boundaries.

N is calculated locally from interpolants, not from a global closure error, and no contributions are renormalised to force closure. N is **not an uncertainty** or a separate emissivity process. Its magnitude and localisation depend on this nodal decomposition and native discretisation. The continuum physical limit and the discrete solver's exact accounting should not be conflated. Reviewer question: is this the most useful and defensible public decomposition, especially where N remains appreciable under refinement?

## 6. Three distinct depth decompositions

The existing `GetContributionfunction(mu, wave, ...)` answers where emergent radiation is contributed. The new `GetLineDepressionContributionfunction(wave, mu, layers, ...)` answers where continuum-minus-full absorption depression is produced under the implemented transfer equation. These are complementary diagnostics, not interchangeable arrays or competing versions of the same definition. The high-level emission-CF switch is unchanged. Neither is a species-population distribution.


- Native emission contributions: layer contributions to emergent Ic or If.
- Difference of emission contributions: an accounting decomposition of Ic−If when its own boundary difference is included.
- Physical line-depression diagnostic: L+Q+N with its physical depression boundary.

Channels 2 and 3 are computed directly from traced native recurrence increments, avoiding the existing emission-CF stride issue. They are native-recurrence emission controls, **not calls to GetContributionfunction**. The original public emission routine remains untouched.

For emission controls, continuum and full boundary attenuation differ. The physical depression boundary uses full attenuation for both boundary intensities. These boundaries must not be interchanged:

[Native source, lines 10294–10298](src/sme/sme_synth_faster.cpp#L10294)

```cpp
  meta[3]=exp(-tf)*f.boundary*FLUX_SCALE;
  meta[4]=exp(-tf)*(c.boundary-f.boundary)*FLUX_SCALE;
  meta[5]=minc*FLUX_SCALE;meta[6]=minf*FLUX_SCALE;
  return 0;
}
```

## 7. Spherical ray construction and shell folding

`cfld_geometry` reproduces the native spherical path construction in a diagnostic helper; it is currently duplicated logic, not a call to a single shared geometry routine. Core-intersecting rays reach the deepest radial node. Tangent rays store near-side nodes, a chord in the turning shell and mirrored far-side nodes. Their mass increments follow spherical path lengths, including special treatment of the turning chord.

The mapping of path-node opacity/source values uses:

[Native source, lines 10373–10377](src/sme/sme_synth_faster.cpp#L10373)

```cpp
      std::vector<double>kf(n),kc(n),sf(n),sc(n),bb(n),local(6*(n-1));
      for(int i=0;i<n;i++){
        int r=grazing[j]?(i<n/2?i:n-1-i):i;
        kf[i]=kf0[r];kc[i]=kc0[r];sf[i]=sf0[r];sc[i]=sc0[r];
        bb[i]=exp(50.7649141-5*log(WL[k]))/expm1(1.43868e8/WL[k]/T[r]);
```

The interval mapping and accumulation are:

[Native source, lines 10381–10385](src/sme/sme_synth_faster.cpp#L10381)

```cpp
      for(int i=1;i<n-1;i++){
        int shell=grazing[j]?(i<n/2?i:n-2-i):i;
        if(shell<0||shell>=nrad-1)return 12;
        for(int ch=0;ch<6;ch++)dest[ch*(nrad-1)+shell]+=local[ch*(n-1)+i];
      }
```

For a tangent path with n=8 entries, the node map is `[0,1,2,3,3,2,1,0]`. Integrated path intervals i=1..6 map to radial intervals `[1,2,3,2,1,0]`. Interval i=3 is the turning chord in shell 3; its two endpoints both use node-3 fields. This is the native approximation across the partial shell, not interpolation to a new turning-point atmospheric node. Near/far contributions add to the same shell; signs are retained. The near-side interval i=0 is omitted, whereas the far-side outer interval maps to shell 0 and remains included.

For core rays, path interval i maps directly to radial interval i. Local arrays are sized `6*(npath−1)` before folding into `6*(nradial−1)`, avoiding a ray-length write into a radial-stride output slot. This avoids the previously identified hazard in the legacy emission-CF interface; it does not repair that interface globally.

Reviewer questions: verify the turning-chord allocation and inherited endpoint approximation, near/far asymmetry from interval omission, and all index ranges. Exact reproduction of an earlier implementation does not independently prove these choices physically correct.

## 8. Finite boundaries and grazing paths

The native formal solver starts with zero incident intensity for tangent rays. Core rays use its existing bottom source/gradient prescription. Both remain separate from local contributions:

[Native source, lines 9292–9303](src/sme/sme_synth_faster.cpp#L9292)

```cpp
  SRC_B=source[NRHOX-1];       // Source function
  SRC_C=source[NRHOX-2];
  OPC_B=opacity[NRHOX-1];  // Opacities
  OPC_C=opacity[NRHOX-2];
  DBNU=2.0*(SRC_B-SRC_C)/((RHOX[NRHOX-1]-RHOX[NRHOX-2])*(OPC_B+OPC_C));
  INTENSITY =(grazing)?0.:0.5*(SRC_B+SRC_C)+DBNU;  // Line intensity at the boundary

  if(cfld_trace) { cfld_trace->boundary=INTENSITY; cfld_trace->cells.resize(NRHOX-1); }
  SPRIME_SAVE=0.0;                          // Initialize S'

  for(IM=NRHOX-2; IM>0; IM--)  // Work your way from the deepest
  {                            // layer to the surface
```

The loop ends at IM=1, so emergent output represents the native truncated domain, not propagation through the outgoing interval 0–1 to the outermost node. The diagnostic also begins its contributing intervals at i=1. It does not assert that the omitted segment has no physical effect.

For two-entry grazing paths, the spherical diagnostic returns zero intensities/contributions and records path count/tangent metadata. These rays retain their supplied projected-area weights; they are not silently removed and the other weights are not renormalised. The separate restored-boundary experiment is excluded from this patch.

## 9. Flux, atmospheric coordinates and interface

Native state channels have shape `(nwave,nray,6,nradial−1)`:

| Channel | Meaning |
|---|---|
|0|L|
|1|Q+N (historical combined remainder)|
|2|Continuum emission control|
|3|Full emission control|
|4|Q|
|5|N|

A nearby legacy C++ comment describes only four channels and calls the remainder “general q”; the assignments above and the Python channel names are authoritative for this six-channel prototype. This comment needs correction during integration.

Metadata: Ic, If, attenuated continuum boundary, attenuated full boundary, physical depression boundary, sampled minimum internal Ic/If, followed in spherical output by path count/tangent flag. Minima are sampled validity diagnostics, not proofs of positivity everywhere.

The Python result computes total from channels 0+4+5. `disc_flux` applies pi times caller-supplied native-compatible **global projected-area weights**, including chunks without renormalisation. The diagnostic does not itself choose an angular quadrature. Flux is reported in the inherited outer-radius convention. No rotational/instrumental convolution is applied.

Shell integrals remain primary. Density in x=log10(tauRoss) is DeltaD/abs(diff(x)); log10(tau5000) and geometric height require their own widths. Peaks must be measured independently in each density. Finite boundaries remain separate, never assigned to an arbitrary shell.

## 10. Evidence, and what each check establishes

| Check | Evidence | Interpretation/limit |
|---|---|---|
|Prescribed tests|22 pass in companion `tests/cfld/test_prescribed.py`|No-line, signed source terms, closure, coordinates, chunk weights, repeated calls and invalid inputs; not a stellar geometry proof|
|Original/develop prescribed comparison|8 cases, 56/64/109/215 nodes, core/tangent|All channels/metadata and ordinary reference recurrence exactly equal|
|Linear-source analytical flux benchmark|401 nodes: relative closure −3.17e−10; depression error 3.28e−10; bin-shape L1/D 4.76e−7|Compatible plane-parallel prescribed-field limit, not general spherical validation|
|Current-develop stellar regression|8 frozen m167 jobs; 184 saved arrays exactly equal; 736 abundance checks; strict ray closure passes|Port preservation for tested inputs, not independent physical validation|
|Historical atmospheric-depth refinement|OH fine-density L1/D 1.90444%; Si 4.57403%|Si fails the declared 2% distribution criterion; closure does not remove this limitation|
|Turbospectrum comparison|Similar approximate OH/FeH/atomic weighting with overlap; source/EOS and opacity differences remain|Not identical physics; do not tune peaks or claim universal ordering|

The analytical target for B=B0+B1*tau0 and constant eta is

\[
C(\log\tau_0)=2\pi\ln(10)\tau_0\eta B_1 E_3[(1+\eta)\tau_0].
\]

It is compared using its compatible flux/coordinate/boundary assumptions. The benchmark implementation is independent of the Turbospectrum numerical kernels. Existing Radau/PCHIP reconstruction is a secondary reference, not part of this native patch.

Local supporting reports are indexed in the review-package README outside this repository; science inputs need not be redistributed with the code. Stellar audit results retain the native boundary/source conventions and full-feature catalogues. The m167 peak tie between one FeH feature and Fe I rules out describing the evidence as strictly separated species shells.

## 11. Requested review and remaining integration work

1. Confirm native source interpretation and the scope in which L is an LTE absorption-driving term.
2. Review the pointwise definition of N and whether exposing both Q and N is appropriate.
3. Review duplicate geometry, turning-chord approximation, fold indices and outer-interval/grazing convention.
4. Agree on API names, supported headers/exports/build integration and test-only isolation of the copied reference recurrence.
5. Add C-ABI allocation-exception handling and assess platform symbol lookup (Linux tested only).
6. Preserve process-wide native-state locking; thread-local traces do not make the solver thread-safe.
7. Keep distribution convergence separate from flux closure and port regression.

No claim of fully self-consistent line scattering, universal atmospheric-depth convergence, or integration-ready cross-platform API is made.
