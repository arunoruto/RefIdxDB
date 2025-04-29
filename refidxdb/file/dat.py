from functools import cached_property

import numpy as np
import polars as pl
from pydantic import ConfigDict
from refidxdb.file import File


class DAT(File):
    _x_type: str = "wavelength"

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def scale(self) -> float:
        # TODO: implement it nicely with a new field, maybe in File?
        return 1e-6

    @cached_property
    def data(self):
        if self.path == "":
            raise Exception("Path is not set, cannot retrieve any data!")

        try:
            data = np.loadtxt(
                self.path,
                comments="#",
                dtype=np.float64,
            )
        except UnicodeDecodeError as ue:
            self._logger.warning(f"UnicodeDecodeError: {ue}")
            self._logger.warning("Trying latin-1")
            data = np.loadtxt(
                self.path,
                comments="#",
                dtype=np.float64,
                encoding="latin-1",
            )

        return pl.DataFrame(
            data,
            schema={h: pl.Float64 for h in ["w", "n", "k"]},
        )

    @cached_property
    def nk(self):
        if self.data is None:
            raise Exception("Data could not have been loaded")
        # Using a small trick
        # micro is 10^-6 and 1/centi is 10^2,
        # but we will use 10^-2, since the value needs to be inverted
        # local_scale = 1e-6 if "WAVL" in self.data.columns else 1e-2
        local_scale = 1e-6 if self.w_column == "wl" else 1e2
        match (self.wavelength, self.w_column):
            case (True, "wl") | (False, "wn"):
                w = self.data["w"]
            case (True, "wn") | (False, "wl"):
                w = 1 / self.data["w"]

        nk = {
            "w": w * local_scale,
            "n": self.data["n"] if ("n" in self.data.columns) else None,
            "k": self.data["k"] if ("k" in self.data.columns) else None,
        }

        return pl.DataFrame(nk).sort("w")
