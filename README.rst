|Python35| |MATLAB2016b|

.. |Python35| image:: https://img.shields.io/badge/python-3.5%2B-blue.svg
.. |MATLAB2016b| image:: https://img.shields.io/badge/MATLAB-2016b%2B-blue.svg

A Jupyter kernel for MATLAB
===========================

This kernel requires `Jupyter
<http://jupyter.readthedocs.org/en/latest/install.html>`_
with Python 3.5+, and the `MATLAB engine for Python
<https://www.mathworks.com/help/matlab/matlab-engine-for-python.html>`_ R2016b+
(this release provides a much better completion API), which needs to be
installed first.

Install with ``python -mpip install imatlab`` (from PyPI) or ``python -mpip
install git+https://github.com/anntzer/imatlab`` (from Github); then run
``python -mimatlab install`` to register the kernel spec.  In the absence of
administrator rights, the ``--user`` flag should be added to any of these
commands.

To use it, run one of::

    $ jupyter notebook
    # In the notebook interface, select Matlab from the 'New' menu
    $ jupyter qtconsole --kernel imatlab
    $ jupyter console --kernel imatlab

To use inline graphics in the notebook, please install `Plotly Offline for
MATLAB <https://plot.ly/matlab/offline/>`_ (and make sure ``fig2plotly`` is
available in your MATLAB path).

Environment variables
---------------------

To connect to an existing, shared MATLAB session, set the ``IMATLAB_CONNECT``
environment variable to a non-empty value.

Asynchronous output
-------------------

A construct such as ``1, pause(1), 2`` will output ``1`` and ``2`` with a one
second interval on Linux and OSX, but together after a one second wait on
Windows.  PRs improving Windows support are welcome.

Asynchronous output using ``timer`` objects seem to be completely unsupported
by the MATLAB engine for Python.

MATLAB debugger
---------------

The MATLAB debugger is cleared (``dbclear all``) before each execution, as
interactive input is not supported by the engine API.

Differences with the Calysto MATLAB Kernel
------------------------------------------

- The completion system is much more robust, by relying on the new API
  available in MATLAB 2016b.
- History is read from and written to MATLAB's own ``History.xml``, and thus
  shared with standard MATLAB sessions.
- Synchronous output is supported on Linux and OSX (see above).
- There is no magics systems, as MATLAB already provides many functions for
  this purpose (``cd``, ``edit``, etc.).
- Inline graphics are based on ``plotly``, and thus interactive.
