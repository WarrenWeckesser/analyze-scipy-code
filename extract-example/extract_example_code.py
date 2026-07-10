import ast
from contextlib import redirect_stdout
from io import StringIO
import sys
from numpydoc.docscrape import NumpyDocString
import scipy


def old_extract_example(fullname):
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
    current_block = []
    prev_import = True
    for line in ds['Examples']:
        line = line.strip()
        if line.startswith('>>> ') or line.startswith('... '):
            codeline = line[4:]
            if "import" in codeline:
                if not prev_import:
                    # Add a blank line before import statements.
                    code.append('')
                    prev_import = True
            elif prev_import:
                # Add a blank line after import statements.
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


matplotlib_preamble = """
# matplotlib preamble to match settings in SciPy's doc/source/conf.py
import matplotlib as mpl
font_size = 13*72/96.0  # 13 px
plot_rcparams = {
    'font.size': font_size,
    'axes.titlesize': font_size,
    'axes.labelsize': font_size,
    'xtick.labelsize': font_size,
    'ytick.labelsize': font_size,
    'legend.fontsize': font_size,
    'figure.figsize': (3*1.62, 3),
    'figure.subplot.bottom': 0.2,
    'figure.subplot.left': 0.2,
    'figure.subplot.right': 0.9,
    'figure.subplot.top': 0.85,
    'figure.subplot.wspace': 0.4,
    'text.usetex': False,
}
for key, value in plot_rcparams.items():
    mpl.rcParams[key] = value
"""

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
    current_block = []
    prev_import = True
    for line in ds['Examples']:
        line = line.strip()
        if line.startswith('... '):
            if len(current_block) == 0:
                raise RuntimeError("'... ' found but there is no line to continue.")
            current_block.append(line[4:])
        elif line.startswith('>>> '):
            if len(current_block) > 0:
                code.append('\n'.join(current_block))
            current_block = [line[4:]]
        else:
            # Not '... ' and not '>>> '
            if len(current_block) > 0:
                code.append('\n'.join(current_block))
                current_block = []
    if len(current_block) > 0:
        code.append('\n'.join(current_block))
        current_block = []

    code2 = []
    prev_import = False
    for line in code:
        if "plt" in line:
            has_plot = True
        if "plt.show()" in code:
            has_show = True
        if "import" in line and not prev_import:
            code2.append("")
            prev_import = True
        if "import" not in line and prev_import:
            code2.append("")
            prev_import = False
        code2.append(line)
    if has_plot:
        code2.insert(0, matplotlib_preamble.lstrip())
    if has_plot and not has_show:
        code2.append('plt.show()')
    return parts[-1], code2


def irun(code):
    """
    `code` must be a list of strings, where each string is a line of Python code.
    """
    g = {}
    for line in code:
        if line.strip() == '':
            continue

        if not line.startswith('# matplotlib preamble'):
            lines = line.split('\n')
            print(f'>>> {lines[0]}')
            for nextline in lines[1:]:
                print(f'... {nextline}')

        p = ast.parse(line).body
        if len(p) == 0:
            continue
        p0 = p[0]
        if isinstance(p0, (ast.Import, ast.ImportFrom, ast.Assign)):
            exec(line, globals=g)
        elif isinstance(p0, ast.Expr):
            tmp = "__tmp = " + line
            f = StringIO()
            with redirect_stdout(f):
                exec(tmp, globals=g)
            out = f.getvalue()
            value = g["__tmp"]
            del g["__tmp"]
            if len(out) > 0:
                print(out)
            if value is not None and not line.startswith('plt.'):
                print(repr(value))
        else:
            f = StringIO()
            with redirect_stdout(f):
                exec(line, globals=g)
            out = f.getvalue()
            if len(out) > 0:
                print(out)


if __name__ == "__main__":
    cmds = ['write', 'run', 'irun']
    if len(sys.argv) != 3 or sys.argv[1] not in cmds:
        print(f'use: {sys.argv[0]} command fully_qualified_scipy_name')
        print(f"where command must be one of {cmds}")
        sys.exit(0)

    command = sys.argv[1]
    fullname = sys.argv[2].strip()

    try:
        name, code = extract_example(fullname)
    except RuntimeError:
        print(f"ERROR: Failed to import {fullname}", file=sys.stderr)
        sys.exit(-1)

    match command:
        case 'write':
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
        case 'run':
            # Run the example code.
            code = '\n'.join(code)
            exec(code)
        case 'irun':
            # Run the example code line by line.
            # Print unassigned expressions that are not None.
            irun(code)
