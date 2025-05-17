# ------------------------------------------------------------------------------
#  ambgen
#  Copyright (c) 2025 Timothy H. Click, Ph.D.
#
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#
#  Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#  Neither the name of the author nor the names of its contributors may be used
#  to endorse or promote products derived from this software without specific
#  prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS”
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
#  OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
#  DAMAGE.
# ------------------------------------------------------------------------------
"""Create simulation subdirectories."""

from enum import StrEnum
from itertools import product
from pathlib import Path
from typing import Annotated

import rich
import typer
from loguru import logger

from .. import __copyright__
from ..libs import logging
from . import FILE_MODE

DEFAULT_OUTDIR = Path.cwd()
DEFAULT_LOGFILE = DEFAULT_OUTDIR / "setup.log"
app = typer.Typer()


class Verbosity(StrEnum):
    """Verbosity levels for controlling logging output detail.

    Attributes
    ----------
    DEBUG : str
        Detailed information for diagnosing issues.
    INFO : str
        General information about program execution.
    WARNING : str
        Indicates unexpected behavior that does not stop execution.
    ERROR : str
        A serious issue that prevents part of the program from functioning.
    CRITICAL : str
        A critical error indicating the program may not continue running.
    """

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@app.command(help="Create simulation subdirectories.")
def setup(
    logfile: Annotated[
        typer.FileTextWrite,
        typer.Option(
            help="Log file",
            show_default=True,
        ),
    ] = DEFAULT_LOGFILE,
    outdir: Annotated[
        Path,
        typer.Option(
            help="Output directory",
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
            writable=True,
            readable=True,
            mode=FILE_MODE,
            show_default=True,
        ),
    ] = DEFAULT_OUTDIR,
    verbosity: Annotated[Verbosity, typer.Option(case_sensitive=False, help="Verbosity level")] = Verbosity.INFO,
) -> None:
    """Create simulation subdirectories.

    Parameters
    ----------
    logfile : typer.FileTextWrite, optional
        th to the log file where logs will be written. If not specified, defaults to "setup.log" in the current
        directory.
    outdir : Path, optional
        Path to the output directory where results or files will be stored. Must be a readable and writable
        directory. Defaults to the current working directory.
    verbosity: Verbosity, optional
        Logging verbosity level. Options include DEBUG, INFO, WARNING, ERROR, and CRITICAL.

    Notes
    -----
    This function is intended to be used as a CLI command with `typer`. It uses type annotations and `typer.Option`
    to define command-line options.
    """
    logging.config_logger(name=__name__, logfile=logfile.name, level=verbosity)

    console = rich.console.Console()
    console.print(__copyright__)

    dirs = ("Prep", "Equil", "Prod", "Analysis")
    for _ in dirs:
        directory = Path(outdir).joinpath(_)
        logger.info("Creating %s", directory.as_posix())
        directory.mkdir(mode=FILE_MODE, parents=True, exist_ok=True)

    equilibration = ("min", "md")
    subsection = (1, 2, 11, 12, 13, 14, 15, 16)
    directories = (
        Path(outdir).joinpath("Equil", f"{x}{y:d}")
        for x, y in product(equilibration, subsection)
        if f"{x}{y:d}" != "min16"
    )
    for directory in directories:
        logger.info("Creating %s", directory.as_posix())
        directory.mkdir(mode=FILE_MODE, parents=True, exist_ok=True)

    production = ("mdst", "mdprod")
    for _ in production:
        directory = Path(outdir).joinpath("Prod", _)
        logger.info("Creating %s", directory.as_posix())
        directory.mkdir(mode=FILE_MODE, parents=True, exist_ok=True)
