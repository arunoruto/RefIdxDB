import polars as pl

from .refidxdb import RefIdxDB


class Aria(RefIdxDB):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    @property
    def url(self) -> str:
        return "https://eodg.atm.ox.ac.uk/ARIA/data_files/ARIA.zip"

    @property
    def data(self):
        absolute_path = f"{self.cache_dir}/{self._path}"
        if self._path is None:
            raise Exception("Path is not set, cannot retrieve any data!")
        with open(absolute_path, "r", encoding="cp1252") as f:
            header = [h[1:].split("=") for h in f.readlines() if h.startswith("#")]
            header = {h[0]: h[1].strip() for h in header}
        return pl.read_csv(
            absolute_path,
            # new_columns=header["FORMAT"].split(" "),
            schema_overrides={h: pl.Float64 for h in header["FORMAT"].split(" ")},
            comment_prefix="#",
            separator="\t",
        )

    @property
    def nk(self):
        if self.data is None:
            raise Exception("Data could not have been loaded")
        nk = {
            "w": self.data["WAVL"] * self.scale
            if (self._wavelength and ("WAVL" in self.data.columns))
            else 1 / (self.data["WAVN"] * self.scale),
            "n": self.data["N"] if ("N" in self.data.columns) else None,
            "k": self.data["K"] if ("K" in self.data.columns) else None,
        }
        return pl.DataFrame(nk).sort("w")
