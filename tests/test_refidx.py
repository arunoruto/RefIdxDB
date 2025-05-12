import os
from io import StringIO
from typing import Any, cast

import numpy as np
import polars as pl
import polars.testing as plt
import yaml

from refidxdb.handler import Handler
from refidxdb.url.refidx import RefIdx


def test_iron_querry():
    with open(os.path.dirname(__file__) + "/data/Querry.yml", "r") as f:
        querry = yaml.safe_load(f)

    data = (
        pl.read_csv(
            StringIO(querry["DATA"][0]["data"]),
            has_header=False,
            new_columns=["w", "n", "k"],
            separator=" ",
        )
        .with_columns(pl.col("w").mul(1e-6))
        .sort("w")
    )

    # Test loading
    refidx = RefIdx(path="database/data-nk/main/Fe/Querry.yml")
    plt.assert_frame_equal(data, refidx.nk.drop("n_is_not_null"))

    # Test interpolation
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

    # Test handler version
    # casting for mitigating linting issue
    handler = Handler(
        url=cast(
            Any, "https://refractiveindex.info/database/data-nk/main/Fe/Querry.yml"
        )
    )
    plt.assert_frame_equal(data, handler.nk.drop("n_is_not_null"))


# express from https://refractiveindex.info/tmp/database/data-nk/other/semiconductor%20alloys/AlAs-GaAs/Perner-0.html
def test_algaas_perner0():
    def n(x):
        return (1 + 9.705183027405873 / (1 - (0.38586135365339097 / x) ** 2)) ** 0.5

    wn = RefIdx(
        path="database/data-nk/other/semiconductor alloys/AlAs-GaAs/Perner-0.yml"
    )
    wn = (
        # wn.nk.filter(pl.col("n").is_not_null())
        wn.nk.filter(pl.col("n_is_not_null"))
        .drop("k")
        .with_columns(pl.col("w").mul(1e6))
    )
    n_gt = wn["n"].to_numpy()
    n_my = n(wn["w"].to_numpy())
    np.testing.assert_allclose(n_gt, n_my, rtol=1e-7)


# express from https://refractiveindex.info/tmp/database/data-nk/glass/ohara/S-BAL2.html
def test_ohara_sbal2():
    def n(x):
        return (
            1
            + 1.30923813 / (1 - 0.00838873953 / x**2)
            + 0.114137353 / (1 - 0.0399436485 / x**2)
            + 1.17882259 / (1 - 140.257892 / x**2)
        ) ** 0.5

    wn = RefIdx(path="database/data-nk/glass/ohara/S-BAL2.yml")
    wn = (
        # wn.nk.filter(pl.col("n").is_not_null())
        wn.nk.filter(pl.col("n_is_not_null"))
        .drop("k")
        .with_columns(pl.col("w").mul(1e6))
    )
    n_gt = wn["n"].to_numpy()
    n_my = n(wn["w"].to_numpy())
    np.testing.assert_allclose(n_gt, n_my, rtol=1e-7)


# express from https://refractiveindex.info/tmp/database/data-nk/glass/ohara/BAL2.html
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

    wn = RefIdx(path="database/data-nk/glass/ohara/BAL2.yml")
    wn = (
        # wn.nk.filter(pl.col("n").is_not_null())
        wn.nk.filter(pl.col("n_is_not_null"))
        .drop("k")
        .with_columns(pl.col("w").mul(1e6))
    )
    n_gt = wn["n"].to_numpy()
    n_my = n(wn["w"].to_numpy())
    np.testing.assert_allclose(n_gt, n_my, rtol=1e-7)
