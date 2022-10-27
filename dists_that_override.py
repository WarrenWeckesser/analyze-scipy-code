import sys
from shutil import get_terminal_size
import scipy
from scipy.stats import _continuous_distns, rv_continuous


def print_names(names):
    max_name_len = 20
    terminal_cols = get_terminal_size().columns
    ncols = (terminal_cols - 4) // max_name_len
    n = len(names)
    nrows, last = divmod(n, ncols)
    for row in range(nrows + int(last > 0)):
        rownames = names[row*ncols:(row+1)*ncols]
        line = ' '.join(f'{name:19s}' for name in rownames)
        print("   ", line)


def overrides(name, target):
    """
    `name` is the name of a SciPy distribution, e.g. "gamma"
    `target` is the name of a method, e.g. "_ppf".
    The function returns True if the distribution overrides the default
    implementation of the method.
    """
    instance_method = getattr(getattr(_continuous_distns, name).__class__,
                              target)
    class_method = getattr(rv_continuous, target)
    return instance_method != class_method


if len(sys.argv) != 2:
    print(f"use: {sys.argv[0]} method_name")
    sys.exit(-1)


target = sys.argv[1]

dist_names = [name for name in dir(_continuous_distns)
              if isinstance(getattr(_continuous_distns, name), rv_continuous)]
with_override = [name for name in dist_names if overrides(name, target)]
without_override = sorted(set(dist_names) - set(with_override))

print(f'SciPy version {scipy.__version__}')
print()

print(f"Distributions that override {target}:")
print_names(with_override)

print()
print(f"Distributions that do not override {target}:")
print_names(without_override)
