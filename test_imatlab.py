import re

import jupyter_kernel_test as jkt


class IMatlabTests(jkt.KernelTests):

    kernel_name = "imatlab"
    language_name = "matlab"
    file_extension = ".m"
    code_hello_world = "fprintf('hello, world')"
    code_stderr = "fprintf(2, 'oops')"
    completion_samples = [
        {"text": "matlabroo", "matches": ["matlabroot"]},
        # Not including prefix (only `cursor_start:cursor_end`).
        {"text": "ls setup.", "matches": ["setup.cfg", "setup.py"]},
    ]
    complete_code_samples = [
        "1+1",
        "for i=1:3\ni\nend",
        # FIXME The following should be considered "invalid", but really all
        # that matters is that they are not "incomplete".
        "function test_complete",
        "function test_complete, end",
        "classdef test_complete, end",
    ]
    incomplete_code_samples = [
        "for i=1:3",
        # FIXME We'd rather consider this as "invalid".
        "classdef test_complete",
    ]
    invalid_code_samples = [
        "for end",
    ]
    code_display_data = [
        {"code": "set(0, 'defaultfigurevisible', 'off'); "
                 "imatlab_export_fig('print-png'); "
                 "plot([1, 2]);",
         "mime": "image/png"},
    ]
    code_inspect_sample = "help"

    # FIXME We actually never send "data" back -- only print it.

    # code_generate_error = "[1, 2] + [3, 4, 5];"
    # code_execute_result = [
    #     {"code": "1+1;", "result": ""},
    # ]

    # FIXME History operations are not tested as (as mentioned in the docs)
    # they are unnecessary (re-implemented by the frontends, overly complex).

    # supported_history_operations = ["tail", "range", "search"]
    # code_history_pattern = [
    #     re.escape("1+1"),
    # ]

    # FIXME Not available.

    # code_page_something = None
    # code_clear_output = None
