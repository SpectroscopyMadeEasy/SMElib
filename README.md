[![make](https://github.com/SpectroscopyMadeEasy/SMElib/actions/workflows/make.yml/badge.svg?branch=master)](https://github.com/SpectroscopyMadeEasy/SMElib/actions/workflows/make.yml)

# SMElib

The C and Fortran spectral-synthesis library used by [PySME](https://github.com/SpectroscopyMadeEasy/PySME).

Important version notes:

- Versions older than v6.0.7 have less accurate hydrogen-line wings because of an earlier EOS error.
- macOS x86/Intel release binaries are not provided from v6.13.13 onward.

Users of versions older than v6.0.7 should update.

The classic IDL version of SME is available from [STScI](http://www.stsci.edu/~valenti/sme.html).
SME was introduced by [Valenti & Piskunov (1996)](https://ui.adsabs.harvard.edu/abs/1996A%26AS..118..595V).

## Documentation

- [Versions and branches](docs/versioning_and_branches.md)
- [Testing](test/README.md)
- [Brackett Stark-profile convolution](docs/brackett_stark_convolution.md)
- [Continuum scattering source](docs/continuum_scattering_source.md)
- [Changelog](CHANGELOG.md)

## Download

Compiled libraries for Linux and macOS are attached to [GitHub Releases](https://github.com/SpectroscopyMadeEasy/SMElib/releases).
Depending on the platform, `libgfortran` may also be required.

## CI and releases

- `develop` contains integration work for the next release.
- `master` is the release branch.
- Precompiled artifacts are published only for tags matching `v*`.

See [Versions and branches](docs/versioning_and_branches.md) for the version scheme and branch roles.

## Data files

SMElib requires the files installed in `share/libsme`.
Set their location with `SetLibraryPath`, inspect it with `GetLibraryPath`, and list the required files with `GetDataFiles`.

## Build

Building from source requires C++, Fortran, Autoconf, Automake, and Libtool.

```bash
git clone https://github.com/SpectroscopyMadeEasy/SMElib.git
cd SMElib
./bootstrap
./configure --prefix="$PWD"
make install
```

The library is installed in `lib`; its data files are installed in `share/libsme`.

If the linker cannot find `libgfortran`, locate it with the compiler and add its directory to `LDFLAGS`.
Compiler selection can be set explicitly with `CXX` and `F77`.

On macOS, a moved `.dylib` may require its install name to be updated with `install_name_tool`.
