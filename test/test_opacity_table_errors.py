import os
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap

import pytest

from pymodule.smelib import libfile as smelib_libfile


DATA_DIR = Path(__file__).resolve().parents[1] / "share" / "libsme"
FE_TABLE = "Fe1_Zatsarinny2019.dat.INTEL"
NH_TABLE = "NH_Stancil2018.dat.INTEL"


def _run_table_failure(tmp_path, table, failure, recover=False):
    data_dir = tmp_path / "data"
    shutil.copytree(DATA_DIR, data_dir)
    code = textwrap.dedent(
        """
        import os
        from pathlib import Path
        import shutil
        import sys

        import pytest

        from pymodule.smelib import SME_DLL

        # "test" would resolve to the standard library's package where it is
        # installed, so import the sibling module directly.
        sys.path.insert(0, "test")
        from test_call import get_abund, get_atmo, get_linelist

        libfile, original_data, data_dir, table, failure, recover = sys.argv[1:]
        data_dir = Path(data_dir)
        target = data_dir / table
        backup = data_dir / (table + ".complete")
        shutil.copy2(target, backup)
        if failure == "unreadable":
            target.chmod(0)
            assert not os.access(target, os.R_OK), "test cannot make the table unreadable"
        elif failure == "truncated":
            target.write_bytes(backup.read_bytes()[:64])
        else:
            raise AssertionError(failure)

        dll = SME_DLL(libfile, original_data)
        dll.SetLibraryPath(str(data_dir) + os.sep)
        dll.InputLineList(get_linelist())
        dll.InputModel(5772, 4.44, 0.7, get_atmo())
        dll.InputAbund(lambda *_, **__: get_abund())
        dll.Ionization(0)
        dll.InputWaveRange(2500.0, 3001.0)

        expected_path = str(target)
        with pytest.raises(RuntimeError) as exc:
            dll.Opacity()
        message = str(exc.value)
        assert table in message
        assert expected_path in message

        if recover == "1":
            target.chmod(0o600)
            shutil.copy2(backup, target)
            dll.Opacity()
        """
    )
    return subprocess.run(
        [
            sys.executable,
            "-c",
            code,
            smelib_libfile,
            str(DATA_DIR) + os.sep,
            str(data_dir),
            table,
            failure,
            "1" if recover else "0",
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize("table", [FE_TABLE, NH_TABLE])
def test_unreadable_opacity_table_reports_path(tmp_path, table):
    result = _run_table_failure(tmp_path, table, "unreadable")
    assert result.returncode == 0, result.stdout + result.stderr


def test_truncated_opacity_table_reports_path(tmp_path):
    result = _run_table_failure(tmp_path, NH_TABLE, "truncated")
    assert result.returncode == 0, result.stdout + result.stderr


def test_opacity_table_load_recovers_in_same_process(tmp_path):
    result = _run_table_failure(tmp_path, FE_TABLE, "truncated", recover=True)
    assert result.returncode == 0, result.stdout + result.stderr
