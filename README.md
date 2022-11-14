Assorted scripts that I use to analyze the SciPy source code.

* `dists_that_override.py`: Display which of the univariate continuous distributions override the given method name.
* `find_functions_missing_examples.py`: Find functions whose docstring is missing the "Examples" section.
* `find_missing_import_np.py`: Find functions where there is an "Examples" section that uses the name `np` but that do not have a corresponding `import numpy as np`.
* `find_docstring_issues.py`: (Work in progress) Looks for several common issues in the docstrings.
* `extract_example_code.py`: Extract the code from the 'Examples' section of the SciPy object.
