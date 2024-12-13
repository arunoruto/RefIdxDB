from functools import cached_property
from typing import Any

import polars as pl
from pydantic import BaseModel, Field, HttpUrl, PrivateAttr
from rich.traceback import install

from refidxdb.aria import Aria
from refidxdb.refidx import RefIdx
from refidxdb.refidxdb import RefIdxDB

_ = install(show_locals=True)


class Handler(BaseModel):
    url: HttpUrl
    wavelength: bool = Field(default=True)
    _source: RefIdxDB | None = PrivateAttr(default=None)

    def model_post_init(self, __context: Any) -> None:
        path = self.url.path
        if path is None:
            raise Exception("Path of url is not present")
        match self.url.host:
            case "refractiveindex.info":
                self._source = RefIdx(
                    path=path.strip("/"),
                    wavelength=self.wavelength,
                )
            case "eodg.atm.ox.ac.uk":
                if path.startswith("/ARIA/"):
                    path = path[6:]
                self._source = Aria(
                    path=path,
                    wavelength=self.wavelength,
                )
            case _:
                raise Exception(f"Unsupported source ${self.url.host}")

    @cached_property
    def nk(self) -> pl.DataFrame:
        return self._source.nk
