# --------------------------------------------------------------------------------------
#  Copyright (C) 2020—2021 by Timothy H. Click <tclick@okstate.edu>
#
#  Permission to use, copy, modify, and/or distribute this software for any purpose
#  with or without fee is hereby granted.
#
#  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
#  REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
#  FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
#  INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
#  OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
#  TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
#  THIS SOFTWARE.
# --------------------------------------------------------------------------------------
"""Test cases for the __main__ module."""
import runpy

import pytest

import ambgen
import ambgen.__main__
import ambgen.cli
from ambgen import create_logging_dict


class TestMain:
    def test_main_module(self):
        """
        GIVEN the main command-line module
        WHEN the module is executed
        THEN the `ambgen` module should be present
        """
        sys_dict = runpy.run_module("ambgen.__main__")
        assert sys_dict["__name__"] == "ambgen.__main__"
        assert isinstance(sys_dict["main"], ambgen.cli._ComplexCLI)

    def test_main_help(self, cli_runner):
        """
        GIVEN the main command-line interface
        WHEN the '-h' or '--help' argument is provided
        THEN the help screen should appear
        """
        result = cli_runner.invoke(ambgen.cli.main, args=("-h",))
        result2 = cli_runner.invoke(ambgen.cli.main, args=("--help",))

        assert "Usage:" in result.output
        assert result.exit_code == 0
        assert result.output == result2.output

    def test_main_version(self, cli_runner):
        """
        GIVEN the main command-line interface
        WHEN the '--version' argument is provided
        THEN the version should print to the screen
        """
        result = cli_runner.invoke(ambgen.cli.main, args=("--version",))
        assert ambgen.__version__ in result.output


class TestLoggingDict:
    def test_create_logging_dict(self):
        """Check create_logging_dict return."""
        logfile = "test.log"
        assert isinstance(create_logging_dict(logfile), dict)

    def test_create_logging_dict_error(self):
        """
        GIVEN create_logging_dict function
        WHEN an empty string for a filename is provided
        THEN an exception is thrown
        """
        logfile = ""
        with pytest.raises(ValueError):
            create_logging_dict(logfile)
