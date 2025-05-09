# ---------------------------------------------------------------------------------------------------------------------
# fluctmatch
# Copyright (c) 2013-2024 Timothy H. Click, Ph.D.
#
# This file is part of fluctmatch.
#
# Fluctmatch is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Fluctmatch is distributed in the hope that it will be useful, # but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <[1](https://www.gnu.org/licenses/)>.
#
# Reference:
# Timothy H. Click, Nixon Raj, and Jhih-Wei Chu. Simulation. Meth Enzymology. 578 (2016), 327-342,
# Calculation of Enzyme Fluctuograms from All-Atom Molecular Dynamics doi:10.1016/bs.mie.2016.05.024.
# ---------------------------------------------------------------------------------------------------------------------
"""Nox session."""

import os
import shutil
import sys
from pathlib import Path

import nox
from nox import Session

os.environ.update({"PDM_IGNORE_SAVED_PYTHON": "1"})
package = "fluctmatch"
python_versions = [
    "3.12",
    "3.13",
]
nox.needs_version = ">= 2024.4.15"
nox.options.sessions = (
    "pre-commit",
    "safety",
    "pyright",
    "tests",
    "typeguard",
    "xdoctest",
    "docs-build",
)


@nox.session(name="pre-commit", python=python_versions[0])
def precommit(session: Session) -> None:
    """Lint using pre-commit."""
    args = session.posargs or ["run", "--all-files", "--hook-stage=manual", "--show-diff-on-failure"]
    session.run("pre-commit", "install", external=True)
    session.run("pre-commit", *args, external=True)


@nox.session(python=python_versions[0])
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages."""
    session.run(*["safety", "scan", "--full-report", "--ignore=70612,74735"], external=True)


@nox.session(python=python_versions)
def pyright(session: Session) -> None:
    """Type-check using pyright.

    Parameters
    ----------
    session: Session
        The Session object.
    """
    args = (
        session.posargs
        or f"-p pyproject.toml --pythonversion {session.python} --pythonpath={sys.executable} src".split()
    )
    session.run("basedpyright", *args, external=True)


@nox.session(python=python_versions)
def tests(session: Session) -> None:
    """Run the test suite."""
    args = [
        "--cov",
        "src",
        "--cov-report=xml",
        "--cov-config=pyproject.toml",
        "--random-order",
        "--disable-pytest-warnings",
    ]

    try:
        session.run("pytest", *args, *session.posargs, external=True)
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@nox.session(python=python_versions[0])
def coverage(session: Session) -> None:
    """Produce the coverage report."""
    args = session.posargs or ["report"]

    session.install("coverage[toml]")

    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")

    session.run("coverage", *args, external=True)


@nox.session(python=python_versions[0])
def typeguard(session: Session) -> None:
    """Runtime type checking using Typeguard."""
    args = ["--typeguard-packages=all", "--random-order", "--disable-pytest-warnings"]
    session.run("pytest", *args, *session.posargs, external=True)


@nox.session(python=python_versions)
def xdoctest(session: Session) -> None:
    """Run examples with xdoctest."""
    if session.posargs:
        args = [package, *session.posargs]
    else:
        args = [f"--modname={package}", "--command=all"]
        if "FORCE_COLOR" in os.environ:
            args.append("--colored=1")

    session.install("xdoctest[colors]")
    session.run("python", "-m", "xdoctest", *args, external=True)


@nox.session(name="docs-build", python=python_versions[0])
def docs_build(session: Session) -> None:
    """Build the documentation."""
    args = session.posargs or ["docs", "docs/_build"]
    if not session.posargs and "FORCE_COLOR" in os.environ:
        args.insert(0, "--color")

    build_dir = Path("docs", "_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-build", *args, external=True)


@nox.session(python=python_versions[0])
def docs(session: Session) -> None:
    """Build and serve the documentation with live reloading on file changes."""
    args = session.posargs or ["--open-browser", "docs", "docs/_build"]

    build_dir = Path("docs", "_build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-autobuild", *args, external=True)
