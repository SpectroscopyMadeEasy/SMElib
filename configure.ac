# Metadata
AC_INIT([libsme], [6.03], [nikolai.piskunov@physics.uu.se])
AC_CANONICAL_TARGET

# Library version reported by SMELibraryVersion: the git tag of the source tree
# without the leading "v" (e.g. 6.13.21, or 6.13.21-3-gabc1234 after a release).
SMELIB_GIT_VERSION=`cd "$srcdir" && git -c safe.directory='*' describe --tags --always --dirty 2>/dev/null | sed 's/^v//'`
if test -z "$SMELIB_GIT_VERSION"; then
    SMELIB_GIT_VERSION=unknown
fi
AC_MSG_NOTICE([SMElib version: $SMELIB_GIT_VERSION])
AC_SUBST([SMELIB_GIT_VERSION])

# Mac trigger
AM_CONDITIONAL([MACOS], [case "$host_os" in *darwin*) true;; *) false;; esac])

# Use Automake
AM_INIT_AUTOMAKE([subdir-objects])
LT_INIT
AC_CONFIG_MACRO_DIRS([m4])

case $target_os in
    linux-gnu)
    target=linux 
    extension=.so
    outdir=libdir
    ;;
    darwin*)
    target=darwin
    extension=.dylib
    outdir=libdir
    ;;
    win32|mingw32)
    target=win32
    extension=-5.dll
    outdir=bindir
    ;;
    *) 
    target=$target_os
    extension=.so
    outdir=libdir
    ;;
esac

AC_SUBST(TARGET_CPU, $target_cpu)
AC_SUBST(TARGET, $target)
AC_SUBST(EXTENSION, $extension)
AC_SUBST(OUTPUT_DIR, $outdir)

# Find Dependecies
AC_PROG_CXX
AC_PROG_F77

# Create Makefile from Makefile.in
AC_CONFIG_FILES([Makefile])

# Create Output files
AC_OUTPUT
