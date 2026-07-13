"""Shared test fixtures and helpers.

The local files in ``tests/data`` let the source tests run without a populated
``~/.cache/refidxdb``. Assertions that genuinely need the downloaded database
(host dispatch, cache-relative path resolution) use :func:`skip_if_not_cached`
so they skip cleanly on a clean checkout instead of erroring.
"""

from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def querry_yml() -> str:
    """Absolute path to a refractiveindex.info ``tabulated nk`` entry (iron)."""
    return str(DATA_DIR / "Querry.yml")


@pytest.fixture
def olivine_ri() -> str:
    """Absolute path to an ARIA ``.ri`` file (olivine, wavenumber format)."""
    return str(DATA_DIR / "olivine_Z_Fabian_2001.ri")


@pytest.fixture
def carbon_csv() -> str:
    """Absolute path to a simple ``w,n,k`` CSV (amorphous carbon, wavenumbers)."""
    return str(DATA_DIR / "amorphous_carbon_duley_1984.csv")


def skip_if_not_cached(source_cls, rel_path: str) -> None:
    """Skip the current test unless ``rel_path`` exists in the source's cache.

    ``source_cls`` is a :class:`~refidxdb.url.URL` subclass (Aria/RefIdx); the
    database must have been downloaded (``refidxdb db --download``) for the
    cache-relative assertions to run.
    """
    cached = Path(source_cls().cache_dir) / rel_path
    if not cached.exists():
        pytest.skip(
            f"{source_cls.__name__} not cached at {cached}; "
            "run `refidxdb db --download` to enable this assertion"
        )
