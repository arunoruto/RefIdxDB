from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Optional
from urllib.request import urlopen
from zipfile import ZipFile

import numpy as np
import polars as pl
from pydantic import BaseModel, Field
from tqdm import tqdm

CHUNK_SIZE = 8192


class RefIdxDB(BaseModel, ABC):
    path: Optional[str] = Field(default=None)
    wavelength: bool = Field(default=True)
    # _scale: Optional[float]

    @property
    def cache_dir(self) -> str:
        """
        The directory where the cached data will.
        Defaults to $HOME/.cache/<__file__>.
        """
        return str(Path.home()) + "/.cache/refidxdb/" + self.__class__.__name__

    # @property
    # def wavelength(self) -> bool:
    #     """
    #     Property that represents if the x-axis column represents
    #     wavelengths (true) or wavenumbers (false).
    #     """
    #     return self.wavelength

    # @wavelength.setter
    # def wavelength(self, value: bool) -> None:
    #     """
    #     Set the default value if the main column is of type
    #     wavelength or wavenumber
    #     """
    #     self.wavelength = value

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
        # return (
        #     self._scale
        #     if (self._scale is not None)
        #     else (1e-6 if self.wavelength else 1e2)
        # )

    # @scale.setter
    # def scale(self, value: float) -> None:
    #     """
    #     Set the wavelength scale if it deviates from the default value.
    #     """
    #     self._scale = value

    def download(self) -> None:
        """
        Download the database from <url>
        and place it in <cache_dir>.
        """
        if self.url.split(".")[-1] == "zip":
            # print(
            #     f"Downloading the database for {self.__class__.__name__} from {self.url} to {self.cache_dir}"
            # )
            response = urlopen(self.url)
            total_size = int(response.headers.get("content-length", 0))
            data = b""
            with tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                desc=self.__class__.__name__,
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
    def nk(self) -> pl.datatypes.DataType:
        """
        Refractive index values from the raw data
        """

    def interpolate(
        self,
        target,
        scale: Optional[float] = None,
        complex: bool = False,
    ) -> pl.datatypes.DataType:
        if scale is None:
            if self.wavelength:
                scale = 1e-6
            else:
                scale = 1e2

        # print(scale)
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
            return interpolated["n"] + 1j * interpolated["k"]
        else:
            return interpolated
