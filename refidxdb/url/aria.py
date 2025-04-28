import re
from functools import cached_property

import polars as pl

from . import URL


class Aria(URL):
    _x_type: str = "wavelength"

    @property
    def url(self) -> str:
        return "https://eodg.atm.ox.ac.uk/ARIA/data_files/ARIA.zip"

    @property
    def scale(self) -> float:
        match self._x_type:
            case "wavelength":
                return 1e-6
            case "wavenumber":
                return 1e2
            case _:
                raise Exception(f"Unsupported {self._x_type} type for x-axis")

    @cached_property
    def data(self):
        if self.path is None:
            raise Exception("Path is not set, cannot retrieve any data!")
        if self.path.startswith("/"):
            absolute_path = self.path
        else:
            absolute_path = f"{self.cache_dir}/{self.path}"
        with open(absolute_path, "r", encoding="cp1252") as f:
            data = f.readlines()
            header = [h for h in data if h.startswith("#")]
            header = [h for h in header if not h.startswith("##")]
            header = [h.split("=") for h in header]
            header = {h[0][1:].strip(): h[1].strip() for h in header}
            # print(header)
            data = [d.strip() for d in data if not d.startswith("#")]
            data = re.sub(r"[ \t]{1,}", " ", "\n".join(data))

        if "WAVN" in header["FORMAT"]:
            self._x_type = "wavenumber"

        return pl.read_csv(
            data.encode(),
            schema_overrides={h: pl.Float64 for h in header["FORMAT"].split(" ")},
            comment_prefix="#",
            separator=" ",
        )

    @cached_property
    def nk(self):
        if self.data is None:
            raise Exception("Data could not have been loaded")
        # Using a small trick
        # micro is 10^-6 and 1/centi is 10^2,
        # but we will use 10^-2, since the value needs to be inverted
        local_scale = 1e-6 if "WAVL" in self.data.columns else 1e-2
        if self.wavelength:
            w = (
                self.data["WAVL"]
                if ("WAVL" in self.data.columns)
                else 1 / (self.data["WAVN"])
            ) * local_scale
        else:
            w = (
                self.data["WAVN"]
                if ("WAVN" in self.data.columns)
                else 1 / (self.data["WAVL"])
            ) / local_scale
        nk = {
            "w": w,
            "n": self.data["N"] if ("N" in self.data.columns) else None,
            "k": self.data["K"] if ("K" in self.data.columns) else None,
        }

        return pl.DataFrame(nk).sort("w")
