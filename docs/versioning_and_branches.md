# Versions and branches

SMElib has a core version and a release tag.
The core version, such as `6.13`, identifies the library generation.
Release tags add a patch number, such as `v6.13.18`, for build, packaging, integration, and compatible maintenance updates on that core version.

PySME pins an exact SMElib release.
Reproducing a PySME result therefore does not depend on whichever SMElib tag happens to be newest.

## Branches

- `develop` contains integration work intended for a future release.
- `master` contains released or release-ready code.
- Release tags are created from `master` after its build and tests pass.

Tags are immutable.
Changes after a release use a new patch number.
