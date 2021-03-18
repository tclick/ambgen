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
from ..datafile import TOPWW, TRJWW

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
LOGGER = logging.getLogger(name="ambgen.commands.cmd_simfiles")

if not sys.warnoptions:
    import os
    import warnings

    warnings.simplefilter("default")  # Change the filter in this process
    os.environ["PYTHONWARNINGS"] = "default"  # Also affect subprocesses


class TestRmsf:
    @pytest.mark.runner_setup()
    def test_help(self, cli_runner: CliRunner, tmp_path: Path):
        """
        GIVEN the rmsf subcommand
        WHEN the help option is invoked
        THEN the help output should be displayed
        """
        result = cli_runner.invoke(
            main,
            args=(
                "rmsf",
                "-h",
            ),
            env=dict(AMBERHOME=tmp_path.as_posix()),
        )

        assert "Usage:" in result.output
        assert result.exit_code == 0

    @pytest.mark.runner_setup()
    @pytest.mark.parametrize("rmsf_type", "ca cab heavy all".split())
    def test_simfiles(
        self,
        cli_runner: CliRunner,
        rmsf_type: str,
        tmp_path: Path,
        mocker: MockerFixture,
    ):
        """
        GIVEN a topology and trajectory file
        WHEN the rmsf subcommand is called
        THEN the root-mean-square fluctuations per residue is calculated
        """
        logfile = tmp_path.joinpath("rmsf.log")
        image = tmp_path.joinpath("rmsf.png")

        result = cli_runner.invoke(
            main,
            args=(
                "rmsf",
                "-s",
                TOPWW,
                "-f",
                TRJWW,
                "-o",
                image,
                "-l",
                logfile.as_posix(),
                "-d",
                tmp_path,
                "-t",
                rmsf_type,
                "--image",
            ),
            env=dict(AMBERHOME=tmp_path.as_posix()),
        )

        assert result.exit_code == 0
        assert logfile.exists()
        assert tmp_path.joinpath(Path(rmsf_type).with_suffix(".csv"))
        assert image.exists()
