# Changelog

## Unreleased

## [v6.13.23] - 2026-11-26

Hydrogen lines: optional blending of the Balmer profiles H10-H22 from Stehle
& Hutcheon to Tremblay & Bergeron (2009). Default results are unchanged: the
new option is off by default.

### Added
- `SetHydrogenTB09(mode, dlo, dhi, path)` and `GetHydrogenTB09Mode()`:
  optional blending of the Balmer profiles H10-H22 from Stehle & Hutcheon
  (1999) with those of Tremblay & Bergeron (2009, ApJ 696, 1755), which
  include the non-ideal (Hummer & Mihalas critical field) cut of the proton
  microfield and are computed 0.5-1.5 dex beyond Stehle's last density (the
  Inglis-Teller limit). The TB09 weight rises as 3t^2 - 2t^3 from `dlo` dex
  below each line's last tabulated Stehle density to `dhi` dex below it
  (defaults 2.0 and 1.5, the values that fitted H10-H22 in metal-poor dwarfs
  and DESI turnoff stars best). The TB09 table is read as distributed with
  SYNSPEC (`data/tremblay.dat`, unchanged); it is not distributed with
  SMElib: download it with the TLUSTY 208 / SYNSPEC 54 package
  (https://www.as.arizona.edu/~hubeny/tlusty208-package/tl208-s54.tar.gz,
  `data/tremblay.dat`) or from P.-E. Tremblay's model grids
  (https://warwick.ac.uk/fac/sci/physics/research/astro/people/tremblay/modelgrids/),
  cite Tremblay & Bergeron (2009), and pass its path (default
  `<data directory>/tremblay.dat`). A missing table, a file in another
  format or an invalid window is returned as an error. Meant to be used with the
  charged-perturber occupation probability (`SetHydrogenOccupation`).
- External hlinop: the blending (`HLINOP_SET_TB09`), which reads
  `tremblay.dat` directly, and its tests (submodule update).

## [v6.13.22] - 2026-11-25

Hydrogen lines. Results on the default path change for hydrogen lines, through
the new line profiles: in the solar model of the tests, Balmer H alpha - H10
and Paschen 7 change by less than 1% in flux and equivalent width, while lines
without Stehle tables (Brackett, Balmer n_up > 30) change much more (the
equivalent width of Br11 halves; the earlier profiles of these lines had
areas of 1.7-2.1). `SetHydrogenProfileMode(0)` restores the earlier profiles.
The line-range fix for hydrogen lines changes default spectra by at most
7e-4 in normalized flux in the tests. Two new options are off by default and
leave default results unchanged: occupation probabilities of H I levels
(`SetHydrogenOccupation`) and the wavelength medium (`SetWavelengthMedium`).
The hydrogen-line code is now the git submodule `external/hlinop`: clone with
`--recursive` or run `git submodule update --init`.

### Changed
- Hydrogen line profiles now come from Paul Barklem's HLINOP/HLINPROF code
  as a git submodule, `external/hlinop` (MingjieJian/hlinop, develop), instead
  of copies in `src/sme`. The broadening mechanisms are convolved instead of
  added: for HLINOP lines (no Stehle table) the Stark profile had areas of
  1.7-2.1 and now agrees with Stehle & Hutcheon and Lemke (VCS, Brackett) to
  2-5% in half width and peak; the Stehle profiles are convolved with
  microturbulence and with the radiative, self and helium Lorentz profiles,
  are interpolated with a monotone cubic, are scaled quasistatically above
  each line's last tabulated density (they were kept at that density), and
  the table covers Lyman, Balmer and Paschen lines to n_up = 30 (Lyman alpha
  included). See `external/hlinop/history.txt` for the changes and tests.
- New table file `stehle_long.dat` (format version 2, built from CDS
  J/A+AS/140/93) replaces `stehle_long.dat.INTEL`; `src/data/stehle_long.dat`
  links to the file in the submodule.
- The line-range scan of hydrogen lines (how far from the centre a line is
  computed, and where the adaptive grid stops following it) uses the largest
  line/continuum ratio over depth, as for the other lines. It used the ratio
  in the deepest layer, which need not be the largest, so lines could be cut
  where they still matter in higher layers. This has been so since SME
  version 574 (before, hydrogen lines were never cut). Over 3659-3681.8 A
  with 98 H and 3297 other lines, default spectra change by at most 7e-4 in
  normalized flux for HD 84937 (6275 K dwarf) and not at all for the giants
  HD 122563 and CS 22949-037 or for the solar test model's H alpha - H10,
  Pa 7 and Br 11.
- Lines outside the Stehle tables go directly to HLINOP (before, the VCS
  Balmer table was tried first). The HLINOP fallback warnings now also list
  lines that fall back because the temperature is outside the table.
- The environment variable `PYSME_H_STARK_CONVOLUTION` (opt-in Stark
  convolution for Brackett lines) is no longer used: all HLINOP lines use the
  convolved Stark profile.
- The hydrogen profile caches are emptied when a new model is read
  (`InputModel`); within a model they are reused across wavelengths and
  segments.
- `SMELibraryVersion` reports the version from the git tag at build time,
  e.g. `SME Library version: 6.13.22, <platform>`, or `6.13.22-3-gabc1234`
  for a build three commits after the release, instead of the fixed
  `6.13, June 2025`. Builds without git information report `unknown`.
  The CI checkouts now fetch the full history so that tags are available.
- `test_stehle_nalpha.py`: the two checks of the padding rows in the old
  table file were removed with that file; the profile check is unchanged.
  A top-level `pytest.ini` restricts the test run to `test/` (the submodule
  has its own suite).

### Added
- `SetHydrogenProfileMode(mode)` and `GetHydrogenProfileMode()`: 1 = convolved
  hydrogen line profiles (default), 0 = the earlier profiles.
- Occupation probabilities of H I levels (Hummer & Mihalas 1988, charged
  perturbers as in Hubeny, Hummer & Lanz 1994), off by default:
  `SetHydrogenOccupation(mode, neutral_scale)` and
  `GetHydrogenOccupationMode()`. With mode 1, hydrogen line opacities are
  multiplied by w(n_up) U/Z (populations with w), tabulated profiles are cut
  at the series limit, and the dissolved-level (pseudo-continuum) absorption
  below the bound-free edges of n = 1-8 is added to Kurucz's HOP, in LTE as
  HOP and at HOP's edges, so that nothing is counted twice. `neutral_scale`
  scales the Hummer & Mihalas neutral-perturber term (0 = off, the default).
  The physics is in external/hlinop (hbop.f: HBOP_LEVELS, HBOP_BF_DISSOLVED).
  Checked against the analysis code of the hydrogen-line study (HD 84937,
  3660.8-3680 A): with that code's profiles above each line's last tabulated
  Stehle density, the R, N and I spectra are reproduced to a median of 1e-4
  to 3e-4 in normalized flux.
- `SetWavelengthMedium("air"|"vac")` and `GetWavelengthMedium()`: the medium
  of the wavelengths given to SMElib (air above 2000 A as VALD, or vacuum).
  When it is set, the continuous opacities take wavelengths in that medium
  (bound-free edges, e.g. the Balmer edge, at their true positions; with air
  wavelengths they were 1 A too red at the Balmer limit and about 2 A at the
  Paschen limit), and so do the series limits, cuts and dissolved levels of
  the hydrogen-line code (HLINOP_SET_MEDIUM). If it is not called, the
  earlier behaviour is kept (continuum as vacuum, hydrogen lines as air
  above 2000 A). The same lines and grid in air and in vacuum give the same
  spectrum to 1.4e-4 in normalized flux.
- Tests: `test/test_hydrogen_lines.py` (both profile modes, HLINOP fallback
  warnings, no Fortran table messages on stdout),
  `test/test_hydrogen_line_range.py`, `test/test_hydrogen_occupation.py`,
  `test/test_wavelength_medium.py`.

### Maintenance
- After a successful release, the build workflow opens a pull request that
  merges `master` back into `develop`, labelled `ignore-for-release`.

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
