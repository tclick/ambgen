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
from pathlib import Path

import numpy as np
import pytest
from numpy import testing
from pytest_mock import MockerFixture

from ambgen.libs import utils

from ..datafile import PDB


@pytest.mark.parametrize("template", "fixed solvate tleap".split())
def test_tleap(template: str, mocker: MockerFixture, tmp_path: Path):
    """
    GIVEN template parameters
    WHEN run_tleap is called
    THEN an input file is created and tleap is run
    """
    subprocess = mocker.patch("subprocess.check_call")
    infile = tmp_path.joinpath(Path(template).with_suffix(".in"))
    logfile = tmp_path.joinpath(Path(template).with_suffix(".log"))

    utils.run_tleap(infile, PDB, prefix=template, template=template, logfile=logfile.as_posix())

    assert infile.exists()
    assert infile.stat().st_size > 0
    assert logfile.exists()
    assert logfile.stat().st_size > 0
    subprocess.assert_called_once()
