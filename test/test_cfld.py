"""Exercise exported CFLD functions using prescribed fields, without an EOS."""
import ctypes
import os
from pathlib import Path
import numpy as np


def test_native_cfld_exports_and_closure():
    root = Path(__file__).resolve().parents[1]
    explicit = os.environ.get('CFLD_LIBRARY')
    candidates = ([Path(explicit)] if explicit else
                  list((root/'lib').glob('libsme*')) + list((root/'src/.libs').glob('libsme*')))
    candidates = [p for p in candidates if p.suffix in ('.so', '.dylib', '.dll')]
    assert candidates, 'Build SMElib first or set CFLD_LIBRARY'
    lib = ctypes.CDLL(str(candidates[0].resolve()))
    ptr = np.ctypeslib.ndpointer(dtype=np.float64, flags='C_CONTIGUOUS')
    fun = lib.SMEPhysicalCFLDPath
    fun.argtypes = [ctypes.c_int]+[ptr]*6+[ctypes.c_int,ctypes.c_int,ptr,ptr]
    fun.restype = ctypes.c_int
    mass = np.geomspace(.001,20,56); k=np.ones(56); b=1+mass
    for tangent in (0,1):
        out=np.zeros((6,55));meta=np.zeros(7)
        assert fun(56,mass,k,2*k,b,b,b,tangent,24,out,meta)==0
        np.testing.assert_allclose((out[0]+out[4]+out[5]).sum()+meta[4],meta[0]-meta[1],rtol=1e-6)
        assert fun(56,mass,k,k,b,b,b,tangent,24,out,meta)==0
        np.testing.assert_allclose(out[0]+out[4]+out[5],0,atol=1e-10,rtol=0)
    ref=lib.SMECFLDReferencePath
    ref.argtypes=[ctypes.c_int,ptr,ptr,ptr,ctypes.c_int,ptr];ref.restype=ctypes.c_int
    value=np.zeros(1)
    assert ref(56,mass,k,b,1,value)==0
    np.testing.assert_allclose(value[0],meta[0],rtol=1e-13)
    assert ref(2,mass,k,b,1,value)==1
    assert np.isnan(value[0])
    bad=k.copy();bad[0]=-1
    assert ref(56,mass,bad,b,1,value)==2
    state=lib.SMEPhysicalCFLD
    state.argtypes=[ctypes.c_int,ptr,ctypes.c_int,ptr,ctypes.c_int,ctypes.c_int,ptr,ptr];state.restype=ctypes.c_int
    assert state(1,np.array([5000.]),1,np.array([1.]),56,24,np.zeros((6,55)),np.zeros(9))==10
    geo=lib.SMECFLDRayGeometry
    ip=np.ctypeslib.ndpointer(dtype=np.int32,flags='C_CONTIGUOUS')
    geo.argtypes=[ctypes.c_int,ptr,ctypes.c_int,ptr,ip,ip];geo.restype=ctypes.c_int
    assert geo(1,np.array([1.]),56,np.zeros(112),np.zeros(1,dtype=np.int32),np.zeros(1,dtype=np.int32))==10


def test_path_mapping_and_trace_entry_points():
    root = Path(__file__).resolve().parents[1]
    explicit = os.environ.get('CFLD_LIBRARY')
    candidates = ([Path(explicit)] if explicit else
                  list((root/'lib').glob('libsme*')) + list((root/'src/.libs').glob('libsme*')))
    candidates = [p for p in candidates if p.suffix in ('.so', '.dylib', '.dll')]
    assert candidates, 'Build SMElib first or set CFLD_LIBRARY'
    lib = ctypes.CDLL(str(candidates[0].resolve()))
    ip = np.ctypeslib.ndpointer(dtype=np.int32, flags='C_CONTIGUOUS')
    mapper = lib.SMECFLDPathShellMap
    mapper.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ip]
    mapper.restype = ctypes.c_int
    for n, tangent, turn in [(55, 0, None), (94, 1, 46), (64, 1, 31)]:
        shells = np.full(n-1, -99, dtype=np.int32)
        assert mapper(n, 55, tangent, shells) == 0
        assert shells[0] == -1
        for i in range(1, n-1):
            assert shells[i] == (i if not tangent or i<n//2 else n-2-i)
        if turn is not None:
            assert shells[n//2-1] == turn
            assert shells[n//2] == turn-1
    assert mapper(2, 55, 0, np.zeros(1, dtype=np.int32)) == 1
    setter = lib.SMECFLDSetPathTrace
    setter.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    setter.restype = ctypes.c_int
    values = np.zeros((1, 1, 6, 109)); shells = np.zeros((1, 109),dtype=np.int32)
    assert setter(values.ctypes.data, shells.ctypes.data) == 0
    assert setter(None, None) == 0  # Clear before another native call.
