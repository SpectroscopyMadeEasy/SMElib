"""Regression check for the Stehle profiles that had zero-padded detuning rows.

The table is now external/hlinop/stehle_long.dat, built from the CDS catalogue
without padding rows (the old stehle_long.dat.INTEL is no longer distributed, so
the checks of its padding rows were removed); hlinprof.f still trims any padding
when it reads a table.  The profile check below exercises the built library.
"""

from __future__ import annotations

from pathlib import Path

from pymodule.smelib import libfile as smelib_libfile
from stehle_profile_diagnostic import measure_profiles


def test_target_profile_integrals_are_near_unity():
    """Exercise the built library so the test fails without the Fortran fix."""

    data = Path(__file__).parents[1] / "share" / "libsme"
    rows = measure_profiles(Path(smelib_libfile), data)
    assert {row[0] for row in rows} == {22, 26, 27, 30}
    for upper, _temperature, _log_ne, area, peak in rows:
        assert 0.94 < area < 1.02, f"H{upper} area={area}"
        assert peak < 10.0, f"H{upper} peak={peak}"
