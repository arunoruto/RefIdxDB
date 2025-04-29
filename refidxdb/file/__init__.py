from functools import cached_property
from io import StringIO
from pathlib import Path
from typing import Literal

import polars as pl
from pydantic import ConfigDict, Field

from refidxdb.refidxdb import RefIdxDB

CHUNK_SIZE = 8192


class File(RefIdxDB):
    path: str | StringIO | Path = Field(default="")
    w_column: Literal["wl", "wn"] = Field(default="wl")
    scale: float | None = Field(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def model_post_init(self, __context):
        super().model_post_init(__context)

        if self.scale is None:
            self.scale = 1e-6 if self.w_column == "wl" else 1e2
        self._logger.info(f"Scale set to {self.scale}")

    @cached_property
    def nk(self):
        if self.data is None:
            raise Exception("Data could not have been loaded")

        w = self.data["w"] * self.scale
        match (self.wavelength, self.w_column):
            case (True, "wn") | (False, "wl"):
                w = 1 / w
            # case (True, "wl") | (False, "wn"):
            #     w = self.data["w"]

        nk = {
            "w": w,
            "n": self.data["n"] if ("n" in self.data.columns) else None,
            "k": self.data["k"] if ("k" in self.data.columns) else None,
        }

        return pl.DataFrame(nk).sort("w")
