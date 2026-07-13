"""Tests for the shared ``RefIdxDB.interpolate`` implementation.

A tiny CSV with **non-monotonic** ``n`` lets us tell endpoint-clamping apart
from the previous (buggy) global-min/max extrapolation.
"""

import numpy as np
import polars.testing as plt
import pytest

from refidxdb.file.csv import CSV


@pytest.fixture
def tiny_csv(tmp_path) -> str:
    path = tmp_path / "tiny.csv"
    path.write_text("w,n,k\n1,3.0,0.1\n2,1.0,0.2\n3,2.0,0.3\n")
    return str(path)


def test_interpolate_linear_in_range(tiny_csv):
    csv = CSV(path=tiny_csv, w_column="wl", wavelength=True)
    out = csv.interpolate(np.array([1.5, 2.5]), scale=1e-6)
    # halfway between (3.0, 1.0) and (1.0, 2.0)
    np.testing.assert_allclose(out["n"].to_numpy(), [2.0, 1.5])
    np.testing.assert_allclose(out["k"].to_numpy(), [0.15, 0.25])


def test_interpolate_clamps_to_endpoints(tiny_csv):
    csv = CSV(path=tiny_csv, w_column="wl", wavelength=True)
    out = csv.interpolate(np.array([0.0, 5.0]), scale=1e-6)
    # Below range -> first value (3.0); above range -> last value (2.0).
    # The old min/max fill would have given [1.0, 3.0] instead.
    np.testing.assert_allclose(out["n"].to_numpy(), [3.0, 2.0])
    np.testing.assert_allclose(out["k"].to_numpy(), [0.1, 0.3])


def test_interpolate_as_complex(tiny_csv):
    csv = CSV(path=tiny_csv, w_column="wl", wavelength=True)
    target = np.array([1.5, 2.5])
    frame = csv.interpolate(target, scale=1e-6)
    result = csv.interpolate(target, scale=1e-6, as_complex=True)
    assert result.dtype == np.complex128
    np.testing.assert_allclose(
        result, frame["n"].to_numpy() + 1j * frame["k"].to_numpy()
    )


def test_default_scale_wavelength(tiny_csv):
    csv = CSV(path=tiny_csv, w_column="wl", wavelength=True)
    target = np.array([1.5, 2.5])
    plt.assert_frame_equal(
        csv.interpolate(target),
        csv.interpolate(target, scale=1e-6),
    )


def test_default_scale_wavenumber(tiny_csv):
    csv = CSV(path=tiny_csv, w_column="wn", wavelength=False)
    target = np.array([1.5, 2.5])
    plt.assert_frame_equal(
        csv.interpolate(target),
        csv.interpolate(target, scale=1e2),
    )
