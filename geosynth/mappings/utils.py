import numpy as np


def to_uint8(data: np.ndarray):
    return np.clip(np.round(data * 255), 0, 255).astype(np.uint8)


def apply_palette(palette: np.ndarray, data: np.ndarray) -> np.ndarray:
    """Colormap data by a pre-defined palette.

    Parameters
    ----------
    palette: np.ndarray
        (n, 3) array where each row is an RGB value.
    data: np.ndarray
        An int or float array that will index into ``palette``.
        If float, data must be in range ``[0, 1]``.
        If int, data must have max value ``<n``

    Returns
    -------
    np.ndarray
        Palette-applied data that has 1 dimensionality greater than ``data``.
        The last dimension is of length 3 and represents the mapped RGB value.
    """
    a = (data * 255).astype(np.uint8)
    b = (a + 1).clip(max=255)
    f = data * 255.0 - a
    pseudo_color = palette[a] + (palette[b] - palette[a]) * f[..., None]
    if palette.max() <= 1:
        return to_uint8(pseudo_color.clip(0, 1))
    else:
        return np.round(np.clip(pseudo_color, 0, 255)).astype(np.uint8)
