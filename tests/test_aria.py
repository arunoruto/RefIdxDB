import os

import polars as pl
import polars.testing as plt

from refidxdb.aria import Aria


def test_olivine_fabian():
    # with open(os.path.dirname(__file__) + "/data/olivine_Z_Fabian_2001.ri", "r") as f:
    #     fabian = pl.read_csv()
    fabian = (
        pl.read_csv(
            os.path.dirname(__file__) + "/data/olivine_Z_Fabian_2001.ri",
            # new_columns=["w", "n", "k"],
            schema_overrides={"WAVN": pl.Float64, "N": pl.Float64, "K": pl.Float64},
            comment_prefix="#",
            separator="\t",
        )
        # .with_columns(pl.col("WAVN").mul(1e2), pl.col("WAVN").pow(-1.0))
        .with_columns(pl.col("WAVN").mul(1e2))
        .with_columns(pl.col("WAVN").pow(-1))
        .sort("WAVN")
    )
    fabian.columns = ["w", "n", "k"]

    # Test loading
    aria = Aria(
        "data_files/Minerals/Olivine/z_orientation_(Fabian_et_al._2001)/olivine_Z_Fabian_2001.ri",
        wavelength=False
    )
    plt.assert_frame_equal(fabian, aria.nk)

    # Test interpolation
    groundtrouth = pl.DataFrame({
        "w": [2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0],
        "n": [0.105641, 1.611649471444462, 1.5898492460210492, 1.5586036797132963, 1.51408793265999, 1.448690631095037, 1.344766586942427, 1.1480505079815155],
        "k": [2.6e-05, 9.432642777690439e-05, 0.000243, 0.0005345957547495901, 0.001089988042820639, 0.002197400666968059, 0.0047149236962747525, 0.012472195473009333]
    })
    interpolated = aria.interpolate(groundtrouth["w"], scale=1e-6)
    plt.assert_frame_equal(groundtrouth, interpolated)
