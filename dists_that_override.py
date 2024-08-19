import argparse
import math
from shutil import get_terminal_size
import scipy
from scipy.stats import distributions, rv_continuous


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
    instance_method = getattr(getattr(distributions, name).__class__,
                              target)
    class_method = getattr(rv_continuous, target)
    return instance_method != class_method


def main():
    parser = argparse.ArgumentParser(
        prog='dists_that_override',
        description=('Show which SciPy continuous univariate distributions '
                     'override methods'),
    )
    parser.add_argument('-s', '--support', action='store_true',
                        help=('Show the standard support of the distribution '
                              'in the output.  (For some distributions, the '
                              'support depends on the parameters. This output '
                              'will not reflect all the possibilities for '
                              'such distributions.)'))
    parser.add_argument('-i', '--infinite-support', action='store_true',
                        help=('Show only distributions that have infinite '
                              'support.'))
    parser.add_argument('method', type=str, nargs='+',
                        help='Method to check for override.')
    args = parser.parse_args()

    print(f'SciPy version {scipy.__version__}')
    print()

    dist_names = [name for name in dir(distributions)
                  if isinstance(getattr(distributions, name),
                                rv_continuous)]

    if len(args.method) == 1:
        target = args.method[0]
        dist_names = [name for name in dir(distributions)
                      if isinstance(getattr(distributions, name),
                                    rv_continuous)]
        with_override = [name for name in dist_names
                         if overrides(name, target)]
        without_override = sorted(set(dist_names) - set(with_override))

        print(f"Continuous univariate distributions that override {target}:")
        print_names(with_override)

        print()
        print("Continuous univariate distributions that do not override "
              f"{target}:")
        print_names(without_override)
    else:
        # More than one argument on the command line.
        # Make a table with checkboxes for the methods that are overridden.
        if args.infinite_support:
            print('Showing only distributions with infinite support.\n')
        print(f'{"distribution":21s}', end='')
        if args.support:
            print(f'{"support":16s}  ', end='')
        w = 1 + max([len(meth) for meth in args.method])
        for method in args.method:
            print(f'{method:{w}}', end='')
        print()
        for name in dist_names:
            dist = getattr(scipy.stats, name)
            if (args.infinite_support and
                    math.inf not in [abs(dist.a), abs(dist.b)]):
                continue
            print(f'{name:21s}', end='')
            if args.support:
                # Show the default support.
                print(f'[{dist.a:6.3g}, {dist.b:6.3g}]   ', end='')
            for method in args.method:
                print(f'{"✔" if overrides(name, method) else "-":{w}}', end='')
            print()


if __name__ == "__main__":
    main()
