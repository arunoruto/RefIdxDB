from functools import cached_property

import numpy as np
import polars as pl
from pydantic import ConfigDict
from refidxdb.file import File


class DAT(File):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @cached_property
    def data(self):
        if self.path == "":
            raise Exception("Path is not set, cannot retrieve any data!")

        try:
            data = np.loadtxt(
                self.path,
                comments="#",
                dtype=np.float64,
                encoding="latin-1",
            )
        except UnicodeDecodeError as ue:
            self._logger.warning(f"UnicodeDecodeError: {ue}")
            self._logger.warning("Trying utf-8")
            data = np.loadtxt(
                self.path,
                comments="#",
                dtype=np.float64,
                encoding="utf-8",
            )

        return pl.DataFrame(
            data,
            schema={h: pl.Float64 for h in ["w", "n", "k"]},
        )
