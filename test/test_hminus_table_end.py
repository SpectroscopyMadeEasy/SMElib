"""H- bound-free opacity in the last interval of its table (1630.00-1643.91 nm).

MAP1 must use only the backward parabola there; there is no point to the right
for a forward one. The check isolates the bound-free part, because the value
that an out-of-bounds read produces depends on the build and need not be NaN.
"""

from os.path import dirname, join

import numpy as np

from pymodule.smelib import SME_DLL, libfile as smelib_libfile
from test_call import get_abund, get_atmo, get_linelist

DATADIR = join(dirname(__file__), "../share/libsme/")

# Last three points of the table in HMINOP: wavelength (nm), cross section
TABLE_END = np.array([[1620.0, 0.4974], [1630.0, 0.1989], [1643.91, 0.0]])
THRESHOLD = 16439.1  # vacuum A; above it only H- free-free is left


def test_hminus_bound_free_in_last_table_interval():
    dll = SME_DLL(smelib_libfile, DATADIR)
    dll.SetLibraryPath(DATADIR)
    # The continuum takes wavelengths as vacuum unless the medium is "air".
    # A medium cannot be unset again, so only change it if it is "air".
    was_air = dll.GetWavelengthMedium() == "air"
    if was_air:
        dll.SetWavelengthMedium("vac")
    dll.SetContinuumOpacityGrid("exact")
    try:
        dll.InputLineList(get_linelist())
        dll.InputModel(5770, 4.44, 0.7, get_atmo())
        abund = get_abund()
        dll.InputAbund(lambda *_, **__: abund)
        dll.Ionization(0)
        dll.InputWaveRange(16240.0, 16500.0)
        dll.Opacity()

        def hminus(wave):
            dll.GetContinuumOpacityComponents(wave)
            return np.array(dll.GetOpacity("AHMIN", species="", key=""), dtype=float)

        # Free-free is smooth: fit it above the threshold and extrapolate down.
        red = np.array([16441.0, 16465.0, 16490.0])
        red_values = np.array([hminus(w) for w in red])
        coeff = np.polyfit(red - THRESHOLD, red_values, 2)

        waves = np.array([16250.0, 16300.0, 16320.0, 16350.0, 16380.0, 16410.0, 16430.0])
        total = np.array([hminus(w) for w in waves])
    finally:
        if was_air:
            dll.SetWavelengthMedium("air")

    assert np.all(np.isfinite(total))
    assert np.all(total > 0)

    free_free = np.array(
        [np.polyval(coeff, w - THRESHOLD) for w in waves]
    )
    bound_free = total - free_free

    # 16250 A lies in the interval before the last one and 16300 A is a table
    # point; neither depends on the end-of-table branch. Their ratio checks
    # that the bound-free part has been isolated correctly. The stimulated
    # emission factor changes by less than 1 % across this range.
    anchor = bound_free[1]
    assert np.all(anchor > 0)
    np.testing.assert_allclose(bound_free[0] / anchor, 0.3364 / 0.1989, rtol=0.02)

    # Inside the last interval: the parabola through the last three points.
    parabola = np.polyfit(TABLE_END[:, 0], TABLE_END[:, 1], 2)
    for i, wave in enumerate(waves[2:], start=2):
        expected = np.polyval(parabola, wave / 10.0) / 0.1989
        np.testing.assert_allclose(
            bound_free[i] / anchor,
            expected,
            rtol=0.02,
            atol=0.003,
            err_msg=f"H- bound-free at {wave} A",
        )
