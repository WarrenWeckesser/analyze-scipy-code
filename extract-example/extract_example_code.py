import sys
from numpydoc.docscrape import NumpyDocString
import scipy


def extract_example(fullname):
    """
    Extract the code from the Examples section of the object specified by fullname.

    Returns the last part of `fullname`, and a list of strings that are the lines of
    Python code from the Examples section.

    Raises a `RuntimeError` if `fullname` cannot be imported.
    """
    fullname = fullname.strip()
    parts = fullname.split('.')
    start = '.'.join(parts[:-1])
    try:
        exec(f'from {start} import {parts[-1]}')
    except Exception:
        raise RuntimeError(f"Unable to import '{fullname}'")

    rest = parts[1:]
    obj = scipy
    for m in rest:
        obj = getattr(obj, m)

    docstring = obj.__doc__

    has_plot = False
    has_show = False
    ds = NumpyDocString(docstring)
    code = []
    prev_import = True
    for line in ds['Examples']:
        line = line.strip()
        if line.startswith('>>> ') or line.startswith('... '):
            codeline = line[4:]
            if "import" in codeline:
                if not prev_import:
                    code.append('')
                    prev_import = True
            elif prev_import:
                code.append('')
                prev_import = False
            if "plt" in codeline:
                has_plot = True
            if "plt.show()" in codeline:
                has_show = True
            code.append(codeline)
    if has_plot and not has_show:
        code.append('plt.show()')
    return parts[-1], code


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ['write', 'run']:
        print(f'use: {sys.argv[0]} command fully_qualified_scipy_name')
        print("where command is either write or run.")
        sys.exit(0)

    command = sys.argv[1]
    fullname = sys.argv[2].strip()

    try:
        name, code = extract_example(fullname)
    except RuntimeError:
        print(f"ERROR: Failed to import {fullname}", file=sys.stderr)
        sys.exit(-1)

    if command == 'write':
        # Write the example code to a file.
        filename = f'example_{name}.py'
        with open(filename, 'w') as f:
            f.write(f"# Python code extracted from the 'Examples' section of\n"
                    f"# {fullname}\n")
            f.write(f'# SciPy version: {scipy.__version__}\n\n')
            f.write('\n'.join(code))
            f.write('\n')

        print(f"Code from the 'Examples' section of {fullname} "
            f"written to '{filename}'.")
    else:
        # command == 'run':
        # Run the example code.
        code = '\n'.join(code)
        exec(code)
