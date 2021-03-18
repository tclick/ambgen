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
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict

import pandas as pd
import pytraj as pt
from pytraj import matrix

from .typing import ArrayLike, FrameOrSeries, Trajectory

logger = logging.getLogger(__name__)


@dataclass
class RmsfData:
    rmsd: ArrayLike
    covariance: ArrayLike
    eigenvalues: ArrayLike
    eigenvectors: ArrayLike
    fluctuations: FrameOrSeries
    calpha: FrameOrSeries


def calculate_rmsf(trajectory: Trajectory, /, *, n_modes: int = 10) -> RmsfData:
    """Calculate the root mean square fluctuations of trajectory eigenvectors.

    Parameters
    ----------
    trajectory : :class:`pytraj.Trajectory` or :class:`pytraj.TrajectoryIterator`
        Trajectory data
    n_modes : int
        Number of eigenmodes to calculate

    Returns
    -------
    Data object containing information about the calculations.
    """
    # Calculate mass-weighted covariance matrix, eigenvalues,
    # eigenvectors, and the r.m.s.f. modes
    logger.debug("Aligning trajectory by mass-weighted r.m.s.d.")
    rmsd: ArrayLike = pt.rmsd(traj=trajectory, mass=True, top=trajectory.topology)

    logger.debug("Calculating the mass-weighted covariance matrix.")
    logger.warning("Depending upon the trajectory size, this could take a while.")
    covariance: ArrayLike = matrix.mwcovar(traj=trajectory, top=trajectory.topology)

    logger.debug("Performing eigendecomposition of the mass-weighted covariance matrix")
    eigenvectors, eigenvalues = matrix.diagonalize(
        covariance, n_vecs=n_modes, scalar_type="mwcovar", mass=trajectory.topology.mass
    )

    logger.debug("Analyzing mode fluctuations from eigendecomposition")
    fluctuations: Dict = pt.analyze_modes(
        "fluct", eigenvectors, eigenvalues, options=f"beg 1 end {n_modes:d}"
    )
    fluctuations: FrameOrSeries = pd.DataFrame.from_dict(fluctuations)
    fluctuations.index.name = "#Atom_no."
    fluctuations.index += 1

    logger.debug("Collecting r.m.s.f. for CA only")
    mask: ArrayLike = trajectory.topology.select("@CA")
    calpha: FrameOrSeries = fluctuations.iloc[mask]
    calpha.index.name = "#Residue_no."
    calpha.index = [_.original_resid for _ in trajectory.topology.residues]

    return RmsfData(
        rmsd=rmsd,
        covariance=covariance,
        eigenvalues=eigenvalues,
        eigenvectors=eigenvectors,
        fluctuations=fluctuations,
        calpha=calpha,
    )
