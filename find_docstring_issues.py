
from collections import Counter
import re
import importlib
import types
import numpy as np
import scipy
from scipy._lib.uarray import _Function


_docstring_sections = [
    ('Parameters', True),
    ('Returns', True),
    ('Yields', False),
    ('Receives', False),
    ('Other Parameters', False),
    ('Raises', False),
    ('Warns', False),
    ('Warnings', False),
    ('See Also', False),
    ('Notes', False),
    ('References', False),
    ('Examples', False),
]


def get_headings(docstring):
    if docstring is None:
        return []
    lines = docstring.splitlines()
    result = []
    for k in range(len(lines)-1):
        line = lines[k]
        if len(line.strip()) > 0:
            m = re.match('^ *', line)
            indent = m.group(0)
            uline = indent + '-'*(len(line) - len(indent))
            if lines[k+1] == uline:
                result.append(line.strip())
    return result


def check_headings(docstring, args):
    result = []
    headings_found = get_headings(docstring)
    if "See also" in headings_found and not args.ignore_see_also_case:
        result.append("'See also' should be 'See Also' "
                      "(according to the standard)")
        idx = headings_found.index('See also')
        headings_found[idx] = 'See Also'
    prev_index = -1
    for k, (heading, req) in enumerate(_docstring_sections):
        n = headings_found.count(heading)
        if n == 0 and req:
            if heading != 'Returns' or not args.ignore_missing_returns:
                result.append(f"missing section: '{heading}'")
        if n > 0:
            if n > 1:
                result.append(f"repeated section: '{heading}'")
            index = headings_found.index(heading)
            if index < prev_index:
                msg = f"section out of order: '{headings_found[prev_index]}'"
                result.append(msg)
            prev_index = index
    return result


def is_missing_import_np(docstring):
    if docstring is None:
        return False
    examples_start = docstring.find('Examples\n')
    if examples_start == -1:
        return False
    examples_section = docstring[examples_start:]
    return ('np.' in examples_section and
            'import numpy as np' not in examples_section)


def find_duplicate_imports_in_examples(docstring):
    """
    The function uses a simple string comparison of lines.
    It will not detect semantic duplication such as

        >>> from numpy import array, asarray
        >>> from numpy import asarray, array

    The function assumes that the Examples section is the last
    section in the docstring.  If that is not the case, it may
    generate a false positive if there are import statements
    in the section(s) after the Examples section.
    """
    if docstring is None:
        return []
    examples_start = docstring.find('Examples\n')
    if examples_start == -1:
        return []
    examples_section = docstring[examples_start:]
    lines = [t.strip() for t in examples_section.splitlines()]
    lines = [line for line in lines if 'import' in line]
    lines.sort()
    result = []
    counts = Counter(lines)
    for key, value in counts.items():
        if value > 1:
            result.append(key)
    return result


def module_objects(module_name, include_classes=True):
    mod = importlib.import_module('.' + module_name, package='scipy')
    objects = [(name, getattr(mod, name))
               for name in getattr(mod, '__all__', dir(mod))
               if not name.startswith('_')]
    funcs = [item for item in objects
             if isinstance(item[1], (types.FunctionType,
                                     types.BuiltinFunctionType,
                                     np.ufunc,
                                     _Function))]
    for item in funcs:
        yield item

    if include_classes:
        classes = [item for item in objects
                   if isinstance(item[1], type)]
        for cls_item in classes:
            name, cls = cls_item
            for cls_attr in dir(cls):
                cls_obj = getattr(cls, cls_attr)
                if (callable(cls_obj)
                        and not cls_attr.startswith('_')
                        and not isinstance(cls_obj,
                                           types.MemberDescriptorType)):
                    yield ('.'.join([name, cls_attr]), cls_obj)


all_modules = ['cluster.hierarchy', 'cluster.vq', 'constants', 'datasets',
               'fft', 'fftpack', 'integrate', 'interpolate',
               'io', 'io.arff', 'io.wavfile',
               'linalg', 'misc', 'ndimage', 'odr', 'optimize',
               'signal', 'signal.windows',
               'sparse', 'sparse.linalg', 'sparse.csgraph',
               'spatial', 'spatial.distance', 'spatial.transform',
               'special',
               'stats', 'stats.contingency', 'stats.mstats']

skip = [
    # These are actually NumPy functions:
    'integrate.trapezoid', 'integrate.trapz', 'special.sinc',
    'fftpack.fftfreq', 'fftpack.fftshift', 'fftpack.ifftshift',
    'fft.fftfreq', 'fft.fftshift', 'fft.ifftshift', 'fft.rfftfreq',
    # These are deprecated names:
    'integrate.cumtrapz', 'integrate.simps',
]

if __name__ == "__main__":
    # import sys
    import argparse
    parser = argparse.ArgumentParser(
        prog='find_docstring_issues.py',
        description=('Check SciPy functions for docstring issues'),
    )
    parser.add_argument('modules', nargs='*', default=all_modules)
    parser.add_argument('-r', '--ignore-missing-returns', action='store_true',
                        help="Ignore missing 'Returns' section.")
    parser.add_argument('-s', '--ignore-see-also-case', action='store_true',
                        help=('Ignore case discrepancy in the "See Also" '
                              'section title'))
    args = parser.parse_args()

    print(f"scipy version {scipy.__version__}")

    for module_name in args.modules:
        print()
        print(f"=== {module_name} ===")
        for obj_name, obj in module_objects(module_name,
                                            include_classes=False):
            full_name = module_name + '.' + obj_name
            if full_name not in skip:
                docstring = obj.__doc__
                sections_issues = check_headings(docstring, args)
                missing_import_np = is_missing_import_np(docstring)
                dup_imports = find_duplicate_imports_in_examples(docstring)
                if sections_issues or missing_import_np or dup_imports:
                    print(full_name)
                for line in sections_issues:
                    print(f'    {line}')
                if missing_import_np:
                    print("    missing 'import numpy as np' in 'Examples'")
                if dup_imports:
                    print("    duplicated imports in Examples:")
                    for line in dup_imports:
                        print(f"        {line}")
