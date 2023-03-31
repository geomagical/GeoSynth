import errno
import json
import os
import urllib.request
from abc import abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Protocol, Union

import cv2
import numpy as np
from autoregistry import Registry

from ._visualize_instances import visualize_instances
from .common import PathLike
from .mappings import SemanticClassesMixin, apply_palette, to_uint8, turbo
from .models.lighting import Lighting as LightingModel

_DOWNLOAD_PREFIX = "https://storage.googleapis.com/geomagical-geosynth-public"


class OpenCVSaveError(Exception):
    """Error saving file with opencv."""


class UrlRetrieveReportHook(Protocol):
    def __call__(self, block_num: int, block_size: int, total_size: int) -> Any:
        ...


class DatasetVariant(str, Enum):
    """Available dataset variants for download.

    The "demo" variant contains the following scenes:
        * AI043_007_v001-8e009bbdcbffb624b8d86b0005a01915
        * AI043_008_v001-43f091c0ab99ee97f02204db92babad3
        * AI043_010_v001-2b71d64e5d04563b56e0d3e5725307d3
        * AI48_003_v001-0a825c69869524ed2518d04de356504d
        * AI48_006_v001-6b752db1da84a977212a6dd18f3cddf7
        * AI48_009_v001-2d5dc4fb7323f2aae0a91430bdadf5ee
    """

    demo = "demo"
    full = "full"

    def __str__(self):
        # https://github.com/tiangolo/typer/issues/290#issuecomment-860275264
        return self.value


class Data(Registry, snake_case=True):
    """Abstract Base Class for all data types."""

    ext: str

    @classmethod
    @abstractmethod
    def read_file(cls, fn: Path):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def write_file(cls, fn: Path, data: Any) -> None:
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not hasattr(cls, "ext"):
            raise ValueError(f"{cls.__name__}.ext must define ``ext``.")

        if not cls.ext.startswith("."):
            raise ValueError(f"{cls.__name__}.ext must start with '.'")

    def __init__(self, scene_path: PathLike):
        self.scene_path = Path(scene_path)

    @property
    def stem(self) -> str:
        """Stem of expected file on-disk."""
        return type(self).__registry__.name

    @property
    def path(self) -> Path:
        """Path to file on-disk."""
        ext = self.ext
        return self.scene_path / (self.stem + ext)

    def exists(self) -> bool:
        """Whether or not the file exists on-disk."""
        return self.path.exists()

    @classmethod
    def visualize(cls, data) -> np.ndarray:
        """Produce a uint8 RGB visualization of data."""
        raise NotImplementedError

    def read(self, *args, **kwargs):
        if not self.exists():
            # Explicitly check for file existence here so that a consistent
            # exception is raised instead of letting downstream readers decide.
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), str(self.path))
        return self.read_file(self.path, *args, **kwargs)

    def write(self, data: Any, *args, **kwargs) -> None:
        self.scene_path.mkdir(parents=True, exist_ok=True)
        return self.write_file(self.path, data, *args, *kwargs)

    @classmethod
    def download_zip(
        cls,
        output_dir: PathLike,
        variant: str = "full",
        force: bool = False,
        reporthook: Optional[UrlRetrieveReportHook] = None,
    ) -> Path:
        """Download a GeoSynth variant zip file.

        Parameters
        ----------
        output_dir: PathLike
            Output folder to download contents to.
            If it doesn't exist, it will be created.
        variant: str
            Variant of GeoSynth to download.
            A variant subfolder in ``output_dir`` will be created.
            Defaults to ``"full"``.
        force: bool
            Force a redownload, despite cached files.
            Defaults to ``False``.
        reporthook: Optional[UrlRetrieveReportHook]
            Optional callable to pass to ``urlretrieve``.
            Commonly used for progress updates.

        Returns
        -------
        Path
            Path to local zip file.
        """
        # Argument Preprocessing
        variant = variant.lower()
        try:
            variant = DatasetVariant[variant]
        except KeyError as e:
            raise ValueError(
                f'Variant "{variant}" not in valid. Choose one of: '
                f"{[x.value for x in DatasetVariant]}."
            ) from e

        output_dir = Path(output_dir).expanduser() / str(variant.value)
        output_dir.mkdir(exist_ok=True, parents=True)

        zip_name = f"{cls.__registry__.name}.zip"
        zip_path = output_dir / zip_name
        zip_path_tmp = zip_path.with_suffix(".tmp")

        if zip_path_tmp.exists():  # Delete a previous incomplete download.
            zip_path_tmp.unlink()

        if force or not zip_path.exists():
            zip_url = f"{_DOWNLOAD_PREFIX}/{variant.value}/{zip_name}"
            urllib.request.urlretrieve(  # noqa: S310
                zip_url,
                filename=zip_path_tmp,
                reporthook=reporthook,
            )
            zip_path_tmp.rename(zip_path)
        elif reporthook:
            reporthook(1, 1, 1)  # Will set reporthook to done.

        return zip_path


