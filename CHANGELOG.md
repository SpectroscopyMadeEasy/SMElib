# Changelog

## Unreleased

### Changed
- `SMELibraryVersion` reports the full release number, e.g.
  `SME Library version: 6.13.21, <platform>`, instead of the fixed
  `6.13, June 2025`. The number is set in `src/sme/sme_synth_faster.cpp`
  and is updated with each release.

## [v6.13.21] - 2026-11-20

Results on the default path change for hydrogen lines with Stehle profiles
(H8-H30; narrow spikes removed, largest changes in H22, H26, H27 and H30) and
for lines whose STARK1 constants were reused from the cache. Continuum-
scattering mode 1 is deprecated; use mode 2.

### Fixed
- Trim Stehle hydrogen profiles when the detuning array reaches its zero
  padding, even if the corresponding profile sample is nonzero. This removes
  narrow high-n spikes produced by zero-detuning interpolation. The malformed
  padding occurs in some table rows of every H8-H30 transition, so those
  profiles change; the largest changes are in H22, H26, H27 and H30.
  H3-H7 are unchanged.
- Include the line-center wavelength in the STARK1 cache key. Previously,
  calls with the same lower/upper level numbers but different line centers
  could reuse stale wavelength-dependent constants, so results depended on
  call order. Add a compiled Fortran cold/warm-cache regression.

### Added
- Add opt-in continuum-scattering source mode 2. It solves the continuum and
  line-plus-continuum radiation fields separately, treating LTE line opacity as
  true absorption. Plane-parallel models use a six-angle Feautrier solve and
  spherical models use the existing spherical moment solver; modes 0 and 1 and
  the default Planck path are unchanged.

### Deprecated
- Deprecate continuum-scattering source mode 1. Its continuum-only mean
  intensity can strongly overfill line cores and wings where scattering is
  important; selecting it now emits a warning once per process. Use mode 2.
  Mode 1 will be removed in a future release. The numerical paths and
  default mode 0 are unchanged.

### Documentation
- Add a contributing guide and a pull-request template. Pull requests opened
  against `master` are retargeted to `develop` automatically.

### Maintenance
- Refresh the GitHub Actions workflows; upload release artifacts only for
  tags; allow pull requests from `develop` in the build workflow.
- Add pull-request automation: labels from branch names, a `tests-modified`
  label for changes to existing tests, and release-note categories.

## [v6.13.20] - 2026-09-24

### Added
- Add `SelectStrongLinesByBins`, a native cumulative wavelength-bin selector
  shared by PySME's CDR and binned-ALMAX workflows.
- Add exact, fixed, and adaptive continuum-opacity grid modes. The adaptive
  mode caches every opacity-source component, protects known physical edges,
  and refines intervals using absorption/scattering/extinction error tests.
- Add generation-batched adaptive transfer for plane-parallel and spherical
  atmospheres. The optimized path uses immutable precomputed line masks and
  physical ranges to evaluate only lines that can contribute at each
  wavelength; the legacy adaptive implementation remains available as a
  reference and compatibility path.

### Changed
- Store the `LINEOP`, `AVOIGT`, and `VVOIGT` line-state caches in single
  precision while retaining double-precision profile and radiative-transfer
  arithmetic, halving their persistent storage requirement.

### Fixed
- Compute physical line-validity ranges during internal fixed-grid transfer
  instead of returning `InputLineList`'s initial `wlcent +/- 150 A` bounds.
- Evaluate spherical rays in a state-safe order so grazing-ray mirroring cannot
  contaminate subsequent normal rays or make the result depend on input
  `mu` ordering.

## [v6.13.19] - 2026-09-15

### Added
- Add an opt-in continuum scattering source for plane-parallel and spherical transfer while retaining the Planck-source treatment by default.
- Expose true absorption, coherent scattering, total continuum extinction, mean intensity, and continuum source through the SMElib API.

## [v6.13.18] - 2026-09-09

### Added
- Add an opt-in shared-support impact--quasistatic convolution for Brackett lines with upper level `m >= 10`; set `PYSME_H_STARK_CONVOLUTION=convolution` to enable it, while the unset/default path retains the legacy additive profile.
- Document the option in [Brackett Stark-profile convolution](docs/brackett_stark_convolution.md).
- Add structured reporting for HLINPROF-to-HLINOP fallbacks, preserving the warning interface already consumed by PySME v1.0.2.

## [v6.13.10] - 2025-08-16

### Added
- (make) update to new make.yml - 2
- (make) update to new make.yml

### Changed
- Merge pull request #4 from MingjieJian/develop
- (make) trigger GA for pull_request

## [v6.13.9] - 2025-08-16

- No user-visible changes recorded by Mingjie Jian.

## [6.13.8] - 2025-08-16

### Changed
- (make) trigger manylinux compile
- (make) modify for macos-13/15
- (sme_synth_faster.h) update it to 6.13 sme version
- (_smelib.cpp) update it to pysme version

## [6.13.7] - 2025-07-24

### Other
- ls lib/

## [6.13.6] - 2025-07-24

### Other
- (compile_smelib.sh) not copying dependnece libraries since we are now compile in each PC

## [6.13.5] - 2025-07-23

### Added
- (smelib) update the code to include libgfortran.so into lib/ for Linux

## [6.13.4] - 2025-07-22

- No user-visible changes recorded by Mingjie Jian.

## [6.13.2] - 2025-07-22

### Added
- (Makefile.am) add MACOS judge to avoid running the code for linux

## [6.13.1] - 2025-07-22

### Added
- create new compile file for Mac

### Changed
- Merge branch 'master' of github.com:MingjieJian/SMElib
- modify compile file for Mac
- Merge pull request #2 from MingjieJian/develop
- Merge pull request #1 from MingjieJian/develop

### Other
- (configure) specify GNU gcc etc

## [6.13.0] - 2025-07-11

### Added
- (cpp) renew the cpp file to fit NLTE central depth

### Changed
- update SMElib to SME version 6.13 (internal release)

### Fixed
- (sme_synth_faster) fix central depth bug

## [6.1.0] - 2025-06-04

### Added
- (indent) add indent to some commened lines
- cpp update in new branch
- cpp update in new branch
- cpp update in new branch
- cpp update in new branch
- cpp update in new branch
- renew eos 240614

### Changed
- update hlinop and hlinprof.f to version 6.11 (25.03.03)
- cpp update
- EOS update

### Fixed
- fix HVCSFILE length inside SVCS of hlinprof.d
- cpp update - correct line cdepth bug

## [v6.0.11] - 2025-08-16

### Other
- (make) upload to release - 4

## [v6.0.10] - 2025-08-16

### Changed
- (make) trigger manylinux compile - 11

### Other
- (make) upload to release - 4
- (make) upload to release - 3
- (make) upload to release - 1
- (make) upload to release - 2
- (make) upload to release - 1

## [v6.0.9] - 2025-08-15

- No user-visible changes recorded by Mingjie Jian.

## [v6.0.8] - 2025-08-15

### Changed
- (make) modify for macos-13/15 - 3

## [v6.0.7] - 2025-08-15

- Fixed the treatment of H2-, CH-, C2-, CN-, OH-, SiH-, HS- moleculars in eos.f, thus the H line wings are better.
