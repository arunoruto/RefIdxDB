from io import StringIO

from pydantic import ConfigDict, Field

from refidxdb.refidxdb import RefIdxDB

CHUNK_SIZE = 8192


class File(RefIdxDB):
    path: str | StringIO = Field(default="")

    model_config = ConfigDict(arbitrary_types_allowed=True)
