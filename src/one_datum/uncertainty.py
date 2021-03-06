# -*- coding: utf-8 -*-

__all__ = ["get_uncertainty_model"]

from typing import Optional

import numpy as np
import pkg_resources
from astropy.io import fits
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import gaussian_filter


def get_uncertainty_model(
    *,
    color_smoothing_scale: float = 0.1,
    mag_smoothing_scale: float = 0.1,
    bounds_error: bool = False,
    fill_value: Optional[float] = None
) -> RegularGridInterpolator:
    filename = pkg_resources.resource_filename(
        __name__, "data/rv_uncertainty_grid.fits"
    )

    with fits.open(filename) as f:
        hdr = f[0].header
        mu = f[1].data

    color_bins = np.linspace(
        hdr["MIN_COL"], hdr["MAX_COL"], hdr["NUM_COL"] + 1
    )
    mag_bins = np.linspace(hdr["MIN_MAG"], hdr["MAX_MAG"], hdr["NUM_MAG"] + 1)

    dc = color_smoothing_scale / (color_bins[1] - color_bins[0])
    dm = mag_smoothing_scale / (mag_bins[1] - mag_bins[0])

    ln_sigma_model = gaussian_filter(np.mean(mu, axis=-1), (dm, dc))
    return RegularGridInterpolator(
        [
            0.5 * (mag_bins[1:] + mag_bins[:-1]),
            0.5 * (color_bins[1:] + color_bins[:-1]),
        ],
        ln_sigma_model,
        bounds_error=bounds_error,
        fill_value=fill_value,
    )
