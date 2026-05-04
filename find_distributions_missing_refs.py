"""
Find SciPy probability distributions whose docstrings do not contain "References".
"""

import scipy
from scipy import stats
from scipy.stats import _multivariate
from scipy.stats._distn_infrastructure import rv_generic


print(f"scipy version {scipy.__version__}")
print()
print("Distributions missing 'References' in their docstring:")

def check_dist(name):
    obj = getattr(stats, name)
    if isinstance(obj, rv_generic) or name in _multivariate.__all__:
        if "References" not in obj.__doc__:
            print(f"    {name}")

for name in dir(stats):
    check_dist(name)
