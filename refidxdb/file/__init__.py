from io import StringIO
from pathlib import Path
from typing import Literal

from pydantic import ConfigDict, Field

from refidxdb.refidxdb import RefIdxDB

CHUNK_SIZE = 8192


class File(RefIdxDB):
    path: str | StringIO | Path = Field(default="")
    w_column: Literal["wl", "wn"] = Field(default="wl")

    model_config = ConfigDict(arbitrary_types_allowed=True)
