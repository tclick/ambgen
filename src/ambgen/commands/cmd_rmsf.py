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
from dataclasses import make_dataclass
from pathlib import Path
from typing import List

import click
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytraj as pt

from .. import create_logging_dict
from ..libs.typing import PathLike, Trajectory
from ..libs.utils import _GRAPHS, save_data


@click.command("rmsf", short_help="Calculate root mean square fluctuations.")
@click.option(
    "-s",
    "--top",
    metavar="FILE",
    default=Path.cwd().joinpath("input.top"),
    show_default=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    help="Topology",
)
@click.option(
    "-f",
    "--traj",
    metavar="FILE",
    default=Path.cwd().joinpath("input.trj"),
    show_default=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    help="Trajectory",
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
    "-o",
    "--outfile",
    metavar="FILE",
    default=Path.cwd().joinpath("rmsf.png").as_posix(),
    show_default=True,
    type=click.Path(exists=False, file_okay=True, dir_okay=False, resolve_path=True),
    help="Image file",
)
@click.option(
    "-l",
    "--logfile",
    metavar="LOG",
    show_default=True,
    default=Path.cwd().joinpath("rmsf.log"),
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
    type=click.Choice("ca cab heavy all".split(), case_sensitive=False),
    multiple=True,
    help="Atom selection",
)
@click.option(
    "--label",
    metavar="LABEL",
    default=10,
    show_default=True,
    type=click.IntRange(min=1, clamp=True),
    help="Spacing for tick labels",
)
@click.option("--image", is_flag=True, help="Save correlation heatmap")
@click.option(
    "--ft",
    "fig_type",
    default="bar",
    type=click.Choice(["bar", "line"], case_sensitive=False),
    help="Graph type to draw",
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
    datadir: PathLike,
    outfile: PathLike,
    logfile: PathLike,
    start: int,
    stop: int,
    offset: int,
    calc_type: List[str],
    label: int,
    image: bool,
    fig_type: str,
    dpi: float,
):
    """Calculate the root mean square fluctuations of both heavy and selected atoms."""
    # Setup logging
    logging.config.dictConfig(create_logging_dict(logfile))
    logger: logging.Logger = logging.getLogger(__name__)

    columns = ["Residue", "r.m.s.f. (Å)"]
    mask = dict(ca="@CA", cab="@CA,CB", heavy="!@H=", all="")
    datadir = Path(datadir)
    Data = make_dataclass(
        "Data",
        [(_.lower(), pd.DataFrame) for _ in calc_type],
    )
    rmsf = {}

    logger.info(f"Loading {traj} with {top}")
    frame_slice = (start, stop, offset)
    topology: pt.Topology = pt.load_topology(top)
    trajectory: Trajectory = (
        pt.iterload(traj, top=top, frame_slice=frame_slice)
        if stop > 0
        else pt.iterload(traj, top=top)
    )

    logger.info("Calculating the r.m.s.f. for all heavy atoms")
    logger.warning("Depending upon the trajectory size, this could take a while.")
    for _ in calc_type:
        rmsf[_] = pt.rmsf(
            traj=trajectory, mask=mask[_.lower()], top=topology, options="byres"
        )
        rmsf[_] = pd.DataFrame(rmsf[_], columns=columns)

    save_data(data_dir=datadir, data=Data(**rmsf))
    if image:
        fig: plt.Figure = plt.figure(figsize=plt.figaspect(0.25))
        for i, ((key, df), title) in enumerate(zip(rmsf.items(), calc_type), 1):
            df[df.columns[0]] = df[df.columns[0]].astype(int)
            ax = fig.add_subplot(1, len(calc_type), i)
            _GRAPHS[fig_type](
                x="Residue", y="r.m.s.f. (Å)", data=df, color="blue", ax=ax
            )
            ax.set_title(f"{title}")
            ax.set_xticks(np.arange(label - 1, df.shape[0], label))
        fig.suptitle("Root mean square fluctuations")
        logger.info("Saving image to %s", outfile)
        fig.autofmt_xdate(rotation=45)
        fig.tight_layout()
        fig.savefig(outfile, dpi=dpi)
