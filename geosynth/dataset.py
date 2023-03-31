from pathlib import Path

from .common import DEFAULT_DATASET_PATH, PathLike
from .scene import Scene

_BLOCKLIST = set()  # TODO: populate, if necessary


class GeoSynth:
    def __init__(
        self,
        path: PathLike = DEFAULT_DATASET_PATH,
        variant: str = "full",
    ):
        """Create a GeoSynth dataset instance.

        Parameters
        ----------
        path : PathLike
            Same path that data was downloaded to.
            Should contain subfolders representing ``variants``.
            Defaults to ``~/data/geosynth/``.
        variant: str
            GeoSynth variant to use. To disable this feature, where the
            ``path`` folder directly contains scene folders, set to an empty
            string. Defaults to ``"full"``.
        """
        self.path = path = Path(path).expanduser()
        self.variant = variant
        self._scenes = [
            Scene(x)
            for x in (path / variant).glob("*/")
            if x.is_dir() and not x.stem.startswith(".") and x.name not in _BLOCKLIST
        ]

    def __len__(self):
        """Return the number of exemplars in the dataset."""
        return len(self._scenes)

    def __repr__(self):
        keywords = ", ".join(
            f"{key}={value!r}"
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        )
        class_name = type(self).__name__
        return f"{class_name}({keywords})"

    def __getitem__(self, index):
        """Get exemplar at ``index``.

        Parameters
        ----------
        index : int
            Index to get scene at.

        Returns
        -------
        Scene
            Scene at ``index``
        """
        return self._scenes[index]
