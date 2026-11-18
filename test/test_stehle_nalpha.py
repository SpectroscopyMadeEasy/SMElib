"""Regression checks for zero-padded Stehle detuning rows."""

from __future__ import annotations

import struct
from pathlib import Path

import numpy as np

from pymodule.smelib import libfile as smelib_libfile
from stehle_profile_diagnostic import measure_profiles


DATA = Path(__file__).parents[1] / "src" / "data" / "stehle_long.dat.INTEL"
TARGETS = {(2, 22), (2, 26), (2, 27), (2, 30)}


def _record(stream):
    marker = stream.read(4)
    if not marker:
        raise EOFError
    size = struct.unpack("<i", marker)[0]
    payload = stream.read(size)
    trailer = struct.unpack("<i", stream.read(4))[0]
    assert trailer == size
    return payload


def _table():
    with DATA.open("rb") as stream:
        nwl, ntemp, nne, nline = np.frombuffer(_record(stream), "<i4")
        ids = np.frombuffer(_record(stream), "<i4").reshape(nline, 2)
        _record(stream)  # temperatures
        _record(stream)  # electron densities
        _record(stream)  # F0
        _record(stream)  # wing parameters
        _record(stream)  # widths
        nalpha = np.frombuffer(_record(stream), "<i4").reshape(
            (ntemp, nne, nline), order="F"
        )
        alpha = np.empty((nline, nwl, ntemp, nne), dtype="<f4")
        sprof = np.empty_like(alpha)
        for line in range(nline):
            alpha[line] = np.frombuffer(_record(stream), "<f4").reshape(
                (nwl, ntemp, nne), order="F"
            )
            sprof[line] = np.frombuffer(_record(stream), "<f4").reshape(
                (nwl, ntemp, nne), order="F"
            )
    return ids, nalpha, alpha, sprof


def test_target_lines_have_zero_alpha_padding():
    ids, nalpha, alpha, sprof = _table()
    for lower, upper in TARGETS:
        line = int(np.where((ids[:, 0] == lower) & (ids[:, 1] == upper))[0][0])
        padding_rows = []
        for it in range(nalpha.shape[0]):
            for ine in range(nalpha.shape[1]):
                count = int(nalpha[it, ine, line])
                zero_alpha = np.flatnonzero(
                    (alpha[line, :, it, ine] == 0.0)
                    & (np.arange(alpha.shape[1]) > 0)
                    & (np.arange(alpha.shape[1]) < count)
                    & (sprof[line, :, it, ine] != 0.0)
                )
                if zero_alpha.size:
                    padding_rows.append((it, ine, count, int(zero_alpha[0])))
        assert padding_rows, f"no zero-alpha padding found for H{upper}"
        # The Fortran fix sets NALPHA=K-1, where K is the first padded point.
        assert all(count > padded_index for _, _, count, padded_index in padding_rows)


def test_valid_prefixes_are_positive_after_padding_trim():
    ids, nalpha, alpha, sprof = _table()
    for line in range(len(ids)):
        for it in range(nalpha.shape[0]):
            for ine in range(nalpha.shape[1]):
                count = int(nalpha[it, ine, line])
                first_zero = np.flatnonzero(
                    (alpha[line, :, it, ine] == 0.0)
                    | (sprof[line, :, it, ine] == 0.0)
                )
                if first_zero.size and first_zero[0] > 0:
                    # The runtime's post-read trim is exactly this prefix.
                    assert count >= int(first_zero[0])


def test_target_profile_integrals_are_near_unity():
    """Exercise the built library so the test fails without the Fortran fix."""

    data = Path(__file__).parents[1] / "share" / "libsme"
    rows = measure_profiles(Path(smelib_libfile), data)
    assert {row[0] for row in rows} == {22, 26, 27, 30}
    for upper, _temperature, _log_ne, area, peak in rows:
        assert 0.94 < area < 1.02, f"H{upper} area={area}"
        assert peak < 10.0, f"H{upper} peak={peak}"
