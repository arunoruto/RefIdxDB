from typing import Any, cast

import numpy as np
import pytest

from refidxdb.file.csv import CSV
from refidxdb.file.dat import DAT
from refidxdb.handler import Handler


def _url(value: str):
    # Handler.url is an HttpUrl field; pydantic coerces the string at runtime.
    return cast(Any, value)


def test_dispatch_csv_and_dat():
    assert isinstance(Handler(path="foo.csv").source, CSV)
    assert isinstance(Handler(path="foo.dat").source, DAT)


def test_dispatch_hosts():
    refidx = Handler(url=_url("https://refractiveindex.info/data/main/Fe/nk/Querry.yml"))
    aria = Handler(url=_url("https://eodg.atm.ox.ac.uk/ARIA/data_files/x.ri"))
    assert type(refidx.source).__name__ == "RefIdx"
    assert type(aria.source).__name__ == "Aria"


def test_requires_path_or_url():
    with pytest.raises(ValueError):
        Handler()


def test_unsupported_extension():
    with pytest.raises(ValueError):
        Handler(path="foo.txt")


def test_unsupported_host():
    with pytest.raises(ValueError):
        Handler(url=_url("https://example.com/some/file.yml"))


@pytest.mark.parametrize(
    ("given", "expected"),
    [(True, "wl"), (False, "wn"), ("wl", "wl"), ("wn", "wn")],
)
def test_w_column_normalization(given, expected):
    assert Handler(path="foo.csv", w_column=given).w_column == expected


def test_uninitialized_source_raises():
    handler = Handler(path="foo.csv")
    handler._source = None  # simulate the defensive branch
    with pytest.raises(RuntimeError):
        _ = handler.nk
    with pytest.raises(RuntimeError):
        handler.interpolate(np.array([1.0]))
