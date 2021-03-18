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
import sys
from itertools import product
from pathlib import Path

import click

from .. import create_logging_dict
from ..libs.typing import PathLike
from . import FILE_MODE


@click.command("setup", short_help="Create subdirectories for Amber simulations")
@click.option(
    "-d",
    "--outdir",
    metavar="DIR",
    default=Path.cwd().joinpath("amber").as_posix(),
    show_default=True,
    type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
    help="Parent directory",
)
@click.option(
    "-l",
    "--logfile",
    metavar="LOG",
    show_default=True,
    default=Path.cwd().joinpath(Path(Path(__file__).stem[4:]).with_suffix(".log")),
    type=click.Path(exists=False, file_okay=True, dir_okay=False, resolve_path=True),
    help="Log file",
)
def cli(outdir: PathLike, logfile: PathLike):
    """Create simulation subdirectories"""
    # Setup logging
    if not sys.warnoptions:
        import warnings

        warnings.simplefilter("ignore")

    logging.config.dictConfig(create_logging_dict(logfile))
    logger: logging.Logger = logging.getLogger(__name__)

    dirs = ("Prep", "Equil", "Prod", "Analysis")
    for _ in dirs:
        directory = Path(outdir).joinpath(_)
        logger.info(f"Creating {directory}")
        directory.mkdir(mode=FILE_MODE, parents=True, exist_ok=True)

    equilibration = ("min", "md")
    subsection = (1, 2, 11, 12, 13, 14, 15, 16)
    directories = (
        Path(outdir).joinpath("Equil", f"{x}{y:d}")
        for x, y in product(equilibration, subsection)
        if f"{x}{y:d}" != "min16"
    )
    for directory in directories:
        logger.info(f"Creating {directory}")
        directory.mkdir(mode=FILE_MODE, parents=True, exist_ok=True)

    production = ("initial", "production")
    for _ in production:
        directory = Path(outdir).joinpath("Prod", _)
        logger.info(f"Creating {directory}")
        directory.mkdir(mode=FILE_MODE, parents=True, exist_ok=True)
