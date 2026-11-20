#!/usr/bin/env python3
"""Measure the four high-n Stehle profiles that exposed NALPHA padding.

The diagnostic is intentionally independent of the PySME wrapper.  Point
``--library`` at a built SMElib shared library and ``--data`` at its
``share/libsme`` directory.  The frequency-integrated profile area should be
near one and the peak should remain finite after the padding fix.
"""

from __future__ import annotations

import argparse
import ctypes
import math
from pathlib import Path

import numpy as np


LINES = {
    22: 3676.3692,
    26: 3667.6881,
    27: 3666.1016,
    30: 3662.2625,
}
# These grid points contain the zero-alpha padding in the distributed table.
POINTS = {22: (5000.0, 10.0), 26: (5000.0, 10.5),
          27: (5000.0, 10.0), 30: (5000.0, 10.5)}
C_A_S = 2.99792458e18
KB = 1.380649e-16
M_H = 1.6735575e-24


def _profile_function(library: Path, data: Path):
    function = ctypes.CDLL(str(library)).hlinprof_
    path = (str(data).rstrip("/") + "/").encode()
    path_length = ctypes.c_int(len(path))
    byte_swap = ctypes.c_int(1)

    def evaluate(wave: float, center: float, temperature: float,
                 log_ne: float, upper: int) -> float:
        wave_c = ctypes.c_double(wave)
        center_c = ctypes.c_double(center)
        temp_c = ctypes.c_float(temperature)
        ne_c = ctypes.c_float(10.0 ** log_ne)
        lower_c = ctypes.c_int(2)
        upper_c = ctypes.c_int(upper)
        zero = ctypes.c_float(0.0)
        doppler = ctypes.c_float(
            math.sqrt(2.0 * KB * temperature / M_H) / 2.99792458e10
        )
        output = ctypes.c_float()
        function(
            ctypes.byref(wave_c), ctypes.byref(center_c), ctypes.byref(temp_c),
            ctypes.byref(ne_c), ctypes.byref(lower_c), ctypes.byref(upper_c),
            ctypes.byref(zero), ctypes.byref(zero), ctypes.byref(doppler),
            ctypes.byref(output), ctypes.c_char_p(path),
            ctypes.byref(path_length), ctypes.byref(byte_swap),
            ctypes.c_size_t(len(path)),
        )
        return float(output.value)

    return evaluate


def measure_profiles(library: Path, data: Path):
    """Return ``(upper, temperature, log_ne, area, peak)`` diagnostics."""
    evaluate = _profile_function(library, data)
    rows = []
    for upper, center in LINES.items():
        temperature, log_ne = POINTS[upper]
        positive = np.unique(np.r_[np.linspace(0.0, 0.02, 301),
                                   np.geomspace(0.02001, 3000.0, 2400)])
        offsets = np.r_[-positive[:0:-1], positive]
        wavelength = center + offsets
        profile = np.asarray([
            evaluate(value, center, temperature, log_ne, upper)
            for value in wavelength
        ])
        frequency = C_A_S / wavelength
        phi_frequency = profile * wavelength * wavelength / C_A_S
        order = np.argsort(frequency)
        area = float(np.trapezoid(phi_frequency[order], frequency[order]))
        rows.append((upper, temperature, log_ne, area, float(profile.max())))

    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    args = parser.parse_args()
    rows = measure_profiles(args.library, args.data)

    print("upper T_K log10_ne area_frequency peak")
    for row in rows:
        print(f"{row[0]:5d} {row[1]:4.0f} {row[2]:8.1f} {row[3]:.9f} {row[4]:.6g}")


if __name__ == "__main__":
    main()
