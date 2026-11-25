"""Hydrogen lines with the profiles of external/hlinop (HLINPROF, HLINOP)."""

import numpy as np
import pytest

from pymodule.smelib import SME_DLL, libfile as smelib_libfile
from test_call import get_abund, get_atmo
from os.path import dirname, join

DATADIR = join(dirname(__file__), "../share/libsme/")


def _hline(wave, excit, gflog, nlo, nup):
    # for hydrogen lines GAMQST and GAMVW hold the principal quantum numbers
    return {"species": np.array(["H 1"]),
            "atomic": np.array([[1.0, 1.0, wave, excit, gflog, 8.0, float(nlo), float(nup)]])}


def _synth(linelist, wfirst, wlast, mode=None):
    dll = SME_DLL(smelib_libfile, DATADIR)
    dll.SetLibraryPath(DATADIR)
    if mode is not None:
        dll.SetHydrogenProfileMode(mode)
    dll.SetHlinopWarningMode(1)  # record only
    dll.InputLineList(linelist)
    dll.InputModel(5770, 4.44, 0.7, get_atmo())
    dll.InputAbund(lambda *_, **__: get_abund())
    dll.Ionization(0)
    dll.InputWaveRange(wfirst, wlast)
    dll.Opacity()
    _, wint, sint, cint = dll.Transf([1], wave=np.linspace(wfirst, wlast, 201))
    return dll, np.asarray(wint), np.asarray(sint)[0] / np.asarray(cint)[0]


H_BETA = _hline(4861.323, 10.199, -0.020, 2, 4)


def test_balmer_line_in_both_profile_modes():
    """H beta is synthesised with the convolved profiles (default) and the earlier ones
    (SetHydrogenProfileMode(0)); both are finite absorption lines, and they differ."""
    dll, w, f1 = _synth(H_BETA, 4840.0, 4882.0)
    assert dll.GetHydrogenProfileMode() == 1
    _, _, f0 = _synth(H_BETA, 4840.0, 4882.0, mode=0)
    for f in (f1, f0):
        assert np.all(np.isfinite(f)) and np.all(f > 0) and np.all(f <= 1.0 + 1e-6)
        assert f[np.argmin(np.abs(w - 4861.323))] < 0.9
    assert np.max(np.abs(f1 - f0)) > 1e-4
    with pytest.raises(RuntimeError):
        dll.SetHydrogenProfileMode(2)
    dll.SetHydrogenProfileMode(1)


def test_lines_without_tables_are_reported(caplog):
    """Lines without a Stehle table (Brackett, Balmer n_up > 30) are computed with HLINOP and
    reported in the fallback warnings (logged by the wrapper after Transf); tabulated lines
    (Balmer to n_up = 30) are not."""
    with caplog.at_level("WARNING"):
        _, _, f = _synth(_hline(16806.52, 12.749, -0.65, 4, 11), 16795.0, 16818.0)
    assert np.all(np.isfinite(f)) and f.min() < 0.99
    assert "(4->11)" in caplog.text
    caplog.clear()
    with caplog.at_level("WARNING"):
        _synth(_hline(3659.4, 10.199, -2.3, 2, 35), 3655.0, 3664.0)
    assert "(2->35)" in caplog.text
    caplog.clear()
    with caplog.at_level("WARNING"):
        _synth(_hline(3662.26, 10.199, -2.0, 2, 30), 3655.0, 3670.0)
    assert "fell back" not in caplog.text


def test_no_table_messages_on_stdout(capfd):
    """SMElib reports fallbacks itself; the Fortran's table messages are switched off."""
    _synth(H_BETA, 4855.0, 4868.0)
    out = capfd.readouterr().out
    assert "Will use Stehle" not in out and "Using Hlinop" not in out
