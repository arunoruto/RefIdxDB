import numpy as np
import polars as pl
import polars.testing as plt
import pytest

from refidxdb.handler import Handler
from refidxdb.url.aria import Aria

from .conftest import skip_if_not_cached

ARIA_REL = (
    "data_files/Minerals/Olivine/z_orientation_(Fabian_et_al._2001)/"
    "olivine_Z_Fabian_2001.ri"
)


def _olivine_ground_truth(olivine_ri) -> pl.DataFrame:
    fabian = (
        pl.read_csv(
            olivine_ri,
            has_header=False,
            new_columns=["WAVN", "N", "K"],
            schema_overrides={"WAVN": pl.Float64, "N": pl.Float64, "K": pl.Float64},
            comment_prefix="#",
            separator="\t",
        )
        .with_columns(pl.col("WAVN").mul(1e2))
        .sort("WAVN")
    )
    fabian.columns = ["w", "n", "k"]
    return fabian


def test_olivine_fabian(olivine_ri):
    fabian = _olivine_ground_truth(olivine_ri)

    # Test loading directly from the local fixture (no cache needed)
    aria = Aria(path=olivine_ri, wavelength=False)
    plt.assert_frame_equal(fabian, aria.nk)

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
    interpolated = aria.interpolate(groundtrouth["w"].to_numpy())
    plt.assert_frame_equal(groundtrouth, interpolated)


def test_olivine_fabian_handler(olivine_ri):
    # Resolves against the download cache + host dispatch; skips if not cached.
    skip_if_not_cached(Aria, ARIA_REL)
    fabian = _olivine_ground_truth(olivine_ri)
    handler = Handler(
        url=f"https://eodg.atm.ox.ac.uk/ARIA/{ARIA_REL}",
        wavelength=False,
    )
    plt.assert_frame_equal(fabian, handler.nk)


def test_aria_scale_wavelength_and_wavenumber():
    aria = Aria()
    aria._x_type = "wavelength"
    assert aria.scale == 1e-6
    aria._x_type = "wavenumber"
    assert aria.scale == 1e2


def test_aria_scale_invalid_x_type():
    aria = Aria()
    aria._x_type = "bogus"
    with pytest.raises(ValueError):
        _ = aria.scale


def test_aria_no_path_raises():
    with pytest.raises(ValueError):
        _ = Aria().data
