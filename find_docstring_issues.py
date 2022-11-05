
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
    ('Recieves', False),
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


def check_headings(docstring):
    result = []
    headings_found = get_headings(docstring)
    if "See also" in headings_found:
        result.append("'See also' should be 'See Also' "
                      "(according to the standard)")
        idx = headings_found.index('See also')
        headings_found[idx] = 'See Also'
    prev_index = -1
    for k, (heading, req) in enumerate(_docstring_sections):
        n = headings_found.count(heading)
        if n == 0 and req:
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
               'spatial', 'special',
               'stats', 'stats.contingency', 'stats.mstats']

skip = ['integrate.trapezoid', 'integrate.trapz', 'special.sinc']

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        modules = sys.argv[1:]
    else:
        modules = all_modules

    print(f"scipy version {scipy.__version__}")

    for module_name in modules:
        print()
        print(f"=== {module_name} ===")
        for obj_name, obj in module_objects(module_name,
                                            include_classes=False):
            full_name = module_name + '.' + obj_name
            if full_name not in skip:
                docstring = obj.__doc__
                sections_issues = check_headings(docstring)
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
