from typing import Any, List, Tuple, Union

import numpy as np
from pydantic import BaseModel, validator

_Vector3 = Union[
    np.ndarray,
    Tuple[float, float, float],
    List[float],
]


class GeoSynthBaseModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class LightSource(GeoSynthBaseModel):
    color: np.ndarray  # RGB in range [0, 1]
    intensity: float  # scalar in the range [0, 1].

    @validator("color", pre=True)
    def _validate_color_numpy(cls, v: _Vector3) -> np.ndarray:
        return np.array(v, dtype=np.float32)


class AmbientLight(LightSource):
    pass


class PointLight(LightSource):
    position: np.ndarray  # (3,) xyz position in the camera's coordinate system in meters.

    @validator("position", pre=True)
    def _validate_position_numpy(cls, v: _Vector3) -> np.ndarray:
        return np.array(v, dtype=np.float32)


class DirectionalLight(LightSource):
    direction: np.ndarray  # (3,) unit-norm xyz vector in the camera's coordinate system
    # (origin at light position)
    volume: np.ndarray  # (3, 3) un-normalized rotation matrix.
    # Row norm is axis length/scale in meters.

    @validator("direction", pre=True)
    def _validate_direction_numpy(cls, v: _Vector3) -> np.ndarray:
        return np.array(v, dtype=np.float32)

    @validator("volume", pre=True)
    def _validate_volume_numpy(cls, v: Any) -> np.ndarray:
        v = np.array(v, dtype=np.float32)
        if v.shape != (3, 3):
            raise ValueError
        return v


class Lighting(GeoSynthBaseModel):
    ambient: AmbientLight
    points: List[PointLight]
    directionals: List[DirectionalLight]
