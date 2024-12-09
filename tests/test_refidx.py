import os
from io import StringIO

import polars as pl
import polars.testing as plt
import yaml

from refidxdb.handler import Handler
from refidxdb.refidx import RefIdx


def test_iron_querry():
    with open(os.path.dirname(__file__) + "/data/Querry.yml", "r") as f:
        querry = yaml.safe_load(f)

    data = (
        pl.read_csv(
            StringIO(querry["DATA"][0]["data"]),
            new_columns=["w", "n", "k"],
            separator=" ",
        )
        .with_columns(pl.col("w").mul(1e-6))
        .sort("w")
    )

    # Test loading
    refidx = RefIdx(path="database/data-nk/main/Fe/Querry.yml")
    plt.assert_frame_equal(data, refidx.nk)

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
    interpolated = refidx.interpolate(groundtrouth["w"], scale=1e-6)
    plt.assert_frame_equal(groundtrouth, interpolated)

    # Test handler version
    handler = Handler(
        url="https://refractiveindex.info/database/data-nk/main/Fe/Querry.yml"
    )
    # print(data, handler.nk)
    plt.assert_frame_equal(data, handler.nk)


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
    print(wn.nk)
    w = wn.nk["w"].to_numpy() / wn.scale
    print(wn.nk["n"])
    print(w, n(w))
