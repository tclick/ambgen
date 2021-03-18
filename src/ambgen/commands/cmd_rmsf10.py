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
import logging.config
from pathlib import Path
from typing import NoReturn

import click
import matplotlib.pyplot as plt
import MDAnalysis as mda
import numpy as np
import pytraj as pt
from MDAnalysis.core.topologyattrs import Tempfactors
from pydantic import PositiveInt, confloat, conint

from .. import create_logging_dict
from ..libs import rmsf
from ..libs.typing import DataFrame, PathLike, Trajectory
from ..libs.utils import _GRAPHS, save_data


def save_pdb(
    topology: PathLike,
    trajectory: PathLike,
    /,
    *,
    filename: PathLike,
    data: DataFrame,
) -> NoReturn:
    """Replaces the temperature factors in a PDB with the rmsf10 fluctuations.

    Parameters
    ----------
    topology : PathLike
        topology file
    trajectory : PathLike
        trajectory file
    filename : PathLike
        Structure file with rmsf10 data
    data : :class:`rmsf.RmsfData`
        Fluctuations data
    """
    universe = mda.Universe(topology, trajectory)
    universe.add_TopologyAttr(Tempfactors(data.values[:, -1]))
    with mda.Writer(filename, n_atoms=universe.atoms.n_atoms) as pdb:
        pdb.write(universe.atoms)


def save_fig(
    n_residues: int,
    /,
    *,
    data: DataFrame,
    filename: PathLike,
    n_modes: PositiveInt = 10,
    figtype: str = "bar",
    width: PositiveInt = 10,
    dpi: confloat(strict=True, ge=100.0) = 600.0,
) -> NoReturn:
    """Translate C-alpha fluctuation data into a bar graph.

    Parameters
    ----------
    n_residues : int
        Number of residues in the system
    data : DataFrame
        Fluctuations data
    filename: PathLike
        Image filename
    n_modes: int
        Number of modes used in fluctuation calculation
    figtype: str
        Type of graph to draw
    width: int
        Width of the x-axis lables
    dpi: float
        Resolution of the figure

    Returns
    -------

    """
    calpha: DataFrame = data.reset_index()
    fig: plt.Figure = plt.figure(figsize=plt.figaspect(0.25))
    ax = fig.add_subplot(1, 1, 1)
    _GRAPHS[figtype](
        x=calpha.columns[0], y=calpha.columns[-1], data=calpha, color="blue", ax=ax
    )
    ax.set_xlabel("Residue #")
    ax.set_ylabel(f"RMSF{n_modes} (Å)")
    ax.set_xticks(np.arange(width, n_residues + width, width))
    fig.suptitle(f"RMSF{n_modes}of C-alpha")
    fig.tight_layout()
    fig.savefig(filename, dpi=dpi)


@click.command("rmsf10", short_help="Calculate RMSF of first 10 eigenvectors")
@click.option(
    "-s",
    "--top",
    metavar="FILE",
    default=Path.cwd().joinpath("input.parm7").as_posix(),
    show_default=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    help="Topology",
)
@click.option(
    "-f",
    "--traj",
    metavar="FILE",
    default=Path.cwd().joinpath("input.trj").as_posix(),
    show_default=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    help="Trajectory",
)
@click.option(
    "-o",
    "--outfile",
    "pdbfile",
    metavar="FILE",
    default=Path.cwd().joinpath("rmsf10.pdb").as_posix(),
    show_default=True,
    type=click.Path(exists=False, file_okay=True, dir_okay=False, resolve_path=True),
    help="PDB file",
)
@click.option(
    "-d",
    "--data",
    "datadir",
    metavar="DIR",
    default=Path.cwd().as_posix(),
    show_default=True,
    type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
    help="Data directory",
)
@click.option(
    "-l",
    "--logfile",
    metavar="LOG",
    show_default=True,
    default=Path.cwd().joinpath("rmsf10.log").as_posix(),
    type=click.Path(exists=False, file_okay=True, dir_okay=False, resolve_path=True),
    help="Log file",
)
@click.option(
    "-b",
    "start",
    metavar="START",
    default=1,
    show_default=True,
    type=click.IntRange(min=1, clamp=True),
    help="Starting trajectory frame",
)
@click.option(
    "-e",
    "stop",
    metavar="STOP",
    default=0,
    show_default=True,
    type=click.IntRange(min=0, clamp=True),
    help="Final trajectory frame",
)
@click.option(
    "--dt",
    "offset",
    metavar="OFFSET",
    default=1,
    show_default=True,
    type=click.IntRange(min=1, clamp=True),
    help="Trajectory output offset (0 = last frame)",
)
@click.option(
    "-n",
    "--nmodes",
    metavar="NMODES",
    default=10,
    show_default=True,
    type=click.INT,
    help="Number of eigenmodes",
)
@click.option(
    "--it",
    "image_type",
    default="png",
    type=click.Choice(["png", "pdf", "svg", "ps"], case_sensitive=False),
    help="Output type for figure",
)
@click.option(
    "--ft",
    "fig_type",
    default="bar",
    type=click.Choice(["bar", "line"], case_sensitive=False),
    help="Graph type to draw",
)
@click.option(
    "--width",
    default=10,
    type=click.IntRange(min=1, clamp=True),
    help="Width of x-labels",
)
@click.option(
    "--dpi",
    default=600.0,
    type=click.FloatRange(min=100.0, clamp=True),
    help="Resolution of the figure",
)
@click.option("--image", is_flag=True, help="Save graph of rmsf10 for C-alpha")
def cli(
    top: PathLike,
    traj: PathLike,
    pdbfile: PathLike,
    datadir: PathLike,
    logfile: PathLike,
    start: PositiveInt,
    stop: PositiveInt,
    offset: PositiveInt,
    nmodes: PositiveInt,
    image_type: str,
    fig_type: str,
    width: conint(strict=True, ge=1),
    image: bool,
    dpi: confloat(strict=True, ge=100.0),
):
    # Setup logging
    logging.config.dictConfig(create_logging_dict(logfile))
    logger: logging.Logger = logging.getLogger(__name__)

    parent = Path(pdbfile).parent

    logger.debug(f"Loading {traj} with {top}")
    topology: pt.Topology = pt.load_topology(top)
    if stop > 0:
        frame_slice = np.arange(start, stop, offset)
        trajectory: Trajectory = pt.load(traj, top=topology, frame_indices=frame_slice)
    else:
        trajectory: Trajectory = pt.load(traj, top=topology)

    data: rmsf.RmsfData = rmsf.calculate_rmsf(trajectory, n_modes=nmodes)

    # Save data to text files
    logger.info(f"Saving all data into {datadir}")
    save_data(data_dir=datadir, data=data)

    # Write data to a PDB file
    logger.info(f"Writing rmsf{nmodes:d} to {pdbfile}")
    save_pdb(top, traj, filename=pdbfile, data=data.fluctuations)

    if image:
        filename = parent.joinpath(Path(pdbfile).with_suffix(f".{image_type.lower()}"))
        logger.info(f"Saving bar plot to {filename}")
        save_fig(
            topology.n_residues,
            data=data.calpha,
            filename=filename,
            n_modes=nmodes,
            width=width,
            dpi=dpi,
        )
