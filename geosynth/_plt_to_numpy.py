import io

import cv2
import numpy as np


def plt_to_numpy(close=True, axis_off=True, dpi=100):
    """Convert matplotlib state to numpy array.

    WARNING: output may be SLIGHTLY different depending on version of matplotlib

    Parameters
    ----------
    close : bool
        Close current figure after saving. Defaults to ``True``
    axis_off : bool
        Removes as many bordering elements as possible, with the goal being
        that the saved image is **just** the image being displayed.
        Defaults to ``True``
    dpi: int
        DPI to render output figure at.
        300 is good for a high resolution visualization.
        100 is good for a low resolution visualization.
        Defaults to matplotlib's default (100).

    Returns
    -------
    arr: numpy.ndarray
        Plotted image.
    """
    import matplotlib.pyplot as plt

    if axis_off:
        plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
        ax = plt.gca()
        ax.axis("off")
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

    with io.BytesIO() as f:
        plt.savefig(
            f,
            bbox_inches="tight",
            transparent="True",
            pad_inches=0,
            dpi=dpi,
            format="png",
        )
        if close:
            plt.close()
        f.seek(0)
        arr = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_UNCHANGED)
        arr = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)

    return arr[..., :3]  # Remove alpha channel
