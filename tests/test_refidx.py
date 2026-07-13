from io import StringIO
from typing import Any, cast

import numpy as np
import polars as pl
import polars.testing as plt
import pytest
import yaml

from refidxdb.handler import Handler
from refidxdb.url.refidx import RefIdx, formula, formula2

from .conftest import skip_if_not_cached


def _querry_ground_truth(querry_yml) -> pl.DataFrame:
    with open(querry_yml, "r") as f:
        querry = yaml.safe_load(f)
    return (
        pl.read_csv(
            StringIO(querry["DATA"][0]["data"]),
            has_header=False,
            new_columns=["w", "n", "k"],
            separator=" ",
        )
        .with_columns(pl.col("w").mul(1e-6))
        .sort("w")
    )


def test_iron_querry(querry_yml):
    data = _querry_ground_truth(querry_yml)

    # Loading directly from the local fixture (no cache needed)
    refidx = RefIdx(path=querry_yml)
    plt.assert_frame_equal(data, refidx.nk.drop("n_is_not_null"))

    # Interpolation
    groundtrouth = pl.DataFrame(
        {
            "w": [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
            "n": [3.483, 3.995, 4.171, 4.225, 4.299665, 4.456988, 4.814, 5.153097],
            "k": [
                6.879,
                9.528667,
                12.111,
                14.823,
                17.690235,
                20.685156,
                23.626,
                26.357261,
            ],
        }
    )
    interpolated = refidx.interpolate(groundtrouth["w"].to_numpy(), scale=1e-6)
    interpolated = pl.DataFrame(interpolated)
    plt.assert_frame_equal(groundtrouth, interpolated)


def test_iron_querry_handler(querry_yml):
    # Resolves against the download cache + host dispatch; skips if not cached.
    skip_if_not_cached(RefIdx, "database/data/main/Fe/nk/Querry.yml")
    data = _querry_ground_truth(querry_yml)
    # casting for mitigating linting issue
    handler = Handler(
        url=cast(
            Any, "https://refractiveindex.info/database/data/main/Fe/nk/Querry.yml"
        )
    )
    plt.assert_frame_equal(data, handler.nk.drop("n_is_not_null"))


# express from https://refractiveindex.info/tmp/database/data/other/semiconductor%20alloys/AlAs-GaAs/nk/Perner-0.html
def test_algaas_perner0():
    def n(x):
        return (1 + 9.705183027405873 / (1 - (0.38586135365339097 / x) ** 2)) ** 0.5

    path = "database/data/other/semiconductor alloys/AlAs-GaAs/nk/Perner-0.yml"
    skip_if_not_cached(RefIdx, path)
    wn = RefIdx(path=path)
    wn = (
        wn.nk.filter(pl.col("n_is_not_null"))
        .drop("k")
        .with_columns(pl.col("w").mul(1e6))
    )
    n_gt = wn["n"].to_numpy()
    n_my = n(wn["w"].to_numpy())
    np.testing.assert_allclose(n_gt, n_my, rtol=1e-7)


# express from https://refractiveindex.info/tmp/database/data/specs/ohara/optical/S-BAL2.html
def test_ohara_sbal2():
    def n(x):
        return (
            1
            + 1.30923813 / (1 - 0.00838873953 / x**2)
            + 0.114137353 / (1 - 0.0399436485 / x**2)
            + 1.17882259 / (1 - 140.257892 / x**2)
        ) ** 0.5

    path = "database/data/specs/ohara/optical/S-BAL2.yml"
    skip_if_not_cached(RefIdx, path)
    wn = RefIdx(path=path)
    wn = (
        wn.nk.filter(pl.col("n_is_not_null"))
        .drop("k")
        .with_columns(pl.col("w").mul(1e6))
    )
    n_gt = wn["n"].to_numpy()
    n_my = n(wn["w"].to_numpy())
    np.testing.assert_allclose(n_gt, n_my, rtol=1e-7)


def test_formula2_matches_sellmeier():
    # Evaluate formula 2 directly against the explicit Sellmeier expression.
    c = np.array([0.0, 1.0, 0.01, 0.2, 0.02])
    f = formula2(c)
    x = np.array([0.5, 0.6, 0.7])
    expected = np.sqrt(1 + c[0] + c[1] / (1 - c[2] / x**2) + c[3] / (1 - c[4] / x**2))
    np.testing.assert_allclose(f(x), expected)


def test_formula_unsupported_number():
    with pytest.raises(NotImplementedError):
        formula(4, {"wavelength_range": "0.4 0.8", "coefficients": "1 2 3"})


def test_refidx_tabulated_n_and_k(tmp_path):
    # Exercise the "tabulated n" and "tabulated k" branches without the cache.
    doc = {
        "DATA": [
            {"type": "tabulated n", "data": "0.5 1.5\n0.6 1.6\n0.7 1.7"},
            {"type": "tabulated k", "data": "0.5 0.1\n0.6 0.2\n0.7 0.3"},
        ]
    }
    path = tmp_path / "tabulated.yml"
    path.write_text(yaml.safe_dump(doc))
    nk = RefIdx(path=str(path)).nk
    assert set(nk.columns) >= {"w", "n", "k"}
    assert nk.height == 6


def test_refidx_unsupported_data_type(tmp_path):
    doc = {"DATA": [{"type": "totally bogus", "data": "0.5 1.0 0.1"}]}
    path = tmp_path / "bad.yml"
    path.write_text(yaml.safe_dump(doc))
    with pytest.raises(ValueError):
        _ = RefIdx(path=str(path)).nk


# express from https://refractiveindex.info/tmp/database/data/specs/ohara/optical/BAL2.html
def test_ohara_bal2():
    def n(x):
        return (
            2.424312
            - 0.00858474 * x**2
            + 0.01472045 * x**-2
            + 0.0005504561 * x**-4
            - 3.170738e-05 * x**-6
            + 2.420757e-06 * x**-8
        ) ** 0.5

    path = "database/data/specs/ohara/optical/BAL2.yml"
    skip_if_not_cached(RefIdx, path)
    wn = RefIdx(path=path)
    wn = (
        wn.nk.filter(pl.col("n_is_not_null"))
        .drop("k")
        .with_columns(pl.col("w").mul(1e6))
    )
    n_gt = wn["n"].to_numpy()
    n_my = n(wn["w"].to_numpy())
    np.testing.assert_allclose(n_gt, n_my, rtol=1e-7)
