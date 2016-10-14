from contextlib import ExitStack
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import time
from xml.etree import ElementTree as ET

from ipykernel.kernelbase import Kernel
import matlab.engine
from matlab.engine import MatlabExecutionError

from . import _redirection, __version__


class MatlabHistory:
    # Parsing of `History.xml` by MATLAB is ridiculously fragile...

    def __init__(self, path):
        self._path = path
        self._et = ET.parse(str(path))
        root = self._et.getroot()
        self._session = ET.SubElement(root, "session")
        self._session.text = "\n"
        self._session.tail = "\n"
        command = ET.SubElement(
            self._session, "command",
            {"time_stamp": format(int(time.time() * 1000), "x")})
        command.text = time.strftime("%%-- %m/%d/%Y %I:%M:%S %p --%%")
        command.tail = "\n"
        self._as_list = [
            (session_number, line_number, elem.text)
            for session_number, session in enumerate(list(root), 1)
            for line_number, elem in enumerate(session, 1)]

    def append(self, text, elapsed, success):
        command = ET.SubElement(
            self._session, "command",
            {"execution_time": str(int(elapsed * 1000)),
             **({} if success else {"error": "true"})})
        command.text = text
        command.tail = "\n"
        last_session, last_line, _ = self._as_list[-1]
        self._as_list.append((last_session, last_line + 1, text))
        with self._path.open("r+b") as file:
            next(file)  # Skip the XML declaration, which is fragile.
            file.truncate()
            self._et.write(file, "utf-8", xml_declaration=False)

    @property
    def as_list(self):
        return self._as_list


class MatlabKernel(Kernel):
    implementation = banner = "MATLAB Kernel"
    implementation_version = __version__
    language = "matlab"

    @property
    def language_info(self):
        return {
            "name": "matlab",
            "version": self._engine.version(),
            "mimetype": "text/x-matlab",
            "file_extension": ".m",
            "pygments_lexer": "matlab",
            "codemirror_mode": "octave",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._engine = matlab.engine.start_matlab()
        self._history = MatlabHistory(
            Path(self._engine.prefdir(), "History.xml"))

    def do_execute(
            self, code, silent, store_history=True,
            # Neither of these is supported.
            user_expressions=None, allow_stdin=False):

        status = "ok"

        with ExitStack() as stack:

            @stack.push
            def __exit__(exc_type, exc_value, tb):
                nonlocal status
                if isinstance(exc_value, (SyntaxError,
                                          MatlabExecutionError,
                                          KeyboardInterrupt)):
                    status = "error"
                    return True  # Suppress it.

            for name in ["stdout", "stderr"]:
                stream = getattr(sys, "__{}__".format(name))
                stack.enter_context(
                    _redirection.redirect(
                        stream.fileno(),
                        ((lambda s: None) if silent else
                         (lambda s, *, _name=name, _stream=stream:
                          self.send_response(
                              self.iopub_socket,
                              "stream",
                              {"name": _name,
                               "text": s.decode(_stream.encoding)})))))
            start = time.perf_counter()
            future = self._engine.eval(code, nargout=0, async=True)
            future.result()

        if store_history:
            elapsed = time.perf_counter() - start
            self._history.append(code, elapsed, status == "ok")

        return {"status": status,
                "execution_count": self.execution_count}

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
        info_s, = self._engine.eval(
            "cell(com.mathworks.jmi.MatlabMCR().mtGetCompletions('{}', {}))"
            .format(code[:cursor_pos], cursor_pos))
        info = json.loads(info_s)
        return {"cursor_start": cursor_pos - len(info["replacedString"]),
                "cursor_end": cursor_pos,
                "matches": [entry["popupCompletion"]
                            for entry in info["finalCompletions"]]}

    # Not supported:
    # def do_inspect(self, code, cursor_pos, detail_level=0):
    #     ...

    def do_history(
            self, hist_access_type, output, raw, session=None, start=None,
            stop=None, n=None, pattern=None, unique=False):
        return {"history": self._history.as_list}

    def do_is_complete(self, code):
        with TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test_complete.m").write_text(code)
            self._engine.eval(
                "try, pcode {} -inplace; catch, end".format(tmpdir),
                nargout=0)
            if Path(tmpdir, "test_complete.p").exists():
                return {"status": "complete"}
            else:
                return {"status": "incomplete"}

    def do_shutdown(self, restart):
        self._engine.exit()
        if restart:
            self._engine = matlab.engine.start_matlab()
