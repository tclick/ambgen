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
"""Various data files for testing."""

from pathlib import Path

from pkg_resources import resource_filename

__all__ = ["PDB", "FASTA", "TOP", "TOPWW", "TRJ", "TRJWW", "RMSF10", "RMSF10PDB"]

PDB = resource_filename(
    __name__, Path().joinpath("data", "rnase2_amber.pdb").as_posix()
)
FASTA = resource_filename(__name__, Path().joinpath("data", "align.fasta").as_posix())
BAD_FASTA = resource_filename(
    __name__, Path().joinpath("data", "bad_align.fasta").as_posix()
)
TOP = resource_filename(__name__, Path().joinpath("data", "rnase2.parm7").as_posix())
TOPWW = resource_filename(
    __name__, Path().joinpath("data", "rnase2_nowat.parm7").as_posix()
)
TRJ = resource_filename(__name__, Path().joinpath("data", "prod.nc").as_posix())
TRJWW = resource_filename(__name__, Path().joinpath("data", "protein.nc").as_posix())
RMSF10 = resource_filename(__name__, Path().joinpath("data", "rmsf10.dat").as_posix())
RMSF10PDB = resource_filename(
    __name__, Path().joinpath("data", "rmsf10.pdb").as_posix()
)
