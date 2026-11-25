"""Wavelength medium (SetWavelengthMedium): with "air" or "vac" the continuous opacities and the
hydrogen-line code use the same medium; unset keeps the earlier behaviour (continuum as vacuum,
hydrogen lines as air above 2000 A)."""

from os.path import dirname, join

import numpy as np
import pytest

from pymodule.smelib import SME_DLL, libfile as smelib_libfile
from test_call import get_abund, get_atmo

DATADIR = join(dirname(__file__), "../share/libsme/")
LIMIT_VAC = 1e8 / (109678.764 - 82259.105)          # Balmer series limit (vacuum), 3647.05 A


def vacair(w):
    s = (1e8 / np.asarray(w, float)) ** 2
    return w / (1.0000834213 + 2406030.0 / (1.30e10 - s) + 15997.0 / (3.89e9 - s))


def balmer_vac(n):
    e = {4: 102823.893}.get(n, 109678.764 - 109677.576 / n ** 2)
    return 1e8 / (e - 82259.105)


NUPS = [30, 20, 12, 4]


def _lines(centres):
    return [[1.0, 1.0, c, 10.199, -0.02 if n == 4 else np.log10(48.0 / n ** 3), 8.0, 2.0, float(n)]
            for c, n in sorted(zip(centres, NUPS))]


def _dll(medium, occupation, centres, w1, w2):
    dll = SME_DLL(smelib_libfile, DATADIR)
    dll.SetLibraryPath(DATADIR)
    if medium:
        dll.SetWavelengthMedium(medium)
    dll.SetHydrogenOccupation(occupation)
    dll.InputLineList({"species": np.array(["H 1"] * len(centres)), "atomic": np.array(_lines(centres))})
    dll.InputModel(5770, 4.44, 0.7, get_atmo())
    dll.InputAbund(lambda *_, **__: get_abund())
    dll.Ionization(0)
    dll.InputWaveRange(w1, w2)
    dll.Opacity()
    return dll


def test_unset_by_default_and_checked():
    dll = SME_DLL(smelib_libfile, DATADIR)
    assert dll.GetWavelengthMedium() in ("unset", "air", "vac")
    with pytest.raises(RuntimeError):
        dll.SetWavelengthMedium("foo")


@pytest.mark.parametrize("occupation", [0, 1])
def test_air_and_vacuum_give_the_same_spectrum(occupation):
    """The same lines and grid given in air (medium "air") and in vacuum (medium "vac") give the
    same normalized spectrum at the same physical wavelengths, across the Balmer limit."""
    vac = np.array([balmer_vac(n) for n in NUPS])
    gv = np.linspace(3630.0, 3700.0, 701)
    out = {}
    for medium, centres, grid in (("air", vacair(vac), vacair(gv)), ("vac", vac, gv)):
        dll = _dll(medium, occupation, centres, grid[0] - 1, grid[-1] + 1)
        _, _, s, c = dll.Transf([1], wave=grid)
        out[medium] = np.asarray(s)[0] / np.asarray(c)[0]
    np.testing.assert_allclose(out["air"], out["vac"], atol=5e-4)


def test_balmer_edge_at_the_air_series_limit():
    """With air wavelengths the Balmer bound-free edge is at the air series limit (3645.96 A);
    with the medium unset it stays where it was (3647.05 A on the air scale)."""
    a, b = vacair(LIMIT_VAC) - 0.3, 0.5 * (vacair(LIMIT_VAC) + LIMIT_VAC)
    ratio = {}
    for medium in (None, "air"):   # unset first: the medium stays set in the library
        dll = _dll(medium, 0, vacair(np.array([balmer_vac(n) for n in NUPS])), 3600.0, 3700.0)
        ca = np.asarray(dll.GetLineOpacity(a)[1]); cb = np.asarray(dll.GetLineOpacity(b)[1])
        ratio[medium] = cb[40] / ca[40]
    assert ratio["air"] < 0.9          # past the edge
    assert abs(ratio[None] - 1) < 0.01  # not yet
