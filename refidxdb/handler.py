from functools import cached_property
from typing import Any

from pydantic import BaseModel, Field, HttpUrl
from rich.traceback import install

from refidxdb.aria import Aria
from refidxdb.refidx import RefIdx
from refidxdb.refidxdb import RefIdxDB

install(show_locals=True)


class Handler(BaseModel):
    url: HttpUrl
    wavelength: bool = Field(default=True)
    _source: RefIdxDB

    def model_post_init(self, __context: Any) -> None:
        match self.url.host:
            case "refractiveindex.info":
                self._source = RefIdx(
                    path=self.url.path.strip("/"),
                    wavelength=self.wavelength,
                )
            case "eodg.atm.ox.ac.uk":
                path = self.url.path
                if path.startswith("/ARIA/"):
                    path = path[6:]
                self._source = Aria(
                    path=path,
                    wavelength=self.wavelength,
                )
            case _:
                raise Exception(f"Unsupported source ${self.url.host}")

    @cached_property
    def nk(self):
        return self._source.nk
