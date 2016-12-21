|Python35|

.. |Python35| image:: https://img.shields.io/badge/python-3.5-blue.svg

A Jupyter kernel for MATLAB
===========================

This requires `Jupyter Notebook <http://jupyter.readthedocs.org/en/latest/install.html>`_
with Python 3.5+, and the `MATLAB engine for Python
<https://www.mathworks.com/help/matlab/matlab-engine-for-python.html>`_
R2016b+ (this release provides a much better completion API).

To install::

    $ python -mpip install git+https://github.com/anntzer/matlab_kernel
    $ python -m matlab_kernel install

or::

    $ python -mpip install --user git+https://github.com/anntzer/matlab_kernel
    $ python -m matlab_kernel install --user

To use it, run one of::

    $ jupyter notebook
    # In the notebook interface, select Matlab from the 'New' menu
    $ jupyter qtconsole --kernel matlab
    $ jupyter console --kernel matlab

Note: This is a rewrite from scratch of the original `Calysto MATLAB Kernel
<https://github.com/Calysto/matlab_kernel>`_, which does not inherit from the
Calysto MetaKernel anymore.  Unlike the original implementation, this kernel
does not support inline graphics in the notebook -- the MATLAB Live Editor is
probably more suited for this use case unless we somehow manage to embed the
figure JFrame into the notebook.

Environment variables
---------------------

To connect to an existing, shared MATLAB session, set the ``CONNECT_MATLAB``
environment variable to a non-empty value.

Asynchronous output
-------------------

A construct such as ``1, pause(1), 2`` will output ``1`` and ``2`` with a one
second interval on Linux and OSX, but together after a one second wait on
Windows.  PRs improving Windows support are welcome.

Asynchronous output using ``timer`` objects seem to be completely unsupported
by the MATLAB engine for Python.
