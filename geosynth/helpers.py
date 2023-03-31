from typing import Dict

import numpy as np


def _first_last_nonzero(mask, axis):
    if mask.ndim != 2:
        raise ValueError

    res = np.nonzero(mask.any(axis=axis))[0]
    return res[0], res[-1]


def instance_bbox(mask: np.ndarray) -> np.ndarray:
    """Compute the normalized inclusive bounding box for a binary mask.

    Parameters
    ----------
    mask: numpy.ndarray
        (H, W) binary mask.

    Returns
    -------
    numpy.ndarray
        A numpy array of shape ``(4)`` representing
        ``[top_left_x, top_left_y, bottom_right_x, bottom_right_y]``.
        All values are in range ``[0, 1]``.
        If there are no ``True`` pixels, then all values are ``nan``.
    """
    if mask.any():
        h, w = mask.shape
        top_left_y, bottom_right_y = _first_last_nonzero(mask, 1)
        top_left_x, bottom_right_x = _first_last_nonzero(mask, 0)
        bbox = np.array(
            [top_left_x, top_left_y, bottom_right_x, bottom_right_y],
            dtype=np.float32,
        )
        bbox[0] /= w
        bbox[1] /= h
        bbox[2] /= w
        bbox[3] /= h
    else:
        bbox = np.array([0, 0, 0, 0], dtype=np.float32)
        bbox[:] = np.nan
    return bbox


def instance_segmentation_bboxes(
    instances_dict: Dict[str, np.ndarray]
) -> Dict[str, np.ndarray]:
    """Compute all bounding boxes for an instance segmentation dictionary.

    Parameters
    ----------
    instances_dict: Dict[str, np.ndarray]
        Instances mapping string labels to ``(N, H, W)`` binary masks.

    Returns
    -------
    Dict[str, np.ndarray]
        Dictionary with same keys as ``instances_dict``, but each value is an ``(N, 4)``
        array where each row represents the normalized coordinates
        ``[top_left_x, top_left_y, bottom_right_x, bottom_right_y]``.
    """
    bboxes = {}
    for label, masks in instances_dict.items():
        bboxes[label] = []
        for mask in masks:
            bboxes[label].append(instance_bbox(mask))
        bboxes[label] = np.stack(bboxes[label], axis=0)
    return bboxes
