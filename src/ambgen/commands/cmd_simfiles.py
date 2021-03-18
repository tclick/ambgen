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
"""Prepares various Amber input files for use in simulations.

Various Amber input files are created from templates. The input files follow the
protocol set forth in the Agarwal group. The production runs are microcanonical
simulations (NVE), and the equilibration runs involve both canonical (NVT) and
isobaric-isothermal (NPT) simulations with minimization steps between the equilibration
runs.
"""
import logging
import logging.config
import os
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Literal, NoReturn, Tuple

import click
import pytraj as pt
from jinja2 import Environment, PackageLoader

from .. import create_logging_dict
from ..libs.typing import PathLike, ArrayLike
from . import FILE_MODE


@dataclass
class Data:
    temp1: float
    temp2: float
    res0: int
    res1: int
    ions0: int
    ions1: int
    solvent0: int
    solvent1: int
    force: float
    simdir: PathLike
    prefix: str
    amberhome: PathLike
    pmemd: str


def _write_template(
    env: Environment,
    temploc: str,
    data: Data,
    subdir: PathLike,
    logger: logging.Logger,
) -> NoReturn:
    env.loader = PackageLoader("ambgen", package_path=f"templates/{temploc}")
    year = time.strftime("%Y")

    for _ in env.loader.list_templates():
        filename = Path(_)
        subdirectory = (
            Path(subdir).joinpath(filename.stem)
            if "Scripts" not in Path(subdir).joinpath(filename.stem).as_posix()
            else Path(subdir)
        )
        subdirectory.mkdir(mode=FILE_MODE, parents=True, exist_ok=True)
        input_file = (
            subdirectory.joinpath(filename).with_suffix(".sh")
            if temploc == "scripts"
            else subdirectory.joinpath(filename).with_suffix(".in")
        )
        with input_file.open(mode="w", encoding="utf-8") as inf:
            template = env.get_template(filename.as_posix())
            logger.info("Writing script to %s", input_file)
            print(template.render(data=data, year=year), file=inf)


@click.command("simfiles", short_help="Prepare Amber input files for simulation.")
@click.option(
    "-s",
    "--topology",
    metavar="FILE",
    default=Path("amber.prmtop").resolve().as_posix(),
    show_default=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    help="Topology file",
)
@click.option(
    "-d",
    "--outdir",
    metavar="DIR",
    default=Path.cwd().as_posix(),
    show_default=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    help="Simulation subdirectory",
)
@click.option(
    "-p",
    "--prefix",
    metavar="PREFIX",
    default=Path.cwd().stem,
    show_default=True,
    help="Prefix for various output files",
)
@click.option(
    "--temp1",
    metavar="TEMP",
    default=100.0,
    show_default=True,
    type=click.FloatRange(min=1.0, clamp=True),
    help="Initial temperature (K)",
)
@click.option(
    "--temp2",
    metavar="TEMP",
    default=300.0,
    show_default=True,
    type=click.FloatRange(min=1.0, clamp=True),
    help="Final temperature (K)",
)
@click.option(
    "--force",
    metavar="FORCE",
    default=100.0,
    show_default=True,
    type=click.FloatRange(min=1.0, clamp=True),
    help="Restraint force (kcal/mol/A^2",
)
@click.option(
    "-l",
    "--logfile",
    metavar="LOG",
    default=Path.cwd().joinpath(Path(Path(__file__).stem[4:]).with_suffix(".log")),
    show_default=True,
    type=click.Path(exists=False, file_okay=True, writable=True, resolve_path=True),
    help="Log file",
)
@click.option(
    "--home",
    metavar="DIR",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    help="Location of Amber files",
)
@click.option(
    "--type",
    "outtype",
    default="all",
    show_default=True,
    type=click.Choice("equil prod scripts all".split(), case_sensitive=False),
    help="Which output files to create",
)
def cli(
    topology: str,
    outdir: str,
    prefix: str,
    temp1: float,
    temp2: float,
    force: float,
    logfile: PathLike,
    home: str,
    outtype: str,
):
    """Prepare various Amber input files to run simulations."""
    if not sys.warnoptions:
        import warnings

        warnings.simplefilter("ignore")

    logging.config.dictConfig(create_logging_dict(logfile))
    logger: logging.Logger = logging.getLogger(__name__)

    universe = pt.load_topology(topology)
    protein: ArrayLike[Literal["int"]] = universe.select("!:Na+,Cl-,WAT")
    ions: ArrayLike[Literal["int"]] = universe.select(":Na+,Cl-")
    solvent: ArrayLike[Literal["int"]] = universe.select(":WAT")
    try:
        amberhome = Path(home) if home is not None else Path(os.environ["AMBERHOME"])
    except KeyError:
        logger.exception("AMBERHOME environment variable not defined.", exc_info=False)
        return

    outdir = Path(outdir)
    data = Data(
        temp1=temp1,
        temp2=temp2,
        res0=protein[0],
        res1=protein[-1],
        ions0=ions[0],
        ions1=ions[-1],
        solvent0=solvent[0],
        solvent1=solvent[-1],
        force=force,
        simdir=outdir,
        prefix=prefix,
        amberhome=amberhome,
        pmemd=(
            "pmemd.MPI"
            if shutil.which(amberhome / "bin" / "pmemd.MPI") is not None
            else "pmemd"
        ),
    )

    env = Environment(autoescape=True)
    temploc: Dict[str, Tuple[str, ...]] = dict(
        equil=("equil",),
        prod=("prod",),
        scripts=("scripts",),
        all=("equil", "prod", "scripts"),
    )

    for _ in temploc.get(outtype.lower(), "all"):
        subdir: Path = outdir.joinpath(_.title())
        subdir.mkdir(mode=FILE_MODE, parents=True, exist_ok=True)
        _write_template(env, _, data, subdir, logger)

    # # Write the shell scripts
    if outtype == "scripts" or outtype == "all":
        logging.debug("Changing file permissions to %s", FILE_MODE)
        subdir: Path = outdir.joinpath("Scripts")
        for _ in subdir.glob("*.sh"):
            _.chmod(mode=FILE_MODE)
