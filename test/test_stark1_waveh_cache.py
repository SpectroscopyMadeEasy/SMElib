"""Native regression for the STARK1 WAVEH-dependent cache entry."""

from pathlib import Path
import os
import shutil
import subprocess
import tempfile

import pytest


DRIVER = r"""
program test_stark1_waveh_cache
  implicit none
  integer :: n,m
  real*8 :: waveh, primed_waveh, wave, primed_wave, value
  real :: temp,xne
  real :: stark1
  character(len=16) :: mode
  external stark1
  call get_command_argument(1,mode)
  n=4
  m=10
  temp=8000.0
  xne=1.0e14
  waveh=10000.0d0
  primed_waveh=11000.0d0
  wave=waveh+5.0d0
  primed_wave=primed_waveh+5.0d0
  if (trim(mode).eq.'warm') value=stark1(n,m,primed_wave,primed_waveh,temp,xne)
  value=stark1(n,m,wave,waveh,temp,xne)
  print '(ES24.16)', value
end program test_stark1_waveh_cache
"""


def _build_and_run(mode):
    # macOS CI selects a versioned GNU compiler through FC.
    configured = os.environ.get("FC", "gfortran")
    compiler = (
        shutil.which(configured)
        if Path(configured).name.startswith("gfortran")
        else None
    ) or shutil.which("gfortran")
    if compiler is None:
        pytest.skip("gfortran is required for the native STARK1 regression")

    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="stark1-waveh-") as tmp:
        tmp = Path(tmp)
        driver = tmp / "driver.f90"
        executable = tmp / "stark1"
        driver.write_text(DRIVER)
        subprocess.run(
            [
                compiler,
                "-std=legacy",
                "-O0",
                "-ffixed-line-length-none",
                "-o",
                str(executable),
                str(root / "src/sme/hlinop.f"),
                str(driver),
            ],
            check=True,
            cwd=root,
        )
        environment = dict(os.environ)
        # Keep this test on the legacy STARK1 path; the convolution path has
        # its own cache and is not part of this regression.
        environment.pop("PYSME_H_STARK_CONVOLUTION", None)
        result = subprocess.run(
            [str(executable), mode],
            check=True,
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
        )
        return float(result.stdout.strip())


def test_stark1_cache_key_includes_waveh():
    cold = _build_and_run("cold")
    warm = _build_and_run("warm")

    assert cold > 0.0
    assert warm > 0.0
    assert abs(warm - cold) <= abs(cold) * 1.0e-7
