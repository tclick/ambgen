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

import click
import matplotlib.pyplot as plt
import numpy as np
import pytraj as pt
import seaborn as sns

from .. import create_logging_dict
from ..libs.typing import PathLike, Trajectory


@click.command("rms2d", short_help="Calculate 2D r.m.s.d..")
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
    default=Path.cwd().joinpath("rms2d.csv").as_posix(),
    show_default=True,
    type=click.Path(exists=False, file_okay=True, dir_okay=False, resolve_path=True),
    help="PDB file",
)
@click.option(
    "-l",
    "--logfile",
    metavar="LOG",
    show_default=True,
    default=Path.cwd().joinpath("rms2d.log").as_posix(),
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
    "-t",
    "--type",
    "calc_type",
    metavar="TYPE",
    default="ca",
    show_default=True,
    type=click.Choice(["ca", "cab", "noh", "all"], case_sensitive=True),
    help="Atom selection",
)
@click.option("--image", is_flag=True, help="Save correlation heatmap")
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
def cli(
    top: PathLike,
    traj: PathLike,
    outfile: PathLike,
    logfile: PathLike,
    start: int,
    stop: int,
    offset: int,
    calc_type: str,
    image: bool,
    image_type: str,
    fig_type: str,
    width: int,
    dpi: float,
):
    """Calculate the 2D r.m.s.d. matrix between specified atoms."""
    # Setup logging
    logging.config.dictConfig(create_logging_dict(logfile))
    logger: logging.Logger = logging.getLogger(__name__)

    outfile = Path(outfile)
    mask = dict(ca="@CA", cab="@CA,CB", noh="!@H=", all=None)

    logger.info("Loading %s with %s", traj, top)
    frame_slice = (start, stop, offset)
    topology: pt.Topology = pt.load_topology(top)
    trajectory: Trajectory = (
        pt.iterload(traj, top=top, frame_slice=frame_slice)
        if stop > 0
        else pt.iterload(traj, top=top)
    )

    logger.info("Calculating the 2D root mean square deviation")
    logger.warning("Depending upon the trajectory size, this could take a while.")
    value = pt.rms2d(traj=trajectory, mask=mask[calc_type], top=topology)

    with outfile.open(mode="w") as w:
        logger.info("Saving 2D r.m.s.d. data to %s", outfile)
        np.savetxt(w, value, delimiter=",")

    if image:
        filename = outfile.with_suffix(f".{image_type.lower()}")

        fig: plt.Figure = plt.figure(figsize=plt.figaspect(1.0))
        ax = fig.add_subplot(1, 1, 1)
        sns.heatmap(
            value,
            vmin=0,
            cmap=plt.cm.cividis_r,
            robust=True,
            square=True,
            ax=ax,
            xticklabels=width,
            yticklabels=width,
            cbar_kws=dict(label="r.m.s.d. (Å)"),
        )
        fig.suptitle(f"2D r.m.s.d. of {mask[calc_type]}")
        fig.autofmt_xdate(rotation=45)
        fig.tight_layout()

        logger.info("Saving image to %s", outfile)
        fig.savefig(filename, dpi=dpi)
