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

import numpy as np
import pytest
import pytraj as pt

from ambgen.cli import main

from ..datafile import TOPWW, TRJWW

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
LOGGER = logging.getLogger(name="ambgen.commands.cmd_rms2d")

if not sys.warnoptions:
    import os
    import warnings

    warnings.simplefilter("default")  # Change the filter in this process
    os.environ["PYTHONWARNINGS"] = "default"  # Also affect subprocesses


class TestRms2d:
    @pytest.fixture
    def data(self):
        topology = pt.load_topology(TOPWW)
        trajectory = pt.iterload(TRJWW, top=topology)
        N_FRAMES = trajectory.n_frames
        return np.random.random((N_FRAMES, N_FRAMES))

    @pytest.mark.runner_setup
    def test_help(self, cli_runner, tmp_path: Path):
        """
        GIVEN the rms2d subcommand
        WHEN the help option is invoked
        THEN the help output should be displayed
        """
        result = cli_runner.invoke(
            main,
            args=(
                "rms2d",
                "-h",
            ),
            env=dict(AMBERHOME=tmp_path.as_posix()),
        )

        assert "Usage:" in result.output
        assert result.exit_code == 0

    @pytest.mark.runner_setup
    def test_calculate_rms2d(self, cli_runner, mocker, tmp_path, data):
        """
        GIVEN a topology and a trajectory file
        WHEN the rms2d subcommand is called
        THEN calculate the 2D r.m.s.d. of a trajectory
        """
        logfile = tmp_path.joinpath("rms2d.log")
        outfile = tmp_path.joinpath("out.csv")
        img_file = outfile.with_suffix(".png")

        patch = mocker.patch.object(pt, "rms2d", return_value=data)
        result = cli_runner.invoke(
            main,
            args=(
                "rms2d",
                "-s",
                TOPWW,
                "-f",
                TRJWW,
                "-o",
                outfile.as_posix(),
                "-l",
                logfile.as_posix(),
                "--image",
            ),
        )

        assert result.exit_code == 0
        assert logfile.exists()
        assert outfile.exists()
        assert outfile.stat().st_size > 0
        assert img_file.exists()
        assert img_file.stat().st_size > 0
        patch.assert_called_once()
