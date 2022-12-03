Assorted scripts that I use to analyze the SciPy source code.

* `dists_that_override.py`: Display which of the SciPy univariate continuous
  distributions override the given method names. For example,::

      $ python3 dists_that_override.py _cdf _ppf _sf _isf _rvs
      SciPy version 1.10.0.dev0+2299.5beb395

      distribution         _cdf _ppf _sf  _isf _rvs
      alpha                ☑    ☑    ☐    ☐    ☐
      anglit               ☑    ☑    ☐    ☐    ☐
      arcsine              ☑    ☑    ☐    ☐    ☐
      argus                ☑    ☐    ☑    ☐    ☑
      beta                 ☑    ☑    ☑    ☑    ☑
      betaprime            ☑    ☐    ☐    ☐    ☑
      bradford             ☑    ☑    ☐    ☐    ☐
      burr                 ☑    ☑    ☑    ☐    ☐
      [...]
      wald                 ☑    ☑    ☑    ☑    ☑
      weibull_max          ☑    ☑    ☑    ☐    ☐
      weibull_min          ☑    ☑    ☑    ☐    ☐
      wrapcauchy           ☑    ☑    ☐    ☐    ☐

* `find_functions_missing_examples.py`: Find functions whose docstring is
  missing the "Examples" section.
* `find_missing_import_np.py`: Find functions where there is an "Examples"
  section that uses the name `np` but that do not have a corresponding
  `import numpy as np`.
* `find_docstring_issues.py`: (Work in progress) Looks for several common
  issues in the docstrings.
* `extract_example_code.py`: Extract the code from the 'Examples' section
  of the SciPy object.
