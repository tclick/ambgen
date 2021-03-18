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
import logging
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

import ambgen.commands.cmd_simfiles
from ambgen.cli import main

from ..datafile import TOP

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
LOGGER = logging.getLogger(name="ambgen.commands.cmd_simfiles")

if not sys.warnoptions:
    import os
    import warnings

    warnings.simplefilter("default")  # Change the filter in this process
    os.environ["PYTHONWARNINGS"] = "default"  # Also affect subprocesses


class TestSimFiles:
    @pytest.mark.runner_setup()
    def test_help(self, cli_runner: CliRunner, tmp_path: Path):
        """
        GIVEN the simfiles subcommand
        WHEN the help option is invoked
        THEN the help output should be displayed
        """
        result = cli_runner.invoke(
            main,
            args=(
                "simfiles",
                "-h",
            ),
            env=dict(AMBERHOME=tmp_path.as_posix()),
        )

        assert "Usage:" in result.output
        assert result.exit_code == 0

    @pytest.mark.runner_setup()
    @pytest.mark.parametrize("sim_type", "equil prod scripts".split())
    def test_simfiles(self, cli_runner, sim_type, tmp_path, mocker):
        """
        GIVEN a simulation type
        WHEN the simfiles subcommand is called
        THEN write Amber simulation files in subdirectories
        """
        logfile = tmp_path.joinpath("simfiles.log")

        patch = mocker.patch.object(
            ambgen.commands.cmd_simfiles, "_write_template", autospec=True
        )
        result = cli_runner.invoke(
            main,
            args=(
                "simfiles",
                "-s",
                TOP,
                "-d",
                tmp_path,
                "-p",
                "rnase2",
                "-l",
                logfile.as_posix(),
                "--type",
                sim_type,
                "--home",
                tmp_path.as_posix(),
            ),
            env=dict(AMBERHOME=tmp_path.as_posix()),
        )
        subdir = tmp_path.joinpath(sim_type.title())

        assert result.exit_code == 0
        assert logfile.exists()
        assert subdir.exists()
        patch.assert_called()
