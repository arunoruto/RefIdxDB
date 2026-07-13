from pathlib import Path
from urllib.error import URLError

import click
import pytest
from click.testing import CliRunner

from refidxdb import __version__
from refidxdb.cli import clean_db, cli, parse_source, resolve_dbs
from refidxdb.sources import DATABASES
from refidxdb.url.aria import Aria
from refidxdb.url.refidx import RefIdx


def test_version():
    result = CliRunner().invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_resolve_dbs_all():
    assert resolve_dbs("all") == list(DATABASES.values())


def test_resolve_dbs_list():
    assert resolve_dbs("aria,refidx") == [Aria, RefIdx]


def test_resolve_dbs_unknown():
    with pytest.raises(click.BadParameter):
        resolve_dbs("nope")


def test_parse_source_valid():
    assert isinstance(parse_source("aria", "x.ri"), Aria)
    assert isinstance(parse_source("refidx", "x.yml"), RefIdx)


def test_parse_source_invalid():
    with pytest.raises(click.BadParameter):
        parse_source("bogus", "x")


def test_clean_db_removes_and_reports(monkeypatch, tmp_path, capsys):
    cache = tmp_path / "Aria"
    cache.mkdir()
    (cache / "file").write_text("data")
    monkeypatch.setattr(Aria, "cache_dir", property(lambda self: str(cache)))

    clean_db("aria")
    assert not cache.exists()
    assert "Removed cache for Aria" in capsys.readouterr().out


def test_clean_db_no_cache(monkeypatch, tmp_path, capsys):
    missing = tmp_path / "gone"
    monkeypatch.setattr(Aria, "cache_dir", property(lambda self: str(missing)))

    clean_db("aria")
    assert "No cache found for Aria" in capsys.readouterr().out


@pytest.mark.network
def test_sync():
    runner = CliRunner()
    result = runner.invoke(cli, ["db", "--download", "all"])

    if result.exit_code != 0 and isinstance(result.exception, (URLError, OSError)):
        pytest.skip(f"network unavailable: {result.exception}")

    assert result.exit_code == 0, result.output
    assert "All databases downloaded!" in result.output
    for db in DATABASES.values():
        assert Path(db().cache_dir).exists()
