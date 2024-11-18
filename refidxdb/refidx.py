from io import StringIO

import polars as pl
import yaml

from .refidxdb import RefIdxDB


class RefIdx(RefIdxDB):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    @property
    def url(self) -> str:
        return "https://github.com/polyanskiy/refractiveindex.info-database/releases/download/v2024-08-14/rii-database-2024-08-14.zip"

    @property
    def data(self):
        absolute_path = f"{self.cache_dir}/{self._path}"
        if self._path is None:
            raise Exception("Path is not set, cannot retrieve any data!")
        with open(absolute_path, "r") as f:
            data = yaml.safe_load(f)
            return data

    @property
    def nk(self):
        nk = pl.DataFrame(schema={"w": float, "n": float, "k": float})

        for data in self.data["DATA"]:
            if data["type"] == "tabulated nk":
                _nk = pl.read_csv(
                    StringIO(data["data"]),
                    new_columns=["w", "n", "k"],
                    separator=" ",
                )
                nk = pl.concat([nk, _nk], how="vertical")

        return nk.with_columns(pl.col("w").mul(self.scale)).sort("w")
