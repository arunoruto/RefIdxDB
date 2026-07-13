"""Network-free tests for URL.download / cache_dir (urlopen is mocked)."""

import io
import zipfile
from pathlib import Path

import pytest

import refidxdb.url as url_mod
from refidxdb.url.aria import Aria


class FakeResponse:
    """Minimal stand-in for the urlopen result used by ``URL.download``."""

    def __init__(self, data: bytes):
        self._buf = io.BytesIO(data)
        self.headers = {"content-length": str(len(data))}

    def read(self, size: int = -1) -> bytes:
        return self._buf.read(size)

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *exc) -> bool:
        return False


def _zip_bytes(name: str, content: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        archive.writestr(name, content)
    return buf.getvalue()


def test_download_extracts_zip(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    monkeypatch.setattr(
        url_mod, "urlopen", lambda u, timeout=None: FakeResponse(_zip_bytes("hi.txt", "x"))
    )

    Aria().download()

    extracted = tmp_path / "refidxdb" / "Aria" / "hi.txt"
    assert extracted.exists()
    assert extracted.read_text() == "x"


def test_download_local_file_is_noop(monkeypatch):
    # A local path url should log and return without ever calling urlopen.
    monkeypatch.setattr(Aria, "url", property(lambda self: "/local/archive.zip"))

    def _boom(*a, **k):
        raise AssertionError("urlopen must not be called for local files")

    monkeypatch.setattr(url_mod, "urlopen", _boom)
    Aria().download()  # should not raise


def test_download_rejects_non_zip(monkeypatch):
    monkeypatch.setattr(Aria, "url", property(lambda self: "https://x.example/file.txt"))
    with pytest.raises(ValueError):
        Aria().download()


def test_cache_dir_honors_xdg(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    assert Aria().cache_dir == str(tmp_path / "refidxdb" / "Aria")


def test_cache_dir_falls_back_to_home(monkeypatch):
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    expected = str(Path.home() / ".cache" / "refidxdb" / "Aria")
    assert Aria().cache_dir == expected
