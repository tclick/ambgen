# --------------------------------------------------------------------------------------
#  Copyright (C) 2021 by Timothy H. Click <tclick@okstate.edu>
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
import sys

import pytest

from ambgen.cli import main
from ambgen.commands import FILE_MODE

if not sys.warnoptions:
    import os
    import warnings

    warnings.simplefilter("default")  # Change the filter in this process
    os.environ["PYTHONWARNINGS"] = "default"  # Also affect subprocesses


class TestSetup:
    @pytest.mark.runner_setup()
    def test_setup_help(self, cli_runner, tmp_path):
        """
        GIVEN the setup subcommand
        WHEN the help option is invoked
        THEN the help output should be displayed
        """
        result = cli_runner.invoke(
            main,
            args=(
                "setup",
                "-h",
            ),
        )

        assert "Usage:" in result.output
        assert result.exit_code == 0

    @pytest.mark.runner_setup()
    def test_setup(self, cli_runner, tmp_path):
        """
        GIVEN a subdirectory
        WHEN the setup subcommand is called
        THEN create a subdirectory structure for simulation and analysis
        """
        logfile = tmp_path.joinpath("setup.log")
        result = cli_runner.invoke(
            main,
            args=(
                "setup",
                "-d",
                tmp_path,
                "-l",
                logfile.as_posix(),
            ),
        )

        assert logfile.exists()
        assert result.exit_code == 0
        assert tmp_path.joinpath("Equil", "md16").exists()
        assert tmp_path.joinpath("Prod", "production").exists()
        assert (
            oct(tmp_path.joinpath("Equil").stat().st_mode)[-3:] == oct(FILE_MODE)[-3:]
        )
