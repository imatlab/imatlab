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


Inline Graphics
---------------------

To use Plotly inline graphics in the notebook, the `Plotly MATLAB API
<https://plot.ly/matlab/getting-started/>`_ must be installed.

1. Clone `plotly/MATLAB-Online <https://github.com/plotly/MATLAB-Online>`_ or
   download the `zip <https://github.com/plotly/MATLAB-api/archive/master.zip>`_.
2. Recursively add the resulting extracted folders to the MATLAB path:
   ``addpath(genpath(<Plotly MATLAB API path>))``.
3. In MATLAB, run: ``getplotlyoffline('https://cdn.plot.ly/plotly-latest.min.js')``
   to copy the javascript files.
4. Set the ``IMATLAB_EXPORT_FIG`` environment variable to use ``fig2plotly`` as
   described below.


Environment variables
---------------------

``IMATLAB_CONNECT``
   If this environment variable is set to a valid MATLAB identifier, the kernel
   will attempt to connect to the shared engine with that name.  If it is set
   to another non-empty value, it will connect to any existing shared engine.

``IMATLAB_CD``
   If this environment variable is set, the engine's working directory will be
   changed to match the kernel's working directory.

``IMATLAB_EXPORT_FIG``
   This environment variable can be set to a MATLAB expression, representing
   a function of one argument (either a quoted function name, or a function
   handle).  If it is, and the current frontend is a notebook, then, after
   each input is evaluated, the given function is evaluated for each figure
   handle, while the current folder is changed to a temporary folder.  Any
   ``.html``, ``.png`` or ``.jpeg`` file that is created is displayed using
   IPython's ``display_data`` mechanism (``.html`` files will also trigger the
   initialization of ``plotly``’s notebook mode.).

   For example, set (e.g., from MATLAB, in ``startup.m``)::

      setenv('IMATLAB_EXPORT_FIG', func2str(@(h) eval([ ...
         'fig2plotly(h, ''filename'', [tempname(''.''), ''.html''], ', ...
                       '''offline'', true, ''open'', false); ', ...
         'close(h);'])));

   to export figures as html with plotly; or set::

     setenv('IMATLAB_EXPORT_FIG', func2str(@(h) eval([ ...
         'print(h, [tempname(''.''), ''.png''], ''-dpng'')', ...
         'close(h);'])));

   to export figures as static png files.

   Note the use of ``eval`` to squeeze in two statements in the function handle
   (export the figure, and close it).

   It may be helpful to wrap such settings in your own helper functions.

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
