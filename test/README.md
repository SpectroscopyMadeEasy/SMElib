# Testing SMElib

The tests call the compiled shared library through the Python wrapper used by PySME.

Build the library and wrapper before running the suite:

```bash
./bootstrap
./configure --prefix="$PWD"
make install
python -m pip install -r test/requirements.txt
(cd pymodule && python setup.py build_ext --inplace)
python -m pytest
```

Changes to EOS, opacity, or line profiles also require a focused spectral regression in PySME.
The SMElib build test alone does not establish scientific equivalence.
