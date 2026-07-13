from functools import cached_property
from typing import Any, Literal
from urllib.parse import unquote

import numpy as np
import numpy.typing as npt
import polars as pl
from pydantic import BaseModel, Field, HttpUrl, PrivateAttr, field_validator

from refidxdb.file.csv import CSV
from refidxdb.file.dat import DAT
from refidxdb.refidxdb import RefIdxDB
from refidxdb.url.aria import Aria
from refidxdb.url.refidx import RefIdx


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
        validate_default=True,
        description="Is the first column providing wavelength or wavenumber data? [True,'wl'] - wavelength, [False,'wn'] - wavenumber",
    )
    _source: RefIdxDB | None = PrivateAttr(default=None)

    @field_validator("w_column", mode="before")
    @classmethod
    def _normalize_w_column(cls, value: Any) -> Any:
        """Normalize the boolean shorthand to the explicit ``wl``/``wn`` form."""
        if isinstance(value, bool):
            return "wl" if value else "wn"
        return value

    def model_post_init(self, __context: Any) -> None:
        if self.url is not None:
            if self.url.path is None:
                raise ValueError("Path of url is not present")
            path = unquote(self.url.path)
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
                    raise ValueError(f"Unsupported source {self.url.host}")
        elif self.path is not None:
            extension = self.path.split(".")[-1].lower()
            match extension:
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
                    raise ValueError(f"Unsupported file type {extension}")
        else:
            raise ValueError("Either path or url should be provided")

    # TODO: implemented for debuging, remove when not needed anymore
    @property
    def source(self) -> RefIdxDB | None:
        return self._source

    @cached_property
    def nk(self) -> pl.DataFrame:
        if self._source is None:
            raise RuntimeError("Source is not initialized")
        return self._source.nk

    def interpolate(
        self,
        target: npt.NDArray[np.float64],
        scale: float | None = None,
        as_complex: bool = False,
    ) -> pl.DataFrame | npt.NDArray[np.complex128]:
        if self._source is None:
            raise RuntimeError("Source is not initialized")
        return self._source.interpolate(
            target=target, scale=scale, as_complex=as_complex
        )
