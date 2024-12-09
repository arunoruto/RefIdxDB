from pathlib import Path

from click.testing import CliRunner

from refidxdb import databases
from refidxdb.cli import cli


def test_sync():
    runner = CliRunner()
    result = runner.invoke(cli, ["db", "--download", "all"])
    assert result.exit_code == 0
    assert "All databases downlaoded!" in result.output

    for db in list(databases.values()):
        dir = db().cache_dir
        assert Path(dir).exists()