class PngMixin:
    ext = ".png"

    @classmethod
    def read_file(cls, fn: Path) -> np.ndarray:
        """Read a png file.

        Returns
        -------
        np.ndarray
            (H, W, 3) RGB or (H, W) grayscale image.
        """
        img = cv2.imread(str(fn), cv2.IMREAD_UNCHANGED)
        if img.ndim == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    @classmethod
    def write_file(cls, fn: Path, data: np.ndarray) -> None:
        """Write a png file.

        Parameters
        ----------
        data: np.ndarray
            (H, W, 3) RGB uint8 image.
        """
        if data.ndim == 3:
            data = cv2.cvtColor(data, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(fn), data)


class NpzMixin:
    """Stores/Reads npz data as-is."""

    ext = ".npz"

    @classmethod
    def read_file(cls, fn: Path) -> Union[Dict[str, np.ndarray], np.ndarray]:
        with np.load(fn) as data:
            data: Dict[str, np.ndarray] = dict(data)
            if len(data) == 1:
                return list(data.values())[0]
            else:
                return data

    @classmethod
    def write_file(
        cls,
        fn: Path,
        data: Union[Dict[str, np.ndarray], np.ndarray],
    ) -> None:
        if isinstance(data, dict):
            pass
        elif isinstance(data, np.ndarray):
            key: str = cls.__registry__.name  # type: ignore[reportGeneralTypeIssues]
            data = {
                key: data,
            }
        else:
            raise TypeError
        np.savez_compressed(fn, **data)


class NpzFloat16Mixin(NpzMixin):
    """Converts stored float16 -> float32 for easier standard processing."""

    @classmethod
    def read_file(cls, fn: Path) -> Union[Dict[str, np.ndarray], np.ndarray]:
        out = super().read_file(fn)
        if isinstance(out, np.ndarray):
            out = out.astype(np.float32)
        elif isinstance(out, dict):
            out = {k: v.astype(np.float32) for k, v in out.items()}
        else:
            raise TypeError
        return out

    @classmethod
    def write_file(cls, fn: Path, data: np.ndarray) -> None:
        data = data.astype(np.float16)
        super().write_file(fn, data)


class HdrMixin:
    ext = ".hdr"

    @classmethod
    def read_file(cls, fn: Path) -> np.ndarray:
        img = cv2.imread(str(fn), cv2.IMREAD_UNCHANGED)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    @classmethod
    def write_file(cls, fn: Path, data: np.ndarray) -> None:
        data = data.astype(np.float32)
        bgr = cv2.cvtColor(data, cv2.COLOR_RGB2BGR)
        if not cv2.imwrite(str(fn), bgr):
            raise OpenCVSaveError


class JsonMixin:
    ext = ".json"

    @classmethod
    def read_file(cls, fn: Path) -> Dict:
        with fn.open("r") as f:
            return json.load(f)

    @classmethod
    def write_file(cls, fn: Path, data: dict) -> None:
        with fn.open("w") as f:
            json.dump(data, f)


class CubeEnvironmentMap(NpzMixin, Data):
    pass


class Depth(NpzFloat16Mixin, Data):
    @classmethod
    def visualize(cls, data, min=0.0, max=10.0) -> np.ndarray:
        return turbo(data, min=min, max=max)


class Extrinsics(NpzMixin, Data):
    pass


class Gravity(NpzMixin, Data):
    pass


class HdrCubeEnvironmentMap(NpzMixin, Data):
    pass


class HdrReflectance(HdrMixin, Data):
    pass


class HdrResidual(HdrMixin, Data):
    pass


class HdrRgb(HdrMixin, Data):
    pass


class HdrShading(HdrMixin, Data):
    pass


class HdrSphereEnvironmentMap(HdrMixin, Data):
    pass


class InstanceSegmentation(NpzMixin, SemanticClassesMixin, Data):
    @classmethod
    def visualize(cls, data, **kwargs) -> np.ndarray:
        return visualize_instances(data, **kwargs)


class Intrinsics(NpzMixin, Data):
    pass


class LayoutLinesFull(NpzMixin, Data):
    pass


class LayoutLinesOccluded(NpzMixin, Data):
    pass


class LayoutLinesVisible(NpzMixin, Data):
    pass


class Lighting(JsonMixin, Data):
    @classmethod
    def read_file(cls, fn: Path) -> LightingModel:
        data = super().read_file(fn)
        return LightingModel(**data)


class Normals(NpzFloat16Mixin, Data):
    @classmethod
    def visualize(cls, data) -> np.ndarray:
        """Visualize normals with RGB representing XYZ."""
        return to_uint8(data / 2 + 0.5)


class Reflectance(PngMixin, Data):
    pass


class Residual(PngMixin, Data):
    pass


class Rgb(PngMixin, Data):
    pass


class SemanticSegmentation(PngMixin, SemanticClassesMixin, Data):
    @classmethod
    def visualize(cls, data) -> np.ndarray:
        return apply_palette(np.array(cls.PALETTE), data / 255)


class Shading(PngMixin, Data):
    pass


class SphereEnvironmentMap(PngMixin, Data):
    pass
