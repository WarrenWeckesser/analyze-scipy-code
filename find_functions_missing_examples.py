"""
Find scipy functions whose docstrings do not contain "Examples".

This looks for *functions* only, not all callables.
"""

import importlib
import types
import numpy as np
import scipy
from scipy._lib.uarray import _Function


# Note: fftpack and stats.mstats are intentionally not included.
modules = ["cluster.hierarchy", "cluster.vq", "constants", "datasets",
           "differentiate", "fft",
           "integrate", "interpolate", "io", "io.arff", "io.wavfile",
           "linalg", "linalg.interpolative",
           "ndimage", "odr", "optimize",
           "signal", "signal.windows",
           "sparse", "sparse.linalg", "sparse.csgraph",
           "spatial", "spatial.distance", "spatial.transform",
           "special", "stats", "stats.contingency"]

skip = ["integrate.cumtrapz", "integrate.simps", "integrate.trapz",
        "ndimage.sum", "signal.cmplx_sort"]

print(f"scipy version {scipy.__version__}")
print()

total = 0
for module_name in modules:
    mod = importlib.import_module("." + module_name, package="scipy")
    objects = [(name, getattr(mod, name))
               for name in getattr(mod, "__all__", dir(mod))
               if not name.startswith("_")]
    funcs = [item for item in objects
             if isinstance(item[1], (types.FunctionType,
                                     types.BuiltinFunctionType,
                                     np.ufunc,
                                     _Function))]
    noex = [item for item in funcs
            if ((module_name + "." + item[0]) not in skip and
                (item[1].__doc__ is None or
                ("is deprecated" not in item[1].__doc__) and
                ("Examples" not in item[1].__doc__)))]
    if len(noex) > 0:
        noex.sort()
        total += len(noex)
        print(f"{module_name} ({len(noex)})")
        for name, func in noex:
            print("   ", name, end="")
            if func.__doc__ is None:
                print(" \t[no docstring]")
            else:
                print()

print()
print(f"Found {total} functions")
