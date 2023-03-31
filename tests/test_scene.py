import cv2
import numpy as np
import pytest

from geosynth import Scene
from geosynth.data import Rgb


@pytest.fixture
def tmp_scene_folder(tmp_path):
    root = tmp_path / "scene_id"
    root.mkdir()

    img = np.zeros((48, 64, 3), dtype=np.uint8)
    img[..., 0] = 1
    img[..., 1] = 2
    img[..., 2] = 3
    Rgb.write_file(root / "rgb.png", img)

    def npz_save(name, data):
        kwargs = {name: data}
        np.savez_compressed(root / f"{name}.npz", **kwargs)

    npz_save("depth", np.ones((64, 48)).astype(np.float16))
    npz_save(
        "intrinsics",
        np.eye(3),
    )

    return root


def test_scene_basic(tmp_scene_folder):
    scene = Scene(tmp_scene_folder)

    rgb = scene.rgb.read()
    assert rgb.shape == (48, 64, 3)

    depth = scene.depth.read()
    assert depth.dtype == np.float32

    intrinsics = scene.intrinsics.read()
    assert intrinsics.shape == (3, 3)
    assert intrinsics.dtype == float
