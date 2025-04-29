from pathlib import Path

import pytest
from click.testing import CliRunner

from refidxdb.cli import cli
from refidxdb.url.aria import Aria
from refidxdb.url.refidx import RefIdx

databases = {
    item.__name__.lower(): item
    for item in [
        Aria,
        RefIdx,
    ]
}


# @pytest.mark.skip(reason="Takes too many resources for now")
def test_sync():
    runner = CliRunner()
    result = runner.invoke(cli, ["db", "--download", "all"])
    assert result.exit_code == 0
    assert "All databases downlaoded!" in result.output

    for db in list(databases.values()):
        dir = db().cache_dir
        assert Path(dir).exists()
