from functools import cached_property

import polars as pl
from pydantic import ConfigDict
from refidxdb.file import File


class CSV(File):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @cached_property
    def data(self):
        if self.path == "":
            raise Exception("Path is not set, cannot retrieve any data!")

        return pl.read_csv(
            self.path,
            schema_overrides={h: pl.Float64 for h in ["w", "n", "k"]},
            comment_prefix="#",
            # separator=" ",
        )
