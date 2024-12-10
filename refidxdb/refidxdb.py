from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

import numpy as np
import numpy.typing as npt
import polars as pl
from pydantic import BaseModel, Field
from tqdm import tqdm

CHUNK_SIZE = 8192


class RefIdxDB(BaseModel, ABC):
    path: str | None = Field(default=None)
    wavelength: bool = Field(default=True)
    # _scale: float | None = None

    @property
    def cache_dir(self) -> str:
        """
        The directory where the cached data will.
        Defaults to $HOME/.cache/<__file__>.
        """
        return str(Path.home()) + "/.cache/refidxdb/" + self.__class__.__name__

    @property
    @abstractmethod
    def url(self) -> str:
        """
        A mandatory property that provides the URL for downloading the database.
        """

    @property
    @abstractmethod
    def scale(self) -> float:
        """
        A mandatory property that provides the default wavelength scale of the data.
        """

    def download(self, position: int | None = None) -> None:
        """
        Download the database from <url>
        and place it in <cache_dir>.
        """
        if self.url.split(".")[-1] == "zip":
            response = urlopen(self.url)
            total_size = int(response.headers.get("content-length", 0))
            data = b""
            with tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                desc=self.__class__.__name__,
                position=position,
            ) as progress:
                while chunk := response.read(CHUNK_SIZE):
                    data += chunk
                    progress.update(len(chunk))
            file = ZipFile(BytesIO(data))
            file.extractall(path=self.cache_dir)
        else:
            raise Exception("Extension not supported for being downloaded")

    @property
    @abstractmethod
    def data(self):
        """
        Get the raw data from the file provided by <path>.
        """

    @property
    @abstractmethod
    def nk(self) -> pl.DataFrame:
        """
        Refractive index values from the raw data
        """

    def interpolate(
        self,
        target: npt.NDArray[np.float64],
        scale: float | None = None,
        complex: bool = False,
    ) -> pl.DataFrame | npt.NDArray[np.complex128]:
        """
        Interpolate the refractive index values to the target array.
        """
        if scale is None:
            if self.wavelength:
                scale = 1e-6
            else:
                scale = 1e2

        interpolated = pl.DataFrame(
            dict(
                {"w": target},
                **{
                    n_k: np.interp(
                        target * scale,
                        self.nk["w"],
                        self.nk[n_k],
                        left=np.min(self.nk[n_k].to_numpy()),
                        right=np.max(self.nk[n_k].to_numpy()),
                    )
                    for n_k in ["n", "k"]
                },
            )
        )

        if complex:
            return interpolated["n"].to_numpy() + 1j * interpolated["k"].to_numpy()

        return interpolated
