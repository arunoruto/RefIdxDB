import logging
from abc import ABC, abstractmethod

import numpy as np
import numpy.typing as npt
import polars as pl
from pydantic import BaseModel, Field, PrivateAttr

CHUNK_SIZE = 8192


class RefIdxDB(BaseModel, ABC):
    wavelength: bool = Field(default=True)
    _logger: logging.Logger = PrivateAttr(default=logging.getLogger(f"Base.{__name__}"))

    def model_post_init(self, __context):
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    @property
    @abstractmethod
    def scale(self) -> float:
        """
        A mandatory property that provides the default wavelength scale of the data.
        """

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
