# --------------------------------------------------------------------------------------
#  Copyright (C) 2020–2021 by Timothy H. Click <tclick@okstate.edu>
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
from pytest_mock import MockerFixture

from ambgen.cli import main

from ..datafile import PDB

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
LOGGER = logging.getLogger(name="ambgen.commands.cmd_simfiles")

if not sys.warnoptions:
    import os
    import warnings

    warnings.simplefilter("default")  # Change the filter in this process
    os.environ["PYTHONWARNINGS"] = "default"  # Also affect subprocesses


class TestSolvate:
    @pytest.mark.runner_setup()
    def test_help(self, cli_runner: CliRunner, tmp_path: Path):
        """
        GIVEN the solvate subcommand
        WHEN the help option is invoked
        THEN the help output should be displayed
        """
        result = cli_runner.invoke(
            main,
            args=(
                "solvate",
                "-h",
            ),
            env=dict(AMBERHOME=tmp_path.as_posix()),
        )

        assert "Usage:" in result.output
        assert result.exit_code == 0

    @pytest.mark.runner_setup()
    def test_simfiles(
        self, cli_runner: CliRunner, tmp_path: Path, mocker: MockerFixture
    ):
        """
        GIVEN a PDB file
        WHEN the solvate subcommand is called
        THEN the system is solvated
        """
        logfile = tmp_path.joinpath("solvate.log")

        prefix = tmp_path.joinpath("rnase2_solvate")
        result = cli_runner.invoke(
            main,
            args=(
                "solvate",
                "-i",
                PDB,
                "-p",
                prefix.as_posix(),
                "-l",
                logfile.as_posix(),
            ),
            env=dict(AMBERHOME=tmp_path.as_posix()),
        )

        assert result.exit_code == 0
        assert logfile.exists()
        assert prefix.with_suffix(".pdb").exists()
        assert prefix.with_suffix(".crd").exists()
        assert prefix.with_suffix(".parm7").exists()
