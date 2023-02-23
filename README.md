Assorted scripts that I use to analyze the SciPy source code.

* `dists_that_override.py`: Display which of the SciPy univariate continuous
  distributions override the given method names. For example,

      $ python dists_that_override.py _cdf _ppf _sf _isf _rvs
      SciPy version 1.11.0.dev0+1566.d5ceb77

      distribution         _cdf _ppf _sf  _isf _rvs
      alpha                ✔    ✔    -    -    -
      anglit               ✔    ✔    -    -    -
      arcsine              ✔    ✔    -    -    -
      argus                ✔    -    ✔    -    ✔
      beta                 ✔    ✔    ✔    ✔    ✔
      betaprime            ✔    ✔    -    -    ✔
      bradford             ✔    ✔    -    -    -
      burr                 ✔    ✔    ✔    -    -
      [...]
      wald                 ✔    ✔    ✔    ✔    ✔
      weibull_max          ✔    ✔    ✔    -    -
      weibull_min          ✔    ✔    ✔    -    -
      wrapcauchy           ✔    ✔    -    -    -

* `find_functions_missing_examples.py`: Find functions whose docstring is
  missing the "Examples" section.
* `find_missing_import_np.py`: Find functions where there is an "Examples"
  section that uses the name `np` but that do not have a corresponding
  `import numpy as np`.
* `find_docstring_issues.py`: (Work in progress) Looks for several common
  issues in the docstrings.  For example,

      $ python find_docstring_issues.py sparse
      scipy version 1.10.0.dev0+2299.5beb395

      === sparse ===
      sparse.block_diag
          section out of order: 'See Also'
      sparse.diags
          missing section: 'Returns'
      sparse.eye
          missing section: 'Returns'
      sparse.hstack
          missing section: 'Returns'
      sparse.identity
          missing section: 'Returns'
      sparse.rand
          section out of order: 'See Also'
      sparse.random
          duplicated imports in Examples:
              >>> from scipy.sparse import random
      sparse.save_npz
          missing section: 'Returns'
      sparse.spdiags
          missing section: 'Returns'
      sparse.vstack
          missing section: 'Returns'

* `extract_example_code.py`: Extract the code from the 'Examples' section
  of the SciPy object.

  For example,

      $ python extract_example_code.py scipy.special.logsumexp
      Code from the 'Examples' section of scipy.special.logsumexp written to 'example_logsumexp.py'.
      $ cat example_logsumexp.py
      # Python code extracted from the 'Examples' section of
      # scipy.special.logsumexp

      import numpy as np
      from scipy.special import logsumexp
      a = np.arange(10)
      logsumexp(a)
      np.log(np.sum(np.exp(a)))
      a = np.arange(10)
      b = np.arange(10, 0, -1)
      logsumexp(a, b=b)
      np.log(np.sum(b*np.exp(a)))
      logsumexp([1,2],b=[1,-1],return_sign=True)
      a = np.ma.array([np.log(2), 2, np.log(3)],
                      mask=[False, True, False])
      b = (~a.mask).astype(int)
      logsumexp(a.data, b=b), np.log(5)
