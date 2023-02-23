import sys
from numpydoc.docscrape import NumpyDocString
import scipy


if len(sys.argv) != 2:
    print(f'use: {sys.argv[0]} fully_qualified_scipy_name')
    sys.exit(0)


fullname = sys.argv[1].strip()
parts = fullname.split('.')
start = '.'.join(parts[:-1])
try:
    exec(f'from {start} import {parts[-1]}')
except Exception:
    print(f"Unable to import '{fullname}'")
    exit(-1)

rest = parts[1:]
obj = scipy
for m in rest:
    obj = getattr(obj, m)

docstring = obj.__doc__

has_plot = False
has_show = False
ds = NumpyDocString(docstring)
code = []
for line in ds['Examples']:
    line = line.strip()
    if line.startswith('>>> ') or line.startswith('... '):
        codeline = line[4:]
        if "plt" in codeline:
            has_plot = True
        if "plt.show()" in codeline:
            has_show = True
        code.append(codeline)
if has_plot and not has_show:
    code.append('plt.show()')

filename = f'example_{parts[-1]}.py'
with open(filename, 'w') as f:
    f.write(f"# Python code extracted from the 'Examples' section of\n"
            f"# {fullname}\n\n")
    f.write('\n'.join(code))
    f.write('\n')

print(f"Code from the 'Examples' section of {fullname} "
      f"written to '{filename}'.")
