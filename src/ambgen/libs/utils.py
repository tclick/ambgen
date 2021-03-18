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
import subprocess
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Literal, NoReturn

import numpy as np
import seaborn as sns
from jinja2 import Environment, PackageLoader, Template, TemplateNotFound

from .typing import ArrayLike, PathLike

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def run_tleap(
    infile: PathLike,
    filename: PathLike,
    /,
    *,
    logfile: PathLike = "tleap.log",
    prefix: str = "tleap",
    template: str = "fixed",
) -> NoReturn:
    """Run the tleap command

    Parameters
    ----------
    infile : :class:`pathlib.Path` or str
        tleap input filename
    filename : :class:`pathlib.Path` or str
        Structure filename (e.g., PDB)
    logfile : :class:`pathlib.Path` or str
        Log file
    prefix : str
        Prefix for output file
    template : str
        Jinja2 template to use
    """
    command = f"tleap -f {infile} > {logfile}"
    try:
        infile = Path(infile)
        with infile.open(mode="w") as inf:
            loader = PackageLoader("ambgen", package_path="templates/leap")
            env = Environment(loader=loader, autoescape=True)
            template: Template = env.get_template(f"{template}.jinja2")
            logger.info("Writing tLeap input script to %s", infile.as_posix())
            print(template.render(input=filename, prefix=prefix), file=inf)
    except TemplateNotFound:
        logger.exception("Could not load %s.jinja2", template, exc_info=True)

    try:
        logger.info("Generating AMBER topology and coordinate files.")
        subprocess.check_call(command, shell=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        logger.exception("Could not run tleap", exc_info=True)
