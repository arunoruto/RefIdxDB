from abc import abstractmethod
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

from pydantic import Field
from refidxdb.refidxdb import RefIdxDB
from tqdm import tqdm

CHUNK_SIZE = 8192


class URL(RefIdxDB):
    path: str | None = Field(default=None)

    @property
    @abstractmethod
    def scale(self) -> float:
        """
        A mandatory property that provides the default wavelength scale of the data.
        """

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

    def download(self, position: int | None = None) -> None:
        """
        Download the database from <url>
        and place it in <cache_dir> if <url> is not a filepath.
        """
        if self.url.startswith("/") or self.url.startswith("file://"):
            self._logger.info(f"Reading from local file: {self.url}")
        else:
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
