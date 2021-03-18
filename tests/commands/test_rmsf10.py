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
from dataclasses import make_dataclass
from pathlib import Path

import MDAnalysis as mda
import numpy as np
import pandas as pd
import pytest
import pytraj as pt

import ambgen.libs.rmsf
import ambgen.libs.utils
from ambgen.cli import main

from ..datafile import TOPWW, TRJWW

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
LOGGER = logging.getLogger(name="ambgen.commands.cmd_rmsf10")

if not sys.warnoptions:
    import os
    import warnings

    warnings.simplefilter("default")  # Change the filter in this process
    os.environ["PYTHONWARNINGS"] = "default"  # Also affect subprocesses


class TestRmsf10:
    @pytest.fixture
    def data(self):
        topology = pt.load_topology(TOPWW)
        trajectory = pt.iterload(TRJWW, top=topology)
        N_ATOMS = topology.n_atoms
        N_RESIDUES = topology.n_residues
        N_FRAMES = trajectory.n_frames

        Data = make_dataclass(
            "Data",
            [
                ("rmsd", np.ndarray),
                ("covariance", np.ndarray),
                ("eigenvalues", np.ndarray),
                ("eigenvectors", np.ndarray),
                ("fluctuations", pd.DataFrame),
                ("calpha", pd.DataFrame),
            ],
        )
        return Data(
            rmsd=np.random.rand(N_FRAMES),
            covariance=np.random.random((N_ATOMS * 3, N_ATOMS * 3)),
            eigenvalues=np.random.rand(N_ATOMS * 3),
            eigenvectors=np.random.random((N_ATOMS * 3, N_ATOMS * 3)),
            fluctuations=pd.DataFrame(np.random.random((N_ATOMS, 4))),
            calpha=pd.DataFrame(np.random.random((N_RESIDUES, 4))),
        )

    @pytest.mark.runner_setup
    def test_help(self, cli_runner, tmp_path: Path):
        """
        GIVEN the rmsf10 subcommand
        WHEN the help option is invoked
        THEN the help output should be displayed
        """
        result = cli_runner.invoke(
            main,
            args=(
                "rmsf10",
                "-h",
            ),
            env=dict(AMBERHOME=tmp_path.as_posix()),
        )

        assert "Usage:" in result.output
        assert result.exit_code == 0

    @pytest.mark.runner_setup
    def test_calculate_rmsf10(self, cli_runner, mocker, tmp_path, data):
        """
        GIVEN a topology and a trajectory file
        WHEN the rmsf10 subcommand is called
        THEN calculate the fluctuations and save data to text and image files
        """
        logfile = tmp_path.joinpath("rmsf10.log")

        patch = mocker.patch.object(
            ambgen.libs.rmsf, "calculate_rmsf", return_value=data
        )
        save_data = mocker.patch.object(ambgen.libs.utils, "save_data", autospec=True)
        writer = mocker.patch.object(mda, "Writer", autospec=True)
        result = cli_runner.invoke(
            main,
            args=(
                "rmsf10",
                "-s",
                TOPWW,
                "-f",
                TRJWW,
                "-o",
                tmp_path.joinpath("out.pdb").as_posix(),
                "-d",
                tmp_path.as_posix(),
                "-l",
                logfile.as_posix(),
                "--image",
            ),
        )

        assert result.exit_code == 0
        assert logfile.exists()
        patch.assert_called_once()
        save_data.assert_called_once()
        writer.assert_called_once()
