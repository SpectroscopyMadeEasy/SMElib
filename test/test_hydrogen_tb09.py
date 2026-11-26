"""Stehle -> TB09 blending of the Balmer profiles H10-H22 (SetHydrogenTB09; external/hlinop HLINOP_SET_TB09).

The TB09 table (SYNSPEC's data/tremblay.dat) is not distributed with SMElib, so the tests use a synthetic table
in the same format. They check: off by default; argument, file and format errors are returned
as errors (the library does not stop); with the blending on, lines of the TB09 table change and others do not;
switching it off again restores the spectrum exactly (the profile caches are emptied)."""

from os.path import dirname, join

import numpy as np
import pytest

from pymodule.smelib import SME_DLL, libfile as smelib_libfile
from test_call import get_abund, get_atmo

DATADIR = join(dirname(__file__), "../share/libsme/")
RH = 109677.576


def balmer_air(n):
    vac = 1e8 / (109678.764 - RH / n ** 2 - 82259.105)
    s = (1e8 / vac) ** 2
    return vac / (1.0000834213 + 2406030.0 / (1.30e10 - s) + 15997.0 / (3.89e9 - s))


def write_tb09(path, nups, la0=-3.0, dla=0.1, mp=55):
    """Synthetic TB09 table in SYNSPEC's tremblay.dat (Lemke) format, Balmer lines nups, one block."""
    la = la0 + dla * np.arange(mp)
    s = np.exp(-(10 ** la / 0.5) ** 2) + 0.05 * (1.0 + 10 ** la) ** -2.5      # narrower than Stehle
    vals = [f"{0.0:8.4f}"] + [f"{v:8.4f}" for v in np.log10(s)]
    rec = ["".join(vals[i:i + 9]) for i in range(0, len(vals), 9)]
    out = [f"{1:6d}", f"{len(nups):12d}"]
    for nup in nups:
        out += [f"{2:12d}{nup:12d}{la0:24.15f}{10.0:24.15f}", f"{np.log10(2500.0):24.15f}{dla:24.15f}{0.5:24.15f}",
                f"{np.log10(2.0):24.15f}{mp:16d}{17:12d}{7:12d}"]
    for nup in nups:
        out.append(f"nl= 2 nu={nup:2d}")
        out += rec * (17 * 7)
    path.write_text("\n".join(out) + "\n")


@pytest.fixture(scope="module")
def table(tmp_path_factory):
    path = tmp_path_factory.mktemp("tb09") / "tremblay_synthetic.dat"
    write_tb09(path, range(10, 23))
    return str(path)


NUPS = (8, 18)


def _spectrum(dll, setup):
    dll.SetLibraryPath(DATADIR)
    setup(dll)
    lines = [[1.0, 1.0, balmer_air(n), 10.199, np.log10(48.0 / n ** 3), 8.0, 2.0, float(n)] for n in sorted(NUPS, key=balmer_air)]
    dll.InputLineList({"species": np.array(["H 1"] * len(lines)), "atomic": np.array(lines)})
    dll.InputModel(5770, 4.44, 0.7, get_atmo())
    dll.InputAbund(lambda *_, **__: get_abund())
    dll.Ionization(0)
    grid = {n: balmer_air(n) + np.linspace(-1.5, 1.5, 61) for n in NUPS}
    w = np.concatenate([grid[n] for n in NUPS])
    dll.InputWaveRange(w.min() - 2, w.max() + 2)
    dll.Opacity()
    _, _, s, c = dll.Transf([1], wave=np.sort(w))
    spec = np.asarray(s)[0] / np.asarray(c)[0]
    ws = np.sort(w)
    return {n: np.interp(grid[n], ws, spec) for n in NUPS}


def test_off_by_default_and_errors_are_returned(tmp_path):
    dll = SME_DLL(smelib_libfile, DATADIR)
    assert dll.GetHydrogenTB09Mode() == 0
    with pytest.raises(RuntimeError, match="not found"):
        dll.SetHydrogenTB09(1, 2.0, 1.5, str(tmp_path / "missing.dat"))
    with pytest.raises(RuntimeError, match="DLO > DHI"):
        dll.SetHydrogenTB09(1, 1.0, 1.5, str(tmp_path / "missing.dat"))
    with pytest.raises(RuntimeError, match="mode"):
        dll.SetHydrogenTB09(2)
    other = tmp_path / "compact.dat"
    other.write_text("13\n2 10 55 17 7 -3 0.1 10 0.5 3.4 0.3\n")
    with pytest.raises(RuntimeError, match="tremblay.dat format"):
        dll.SetHydrogenTB09(1, 2.0, 1.5, str(other))
    assert dll.GetHydrogenTB09Mode() == 0


def test_blending_changes_only_the_tb09_lines_and_is_undone(table):
    dll = SME_DLL(smelib_libfile, DATADIR)
    off = _spectrum(dll, lambda d: d.SetHydrogenTB09(0))
    on = _spectrum(dll, lambda d: d.SetHydrogenTB09(1, 2.0, 1.5, table))
    assert dll.GetHydrogenTB09Mode() == 1
    back = _spectrum(dll, lambda d: d.SetHydrogenTB09(0))
    assert np.max(np.abs(on[18] - off[18])) > 1e-3          # H18 is in the TB09 table
    np.testing.assert_allclose(on[8], off[8], rtol=0, atol=1e-5)   # H8 is not (only H18's far wing reaches it)
    np.testing.assert_array_equal(back[18], off[18])        # caches emptied when switched back
