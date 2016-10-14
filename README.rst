|Python35|

.. |Python35| image:: https://img.shields.io/badge/python-3.5-blue.svg

A Jupyter kernel for MATLAB
===========================

This requires `Jupyter Notebook <http://jupyter.readthedocs.org/en/latest/install.html>`_
with Python 3.5+, and the
`MATLAB engine for Python <https://www.mathworks.com/help/matlab/matlab-engine-for-python.html>`_ R2016b+.

To install::

    $ python -mpip install matlab_kernel
    # or `python -mpip install git+https://github.com/anntzer/matlab_kernel`
    # for the devel version.
    $ python -m matlab_kernel install

To use it, run one of::

    $ jupyter notebook
    # In the notebook interface, select Matlab from the 'New' menu
    $ jupyter qtconsole --kernel matlab
    $ jupyter console --kernel matlab

Note: This is a rewrite from scratch of the original `Calysto MATLAB Kernel
<https://github.com/Calysto/matlab_kernel>`, which does not inherit from the
Calysto MetaKernel anymore.
