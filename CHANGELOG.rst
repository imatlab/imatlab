v0.3
====

- When an error occurs, don't display the outermost error from `eval`.
- Clarify message when errors come from plotly.
- Drop support for Jupyter 5.0 (requires workarounds); fix support for IPython
  6.2.

v0.2
====

- Notebooks are saved as MATLAB files with ``%%``-separated cells.
- Run the `imatlab_export_fig` hook after each notebook cell.  Support
  `plotly`-based inline graphics.
- If both `IMATLAB_CONNECT` and `IMATLAB_CD` are set, forcefully change
  MATLAB's working directory to match the kernel's.
- Miscellaneous improvements and bugfixes for the command history, the code
  completeness checker, and engine shutdown.

v0.1
====

- First public release.
