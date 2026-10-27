from os.path import join, dirname, abspath
from distutils.core import setup, Extension
import numpy as np
import sys

libdir = abspath(join(dirname(__file__), "../lib"))
include_dirs = [np.get_include()]
include_dirs += [libdir]
extra_link_args = ["-ldl"] if sys.platform.startswith("linux") else []

module = Extension(
    "_smelib",
    sources=["_smelib.cpp"],
    language="c++",
    include_dirs=include_dirs,
    libraries=["sme"],
    library_dirs=[libdir],
    extra_link_args=extra_link_args,
)

setup(ext_modules=[module])

