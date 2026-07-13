from pathlib import Path

import numpy as np
import polars as pl
import polars.testing as plt
import pytest

from refidxdb.file.dat import DAT


def test_dat_empty_path_raises():
    with pytest.raises(ValueError):
        _ = DAT().data


def test_olivine_fabian_dat():
    file = Path(__file__).parent / "data/olivine_Z_Fabian_2001.ri"
    fabian = (
        pl.DataFrame(
            np.loadtxt(file, encoding="latin-1"),
            schema={"WAVN": pl.Float64, "N": pl.Float64, "K": pl.Float64},
        )
        .with_columns(pl.col("WAVN").mul(1e2))
        .sort("WAVN")
    )
    fabian.columns = ["w", "n", "k"]

    # Test loading
    dat = DAT(
        path=file,
        wavelength=False,
        w_column="wn",
    )
    plt.assert_frame_equal(fabian, dat.nk)

    # Test interpolation
    groundtrouth = pl.DataFrame(
        {
            "w": np.arange(1, 10),
            "n": [
                2.468589000000000,
                2.468603409016394,
                2.468626565929566,
                2.468658287469288,
                2.468698850000000,
                2.468748850000000,
                2.468809098280098,
                2.468878274365274,
                2.468956009828010,
            ],
            "k": [
                0.000063882063882,
                0.000127804918033,
                0.000191710073710,
                0.000255592137592,
                0.000319576229508,
                0.000384330327869,
                0.000448302211302,
                0.000512184275184,
                0.000576438984439,
            ],
        }
    )
    interpolated = dat.interpolate(groundtrouth["w"].to_numpy())
    plt.assert_frame_equal(groundtrouth, interpolated)
