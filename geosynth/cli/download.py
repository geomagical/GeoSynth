from pathlib import Path
from typing import List, Optional

from rich.progress import Progress, TimeElapsedColumn
from typer import Argument, Option

import geosynth
from geosynth.common import DEFAULT_DATASET_PATH
from geosynth.data import Data, DatasetVariant

_AVAILABLE_DTYPES = f"[{', '.join(sorted(Data))}])"


def download(
    dtypes: List[str] = Argument(
        ...,
        show_default=False,
        help="Assets to download. "
        f'Either specify "non-hdr", "all", or a subset of: {_AVAILABLE_DTYPES}.',
    ),
    dst: Path = Option(DEFAULT_DATASET_PATH, help="GeoSynth download directory."),
    variant: DatasetVariant = Option(
        DatasetVariant.demo, help="Variant of dataset to download."
    ),
    force: bool = Option(
        False, help="Force a re-download, despite locally cached files."
    ),
    cleanup: bool = Option(True, help="Delete zip files after unzipping."),
):
    """Download the GeoSynth data."""
    with Progress(
        *Progress.get_default_columns(),  # type: ignore[reportGeneralTypeIssues]
        TimeElapsedColumn(),
    ) as progress:
        output_path = geosynth.download(
            dst,
            dtypes,
            variant=variant.value,
            cleanup=cleanup,
            force=force,
            progress=progress,
        )

    print(f"Downloaded contents to {output_path}.")
