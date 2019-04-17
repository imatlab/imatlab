import base64
from contextlib import ExitStack
from io import StringIO
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
from unittest.mock import patch
import uuid
import warnings
import weakref
from xml.etree import ElementTree as ET

import ipykernel.kernelspec
from ipykernel.kernelbase import Kernel
import IPython
from IPython.core.interactiveshell import InteractiveShell

# Work around LD_PRELOAD tricks played by MATLAB by looking for a working
# import order.
if subprocess.call(
        [sys.executable, "-c", "import plotly, matlab.engine"],
        stderr=subprocess.DEVNULL) == 0:
    import plotly
    import matlab.engine
    from matlab.engine import EngineError, MatlabExecutionError
elif subprocess.call(
        [sys.executable, "-c", "import matlab.engine, plotly"],
        stderr=subprocess.DEVNULL) == 0:
    import matlab.engine
    from matlab.engine import EngineError, MatlabExecutionError
    import plotly
else:
    import matlab.engine
    from matlab.engine import EngineError, MatlabExecutionError
    plotly = None
    warnings.warn(
        "Failed to import both matlab.engine and plotly in the same process; "
        "plotly output is unavailable.")

from . import _redirection, __version__


# Support `python -mimatlab install`.
ipykernel.kernelspec.KERNEL_NAME = "imatlab"
ipykernel.kernelspec.get_kernel_dict = lambda extra_arguments=None: {
    "argv": [sys.executable,
             "-m", __name__.split(".")[0],
             "-f", "{connection_file}"],
    "display_name": "MATLAB",
    "language": "matlab",
}


class MatlabHistory:
    # The MATLAB GUI relies on `History.xml` (which uses a ridiculously fragile
    # parser); the command line (-nodesktop) interface on `history.m`.  We read
    # the former but update both files.

    def __init__(self, prefdir):
        self._prefdir = prefdir
        self._as_list = []
        try:
            self._et = ET.parse(str(prefdir / "History.xml"))
            root = self._et.getroot()
            self._session = ET.SubElement(root, "session")
            self._session.text = "\n"
            self._session.tail = "\n"
            command = ET.SubElement(
                self._session, "command",
                {"time_stamp": format(int(time.time() * 1000), "x")})
            command.text = time.strftime("%%-- %m/%d/%Y %I:%M:%S %p --%%")
            command.tail = "\n"
            self._as_list.extend(
                (session_number, line_number, elem.text)
                for session_number, session in enumerate(list(root), 1)
                for line_number, elem in enumerate(session, 1))
        except FileNotFoundError:
            self._et = self._session = None

    def append(self, text, elapsed, success):
        if self._et is not None:
            command = ET.SubElement(
                self._session, "command",
                {"execution_time": str(int(elapsed * 1000)),
                 **({} if success else {"error": "true"})})
            command.text = text
            command.tail = "\n"
            last_session, last_line, _ = self._as_list[-1]
            self._as_list.append((last_session, last_line + 1, text))
            with (self._prefdir / "History.xml").open("r+b") as file:
                next(file)  # Skip the XML declaration, which is fragile.
                file.truncate()
                self._et.write(file, "utf-8", xml_declaration=False)
        with (self._prefdir / "history.m").open("a") as file:
            file.write(text)
            file.write("\n")

    @property
    def as_list(self):
        return self._as_list


