"""Instance segmentation visualization tools.

Some of this code has been heavily modified from MMSegmentation.
"""
import contextlib
from typing import Dict, Optional

import numpy as np

with contextlib.suppress(ImportError):
    import matplotlib.pyplot as plt
    from matplotlib.collections import PatchCollection
    from matplotlib.patches import Polygon

from ._plt_to_numpy import plt_to_numpy
from .helpers import instance_segmentation_bboxes


def plot_instances(
    img: np.ndarray,
    bboxes: np.ndarray,
    labels,
    segms=None,
    class_names=None,
    score_thr=0,
    thickness=1,
    font_size=10,
    min_area=0,
    show=False,
):
    """Draw bboxes and class labels (with scores) on an image.

    Parameters
    ----------
    img: np.ndarray
        RGB image.
    bboxes: np.ndarray
        Bounding boxes (with scores), shaped (n, 4) or (n, 5).
    labels: np.ndarray
        Labels of bboxes.
    segms: (ndarray or None)
        Masks, shaped (n,h,w) or None
    class_names: list[str]
        Names of each classes.
    score_thr: float
        Minimum score of bboxes to be shown.  Default: 0
    thickness: int
        Thickness of lines. Default: 1
    font_size: int
        Font size of texts. Default: 10
    show: bool
        Whether to show the image. Default: False

    Returns
    -------
        ndarray: The image with bboxes drawn on it.
    """
    if bboxes.ndim != 2:
        raise ValueError(f"bboxes ndim should be 2, but its ndim is {bboxes.ndim}.")
    if labels.ndim != 1:
        raise ValueError(f"labels ndim should be 1, but its ndim is {labels.ndim}.")
    if len(bboxes) != len(labels):
        raise ValueError("bboxes and labels must have the same length.")

    img = np.ascontiguousarray(img)

    if score_thr > 0:
        if bboxes.shape[1] != 5:
            raise ValueError("bbox scores must be provided if thresholding.")
        scores = bboxes[:, -1]
        inds = scores > score_thr
        bboxes = bboxes[inds, :]
        labels = labels[inds]
        if segms is not None:
            segms = segms[inds, ...]

    mask_colors = []
    if labels.shape[0] > 0:
        # random color
        np.random.seed(42)
        mask_colors = [
            np.random.randint(0, 256, (1, 3), dtype=np.uint8)
            for _ in range(max(labels) + 1)
        ]

    bbox_color = (0, 1, 0)
    text_color = (0, 1, 0)

    # remove white edges by set subplot margin
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax = plt.gca()
    ax.axis("off")
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    polygons = []
    color = []
    for i, (bbox, label) in enumerate(zip(bboxes, labels)):
        if np.isnan(bbox).any():
            continue

        bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        if bbox_area < min_area:
            continue

        bbox_int = bbox.astype(np.int32)
        poly = [
            [bbox_int[0], bbox_int[1]],
            [bbox_int[0], bbox_int[3]],
            [bbox_int[2], bbox_int[3]],
            [bbox_int[2], bbox_int[1]],
        ]
        np_poly = np.array(poly).reshape((4, 2))
        polygons.append(Polygon(np_poly))
        color.append(bbox_color)
        label_text = class_names[label] if class_names is not None else f"class {label}"
        if len(bbox) > 4:
            label_text += f"|{bbox[-1]:.02f}"
        ax.text(
            bbox_int[0],
            bbox_int[1],
            f"{label_text}",
            bbox={"facecolor": "black", "alpha": 0.8, "pad": 0.7, "edgecolor": "none"},
            color=text_color,
            fontsize=font_size,
            verticalalignment="top",
            horizontalalignment="left",
        )
        if segms is not None:
            color_mask = mask_colors[labels[i]]
            mask = segms[i].astype(bool)
            img[mask] = img[mask] * 0.5 + color_mask * 0.5

    plt.imshow(img)

    p = PatchCollection(
        polygons, facecolor="none", edgecolors=color, linewidths=thickness
    )
    ax.add_collection(p)

    if show:
        # We do not use cv2 for display because in some cases, opencv will
        # conflict with Qt, it will output a warning: Current thread
        # is not the object's thread. You can refer to
        # https://github.com/opencv/opencv-python/issues/46 for details
        plt.show()

    return img


def visualize_instances(
    instances_dict: Dict[str, np.ndarray],
    bboxes_dict: Optional[Dict[str, np.ndarray]] = None,
    rgb: Optional[np.ndarray] = None,
    dpi: int = 300,
    **kwargs,
) -> np.ndarray:
    """Plot object masks and bounding boxes over rgb image.

    Parameters
    ----------
    instances_dict : dict
        Dictionary mapping object label to a (N, H, W) boolean mask.
    bboxes_dict : dict
        If not provided, computed from ssegs.
    rgb : numpy.ndarray
        uint8 rgb image.
        If not provided, defaults to a black background.
    dpi: int
        DPI to render output figure at.
        300 is good for a high resolution visualization.
        100 is good for a low resolution visualization.
        Defaults 300.
    **kwargs
        Passed along to ``plot_instances``.  See ``plot_instances``.

    Returns
    -------
    np.ndarray
        RGB visualization of instance segmentation masks and bboxes.
    """
    if rgb is None:
        # Make a dummy black background
        h, w = list(instances_dict.values())[0].shape[1:3]
        rgb = np.zeros((h, w, 3), dtype=np.uint8)
    else:
        rgb = rgb.copy()

    if not instances_dict:
        return rgb

    if bboxes_dict is None:
        bboxes_dict = instance_segmentation_bboxes(instances_dict)

    classes = list(instances_dict.keys())
    h, w = rgb.shape[:2]

    segms_list = list(instances_dict.values())
    segms = np.concatenate(segms_list, axis=0)

    bboxes = []
    for cls in classes:
        bboxes.append(bboxes_dict[cls])
    bboxes = np.vstack(bboxes)
    bboxes[:, 0] *= w
    bboxes[:, 1] *= h
    bboxes[:, 2] *= w
    bboxes[:, 3] *= h

    labels = [np.full(s.shape[0], i, dtype=np.int32) for i, s in enumerate(segms_list)]
    labels = np.concatenate(labels)

    plot_instances(rgb, bboxes, labels, segms=segms, class_names=classes, **kwargs)
    viz = plt_to_numpy(dpi=dpi)
    return viz
