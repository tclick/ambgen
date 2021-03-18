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

from .. import create_logging_dict
from ..libs.typing import PathLike
from ..libs.utils import run_tleap


@click.command("solvate", short_help="Neutralize and solvate a system.")
@click.option(
    "-f",
    "--infile",
    metavar="FILE",
    default=Path.cwd().joinpath("input.pdb"),
    show_default=True,
    type=click.Path(exists=False, file_okay=True, dir_okay=False, resolve_path=True),
    help="Input PDB file",
)
@click.option(
    "-p",
    "--prefix",
    metavar="FILE",
    default="solvated",
    show_default=True,
    type=click.Path(exists=False, file_okay=True, dir_okay=False, resolve_path=True),
    help="Prefix for output files",
)
@click.option(
    "-l",
    "--logfile",
    metavar="LOG",
    show_default=True,
    default=Path.cwd().joinpath("solvate.log"),
    type=click.Path(exists=False, file_okay=True, dir_okay=False, resolve_path=True),
    help="Log file",
)
def cli(infile: PathLike, prefix: PathLike, logfile: PathLike):
    """Neutralize and solvate a system."""
    logging.config.dictConfig(create_logging_dict(logfile))
    logger: logging.Logger = logging.getLogger(__name__)

    prefix = Path(prefix)
    tleap = prefix.with_suffix(".in")
    logname = prefix.with_suffix(".log")
    logger.info("Adding ions and solvating the system")
    run_tleap(tleap, infile, prefix=prefix, logfile=logname, template="solvate")
