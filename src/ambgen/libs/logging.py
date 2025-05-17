# ------------------------------------------------------------------------------
# ambgen
# Copyright (c) 2013-2024 Timothy H. Click, Ph.D.
#
# This file is part of fluctmatch.
#
# Fluctmatch is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Fluctmatch is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>.
#
# Reference:
# Timothy H. Click, Nixon Raj, and Jhih-Wei Chu. Simulation. Meth Enzymology. 578 (2016), 327-342,
# Calculation of Enzyme Fluctuograms from All-Atom Molecular Dynamics doi:10.1016/bs.mie.2016.05.024.
# ------------------------------------------------------------------------------
# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnusedCallResult=false
# pyright: reportAttributeAccessIssue=false, reportArgumentType=false, reportUnusedParameter=false
"""Logging module for the ambgen package.

This module provides functions for configuring logging using the loguru package
and for handling warnings in a consistent manner.
"""

import getpass
import logging
import sys
import warnings
from pathlib import Path
from typing import TextIO

from loguru import logger
from loguru_logging_intercept import setup_loguru_logging_intercept


def config_logger(name: str, logfile: str | Path | None = None, level: str | int = "INFO") -> None:
    """Configure the loguru logger with specified parameters.

    This function sets up a logger with the given name and logging level. It configures
    handlers for console output and optionally for file output if a logfile is specified.
    It also sets up loguru to intercept standard logging calls.

    Parameters
    ----------
    name : str
        Name associated with the logger, used for identification.
    logfile : str or Path or None, optional
        Path to the log file where logs will be written. If None, logs will only
        be output to stderr, by default None.
    level : str or int, optional
        Minimum level for logging. Can be a string like "INFO", "DEBUG", "WARNING",
        "ERROR", "CRITICAL" or an integer level, by default "INFO".

    Notes
    -----
    The logger is configured with colorized output to stderr and optionally to a file.
    It includes backtrace and diagnostic information for better debugging.
    The function also sets up loguru to intercept standard logging calls.
    """
    config = {
        "handlers": [
            {
                "sink": sys.stderr,
                "format": "{time:YYYY-MM-DD HH:mm} | <level>{level.name}</level> | {message}",
                "colorize": True,
                "level": level,
                "backtrace": True,
                "diagnose": True,
            },
        ],
        "extra": {"name": name, "user": getpass.getuser()},
    }
    if logfile is not None:
        log_dict = {"sink": logfile, "format": "{time:YYYY-MM-DD HH:mm} | {level} | {message}", "level": level}
        config["handlers"].append(log_dict)

    logger.remove()
    logger.configure(**config)
    setup_loguru_logging_intercept(level=logging.DEBUG, modules=f"root {name}".split())


def warning_handler(
    message: str,
    category: Warning,
    filename: str,
    lineno: int,
    file: TextIO | None = None,  # noqa: ARG001
    line: str | None = None,  # noqa: ARG001
) -> None:
    """Redirect warnings to loguru.

    This function is designed to be used as a replacement for the default
    warnings.showwarning function. It formats warning messages and sends them
    to loguru's warning level instead of the default output.

    Parameters
    ----------
    message : str
        The warning message to be logged.
    category : Warning
        The warning category class (e.g., DeprecationWarning, UserWarning).
    filename : str
        The path to the file where the warning was triggered.
    lineno : int
        The line number in the file where the warning was triggered.
    file : TextIO or None, optional
        The file to write the warning to. This parameter is ignored in this
        implementation as warnings are sent to loguru instead, by default None.
    line : str or None, optional
        The line of source code that triggered the warning. This parameter is
        ignored in this implementation, by default None.

    Notes
    -----
    This function is set as the default warning handler by assigning it to
    warnings.showwarning at the module level.
    """
    logger.warning(f"{filename}:{lineno} - {category.__name__}: {message}")


warnings.showwarning = warning_handler
