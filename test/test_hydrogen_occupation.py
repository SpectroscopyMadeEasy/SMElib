"""Occupation probabilities of H I levels (SetHydrogenOccupation, external/hlinop hbop.f)."""

import logging
from os.path import dirname, join

import numpy as np
import pytest

from pymodule.smelib import SME_DLL, libfile as smelib_libfile
from test_call import get_abund, get_atmo

DATADIR = join(dirname(__file__), "../share/libsme/")


def _balmer(nup, loggf):
    # air wavelength of H(2-nup) from the level energies of hlinop.f
    e = {3: 97492.302, 4: 102823.893}.get(nup, 109678.764 - 109677.576 / nup ** 2)
    wv = 1e8 / (e - 82259.105)
    s2 = (1e4 / wv) ** 2
    wa = wv / (1 + 0.0000834254 + 0.02406147 / (130 - s2) + 0.00015998 / (38.9 - s2))
    return [1.0, 1.0, wa, 10.199, loggf, 8.0, 2.0, float(nup)]


def _run(mode, lines, w1, w2, probe=(), synth=True, scale=0.0):
    dll = SME_DLL(smelib_libfile, DATADIR)
    dll.SetLibraryPath(DATADIR)
    dll.SetHydrogenOccupation(mode, scale)
    dll.InputLineList({"species": np.array(["H 1"] * len(lines)), "atomic": np.array(lines, float)})
    dll.InputModel(5770, 4.44, 0.7, get_atmo())
    dll.InputAbund(lambda *_, **__: get_abund())
    dll.Ionization(0)
    dll.InputWaveRange(w1, w2)
    dll.Opacity()
    out = {}
    if synth:
        w = np.linspace(w1, w2, 401)
        _, _, sint, cint = dll.Transf([1], wave=w)
        out["wave"], out["flux"] = w, np.asarray(sint)[0] / np.asarray(cint)[0]
    for x in probe:
        lop, cop, *_ = dll.GetLineOpacity(x)
        out[x] = (np.asarray(lop).copy(), np.asarray(cop).copy())
    return dll, out


H_BETA = _balmer(4, -0.020)
H22 = _balmer(22, -2.70)


def test_off_by_default():
    dll = SME_DLL(smelib_libfile, DATADIR)
    assert dll.GetHydrogenOccupationMode() == 0
    with pytest.raises(RuntimeError):
        dll.SetHydrogenOccupation(2)
    with pytest.raises(RuntimeError):
        dll.SetHydrogenOccupation(1, -1.0)


def test_dissolved_continuum_is_smooth_at_the_balmer_edge():
    """Off: the continuum drops at the n = 2 edge of HOP (3647.05 A on SMElib's wavelength scale).
    On: the dissolved-level absorption continues it redward (no jump, nothing counted twice), and
    blueward of the edge nothing changes."""
    probe = (3640.0, 3647.0, 3647.1, 3700.0)
    _, off = _run(0, [H_BETA], 3600, 4900, probe, synth=False)
    _, on = _run(1, [H_BETA], 3600, 4900, probe, synth=False)
    deep = 40
    assert off[3647.1][1][deep] / off[3647.0][1][deep] < 0.8             # the Balmer jump
    assert abs(on[3647.1][1][deep] / on[3647.0][1][deep] - 1) < 0.01     # continuous with occupation
    np.testing.assert_allclose(on[3640.0][1], off[3640.0][1], rtol=1e-6)
    assert np.all(on[3700.0][1] >= off[3700.0][1])
    assert on[3700.0][1][deep] > 1.05 * off[3700.0][1][deep]


def test_line_opacity_and_line_range():
    """Line opacity is multiplied by w(n_up): about unchanged in the upper layers, much smaller in
    the deep ones for H22.  The line range is not cut at the core (it was, when the range scan used
    the deepest layer only), so the wings 1 A out keep their opacity."""
    probe = (H22[2], H22[2] + 1.0)
    _, off = _run(0, [H22], H22[2] - 6, H22[2] + 6, probe)
    _, on = _run(1, [H22], H22[2] - 6, H22[2] + 6, probe)
    r = on[H22[2]][0] / off[H22[2]][0]
    assert 0.9 < r[10] <= 1.0 and r[-1] < 1e-2
    wing_on, wing_off = on[H22[2] + 1.0][0], off[H22[2] + 1.0][0]
    assert wing_on[20] > 0.5 * wing_off[20]
    assert np.all(np.isfinite(on["flux"])) and on["flux"].min() > off["flux"].min()


def test_balmer_beta_nearly_unchanged():
    _, off = _run(0, [H_BETA], 4840, 4882)
    _, on = _run(1, [H_BETA], 4840, 4882)
    ew = lambda o: np.trapezoid(1 - o["flux"], o["wave"]) if hasattr(np, "trapezoid") else np.trapz(1 - o["flux"], o["wave"])
    assert abs(ew(on) / ew(off) - 1) < 0.01


def test_switching_off_restores_the_default(caplog):
    """Mode 0 after mode 1 gives the default spectrum bit for bit."""
    _, ref = _run(0, [H22, H_BETA], 3660, 3690)
    _run(1, [H22, H_BETA], 3660, 3690)
    _, again = _run(0, [H22, H_BETA], 3660, 3690)
    np.testing.assert_array_equal(ref["flux"], again["flux"])
