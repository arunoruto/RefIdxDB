import numpy as np
import polars as pl
import polars.testing as plt
import pytest

from refidxdb.file.csv import CSV
from refidxdb.handler import Handler


def test_csv_empty_path_raises():
    with pytest.raises(ValueError):
        _ = CSV().data


def _raw(carbon_csv) -> pl.DataFrame:
    return pl.read_csv(
        carbon_csv,
        schema_overrides={h: pl.Float64 for h in ["w", "n", "k"]},
    )


def test_csv_wavenumber_to_wavelength(carbon_csv):
    raw = _raw(carbon_csv)
    # Source treats the first column as wavenumber (scale 1e2) and, for a
    # wavelength request, inverts it: w = 1 / (w_raw * 1e2).
    expected = pl.DataFrame(
        {
            "w": 1.0 / (raw["w"] * 1e2),
            "n": raw["n"],
            "k": raw["k"],
        }
    ).sort("w")

    csv = CSV(path=carbon_csv, w_column="wn", wavelength=True)
    plt.assert_frame_equal(expected, csv.nk)


def test_csv_wavenumber_passthrough(carbon_csv):
    raw = _raw(carbon_csv)
    # wavenumber in / wavenumber out: no inversion, just the 1e2 scale.
    expected = pl.DataFrame(
        {"w": raw["w"] * 1e2, "n": raw["n"], "k": raw["k"]}
    ).sort("w")

    csv = CSV(path=carbon_csv, w_column="wn", wavelength=False)
    plt.assert_frame_equal(expected, csv.nk)


def test_csv_interpolate_in_range(carbon_csv):
    csv = CSV(path=carbon_csv, w_column="wn", wavelength=False)
    lo, hi = csv.nk["w"].min(), csv.nk["w"].max()
    target = np.linspace(lo, hi, 5) / 1e2  # interpolate() rescales by 1e2
    out = csv.interpolate(target)
    assert set(out.columns) == {"w", "n", "k"}
    assert out["n"].is_finite().all()
    assert out["k"].is_finite().all()


def test_csv_handler_dispatch(carbon_csv):
    # Handler routes a .csv path to the CSV source; boolean w_column=False -> "wn".
    handler = Handler(path=carbon_csv, w_column=False, wavelength=False)
    assert isinstance(handler.source, CSV)

    direct = CSV(path=carbon_csv, w_column="wn", wavelength=False)
    plt.assert_frame_equal(direct.nk, handler.nk)
