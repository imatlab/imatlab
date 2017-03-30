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
install git+https://github.com/imatlab/imatlab`` (from Github); then run
``python -mimatlab install`` to register the kernel spec.  In the absence of
administrator rights, the ``--user`` flag should be added to any of these
commands.

To use it, run one of::

    $ jupyter notebook
    # In the notebook interface, select Matlab from the 'New' menu
    $ jupyter qtconsole --kernel imatlab
    $ jupyter console --kernel imatlab


Inline Graphics
---------------

To use Plotly inline graphics in the notebook, the `Plotly MATLAB API
<https://plot.ly/matlab>`_ must be installed.

1. Clone `plotly/MATLAB-Online <https://github.com/plotly/MATLAB-Online>`_ or
   download the `zip <https://github.com/plotly/MATLAB-api/archive/master.zip>`_.
2. Recursively add the resulting extracted folders to the MATLAB path:
   ``addpath(genpath(<Plotly MATLAB API path>))``.
3. In MATLAB, run: ``getplotlyoffline('https://cdn.plot.ly/plotly-latest.min.js')``
   to copy the JavaScript files.
4. Call ``imatlab_export_fig('fig2plotly')`` at the beginning of the notebook.

Other valid values for the exporter (which do not rely on Plotly) are
``'print-png'`` and ``'print-jpeg'``, which create static images in the
respective formats.

For further customization, you may override the ``imatlab_export_fig`` function
(the default version is provided by ``imatlab`` and added to the MATLAB path).
This function is called with no arguments after each notebook cell is executed,
while the current directory is temporarily switched to a temporary folder; this
function should return a cell array of filenames with ``.html``, ``.png``, or
``.jpg``/``.jpeg`` extension.  The corresponding files, which should have been
created by the function, will be loaded into the notebook.


Environment variables
---------------------

``IMATLAB_CONNECT``
   If this environment variable is set to a valid MATLAB identifier, the kernel
   will attempt to connect to the shared engine with that name.  If it is set
   to another non-empty value, it will connect to any existing shared engine.

``IMATLAB_CD``
   If this environment variable is set, the engine's working directory will be
   changed to match the kernel's working directory.

``IMATLAB_CONNECT`` needs to be set outside of MATLAB (as it is checked before
the connection to the engine is made).  Other environment variables can be set
either outside of MATLAB (before starting the kernel) or from within MATLAB
(using ``setenv``).

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
  shared with standard MATLAB sessions.  Note that if the file does not exist
  (e.g. if the **don't save history file** option is set, or in a console-only
  setup), history not be reloaded into later sessions.  (A PR for loading
  ``history.m`` instead would be welcome; it would need to properly parse
  multiline inputs in that file.)
- Synchronous output is supported on Linux and OSX (see above).
- There is no magics systems, as MATLAB already provides many functions for
  this purpose (``cd``, ``edit``, etc.).
- Inline graphics can be based on ``plotly``, and thus interactive.
