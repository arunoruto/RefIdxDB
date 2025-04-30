from functools import cached_property
from typing import Any, Literal
from urllib.parse import unquote

import numpy as np
import numpy.typing as npt
import polars as pl
from pydantic import BaseModel, Field, HttpUrl, PrivateAttr
from rich.traceback import install

from refidxdb.file.csv import CSV
from refidxdb.file.dat import DAT
from refidxdb.refidxdb import RefIdxDB
from refidxdb.url.aria import Aria
from refidxdb.url.refidx import RefIdx

_ = install(show_locals=True)


class Handler(BaseModel):
    path: str | None = Field(
        default=None,
        description="Path to the refractive index file. Supported formats: CSV, DAT ",
    )
    url: HttpUrl | None = Field(
        default=None,
        description="URL of the refractive index data source. Supported sources: refractiveindex.info, eodg.atm.ox.ac.uk",
    )
    wavelength: bool = Field(
        default=True,
        description="How the output data should be treated: True - wavelength, False - wavenumber",
    )
    w_column: bool | Literal["wl", "wn"] = Field(
        default=True,
        description="Is the first column providing wavelength or wavenumber data? [True,'wl'] - wavelength, [False,'wn'] - wavenumber",
    )
    _source: RefIdxDB | None = PrivateAttr(default=None)

    def model_post_init(self, __context: Any) -> None:
        if self.url is not None:
            if self.url.path is None:
                raise Exception("Path of url is not present")
            path = unquote(self.url.path)
            # if path is None:
            #     raise Exception("Path of url is not present")
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
        elif self.path is not None:
            # TODO: quick fix, can be done nicer!
            if isinstance(self.w_column, bool):
                self.w_column = "wl" if self.w_column else "wn"
            match self.path.split(".")[-1].lower():
                case "csv":
                    self._source = CSV(
                        path=self.path,
                        wavelength=self.wavelength,
                        w_column=self.w_column,
                    )
                case "dat":
                    self._source = DAT(
                        path=self.path,
                        wavelength=self.wavelength,
                        w_column=self.w_column,
                    )
                case _:
                    raise Exception(f"Unsupported file type {self.path.split('.')[-1]}")
        else:
            raise Exception("Either path or url should be provided")

    # TODO: implemented for debuging, remove when not needed anymore
    @property
    def source(self) -> RefIdxDB | None:
        return self._source

    @cached_property
    def nk(self) -> pl.DataFrame:
        if self._source is None:
            raise Exception("Source is not initialized")
        return self._source.nk

    def interpolate(
        self,
        target: npt.NDArray[np.float64],
        scale: float | None = None,
        complex: bool = False,
    ) -> pl.DataFrame | npt.NDArray[np.complex128]:
        if self._source is None:
            raise Exception("Source is not initialized")
        return self._source.interpolate(target=target, scale=scale, complex=complex)
