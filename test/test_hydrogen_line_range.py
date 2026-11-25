"""Line range of hydrogen lines: the scan that decides how far from the centre a line is computed
uses the largest line/continuum ratio over depth, as for the other lines.  It used the ratio in the
deepest layer, which need not be the largest, and then cut lines that still matter higher up."""

from os.path import dirname, join

import numpy as np

from pymodule.smelib import SME_DLL, libfile as smelib_libfile
from test_call import get_abund, get_atmo

DATADIR = join(dirname(__file__), "../share/libsme/")
ACCRT = 1e-4   # Transf default: the line/continuum threshold of the range scan
# H22 made 1000 times weaker (log gf -5.35 instead of -2.35): in the solar test model its line/continuum ratio 0.3 A from the
# centre is below ACCRT in the deepest layer but above it in layers further up
H22_WEAK = [1.0, 1.0, 3676.365, 10.199, -5.35, 8.0, 2.0, 22.0]


def test_hydrogen_line_range_uses_all_depths():
    dll = SME_DLL(smelib_libfile, DATADIR)
    dll.SetLibraryPath(DATADIR)
    dll.InputLineList({"species": np.array(["H 1"]), "atomic": np.array([H22_WEAK])})
    dll.InputModel(5770, 4.44, 0.7, get_atmo())
    dll.InputAbund(lambda *_, **__: get_abund())
    dll.Ionization(0)
    dll.InputWaveRange(3650.0, 3700.0)
    dll.Opacity()
    dll.Transf([1], wave=np.linspace(3650.0, 3700.0, 1001), accrt=ACCRT)
    left, right = np.asarray(dll.GetLineRange())[0]
    # the range reaches beyond the first scan step (0.3 A; it stopped there before)
    assert right - H22_WEAK[2] > 1.0 and H22_WEAK[2] - left > 1.0
    # and the line does matter there: 1 A out, some layer has line/continuum > ACCRT
    lop, cop = [np.asarray(v) for v in dll.GetLineOpacity(H22_WEAK[2] + 1.0)[:2]]
    ratio = lop / cop
    assert ratio.max() > ACCRT and ratio[-1] < ratio.max()