class MatlabKernel(Kernel):
    implementation = banner = "MATLAB Kernel"
    implementation_version = __version__
    language = "matlab"

    def _call(self, *args, **kwargs):
        """Call a MATLAB function through `builtin` to bypass overloading."""
        return self._engine.builtin(*args, **kwargs)

    @property
    def language_info(self):
        # We also hook this property to `cd` into the current directory if
        # required.
        if self._call("getenv", "IMATLAB_CD"):
            self._call("cd", str(Path().resolve()))
        return {
            "name": "matlab",
            "version": self._call("version"),
            "mimetype": "text/x-matlab",
            "file_extension": ".m",
            "pygments_lexer": "matlab",
            "codemirror_mode": "octave",
            "nbconvert_exporter": "imatlab._exporter.MatlabExporter",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._silent = False

        # console, qtconsole uses `kernel-$pid`, notebook uses `kernel-$uuid`.
        self._has_console_frontend = bool(re.match(
            r"\Akernel-\d+\Z",
            Path(self.config["IPKernelApp"]["connection_file"]).stem))

        if os.name == "posix":
            with ExitStack() as stack:
                for name in ["stdout", "stderr"]:
                    stream = getattr(sys, "__{}__".format(name))
                    def callback(data, *, _name=name, _stream=stream):
                        if not self._silent:
                            self._send_stream(
                                _name, data.decode(_stream.encoding))
                    stack.enter_context(
                        _redirection.redirect(stream.fileno(), callback))
                weakref.finalize(self, stack.pop_all().close)

        self._dead_engines = []
        engine_name = os.environ.get("IMATLAB_CONNECT")
        if engine_name:
            if re.match(r"\A(?a)[a-zA-Z]\w*\Z", engine_name):
                self._engine = matlab.engine.connect_matlab(engine_name)
            else:
                self._engine = matlab.engine.connect_matlab()
        else:
            self._engine = matlab.engine.start_matlab()
        self._history = MatlabHistory(Path(self._call("prefdir")))
        self._engine.addpath(
            str(Path(sys.modules[__name__.split(".")[0]].__file__).
                with_name("data")),
            "-end")

    def _send_stream(self, stream, text):
        self.send_response(self.iopub_socket,
                           "stream",
                           {"name": stream, "text": text})

    def _send_display_data(self, data, metadata):
        # ZMQDisplayPublisher normally handles the conversion of `None`
        # metadata to {}.
        self.send_response(self.iopub_socket,
                           "display_data",
                           {"data": data, "metadata": metadata or {}})

    def do_execute(
            self, code, silent, store_history=True,
            # Neither of these is supported.
            user_expressions=None, allow_stdin=False):

        status = "ok"
        if silent:
            self._silent = True
        start = time.perf_counter()

        # The debugger may have been set e.g. in startup.m (or later), but it
        # interacts poorly with the engine.
        self._call("dbclear", "all", nargout=0)

        # Don't include the "Error using eval" before each output.
        # This does not distinguish between `x` and `eval('x')` (with `x`
        # undefined), so a better solution would be preferred.
        try_code = (
            "try, {code}\n"   # Newline needed as code may end with a comment.
            r"catch {me}, fprintf('%s\n', {me}.getReport); clear {me}; end;"
            .format(code=code,
                    me="ME{}".format(str(uuid.uuid4()).replace("-", ""))))

        if os.name == "posix":
            try:
                self._call("eval", try_code, nargout=0)
            except (SyntaxError, MatlabExecutionError, KeyboardInterrupt):
                status = "error"
            except EngineError as engine_error:
                # Check whether the engine died.
                try:
                    self._call("eval", "1")
                except EngineError:
                    self._send_stream(
                        "stderr",
                        "Please quit the front-end (Ctrl-D from the console "
                        "or qtconsole) to shut the kernel down.\n")
                    # We don't want to GC the engines as that'll lead to an
                    # attempt to close an already closed MATLAB during
                    # `__del__`, which raises an uncatchable exception.  So
                    # we just keep them around instead.
                    self._dead_engines.append(self._engine)
                    self._engine = matlab.engine.start_matlab()
                else:
                    raise engine_error
        elif os.name == "nt":
            try:
                out = StringIO()
                err = StringIO()
                self._call("eval", try_code, nargout=0, stdout=out, stderr=err)
            except (SyntaxError, MatlabExecutionError, KeyboardInterrupt):
                status = "error"
            finally:
                for name, buf in [("stdout", out), ("stderr", err)]:
                    self._send_stream(name, buf.getvalue())
        else:
            raise OSError("Unsupported OS")

        self._export_figures()

        if store_history and code:  # Skip empty lines.
            elapsed = time.perf_counter() - start
            self._history.append(code, elapsed, status == "ok")
        self._silent = False

        if status == "ok":
            return {
                "status": status,
                "execution_count": self.execution_count,
                "payload": [],
                "user_expressions": {},
            }
        elif status == "error":  # The mechanism is Python-specific.
            return {
                "status": status,
                "execution_count": self.execution_count,
                "ename": "",
                "evalue": "",
                "traceback": [],
            }

    def _export_figures(self):
        if (self._has_console_frontend
                or not len(self._call("get", 0., "children"))
                or not self._call("which", "imatlab_export_fig")):
            return
        with TemporaryDirectory() as tmpdir:
            cwd = self._call("cd")
            try:
                self._call("cd", tmpdir)
                exported = self._engine.imatlab_export_fig()
            finally:
                self._call("cd", cwd)
            for path in map(Path(tmpdir).joinpath, exported):
                if path.suffix.lower() == ".html":
                    # https://github.com/jupyter/notebook/issues/2287
                    # Delay import, as this is not a dependency otherwise.
                    import notebook
                    if notebook.__version__ == "5.0.0":
                        self._send_stream(
                            "stderr",
                            "Plotly output is not supported with "
                            "notebook==5.0.0.  Please update to a newer "
                            "version.")
                    elif not plotly:
                        self._send_stream(
                            "stderr",
                            "Failed to import both matlab.engine and plotly "
                            "in the same process; plotly output is "
                            "unavailable.")
                    else:
                        self._plotly_init_notebook_mode()
                        self._send_display_data(
                            {"text/html": path.read_text()}, {})
                elif path.suffix.lower() == ".png":
                    self._send_display_data(
                        {"image/png":
                         base64.b64encode(path.read_bytes()).decode("ascii")},
                        {})
                elif path.suffix.lower() in ".jpeg":
                    self._send_display_data(
                        {"image/jpeg":
                         base64.b64encode(path.read_bytes()).decode("ascii")},
                        {})
                elif path.suffix.lower() == ".svg":
                    self._send_display_data(
                        # Probably should read the encoding from the file.
                        {"image/svg+xml": path.read_text(encoding="ascii")},
                        {})

    def _plotly_init_notebook_mode(self):
        # Hack into display routine.  Also pretend that the InteractiveShell is
        # initialized as display() is otherwise turned into a no-op.
        with patch.multiple(IPython.core.display,
                            publish_display_data=self._send_display_data), \
             patch.multiple(InteractiveShell,
                            initialized=lambda: True):
            plotly.offline.init_notebook_mode()

    def do_complete(self, code, cursor_pos):
        # The following API is only present since MATLAB2016b:
        #     String com.mathworks.jmi.MatlabMCR.mtGetCompletions(String, int)
        # (where the second argument is the length of the first) returns a json
        # string:
        # { "replacedString": <str>,
        #   ?"partialCompletion":
        #       {"completionString": "",
        #        "offset": 0}
        #   "finalCompletions":
        #       [{ "completion":
        #              { "completionString": <str>,
        #                "offset": 0 },
        #          "matchType": <str>,
        #          "popupCompletion": <str> },
        #        ...]}
        # It's not clear whether "completionString" and "popupCompletion" are
        # ever different.
        # It is the presence of "replacedString" (or "offset") which makes
        # this API preferable to the older mtFindAllTabCompletions (used by
        # matlab_kernel).
        # Failing modes:
        #   - "" -> ""
        #   - "(" -> { "cannotComplete": true}
        info_s, = self._call(
            "eval",
            "cell(com.mathworks.jmi.MatlabMCR().mtGetCompletions('{}', {}))"
            .format(code[:cursor_pos].replace("'", "''"), cursor_pos))
        info = json.loads(info_s)
        if not info or info == {"cannotComplete": True}:
            info = {"replacedString": "", "finalCompletions": []}
        return {
            "status": "ok",
            "cursor_start": cursor_pos - len(info["replacedString"]),
            "cursor_end": cursor_pos,
            "matches": [entry["popupCompletion"]
                        for entry in info["finalCompletions"]],
            "metadata": {},
        }

    def do_inspect(self, code, cursor_pos, detail_level=0):
        try:
            token, = re.findall(r"\b[a-z]\w*(?=\(?\Z)", code[:cursor_pos])
        except ValueError:
            help = ""
        else:
            help = self._engine.help(token)  # Not a builtin.
        return {
            "status": "ok",
            "found": bool(help),
            "data": {"text/plain": help},
            "metadata": {},
        }

    def do_history(
            self, hist_access_type, output, raw, session=None, start=None,
            stop=None, n=None, pattern=None, unique=False):
        return {"history": self._history.as_list}

    def do_is_complete(self, code):
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir, "test_complete.m")
            path.write_text(code)
            errs = self._call(
                "eval",
                "feval(@(e) {{e.message}}, checkcode('-m2', '{}'))"
                .format(str(path).replace("'", "''")))
            # 'Invalid syntax': unmatched brackets.
            # 'Parse error': unmatched keywords.
            if any(err.startswith(("Invalid syntax at",
                                   "Parse error at")) for err in errs):
                return {"status": "invalid"}
            # `mtree` returns a single node tree on parse error (but not
            # otherwise -- empty inputs give no nodes, expressions give two
            # nodes).  Given that we already excluded (some) errors earlier,
            # this likely means incomplete code.
            # Using the (non-documented) `mtree` works better than checking
            # whether `pcode` successfully generates code as `pcode` refuses
            # to generate code for classdefs with a name not matching the file
            # name, whereas we actually want to report `classdef foo, end` to
            # be reported as complete (so that MATLAB errors at evaluation).
            incomplete = self._call(
                "eval",
                "builtin('numel', mtree('{}', '-file').indices) == 1"
                .format(str(path).replace("'", "''")))
            if incomplete:
                return {  # FIXME
                    "status": "incomplete",
                    "indent": "",
                }
            else:
                return {"status": "complete"}

    def do_shutdown(self, restart):
        self._call("exit", nargout=0)
        if restart:
            self._engine = matlab.engine.start_matlab()
