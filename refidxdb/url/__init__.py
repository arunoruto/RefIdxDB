import os
from abc import abstractmethod
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

from pydantic import Field
from tqdm import tqdm

from refidxdb.refidxdb import RefIdxDB

CHUNK_SIZE = 8192
# Per-socket-operation timeout (seconds) so a stalled connection cannot hang
# the download forever.
DOWNLOAD_TIMEOUT = 30


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
        The directory where the cached data is stored.
        Defaults to ``$XDG_CACHE_HOME/refidxdb/<class name>``, falling back to
        ``$HOME/.cache/refidxdb/<class name>``.
        """
        base = os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache")
        return str(Path(base) / "refidxdb" / self.__class__.__name__)

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
            return

        if not self.url.endswith(".zip"):
            raise ValueError("Extension not supported for being downloaded")

        buffer = bytearray()
        with urlopen(self.url, timeout=DOWNLOAD_TIMEOUT) as response:
            total_size = int(response.headers.get("content-length", 0))
            with tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                desc=self.__class__.__name__,
                position=position,
            ) as progress:
                while chunk := response.read(CHUNK_SIZE):
                    buffer.extend(chunk)
                    progress.update(len(chunk))

        with ZipFile(BytesIO(bytes(buffer))) as archive:
            archive.extractall(path=self.cache_dir)
