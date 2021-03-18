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

import numpy as np
import pytest
import pytraj as pt
from numpy import testing
from pytest_mock import MockerFixture
from pytraj import matrix

from ambgen.libs import rmsf

from ..datafile import TOPWW, TRJWW


class TestRmsf:
    @pytest.fixture
    def topology(self) -> pt.Topology:
        return pt.load_topology(TOPWW)

    @pytest.fixture
    def trajectory(self, topology) -> pt.Trajectory:
        return pt.load(TRJWW, top=topology)

    @pytest.fixture
    def eigenval(self, topology) -> np.ndarray:
        return np.random.random(topology.n_atoms * 3)

    @pytest.fixture
    def eigenvec(self, topology) -> np.ndarray:
        return np.random.random((topology.n_atoms * 3, topology.n_atoms * 3))

    def test_calculate(
        self, mocker: MockerFixture, topology, trajectory, eigenval, eigenvec
    ):
        """
        GIVEN a topology and trajectory files
        WHEN calculating the fluctuations of the trajectory
        THEN an object with various information is returned
        """
        N_ATOMS = topology.n_atoms
        N_RESIDUES = topology.n_residues

        patch = mocker.patch.object(
            matrix, "diagonalize", return_value=(eigenvec, eigenval), autospec=True
        )
        data = rmsf.calculate_rmsf(trajectory)

        patch.assert_called_once()
        testing.assert_allclose(data.eigenvalues, eigenval)
        testing.assert_allclose(data.eigenvectors, eigenvec)
        testing.assert_equal(data.fluctuations.shape, (N_ATOMS, 4))
        testing.assert_equal(data.covariance.shape, (N_ATOMS * 3, N_ATOMS * 3))
        testing.assert_equal(data.calpha.shape, (N_RESIDUES, 4))
        assert data.rmsd.size == trajectory.n_frames
