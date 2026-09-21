# Changelog

## Unreleased

### Added
- Add `SelectStrongLinesByBins`, a native cumulative wavelength-bin selector
  shared by PySME's CDR and binned-ALMAX workflows.

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
