import warnings
from typing import Tuple

import numpy as np
import scipy.optimize as opt
from scipy.ndimage import median_filter


def get_xy_arrays(
    image: np.ndarray, sx: int = 0, sy: int = 0, xscale: float = 1.0, yscale: float = 1.0
) -> Tuple[np.ndarray, np.ndarray]:
    """Returns arrays of pixel center coordinates along the x and y axis.

    Args:
        image: 2D array representing the image data.
        sx: Index of the first x pixel when using an ROI, defaults to 0.
        sy: Index of the first y pixel when using an ROI, defaults to 0.

    Returns:
        x: Center corrdinates of each pixel in the x direction.
        y: Center coordinates of each pixel in the y direction.
    """
    Y, X = image.shape
    x = np.arange(0, X) + sx + 0.5
    y = np.arange(0, Y) + sy + 0.5
    x = x*xscale
    y = y*yscale
    return x, y


def gaussian_fit_projections(
    image: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    p0x,
    p0y,
    estimateA=False,
    estimateCen=False,
    estimateOffset=False,
    medianFilter=False,
):
    """Fits a Gaussian to the projections of an image.

    If the fit fails to converge, None will be returned instead of the parameters for an axis.

    Args:
        image: 2D array representing image data.
        x: Center coordinates of each pixel in the x direction.
        y: Center coordinates of each pixel in the y direction.
        p0x: Initial guess for the x fit (A, x0, sigma, offset).
        p0y: Initial guess for the y fit (A, y0, sigma, offset).

    Returns:
        x_proj: Projection of the image in x after filtering.
        y_proj: Projection of the image in y after filtering.
        px: Fit parameters for the x fit (A, x0, sigma, offset).
        py: Fit parameters for the y fit (A, y0, sigma, offset).
    """
    if medianFilter:
        image = median_filter(image, 3)
    x_proj = image.sum(axis=0, dtype="float")
    y_proj = image.sum(axis=1, dtype="float")

    # Use the maximum value of the projections as the amplitude
    if estimateA:
        p0x[0] = np.max(x_proj)
        p0y[0] = np.max(y_proj)
        if p0x[0] < 0.0:
            p0x[0] = 1.0
        if p0y[0] < 0.0:
            p0y[0] = 1.0
    # Use the location of the maximum value as the center
    if estimateCen:
        p0x[1] = x[np.argmax(x_proj)]
        p0y[1] = y[np.argmax(y_proj)]
    # Use the values at the edge to estimate the offset
    if estimateOffset:
        p0x[3] = np.average(x_proj[0:10])
        p0y[3] = np.average(y_proj[0:10])
    # If we start fitting a hot pixel, snap out of it!
    if p0x[2] < 1.0:
        p0x[2] = 10.0
    if p0y[2] < 1.0:
        p0y[2] = 10.0
    p0x[2] = 1 / (2 * p0x[2] ** 2)
    p0y[2] = 1 / (2 * p0y[2] ** 2)
    boundsx = ([0.0, x[0], 0.0, 0.0], [np.inf, x[-1], np.inf, np.inf])
    boundsy = ([0.0, y[0], 0.0, 0.0], [np.inf, y[-1], np.inf, np.inf])
    try:
        px, covariancex = opt.curve_fit(_gaussian, x, x_proj, p0=p0x, bounds=boundsx)
        px[2] = 1 / np.sqrt(2 * px[2])
    except RuntimeError:
        px = None
    except ValueError:
        px = None
        print(
            f"Fit failed. Guess of: {p0x} is not within bounds ({boundsx[0]}, {boundsx[1]})"
        )
    try:
        py, covariancey = opt.curve_fit(_gaussian, y, y_proj, p0=p0y, bounds=boundsy)
        py[2] = 1 / np.sqrt(2 * py[2])
    except RuntimeError:
        py = None
    except ValueError:
        py = None
        print(
            f"Fit failed. Guess of: {p0y} is not within bounds ({boundsy[0]}, {boundsy[1]})"
        )
    return x_proj, y_proj, px, py


def _gaussian(x, A, x0, C, offset):
    y = A * np.exp(-C * ((x - x0) ** 2)) + offset
    return y


def gaussian(x, A, x0, sigma, offset):
    y = A * np.exp(-((x - x0) ** 2) / (2 * sigma**2)) + offset
    return y


def findImageCenter(image, x, y, config, previousPx, previousPy):
    medianFilter = False
    if "medianFilter" in config:
        medianFilter = config["medianFilter"]
    p0x = [1.0, x[0], 10.0, 0.0]
    p0y = [1.0, y[0], 10.0, 0.0]
    if previousPx is not None and previousPy is not None:
        p0x = previousPx
        p0y = previousPy
    x_proj, y_proj, px, py = gaussian_fit_projections(
        image,
        x,
        y,
        p0x,
        p0y,
        estimateA=True,
        estimateCen=True,
        medianFilter=medianFilter,
    )
    if px is None:
        px = p0x
    if py is None:
        py = p0x
    centerX = px[1]
    centerY = py[1]
    centroid = (centerX, centerY)
    return centroid, px, py, x_proj, y_proj
