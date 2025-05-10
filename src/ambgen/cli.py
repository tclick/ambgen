# ------------------------------------------------------------------------------
#  mdsetup
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
# pyright: reportAny=false
"""Command-line interface for ambgen."""

import importlib
import pkgutil

import typer
from rich.console import Console

from ambgen import NAME, __copyright__, __version__, commands

console = Console()
app: typer.Typer = typer.Typer(
    name=NAME,
    short_help="Amber input file generator",
)


def version_callback(value: bool) -> None:
    """Print the version of the package.

    Parameters
    ----------
    value : bool
        Print the version of the package if True

    Raises
    ------
    typer.Exit
        Exit application
    """
    if value:
        console.print(f"{NAME} {__version__}")
        raise typer.Exit()


@app.callback()
def ambgen(
    ctx: typer.Context,
    version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True, help="Show version"),
) -> None:
    """Entry point for the command-line interface.

    Parameters
    ----------
    ctx : typer.Context
        Context for the command-line interface
    version : bool
        Show version
    """
    console.print(__copyright__)

    # Auto-discover and register plugins
    for _, module_name, _ in pkgutil.iter_modules(commands.__path__):
        module = importlib.import_module(f"ambgen.commands.{module_name}")
        if hasattr(module, "app"):
            app.add_typer(module.app, name=module_name)
