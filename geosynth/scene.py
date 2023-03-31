from pathlib import Path

from geosynth.common import PathLike
from geosynth.data import (
    CubeEnvironmentMap,
    Data,
    Depth,
    Extrinsics,
    Gravity,
    HdrCubeEnvironmentMap,
    HdrReflectance,
    HdrResidual,
    HdrRgb,
    HdrShading,
    HdrSphereEnvironmentMap,
    InstanceSegmentation,
    Intrinsics,
    LayoutLinesFull,
    LayoutLinesOccluded,
    LayoutLinesVisible,
    Lighting,
    Normals,
    Reflectance,
    Residual,
    Rgb,
    SemanticSegmentation,
    Shading,
    SphereEnvironmentMap,
)


class Scene:
    """Container for datatype readers for a single exemplar."""

    cube_environment_map: CubeEnvironmentMap
    depth: Depth
    extrinsics: Extrinsics
    gravity: Gravity
    hdr_cube_environment_map: HdrCubeEnvironmentMap
    hdr_reflectance: HdrReflectance
    hdr_residual: HdrResidual
    hdr_rgb: HdrRgb
    hdr_shading: HdrShading
    hdr_sphere_environment_map: HdrSphereEnvironmentMap
    instance_segmentation: InstanceSegmentation
    intrinsics: Intrinsics
    layout_lines_full: LayoutLinesFull
    layout_lines_occluded: LayoutLinesOccluded
    layout_lines_visible: LayoutLinesVisible
    lighting: Lighting
    normals: Normals
    reflectance: Reflectance
    residual: Residual
    rgb: Rgb
    semantic_segmentation: SemanticSegmentation
    shading: Shading
    sphere_environment_map: SphereEnvironmentMap

    def __init__(self, path: PathLike):
        """Create a scene object.

        Parameters
        ----------
        path: PathLike
            Path to where contents are downloaded to.
            Must contain a subfolder
        """
        self.path = Path(path)

    def __getattr__(self, name) -> Data:
        try:
            # We could setattr here, but then memory-usage would increase over time.
            return Data[name](self.path)
        except KeyError as e:
            raise AttributeError from e

    def __repr__(self):
        keywords = ", ".join(
            f"{key}={value!r}"
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        )
        class_name = type(self).__name__
        return f"{class_name}({keywords})"
